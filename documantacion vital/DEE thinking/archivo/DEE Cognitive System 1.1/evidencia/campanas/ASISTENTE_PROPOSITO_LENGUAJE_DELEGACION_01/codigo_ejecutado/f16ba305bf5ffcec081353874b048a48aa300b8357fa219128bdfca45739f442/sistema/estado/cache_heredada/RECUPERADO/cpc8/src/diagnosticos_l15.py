"""Read-only heritage replay and an explicitly instrumental early-access branch.

Neither branch is the new E1. No reconstructed result is returned to MAIN.
"""
import argparse,gc,hashlib,json,shutil,sys,time
from array import array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phys(w):
 r=w.runtime;return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def observe(w,q):return exact_observation(w.runtime.observe(d.Coordinate(*q)))
def neigh(w,q):return[observe(w,[(q[i]+v[i])%131 for i in range(3)])for v in((x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1))]
def run(out):
 out.mkdir(parents=True,exist_ok=False)
 original=ROOT.parent/'RUN_20261018_204718/resultados/integracion/RL_P11_BA/checkpoints'
 bases=ROOT/'genealogia/primer_cpc8/diagnostico_L15';bases.mkdir(parents=True,exist_ok=True)
 copies=[]
 for n in('T20.deetsnap.gz','T134.deetsnap.gz'):
  if not(bases/n).exists():shutil.copyfile(original/n,bases/n)
  if sha(original/n)!=sha(bases/n):raise ValueError('Historical base changed')
  copies.append({'source':str(original/n),'path':(bases/n).relative_to(ROOT).as_posix(),'sha256':sha(bases/n)})
 config={'schema':'CPC8R.heritage.L15.frozen.r1','technical_correction':'Runtime.probe(channel,at_tick,s_reg) differs from OrganizationalWorld.probe(port,payload,tick); previous early reader was rejected_late and is not a negative memory test','frozen_before_runtime_load':True,'parent':'RL_P11_BA/T20','modality':'HERITAGE_DIAGNOSTIC_NOT_NEW_E1',
  'predicted_memory':{'hub':[90,90,29],'native_teaching_contact_tick':3,'direction':[0,-1,0],'expected_load':16},
  'passive_horizon':[20,134],'original_query_input':131,'original_read':134,
  'early_reader':{'added_channel':'diagnostic.L15.early','input_tick':26,'physical_meeting_tick':29,'input_site':[93,64,29],'direction':[-1,0,0],'payload':9},
  'prediction':'If the learned moving support exists before the later access failure, the explicit diagnostic early reader can expose it. This is instrumental access, not learned source selection.',
  'no_RAW_clock_edits':True,'sources':copies}
 put(out/'CONFIG.json',config);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py')
 rows=[]
 for condition in('passive_original','early_reader'):
  w,_=load_world_snapshot(bases/'T20.deetsnap.gz',max_bytes=1024**3);entry=phys(w);trace=[];windows=[];receipt_id=None
  if condition=='early_reader':
   ch=d.ChannelSpec();ch.name='diagnostic.L15.early';ch.injection_site=d.Coordinate(93,64,29);ch.direction=d.Direction(-1,0,0);ch.state=1;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=False
   w.runtime.register_channel(ch);r=w.runtime.probe(ch.name,26,9);receipt_id=int(r.id)
  first_unexpected=None
  for tick in range(20,135):
   if tick>20:w.run_until(tick)
   predicted=[90,(90-(tick-3))%131,29];o=observe(w,predicted)
   valid=o['active']and o['semantic']==1 and o['s_reg']==16 and o['direction']==[0,-1,0]
   trace.append({'tick':tick,'prediction_site':predicted,'physical':o,'matches_uninteracted_memory':valid})
   if not valid and first_unexpected is None:
    first_unexpected=tick;windows.append({'tick':tick,'center':predicted,'Moore27':neigh(w,predicted)})
    save_world_snapshot(w,out/(condition+f'_FIRST_DIFF_T{tick}.deetsnap.gz'),compress=True)
   if tick in(25,26,28,29,30,78,130,131,133,134):
    q=[90,64,29]if tick<31 else[90,14,29]if tick==78 else[90,90,29];windows.append({'tick':tick,'center':q,'Moore27':neigh(w,q)})
   if tick==78:save_world_snapshot(w,out/(condition+'_PRE_JOIN_T78.deetsnap.gz'),compress=True)
   if tick==29:early=observe(w,[90,64,29])
  final=phys(w);save_world_snapshot(w,out/(condition+'_T134.deetsnap.gz'),compress=True)
  rows.append({'condition':condition,'entry':entry,'first_miss_on_uninteracted_prediction':first_unexpected,'trace':trace,'windows':windows,'early_read29':early,'original_port134':observe(w,[90,90,29]),'early_receipt':exact_receipt(w.runtime.receipt(receipt_id))if receipt_id else None,'final':final})
  del w;gc.collect()
 refworld,_=load_world_snapshot(bases/'T134.deetsnap.gz',max_bytes=1024**3);reference=phys(refworld)
 result={'schema':'CPC8R.heritage.L15.measurements.v1','case_id':'L15_REPLAY_AND_EARLY_ACCESS','references':copies,'conditions':rows,
  'passive_replay_full_physical_equal':rows[0]['final']==reference,'reference134':reference,
  'scope':'An early explicit diagnostic reader changes a continuation; it does not prove E1 learned to locate the memory or that every missing later signal denotes forgetting. Full trajectory observer gaps declared outside local windows.'}
 put(out/'MEASUREMENTS.json',result);print(json.dumps({'passive_replay_equal':result['passive_replay_full_physical_equal'],'first_miss':[r['first_miss_on_uninteracted_prediction']for r in rows],'early_reads':[r['early_read29']for r in rows]},ensure_ascii=False))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
