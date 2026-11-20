"""Bounded functional additive update while old composite word remains in MAIN."""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.complete_e1 import CompleteE1Session
from integracion.relational_pair import physical,move
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 t=p.with_name(p.name+'.pending');t.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);protocol=cfg['protocol'];a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 pp=ROOT/'resultados/integracion'/case['parent_id']/case['parent_snapshot'];psha=sha(pp);s=CompleteE1Session.load(pp);before_ids={r['id']for r in s.receipts()};initial=physical(s.world)
 paths=[Path(__file__)]+[ROOT/'src/integracion'/n for n in('complete_e1.py','quantity_core.py','relational_guarded_v2.py','relational_social.py','relational_ensemble.py','relational_pair_v2.py','relational_pair.py')]+[ROOT/'src/comunicacion/mode_communication.py',ROOT/'src/relaciones/mode_reference.py'];src=a.out/'executed_source';src.mkdir()
 for path in paths:shutil.copyfile(path,src/path.name)
 m={'schema':'CPC8R.completeE1.update.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{x.name:sha(x)for x in paths},'parent':{'path':str(pp.relative_to(ROOT)),'sha256':psha,'tick':s.tick,'loaded_physical':initial},'preparations':0,'continuations':1,'diagnostic_forks':0,'host_RAW_clock_edits_on_MAIN':[],'frames':[],'windows':[],'quantity_reads':[],'snapshots':[],'status':'RUNNING','prediction_recorded_before_targets':{'call_tick':s.tick,'hypothesis':cfg['before_target_hypothesis'],'criteria':cfg['decoders']}}
 if case['addition_mode']!='omitted':
  s.quantity.input('quantity.reference.cue',0,protocol['add_tick']+int(case['addition_mode']=='unpaired'));s.quantity.input('quantity.reference.resource',case['addition_value'],protocol['add_tick'])
 for value,index,tick in zip(protocol['actual_objects'],protocol['round_indices'],protocol['reader_ticks']):s.quantity.present_object(value,round_index=index);s.quantity.input('quantity.reader',7,tick,True)
 for q in s.geometry['joint_names'].values():s.input(q['query_port'],protocol['new_word_payload'],protocol['new_word_input_tick'],'probe','OLD_WORD_NEW_QUERY_AFTER_NEW_QUANTITY_NOT_RETEACHING')
 targets=set(protocol['read_targets']+protocol['old_word_target_ticks']+[protocol['add_contact_tick']]);boundaries={267,268,270,271,348,415,546,548,549}
 for t in targets:boundaries.update((t-1,t))
 for tick in sorted(t for t in boundaries if t>s.tick):
  s.run_until(tick);m['frames'].append(s.view());qg=s.geometry['quantity']
  if tick in targets or tick+1 in targets:
   m['quantity_reads'].append({'tick':tick,'center':s.quantity.observe(qg['center']),'reference_hub':s.quantity.observe(qg['reference_hub']),'reference_preoperand':s.quantity.observe(qg['reference_site']),'object_site':s.quantity.observe(qg['object_site']),'Moore27':[s.quantity.observe(move(qg['center'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  if tick in protocol['old_word_target_ticks']or tick+1 in protocol['old_word_target_ticks']:
   for q in s.geometry['joint_names'].values():m['windows'].append({'tick':tick,'center':q['delivery_site'],'Moore27':[s.observe(move(q['delivery_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  if tick in(271,348,415,539,549):
   target=a.out/('T'+str(tick)+'.deetsnap.gz');storage=s.save(target);m['snapshots'].append({'path':target.name,'sha256':sha(target),'tick':tick,'physical':physical(s.world),'storage':storage})
  m.update(last_complete_tick=s.tick,requests=s.receipts(),new_requests=[r for r in s.receipts()if r['id']not in before_ids],elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
 m.update(status='MEASURED',final_physical=physical(s.world),parent_sha256_after=sha(pp));m['parent_file_unchanged']=psha==m['parent_sha256_after'];put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'quantity':[(r['tick'],r['center']['direction'],r['center']['active'],r['center']['s_reg'],r['reference_hub']['s_reg'])for r in m['quantity_reads']if r['tick']in protocol['read_targets']],'oldword549':{k:v['delivery_site']for k,v in m['frames'][-1]['joint'].items()}}),flush=True)
if __name__=='__main__':main()
