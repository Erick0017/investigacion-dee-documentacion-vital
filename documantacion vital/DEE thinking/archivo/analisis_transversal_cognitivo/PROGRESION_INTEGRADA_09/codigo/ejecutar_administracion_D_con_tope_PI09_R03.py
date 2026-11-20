"""Root-only512MiB owned job for conditional administrative Store phases.
No Native import in this supervisor. Default is a plan. A timeout is logged
and kept under supervision; it never silently kills an uncertain moving world.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sys,time,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';SYSTEM=C/'sistema';PY=C/'motor/python313/python.exe';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';LIMIT=512*1024*1024
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(path,value):
 temporary=path.with_name(path.name+'.WRITING')
 with temporary.open('w',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temporary,path)
def successful_state(a):
 path=P/'control'/('PREPARACION_TRASLADO_D_PRODUCTO_PI09.json'if a.accion=='preparar'else'ADOPCION_D_PRODUCTO_PI09.json')
 if not path.is_file():return None
 proof=json.loads(path.read_text('utf-8-sig'))
 if proof.get('life_id')!=LIFE or proof.get('phase')not in('PREPARED_MOVED_NOT_PROMOTED','COMMITTED')or proof.get('comparison',{}).get('complete_Native_prefix_equal')is not True:return None
 if proof.get('new_ticks',proof.get('new_ticks_for_movement_mapping_promotion'))!=0:return None
 for system,life in((SYSTEM,LIFE),(SYSTEM,'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01')):
  card=system/'estado/vidas'/life/'VIDA.json'
  if not card.is_file():return None
  value=json.loads(card.read_text('utf-8-sig'));world=value['world_id'];db=system/'estado/servicios_persistentes'/world/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
  if(wal.exists()and wal.stat().st_size)or(system/'estado/locks'/(world+'.lock')).exists()or(card.parent/'FUTURO_INTERRUMPIDO.json').exists():return None
  con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
  try:
   row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else{};pending=con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]
   if owner.get('running')is not False or pending:return None
  finally:con.close()
 return {'path':str(path),'sha256':sha(path),'coherent_saved_state_and_no_pending_or_writer':True}

def _run_owned(a):
 script=P/'codigo/incorporar_D_PI09_misma_identidad_R03.py'
 command=[str(PY),'-I','-B','-X','utf8',str(script),'--prepare-move'if a.accion=='preparar'else'--adopt','--decision',str(a.decision.resolve(strict=True)),'--process-proof',str(a.process_proof.resolve(strict=True))]
 if a.accion=='adoptar':
  if a.reopening_proof is None:raise ValueError('Actual product reopening witness required')
  command+=['--reopening-proof',str(a.reopening_proof.resolve(strict=True))]
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','command':command,'owned_job_memory_limit':LIMIT,'NativeRuntime_opened':False,'Native_inputs':0,'tick_advance_requested':0}));return
 if not 30<=a.horizonte_segundos<=1800:raise ValueError('Prospective finite administrative horizon30..1800sec required')
 output=P/'control'/('ADMINISTRACION_D_'+a.accion.upper()+'_512M_PI09_R03.json');stdout=output.with_suffix('.stdout.txt');stderr=output.with_suffix('.stderr.txt')
 if any(path.exists()for path in(output,stdout,stderr)):raise FileExistsError('Existing administration preserved; no automatic repeat')
 sys.path.insert(0,str(SYSTEM));from app import process_control as pc
 started=time.monotonic();samples=[];timed_out=False;interrupted=False;handle=None;proc=None;cleanup=None
 base={'schema':'DEE.PI09.D.owned_admin512.R03','phase':a.accion,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'script_sha256':sha(script),'supervisor_sha256':sha(Path(__file__)),'memory_limit_bytes':LIMIT,'Native_threads_environment':1,'tick_advance_requested':0,'scope':'Existing administrative load/save/promote only. No cognitive input; the actual official subprocess and all descendants are bounded by this job.'}
 with stdout.open('x',encoding='utf8')as out,stderr.open('x',encoding='utf8')as err:
  proc,handle,name=pc.spawn_owned(command,cwd=str(P),stdout=out,stderr=err,memory_limit=LIMIT);base.update(pid=proc.pid,job_name=name)
  record(output,{**base,'status':'RUNNING'})
  while True:
   try:
    sample={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,'process_exit_code':proc.poll(),**pc.job_resources(handle)};samples.append(sample)
    active=sample.get('job_active_processes')
    if proc.poll()is not None and active==0:break
    if proc.poll()==0 and active==1 and not timed_out and not interrupted:
     saved=successful_state(a)
     if saved:
      cleanup={'kind':'EXPLICIT_SUCCESSFUL_ADMIN_JOB_HANDLE_CLOSE','root_exit_code':0,'residual_owned_processes_before_close':1,'saved_state_witness':saved,'mechanism':'KILL_ON_JOB_CLOSE may stop this owned idle bridge; not a cognitive action or an unlogged kill.','only_after_successful_saved_state_no_pending_no_writer':True}
      record(output,{**base,'status':'CLOSING_SUCCESSFUL_OWNED_IDLE_BRIDGE_EXPLICITLY','cleanup':cleanup,'samples':samples,'automatic_retry':False})
      pc.close_job(handle);handle=None
      break
    if not timed_out and sample['elapsed_seconds']>a.horizonte_segundos:
     timed_out=True;record(output,{**base,'status':'ADMINISTRATIVE_HORIZON_EXCEEDED_LIVE_JOB_PRESERVED','samples':samples,'automatic_kill':False,'automatic_retry':False,'next':'Root must inspect this exact owned job. Supervisor keeps its handle; no new admin/Native phase may start.'})
     print(json.dumps({'administrative_timeout_preserved':str(output),'pid':proc.pid,'job':name,'automatic_kill':False}),flush=True)
    time.sleep(.5)
   except KeyboardInterrupt:
    interrupted=True;record(output,{**base,'status':'ROOT_INTERRUPTION_LIVE_JOB_PRESERVED','samples':samples,'automatic_kill':False,'automatic_retry':False});print(json.dumps({'root_interruption_preserved':str(output),'pid':proc.pid,'job':name,'automatic_kill':False}),flush=True)
  exitcode=proc.wait(timeout=1)
  if handle is not None:
   last=pc.job_resources(handle)
   if last.get('job_active_processes')!=0:raise RuntimeError('Residual uncertain job process remains; preserve supervision')
   pc.close_job(handle);handle=None
  else:last={'job_handle_closed_after_structured_success':True,'residual_bridge_cleanup_explicitly_recorded':True}

 final={**base,'status':'COMPLETED'if exitcode==0 and not timed_out and not interrupted else'FAILED_OR_LIMIT_PRESERVED','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':exitcode,'elapsed_seconds':time.monotonic()-started,'samples':samples,'last_job_resources':last,'root_process_exited':True,'all_owned_processes_exited_naturally':cleanup is None,'job_handle_closed_only_after_active0':cleanup is None,'explicit_successful_idle_bridge_cleanup':cleanup,'peak_job_committed_bytes':max(row.get('peak_job_committed_bytes',0)for row in samples),'actual_processes_total':max(row.get('job_total_processes',0)for row in samples),'administrative_horizon_exceeded':timed_out,'interrupted':interrupted,'automatic_kill':False,'automatic_retry':False,'stdout':{'path':str(stdout),'bytes':stdout.stat().st_size,'sha256':sha(stdout)},'stderr':{'path':str(stderr),'bytes':stderr.stat().st_size,'sha256':sha(stderr)},'scientific_operation':'No new Native input or tick advance was requested; Native process was opened only by the explicitly authorized child administrative CLI.'}
 final.pop('automatic_kill',None)
 final['unlogged_or_uncertain_job_termination']=False
 final['owned_idle_bridge_may_be_stopped_by_explicit_job_close']=cleanup is not None
 record(output,final);print(json.dumps({'proof':str(output),'sha256':sha(output),'status':final['status'],'exit_code':exitcode,'peak_job_committed_bytes':final['peak_job_committed_bytes'],'root_process_exited':True,'explicit_idle_bridge_cleanup':cleanup is not None}));return exitcode if exitcode else 2 if timed_out or interrupted else 0
def main(a):
 if not a.ejecutar:return _run_owned(a)
 lock=P/'PI09_ROOT_NATIVE_WRITER.lock'
 with lock.open('x',encoding='utf8')as stream:
  json.dump({'schema':'DEE.PI09.Root_owned_admin_writer.v1','pid':os.getpid(),'phase':a.accion,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memory_limit_bytes':LIMIT,'new_native_inputs':0,'no_automatic_stale_lock_removal':True},stream,indent=2);stream.flush();os.fsync(stream.fileno())
 result=_run_owned(a)
 if result==0:lock.unlink()
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--accion',choices=('preparar','adoptar'),required=True);ap.add_argument('--decision',type=Path,required=True);ap.add_argument('--process-proof',type=Path,required=True);ap.add_argument('--reopening-proof',type=Path);ap.add_argument('--horizonte-segundos',type=int,default=900);ap.add_argument('--ejecutar',action='store_true');raise SystemExit(main(ap.parse_args()))
