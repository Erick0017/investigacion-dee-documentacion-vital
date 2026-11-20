"""Late query-dose contrast after the actual continued/refilled life."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_CONTACT_RETURN27_refree';life='ES01_LATE_ACCESS29_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'episodes':[],
 'criteria_before':'Same actual scenes and fixed3access calendar on the late continued life. Change only material word probe dose: both, none, or no legacy probes. No reader shutdown; explicit later word queries remain available. Decoder uses exact declared dose and unchanged6/10 increments, not context sign.'}
def trial(x):
 oldprobe=a.case=='available';newprobe=a.case!='passive'
 for k,load in((5,3),(-3,5),(3,3),(-5,5),(5,5),(1,3),(-1,3),(3,5),(-3,3),(5,3)):
  row=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=k,load=load,legacy_word_probes=oldprobe,bridge_word_probe=newprobe);row['episode']=len(data['episodes'])+1;data['episodes'].append(row)
 data['forms']=f.query(x,frame='lexical05');data['bridge']=z.query(x,bridge='near5Bridge');data['less']=e.context(x,value=62,method='B');data['more']=e.context(x,value=122,method='B');data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeLate27');data['equal']=eq.query(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'scenes':[{'k':r['ENTORNO']['actual_parameter'],'load':r['ENTORNO']['load_each'],'words':r['SPANISH_DECODED']}for r in data['episodes']],'forms':data['forms']['SPANISH_DECODED'],'bridge':data['bridge']['SPANISH_DECODED'],'comparison':[data['less']['TRADUCCION']['SPANISH_DECODED'],data['more']['TRADUCCION']['SPANISH_DECODED']],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_LATE_CURRENT_CONTEXT_MATERIAL_QUERY_DOSE_CONTRAST29',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
