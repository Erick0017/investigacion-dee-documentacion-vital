"""Synthetic clock/latch tests only: no real wait, HTTP, Native, owner or DB."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
b=load(ROOT/'puente/rbx02_bridge_C02.py','_resume_gate_R04_fixture')
o=load(ROOT/'control/verificar_no_idle_C02_R04.py','_noidle_R04_fixture')
checks=[]
g=b.ResumeBootstrapGate(True,'SUSPENDED_BOUNDARY',100,600,now=0)
assert g.observe(90,now=5)=='AWAIT_EXPLICIT_RESUME'and g.observe(100,now=599)=='AWAIT_EXPLICIT_RESUME';checks.append('Old suspended row and old resume audit do not close or resume new host')
assert g.observe(101,now=599)=='NORMAL'and g.observe(101,now=601)=='NORMAL';checks.append('Only new successful resume audit releases latch permanently')
g=b.ResumeBootstrapGate(True,'SUSPENDED_BOUNDARY',100,600,now=0);assert g.observe(100,now=600)=='RESUME_BOOTSTRAP_TIMEOUT';checks.append('No explicit resume times out at fixed600seconds')
assert b.ResumeBootstrapGate(True,None,0,600,now=0).observe(0,now=1)=='NORMAL';checks.append('Fresh session startup keeps original terminal behavior')
physical={'N':67,'tick':950523,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}
origin=datetime.datetime(2026,11,15,tzinfo=datetime.timezone.utc)
class Clock:
    def __init__(self):self.t=0
    def now(self):return self.t
    def sleep(self,dt):self.t+=dt
    def utc(self):return origin+datetime.timedelta(seconds=self.t)
def trial(publish_after=None,changed=False):
    clock=Clock()
    def reader():
        age=0 if publish_after is None or clock.t<publish_after else clock.t
        p=dict(physical)
        if changed and clock.t>=2:p['tick']+=1
        return {'physical':p,'idle_ticks':138355,'C02_host_event_driven':True,'running':True,'paused':False,
                'host_elapsed_seconds':age,'wall_utc':(origin+datetime.timedelta(seconds=age)).isoformat()}
    return o.observe(reader,lambda:True,physical,5,clock=clock.now,sleep=clock.sleep,utcnow=clock.utc)
r=trial(8);assert r['passed']and r['seconds']==8 and r['before']and r['after'];checks.append('Real cache progress after8seconds passes5second minimum without relaxing physics')
r=trial();assert not r['passed']and r['seconds']==75 and r['before']and r['after']and r['samples'];checks.append('Unchanged cache fails bounded75seconds with both observations retained')
r=trial(8,True);assert not r['passed']and r['seconds']==2 and r['reason']=='PHYSICAL_IDLE_OR_HOST_INVARIANT_CHANGED';checks.append('One physical tick change fails immediately before minimum')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
sources={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()for name in('puente/rbx02_bridge_C02.py','control/orquestar_C02.py','control/verificar_no_idle_C02_R04.py')}
report={'scope':'SYNTHETIC_CLOCK_AND_RESUME_LATCH_ONLY','tests':len(checks),'checks':checks,'source_files_sha256':sources,
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'real_wait_seconds':0,'HTTP_requests':0}
out=ROOT/'pruebas'/('REANUDACION_NO_IDLE_R04_'+stamp+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
