"""Explicit Root-approved successful-job cleanup policy; preserve supervisorR01.
Never close a failed/uncertain live job. Successful coherent root exit may
leave one idle owned bridge; KILL_ON_JOB_CLOSE cleanup is logged explicitly.
"""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;source=H/'ejecutar_administracion_con_tope_PI08.py';target=H/'ejecutar_administracion_con_tope_PI08_R02.py'
if target.exists():raise FileExistsError('Prepared supervisor revision preserved')
s=source.read_text('utf8').replace('import argparse,datetime,hashlib,json,os,sys,time','import argparse,datetime,hashlib,json,os,sys,time,sqlite3').replace("a.accion.upper()+'_512M_PI08_R01.json'","a.accion.upper()+'_512M_PI08_R02.json'")
anchor='def main(a):'
helper='''def successful_state(a):
 path=P/'control'/('PREPARACION_TRASLADO_PRODUCTO_PI08.json'if a.accion=='preparar'else'ADOPCION_PRODUCTO_PI08.json')
 if not path.is_file():return None
 proof=json.loads(path.read_text('utf-8-sig'))
 if proof.get('life_id')!=LIFE or proof.get('phase')not in('PREPARED_MOVED_NOT_PROMOTED','COMMITTED')or proof.get('comparison',{}).get('complete_Native_prefix_equal')is not True:return None
 if proof.get('new_ticks',proof.get('new_ticks_for_movement_mapping_promotion'))!=0:return None
 for system,life in((SYSTEM,LIFE),(SYSTEM,'ECI02_PI03_REPRO_PI04_PI05_MAIN_01')):
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

'''
if s.count(anchor)!=1:raise ValueError('Exact supervisor main required')
s=s.replace(anchor,helper+anchor)
s=s.replace('samples=[];timed_out=False;interrupted=False;handle=None;proc=None','samples=[];timed_out=False;interrupted=False;handle=None;proc=None;cleanup=None')
old="    if proc.poll()is not None and active==0:break"
new="""    if proc.poll()is not None and active==0:break
    if proc.poll()==0 and active==1 and not timed_out and not interrupted:
     saved=successful_state(a)
     if saved:
      cleanup={'kind':'EXPLICIT_SUCCESSFUL_ADMIN_JOB_HANDLE_CLOSE','root_exit_code':0,'residual_owned_processes_before_close':1,'saved_state_witness':saved,'mechanism':'KILL_ON_JOB_CLOSE may stop this owned idle bridge; not a cognitive action or an unlogged kill.','only_after_successful_saved_state_no_pending_no_writer':True}
      record(output,{**base,'status':'CLOSING_SUCCESSFUL_OWNED_IDLE_BRIDGE_EXPLICITLY','cleanup':cleanup,'samples':samples,'automatic_retry':False})
      pc.close_job(handle);handle=None
      break"""
if old not in s:raise ValueError('Exact successful-root loop gate required')
s=s.replace(old,new)
old="  exitcode=proc.wait(timeout=1);last=pc.job_resources(handle)\n  # Close a KILL_ON_JOB_CLOSE handle only after actual zero active processes.\n  if last.get('job_active_processes')!=0:raise RuntimeError('Residual job process unexpectedly remains; preserve supervision')\n  pc.close_job(handle);handle=None"
new="""  exitcode=proc.wait(timeout=1)
  if handle is not None:
   last=pc.job_resources(handle)
   if last.get('job_active_processes')!=0:raise RuntimeError('Residual uncertain job process remains; preserve supervision')
   pc.close_job(handle);handle=None
  else:last={'job_handle_closed_after_structured_success':True,'residual_bridge_cleanup_explicitly_recorded':True}
"""
if old not in s:raise ValueError('Exact job close sequence required')
s=s.replace(old,new).replace("'all_owned_processes_exited':True,'job_handle_closed_only_after_active0':True", "'root_process_exited':True,'all_owned_processes_exited_naturally':cleanup is None,'job_handle_closed_only_after_active0':cleanup is None,'explicit_successful_idle_bridge_cleanup':cleanup")
s=s.replace("'all_owned_processes_exited':True}","'root_process_exited':True,'explicit_idle_bridge_cleanup':cleanup is not None}")
compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
