"""Literal PI07 R03 episode with declared PI08 B reference hooks.
Source: pi07_regulacion_R03.py SHA40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5.
The two behavioral hooks choose ONLY the external reference action after the
actual sensor, and update ONLY its table after the actual outcome. Native arms
execute their measured Native choice. Remaining changes expose provenance.
This file executes only in the isolated component namespace, never standalone.
"""
def episode(a,row,directory):
 validate(a,row);p,ph=protocol(material=True);identity=_identity(a);m=_get(a);start=int(a.tick);spec=(p['viability']['schedule']if m['role']=='viability'else p['schedule'])[m['ordinal']]
 refs=[_observe(a,at(v))for v in((-1,-1,0),(1,-1,0))]
 if int(refs[0]['clock'])%782!=int(refs[1]['clock'])%782:raise ValueError('Reference phases diverged; no repair')
 cal=_helper().schedule_trial(start+16,int(refs[0]['clock'])+16,6);q=cal['query_tick'];seed=cal['seed_tick'];S=q-1;end=cal['contact_tick']+2
 if seed!=q+7 or cal['outcome_injection_tick']!=q+408 or end-start>p['max_ticks_per_episode']or q-2<=start:raise ValueError('Frozen six-lap calendar/source lead cannot fit; no adaptive retiming')
 forced=row.get('forzar')if row['modo']==CALIBRATE else None;ablation=row.get('actuator_ablation',False);sensor_ablation=row.get('sensor_ablation',False)
 used,safety,recorder=_instrumented(a,m,p,q,identity);body_literal_before=_old_literals(a)
 if forced is not None:m['forced_action']=forced
 m['pending']={'phase':'episode_started','ordinal':m['ordinal'],'query_tick':q};m['uncertain']=True;_save(a,m)
 _record(a,m,directory,{'kind':'OPPORTUNITY_INTENT','ordinal':m['ordinal'],'calendar':cal,'environment_spec':spec,'forced_operator_action':forced,'actuator_ablation':ablation,'attribution':'Environment inputs are prepared. Actor sees only the fixed physical state datum; diagnostic force is not learned selection.'})
 requests=[];message_artifact=None
 try:
  if spec['cue']!='none':
   site,direction=CUES[spec['cue']];_submit(a,'PI07.environment.'+spec['cue']+'.R01',0,q-2,requests,site=site,direction=direction)
  used.run_until(S);sensor=_observe(a,SENSOR);datum=int(sensor['state'])
  if not 0<=datum<=3:raise RuntimeError('Native2bit state outside declared identity codec')
  sent_datum=0 if sensor_ablation else datum
  requests.extend(_helper().submit_query(a.world,q,prefix=PREFIX));_submit(a,PREFIX+'.datum',sent_datum,q+3,requests,site=at((-1,0,1)),direction=(0,0,0))
  used.run_until(q+4);reader=_read(a,q);used.run_until(q+6);native_motor=_motor(reader['choice']);reference_policy_before=dict(m['reference_policy'])if m['control']['arm']=='reference'else None;motor=_b_choose_action(m,datum,native_motor)
  if motor is not None:requests.append(_helper().submit_motor_copy(a.world,motor,seed,prefix=PREFIX))
  # A fixed environment pulse may compete with the selected actuator at one
  # Native inlet. Runtime, not this host, resolves the same-boundary conflict.
  message_request=None
  if spec['message_payload']is not None:message_request=_submit(a,MESSAGE_CHANNEL,spec['message_payload'],seed,requests,site=ACTUATOR,direction=(1,0,0))
  action=_emit(a,motor,seed,requests,ablation)
  _record(a,m,directory,{'kind':'NATIVE_SELECTION_AND_FIXED_ACTUATOR','sensor':{'site':list(SENSOR),'tick':S,'observation':sensor,'actual_state_datum':datum,'submitted_state_datum':sent_datum,'link_ablation_to_material_zero':sensor_ablation},'reader':reader,'native_motor':native_motor,'actual_motor':motor,'operator_forced':forced is not None,'copy_at_seed':motor is not None,'actuator_request':action})
  used.run_until(seed+1);message_observation=_observe(a,MESSAGE_READER);mv=list(message_observation['direction']);message_valid=int(message_observation['state'])>0 and int(message_observation['semantic'])==1 and mv==[1,0,0]
  actual_message=int(message_observation['s_reg'])if message_valid else None
  message_receipt=None
  if message_request is not None:
   _,_,exact,_,_=_native();message_receipt=exact(a.world.runtime.receipt(message_request['id']))
  delivered=bool(message_receipt and message_receipt['status']=='applied'and message_valid and spec['message_payload']is not None and actual_message==spec['message_payload'])
  if message_valid:
   home=_home(directory,identity['life_id']);name='mensaje_%04d.bin'%m['ordinal'];file=home/name;content=actual_message.to_bytes(8,'little')*8
   with file.open('xb')as out:out.write(content);out.flush();os.fsync(out.fileno())
   message_artifact={'file':name,'bytes':64,'sha256':_sha(content),'actual_Native_payload':actual_message,'scope':'Actual measured Native value, no expected-value substitution; simulated information resource, not physical food or energy.'}
  used.run_until(q+136)
  from capacidades import pi05_transito_causal_R01 as baseline
  planned_FI=baseline._calendar(used)
  result_FI=baseline._fiplus(used,{'modo':baseline.FIPLUS,'izquierda':spec['left'],'derecha':spec['right'],'captura':'normal'},directory)
  requests.extend(result_FI['requests'])
  if int(a.tick)>=cal['outcome_injection_tick']:raise RuntimeError('Actual function missed generic-return deadline; no past return or reset')
  actual_failed=(result_FI['old_q6_choice']!=1)or(spec['message_payload']is not None and not delivered)
  arm=m['control']['arm'];_b_after_actual_outcome(m,datum,motor,actual_failed);returned=_return(m,actual_failed)
  used.run_until(cal['outcome_injection_tick']-1)
  outcome=_helper().submit_generic_outcome(a.world,returned,cal['outcome_injection_tick'],prefix=PREFIX);requests.append(outcome)
  _record(a,m,directory,{'kind':'ACTUAL_FUNCTION_AND_GENERIC_RETURN','FI':result_FI,'message':{'required_payload':spec['message_payload'],'observation_tick':seed+1,'observation':message_observation,'actual_payload':actual_message,'own_native_receipt':message_receipt,'delivered_exact':delivered,'artifact':message_artifact},'actual_failed':actual_failed,'returned_failed':returned,'feedback_arm':arm,'outcome':outcome,'no_action_or_bank_argument_to_return':True})
  return_frames=[]
  for tick in(cal['outcome_injection_tick'],cal['collision_tick'],cal['contact_tick'],end):
   used.run_until(tick);return_frames.append({'tick':int(a.tick),'hub':_observe(a,at((0,-1,-2))),'A':_observe(a,at((-1,-1,0))),'B':_observe(a,at((1,-1,0)))})
  requests=_receipts(a,requests);summary=_summary(requests,start,int(a.tick));terminal=summary['all_terminal']
  if action is not None:action=next(r for r in requests if r['id']==action['id'])
  if message_request is not None:message_request=next(r for r in requests if r['id']==message_request['id'])
  pulse_applied=bool(action is not None and action['receipt']['status']=='applied')
  result={'version':VERSION,'life_id':identity['life_id'],'preparation_life_id':m['body_P0']['preparation_life_id'],'ordinal':m['ordinal'],'cumulative_PI07_ordinal':28+m['ordinal'],'before_tick':start,'after_tick':int(a.tick),'new_native_ticks':int(a.tick)-start,'calendar':cal,'environment_spec':spec,
   'sensor':{'site':list(SENSOR),'tick':S,'observation':sensor,'actual_state_datum':datum,'submitted_state_datum':sent_datum,'link_ablation_to_material_zero':sensor_ablation},'reader':reader,'native_motor':native_motor,'actual_motor':motor,'operator_forced_action':forced,'executed_action_source':'external_contextual_WSLS'if arm=='reference'else 'Native_TC','reference_policy_before':reference_policy_before,'reference_policy_after':dict(m['reference_policy'])if arm=='reference'else None,'B_ordinal':m['ordinal']-m['control']['from_ordinal'],'global_regulatory_ordinal':m['ordinal'],
   'Native_selection_valid':native_motor is not None,'actuator_ablation':ablation,'sensor_ablation':sensor_ablation,'actuator_request':action,'pulse_scheduled':action is not None,'pulse_applied':pulse_applied,'pulse_emitted':pulse_applied,
   'message':{'request':message_request,'own_native_receipt':message_receipt,'read_tick':seed+1,'site':list(MESSAGE_READER),'observation':message_observation,'actual_payload':actual_message,'required_payload':spec['message_payload'],'delivered_exact':delivered,'artifact':message_artifact},
   'FI':result_FI,'FI_planned_calendar':planned_FI,'FI_query_expected':q+192,'FI_query_matches_predicted_phase':result_FI['calendar']['query_tick']==q+192,
   'actual_failed':actual_failed,'returned_failed':returned,'feedback_arm':arm,'requests':requests,'Native_inputs':summary,'reference_before':refs,'return_frames':return_frames,
   'physical_after':_physical(a),'external_global_capture':None if recorder is None else recorder.close(),'R01_R02_metadata_literal_unchanged':_old_literals(a)==body_literal_before,
   'host_safety':{'check_max_step_ticks':32,'observations':safety.safety,'is_external_not_learned_regulation':True},
   'scope':'New prepared Native selection plus identity sensor and fixed transducer. Host offers opportunities/environment and evaluates actual function; forced controls are not Native learned decisions. Useful learning requires causal controls and conservation.'}
  if _old_literals(a)!=body_literal_before:raise RuntimeError('R01 preparation metadata was modified')
  m['ordinal']+=1;m['rows'].append({'ordinal':result['ordinal'],'after_tick':int(a.tick),'native_choice':reader['choice'],'actual_failed':actual_failed,'pulse_scheduled':action is not None,'pulse_applied':pulse_applied,'message_delivered':delivered,'message_artifact':message_artifact,'FI_choice':result_FI['old_q6_choice'],'forced':m['control']['arm']=='reference'})
  m['pending']=None if terminal else{'phase':'unknown_terminal_receipts'};m['uncertain']=not terminal
  _record(a,m,directory,{'kind':'EPISODE_COMPLETED','result':result})
  return result
 except BaseException as error:
  if recorder is not None:
   try:recorder.close()
   except Exception:pass # A previously finalized capture is preserved, never overwritten.
  m['uncertain']=True;m['pending']={'phase':'preserved_incomplete_episode','ordinal':m['ordinal'],'tick':int(a.tick),'reason':type(error).__name__}
  _save(a,m)
  raise

