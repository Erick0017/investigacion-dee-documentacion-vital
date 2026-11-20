"""Run one explicit same-ID movement/promotion helper in a 512 MiB Job.

The exact decision is separately validated and reviewed before this call.
Only the existing pi11_adoptar_R01.py may run. No retry/rollback/kill of a
live or uncertain operation. Administrative loads advance zero Native ticks.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,importlib.util,json,os,subprocess,sys,time
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';PY=C/'motor/python313/python.exe'
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)
def write(p,v):
    with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--phase',choices=('prepare-move','adopt'),required=True);ap.add_argument('--decision',type=Path,required=True);ap.add_argument('--decision-sha256',required=True);ap.add_argument('--process-proof',type=Path,required=True);ap.add_argument('--reopening-proof',type=Path);ap.add_argument('--ejecutar',action='store_true');a=ap.parse_args()
    helper=H/'pi11_adoptar_R01.py';decision=a.decision.resolve(strict=True);need(decision.is_relative_to(P.resolve())and sha(decision)==a.decision_sha256,'Exact local decision CAS');ast.parse(helper.read_bytes());proofpath=P/'control'/('PI11_ADMIN_'+a.phase.upper().replace('-','_')+'_JOB_R01.json');expected=P/'control'/('PREPARACION_TRASLADO_PRODUCTO_PI11_R01.json'if a.phase=='prepare-move'else'ADOPCION_PRODUCTO_PI11_R01.json')
    command=[str(PY),'-I','-B','-X','utf8',str(helper),'--'+a.phase,'--decision',str(decision),'--decision-sha256',a.decision_sha256,'--process-proof',str(a.process_proof.resolve(strict=True))]
    if a.phase=='adopt':need(a.reopening_proof is not None,'Exact actual reopening0 proof');command+=['--reopening-proof',str(a.reopening_proof.resolve(strict=True))]
    if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','command':command,'memory_limit_bytes':536870912,'new_Native_ticks':0}));return
    need(Path(sys.executable).resolve()==PY.resolve(),'Official Python');budget=read(P/'REGISTRO_CAMPANA.json')['budget'];need(datetime.now(timezone.utc)<datetime.fromisoformat(budget['new_experimental_uses_cutoff_utc']).astimezone(timezone.utc),'Native cutoff reached')
    marker=P/'PI11_ROOT_NATIVE_WRITER.lock';need(not marker.exists()and not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists()and not proofpath.exists()and not expected.exists(),'No overlapping/repeated administrative phase')
    card=read(S/'estado/vidas'/PARENT/'VIDA.json');protected=[S/'estado/vidas'/PARENT/'VIDA.json',S/card['snapshot']];before={str(p):sha(p)for p in protected};source_system=Path(read(decision)['source_system']);sys.path.insert(0,str(source_system));from app import process_control as pc
    sp=importlib.util.spec_from_file_location('PI11_admin_closed_guard',H/'comprobar_proceso_PI11_R01.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
    write(marker,{'pid':os.getpid(),'life_id':MAIN,'phase':'ADMIN_'+a.phase,'new_Native_ticks':0});out=P/'ensayos'/('PI11_ADMIN_'+a.phase.upper().replace('-','_')+'_R01.stdout.txt');err=out.with_name(out.name.replace('.stdout.','.stderr.'));samples=[];proc=job=None;closed_idle=False;started=time.monotonic();error=None
    try:
        with out.open('x',encoding='utf8')as stdout,err.open('x',encoding='utf8')as stderr:
            proc,job,name=pc.spawn_owned(command,cwd=P,stdout=stdout,stderr=stderr,memory_limit=536870912);last=-5
            while True:
                resources=pc.job_resources(job)
                if time.monotonic()-last>=3:samples.append({'utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,**resources});last=time.monotonic()
                code=proc.poll();active=resources.get('job_active_processes',0)
                if code is not None and active==0:break
                if code==0 and active==1 and expected.exists():
                    v=read(expected);need(v.get('phase')==('PREPARED_MOVED_NOT_PROMOTED'if a.phase=='prepare-move'else'COMMITTED')and v.get('life_id')==MAIN,'Actual completed administrative receipt')
                    checks=[g.inspect('PI11_admin_idle_bridge_parent',S,PARENT),g.inspect('PI11_admin_idle_bridge_MAIN',S,MAIN)];need(all(v.get('no_live_affected_writer')for v in checks),'Actual closed queues/state before idle bridge close');pc.close_job(job);job=None;closed_idle=True;break
                time.sleep(.1)
            need(proc.wait(timeout=1)==0,'Administrative helper failed; preserve reached state and receipt')
    except BaseException as exc:error={'type':type(exc).__name__,'detail':str(exc),'automatic_retry':False}
    if proc is not None and proc.poll()is None:
        while proc.poll()is None:
            try:time.sleep(.1)
            except KeyboardInterrupt:pass
    if job is not None:
        # A failed validation is not proof that an owned bridge is idle.
        # Keep the only handle until all members actually exit; never infer
        # that a parent's exit permits terminating an uncertain child.
        while pc.job_resources(job).get('job_active_processes',0)>0:
            try:time.sleep(.1)
            except KeyboardInterrupt:pass
        pc.close_job(job)
    unchanged=before=={p:sha(Path(p))for p in before};need(unchanged,'Original principal card/snapshot changed')
    result={'schema':'DEE.PI11.actual_owned_administrative_phase.R01','phase':a.phase,'command':command,'closed':bool(proc is not None and proc.poll()is not None),'exit_code':None if proc is None else proc.returncode,'error':error,'new_Native_ticks':0,'outer_job_memory_limit_bytes':536870912,'resources':samples,'explicit_closed_idle_bridge_release':closed_idle,'protected_original_unchanged':unchanged,'protected_hashes':before,'actual_phase_receipt':None if not expected.exists()else{'path':str(expected),'sha256':sha(expected)},'stdout':{'path':str(out),'sha256':sha(out)},'stderr':{'path':str(err),'sha256':sha(err)},'automatic_retry':False}
    write(proofpath,result)
    if result['closed']and error is None and marker.exists():marker.unlink()
    print(json.dumps({'proof':str(proofpath),'error':error,'phase_receipt':result['actual_phase_receipt'],'Native_ticks':0}));raise SystemExit(1 if error else 0)
if __name__=='__main__':main()
