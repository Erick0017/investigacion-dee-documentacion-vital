"""Explicit audit forks of the complete same-Runtime gradient/request world.

No edited audit branch is returned to the operative MAIN. The unchanged loaded
branch is a technical continuation, not a new independent preparation.
"""
from pathlib import Path
from copy import deepcopy
import argparse,gc,hashlib,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from iniciativa_accion.solicitud import InitiativeSession,phys,move
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,x):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def operations(world):return{'channels':sorted(world.runtime.channel_names),'receipts':[exact_receipt(r)for r in world.runtime.receipts]}
def local(session,site):return[session.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 base=ROOT/'resultados/iniciativa/GRAD_D01_REFERENCE31/T73.deetsnap.gz'
 configuration={'schema':'CPC8R.initiative.gradient.causal.frozen.v1','base':base.relative_to(ROOT).as_posix(),'base_sha256':sha(base),
  'conditions':['restore_unchanged','request_cut','request_identical_sham','source_cut','source_identical_sham'],
  'cut_fields':'RAW only on diagnostic forks; preserve clocks and original pending inputs/receipts',
  'horizon':214,'readout_windows':{'source':77,'effect':81,'return':86,'quantity_before':[136,203],'quantity_after':[137,204]},
  'prediction_before_execution':'The formed request7 or separately acquired source16 is necessary for the native return30; identicalRAWshams retain it. Later quantity functionality is measured rather than assumed.',
  'scope':'Five continuations of one saved learned world, zero new independent preparations. No edited branch or computed answer is written to MAIN.'}
 put(a.out/'CONFIG.json',configuration)
 source=a.out/'executed_source';source.mkdir();shutil.copyfile(Path(__file__),source/Path(__file__).name);shutil.copyfile(ROOT/'src/iniciativa_accion/solicitud.py',source/'solicitud.py')
 parent=InitiativeSession.load(base);parent_phys=phys(parent.world);parent_ops=operations(parent.world)
 branch=parent.geometry['branches'][0];request_site=branch['request_probe_site'];ss=branch['sources']['1'];source_site=move(ss['hub'],ss['direction'],73-3)
 assert parent.observe(request_site)['s_reg']==7 and parent.observe(source_site)['s_reg']==16
 original=json.loads((base.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'))
 result={'schema':'CPC8R.initiative.gradient.causal.measurements.v1','configuration':configuration,'parent_physical':parent_phys,'parent_operational':parent_ops,
  'preparations':0,'audit_forks':4,'technical_restored_continuations':1,'rows':[],
  'source_sha256':{p.name:sha(p)for p in source.iterdir()},'status':'RUNNING'}
 started=time.monotonic();cpu=time.process_time()
 for condition in configuration['conditions']:
  location=request_site if condition.startswith('request')else source_site if condition.startswith('source')else None
  edits=[]
  if location is not None:
   before=parent.observe(location);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*location);e.raw=int(before['raw'])if'sham'in condition else 0;e.clock=None;e.label=condition;edits=[e]
  world=parent.world.diagnostic_fork(edits,True)if edits else parent.world.fork()
  session=InitiativeSession(world,parent.geometry,deepcopy(parent.state));interventions=[]
  if location is not None:interventions=[{'site':location,'before':parent.observe(location),'after':session.observe(location),'clock_preserved':parent.observe(location)['clock']==session.observe(location)['clock'],'before_Moore27':local(parent,location),'after_Moore27':local(session,location)}]
  row={'condition':condition,'modality':'DIAGNOSTIC_FORK'if edits else'TECHNICAL_RESTORED_CONTINUATION','entry':phys(world),'interventions':interventions,
   'original_operative_queue_preserved':operations(world)==parent_ops,'frames':[],'quantity':[]}
  for tick in list(range(73,89))+[136,137,180,203,204,214]:
   if tick>session.tick:session.run_until(tick)
   row['frames'].append(session.capture())
   if tick in(136,137,203,204):row['quantity'].append({'tick':tick,'center':session.observe((50,35,35)),'reference':session.observe((49,35,35)),'object':session.observe((51,35,35)),'Moore27':local(session,(50,35,35))})
  returns=[o for f in row['frames']if f['tick']==86 for b in f['branches']for o in b['return'].values()]
  row['return_readouts']=[{'physical':o,'covered':o['active']and o['semantic']==1 and o['direction'][0]in(-1,1)and o['direction'][1:]==[-1,-1]and o['s_reg']>7}for o in returns]
  row.update(final_physical=phys(world),final_receipts=operations(world)['receipts'],parent_unchanged=phys(parent.world)==parent_phys and operations(parent.world)==parent_ops)
  assert row['parent_unchanged']
  path=a.out/(condition+'_T214.deetsnap.gz');row['snapshot']={'path':path.name,'storage':session.save(path)}
  result['rows'].append(row);put(a.out/'INCREMENTAL.json',result);del session,world;gc.collect()
 result['checks']={'restore_physical_equal_original':result['rows'][0]['final_physical']==original['final_physical'],
  'restore_receipts_equal_original':result['rows'][0]['final_receipts']==sorted([r['receipt']for r in original['quantity_receipts']+original['initiative_receipts']],key=lambda r:r['id']),
  'all_parent_unchanged':all(r['parent_unchanged']for r in result['rows']),'all_queues_preserved':all(r['original_operative_queue_preserved']for r in result['rows']),
  'all_clocks_preserved':all(e['clock_preserved']for r in result['rows']for e in r['interventions']),'base_unchanged':sha(base)==configuration['base_sha256']}
 result.update(status='MEASURED',elapsed_seconds=time.monotonic()-started,cpu_seconds=time.process_time()-cpu);put(a.out/'MEASUREMENTS.json',result)
 print(json.dumps({'checks':result['checks'],'returns':{r['condition']:[x['physical']for x in r['return_readouts']if x['covered']]for r in result['rows']}}))
if __name__=='__main__':main()
