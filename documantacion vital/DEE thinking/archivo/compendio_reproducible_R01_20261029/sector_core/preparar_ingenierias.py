from pathlib import Path
import zipfile,json,gzip,hashlib,base64,shutil
WORK=Path(__file__).resolve().parent;STAGE=WORK/'stage'
BASE=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking').parent/'ingenieria'
INDEX=STAGE/'documentacion/INDICE_MIEMBROS.json';STORE=STAGE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
sha=lambda b:hashlib.sha256(b).hexdigest()
index=json.loads(INDEX.read_text(encoding='utf8'));old_hashes={x['sha256'] for x in index['paths'].values()};added={};sources=[]
def add(name,data,original):
    h=sha(data);index['paths'][name]={'sha256':h,'bytes':len(data),'origin':original};added[h]=data;sources.append({'original':original,'relative_materialized':name,'sha256':h,'bytes':len(data)})
archives={n:BASE/f for n,f in [('ING05','INGENIERIA_05_DEE_V27_INTEGRADA_RESULTADOS.zip'),('ING06','INGENIERIA_06_DEE_V27_CAPACIDAD_ADAPTATIVA_Y_FRONTERA_L4_RESULTADOS.zip')]}
selected={
 'ING05':['04_RAW_CAUSAL_MINIMUM/RUNNERS/run_nrd04_stage_ab.py','04_RAW_CAUSAL_MINIMUM/DEPENDENCIES/INGENIERIA_02_RUNNERS/ing02_common.py','04_RAW_CAUSAL_MINIMUM/DEPENDENCIES/INGENIERIA_02_RUNNERS/temporal_order_apparatus_v1.py','04_RAW_CAUSAL_MINIMUM/DEPENDENCIES/INGENIERIA_02_RUNNERS/run_d09_relative_readout_longevity.py','05_HISTORY_CONDITIONED_TRANSFORMATION/RUNNERS/run_nrd05_history_conditioned_transformation.py','05_HISTORY_CONDITIONED_TRANSFORMATION/FREEZE/NRD05_LOCK.json','06_HISTORY_SPECIFICITY/RUNNERS/run_nrd06_history_specificity.py','06_HISTORY_SPECIFICITY/FREEZE/NRD06_LOCK.json'],
 'ING06':['09_ENDOGENOUS_FREE_RUN/RUNNERS/run_ing06_endogenous_free_run.py','11_RAW_ONLY_FRESH_POST_HOST/RUNNERS/run_ing06_raw_only_fresh.py','12_CAUSALLY_SENSITIVE_OPPORTUNITIES/RUNNERS/run_ing06_sensitive_opportunities.py','12_CAUSALLY_SENSITIVE_OPPORTUNITIES/RUNNERS/run_ing06_sensitive_opportunities_v2.py']}
cases=[]
with zipfile.ZipFile(archives['ING05']) as z:
    member='INGENIERIA_05/04_RAW_CAUSAL_MINIMUM/DEPENDENCIES/dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl';wheel=z.read(member);assert sha(wheel)=='69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939'
    dest=WORK.parent/'package/motor'/Path(member).name;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==wheel
    else:dest.write_bytes(wheel)
for kind,archive in archives.items():
    prefix='INGENIERIA_05/' if kind=='ING05' else 'INGENIERIA_06/'
    with zipfile.ZipFile(archive) as z:
        for name in selected[kind]:
            full=prefix+name;add('ingenierias/codigo/'+full,z.read(full),str(archive)+'!/'+full)
        if kind=='ING05':
            specs=[('NRD05','05_HISTORY_CONDITIONED_TRANSFORMATION','NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json','NRD05_FACTORIAL_STATES_AND_FUTURES.npz','run_nrd05_history_conditioned_transformation.py'),('NRD06','06_HISTORY_SPECIFICITY','NRD06_HISTORY_SPECIFICITY.json','NRD06_SPECIFICITY_STATES_AND_FUTURES.npz','run_nrd06_history_specificity.py')]
        else:
            specs=[('ING06_FREE','09_ENDOGENOUS_FREE_RUN','ING06_ENDOGENOUS_FREE_RUN.json','ING06_ENDOGENOUS_FREE_RUN.npz','run_ing06_endogenous_free_run.py'),('ING06_RAW','11_RAW_ONLY_FRESH_POST_HOST','ING06_RAW_ONLY_FRESH.json','ING06_RAW_ONLY_FRESH.npz','run_ing06_raw_only_fresh.py'),('ING06_SENSITIVE_V2','12_CAUSALLY_SENSITIVE_OPPORTUNITIES','ING06_SENSITIVE_OPPORTUNITIES_V2.json','ING06_SENSITIVE_OPPORTUNITIES_V2.npz','run_ing06_sensitive_opportunities_v2.py')]
        for cid,folder,result,telemetry,script in specs:
            refs={}
            for group,name in [('RESULTS',result),('TELEMETRY',telemetry)]:
                src=prefix+folder+'/'+group+'/'+name;target='ingenierias/primarios/'+cid+'/'+name;value=z.read(src);add(target,value,str(archive)+'!/'+src);refs[group.lower()]={'path':target,'sha256':sha(value)}
            cases.append({'id':cid,'mechanism':'M042' if kind=='ING05' else 'M043','entry':prefix+folder+'/RUNNERS/'+script,'output_result':prefix+folder+'/RESULTS/'+result,'output_telemetry':prefix+folder+'/TELEMETRY/'+telemetry,'references':refs,'arguments':['--threads','1']})
temp=STORE.with_suffix('.ingenierias.gz')
with gzip.open(STORE,'rb') as src,temp.open('wb') as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=9) as dst:
        shutil.copyfileobj(src,dst)
        for h,data in added.items():
            if h not in old_hashes:dst.write((json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode('ascii')},separators=(',',':'))+'\n').encode('ascii'))
temp.replace(STORE);index['content_store_sha256']=sha(STORE.read_bytes());INDEX.write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf8')
(STAGE/'configuraciones/INGENIERIAS_RECUPERACION.json').write_text(json.dumps({'cases':cases,'engine':'dee_universe_v27-27.0.0 original ABI, not a silent4.5 port','wheel_sha256':sha(wheel)},ensure_ascii=False,indent=2),encoding='utf8')
(WORK/'ingenierias_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'variants':len(cases),'store_bytes':STORE.stat().st_size,'legacy_wheel_bytes':len(wheel)},ensure_ascii=False))
