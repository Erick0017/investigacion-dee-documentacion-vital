"""Finite stream decoder over native acquired comparison-word carriers.

The external decoder demodulates a fixed material signal code. It does not
compare object and reference magnitudes, inspect targets or choose DEE inputs.
Native comparison and carrier modulation are observable before translation.
"""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import observe,physical,moore27
from app.process_control import protect_current
from dee_thinking.consolidated import exact_receipt
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
plans={'A_every_word_probe':('paired','A'),'B_context_only':('paired','B'),'C_final_query_only':('paired','C'),'B_no_word_teaching':('omitted','B'),'B_no_past_event':('noevent','B'),'B_opposite_teaching':('opposite','B')}
source,method=plans[a.case];s=Store(a.system);life='ES01_STREAM_'+a.case;s.fork('ES01_R6_'+source,life,kind='CANDIDATE')
values=[56,93,73,80,99,86,42,101,86,65,123,86,79,92,86,81,98,86,55,96,86,70,94,86]
data={'case':a.case,'life':life,'parent':s.record('ES01_R6_'+source),'method':method,'values':values,'fixed_decoder':'Prior and current active acquired signature; native load change7 above declared word-reader dose. No arithmetic relation is computed by decoder. It is an instrument, not a native learned language rule.','teacher_labels_during_evaluation':False,'requests':[],'episodes':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
def signature(record,sign):return record['active'] and record['state']==1 and record['semantic']==1 and record['direction']==[sign,sign,-sign]
def decode(previous,current,word_probe):
 emissions=[];details={}
 for word,sign in [('menos',1),('mas',-1)]:
  before=previous[word];after=current[word];delta=after['s_reg']-before['s_reg'];prior_valid=signature(before,sign);now_valid=signature(after,sign)
  details[word]={'prior_valid':prior_valid,'current_valid':now_valid,'native_material_delta':delta,'declared_word_probe_dose':word_probe,'modulation_delta':delta-word_probe}
  if prior_valid and now_valid and delta-word_probe==7:emissions.append('más'if word=='mas'else'menos')
 return {'ENTE_SIGNAL':current,'INSTRUMENTO_FIXED_DECODER':details,'SPANISH_DECODED':emissions,'UNRESOLVED':not emissions,'not_a_general_language_decoder':True}
def trial(x):
 w=x.world;c=x.quantity.geometry['center'];hubs={word:move(c,(sign,0,0),3)for word,sign in [('menos',1),('mas',-1)]}
 previous={word:observe(w,site)for word,site in hubs.items()};data['initial_words']=previous;data['initial']=physical(w,occupation=True)
 for j,value in enumerate(values,1):
  k=58+j;center=70+67*k;target=center+3
  requested_before=len(x.quantity.state['requests']);x.quantity.present_object(value,round_index=k)
  ask=(method!='C'or j==len(values))
  if ask:x.quantity.input('quantity.reader',7,center-1,True)
  if j==3:
   x.quantity.input('quantity.reference.cue',0,center-3)
   x.quantity.input('quantity.reference.resource',13,center-3)
  word_probe=7 if method=='A'else 0
  if word_probe:
   for word,sign in [('menos',1),('mas',-1)]:
    rr=w.probe('EF01.R1.'+word+'.'+('query_minus'if sign==1 else'query_plus'),word_probe,target-3)
    data['requests'].append({'id':int(rr.id),'port':'EF01.R1.'+word+'.'+('query_minus'if sign==1 else'query_plus'),'payload':word_probe,'tick':target-3})
  old_two_window=None
  if j in(1,12,24):x.two_memory.input('quantity.reader',7,center+1,True)
  x.run_until(center-1);pre={'center':observe(w,c),'moore':moore27(w,c)}
  x.run_until(center);comparison={'center':observe(w,c),'reference':observe(w,x.quantity.geometry['reference_site']),'object':observe(w,x.quantity.geometry['object_site']),'moore':moore27(w,c)}
  x.run_until(target-1)
  if j in(1,12,24):old_two_window={'tick':x.tick,'center':observe(w,x.two_memory.geometry['center']),'moore':moore27(w,x.two_memory.geometry['center'])}
  x.run_until(target);current={word:observe(w,site)for word,site in hubs.items()}
  decoded=decode(previous,current,word_probe);data['episodes'].append({'episode':j,'actual_object_input':value,'comparison_tick':center,'word_tick':target,'query_requested':ask,'word_probe_dose':word_probe,'pre_comparison':pre,'native_comparison':comparison,'previous_word_signal':previous,'current_word_signal':current,'decoded':decoded,'old_two':old_two_window,'physical':physical(w,occupation=True)})
  previous=current
  if j in(4,12,24):x.save(a.out/('T'+str(x.tick)+'.deetsnap.gz'))
 # One later word-only query to measure retained associations after all new inputs.
 target+=67
 for word,sign in [('menos',1),('mas',-1)]:
  name='EF01.R1.'+word+'.'+('query_minus'if sign==1 else'query_plus');r=w.probe(name,7,target-3);data['requests'].append({'id':int(r.id),'port':name,'payload':7,'tick':target-3})
 x.run_until(target);data['retention_words']={word:observe(w,site)for word,site in hubs.items()}
 data['receipts']=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in data['requests']]
 data['quantity_receipts']=x.quantity.receipts();data['old_two_receipts']=x.two_memory.receipts();data['post']=physical(w,occupation=True)
 w.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.EF01.stream.v1',encode_metadata({'word_hubs':hubs,'word_signature':{'menos':[1,1,-1],'mas':[-1,-1,1]},'word_phase':3490,'period':67,'last_word_tick':target,'decoder_modality':'External fixed channel demodulator, not participant knowledge/targets','method':method,'new_reference_update_request':13}))
 return {'tick':x.tick,'new_contexts':len(values),'word_teaching_repeated':False,'modality':'Native material modulation plus declared external Spanish decoder'}
data['commit']=s.mutate(life,'EF01_CONTINUOUS_SPANISH_STREAM_R1',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'case':a.case,'tick':data['post']['tick'],'occupied':data['post']['occupied'],'decoded':[e['decoded']['SPANISH_DECODED']for e in data['episodes']],'retention':data['retention_words']},ensure_ascii=False))

