"""Root-only one authenticated INFRASTRUCTURE stop of preserved AI attempt01.

No ACK, replay, policy call, Native, queue edit or purge. The already COMPLETED
ASK remains unacknowledged. Root must wait for actual host exit before attempt02.
"""
from pathlib import Path
import argparse,datetime,hashlib,http.client,json,sqlite3,uuid
ROOT=Path(__file__).resolve().parents[1]
SID='2bfcd7d04b9d497481b7a1ff23b596a2';OP='a2ff4f3c9309494aab3367eac9aa5077'
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def safe(p):
 p=Path(p);p=p if p.is_absolute()else ROOT/p;p=p.absolute()
 need(p.is_relative_to(ROOT),'R05 subtree only')
 for q in(p,*p.parents):need(not q.is_symlink()and not(q.exists()and getattr(q.lstat(),'st_file_attributes',0)&1024),'No links')
 return p.resolve()
def inspect(db):
 c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,timeout=3);c.row_factory=sqlite3.Row
 try:
  c.execute('BEGIN');s=c.execute('SELECT *FROM session').fetchone();op=c.execute('SELECT *FROM operation WHERE id=?',(OP,)).fetchone()
  acts=[dict(x)for x in c.execute('SELECT *FROM action')]
  counts={r['status']:r['n']for r in c.execute('SELECT status,count(*)n FROM operation GROUP BY status')}
  tools=c.execute('SELECT count(*)FROM tool_call').fetchone()[0]
  feedback=c.execute("SELECT count(*)FROM operation WHERE kind='feedback'").fetchone()[0];c.rollback()
 finally:c.close()
 need(s and op,'Original session and completed operation required')
 s=dict(s);op=dict(op)
 need(s['id']==SID and s['mode']=='CONVENTIONAL_AI'and s['ticks']==0,'Exact non-Native AI attempt01')
 need(op['kind']=='decision'and op['status']=='COMPLETED'and counts=={'COMPLETED':1},'Only one known completed decision; no pending/uncertain operations')
 need(len(acts)==1 and acts[0]['operation_id']==OP and acts[0]['name']=='ASK_STATION'and acts[0]['acknowledged']==0
      and acts[0]['execution_status']is None and tools==feedback==0,'Original unapplied ASK must remain preserved, no fabricated ACK')
 return dict(session=s,operation=op,actions=acts,counts=counts,tool_calls=tools,feedback_operations=feedback)
def run(a):
 need(a.root_run,'Explicit Root-only operator stop')
 config=safe(a.config);out=safe(a.output)
 need(config==ROOT/'configuracion_privada/conventional_ai_r06.json'and not out.exists()and out.is_relative_to(ROOT/'evidencia'),'Exact attempt01 private config and new evidence output')
 adverse=ROOT/'evidencia/CONVENTIONAL_AI_R06_PERIODO_01/ESTADO_ADVERSO_NO_CONTINUABLE.json'
 need(adverse.is_file(),'Root must first preserve adversarial non-continuable World state')
 cfg=read(config);need(cfg['port']==8895 and cfg['bind']=='127.0.0.1'and cfg['allowControl']is True,'Fixed local comparator endpoint only')
 db=safe(config.parent/cfg['databaseFile']);before=inspect(db)
 need(before['session']['status']=='ACTIVE'and before['session']['phase']=='WAIT_ACK_QUERY','Original waiting phase required')
 out.mkdir();write(out/'BRIDGE_BEFORE.json',before)
 body=dict(apiVersion='RBX01.C02.v1',requestId=uuid.uuid4().hex,sessionId=SID,serverInstanceId=before['session']['server_id'],reason='INFRASTRUCTURE')
 write(out/'STOP_INTENT_ONCE.json',dict(path='/v1/stop',body=body,no_retry=True,ACK_sent=False,Native_calls=0,policy_replayed=False,
      adverse_world_file=str(adverse),adverse_world_sha256=sha(adverse)))
 token=safe(config.parent/cfg['tokenFile']).read_text('ascii').strip();c=http.client.HTTPConnection('127.0.0.1',8895,timeout=15)
 try:
  c.request('POST','/v1/stop',body=json.dumps(body,separators=(',',':')).encode('utf8'),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
  r=c.getresponse();raw=r.read(65537);need(len(raw)<=65536,'Bounded response required');reply=dict(http_status=r.status,body=json.loads(raw))
 except BaseException as error:
  write(out/'STOP_UNKNOWN_PRESERVED.json',dict(error_type=type(error).__name__,no_retry=True));raise
 finally:c.close()
 write(out/'STOP_REPLY.json',reply);need(reply['http_status']==200 and reply['body']['status']=='STOPPED','Stop must be known successful; no retry or fabricated closure')
 after=inspect(db);need(after['session']['status']=='STOPPED'and before['operation']==after['operation']and before['actions']==after['actions'],'Completed operation or unacked action changed')
 write(out/'BRIDGE_AFTER.json',after)
 result=dict(schema='DEE.RBX01.C02.unapplied_AI_attempt_operator_stop.R01',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  status='HTTP_STOPPED_KNOWN_COMPLETED_ASK_STILL_UNACKNOWLEDGED',operation_id=OP,session_id=SID,
  action_and_operation_unchanged=True,Native_calls=0,policy_calls=0,ACK_sent=False,files_purged=0,
  host_exit_not_yet_verified=True,next='Wait original comparator host actual exit and preserved closure. Unacknowledged action means this attempt is NOT a coherent resumable pair. New attempt02 is separate, quota preserved.')
 write(out/'RESULTADO.json',result);return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
 p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 print(json.dumps(run(p.parse_args()),indent=2))
