"""Synthetic passive fixtures only; no actual R06 run, world, model or SQL."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('passive_r06_fixture',HERE/'RECALCULO_INTEGRAL_V2_R02.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
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
   {'kind':'NATIVE_COMPLETED','cycle':5,'phase':'feedback','operation_id':'f','result':{'nativeTick':955215},'wall_seconds':2},
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
if __name__=='__main__':unittest.main(verbosity=2)
