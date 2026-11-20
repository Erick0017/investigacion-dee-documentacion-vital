"""Repeated native feedback opportunities with actual additive acquisition.

The schedule is fixed. It never reads a response to select a port or a pulse
direction. All candidate zero-load formatting opportunities are supplied.
"""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from feedback_regulador import FeedbackSession
from cantidad_renovable import physical
CASES={'FBL_P01':('onpath',True,31,11,[16,45,31,36,42,31,50]),'FBL_C01':('onpath',False,31,11,[16,45,31,36,42,31,50]),
 'FBL_C02':('offpath',True,31,11,[16,45,31,36,42,31,50]),'FBL_H01':('onpath',True,11,31,[16,45,31,36,42,31,50]),
 'FBL_R01':('onpath',True,17,19,[7,31,17,16,36,41,7])}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);route,enabled,ref,add,objects=CASES[case];indices=(0,1,2,4,5,6,7);ticks=[70+67*i for i in indices]
 cfg={'case_id':case,'route':route,'relays_enabled':enabled,'reference':ref,'addition':add,'actual_objects':objects,'reading_ticks':ticks,'frozen_before_constructor':True,
 'scope':'First external counterflow acquired once. Later counterflows, if present, arise from native comparisonproducts via fixed material relay. Not a learnedutilitypolicy, and repeatedsame-sign/adversehistories retained.',
 'criterion':'At everypreboundary reference and actualobject must remainavailable with their declared quantities/directions, then exactnative c7readsign. Zero mustbeactive, notsilence.'}
 put(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/feedback_regulador.py',ROOT/'src/regulacion_adquirida.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=FeedbackSession.create(route=route);s.experience_reference(ref);s.acquire_other();s.first_regulation_experience()
 for index,v,t in zip(indices,objects,ticks):
  s.present_object(v,round_index=index);s.input('quantity.reader',7,t-1,True)
  if enabled:
   for r in s.geometry['feedback_relays']:s.input(r['port'],0,r['tick']-3+t-70)
 s.input('quantity.reference.cue',0,268);s.input('quantity.reference.resource',add,268)
 s.save(out/'T0.deetsnap.gz');rows=[]
 for k,(t,value)in enumerate(zip(ticks,objects)):
  expectedref=ref+5+(add if t>271 else 0);expected=(expectedref>value+5)-(expectedref<value+5)
  s.run_until(t-1);pre=s.capture();s.run_until(t);post=s.capture();q=pre['reference'];v=pre['object'];o=post['center']
  correct=bool(q['active']and q['s_reg']==expectedref and q['direction']==[0,1,0]and v['active']and v['s_reg']==value+5 and v['direction']==[0,1,0]and o['active']and o['s_reg']==7 and o['direction']==[expected,0,0])
  rows.append({'tick':t,'pre':pre,'post':post,'expected_reference_auditor_only':expectedref,'correct':correct})
  if t in(70,204,338,539):s.save(out/f'T{t}.deetsnap.gz')
 s.run_until(570);s.save(out/'T570.deetsnap.gz')
 put(out/'MEASUREMENTS.json',{'case_id':case,'config':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'inputs':s.receipts(),'rounds':rows,'final':physical(s.world),'RAW_clock_edits_on_MAIN':[]})
 print(json.dumps({'case_id':case,'correct':[x['correct']for x in rows],'directions':[x['post']['center']['direction']for x in rows],'reference':[x['pre']['reference']['s_reg']for x in rows]}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
