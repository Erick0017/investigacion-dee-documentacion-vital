"""Actual Python subprocess with spaces in executable, script and arguments; no DEE."""
from pathlib import Path
import ast
import json
import subprocess
import sys
import tempfile
import unittest

class WindowsArguments(unittest.TestCase):
    def test_python_script_and_arguments_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='SDK argv spaces ') as d:
            root = Path(d); script = root / 'server argument probe.py'
            script.write_text('import json,sys;print(json.dumps(sys.argv[1:]));raise SystemExit(7)\n', encoding='utf8')
            values = ['D:\\GENESIS AI\\SDK local\\state.json', 'SDK_DEMO_0123456789ABCDEF']
            result = subprocess.run([sys.executable, '-I', '-B', str(script), *values], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 7)
            self.assertEqual(json.loads(result.stdout), values)

    def test_native_launcher_uses_argument_list_subprocess_not_execv(self):
        source = Path(__file__).with_name('iniciar_sesion.py').read_text('utf8')
        tree = ast.parse(source)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertFalse(any(isinstance(n.func, ast.Attribute) and n.func.attr == 'execv' for n in calls))
        self.assertTrue(any(isinstance(n.func, ast.Attribute) and n.func.attr == 'run' for n in calls))

if __name__ == '__main__': unittest.main(verbosity=2)
