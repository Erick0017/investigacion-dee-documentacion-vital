"""Selective diagnostic of an actually emitted native counterflow; never MAIN."""
import argparse,gc,json,sys
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from dee_thinking import _native as d
from feedback_regulador import FeedbackSession
from cantidad_renovable import physical,move

def run(out):
 out.mkdir(parents=True,exist_ok=False);rows=[];parent_path=ROOT/'resultados/regulacion/FB3_P01/T97.deetsnap.gz'
 baseline=json.loads((parent_path.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'))
 for mode in('cut','sham'):
  parent=FeedbackSession.load(parent_path);before=physical(parent.world);site=move(parent.geometry['center'],(19,0,0));pre=parent.observe(site)
  if not(pre['active']and pre['s_reg']==7 and pre['direction']==[1,0,0]):raise RuntimeError('Frozen native pulse not present')
  e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site);e.raw=0 if mode=='cut'else int(pre['raw']);e.label='AUDITOR_NATIVE_FEEDBACK_'+mode
  child=parent.world.diagnostic_fork([e],True);s=FeedbackSession(child,parent.geometry,deepcopy(parent.state));trace=[]
  for t in(97,98,136,137,140,141,142,203,204):
   s.run_until(t);r=s.capture();center=move(s.geometry['center'],(-4,0,0));r['meeting_Moore27']=[s.observe(move(center,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)];trace.append(r)
  final=physical(s.world);s.save(out/(mode+'_T204.deetsnap.gz'))
  rows.append({'mode':mode,'preparations':0,'diagnostic_forks':1,'parent_path':parent_path.relative_to(ROOT).as_posix(),'parent_unchanged':before==physical(parent.world),'intervention':{'site':site,'pre':pre,'raw_written':str(e.raw),'clock_edit':None},'observations':trace,'inputs':s.receipts(),'final':final,'full_physical204_equal_reference':final==baseline['final']})
  del s,child,parent;gc.collect()
 result={'schema':'CPC8R.native_feedback.causal.v1','freeze':'Exact already observed pulse97, selectiveRAW edit only in diagnosticfork; shamsameRAW/unchangedclocks. No result returns to MAIN.','results':rows,'interpretation_scope':'R1/fixed feedback path; no R2 strategy acquired from utility.','baseline_final':baseline['final']}
 (out/'MEASUREMENTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps([{'mode':r['mode'],'parent_unchanged':r['parent_unchanged'],'same_full204':r['full_physical204_equal_reference'],'last':r['observations'][-1]['center']}for r in rows]))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
