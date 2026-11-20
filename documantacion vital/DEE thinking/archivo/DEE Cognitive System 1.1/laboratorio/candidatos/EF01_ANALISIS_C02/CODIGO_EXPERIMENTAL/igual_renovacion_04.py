"""Direction-conditioned equality and fixed native renewal versus scalar/sham."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
parent='ES01_MAIN_04'if a.case=='no_word_history'else'ES01_MAIN_05';s=Store(a.system);life='ES01_EQUAL_RENEW4_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'rows':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'criteria_before':'Conditional output state1SEM1[1,-1,1] -> igual; original template must return at+134. Exact same scalar-history control, sham residual guards and absent acquired word. Zero-load material counted.'}
def trial(x):
 values=[86,56,110,86]if a.case!='start_unequal_reserve'else[56,86,110,86]
 for j,value in enumerate(values):
  if a.case=='scalar_existing':row=f.context(x,value=value)
  else:row=f.context_renewable(x,value=value,sham_guards=a.case=='sham',require_learned=a.case!='no_word_history')
  row['episode']=j;row['physical']=physical(x.world,occupation=True);data['rows'].append(row)
  if a.case!='scalar_existing'and a.case!='no_word_history'and not row['INSTRUMENTO']['returned_to_declared_reader']:break
 data['old_words']=e.query_words(x);data['old_contact']=e.contact_query(x,frame='contactoA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'equality':[r['SPANISH_DECODED']for r in data['rows']],'returned':[r['INSTRUMENTO'].get('returned_to_declared_reader')for r in data['rows']],'old_words':data['old_words']['FORMAS_ACCESIBLES'],'old_contact':data['old_contact']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_DIRECTIONAL_EQUALITY_NATIVE_RENEWAL_VS_SCALAR_R4',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
