"""Native alternative perception-to-word route after a witnessed collision."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_LONG7_D_no_material_queries';life='ES01_BRIDGE10_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'queries':[],'contexts':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependencies':{m.__name__:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in(e,f,z,eq)},
 'criteria_before':'Word from nativeXsign, state1SEM1Y=Z=1. New normalized bus path shifts the word orbit; old d5 bank not moved/overwritten. Strict6/10 and predeclared band6/7/8/10/11/12 both reported; old results not reclassified.'}
def trial(x):
 data['bridge']=z.prepare(x,bridge='near5Bridge',source_frame='lexical05',source_bank='d5')
 data['teaching']=z.teach(x,bridge='near5Bridge',word='lejos'if a.case=='wrong_teacher'else'cerca',signal=a.case!='no_cue',cut=a.case=='cut_bus',sham=a.case=='sham_bus')
 for j in range(3):data['queries'].append(z.query(x,bridge='near5Bridge'))
 for k,load in((5,5),(-5,3),(3,3),(-3,5),(5,3)):
  row=z.context(x,bridge='near5Bridge',parameter=k,load=load,event_a=a.case!='current_no_A',probe=a.case!='passive_production');row['physical']=physical(x.world,occupation=True);data['contexts'].append(row)
 data['final_new_word']=z.query(x,bridge='near5Bridge');data['prior_lexicon']=f.query(x,frame='lexical05');data['old_words']=e.query_words(x);data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeRepair5');data['time']=e.temporal_query(x,frame='secuenciaA');data['equality']=eq.query(x);data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'queries':[r['SPANISH_DECODED']for r in data['queries']],'contexts':[{'parameter':r['ENTORNO']['actual_parameter'],'strict':r['SPANISH_DECODED'],'band':r['BOUNDED_PROVISION_DECODED']}for r in data['contexts']],
  'final':data['final_new_word']['SPANISH_DECODED'],'prior_lexicon':data['prior_lexicon']['SPANISH_DECODED'],'old_words':data['old_words']['FORMAS_ACCESIBLES'],'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED'],'equal':data['equality']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_NORMALIZED_NATIVE_LEXICAL_BRIDGE_ALTERNATIVE10',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
