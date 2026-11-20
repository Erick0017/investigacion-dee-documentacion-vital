"""Explicit formed-emission cuts/sham; first count effect and finite restore."""
import argparse,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import put,physical,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--mode',choices=('cut_A','cut_B','cut_both','sham','restore'),required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent.parent/'executed_source'/'src'))
    from presence_count import PresenceCountSession
    from dee_thinking import _native as d
    primary=json.loads((a.parent/'MEASUREMENTS.json').read_text(encoding='utf8'));edits=[];interventions=[]
    if a.mode=='restore':
        snap=a.parent/'T77.deetsnap.gz';s=PresenceCountSession.load(snap);parent=None;before=physical(s.world)
    else:
        snap=a.parent/'T0.deetsnap.gz';parent=PresenceCountSession.load(snap);parent.run_until(7);before=physical(parent.world)
        for n in parent.geometry['normalizers']:
            q=n['center'];obs=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q)
            cut=a.mode=='cut_both'or a.mode=='cut_'+n['name'];e.raw=0 if cut else int(obs['raw']);e.label='NORMALIZED_EMISSION_'+a.mode.upper();edits.append(e)
            interventions.append({'name':n['name'],'site':q,'before':obs,'requested_RAW':str(e.raw),'clock_edit':None})
        w=parent.world.diagnostic_fork(edits,True);s=PresenceCountSession(w,parent.geometry,deepcopy(parent.requests))
    frames=[]
    targets=(77,78,100,103,143,144,145,170,171)if a.mode=='restore'else(7,8,9,10,11,12,77,100,103,144,170,171)
    for tick in targets:
        f=s.run_until(tick);f['physical']=physical(s.world);frames.append(f)
    expected=next(f['physical']for f in primary['frames']if f['tick']==171)
    m={'schema':'CPC9.presence_count.causal_restore.v1','id':a.out.name,'mode':a.mode,'preparations':0,'forks':int(a.mode!='restore'),'continuations':int(a.mode=='restore'),
       'parent':{'case':primary['case']['id'],'snapshot':snap.name,'sha256':sha(snap),'primary_sha256':sha(a.parent/'MEASUREMENTS.json')},'interventions':interventions,
       'new_requests':[],'frames':frames,'requests':s.receipts(),'geometry':s.geometry,'parent_before':before,
       'parent_after':physical(parent.world)if parent is not None else None,'parent_unchanged':parent is None or before==physical(parent.world),
       'final_physical_equal_reference':physical(s.world)==expected,'receipts_equal_reference':s.receipts()==primary['requests'],
       'source_sha256':sha(__file__),'status':'MEASURED'}
    put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':a.out.name,'mode':a.mode,'counts':[(f['tick'],f['collector']['s_reg'],f['collector']['direction'])for f in frames if f['tick']in(10,77,144)],'physical_equal_reference':m['final_physical_equal_reference'],'receipts_equal_reference':m['receipts_equal_reference']}),flush=True)
    if a.mode in('sham','restore')and not(m['final_physical_equal_reference']and m['receipts_equal_reference']):raise AssertionError('Exactsham/restore mismatch')


if __name__=='__main__':main()
