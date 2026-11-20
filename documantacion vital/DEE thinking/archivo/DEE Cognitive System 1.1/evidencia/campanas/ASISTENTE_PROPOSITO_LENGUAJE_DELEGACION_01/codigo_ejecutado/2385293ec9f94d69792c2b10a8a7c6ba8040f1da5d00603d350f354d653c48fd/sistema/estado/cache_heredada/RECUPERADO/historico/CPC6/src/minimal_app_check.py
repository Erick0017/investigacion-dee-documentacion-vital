"""Run a physically complete demo with no old results, targets or meaning map.

The actual participant finishes before the external comparator opens a reference
snapshot. Use a short, new staging directory: no prior material is deleted.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, put, sha, WHEEL_SHA
from supervisor import OwnedJob
from check_snapshot_equivalence import compare

WHL = 'dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
FILES = ('app.py', 'src/common.py', 'src/integrated.py', 'src/order_memory.py',
         'src/action_feedback.py', 'src/action_feedback_access.py', 'src/language.py',
         'src/consolidation.py', 'src/curriculum.py', 'src/order_language.py',
         'src/snapshot_storage.py', 'src/balanced_sources.py', 'src/word_bus.py', 'runtime/' + WHL)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--staging', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); p.add_argument('--baseline-snapshot', type=Path, required=True)
    p.add_argument('--seed', type=int, default=1); p.add_argument('--timeout', type=int, default=180); a = p.parse_args()
    start = time.monotonic(); a.output.mkdir(parents=True, exist_ok=False); stage = a.staging.resolve()
    stage.mkdir(parents=True, exist_ok=False); payload = stage / 'minimal_payload'; payload.mkdir()
    generated = stage / 'generated'; generated.mkdir(); inventory = []
    for name in FILES:
        source, target = ROOT / name, payload / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        inventory.append({'path': name, 'sha256': sha(target), 'bytes': target.stat().st_size})
    assert sha(payload / 'runtime' / WHL) == WHEEL_SHA
    assert not any((payload / name).exists() for name in ('resultados', 'genealogia', 'revision', 'configuraciones', 'targets', 'NSM65_EVIDENCIAS.json'))
    argv = [sys.executable, '-I', '-B', '-X', 'utf8', str(payload / 'app.py'), '--demo', '--seed', str(a.seed),
            '--salida', str(generated / 'DIALOGOS.jsonl'), '--snapshot', str(generated / 'SESSION.deetsnap')]
    env = dict(os.environ, PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', OMP_NUM_THREADS='1')
    env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None); job = None; error = None; command = None
    try:
        with (a.output / 'stdout.log').open('wb') as out, (a.output / 'stderr.log').open('wb') as err:
            child = subprocess.Popen(argv, cwd=payload, env=env, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job = OwnedJob(child)
                try: child.wait(timeout=min(max(a.timeout, 1), 600))
                except subprocess.TimeoutExpired: job.terminate(); child.wait(timeout=15); raise
            except BaseException:
                if child.poll() is None:
                    if job: job.terminate()
                    else: child.kill()
                    child.wait(timeout=15)
                raise
            finally:
                if job: job.close()
            command = {'argv': argv, 'exit_code': child.returncode, 'seconds': time.monotonic() - start}
        assert child.returncode == 0
        # The first and only reference read occurs here, after the child ends.
        comparison = compare(generated / 'SESSION.deetsnap', a.baseline_snapshot)
        assert comparison['verified']; status = 'VERIFIED'
    except BaseException as exc:
        status = 'ERROR'; error = repr(exc); comparison = None
    report = {'schema': 'CPC6.minimal-app.v1', 'status': status, 'error': error,
        'copied_files': inventory, 'copied_count': len(inventory), 'command': command,
        'comparisons_after_trajectories_only': True, 'comparison': comparison,
        'seed_used_only_by_explicit_environment_generator': a.seed,
        'excluded': ['historical ZIPs', 'results', 'targets', 'teaching maps', 'NSM catalogue', 'external response tables', 'private runtime paths'],
        'generated_files': [{'path': path.relative_to(generated).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)} for path in generated.rglob('*') if path.is_file()],
        'elapsed_seconds': time.monotonic() - start,
        'scope': 'Physical trajectories executed using only the explicitly listed current files and installed official 4.0.0. Reference comparison is an external instrument, not participant cognition.'}
    put(a.output / 'MINIMAL_REPORT.json', report); print(json.dumps({'status': status, 'files': len(inventory), 'error': error}))
    if status != 'VERIFIED': raise SystemExit(1)


if __name__ == '__main__': main()
