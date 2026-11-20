"""Aggregate explicit closed phase proofs without creating a fictitious Owner.

Pure documentary calculation: no DEE, Native, database, process or execution.
Evaluation requires the exact twelve unforced REAL2 episodes0..11. Conservation
preserves records with an explicit external observer comparison, including
errors. All actual Native ticks across the supplied phases are retained.
No output is created until every source/primary and phase boundary validates.
"""
from pathlib import Path
import argparse,hashlib,json

P=Path(__file__).resolve().parents[1]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
PHASE_SCHEMA='DEE.PI10.actual.finite_owner_plan.R01'
SCHEMA='DEE.PI10.actual_composite_closed_trajectory.R02'
EP='eci01-pi10-episodio'
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def bounded(path):
 path=Path(path)
 for node in(path,*path.parents):need(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked/reparse source')
 resolved=path.resolve(strict=True);need(resolved.is_relative_to(P.resolve())and resolved.is_file(),'Explicit existing PI10 file only');return resolved
def unpack_result(primary):
 need(primary.get('status')=='completed'and primary.get('error')is None,'Actual completed immutable primary required')
 v=primary['result'];return json.loads(v)if isinstance(v,str)else v
def verify_primary(record,life,retained):
 if record.get('no_Native_request')is True:
  need(record['ticks']==0 and record['before_tick']==record['after_tick'],'Prequeue rejection may not manufacture a Native use')
  return {'no_Native_request':True}
 file=bounded(record['primary']);b=file.read_bytes();need(sha(b)==record['sha256'],'Original primary SHA changed')
 outer=unpack_result(json.loads(b));need(outer['before_tick']==record['before_tick']and outer['after_tick']==record['after_tick'],'Original primary Native interval differs')
 need(outer.get('result',{}).get('rows',[])==record.get('rows',[]),'Phase rows differ from original primary')
 if 'committed_snapshot'in outer:need(outer['committed_snapshot']['life_id']==life,'Primary belongs to a different physical life')
 retained.append((file,b));return {'file':str(file),'bytes':len(b),'sha256':sha(b),'owner_epoch':outer.get('owner_epoch')}
def aggregate(paths,mode,expected_conservation_count=None):
 need(len(paths)>=1,'At least one actual closed phase')
 if mode=='evaluacion':need(len(paths)>=2,'Split Real12 requires its two or more actual closed phases; never emit from F0 alone')
 retained=[];phases=[];selected=[];provenance=[];unselected=[];all_ids=set();previous=None;all_request_ids=set();episode_native_requests=0
 for phase_index,path in enumerate(paths):
  file=bounded(path);b=file.read_bytes();v=json.loads(b)
  need(v.get('schema')==PHASE_SCHEMA and v.get('closed')is True and v.get('error')is None and v.get('life_id')==LIFE,'Every original exact REAL2 phase must be closed without error')
  need(v.get('protected_before')==v.get('protected_after'),'Original phase protection witness differs')
  before=v['initial_saved_Native'];after=v['final_saved_Native']
  need(before['physical']['tick']==v['initial_tick']and after['physical']['tick']==v['final_tick']and v['new_Native_ticks']==v['final_tick']-v['initial_tick']and v['new_Native_ticks']>=0,'Actual phase ticks disagree with saved Native endpoints')
  if previous is not None:
   need(previous['final_tick']==v['initial_tick'],'A Native interval between phases is missing; do not invent zero ticks')
   need(previous['final_saved_Native']['physical']==before['physical'],'Whole RAW/clocks physical boundary differs between phases')
   need(previous['final_saved_Native']['causal_prefix_sha256']==before['causal_prefix_sha256'],'Native interfaces/agenda/receipts boundary differs; retain and diagnose')
  cursor=v['initial_tick'];phase_selected=[];phase_other_ticks=0
  for record_index,record in enumerate(v['records']):
   ident=record['id'];need(ident not in all_ids,'Repeated transport record is not a second execution');all_ids.add(ident)
   need(record['before_tick']==cursor and record['after_tick']>=cursor and record['ticks']==record['after_tick']-record['before_tick'],'Original records must cover their phase in order')
   cursor=record['after_tick'];primary=verify_primary(record,LIFE,retained)
   use=record.get('literal',{}).get('modo')==EP if mode=='evaluacion'else record.get('correct')is not None
   if use:
    need(not record.get('no_Native_request'),'A prequeue rejection cannot count as a capacity use')
    if mode=='evaluacion':
     need(len(record.get('rows',[]))==1,'One actual episode row per evaluation request');row=record['rows'][0]
     need(row.get('version')=='DEE.PI10.adaptive_query.two_native_traces.R02'and row.get('life_id')==LIFE and row.get('operator_calibration')is False and row.get('feedback_arm')=='real'and row.get('trace_control')=='none','Only native unforced REAL2 evaluation history')
     need(row.get('Native_inputs',{}).get('all_terminal')is True,'Completed terminal receipt set required')
     request_ids={r['id']for r in row['requests']};need(not(all_request_ids&request_ids),'A Native ID was reused across distinct same-life episodes');all_request_ids|=request_ids;episode_native_requests+=row['Native_inputs']['unique_requested']
     need(len(request_ids)==row['Native_inputs']['unique_requested'],'Episode request denominator differs')
     phase_selected.append(row['ordinal'])
    else:need(type(record['correct'])is bool,'Actual external comparison is a Boolean, not an inferred score')
    selected.append(record);provenance.append({'aggregate_index':len(selected)-1,'phase_index':phase_index,'original_record_index':record_index,'original_id':ident,'original_primary':primary})
   else:
    phase_other_ticks+=record['ticks'];unselected.append({'phase_index':phase_index,'original_record_index':record_index,'id':ident,'label':record.get('label'),'literal':record.get('literal'),'before_tick':record['before_tick'],'after_tick':record['after_tick'],'ticks':record['ticks'],'primary':primary})
  need(cursor==v['final_tick'],'Phase has unaccounted Native advancement outside its records')
  phases.append({'file':str(file),'bytes':len(b),'sha256':sha(b),'schema':v['schema'],'tag':v.get('tag'),'life_id':v['life_id'],'closed':True,'error':None,'initial_tick':v['initial_tick'],'final_tick':v['final_tick'],'new_Native_ticks':v['new_Native_ticks'],'initial_saved_Native':before,'final_saved_Native':after,'selected_ordinals':phase_selected,'other_record_Native_ticks':phase_other_ticks,'closed_process_queue':v.get('closed_process_queue')})
  retained.append((file,b));previous=v
 if mode=='evaluacion':
  ordinals=[r['rows'][0]['ordinal']for r in selected];need(ordinals==list(range(12)),'All original ordinals0..11, exactly once and in order, are required')
  need(all_request_ids and len(all_request_ids)==episode_native_requests,'Cross-episode Native request totals differ')
 else:
  need(selected,'No actual conservation comparisons exist')
  if expected_conservation_count is not None:need(len(selected)==expected_conservation_count,'Actual conservation denominator differs from supplied planned count')
 total=sum(v['new_Native_ticks']for v in phases);need(total==phases[-1]['final_tick']-phases[0]['initial_tick'],'Actual total Native time differs')
 need(all(path.read_bytes()==data for path,data in retained),'A closed source changed during documentary aggregation')
 return {'schema':SCHEMA,'mode':mode,'status':'COMPOSITE_OF_CLOSED_RECORDED_PHASES','life_id':LIFE,'closed':True,'error':None,'initial_tick':phases[0]['initial_tick'],'final_tick':phases[-1]['final_tick'],'new_Native_ticks':total,
  'initial_saved_Native':phases[0]['initial_saved_Native'],'final_saved_Native':phases[-1]['final_saved_Native'],'phases':phases,'records':selected,'record_provenance':provenance,'unselected_original_records':unselected,
  'correct':sum(r.get('correct')is True for r in selected)if mode=='conservacion'else None,'incorrect':sum(r.get('correct')is False for r in selected)if mode=='conservacion'else None,
  'Native_executed_by_aggregator':False,'new_ticks_by_aggregator':0,'original_phase_count':len(phases),'is_one_owner_proof':False,
  'scope':'Documentary aggregation of hashed original closed phase/primary records. No fabricated single Owner, no new execution and no tick-zero attribution. Original phase proofs and observer comparisons remain authoritative.'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--modo',choices=('evaluacion','conservacion'),required=True);ap.add_argument('--fase',type=Path,action='append',required=True);ap.add_argument('--cantidad-conservacion',type=int);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
 need(not a.salida.exists(),'Do not replace an earlier aggregate');need(a.salida.resolve().is_relative_to(P.resolve()),'New PI10 analysis destination only')
 value=aggregate(a.fase,a.modo,a.cantidad_conservacion);a.salida.parent.mkdir(parents=True,exist_ok=True)
 with a.salida.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'file':str(a.salida),'sha256':sha(a.salida.read_bytes()),'mode':a.modo,'phases':len(value['phases']),'records':len(value['records']),'original_Native_ticks':value['new_Native_ticks'],'Native_executed_by_aggregator':False}))
if __name__=='__main__':main()
