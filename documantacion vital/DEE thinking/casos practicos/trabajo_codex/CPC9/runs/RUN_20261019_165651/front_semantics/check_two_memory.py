"""Two operand cuts/shams and cross-process continuation; all auditor-owned."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import physical,sha,put


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--mode',choices=('cut','sham','restore'),required=True);p.add_argument('--operand',choices=('R','O'),default='R');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent.parent/'executed_source'/'src'))
    from two_memory import TwoMemorySession
    from dee_thinking import _native as d
    reference=json.loads((a.parent/'MEASUREMENTS.json').read_text(encoding='utf8'));start=time.monotonic()
    if a.mode=='restore':
        snapshot=a.parent/'T72.deetsnap.gz';s=TwoMemorySession.load(snapshot);parent=None;interventions=[];before=physical(s.world)
    else:
        snapshot=a.parent/'T5.deetsnap.gz';parent=TwoMemorySession.load(snapshot);parent.run_until(71);before=physical(parent.world)
        key='reference_site'if a.operand=='R'else'object_site';q=parent.geometry[key];observation=parent.observe(q)
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*q);edit.raw=0 if a.mode=='cut'else int(observation['raw']);edit.label='ACQUIRED_'+a.operand+'_'+a.mode.upper()
        w=parent.world.diagnostic_fork([edit],True);s=TwoMemorySession(w,parent.geometry,deepcopy(parent.state))
        interventions=[{'site':q,'before':observation,'requested_RAW':str(edit.raw),'clock_edit':None}]
    frames=[]
    for t in ([71]if a.mode!='restore'else[])+[72,73,110,113,138,139,140,177,180,205,206,207]:
        s.run_until(t);frames.append(s.capture())
    expected_final=next(f['physical']for f in reference['frames']if f['tick']==207)
    m={'schema':'CPC9.two_memory.causal_restore.v1','id':a.out.name,'mode':a.mode,'operand':a.operand,
       'preparations':0,'forks':int(a.mode!='restore'),'continuations':int(a.mode=='restore'),
       'parent':{'id':reference['case']['id'],'snapshot':snapshot.name,'sha256':sha(snapshot),'primary_sha256':sha(a.parent/'MEASUREMENTS.json')},
       'parent_before':before,'parent_after':physical(parent.world)if parent is not None else None,
       'parent_unchanged':parent is None or before==physical(parent.world),'interventions':interventions,
       'new_requests':[],'requests':s.receipts(),'frames':frames,'geometry':s.geometry,
       'final_physical':physical(s.world),'final_physical_equal_reference':physical(s.world)==expected_final,
       'receipts_equal_reference':s.receipts()==reference['requests'],'source_sha256':sha(__file__),
       'status':'MEASURED','elapsed_seconds':time.monotonic()-start}
    path=a.out/'T207.deetsnap.gz';m['snapshot']={'path':path.name,'storage':s.save(path),'sha256':sha(path)};put(a.out/'MEASUREMENTS.json',m)
    print(json.dumps({'id':a.out.name,'mode':a.mode,'first_direction':frames[0 if a.mode=='restore' else 1]['center']['direction'],
        'physical_equal_reference':m['final_physical_equal_reference'],'receipts_equal_reference':m['receipts_equal_reference']}),flush=True)
    if a.mode!='cut'and not(m['final_physical_equal_reference']and m['receipts_equal_reference']):raise AssertionError('Sham/restore exact mismatch')


if __name__=='__main__':main()
