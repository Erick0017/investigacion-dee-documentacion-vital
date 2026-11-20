"""Recálculo archivado APD04, stdlib, sin motor ni ticks nuevos.

Adaptación del ejecutor archivado APD03: CLIs reales con argumentos relativos,
salidas nuevas y comparación explícita. Cada job corre aislado con una cerca de
lectura/escritura; el paquete y la biblioteca estándar son sus únicas entradas.
No es reproducción Native, adquisición nueva ni comprobación del Full.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def safe(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('No absolute/traversal package member: ' + str(name))
    result = (root / p).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Member escapes supplied package')
    return result


def emit(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def install_fence(package, output):
    """Reject historical inputs, Native/site packages, network and subprocesses.

    This is an auditable dependency diagnostic, not an OS security sandbox.
    Scripts are trusted archived calculators, not arbitrary untrusted programs.
    """
    standard = {Path(sys.base_prefix).resolve(), Path(sys.prefix).resolve()}
    allowed_reads = [package, output, *standard]
    denied = []

    def inside(path, roots):
        return any(path == r or path.is_relative_to(r) for r in roots)

    def hook(event, args):
        if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            write = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            site = 'site-packages' in (part.casefold() for part in path.parts)
            if (write and not inside(path, [output])) or (not write and (not inside(path, allowed_reads) or site)):
                denied.append({'event': event, 'path': str(path), 'write': bool(write)})
                raise PermissionError('Archived recalculation crossed its file boundary: ' + str(path))
        if event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'socket.connect', 'socket.bind',
                     'ctypes.dlopen', 'os.remove', 'os.rmdir', 'os.rename', 'os.replace'):
            denied.append({'event': event})
            raise PermissionError('Not an archived-only calculator: ' + event)
        if event == 'import' and args:
            name = str(args[0])
            if name.startswith(('dee_', '_dee', 'numpy', 'ctypes')):
                denied.append({'event': event, 'name': name})
                raise PermissionError('Native/runtime dependency forbidden: ' + name)

    sys.addaudithook(hook)
    return denied


def worker(root, number, out):
    root, out = root.resolve(), out.resolve()
    if out.is_relative_to(root):
        raise ValueError('Worker writes must remain outside the package')
    plan = json.loads((root / 'RECALCULO/PLAN_GLOBAL.json').read_bytes())
    job = plan['jobs'][number]
    base = safe(root, job.get('base', '.'))
    script = safe(base, job['script'])
    result = out / (f'{number:02d}_' + job['id'] + '.json')
    argv = []
    for arg in job['args']:
        if isinstance(arg, dict) and set(arg) == {'input'}:
            argv.append(str(safe(base, arg['input'])))
        elif arg == '{output}':
            argv.append(str(result))
        elif isinstance(arg, str) and not Path(arg).is_absolute():
            argv.append(arg)
        else:
            raise ValueError('Argument must be literal, typed relative input, or {output}')
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script), *argv]
    os.chdir(tempfile.gettempdir())
    denied = install_fence(root, out)
    runpy.run_path(str(script), run_name='__main__')
    if denied:
        raise ValueError('A calculator caught a denied dependency: ' + repr(denied))


def run(root, out):
    root, out = root.resolve(), out.resolve()
    if out.is_relative_to(root) or root.is_relative_to(out):
        raise ValueError('Choose a disjoint fresh output directory')
    out.mkdir(parents=True, exist_ok=False)
    inventory = json.loads((root / 'MANIFIESTO_HASHES.json').read_bytes())
    for row in inventory['members']:
        path = safe(root, row['file'])
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Package input differs: ' + row['file'])
    plan = json.loads((root / 'RECALCULO/PLAN_GLOBAL.json').read_bytes())
    if not plan['jobs']:
        raise ValueError('No empty recalculation success')
    before = {row['file']: row['sha256'] for row in inventory['members']}
    results = []
    for number, job in enumerate(plan['jobs']):
        base = safe(root, job.get('base', '.'))
        script, expected = safe(base, job['script']), safe(base, job['expected'])
        if sha(script) != job['script_sha256'] or sha(expected) != job['expected_sha256']:
            raise ValueError('Job source/reference identity differs')
        output = out / (f'{number:02d}_' + job['id'] + '.json')
        command = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker', str(number),
                   '--root', str(root), '--out', str(out)]
        started = time.monotonic()
        completed = subprocess.run(command, cwd=tempfile.gettempdir(), capture_output=True,
                                   text=True, encoding='utf8', timeout=job.get('timeout_seconds', 180))
        comparison = job.get('comparison', 'bytes')
        identical = False
        if completed.returncode == 0 and output.is_file():
            if comparison == 'bytes':
                identical = output.read_bytes() == expected.read_bytes()
            elif comparison == 'json_values':
                identical = json.loads(output.read_bytes()) == json.loads(expected.read_bytes())
            else:
                raise ValueError('Unknown comparison; do not silently weaken the test')
        row = {'id': job['id'], 'command': command, 'exit_code': completed.returncode,
               'stdout': completed.stdout, 'stderr': completed.stderr, 'comparison': comparison,
               'matched': identical, 'expected_sha256': sha(expected),
               'actual_sha256': sha(output) if output.is_file() else None,
               'archived_calculation_wall_seconds': time.monotonic() - started}
        emit(out / (f'{number:02d}_RECIBO_' + job['id'] + '.json'), row)
        results.append(row)
        if not identical:
            raise ValueError('Archived CLI/reference mismatch: ' + job['id'])
    if any(sha(safe(root, name)) != digest for name, digest in before.items()):
        raise ValueError('Read-only package changed during recalculation')
    report = {'schema': 'APD04.archived_recalculation.actual_clis.R01', 'jobs': results,
              'jobs_completed': len(results), 'input_members_verified': len(before),
              'all_selected_calculations_match': all(r['matched'] for r in results),
              'new_native_ticks': 0, 'new_provider_calls': 0,
              'scope': 'Archived data only; not Native replay, another acquisition, Full use, or a scientific global PASS.'}
    emit(out / 'RESULTADO_GLOBAL.json', report)
    print(json.dumps({'out': str(out), 'jobs_completed': len(results), 'new_native_ticks': 0,
                      'scope': 'ARCHIVED_RECALCULATION_ONLY'}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--worker', type=int)
    args = parser.parse_args()
    if args.worker is not None:
        worker(args.root, args.worker, args.out)
    else:
        run(args.root, args.out)
