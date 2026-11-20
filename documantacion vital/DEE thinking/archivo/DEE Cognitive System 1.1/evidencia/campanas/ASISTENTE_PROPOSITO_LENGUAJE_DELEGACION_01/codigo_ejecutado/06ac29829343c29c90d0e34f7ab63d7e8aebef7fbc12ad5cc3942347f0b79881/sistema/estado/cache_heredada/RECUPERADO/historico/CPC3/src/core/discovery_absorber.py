"""Family C: fixed pre-T0 off-core absorbers limit native toroidal read traffic."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.entity import Entity,BarrierHabitat,atomic_json,add,xyz
import dee_thinking as d

def create(offsets,origin=(15,15,15)):
    r=d.OrganizationRecipe.relational(d.reference_seed_path(),d.BasalHistory.H0,False,d.Coordinate(*origin));opts=d.TickOptions();opts.backend=d.Backend.LAZY;opts.threads=1;r.execution=opts;ps=[]
    for j,off in enumerate(offsets):
        p=d.InitialPlacement();p.site=d.Coordinate(*add(origin,off));p.raw=d.pack_record(8000+j,0,0,0,0,4);p.clock=100+j;p.role='declared_fixed_native_route_absorber_outside_A_B_Moore';ps.append(p)
    r.placements=ps;w=d.OrganizationalWorld.create(r);spec=w.view('body').spec
    for key,center,off,dr in [('A',spec.a,(0,-1,0),(0,0,-1)),('B',spec.b,(0,1,0),(0,0,1))]:
        i=d.InterfaceSpec();i.name='sensor.'+key;c=d.ChannelSpec();c.name=i.name;c.injection_site=d.Coordinate(*add(xyz(center),off));c.direction=d.Direction(*dr);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True;i.channel=c;w.declare_interface(i)
    return Entity(w,BarrierHabitat(False,80),origin)
def run(offsets,payload,root,ident):
    e=create(offsets);rows=[];e.event_sink=root/'experimentos/continuidad/absorber'/(ident+'.jsonl');e.sense();r=e.world.probe('body.common_query',payload,34);e._advance_to(37);e.reader_primed=e.world.runtime.receipt(r.id).status==d.AdmissionStatus.APPLIED if hasattr(d,'AdmissionStatus') else str(e.world.runtime.receipt(r.id).status)=='applied';rows.append(e.observe())
    for t in (50,100,150,163,164,292,293,554,555,812,813,945,946,1000,1032):
        e._advance_to(t)
        if t in (163,292,554,812,945):e._input('A',t,{'kind':'DECLARED_EXPERIENCE_PROTOCOL','observed_class':'arrival','diagnostic_payload':False})
        rows.append(e.observe())
    out={'id':ident,'offsets':offsets,'payload':payload,'rows':rows,'events':e.events,'operational_forks':0,'interventions_after_t0':'only declared physical experience/probe, no field edits'};atomic_json(root/'experimentos/continuidad/absorber'/(ident+'.json'),out);print(json.dumps({'id':ident,'states':[(x['tick'],x['delta'],x['physical_output']['direction'],x['write_gates']['A']['n_active'],x['write_gates']['B']['n_active']) for x in rows],'receipts':[(x['tick'],x['receipt']['status']) for x in e.events if x['kind']=='EXPERIENCE']},ensure_ascii=True),flush=True)
if __name__=='__main__':
    root=Path(sys.argv[1]);(root/'experimentos/continuidad/absorber').mkdir(parents=True,exist_ok=True)
    for ident,offsets,payload in [('near_zero',[(-1,-2,0),(1,-2,0)],0),('far_zero',[(-2,-3,0),(2,-3,0)],0),('near_seven',[(-1,-2,0),(1,-2,0)],7),('far_seven',[(-2,-3,0),(2,-3,0)],7)]:run(offsets,payload,root,ident)
