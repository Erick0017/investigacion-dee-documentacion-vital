"""Install and exercise the exact sealed 4.5 ZIP in a fresh, offline environment.

The plan is read from that ZIP. Native tasks run in owned, bounded Windows jobs.
Assertions are evaluated after the trajectories, not provided to participants.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from package45 import ROOT, ARCHIVE_ROOT, WHEEL, safe_name, sha, put, verify
sys.path.insert(0, str(ROOT / 'src'))
from supervisor import OwnedJob, remaining

ENGINE_CHECK = r'''
import hashlib,json,pathlib,sys
import dee_thinking as d
identity=json.loads(sys.argv[1])
assert sys.version_info[:2]==(3,13) and sys.maxsize>2**32
assert d.__version__=='4.5.0' and d.kernel_identity()['kernel_version']==27
module=pathlib.Path(d.__file__).resolve()
assert module.is_relative_to(pathlib.Path(sys.prefix).resolve()/'Lib'/'site-packages')
native=pathlib.Path(d._native.__file__).resolve()
assert native.is_relative_to(pathlib.Path(sys.prefix).resolve()/'Lib'/'site-packages')
assert hashlib.sha256(native.read_bytes()).hexdigest()==identity['native_sha256']
assert not any(name.startswith(('dee_universe','CPC3','CPC4','CPC5','CPC6','CPC7','SEM01')) for name in sys.modules)
pathlib.Path(sys.argv[2]).write_text(json.dumps({'version':d.__version__,'kernel':d.kernel_identity(),
 'module':str(module),'native':str(native),'python':sys.executable,'prefix':sys.prefix,
 'native_sha256':identity['native_sha256'],'wheel_sha256':identity['wheel_sha256']},indent=2),encoding='utf-8')
'''


def run_command(argv, cwd, directory, label, timeout, deadline):
    allowed = min(float(timeout), max(0, deadline - time.monotonic()))
    if allowed <= 0:
        raise TimeoutError('Original campaign/task deadline reached')
    env = dict(os.environ, PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None)
    started = time.monotonic(); job = None; status = 'START_ERROR'; process = None; error = None
    with (directory / (label + '.stdout.log')).open('wb') as stdout, (directory / (label + '.stderr.log')).open('wb') as stderr:
        try:
            process = subprocess.Popen([str(x) for x in argv], cwd=str(cwd), env=env, stdout=stdout, stderr=stderr,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            job = OwnedJob(process); status = 'COMPLETED'
            try:
                process.wait(timeout=allowed)
            except subprocess.TimeoutExpired:
                status = 'TIMEOUT'; job.terminate(); process.wait(timeout=30)
        except BaseException as exc:
            error = repr(exc)
            if process is not None and process.poll() is None:
                if job:
                    job.terminate()
                else:
                    process.kill()
                process.wait(timeout=30)
        finally:
            if job:
                job.close()
    result = {'label': label, 'argv': [str(x) for x in argv], 'cwd': str(cwd), 'elapsed_seconds': time.monotonic() - started,
              'timeout_seconds': allowed, 'status': status, 'exit_code': process.returncode if process else None, 'error': error,
              'owned_worker_waited': process is not None and process.poll() is not None,
              'owned_job_closed': job is not None and job.handle is None}
    put(directory / (label + '.COMMAND.json'), result)
    return result


def pointer(data, path):
    if path == '':
        return data
    if not path.startswith('/'):
        raise ValueError('Use JSON Pointer')
    for part in path[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        data = data[int(part)] if isinstance(data, list) else data[part]
    return data


def validate_plan(plan):
    if plan.get('schema') != 'DEE45.clean-plan.v1' or not plan.get('commands') or not plan.get('assertions'):
        raise ValueError('Plan must contain real trajectory commands and assertions')
    ids = [r['id'] for r in plan['commands']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate command ids')
    for row in plan['commands']:
        if not row['id'] or not all(c.isalnum() or c in '_-' for c in row['id']):
            raise ValueError('Unsafe command id')
        if row['argv'][0] != '{python}' or not all(isinstance(x, str) for x in row['argv']):
            raise ValueError('Commands must launch the fresh isolated Python interpreter')
        if not 0 < row.get('timeout_seconds', 300) <= 1800:
            raise ValueError('Invalid timeout')
    for row in plan['assertions']:
        safe_name(row['path'])
        if not row['equals'] or not all(k == '' or k.startswith('/') for k in row['equals']):
            raise ValueError('Assertions must have explicit JSON Pointer checks')
    for name in plan.get('required_outputs', []):
        safe_name(name)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    p.add_argument('--plan-member', default='CLEAN_PLAN.json')
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=1800)
    p.add_argument('--respect-budget', action='store_true')
    args = p.parse_args()
    start = time.monotonic(); deadline = start + args.timeout
    if args.respect_budget:
        deadline = min(deadline, start + remaining())
    commands = []; assertions = []; container = None; error = None; status = 'ERROR'; plan_sha = None
    directory = args.destination.resolve()
    try:
        if directory.is_relative_to(ROOT.resolve()):
            raise ValueError('Clean extraction must be outside the source workspace')
        if len(str(directory)) > 180:
            raise ValueError('Choose an explicit short Windows verification directory')
        if directory.exists():
            raise FileExistsError(directory)
        safe_name(args.plan_member)
        container = verify(args.candidate)
        with zipfile.ZipFile(args.candidate) as archive:
            raw = archive.read(ARCHIVE_ROOT + '/' + args.plan_member)
            plan = json.loads(raw); validate_plan(plan); plan_sha = hashlib.sha256(raw).hexdigest()
            directory.mkdir(parents=True, exist_ok=False)
            extraction = directory / 'extracted'; extraction.mkdir()
            archive.extractall(extraction)
        root = extraction / ARCHIVE_ROOT
        if sha(root / 'wheel' / WHEEL) != container['identity']['wheel_sha256']:
            raise ValueError('Extracted wheel mismatch')
        output = directory / 'generated'; output.mkdir()
        envdir = directory / 'isolated_env'; python = envdir / 'Scripts/python.exe'
        automatic = [
            ('00_venv', [sys.executable, '-I', '-m', 'venv', str(envdir)], 120),
            ('01_offline_install', [str(python), '-I', '-m', 'pip', 'install', '--no-index', '--no-deps', str(root / 'wheel' / WHEEL)], 120),
            ('02_engine_identity', [str(python), '-I', '-c', ENGINE_CHECK, json.dumps(container['identity']), str(directory / 'ENGINE_IDENTITY.json')], 90)]
        for label, argv, timeout in automatic:
            result = run_command(argv, directory, directory, label, timeout, deadline); commands.append(result)
            if result['exit_code'] != 0 or result['status'] != 'COMPLETED':
                raise RuntimeError('Clean command failed: ' + label)
        mapping = {'{python}': str(python), '{root}': str(root), '{out}': str(output), '{work}': str(directory)}
        for i, row in enumerate(plan['commands']):
            argv = []
            for argument in row['argv']:
                for key, value in mapping.items():
                    argument = argument.replace(key, value)
                if any(token in argument for token in ('{python}', '{root}', '{out}', '{work}')):
                    raise ValueError('Unresolved placeholder')
                argv.append(argument)
            label = f'{i + 3:02d}_' + row['id']
            result = run_command(argv, directory, directory, label, row.get('timeout_seconds', 300), deadline); commands.append(result)
            if result['exit_code'] != 0 or result['status'] != 'COMPLETED':
                raise RuntimeError('Clean command failed: ' + label)
        for name in plan.get('required_outputs', []):
            path = output / name
            if not path.is_file() or not path.stat().st_size:
                raise ValueError('Missing required output: ' + name)
        for row in plan['assertions']:
            path = output / row['path']; data = json.loads(path.read_text(encoding='utf-8-sig'))
            checks = {key: pointer(data, key) == expected for key, expected in row['equals'].items()}
            assertions.append({'path': row['path'], 'sha256': sha(path), 'checks': checks, 'observations': data})
            if not all(checks.values()):
                raise AssertionError(('Posttrajectory assertion failed', row['path'], checks))
        if not assertions or not all(x['owned_worker_waited'] and x['owned_job_closed'] for x in commands):
            raise AssertionError('Incomplete proof or unclosed worker')
        status = 'VERIFIED'
    except BaseException as exc:
        error = repr(exc)
    report = {'schema': 'DEE45.exact-clean.v1', 'status': status,
              'candidate_sha256': container['sha256'] if container else sha(args.candidate) if args.candidate.is_file() else None,
              'candidate_bytes': container['bytes'] if container else None, 'plan_member': args.plan_member, 'plan_sha256': plan_sha,
              'container_verification': container, 'commands': commands, 'posttrajectory_assertions': assertions,
              'error': error, 'directory': str(directory), 'elapsed_seconds': time.monotonic() - start,
              'completed_utc': datetime.now(timezone.utc).isoformat(),
              'engine_identity': json.loads((directory / 'ENGINE_IDENTITY.json').read_text(encoding='utf-8')) if (directory / 'ENGINE_IDENTITY.json').is_file() else None,
              'scope': 'Exact ZIP, immutable embedded plan, fresh noneditable offline installation. Native tasks in owned bounded processes; comparisons only after trajectories.'}
    put(args.report, report)
    print(json.dumps({'status': status, 'commands': len(commands), 'assertions': len(assertions), 'error': error, 'elapsed_seconds': report['elapsed_seconds']}, ensure_ascii=False, indent=2))
    if status != 'VERIFIED':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
