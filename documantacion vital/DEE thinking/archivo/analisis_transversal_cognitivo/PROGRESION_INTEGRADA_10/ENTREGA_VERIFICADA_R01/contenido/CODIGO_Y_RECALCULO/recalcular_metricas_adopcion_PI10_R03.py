"""Passive actual panel/utility metrics; never executes a test or approves.

--panel CLOSED_OWNER.json --salida NEW.json. Refuses unfinished proof and
changed fixed panel. Expected13/8 remain evaluator-only. Second subtraction
must receive the first ACTUAL integer, even when wrong; NULL is retained as
dependent abstention, never expected13. No DOCX/product/Native import.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
FIXED=H/'PANEL_HEREDADO_12_PI10_R03_PASOS.json'
COMPARISON=P/'fuentes/CONTRASTE_REAL_NONE12_PI10_R02.json'
REAL=P/'fuentes/RECALCULO_REAL2_12_PI10_R03.json'
YOKE=P/'fuentes/CONTRASTE_TRES_BRAZOS12_PI10_R02.json'
CUT=P/'fuentes/CONTRASTE_CUT_SHAM_PI10_R02.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):p=Path(p).resolve(strict=True);return {'path':str(p),'sha256':sha(p)}
def bounded(p):
 p=Path(p).resolve(strict=True);need(p.is_relative_to(P.resolve())and p.is_file(),'Actual file under P10 required');return p
def at(v,path):
 for key in path:v=v[key]
 return v
def score(panel):
 proof=read(panel);fixed=read(FIXED)
 need(proof.get('closed')is True and proof.get('error')is None and proof.get('life_id')==LIFE,'Only actual closed successful REAL2 panel')
 planfile=bounded(proof['plan']);plan=read(planfile);need(sha(planfile)==proof['plan_sha256']and plan['steps']==fixed['steps'],'Actual driver plan must equal fixed exact P9-derived thirteen steps')
 need([s['label']for s in fixed['steps']]==['habitat_off','luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','number13','number8','alfa_after','luma_after'],'Fixed panel labels/order required')
 records=proof['records'];need(len(records)==len(fixed['steps'])and[len({r['label']for r in records})][0]==len(records),'All13 fixed records exactly once')
 need([r['label']for r in records]==[s['label']for s in fixed['steps']],'Actual panel order differs')
 rows=[];by={}
 for step,r in zip(fixed['steps'],records):
  need(r['expected']==step.get('expected')if'expected'in step else'expected'not in r,'Expected value differs from frozen plan')
  if 'expected'not in step:
   need(r['literal']==step['literal']and r['ticks']==0,'Only declared habitat pause is unscored, zero tick');continue
  dependent=r.get('no_Native_request')is True
  if dependent:
   need(step['label']=='number8'and r.get('status')=='DEPENDENT_ABSTENTION_NONINTEGER_ACTUAL'and r['ticks']==0 and type(by['number13']['actual'])is not int,'Only declared dependent noninteger abstention may omit a Native request');actual=None;primary=None
  else:
   primary=bounded(r['primary']);need(sha(primary)==r['sha256'],'Actual immutable panel primary changed');outer=read(primary);actual=at(outer,step['read_path'])
  formed=type(actual)is int;correct=formed and actual==step['expected']
  need(r.get('actual')==actual and r.get('correct')is correct,'Driver scoring and independent fixed-path extraction differ')
  literal=dict(step['literal'])
  if step.get('actual_integer_binding'):
   binding=step['actual_integer_binding'];prior=by[binding['from_step']];br=r.get('binding',{})
   need(br.get('actual')==prior['actual']and br.get('source_id')==prior['transport_id']and br.get('expected_used')is False,'Actual integer provenance required; no expected-value substitution')
   if not dependent:need(type(prior['actual'])is int,'Only actual integer may be transported');literal[binding['field']]=prior['actual']
  need(r['literal']==literal,'Actual literal differs from fixed input/transduced actual result')
  item={'label':r['label'],'actual':actual,'expected_auditor_only':step['expected'],'formed_integer':formed,'is_NULL':actual is None,'correct':correct,'dependent_abstention':dependent,'read_path':step['read_path'],'literal':r['literal'],'transport_id':r['id'],'before_tick':r['before_tick'],'after_tick':r['after_tick'],'primary':None if primary is None else info(primary)}
  rows.append(item);by[item['label']]=item
 core=[by[x]for x in fixed['coverage']['critical_core10']];numeric=[by[x]for x in fixed['coverage']['numeric2']]
 need(len(core)==10 and len(numeric)==2 and set(by)=={s['label']for s in fixed['steps']if'expected'in s},'Exact10core+2numeric denominators')
 utility=read(COMPARISON);real=read(REAL);samples=real['rows'];need(len(samples)==12 and all(r['life_id']==LIFE and r['arm']=='real'and not r['calibration']for r in samples),'Actual Real12 primary recalc required')
 by_ord={r['ordinal']:r for r in samples}
 # Prospectively chosen A/B/A' boundary cases, not a search for a good reader.
 bypass=by_ord[4]['returned_failed']is True and by_ord[4]['q1_before']==0 and by_ord[4]['q1_after']==-1 and all(by_ord[x]['regime']=='bypass'and by_ord[x]['q1_valid']and by_ord[x]['q1_STATE']==1 and by_ord[x]['actual_preview_bit']==1 and not by_ord[x]['query_requested']and by_ord[x]['attributed_useful']for x in(5,7))
 returned=by_ord[8]['returned_failed']is True and by_ord[8]['q1_before']==-1 and by_ord[8]['q1_after']==0 and by_ord[10]['regime']=='need_return'and by_ord[10]['q1_valid']and by_ord[10]['actual_preview_bit']==1 and by_ord[10]['query_requested']and by_ord[10]['attributed_useful']
 operational_uncertainty=not(proof.get('closed')is True and proof.get('error')is None and proof['final_saved_Native']['pending_native']==0 and proof['protected_before']==proof['protected_after'])
 metrics={'reserved_attributed_gain':utility['reserved_attributed_gain'],'total_physical_gain':utility['whole_physical_gain'],'core_requested':len(core),'core_responded':sum(r['formed_integer']for r in core),'core_correct':sum(r['correct']for r in core),'numerical_requested':len(numeric),'numerical_formed':sum(r['formed_integer']for r in numeric),'numerical_correct':sum(r['correct']for r in numeric),'numerical_incorrect':sum(r['formed_integer']and not r['correct']for r in numeric),'useful_revision_bypass':bool(bypass),'useful_return_to_query':bool(returned),'operational_uncertainty':operational_uncertainty,'additional_actual_arithmetic_correct':False}
 conservation=metrics['core_requested']==metrics['core_responded']==metrics['core_correct']==10 and metrics['numerical_requested']==metrics['numerical_formed']==2 and(metrics['numerical_correct']==2 or(metrics['reserved_attributed_gain']>=3 and metrics['numerical_correct']==1 and metrics['numerical_incorrect']==1 and metrics['additional_actual_arithmetic_correct']))
 return {'schema':'DEE.PI10.actual_adoption_science_metrics.R03','recorded_utc':datetime.now(timezone.utc).isoformat(),'Native_executed':False,'DEE_imported':False,'automatic_approval':False,'measured_adoption_metrics':metrics,'scored_panel':{'life_id':LIFE,'initial_tick':proof['initial_tick'],'final_tick':proof['final_tick'],'actual_Native_ticks':proof['new_Native_ticks'],'core10_labels':fixed['coverage']['critical_core10'],'numerical2_labels':fixed['coverage']['numeric2'],'scored12':rows,'frozen_exact_conservation_gate_met':bool(conservation),'NULL_is_not_formed_numerical_loss':True,'second_operand_is_actual_not_expected':True,'panel_at_this_cut_not_a_second_panel_at_a_later_final_tick':True},'actual_evidence':[info(x)for x in(panel,FIXED,planfile,COMPARISON,REAL,YOKE,CUT)],'causal_qualification':{'cut_sham_local_trace_effect':read(CUT)['formed_choice_same_before_first_barrier']and read(CUT)['all_q2_and_FI_stable'],'true_contingency_advantage_not_demonstrated':read(YOKE)['reserved_gain_vs_yoked']==0,'preserve_adverse_yoke_and_R01_failure':True},'remaining_separate_gates':['Actual useful new function after reopening at final cut','Full coherent source zero reopening','Root explicit adoption decision and same-ID whole-state move','Actual committed public use if adopted']}
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();need(not a.salida.exists(),'Prior proof preserved');v=score(bounded(a.panel));a.salida.parent.mkdir(parents=True,exist_ok=True)
 with a.salida.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':info(a.salida),'measured_adoption_metrics':v['measured_adoption_metrics'],'frozen_conservation_gate_met':v['scored_panel']['frozen_exact_conservation_gate_met'],'Native':0},ensure_ascii=False))
