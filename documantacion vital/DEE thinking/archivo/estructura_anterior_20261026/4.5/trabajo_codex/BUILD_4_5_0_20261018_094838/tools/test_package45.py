"""Engineering unit tests with synthetic containers; not DEE validation."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import package45 as p
from clean45 import validate_plan, pointer
from reunir45 import join


class DeliveryTests(unittest.TestCase):
    def test_unsafe_names_and_path_case(self):
        for name in ('../x', '/x', 'a/../b', 'a\\b', 'C:/x', 'a//b', 'a/./b', 'a\nb'):
            with self.assertRaises(ValueError): p.safe_name(name)
        self.assertEqual(str(p.safe_name('source/src/kernel_v27.cpp')), 'source/src/kernel_v27.cpp')

    def test_plan_requires_executions_and_posttrajectory_checks(self):
        plan = {'schema': 'DEE45.clean-plan.v1', 'commands': [{'id': 'smoke', 'argv': ['{python}', '-I', '{root}/tools/smoke_installed45.py', '--output', '{out}/smoke']}],
                'assertions': [{'path': 'smoke/SMOKE_REPORT.json', 'equals': {'/status': 'VERIFIED'}}]}
        validate_plan(plan)
        self.assertEqual(pointer({'a/b': [{'x~z': 3}]}, '/a~1b/0/x~0z'), 3)
        for field in ('commands', 'assertions'):
            invalid = dict(plan, **{field: []})
            with self.assertRaises(ValueError): validate_plan(invalid)

    def test_pid_reuse_after_original_completion(self):
        result = p.assess_current_pid({'kind': 'ACTIVE', 'creation_unix_ns': 101}, 100)
        self.assertEqual(result['observation'], 'PID_REUSED_AFTER_LEDGER_COMPLETION')
        self.assertFalse(result['current_process_unknown'])

    def test_pid_denied_is_not_a_global_existence_claim(self):
        result = p.assess_current_pid({'kind': 'DENIED'}, 100)
        self.assertEqual(result['observation'], 'PID_DENIED')
        self.assertTrue(result['current_process_unknown'])
        self.assertNotIn('process_exists', result)

    def test_active_original_not_separated_blocks_publication(self):
        for creation in (99, 100):
            with self.assertRaises(RuntimeError):
                p.assess_current_pid({'kind': 'ACTIVE', 'creation_unix_ns': creation}, 100)

    def test_original_ledger_requires_close_contract_and_acknowledged_errors(self):
        row = {'status': 'COMPLETED', 'exit_code': 0, 'pid': 123, 'owned_job_kill_on_close': True}
        self.assertTrue(p.validate_worker_ledger(row, 'hash')['original_worker_waited_and_closed'])
        with self.assertRaises(ValueError): p.validate_worker_ledger(dict(row, owned_job_kill_on_close=False), 'hash')
        failed = dict(row, exit_code=1)
        with self.assertRaises(ValueError): p.validate_worker_ledger(failed, 'hash')
        result = p.validate_worker_ledger(failed, 'hash', {'status': 'COMPLETED', 'exit_code': 1, 'ledger_sha256': 'hash'})
        self.assertTrue(result['historical_failure_preserved'])
        self.assertEqual(result['functional_status'], 'NONZERO_PRESERVED_NOT_PASS')

    def test_synthetic_container_hashes_exclusions_and_tamper(self):
        old_root, old_kernel = p.ROOT, p.KERNEL_SHA
        try:
            with tempfile.TemporaryDirectory(prefix='dee45-test-') as folder:
                root = Path(folder) / 'work'; product = Path(folder) / 'product'
                p.ROOT = root
                kernel = b'unit test fixture, not a physical kernel'
                p.KERNEL_SHA = hashlib.sha256(kernel).hexdigest()
                inputs = {'source/src/kernel_v27.cpp': kernel, 'source/CMakeLists.txt': b'fixture', 'source/pyproject.toml': b'fixture', 'source/setup.py': b'fixture',
                          'source/build/not_selected.obj': b'build artifact', 'tools/example.py': b'print("fixture")', 'jobs/adverse/stderr.log': b'adverse preserved',
                          'jobs/adverse/COMMAND.json': b'{"exit_code":1}', '.venv/unselected.txt': b'environment', 'source/tests/test_fixture.py': b'pass'}
                for name, data in inputs.items():
                    path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
                wheel_path = product / 'wheel' / p.WHEEL; wheel_path.parent.mkdir(parents=True)
                with zipfile.ZipFile(wheel_path, 'w') as wheel:
                    wheel.writestr('dee_thinking/_native.cp313-win_amd64.pyd', b'unit test only, not executable')
                    wheel.writestr('dee_thinking-4.5.0.dist-info/METADATA', 'Name: dee_thinking\r\nVersion: 4.5.0\r\n')
                    wheel.writestr('dee_thinking-4.5.0.dist-info/WHEEL', 'Wheel-Version: 1.0\r\nTag: cp313-cp313-win_amd64\r\n')
                (product / 'install_cpp').mkdir()
                (product / 'install_cpp/test.h').write_text('fixture', encoding='utf-8')
                candidate = Path(folder) / 'synthetic.zip'
                result = p.build(product, candidate, Path(folder) / 'proof.json')
                self.assertEqual(result['status'], 'VERIFIED')
                with zipfile.ZipFile(candidate) as archive:
                    self.assertIn(p.ARCHIVE_ROOT + '/jobs/adverse/stderr.log', archive.namelist())
                    self.assertFalse(any('not_selected.obj' in n or '.venv/' in n for n in archive.namelist()))
                tampered = Path(folder) / 'tampered.zip'
                with zipfile.ZipFile(candidate) as original, zipfile.ZipFile(tampered, 'w') as changed:
                    for row in original.infolist():
                        data = original.read(row)
                        if row.filename.endswith('test_fixture.py'): data += b'changed'
                        changed.writestr(row, data)
                with self.assertRaises(ValueError): p.verify(tampered)
        finally:
            p.ROOT, p.KERNEL_SHA = old_root, old_kernel

    def test_two_binary_parts_real_reconstruction_and_overwrite_protection(self):
        old_threshold = p.THRESHOLD
        try:
            p.THRESHOLD = 1
            with tempfile.TemporaryDirectory(prefix='dee45-parts-') as folder:
                source = Path(folder) / 'transport.zip'
                with zipfile.ZipFile(source, 'w') as archive: archive.writestr('data.txt', b'exact bytes retained\x00\xff')
                out = Path(folder) / 'parts'
                result = p.split(source, out)
                self.assertEqual(len(result['parts']), 2)
                self.assertTrue(result['real_reconstruction_verified'])
                restored = Path(folder) / 'restored.zip'
                join(out / 'PARTES.json', restored)
                self.assertEqual(source.read_bytes(), restored.read_bytes())
                with self.assertRaises(FileExistsError): join(out / 'PARTES.json', restored)
                first = out / result['parts'][0]['name']; first.write_bytes(first.read_bytes() + b'corrupt')
                with self.assertRaises(ValueError): join(out / 'PARTES.json', Path(folder) / 'bad.zip')
        finally:
            p.THRESHOLD = old_threshold


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeliveryTests))
    report = {'schema': 'DEE45.packaging-unit-tests.v1', 'status': 'VERIFIED' if result.wasSuccessful() else 'FAILED',
              'tests': result.testsRun, 'failures': [(str(t), text) for t, text in result.failures], 'errors': [(str(t), text) for t, text in result.errors],
              'scope': 'Synthetic containers, path safety, real two-part reconstruction, immutable hash manifests and plan validation. No native capacity claim.'}
    p.put(args.report, report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
