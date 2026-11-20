"""Prepared guard blocked the old action entry, not the learned word match."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_INTEGRATED12_intact';life='ES01_WORD_ACTION16_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'criteria_before':'Old lead3 failed because action input points coincide with native latent-cue guards. Keep the same token, native match and consequence location; use lead1. Expected consequence direction[0,0,1] unchanged. Equal-dose offpath controls leave the word match available.'}
def trial(x):
 data['old_blocked_sites']={label:observe(x.world,site)for label,site in{'far3_action_entry':[42,2,24],'far5_action_entry':[41,0,22]}.items()}
 word='cerca'if a.case=='cerca_lead1'else'lejos';data['word_use']=f.comprehend(x,frame='lexical05',word=word,action_lead=1,action_offpath=a.case=='lejos_offpath')
 data['bridge_use']=z.comprehend(x,bridge='near5Bridge',word=word);data['old_comparison']=e.query_words(x);data['old_contact']=e.contact_query(x,frame='contactoA');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'actions':[row['action_banks']for row in data['word_use']['ENTE']],'bridge_action':data['bridge_use']['NATIVE_ACTION_OBSERVED'],'old_comparisons':data['old_comparison']['FORMAS_ACCESIBLES'],'old_contact':data['old_contact']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_WORD_ACTUATOR_LEAD1_COMPATIBILITY_CORRECTION16',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
