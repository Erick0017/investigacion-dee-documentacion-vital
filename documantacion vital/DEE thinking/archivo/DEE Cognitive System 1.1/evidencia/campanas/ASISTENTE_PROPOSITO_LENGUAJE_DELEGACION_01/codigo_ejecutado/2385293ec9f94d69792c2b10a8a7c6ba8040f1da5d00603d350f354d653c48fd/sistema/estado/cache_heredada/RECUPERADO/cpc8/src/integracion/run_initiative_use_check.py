"""Integrated return necessity, byte-exact continuation and a new physical query."""
import argparse,json,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.initiative_use_e1 import InitiativeUseE1Session
from integracion.relational_pair import physical,move
from integracion.run_longitudinal_e1 import sha,put
from dee_thinking import _native as d
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pp=ROOT/'resultados/integracion'/case['parent_id']/case['snapshot'];psha=sha(pp);parent=InitiativeUseE1Session.load(pp);rows=[]
 if case['kind']=='fork':
  parent.run_until(87);before=physical(parent.world);edits=[]
  for b in parent.geometry['initiative']['branches']:
   for value,effect in b['effects'].items():
    q=move(effect['return_site'],effect['return_direction']);pre=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=0 if case['mode']=='cut'else int(pre['raw']);e.label='Late native-return '+case['mode'];edits.append(e);rows.append({'candidate':value,'site':q,'pre':pre,'requested_raw':str(e.raw),'clock_edit':None})
  child=parent.world.diagnostic_fork(edits,True);state=deepcopy(parent.state)
  for key in('mode','quantity','initiative'):state[key]=deepcopy(getattr(parent,key).state)
  s=InitiativeUseE1Session(child,parent.geometry,state,parent.identifier+'.'+case['id'])
  for row in rows:row['post']=s.observe(row['site'])
 else:s=parent;before=physical(parent.world)
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('initiative_use_e1.py','initiative_e1.py','contact_renewal_e1.py','longitudinal_e1.py','complete_e1.py','quantity_core.py','relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/iniciativa_accion/solicitud.py',ROOT/'src/iniciativa_accion/return_use.py',ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 m={'schema':'CPC8R.initiativeUseE1.causal_restore.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'saved_tick':86,'start_tick':s.tick},'preparations':0,'continuations':int(case['kind']=='restore'),'technical_reproductions':int(case['kind']=='restore'),'diagnostic_forks':int(case['kind']=='fork'),'edited_sites':rows,'start_physical':before,'host_RAW_clock_edits_on_MAIN':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
 inherited={r['id']for r in s.receipts()}
 for tick in(88,89,90,338,405,411,415,428,436,472,478,539,549):
  s.run_until(tick);m['frames'].append(s.view())
  if tick in(88,89,90):
   for rx in s.geometry['initiative']['return_use']['items']:m['windows'].append({'tick':tick,'center':rx['meeting_site'],'Moore27':[s.observe(move(rx['meeting_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  m.update(last_complete_tick=s.tick,requests=sorted(s.receipts(),key=lambda r:r['id']),elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 m['continued_physical549']=physical(s.world);m['continued_native_receipts549']=[r['receipt']for r in sorted(s.receipts(),key=lambda r:r['id'])]
 if case['kind']=='restore':
  m['new_query_prediction_before_target']={'call_tick':549,'input_tick':613,'target_tick':616,'reader':'active semantic1(0,+1,+1) beyondprobe13, allfixedwordbanksqueried; no history-based selection'}
  for q in s.geometry['joint_names'].values():s.input(q['query_port'],13,613,'probe','NEW_QUERY_AFTER_EXACT_WHOLELIFE_RESTORATION_NO_RETEACHING')
  for tick in(613,615,616):s.run_until(tick);m['frames'].append(s.view())
 target=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(target);m['snapshots'].append({'path':target.name,'tick':s.tick,'sha256':sha(target),'physical':physical(s.world),'storage':storage})
 # Audit only AFTER both native trajectories and the new predeclared interaction.
 baseline=json.loads((pp.parent/'MEASUREMENTS.json').read_text(encoding='utf8'));m['baseline_comparison549']={'full_physical_equal':m['continued_physical549']==baseline['final_physical'],'native_receipts_equal':m['continued_native_receipts549']==[r['receipt']for r in baseline['requests']]};m.update(status='MEASURED',final_physical=physical(s.world),requests=sorted(s.receipts(),key=lambda r:r['id']),new_requests=[r for r in s.receipts()if r['id']not in inherited],return_use_observations=s.state['return_use_observations'],renewal_observations=s.state['renewal_observations'],initiative_captures=s.initiative.state['captures'],social_captures=s.mode.state.get('social_captures',[]),quantity_observations=s.quantity.state['observations'],parent_file_sha256_after=sha(pp));m['parent_file_unchanged']=psha==m['parent_file_sha256_after']
 if case['kind']=='fork':m['unmodified_parent_physical_equal']=physical(parent.world)==before
 put(a.out/'MEASUREMENTS.json',m);print(json.dumps({'id':case['id'],'comparison549':m['baseline_comparison549'],'use89':next(f['return_use']for f in m['frames']if f['tick']==89),'finalword':[(k,v['delivery_site']['direction'],v['delivery_site']['s_reg'])for k,v in m['frames'][-1]['joint'].items()]}),flush=True)
if __name__=='__main__':main()
