"""Published K65 physical-form reference on official4.5, not NSMmeaning.

Native preparation N131 uses period131. The32+33 exposures, signopposite
history, teacher controls and finite L01revision are explicit instruments.
Expected mappings below are auditor/teacher fixtures, never participant memory.
"""
import argparse,hashlib,json,sys,shutil
from array import array
from pathlib import Path
import dee_thinking
from dee_thinking.consolidated import RepertoireSession
ROOT=Path(__file__).resolve().parents[1]
def physical(s):
 r=s.world.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def run(case,out,resume=None):
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'EXECUTED_SOURCE.py');mode='no_symbol'if case.startswith('K65_NO_SYMBOL')else('unpaired'if case.startswith('K65_UNPAIRED')else'paired');sign=-1 if case=='K65_OPPOSITE'else 1;translation=(3,5,7)if case=='K65_RESERVE'else(0,0,0)
 observations={f'L{i+1:02d}':sign*(1 if (i*7+i//4)%3 else-1)for i in range(65)}
 revision_cohort=case in('K65_REVISION_CADENCE','K65_REVISION_OFFPATH');low_eval=case.endswith('_LOW_EVAL');ticks=(131,262,393)if revision_cohort else(393,524,655)
 cfg={'case_id':case,'count':65,'N':131,'period':131,'first_block':65 if revision_cohort else 32,'second_block':0 if revision_cohort else 33,'first_teaching_tick':0,'second_teaching_tick':None if revision_cohort else 262,'all_query_ticks':ticks,'mode':mode,'translation':translation,'frozen_before_create':True,'claim':'65opaqueform/direction correspondences, not65NSMprimitives','auditor_teacher_fixture':observations,'resume_same_life':str(resume)if resume else None}
 (out/'CONFIG.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8');rows=[];first=None
 def score(q,phase_physical):
  return{'input_tick':q['input_tick'],'captured':q,'auditor_correct':sum(bool(r['covered'])and r['value']==observations[r['form']]for r in q['responses']),'denominator':65,'physical':phase_physical}
 if resume:
  s=RepertoireSession.load(resume);assert s.dimension==131 and s.tick==658
  queries=s.queries;first=queries[0]['captured'];rows=[score(q['captured'],physical(s)if q['input_tick']==655 else None)for q in queries[1:]]
 else:
  s=RepertoireSession.create(count=65,dimension=131,translation=translation,identifier=case);assert s.dimension==131
  s.acquire_block(observations if revision_cohort else dict(list(observations.items())[:32]),0,mode=mode);s.save(out/'T0.deetsnap.gz',compress=True)
  if not revision_cohort:
   if not low_eval:first=s.query(list(observations)[:32],131)
   s.acquire_block(dict(list(observations.items())[32:]),262,mode=mode);s.run_until(265);s.save(out/'T265.deetsnap.gz',compress=True)
  for tick in ticks:
   q=s.query(list(observations),tick);rows.append(score(q,physical(s)))
   if tick in(393,655):s.save(out/f'T{tick+3}.deetsnap.gz',compress=True)
 revision=None
 if resume:revision={'status':'PRIOR_API_REJECTION_PRESERVED','attempted_tick':786,'reason':'revision outside published finite cadence','old_stdout_stderr':'jobs/base_k65_paired','scope':'No physical revision result inferred from rejected API call. Queries recovered exactly from T658metadata, not re-taught.'}
 if revision_cohort:
  before=dict(observations);new=-before['L01'];start=physical(s)
  try:
   s.revise('L01',new,524,method='double_teacher',mode='offpath_sham'if case=='K65_REVISION_OFFPATH'else'treatment');q=s.query(list(observations),655);target={**before,'L01':new};revision={'status':'EXECUTED','teaching_tick':524,'query_tick':655,'captured':q,'auditor_revised_correct':q['responses'][0]['covered']and q['responses'][0]['value']==new,'auditor_other_correct':sum(bool(r['covered'])and r['value']==target[r['form']]for r in q['responses'][1:]),'other_denominator':64,'method':'Published double_teacher at4N, explicit additional doses and same-dose offpath control; no resource-freeoverwrite'};s.save(out/'T658.deetsnap.gz',compress=True)
  except ValueError as e:revision={'status':'API_REJECTED','reason':str(e),'unchanged_physical':physical(s)==start,'cadence_requested':524,'scope':'Instrument domain, not a failed physical learning trial'}
 m={'schema':'CPC8R.K65published.reference.v2','case_id':case,'reference_reproductions':1,'fresh_preparations':0 if resume else 1,'continuations':1 if resume else 0,'new_semantic_individuals':0,'configuration':cfg,'instrument':{'version':dee_thinking.__version__,'import':dee_thinking.__file__},'first32query':first,'all65queries':rows,'revision':revision,'inputs':s.journal,'final':physical(s),'MAIN_RAW_clock_edits':[]}
 (out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'case':case,'correct':[r['auditor_correct']for r in rows],'revision':None if revision is None else{k:revision.get(k)for k in('status','auditor_revised_correct','auditor_other_correct','other_denominator')}}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['K65_PAIRED','K65_OPPOSITE','K65_NO_SYMBOL','K65_UNPAIRED','K65_RESERVE','K65_REVISION_CADENCE','K65_REVISION_OFFPATH','K65_NO_SYMBOL_LOW_EVAL','K65_UNPAIRED_LOW_EVAL'],required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--resume',type=Path);a=p.parse_args();run(a.case,a.out,a.resume)
