"""Long matched A/B/C query-dose trajectories; more acquisition in each life."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
if a.case not in('A_available','B_query_regulated','C_fewer_queries'):raise ValueError('Unknown fixed comparison arm')
s=Store(a.system);parent='ES01_LEXICAL5_source_guards_strict';life='ES01_LONG6_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'episodes':[],'teaching':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'dependency_sha256':{m.__name__:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in(e,f,eq)},
 'contract_before':{'decoder':'strict unchanged6/10','block_ticks':402,'episodes':24,'same_initial_state':True,'same_current_event_ticks':True,'B_extra_R0_guards':6,'A_B_extra_all_phase_word_query_each_episode':True,'C_no_extra_intermediate_word_query':True,'no_independent_replicate_claim':True}}
sequence=[(3,5),(-5,3),(-3,5),(5,3),(3,3),(-3,3),(-5,5),(5,5),(-3,3),(3,5),(5,3),(-5,3),
 (5,5),(-3,5),(3,3),(-5,5),(-3,3),(5,3),(-5,3),(3,5),(5,5),(3,3),(-3,5),(-5,3)]
data['predeclared_current_events']=sequence
def trial(x):
 if a.case=='B_query_regulated':data['query_regulator']=f.regulate_queries(x,frame='lexical05')
 # Align after the optional guard installation, before identical real lessons.
 boundary=e.tick_at_or_after(x.tick,phase=13,lead=4);x.run_until(boundary)
 data['teaching'].append(f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=0))
 data['teaching'].append(f.teach(x,frame='lexical05',parameter=-5,word='lejos',phase_shift=4))
 data['four_acquisitions_before_stream']=f.query(x,frame='lexical05')
 first=e.tick_at_or_after(x.tick,phase=13,lead=4);data['first_block_tick']=first
 for j,(k,load)in enumerate(sequence):
  boundary=first+402*j
  if x.tick>boundary:raise RuntimeError('Fixed trial calendar exceeded; do not shift it to hide a delay')
  x.run_until(boundary);row={'episode':j+1,'block_start':boundary,'environment_parameter':k,'load_each':load,'expected_auditor_only':'cerca'if k>0 else'lejos'}
  row['current']=f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict')
  if a.case!='C_fewer_queries':row['extra_probe']=f.query(x,frame='lexical05')
  x.run_until(boundary+401);row['block_end']=x.tick;row['physical']=physical(x.world,occupation=True);data['episodes'].append(row)
  if j in(3,11,23):x.save(a.out/('T'+str(x.tick)+'.deetsnap.gz'))
 data['final_lexical_query']=f.query(x,frame='lexical05');data['prior_comparison_forms']=e.query_words(x)
 data['prior_contact']=e.contact_query(x,frame='contactoA');data['prior_free']=e.contact_query(x,frame='freeRepair5');data['prior_temporal']=e.temporal_query(x,frame='secuenciaA');data['prior_equal']=eq.query(x)
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'current_responses':[r['current']['SPANISH_DECODED']for r in data['episodes']],
  'final_words':data['final_lexical_query']['SPANISH_DECODED'],'prior_comparisons':data['prior_comparison_forms']['FORMAS_ACCESIBLES'],'prior_contact':data['prior_contact']['SPANISH_DECODED'],'prior_free':data['prior_free']['SPANISH_DECODED'],'prior_equal':data['prior_equal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_ACCUMULATIVE_LEXICAL_LONG_MATCHED_QUERY_DOSE_R6',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
