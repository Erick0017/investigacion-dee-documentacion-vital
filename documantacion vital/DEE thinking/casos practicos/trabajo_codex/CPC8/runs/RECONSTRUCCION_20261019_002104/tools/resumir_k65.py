"""Recalculate finite published physical-form references; no semantic grading."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def source(p):
 f=ROOT/p
 return {'path':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def main():
 rows=[]
 for f in sorted((ROOT/'resultados/repertorio65_referencia').glob('*/MEASUREMENTS.json')):
  m=json.loads(f.read_text(encoding='utf8'));fixture=m['configuration']['auditor_teacher_fixture'];first=m.get('first32query');observed=[]
  for q in m['all65queries']:
   rs=q['captured']['responses'];n=sum(bool(r['covered'])and r['value']==fixture[r['form']]for r in rs)
   assert n==q['auditor_correct'] and len(rs)==65
   observed.append({'input_tick':q['input_tick'],'covered':sum(bool(r['covered'])for r in rs),'correct':n,'denominator':65,'first_read_of_all65':len(observed)==0})
  rows.append({'case':m['case_id'],'source':source(f.relative_to(ROOT).as_posix()),'fresh_preparations':m['fresh_preparations'],'continuations':m['continuations'],'first32_query':None if first is None else{'input_tick':first['input_tick'],'correct':sum(bool(r['covered'])and r['value']==fixture[r['form']]for r in first['responses']),'denominator':32},'all65queries':observed,'revision':m['revision'],'MAIN_member':False,'NSM_meanings_credited':0})
 lookup={r['case']:r for r in rows}
 pairs=[]
 for mode in ['NO_SYMBOL','UNPAIRED']:
  a=lookup['K65_'+mode];b=lookup['K65_'+mode+'_LOW_EVAL']
  pairs.append({'mode':mode,'single_protocol_difference':'LOW_EVAL omits early32 physical queries at131; same actual teaching/resource histories and remaining events','early32_first_read':a['first32_query'],'first_all65_with_early_queries':a['all65queries'][0],'first_all65_without_early_queries':b['all65queries'][0],'later_all65_with':a['all65queries'][1:],'later_all65_without':b['all65queries'][1:],'inference':'Early material probes change later accessible associations. Later65/65cannot be attributed exclusively to original paired teaching or passive retention. No hidden results-table is supplied to participant.'})
 result={'schema':'CPC8R.publishedK65.review.v1','domain':'Official4.5 RepertoireSession physical opaque-form/direction correspondences; N131, distinct from selected N67E1','cases':rows,'early_probe_controls':pairs,'partial_original_attempt':{'case':'K65_PAIRED','configuration':source('resultados/repertorio65_referencia/K65_PAIRED/CONFIG.json'),'snapshot':'resultados/repertorio65_referencia/K65_PAIRED/T658.deetsnap.gz','failure':'After3×65/65, revise786 raises ValueError outside published finite cadence. No MEASUREMENTS file was written. Recoveryloads this exact state and captured query records; no re-teaching or newpreparation.','recovery':'K65_PAIRED_RECOVER658','logs':'jobs/base_k65_paired','source_before_failed_call':source('resultados/repertorio65_referencia/K65_PAIRED/EXECUTED_SOURCE_BEFORE_CADENCE_CHECK.py')},'revision_protocol':'A DIFFERENT freshcohort teaches all65 atT0, queries131/262/393, then revisesL01at524(4N) andqueries655. This does not claim the rejected32+33/786protocol is supported. Extra double-teacher resources are explicit.','revision_treatment':lookup['K65_REVISION_CADENCE']['revision'],'revision_equal_dose_offpath':lookup['K65_REVISION_OFFPATH']['revision'],'unmodified_relations_note':'Treatment preserves64/64otherforms; offpathcontrol63/64. Offroute is not assumed inert merely because outside target route.','counts_scope':'Reference preps/continuations/replays only; no additional MAINknowledge or independent human semantic meanings. K65OPPOSITE changes actual teaching directions with fixed encoder/decoder. Reserve translates prepared geometry only, not semantic generalization.','recalculation_script':'tools/resumir_k65.py'}
 (ROOT/'revision/REPERTORIO65_REFERENCIA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'cases':len(rows),'early_probe_controls':pairs},ensure_ascii=False))
if __name__=='__main__':main()
