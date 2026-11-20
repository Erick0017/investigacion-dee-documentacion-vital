"""Word cue -> native use and learned-word communication after integration."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_INTEGRATED12_intact';life='ES01_LANGUAGE13_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependencies':{m.__name__:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in(e,f,z)},'scope_before':'Word-recognition is fixed transduction. Acquired marker supplies the match; no environmental correct answer reaches the action function. Consumptive branches are not promoted over the retained source state.'}
def trial(x):
 if a.case.startswith('understand_'):
  word='cerca'if a.case=='understand_cerca'else'lejos';data['legacy_word_use']=f.comprehend(x,frame='lexical05',word=word);data['bridge_word_use']=z.comprehend(x,bridge='near5Bridge',word=word)
 else:
  request='cerca'if a.case=='social_match'else('lejos'if a.case=='social_wrong_word'else None)
  data['social']=z.communicate(x,bridge='near5Bridge',communication='lexsocial13',cut=a.case=='social_cut',sham=a.case=='social_sham',request_word=request,omit_receiver_cue=a.case=='social_no_B_cue')
 data['older_comparison']=e.query_words(x);data['older_contact']=e.contact_query(x,frame='contactoA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'legacy_action':None if'legacy_word_use'not in data else[r['action_banks']for r in data['legacy_word_use']['ENTE']],
  'bridge_action':data.get('bridge_word_use',{}).get('NATIVE_ACTION_OBSERVED'),'B_words':data.get('social',{}).get('B_WORDS_DECODED'),'B_action':data.get('social',{}).get('B_NATIVE_ACTION_BRANCHES'),'older_comparison':data['older_comparison']['FORMAS_ACCESIBLES'],'older_contact':data['older_contact']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_PHYSICAL_WORD_UNDERSTANDING_AND_PEER_LEARNING13',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
