"""All-bank reference cut/sham or exact restoration, never returned to MAIN."""
import argparse,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import put,physical,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--mode',choices=('cut','sham','restore'),required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent.parent/'executed_source'/'src'))
    from presence_remote import RemotePresenceSession
    from dee_thinking import _native as d
    parent=RemotePresenceSession.load(a.parent/'T23.deetsnap.gz');reference=json.loads((a.parent/'MEASUREMENTS.json').read_text(encoding='utf8'));before=physical(parent.world);interventions=[]
    if a.mode=='restore':s=parent
    else:
        edits=[]
        for b in parent.geometry['branches']:
            q=b['reference_hub23'];obs=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=0 if a.mode=='cut'else int(obs['raw']);e.label='ALL_REMOTE_REFERENCES_'+a.mode.upper();edits.append(e);interventions.append({'site':q,'before':obs,'requested_RAW':str(e.raw),'clock_edit':None})
        s=RemotePresenceSession(parent.world.diagnostic_fork(edits,True),parent.geometry,deepcopy(parent.requests))
    frames=[]
    for tick in(23,24,88,89,90,91,100,103,155,156,157,158,167,170,222,223,224,225):
        frame=s.run_until(tick);frame['physical']=physical(s.world);frames.append(frame)
    expected=next(f['physical']for f in reference['frames']if f['tick']==225)
    m={'schema':'CPC9.presence_remote.causal_restore.v1','id':a.out.name,'mode':a.mode,'preparations':0,'forks':int(a.mode!='restore'),'continuations':int(a.mode=='restore'),
       'parent':{'case':a.parent.name,'snapshot':'T23.deetsnap.gz','sha256':sha(a.parent/'T23.deetsnap.gz'),'primary_sha256':sha(a.parent/'MEASUREMENTS.json')},'interventions':interventions,'new_inputs':[],
       'parent_before':before,'parent_after':physical(parent.world),'parent_unchanged_for_fork':a.mode=='restore'or before==physical(parent.world),
       'frames':frames,'geometry':s.geometry,'requests':s.receipts(),'source_sha256':sha(__file__),
       'final_physical_equal_reference':physical(s.world)==expected,'receipts_equal_reference':s.receipts()==reference['requests'],'status':'MEASURED'}
    path=a.out/'T225.deetsnap.gz';m['snapshot']={'path':path.name,'storage':s.save(path),'sha256':sha(path)};put(a.out/'MEASUREMENTS.json',m)
    print(json.dumps({'id':a.out.name,'mode':a.mode,'physical_equal_reference':m['final_physical_equal_reference'],'receipts_equal_reference':m['receipts_equal_reference'],'responses':{str(f['tick']):[(r['heading'],r['output']['direction'],r['output']['s_reg'])for r in f['remote']]for f in frames if f['tick']in(90,157,224)}}),flush=True)
    if a.mode!='cut'and not(m['final_physical_equal_reference']and m['receipts_equal_reference']):raise AssertionError('Exactsham/restore mismatch')


if __name__=='__main__':main()
