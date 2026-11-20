"""Native learned contact/free-flight transmission, receptor acquisition and use."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'toca':('contactoA',False,False,False,False),'free':('freeRepair5',False,False,False,False),'cut_toca':('contactoA',True,False,False,False),'sham_toca':('contactoA',False,True,False,False),'no_B_cue':('contactoA',False,False,True,False),'no_C_cue':('contactoA',False,False,False,True)}
source,cut,sham,noB,noC=plans[a.case];s=Store(a.system);parent='ES01_MAIN_03';life='ES01_SOCIAL_CONTACT1_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'criteria_before':'B and C require native[-1,1,z] and final native[0,1,z], where z0 contact and z-1 free flight. All two content opportunities supplied equally; recipient is prepared.'}
def trial(x):
 data['transfer']=e.contact_social(x,source_frame=source,communication='social01',cut_message=cut,sham=sham,omit_B_cue=noB,omit_C_cue=noC)
 data['later_query']=e.contact_social_query(x,communication='social01')
 data['later_use']=e.contact_social_query(x,communication='social01',use=True)
 data['previous_comparison']=e.query_words(x);data['previous_temporal']=e.temporal_query(x,frame='secuenciaA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'C_return':data['transfer']['SPANISH_DECODED'],'later_query':data['later_query']['SPANISH_DECODED'],'later_use':data['later_use']['SPANISH_DECODED'],'comparison':data['previous_comparison']['FORMAS_ACCESIBLES'],'temporal':data['previous_temporal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_CONTACT_SOCIAL_NATIVE_RETURN',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
