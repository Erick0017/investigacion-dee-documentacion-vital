"""Calibración dirigida de expresión desde huella de presencia no consumidora.
No demuestra copia de valor ni se atribuye a MU_MAIN sin integración.
"""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,json,time
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import save_world_snapshot
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/expresion';OUT.mkdir(parents=True,exist_ok=True)
N=17;D=(8,8,8);P=(9,8,8);E=(8,8,9);V=(0,0,1)
SUPPORT=[(-1,0,0),(0,1,0),(0,-1,0),(1,1,0),(-1,-1,0),(0,1,1),(0,-1,-1)]
def add(p,v,k=1):return tuple((p[i]+k*v[i])%N for i in range(3))
def put(p,x):
    if p.exists():raise FileExistsError('Existing trial protected')
    data=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def run(label,packet=True,probe=True,payload=37,frame=True):
    budget=json.loads((LAB/'PRESUPUESTO.json').read_bytes())
    if time.monotonic()>=budget['block_A_deadline_monotonic']:raise TimeoutError('A budget exhausted')
    placements=[]
    for v in SUPPORT if frame else []:
        a=d.InitialPlacement();a.site=d.Coordinate(*add(D,v));a.raw=d.pack_record(1,0,0,0,0,4);a.clock=0;a.role='Declared fixed zero-load detector anatomy';placements.append(a)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(recipe)
    requests=[]
    def send(name,p,v,val,t):
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*p);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        it=d.InterfaceSpec();it.name=name;it.channel=ch;w.declare_interface(it);rid=w.submit(name,val,t)
        requests.append({'id':int(rid.id),'channel':name,'position':list(p),'direction':list(v),'value':val,'tick':t})
    if packet:send('source.carrier',add(P,V,-1),V,payload,0)
    if probe:send('generic.expression',E,(1,0,0),0,4)
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    rows=[]
    for tick in range(10):
        w.run_until(tick);rows.append({'tick':tick,'detector':obs(D),'pump':obs(E),'fixed_gate':obs(add(E,V,2)),
          'parent_expected_site':list(add(P,V,tick-1)),'parent':obs(add(P,V,tick-1)),
          'roi':[obs(add(D,(dx,dy,dz)))for dx in range(-2,3)for dy in range(-2,3)for dz in range(-2,5)]})
    p=OUT/(label+'.T9.deetsnap.gz');save_world_snapshot(w,p,compress=True)
    result={'label':label,'new_auxiliary_T0':True,'N':N,'packet':packet,'probe':probe,'payload':payload,'frame':frame,
      'rows':rows,'requests':[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests],
      'read_tick':6,'read_site':list(add(E,V,2)),'raw_reader':'Active SEM1 pure+Z only; no packet/probe truth supplied to decoder',
      'snapshot':{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    put(OUT/(label+'.json.gz'),result)
    o=rows[6]['fixed_gate'];print(json.dumps({'case':label,'read':o,'detector':[r['detector']['state']for r in rows]},ensure_ascii=False),flush=True)
def main():
    put(OUT/'PROTOCOLO_TAP_EXPRESION_A01.json',{'fixed_utc':datetime.now(timezone.utc).isoformat(),
      'question':'Can a prepared non-consuming presence trace steer a later generic zero-load pump into a material expression?',
      'support':SUPPORT,'source_tick':0,'generic_pump_tick':4,'fixed_read_tick':6,'gate':list(add(E,V,2)),
      'controls':'No packet, no pump, no frame, second payload; compare exact parent RAW at its expected route, not just expression',
      'scope':'Auxiliary calibration; not copying scalar content, semantic memory or MAIN skill'})
    run('MU_TAP_EXPR_A01_FULL');run('MU_TAP_EXPR_A01_NO_PACKET',packet=False);run('MU_TAP_EXPR_A01_NO_PUMP',probe=False);run('MU_TAP_EXPR_A01_NO_FRAME',frame=False);run('MU_TAP_EXPR_A01_PAYLOAD53',payload=53)
if __name__=='__main__':main()
