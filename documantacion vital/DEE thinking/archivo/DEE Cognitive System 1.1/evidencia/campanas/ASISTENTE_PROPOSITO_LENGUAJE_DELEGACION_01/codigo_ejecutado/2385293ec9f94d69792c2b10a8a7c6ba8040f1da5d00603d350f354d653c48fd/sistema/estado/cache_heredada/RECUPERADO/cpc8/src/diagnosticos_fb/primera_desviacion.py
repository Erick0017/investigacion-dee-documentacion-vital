"""Locate and contrast the first reference deviation in nativefeedbackFBL.

This is a labelled auditor trajectory from a complete existing state. It neither
edits a MAIN nor returns corrected states to it. RAW/clocks remain exact64bit.
"""
from pathlib import Path
from copy import deepcopy
from array import array
import argparse,gc,hashlib,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot,decode_metadata,encode_metadata

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def move(q,v,k=1):return[(int(q[i])+k*int(v[i]))%67 for i in range(3)]
def phys(w):return{'tick':int(w.runtime.current_tick),'RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
def observe(w,q):return exact_observation(w.runtime.observe(d.Coordinate(*q)))
def neighborhood(w,q):return[observe(w,move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
def incoming(w,q):
 out=[]
 for o in neighborhood(w,q):
  if o['site']==q or o['direction']==[0,0,0]:continue
  if move(o['site'],o['direction'])==q:out.append(o)
 return out
def operations(w):return{'channels':sorted(w.runtime.channel_names),'receipts':[exact_receipt(x)for x in w.runtime.receipts]}
def save(w,p):
 # Only inert metadata is refreshed for a valid later operative checkpoint;
 # all original requests/geometry are preserved. No clocks/RAW are edited.
 for key,value in dict(w.runtime.snapshot_metadata_entries).items():
  if key.startswith('CPC8R.quantity.'):
   m=decode_metadata(value);m['tick']=int(w.runtime.current_tick);m['channels']=sorted(w.runtime.channel_names);w.runtime.set_snapshot_metadata(key,encode_metadata(m))
 return save_world_snapshot(w,p,compress=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 base=ROOT/'resultados/regulacion/FBL_P01/T204.deetsnap.gz';source=base.parent/'MEASUREMENTS.json';primary=json.loads(source.read_text(encoding='utf-8'));g=primary['geometry'];hub=g['reference_hub'];cfg=primary['config']
 frozen={'schema':'CPC8R.feedback.reference_diagnostic.frozen.v1','parent':base.relative_to(ROOT).as_posix(),'parent_sha256':sha(base),'primary_sha256':sha(source),
  'frozen_before_load':True,'horizon':338,'candidate_reference_path':'reference_hub+(tick-3)*(0,1,0) modulo67, certified only until first changed record',
  'expected_before_addition':cfg['reference']+5,'expected_from271':cfg['reference']+5+cfg['addition'],
  'criterion':'First path record that is not active semantic1, direction(0,1,0), exact expected reference quantity. At271+ only actually applied cue/resource receipts justify adding the declared experience.',
  'conditional_diagnostic_rule':'If and only if exactly one incoming record has load7 distinct from reference and addition, cut that one RAW in a diagnostic fork and compare identicalRAWsham. Preserve all clocks and original queue. No edited branch returns to MAIN.',
  'scope':'Reference/input interference diagnosis of one finite feedback circuit; not a newstrategy-learning proof or new independent history.'}
 put(a.out/'CONFIG.json',frozen);shutil.copyfile(Path(__file__),a.out/'EXECUTED_SOURCE.py')
 parent,_=load_world_snapshot(base,max_bytes=512*1024**2);before=phys(parent);before_ops=operations(parent);w=parent.fork()
 m={'schema':'CPC8R.feedback.reference_diagnostic.measurements.v1','configuration':frozen,'preparations':0,'unaltered_continuations':1,'diagnostic_forks':0,'instrument':{'PYD_sha256':sha(Path(d.__file__))},'source_sha256':sha(Path(__file__)),'parent':before,'trace':[],'first_deviation':None,'conditional_forks':[],'status':'RUNNING'}
 assert m['instrument']['PYD_sha256']=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
 start=time.monotonic();cpu=time.process_time();pre_world=None
 # Selected secondary/relay windows are checked before attribution. Direction
 # zero/inactive records are retained; no state>0filter is used in incoming().
 interesting={204,205,206,208,209,210,215,216,217,219,220,221,230,231,232,267,268,269,270,271,272,273,336,337,338}
 for tick in range(204,339):
  if tick>w.runtime.current_tick:
   if m['first_deviation']is None:pre_world=w.fork()
   w.run_until(tick)
  q=move(hub,(0,1,0),tick-3);o=observe(w,q);expected=cfg['reference']+5+(cfg['addition']if tick>=271 else 0)
  correct=o['active']and o['semantic']==1 and o['direction']==[0,1,0]and o['s_reg']==expected
  entry={'tick':tick,'declared_path_site':q,'physical':o,'auditor_expected_reference':expected,'same_reference_signature':bool(correct),'ancestry_certified_before_this_first_change':m['first_deviation']is None}
  m['trace'].append(entry)
  if tick in interesting:
   entry['center_Moore27']=neighborhood(w,g['center']);entry['fixed_relay_sites']=[{'port':r['port'],'target':r['target'],'physical':observe(w,r['target'])}for r in g['feedback_relays']]
  if not correct and m['first_deviation']is None:
   assert pre_world is not None
   event={'pre_tick':tick-1,'tick':tick,'destination':q,'expected':expected,'pre_at_destination':observe(pre_world,q),'post':o,'incoming':incoming(pre_world,q),'pre_Moore27':neighborhood(pre_world,q),'post_Moore27':neighborhood(w,q),'pre_physical':phys(pre_world),'post_physical':phys(w)}
   event['snapshots']={'pre':save(pre_world,a.out/('FIRST_PRE_T'+str(tick-1)+'.deetsnap.gz')),'post':save(w,a.out/('FIRST_POST_T'+str(tick)+'.deetsnap.gz'))}
   m['first_deviation']=event;put(a.out/'INCREMENTAL.json',m)
   extras=[x for x in event['incoming']if x['s_reg']==7]
   event['unique_load7_incoming']=len(extras)==1
   if len(extras)==1:
    extra=extras[0]
    for mode in('cut_extra7_RAW_only','identical_RAW_sham'):
     edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*extra['site']);edit.raw=0 if mode.startswith('cut')else int(extra['raw']);edit.clock=None;edit.label=mode
     branch=pre_world.diagnostic_fork([edit],True);row={'condition':mode,'intervention':{'before':extra,'after':observe(branch,extra['site']),'fields':['RAW'],'clock_preserved':observe(branch,extra['site'])['clock']==extra['clock']},'queue_equal_to_unaltered_pre':operations(branch)==operations(pre_world),'frames':[]}
     for t in sorted({tick,tick+1,270,271,272,273,337,338}):
      if t<branch.runtime.current_tick:continue
      branch.run_until(t);rq=move(hub,(0,1,0),t-3);row['frames'].append({'tick':t,'reference_path':observe(branch,rq),'reference_site':observe(branch,g['reference_site']),'object_site':observe(branch,g['object_site']),'center':observe(branch,g['center'])})
     row['final']=phys(branch);row['receipts']=operations(branch)['receipts'];row['snapshot']=save(branch,a.out/(mode+'_T338.deetsnap.gz'));m['conditional_forks'].append(row);m['diagnostic_forks']+=1;del branch;gc.collect()
   del pre_world;pre_world=None
  elif pre_world is not None:
   del pre_world;pre_world=None
  if tick%10==0:put(a.out/'INCREMENTAL.json',m)
 expected338,_=load_world_snapshot(base.parent/'T338.deetsnap.gz',max_bytes=512*1024**2)
 m.update(status='MEASURED',final=phys(w),final_receipts=operations(w)['receipts'],unchanged_replay338_equal=phys(w)==phys(expected338),parent_unchanged=phys(parent)==before and operations(parent)==before_ops,base_bytes_unchanged=sha(base)==frozen['parent_sha256'],elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu)
 m['snapshot']=save(w,a.out/'UNALTERED_T338.deetsnap.gz');put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'first_deviation':{k:v for k,v in(m['first_deviation']or{}).items()if k in('tick','destination','expected','pre_at_destination','post','incoming','unique_load7_incoming')},'replay338_equal':m['unchanged_replay338_equal'],'parent_unchanged':m['parent_unchanged'],'diagnostic_forks':m['diagnostic_forks']}))
if __name__=='__main__':main()
