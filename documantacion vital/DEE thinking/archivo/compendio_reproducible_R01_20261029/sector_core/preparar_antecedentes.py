from pathlib import Path
import zipfile,json,gzip,hashlib,base64,shutil,re
W=Path(__file__).resolve().parent;S=W/'stage';BASE=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking').parent
INDEX=S/'documentacion/INDICE_MIEMBROS.json';STORE=S/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
sha=lambda b:hashlib.sha256(b).hexdigest()
idx=json.loads(INDEX.read_text(encoding='utf8'));seen={x['sha256'] for x in idx['paths'].values()};added={};sources=[]
def add(name,data,origin):
    h=sha(data);idx['paths'][name]={'sha256':h,'bytes':len(data),'origin':origin};added[h]=data;sources.append({'original':origin,'relative_materialized':name,'sha256':h,'bytes':len(data)})
cases=[]
p=BASE/'ingenieria/INGENIERIA_02_DEE_V27_PROCESAMIENTO_INTEGRADO_ADAPTACION_Y_AUTONOMIA_RESULTADOS.zip'
selected=['run_d06_relative_memory.py','run_d09_relative_readout_longevity.py','run_d14_persistent_native_reader.py','run_d17_temporal_order_zero_payload.py','run_d19_parallel_temporal_bank.py']
with zipfile.ZipFile(p) as z:
    for n in ['ing02_common.py','paired_relative_apparatus_v1.py','paired_relative_apparatus_v2.py','temporal_order_apparatus_v1.py',*selected]:add('ingenierias/codigo/INGENIERIA_02/RUNNERS/'+n,z.read('RUNNERS/'+n),str(p)+'!/RUNNERS/'+n)
    for n in selected:
        data=z.read('RUNNERS/'+n);text=data.decode('utf8');result=re.findall(r'"(ING02_[A-Z0-9_]+\.json)"',text)[-1]
        expected='DISCOVERY/'+result;target='ingenierias/primarios/'+result;value=z.read(expected);add(target,value,str(p)+'!/'+expected)
        cases.append({'id':result[:-5],'mechanism':'M044','entry':'INGENIERIA_02/RUNNERS/'+n,'output_result':'INGENIERIA_02/DISCOVERY/'+result,'arguments':[],'references':{'results':{'path':target,'sha256':sha(value)}}})
p=BASE/'procesos/PROCESOS_02_DEE_V27_CONTINUIDAD_CAUSAL_POST_TRANSICION_RESULTADOS.zip'
with zipfile.ZipFile(p) as z:
    for n in ['runner_procesos02.py','config.json']:add('procesos02/codigo/'+n,z.read(n),str(p)+'!/'+n)
    for n in ['results.json','telemetry.npz']:add('procesos02/primarios/'+n,z.read(n),str(p)+'!/'+n)
    cases.append({'id':'PROCESOS02_TRES_GEOMETRIAS','mechanism':'M045','entry':'runner_procesos02.py','configurations':['MAIN_S0','FRESH_V1','FRESH_V2'],'references':{n:{'path':'procesos02/primarios/'+n,'sha256':sha(z.read(n))} for n in ['results.json','telemetry.npz']}})
p=BASE/'procesos/PROCESOS_03_DEE_V27_NATIVE_THERMODYNAMICS_REFOUNDATION_R4_NEW_RESULTADOS.zip'
with zipfile.ZipFile(p) as z:
    for item in z.infolist():
        if item.is_dir() or item.filename in ('MANIFEST.json',):continue
        if item.filename.endswith(('.pyd','.whl','.zip','.cpp','.pyc')):continue
        add('procesos03/'+item.filename,z.read(item.filename),str(p)+'!/'+item.filename)
tmp=STORE.with_suffix('.antecedentes.gz')
with gzip.open(STORE,'rb') as src,tmp.open('wb') as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=9) as dst:
        shutil.copyfileobj(src,dst)
        for h,data in added.items():
            if h not in seen:dst.write((json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode('ascii')},separators=(',',':'))+'\n').encode('ascii'))
tmp.replace(STORE);idx['content_store_sha256']=sha(STORE.read_bytes());INDEX.write_text(json.dumps(idx,ensure_ascii=False,separators=(',',':')),encoding='utf8')
cfgpath=S/'configuraciones/INGENIERIAS_RECUPERACION.json';cfg=json.loads(cfgpath.read_text(encoding='utf8'));cfg['cases']+=cases;cfgpath.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
(W/'antecedentes_sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'new_variants':len(cases),'store_bytes':STORE.stat().st_size,'materialized_paths':len(idx['paths'])},ensure_ascii=False))
