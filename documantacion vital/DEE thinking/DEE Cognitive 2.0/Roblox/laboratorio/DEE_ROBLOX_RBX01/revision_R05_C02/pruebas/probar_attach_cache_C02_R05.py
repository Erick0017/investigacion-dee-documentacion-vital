"""Offline fixtures; imports only stdlib and the pure cached observer."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'control/preparar_recuperacion_cache_C02_R05.py'
s=importlib.util.spec_from_file_location('_pure_R05_fixture',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
physical=dict(N=67,tick=947395,RAW_sha256='a'*64,clocks_sha256='b'*64)
def case(kind):
 now=[0.0];origin=datetime.datetime(2026,11,15,8,30,tzinfo=datetime.timezone.utc)
 def reader():
  t=now[0];paused=t<2
  row=dict(physical=dict(physical),idle_ticks=138355,C02_host_event_driven=True,
           wall_utc=(origin+datetime.timedelta(seconds=t)).isoformat(),host_elapsed_seconds=t,
           paused=paused,running=True)
  if kind=='physical'and t>=3:row['physical']['tick']+=1
  if kind=='idle'and t>=3:row['idle_ticks']+=1
  if kind=='repaused'and t>=3:row['paused']=True
  if kind=='stale':row['wall_utc']=(origin-datetime.timedelta(seconds=30)).isoformat()
  return row
 def sleep(dt):now[0]+=dt
 r=m.observe(reader,lambda:True,physical,5,clock=lambda:now[0],sleep=sleep,utcnow=lambda:origin+datetime.timedelta(seconds=now[0]))
 return r
good=case('good');assert good['passed']and good['initial']['paused']is True and good['before']['paused']is False
assert good['seconds']>=7 and good['samples'][-1]['active_window_seconds']>=5
tests=[dict(name='stale_paused_initial_full_fresh_window',passed=True,seconds=good['seconds'])]
for kind in('physical','idle','repaused','stale'):
 r=case(kind);assert not r['passed'];tests.append(dict(name=kind,passed=True,reason=r['reason']))
attach=ROOT/'control/adjuntar_propietario_sin_material_C02_R05.py';text=attach.read_text('utf8');tree=ast.parse(text)
assert 'subprocess.Popen'not in text.split('def run(a):')[0]
assert text.count("code=o.client_control('START_NATIVE')")==1
assert text.index("while not(original/'RESULTADO.json').exists()")<text.index("transport.capture_world(mcp,context")
assert "out/'relay.jsonl'"in text and "original/'relay.jsonl'"not in text
tests.append(dict(name='first_start_only_new_relay_export_after_original_completion',passed=True))
for p in(P,attach):ast.parse(p.read_text('utf8'))
report=dict(schema='DEE.RBX01.C02.attach_offline_fixtures.R05',tests=tests,
            source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(P,attach)},
            Native_actions=0,MCP_calls=0,HTTP_requests=0,process_actions=0)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out=ROOT/'pruebas'/('ATTACH_CACHE_R05_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(tests=len(tests),all_passed=True,report=str(out),sha256=report['source_sha256']),indent=2))
