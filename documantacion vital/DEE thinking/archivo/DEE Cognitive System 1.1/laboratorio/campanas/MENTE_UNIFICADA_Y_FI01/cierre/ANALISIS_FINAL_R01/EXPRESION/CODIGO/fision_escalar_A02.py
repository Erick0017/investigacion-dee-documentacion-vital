"""Nueva revisión: adquisición por encuentro y expresión material no consumidora.
Calibración auxiliar T0; no es aún una memoria semántica de MU_MAIN.
"""
from pathlib import Path
from datetime import datetime, timezone
import gzip, hashlib, json, time
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import save_world_snapshot
HERE=Path(__file__).resolve().parent; LAB=HERE.parent; ROOT=LAB.parents[2]
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/expresion'; OUT.mkdir(parents=True,exist_ok=True)
N=23; E=(11,11,11); V=(0,0,1)
FRAME=[(x,y,0)for x in(-1,1)for y in(-1,1)]+[(0,-1,0),(0,1,0)]
def pos(v,k=1):return tuple((E[i]+v[i]*k)%N for i in range(3))
def put(path,x):
    if path.exists():raise FileExistsError(path)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode()
    path.write_bytes(gzip.compress(b,mtime=0)if path.suffix=='.gz'else b)
def run(label,a=17,b=20,anchor=512,frame=True):
    budget=json.loads((LAB/'PRESUPUESTO.json').read_bytes())
    if time.monotonic()>=budget['block_A_deadline_monotonic']:raise TimeoutError('A closed')
    placements=[]
    for v,value in [(v,0)for v in FRAME if frame]+([((0,0,-1),anchor)]if anchor else[]):
        p=d.InitialPlacement();p.site=d.Coordinate(*pos(v));p.raw=d.pack_record(1,value,0,0,0,4);p.clock=0;p.role='Prepared scalar-expression frame; not acquired answer';placements.append(p)
    recipe=d.OrganizationRecipe.research(N,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(recipe)
    requests=[]
    for name,offset,direction,value in [('experience.left',(-1,0,-1),(1,0,1),a),('experience.right',(1,0,-1),(-1,0,1),b)]:
        if value is None:continue
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*pos(offset));ch.direction=d.Direction(*direction);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        it=d.InterfaceSpec();it.name=name;it.channel=ch;w.declare_interface(it);rid=w.submit(name,value,0)
        requests.append({'id':int(rid.id),'channel':name,'position':list(pos(offset)),'direction':list(direction),'value':value,'tick':0})
    def observe(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    rows=[]
    for t in range(71):
        w.run_until(t)
        rows.append({'tick':t,'memory':observe(E),'fixed_gate':observe(pos(V,2)),
          'axis':[observe(pos(V,k))for k in range(-3,6)],
          'roi':[observe(pos((x,y,z)))for x in range(-3,4)for y in range(-3,4)for z in range(-3,6)]if t in[0,1,2,3,4,5,6,7,10,22,23,24,46,69,70]else []})
    snap=OUT/(label+'.T70.deetsnap.gz');save_world_snapshot(w,snap,compress=True)
    r={'case':label,'N':N,'life':'new auxiliary T0, no imported learned fields','a':a,'b':b,'anchor':anchor,'frame':frame,'requests':[{**x,'receipt':exact_receipt(w.runtime.receipt(x['id']))}for x in requests],
       'rows':rows,'fixed_reader':{'site':list(pos(V,2)),'ticks':[4,10,23,46,69],'rule':'raw scalar value and direction as observed, no target in decoder'},
       'snapshot':{'path':str(snap),'sha256':hashlib.sha256(snap.read_bytes()).hexdigest()},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    put(OUT/(label+'.json.gz'),r)
    print(json.dumps({'case':label,'sample':[{k:x[k]for k in('tick','memory','fixed_gate')}for x in rows if x['tick']in[2,3,4,10,23,46,69,70]]}),flush=True)
def main():
    put(OUT/'PROTOCOLO_FISION_ESCALAR_A02.json',{'fixed_utc':datetime.now(timezone.utc).isoformat(),'N':N,'frame':FRAME,'anchor':512,
      'question':'Can a native encounter of two experiences form a scalar support that expresses material copies while retaining its acquired scalar?',
      'reader':'E+2Z at4,10,23,46,69; active SEM1 pure+Z is a directional expression; acquired scalar is read, not injected by a correcting query',
      'cases':['17+20','18+20','17 only','no experience','no anchor','no frame'],'horizon':70,
      'limits':'Prepared anatomy, scalar aggregation rather than semantic meaning, continuous expression not spontaneous choice; any failure retained'})
    run('MU_FISION_A02_37');run('MU_FISION_A02_38',a=18);run('MU_FISION_A02_SINGLE',b=None);run('MU_FISION_A02_UNTAUGHT',a=None,b=None);run('MU_FISION_A02_NO_ANCHOR',anchor=0);run('MU_FISION_A02_NO_FRAME',frame=False)
if __name__=='__main__':main()
