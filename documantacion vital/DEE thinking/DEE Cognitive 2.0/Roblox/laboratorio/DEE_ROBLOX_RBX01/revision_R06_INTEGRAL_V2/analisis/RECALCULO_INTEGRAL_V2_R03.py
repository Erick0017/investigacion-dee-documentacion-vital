"""Portable passive R06 accounting R03: interrupted and continued operation16.

Physical time comes only from unique actually completed Native phase IDs, never
from copied Q1/Q2 fields in a completed opportunity or sums of segment summaries.
An explicit known-not-admitted record permits ONE transport-shape correction;
both host attempts remain visible and only the actual completion contributes.

Does not import DEE/SQLite, run a model/Studio, follow historical source paths,
retry operations or simulate unobserved futures. Proposed criteria assessments
are scoped evidence, not an automatic scientific approval or global PASS.
"""
from pathlib import Path
from collections import Counter
import argparse,csv,datetime,hashlib,json,math,statistics
ARMS=('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI')
PARENT_TICK=953651;PARENT_CYCLES=4
PARENT_WORLD_SHA='7813c015dbf7a8b0eef33006ce0a3864b591359c68609051fec746a6d3890435'

def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def integer(v):return type(v)is int
def number(v):return type(v)in(int,float)and math.isfinite(v)
def read(path,sources):
 path=Path(path).resolve(strict=True)
 if path.is_symlink():raise ValueError('Explicit regular input required')
 before=path.stat();raw=path.read_bytes();after=path.stat()
 if(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Input changed while reading; freeze it first')
 if len(raw)>100_000_000:raise ValueError('Finite100MB input bound; no massive telemetry assumed')
 h=hashlib.sha256(raw).hexdigest();sources.append({'path':str(path),'bytes':len(raw),'sha256':h,'stable_size_mtime_during_read':True})
 text=raw.decode('utf-8-sig')
 reject=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON'))
 if path.suffix.lower()=='.jsonl':return [json.loads(line,parse_constant=reject)for line in text.splitlines()if line.strip()]
 return json.loads(text,parse_constant=reject)
def csv_file(path,rows):
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with path.open('w',encoding='utf-8-sig',newline='')as f:
  writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
  writer.writerows({k:canonical(v)if isinstance(v,(dict,list))else v for k,v in row.items()}for row in rows)
def stats(values):
 v=sorted(x for x in values if number(x))
 return {'n':len(v),'sum':sum(v)if v else None,'p50':statistics.median(v)if v else None,
         'p95_nearest_rank':v[max(0,math.ceil(.95*len(v))-1)]if v else None,'max':v[-1]if v else None}
def files(paths):
 result=[]
 for path in paths:
  p=Path(path)
  result.extend(sorted(p.glob('*.json'))if p.is_dir()else[p])
 return list(dict.fromkeys(result))
def classify_numeric(tool,request=None):
 tool=tool if isinstance(tool,dict)else{};request=request or{}
 if tool.get('kind')!='CALCULATE':return None
 actual=tool.get('numeric_result');formed=integer(actual)and tool.get('formed')is not False
 operands=tool.get('inputs')
 left=request.get('left',operands[0]if isinstance(operands,list)and len(operands)==2 else None)
 right=request.get('right',operands[1]if isinstance(operands,list)and len(operands)==2 else None)
 op=tool.get('operation');reference=left+right if integer(left)and integer(right)and op=='suma'else left-right if integer(left)and integer(right)and op=='diferencia'else None
 return {'slot':tool.get('slot',request.get('slot')),'form':tool.get('form',request.get('form')),
  'left':left,'right':right,'memory_value':tool.get('memory_value'),'operation':op,'actual':actual,'formed':formed,
  'zero_valid':formed and actual==0,'absent_or_NULL':not integer(actual),'reason':tool.get('reason'),
  'reference_offline_only':reference,'correct_for_actual_opcode':actual==reference if formed and reference is not None else None,
  'arithmetic_is_prepared_not_learned_algorithm':True}
def receipt_rows(value,life,receipts,issues):
 if isinstance(value,list):
  for x in value:receipt_rows(x,life,receipts,issues)
 elif isinstance(value,dict):
  if integer(value.get('id'))and isinstance(value.get('receipt'),dict)and isinstance(value.get('channel',value.get('port')),str):
   key=(life,value['id']);row={'life':life,'id':value['id'],'channel':value.get('channel',value.get('port')),
    'payload':value.get('payload',value.get('value')),'requested_tick':value.get('requested_tick',value.get('tick')),
    'status':value['receipt'].get('status')}
   if key in receipts:
    prior=receipts[key]
    for k in row:
     if row[k]is not None and prior.get(k)is not None and row[k]!=prior[k]:issues.append({'issue':'CONFLICTING_NATIVE_RECEIPT','life':life,'id':key[1],'field':k})
     if prior.get(k)is None:prior[k]=row[k]
   else:receipts[key]=row
  for x in value.values():receipt_rows(x,life,receipts,issues)
def source_arm(value,default):
 identity=value.get('identity',{})if isinstance(value,dict)else{}
 return identity.get('participant',default)
def transport_shape_equivalent(rejected,repaired):
 """Only the documented Lua numeric-key object -> ordered array conversion."""
 if not isinstance(rejected,dict)or not isinstance(repaired,dict)or set(rejected)!=set(repaired):return False
 if set(rejected)!={'tool'}:return False
 a,b=rejected['tool'],repaired['tool']
 if not isinstance(a,dict)or not isinstance(b,dict)or set(a)!=set(b)or set(a)!={'kind','items'}:return False
 if a.get('kind')!='LESSON'or b.get('kind')!='LESSON':return False
 old,new=a['items'],b['items']
 return isinstance(old,dict)and isinstance(new,list)and 1<=len(new)<=2 and set(old)=={str(i+1)for i in range(len(new))}and new==[old[str(i+1)]for i in range(len(new))]

def completed_phase_accounting(phases,intents,phase_arms,issues):
 """Unique operation IDs, exact actual deltas and interval overlaps/gaps."""
 records=[];groups={}
 for identifier,row in phases.items():
  if row.get('kind')!='NATIVE_COMPLETED':continue
  result=row.get('result')or{};after=result.get('nativeTick');ticks=result.get('nativeTicks')
  context=intents.get(identifier,{}).get('context',{});session=context.get('session_id')
  if not(integer(after)and integer(ticks)and ticks>=0):
   issues.append({'issue':'NATIVE_COMPLETION_WITHOUT_EXACT_TICK_INTERVAL','id':identifier});continue
  record={'operation_id':identifier,'participant':phase_arms.get(identifier),'session':session,
          'cycle':row.get('cycle'),'phase':row.get('phase'),'before_tick':after-ticks,
          'after_tick':after,'actual_ticks':ticks,'wall_seconds':row.get('wall_seconds')}
  if session is None:issues.append({'issue':'NATIVE_PHASE_SESSION_UNKNOWN','id':identifier})
  records.append(record);groups.setdefault((record['participant'],session),[]).append(record)
 summary=[]
 for (arm,session),values in sorted(groups.items(),key=lambda x:str(x[0])):
  ordered=sorted(values,key=lambda x:(x['before_tick'],x['after_tick'],x['operation_id']))
  intervals=[x for x in ordered if x['actual_ticks']>0];gaps=[];overlaps=[]
  previous=None
  for row in intervals:
   if previous is not None:
    if row['before_tick']<previous['after_tick']:
     overlaps.append({'previous_id':previous['operation_id'],'id':row['operation_id'],'previous_after':previous['after_tick'],'current_before':row['before_tick']})
    elif row['before_tick']>previous['after_tick']:
     gaps.append({'previous_id':previous['operation_id'],'id':row['operation_id'],'previous_after':previous['after_tick'],'current_before':row['before_tick']})
   if previous is None or row['after_tick']>previous['after_tick']:previous=row
  if overlaps:issues.append({'issue':'OVERLAPPING_DISTINCT_NATIVE_PHASES','participant':arm,'session':session,'overlaps':overlaps})
  total=sum(x['actual_ticks']for x in ordered)
  first=min((x['before_tick']for x in intervals),default=None);last=max((x['after_tick']for x in intervals),default=None)
  summary.append({'participant':arm,'session':session,'unique_completed_phase_count':len(ordered),
   'actual_ticks_sum_unique_ids':total,'first_tick':first,'last_tick':last,
   'elapsed_tick_span':last-first if last is not None else None,'gaps':gaps,'overlaps':overlaps,
   'contiguous_recorded_interval':not gaps and not overlaps,
   'delta_from_DEV4_if_recorded_from_parent':last-PARENT_TICK if first==PARENT_TICK and last is not None else None})
 return {'method':'Unique actually NATIVE_COMPLETED operation IDs; Native_Q1/Q2 copied into result rows add no time.',
         'phases':records,'histories':summary,'unique_completed_phase_count':len(records),
         'actual_ticks_sum_unique_ids':sum(x['actual_ticks']for x in records)}

def main_recalculate(datasets,world_paths,parent_world,primary_paths,actor_paths,protocol_path,output,partial_paths=()):
 output=Path(output)
 if output.exists():raise FileExistsError('New absent output required; preserve prior recalculations')
 sources=[];issues=[];opportunities={};phase_intents={};phases={};states={};world_events={};world_aliases=0;numeric_primaries={};receipts={};post_tool_results={}
 known_not_admitted={};partial_records=[];intent_variants={};phase_arms={};phase_aliases=0;intent_aliases=0
 protocol=read(protocol_path,sources)if protocol_path else{}
 parent=read(parent_world,sources)if parent_world else None
 parent_proven=bool(parent and sources[-1]['sha256']==PARENT_WORLD_SHA and parent.get('native_tick')==PARENT_TICK and parent.get('S',{}).get('completedCycles')==4)
 starts=[];closures=[];resume_contexts=[];live_reattachments=[];segment_summaries=[]
 def add_post_tool(arm,value,source):
  if not isinstance(value,dict)or not isinstance(value.get('S'),dict)or not isinstance(value.get('result'),dict):return
  state=value['S'];session=state.get('sessionId');cycle=state.get('cycle')
  if not session or not integer(cycle):return
  key=(arm,session,cycle);result=value['result']
  if key in post_tool_results and canonical(post_tool_results[key]['result'])!=canonical(result):
   issues.append({'issue':'CONFLICTING_POST_TOOL_WORLD_RESULT','participant':arm,'session':session,'cycle':cycle})
  else:post_tool_results[key]={'result':result,'source':source,'executionStatus':value.get('executionStatus')}
 def add_op(arm,session,row,source):
  if arm not in ARMS:issues.append({'issue':'UNKNOWN_PARTICIPANT','participant':arm,'source':source});return
  cycle=row.get('cycle')
  if not integer(cycle)or cycle<=4:return
  clean={k:v for k,v in row.items()if k not in('kind','utc','event')};key=(arm,session,cycle)
  if key in opportunities and canonical(opportunities[key]['row'])!=canonical(clean):
   issues.append({'issue':'CONFLICTING_OPPORTUNITY_ALIAS','participant':arm,'session':session,'cycle':cycle})
  else:opportunities[key]={'row':clean,'source':source}
 for path in partial_paths:
  partial=read(path,sources)
  if partial.get('classification')!='TECHNICAL_VALIDATOR_ERROR_BEFORE_QUEUE' or partial.get('schema')!='DEE.RBX06.partial_known_not_admitted.FUNCTION16.R01':
   raise ValueError('Only explicit known pre-queue FUNCTION16 record accepted')
  part=partial.get('partial_opportunity')or{};identifier=part.get('function_id');identity=partial.get('identity')or{}
  if not(isinstance(identifier,str)and part.get('function_native_admitted')is False and part.get('cycle')==16 and partial.get('current_closed_native_tick')==971233):
   raise ValueError('Known not-admitted record identity/tick mismatch')
  declaration={'source':str(path),'id':identifier,'session':identity.get('session_id'),'life':identity.get('life'),
   'rejected_payload':part.get('host_intent_payload'),'closed_native_tick':partial['current_closed_native_tick'],
   'classification':'REJECTED_BEFORE_QUEUE','physical_ticks_for_rejected_function':0,
   'proof_reference':partial.get('provenance',{}),'completed_global_cycles':partial.get('complete_global_cycles',[])}
  if identifier in known_not_admitted and canonical(known_not_admitted[identifier])!=canonical(declaration):
   raise ValueError('Conflicting known not-admitted declaration')
  known_not_admitted[identifier]=declaration;partial_records.append(declaration)
  for row in partial.get('completed_rows',[]):add_op('LIVE_NATIVE',identity.get('session_id'),row,str(path))
 for arm,directory in datasets:
  directory=Path(directory);events=directory/'EVENTS.jsonl';result=directory/'RESULTADO.json';current_session=None
  if result.is_file():
   value=read(result,sources);a=source_arm(value,arm);identity=value.get('identity',{});session=identity.get('session');current_session=session
   segment_summaries.append({'participant':a,'session':session,'source':str(result),'source_tick':value.get('source_tick'),
    'final_tick':value.get('final_tick'),'reported_new_ticks':value.get('new_Native_ticks'),
    'continued_partial_original_opportunity':value.get('continued_partial_original_opportunity'),
    'scope':'Segment metadata only; never summed blindly with copied-prefix rows.'})
   for row in value.get('rows',[]):add_op(a,session,row,str(result))
   if value.get('owner_closed')is True:closures.append({'participant':a,'session':session,'source':str(result),'final_tick':value.get('final_tick')})
  if events.is_file():
   for row in read(events,sources):
    kind=row.get('kind',row.get('event'))
    if kind=='PROTOCOL_STARTED':
     identity=row.get('identity',{});current_session=identity.get('session');starts.append({'participant':arm,'session':current_session,'source_tick':row.get('source_tick'),'source':str(events)})
    if kind=='RESTORED':resume_contexts.append({'participant':arm,'identity':row.get('identity'),'result':row.get('result'),'source':str(events)})
    if kind=='MCP_COMPLETED'and row.get('label')=='tool':add_post_tool(arm,row.get('result'),str(events))
    if kind=='LIVE_PENDING_ATTACHED':
     state=(row.get('status')or{}).get('S',{});session=state.get('sessionId')
     if current_session is not None and session!=current_session:issues.append({'issue':'LIVE_ATTACH_SESSION_MISMATCH','source':str(events)})
     current_session=session
     live_reattachments.append({'participant':arm,'session':session,'source':str(events),'status':row.get('status'),
      'original_function_operation_id':row.get('original_function_operation_id'),'no_world_restore':row.get('no_world_restore'),
      'no_Q1_Q2_or_movement_repeated':row.get('no_Q1_Q2_or_movement_repeated'),
      'scope':'Attach to already-live half-operation, not a restored full World checkpoint.'})
    if kind in('NATIVE_INTENT','BACKEND_INTENT'):
     context=row.get('context',{});identifier=context.get('operation_id')
     if identifier:
      clean={k:v for k,v in row.items()if k!='utc'}
      variants=intent_variants.setdefault(identifier,[])
      if any(canonical(x['row'])==canonical(clean)for x in variants):intent_aliases+=1
      else:variants.append({'source':str(events),'row':clean})
      known=known_not_admitted.get(identifier)
      if known and row.get('payload')==known['rejected_payload']:
       if context.get('session_id')!=known['session']or row.get('phase')!='function':issues.append({'issue':'REJECTED_INTENT_IDENTITY_MISMATCH','id':identifier})
       continue
      if known and not transport_shape_equivalent(known['rejected_payload'],row.get('payload')):
       issues.append({'issue':'TRANSPORT_REPAIR_CHANGED_EXPERIENCE','id':identifier});continue
      if identifier in phase_intents and canonical({k:v for k,v in phase_intents[identifier].items()if k!='utc'})!=canonical(clean):
       issues.append({'issue':'CONFLICTING_NATIVE_INTENT','id':identifier})
      else:phase_intents[identifier]=row
    if kind in('NATIVE_COMPLETED','POLICY_COMPLETED','BACKEND_COMPLETED'):
     identifier=row.get('operation_id')
     if identifier:
      content={k:v for k,v in row.items()if k not in('utc',)}
      if identifier in phases:
       if canonical(phases[identifier])!=canonical(content):issues.append({'issue':'CONFLICTING_PHASE_COMPLETION','id':identifier})
       else:phase_aliases+=1
      else:phases[identifier]=content;phase_arms[identifier]=arm
    if kind=='OPPORTUNITY_COMPLETED':add_op(arm,current_session,row,str(events))
    if kind=='OWNER_CLOSED':closures.append({'participant':arm,'source':str(events),'life':row.get('life'),'expected_tick':row.get('expected_tick')})
 for path in world_paths:
  value=read(path,sources)
  if not isinstance(value,dict)or not isinstance(value.get('S'),dict)or not isinstance(value.get('events'),list):raise ValueError('Full World checkpoint required')
  arm=value['S'].get('participant')or next((r.get('participant')for r in reversed(value['events'])if r.get('participant')in ARMS),'LIVE_NATIVE')
  session=value['S'].get('sessionId');cursor=value.get('boundary',{}).get('completed_opportunities',value['S'].get('completedCycles'))
  states[(arm,session,cursor)]={'S':value['S'],'native_tick':value.get('native_tick'),'boundary':value.get('boundary'),'source':str(path)}
  for command_id,command in(value.get('controller',{}).get('r06_commands',{})or{}).items():
   if command.get('kind')=='tool'and command.get('status')=='COMPLETED':add_post_tool(arm,command.get('result'),str(path)+'#/controller/r06_commands/'+command_id)
  for event in value['events']:
   h=hashlib.sha256(canonical(event).encode()).hexdigest()
   if h in world_events:world_aliases+=1
   else:world_events[h]=event
 for path in files(primary_paths):
  p=read(path,sources)
  if not isinstance(p,dict)or not isinstance(p.get('requests_normalized'),list):continue
  operation=p.get('context',{}).get('operation_id');life=p.get('life_id')
  if not operation:issues.append({'issue':'FUNCTION_PRIMARY_WITHOUT_OPERATION_ID','source':str(path)});continue
  if operation in numeric_primaries and numeric_primaries[operation]!=p:issues.append({'issue':'CONFLICTING_FUNCTION_PRIMARY','id':operation})
  numeric_primaries[operation]=p;receipt_rows(p,life,receipts,issues)
 for path in actor_paths:
  life=Path(path).parent.parent.name
  for row in read(path,sources):
   if row.get('kind')=='PHASE_COMPLETED':receipt_rows(row,life,receipts,issues)
 # Correlate exact Native operation and observation IDs with World events. No
 # cursor/phase is guessed from seq arithmetic if Q1 terminated in NULL.
 by_action={};by_seq={};phase_by_cycle={}
 for identifier,intent in phase_intents.items():
  cycle=intent.get('cycle');context=intent.get('context',{});session=context.get('session_id');phase=intent.get('phase')
  by_action[identifier]=(session,cycle);by_seq[(session,context.get('sequence'))]=(session,cycle)
  phase_by_cycle.setdefault((session,cycle),{})[phase]={'intent':intent,'completed':phases.get(identifier),'operation_id':identifier}
 events_by_cycle={}
 for event in world_events.values():
  session=event.get('sessionId');data=event.get('data',{});action=data.get('action',{})
  identifier=action.get('actionId',data.get('actionId'))
  key=by_action.get(identifier)or by_seq.get((session,event.get('seq')))
  if key and integer(key[1])and key[1]>4:events_by_cycle.setdefault(key,[]).append(event)
 for identifier,known in known_not_admitted.items():
  rejected=[v['row']for v in intent_variants.get(identifier,[])if v['row'].get('payload')==known['rejected_payload']]
  selected=phase_intents.get(identifier)
  if selected and rejected and any(x.get('context')!=selected.get('context')or x.get('cycle')!=selected.get('cycle')or x.get('phase')!=selected.get('phase')for x in rejected):
   issues.append({'issue':'TRANSPORT_REPAIR_CONTEXT_CHANGED','id':identifier})
 tick_accounting=completed_phase_accounting(phases,phase_intents,phase_arms,issues)
 rows=[]
 for (arm,session,cycle),stored in sorted(opportunities.items(),key=lambda t:(t[0][0],str(t[0][1]),t[0][2])):
  row=stored['row'];s=row.get('state_after',{});tool=row.get('tool_result');numeric=classify_numeric(tool)
  native=row.get('Native_Q1',{});route=row.get('Native_Q2')or{};parts=phase_by_cycle.get((session,cycle),{});events=events_by_cycle.get((session,cycle),[])
  function=parts.get('function',{});primary=numeric_primaries.get(function.get('operation_id'));request=primary.get('visible_tool',{})if primary else{}
  if numeric:numeric=classify_numeric(tool,request)
  feedback=parts.get('feedback',{}).get('intent',{}).get('payload',{})
  locks=[e['data']for e in events if e.get('kind')=='EVALUATOR_LOCK_CHECK']
  actual=row.get('world_result',{})
  post_tool=post_tool_results.get((arm,session,cycle))
  # Tool application can mutate outcome/failure AFTER the route result was
  # returned. Prefer the actual post-tool RPC or, otherwise, recorded feedback.
  authoritative=dict(actual)
  if post_tool:authoritative.update(post_tool['result'])
  elif isinstance(tool,dict):
   # This field may have changed in applyTool. An old route flag is not a
   # post-tool observation; the feedback outcome/failure remains available.
   authoritative.pop('invalidAction',None)
  for key in('outcome','collision','resourceCollected','resourceDelivered','permissionSpent','durationMs','materialConsequence'):
   if key in feedback:authoritative[key]=feedback[key]
  authority='RECORDED_POST_TOOL_WORLD_RESULT'if post_tool else'ACTUAL_FEEDBACK_INTENT'if feedback else'OPPORTUNITY_ROW_ONLY'
  applied=[e['data']for e in events if e.get('kind')=='FUNCTION_APPLIED']
  assisted=[e['data']for e in events if e.get('kind')=='ASSISTED_ORDER']
  before_s=states.get((arm,session,cycle-1),{}).get('S')
  q1=row.get('Native_Q1',{});q2=row.get('Native_Q2')
  primary_inputs=primary.get('Native_inputs')if primary else None
  own_phases=[p for p in tick_accounting['phases']if p['participant']==arm and p['session']==session and p['cycle']==cycle]
  rows.append({'participant':arm,'session':session,'global_cycle':cycle,'new_opportunity':cycle-4,'completed':True,
   'source':stored['source'],'processor_kind':'DEE_NATIVE'if arm=='LIVE_NATIVE'else'EXTERNAL_REFERENCE',
   'Native_Q_fieldnames_are_transport_compatibility_not_attribution':arm!='LIVE_NATIVE','native_Q1_action':q1.get('action'),'native_Q1_NULL':q1.get('null'),
   'native_Q2_action':q2.get('action')if isinstance(q2,dict)else None,'native_Q2_NULL':q2.get('null')if isinstance(q2,dict)else None,
   'executed_route':row.get('executed_route'),'selected_route_record':row.get('Native_route'),
   'host_order_prepared':row.get('host_order_prepared'),'native_route_overridden':bool(q2 and row.get('executed_route')not in(None,q2.get('action'))),
   'function_kind':tool.get('kind')if isinstance(tool,dict)else None,'function_result':tool,'numeric':numeric,
   'primary_supplied':primary is not None,'primary_all_inputs_applied':primary.get('input_admission_complete')if primary else None,
   'primary_input_summary':primary_inputs,'lesson_partial_admission':isinstance(tool,dict)and tool.get('kind')=='LESSON'and(tool.get('reason')=='NATIVE_PARTIAL_ADMISSION'or tool.get('capability_execution_admitted')is False),
   'actual_feedback':feedback,'actual_material_failure':feedback.get('materialConsequence',authoritative.get('materialConsequence')),
   'world_result_authoritative_after_tool':authoritative,'world_result_authority':authority,
   'post_tool_world_record':post_tool,'function_applied_world_events':applied,
   'function_transport_request_completed':function.get('completed')is not None,
   'function_transport_request_accepted':(function.get('completed',{}).get('result')or{}).get('accepted')if function.get('completed')else None,
   'function_capability_execution_admitted':tool.get('capability_execution_admitted')if isinstance(tool,dict)else None,
   'function_admission_scope':'A completed/accepted transport request does not assert that all underlying material inputs were admitted; inspect primary_input_summary.',
   'assisted_order_events':assisted,'assisted_order_event_count':len(assisted),
   'world_result_before_tool_update':actual,'codes_accepted':sum(l.get('accepted')is True for l in locks),'codes_rejected':sum(l.get('accepted')is False for l in locks),
   'lock_checks':locks,'resource_collected':authoritative.get('resourceCollected')is True,'resource_delivered':authoritative.get('resourceDelivered')is True,
   'state_after_literal':s,'S_before_literal_if_supplied':before_s,'Native_tick_after':s.get('nativeTick'),
   'operation_wall_seconds':{k:v['completed'].get('wall_seconds')for k,v in parts.items()if v.get('completed')},
   'Native_phase_ticks_unique':sum(p['actual_ticks']for p in own_phases),
   'Native_phase_operation_ids':[p['operation_id']for p in own_phases],
   'Native_phase_intervals':own_phases,
   'original_Q1_Q2_reused_after_known_nonadmission':row.get('Q1_Q2_and_motion_from_interrupted_prefix')is True,
   'clock_scope':'Actual records only; no full S reconstructed between checkpoints.'})
 totals={}
 for arm in ARMS:
  own=[r for r in rows if r['participant']==arm];numerics=[r['numeric']for r in own if r['numeric']]
  collected=sum(r['resource_collected']for r in own);delivered=sum(r['resource_delivered']for r in own)
  # First delivery consumes the actual resource carried into this continuation.
  carry_delivery=min(1,delivered)if parent_proven else None
  final=max((r for r in own),key=lambda r:r['global_cycle'])if own else None
  walls=[v for r in own for v in r['operation_wall_seconds'].values()]
  totals[arm]={'opportunities_completed':len(own),'planned_new_opportunities':24,'unoffered_not_scored':24-len(own),
   'global_cycles_observed':[r['global_cycle']for r in own],'query_actions':sum(r['native_Q1_action']=='ASK_STATION'for r in own),
   'skip_actions':sum(r['native_Q1_action']=='SKIP_STATION'for r in own),'Q1_NULL':sum(r['native_Q1_NULL']is True for r in own),
   'Q2_NULL':sum(r['native_Q2_NULL']is True for r in own),'assisted_route_overrides':sum(r['native_route_overridden']for r in own),
   'prepared_assisted_contract_opportunities':sum(r['host_order_prepared']is True for r in own),
   'assisted_order_world_events':sum(r['assisted_order_event_count']for r in own),
   'assistance_counter_scope':'ASSISTED_ORDER is emitted even when selected==executed; effective override count uses actual action inequality only.',
   'function_opportunities':sum(r['function_kind']is not None for r in own),'lesson_opportunities':sum(r['function_kind']=='LESSON'for r in own),'numeric_opportunities':len(numerics),
   'numeric_formed':sum(n['formed']for n in numerics),'numeric_valid_zero':sum(n['zero_valid']for n in numerics),
   'numeric_NULL_or_absent':sum(n['absent_or_NULL']for n in numerics),'arithmetic_correct_for_actual_opcode':sum(n['correct_for_actual_opcode']is True for n in numerics),
   'arithmetic_incorrect_for_actual_opcode':sum(n['correct_for_actual_opcode']is False for n in numerics),
   'numeric_opportunity_success_fraction':sum(n['correct_for_actual_opcode']is True for n in numerics)/len(numerics)if numerics else None,
   'arithmetic_evaluable_count':sum(n['correct_for_actual_opcode']is not None for n in numerics),
   'arithmetic_accuracy_among_evaluable':sum(n['correct_for_actual_opcode']is True for n in numerics)/sum(n['correct_for_actual_opcode']is not None for n in numerics)if any(n['correct_for_actual_opcode']is not None for n in numerics)else None,
   'new_resources_collected':collected,'resources_delivered_total_in_this_continuation':delivered,'delivered_inherited_resource':carry_delivery,
   'delivered_new_resources':max(0,delivered-carry_delivery)if carry_delivery is not None else None,
   'code_checks_accepted':sum(r['codes_accepted']for r in own),'code_checks_rejected':sum(r['codes_rejected']for r in own),
   'partial_lesson_admissions':sum(r['lesson_partial_admission']for r in own),'operation_latency_seconds':stats(walls),
   'function_transport_requests_completed':sum(r['function_transport_request_completed']for r in own),
   'function_transport_requests_accepted_explicitly':sum(r['function_transport_request_accepted']is True for r in own),
   'function_capability_execution_not_admitted':sum(r['function_capability_execution_admitted']is False for r in own),
   'final_S':final['state_after_literal']if final else None,
   'new_Native_tick_delta_from_DEV4':final['Native_tick_after']-PARENT_TICK if final and integer(final['Native_tick_after'])and arm=='LIVE_NATIVE'else None,
   'actual_Native_ticks_unique_completed_phases':sum(p['actual_ticks']for p in tick_accounting['phases']if p['participant']==arm),
   'partial_completed_phases_not_counted_as_opportunities':[p for p in tick_accounting['phases']if p['participant']==arm and not any(r['session']==p['session']and r['global_cycle']==p['cycle']for r in own)],
   'time_per_new_resource_native_phase_wall_seconds':sum(walls)/collected if collected and walls else None,
   'cost_per_success_scope':'Undefined/null when no success; phase latency is not total host CPU/energy or elapsed campaign walltime.'}
 native_reopens=[]
 for restore in resume_contexts:
  if restore.get('participant')!='LIVE_NATIVE':continue
  result=restore.get('result')or{};identity=restore.get('identity')or{};state=result.get('S',{})
  cursor=state.get('completedCycles');session=identity.get('session')
  if integer(cursor)and cursor>4:
   later=[r for r in rows if r['participant']=='LIVE_NATIVE'and r['session']==session and r['global_cycle']>cursor and r['numeric']and r['numeric']['formed']]
   native_reopens.append({'session':session,'restored_after_global_cycle':cursor,'later_formed_numeric_cycles':[r['global_cycle']for r in later],
      'scope':'Recorded restore and later same-session numeric use; exact full-pair identity/hash witness must also be reviewed.'})
 reconciliation=[]
 for identifier,known in known_not_admitted.items():
  variants=intent_variants.get(identifier,[]);selected=phase_intents.get(identifier);completed=phases.get(identifier)
  rejected=[v['row']for v in variants if v['row'].get('payload')==known['rejected_payload']]
  context_preserved=bool(selected and rejected and all(x.get('context')==selected.get('context')and x.get('cycle')==selected.get('cycle')and x.get('phase')==selected.get('phase')for x in rejected))
  reconciliation.append({**known,'host_intent_variants':variants,'repaired_admitted_intent_present':selected is not None,
   'Native_completion_present':completed is not None,'completed_native_ticks':(completed.get('result')or{}).get('nativeTicks')if completed else None,
   'original_context_preserved':context_preserved,
   'transport_only_equivalence_checked':bool(selected and context_preserved and transport_shape_equivalent(known['rejected_payload'],selected.get('payload'))),
   'native_admission_scope':'Known rejected host packet contributes0Native ticks; valid resumed packet counted once only when actually completed.'})
 unmatched=[{'id':identifier,'phase':intent.get('phase'),'cycle':intent.get('cycle'),'context':intent.get('context'),
             'classification':'HOST_INTENT_WITHOUT_COMPLETION_ADMISSION_UNKNOWN'}for identifier,intent in phase_intents.items()if identifier not in phases]
 return_data={'schema':'DEE.RBX01.INTEGRAL.V2.passive_recalculation.R03','inspected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'Native_executed':False,'model_MCP_HTTP_SQLite_calls':0,'sources':sources,'issues':issues,
  'parent_DEV4_exact_world_verified':parent_proven,'parent_context':{'tick':PARENT_TICK,'completed_opportunities':4,'resource_carried_in':1 if parent_proven else None,'A':4 if parent_proven else None,'B':5 if parent_proven else None},
  'totals':totals,'world_event_aliases_deduplicated':world_aliases,'new_opportunity_rows':rows,
  'Native_receipts_coverage':{'unique':len(receipts),'statuses':dict(Counter(x['status']for x in receipts.values())),
  'scope':'Only explicitly supplied function primaries/actor journals; absent source is NOT zero material dose.'},
  'starts':starts,'closures':closures,'restores':resume_contexts,'native_reopens_with_later_use':native_reopens,
  'live_partial_reattachments':live_reattachments,'known_not_admitted_reconciliations':reconciliation,
  'reported_segment_summaries_not_blindly_added':segment_summaries,'partial_record_inputs':partial_records,
  'Native_tick_accounting':tick_accounting,'phase_completion_aliases_deduplicated':phase_aliases,
  'phase_intent_aliases_deduplicated':intent_aliases,'uncompleted_host_intents_admission_unknown':unmatched,
  'limits':['No global PASS or cognitive approval is inferred. E/F outputs below require review of evidence scope.',
  'Native_Q1/Native_Q2 are legacy transport column names in reference RESULTADO; BACKEND phases and0Native ticks identify external policy/model processing, never DEE execution.',
  'An interrupted opportunity is complete only after its recorded function/feedback and World completion. Copied Q1/Q2 values in resumed result rows are not additional execution.',
  'Known FUNCTION16 packet rejection is kept with both raw host intents. Shape-only repair is accepted only with explicit not-admitted evidence; content changes remain discrepancies.',
  'Reported segment source/final tick ranges overlap at a partial opportunity and are not independent trials or new lives.',
  'One continued history per participant, not independent samples per tick/opportunity or a shared-life fusion.',
  'Host-prepared locomotion and Native Q2 output are kept distinct. Its consequence cannot isolate credit to the overridden motor.',
  'Native Q1 sensors are a prepared scalar; bit comprehension is not inferred.',
  'Correctness of actual opcode is separate from environmental utility and new association acquisition.',
  'No arithmetic opportunities means accuracy null, never0%. Missing input is distinct from numeric zero.',
  'Old resource1/A4/B5 belong to the verified parent; first inherited-resource delivery is separate from new collection/delivery.',
  'RESULTADO.world_result can precede function mutation; the actual feedback Native-intent payload takes precedence for failure.',
  'ASSISTED_ORDER event count and host-prepared contract count are separate from effective changes to a selected route.',
  'Wall latency includes host checks/transport and any overlapping source-import or resource contention; no efficiency or CPU ranking is inferred.',
  'Reopening is not proven by a save alone. Same-session later use after a recorded restore must be inspected.',
  'E4 needs a relevant control for an acquired-change claim. No controlled-learning verdict is invented from parameter or hash differences.',
  'No unexecuted counterfactual, route solution, missing S, full microcause or energy value is calculated.']}
 matrix=family_matrix(return_data,protocol);criteria=criteria_matrix(return_data,protocol)
 output.mkdir(parents=True)
 for name,value in(('HECHOS_RECALCULADOS.json',return_data),('CRITERIOS_E1_E6.json',criteria),('MANIFIESTO_FUENTES.json',sources)):
  (output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 csv_file(output/'OPORTUNIDADES.csv',rows);csv_file(output/'MATRIZ_F01_F16.csv',matrix)
 return return_data

def family_matrix(report,protocol):
 n=report['totals']['LIVE_NATIVE'];has=n['opportunities_completed']>0;history=report['parent_DEV4_exact_world_verified']
 definitions=[
 ('F01','Percepción local','Sensor local y productos_v1 preparado; no descomposición de bits demostrada','DEE_CON_ASISTENCIA',has,'Observar campos/intentos y valor material en actor journal'),
 ('F02','Memoria contextual/asociativa','luma-/nara+ heredados en DEV4; signo ausente en consulta posterior','DEE_CON_ASISTENCIA',n['numeric_opportunities']>0,'Primario recall.common36 y uso posterior; A/B externo no es memoria Native'),
 ('F03','Revisión/plasticidad','MEMPAIR histórico separado; enseñanza nueva no equivale a adquisición útil','DEE_CON_ASISTENCIA',n['lesson_opportunities']>0,'Contraste mínimo de revisión nueva pendiente si se alega E4'),
 ('F04','Comparación/aritmética','FI128 preparado; comparación±/0 histórica no reensayada','DEE_CON_ASISTENCIA',n['numeric_opportunities']>0,'Exactitud para opcode real; no algoritmo aritmético adquirido'),
 ('F05','Composición A hacia B','Orden preparado; entero A real alimenta B; dependencia de enlace C02 reutilizable','DEE_CON_ASISTENCIA',n['numeric_opportunities']>0,'Versión/origenA y B y gate real, no objetivo previsto'),
 ('F06','Consulta/omisión/reutilización','Q1 real; reutilizaciónA/B por soporte técnico declarado','DEE_CON_ASISTENCIA',has,'ASK/SKIP/NULL por salida auténtica y recursos consumidos'),
 ('F07','Herramienta/momento/secuencia','Orden asistido5..22; Q2 efectivo23..28 por contrato','DEE_CON_ASISTENCIA',has,'Separar selección Native y movimiento preparado porID'),
 ('F08','Destino/interacción/entrega','Body mueve/recoge/entrega por contacto; asistencia explícita','DEE_CON_ASISTENCIA',has,'E3 separa recogida heredada, nueva recogida y entrega'),
 ('F09','Consecuencias/costes','Retorno genérico real; False no es recompensa positiva acreditada','DEE_CON_ASISTENCIA',has,'Crédito de motor no aislado en acciones reemplazadas por anfitrión'),
 ('F10','Persistencia conjunta','DEV reapertura2 con uso real; nueva frontera10 requiere uso posterior','DEE_CON_ASISTENCIA',any(r['later_formed_numeric_cycles']for r in report['native_reopens_with_later_use']),'Mismo Native+World y sesión, sin reenseñanza de conveniencia'),
 ('F11','Cambio/transferencia','Cambio en17 y tuplas reservadas sólo si fueron realmente presentadas','DEE_CON_ASISTENCIA',any(r['global_cycle']>=17 for r in report['new_opportunity_rows']if r['participant']=='LIVE_NATIVE'),'Calendario no equivale a exposición; registrar roundOperands de llave'),
 ('F12','Acceso/recuperación/resiliencia','NO_RESULT técnico; no autorrecuperación nueva demostrada','ANFITRIÓN',n['partial_lesson_admissions']>0,'Rechazo local/lecturaNULL no prueba borrado global'),
 ('F13','Señales/español funcional','luma/nara firmados; no conversación general','DEE_CON_ASISTENCIA',n['numeric_opportunities']>0,'Dominio heredado y lector fijo'),
 ('F14','Comunicación independiente','No canal de dos interlocutores independientes en esta vida','DEE',False,'No añadir anatomía para simular cumplimiento'),
 ('F15','Carga/aislamiento/estabilidad','Owners/procesos aislados y ledger100k preparados','ANFITRIÓN',False,'Necesita resultados reales1->2->3 y recursos; fuente ausente no es cero carga'),
 ('F16','Patrones inesperados','Sin predicción funcional independiente fijada en el recálculo','DEE',False,'No descubrir retrospectivamente y llamarlo reserva')]
 rows=[]
 for identifier,capability,base,attribution,evaluated,limit in definitions:
  status='EVALUADO'if evaluated else'NO_DISPONIBLE_EN_ESTA_VIDA'if identifier=='F14'else'NO_EVALUADO_CON_MOTIVO'
  rows.append({'ID':identifier,'capacidad':capability,'base_y_origen':base,'atribución':attribution,'estado_evaluación':status,
   'resultado':'PARCIAL'if evaluated else'NO_APLICA','procedencia':'HEREDADO_USADO'if evaluated and identifier in('F02','F04','F05','F13')else'HISTORICO_NO_REENSAYADO',
   'límite_y_comprobación_pendiente':limit,'evidencia':'HECHOS_RECALCULADOS.json/new_opportunity_rows','veredicto_automático':False})
 return rows

def criteria_matrix(report,protocol):
 n=report['totals']['LIVE_NATIVE'];history=report['parent_DEV4_exact_world_verified'];has=n['opportunities_completed']>0
 return {'schema':'DEE.INTEGRAL.V2.criteria_evidence.R01','automatic_approval':False,
 'E1':{'recorded_historical_demonstration':history,'new_calculations':n['numeric_opportunities'],'new_resources':n['new_resources_collected'],'scope':'C02DEV Native chain→resource accepted; new link/control must be checked where changed.'},
 'E2':{'historical_memory_and_reopen':history,'new_memory_uses':n['numeric_opportunities'],'recorded_restores_by_participant':dict(Counter(x.get('participant')for x in report['restores'])),'native_reopen_with_later_numeric_use':report['native_reopens_with_later_use'],
       'scope':'Initialrestore is import/technical continuation, not a new demonstrated same-pair reopen. Need later actual use after boundary10.'},
 'E3':{'delivery_recorded':n['resources_delivered_total_in_this_continuation']>0,'delivered_inherited_resource':n['delivered_inherited_resource'],
       'new_resources':n['new_resources_collected'],'delivered_new_resources':n['delivered_new_resources'],'assistance':'Prepared route order is allowed; Native numeric content is separately evidenced.'},
 'E4':{'new_learning_isolated':False,'scope':'No relevant controlled-acquisition result supplied to this generic recalc; do not infer from success, sign change or metadata.'},
 'E5':{'completed_by_participant':{k:v['opportunities_completed']for k,v in report['totals'].items()},'three_participants_observed':all(report['totals'][a]['opportunities_completed']>0 for a in ARMS),
       'scope':'Compare actual configurations; equality of fieldnames is not equal prior semantic preparation.'},
 'E6':{'video_evaluated_by_this_script':False,'module_installation_evaluated':False,'load_evaluated':False,'scope':'These require their own frozen verification primaries; do not replace by code availability.'}}

def cli():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dataset',action='append',required=True,help='PARTICIPANT=folder with EVENTS.jsonl/RESULTADO.json; repeated for closed blocks')
 p.add_argument('--world',nargs='*',type=Path,default=[]);p.add_argument('--parent-world',type=Path);p.add_argument('--native-functions',nargs='*',type=Path,default=[])
 p.add_argument('--actor-events',nargs='*',type=Path,default=[]);p.add_argument('--protocol',type=Path);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--partial-result',action='append',type=Path,default=[],help='Explicit immutable known-before-queue partial record; repeated if needed')
 a=p.parse_args();datasets=[]
 for entry in a.dataset:
  arm,path=entry.split('=',1)
  if arm not in ARMS:raise ValueError('Closed participant names only')
  datasets.append((arm,Path(path)))
 r=main_recalculate(datasets,a.world,a.parent_world,a.native_functions,a.actor_events,a.protocol,a.output,a.partial_result)
 print(json.dumps({'output':str(a.output),'completed':{k:v['opportunities_completed']for k,v in r['totals'].items()},'issues':r['issues'],'Native_executed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':cli()
