"""New phase/frame reservations for the admitted system contact component."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'known_contact':([28,34,54],True,1,1),'known_free':([28,34,54],False,1,1),'new_contact':([43,19,41],True,1,1),'new_free':([43,19,41],False,1,1),'new_medium3':([43,19,41],True,3,1),'new_actor17':([43,19,41],True,1,17)}
base,present,medium,actor=plans[a.case];s=Store(a.system);life='ES01_CONTACT_API_'+a.case;parent='ES01_MAIN_01';s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reads':[],'phase_reservation':64,'physical_frame_reservation':base}
def trial(x):
 data['pre']=physical(x.world,occupation=True);g=e.prepare(x);entry=e.contact_prepare(x,frame='api01',base=base);data['frame']=entry
 data['teaching']=e.contact_teach(x,frame='api01',present=present,medium=medium,actor_state=actor)
 data['after_teaching_neighborhoods']={k:moore27(x.world,b['hub'])for k,b in entry['banks'].items()}
 for j in range(6):
  row=e.contact_query(x,frame='api01',use=j==5);row['round']=j;row['physical']=physical(x.world,occupation=True);data['reads'].append(row)
 data['old_words']=e.query_words(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'first_read':data['reads'][0]['SPANISH_DECODED'],'sixth_read_and_use':data['reads'][-1]['SPANISH_DECODED'],'old_words':data['old_words']['FORMAS_ACCESIBLES']}
data['commit']=s.mutate(life,'EF01_CONTACT_NEW_PHASE_AND_FRAME',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'case':a.case,'first':data['reads'][0]['SPANISH_DECODED'],'sixth':data['reads'][-1]['SPANISH_DECODED'],'old_words':data['old_words']['FORMAS_ACCESIBLES'],'tick':data['post']['tick']},ensure_ascii=False))
