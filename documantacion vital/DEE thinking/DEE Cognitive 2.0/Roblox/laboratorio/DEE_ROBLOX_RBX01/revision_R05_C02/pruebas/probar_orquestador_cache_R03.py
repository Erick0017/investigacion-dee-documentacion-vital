"""Static delta verification plus cached observer fixtures; no Native/MCP."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'control/orquestar_C02_R02.py';b=ROOT/'control/orquestar_C02_R03.py'
old="no_idle=load('control/verificar_no_idle_C02_R04.py','_C02_bounded_cached_observer_R04')"
new="no_idle=load('control/preparar_recuperacion_cache_C02_R05.py','_C02_bounded_fresh_cache_observer_R05')"
x=a.read_text('utf8');y=b.read_text('utf8')
assert x.count(old)==1 and y.count(new)==1 and x.replace(old,new)==y
ast.parse(y)
assert "CUTOFF = 1794738600"in y and "CUTOFF - 1800"in y and "CUTOFF - 1890"in y
assert "(maximum,suspension)in((18,6),)"in y
spec=importlib.util.spec_from_file_location('_R03_pure_cache',ROOT/'control/preparar_recuperacion_cache_C02_R05.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
t=[0.0];origin=datetime.datetime(2026,11,15,tzinfo=datetime.timezone.utc)
p=dict(N=67,tick=950523,RAW_sha256='a'*64,clocks_sha256='b'*64)
def reader():return dict(physical=dict(p),idle_ticks=12,C02_host_event_driven=True,running=True,paused=t[0]<1,host_elapsed_seconds=t[0],wall_utc=(origin+datetime.timedelta(seconds=t[0])).isoformat())
def sleep(dt):t[0]+=dt
r=m.observe(reader,lambda:True,p,5,clock=lambda:t[0],sleep=sleep,utcnow=lambda:origin+datetime.timedelta(seconds=t[0]))
assert r['passed']and r['initial']['paused']is True and r['before']['paused']is False and r['seconds']>=6
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report=dict(schema='DEE.RBX01.C02.orchestrator_R03.offline_verification',checks=4,passed=True,Native_actions=0,MCP_calls=0,HTTP_requests=0,
            only_change='Cached observer load R04 to R05; all caller fields remain compatible',
            hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(a,b)},observer_result=r)
out=ROOT/'pruebas'/('ORQUESTADOR_CACHE_R03_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(out)
