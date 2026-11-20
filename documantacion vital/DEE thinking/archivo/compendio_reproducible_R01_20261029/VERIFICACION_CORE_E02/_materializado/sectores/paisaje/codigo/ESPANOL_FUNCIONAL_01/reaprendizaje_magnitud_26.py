"""Can late E1 regain actual comparison through explicit new experience?"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,recuperacion_magnitud_26 as r,ensenanza_lexica_03 as f,puente_lexico_10 as z,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='E1_ESPANOL_01';life='ES01_MAG_RELEARN26_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'episodes':[],
 'criteria_before':'Native explicit reference experience86+format5, no word re-teaching; same strict comparative decoder. New objects61/119/... never labelled for the participant. On-route/sham guards have equal material. Omitting or decoupling teaching must be distinguished from native retention. Retest old lexical/contact/equality forms and two current spatial scenes after recurrent comparisons.'}
def trial(x):
 guard='on_route'if a.case in('paired_guard','unpaired_guard','omitted_guard')else('sham'if a.case=='paired_sham'else'none');teaching='unpaired'if a.case=='unpaired_guard'else('omitted'if a.case=='omitted_guard'else'paired')
 data['reacquisition']=r.reacquire(x,value=86,guard=guard,teaching=teaching)
 for value in(61,119,52,105,73,113,80,118):
  row=e.context(x,value=value,method='B');row['episode']=len(data['episodes'])+1;data['episodes'].append(row)
 data['spatial_near']=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=5,load=5);data['spatial_far']=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=-3,load=5)
 data['late_less']=e.context(x,value=63,method='B');data['late_more']=e.context(x,value=121,method='B')
 data['old_word_query']=f.query(x,frame='lexical05');data['bridge_query']=z.query(x,bridge='near5Bridge');data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeRepair5');data['equal']=eq.query(x);data['time']=e.temporal_query(x,frame='secuenciaA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'words':[r['TRADUCCION']['SPANISH_DECODED']for r in data['episodes']],'late':[data['late_less']['TRADUCCION']['SPANISH_DECODED'],data['late_more']['TRADUCCION']['SPANISH_DECODED']],'spatial':[data['spatial_near']['SPANISH_DECODED'],data['spatial_far']['SPANISH_DECODED']],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED'],'equal':data['equal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_LATE_NATIVE_REFERENCE_RELEARNING_WITH_ROUTE_CONTROLS26',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
