"""Locate declared experiment-source hashes, including failed older variants."""
from pathlib import Path
from collections import defaultdict
import argparse,re,json,zipfile,hashlib,sys
sys.stdout.reconfigure(encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--package',type=Path,required=True);a=p.parse_args();existing={}
    for f in a.package.rglob('*.py'):
        if f.name=='audit_primary.py':continue
        existing.setdefault(sha(f.read_bytes()),f.relative_to(a.package).as_posix())
    referenced=defaultdict(set);available=defaultdict(list);data={};exclusions=[]
    with zipfile.ZipFile(a.zip)as z:
        idx=json.loads(z.read('CPC9/revision/INDICE_EVIDENCIA.json'))
        for r in idx['files']:
            n='CPC9/'+r['member'].replace('\\','/');b=z.read(n)
            for h in set(re.findall(rb'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',b)):referenced[h.decode()].add(n)
        for i in z.infolist():
            if not i.filename.endswith('.py'):continue
            b=z.read(i.filename);h=sha(b)
            if h not in referenced:continue
            if i.filename.endswith('/audit_primary.py')or re.search(rb'#include\s*[<"]|PYBIND11_MODULE|__global__|def\s+one_step\s*\(',b):
                exclusions.append({'member':i.filename,'sha256':h,'reason':'Transition implementation or embedded compiled source excluded from external reduced audit; source remains in original.'});continue
            available[h].append(i.filename);data[h]=b
        rows=[]
        folder=a.package/'CONFIGURACIONES_Y_REPRODUCCION/CODIGOS_POR_HASH';folder.mkdir(exist_ok=False)
        for h,names in sorted(available.items()):
            if h in existing:inc=existing[h]
            else:
                f=folder/(h[:24]+'.py');f.write_bytes(data[h]);inc=f.relative_to(a.package).as_posix()
            rows.append({'sha256':h,'included':inc,'original_archive':a.zip.name,'archive_sha256':'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad','original_members':names,'referenced_by_primaries':sorted(referenced[h]),
              'scope':'A source hash occurs in these primary records. This is not proof that every listed module was imported into every participant.'})
    report={'schema':'CPC9.audit.recovered_scientific_source_hashes.v1','unique_source_texts':len(rows),'entries':rows,'excluded':exclusions,
      'deduplication':'Exact same source hash uses one existing file or one additional canonical file; previous unsuccessful versions are not removed because they failed.'}
    (a.package/'CONFIGURACIONES_Y_REPRODUCCION/FUENTES_POR_HASH.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':'PASS','source_hashes':len(rows),'additional_files':len(list(folder.glob('*.py'))),'excluded_transition_sources':len(exclusions)}))
if __name__=='__main__':main()
