"""Standard executed-route WSLS fixtures, no MAIN outcomes or Native."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(file))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
c=load('standard','comparadores_apd03_wsls_estandar_r03.py')
old=load('preference','comparadores_apd03_r02.py')
fixtures=load('referencefixtures','test_comparadores_r02_n0.py')


class StandardFixtures(unittest.TestCase):
    def test_stay_on_actual_forced_route_after_success(self):
        task=fixtures.fixture()['events'][0];task['public_resources']['allowed_procedures']=['native']
        p=c.StandardWSLS();p.teach({'text':'suma','operation':'add'});p.route='external'
        obs=c.projection(task,3);actual=p.choose(obs);self.assertEqual(actual['procedure'],'native')
        p.feedback(obs,actual,{'category':'SUCCESS'});self.assertEqual(p.route,'native')

    def test_shift_from_actual_not_old_preference_after_failure(self):
        task=fixtures.fixture()['events'][0];task['public_resources']['allowed_procedures']=['native']
        p=c.StandardWSLS();p.teach({'text':'suma','operation':'add'});p.route='external'
        obs=c.projection(task,3);actual=p.choose(obs)
        p.feedback(obs,actual,{'category':'FAILURE'});self.assertEqual(p.route,'external')

    def test_only_change_is_update_law_and_policy_name(self):
        original=fixtures.fixture()['events'][0]
        for missing in(False,True):
            projection=[];actions=[]
            for left,second,ctx in((0,0,0),(32,31,1),(17,9,None)):
                task=copy.deepcopy(original);task.update(left=left,second=second,context=ctx)
                obs=c.projection(task,None if missing else second)
                self.assertEqual(obs,old.projection(task,None if missing else second))
                p=c.StandardWSLS();p.teach({'text':'suma','operation':'add'});p.begin_task()
                projection.append(obs);actions.append(p.choose(obs))
            self.assertEqual(projection,[projection[0]]*3);self.assertEqual(actions,[actions[0]]*3)

    def test_file_effects_and_omitted_feedback_replay(self):
        with tempfile.TemporaryDirectory(prefix='dee_apd03_standard_fixture_')as directory:
            root=Path(directory);program=root/'fixture.json';program.write_bytes(c.base.canonical(fixtures.fixture()))
            summary=c.run(program,root/'output','wsls_estandar');recalculated=c.recalculate(root/'output')
            self.assertEqual(recalculated['issues'],0);self.assertEqual(summary['task_count'],4)
            rows=[json.loads(line)for line in(root/'output/eventos_primarios.jsonl').read_bytes().splitlines()]
            self.assertTrue(all(r['public_return']is None for r in rows if r['kind']=='opportunity'and r['task_id']=='fixture_3'))
            restored=c.restore_policy('wsls_estandar',{'lexicon':{},'last_route':'external','queries':1})
            self.assertEqual(restored.route,'external')


if __name__=='__main__':unittest.main()
