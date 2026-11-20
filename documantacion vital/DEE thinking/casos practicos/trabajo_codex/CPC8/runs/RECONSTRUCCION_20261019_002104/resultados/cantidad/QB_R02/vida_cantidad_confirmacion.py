"""New predeclared contrast: post-update objects straddle old/new references.

QA discovery preserved: its post-update objects did not distinguish31vs42.
This protocol supplies only actual incremental matter, never the target sum.
"""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cantidad_renovable import QuantitySession,physical,move
CASES={'QB_P01':{'reference':31,'objects':[16,45,31,39,36,47,34,56],'addition':11,'guards':'on_path'},
 'QB_C01':{'reference':31,'objects':[16,45,31,39,36,47,34,56],'addition':None,'guards':'on_path'},
 'QB_H01':{'reference':11,'objects':[16,45,31,39,36,47,34,56],'addition':31,'guards':'on_path'},
 'QB_G01':{'reference':31,'objects':[16,45,31,39,36,47,34,56],'addition':11,'guards':'off_path'},
 'QB_R01':{'reference':23,'objects':[9,37,23,29,27,41,25,47],'addition':7,'guards':'on_path','center':[47,33,37]},
 'QB_R02':{'reference':19,'objects':[8,43,19,37,24,41,26,52],'addition':13,'guards':'on_path','center':[44,36,39]}}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);cfg={'case_id':case,**CASES[case],'schema':'CPC8R.quantity.accumulation.confirmation.v2','frozen_before_constructor':True,
 'criterion':'Active normal1 c7 and correctdirection relative to material reference separately confirmed. Read actual output destinationsC+/-2 at72+67k; active equality at center is distinct from missing output.',
 'correction':'QA postupdateobjects were not sensitive to referenceupdate; QB postupdateobjects straddleold/new reference. Previous QAattempts remain discovery, not this reserve.',
 'update_contact_tick':271,'cue_load':0,'query_control':'8 externally supplied identical opportunities. Same actualobjects after each history.'}
 put(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=QuantitySession.create(center=cfg.get('center',(30,30,30)),guards=cfg['guards'])
 s.input('quantity.reference.cue',0,0);s.input('quantity.reference.resource',cfg['reference'],0);s.acquire_other()
 for k,value in enumerate(cfg['objects']):
  t=65+67*k;s.input('quantity.object.cue',0,t);s.input('quantity.object.resource',value,t);s.input('quantity.reader',7,69+67*k,True)
 if cfg['addition']is not None:s.input('quantity.reference.cue',0,268);s.input('quantity.reference.resource',cfg['addition'],268)
 s.save(out/'T0.deetsnap.gz');rows=[];pred=[]
 for k,value in enumerate(cfg['objects']):
  ref=cfg['reference']+((cfg['addition']or 0)if k>=4 else 0);t=70+67*k;expected=(ref>value)-(ref<value)
  pred.append({'registered_before_target_tick':s.tick,'target_tick':t,'auditor_only_reference_sum':ref,'auditor_only_expected_direction':[expected,0,0]})
  s.run_until(t-1);pre=s.capture();s.run_until(t);post=s.capture();o=post['center'];s.run_until(t+2)
  destinations=[{'sign':sgn,'reading':s.observe(move(s.geometry['center'],(sgn,0,0),2))}for sgn in(-1,1)]
  available=pre['reference']['s_reg']==ref and pre['reference']['active']and pre['reference']['direction']==[0,1,0]
  correct=o['active']and o['state']==1 and o['s_reg']==7 and o['semantic']==1 and o['direction']==[expected,0,0]
  rows.append({'round':k,'pre':pre,'post':post,'destinations_tick':s.tick,'destinations':destinations,'expected_reference_auditor_only':ref,'reference_preserved':available,'correct_with_reference':bool(available and correct)})
  if k in(0,3,4,7):s.save(out/f'T{s.tick}.deetsnap.gz')
 result={'case_id':case,'config':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'predictions':pred,'rounds':rows,'inputs':s.receipts(),'final':physical(s.world),'RAW_clock_edits_on_MAIN':[],
 'scope':'Acquired scalar quantity, native additiveupdate, and actual material routeconsequence; not learned comparison algorithm, arbitraryselectivereplacement or autonomousquery.'}
 put(out/'MEASUREMENTS.json',result);print(json.dumps({'case_id':case,'correct_with_reference':sum(x['correct_with_reference']for x in rows),'denominator':len(rows),'directions':[x['post']['center']['direction']for x in rows]}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
