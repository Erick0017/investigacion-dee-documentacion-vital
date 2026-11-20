"""Finite native feedback discovery and controls. No outcome-based host inputs."""
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from feedback_regulador import FeedbackSession
from cantidad_renovable import physical,move
CASES={'FB_P01':('onpath',True,31,(16,45,31)),'FB_C01':('offpath',True,31,(16,45,31)),'FB_N01':('onpath',False,31,(16,45,31)),'FB_H01':('onpath',True,11,(16,45,31)),'FB_R01':('onpath',True,17,(9,37,17))}
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);route,enabled,ref,objects=CASES[case]
 cfg={'case_id':case,'route':route,'relays_enabled':enabled,'reference':ref,'objects':objects,'frozen_before_constructor':True,
 'prediction':'If transformed secondarynativeproduct can substitute for second learnedcounterflow, actualreference andthirdobject mayremainusable without secondexternallytaughtdirection. Later encounters may instead interfere; record all.',
 'attribution':'Experiment for native history-dependent feedback. R2utility-selection is NOT established by this fixed path.'}
 put(out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/feedback_regulador.py',ROOT/'src/regulacion_adquirida.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,out/p.name)
 s=FeedbackSession.create(route=route);s.experience_reference(ref);s.reader_opportunity();s.acquire_other();s.first_regulation_experience();s.feedback_opportunities(enabled)
 for k,v in enumerate(objects):s.present_object(v,round_index=k)
 s.save(out/'T0.deetsnap.gz');rows=[]
 for t in(3,69,70,71,73,74,75,76,78,79,80,82,83,84,110,135,136,137,138,140,170,171,172,180,203,204):
  s.run_until(t);row=s.capture();row['relays']=[{'id':r['port'],'reading':s.observe(r['target'])}for r in s.geometry['feedback_relays']]
  row['neutralization_prediction_only']=s.observe(move(s.geometry['center'],(1,0,0),33))
  rows.append(row)
  if t in(71,74,75,83,137,171,204):s.save(out/f'T{t}.deetsnap.gz')
 readings=[]
 for k,t in enumerate((70,137,204)):
  pre=next(x for x in rows if x['tick']==t-1);o=next(x for x in rows if x['tick']==t)['center'];q=pre['reference'];v=pre['object'];expected=[(ref>objects[k])-(ref<objects[k]),0,0]
  readings.append({'tick':t,'reference_pre':q,'object_pre':v,'reading':o,'correct':bool(q['active']and q['s_reg']==ref+5 and q['direction']==[0,1,0]and v['active']and v['s_reg']==objects[k]+5 and v['direction']==[0,1,0]and o['active']and o['s_reg']==7 and o['direction']==expected)})
 put(out/'MEASUREMENTS.json',{'case_id':case,'config':cfg,'geometry':s.geometry,'preparations':1,'continuations':0,'diagnostic_forks':0,'inputs':s.receipts(),'observations':rows,'readings':readings,'final':physical(s.world),'RAW_clock_edits_on_MAIN':[]})
 print(json.dumps({'case_id':case,'readings':readings}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.case,a.out)
