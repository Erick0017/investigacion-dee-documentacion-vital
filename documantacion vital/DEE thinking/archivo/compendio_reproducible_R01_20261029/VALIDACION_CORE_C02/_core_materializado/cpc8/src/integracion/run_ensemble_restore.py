"""Restore in a new process, verify existing future, then issue a new actual query."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_ensemble import EnsembleSession
from integracion.relational_pair import physical,move
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 pp=ROOT/'resultados/integracion'/case['parent_id']/case['snapshot'];parent_sha=sha(pp);s=EnsembleSession.load(pp)
 src=a.out/'executed_source';src.mkdir();paths=[Path(__file__),ROOT/'src/integracion/relational_ensemble.py',ROOT/'src/integracion/relational_pair.py',ROOT/'src/integracion/relational_pair_v2.py',ROOT/'src/relaciones/mode_reference.py']
 for path in paths:shutil.copyfile(path,src/path.name)
 m={'schema':'CPC8R.ensemble.restoration.measurements.v1','case':case,'parent':{'path':str(pp.relative_to(ROOT)),'sha256':parent_sha,'tick':s.tick},'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'preparations':0,'continuations':1,'diagnostic_forks':0,'host_RAW_clock_edits_on_MAIN':[],'status':'RUNNING','frames':[],'windows':[],'snapshots':[]}
 s.run_until(348);m['continuation_physical']=physical(s.world);m['continuation_receipts']=s.receipts();m['frames'].append(s.view())
 # Audit after evolution, never read by the participant or used to select inputs.
 baseline=json.loads((pp.parent/'MEASUREMENTS.json').read_text(encoding='utf8'));m['comparison348']={'physical_arrays_tick_equal':m['continuation_physical']==baseline['final_physical'],'all_receipts_equal':m['continuation_receipts']==baseline['requests'],'public_view_equal':m['frames'][0]==next(f for f in baseline['frames']if f['tick']==348)}
 m['new_query_prediction_before_target']={'emission_call_tick':s.tick,'target_tick':case['observe_tick'],'frozen_reader':'active semantic1 direction(0,+1,+1), load beyondquery; every candidate queried, no bank selected from history'}
 before={r['id']for r in s.receipts()}
 for q in s.geometry['joint_names'].values():s.input(q['query_port'],case['new_query_payload'],case['new_query_tick'],'probe','NEW_INTERLOCUTOR_QUERY_AFTER_RESTORATION')
 for tick in(case['new_query_tick'],case['observe_tick']-1,case['observe_tick']):
  s.run_until(tick);m['frames'].append(s.view())
  for q in s.geometry['joint_names'].values():m['windows'].append({'tick':tick,'center':q['delivery_site'],'Moore27':[s.observe(move(q['delivery_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
 final=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(final);m.update(status='MEASURED',requests=s.receipts(),new_requests=[r for r in s.receipts()if r['id']not in before],final_physical=physical(s.world),elapsed_seconds=time.monotonic()-start,parent_snapshot_after_sha256=sha(pp));m['snapshots'].append({'path':final.name,'sha256':sha(final),'tick':s.tick,'storage':storage});m['parent_file_unchanged']=parent_sha==m['parent_snapshot_after_sha256'];put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'comparison348':m['comparison348'],'word415':{k:v['delivery_site']for k,v in m['frames'][-1]['joint'].items()},'parent_unchanged':m['parent_file_unchanged']}),flush=True)
if __name__=='__main__':main()
