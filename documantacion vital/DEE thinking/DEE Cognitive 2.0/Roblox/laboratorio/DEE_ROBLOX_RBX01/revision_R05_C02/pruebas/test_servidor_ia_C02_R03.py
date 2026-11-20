"""Daemon version/guard fixtures; no HTTP, model, Native, subprocess or GUI."""
import ast
import datetime
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'comparadores/servidor_ia_local_C02_R03.py'
spec=importlib.util.spec_from_file_location('_C02_AI_daemon_R03_fixture',FILE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class DaemonTests(unittest.TestCase):
    def test_exact_new_deadline_and_preserved_old_source(self):
        self.assertEqual(datetime.datetime.fromtimestamp(m.HARD_FINISH,datetime.timezone.utc).isoformat(),'2026-11-15T20:15:00+00:00')
        self.assertIn('HARD_FINISH=1794744900',(ROOT/'comparadores/servidor_ia_local_C02.py').read_text('utf8'))
    def test_old_or_out_of_window_deadlines_rejected_before_any_IO(self):
        with patch.object(m,'get_json',side_effect=AssertionError('HTTP forbidden in fixture')), patch.object(m.time,'time',return_value=m.HARD_FINISH-30):
            for deadline in(1794744900,m.HARD_FINISH+1,float('nan'),float('inf'),'18:15'):
                with self.assertRaises(ValueError):m.run(deadline)
    def test_lifecycle_outputs_are_new_and_old_names_not_reused(self):
        source=FILE.read_text('utf8')
        for name in('SERVIDOR_IA_C02_R03.jsonl','ollama_R03.stop','ollama_isolated_R03_stdout.log','ollama_isolated_R03_stderr.log','tmp_ollama_R03'):
            self.assertIn(name,source)
        self.assertNotIn("log=ROOT/'SERVIDOR_IA_C02.jsonl'",source)
        self.assertIn("if log.exists()or stop.exists():raise ValueError",source)
    def test_model_memory_endpoint_and_cloud_guards_unchanged(self):
        self.assertEqual(m.MEMORY_LIMIT,6*1024**3)
        self.assertEqual(m.ENDPOINT,'http://127.0.0.1:11435')
        source=FILE.read_text('utf8')
        self.assertIn('a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72',source)
        self.assertIn("'OLLAMA_NO_CLOUD':'1'",source)
        self.assertIn("'OLLAMA_CONTEXT_LENGTH':'8192'",source)
        self.assertIn('identity.stat()',source)
        self.assertNotIn('identity.read_',source)
    def test_policy_and_global_budget_not_written_by_daemon(self):
        source=FILE.read_text('utf8')
        self.assertNotIn('CUOTA_LLM_C02',source)
        self.assertNotIn('POLICY_STATE_C02',source)
        self.assertNotIn('PUBLIC_RULES',source)
        tree=ast.parse(source)
        self.assertTrue(any(isinstance(n,ast.If)and '__name__'in ast.unparse(n.test)for n in tree.body))


if __name__=='__main__':unittest.main(verbosity=2)
