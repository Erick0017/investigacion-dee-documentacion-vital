"""Seal and verify a private DEE thinking 4.5.0 delivery; publication is separate.

No compilation, scientific runner, historical archive or cleanup is invoked.
MANIFEST paths are relative to DEE_thinking_4_5_0/. ZIP identity stays outside it.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from email.parser import BytesParser
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = 'DEE_thinking_4_5_0'
NAME = 'DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip'
WHEEL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
BLOCK = 4 * 1024 * 1024
THRESHOLD = 20 * 1024 * 1024
SUPERVISOR_SHA = 'c3fb4f02f75debb381e9814d56b10ddeb53ea7443ab6d5627ba77cce9745283f'
TOP_DIRS = {'source', 'src', 'tools', 'validation', 'evidence', 'revision', 'examples', 'tests', 'docs'}
SOURCE_DIRS = {'include', 'src', 'bindings', 'python', 'cmake', 'tests', 'examples', 'fixtures', 'tools', 'benchmarks'}
EXCLUDED_DIRS = {'build', 'dist', '__pycache__', '.git', '.pytest_cache', '.mypy_cache', 'node_modules', '_delivery', '_distribution', '.venv', 'venv'}
FORBIDDEN_EXTENSIONS = {'.zip', '.001', '.002', '.pdb', '.obj', '.pyc', '.docx', '.ttf', '.otf'}
VIRTUAL = {'MANIFEST.json', 'HASHES.sha256', 'PACKAGING_SELECTION.json', 'RELEASE_IDENTITY.json'}


def sha_stream(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(BLOCK), b''):
        result.update(block)
    return result.hexdigest()


def sha(path):
    with Path(path).open('rb') as stream:
        return sha_stream(stream)


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def put(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending.' + str(os.getpid()))
    temporary.write_bytes(json_bytes(data))
    os.replace(temporary, path)


def safe_name(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or p.as_posix() != name or any(c in name for c in ('\\', '\x00', '\n', '\r')):
        raise ValueError('Noncanonical relative path: ' + repr(name))
    if any(part in {'', '.', '..'} or ':' in part for part in p.parts):
        raise ValueError(name)
    return p


def excluded(relative):
    return any(part in EXCLUDED_DIRS or part.startswith(('.venv', '.tmp-', 'cmake-build-', 'build.')) or part.endswith('.egg-info')
               for part in relative.parts)


def selection(product_root):
    """Positive scope; every omitted file is recorded, not silently discarded."""
    product_root = Path(product_root).resolve()
    files = {}
    omitted = []

    def add(path, relative, origin):
        relative = safe_name(relative).as_posix()
        if path.is_symlink():
            raise ValueError('No symlinks: ' + str(path))
        if relative in VIRTUAL:
            omitted.append({'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name, 'reason': 'virtual manifest regenerated'})
            return
        if relative in files:
            if sha(files[relative]['source']) != sha(path):
                raise ValueError('Different inputs collide at ' + relative)
            return
        files[relative] = {'source': path, 'origin': origin}

    for directory in sorted(TOP_DIRS):
        base = ROOT / directory
        if not base.is_dir():
            continue
        for parent, dirs, names in os.walk(base):
            parent = Path(parent)
            retained = []
            for name in sorted(dirs):
                relative = (parent / name).relative_to(ROOT)
                if excluded(relative) or (directory == 'source' and parent == base and name not in SOURCE_DIRS):
                    omitted.append({'path': relative.as_posix() + '/', 'reason': 'build/cache/unselected source subtree'})
                else:
                    retained.append(name)
            dirs[:] = retained
            for name in sorted(names):
                path = parent / name
                relative = path.relative_to(ROOT)
                if excluded(relative) or path.suffix.lower() in FORBIDDEN_EXTENSIONS or name.endswith(('.pending', '.candidate.zip')):
                    omitted.append({'path': relative.as_posix(), 'reason': 'cache, generated binary, historical archive or unrequested document'})
                    continue
                add(path, relative.as_posix(), 'workspace')
    for path in sorted(ROOT.iterdir()):
        if path.is_file() and path.suffix.lower() in {'.json', '.md', '.txt', '.ps1', '.py', '.toml'}:
            add(path, path.name, 'workspace-root')
    # Preserve every bounded job status and adverse log. Build stdout is also
    # evidence, not a native build tree. No job executables/venvs are selected.
    jobs = ROOT / 'jobs'
    if jobs.is_dir():
        for path in sorted(jobs.rglob('*')):
            if path.is_file() and path.suffix.lower() in {'.json', '.log', '.txt'} and not excluded(path.relative_to(ROOT)):
                add(path, path.relative_to(ROOT).as_posix(), 'job-provenance')
    for directory in ('wheel', 'install_cpp'):
        base = product_root / directory
        if not base.is_dir():
            raise FileNotFoundError(base)
        for path in sorted(base.rglob('*')):
            if path.is_file() and not excluded(path.relative_to(base)):
                add(path, directory + '/' + path.relative_to(base).as_posix(), 'compiled-product')
    for path in sorted(product_root.glob('BUILD_*.json')):
        add(path, 'validation/build/' + path.name, 'compiled-product')
    val = product_root / 'validation'
    if val.is_dir():
        for path in sorted(val.rglob('*')):
            if path.is_file() and not excluded(path.relative_to(val)):
                add(path, 'validation/native-build/' + path.relative_to(val).as_posix(), 'compiled-product')
    lowered = [name.casefold() for name in files]
    if len(lowered) != len(set(lowered)):
        raise ValueError('Case-insensitive Windows path collision')
    return files, omitted


def wheel_identity(data):
    with zipfile.ZipFile(io.BytesIO(data)) as wheel:
        if wheel.testzip() is not None:
            raise ValueError('Wheel CRC failure')
        names = wheel.namelist()
        metadata = [n for n in names if n.endswith('.dist-info/METADATA')]
        native = [n for n in names if n.startswith('dee_thinking/') and n.endswith('.pyd')]
        if len(metadata) != 1 or len(native) != 1:
            raise ValueError('Expected one native PYD and one METADATA')
        metadata_fields = BytesParser().parsebytes(wheel.read(metadata[0]), headersonly=True)
        if metadata_fields.get_all('Version') != ['4.5.0']:
            raise ValueError('Wheel metadata is not 4.5.0')
        if 'dee_thinking-4.5.0.dist-info/WHEEL' not in names:
            raise ValueError('Wrong dist-info version')
        wheel_fields = BytesParser().parsebytes(wheel.read('dee_thinking-4.5.0.dist-info/WHEEL'), headersonly=True)
        if wheel_fields.get_all('Tag') != ['cp313-cp313-win_amd64']:
            raise ValueError('Wrong wheel platform tag')
        return {'version': '4.5.0', 'wheel_name': WHEEL, 'wheel_sha256': hashlib.sha256(data).hexdigest(),
                'wheel_bytes': len(data), 'native_member': native[0], 'native_sha256': hashlib.sha256(wheel.read(native[0])).hexdigest(),
                'kernel_source_sha256': KERNEL_SHA, 'kernel_version': 27, 'metadata_member': metadata[0]}


def build(product_root, output, report, require_final=False):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(output)
    files, omitted = selection(product_root)
    needed = {'source/src/kernel_v27.cpp', 'source/CMakeLists.txt', 'source/setup.py', 'source/pyproject.toml', 'wheel/' + WHEEL}
    if require_final:
        needed |= {'README.md', 'PRODUCT_CONTRACT.json', 'VALIDATION_REPORT.json', 'CLEAN_PLAN.json'}
    if not needed.issubset(files):
        raise ValueError('Missing mandatory payload: ' + repr(sorted(needed - files.keys())))
    if sha(files['source/src/kernel_v27.cpp']['source']) != KERNEL_SHA:
        raise ValueError('Kernel source changed')
    whls = [name for name in files if name.startswith('wheel/') and name.endswith('.whl')]
    if whls != ['wheel/' + WHEEL]:
        raise ValueError('Exactly one final 4.5 wheel is required: ' + repr(whls))
    identity = wheel_identity(files['wheel/' + WHEEL]['source'].read_bytes())
    rows = []
    for name, item in sorted(files.items()):
        rows.append({'path': name, 'bytes': item['source'].stat().st_size, 'sha256': sha(item['source']), 'origin': item['origin']})
    selected = {'schema': 'DEE45.selection.v1', 'files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'omissions': omitted,
                'scope': 'Private reconstruction; historical archives and all build/cache/venv/toolchain trees omitted. Job status and adverse logs retained.'}
    virtual = {'PACKAGING_SELECTION.json': json_bytes(selected), 'RELEASE_IDENTITY.json': json_bytes(identity)}
    manifest_rows = [{k: r[k] for k in ('path', 'bytes', 'sha256')} for r in rows]
    manifest_rows += [{'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, data in sorted(virtual.items())]
    manifest = {'schema': 'DEE45.manifest.v1', 'archive_root': ARCHIVE_ROOT,
                'scope': 'All regular payload files except MANIFEST.json and HASHES.sha256; hashes are relative to archive_root.',
                'files': sorted(manifest_rows, key=lambda r: r['path'])}
    virtual['MANIFEST.json'] = json_bytes(manifest)
    hash_rows = [(r['path'], r['sha256']) for r in manifest_rows]
    hash_rows.append(('MANIFEST.json', hashlib.sha256(virtual['MANIFEST.json']).hexdigest()))
    virtual['HASHES.sha256'] = ''.join(digest + '  ' + name + '\n' for name, digest in sorted(hash_rows)).encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + '.pending.' + str(os.getpid()))
    try:
        with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for row in rows:
                source = files[row['path']]['source']
                info = zipfile.ZipInfo(ARCHIVE_ROOT + '/' + row['path'], (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                with source.open('rb') as input_stream, archive.open(info, 'w', force_zip64=True) as target:
                    h = hashlib.sha256()
                    count = 0
                    for block in iter(lambda: input_stream.read(BLOCK), b''):
                        target.write(block); h.update(block); count += len(block)
                if h.hexdigest() != row['sha256'] or count != row['bytes']:
                    raise RuntimeError('Source changed while sealing: ' + row['path'])
            for name, data in sorted(virtual.items()):
                info = zipfile.ZipInfo(ARCHIVE_ROOT + '/' + name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, data)
        os.rename(temporary, output)
        result = verify(output)
        result['selection'] = {'files': len(rows), 'omissions': len(omitted), 'by_top_level': dict(Counter(r['path'].split('/')[0] for r in rows))}
        result['final_required'] = require_final
        put(report, result)
        return result
    except BaseException as exc:
        put(report, {'status': 'FAILED', 'error': repr(exc), 'candidate': str(output), 'temporary_preserved': str(temporary)})
        raise


def verify(path):
    path = Path(path)
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(n.casefold() for n in names)):
            raise ValueError('Duplicate or case-colliding ZIP paths')
        for info in infos:
            rel = safe_name(info.filename)
            if rel.parts[0] != ARCHIVE_ROOT or info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('Unexpected archive member: ' + info.filename)
        if archive.testzip() is not None:
            raise ValueError('ZIP CRC failure')
        prefix = ARCHIVE_ROOT + '/'
        manifest = json.loads(archive.read(prefix + 'MANIFEST.json'))
        if manifest['schema'] != 'DEE45.manifest.v1' or manifest['archive_root'] != ARCHIVE_ROOT:
            raise ValueError('Wrong manifest root')
        records = manifest['files']
        expected = {prefix + r['path'] for r in records} | {prefix + 'MANIFEST.json', prefix + 'HASHES.sha256'}
        if set(names) != expected or len(records) != len({r['path'] for r in records}):
            raise ValueError('Manifest/member set mismatch')
        for row in records:
            safe_name(row['path'])
            info = archive.getinfo(prefix + row['path'])
            with archive.open(info) as stream:
                actual = sha_stream(stream)
            if info.file_size != row['bytes'] or actual != row['sha256']:
                raise ValueError('Manifest failed: ' + row['path'])
        hashes = archive.read(prefix + 'HASHES.sha256').decode('utf-8').splitlines()
        wanted = {r['path']: r['sha256'] for r in records}
        wanted['MANIFEST.json'] = hashlib.sha256(archive.read(prefix + 'MANIFEST.json')).hexdigest()
        observed = {}
        for line in hashes:
            digest, name = line.split('  ', 1); safe_name(name)
            if name in observed:
                raise ValueError('Repeated hash path')
            observed[name] = digest
        if observed != wanted:
            raise ValueError('HASHES.sha256 scope/value mismatch')
        if hashlib.sha256(archive.read(prefix + 'source/src/kernel_v27.cpp')).hexdigest() != KERNEL_SHA:
            raise ValueError('Kernel mismatch')
        identity = wheel_identity(archive.read(prefix + 'wheel/' + WHEEL))
        if identity != json.loads(archive.read(prefix + 'RELEASE_IDENTITY.json')):
            raise ValueError('Release identity mismatch')
        return {'schema': 'DEE45.container-proof.v1', 'status': 'VERIFIED', 'candidate': str(path.resolve()), 'sha256': sha(path),
                'bytes': path.stat().st_size, 'expanded_bytes': sum(i.file_size for i in infos), 'members': len(infos),
                'hashes_verified': len(wanted), 'crc': 'PASS', 'kernel': 'UNCHANGED', 'identity': identity,
                'completed_utc': datetime.now(timezone.utc).isoformat()}


def check_protected():
    refs = ROOT / 'evidence/REFERENCES.json'
    base = ROOT.parents[2]
    result = []
    for row in json.loads(refs.read_text(encoding='utf-8-sig')):
        path = base / ('4.0' if row['id'] in {'PRODUCT40', 'WHEEL40'} else 'casos practicos') / row['name']
        observed = sha(path)
        if observed != row['sha256'] or path.stat().st_size != row['bytes']:
            raise ValueError('Protected artifact changed: ' + str(path))
        result.append({'id': row['id'], 'sha256': observed, 'bytes': row['bytes'], 'unchanged': True})
    return result


def split(path, output_dir):
    path = Path(path).resolve(); output_dir = Path(output_dir).resolve()
    if path.stat().st_size <= THRESHOLD:
        return {'required': False, 'threshold_bytes': THRESHOLD, 'zip_bytes': path.stat().st_size, 'parts': []}
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = [output_dir / (path.name + suffix) for suffix in ('.001', '.002')]
    targets += [output_dir / name for name in ('PARTES.json', 'REUNIR_4_5.py', 'INSTRUCCIONES_PARTES.txt')]
    if any(target.exists() for target in targets):
        raise FileExistsError('Existing transport files preserved: ' + repr([str(p) for p in targets if p.exists()]))
    sizes = [(path.stat().st_size + 1) // 2, path.stat().st_size // 2]
    rows = []
    with path.open('rb') as source:
        for index, size in enumerate(sizes, 1):
            part = output_dir / (path.name + f'.{index:03d}')
            if part.exists():
                raise FileExistsError(part)
            h = hashlib.sha256(); remaining_bytes = size
            temporary = part.with_name(part.name + '.pending.' + str(os.getpid()))
            with temporary.open('xb') as target:
                while remaining_bytes:
                    block = source.read(min(BLOCK, remaining_bytes))
                    if not block:
                        raise EOFError('Unexpected source EOF')
                    target.write(block); h.update(block); remaining_bytes -= len(block)
            os.rename(temporary, part)
            rows.append({'order': index, 'name': part.name, 'bytes': size, 'sha256': h.hexdigest()})
        if source.read(1):
            raise ValueError('Unexpected source bytes')
    metadata = {'schema': 'DEE45.binary-parts.v1', 'zip_name': path.name, 'zip_bytes': path.stat().st_size,
                'zip_sha256': sha(path), 'parts': rows, 'parts_directory': '.', 'threshold_bytes': THRESHOLD}
    meta = output_dir / 'PARTES.json'
    if meta.exists():
        raise FileExistsError(meta)
    put(meta, metadata)
    helper = output_dir / 'REUNIR_4_5.py'
    if helper.exists():
        raise FileExistsError(helper)
    shutil.copyfile(ROOT / 'tools/reunir45.py', helper)
    from reunir45 import join
    with tempfile.TemporaryDirectory(prefix='dee45_join_') as temp:
        reconstructed = join(meta, Path(temp) / path.name)
        with zipfile.ZipFile(reconstructed['output']) as archive:
            if archive.testzip() is not None:
                raise ValueError('Reconstructed ZIP CRC failed')
    instructions = output_dir / 'INSTRUCCIONES_PARTES.txt'
    if instructions.exists():
        raise FileExistsError(instructions)
    instructions.write_text('Las partes son bytes secuenciales, no dos ZIP independientes.\nConserve .001, .002, PARTES.json y REUNIR_4_5.py en la misma carpeta.\nEjecute: python REUNIR_4_5.py\nEl programa verifica ambas partes, reúne por bloques y protege archivos existentes.\nEl ZIP canónico completo también se conserva.\n', encoding='utf-8')
    return dict(metadata, required=True, real_reconstruction_verified=True, reconstructed_crc='PASS')


def assess_current_pid(observation, ledger_mtime_ns):
    """PID observations cannot replace the original process's wait/close proof."""
    kind = observation['kind']
    if kind == 'DENIED':
        return {'observation': 'PID_DENIED', 'current_process_unknown': True,
                'scope': 'Access denied. No assertion that a current process exists, is absent or is the original campaign worker.'}
    if kind == 'ABSENT':
        return {'observation': 'PID_NOT_PRESENT_AT_QUERY', 'current_process_unknown': False}
    if kind == 'EXITED':
        return {'observation': 'PID_HANDLE_EXITED', 'current_process_unknown': False}
    if kind == 'ACTIVE':
        if observation['creation_unix_ns'] > ledger_mtime_ns:
            return {'observation': 'PID_REUSED_AFTER_LEDGER_COMPLETION', 'current_process_unknown': False,
                    'creation_unix_ns': observation['creation_unix_ns'],
                    'scope': 'Current PID generation was created after the original worker completion ledger; not a campaign worker.'}
        raise RuntimeError('An accessible live PID cannot be separated from the original campaign worker')
    raise ValueError('Unknown PID observation')


def validate_worker_ledger(row, ledger_sha256, acknowledgement=None):
    if row.get('owned_job_kill_on_close') is not True or type(row.get('pid')) is not int or row['pid'] <= 0:
        raise ValueError('Missing original owned JobObject closure contract')
    if row.get('status') == 'COMPLETED' and row.get('exit_code') == 0:
        return {'original_worker_waited_and_closed': True, 'historical_failure_preserved': False}
    expected = {'status': row.get('status'), 'exit_code': row.get('exit_code'), 'ledger_sha256': ledger_sha256}
    if (row.get('status') not in {'COMPLETED', 'TIMEOUT'} or type(row.get('exit_code')) is not int
            or acknowledgement is None or any(acknowledgement.get(k) != v for k, v in expected.items())):
        raise ValueError('Nonzero/timeout worker requires an exact explicitly reviewed failure acknowledgement')
    return {'original_worker_waited_and_closed': True, 'historical_failure_preserved': True,
            'functional_status': 'NONZERO_PRESERVED_NOT_PASS'}


def worker_audit():
    """Read campaign ledgers and inspect only their exact PIDs; never terminate."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    supervisor = ROOT / 'src/supervisor.py'
    if sha(supervisor) != SUPERVISOR_SHA:
        raise ValueError('Supervisor source differs from the reviewed wait/finally-close/then-ledger contract')
    acknowledged = {}
    ack_path = ROOT / 'validation/PRESERVED_JOB_FAILURES.json'
    if ack_path.is_file():
        data = json.loads(ack_path.read_text(encoding='utf-8-sig'))
        if data.get('schema') != 'DEE45.preserved-job-failures.v1':
            raise ValueError('Wrong failure acknowledgement schema')
        acknowledged = {r['job']: r for r in data['jobs']}
        if len(acknowledged) != len(data['jobs']):
            raise ValueError('Duplicate historical failure acknowledgement')
    rows = []
    for path in sorted((ROOT / 'jobs').rglob('COMMAND.json')):
        row = json.loads(path.read_text(encoding='utf-8-sig'))
        if 'pid' not in row:
            continue
        ledger_sha = sha(path)
        closure = validate_worker_ledger(row, ledger_sha, acknowledged.get(path.parent.name))
        pid = row['pid']
        handle = kernel.OpenProcess(0x1000, False, pid)
        if handle:
            try:
                code = wintypes.DWORD()
                if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                    raise ctypes.WinError(ctypes.get_last_error())
                if code.value == 259:
                    creation, exit_time, kernel_time, user_time = (wintypes.FILETIME() for _ in range(4))
                    if not kernel.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time), ctypes.byref(kernel_time), ctypes.byref(user_time)):
                        raise ctypes.WinError(ctypes.get_last_error())
                    filetime = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
                    observation = {'kind': 'ACTIVE', 'creation_unix_ns': (filetime - 116444736000000000) * 100}
                else:
                    observation = {'kind': 'EXITED'}
            finally:
                kernel.CloseHandle(handle)
        else:
            error = ctypes.get_last_error()
            if error == 5:
                observation = {'kind': 'DENIED'}
            elif error == 87:
                observation = {'kind': 'ABSENT'}
            else:
                raise OSError(error, 'Cannot verify campaign worker PID ' + str(pid))
        observed = assess_current_pid(observation, path.stat().st_mtime_ns)
        rows.append({'ledger': path.relative_to(ROOT).as_posix(), 'ledger_sha256': ledger_sha, 'pid': pid,
                     'status': row['status'], 'exit_code': row['exit_code'], **closure, **observed,
                     'owned_job_kill_on_close': row.get('owned_job_kill_on_close')})
    if not rows:
        raise ValueError('No campaign-owned worker ledgers available')
    return {'status': 'VERIFIED', 'original_campaign_workers_waited_and_closed': True, 'records': rows,
            'supervisor_source_sha256': SUPERVISOR_SHA,
            'acknowledged_historical_failures_sha256': sha(ack_path) if ack_path.is_file() else None,
            'scope': 'Original campaign process closure follows process.wait + finally OwnedJob.close, with ledger written afterwards in the reviewed supervisor source. Revisited PIDs may be reused or inaccessible; no global process-state claim, enumeration or termination.'}


def publish(candidate, proof, destination, report):
    """Explicit final action; requires a successful exact-candidate clean proof."""
    candidate = Path(candidate).resolve(); destination = Path(destination).resolve()
    if destination.name != NAME or destination.parent != ROOT.parents[1]:
        raise ValueError('Publication restricted to this new 4.5 canonical destination')
    if destination.exists():
        raise FileExistsError('Existing canonical preserved: ' + str(destination))
    before = check_protected()
    container = verify(candidate)
    clean = json.loads(Path(proof).read_text(encoding='utf-8-sig'))
    if clean.get('schema') != 'DEE45.exact-clean.v1' or clean.get('status') != 'VERIFIED' or clean.get('candidate_sha256') != container['sha256']:
        raise ValueError('Exact candidate clean proof required')
    if not clean.get('commands') or not clean.get('posttrajectory_assertions'):
        raise ValueError('Proof lacks finite executions/assertions')
    if any(r['status'] != 'COMPLETED' or r['exit_code'] != 0 or not r['owned_worker_waited'] or not r['owned_job_closed'] for r in clean['commands']):
        raise ValueError('Clean worker not successfully closed')
    workers = worker_audit()
    temporary = destination.with_name(destination.name + '.pending.' + str(os.getpid()))
    shutil.copyfile(candidate, temporary)
    if sha(temporary) != container['sha256']:
        raise ValueError('Publication copy changed bytes')
    os.rename(temporary, destination)
    final = verify(destination)
    transport = split(destination, destination.parent)
    after = check_protected()
    if before != after:
        raise ValueError('Protected artifact audit mismatch')
    sys.path.insert(0, str(ROOT / 'src'))
    from supervisor import remaining
    result = {'schema': 'DEE45.publication.v1', 'status': 'VERIFIED', 'canonical': final, 'clean_proof_sha256': sha(proof),
              'parts': transport, 'protected_artifacts': after, 'workers': workers,
              'original_campaign_workers_waited_and_closed': workers['original_campaign_workers_waited_and_closed'] and all(r['owned_worker_waited'] and r['owned_job_closed'] for r in clean['commands']),
              'elapsed_original_budget_seconds': 14400 - remaining(), 'budget': json.loads((ROOT / 'BUDGET.json').read_text(encoding='utf-8-sig'))}
    put(report, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('inventory'); p.add_argument('--product-root', type=Path, required=True); p.add_argument('--report', type=Path, required=True)
    p = commands.add_parser('build'); p.add_argument('--product-root', type=Path, required=True); p.add_argument('--output', type=Path, required=True); p.add_argument('--report', type=Path, required=True); p.add_argument('--require-final', action='store_true')
    p = commands.add_parser('verify'); p.add_argument('candidate', type=Path); p.add_argument('--report', type=Path, required=True)
    p = commands.add_parser('parts'); p.add_argument('candidate', type=Path); p.add_argument('--output-dir', type=Path, required=True); p.add_argument('--report', type=Path, required=True)
    p = commands.add_parser('publish'); p.add_argument('--candidate', type=Path, required=True); p.add_argument('--proof', type=Path, required=True); p.add_argument('--destination', type=Path, required=True); p.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'inventory':
        files, omitted = selection(args.product_root)
        result = {'selected': [{'path': n, 'bytes': x['source'].stat().st_size, 'origin': x['origin']} for n, x in sorted(files.items())], 'omitted': omitted}
        put(args.report, result)
    elif args.command == 'build': result = build(args.product_root, args.output, args.report, args.require_final)
    elif args.command == 'verify': result = verify(args.candidate); put(args.report, result)
    elif args.command == 'parts':
        verify(args.candidate); result = split(args.candidate, args.output_dir); put(args.report, result)
    else: result = publish(args.candidate, args.proof, args.destination, args.report)
    print(json.dumps(result if args.command != 'inventory' else {'selected': len(result['selected']), 'bytes': sum(r['bytes'] for r in result['selected']), 'omitted': len(result['omitted'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
