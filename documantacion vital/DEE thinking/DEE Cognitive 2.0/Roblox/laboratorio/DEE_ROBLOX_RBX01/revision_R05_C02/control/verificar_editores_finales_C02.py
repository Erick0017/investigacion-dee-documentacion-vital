"""Read-only prerequisites for closing two finished experimental Studio editors.

Never closes a process or calls Native/MCP/HTTP/model APIs. Requires final18
Worlds, closed Native/policy writers, settled exact bridge sessions and a recent
Root-preserved MCP Edit marker. No assumption that today's active run is closed.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02'
FP='562d277322ab2a2094bc34009aad03b352d151b2865f4843965e6eb1bc6964d7'
TARGETS={13064:dict(file='DEE_RBX01_C02_R02.rbxlx',creation_filetime=134392045744396167,start_utc='2026-11-15T08:22:54.4396167Z'),
         7820:dict(file='DEE_RBX01_C02_R02_PROGRAMMED.rbxlx',creation_filetime=134392069521419811,start_utc='2026-11-15T09:02:32.1419811Z')}
def load(path,name):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def need(ok,message):
 if not ok:raise RuntimeError(message)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(p):
 p=Path(p);p=(p if p.is_absolute()else ROOT/p).absolute()
 need(p.is_relative_to(ROOT),'R05 paths only')
 for q in(p,*p.parents):need(not q.is_symlink()and not(q.exists()and getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked paths')
 return p.resolve()
def final_world(world,life,tick):
 need(world.get('schema')=='DEE.RBX01.C02.world_checkpoint.v1'and world.get('world_id')=='RBX01_R05_C02_R02'and world.get('scenario_sha256')==FP,'Exact final R02 World required')
 need(world.get('native_life_id')==life and world.get('native_tick')==tick and world.get('S',{}).get('nativeTick')==tick,'World life/tick identity mismatch')
 b=world.get('boundary',{});s=world.get('S',{})
 need(b.get('completed_opportunities')==s.get('completedCycles')==s.get('cycle')==18 and b.get('next_opportunity')==19,'All18 completed opportunities required')
 need(b.get('phase')=='BOUNDARY'and b.get('native_phase')=='IDLE'and b.get('uncertain')is False and b.get('pending_action')is None and b.get('pending_operation')is None,'Settled final World boundary required')
 need(isinstance(world.get('events'),list)and len(world['events'])>0 and isinstance(world.get('pose_trace'),list)and len(world['pose_trace'])>0
      and len(world.get('body_pose',[]))==12 and len(world.get('physical',{}).get('parts',[]))>0,'Complete observed World/events/poses/geometry required')
 return b
def bridge_final(u,config,world):
 c=read(ROOT/'configuracion_privada'/config);db=safe(ROOT/'configuracion_privada'/c['databaseFile']);s=u.bridge_read(db)
 need(s and s['session']and s['session']['status']=='STOPPED'and s['feedback_operations_completed']==18,'Full horizon closed transport required')
 need(s['pending']==s['uncertain']==s['unacknowledged_actions']==s['unacknowledged_tools']==0,'Pending/uncertain final bridge state')
 need(s['session']['id']==world['bridge']['session_id']and s['session']['server_id']==world['bridge']['server_id'],'Final World/bridge logical identity mismatch')
 return dict(database=str(db),session=s['session'],completed_cycles=18,final_feedback_operations_completed=s['feedback_operations_completed'],
             last_suspended_boundary=s['boundary'],pending=0,uncertain=0)
def verify(a):
 need(a.root_run,'Explicit Root-only precondition check')
 u=load('control/orquestar_C02_R04.py','_final_editor_safe_util')
 pid=load('control/adjuntar_propietario_sin_material_C02_R06.py','_final_editor_process_identity')
 comp=load('control/orquestar_comparador_C02_R04.py','_final_editor_comparator')
 marker=safe(a.edit_proof);edit=read(marker)
 need(edit.get('schema')=='DEE.RBX01.C02.final_editors_edit_proof.R01','Root MCP Edit proof marker required')
 need(edit.get('all_unique_state_preserved')is True and edit.get('no_save_required')is True,'Root must confirm all unique state is preserved and no editor save is needed')
 stamp=datetime.datetime.fromisoformat(edit['captured_utc'].replace('Z','+00:00'))
 age=(datetime.datetime.now(datetime.timezone.utc)-stamp).total_seconds();need(0<=age<=600,'Edit proof must be recent within600s')
 entries=edit.get('studios',[]);need({x.get('pid')for x in entries}==set(TARGETS)and len(entries)==2,'Exactly the two finished editors required')
 manifest=read(ROOT/'protocolo/FUENTES_CONGELADAS_EVALUACION_R03.json');preserved={str(marker):sha(marker)}
 for row in entries:
  target=TARGETS[row['pid']];need(row.get('mode')=='Edit'and row.get('file')==target['file']and row.get('creation_filetime')==target['creation_filetime'],'Exact Root Edit/start identity mismatch')
  mcp=safe(row['mcp_report']);need(sha(mcp)==row['mcp_report_sha256'],'MCP evidence bytes mismatch');preserved[str(mcp)]=sha(mcp)
  scene=safe(ROOT/'mundo'/target['file']);role='LIVE_NATIVE'if row['pid']==13064 else'PROGRAMMED'
  need(sha(scene)==manifest['scenes'][role]['sha256'],'Frozen scene changed');preserved[str(scene)]=sha(scene)
 nroot=ROOT/'native/MAIN_R02';nproof_path=ROOT/'evidencia/MAIN_R02_PERIODO_02/SOURCE_OWNER_CLOSED.json';nw_path=ROOT/'evidencia/MAIN_R02_PERIODO_02/WORLD_FINAL.json'
 nproof=read(nproof_path);status=nproof.get('source_journal_event',{}).get('final_status',{})
 need(nproof.get('lifeId')==LIFE and nproof.get('ownerClosed')is True and nproof.get('writerDrained')is True and nproof.get('exit_code')==0
      and nproof.get('source_journal_event',{}).get('exit_code')==0 and status.get('running')is False and status.get('uncertain_external_result')is False,'Actual final Native closure required')
 owner_pid=nproof['source_journal_event']['pid'];need(not pid.alive(owner_pid),'Native child PID is still alive; no editor close')
 card=read(nroot/'sistema/estado/vidas'/LIFE/'VIDA.json');nw=read(nw_path);final_world(nw,LIFE,card['physical']['tick'])
 need(all(status.get('physical',{}).get(k)==card['physical'].get(k)for k in('N','tick','RAW_sha256','clocks_sha256')),'Final Native close and saved card mismatch')
 meta=u.owner_meta(nroot,LIFE);need(meta.get('running')is False and meta.get('uncertain_external_result')is False and meta.get('pid')==owner_pid,'Native cached owner is live/changed/uncertain')
 need(not(nroot/'sistema/estado/locks'/(LIFE+'.lock')).exists(),'Native life lock remains; preserve editor until reconciled')
 db=nroot/'sistema/estado/servicios_persistentes'/LIFE/'cola.sqlite3';con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
 try:
  con.execute('BEGIN');need(con.execute("SELECT count(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'Native queue has pending/uncertain requests');con.rollback()
 finally:con.close()
 native_bridge=bridge_final(u,'main_r02.json',nw)
 poriginal=ROOT/'evidencia/PROGRAMMED_PERIODO_02';pp_path=poriginal/'COMPARATOR_CLOSED.json';pw_path=poriginal/'WORLD_CHECKPOINT.json';pp=read(pp_path);pw=read(pw_path)
 need(pp.get('participant')=='PROGRAMMED'and pp.get('policyWriterClosed')is True and pp.get('writerDrained')is True and pp.get('nativeOwnerOpened')is False and pp.get('nativeTicks')==0
      and pp.get('coherence_error')is None and pp.get('coherence',{}).get('coherent')is True
      and pp['coherence']['completed_cycles']==6 and pp['coherence']['completed_operations']==66,'Final coherent PROGRAMMED closure with preserved six-cycle suspension record required')
 journal=[json.loads(x)for x in(poriginal/'supervisor.jsonl').read_text('utf8').splitlines()if x.strip()];hosts=[x for x in journal if x.get('kind')=='ONE_COMPARATOR_HOST_STARTED']
 need(len(hosts)==1 and not pid.alive(hosts[0]['pid']),'Final PROGRAMMED host is still alive')
 policy=safe(pp['policy_checkpoint']['file']);need(sha(policy)==pp['policy_checkpoint']['sha256']and pp['policy_checkpoint'].get('pending')is None,'Final policy checkpoint changed or pending')
 need(not(policy.parent/'policy_writer.lock').exists()and not policy.with_name(policy.name+'.WRITING').exists(),'Final policy writer/uncertain transaction remains')
 final_world(pw,'COMPARATOR_PROGRAMMED_'+pp['run_id'],0);comp.verify_world(pw,'PROGRAMMED',pp['run_id']);program_bridge=bridge_final(u,'programmed_r02.json',pw)
 runner=load('puente/run_comparador_C02_R02.py','_final_editor_record_recalculation')
 actual_program_db=runner.db_read(Path(program_bridge['database']));policy_record=read(policy)
 coherence=runner.compare_states(actual_program_db,policy_record)
 # Frozen runner reports completed_cycles from boundary, which records the
 # last suspension at6 and is not rewritten by STOPPED at horizon18. Preserve
 # that raw field and verify it as such, independently of actual final progress.
 need(coherence['coherent']is True and coherence['completed_cycles']==6
      and actual_program_db['boundary']['completed_cycles']==6
      and actual_program_db['boundary']['next_opportunity']==7
      and pp['coherence']['session_id']==coherence['session_id']==program_bridge['session']['id']
      and coherence['completed_operations']==pp['coherence']['completed_operations']==len(policy_record['cache'])==len(actual_program_db['operations'])==66
      and coherence['status']=='STOPPED'and program_bridge['final_feedback_operations_completed']==18,
      'Actual final18 feedback/World plus66 policy operations and unchanged last-suspended-boundary6 reconciliation failed')
 for p in(nproof_path,nw_path,pp_path,pw_path,policy):preserved[str(p)]=sha(p)
 return dict(schema='DEE.RBX01.C02.final_editor_close_prerequisites.R01',verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             all18_closed_and_exported=True,targets=TARGETS,preserved_hashes=preserved,native_life=LIFE,native_tick=nw['native_tick'],
             native_owner_pid_closed=owner_pid,programmed_host_pid_closed=hosts[0]['pid'],native_bridge=native_bridge,programmed_bridge=program_bridge,
             programmed_progress_interpretation=dict(final_World_completed_cycles=18,final_World_next_opportunity=19,
              final_feedback_operations_completed=18,completed_policy_operations=66,last_suspended_boundary_cycles=6,
              last_suspended_boundary_next_opportunity=7,frozen_runner_raw_coherence=coherence,
              erratum='Frozen runner coherence.completed_cycles reads last suspended boundary, not final horizon progress. No original closure, runner or policy was rewritten.'),
             Native_calls=0,MCP_calls=0,HTTP_calls=0,process_close_calls=0)
def parser():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True);p.add_argument('--edit-proof',type=Path,required=True);return p
if __name__=='__main__':print(json.dumps(verify(parser().parse_args()),indent=2))
