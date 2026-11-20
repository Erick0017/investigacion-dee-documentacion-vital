"""Root-only offline maintenance and first seal of a CLOSED comparator pair.

No Native, HTTP, MCP, model or policy decisions. SQLite itself preserves and
checkpoints committed WAL frames; this helper never deletes auxiliary files.
Requires the original exact World, drained policy proof, absent live host,
writer lease, no pending work and no previous checkpoint binding.
"""
from pathlib import Path
import argparse,datetime,importlib.util,json,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def verify_proof(proof,participant,run_id,policy_sha):
 if not(proof.get('schema')=='DEE.RBX01.C02.comparator_closure.v1'and proof.get('status')=='CLOSED'
        and proof.get('participant')==participant and proof.get('run_id')==run_id
        and proof.get('policyWriterClosed')is True and proof.get('writerDrained')is True
        and proof.get('nativeOwnerOpened')is False and proof.get('nativeTicks')==0
        and proof.get('coherence_error')is None and proof.get('coherence',{}).get('coherent')is True
        and proof.get('policy_checkpoint',{}).get('pending')is None
        and proof.get('policy_checkpoint',{}).get('sha256')==policy_sha):
  raise RuntimeError('Exact closed coherent comparator/policy bytes required')
def run(a):
 v=load('control/orquestar_comparador_C02_R04.py','_C02_comparator_closed_seal')
 m=load('control/normalizar_sqlite_cerrado_C02.py','_C02_generic_sqlite_semantics')
 b=load('puente/rbx02_bridge_C02.py','_C02_comparator_offline_lease')
 runner=load('puente/run_comparador_C02_R02.py','_C02_closed_policy_recalculation')
 process=load('control/adjuntar_propietario_sin_material_C02_R06.py','_C02_pid_identity_only')
 need,read,sha,write,safe=v.need,v.read,v.sha,v.write,v.safe
 need(a.root_run,'Explicit Root-only offline maintenance')
 directory,config,world_path,proof_path,original,out=map(safe,(a.policy_directory,a.config,a.world_checkpoint,a.close_proof,a.original_output,a.output))
 need(not out.exists()and out.is_relative_to(ROOT/'evidencia'),'New evidence output only')
 need(world_path==original/'WORLD_CHECKPOINT.json'and proof_path==original/'COMPARATOR_CLOSED.json','Use original preferred World/closure, not an unbound recovery checkpoint')
 proof=read(proof_path);participant=proof['participant'];run_id=proof['run_id']
 need(participant in v.FILES,'Actual comparator only')
 policy=directory/'POLICY_STATE_C02.json';identity=directory/'RUNNER_IDENTITY_C02.json'
 policy_sha=sha(policy);verify_proof(proof,participant,run_id,policy_sha)
 need(not(directory/'policy_writer.lock').exists()and not policy.with_name(policy.name+'.WRITING').exists(),'Policy writer or uncertain write is present')
 journal=[json.loads(x)for x in(original/'supervisor.jsonl').read_text('utf8').splitlines()if x.strip()]
 hosts=[x for x in journal if x.get('kind')=='ONE_COMPARATOR_HOST_STARTED']
 need(len(hosts)==1 and not process.alive(hosts[0]['pid']),'Original sole policy host must have exited')
 old=read(original/'RESULTADO.json');need(old.get('policy_closed')is True and old.get('process_returncode')==0,'Original supervisor must prove clean host exit')
 c=read(config);need(c.get('worldId')==v.WORLD_ID and c.get('port')==8895 and c.get('allowControl')is True and c.get('resumeAllowed')is True,'Exact resumable comparator config')
 database=safe(ROOT/'configuracion_privada'/c['databaseFile']);need(database.parent==ROOT/'configuracion_privada','Explicit private DB only')
 need(Path(proof['database']).resolve()==database and Path(proof['policy_checkpoint']['file']).resolve()==policy,'Closure localizers do not match live files')
 world=read(world_path);v.verify_world(world,participant,run_id)
 need(world['world_id']==v.WORLD_ID and world['bridge']['session_id']==proof['coherence']['session_id'],'Original World/closed policy session mismatch')
 frozen={str(p):sha(p)for p in(world_path,proof_path,policy,identity)}
 out.mkdir();report=dict(schema='DEE.RBX01.C02.closed_comparator_sqlite_and_pair.R01',started_utc=v.utc(),
  participant=participant,run_id=run_id,original_world=str(world_path),original_world_sha256=sha(world_path),
  original_proof=str(proof_path),policy_directory=str(directory),database=str(database),
  Native_calls=0,MCP_calls=0,HTTP_calls=0,model_calls=0,policy_decisions=0,files_deleted_by_script=0,
  frozen_before=frozen,old_host_pid=hosts[0]['pid'],old_host_confirmed_exited=True)
 lease=con=None
 try:
  lease=b.ProcessLease(database)
  report['before_files']=m.files(database)
  before_policy_state=runner.db_read(database)
  report['policy_bridge_coherence_before']=runner.compare_states(before_policy_state,read(policy))
  need(before_policy_state['binding']is None,'Previously bound comparator must be reconciled, never rebound')
  con=sqlite3.connect(str(database),isolation_level=None,timeout=5);con.execute('PRAGMA busy_timeout=5000')
  need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Pre-maintenance quick_check failed')
  before=m.semantics(con)
  need(before['session']['mode']==participant and before['session']['ticks']==0,'Comparator session cannot claim Native ticks')
  need(con.execute('SELECT count(*)FROM checkpoint_binding').fetchone()[0]==0,'Already bound: preserve and reconcile; never create a new binding')
  need(world['bridge']['session_id']==before['session']['id']and world['bridge']['server_id']==before['session']['server_id'],'World and SQLite logical identity mismatch')
  need(world['boundary']['completed_opportunities']==before['boundary']['completed_cycles'],'World and SQLite cursor mismatch')
  backup=out/'BEFORE_COHERENT_BRIDGE.sqlite3';target=sqlite3.connect(backup)
  try:con.backup(target);need(target.execute('PRAGMA quick_check').fetchone()[0]=='ok','Backup integrity failed')
  finally:target.close()
  report.update(before_semantics=before,coherent_backup=dict(file=str(backup),bytes=backup.stat().st_size,sha256=sha(backup)))
  checkpoint=list(con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone());report['wal_checkpoint_result']=checkpoint
  need(checkpoint[0]==0,'Checkpoint busy: preserve, no deletion or forced reader termination')
  need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','Post-maintenance integrity failed')
  after=m.semantics(con);need(before==after,'Scientific table rows changed during maintenance')
  report.update(after_semantics=after,scientific_rows_equal=True)
  con.close();con=None
  report['after_files']=m.files(database)
  for suffix in('-wal','-shm','-journal'):
   p=Path(str(database)+suffix);need(not p.exists()or p.stat().st_size==0,'Auxiliary still held after close; preserve without deletion: '+suffix)
  # Lease must be released before the established binder obtains its own lease.
  lease.close();lease=None
  need(all(sha(Path(path))==digest for path,digest in frozen.items()),'World/policy/proof changed concurrently')
  normalized=dict(c,databaseFile=str(database))
  pair=v.seal_comparator(directory,normalized,world_path,proof,out,runner)
  pack=Path(pair['directory']);manifest=read(pack/'PAIR_COMPARATOR_C02.json')
  for name,row in manifest['members'].items():
   p=pack/name;need(p.is_file()and p.stat().st_size==row['bytes']and sha(p)==row['sha256'],'Final pair member verification failed')
  need(sha(pack/'WORLD_CHECKPOINT.json')==frozen[str(world_path)]and sha(pack/'POLICY_STATE_C02.json')==policy_sha,'Final pair changed original World/policy bytes')
  need(all(sha(Path(path))==digest for path,digest in frozen.items()),'Preserved scientific originals changed after sealing')
  resume=dict(config=str(config),policy_directory=str(directory),participant=participant,run_id=run_id,
   world_checkpoint=pair['world_file'],world_checkpoint_sha256=pair['world_checkpoint_sha256'],
   bound_checkpoint_sha256=pair['bound_checkpoint_sha256'],
   next_opportunity=world['boundary']['next_opportunity'],Native_backup=False,
   command_entry='control/orquestar_comparador_C02_R04.py',
   required_additional_args='--root-run --studio-id <fresh same participant Studio> --expected-place <same frozen filename> --scenario-sha256 <frozen> --output <new evidence>')
  write(out/'RESUMIR_COMPARADOR.json',resume)
  report.update(status='COMPARATOR_CLOSED_CHECKPOINTED_AND_SEALED',pair=pair,resume=resume,
   preservation_frozen_originals=True,binding_metadata_change_declared=True,
   maintenance_scope='All scientific table rows identical during SQLite maintenance. First offline binding is separately declared and verified by established seal_comparator.')
 except BaseException as error:
  report.update(status='OFFLINE_MAINTENANCE_OR_SEAL_INCOMPLETE_PRESERVED',error_type=type(error).__name__,error=str(error));raise
 finally:
  if con is not None:con.close()
  if lease is not None:lease.close()
  report['ended_utc']=v.utc();write(out/'NORMALIZACION_Y_SELLADO_COMPARADOR.json',report)
 return report
def parser():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
 for n in('policy-directory','config','world-checkpoint','close-proof','original-output','output'):p.add_argument('--'+n,type=Path,required=True)
 return p
if __name__=='__main__':print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
