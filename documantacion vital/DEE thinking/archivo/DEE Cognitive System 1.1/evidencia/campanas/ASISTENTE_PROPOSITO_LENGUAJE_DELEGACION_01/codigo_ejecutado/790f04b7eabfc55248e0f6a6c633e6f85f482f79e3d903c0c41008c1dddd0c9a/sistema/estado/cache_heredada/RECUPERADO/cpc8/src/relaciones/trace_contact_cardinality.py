"""Passive technical re-observation of the first apparatus, not a new preparation."""
import argparse,hashlib,json,os
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation
from dee_thinking.persistence import load_world_snapshot

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 w,_=load_world_snapshot(a.snapshot,max_bytes=64*1024**2);n=67
 m={'schema':'CPC8R.contact_cardinality.passive_trace.v1','parent_snapshot':str(a.snapshot),'parent_sha256':hashlib.sha256(a.snapshot.read_bytes()).hexdigest(),'preparations':0,'continuations':1,'technical_reobservation':True,'frames':[]}
 for t in range(10,79):
  w.run_until(t);raw=w.runtime.raw_copy(); records=[]
  for i,r in enumerate(raw):
   if r:
    q=d.Coordinate(i//(67*67),(i//67)%67,i%67);o=exact_observation(w.runtime.observe(q))
    if int(o['raw'])!=int(r):raise RuntimeError('Sparse index disagrees with exact native observation')
    if o['active']:records.append(o)
  m['frames'].append({'tick':t,'active_records':records})
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({'frames':len(m['frames']),'active_counts':[len(f['active_records'])for f in m['frames']]}))
