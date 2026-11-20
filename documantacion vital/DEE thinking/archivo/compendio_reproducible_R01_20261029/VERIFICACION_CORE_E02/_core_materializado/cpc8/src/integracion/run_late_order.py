"""Late actual events on unchanged sensors; no reopening of occupied matter."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_guarded_v2 import GuardedV2Session
from integracion.relational_pair import physical,move
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pp=ROOT/'resultados/integracion'/cfg['parent_id']/cfg['snapshot'];psha=sha(pp);s=GuardedV2Session.load(pp)
 src=a.out/'executed_source';src.mkdir();paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py']
 for path in paths:shutil.copyfile(path,src/path.name)
 before={r['id']for r in s.receipts()};m={'schema':'CPC8R.ensemble.late_order.measurements.v1','case':case,'configuration_sha256':sha(a.config),'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'tick':s.tick},'source_sha256':{x.name:sha(x)for x in paths},'preparations':0,'continuations':1,'diagnostic_forks':0,'host_RAW_clock_edits_on_MAIN':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
 if case['new_order'] is not None:
  for letter,tick in zip(case['new_order'],cfg['new_event_ticks']):s.input('order.'+letter,3,tick,origin='NEW_CURRENT_EVENT_ON_OLD_SENSOR_NO_TEACHING_MAP')
 s.input('order.read',7,cfg['read_tick'],'probe','EXPLICIT_COMMON_ORDER_READER_LATE')
 for q in s.geometry['joint_names'].values():s.input(q['query_port'],cfg['word_payload'],cfg['word_query_tick'],'probe','OLD_COMPOSITE_WORD_QUERY_AFTER_NEW_EVENTS_NO_RETEACHING')
 m['prediction_before_targets']={'call_tick':s.tick,'order_target':cfg['emission_tick'],'word_target':cfg['word_target_tick'],'scope':'Attempt new current order measurement without target assumptions; prior word frozen decoder(0,+1,+1) beyondquery.'}
 for tick in(468,469,470,471,472,474,475,478,479,481,482):
  s.run_until(tick);m['frames'].append(s.view());centers=list(s.geometry['body'].values())if tick<=475 else[q['delivery_site']for q in s.geometry['joint_names'].values()]
  for q in centers:m['windows'].append({'tick':tick,'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  m.update(last_complete_tick=s.tick,requests=s.receipts(),new_requests=[r for r in s.receipts()if r['id']not in before],elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 target=a.out/'T482.deetsnap.gz';storage=s.save(target);m['snapshots'].append({'path':target.name,'sha256':sha(target),'tick':s.tick,'storage':storage});m.update(status='MEASURED',final_physical=physical(s.world),parent_sha256_after=sha(pp));m['parent_file_unchanged']=psha==m['parent_sha256_after'];put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'new_requests':[(r['port'],r['receipt']['status'])for r in m['new_requests']],'emission475':next(f for f in m['frames']if f['tick']==475)['body']['emission'],'word482':{k:v['delivery_site']for k,v in m['frames'][-1]['joint'].items()}}),flush=True)
if __name__=='__main__':main()
