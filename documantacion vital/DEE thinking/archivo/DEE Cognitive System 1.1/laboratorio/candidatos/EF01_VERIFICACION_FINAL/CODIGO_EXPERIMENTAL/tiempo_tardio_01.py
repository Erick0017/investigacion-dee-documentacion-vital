"""Late native temporal teaching and reserves from a continuous four-form branch."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'AB5':('AB',5,True,0,True,True,False,3),'BA5':('BA',5,True,0,True,True,False,3),'AB3_reserve':('AB',3,True,0,True,True,False,3),'BA1_reserve':('BA',1,True,0,True,True,False,3),'load5_reserve':('AB',3,True,0,True,True,False,5),'no_signal':('AB',5,False,0,True,True,False,3),'unpaired':('AB',5,True,1,True,True,False,3),'no_A':('AB',5,True,0,False,True,False,3),'no_B':('AB',5,True,0,True,False,False,3),'B_offroute':('AB',5,True,0,True,True,True,3)}
order,interval,signal,delay,aa,bb,off,load=plans[a.case];s=Store(a.system);parent='ES01_CONTACT_ACCESS5_x18';life='ES01_TIME1_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'queries':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'criteria_before':'Read native[0,1,1], use[0,0,1], state1SEM1, positive delta=A before B, negative=A after B; all six banks equally probed. Geometry is prepared.'}
def trial(x):
 entry=e.temporal_prepare(x,frame='time01',origin=(8,8,22));data['frame']=entry
 data['teaching']=e.temporal_experience(x,frame='time01',order=order,interval=interval,signal=signal,delay=delay,event_a=aa,event_b=bb,offroute=off,a_load=load,b_load=load)
 data['teaching_neighborhoods']={b['id']:moore27(x.world,b['hub'])for b in entry['surfaces']}
 for j in range(4):
  row=e.temporal_query(x,frame='time01',use=j==3);row['round']=j;data['queries'].append(row)
 data['prior_contact']=e.contact_query(x,frame='contactoA');data['prior_free']=e.contact_query(x,frame='freeRepair5');data['prior_comparison']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'temporal':[r['SPANISH_DECODED']for r in data['queries']],'contact':data['prior_contact']['SPANISH_DECODED'],'free':data['prior_free']['SPANISH_DECODED'],'comparison':data['prior_comparison']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_NEW_TEMPORAL_EXPERIENCES_AFTER_FOUR_LEARNED_FORMS',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
