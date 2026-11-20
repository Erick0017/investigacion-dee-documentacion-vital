"""Auditor-only exact recomputation; never imported by native participants."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def calculate(folder):
 rows=[]
 for p in sorted(folder.glob('Q*/MEASUREMENTS.json')):
  m=json.loads(p.read_text(encoding='utf-8'));rs=[]
  for c in m.get('calculations',[]):
   o=c['raw_reading'];qualified=o['active']and o['state']==1 and o['semantic']==1 and o['s_reg']==7
   rs.append({'tick':c['tick'],'direction_field_equal':c['correct_direction'],'active_reader_output':qualified,'reference_preserved':c['acquired_reference_available'],
    'functional_comparison_correct':qualified and c['acquired_reference_available']and c['correct_direction'],
    'valid_equality_not_absence':qualified and c['acquired_reference_available']and o['direction']==[0,0,0],
    'locator':p.relative_to(ROOT).as_posix()+'#/calculations/'+str(len(rs))})
  if rs:rows.append({'case_id':m['case_id'],'denominator':len(rs),'correct_with_reference':sum(x['functional_comparison_correct']for x in rs),'readings':rs})
 return{'schema':'CPC8R.quantity.recalculation.v1','formula':'functional_correct = active and state1 and semantic1 and s_reg7 and acquired_reference_available and observed_direction==sign(reference-current)X. A matching direction in RAW0 is never counted.',
  'unit':'One defined reading in one separately identified life; historical pilots not pooled into MAIN or independent statistical replicas.','cases':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(calculate(ROOT/'resultados/cantidad'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
