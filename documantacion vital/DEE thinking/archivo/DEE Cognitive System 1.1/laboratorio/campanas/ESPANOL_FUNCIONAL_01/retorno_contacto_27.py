"""Explicit new physical contact/free-flight experience after late reader loss."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAG_RELEARN26_paired_guard';life='ES01_CONTACT_RETURN27_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'queries':[],
 'criteria_before':'New named physical experience, not reset of the old freeRepair5 contract. Reuse original site or a declared relocation; all class banks receive equal post-event cue. First and later queries separated because probes can teach. Revalidate newly relearned comparison and existing Spanish frames; do not claim retention of a reference that was explicitly re-taught.'}
def trial(x):
 base=(18,34,44)if a.case=='translated'else(18,34,54);e.contact_prepare(x,frame='freeLate27',base=base)
 data['experience']=e.contact_teach(x,frame='freeLate27',present=a.case=='contact',signal=a.case!='no_signal',medium=1,actor_state=17)
 for j in range(6):data['queries'].append(e.contact_query(x,frame='freeLate27'))
 data['less']=e.context(x,value=62,method='B');data['more']=e.context(x,value=122,method='B');data['spatial_near']=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=5,load=3);data['spatial_far']=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=-5,load=5)
 data['last_query']=e.contact_query(x,frame='freeLate27');data['older_contact']=e.contact_query(x,frame='contactoA');data['word_old']=f.query(x,frame='lexical05');data['word_bridge']=z.query(x,bridge='near5Bridge');data['equal']=eq.query(x);data['time']=e.temporal_query(x,frame='secuenciaA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'first_to_later':[q['SPANISH_DECODED']for q in data['queries']],'last':data['last_query']['SPANISH_DECODED'],'less':data['less']['TRADUCCION']['SPANISH_DECODED'],'more':data['more']['TRADUCCION']['SPANISH_DECODED'],'spatial':[data['spatial_near']['SPANISH_DECODED'],data['spatial_far']['SPANISH_DECODED']],'older_contact':data['older_contact']['SPANISH_DECODED'],'equal':data['equal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_DECLARED_NEW_CONTACT_EXPERIENCE_AFTER_LATE_ACCESS_LOSS27',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
