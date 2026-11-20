"""Only two runtime budget fields; no World/backend/model/Native is opened."""
import importlib.util,pathlib,types,unittest
p=pathlib.Path(__file__).with_name('runner_comparador_v3_R13_REANUDAR30.py');s=importlib.util.spec_from_file_location('r13_budget_fixture',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Budget(unittest.TestCase):
 def test_exact_old_new_and_unchanged_hard_policy(self):
  sentinel={'calls':4,'messages':['real29','real30'],'seed':404271,'quota':160}
  runner=types.SimpleNamespace(CUTOFF=m.OLD,HARD_CLOSE=m.HARD,policy=sentinel)
  client=types.SimpleNamespace(STOP_NEW_CALLS=m.OLD,policy=sentinel)
  result=m.configure_budget(runner,client)
  self.assertEqual(result['changed'],['loop_admission','client_admission']);self.assertEqual(runner.HARD_CLOSE,m.HARD)
  self.assertIs(runner.policy,sentinel);self.assertIs(client.policy,sentinel);self.assertEqual(sentinel['calls'],4)
  self.assertEqual((runner.CUTOFF,client.STOP_NEW_CALLS),(m.NEW,m.NEW))
if __name__=='__main__':unittest.main()
