"""Clean installed-engine repetition of the bounded B-only auxiliary result.

Only current physical case parameters enter create/curriculum. Frozen outcome
files are read exclusively AFTER the native trajectory by this auditor.
"""
import argparse,hashlib,json,sys
from array import array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from count_sign.branch_session import BranchCountSignSession
def physical(s):
 r=s.world.runtime
 return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--config',type=Path);p.add_argument('--restore',type=Path);p.add_argument('--reference',type=Path,required=True);a=p.parse_args();out=a.out.resolve()
 if out.is_relative_to(ROOT)or ROOT.is_relative_to(out):raise ValueError('External independent output required')
 out.mkdir(parents=True,exist_ok=False);frames=[];before=None
 if a.restore:
  s=BranchCountSignSession.load(a.restore);assert s.tick==94;before=physical(s);created=False
 else:
  cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(x for x in cfg['cases']if x['id']==a.case)
  s=BranchCountSignSession.create(case);s.curriculum(form=case.get('form','paired'),route=case.get('route',True),query=case.get('query',True));created=True
 ticks=(0,4,5,9,10,19,20,23,24,25,89,90,91,92,93,94,95,103,113,114,115,147,148,149,170,171)
 for t in ticks:
  if t<s.tick:continue
  frame=s.run_until(t)
  frames.append({'tick':t,'names':frame['names'],'physical':physical(s)})
  if t==94 and created:s.save(out/'T94.deetsnap.gz')
 actual_final=physical(s);actual_receipts=[r['receipt']for r in s.receipts()]
 # Outcome data now enters only post-trajectory audit, never s.curriculum.
 reference=json.loads(a.reference.read_text(encoding='utf8'));ref_frames={x['tick']:x for x in reference['frames']}
 checks=[{'tick':x['tick'],'exact_native_names':x['names']==ref_frames[x['tick']]['names'],'full_physical_equal':x['physical']==ref_frames[x['tick']]['physical']}for x in frames]
 native_receipts=actual_receipts==[r['receipt']for r in reference['requests']]
 result={'schema':'CPC8R.clean.count_sign.v1','case':a.case,'fresh_technical_reproduction':created,'restored_same_life':not created,'restore_before':before,'no_reteaching_on_restore':True,'checks':checks,'exact_native_receipts':native_receipts,'final_physical':actual_final,'frozen_final_physical_equal':actual_final==reference['final_physical'],'scope':'Calibrated auxiliary B-only native threshold/form reuse, not MAIN, not general numeric semantics. No evaluator data read until after trajectory.','passed':all(x['exact_native_names']and x['full_physical_equal']for x in checks)and native_receipts and actual_final==reference['final_physical']}
 (out/'CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'case':a.case,'passed':result['passed']}))
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
