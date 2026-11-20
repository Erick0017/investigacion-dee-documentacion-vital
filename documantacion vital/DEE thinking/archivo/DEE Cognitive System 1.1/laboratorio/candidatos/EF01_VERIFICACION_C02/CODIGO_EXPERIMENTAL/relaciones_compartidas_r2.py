"""Shared teaching method, causal cue tests and held-out physical paths."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_relacional_02 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'path_near3':('relative_path',3,True,0,True,True,False,3),'path_far3':('relative_path',-3,True,0,True,True,False,3),'path_near1_reserve':('relative_path',1,True,0,True,True,False,3),'path_far5_reserve':('relative_path',-5,True,0,True,True,False,3),'path_load5_reserve':('relative_path',3,True,0,True,True,False,5),'path_no_signal':('relative_path',3,False,0,True,True,False,3),'path_unpaired':('relative_path',3,True,1,True,True,False,3),'path_no_A':('relative_path',3,True,0,False,True,False,3),'path_B_offroute':('relative_path',3,True,0,True,True,True,3),'time_AB5':('event_order',5,True,0,True,True,False,3),'time_BA5':('event_order',-5,True,0,True,True,False,3),'time_AB3_reserve':('event_order',3,True,0,True,True,False,3),'time_no_signal':('event_order',5,False,0,True,True,False,3)}
mode,k,signal,delay,aa,bb,off,load=plans[a.case];s=Store(a.system);parent='ES01_MAIN_04';life='ES01_SHARED_R2_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'queries':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'criteria_before':{'read':[1,1,0],'use':[0,1,0],'state':1,'semantic':1,'word_reference':'Positive path offset: closer to the prepared physical reference pattern, negative: farther. Same emission time for every path. Not an unlearned simulator-Z perspective.'}}
def trial(x):
 entry=f.prepare(x,frame='shared02',mode=mode,origin=(38,50,8));data['geometry']=entry
 data['teaching']=f.experience(x,frame='shared02',parameter=k,a_load=load,b_load=load,signal=signal,delay=delay,event_a=aa,event_b=bb,offroute=off)
 data['post_teaching_neighbors']={b['id']:moore27(x.world,b['hub'])for b in entry['banks']}
 for j in range(5):
  row=f.query(x,frame='shared02',use=j==4);row['round']=j;data['queries'].append(row)
 data['old_contact']=e.contact_query(x,frame='contactoA');data['old_free']=e.contact_query(x,frame='freeRepair5');data['old_words']=e.query_words(x);data['old_time']=e.temporal_query(x,frame='secuenciaA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'new':[r['SPANISH_DECODED']for r in data['queries']],'contact':data['old_contact']['SPANISH_DECODED'],'free':data['old_free']['SPANISH_DECODED'],'words':data['old_words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_SHARED_NATIVE_RELATIONAL_WORD_TEACHING_R2',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
