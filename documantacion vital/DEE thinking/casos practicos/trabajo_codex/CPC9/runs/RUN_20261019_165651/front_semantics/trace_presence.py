"""Passive new-process continuation of exactT10; no repair or new input."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import physical,sha,put

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--until',type=int,default=18);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent.parent/'executed_source'/'src'))
    from presence_count import PresenceCountSession
    from relaciones.contact_cardinality import move
    s=PresenceCountSession.load(a.parent/'T10.deetsnap.gz');rows=[]
    if not 10 <= a.until <= 76:raise ValueError('Trace is strictly before first renewedquery')
    for t in range(10,a.until+1):
        s.run_until(t);q=s.geometry['collector'];candidates=[]
        for x in(-1,0,1):
            site=move(q,(x,0,1),t-10);candidates.append({'initial_heading':x,'site':site,'observation':s.observe(site),'Moore27':[s.observe(move(site,(dx,dy,dz)))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]})
        rows.append({'tick':t,'fixed_candidate_paths':candidates,'physical':physical(s.world)})
    m={'schema':'CPC9.presence_count.passive_path_trace.v1','case':a.out.name,'preparations':0,'forks':0,'continuations':1,'technical_reproduction':1,
       'parent':{'snapshot':'T10.deetsnap.gz','sha256':sha(a.parent/'T10.deetsnap.gz'),'case':a.parent.name},'new_inputs':[],'frames':rows,'requests':s.receipts(),'source_sha256':sha(__file__),
       'coverage':'Three fixed straight candidate paths and Moore27, not unique lineage reconstructed byequalcharge. Exact nativecontinuousworld, passive views only.','status':'MEASURED'}
    put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'end_paths':[(r['initial_heading'],r['observation']['s_reg'],r['observation']['direction'])for r in rows[-1]['fixed_candidate_paths']]}))
