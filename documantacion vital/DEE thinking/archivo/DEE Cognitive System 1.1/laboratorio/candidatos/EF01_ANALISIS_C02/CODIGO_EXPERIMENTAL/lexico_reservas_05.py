"""New reserved sequences after cue cleanup and optional physical source renewal.

The old strict decoder failures remain unchanged. This cut preregisters a
bounded native-provision band and evaluates missing-current-event controls.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
s=Store(a.system);parent='ES01_MAIN_05';life='ES01_LEXICAL5_'+a.case;s.fork(parent,life,kind='CANDIDATE')
renew=a.case!='band_only_no_source_guards';decoder='strict'if a.case=='source_guards_strict'else'bounded_native_provision'
data={'case':a.case,'life':life,'parent':s.record(parent),'phases':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependency_sha256':{m.__name__:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in(e,f)},
 'predeclared_decoder':decoder,'native_source_renewal':renew,'scope_before':'Prepared19supports=12latent-cue absorbers+7unmatched-source absorbers; phase0/4 teacher scheduling. Current scenes repeated at both acquired phases, no semantic phase selection. No R2 autonomy claim.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row,'physical':physical(x.world,occupation=True)})
def trial(x):
 f.prepare(x,frame='lexical05',mode='relative_path',origin=(38,50,8),guarded=True,renew_sources=renew)
 cap(x,'teach_near3',f.teach(x,frame='lexical05',parameter=3,word='cerca',phase_shift=0))
 cap(x,'first_near_recall',f.query(x,frame='lexical05'))
 cap(x,'teach_far3_phase4',f.teach(x,frame='lexical05',parameter=-3,word='lejos',phase_shift=4))
 cap(x,'both_recall',f.query(x,frame='lexical05'))
 sequence=[(-3,5),(3,3),(-3,3),(3,5),(5,3),(-5,3)]
 if a.case=='order_delay_reserve':sequence=[(3,5),(-3,3),(3,3),(-3,5),(-1,3),(1,3)]
 for j,(k,load)in enumerate(sequence):
  kwargs={}
  if a.case=='current_no_A':kwargs['event_a']=False
  if a.case=='current_B_offroute':kwargs['offroute']=True
  if a.case=='current_no_events':kwargs.update(event_a=False,event_b=False)
  cap(x,'current_'+str(j)+'_'+str(k),f.context(x,frame='lexical05',parameter=k,load=load,decoder=decoder,**kwargs))
 cap(x,'retention_after_all_current_scenes',f.query(x,frame='lexical05'))
 data['old_words']=e.query_words(x);data['old_contact']=e.contact_query(x,frame='contactoA');data['old_free']=e.contact_query(x,frame='freeRepair5');data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'responses':[{'label':r['label'],'response':r['result'].get('SPANISH_DECODED')}for r in data['phases']],'old_words':data['old_words']['FORMAS_ACCESIBLES'],'contact':data['old_contact']['SPANISH_DECODED'],'free':data['old_free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_LEXICAL_SOURCE_RENEWAL_NEW_DECODER_RESERVED_CUT5',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
