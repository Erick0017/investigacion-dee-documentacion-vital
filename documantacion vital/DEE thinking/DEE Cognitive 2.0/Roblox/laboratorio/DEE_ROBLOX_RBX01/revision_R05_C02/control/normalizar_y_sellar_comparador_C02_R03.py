"""Root-only verification of official bound5 -> resumed -> suspended6.

The frozen /v1/suspend already removes the previous active binding. This wrapper
NEVER deletes or updates it. It preserves pair5/old binding, verifies audit order,
then delegates the same closed normalization/first binding to preserved R02.
No Native, model, HTTP or MCP operation. Rejects every live policy writer.
"""
from pathlib import Path
import argparse,importlib.util,json,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]
def load(name,alias):
 s=importlib.util.spec_from_file_location(alias,ROOT/name);m=importlib.util.module_from_spec(s);sys.modules[alias]=m;s.loader.exec_module(m);return m
def verify_transition(old,session,boundary,audits):
 if not(session['status']=='SUSPENDED_BOUNDARY'and session['phase']=='READY_QUERY'and boundary['completed_cycles']==6
        and boundary['next_opportunity']==7 and boundary['session_id']==session['id']):raise RuntimeError('Exact closed later boundary6 required')
 resumed=[r for r in audits if r['event']=='SESSION_RESUMED'and r['detail'].get('checkpointId')==old['checkpoint_id']and r['detail'].get('checkpointSha256')==old['checkpoint_sha256']]
 if not resumed:raise RuntimeError('Actual previous-bound SESSION_RESUMED missing')
 r=resumed[-1];suspended=[r2 for r2 in audits if r2['id']>r['id']and r2['event']=='SESSION_SUSPENDED_BOUNDARY'
    and r2['detail'].get('completedCycles')==6 and r2['detail'].get('nextOpportunity')==7]
 if not suspended:raise RuntimeError('Later official suspension6 missing')
 return dict(resumed=r,suspended=suspended[-1],binding_retirement='Frozen /v1/suspend legitimately deletes active binding; wrapper never deletes or updates it.')
def pair_check(folder,read,sha,need):
 manifest=read(folder/'PAIR_COMPARATOR_C02.json')
 for name,row in manifest['members'].items():
  p=folder/name;need(p.is_file()and p.stat().st_size==row['bytes']and sha(p)==row['sha256'],'Previous sealed pair member mismatch')
 return manifest
def run(a):
 base=load('control/normalizar_y_sellar_comparador_C02_R02.py','_C02_same_closed_sealer_R02')
 v=load('control/orquestar_comparador_C02_R04.py','_C02_boundary_transition_utils')
 process=load('control/adjuntar_propietario_sin_material_C02_R06.py','_C02_closed_pid_read')
 read,sha,need,safe=v.read,v.sha,v.need,v.safe
 need(a.root_run,'Root-only closed transition verification')
 previous=safe(a.previous_pair);original=safe(a.original_output);output=safe(a.output)
 need(not output.exists(),'Fresh wrapper output only')
 pm=pair_check(previous,read,sha,need);pw=read(previous/'WORLD_CHECKPOINT.json')
 need(pw['boundary']['completed_opportunities']==5 and pw['boundary']['next_opportunity']==6,'Actual preserved previous pair5 required')
 prev_db=previous/'BRIDGE.sqlite3';oldcon=sqlite3.connect(prev_db.as_uri()+'?mode=ro&immutable=1',uri=True);oldcon.row_factory=sqlite3.Row
 try:old=dict(oldcon.execute('SELECT *FROM checkpoint_binding').fetchone())
 finally:oldcon.close()
 need(old['checkpoint_id']==pw['checkpoint_id']and old['checkpoint_sha256']==pm['anchor_sha256'],'Sealed old binding/anchor mismatch')
 proof=read(safe(a.close_proof));need(proof.get('writerDrained')is True and proof.get('policyWriterClosed')is True and proof.get('coherence_error')is None,'Actual coherent closed policy proof required')
 hosts=[json.loads(x)for x in(original/'supervisor.jsonl').read_text('utf8').splitlines()if x.strip()]
 hosts=[r for r in hosts if r.get('kind')=='ONE_COMPARATOR_HOST_STARTED'];need(len(hosts)==1 and not process.alive(hosts[0]['pid']),'Current policy process still alive')
 c=read(safe(a.config));db=safe(ROOT/'configuracion_privada'/c['databaseFile'])
 con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,timeout=3);con.row_factory=sqlite3.Row
 try:
  con.execute('BEGIN');session=dict(con.execute('SELECT *FROM session').fetchone());boundary=dict(con.execute('SELECT *FROM boundary').fetchone())
  binding=con.execute('SELECT *FROM checkpoint_binding').fetchone()
  audits=[dict(r)for r in con.execute("SELECT id,at,event,detail FROM audit WHERE event IN('SESSION_RESUMED','SESSION_SUSPENDED_BOUNDARY')ORDER BY id")]
  for r in audits:r['detail']=json.loads(r['detail'])
  need(con.execute("SELECT count(*)FROM operation WHERE status!='COMPLETED'").fetchone()[0]==0,'Pending/uncertain work preserved')
  need(con.execute("SELECT count(*)FROM action WHERE acknowledged!=1 OR execution_status!='EXECUTED'").fetchone()[0]==0,'Unacked action preserved')
  need(con.execute('SELECT count(*)FROM tool_call WHERE acknowledged!=1').fetchone()[0]==0,'Unacked tool preserved');con.rollback()
 finally:con.close()
 need(session['id']==pw['bridge']['session_id']and session['server_id']==pw['bridge']['server_id'],'Same logical history required')
 transition=verify_transition(old,session,boundary,audits)
 record=dict(schema='DEE.RBX01.C02.official_binding_progression5_to6.R03',previous_pair=str(previous),previous_manifest_sha256=sha(previous/'PAIR_COMPARATOR_C02.json'),
  previous_binding=old,previous_bridge_sha256=sha(prev_db),previous_members=pm['members'],official_transition=transition,
  actual_resume_orchestrator='control/orquestar_comparador_C02_R09.py',
  transport_note='Use R09 ASCII-hex restore; the preserved base R02 may still name historical R08 in its own resume metadata. No historical output is rewritten.',
  wrapper_SQL_deletes=0,wrapper_SQL_updates=0,Native_calls=0,model_calls=0,MCP_calls=0)
 if binding is not None:
  # If the original orchestrator already sealed6 successfully, reuse that pair.
  pack=original/'PAIR_COMPARATOR_C02';current=pair_check(pack,read,sha,need);world=read(pack/'WORLD_CHECKPOINT.json')
  need(world['boundary']['completed_opportunities']==6 and dict(binding)['checkpoint_id']==world['checkpoint_id']and dict(binding)['checkpoint_sha256']==current['anchor_sha256'],'Unexpected existing binding; no overwrite')
  output.mkdir();result=dict(status='EXISTING_OFFICIAL_PAIR6_VERIFIED_REUSED',pair=str(pack),anchor_sha256=current['anchor_sha256'])
 else:
  result=base.run(a)
 pair_check(previous,read,sha,need)
 v.write(output/'VERIFICACION_BINDING5_A6_R03.json',record)
 return dict(result=result,transition_verified=True,previous_pair_preserved=True,manual_rebind_performed=False)
if __name__=='__main__':
 base=load('control/normalizar_y_sellar_comparador_C02_R02.py','_C02_R03_cli_base');p=base.parser();p.add_argument('--previous-pair',type=Path,required=True)
 print(json.dumps(run(p.parse_args()),indent=2))
