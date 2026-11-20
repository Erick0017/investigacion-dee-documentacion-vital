"""Published K65 physical-form reference on official4.5, not NSMmeaning.

Native preparation N131 uses period131. The32+33 exposures, signopposite
history, teacher controls and finite L01revision are explicit instruments.
Expected mappings below are auditor/teacher fixtures, never participant memory.
"""
import argparse,hashlib,json,sys
from array import array
from pathlib import Path
import dee_thinking
from dee_thinking.consolidated import RepertoireSession
ROOT=Path(__file__).resolve().parents[1]
def physical(s):
 r=s.world.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);mode='paired'if case not in('K65_NO_SYMBOL','K65_UNPAIRED')else('no_symbol'if case=='K65_NO_SYMBOL'else'unpaired');sign=-1 if case=='K65_OPPOSITE'else 1;translation=(3,5,7)if case=='K65_RESERVE'else(0,0,0)
 observations={f'L{i+1:02d}':sign*(1 if (i*7+i//4)%3 else-1)for i in range(65)}
 cfg={'case_id':case,'count':65,'N':131,'period':131,'first_block':32,'second_block':33,'first_teaching_tick':0,'second_teaching_tick':262,'all_query_ticks':[393,524,655],'mode':mode,'translation':translation,'frozen_before_create':True,'claim':'65opaqueform/direction correspondences, not65NSMprimitives','auditor_teacher_fixture':observations}
 (out/'CONFIG.json').write_text(json.dumps(cfg,indent=2)+'\n',encoding='utf-8');s=RepertoireSession.create(count=65,dimension=131,translation=translation,identifier=case);assert s.dimension==131
 s.acquire_block(dict(list(observations.items())[:32]),0,mode=mode);s.save(out/'T0.deetsnap.gz',compress=True)
 first=s.query(list(observations)[:32],131);s.acquire_block(dict(list(observations.items())[32:]),262,mode=mode);s.run_until(265);s.save(out/'T265.deetsnap.gz',compress=True);rows=[]
 for tick in(393,524,655):
  q=s.query(list(observations),tick);rows.append({'input_tick':tick,'captured':q,'auditor_correct':sum(bool(r['covered'])and r['value']==observations[r['form']]for r in q['responses']),'denominator':65,'physical':physical(s)})
  if tick in(393,655):s.save(out/f'T{tick+3}.deetsnap.gz',compress=True)
 revision=None
 if case in('K65_PAIRED','K65_RESERVE'):
  before=dict(observations);new=-before['L01'];s.revise('L01',new,786,method='double_teacher');q=s.query(list(observations),917);target={**before,'L01':new};revision={'teaching_tick':786,'query_tick':917,'captured':q,'auditor_revised_correct':q['responses'][0]['covered']and q['responses'][0]['value']==new,'auditor_other_correct':sum(bool(r['covered'])and r['value']==target[r['form']]for r in q['responses'][1:]),'other_denominator':64,'method':'Published double_teacher, explicit additional doses; not arbitraryresource-freeoverwrite'};s.save(out/'T920.deetsnap.gz',compress=True)
 m={'schema':'CPC8R.K65published.reference.v1','case_id':case,'reference_reproductions':1,'fresh_preparations':1,'new_semantic_individuals':0,'configuration':cfg,'instrument':{'version':dee_thinking.__version__,'import':dee_thinking.__file__},'first32query':first,'all65queries':rows,'revision':revision,'inputs':s.journal,'final':physical(s),'MAIN_RAW_clock_edits':[]}
 (out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'case':case,'correct':[r['auditor_correct']for r in rows],'revision':None if revision is None else{k:revision[k]for k in('auditor_revised_correct','auditor_other_correct','other_denominator')}}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--case',choices=['K65_PAIRED','K65_OPPOSITE','K65_NO_SYMBOL','K65_UNPAIRED','K65_RESERVE'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
