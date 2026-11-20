"""Verify one exact CPC9 ZIP in a NEW isolated, offline reconstruction.

This is an explicitly invoked new technical reproduction, not continuation of
the historical campaign budget. Outputs, venv and generated proofs stay outside
the archive. Historical/private filesystem reads are denied in Python children.
"""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import runpy
import re
import stat
import subprocess
import sys
import time
import traceback
import zipfile

WHL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHL_SHA = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA = '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
ROOT = Path(__file__).resolve().parents[1]
_JOB = None


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def windows_memory_limit(mib):
    """One process cap; preserve handle until exit. Nested jobs require Win8+."""
    global _JOB
    if os.name != 'nt':
        raise RuntimeError('Official instrument and this proof require Windows')
    import ctypes
    from ctypes import wintypes as w
    class Basic(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', ctypes.c_int64), ('PerJobUserTimeLimit', ctypes.c_int64),
                    ('LimitFlags', w.DWORD), ('MinimumWorkingSetSize', ctypes.c_size_t), ('MaximumWorkingSetSize', ctypes.c_size_t),
                    ('ActiveProcessLimit', w.DWORD), ('Affinity', ctypes.c_size_t), ('PriorityClass', w.DWORD), ('SchedulingClass', w.DWORD)]
    class IO(ctypes.Structure):
        _fields_ = [(x, ctypes.c_uint64) for x in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
    class Extended(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', Basic), ('IoInfo', IO), ('ProcessMemoryLimit', ctypes.c_size_t),
                    ('JobMemoryLimit', ctypes.c_size_t), ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.CreateJobObjectW.restype = w.HANDLE
    k.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
    k.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
    k.GetCurrentProcess.restype = w.HANDLE
    _JOB = k.CreateJobObjectW(None, None)
    limits = Extended()
    limits.BasicLimitInformation.LimitFlags = 0x100
    limits.ProcessMemoryLimit = mib * 1024 * 1024
    if not _JOB or not k.SetInformationJobObject(_JOB, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not k.AssignProcessToJobObject(_JOB, k.GetCurrentProcess()):
        raise OSError(ctypes.get_last_error(), 'Cannot enforce per-proof process memory budget')


def install_guard(work, log):
    """Audit Python filesystem operations, not a claim of full OS sandboxing."""
    base = Path(sys.base_prefix).resolve()
    allowed = [ROOT.resolve(), work.resolve(), Path(sys.prefix).resolve(), base / 'Lib', base / 'DLLs']
    if os.environ.get('SystemRoot'):
        allowed.append(Path(os.environ['SystemRoot']) / 'System32')
    exact = {Path(sys._base_executable).resolve(), Path(os.devnull).resolve()}
    denied = []
    guard_busy = False

    def audit(event, args):
        nonlocal guard_busy
        if guard_busy:
            return
        if event in ('socket.connect', 'socket.connect_ex', 'socket.bind', 'subprocess.Popen', 'os.system'):
            denied.append({'event': event, 'path': '<network or child process>'})
            raise PermissionError('Clean proof forbids network and nested processes')
        if event not in ('open', 'os.listdir', 'os.scandir', 'ctypes.dlopen') or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        raw = os.fsdecode(args[0])
        # Loading a named Windows DLL is normal; absolute paths still checked.
        if event == 'ctypes.dlopen' and not Path(raw).is_absolute():
            return
        guard_busy = True
        try:
            path = Path(raw).resolve()
            ok = path in exact or any(path.is_relative_to(q) for q in allowed)
            if event == 'open':
                mode = args[1] if len(args) > 1 else None
                flags = args[2] if len(args) > 2 else 0
                writing = (isinstance(mode, str) and any(x in mode for x in 'wax+')) or (
                    isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
                if writing and not path.is_relative_to(work) and not path.is_relative_to(ROOT / 'genealogia/code_by_hash') and path != Path(os.devnull).resolve():
                    ok = False
            # Base site-packages must not leak into the isolated environment.
            if path.is_relative_to(base / 'Lib' / 'site-packages') and not path.is_relative_to(Path(sys.prefix)):
                ok = False
            if not ok:
                denied.append({'event': event, 'path': str(path)})
                raise PermissionError('Private/historical path denied by clean proof: ' + str(path))
        finally:
            guard_busy = False
    sys.addaudithook(audit)
    return denied


def identity():
    import platform
    import dee_thinking
    from dee_thinking import _native as d
    extension = Path(d.__file__).resolve()
    build = d.build_info()
    value = {'python': sys.version, 'python_executable': sys.executable,
             'implementation': platform.python_implementation(), 'architecture': platform.architecture()[0],
             'module': str(Path(dee_thinking.__file__).resolve()), 'extension': str(extension),
             'extension_sha256': sha(extension), 'version': str(dee_thinking.__version__),
             'build_info': build, 'wheel_sha256': sha(ROOT / 'runtime' / WHL)}
    if sys.version_info[:2] != (3, 13) or platform.architecture()[0] != '64bit' or value['version'] != '4.5.0':
        raise RuntimeError('Wrong interpreter/platform/product')
    if value['wheel_sha256'] != WHL_SHA or value['extension_sha256'] != PYD_SHA:
        raise RuntimeError('Instrument identity mismatch')
    if KERNEL_SHA not in json.dumps(build):
        raise RuntimeError('Kernel identity not provided by installed build_info')
    if not extension.is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError('Extension did not import from fresh environment')
    return value


def signature(session):
    from integracion.relational_pair import physical
    return {'physical': physical(session.world), 'receipts': session.receipts(), 'view': session.view()}


def later_interaction(session):
    # Current native inputs on declared interfaces; no correct output is injected.
    for item in session.geometry['joint_names'].values():
        session.input(item['query_port'], 17, 680, 'probe', 'CLEAN_POST_RESTORE_NEW_QUERY')
    session.input('extra.signal', 9, 620, origin='CLEAN_NEW_CURRENT_EXPERIENCE')
    session.run_until(683)
    result = signature(session)
    result['new_interaction_receipts'] = [r for r in result['receipts'] if r.get('origin') in ('CLEAN_POST_RESTORE_NEW_QUERY', 'CLEAN_NEW_CURRENT_EXPERIENCE')]
    result['at_least_one_new_input_applied'] = any(r.get('receipt', {}).get('status') == 'applied' for r in result['new_interaction_receipts'])
    if not result['at_least_one_new_input_applied']:
        raise AssertionError('No newly requested physical input was applied after restoration boundary')
    return result


def integral_chain(work):
    """Fresh T0 lineage; only regenerated snapshot parents, no original state.

Frozen primary outputs are read by this auditor ONLY AFTER all seven native
segments finish. Their values never determine inputs or select a branch.
"""
    import gc
    base = work / 'integral_chain'
    base.mkdir(exist_ok=False)
    plan = [
        ('0_884', 'src/ejecutar_vida_integral.py', 'resultados/vida_integral/EI_D01', 884,
         ['--case', 'EI_D01', '--until', '884']),
        ('884_1220', 'src/continuar_e1.py', 'resultados/continuacion/E1_MAIN_884_1220', 1220,
         ['--case', 'E1_MAIN_884_1220']),
        ('1220_1371', 'front_relations/src/continuar_main_social.py', 'front_relations/resultados/E1_MAIN_1220_1371', 1371,
         ['--case', 'E1_MAIN_1220_1371', '--config', str(ROOT / 'front_relations/configuraciones/MAIN_SOCIAL_1220_1371_FROZEN.json')]),
        ('1371_1639', 'front_relations/src/continuar_main_social2.py', 'front_relations/resultados/E1_MAIN_1371_1639', 1639,
         ['--case', 'E1_MAIN_1371_1639', '--config', str(ROOT / 'front_relations/configuraciones/MAIN_SOCIAL_1371_1639_FROZEN.json')]),
        ('1639_1907', 'front_relations/src/continuar_main_noform.py', 'front_relations/resultados/E1_MAIN_1639_1907', 1907,
         ['--case', 'E1_MAIN_1639_1907', '--config', str(ROOT / 'front_relations/configuraciones/MAIN_NOFORM_1639_1907_FROZEN.json')]),
        ('1907_2353', 'src/continuar_repertorio_e1.py', 'resultados/continuacion/E1_MAIN_K65_1907_2353', 2353,
         ['--case', 'E1_MAIN_K65_1907_2353']),
        ('2353_2493', 'src/continuar_e1_tail.py', 'resultados/continuacion/E1_MAIN_TAIL_2353_2493', 2493, []),
    ]
    executions = []
    parent = None
    # No primary expected target/measurement is read in this execution loop.
    for name, script, reference, boundary, flags in plan:
        out = base / name
        args = [str(ROOT / script), '--out', str(out), *flags]
        if parent is not None:
            if not parent.is_relative_to(base) or not parent.is_file():
                raise ValueError('Only newly regenerated parents are permitted')
            args.extend(['--parent', str(parent)])
        sys.argv = args
        started = time.monotonic()
        try:
            runpy.run_path(str(ROOT / script), run_name='__main__')
        except SystemExit as e:
            if e.code not in (None, 0):
                raise
        executions.append({'segment': name, 'source': script, 'arguments': args,
                           'boundary': boundary, 'elapsed_seconds': time.monotonic() - started})
        parent = out / ('T' + str(boundary) + '.deetsnap.gz')
        gc.collect()
    # Auditor-only readback after the complete trajectory.
    rows = []
    for (name, script, reference, boundary, flags), execution in zip(plan, executions):
        actual_path = base / name / 'MEDICIONES.json'
        expected_path = ROOT / reference / 'MEDICIONES.json'
        actual, expected = load(actual_path), load(expected_path)
        checks = {'status': actual['status'] == expected['status'] == 'MEASURED',
                  'final_physical': actual['final_physical'] == expected['final_physical'],
                  'all_frames': actual['frames'] == expected['frames'],
                  'all_requests_and_receipts': actual['requests'] == expected['requests']}
        if 'initial_physical' in expected:
            checks['initial_physical'] = actual['initial_physical'] == expected['initial_physical']
        row = execution | {'primary_reference': reference + '/MEDICIONES.json',
                           'primary_sha256': sha(expected_path), 'reproduced_sha256': sha(actual_path),
                           'comparisons': checks, 'final_physical': actual['final_physical'],
                           'frames': len(actual['frames']), 'requests': len(actual['requests'])}
        rows.append(row)
        if not all(checks.values()):
            dump(work / 'integral_chain_partial_comparison.json', {'segments': rows, 'status': 'FAILED'})
            raise AssertionError('Fresh integral lineage differs at segment ' + name)
        del actual, expected
        gc.collect()
    return {'segments': rows, 'seven_boundaries_exact': all(all(x['comparisons'].values()) for x in rows),
            'lineage': 'Fresh T0 to2493; seven existing CLI phases, newly regenerated parents only.',
            'expected_measurements_read_after_complete_trajectory': True,
            'original_snapshots_used_as_parents': False,
            'architecture_note': 'Includes only originally declared external interface additions at1220/1907, no RAW/clock editing or hidden growth.'}


def child(a):
    started = time.monotonic()
    work = a.work.resolve(strict=True)
    windows_memory_limit(a.memory_mib)
    sys.path[:0] = [str(ROOT), str(ROOT / 'src'), str(ROOT / 'base_validada/cpc8/src'),
                   str(ROOT / 'front_relations/src'), str(ROOT / 'front_semantics/src')]
    denied = install_guard(work, a.report)
    result = {'schema': 'CPC9.clean.proof.v1', 'proof': a.child, 'status': 'RUNNING',
              'process_memory_limit_bytes': a.memory_mib * 1024 * 1024}
    try:
        result['identity'] = identity()
        if a.child == 'parser':
            import unittest
            suite = unittest.defaultTestLoader.discover(str(ROOT / 'app'), pattern='test_contract.py', top_level_dir=str(ROOT))
            run = unittest.TextTestRunner(verbosity=2).run(suite)
            result.update(tests=run.testsRun, failures=len(run.failures), errors=len(run.errors))
            if not run.wasSuccessful() or run.testsRun < 5:
                raise AssertionError('Parser contract proof failed or incomplete')
        elif a.child in ('demo', 'control'):
            sys.argv = [str(ROOT / 'ejecutar.py'), 'demo', '--until', '606', '--out', str(work / a.child),
                        '--ascii-temp', str(work / 'tmp'), '--quiet']
            if a.child == 'control':
                sys.argv.append('--control-no-order-a')
            try:
                runpy.run_path(str(ROOT / 'ejecutar.py'), run_name='__main__')
            except SystemExit as e:
                if e.code not in (None, 0):
                    raise
            summary = load(work / a.child / 'RESUMEN_EJECUCION.json')
            result['summary'] = summary
            if summary.get('instrument_errors', 0):
                raise AssertionError('App returned event errors')
        elif a.child == 'reference-baseline':
            from transferencia_magnitud.cts_integrado import MagnitudeCTSSession
            s = MagnitudeCTSSession.create(identifier='CLEAN_LEGACY_MCTS')
            s.curriculum()
            s.run_until(343)
            result['saved'] = signature(s)
            s.save(work / 'MCTS_T343.deetsnap.gz')
            s.run_until(616)
            result['reference'] = signature(s)
            result['later'] = later_interaction(s)
            # This is a validation fixture, not participant information.
            observation = result['reference']['view']['joint']['plus.changed']['delivery_site']
            result['positive_reference_observation'] = observation
            if int(observation['s_reg']) != 115:
                raise AssertionError('Preserved MCTS reference no longer produces published load115')
        elif a.child == 'reference-restored':
            from transferencia_magnitud.cts_integrado import MagnitudeCTSSession
            s = MagnitudeCTSSession.load(work / 'MCTS_T343.deetsnap.gz')
            result['saved'] = signature(s)
            s.run_until(616)
            result['reference'] = signature(s)
            result['later'] = later_interaction(s)
            baseline = load(work / 'proof_reference-baseline.json')
            result['comparisons'] = {k: result[k] == baseline[k] for k in ('saved', 'reference', 'later')}
            if not all(result['comparisons'].values()):
                raise AssertionError('Restored physical/operational state or later interaction diverged')
        elif a.child == 'integral':
            result['integral_chain'] = integral_chain(work)
        elif a.child == 'recalculate':
            out = work / 'CALCULOS_RECALCULADOS.json'
            sys.argv = [str(ROOT / 'tools/recalcular_cpc9.py'), '--out', str(out)]
            runpy.run_path(str(ROOT / 'tools/recalcular_cpc9.py'), run_name='__main__')
            result['matches_frozen_calculations'] = load(out) == load(ROOT / 'revision/CALCULOS.json')
            result['recalculated_sha256'] = sha(out)
            if not result['matches_frozen_calculations']:
                raise AssertionError('Primary-data recalculation differs from sealed calculation')
        else:
            raise ValueError('Unknown proof')
        result['status'] = 'PASSED'
    except BaseException as e:
        result.update(status='FAILED', error=repr(e), traceback=traceback.format_exc())
    finally:
        result.update(elapsed_seconds=time.monotonic() - started, denied_operations=denied,
                      audit_scope='Python open/listdir/scandir/ctypes.dlopen, network and child-process events. Not an OS-level proof of every native syscall.')
        dump(a.report, result)
    return 0 if result['status'] == 'PASSED' and not denied else 1


def verify_members(root, manifest):
    bad = []
    paths = set()
    for row in manifest['files']:
        rel = Path(row['path'])
        if rel.is_absolute() or '..' in rel.parts or '\\' in row['path'] or ':' in row['path'] or row['path'].casefold() in paths:
            raise ValueError('Unsafe or duplicate manifest path: ' + row['path'])
        paths.add(row['path'].casefold())
        path = root / row['path']
        if not path.is_file() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            bad.append(row['path'])
    return bad


def static_private_path_check(root):
    """Active participant/app trees only; documentary genealogy is not imported."""
    checked = []
    findings = []
    folders = ('src', 'app', 'base_validada/cpc8/src', 'front_relations/src', 'front_semantics/src')
    groups = [sorted((root / folder).rglob('*.py')) for folder in folders]
    groups.append(sorted((root / 'front_semantics').glob('*.py')))
    for paths in groups:
        for path in paths:
            checked.append(path.relative_to(root).as_posix())
            tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.match(r'^[A-Za-z]:[\\/]', node.value):
                    findings.append({'path': path.relative_to(root).as_posix(), 'line': node.lineno, 'literal': node.value})
    return {'checked_python_files': checked, 'absolute_windows_path_literals': findings,
            'scope': 'AST string literals in active sources, plus runtime Python audit. Documentary provenance may contain historical absolute paths; that is not an operational dependency.',
            'native_io_scope': 'Snapshot filenames are explicitly supplied under clean work. Python audit does not intercept every possible C++/OS syscall.'}


def safe_extract(archive_path, destination):
    names = set()
    with zipfile.ZipFile(archive_path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError('ZIP CRC failed: ' + bad)
        for entry in archive.infolist():
            rel = Path(entry.filename)
            if '\\' in entry.filename or rel.is_absolute() or '..' in rel.parts or not entry.filename.startswith('CPC9/'):
                raise ValueError('Unsafe/unexpected ZIP path: ' + entry.filename)
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('ZIP symlink forbidden')
            key = entry.filename.casefold().rstrip('/')
            if key in names:
                raise ValueError('Duplicate/case-colliding ZIP member')
            names.add(key)
        archive.extractall(destination)
    return len(names)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip', type=Path)
    p.add_argument('--work', required=True, type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--base-python', type=Path, default=Path(sys._base_executable))
    p.add_argument('--budget-seconds', type=int, default=2700)
    p.add_argument('--memory-mib', type=int, default=512)
    p.add_argument('--child', choices=['parser', 'demo', 'control', 'reference-baseline', 'reference-restored', 'integral', 'recalculate'])
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    if not 120 <= a.budget_seconds <= 21600 or not 256 <= a.memory_mib <= 1024:
        p.error('Finite budget120..21600 seconds and per-process memory256..1024MiB required')
    if a.child:
        if a.report is None:
            p.error('--child requires --report')
        return child(a)
    if a.zip is None or a.out is None:
        p.error('--zip and --out required')
    if a.work.exists() or a.out.exists():
        raise FileExistsError('Use a NEW work directory and NEW external report')
    if not str(a.work.resolve()).isascii():
        raise ValueError('Clean work path must contain only ASCII characters')
    source = a.zip.resolve(strict=True)
    work = a.work.resolve()
    a.out = a.out.resolve()
    if a.out.is_relative_to(work / 'extracted'):
        raise ValueError('Verification receipt must be outside extracted container')
    work.mkdir(parents=True)
    started = time.monotonic()
    deadline = started + a.budget_seconds
    result = {'schema': 'CPC9.final.external.verification.v1', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'zip_name': source.name, 'zip_sha256': sha(source), 'compressed_bytes': source.stat().st_size,
              'new_explicit_budget_seconds': a.budget_seconds, 'per_process_memory_limit_bytes': a.memory_mib * 1024 * 1024,
              'work': str(work), 'status': 'RUNNING', 'commands': [], 'proofs': [],
              'historical_campaign_budget_unchanged': True, 'scientific_new_replica_claim': False}
    child_env = os.environ.copy()
    child_env.pop('PYTHONPATH', None)
    child_env.pop('PYTHONHOME', None)
    (work / 'tmp').mkdir()
    child_env.update(TEMP=str(work / 'tmp'), TMP=str(work / 'tmp'), PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1', PYTHONNOUSERSITE='1')

    def command(args, label, limit=900):
        remaining = deadline - time.monotonic() - 10
        if remaining <= 0:
            raise TimeoutError('Explicit clean-reproduction budget exhausted')
        t = time.monotonic()
        entry = {'label': label, 'command': [str(x) for x in args]}
        result['commands'].append(entry)
        try:
            completed = subprocess.run([str(x) for x in args], cwd=work, env=child_env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=min(limit, remaining), text=True, encoding='utf-8', errors='replace')
            entry.update(exit_code=completed.returncode, elapsed_seconds=time.monotonic() - t)
            (work / (label + '.log')).write_text(completed.stdout, encoding='utf-8')
            entry['log'] = str(work / (label + '.log'))
            if completed.returncode:
                raise RuntimeError('Clean command failed: ' + label)
        except subprocess.TimeoutExpired as e:
            entry.update(status='TIMEOUT', elapsed_seconds=time.monotonic() - t)
            raise TimeoutError('Clean command timed out: ' + label) from e
        dump(a.out, result)

    try:
        extracted = work / 'extracted'
        result['members'] = safe_extract(source, extracted)
        root = extracted / 'CPC9'
        manifest = load(root / 'MANIFEST.json')
        result['expanded_bytes'] = sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
        result['manifest_failures_before'] = verify_members(root, manifest)
        if result['manifest_failures_before']:
            raise ValueError('Manifest mismatch before proof')
        hashes = {}
        for line in (root / 'HASHES.sha256').read_text(encoding='utf-8').splitlines():
            digest, rel = line.split('  ', 1)
            if Path(rel).is_absolute() or '..' in Path(rel).parts or '\\' in rel or ':' in rel or rel in hashes or sha(root / rel) != digest:
                raise ValueError('HASHES mismatch or unsafe path: ' + rel)
            hashes[rel] = digest
        result['hash_index_entries_verified'] = len(hashes)
        if hashes.get('MANIFEST.json') != sha(root / 'MANIFEST.json') or set(hashes) != {x['path'] for x in manifest['files']} | {'MANIFEST.json'}:
            raise ValueError('Hash index does not cover exactly the scientific payload/manifest')
        result['private_path_check'] = static_private_path_check(root)
        if result['private_path_check']['absolute_windows_path_literals']:
            raise ValueError('Review absolute path literals in active code before declaring clean reconstruction')
        wheel = root / 'runtime' / WHL
        result['wheel_sha256'] = sha(wheel)
        if result['wheel_sha256'] != WHL_SHA:
            raise ValueError('Wrong wheel in exact ZIP')
        result['kernel_source_sha256'] = sha(root / 'genealogia/kernel_v27.cpp')
        if result['kernel_source_sha256'] != KERNEL_SHA:
            raise ValueError('Kernel source mismatch')
        venv = work / 'env'
        command([a.base_python, '-I', '-B', '-X', 'utf8', '-m', 'venv', str(venv)], 'create_env', 180)
        python = venv / 'Scripts/python.exe'
        command([python, '-I', '-B', '-X', 'utf8', '-m', 'pip', 'install', '--no-index', '--no-deps', '--disable-pip-version-check', str(wheel)], 'offline_install', 180)
        for name in ('parser', 'demo', 'control', 'reference-baseline', 'reference-restored', 'integral', 'recalculate'):
            report = work / ('proof_' + name + '.json')
            command([python, '-I', '-B', '-X', 'utf8', root / 'tools/verify_cpc9_clean.py',
                     '--child', name, '--work', work, '--report', report, '--memory-mib', str(a.memory_mib)], name)
            proof = load(report)
            result['proofs'].append(proof)
            if proof['status'] != 'PASSED' or proof['denied_operations']:
                raise RuntimeError('Proof failed: ' + name)
        # The demo and matched no-A control must actually differ physically.
        demos = {x['proof']: x for x in result['proofs'] if x['proof'] in ('demo', 'control')}
        result['demo_control_summaries_differ'] = demos['demo']['summary'].get('physical') != demos['control']['summary'].get('physical')
        if not result['demo_control_summaries_differ']:
            raise AssertionError('Matched causal control has no physical distinction')
        result['manifest_failures_after'] = verify_members(root, manifest)
        if result['manifest_failures_after']:
            raise ValueError('A sealed payload member was modified during clean proof')
        result['new_extraction_files'] = [x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file() and x.relative_to(root).as_posix() not in hashes and x.name != 'HASHES.sha256']
        result['zip_sha256_after'] = sha(source)
        if result['zip_sha256_after'] != result['zip_sha256']:
            raise ValueError('Canonical ZIP changed during verification')
        result['status'] = 'VERIFIED_EXACT_ZIP'
    except BaseException as e:
        result.update(status='NOT_VERIFIED', error=repr(e), traceback=traceback.format_exc())
    finally:
        result.update(elapsed_seconds=time.monotonic() - started, remaining_seconds=max(0, deadline - time.monotonic()),
            closed_utc=datetime.now(timezone.utc).isoformat(),
            scope='Finite technical reproduction of listed contracts, not proof of all possible DEE states or NSM65 mastery.')
        dump(a.out, result)
    print(json.dumps({'status': result['status'], 'zip_sha256': result['zip_sha256'], 'receipt': str(a.out)}))
    return 0 if result['status'] == 'VERIFIED_EXACT_ZIP' else 1


if __name__ == '__main__':
    raise SystemExit(main())
