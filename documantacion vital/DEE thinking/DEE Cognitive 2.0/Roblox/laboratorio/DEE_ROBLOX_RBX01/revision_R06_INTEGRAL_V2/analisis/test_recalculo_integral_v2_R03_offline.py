"""Synthetic passive fixtures only; no actual R06 run, world, model or SQL."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('passive_r06_fixture',HERE/'RECALCULO_INTEGRAL_V2_R03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def case(self,tool=None,failure=False):
  tmp=tempfile.TemporaryDirectory(dir=HERE);root=Path(tmp.name);d=root/'closed';d.mkdir();session='SYNTHETIC_ONLY'
  q1={'action':'ASK_STATION','null':False,'nativeTick':953700};q2={'action':'EXIT_1','null':False,'nativeTick':954029}
  state={'nativeTick':955215,'completedCycles':5,'inventoryResource':False,'delivered':1,'resourceCount':1}
  row={'cycle':5,'new_opportunity':1,'Native_Q1':q1,'Native_Q2':q2,'tool_result':tool,
   'actual_numeric':tool.get('numeric_result')if tool else None,'executed_route':'EXIT_0','Native_route':'EXIT_1',
   'host_order_prepared':True,'world_result':{'resourceDelivered':True,'resourceCollected':False,'materialConsequence':False},'state_after':state}
  result={'identity':{'participant':'LIVE_NATIVE','session':session},'rows':[row],'owner_closed':True,'final_tick':955215}
  (d/'RESULTADO.json').write_text(json.dumps(result),encoding='utf8')
  events=[{'kind':'PROTOCOL_STARTED','identity':{'session':session},'source_tick':953651},
   {'kind':'NATIVE_INTENT','cycle':5,'phase':'feedback','payload':{'materialConsequence':failure},'context':{'operation_id':'f','session_id':session,'sequence':10}},
   {'kind':'NATIVE_COMPLETED','cycle':5,'phase':'feedback','operation_id':'f','result':{'nativeTick':955215,'nativeTicks':1564},'wall_seconds':2},
   {'kind':'OPPORTUNITY_COMPLETED',**row}]
  (d/'EVENTS.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in events),encoding='utf8')
  parent=root/'parent.json';parent.write_text(json.dumps({'native_tick':953651,'S':{'completedCycles':4}}),encoding='utf8')
  old=m.PARENT_WORLD_SHA;m.PARENT_WORLD_SHA=hashlib.sha256(parent.read_bytes()).hexdigest()
  try:r=m.main_recalculate([('LIVE_NATIVE',d)],[],parent,[],[],None,root/'out')
  finally:m.PARENT_WORLD_SHA=old
  return tmp,r,root/'out'
 def test_aliases_count_once_and_inherited_delivery_separate(self):
  t,r,o=self.case()
  try:
   s=r['totals']['LIVE_NATIVE'];self.assertEqual(s['opportunities_completed'],1)
   self.assertEqual(s['delivered_inherited_resource'],1);self.assertEqual(s['delivered_new_resources'],0)
   self.assertEqual(s['new_resources_collected'],0);self.assertEqual(s['assisted_route_overrides'],1)
   self.assertIsNone(s['arithmetic_accuracy_among_evaluable']);self.assertEqual(r['issues'],[])
   criteria=json.loads((o/'CRITERIOS_E1_E6.json').read_text('utf8'));self.assertFalse(criteria['automatic_approval']);self.assertFalse(criteria['E4']['new_learning_isolated'])
  finally:t.cleanup()
 def test_zero_is_real_numeric(self):
  t,r,_=self.case({'kind':'CALCULATE','slot':'A','form':'luma','inputs':[2,2],'memory_value':-1,'operation':'diferencia','numeric_result':0,'formed':True})
  try:
   s=r['totals']['LIVE_NATIVE'];self.assertEqual(s['numeric_valid_zero'],1);self.assertEqual(s['numeric_NULL_or_absent'],0)
   self.assertEqual(s['arithmetic_accuracy_among_evaluable'],1)
  finally:t.cleanup()
 def test_no_emission_not_math_error_and_feedback_is_authoritative(self):
  t,r,_=self.case({'kind':'CALCULATE','slot':'A','form':'luma','inputs':[2,2],'memory_value':None,'operation':None,'numeric_result':None,'formed':False},True)
  try:
   s=r['totals']['LIVE_NATIVE'];self.assertEqual(s['numeric_NULL_or_absent'],1);self.assertEqual(s['arithmetic_evaluable_count'],0)
   self.assertIsNone(s['arithmetic_accuracy_among_evaluable']);self.assertEqual(s['numeric_opportunity_success_fraction'],0)
   self.assertTrue(r['new_opportunity_rows'][0]['actual_material_failure'])
   self.assertFalse(r['new_opportunity_rows'][0]['world_result_before_tool_update']['materialConsequence'])
  finally:t.cleanup()
 def test_every_family_has_explicit_status_and_no_automatic_pass(self):
  t,r,o=self.case()
  try:
   import csv
   with (o/'MATRIZ_F01_F16.csv').open(encoding='utf-8-sig')as f:rows=list(csv.DictReader(f))
   self.assertEqual([x['ID']for x in rows],['F'+str(i).zfill(2)for i in range(1,17)])
   self.assertEqual(next(x for x in rows if x['ID']=='F14')['estado_evaluación'],'NO_DISPONIBLE_EN_ESTA_VIDA')
  finally:t.cleanup()
 def test_other_participants_restores_do_not_prove_native_reopening(self):
  t,r,o=self.case()
  try:
   r['restores']=[{'participant':'PROGRAMMED'},{'participant':'CONVENTIONAL_AI'}]
   rows=m.family_matrix(r,{})
   self.assertEqual(next(x for x in rows if x['ID']=='F10')['estado_evaluación'],'NO_EVALUADO_CON_MOTIVO')
   self.assertEqual(r['native_reopens_with_later_use'],[])
  finally:t.cleanup()
 def test_backend_event_ABI_preserves_feedback_and_latency_without_native_attribution(self):
  t,r,o=self.case()
  try:
   root=o.parent;d=root/'closed';data=json.loads((d/'RESULTADO.json').read_text('utf8'));data['identity']['participant']='PROGRAMMED'
   (d/'RESULTADO.json').write_text(json.dumps(data),encoding='utf8')
   lines=[json.loads(x)for x in(d/'EVENTS.jsonl').read_text('utf8').splitlines()]
   for row in lines:
    if row['kind']=='NATIVE_INTENT':row['kind']='BACKEND_INTENT'
    elif row['kind']=='NATIVE_COMPLETED':row['kind']='BACKEND_COMPLETED'
   (d/'EVENTS.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in lines),encoding='utf8')
   report=m.main_recalculate([('PROGRAMMED',d)],[],None,[],[],None,root/'out_ref')
   total=report['totals']['PROGRAMMED'];self.assertEqual(total['operation_latency_seconds']['n'],1)
   self.assertFalse(report['new_opportunity_rows'][0]['actual_material_failure'])
   self.assertTrue(report['new_opportunity_rows'][0]['Native_Q_fieldnames_are_transport_compatibility_not_attribution'])
   self.assertIsNone(total['new_Native_tick_delta_from_DEV4'])
  finally:t.cleanup()
 def test_receipts_are_deduplicated_by_life_and_id(self):
  r={};issues=[];x={'id':1,'channel':'c','payload':0,'requested_tick':100,'receipt':{'status':'applied'}}
  m.receipt_rows([x,x],'A',r,issues);m.receipt_rows(x,'B',r,issues)
  self.assertEqual(len(r),2);self.assertEqual(issues,[])
 def test_recovered_preparer_exact_hash(self):
  p=HERE/'preservado/preparar_R01_compilado.py'
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'121f812984feb44c316ad76cc2b7cf0fc03920be2bc870c37632c7d18ba7ab14')
class PartialContinuation(unittest.TestCase):
 def case(self,repaired=True,changed_experience=False,duplicates=True):
  tmp=tempfile.TemporaryDirectory(dir=HERE);root=Path(tmp.name);old=root/'interrupted';old.mkdir();new=root/'continued';new.mkdir()
  session='SYNTHETIC_CONTINUATION';op='R06_'+session+'_16_';bad={'tool':{'kind':'LESSON','items':{'1':{'form':'luma','observedSign':-1},'2':{'form':'nara','observedSign':1}}}}
  good={'tool':{'kind':'LESSON','items':[{'form':'luma','observedSign':-1},{'form':'nara','observedSign':1}]}}
  if changed_experience:good['tool']['items'][0]['observedSign']=1
  def intent(phase,payload=None):
   return {'kind':'NATIVE_INTENT','cycle':16,'phase':phase,'payload':payload or{},'context':{'session_id':session,'operation_id':op+phase.upper(),'sequence':32,'observation_id':'SYNTHETIC_OBS','mode':'LIVE_NATIVE'}}
  def done(phase,after,ticks):
   return {'kind':'NATIVE_COMPLETED','cycle':16,'phase':phase,'operation_id':op+phase.upper(),'result':{'nativeTick':after,'nativeTicks':ticks},'wall_seconds':1}
  q1={'action':'ASK_STATION','null':False,'nativeTick':971211,'nativeTicks':356};q2={'action':'EXIT_0','null':False,'nativeTick':971233,'nativeTicks':22}
  old_events=[{'kind':'PROTOCOL_STARTED','identity':{'session':session},'source_tick':970855},intent('decision'),done('decision',971211,356),intent('query_sensor'),done('query_sensor',971233,22),intent('function',bad)]
  row={'cycle':16,'new_opportunity':12,'Native_Q1':q1,'Native_Q2':q2,'tool_result':{'kind':'LESSON','formed':True},'actual_numeric':None,
   'world_result':{'resourceDelivered':False,'resourceCollected':False,'outcome':'KEY_COLLECTED'},'executed_route':'EXIT_0','Native_route':'EXIT_0','host_order_prepared':True,
   'state_after':{'nativeTick':972419,'completedCycles':16,'delivered':0,'resourceCount':0},'Q1_Q2_and_motion_from_interrupted_prefix':True}
  new_events=[{'kind':'LIVE_PENDING_ATTACHED','status':{'S':{'sessionId':session,'completedCycles':15,'cycle':16,'nativeTick':971233}},'no_world_restore':True,'no_Q1_Q2_or_movement_repeated':True,'original_function_operation_id':op+'FUNCTION'}]
  if repaired:
   new_events +=[intent('function',good),done('function',971395,162),intent('feedback',{'materialConsequence':False}),done('feedback',972419,1024),{'kind':'OPPORTUNITY_COMPLETED',**row}]
   (new/'RESULTADO.json').write_text(json.dumps({'identity':{'participant':'LIVE_NATIVE','session':session},'source_tick':971233,'final_tick':972419,'new_Native_ticks':1186,'owner_closed':True,'continued_partial_original_opportunity':16,'rows':[row]}),'utf8')
  if duplicates:
   # Duplicate full-prefix completion records are aliases, not more evolution.
   new_events[1:1]=old_events[1:5]
  for directory,events in((old,old_events),(new,new_events)):
   (directory/'EVENTS.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in events),'utf8')
  partial=root/'partial.json';partial.write_text(json.dumps({'schema':'DEE.RBX06.partial_known_not_admitted.FUNCTION16.R01',
   'classification':'TECHNICAL_VALIDATOR_ERROR_BEFORE_QUEUE','identity':{'life':'SYNTHETIC_ONLY','session_id':session},'current_closed_native_tick':971233,
   'partial_opportunity':{'cycle':16,'function_id':op+'FUNCTION','function_native_admitted':False,'host_intent_payload':bad}}),'utf8')
  result=m.main_recalculate([('LIVE_NATIVE',old),('LIVE_NATIVE',new)],[],None,[],[],None,root/'output',[partial])
  return tmp,result,root
 def test_partial_and_resumed_phase_sum_not_copied_q1_q2(self):
  t,r,_=self.case()
  try:
   self.assertEqual(r['issues'],[])
   self.assertEqual(r['totals']['LIVE_NATIVE']['opportunities_completed'],1)
   self.assertEqual(r['Native_tick_accounting']['unique_completed_phase_count'],4)
   self.assertEqual(r['Native_tick_accounting']['actual_ticks_sum_unique_ids'],1564)
   self.assertEqual(r['phase_completion_aliases_deduplicated'],2)
   row=r['new_opportunity_rows'][0];self.assertEqual(row['Native_phase_ticks_unique'],1564)
   self.assertEqual(row['session'],'SYNTHETIC_CONTINUATION')
   self.assertTrue(row['original_Q1_Q2_reused_after_known_nonadmission'])
   self.assertEqual(r['known_not_admitted_reconciliations'][0]['completed_native_ticks'],162)
   self.assertTrue(r['known_not_admitted_reconciliations'][0]['transport_only_equivalence_checked'])
  finally:t.cleanup()
 def test_partial_only_counts_378ticks_but_zero_complete_opportunities(self):
  t,r,_=self.case(repaired=False)
  try:
   self.assertEqual(r['issues'],[]);self.assertEqual(r['totals']['LIVE_NATIVE']['opportunities_completed'],0)
   self.assertEqual(r['Native_tick_accounting']['actual_ticks_sum_unique_ids'],378)
   self.assertEqual(len(r['totals']['LIVE_NATIVE']['partial_completed_phases_not_counted_as_opportunities']),2)
   self.assertFalse(r['known_not_admitted_reconciliations'][0]['Native_completion_present'])
  finally:t.cleanup()
 def test_changed_lesson_content_is_discrepancy_not_transport_repair(self):
  t,r,_=self.case(changed_experience=True)
  try:
   self.assertTrue(any(x['issue']=='TRANSPORT_REPAIR_CHANGED_EXPERIENCE'for x in r['issues']))
   self.assertFalse(r['known_not_admitted_reconciliations'][0]['transport_only_equivalence_checked'])
  finally:t.cleanup()
 def test_exact_shape_repair_and_zero_not_none(self):
  bad={'tool':{'kind':'LESSON','items':{'1':{'form':'luma','observedSign':-1}}}}
  good={'tool':{'kind':'LESSON','items':[{'form':'luma','observedSign':-1}]}}
  self.assertTrue(m.transport_shape_equivalent(bad,good));good['tool']['items'][0]['observedSign']=0
  self.assertFalse(m.transport_shape_equivalent(bad,good))
 def test_distinct_overlapping_ids_are_not_deduplicated_as_time(self):
  p={'a':{'kind':'NATIVE_COMPLETED','cycle':5,'phase':'decision','result':{'nativeTick':100,'nativeTicks':10}},
     'b':{'kind':'NATIVE_COMPLETED','cycle':5,'phase':'query_sensor','result':{'nativeTick':105,'nativeTicks':10}}}
  i={x:{'context':{'session_id':'FIXTURE'}}for x in p};issues=[]
  report=m.completed_phase_accounting(p,i,{x:'LIVE_NATIVE'for x in p},issues)
  self.assertEqual(report['actual_ticks_sum_unique_ids'],20)
  self.assertTrue(any(x['issue']=='OVERLAPPING_DISTINCT_NATIVE_PHASES'for x in issues))
  self.assertFalse(report['histories'][0]['contiguous_recorded_interval'])
 def test_timing_gap_is_reported_not_filled(self):
  p={'a':{'kind':'NATIVE_COMPLETED','cycle':5,'phase':'decision','result':{'nativeTick':100,'nativeTicks':10}},
     'b':{'kind':'NATIVE_COMPLETED','cycle':5,'phase':'query_sensor','result':{'nativeTick':112,'nativeTicks':10}}}
  i={x:{'context':{'session_id':'FIXTURE'}}for x in p};issues=[]
  report=m.completed_phase_accounting(p,i,{x:'LIVE_NATIVE'for x in p},issues)
  self.assertEqual(report['actual_ticks_sum_unique_ids'],20)
  self.assertEqual(report['histories'][0]['elapsed_tick_span'],22)
  self.assertEqual(len(report['histories'][0]['gaps']),1)
  self.assertEqual(issues,[])
 def test_same_assisted_action_is_not_effective_override(self):
  t,_,root=self.case()
  try:
   session='SYNTHETIC_CONTINUATION'
   world=root/'world.json';world.write_text(json.dumps({'S':{'participant':'LIVE_NATIVE','sessionId':session,'cycle':16,'completedCycles':16},'native_tick':972419,
    'events':[{'kind':'ASSISTED_ORDER','sessionId':session,'seq':32,'data':{'actionId':'R06_'+session+'_16_QUERY_SENSOR','native_action':'EXIT_0','executed_action':'EXIT_0'}}]}),'utf8')
   r=m.main_recalculate([('LIVE_NATIVE',root/'interrupted'),('LIVE_NATIVE',root/'continued')],[world],None,[],[],None,root/'with_world',[root/'partial.json'])
   s=r['totals']['LIVE_NATIVE'];self.assertEqual(s['assisted_order_world_events'],1)
   self.assertEqual(s['prepared_assisted_contract_opportunities'],1);self.assertEqual(s['assisted_route_overrides'],0)
  finally:t.cleanup()
 def test_completed_request_and_partial_material_admission_are_different(self):
  t,_,root=self.case()
  try:
   session='SYNTHETIC_CONTINUATION';operation='R06_'+session+'_16_FUNCTION';d=root/'continued'
   data=json.loads((d/'RESULTADO.json').read_text('utf8'));tool={'kind':'LESSON','formed':False,'capability_execution_admitted':False,'reason':'NATIVE_PARTIAL_ADMISSION'}
   data['rows'][0]['tool_result']=tool;(d/'RESULTADO.json').write_text(json.dumps(data),'utf8')
   events=[json.loads(x)for x in(d/'EVENTS.jsonl').read_text('utf8').splitlines()]
   for row in events:
    if row.get('kind')=='NATIVE_COMPLETED'and row.get('phase')=='function':row['result'].update(accepted=True,toolResult=tool)
    if row.get('kind')=='NATIVE_INTENT'and row.get('phase')=='feedback':row['payload']={'materialConsequence':True,'outcome':'TOOL_NO_RESULT'}
    if row.get('kind')=='OPPORTUNITY_COMPLETED':row['tool_result']=tool
   events.insert(-1,{'kind':'MCP_COMPLETED','label':'tool','result':{'executionStatus':'NO_RESULT','S':{'sessionId':session,'cycle':16},'result':{'outcome':'TOOL_NO_RESULT','invalidAction':True,'materialConsequence':True,'resourceCollected':False,'resourceDelivered':False}}})
   (d/'EVENTS.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in events),'utf8')
   primary=root/'primary.json';primary.write_text(json.dumps({'context':{'operation_id':operation},'life_id':'SYNTHETIC_ONLY','visible_tool':{'kind':'LESSON'},'input_admission_complete':False,
    'Native_inputs':{'unique_requested':6,'applied':4,'rejected':2},'requests_normalized':[{'id':i,'channel':'fixture','payload':0,'requested_tick':100+i,'receipt':{'status':'applied'if i<4 else'rejected'}}for i in range(6)]}),'utf8')
   r=m.main_recalculate([('LIVE_NATIVE',root/'interrupted'),('LIVE_NATIVE',d)],[],None,[primary],[],None,root/'with_partial_lesson',[root/'partial.json'])
   n=r['totals']['LIVE_NATIVE'];row=r['new_opportunity_rows'][0]
   self.assertEqual(n['function_transport_requests_completed'],1);self.assertEqual(n['function_transport_requests_accepted_explicitly'],1)
   self.assertEqual(n['function_capability_execution_not_admitted'],1);self.assertEqual(n['partial_lesson_admissions'],1)
   self.assertFalse(row['primary_all_inputs_applied']);self.assertEqual(row['primary_input_summary']['unique_requested'],6)
   self.assertEqual(r['Native_receipts_coverage']['unique'],6);self.assertEqual(r['Native_receipts_coverage']['statuses'],{'applied':4,'rejected':2})
   self.assertTrue(row['actual_material_failure']);self.assertEqual(row['world_result_authoritative_after_tool']['outcome'],'TOOL_NO_RESULT')
   self.assertEqual(row['world_result_before_tool_update']['outcome'],'KEY_COLLECTED');self.assertTrue(row['world_result_authoritative_after_tool']['invalidAction'])
   self.assertEqual(r['Native_tick_accounting']['actual_ticks_sum_unique_ids'],1564)
  finally:t.cleanup()
if __name__=='__main__':unittest.main(verbosity=2)
