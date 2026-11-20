"""Auditoría aritmética sin motor: no ejecuta mundos ni decide entradas del ente.

Lee campos primarios exactos; no toma un PASS ni SPANISH_DECODED como verdad.
Uso: python recalcular.py --datos EVIDENCIA_PRIMARIA --salida CALCULOS.json
"""
from pathlib import Path
import argparse,json,hashlib,collections

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def good(r,v):return bool(r.get('active'))and r.get('state')==1 and r.get('semantic')==1 and r.get('direction')==list(v)
def lexical(r,labels=('cerca','lejos')):
 v=r.get('direction',[])
 return (labels[0]if v[0]==1 else labels[1])if len(v)==3 and v[0]in(-1,1)and good(r,(v[0],1,1))else None
def context(c,dose=7,labels=('cerca','lejos')):
 out=[];details=[]
 for row in c['ENTE']:
  words=[]
  for bank,old in row['before'].items():
   new=row['after'][bank];delta=new['s_reg']-old['s_reg']-dose
   if delta in(6,10)and lexical(old,labels)is not None and lexical(new,labels)is not None:words.append(lexical(new,labels))
  out.extend(words);details.append({'tick':row['tick'],'words_from_primary':words})
 return sorted(set(out)),details
def bridge(c):
 old,new=c['ENTE']['before'],c['ENTE']['after'];dose=7 if c['INSTRUMENTO']['probe']else 0
 delta=new['s_reg']-old['s_reg']-dose;w=lexical(new)
 return ([w]if w is not None and lexical(old)==w and delta in(6,10)else[])
def comparative(c):
 words=[];old=c['ENTE']['previous_word_signal'];new=c['ENTE']['current_word_signal'];dose=7 if c['INSTRUMENTO']['method']=='A'else 0
 for word,sign in(('menos',1),('más',-1)):
  if good(old[word],(sign,sign,-sign))and good(new[word],(sign,sign,-sign))and new[word]['s_reg']-old[word]['s_reg']-dose==7:words.append(word)
 return words
def walk(x,path='$'):
 if isinstance(x,dict):
  yield path,x
  for k,v in x.items():
   if k not in('parent','commit'):yield from walk(v,path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,path+'['+str(i)+']')
def run(root):
 files=sorted(root.rglob('PRIMARIOS.json'));out={'schema':'DCS1.1.EF01.recalculo.sin_motor.v1','primary_files':len(files),'formulas':{
 'comparative':'state1SEM1/signature before and after; s_after-s_before-declared_word_probe_dose == 7',
 'lexical_context':'state1SEM1 with native Y=Z=1, native X selects fixed codeword; s_after-s_before-dose in {6,10}',
 'bridge':'same acquired word before/after and net native increment in {6,10}',
 'quality':'correct/requested scenes, answered/requested scenes, incorrect and abstentions all retained',
 'not_energy':'s_reg is a native field, not electricity, RAM, or a count of thoughts'},'streams':{},'long_query_dose':{},'integrated':{},'expansion':{},'receipt_coverage_by_file':{},'uint64_errors':[],'translated_record_mismatches':[]}
 total_records=0
 out.update(temporal_arbitrary={},causal_composition={},peer_word_learning={},actuator_lead={},reference_relearning={},contact_return={},exact_replays={},late_access={},public_cli={},cross_process_saved_states=[])
 for p in files:
  rel=p.relative_to(root).as_posix();d=read(p);receipts={};record_count=0
  for loc,r in walk(d):
   if 'raw'in r and'clock'in r:
    record_count+=1
    for key in('raw','clock'):
     v=r[key]
     if isinstance(v,bool)or not isinstance(v,(int,str)):
      out['uint64_errors'].append([rel,loc+'.'+key,'not_exact_integer']);continue
     try:
      n=int(v)
      if not 0<=n<2**64:raise ValueError('range')
     except(ValueError,TypeError):out['uint64_errors'].append([rel,loc+'.'+key,'out_of_range'])
   if 'id'in r and'status'in r and'requested_tick'in r:
    key=str(r['id']);old=receipts.get(key)
    if old is None or old['status']in('pending','queued','accepted'):receipts[key]=r
  total_records+=record_count
  statuses=collections.Counter(r['status']for r in receipts.values())
  out['receipt_coverage_by_file'][rel]={'unique_recorded_ids':len(receipts),'statuses':dict(statuses),'coverage':'Only receipts actually present in this file; initial exploratory files may omit other protocol requests. Not a global admission denominator.','exact_records':record_count}
  if rel.startswith('FLUJO_R1/'):
   rows=[]
   for ep in d['episodes']:
    words=[]
    for word,sign in(('menos',1),('mas',-1)):
     old=ep['previous_word_signal'][word];new=ep['current_word_signal'][word]
     if good(old,(sign,sign,-sign))and good(new,(sign,sign,-sign))and new['s_reg']-old['s_reg']-ep['word_probe_dose']==7:words.append('más'if word=='mas'else'menos')
    center=ep['native_comparison']['center'];v=center['direction'];expected='menos'if good(center,(1,0,0))else('más'if good(center,(-1,0,0))else('igual_sin_palabra_en_este_protocolo'if good(center,(0,0,0))else'indeterminado'))
    if words!=ep['decoded']['SPANISH_DECODED']:out['translated_record_mismatches'].append([rel,ep['episode'],'comparative'])
    rows.append({'episode':ep['episode'],'object_input':ep['actual_object_input'],'native_direction':v,'native_relation':expected,'recomputed_words':words,'correct_two_word_domain':words==[expected]})
   out['streams'][d['case']]={'scenes':len(rows),'non_equal_native':sum(r['native_relation']in('menos','más')for r in rows),'correct_non_equal':sum(r['correct_two_word_domain']for r in rows),'abstentions':sum(not r['recomputed_words']for r in rows),'rows':rows}
  if rel.startswith(('CONTINUIDAD_LEXICA_06/','CONTINUIDAD_SIN_SONDAS_07/')):
   rows=[];dose=0 if d['case']=='D_no_material_queries'else 7
   for ep in d['episodes']:
    words,detail=context(ep['current'],dose);k=ep['environment_parameter'];expected='cerca'if k>0 else'lejos';stored=sorted(set(r['text']for r in ep['current']['SPANISH_DECODED']))
    if words!=stored:out['translated_record_mismatches'].append([rel,ep['episode'],'long'])
    rows.append({'episode':ep['episode'],'block_start':ep['block_start'],'parameter':k,'load':ep['load_each'],'words':words,'correct':words==[expected],'abstention':not words,'phase_details':detail})
   out['long_query_dose'][d['case']]={'scenes':len(rows),'correct':sum(r['correct']for r in rows),'abstentions':sum(r['abstention']for r in rows),'incorrect_nonempty':sum(not r['correct']and not r['abstention']for r in rows),'final_tick':d['post']['tick'],'occupied':d['post']['occupied'],'rows':rows}
  if rel.startswith(('INTEGRACION_PUENTE_12/','AMPLIACION_17/','ACCESO_TARDIO_29/')):
   rows=[]
   for ep in d['episodes']:
    legacy=ep['ENTE']['legacy'];dose=legacy.get('INSTRUMENTO',{}).get('word_probe_dose_per_bank',7);words,_=context(legacy,dose);words=sorted(set(words+bridge(ep['ENTE']['alternative'])));k=ep['ENTORNO']['actual_parameter'];expected='cerca'if k>0 else'lejos'
    if words!=ep['SPANISH_DECODED']:out['translated_record_mismatches'].append([rel,ep.get('episode'),'integrated'])
    rows.append({'episode':ep.get('episode'),'parameter':k,'load':ep['ENTORNO']['load_each'],'presentations':ep['ENTORNO']['physical_scene_presentations'],'words':words,'correct_trained':words==[expected],'abstention':not words})
   group='integrated'if rel.startswith('INTEGRACION')else('late_access'if rel.startswith('ACCESO_TARDIO')else'expansion');trained=rows if group=='expansion'else[r for r in rows if abs(r['parameter'])in(3,5)]
   out[group][d['case']]={'scenes':len(rows),'trained_scenes':len(trained),'correct_trained':sum(r['correct_trained']for r in trained),'abstentions_all':sum(r['abstention']for r in rows),'wrong_nonempty':sum(not r['correct_trained']and not r['abstention']for r in rows),'rows':rows}
  if rel.startswith('TIEMPO_LEXICO_20/'):
   rows=[]
   for ep in d['episodes']:
    words,details=context(ep,labels=('antes','después'));expected='antes'if ep['ENTORNO']['actual_parameter']>0 else'después'
    if words!=sorted(set(r['text']for r in ep['SPANISH_DECODED'])):out['translated_record_mismatches'].append([rel,ep['episode'],'time20'])
    rows.append({'episode':ep['episode'],'parameter':ep['ENTORNO']['actual_parameter'],'load':ep['ENTORNO']['load_each'],'words':words,'correct_relation':words==[expected]})
   out['temporal_arbitrary'][d['case']]={'rows':rows,'correct':sum(r['correct_relation']for r in rows),'scenes':len(rows),'abstentions':sum(not r['words']for r in rows)}
  if rel.startswith('COMPOSICION_01/'):
   records={r['label']:r['record']for r in d['frames']};out['causal_composition'][d['case']]={'join':good(records['join'],(-1,1,1)),'physical_consequence':good(records['consequence'],(0,1,1)),'join_raw':records['join']['raw'],'consequence_raw':records['consequence']['raw']}
  if rel.startswith('COMPRENSION_Y_SOCIAL_13/')and'social'in d:
   c=d['social'];frames={r['label']:r for r in c['ENTE']};words=[lexical(r)for r in frames['B_query']['records'].values()if lexical(r)is not None];actions=[]
   if'B_action'in frames:actions=[k for k,r in frames['B_action']['records'].items()if good(r,(0,0,1))]
   if words!=c['B_WORDS_DECODED']or actions!=c['B_NATIVE_ACTION_BRANCHES']:out['translated_record_mismatches'].append([rel,'social13'])
   out['peer_word_learning'][d['case']]={'B_words_from_primary':words,'B_actions_from_primary':actions,'same_world_prepared_recipient':True,'not_human_distance_semantics':True}
  if rel.startswith('ACCION_LEIDA_16/'):
   actions=[[k for k,r in row['effects'].items()if good(r,(0,0,1))]for row in d['word_use']['ENTE']];bridge_action=good(d['bridge_use']['ENTE']['effect'],(0,0,1))
   out['actuator_lead'][d['case']]={'actions':actions,'bridge_action':bridge_action}
  if rel.startswith('REAPRENDIZAJE_MAGNITUD_26/'):
   rows=[]
   for ep in d['episodes']+[d['late_less'],d['late_more']]:
    words=comparative(ep);value=ep['ENTORNO']['actual_object_magnitude'];expected='menos'if value+5<91 else'más'
    if words!=ep['TRADUCCION']['SPANISH_DECODED']:out['translated_record_mismatches'].append([rel,ep.get('episode'),'relearning26'])
    rows.append({'object_value':value,'native_comparison':ep['ENTE']['native_comparison'],'words':words,'correct':words==[expected]})
   out['reference_relearning'][d['case']]={'scenes':len(rows),'correct':sum(r['correct']for r in rows),'abstentions':sum(not r['words']for r in rows),'rows':rows,'explicit_new_reference_experience_not_retention':True}
  if rel.startswith('RETORNO_CONTACTO_27/'):
   observed=[]
   for ep in d['queries']+[d['last_query']]:
    words=[]
    for bank,r in ep['ENTE']['output'].items():
     axis=-1 if bank.endswith('izq')else 1;z=0 if bank.startswith('toca')else-1
     if good(r,(-axis,1,z)):words.append('toca'if z==0 else'no toca')
    words=list(dict.fromkeys(words))
    if words!=ep['SPANISH_DECODED']:out['translated_record_mismatches'].append([rel,'contact27'])
    observed.append(words)
   out['contact_return'][d['case']]={'first_and_later':observed,'comparatives':[comparative(d['less']),comparative(d['more'])],'spatial':[d['spatial_near']['SPANISH_DECODED'],d['spatial_far']['SPANISH_DECODED']]}
  if rel.startswith(('TRAZA_REFERENCIA_SOCIAL_23/','TRAZA_REFERENCIA_IGUAL_24/')):
   original=next((root/'MAIN_SOCIAL_04'if rel.startswith('TRAZA_REFERENCIA_SOCIAL')else root/'MAIN_IGUAL_05').rglob('PRIMARIOS.json'));ref=read(original)['post']
   out['exact_replays'][rel]={'physical_identity':{k:d['post'][k]==ref[k]for k in('tick','RAW_sha256','clocks_sha256')},'first_tracked_direction_change_tick':None if d['first_change']is None else d['first_change']['post_tick'],'not_independent_new_sample':True}
 complete=root/'RECIBOS_COMPLETOS_SNAPSHOTS.json'
 if complete.exists():
  out['complete_admission_denominators']=[]
  for item in read(complete)['cases']:
   if'new_receipts'not in item:
    out['complete_admission_denominators'].append({'primary':item['primary'],'coverage':item['coverage'],'unknown_not_zero':True});continue
   r=item['new_receipts'];counts=dict(collections.Counter(v['status']for v in r))
   if len(r)!=item['new_request_count']or counts!=item['new_request_statuses']:out['translated_record_mismatches'].append([item['primary'],'receipt_denominator'])
   out['complete_admission_denominators'].append({'primary':item['primary'],'coverage':item['coverage'],'requested_new':len(r),'statuses_recomputed':counts,'inherited_status_transitions':len(item['inherited_receipt_transitions']),'read_did_not_change_physical_state':item['physical_before']==item['physical_after']})
 # Also validate exact integers in route witnesses, CLI outputs and extracted receipts.
 for p in sorted(root.rglob('*.json')):
  if p.name=='PRIMARIOS.json':continue
  for loc,r in walk(read(p)):
   if'raw'in r and'clock'in r:
    total_records+=1
    for key in('raw','clock'):
     v=r[key]
     try:
      if isinstance(v,bool)or not isinstance(v,(int,str))or not 0<=int(v)<2**64:raise ValueError('not uint64')
     except(ValueError,TypeError):out['uint64_errors'].append([p.relative_to(root).as_posix(),loc+'.'+key,'not_exact_uint64'])
 for p in sorted(root.rglob('COMANDOS.json')):
  rows=[];saved=None
  for i,command in enumerate(read(p)):
   result_file=p.parent/command['stdout'];document=read(result_file)if command['exit_code']==0 else{};r=document.get('result',{});argv=command['command'];row={'step':i,'exit_code':command['exit_code'],'primary':result_file.relative_to(root).as_posix()}
   if isinstance(r,dict)and isinstance(r.get('ENTE'),dict)and'legacy'in r['ENTE']and'alternative'in r['ENTE']:
    old=r['ENTE']['legacy'];words,_=context(old,old['INSTRUMENTO'].get('word_probe_dose_per_bank',7));words=sorted(set(words+bridge(r['ENTE']['alternative'])));row.update(words=words,actual_parameter=r['ENTORNO']['actual_parameter'])
    if words!=r['SPANISH_DECODED']:out['translated_record_mismatches'].append([row['primary'],'CLI_integrated'])
   elif isinstance(r,dict)and'TRADUCCION'in r and'previous_word_signal'in r.get('ENTE',{}):
    words=comparative(r);row.update(words=words,actual_magnitude=r['ENTORNO']['actual_object_magnitude'])
    if words!=r['TRADUCCION']['SPANISH_DECODED']:out['translated_record_mismatches'].append([row['primary'],'CLI_comparative'])
   elif isinstance(r,dict)and isinstance(r.get('ENTE'),list)and r['ENTE']and'before'in r['ENTE'][0]:
    words,_=context(r,r['INSTRUMENTO'].get('word_probe_dose_per_bank',7));row['words']=words
    if words!=sorted(set(v['text']for v in r['SPANISH_DECODED'])):out['translated_record_mismatches'].append([row['primary'],'CLI_lexical'])
   if'guardar'in argv and command['exit_code']==0:saved={'physical':document['physical'],'snapshot_sha256':document['INSTRUMENTO']['snapshot_sha256'],'primary':row['primary']}
   if'restaurar'in argv and saved is not None and command['exit_code']==0:
    out['cross_process_saved_states'].append({'saved':saved['primary'],'loaded':row['primary'],'equal_tick_RAW_clocks':all(saved['physical'][k]==document['physical'][k]for k in('tick','RAW_sha256','clocks_sha256')),'same_complete_snapshot_sha256':saved['snapshot_sha256']==document['INSTRUMENTO']['snapshot_sha256']})
   rows.append(row)
  out['public_cli'][p.parent.relative_to(root).as_posix()]=rows
 out['exact_record_count']=total_records
 out['no_automatic_mind_verdict']=True;out['uses_native_engine']=False
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--datos',type=Path,required=True);p.add_argument('--salida',type=Path);a=p.parse_args();result=run(a.datos);body=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if a.salida:a.salida.write_text(body,encoding='utf8')
 else:print(body)
 print(json.dumps({'files':result['primary_files'],'exact_records':result['exact_record_count'],'uint64_errors':len(result['uint64_errors']),'translation_mismatches':len(result['translated_record_mismatches'])}))
 raise SystemExit(bool(result['uint64_errors']or result['translated_record_mismatches']))
