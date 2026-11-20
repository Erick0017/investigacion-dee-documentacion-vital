"""Passive continuation of all fixed remote reference paths, no selector."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import put,physical,sha

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent.parent/'executed_source'/'src'))
    from presence_remote import RemotePresenceSession
    from count_sign.session import move
    s=RemotePresenceSession.load(a.parent/'T23.deetsnap.gz');frames=[]
    for t in range(23,90):
        s.run_until(t);rows=[]
        for b in s.geometry['branches']:
            q=move(b['reference_hub23'],(0,1,0),t-23)
            rows.append({'heading':b['heading'],'site':q,'observation':s.observe(q),
                'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        frames.append({'tick':t,'fixed_reference_paths':rows,'physical':physical(s.world)})
    data={'schema':'CPC9.remote_reference.passive_trace.v1','parent':{'case':a.parent.name,'snapshot':'T23.deetsnap.gz','sha256':sha(a.parent/'T23.deetsnap.gz')},
          'preparations':0,'forks':0,'continuations':1,'technical_reproduction':1,'new_inputs':[],'frames':frames,'requests':s.receipts(),
          'source_sha256':sha(__file__),'coverage':'All3fixed+Yreferencepaths/Moore27 only, no unique genealogicalclaim','status':'MEASURED'}
    put(a.out/'MEASUREMENTS.json',data);print(json.dumps({'case':a.parent.name,'middle':[(f['tick'],f['fixed_reference_paths'][1]['observation']['s_reg'],f['fixed_reference_paths'][1]['observation']['direction'])for f in frames]}),flush=True)
