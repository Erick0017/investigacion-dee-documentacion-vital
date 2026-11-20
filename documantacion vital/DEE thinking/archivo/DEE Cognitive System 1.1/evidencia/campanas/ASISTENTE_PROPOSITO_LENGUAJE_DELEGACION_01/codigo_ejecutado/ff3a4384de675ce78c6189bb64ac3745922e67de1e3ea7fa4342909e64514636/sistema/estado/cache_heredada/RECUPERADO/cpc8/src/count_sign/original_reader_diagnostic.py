"""Cut/sham of all formed sites, using only already-queued ORIGINAL readers."""
import argparse,hashlib,json,shutil,sys
from copy import deepcopy
from pathlib import Path
from array import array
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def physical(w):
 r=w.runtime;return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cut',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 cut=a.out/'executed_source';shutil.copytree(a.parent/'executed_source',cut);shutil.copyfile(__file__,cut/'original_reader_diagnostic.py');sys.path.insert(0,str(cut/'src'))
 from count_sign.branch_session import BranchCountSignSession
 from dee_thinking import _native as d
 parent=BranchCountSignSession.load(a.parent/'T94.deetsnap.gz');before=physical(parent.world);edits=[];interventions=[]
 for bank in parent.geometry['names']:
  q=bank['memory_site'];pre=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=0 if a.cut else int(pre['raw']);e.label='ALL_FORM_BANKS_CUT'if a.cut else'ALL_FORM_BANKS_EXACT_SHAM';edits.append(e);interventions.append({'site':q,'before':pre,'requested_RAW':str(e.raw),'clock_edit':None})
 world=parent.world.diagnostic_fork(edits,True);s=BranchCountSignSession(world,parent.geometry,deepcopy(parent.state),a.out.name);frames=[];snapshots=[]
 for t in(94,100,103,113,114,115,147,148,149,170,171):
  f=s.run_until(t);f['physical']=physical(s.world);frames.append(f)
  if t in(94,114,148,171):
   path=a.out/('T'+str(t)+'.deetsnap.gz');storage=s.save(path);snapshots.append({'path':path.name,'tick':t,'sha256':sha(path),'storage':storage})
 m={'schema':'CPC8R.count_sign.original_reader_diagnostic.v1','case':{'id':a.out.name,'cut':a.cut},'preparations':0,'diagnostic_forks':1,'continuations':0,'parent':{'snapshot':str((a.parent/'T94.deetsnap.gz').relative_to(ROOT)),'sha256':sha(a.parent/'T94.deetsnap.gz'),'case_id':a.parent.name},'interventions':interventions,'geometry':s.geometry,'frames':frames,'requests':s.receipts(),'new_requests':[],'source_sha256':json.loads((a.parent/'MEASUREMENTS.json').read_text(encoding='utf8'))['source_sha256'],'diagnostic_source_sha256':sha(cut/'original_reader_diagnostic.py'),'snapshots':snapshots,'parent_before':before,'parent_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'status':'MEASURED','scope':'All original queued requests, no new channel/probe, same frozen114/148 decoder. Extra experience100 remains queued. Diagnostic fork is never returned to MAIN.'}
 (a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged']}))
