"""Native material accumulation and finite repeated comparison.

Zero-load formatting cues are still real state1 directional matter. Magnitudes
are actual introduced resources. Neither accumulated value nor comparison
answer is injected as a computed input. Summation occurs only in v27 reducer.
"""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_renovable import QuantitySession,physical,move
CASES={'QA_P01':{'reference':31,'objects':[16,45,31,39,22,47,8,56],'addition':11,'guards':'on_path'},
 'QA_C01':{'reference':31,'objects':[16,45,31,39,22,47,8,56],'addition':None,'guards':'on_path'},
 'QA_H01':{'reference':11,'objects':[16,45,31,39,22,47,8,56],'addition':31,'guards':'on_path'},
 'QA_G01':{'reference':31,'objects':[16,45,31,39,22,47,8,56],'addition':11,'guards':'off_path'},
 'QA_R01':{'reference':23,'objects':[9,37,23,29,18,41,6,47],'addition':7,'guards':'on_path','center':[47,33,37]}}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);cfg={'case_id':case,**CASES[case],'schema':'CPC8R.quantity.accumulation.protocol.v1','frozen_before_constructor':True,
 'criterion':'At70+67k active normal1 c7 reader direction(sign(acquired_material_reference-current_actual_object),0,0), exact moving reference separately checked. The later added resource, not its target sum, is externally supplied. Native reducer performs addition.',
 'update_contact_tick':271,'cue_load':0,'query_control':'8 externally supplied identical opportunities, not autonomous initiative. Same objects after each history.','independent_acquisition_times':[3,271]}
 put(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=QuantitySession.create(center=cfg.get('center',(30,30,30)),guards=cfg['guards'])
 s.input('quantity.reference.cue',0,0);s.input('quantity.reference.resource',cfg['reference'],0);s.acquire_other()
 for k,value in enumerate(cfg['objects']):
  t=65+67*k;s.input('quantity.object.cue',0,t);s.input('quantity.object.resource',value,t);s.input('quantity.reader',7,69+67*k,True)
 if cfg['addition']is not None:
  s.input('quantity.reference.cue',0,268);s.input('quantity.reference.resource',cfg['addition'],268)
 s.save(out/'T0.deetsnap.gz');rows=[];pred=[]
 for k,value in enumerate(cfg['objects']):
  ref=cfg['reference']+(cfg['addition']or 0 if k>=4 else 0);t=70+67*k
  pred.append({'prediction_registered_before_target_tick':s.tick,'target_tick':t,'auditor_only_reference_sum':ref,'auditor_only_expected_direction':[(ref>value)-(ref<value),0,0]})
  s.run_until(t-1);pre=s.capture();s.run_until(t);post=s.capture();o=post['center']
  rows.append({'round':k,'pre':pre,'post':post,'expected_reference_auditor_only':ref,'reference_preserved':pre['reference']['s_reg']==ref and pre['reference']['active']and pre['reference']['direction']==[0,1,0],
   'correct':o['active']and o['state']==1 and o['s_reg']==7 and o['semantic']==1 and o['direction']==[(ref>value)-(ref<value),0,0]})
  if k in(0,3,4,7):s.save(out/f'T{t}.deetsnap.gz')
 result={'case_id':case,'config':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'predictions':pred,'rounds':rows,'inputs':s.receipts(),'final':physical(s.world),'RAW_clock_edits_on_MAIN':[],
 'scope':'Acquired scalar quantity and native accumulation, not learned algorithm or arbitrary selective replacement. Additive update is recorded as such; no outcome feedback and no sum supplied to participant.'}
 put(out/'MEASUREMENTS.json',result);print(json.dumps({'case_id':case,'rounds':[{'tick':x['post']['tick'],'direction':x['post']['center']['direction'],'reference':x['pre']['reference']['s_reg'],'reference_preserved':x['reference_preserved'],'correct':x['correct']}for x in rows]}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
