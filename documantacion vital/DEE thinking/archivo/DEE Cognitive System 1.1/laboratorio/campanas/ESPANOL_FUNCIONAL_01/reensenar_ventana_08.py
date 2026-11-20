"""A real later lesson for the failed near5 acquisition, matched phase variants."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
phase,signal={'same_phase0':(0,True),'new_phase8':(8,True),'phase12_reserve':(12,True),'phase8_no_cue':(8,False)}[a.case]
s=Store(a.system);parent='ES01_LONG7_D_no_material_queries';life='ES01_RETEACH8_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'phases':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependencies':{m.__name__:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in(e,f,eq)},
 'criteria_before':'Word from acquiredX, Y=Z=1. Native current strictdelta6/10. New phase is prepared externally, not an acquired calendar policy. All older acquired phases remain queried equally.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 cap(x,'new_actual_near5_lesson',f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=phase,signal=signal))
 for j in range(2):cap(x,'recall_after_new_lesson_'+str(j),f.query(x,frame='lexical05'))
 for k,load in((5,5),(-5,3),(3,3),(-3,5)):
  cap(x,'reserved_current_'+str(k)+'_load'+str(load),f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict'))
 cap(x,'all_word_associations_retention',f.query(x,frame='lexical05'))
 data['old_words']=e.query_words(x);data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeRepair5');data['time']=e.temporal_query(x,frame='secuenciaA');data['equality']=eq.query(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'new_results':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED')}for r in data['phases']],'old_words':data['old_words']['FORMAS_ACCESIBLES'],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED'],'igual':data['equality']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_EXPLICIT_LATER_RETEACHING_NOT_HIDDEN_RETENTION',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
