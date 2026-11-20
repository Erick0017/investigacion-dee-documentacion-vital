"""Physical learned word markers; wrong-teacher and phase-interference controls."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_04';life='ES01_LEXICAL3_'+a.case;s.fork(parent,life,kind='CANDIDATE')
plans={'near':(3,'cerca',True,True,False,None),'far':(-3,'lejos',True,True,False,None),'wrong_teacher':(3,'lejos',True,True,False,None),'no_signal':(3,'cerca',False,True,False,None),'no_event_A':(3,'cerca',True,False,False,None),'offroute_B':(3,'cerca',True,True,True,None),'two_same_phase':(3,'cerca',True,True,False,0),'two_phase4':(3,'cerca',True,True,False,4),'near_comprehend_far':(3,'cerca',True,True,False,None)}
k,word,signal,aa,off,second=plans[a.case]
data={'case':a.case,'life':life,'parent':s.record(parent),'phases':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'frozen_decoder':'Word from nativeXsign, never bank ID; Y=Z=1,state1SEM1. Current modulation strictly6/10 after known query7. Wrong teacher is expected to produce its taught wrong token, not a host-corrected answer.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 f.prepare(x,frame='arbitrary03',mode='relative_path',origin=(38,50,8))
 cap(x,'teach_first',f.teach(x,frame='arbitrary03',parameter=k,word=word,signal=signal,event_a=aa,offroute=off))
 for j in range(3):cap(x,'first_recall_'+str(j),f.query(x,frame='arbitrary03'))
 if second is not None:
  cap(x,'teach_far_without_reset',f.teach(x,frame='arbitrary03',parameter=-3,word='lejos',phase_shift=second))
  for j in range(3):cap(x,'both_recall_'+str(j),f.query(x,frame='arbitrary03'))
 for context,load in((3,5),(-3,3),(1,3)):
  cap(x,'current_context_'+str(context)+'_load'+str(load),f.context(x,frame='arbitrary03',parameter=context,load=load))
 cap(x,'lexical_final_recall',f.query(x,frame='arbitrary03'))
 cap(x,'token_to_native_use',f.comprehend(x,frame='arbitrary03',word='lejos'if a.case=='near_comprehend_far'else word))
 data['old_words']=e.query_words(x);data['old_contact']=e.contact_query(x,frame='contactoA');data['old_free']=e.contact_query(x,frame='freeRepair5');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'rows':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED'),'actions':[p['action_banks']for p in r['result'].get('ENTE',[])if isinstance(p,dict)and'action_banks'in p]}for r in data['phases']],'old_words':data['old_words']['FORMAS_ACCESIBLES'],'contact':data['old_contact']['SPANISH_DECODED'],'free':data['old_free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_ARBITRARY_LEXICAL_BINDING_AND_PHASE_REGULATION_R3',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
