"""Bounded N0 fixtures, not a Native experiment or E1 comparison."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('comparadores_apd03',Path(__file__).with_name('comparadores_apd03.py'))
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def fixture_program():
    events=[{'kind':'teach','teaching':{'text':'suma','operation':'add'}}]
    for i in range(4):
        events.append({'kind':'task','task':{
            'task_id':'fixture_'+str(i),'text':'suma','left':5+i,'second':3,
            'second_initially_public':bool(i%2),'context':i%2,
            'public_resources':{'available':['native','external'],'query_price':1},
            'required_operation':'add','purpose':'N0_contract_fixture',
            'max_opportunities':4,
            'laws':{route:{'price':1,'delay_ticks':0,'available':True} for route in c.ROUTES},
            'faults':{'native':{'wrong_value_delta':1} if i in (0,1) else {},
                      'external':{} if i in (0,1) else {'wrong_value_delta':1}}}})
    return {'schema':'DEE.APD03.common_task_program.R01','events':events,
            'scope':'N0 fixture only; does not advance DEE'}


class ContractTests(unittest.TestCase):
    def test_public_projection_excludes_private(self):
        task=fixture_program()['events'][1]['task']
        obs=c.public_observation(task,None)
        self.assertEqual(set(obs),c.PUBLIC_KEYS)
        for forbidden in ('task_id','required_operation','laws','faults','seed','purpose'):
            self.assertNotIn(forbidden,obs)

    def test_binary_feedback_only(self):
        p=c.WinStayLoseShift();p.teach({'text':'suma','operation':'add'})
        obs=c.public_observation(fixture_program()['events'][1]['task'],3)
        action=p.choose(obs)
        with self.assertRaises(ValueError):
            p.feedback(obs,action,{'category':'FAILURE','correct_route':'external'})
        p.feedback(obs,action,{'category':'FAILURE'})
        self.assertEqual(p.choose(obs)['procedure'],'external')

    def test_context_memory_is_separate(self):
        p=c.ContextTable();p.teach({'text':'suma','operation':'add'})
        obs=c.public_observation(fixture_program()['events'][1]['task'],3)
        a=p.choose(obs);p.feedback(obs,a,{'category':'FAILURE'})
        self.assertEqual(p.choose(obs)['procedure'],'external')
        other=copy.deepcopy(obs);other['context']=1
        self.assertEqual(p.choose(other)['procedure'],'native')

    def test_fixed_queries_even_visible(self):
        p=c.Fixed();p.teach({'text':'suma','operation':'add'});p.begin_task()
        obs=c.public_observation(fixture_program()['events'][1]['task'],3)
        self.assertEqual(p.choose(obs),{'kind':'QUERY'})
        self.assertEqual(p.choose(obs)['procedure'],'native')

    def test_full_execution_and_portable_recalculation(self):
        with tempfile.TemporaryDirectory(prefix='apd03_comparator_fixture_') as directory:
            root=Path(directory);path=root/'fixture.json'
            path.write_bytes(c.canonical(fixture_program()))
            for policy in c.POLICIES:
                out=root/policy;summary=c.run(path,out,policy)
                recalculated=c.recalculate(out)
                for key,value in recalculated.items():
                    self.assertEqual(summary[key],value)
                self.assertEqual(summary['task_count'],4)
                self.assertLess(summary['process_total']['peak_working_set_bytes_process_to_date'],256*1024*1024)
                self.assertEqual(summary['energy'],'NO MEDIDA')
                for row in (json.loads(line) for line in (out/'eventos_primarios.jsonl').read_text('utf8').splitlines()):
                    if row['kind']=='opportunity' and row.get('committed_effect'):
                        self.assertEqual(sum(row['committed_effect']['provider_calls'].values()),1)
                        self.assertTrue(row['committed_effect']['no_dual_execution_or_fallback'])

    def test_uncertain_effect_is_preserved_without_retry_or_return(self):
        program=fixture_program();program['events']=program['events'][:2]
        task=program['events'][1]['task'];task['second_initially_public']=True
        task['faults']['native']={'fail_after_write':True}
        with tempfile.TemporaryDirectory(prefix='apd03_comparator_uncertain_') as directory:
            root=Path(directory);path=root/'fixture.json';path.write_bytes(c.canonical(program))
            summary=c.run(path,root/'output','wsls')
            self.assertEqual(summary['uncertain_effects'],1)
            self.assertEqual(summary['opportunities_requested'],1)
            rows=[json.loads(line) for line in (root/'output'/'eventos_primarios.jsonl').read_text('utf8').splitlines()]
            self.assertIsNone(rows[-1]['public_return'])
            self.assertEqual(rows[-1]['committed_effect']['state'],'uncertain')
            self.assertEqual(rows[-1]['policy_state_after']['last_route'],'native')
            self.assertTrue(list((root/'output'/'artifacts').glob('*.json')))


if __name__=='__main__':
    unittest.main()
