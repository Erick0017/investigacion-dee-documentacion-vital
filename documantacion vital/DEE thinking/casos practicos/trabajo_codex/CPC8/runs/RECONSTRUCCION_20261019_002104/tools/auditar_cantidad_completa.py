"""Pure data recalculation; no native engine, targets or logs fed to participant."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sign(x):return(x>0)-(x<0)
def pack(state,load,v,semantic=1):return state|(load<<32)|((v[0]&15)<<48)|((v[1]&15)<<52)|((v[2]&15)<<56)|(semantic<<60)
def run(out):
 base=ROOT/'resultados/cantidad';rows=[];kernel=[]
 for p in sorted(base.glob('QB_*/MEASUREMENTS.json')):
  m=read(p)
  if 'rounds'not in m:continue
  valid=[]
  for i,x in enumerate(m['rounds']):
   q=x['pre']['reference'];obj=x['pre']['object'];o=x['post']['center'];required=x['expected_reference_auditor_only'];s=m['config']['objects'][i]
   rawvalid=q['active']and q['s_reg']==required and q['direction']==[0,1,0]and obj['active']and obj['s_reg']==s and obj['direction']==[0,1,0]
   expected=[sign(required-s),0,0];correct=bool(rawvalid and o['raw']==str(pack(1,7,expected)))
   n=0;grad=[0,0,0];c=m['geometry']['center']
   for z in x['pre']['Moore27']:
    off=[((z['site'][j]-c[j]+33)%67)-33 for j in range(3)]
    if off==[0,0,0]:continue
    n+=bool(z['state']>0 and z['semantic']!=5)
    if z['state']>0:
     for j in range(3):grad[j]-=off[j]*z['s_reg']
   # No tetrahedral pattern in this published six-neighbor prepared geometry.
   rule=int(n*2.5/26+0.5);direction=[sign(v)for v in grad];predraw=pack(rule,7,direction)if rule else 0
   branch_match=str(predraw)==o['raw'];valid.append({'round':i,'tick':o['tick'],'raw_function_correct':correct,'reference_available':rawvalid,'expected_auditor_only':expected,'read_original':o,
    'locator':p.relative_to(ROOT).as_posix()+'#/rounds/'+str(i)})
   kernel.append({'case_id':m['case_id'],'round':i,'preclock':x['pre']['center']['clock'],'queued_probe_applied_before_transition':{'load':7,'state':1,'semantic':1,'direction':[0,0,1]},'neighbor_count':n,'gradient':grad,'rule_value_from_published_nonhadron_branch':rule,'reconstructed_post_raw':str(predraw),'observed_post_raw':o['raw'],'exact_match':branch_match,'scope':'Local material branch calculation; not a replacement simulation or proof of unrelated kernelbranches.'})
  rows.append({'case_id':m['case_id'],'correct':sum(x['raw_function_correct']for x in valid),'denominator':len(valid),'readings':valid})
 p=read(base/'QB_P01/MEASUREMENTS.json');c=read(base/'QB_C01/MEASUREMENTS.json');contrast=[{'round':i,'same_current_quantity':p['config']['objects'][i]==c['config']['objects'][i],'with_addition':p['rounds'][i]['post']['center'],'without_addition':c['rounds'][i]['post']['center'],'direction_changed':p['rounds'][i]['post']['center']['direction']!=c['rounds'][i]['post']['center']['direction']}for i in range(4,8)]
 a=read(base/'QB_RESTORE_273/MEASUREMENTS.json');b=read(base/'QB_RESTORE_541/MEASUREMENTS.json')
 result={'schema':'CPC8R.quantity.complete.audit.v1','formulas':{'physical_comparison':'Gx = reference_material - current_material; Gy=Gz=0 in the frozen six-neighbor geometry. A moving supplied reader obeys sign(G) under v27. Material references are actual post-T0 acquisition products.',
  'functional_correct':'Exact active RAW pack(state1,load7,sign(reference-current),0,0,semantic1) AND actual reference/object available at preboundary. A matching direction in RAW0 does not count.',
  'updated_reference':'At native contact271 reducer sums actual storedreference31+introduced11 =42. The sum is calculated only by the auditor after the trajectory; participant receives separate matter.',
  'cost':'8 scheduled reader opportunities,7 prepared supports including2interceptors, actual matter inputs and auxiliary experience. No energy claim.'},
 'cases':rows,'kernel_branch_reconstruction':kernel,'update_contrast':contrast,'postupdate_direction_changes':sum(x['direction_changed']for x in contrast),
 'restore':{'sources':[a['config']['source'],b['config']['source']],'physical541_equal':a['physical541']==b['physical541']==p['final'],'receipts541_equal':a['receipts541']==b['receipts541'],'final608_equal':a['final']==b['final'],'receipts608_equal':a['receipts_final']==b['receipts_final'],'channels_equal':a['channels']==b['channels'],'new_function_both':[a['qualified_new_function'],b['qualified_new_function']]},
 'semantic_limits':['Reference value acquired, comparison/gradient operation prepared.','These are separate component lives until expressly integrated in E1, not pooled knowledge.','Additive accumulation is not arbitrary selective overwrite.','Scalar equality is not identity of a referent.','QF postfunction form association has a positive first query but failed later access; no unlimited reusable word claim.','No subjective state, general arithmetic or65semanticmeanings attributed.'],
 'evidence_links':['resultados/cantidad/CALCULOS_REVISADOS.json','resultados/cantidad/Q6_REFERENCE_CAUSAL/MEASUREMENTS.json','resultados/cantidad/QF_P01/MEASUREMENTS.json','resultados/cantidad/QF_H01/MEASUREMENTS.json','resultados/cantidad/QF_N01/MEASUREMENTS.json','resultados/cantidad/QF_N02/MEASUREMENTS.json']}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'cases':[{k:x[k]for k in('case_id','correct','denominator')}for x in rows],'kernel_match':sum(x['exact_match']for x in kernel),'kernel_denominator':len(kernel),'update_changes':result['postupdate_direction_changes'],'restore':result['restore']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
