"""Complete-state audit forks and restored continuation of initiativeF1."""
from pathlib import Path
from copy import deepcopy
import argparse,gc,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from iniciativa_accion.solicitud import InitiativeSession,phys,move
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,x):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def operations(world):return{'channels':sorted(world.runtime.channel_names),'receipts':[exact_receipt(r)for r in world.runtime.receipts]}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 base=ROOT/'resultados/iniciativa/INI_D02_REFERENCE_MINUS_MISMATCH/T74.deetsnap.gz'
 configuration={'schema':'CPC8R.initiative.causal.frozen.v1','base':base.relative_to(ROOT).as_posix(),'base_sha256':sha(base),
  'conditions':['restore_unchanged','request_cut','request_identical_sham','source_cut','source_identical_sham'],
  'cut_fields':'RAW only on diagnostic fork; preserve clock and full original pending inputs/receipts',
  'horizon':94,'readouts':{'source':78,'effect':82,'return':87},
  'before_execution_hypothesis':'Removing the formed request or acquired source eliminates the compound return; exactRAWshams preserve it. No edited branch returns toMAIN.',
  'scope':'Five continuations of one saved learned world; zero independent preparations.'}
 put(a.out/'CONFIG.json',configuration)
 parent=InitiativeSession.load(base);parent_phys=phys(parent.world);parent_ops=operations(parent.world)
 branch=next(b for b in parent.geometry['branches']if b['reference_candidate']==-1)
 request_site=branch['request_probe_site'];source_spec=branch['sources']['1'];source_site=move(source_spec['hub'],source_spec['direction'],74-3)
 assert parent.observe(request_site)['s_reg']==18 and parent.observe(source_site)['s_reg']==16
 source_primary=json.loads((base.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'))
 result={'schema':'CPC8R.initiative.causal.measurements.v1','parent_physical':parent_phys,'parent_operational':parent_ops,
  'base_sha256':configuration['base_sha256'],'modality':'DIAGNOSTIC_FORK_AND_TECHNICAL_RESTORE','preparations':0,'continuations':5,'rows':[],'source_sha256':sha(Path(__file__))}
 start=time.monotonic();cpu=time.process_time()
 for condition in configuration['conditions']:
  edits=[];location=None
  if condition.startswith('request'):location=request_site
  elif condition.startswith('source'):location=source_site
  if location is not None:
   before=parent.observe(location);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*location);e.raw=int(before['raw'])if'sham'in condition else 0;e.clock=None;e.label=condition;edits=[e]
  world=parent.world.diagnostic_fork(edits,True)if edits else parent.world.fork()
  s=InitiativeSession(world,parent.geometry,deepcopy(parent.state));intervention=[]
  if location is not None:intervention=[{'site':location,'before':parent.observe(location),'after':s.observe(location),'fields':['RAW'],'clocks_preserved':parent.observe(location)['clock']==s.observe(location)['clock']}]
  row={'condition':condition,'entry':phys(world),'intervention':intervention,'operational_queue_equal_to_parent_before_run':operations(world)==parent_ops,'captures':[]}
  for tick in(74,77,78,81,82,86,87,88,94):
   if tick>s.tick:s.run_until(tick)
   row['captures'].append(s.capture())
  returns=[o for f in row['captures']if f['tick']==87 for b in f['branches']for o in b['return'].values()]
  row['return_readouts']=[{'physical':o,'covered':o['active']and o['semantic']==1 and o['direction'][0]in(-1,1)and o['direction'][1:]==[-1,-1]and o['s_reg']>7}for o in returns]
  row['final_physical']=phys(world);row['final_receipts']=operations(world)['receipts']
  row['parent_unchanged']=phys(parent.world)==parent_phys and operations(parent.world)==parent_ops
  assert row['parent_unchanged']
  path=a.out/(condition+'_T94.deetsnap.gz');row['snapshot']={'path':path.name,'storage':s.save(path)}
  result['rows'].append(row);put(a.out/'INCREMENTAL.json',result);del s,world;gc.collect()
 restored=result['rows'][0]
 result['checks']={'restored_continuation_physical_equals_original':restored['final_physical']==source_primary['final_physical'],
  'restored_continuation_receipts_equal_original':restored['final_receipts']==[x['receipt']for x in source_primary['receipts']],
  'all_parent_unchanged':all(r['parent_unchanged']for r in result['rows']),
  'all_original_queues_preserved':all(r['operational_queue_equal_to_parent_before_run']for r in result['rows']),
  'all_edited_clocks_preserved':all(e['clocks_preserved']for r in result['rows']for e in r['intervention']),
  'base_bytes_unchanged':sha(base)==configuration['base_sha256']}
 result.update(status='MEASURED',elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu)
 put(a.out/'MEASUREMENTS.json',result)
 print(json.dumps({'checks':result['checks'],'returns':{r['condition']:[x['physical']for x in r['return_readouts']if x['covered']]for r in result['rows']}}))
if __name__=='__main__':main()
