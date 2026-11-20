"""Explicit heritage diagnostic: incoming residue versus lost access, not E1.

Uses the complete saved T78 state and its original pending queries. All RAW
edits occur only in authorized diagnostic forks; clocks and parent stay exact.
The alternative reader is a declared physical probe, never a cached response.
"""
from pathlib import Path
from array import array
from datetime import datetime,timezone
import argparse,gc,hashlib,json,shutil,sys,time
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot
ROOT=Path(__file__).resolve().parents[1]
N=131
WHL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
JOIN=[90,14,29];MEMORY=[90,15,29];EXTRA=[89,15,29];OFFPATH=[91,13,29]

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 temporary=path.with_name(path.name+'.pending')
 temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
 temporary.replace(path)
def phys(world):
 r=world.runtime
 return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
  'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def at(world,site):return exact_observation(world.runtime.observe(d.Coordinate(*site)))
def move(q,v,k=1):return [(q[i]+v[i]*k)%N for i in range(3)]
def neighborhood(world,q):return [at(world,move(q,(x,y,z))) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1)]
def incoming(world,q):
 # Match buscar_fuente_demux: nonzero direction and destination match. Do not
 # filter by state, semantic or the observer's active flag.
 return [o for o in neighborhood(world,q) if o['site']!=q and o['direction']!=[0,0,0] and move(o['site'],o['direction'])==q]
def operational(world):
 return {'channels':sorted(world.runtime.channel_names),'receipts':[exact_receipt(r) for r in world.runtime.receipts],
  'world_interface_names':sorted(p.name for p in world.interfaces)}
def edit(site,raw,label):
 e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*site);e.raw=raw;e.clock=None;e.label=label;return e
def gate(world,q):
 g=d.inspect_write_gate(world.runtime,d.Coordinate(*q),True)
 return {'site':q,'branch':g.branch,'n_active':g.n_active,'center_available':g.center_available,
  'center_state':g.center.state,'center_s_reg':g.center.s_reg,'center_semantic':g.center.semantic,
  'clock':str(g.local_clock),'k':g.k,'period':None if g.period is None else str(g.period),
  'phase_remainder':None if g.phase_remainder is None else str(g.phase_remainder),
  'scope':'Passive local write-gate inspection, not a substitute for the native transition.'}

def run(out):
 out.mkdir(parents=True,exist_ok=False)
 base=ROOT/'resultados/diagnostico_L15_r1/passive_original_PRE_JOIN_T78.deetsnap.gz'
 kernel=ROOT/'genealogia/product45/kernel_v27.cpp'
 if sha(kernel)!=KERNEL_SHA:raise ValueError('Kernel source identity differs')
 config={'schema':'CPC8R.heritage.L15.causal.frozen.v1','frozen_utc':datetime.now(timezone.utc).isoformat(),
  'modality':'HERITAGE_DIAGNOSTIC_FORKS_NOT_NEW_E1','base':base.relative_to(ROOT).as_posix(),'base_sha256':sha(base),
  'N':N,'parent_tick':78,'horizon':134,'parent_run':'RL_P11_BA, earlier CPC8 cut, already copied selectively',
  'conditions':['unaltered_fork','cut_extraneous7','identical_RAW_sham','cut_equal_dose_offpath7','late_alternative_reader','late_reader_cut_memory16'],
  'edits':{'cut_extraneous7':{'site':EXTRA,'raw':'0','clock':'PRESERVE'},
   'identical_RAW_sham':{'site':EXTRA,'raw':'IDENTICAL_CURRENT_RAW','clock':'PRESERVE'},
   'cut_equal_dose_offpath7':{'site':OFFPATH,'raw':'0','clock':'PRESERVE'},
   'late_reader_cut_memory16':{'site':MEMORY,'raw':'0','clock':'PRESERVE'}},
  'alternative_reader':{'site':[96,11,29],'direction':[-1,0,0],'payload':9,'input_tick':79,'meeting_site':[93,11,29],'read_tick':82,
    'API':'Runtime.probe(channel,at_tick,s_reg)','state':1,'semantic':1,'clock_on_admission':'Runtime standard0'},
  'prediction_before_run':{'uncut79':{'s_reg':23,'direction':[1,-1,0]},'cut7_79':{'s_reg':16,'direction':[0,-1,0]},
   'late_reader82':{'s_reg':32,'direction':[0,-1,0]},'late_reader_cut_memory82':{'s_reg':16,'direction':[0,-1,0]},
   'scope':'Mechanism hypotheses/evaluation only; predictions are never input into the participant or decoder.'},
  'kernel_reducer_reference':{'path':kernel.relative_to(ROOT).as_posix(),'sha256':KERNEL_SHA,'lines':'189-226 and empty-destination318-322',
   'important':'Directional sources are not filtered by state or active flag. No scalar arithmetic is used to generate native outputs.'},
  'bounds':'Six independent audit continuations from one historical parent; zero new preparations and zero new E1 histories; no attribution of autonomous source selection.'}
 put(out/'CONFIG.json',config);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py')
 import dee_thinking as dee
 assert dee.__version__=='4.5.0' and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
 assert sha(d.__file__)==PYD_SHA
 main,storage=load_world_snapshot(base,max_bytes=512*1024**2)
 assert int(main.runtime.dimension)==N and int(main.runtime.current_tick)==78
 baseline=phys(main);parent_ops=operational(main);parents=[at(main,q) for q in (JOIN,MEMORY,EXTRA,OFFPATH)]
 assert parents[1]['s_reg']==16 and parents[1]['direction']==[0,-1,0]
 assert parents[2]['s_reg']==7 and parents[3]['s_reg']==7
 contributors=incoming(main,JOIN)
 assert {tuple(o['site']) for o in contributors}=={tuple(MEMORY),tuple(EXTRA)}
 result={'schema':'CPC8R.heritage.L15.causal.measurements.v1','status':'RUNNING','case_id':'L15_INCOMING_RESIDUE_AND_RELOCATED_ACCESS',
  'instrument':{'version':dee.__version__,'module':dee.__file__,'WHL_sha256':WHL_SHA,'PYD_sha256':PYD_SHA,'kernel_source_sha256':KERNEL_SHA},
  'base':config['base'],'base_sha256':config['base_sha256'],'base_storage':storage,'parent_physical':baseline,'parent_operational':parent_ops,
  'prestate_Moore27':neighborhood(main,JOIN),'incoming_to79':contributors,'incoming_state0_count':sum(o['state']==0 for o in contributors),
  'parent_gate78':gate(main,JOIN),'conditions':[],'preparations':0,'audit_continuation_forks':6,'new_E1_histories':0}
 started=time.monotonic();cpu=time.process_time()
 for condition in config['conditions']:
  edits=[]
  if condition=='cut_extraneous7':edits=[edit(EXTRA,0,condition)]
  elif condition=='identical_RAW_sham':edits=[edit(EXTRA,int(at(main,EXTRA)['raw']),condition)]
  elif condition=='cut_equal_dose_offpath7':edits=[edit(OFFPATH,0,condition)]
  elif condition=='late_reader_cut_memory16':edits=[edit(MEMORY,0,condition)]
  w=main.diagnostic_fork(edits,True) if edits else main.fork()
  row={'condition':condition,'parent_tick':78,'entry_physical':phys(w),'parent_queue_receipts_preserved':operational(w)==parent_ops,
   'interventions':[{'site':[e.coordinate.x,e.coordinate.y,e.coordinate.z],'raw_before':at(main,[e.coordinate.x,e.coordinate.y,e.coordinate.z])['raw'],
    'raw_after':at(w,[e.coordinate.x,e.coordinate.y,e.coordinate.z])['raw'],'clock_before':at(main,[e.coordinate.x,e.coordinate.y,e.coordinate.z])['clock'],
    'clock_after':at(w,[e.coordinate.x,e.coordinate.y,e.coordinate.z])['clock'],'clock_was_edited':False,'modality':'DIAGNOSTIC_FORK'}for e in edits],
   'frames':[],'reader_receipt':None}
  if condition in('late_alternative_reader','late_reader_cut_memory16'):
   ch=d.ChannelSpec();ch.name='diagnostic.L15.relocated_reader';ch.injection_site=d.Coordinate(96,11,29);ch.direction=d.Direction(-1,0,0)
   ch.state=1;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=False;w.runtime.register_channel(ch)
   rr=w.runtime.probe(ch.name,79,9);reader_id=int(rr.id);row['reader_request_before_advance']=exact_receipt(rr)
  else:reader_id=None
  for tick in(78,79,80,81,82,83,130,131,133,134):
   if tick>78:w.run_until(tick)
   frame={'tick':tick,'original_port':at(w,[90,90,29]),'uninteracted_L15_prediction':at(w,[90,(93-tick)%N,29]),
    'post79_biased_ray_prediction':at(w,move(JOIN,(1,-1,0),tick-79)) if tick>=79 else None}
   if tick in(78,79):frame.update(Moore27_join=neighborhood(w,JOIN),incoming_to_next_join=incoming(w,JOIN))
   if tick in(81,82):frame.update(Moore27_alternate=neighborhood(w,[93,11,29]))
   if tick==79:row['actual79']=at(w,JOIN)
   if tick==82:row['alternate82']=at(w,[93,11,29])
   if tick==134:row['original_port134']=at(w,[90,90,29])
   row['frames'].append(frame)
   if (condition=='cut_extraneous7' and tick==79) or (condition=='late_alternative_reader' and tick==82):
    path=out/(condition+f'_T{tick}.deetsnap.gz');row.setdefault('snapshots',[]).append({'path':path.name,'physical':phys(w),'storage':save_world_snapshot(w,path,compress=True)})
  row['reader_receipt']=exact_receipt(w.runtime.receipt(reader_id)) if reader_id else None
  row['final_receipts']=[exact_receipt(r) for r in w.runtime.receipts];row['final_physical']=phys(w)
  path=out/(condition+'_T134.deetsnap.gz');row.setdefault('snapshots',[]).append({'path':path.name,'physical':row['final_physical'],'storage':save_world_snapshot(w,path,compress=True)})
  row['parent_unchanged_after_fork']=phys(main)==baseline and operational(main)==parent_ops
  assert row['parent_unchanged_after_fork']
  result['conditions'].append(row);put(out/'INCREMENTAL.json',result)
  del w;gc.collect()
 by={r['condition']:r for r in result['conditions']}
 result['checks']={'unchanged_parent_all':all(r['parent_unchanged_after_fork']for r in by.values()),
  'identical_sham_full_physics_equals_unaltered':by['identical_RAW_sham']['final_physical']==by['unaltered_fork']['final_physical'],
  'all_clock_edits_absent':all(not e['clock_was_edited'] and e['clock_before']==e['clock_after']for r in by.values()for e in r['interventions']),
  'original_queue_all_preserved_before_added_probe':all(r['parent_queue_receipts_preserved']for r in by.values()),
  'base_file_unchanged':sha(base)==config['base_sha256']}
 result.update(status='MEASURED',elapsed_seconds=time.monotonic()-started,cpu_seconds=time.process_time()-cpu)
 put(out/'MEASUREMENTS.json',result)
 print(json.dumps({'status':result['status'],'conditions':[{'condition':r['condition'],'at79':r['actual79'],'at82':r['alternate82'],'at134':r['original_port134'],'receipt':r['reader_receipt']}for r in result['conditions']],'checks':result['checks']},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
