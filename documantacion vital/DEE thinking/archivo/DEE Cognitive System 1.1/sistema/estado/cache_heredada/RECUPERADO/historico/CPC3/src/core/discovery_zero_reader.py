"""Finite payload variation: zero-load physical readout in the same MAIN."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from discovery_reader import *
def run_case(payload,history='AB',origin=(15,15,15)):
    w,target,inlet,dr=make((0,0,0),False,origin);opts=d.TickOptions();opts.backend=d.Backend.LAZY;opts.threads=1;w.runtime.execution_options=opts
    rows=[];receipts=[]
    for tick,key in zip((32,33),history):
        r=w.submit('sensor.'+key,0,tick);w.run_until(tick+1);receipts.append(rec(w.runtime.receipt(r.id)))
    r=w.probe('body.common_query',payload,34);w.run_until(37);receipts.append(rec(w.runtime.receipt(r.id)))
    for t in (37,40,50,100,150,163,164,292,293,554,555,812,813,945,946,1000,1032):
        w.run_until(t)
        if t in (163,292,554,812,945):
            r=w.submit('sensor.'+('B' if history=='AB' else 'A'),0,t);w.advance();receipts.append(rec(w.runtime.receipt(r.id)))
        p=panel(w,target);p['moore']={}
        for key,q in [('A',xyz(w.view('body').spec.a)),('B',xyz(w.view('body').spec.b))]:
            ns=[obs(w.runtime,add(q,(x,y,z))) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1) if (x,y,z)!=(0,0,0)]
            p['moore'][key]={'n_active':sum(n['active'] for n in ns),'neighbors':ns}
        rows.append(p)
    return {'payload':payload,'history':history,'receipts':receipts,'samples':rows}
if __name__=='__main__':
    root=Path(sys.argv[1]);out=root/'experimentos/continuidad/DISCOVERY_ZERO_READER.json';rows=[]
    for payload,history in [(0,'AB'),(0,'BA'),(1,'AB')]:
        r=run_case(payload,history);rows.append(r);out.write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps({'payload':payload,'history':history,'states':[(p['tick'],p['delta'],p['output']['direction'],p['moore']['A']['n_active'],p['moore']['B']['n_active']) for p in r['samples']],'receipts':[q['status'] for q in r['receipts']]},ensure_ascii=True),flush=True)
