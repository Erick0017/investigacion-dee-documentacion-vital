"""Main gains equality cue and tests new current comparisons without re-teaching."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_04';life='ES01_MAIN_05';s.fork(parent,life,kind='CANDIDATE')
data={'life':life,'parent':s.record(parent),'phases':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'criteria_before':'Read[1,-1,1], state1SEM1; current equality emission requires acquired signal and exact native-word increment7. No external equality arithmetic in participant.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 f.prepare(x);cap(x,'actual_equality_and_later_word_teaching',f.present(x,value=86,teacher=True,probe_lead=1))
 for j in range(3):cap(x,'equality_recall_'+str(j),f.query(x))
 for value in(86,56,110,86):cap(x,'current_equality_test_'+str(value),f.context(x,value=value,probe_lead=1))
 for frame in('contactoA','freeRepair5'):cap(x,'previous_'+frame,e.contact_query(x,frame=frame))
 cap(x,'previous_time',e.temporal_query(x,frame='secuenciaA'));cap(x,'previous_comparison_forms',e.query_words(x));cap(x,'equality_after_other_queries',f.query(x))
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'no_teacher_during_contexts':True}
data['commit']=s.mutate(life,'EF01_MAIN_EQUALITY_POST_EXPERIENCE_WORD_R3',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'life':life,'tick':data['post']['tick'],'rows':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED',r['result'].get('FORMAS_ACCESIBLES'))}for r in data['phases']]},ensure_ascii=False))
