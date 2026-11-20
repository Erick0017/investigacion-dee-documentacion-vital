"""New contact association/use causal panel on explicit laboratory forks."""
import argparse,json,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.contact_renewal_e1 import ContactRenewalE1Session
from integracion.relational_pair import physical,move
from integracion.run_longitudinal_e1 import sha,put
from dee_thinking import _native as d
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pp=ROOT/'resultados/integracion'/cfg['parent_id']/cfg['snapshot'];psha=sha(pp);parent=ContactRenewalE1Session.load(pp);parent.run_until(case['fork_tick']);before=physical(parent.world)
 sites=[]
 for label,q in parent.geometry['contact'].items():
  site=move(q['hub'],(-q['axis'],0,0),-1)if case['target']=='teacher'else move(q['hub'],(0,1,q['consequence_z']),case['fork_tick']-344)
  sites.append({'role':label,'site':site})
 edits=[];rows=[]
 for item in sites:
  pre=parent.observe(item['site']);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*item['site']);e.raw=0 if case['mode']=='cut'else int(pre['raw']);e.label='Newcontactdiagnostic '+case['target']+' '+case['mode'];edits.append(e);rows.append({**item,'pre':pre,'requested_raw':str(e.raw),'clock_edit':None})
 child=parent.world.diagnostic_fork(edits,True);state=deepcopy(parent.state);state['mode']=deepcopy(parent.mode.state);state['quantity']=deepcopy(parent.quantity.state);s=ContactRenewalE1Session(child,parent.geometry,state,parent.identifier+'.'+case['id'])
 for row in rows:row['post']=s.observe(row['site'])
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('contact_renewal_e1.py','longitudinal_e1.py','complete_e1.py','quantity_core.py','relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 m={'schema':'CPC8R.contactRenewalE1.diagnostic.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'saved_tick':340,'fork_tick':case['fork_tick']},'preparations':0,'continuations':0,'diagnostic_forks':1,'edited_sites':rows,'parent_physical_before':before,'fork_physical':physical(s.world),'new_inputs_after_fork':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
 for tick in sorted(set((case['fork_tick'],344,405,411,415,417,428,433,436,472,478,484,539,549))):
  if tick<s.tick:continue
  s.run_until(tick);m['frames'].append(s.view());centers=[r['site']for r in sites]if tick==case['fork_tick']else[s.geometry['quantity']['center']]
  if tick in(411,478):centers+=[q['query_site'if tick==411 else'renewed_site']for q in s.geometry['contact'].values()]
  if tick in(428,433,436):centers+=[q['memory_site'if tick==428 else'context_site']for q in s.geometry['mode']['communication']['receivers']]
  if tick in(415,549):centers+=[q['delivery_site']for q in s.geometry['joint_names'].values()]
  for q in centers:m['windows'].append({'tick':tick,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  m.update(last_complete_tick=s.tick,requests=sorted(s.receipts(),key=lambda r:r['id']),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 path=a.out/'T549.deetsnap.gz';storage=s.save(path);m['snapshots'].append({'path':path.name,'tick':549,'sha256':sha(path),'physical':physical(s.world),'storage':storage});baseline=json.loads((pp.parent/'MEASUREMENTS.json').read_text(encoding='utf8'))
 m.update(status='MEASURED',final_physical=physical(s.world),renewal_observations=s.state['renewal_observations'],social_captures=s.mode.state.get('social_captures',[]),quantity_observations=s.quantity.state['observations'],parent_physical_after=physical(parent.world),parent_file_sha256_after=sha(pp));m['parent_unchanged']=m['parent_physical_before']==m['parent_physical_after']and psha==m['parent_file_sha256_after'];m['baseline_comparison']={'full_physical_equal':m['final_physical']==baseline['final_physical'],'native_receipts_equal':[r['receipt']for r in m['requests']]==[r['receipt']for r in baseline['requests']]};put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'comparison':m['baseline_comparison'],'edited':[(r['role'],r['pre']['direction'],r['pre']['s_reg'])for r in rows]}),flush=True)
if __name__=='__main__':main()
