"""Check extracted JSON values/text/arrays directly against immutable originals.

Read-only on source archives/files. This script is optional for recipients:
all values needed by the included recalculation are already in the audit ZIP.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,sys,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import Reader,canonical,sha
from campos_guardados import decode,array_bytes
sys.stdout.reconfigure(encoding='utf8')
def filehash(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--sources',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=Reader(a.root/'EVIDENCIA_PRIMARIA_ESENCIAL');source=a.sources
    names={'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip':'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad','DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip':'412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2'}
    for n,h in names.items():
        if filehash(source/n)!=h:raise ValueError('Wrong original archive')
    checked=0;byte_verified=0;core_jobs={};paths=[];dedup=set()
    def compare(row,o,b):
        nonlocal checked,byte_verified
        if sha(b)!=o['sha256']or len(b)!=o['bytes']:raise ValueError('Original bytes differ: '+str(o))
        byte_verified+=1
        if sha(canonical(json.loads(b)))!=row['canonical_sha256']:raise ValueError('Extracted original JSON values differ')
        if canonical(r.get(row['id']))!=canonical(json.loads(b)):raise ValueError('Reconstructed primary differs from original')
        checked+=1
    with zipfile.ZipFile(source/next(n for n in names if n.startswith('CPC9_')))as c9,zipfile.ZipFile(source/next(n for n in names if n.startswith('DEE_')))as core:
        for row in r.index['documents']:
            for o in row['origins']:
                identity=(o.get('kind'),o.get('archive'),o.get('member'),o.get('logical_path'),o.get('path'))
                if identity in dedup:continue
                dedup.add(identity)
                if o['kind']=='CORE_LOGICAL_MEMBER':core_jobs.setdefault(o['sha256'],[]).append((row,o));continue
                if o['kind']=='ZIP_MEMBER':compare(row,o,(c9 if o['archive'].startswith('CPC9_')else core).read(o['member']))
                else:
                    path=Path(o['path']);paths.append({'path':str(path),'sha256':o['sha256']});compare(row,o,path.read_bytes())
        store='DEE_COGNITIVE_CORE/mecanismos/RECUPERACION_POR_HASH.jsonl.gz';seen=set()
        for line in gzip.GzipFile(fileobj=core.open(store)):
            v=json.loads(line)
            if v['sha256']not in core_jobs:continue
            b=base64.b64decode(v['base64'],validate=True)
            for row,o in core_jobs[v['sha256']]:compare(row,o,b)
            seen.add(v['sha256'])
        if seen!=set(core_jobs):raise ValueError('Historical original absent from Core store')
        arrays=[]
        for f in sorted((a.root/'EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPACTOS').glob('S*.json')):
            d=json.loads(f.read_bytes());o=d['source_snapshot'];b=c9.read(o['member'])
            if sha(b)!=o['sha256']:raise ValueError('Snapshot byte identity mismatch')
            n,t,raw,clocks,offset=decode(gzip.decompress(b))
            if raw!=array_bytes(d,'RAW',f.parent)or clocks!=array_bytes(d,'CLOCKS',f.parent)or n!=d['N']or t!=d['physical']['tick']:raise ValueError('Physical field extraction differs from original snapshot')
            arrays.append({'member':o['member'],'original_sha256':sha(b),'RAW_bytes_compared':len(raw),'clocks_bytes_compared':len(clocks),'exact':True})
        textidx=json.loads((a.root/'EVIDENCIA_PRIMARIA_ESENCIAL/TESTIGOS_HISTORICOS/INDICE_DOCUMENTAL.json').read_bytes());text_jobs={q['sha256']:q for q in textidx['files']}
        for line in gzip.GzipFile(fileobj=core.open(store)):
            v=json.loads(line)
            if v['sha256']not in text_jobs:continue
            row=text_jobs.pop(v['sha256']);b=base64.b64decode(v['base64'],validate=True);target=a.root/'EVIDENCIA_PRIMARIA_ESENCIAL/TESTIGOS_HISTORICOS'/row['file']
            if sha(b)!=row['sha256']or target.read_bytes()!=b:raise ValueError('Historical textual witness differs')
        if text_jobs:raise ValueError('Historical textual witness origin missing')
    for n,h in names.items():
        if filehash(source/n)!=h:raise ValueError('Original archive changed during audit')
    report={'schema':'CPC9.essential.direct_original_comparison.v1','status':'PASS','engine_imported':False,'native_campaign_executed':False,
      'source_archives':names,'source_JSON_aliases_byte_and_value_verified':checked,'original_byte_hashes_verified':byte_verified,'full_physical_array_extractions':arrays,'historical_text_witnesses_verified':len(textidx['files']),
      'completed_clean_run_sources':paths,'originals_modified':False,'scope':'Original byte hashes and reconstructed JSON values checked separately; original whitespace/object-member ordering are not recreated.'}
    with a.out.open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:report[k]for k in('status','source_JSON_aliases_byte_and_value_verified','historical_text_witnesses_verified','engine_imported','originals_modified')}))
if __name__=='__main__':main()
