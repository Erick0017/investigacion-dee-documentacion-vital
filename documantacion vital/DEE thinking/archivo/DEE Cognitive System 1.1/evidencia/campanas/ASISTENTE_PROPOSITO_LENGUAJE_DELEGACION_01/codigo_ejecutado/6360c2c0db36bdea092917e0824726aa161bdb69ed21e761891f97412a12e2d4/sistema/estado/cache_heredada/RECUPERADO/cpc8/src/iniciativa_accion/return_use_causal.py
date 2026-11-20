"""Late cut/sham of an already formed native return, never an omitted T0input."""
from pathlib import Path
from copy import deepcopy
import argparse,gc,hashlib,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from iniciativa_accion.solicitud import InitiativeSession,phys,move
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ops(w):return{'channels':sorted(w.runtime.channel_names),'receipts':[exact_receipt(x)for x in w.runtime.receipts]}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 base=ROOT/'resultados/iniciativa/USE_D01_POSITIVE/T87.deetsnap.gz';original=json.loads((base.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'))
 cfg={'schema':'CPC8R.initiative.return_use.causal.frozen.v1','base':base.relative_to(ROOT).as_posix(),'base_sha256':sha(base),'conditions':['restore','return_cut_RAW_only','return_identical_RAW_sham'],
  'prediction_before_execution':'A cut of the already formed return30 at87 removes the43 receiving product89; RAW-identical sham and unchanged restore retain it. All receiving resource inputs have already been applied86.',
  'modality':'AUDIT_FORKS_AND_TECHNICAL_RESTORE','horizon':214,'preparations':0,'technical_restored_continuations':1,'audit_forks':2}
 put(a.out/'CONFIG.json',cfg);bundle=a.out/'executed_source';bundle.mkdir();shutil.copyfile(Path(__file__),bundle/Path(__file__).name);shutil.copyfile(ROOT/'src/iniciativa_accion/solicitud.py',bundle/'solicitud.py')
 s=InitiativeSession.load(base);before=phys(s.world);beforeops=ops(s.world);b=s.geometry['branches'][0];e=b['effects']['1'];location=move(e['return_site'],e['return_direction']);actual=s.observe(location);assert actual['s_reg']==30
 m={'schema':'CPC8R.initiative.return_use.causal.measurements.v1','configuration':cfg,'parent_physical':before,'parent_operational':beforeops,'rows':[],'status':'RUNNING','source_sha256':{x.name:sha(x)for x in bundle.iterdir()}}
 start=time.monotonic();cpu=time.process_time()
 for condition in cfg['conditions']:
  edits=[]
  if condition!='restore':
   edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*location);edit.raw=int(actual['raw'])if'sham'in condition else 0;edit.clock=None;edit.label=condition;edits=[edit]
  w=s.world.diagnostic_fork(edits,True)if edits else s.world.fork();c=InitiativeSession(w,s.geometry,deepcopy(s.state));row={'condition':condition,'before':actual,'after':c.observe(location),'operative_queue_equal_to_parent':ops(w)==beforeops,'clock_preserved':c.observe(location)['clock']==actual['clock'],'frames':[]}
  for t in(87,88,89,90,91,136,137,203,204,214):
   if t>c.tick:c.run_until(t)
   row['frames'].append({'tick':c.tick,'receiving_contacts':[c.observe(rx['meeting_site'])for rx in c.geometry['return_use']['items']],'receiving_emissions':[c.observe(rx['emission_site'])for rx in c.geometry['return_use']['items']],'quantity':[c.observe(q)for q in((50,35,35),(49,35,35),(51,35,35))]})
  row['used_return_readouts']=[o for f in row['frames']if f['tick']==89 for o in f['receiving_contacts']if o['active']and o['semantic']==1 and o['direction']==[0,0,-1]and o['s_reg']>13]
  row.update(final_physical=phys(w),final_receipts=ops(w)['receipts'],parent_unchanged=phys(s.world)==before and ops(s.world)==beforeops)
  assert row['parent_unchanged'];path=a.out/(condition+'_T214.deetsnap.gz');row['snapshot']={'path':path.name,'storage':c.save(path)};m['rows'].append(row);put(a.out/'INCREMENTAL.json',m);del c,w;gc.collect()
 m['checks']={'restore_physical_equals_original':m['rows'][0]['final_physical']==original['final_physical'],
  'restore_receipts_equal_original':m['rows'][0]['final_receipts']==sorted([r['receipt']for r in original['quantity_receipts']+original['initiative_receipts']],key=lambda r:r['id']),
  'parent_unchanged':all(x['parent_unchanged']for x in m['rows']),'clocks_preserved':all(x['clock_preserved']for x in m['rows']),'original_queue_preserved':all(x['operative_queue_equal_to_parent']for x in m['rows']),'base_bytes_unchanged':sha(base)==cfg['base_sha256']}
 m.update(status='MEASURED',elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu);put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'checks':m['checks'],'used_return':{x['condition']:x['used_return_readouts']for x in m['rows']}}))
if __name__=='__main__':main()
