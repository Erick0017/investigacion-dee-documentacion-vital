"""One supervised owner and the existing FIFO protocol; no solver or restart."""
import argparse,datetime as dt,gzip,hashlib,importlib.util,json,os,shutil,sys,time
from pathlib import Path

def read(p): return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def mod(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def now():return dt.datetime.now(dt.timezone.utc).isoformat()

def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    s=a.sistema.resolve();proto=read(a.protocolo);out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False)
    life=proto['life'];prefix=proto['prefix'];card=s/'estado/vidas'/life/'VIDA.json';initial=read(card)
    if initial['snapshot_sha256']!=proto['snapshot_sha256'] or sha(s/initial['snapshot'])!=initial['snapshot_sha256']:raise ValueError('Exact complete lived snapshot required')
    if (s/'estado/locks'/(initial['world_id']+'.lock')).exists():raise ValueError('Another owner holds world')
    deadline=dt.datetime.fromisoformat('2026-10-26T11:17:43+00:00');remaining=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()
    if remaining<proto.get('enabled_seconds',0)+600:raise ValueError('Insufficient unchanged campaign budget')
    sys.path.insert(0,str(s))
    qm=mod('apd02_queue',s/'app/cola_local.py');pc=mod('apd02_process',s/'app/process_control.py')
    db=qm.QueueDB(s/'estado/servicios_persistentes'/initial['world_id']/'cola.sqlite3')
    outstanding=db.outstanding();expected=proto.get('expected_initial_pending',[])
    if [x['id']for x in outstanding]!=[x['id']for x in expected]:raise ValueError('Exact pending IDs required; never discard, replace or manufacture an inherited queue')
    for x,y in zip(outstanding,expected):
        body=json.loads(x['payload'])if isinstance(x['payload'],str)else x['payload']
        if body!=y['payload']:raise ValueError('Pending literal request changed')
    for e in proto['events']+proto.get('pending_after_pause',[]):
        if 'payload'in e:qm.validate_request(e['payload'])
    write(out/'PROTOCOLO.json',proto);shutil.copyfile(Path(__file__),out/'CODIGO_EJECUTADO.py')
    sources=[]
    for rel in [Path('gestionar.py'),*sorted(p.relative_to(s)for p in(s/'app').glob('*.py')),*sorted(p.relative_to(s)for p in(s/'capacidades').glob('*apd*.py'))]:
        f=s/rel;t=out/'codigo'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,t);sources.append({'file':rel.as_posix(),'sha256':sha(f),'bytes':f.stat().st_size})
    write(out/'FUENTES_ANTES_TICKS.json',sources)
    result={'schema':'APD02.one_owner_window.v1','life':life,'initial':{k:initial.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')},'sources':sources,'records':{},'owner_samples':[],'new_ticks_before_start':0}
    log=(out/'ADMISIONES.jsonl').open('x',encoding='utf8');owner=None;job=None;began=time.monotonic();origin=None
    def emit(x):log.write(json.dumps({'utc':now(),**x},sort_keys=True,ensure_ascii=False)+'\n');log.flush()
    def wait(identifier,seconds=240):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            row=db.get(identifier)
            if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
                result['records'][identifier]=row
                if row['status']!='completed':raise RuntimeError('Preserved adverse transport '+identifier+': '+row['status'])
                return json.loads(row['result'])
            if owner and owner.poll()is not None:raise RuntimeError('Owner exited; no replacement')
            time.sleep(.1)
        raise TimeoutError('Same ID remains pending: '+identifier)
    def submit(identifier,payload):
        reply=db.put(identifier,payload);emit({'id':identifier,'payload':payload,'admission':reply,'enabled_seconds':None if origin is None else time.monotonic()-origin})
        if reply.get('admission')!='queued':raise ValueError('Literal request not queued, no replay: '+identifier)
        return wait(identifier)
    def ctl(label,operation):return submit(prefix+label,{'operacion':operation})
    try:
        argv=[sys.executable,'-I','-B','-X','utf8',str(s/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','.1','--ticks-ocio','1','--guardar-cada','60','--max-segundos',str(proto.get('enabled_seconds',0)+1200)]
        launch=time.time();owner,job,name=pc.spawn_owned(argv,cwd=s,stdout=(out/'OWNER_OUT.txt').open('x',encoding='utf8'),stderr=(out/'OWNER_ERR.txt').open('x',encoding='utf8'),memory_limit=536870912)
        result['job']={'name':name,'launcher_pid':owner.pid,'limit_bytes':536870912}
        end=time.monotonic()+90
        while time.monotonic()<end:
            st=db.get_meta('owner')
            if st and st.get('running')and dt.datetime.fromisoformat(st['wall_utc']).timestamp()>=launch:result['owner_initial']=st;break
            if owner.poll()is not None:raise RuntimeError('Owner exited before ready')
            time.sleep(.1)
        else:raise TimeoutError('Owner readiness')
        result['resume']=ctl('resume','reanudar');origin=time.monotonic();last_sample=-10
        for event in proto['events']:
            target=event.get('at_seconds',0)
            while time.monotonic()-origin<target:
                if time.monotonic()-origin-last_sample>=10:
                    result['owner_samples'].append({'seconds':time.monotonic()-origin,'owner':db.get_meta('owner'),'resources':pc.job_resources(job)});last_sample=time.monotonic()-origin
                if owner.poll()is not None:raise RuntimeError('Single owner lost')
                time.sleep(.1)
            if 'await_existing'in event:
                if event['await_existing']not in[x['id']for x in expected]:raise ValueError('Only prospectively declared exact inherited work may be awaited')
                result['records'][event['await_existing']+'_parsed']=wait(event['await_existing'])
            else:result['records'][prefix+event['id']+'_parsed']=submit(prefix+event['id'],event['payload'])
        while time.monotonic()-origin<proto.get('enabled_seconds',0):
            if time.monotonic()-origin-last_sample>=10:
                st=db.get_meta('owner');result['owner_samples'].append({'seconds':time.monotonic()-origin,'owner':st,'resources':pc.job_resources(job)});last_sample=time.monotonic()-origin
                if st.get('paused')or not st.get('running'):raise RuntimeError('Single owner paused/exited unexpectedly')
            if owner.poll()is not None:raise RuntimeError('Single owner lost')
            time.sleep(.1)
        result['enabled_seconds']=time.monotonic()-origin;result['pause']=ctl('pause','pausar')
        for event in proto.get('pending_after_pause',[]):
            identifier=prefix+event['id'];reply=db.put(identifier,event['payload']);emit({'id':identifier,'payload':event['payload'],'admission':reply,'purpose':'preserved_pending_after_pause_no_material_execution'})
            if reply.get('admission')!='queued':raise ValueError('No replay of pending work')
        result['pending_before_export']=db.outstanding();result['export']=ctl('export','exportar');result['stop']=ctl('stop','detener');owner.wait(timeout=90)
    except Exception as e:
        result['error']={'type':type(e).__name__,'detail':str(e)}
        if owner and owner.poll()is None:
            try:result['emergency_stop']=ctl('emergency_stop','detener');owner.wait(timeout=90)
            except Exception as x:result['stop_error']=str(x)
    finally:
        if job is not None:
            end=time.monotonic()+5;res=pc.job_resources(job)
            while owner.poll()is not None and res.get('job_active_processes',0)and time.monotonic()<end:time.sleep(.02);res=pc.job_resources(job)
            result['job_before_cleanup']=res
            if owner.poll()is None or res.get('job_active_processes',0):pc.terminate_job(job,125);result['forced_own_job_close']=True;owner.wait(timeout=30)
            result['job_final']=pc.job_resources(job);pc.close_job(job)
        result['owner_final']=db.get_meta('owner');result['pending']=db.outstanding();final=read(card);result['final']={k:final.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')};result['host_seconds']=time.monotonic()-began
        result['sources_unchanged']=all(sha(s/r['file'])==r['sha256']for r in sources);result['owner_returncode']=None if owner is None else owner.poll()
        log.close()
        with gzip.GzipFile(filename=str(out/'REGISTROS_VENTANA.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
        write(out/'RESUMEN.json',{k:v for k,v in result.items()if k not in('records','sources','owner_samples')})
    print(json.dumps({'out':str(out),'error':result.get('error'),'final':result['final'],'seconds':result.get('enabled_seconds'),'sources_unchanged':result['sources_unchanged']},ensure_ascii=False))
    return bool(result.get('error'))
if __name__=='__main__':raise SystemExit(main())
