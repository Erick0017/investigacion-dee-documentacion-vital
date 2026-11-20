from pathlib import Path
import base64,gzip,hashlib,json,re,sqlite3,zipfile

B=Path(__file__).resolve().parent.parent;W=Path(__file__).resolve().parent;S=W/'stage';S.mkdir(parents=True,exist_ok=True)
ARCH=B.parent/'DEE Cognitive System 1.1';SYS=ARCH/'sistema';APD=B/'sector_apd/stage/archivo';CAS=APD/'APD04/EVIDENCIA_CAS'
sha=lambda b:hashlib.sha256(b).hexdigest()
blobs={};paths={};plans=[]
def add(name,data,origin):
    h=sha(data);old=paths.get(name)
    if old and old['sha256']!=h:raise ValueError('logical collision '+name)
    paths[name]={'sha256':h,'bytes':len(data),'original':str(origin)};blobs[h]=data;return name
def file(name,p):return add(name,Path(p).read_bytes(),p)
def pair(key,folder):
    m=json.loads((folder/'EXPORTACION_SERVICIO.json').read_bytes())
    file('pares/'+key+'/EXPORTACION_SERVICIO.json',folder/'EXPORTACION_SERVICIO.json')
    for x in m['members']:
        p=folder/x['file'];data=p.read_bytes()
        assert len(data)==x['bytes'] and sha(data)==x['sha256'],p
        add('pares/'+key+'/'+x['file'],data,p)
    return m
def sqlite_rows(p):
    con=sqlite3.connect(p.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
    try:return {x['id']:dict(x) for x in con.execute('SELECT * FROM requests')}
    finally:con.close()
def operations(key,m,record,service,*,reference_result=None):
    rows=sqlite_rows(service/'cola.sqlite3');result=[]
    for x in record['operations']:
        if x.get('before_tick',-1)<m['physical']['tick'] or 'transport_id' not in x:continue
        id=x['transport_id'];row=rows[id];payload=json.loads(row['payload'])
        if payload['operacion'] in ('guardar','detener','reanudar','pausar','estado'):continue
        p=service/x['result_file'];data=p.read_bytes();assert sha(data)==x['result_sha256']
        n=file('referencias/'+key+'/'+id+'.json',p)
        result.append({'id':id,'payload':payload,'before_tick':x['before_tick'],'after_tick':x['after_tick'],'reference':n,'reference_sha256':sha(data)})
    return {'id':key,'pair':'pares/'+key,'parent_sha256':m['snapshot_sha256'],'initial_physical':m['physical'],'operations':result,'final_physical':record['physical'],'reference_result':reference_result}

# M306: the exact stopped queued request plus its original continuation panel.
main=ARCH/'evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/MAIN_INTEGRADO_R01'
m=pair('APD03_PENDING',main/'PAR_POSTSTOP_PENDIENTE')
final=json.loads((APD/'APD03/DEE_APD03_ANALISIS/MAIN/EVIDENCIA_MAIN/CORTE_FINAL_POSTSTOP.json').read_bytes())
plan=operations('APD03_PENDING',m,final['record'],main/'PAR_POSTSTOP_FINAL')
plan.update(mechanism='M306',source_overlay='fuentes/APD03',scope='Exact continuation of the archived pending goal and subsequent panel; not a replay of the preceding hour.')
plans.append(plan)
frozen=APD/'APD03/DEE_APD03_ANALISIS/MAIN/EVIDENCIA_MAIN/FUENTES_ANTES_DE_NATIVE'
for p in frozen.rglob('*.py'):
    if p.relative_to(frozen).parts[0] in ('app','capacidades'):file('fuentes/APD03/'+p.relative_to(frozen).as_posix(),p)
file('fuentes/APD03/app/importacion_emparejada.py',SYS/'app/importacion_emparejada.py')

# M307: equivalent post-ten-opportunity histories, then the original common panel.
cas_index=json.loads((CAS/'RUTAS_Y_HASHES.json').read_bytes())['sources']
for label in ('REAL','OMIT'):
    key='APD04_WAIT_'+label
    name='APD04_MAIN_T639374_EXPLORACION_R01'
    m=pair(key,SYS/'estado/fuentes_emparejadas'/name)
    source=next(x for x in cas_index if '/WAIT_R03_POST10_' in x['source_original'] and '/'+label+'/continuidad/TRAYECTORIA/RESULTADO.json' in x['source_original'])
    data=(CAS/source['object']).read_bytes();assert sha(data)==source['sha256'];full=json.loads(data)
    reference=add('referencias/'+key+'/TRAYECTORIA.json',data,source['source_original'])
    service=SYS/'estado/servicios_persistentes'/full['final_record']['life_id']
    plan=operations(key,m,full['final_record'],service,reference_result=reference)
    plan.update(mechanism='M307',source_overlay='fuentes/APD04',scope='Original ten opportunities and changes after a common complete parent with two different consequence histories. Prepared action codec R03, not an autonomous general policy.')
    plans.append(plan)
for x in cas_index:
    n=x['source_original']
    if '/WAIT_R03_POST10_' not in n or '/fuentes/' not in n or not n.endswith('.py'):continue
    fname=n.rsplit('/',1)[-1];fname=re.sub(r'^[0-9a-f]{64}_\d+_','',fname)
    folder='app' if fname in ('servicio_persistente.py','cola_local.py','protocolo_apd03.py','protocolo_apd04.py','process_control.py','usar_dee.py') else 'capacidades'
    if fname in ('ejecutar_plan_apd04_r04.py','gestionar.py'):continue
    data=(CAS/x['object']).read_bytes();assert sha(data)==x['sha256'];add('fuentes/APD04/'+folder+'/'+fname,data,n)
file('fuentes/APD04/app/importacion_emparejada.py',SYS/'app/importacion_emparejada.py')

# M308: exact8192tick task-off reference, including its first common material panel.
seed='APD04_SEMILLA_COLABORADOR_R01_T654959_COMPLETO_N0_R01'
m=pair('APD05_REST',SYS/'estado/fuentes_emparejadas'/seed)
ref=APD/'APD05/EVIDENCIA_CAUSAL/CONTROLES'
matches=[p for p in ref.rglob('RESULTADO.json') if 'APD05_CTL_PREV_REST_R03' in p.as_posix()]
if not matches:matches=[ARCH/'evidencia/campanas/APD05_GENESIS_SIN_LLM/controles/REPOSO_Y_ACCESO_R03/APD05_CTL_PREV_REST_R03/NATIVE/RESULTADO.json']
if len(matches)!=1 or not matches[0].is_file():raise ValueError(('REST reference',matches))
orig=json.loads(matches[0].read_bytes());file('referencias/APD05_REST/RESULTADO.json',matches[0])
sessions=matches[0].with_name('SESIONES.jsonl');file('referencias/APD05_REST/SESIONES.jsonl',sessions)
ops=[]
for line in sessions.read_text(encoding='utf8').splitlines():
    x=json.loads(line);payload=x['payload'];res=x['result']
    if payload['operacion'] not in ('avanzar','sesion'):continue
    n=add('referencias/APD05_REST/'+x['id']+'.json',(json.dumps(res,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode(),str(sessions)+'#'+x['id'])
    ops.append({'id':x['id'],'payload':payload,'before_tick':res['before_tick'],'after_tick':res['after_tick'],'reference':n,'reference_sha256':paths[n]['sha256']})
plans.append({'id':'APD05_REST','mechanism':'M308','pair':'pares/APD05_REST','parent_sha256':m['snapshot_sha256'],'initial_physical':m['physical'],'operations':ops,'final_physical':orig['final']['physical'],'source_overlay':'fuentes/APD05','scope':'Reproduce8192 native ticks with no task or auditor probes, then the first fixed8-use panel. Not a new hour-long run or a general maintenance strategy.'})
code=ref/'CODIGO'
for p in sorted(code.rglob('*.py'),key=lambda p:(0 if 'FUENTES_COMUNES' in p.parts else 1 if 'FUENTES_R04' in p.parts else 2,str(p))):
    rel=p.relative_to(code)
    if rel.parts[0] in ('FUENTES_COMUNES','FUENTES_R03','FUENTES_R04'):
        rest=Path(*rel.parts[1:]);n='fuentes/APD05/'+rest.as_posix()
        if n in paths and sha(p.read_bytes())!=paths[n]['sha256']:
            previous=paths.pop(n);paths['fuentes_versiones/APD05/'+previous['sha256']+'/'+rest.as_posix()]=previous
        file(n,p)
    elif p.name=='lexico_compartido_apd04.py':file('fuentes/APD05/capacidades/'+p.name,p)
file('fuentes/APD05/app/importacion_emparejada.py',SYS/'app/importacion_emparejada.py')

(S/'configuraciones').mkdir(exist_ok=True)
(S/'configuraciones/EPISODIOS.json').write_text(json.dumps({'plans':plans},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(S/'almacen').mkdir(exist_ok=True)
store=S/'almacen/CONTENIDOS.jsonl.gz'
with store.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=9) as gz:
    for h,data in sorted(blobs.items()):gz.write((json.dumps({'sha256':h,'bytes':len(data),'base64':base64.b64encode(data).decode()},separators=(',',':'))+'\n').encode('ascii'))
(S/'almacen/INDICE.json').write_text(json.dumps({'paths':paths,'store_sha256':sha(store.read_bytes())},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'plans':[(x['id'],len(x['operations'])) for x in plans],'paths':len(paths),'blobs':len(blobs),'store_bytes':store.stat().st_size},ensure_ascii=False))
