"""Two prospectively fixed post-reserve requests on the SAME reached APD life.

No teaching, restoration, route selection or result repair. Cost returns are
explicitly omitted while real queries retain all their native material effects.
The final R03 archive remains a separate parent window, not overwritten.
"""
import argparse,gzip,hashlib,importlib.util,json,sqlite3,sys,time
from datetime import datetime,timezone
from pathlib import Path

FORMS=('suma','diferencia','agrega','resta','total','quita')
PAIRS=((8,20),(30,10),(9,12),(28,9),(15,8),(26,7))
REQUESTS=[{'id':'apdpost01_memorias','payload':{'operacion':'sesion','retorno':'omit','situaciones':[{'modo':'memoria','contexto':c}for c in('alfa','beta','gamma','delta','epsilon','zeta')]}},{'id':'apdpost01_funciones','payload':{'operacion':'sesion','retorno':'omit','situaciones':[{'modo':'apd','texto':form,'operandos':list(pair)}for form,pair in zip(FORMS,PAIRS)]+[{'modo':'apd-conteo','presencias':[1,1,0]}]}}]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def freeze(system,hour_cut,hour_protocol,out):
    cut=read(hour_cut);base=read(hour_protocol);record=read(system/'estado/vidas/ASISTENTE_MAIN/VIDA.json')
    if cut.get('issues')or not cut['persistent_service']['owner_stopped']or cut['persistent_service']['pending_or_uncertain']:raise ValueError('Only the actual stopped R03 cut with complete empty transport/protocol can be handed off')
    if record['snapshot_sha256']!=cut['main']['snapshot_sha256']or record['physical']!=cut['main']['physical']:raise ValueError('Reached MAIN differs; never select another future')
    value={'schema':'DEE.APD01.post_reserve.two_literal_requests.v1','status':'FROZEN_FOR_ROOT_GO','life_id':'ASISTENTE_MAIN','prefix':'apdpost01_','initial_cut':cut['main'],'source_sha256':base['source_sha256'],'requests':REQUESTS,'source_harness_sha256':sha(Path(__file__)),'maximum_process_RAM_bytes':536870912,'owner_seconds':900,'control_wait_seconds':300,'budget_deadline_utc':base['budget_deadline_utc'],'R03_result_parent':{'cut':str(hour_cut),'cut_sha256':sha(hour_cut),'protocol_sha256':sha(hour_protocol)},'teaching':None,'no_route_docencia':True,'no_previous_minutes_added':True,'scope':'Two requested material panels in the same reached life, not a copied diagnostic fork and not another sixty-minute trial. No result-dependent selection or retry. Each physical response, admission, artifact and content/history is evaluated later.'}
    for rel,digest in value['source_sha256'].items():
        if sha(system/rel)!=digest:raise ValueError('S source changed after R03: '+rel)
    write(out,value);return {'protocol':str(out),'sha256':sha(out),'new_ticks':0}
def execute(system,protocol,out):
    p=read(protocol);out.mkdir(parents=True,exist_ok=False)
    if p['status']!='FROZEN_FOR_ROOT_GO'or p['source_harness_sha256']!=sha(Path(__file__))or p['requests']!=REQUESTS:raise ValueError('An exact prospectively reviewed post-reserve protocol is required')
    life=p['life_id'];card=system/'estado/vidas'/life/'VIDA.json';before=read(card)
    if before['snapshot_sha256']!=p['initial_cut']['snapshot_sha256']or before['physical']!=p['initial_cut']['physical']:raise ValueError('No restored/favorable state substitution')
    if(system/'estado/locks'/(before['world_id']+'.lock')).exists():raise ValueError('Another writer still owns MAIN')
    for rel,digest in p['source_sha256'].items():
        if sha(system/rel)!=digest:raise ValueError('Frozen source differs: '+rel)
        dest=out/'codigo'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((system/rel).read_bytes())
    queue_module=module('apd_post_queue',system/'app/cola_local.py');pc=module('apd_post_own_job',system/'app/process_control.py');qpath=system/'estado/servicios_persistentes'/before['world_id']/'cola.sqlite3';wal=qpath.with_name(qpath.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Unsettled WAL is not disposable')
    with sqlite3.connect(qpath.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        if c.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:raise ValueError('Complete actual pending transport must be retained, not discarded for this panel')
        if any(r[0].startswith(p['prefix'])for r in c.execute('SELECT id FROM requests')):raise ValueError('Post-reserve IDs already used; no replay')
    for row in REQUESTS:queue_module.validate_request(row['payload'])
    (out/'PROTOCOLO.json').write_bytes(protocol.read_bytes());(out/'CODIGO_EJECUTADO.py').write_bytes(Path(__file__).read_bytes());records={};owner=None;job=None;q=None;started=time.monotonic();error=None;resource=None;actual={k:before.get(k)for k in('life_id','world_id','profile','parent','physical','snapshot','snapshot_sha256')};deadline=datetime.fromisoformat(p['budget_deadline_utc'])
    def wait(identifier):
        until=time.monotonic()+p['control_wait_seconds']
        while time.monotonic()<until:
            row=q.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):
                records[identifier]=row
                if row['status']!='completed':raise RuntimeError('Actual request did not complete; no retry or repaired response')
                return json.loads(row['result'])
            if owner.poll()is not None:raise RuntimeError('Own owner exited while a request remains unresolved')
            time.sleep(.1)
        raise TimeoutError('Same admitted ID still unresolved: '+identifier)
    def submit(identifier,payload):
        reply=q.put(identifier,payload);records[identifier+'_admission']=reply
        if reply.get('admission')!='queued':raise ValueError('New literal request not queued; no alternate ID or retry')
        return wait(identifier)
    try:
        seconds=min(p['owner_seconds'],(deadline-datetime.now(timezone.utc)).total_seconds())
        if seconds<p['owner_seconds']:raise ValueError('Insufficient unchanged campaign budget for bounded post-reserve close')
        launch=time.time();argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','.1','--guardar-cada','60','--max-segundos',str(seconds)]
        owner,job,name=pc.spawn_owned(argv,cwd=system,stdout=(out/'OWNER_STDOUT.txt').open('x',encoding='utf8'),stderr=(out/'OWNER_STDERR.txt').open('x',encoding='utf8'),memory_limit=p['maximum_process_RAM_bytes']);until=time.monotonic()+90
        while time.monotonic()<until:
            if owner.poll()is not None:raise RuntimeError('Post-reserve owner failed before readiness')
            q=queue_module.QueueDB(qpath);state=q.get_meta('owner')
            if state and state.get('running')and datetime.fromisoformat(state['wall_utc']).timestamp()>=launch:records['initial_owner']=state;break
            time.sleep(.1)
        else:raise TimeoutError('Owner readiness')
        submit('apdpost01_reanudar',{'operacion':'reanudar'})
        for row in REQUESTS:submit(row['id'],row['payload'])
        submit('apdpost01_pausar',{'operacion':'pausar'});records['exported_before_STOP']=submit('apdpost01_exportar',{'operacion':'exportar'});submit('apdpost01_guardar',{'operacion':'guardar'});submit('apdpost01_detener',{'operacion':'detener'});owner.wait(timeout=60)
    except Exception as exc:
        error={'type':type(exc).__name__,'detail':str(exc)}
        if owner and owner.poll()is None and q:
            try:submit('apdpost01_emergency_stop',{'operacion':'detener'});owner.wait(timeout=60)
            except Exception as stopping:records['graceful_stop_error']=str(stopping)
    finally:
        if job:
            if owner.poll()is None:pc.terminate_job(job,125);owner.wait(timeout=60);records['forced_own_job_termination_no_retry']=True
            resource=pc.job_resources(job);pc.close_job(job)
    after=read(card);final={k:after.get(k)for k in('life_id','world_id','profile','parent','physical','snapshot','snapshot_sha256')}
    if q:records['final_owner']=q.get_meta('owner');records['remaining_transport']=q.outstanding()
    output={'schema':'DEE.APD01.actual_post_reserve.two_panels.v1','protocol':p,'protocol_sha256':sha(protocol),'before':actual,'final':final,'records':records,'harness_error':error,'host_seconds':time.monotonic()-started,'actual_owned_job_resources':resource,'sources_unchanged':all(sha(system/rel)==digest for rel,digest in p['source_sha256'].items()),'scope':'Real post-reserve MAIN use. Physical errors/silences are not repaired or converted into host answers. This window is separate from the fixed R03 real-time reserve.'}
    target=out/'POST_RESERVA.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(output,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'tick':final['physical']['tick'],'error':error,'seconds':output['host_seconds']}));return bool(error)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True);f=sub.add_parser('freeze');f.add_argument('--sistema',type=Path,required=True);f.add_argument('--corte-hora',type=Path,required=True);f.add_argument('--protocolo-hora',type=Path,required=True);f.add_argument('--salida',type=Path,required=True);e=sub.add_parser('execute');e.add_argument('--sistema',type=Path,required=True);e.add_argument('--protocolo',type=Path,required=True);e.add_argument('--salida',type=Path,required=True);a=parser.parse_args()
    if a.mode=='freeze':print(json.dumps(freeze(a.sistema,a.corte_hora,a.protocolo_hora,a.salida)))
    else:raise SystemExit(execute(a.sistema,a.protocolo,a.salida))
