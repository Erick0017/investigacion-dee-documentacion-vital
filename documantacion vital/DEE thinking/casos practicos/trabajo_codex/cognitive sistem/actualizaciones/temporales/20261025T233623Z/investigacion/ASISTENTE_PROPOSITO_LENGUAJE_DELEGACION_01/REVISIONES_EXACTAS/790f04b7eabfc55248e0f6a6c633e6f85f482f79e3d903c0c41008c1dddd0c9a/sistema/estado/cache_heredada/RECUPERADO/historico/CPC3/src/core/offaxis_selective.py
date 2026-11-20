"""Bounded family-B refinement: inspect the other fixed inlet, not a new port."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.entity import Entity,BarrierHabitat,atomic_json,receipt
from core.discovery_offaxis import create
def main(root):
    rows=[]
    for history,new in [('AB','A'),('AB',None),('BA','B'),('BA',None)]:
        w,target,inlet=create(((0,2,1),),False);e=Entity(w,BarrierHabitat(history=='AB',80),(15,15,15));samples=[]
        for tick,key in zip((32,33),history):e._input(key,tick,{'kind':'PREDECLARED_HISTORY_EVENT'})
        r=w.probe('read.renewed',7,34);e._advance_to(37)
        for t in (37,50,100,150,162,163,164,170,200):
            e._advance_to(t);p=e.observe();p['offaxis_output']=__import__('core.entity',fromlist=['observation']).observation(w.runtime.observe(__import__('dee_thinking').Coordinate(*target)))
            samples.append(p)
            if t==163 and new:e._input(new,t,{'kind':'FIXED_ALTERNATE_EXISTING_INLET','not_new_sensor':True})
        row={'history':history,'new_event':new,'samples':samples,'events':e.events,'probe_receipt':receipt(w.runtime.receipt(r.id))};rows.append(row);print(json.dumps({'history':history,'new':new,'states':[(p['tick'],p['delta'],p['offaxis_output']['direction'],p['write_gates']['A']['n_active'],p['write_gates']['B']['n_active']) for p in samples],'receipt':[x['receipt']['status'] for x in e.events if x['kind']=='EXPERIENCE']},ensure_ascii=True),flush=True)
        atomic_json(root/'experimentos/continuidad/OFFAXIS_SELECTIVE.json',rows)
if __name__=='__main__':main(Path(sys.argv[1]))
