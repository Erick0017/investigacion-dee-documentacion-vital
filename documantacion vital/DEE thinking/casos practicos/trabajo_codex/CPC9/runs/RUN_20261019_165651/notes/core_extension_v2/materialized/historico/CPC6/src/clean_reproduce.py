"""Fresh exact-candidate CPC6 extraction, offline install and native replay.

Expected states are read only by explicit external post-trajectory assertions.
The final report is external to the candidate whose SHA it verifies.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from package_cpc6 import ROOT, WHL, WHL_SHA, PYD_SHA, put, sha, verify
from supervisor import OwnedJob, remaining

ENGINE_CHECK = r'''
import hashlib,json,pathlib,sys
import dee_thinking as d
assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32
assert d.__version__=='4.0.0' and d.kernel_identity()['kernel_version']==27
module=pathlib.Path(d.__file__).resolve()
assert module.is_relative_to(pathlib.Path(sys.prefix).resolve())
assert hashlib.sha256(pathlib.Path(d._native.__file__).read_bytes()).hexdigest()==sys.argv[1]
assert not any(x.startswith(('dee_universe','CPC3','SEM01')) for x in sys.modules)
pathlib.Path(sys.argv[2]).write_text(json.dumps({'version':d.__version__,'kernel':d.kernel_identity(),
 'module':str(module),'python':sys.executable,'native_sha256':sys.argv[1]},indent=2),encoding='utf-8')
'''


def run(argv, cwd, directory, label, timeout, deadline):
    allowed = min(timeout, max(0, deadline - time.monotonic()))
    if allowed <= 0: raise TimeoutError('Clean replay deadline reached')
    env = dict(os.environ, PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None); started = time.monotonic(); job = None
    with (directory / (label + '.stdout.log')).open('w', encoding='utf-8') as stdout, (directory / (label + '.stderr.log')).open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            job = OwnedJob(process); status = 'COMPLETED'
            try: process.wait(timeout=allowed)
            except subprocess.TimeoutExpired: status = 'TIMEOUT'; job.terminate(); process.wait(timeout=30)
        except BaseException:
            if process.poll() is None:
                if job: job.terminate()
                else: process.kill()
                process.wait(timeout=30)
            raise
        finally:
            if job: job.close()
    report = {'label': label, 'argv': argv, 'elapsed_seconds': time.monotonic() - started,
              'status': status, 'exit_code': process.returncode, 'timeout_seconds': allowed}
    put(directory / (label + '.COMMAND.json'), report)
    if process.returncode: raise RuntimeError('Clean command failed: ' + label)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True); p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True); p.add_argument('--timeout', type=int, default=1200)
    p.add_argument('--respect-campaign-deadline', action='store_true'); a = p.parse_args()
    started = time.monotonic(); deadline = started + a.timeout
    if a.respect_campaign_deadline: deadline = min(deadline, started + remaining())
    plan = json.loads(a.plan.read_text(encoding='utf-8-sig')); assert plan['schema'] == 'CPC6.clean-reproduction-plan.v1'
    assert plan.get('commands') and plan.get('asserted_json_outputs'), 'Actual native replay and explicit state checks required'
    container = verify(a.candidate); directory = a.destination.resolve(); directory.mkdir(parents=True, exist_ok=False)
    commands = []; assertions = []; error = None; status = 'ERROR'
    try:
        extraction = directory / 'extracted'; extraction.mkdir()
        with zipfile.ZipFile(a.candidate) as z: z.extractall(extraction)
        root = extraction / 'CPC6'; assert sha(root / 'runtime' / WHL) == WHL_SHA
        envdir = directory / 'isolated_env'
        commands.append(run([sys.executable, '-I', '-m', 'venv', str(envdir)], directory, directory, '00_venv', 90, deadline))
        python = envdir / 'Scripts/python.exe'
        commands.append(run([str(python), '-I', '-m', 'pip', 'install', '--no-index', '--no-deps', str(root / 'runtime' / WHL)], directory, directory, '01_offline_install', 90, deadline))
        commands.append(run([str(python), '-I', '-c', ENGINE_CHECK, PYD_SHA, str(directory / 'ENGINE_IDENTITY.json')], directory, directory, '02_identity', 90, deadline))
        output = directory / 'generated'; output.mkdir()
        mapping = {'{python}': str(python), '{root}': str(root), '{out}': str(output)}
        for i, test in enumerate(plan['commands']):
            argv = []
            for arg in test['argv']:
                for key, value in mapping.items(): arg = arg.replace(key, value)
                argv.append(arg)
            commands.append(run(argv, directory, directory, f'{i+3:02d}_{test["id"]}', test.get('timeout_seconds', 300), deadline))
        for name in plan.get('required_outputs', []):
            path = (output / name).resolve(); assert path.is_relative_to(output) and path.is_file() and path.stat().st_size
        for assertion in plan['asserted_json_outputs']:
            path = (output / assertion['path']).resolve(); assert path.is_relative_to(output)
            data = json.loads(path.read_text(encoding='utf-8-sig'))
            checks = {key: data.get(key) == value for key, value in assertion['field_equals'].items()}
            assert checks and all(checks.values()), (assertion, checks)
            assertions.append({'path': assertion['path'], 'sha256': sha(path), 'assertions': checks, 'observations': data})
        assert assertions; status = 'VERIFIED'
    except BaseException as exc: error = repr(exc)
    result = {'schema': 'CPC6.clean-reproduction.v1', 'status': status, 'candidate_sha256': container['sha256'],
        'candidate_bytes': container['bytes'], 'plan_sha256': sha(a.plan), 'commands': commands,
        'explicit_posttrajectory_verification': assertions, 'error': error,
        'engine_identity': json.loads((directory / 'ENGINE_IDENTITY.json').read_text(encoding='utf-8')) if (directory / 'ENGINE_IDENTITY.json').is_file() else None,
        'directory': str(directory), 'elapsed_seconds': time.monotonic() - started,
        'completed_utc': datetime.now(timezone.utc).isoformat()}
    put(a.report, result); print(json.dumps(result, ensure_ascii=False, indent=2))
    if status != 'VERIFIED': raise SystemExit(1)


if __name__ == '__main__': main()
