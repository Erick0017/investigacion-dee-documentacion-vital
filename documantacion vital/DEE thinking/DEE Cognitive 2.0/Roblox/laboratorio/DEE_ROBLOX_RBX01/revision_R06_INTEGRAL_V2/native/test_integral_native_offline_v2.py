"""Offline stdlib fixtures only; no DEE, owner, clone, HTTP or Studio execution."""
from pathlib import Path
import ast,importlib.util,json,tempfile,threading,unittest
ROOT=Path(__file__).resolve().parent

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
actor=module('integral_fixture_actor','bundle/rbx06_native_integral.py')
helper=module('integral_fixture_helper','bundle/rbx06_funciones_native.py')
support=module('integral_fixture_support','owner_support_integral_v2.py')
prep=module('integral_fixture_preparer','preparar_descendiente_integral_v2.py')
adapter=module('integral_fixture_adapter','adapter_integral_v2.py')
class Tests(unittest.TestCase):
 def sensors(self):return dict(station=5,stage=2,contact=2,inventoryKey=False,inventoryResource=True,queryAvailable=True,stationSignal=-1,permissionStock=196,publicContactCode=5,lastFailure=False,numberAPresent=True,codeBPresent=True,numberAVersion=1,codeBCurrent=True,goalDelivery=True)
 def test_sensor_codec_no_expected_value_or_route(self):
  s=self.sensors();self.assertEqual(actor.contact_datum(s),17366)
  s['numberAVersion']=31;s['inventoryKey']=True;s['lastFailure']=True
  self.assertLessEqual(actor.contact_datum(s),32766)
  self.assertFalse(any(k in s for k in('expected','target','route','solution','numberA','finalCode')))
 def test_no_world_created_by_bundle_import(self):
  self.assertEqual(helper.declared_scope()['Native_ticks_on_import'],0)
  self.assertNotIn('dee_thinking',actor.__dict__);self.assertNotIn('dee_thinking',helper.__dict__)
 def test_legacy_keys_guarded_new_epoch(self):
  text=(ROOT/'bundle/rbx06_native_integral.py').read_text('utf8')
  self.assertIn('DEE.Cognitive.RBX01.async_native.C02.R01',text)
  self.assertIn("'cycles': 0, 'last_sequence': 8, 'parent_completed_opportunities': 4",text)
  self.assertIn("c.get('source_tick') == 953651",text)
  self.assertNotIn('947395',text)
 def test_readers_and_arithmetic_unchanged(self):
  self.assertEqual(helper.SIGN_OPERATION,{1:'suma',-1:'diferencia'})
  f=helper.forecast_solve(953651);self.assertGreater(f['word_read_tick'],953651)
  self.assertLessEqual(f['end_tick_upper']-953651,282)
 def test_global_ledger_distinct_world_intents(self):
  with tempfile.TemporaryDirectory(dir=ROOT)as temp:
   path=Path(temp)/'budget.json';a=support.TickLedger(path,'A',24);b=support.TickLedger(path,'B',24)
   a.begin('A','a','eci01-rbx01-decision');b.begin('B','b','eci01-rbx01-decision')
   self.assertEqual(set(a.read()['intents']),{'A','B'})
   a.finish('A','a',100,120,'eci01-rbx01-decision');self.assertIn('B',b.read()['intents'])
   b.finish('B','b',200,230,'eci01-rbx01-decision');self.assertEqual(a.read()['consumed'],50)
   with self.assertRaises(RuntimeError):a.begin('A','newq','eci01-rbx01-decision')
 def test_ledger_concurrent_accounting_no_lost_updates(self):
  with tempfile.TemporaryDirectory(dir=ROOT)as temp:
   path=Path(temp)/'budget.json';worlds=[support.TickLedger(path,str(i),24)for i in range(3)];errors=[]
   def work(i):
    try:
     w=worlds[i];w.begin(str(i),'q'+str(i),'eci01-rbx01-decision');w.finish(str(i),'q'+str(i),100,120,'eci01-rbx01-decision')
     w.begin(str(i),'f'+str(i),'eci01-rbx01-feedback');w.finish(str(i),'f'+str(i),120,130,'eci01-rbx01-feedback')
    except Exception as e:errors.append(e)
   ts=[threading.Thread(target=work,args=(i,))for i in range(3)]
   for t in ts:t.start()
   for t in ts:t.join()
   self.assertFalse(errors);v=worlds[0].read();self.assertEqual(v['consumed'],90);self.assertEqual(v['intents'],{})
   self.assertEqual(sum(x['reserved']for x in v['worlds'].values()),0)
 def test_scope_deadlines_budget_fixed(self):
  self.assertEqual((prep.START,prep.LAST_Q1,prep.CUTOFF),(1794780780,1794798600,1794802380))
  self.assertEqual(support.AGGREGATE,100000);self.assertEqual(support.MAX_WORLDS,6)
 def test_preparer_does_not_call_importer_or_engine(self):
  t=ast.parse((ROOT/'preparar_descendiente_integral_v2.py').read_text('utf8'))
  names={n.func.attr if isinstance(n.func,ast.Attribute)else n.func.id for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,(ast.Name,ast.Attribute))}
  self.assertFalse(names&{'run_until','create','import_pair','Popen','run','set_raw','set_clock','load_world_snapshot'})
 def test_adapter_forwards_actual_values_without_calculator(self):
  class Owner:
   life='fixture'
   def material(self,identifier,literal,**kwargs):
    self.args=identifier,literal,kwargs
    return {'rows':[{'version':'DEE.RBX01.async_native.INTEGRAL.V2.R01','numeric_result':0,'nativeTick':953651,'nativeTicks':0,'null':False}]}
  owner=Owner();a=adapter.create_adapter({'owner':owner})
  c={'session_id':'S','sequence':9,'observation_id':'O','operation_id':'ID','mode':'LIVE_NATIVE'}
  result=a.execute('function',{'tool':{'kind':'CALCULATE','slot':'A','form':'luma','left':2,'right':2}},c)
  self.assertEqual(result['numeric_result'],0);self.assertFalse(result['null']);self.assertEqual(owner.args[2],{'feedback':'omit','actuator':'closed'})
if __name__=='__main__':unittest.main(verbosity=2)
