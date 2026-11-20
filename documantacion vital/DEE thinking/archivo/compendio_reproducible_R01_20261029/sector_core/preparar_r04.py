from pathlib import Path
import zipfile,json,gzip,hashlib,base64,shutil
W=Path(__file__).resolve().parent;S=W/'stage';P=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking').parent/'ingenieria/INGENIERIA_01_DEE_V27_MEMORIA_APRENDIZAJE_PLASTICIDAD_Y_PROCESAMIENTO_RESULTADOS.zip'
I=S/'documentacion/INDICE_MIEMBROS.json';F=S/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';d=json.loads(I.read_text(encoding='utf8'));seen={x['sha256'] for x in d['paths'].values()};added={};sources=[]
sha=lambda x:hashlib.sha256(x).hexdigest()
names=['RUNNERS/ing01_common.py','RUNNERS/ing01_apparatus.py','RUNNERS/VENDORED/core10_common.py','RUNNERS/VENDORED/core10_apparatus.py','REWRITE_WORK/RUNNERS/rewrite_common.py','REWRITE_WORK/RUNNERS/reset_apparatus_v1.py','REWRITE_WORK/RUNNERS/run_r04_reset_corrected_holdout.py','REWRITE_WORK/FREEZE/R04_RESET_CORRECTED_LOCK.json','REWRITE_WORK/CHALLENGES/R04_RESET_CORRECTED_CHALLENGES.json']
with zipfile.ZipFile(P) as z:
    for n in names+['REWRITE_WORK/HOLDOUT/R04_RESET_CORRECTED_HOLDOUT.json']:
        target='ingenierias/primarios/R04_RESET_CORRECTED_HOLDOUT.json' if n.endswith('HOLDOUT/R04_RESET_CORRECTED_HOLDOUT.json') else 'ingenierias/codigo/INGENIERIA_01/'+n
        raw=z.read(n);h=sha(raw);d['paths'][target]={'sha256':h,'bytes':len(raw),'origin':str(P)+'!/'+n};added[h]=raw;sources.append({'original':str(P)+'!/'+n,'relative_materialized':target,'sha256':h,'bytes':len(raw)})
    reference=z.read('REWRITE_WORK/HOLDOUT/R04_RESET_CORRECTED_HOLDOUT.json')
tmp=F.with_suffix('.r04.gz')
with gzip.open(F,'rb') as src,tmp.open('wb') as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=9) as dst:
        shutil.copyfileobj(src,dst)
        for h,data in added.items():
            if h not in seen:dst.write((json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode('ascii')},separators=(',',':'))+'\n').encode('ascii'))
tmp.replace(F);d['content_store_sha256']=sha(F.read_bytes());I.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
cp=S/'configuraciones/INGENIERIAS_RECUPERACION.json';cfg=json.loads(cp.read_text(encoding='utf8'));cfg['cases'].append({'id':'ING01_R04_CORREGIDO','mechanism':'M047','entry':'INGENIERIA_01/REWRITE_WORK/RUNNERS/run_r04_reset_corrected_holdout.py','output_result':'INGENIERIA_01/REWRITE_WORK/HOLDOUT/R04_RESET_CORRECTED_HOLDOUT.json','arguments':[],'references':{'results':{'path':'ingenierias/primarios/R04_RESET_CORRECTED_HOLDOUT.json','sha256':sha(reference)}}});cp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
(W/'r04_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8');print('R04 materials included; Native not executed')
