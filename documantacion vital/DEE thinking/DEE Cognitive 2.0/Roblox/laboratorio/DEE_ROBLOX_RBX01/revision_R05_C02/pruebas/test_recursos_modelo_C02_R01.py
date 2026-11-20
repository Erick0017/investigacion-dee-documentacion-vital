"""Synthetic offline fixtures; no live logs/models/Native are read or run."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/'analisis/RECALCULO_RECURSOS_MODELO_C02_R01.py'
spec=importlib.util.spec_from_file_location('resources_fixture',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Fixtures(unittest.TestCase):
 def run_case(self,policy,server=()):
  root=Path(tempfile.mkdtemp(prefix='c02_resources_fixture_'));p=root/'policy.jsonl';s=root/'server.jsonl'
  p.write_text(''.join(json.dumps(r)+'\n'for r in policy),encoding='utf-8');s.write_text(''.join(json.dumps(r)+'\n'for r in server),encoding='utf-8')
  out=root/'out';return m.recalculate([p],[s]if server else[],out),out
 def response(self,call=1,choice=None):
  return {'utc':'2026-11-15T18:00:00+00:00','kind':'MODEL_RESPONSE','run_id':'FIXTURE','call':call,
   'kind_requested':'query_sensor','choice':choice,'wall_seconds':3.0,'metrics':{'prompt_eval_count':40,'eval_count':8,
   'total_duration':2_000_000_000,'eval_duration':1_000_000_000}}
 def test_valid_wait_not_null(self):
  r,o=self.run_case([self.response(choice={'action':'SAFE_WAIT'})]);s=r['runs']['FIXTURE']
  self.assertEqual(s['valid_choices'],1);self.assertEqual(s['voluntary_safe_wait_responses'],1)
  self.assertEqual(s['response_kind_counts'],{'query_sensor':1});self.assertEqual(s['aggregate_generated_tokens_per_eval_second'],8)
  self.assertEqual(json.loads((o/'RECURSOS_MODELO.json').read_text('utf-8'))['model_HTTP_MCP_calls'],0)
 def test_null_not_intentional_wait(self):
  r,_=self.run_case([self.response()]);s=r['runs']['FIXTURE']
  self.assertEqual(s['valid_choices'],0);self.assertEqual(s['voluntary_safe_wait_responses'],0)
 def test_alias_dedup_and_completion(self):
  a=self.response(choice={'action':'SAFE_WAIT'});completed={'kind':'COMPLETED','run_id':'FIXTURE','operation_id':'op1',
   'result':{'evidence':{'model_call':1}}};r,_=self.run_case([a,a,completed])
  self.assertEqual(r['response_aliases_deduplicated'],1);self.assertEqual(r['runs']['FIXTURE']['recorded_responses'],1)
  self.assertEqual(r['runs']['FIXTURE']['responses_linked_to_completed_operations'],1)
 def test_cpu_delta_is_lifecycle_not_call(self):
  rows=[{'kind':'HOST_RESOURCES','utc':'2026-11-15T18:00:00+00:00','cpu_user_seconds':5,'cpu_kernel_seconds':2},
    {'kind':'HOST_RESOURCES','utc':'2026-11-15T18:00:05+00:00','cpu_user_seconds':9,'cpu_kernel_seconds':3}]
  r,_=self.run_case([self.response()],rows);self.assertEqual(r['server_lifecycles'][0]['observed_cumulative_job_cpu_delta_seconds'],5)
  self.assertNotIn('cpu_seconds',r['runs']['FIXTURE'])
 def test_empty_response_metrics_not_zero(self):
  row=self.response();row['metrics']={};r,_=self.run_case([row]);stats=r['runs']['FIXTURE']['metrics']
  self.assertIsNone(stats['generated_tokens_reported']['sum']);self.assertIsNone(r['runs']['FIXTURE']['aggregate_generated_tokens_per_eval_second'])
 def test_new_output_required(self):
  r,out=self.run_case([self.response()])
  with self.assertRaises(FileExistsError):m.recalculate([],[],out)
if __name__=='__main__':unittest.main()
