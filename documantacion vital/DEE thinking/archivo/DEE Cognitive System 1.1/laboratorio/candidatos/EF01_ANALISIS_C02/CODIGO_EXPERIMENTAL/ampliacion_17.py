"""Two new physical contexts in the same inherited lexical life, fixed criteria."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_INTEGRATED12_intact';life='ES01_EXPAND17_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'criteria_before':'Explicitly teach the previously untrained physical contexts +/-1; a new acquired context is not zero-shot generalization. Same decoder and all routes. Preserve four earlier contexts, contrast no cue and opposite arbitrary cue. Do not discard a failing future.','episodes':[]}
def trial(x):
 phases=(8,12)if a.case!='reversed_phases'else(12,8)
 data['lessons']=[]
 for k,w,p in zip((1,-1),('cerca','lejos'),phases):
  if a.case=='opposite':w='lejos'if w=='cerca'else'cerca'
  data['lessons'].append(f.teach(x,frame='lexical05',parameter=k,word=w,phase_shift=p,signal=a.case!='no_cue'))
 data['initial_recall']=f.query(x,frame='lexical05')
 for k,load in((1,3),(-1,3),(3,5),(-3,5),(5,3),(-5,5),(1,5),(-1,5)):
  row=e.produce_relations(x,frame='lexical05',bridge='near5Bridge',parameter=k,load=load);row['episode']=len(data['episodes'])+1;data['episodes'].append(row)
 data['last_recall']=f.query(x,frame='lexical05');data['bridge']=z.query(x,bridge='near5Bridge');data['comparisons']=e.query_words(x);data['contact']=e.contact_query(x,frame='contactoA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'responses':[{'parameter':r['ENTORNO']['actual_parameter'],'load':r['ENTORNO']['load_each'],'word':r['SPANISH_DECODED']}for r in data['episodes']],'retained':data['last_recall']['SPANISH_DECODED'],'bridge':data['bridge']['SPANISH_DECODED'],'comparison':data['comparisons']['FORMAS_ACCESIBLES'],'contact':data['contact']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_ADDITIONAL_CONTEXT_ACQUISITION_WITH_OLD_RETENTION17',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
