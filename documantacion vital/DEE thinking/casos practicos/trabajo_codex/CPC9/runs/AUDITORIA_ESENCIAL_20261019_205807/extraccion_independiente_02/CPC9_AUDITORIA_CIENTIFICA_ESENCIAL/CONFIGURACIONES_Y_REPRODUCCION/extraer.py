"""Scientific evidence extraction only. Does not import or run the DEE engine."""
from pathlib import Path
from collections import Counter,OrderedDict
import argparse,base64,gzip,hashlib,io,json,re,shutil,sys,time,zipfile,zlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import canonical,sha,diff,apply
sys.stdout.reconfigure(encoding='utf8')

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def filehash(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def vals(x):
    if isinstance(x,dict):
        for v in x.values():yield from vals(v)
    elif isinstance(x,list):
        for v in x:yield from vals(v)
    elif isinstance(x,str):yield x

class Writer:
    def __init__(self,out):
        self.root=out/'EVIDENCIA_PRIMARIA_ESENCIAL';self.root.mkdir(parents=True)
        (self.root/'datos').mkdir();self.rows=[];self.seen={};self.bases={};self.cache=OrderedDict();self.aliases=[]
    def base(self,row):
        k=row['id']
        if k not in self.cache:self.cache[k]=json.loads((self.root/row['data_file']).read_bytes())['value']
        self.cache.move_to_end(k)
        while len(self.cache)>4:self.cache.popitem(last=False)
        return self.cache[k]
    def add(self,b,origin,role):
        source_sha=sha(b);x=json.loads(b);cb=canonical(x);ch=sha(cb)
        origin.update(sha256=source_sha,bytes=len(b),canonical_sha256=ch)
        if ch in self.seen:
            row=self.seen[ch];row['origins'].append(origin);self.aliases.append({'id':row['id'],**origin});return row['id']
        ident='D'+str(len(self.rows)+1).zfill(5)
        group=(x.get('schema'),tuple(sorted(x)),len(x.get('frames',[])),len(x.get('rows',[])))if isinstance(x,dict)else('LIST',len(x))if isinstance(x,list)else(type(x).__name__,)
        payload={'mode':'full','value':x};mode='full';baseid=None
        if group in self.bases and len(cb)>2000:
            br=self.bases[group];base=self.base(br);ops=diff(base,x);patch={'mode':'delta','base':br['id'],'operations':ops}
            pb=canonical(patch)
            if len(pb)<len(cb)*.90:
                restored=apply(base,ops)
                if canonical(restored)!=cb:raise ValueError('Delta round-trip mismatch')
                payload=patch;mode='delta';baseid=br['id']
        data=canonical(payload)+b'\n';rel='datos/'+ident+'.json';(self.root/rel).write_bytes(data)
        row={'id':ident,'role':role,'schema':x.get('schema')if isinstance(x,dict)else None,'case_id':x.get('case_id',x.get('case'))if isinstance(x,dict)else None,
          'mode':mode,'base':baseid,'data_file':rel,'data_sha256':sha(data),'encoded_bytes':len(data),'canonical_bytes':len(cb),'canonical_sha256':ch,'origins':[origin]}
        self.rows.append(row);self.seen[ch]=row;self.aliases.append({'id':ident,**origin})
        if mode=='full'and group not in self.bases:self.bases[group]=row
        return ident
    def finish(self):
        obj={'schema':'CPC9.essential.lossless_json_values.v1','guarantee':'Every JSON value, field, array order and integer retained. Original formatting bytes are referenced by SHA, not reconstructed.',
             'original_byte_identity_is_not_canonical_identity':True,'documents':self.rows,'source_aliases':self.aliases}
        (self.root/'INDICE_DOCUMENTOS.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        return obj

def main():
    p=argparse.ArgumentParser();p.add_argument('--sources',type=Path,required=True);p.add_argument('--clean-core',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    start=time.monotonic();source=a.sources.resolve(strict=True);out=a.out.resolve()
    if out.exists():raise FileExistsError('Use a new empty output path')
    out.mkdir(parents=True);writer=Writer(out);events=[];sources=[]
    c9=source/'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip';core=source/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'
    expected={c9:'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad',core:'412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2'}
    for path,h in expected.items():
        if filehash(path)!=h:raise ValueError('Original archive identity mismatch: '+str(path))
        sources.append({'path':str(path),'sha256':h,'bytes':path.stat().st_size})
    with zipfile.ZipFile(c9)as z:
        index=json.loads(z.read('CPC9/revision/INDICE_EVIDENCIA.json'))
        primary_names={'CPC9/'+v['member'].replace('\\','/')for v in index['files']}
        # Whole primary containers: all281, including failed/incomplete attempts.
        for i,row in enumerate(index['files']):
            name='CPC9/'+row['member'].replace('\\','/');b=z.read(name)
            if sha(b)!=row['sha256']:raise ValueError('CPC9 primary/index mismatch: '+name)
            writer.add(b,{'kind':'ZIP_MEMBER','archive':c9.name,'archive_sha256':expected[c9],'member':name},'CPC9_PRIMARY')
            if i%40==0:print('CPC9 primary',i,flush=True)
        # Frozen operationalization/configuration and provenance, not primary facts.
        for i in z.infolist():
            name=i.filename
            if name.endswith('.json')and(name.startswith('CPC9/configuraciones/')or name in[
              'CPC9/revision/NSM65_EVIDENCIAS.json','CPC9/genealogia/NSM65_CATALOGO_4_5.json','CPC9/revision/VIDA_PRINCIPAL.json',
              'CPC9/revision/CALCULOS.json','CPC9/revision/INTEGRACION_CAUSAL.json','CPC9/revision/ARQUITECTURA_E1.json',
              'CPC9/revision/INDICE_EVIDENCIA.json','CPC9/revision/RECURSOS_Y_COSTES.json','CPC9/revision/CONTROLES_Y_RESERVAS.json',
              'CPC9/front_semantics/revision/NSM65_PLAN_CPC9.json','CPC9/revision/REGULACION_NATIVA.json',
              'CPC9/revision/DIAGNOSTICOS_DE_INTERFERENCIA.json','CPC9/revision/RETENCION_Y_PLASTICIDAD.json']):
                writer.add(z.read(name),{'kind':'ZIP_MEMBER','archive':c9.name,'archive_sha256':expected[c9],'member':name},'CONFIGURATION_OR_PRIOR_INTERPRETATION')
        # Experiment-side recipes/decoders only. No engine or product code.
        code=[]
        for i in z.infolist():
            n=i.filename
            if n.endswith('.py')and any(n.startswith('CPC9/'+x)for x in('src/','front_relations/src/','front_semantics/src/')):
                if '/versiones/'in n:continue
                b=z.read(n);target=out/'CONFIGURACIONES_Y_REPRODUCCION'/'FUENTES_EXPERIMENTALES'/n[5:];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
                code.append({'included':target.relative_to(out).as_posix(),'archive':c9.name,'archive_sha256':expected[c9],'member':n,'sha256':sha(b),'bytes':len(b)})
        (out/'FUENTES_EXPERIMENTALES_ORIGEN.json').write_text(json.dumps(code,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    # Include the completed exact-ZIP proofs as recorded data, never rerun them.
    proof=read(source/'PRUEBA_RECUPERACION_DESDE_CERO.json')
    for name in('PRUEBA_RECUPERACION_DESDE_CERO.json','VERIFICACION_CORE_FINAL_EXTERNA.json','VERIFICACION_CPC9_FINAL_EXTERNA.json','VERIFICACION_FINAL.json','AUDITORIA_ENTREGA_INDEPENDIENTE.json'):
        path=source/name;writer.add(path.read_bytes(),{'kind':'ORIGINAL_EXTERNAL_FILE','path':str(path),'member':name},'RECORDED_TECHNICAL_PROOF_NOT_NEW_EXECUTION')
    with zipfile.ZipFile(core)as z:
        mat=json.loads(z.read('DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json'));ix=json.loads(z.read('DEE_COGNITIVE_CORE/documentacion/INDICE_MIEMBROS.json'))
        refs=set(vals(mat))|set(vals(proof));external_docs=[]
        for i in z.infolist():
            name=i.filename
            if name.endswith('.json')and('/verificaciones/'in name and'CANDIDATO_'not in name or'/configuraciones/'in name):
                b=z.read(name);d=json.loads(b);refs.update(vals(d));external_docs.append((name,b))
        choose={n:r for n,r in ix['paths'].items()if (r['sha256']in refs or n in refs)and n.endswith('.json')}
        bysha={}
        for n,r in choose.items():bysha.setdefault(r['sha256'],[]).append((n,r))
        store='DEE_COGNITIVE_CORE/mecanismos/RECUPERACION_POR_HASH.jsonl.gz';seen=set()
        for line in gzip.GzipFile(fileobj=z.open(store)):
            item=json.loads(line);h=item['sha256']
            if h not in bysha:continue
            b=base64.b64decode(item['base64'],validate=True)
            if len(b)!=item['bytes']or sha(b)!=h:raise ValueError('Core blob checksum mismatch')
            for name,row in bysha[h]:
                writer.add(b,{'kind':'CORE_LOGICAL_MEMBER','archive':core.name,'archive_sha256':expected[core],'member':store,'logical_path':name,'origin':row.get('origin',{})},'HISTORICAL_REFERENCED_RECORD')
            seen.add(h)
        if seen!=set(bysha):raise ValueError('Historical referenced evidence absent')
        for name,b in external_docs:writer.add(b,{'kind':'ZIP_MEMBER','archive':core.name,'archive_sha256':expected[core],'member':name},'HISTORICAL_RECALCULATION_OR_CONFIGURATION')
        for name in('documentacion/MATRIZ_CAPACIDADES.json','documentacion/COMPRESION.json','IDENTIDAD_KERNEL.json','documentacion/COMPARACION_DOS_CPC8.json'):
            writer.add(z.read('DEE_COGNITIVE_CORE/'+name),{'kind':'ZIP_MEMBER','archive':core.name,'archive_sha256':expected[core],'member':'DEE_COGNITIVE_CORE/'+name},'HISTORICAL_SCOPE_METADATA')
    # Fresh recorded outputs of the already completed clean recovery. No execution.
    fresh=[]
    for folder in sorted(a.clean_core.glob('native_*')):
        for f in sorted(folder.rglob('*.json')):
            b=f.read_bytes();r=f.relative_to(a.clean_core).as_posix();writer.add(b,{'kind':'COMPLETED_CLEAN_RUN_FILE','path':str(f),'member':r,'family':folder.name[7:]},'COMPLETED_REPLAY_PRIMARY_OR_CONFIGURATION');fresh.append(r)
    index=writer.finish()
    for path,h in expected.items():
        if filehash(path)!=h:raise ValueError('Original unexpectedly changed during extraction')
    result={'schema':'CPC9.essential.extraction.v1','status':'PASS','engine_imported':False,'campaign_rerun':False,'originals_modified':False,
       'source_archives':sources,'cpc9_primary_containers':len(primary_names),
       'core_referenced_json_paths':len(choose),'completed_recovery_files':len(fresh),'unique_documents':len(index['documents']),'source_aliases':len(index['source_aliases']),
       'modes':dict(Counter(r['mode']for r in writer.rows)),'canonical_json_bytes':sum(r['canonical_bytes']for r in writer.rows),'encoded_json_bytes':sum(r['encoded_bytes']for r in writer.rows),
       'extraction_roundtrips_verified':True,'elapsed_seconds':time.monotonic()-start,'scope':'All indexed281CPC9 primary containers; referenced historical JSON and completed clean-runJSON; no engine binaries/source or dense states.'}
    (out/'EXTRACCION_VERIFICADA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
