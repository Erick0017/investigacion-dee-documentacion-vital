"""Main continues two actual social transmissions without consuming returned forms."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_03';life='ES01_MAIN_04';s.fork(parent,life,kind='CANDIDATE')
data={'life':life,'parent':s.record(parent),'phases':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope_before':'One world; B is a receiver region, C an E1 return region. Acquired contact/free-flight content, prepared channels/recipient, not role-relative YO/TU or autonomous interlocutor selection.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 for source,com in(('contactoA','socialToca'),('freeRepair5','socialFree')):
  cap(x,'transmit_'+com,e.contact_social(x,source_frame=source,communication=com,distance=7))
  cap(x,'original_source_after_'+com,e.contact_query(x,frame=source))
 for com in('socialToca','socialFree'):cap(x,'return_reuse_'+com,e.contact_social_query(x,communication=com))
 for value in(66,108):cap(x,'new_current_context_'+str(value),e.context(x,value=value,method='B'))
 for source in('contactoA','freeRepair5'):cap(x,'original_relation_retention_'+source,e.contact_query(x,frame=source))
 cap(x,'time_retention',e.temporal_query(x,frame='secuenciaA'));cap(x,'comparison_forms',e.query_words(x))
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'all_results_are_new_native_interactions':True}
data['commit']=s.mutate(life,'EF01_MAIN_CONTACT_FREE_SOCIAL_CONTINUITY',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'life':life,'tick':data['post']['tick'],'rows':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED',r['result'].get('FORMAS_ACCESIBLES',r['result'].get('TRADUCCION',{}).get('SPANISH_DECODED')))}for r in data['phases']]},ensure_ascii=False))
