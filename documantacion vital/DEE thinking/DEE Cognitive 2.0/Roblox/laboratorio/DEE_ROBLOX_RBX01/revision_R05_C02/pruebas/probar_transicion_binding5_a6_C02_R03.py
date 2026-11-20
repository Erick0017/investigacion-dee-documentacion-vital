"""Pure transition fixtures; does not open any real or synthetic SQLite."""
from pathlib import Path
import importlib.util,hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'control/normalizar_y_sellar_comparador_C02_R03.py'
s=importlib.util.spec_from_file_location('_transition_fixture',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old=dict(checkpoint_id='OLD5',checkpoint_sha256='a'*64)
session=dict(status='SUSPENDED_BOUNDARY',phase='READY_QUERY',id='S')
boundary=dict(completed_cycles=6,next_opportunity=7,session_id='S')
audits=[dict(id=2,event='SESSION_RESUMED',detail=dict(checkpointId='OLD5',checkpointSha256='a'*64)),
        dict(id=3,event='SESSION_SUSPENDED_BOUNDARY',detail=dict(completedCycles=6,nextOpportunity=7))]
assert m.verify_transition(old,session,boundary,audits)['resumed']['id']==2
checks=[dict(name='real_order_resumed5_then_suspended6',passed=True)]
for rows in(audits[:1],audits[1:]):
 try:m.verify_transition(old,session,boundary,rows)
 except RuntimeError:checks.append(dict(name='reject_missing_transition_event',passed=True))
 else:raise AssertionError('Missing transition accepted')
text=p.read_text('utf8');assert 'DELETE FROM'not in text and 'UPDATE 'not in text
checks.append(dict(name='wrapper_never_deletes_or_updates_binding',passed=True))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report=dict(schema='DEE.RBX01.C02.binding5to6_transition.offline.R03',checks=checks,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
 Native_calls=0,model_calls=0,MCP_calls=0,SQLite_connections=0)
out=ROOT/'pruebas'/('BINDING5_A6_R03_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
