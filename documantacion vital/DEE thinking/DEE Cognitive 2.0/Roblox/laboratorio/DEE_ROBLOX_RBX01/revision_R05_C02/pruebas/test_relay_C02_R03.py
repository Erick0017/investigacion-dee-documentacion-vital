"""Pure explicit-resume mode tests: no Native, MCP, HTTP or process calls."""
import ast
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'control/studio_mailbox_relay_C02_R03.py'
spec=importlib.util.spec_from_file_location('_C02_R03_relay_test',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class ExplicitResumeTests(unittest.TestCase):
    def test_permission_true_without_argument_is_fresh(self):
        self.assertFalse(m.explicit_resume_requested({'resumeAllowed':True},None))
    def test_permission_false_without_argument_is_fresh(self):
        self.assertFalse(m.explicit_resume_requested({'resumeAllowed':False},None))
        self.assertFalse(m.explicit_resume_requested({},None))
    def test_explicit_witness_with_permission_requests_resume(self):
        self.assertTrue(m.explicit_resume_requested({'resumeAllowed':True},Path('EXPLICIT_WORLD.json')))
    def test_explicit_witness_without_permission_rejects(self):
        with self.assertRaises(ValueError):m.explicit_resume_requested({'resumeAllowed':False},Path('WORLD.json'))
        with self.assertRaises(ValueError):m.explicit_resume_requested({},Path('WORLD.json'))
    def test_old_R02_still_preserved_and_no_implicit_path_in_R03_run(self):
        old=(ROOT/'control/studio_mailbox_relay_C02_R02.py').read_text('utf8')
        self.assertIn("witness_path=resume_boundary or",old)
        tree=ast.parse(SOURCE.read_text('utf8'))
        run=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='run')
        run_text=ast.get_source_segment(SOURCE.read_text('utf8'),run)
        self.assertNotIn('WORLD_RESTORED_BEFORE_NATIVE.json',run_text)
        self.assertIn('if explicit_resume_requested(configuration, resume_boundary)',run_text)
        self.assertIn('resume_witness(config_path,resume_boundary)',run_text)
    def test_other_closed_guards_and_routes_unchanged(self):
        profile=m.configure_profile('RBX01_R05_C02_R02',max_cycles=48)
        self.assertEqual(profile['target_cycles'],18)
        self.assertIn('c.SuspendAfter==6',m.PREPARED_SERVER_CODE)
        self.assertEqual(m.HTTP_PORT,8895)
        self.assertIn('/v1/function',m.ROUTES)
        self.assertTrue(callable(m.resume_witness))


if __name__=='__main__':unittest.main(verbosity=2)
