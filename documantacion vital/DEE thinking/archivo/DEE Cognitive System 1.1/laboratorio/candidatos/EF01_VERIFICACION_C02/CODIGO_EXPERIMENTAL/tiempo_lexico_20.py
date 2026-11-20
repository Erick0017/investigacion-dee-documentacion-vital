"""Test whether source guards transfer the arbitrary marker method to order.

Earlier unguarded shared-order candidates destabilized; do not rerun them.
This is a new guarded preparation on an exact fork of the current lived E1.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as z
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='E1_ESPANOL_01';life='ES01_TIME_LEX20_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'lessons':[],'episodes':[],
 'criteria_before':'Arbitrary native X binds antes/después only in acquisition, not inferred from currentA/Bticks. State1SEM1 XYZ marker, strict6/10 net modulation unchanged. New temporal frame has cue guards and source guards; sham spatially shifts cue guards. +/-3 taught; load5 reserved; +/-5 untrained probes must not be counted as successful generalization when silent. Earlier Spanish frames must remain queryable.'}
def translated(c):
 return sorted(set(r['text']for r in c['SPANISH_DECODED']))
def trial(x):
 f.prepare(x,frame='timeLex20',mode='event_order',origin=(5,14,44),guarded=True,sham_guards=a.case=='sham',renew_sources=True)
 for k,word,phase in((3,'antes',0),(-3,'después',4)):
  if a.case=='opposite':word='después'if word=='antes'else'antes'
  data['lessons'].append(f.teach(x,frame='timeLex20',parameter=k,word=word,phase_shift=phase,signal=a.case!='no_cue',event_a=a.case!='no_A',offroute=a.case=='offroute'))
 data['recall_initial']=f.query(x,frame='timeLex20')
 for k,load in((3,5),(-3,5),(5,3),(-5,3),(3,3),(-3,3)):
  row=f.context(x,frame='timeLex20',parameter=k,load=load);row['episode']=len(data['episodes'])+1;data['episodes'].append(row)
 data['recall_final']=f.query(x,frame='timeLex20');data['old_lexicon']=f.query(x,frame='lexical05');data['old_bridge']=z.query(x,bridge='near5Bridge');data['old_comparison']=e.query_words(x);data['old_contact']=e.contact_query(x,frame='contactoA');data['old_free']=e.contact_query(x,frame='freeRepair5');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'initial':data['recall_initial']['SPANISH_DECODED'],'new_contexts':[{'k':r['ENTORNO']['actual_parameter'],'load':r['ENTORNO']['load_each'],'words':translated(r)}for r in data['episodes']],'old_lexicon':data['old_lexicon']['SPANISH_DECODED'],'old_bridge':data['old_bridge']['SPANISH_DECODED'],'old_comparison':data['old_comparison']['FORMAS_ACCESIBLES'],'contact':data['old_contact']['SPANISH_DECODED'],'free':data['old_free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_SHARED_ARBITRARY_LEXICAL_METHOD_FOR_NATIVE_ORDER20',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
