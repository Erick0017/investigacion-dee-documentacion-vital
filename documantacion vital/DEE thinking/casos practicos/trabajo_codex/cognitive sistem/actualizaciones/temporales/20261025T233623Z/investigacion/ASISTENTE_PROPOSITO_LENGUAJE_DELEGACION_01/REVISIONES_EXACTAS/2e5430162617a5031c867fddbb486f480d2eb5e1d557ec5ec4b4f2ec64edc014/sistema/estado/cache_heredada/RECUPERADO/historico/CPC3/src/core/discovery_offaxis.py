"""Family B: spatially separated renewable readout, finite pre-T0 support."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from discovery_reader import *

def create(extra=((0,2,1),),persistent=False,origin=(15,15,15)):
    r=d.OrganizationRecipe.relational(d.reference_seed_path(),d.BasalHistory.H0,False,d.Coordinate(*origin))
    opts=d.TickOptions();opts.backend=d.Backend.LAZY;opts.threads=1;r.execution=opts
    ps=[]
    for j,off in enumerate(extra):
        p=d.InitialPlacement();p.site=d.Coordinate(*add(origin,off));p.raw=d.pack_record(7000+j,0,0,0,0,4);p.clock=71+j;p.role='finite_initial_reader_support';ps.append(p)
    if persistent:
        p=d.InitialPlacement();p.site=d.Coordinate(*add(origin,(0,3,0)));p.raw=d.pack_record(8000,7,0,-1,0,4);p.clock=73;p.role='reader_source_supported';ps.append(p)
    r.placements=ps;w=d.OrganizationalWorld.create(r);s=w.view('body').spec
    channel(w,'sensor.A',add(xyz(s.a),(0,-1,0)),(0,0,-1));channel(w,'sensor.B',add(xyz(s.b),(0,1,0)),(0,0,1))
    target=add(origin,(0,1,0));inlet=add(origin,(0,3,0));channel(w,'read.renewed',inlet,(0,-1,0))
    return w,target,inlet
def run_one(extra,persistent=False):
    w,target,inlet=create(extra,persistent);rows=[];receipts=[]
    for tick,key in [(32,'A'),(33,'B')]:
        q=w.submit('sensor.'+key,0,tick);w.run_until(tick+1);receipts.append(rec(w.runtime.receipt(q.id)))
    if not persistent:q=w.probe('read.renewed',7,34)
    for t in range(35,43):w.run_until(t);rows.append(panel(w,target))
    if not persistent:receipts.append(rec(w.runtime.receipt(q.id)))
    for t in (50,100,150,162,163,164,260,292,293,390,391,392,553,554,555,782,783,945,946,1000,1032):
        w.run_until(t)
        if t in (163,554,945):
            r=w.submit('sensor.B',0,t);w.advance();receipts.append(rec(w.runtime.receipt(r.id)))
        rows.append(panel(w,target))
    return {'extra':extra,'persistent':persistent,'receipts':receipts,'samples':rows}
if __name__=='__main__':
    root=Path(sys.argv[1]);out=root/'experimentos/continuidad/DISCOVERY_OFFAXIS.json';out.parent.mkdir(parents=True,exist_ok=True);rows=[]
    for extra,persistent in [(((0,2,1),),False),(((0,2,-1),),False),(((0,2,1),),True),(((0,2,-1),),True)]:
        try:r=run_one(extra,persistent);rows.append(r);print(json.dumps({'extra':extra,'persistent':persistent,'states':[(x['tick'],x['delta'],x['output']['active'],x['output']['direction']) for x in r['samples']],'receipts':[x['status'] for x in r['receipts']]},ensure_ascii=True),flush=True)
        except Exception as e:rows.append({'extra':extra,'persistent':persistent,'error':repr(e)});print(repr(e),flush=True)
        out.write_text(json.dumps(rows,indent=2),encoding='utf-8')
