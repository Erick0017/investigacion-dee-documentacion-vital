"""N0 contract checks with conventional callback fixtures, never a DEE life."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


def load(name,file):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parent/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


e=load('apd03env','entorno_compartido_apd03_r01.py')
q=load('apd02quality','vendor/evaluador_calidad_apd02.py')
p=load('apd02effects','vendor/proveedores_prueba_apd02.py')


class EnvironmentTests(unittest.TestCase):
    def create(self,directory,mode='local_useful',visible=False):
        return e.SharedGoalEnvironment(task_id='fixture_goal',text='suma',left=7,second=4,
            second_initially_public=visible,directory=directory,quality=q,effects=p,
            context=0,feedback_mode=mode)
    def calc(self,op,operands):
        return operands[0]+operands[1]if op=='add'else operands[0]-operands[1]
    def test_local_information_consequence_and_final_file_are_distinct(self):
        with tempfile.TemporaryDirectory()as directory:
            world=self.create(Path(directory)/'goal')
            row=world.commit_selected(0,1,native_value_reader=self.calc,synthetic_fixture=True)
            self.assertEqual(row['feedback'],{'category':'SUCCESS'})
            self.assertTrue(row['local_action_useful'])
            self.assertFalse(row['final_goal_file_completed'])
            self.assertFalse(row['native_provider_called'])
            row=world.commit_selected(0,1,native_value_reader=self.calc,synthetic_fixture=True)
            self.assertEqual(row['feedback'],{'category':'FAILURE'})
            self.assertFalse(row['new_public_fact_revealed'])
            row=world.commit_selected(-1,1,native_value_reader=self.calc,synthetic_fixture=True)
            self.assertTrue(row['final_goal_file_completed'])
            self.assertEqual(row['feedback'],{'category':'SUCCESS'})
            self.assertEqual(row['committed_effect']['provider_calls'],{'native':1,'external':0})
    def test_file_only_contrast_keeps_query_failure(self):
        with tempfile.TemporaryDirectory()as directory:
            world=self.create(Path(directory)/'goal',mode='file_only')
            row=world.commit_selected(0,1,native_value_reader=self.calc,synthetic_fixture=True)
            self.assertEqual(row['feedback'],{'category':'FAILURE'})
            self.assertTrue(row['local_action_useful'])
            self.assertFalse(row['final_goal_file_completed'])
    def test_visible_redundant_query_is_not_new_information(self):
        with tempfile.TemporaryDirectory()as directory:
            world=self.create(Path(directory)/'goal',visible=True)
            row=world.commit_selected(0,1,native_value_reader=self.calc,synthetic_fixture=True)
            self.assertFalse(row['new_public_fact_revealed'])
            self.assertEqual(row['feedback'],{'category':'FAILURE'})
    def test_incomplete_act_calls_no_provider(self):
        with tempfile.TemporaryDirectory()as directory:
            world=self.create(Path(directory)/'goal')
            def forbidden(*args):raise AssertionError('No provider when missing')
            row=world.commit_selected(-1,1,native_value_reader=forbidden,synthetic_fixture=True)
            self.assertEqual(row['environment_effect'],'ACT_FAILED_MISSING_OBSERVATION')
            self.assertEqual(row['feedback'],{'category':'FAILURE'})
    def test_complete_operational_restore_retains_fact_and_counter(self):
        with tempfile.TemporaryDirectory()as directory:
            world=self.create(Path(directory)/'goal')
            world.commit_selected(0,1,native_value_reader=self.calc,synthetic_fixture=True)
            state=world.operational_state()
            restored=e.restore_operational(state,directory=Path(directory)/'restored',quality=q,effects=p)
            self.assertEqual(world.observation(),restored.observation())
            self.assertEqual(world.progress(),restored.progress())
            row=restored.commit_selected(-1,1,native_value_reader=self.calc,synthetic_fixture=True)
            self.assertEqual(row['opportunity'],2)
            self.assertTrue(row['final_goal_file_completed'])
    def test_frozen_mode_cannot_restore_as_other_mode(self):
        with tempfile.TemporaryDirectory()as directory:
            world=self.create(Path(directory)/'goal');state=world.operational_state()
            state['feedback_mode']='retarget_after_outcome'
            with self.assertRaises(ValueError):
                e.restore_operational(state,directory=Path(directory)/'bad',quality=q,effects=p)


if __name__=='__main__':unittest.main()
