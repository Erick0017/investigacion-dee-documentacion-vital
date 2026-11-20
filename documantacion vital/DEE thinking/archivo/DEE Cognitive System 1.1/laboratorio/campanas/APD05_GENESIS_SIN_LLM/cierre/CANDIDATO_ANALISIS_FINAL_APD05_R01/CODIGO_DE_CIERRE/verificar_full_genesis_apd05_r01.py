"""Verificación prospectiva del Full exacto por la API real de GÉNESIS.

Preparado, no ejecutado por defecto. El driver no elige respuestas, no edita
Source, no enseña fuera del plan y nunca reintenta una operación material.
HTTP y frame no equivalen a inspección visual del navegador ni a otro equipo.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile

WHL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHL_SHA = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA = '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
TERMINAL = {'completed', 'failed_preserved', 'uncertain', 'rejected_invalid'}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def emit(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def safe(root, name):
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Portable relative member required')
    part = PurePosixPath(name)
    if part.is_absolute() or not part.parts or '..' in part.parts:
        raise ValueError('Unsafe member')
    result = (root / Path(*part.parts)).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Member escapes declared extraction')
    return result


def archive_members(archive):
    seen, files = set(), []
    for item in archive.infolist():
        p = PurePosixPath(item.filename)
        if getattr(item, 'orig_filename', item.filename) != item.filename:
            raise ValueError('Archive member changed while parsing')
        if p.is_absolute() or not p.parts or p.parts[0] != 'cognitive sistem' or '..' in p.parts or '\\' in item.filename or ':' in item.filename:
            raise ValueError('Unsafe/noncanonical Full member')
        if stat.S_ISLNK(item.external_attr >> 16):
            raise ValueError('Symbolic links forbidden')
        key = item.filename.rstrip('/').casefold()
        if key in seen:
            raise ValueError('Case-insensitive repeated member')
        seen.add(key)
        if not item.is_dir():
            files.append(item.filename)
    return files


def verify_managed(root):
    path = root / 'actualizaciones/ARCHIVOS_GESTIONADOS.json'
    manifest = read(path)
    for name, row in manifest['members'].items():
        file = safe(root, name)
        if file.is_symlink() or not file.is_file() or file.stat().st_size != row['bytes'] or sha(file) != row['sha256']:
            raise ValueError('Managed bytes differ: ' + name)
    return {'manifest_sha256': sha(path), 'members': len(manifest['members']),
            'release': manifest.get('release'), 'campaign': manifest.get('source_campaign')}


def runtime_probe(root):
    python = root / 'motor/python313/python.exe'
    code = "import sys,struct,json,importlib.metadata,dee_thinking,dee_thinking._native as n; print(json.dumps({'python':sys.version,'pointer_bytes':struct.calcsize('P'),'version':importlib.metadata.version('dee-thinking'),'module':dee_thinking.__file__,'pyd':n.__file__,'loaded_files':sorted({str(m.__file__)for m in list(sys.modules.values())if isinstance(getattr(m,'__file__',None),str)and not m.__file__.startswith('<')}),'runtime_created':False}))"
    command = [str(python), '-I', '-B', '-X', 'utf8', '-c', code]
    start = time.monotonic()
    operation = subprocess.run(command, cwd=python.parent, capture_output=True, text=True, encoding='utf8', timeout=60)
    if operation.returncode:
        raise RuntimeError('Included import failed: ' + operation.stderr)
    value = json.loads(operation.stdout)
    if value['pointer_bytes'] != 8 or not value['python'].startswith('3.13.') or value['version'] != '4.5.0':
        raise ValueError('Included Python/engine identity differs')
    if sha(value['pyd']) != PYD_SHA or any(not Path(name).resolve().is_relative_to(root) for name in value['loaded_files']):
        raise ValueError('Included import used a library outside exact Full')
    return {'argv': command, 'identity': value, 'wall_seconds': time.monotonic() - start,
            'new_native_ticks': 0, 'scope': 'Official module import only; no world created.'}


class HTTP:
    def __init__(self, port, evidence):
        self.base = 'http://127.0.0.1:' + str(port)
        self.token, self.rows, self.evidence = None, [], evidence
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(self, path, value=None, *, timeout=10, save=True):
        if not path.startswith('/') or path.startswith('//'):
            raise ValueError('Fixed loopback endpoints only')
        data = None if value is None else json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf8')
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['X-Genesis-Token'] = self.token
        request = urllib.request.Request(self.base + path, data=data, headers=headers)
        start = time.monotonic()
        try:
            with self.opener.open(request, timeout=timeout) as result:
                body, status = result.read(), result.status
        except urllib.error.HTTPError as error:
            body, status = error.read(), error.code
        content = json.loads(body) if body[:1] in (b'{', b'[') else {'body_bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
        if save:
            self.rows.append({'sequence': len(self.rows), 'wall_utc': now(), 'path': path,
                              'method': 'GET' if data is None else 'POST', 'request': value,
                              'http_status': status, 'response': content,
                              'host_wall_seconds': time.monotonic() - start})
        return status, content

    def connect(self, process, seconds):
        start = time.monotonic()
        while time.monotonic() - start < seconds:
            if process.poll() is not None:
                raise RuntimeError('GUI exited before local session became available')
            try:
                status, value = self.request('/api/session', save=False)
                if status == 200 and isinstance(value.get('token'), str):
                    self.token = value['token']
                    self.rows.append({'wall_utc': now(), 'event': 'local_session_connected',
                                      'version': value.get('version'), 'token_omitted': True})
                    return
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(.25)
        raise TimeoutError('Local session startup bound reached')

    def action(self, step):
        status, response = self.request('/api/action', {'action': step['action'], 'value': step.get('value')})
        if status != 202 or not response.get('id'):
            raise RuntimeError('Action not accepted by the real GUI service: ' + str(response))
        ident = response['id']
        start = time.monotonic()
        while time.monotonic() - start < step['timeout_seconds']:
            code, state = self.request('/api/status', save=False)
            found = [row for row in state.get('jobs', []) if row['id'] == ident] if code == 200 else []
            if found and found[0]['status'] in ('completed', 'error'):
                result = found[0]
                self.rows.append({'wall_utc': now(), 'event': 'gui_job_terminal', 'step': step['id'],
                                  'job': result, 'status': state,
                                  'host_wait_seconds': time.monotonic() - start})
                expected = step.get('expected_job_status', 'completed')
                if result['status'] != expected:
                    raise RuntimeError('GUI job status outside prospective criterion: ' + step['id'])
                return result, state
            time.sleep(.2)
        raise TimeoutError('GUI job bound reached; action is not resent: ' + step['id'])

    def save(self, name):
        output = self.evidence / (name + '.jsonl.gz')
        with output.open('xb') as raw:
            with gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0, compresslevel=9) as zipped:
                for row in self.rows:
                    zipped.write((json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf8'))
        return {'file': output.name, 'bytes': output.stat().st_size, 'sha256': sha(output), 'records': len(self.rows)}


def validate_frame(frame, life, n):
    if frame.get('available') is not True or frame.get('coherent_tick') is not True or frame.get('life_id') != life or frame.get('N') != n:
        raise ValueError('No coherent real frame for the declared life')
    if not isinstance(frame['tick'], str) or not frame['tick'].isdigit() or frame['counts']['sites'] != n ** 3:
        raise ValueError('Frame tick/count not exact')
    for row in frame['cells']:
        if not isinstance(row['raw'], str) or not isinstance(row['clock'], str):
            raise ValueError('uint64 must cross the GUI boundary as decimal strings')
        raw, clock = int(row['raw']), int(row['clock'])
        if not 0 <= raw < 2**64 or not 0 <= clock < 2**64:
            raise ValueError('Out-of-range uint64 frame witness')
        x, y, z = row['xyz']
        if row['index'] != (x * n + y) * n + z or row['state'] != raw & 0xffffffff or row['semantic'] != raw >> 60 or row['s_reg'] != (raw >> 32) & 65535:
            raise ValueError('Frame physical field decoding or coordinate mismatch')
    official = frame['coordinate_proof']['official_observe_samples']
    if not official or not all(row.get('official_observe_matches') for row in official):
        raise ValueError('No official accessor cross-check for the 3D projection')
    return {'tick': frame['tick'], 'RAW_sha256': frame['RAW_sha256'], 'clocks_sha256': frame['clocks_sha256'],
            'displayed_cells': len(frame['cells']), 'counts': frame['counts'], 'coverage': frame['coverage'],
            'official_coordinate_witnesses': len(official), 'not_a_continuable_snapshot': True}


def transport_snapshot(root, state, baseline_max_seq=None):
    record = state.get('record')
    if not record:
        return None
    world, life = record['world_id'], state['life_id']
    path = safe(root, 'trabajo_personal/estado/servicios_persistentes/' + world + '/cola.sqlite3')
    # Read-only SQLite, including legitimate WAL. Never run QueueDB.put/init.
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=5) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute('BEGIN')
        index = [dict(row) for row in connection.execute('SELECT seq,id,payload_sha,is_control,status FROM requests ORDER BY seq')]
        actual_max = max((row['seq'] for row in index), default=0)
        rows = [] if baseline_max_seq is None else [dict(row) for row in connection.execute(
            'SELECT * FROM requests WHERE seq>? ORDER BY seq', (baseline_max_seq,))]
    protocol = safe(root, 'trabajo_personal/entrada_sencilla/vidas/' + life + '/PROTOCOLO.json')
    sessions = protocol.with_name('SESIONES.jsonl')
    return {'life': life, 'world_id': world, 'record': record,
            'transport_rows': rows, 'transport_index': index, 'max_seq': actual_max,
            'inherited_prefix_max_seq': baseline_max_seq,
            'inherited_results_not_duplicated_here': True, 'protocol': read(protocol),
            'sessions': [json.loads(line) for line in sessions.read_text(encoding='utf8').splitlines()] if sessions.is_file() else [],
            'queues_are_operational_state_not_external_answer_memory': True}


def runtime_inventory(root):
    runtime = root / 'motor/python313'
    return {path.relative_to(runtime).as_posix(): {'bytes': path.stat().st_size,
            'sha256': sha(path), 'mtime_ns': path.stat().st_mtime_ns}
            for path in sorted(runtime.rglob('*')) if path.is_file()}


def original_transport_index(root, catalog_row):
    bundle = read(safe(root, catalog_row['persistent_service']['bundle']))
    database = safe(root, bundle['assets_prefix'] + '/cola.sqlite3')
    declared = [row for row in bundle['paired_export_manifest']['members'] if row['file'] == 'cola.sqlite3']
    if len(declared) != 1 or sha(database) != declared[0]['sha256']:
        raise ValueError('Distributed original full-cut journal differs')
    with sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute('SELECT seq,id,payload_sha,is_control,status FROM requests ORDER BY seq')]


def audit_artifacts(root, protocol, phases):
    """Verify actual app exports; no replacement recording or synthetic frame."""
    recordings, contexts = [], []
    for phase in phases:
        for step in phase['steps']:
            job = step.get('job') or {}
            result = job.get('result') or {}
            if job.get('action') == 'grabar' and result.get('recording') is False:
                relative = result['file'].replace('\\', '/')
                if not relative.startswith('trabajo_personal/genesis/'):
                    raise ValueError('Recording outside the personal application state')
                path = safe(root, relative)
                events, frames, ticks, expanded = 0, 0, [], 0
                with gzip.open(path, 'rt', encoding='utf8') as stream:
                    for line in stream:
                        expanded += len(line.encode('utf8'))
                        if expanded > 256_000_000:
                            raise ValueError('Recording expansion exceeds the declared audit bound')
                        row = json.loads(line)
                        if row.get('life_id') not in (None, protocol['personal_life']):
                            raise ValueError('Another life mixed into the recorded session')
                        events += 1
                        if row.get('event') == 'passive_frame':
                            frame = row['frame']
                            validate_frame(frame, protocol['personal_life'], protocol['N'])
                            ticks.append(frame['tick'])
                            frames += 1
                if not events or not frames:
                    raise ValueError('Recording contains no actual synchronized frame')
                recordings.append({'file': relative, 'bytes': path.stat().st_size,
                                   'sha256': sha(path), 'expanded_bytes': expanded,
                                   'events': events, 'frames': frames, 'frame_ticks': ticks,
                                   'replay_is_archived_not_new_native_execution': True,
                                   'browser_replay_must_be_checked_separately': True})
            if job.get('action') == 'exportar':
                relative = result['file'].replace('\\', '/')
                path = safe(root, relative)
                if sha(path) != result['sha256'] or path.stat().st_size != result['bytes']:
                    raise ValueError('Exported continuity bytes differ from the GUI receipt')
                with zipfile.ZipFile(path) as archive:
                    if archive.testzip() is not None:
                        raise ValueError('Continuity context ZIP is corrupt')
                    value = json.loads(archive.read('CONTINUIDAD.json'))
                    if value['life_id'] != protocol['personal_life'] or value.get('not_a_restorable_mind_copy') is not True:
                        raise ValueError('Continuity export falsely identifies the life or a restorable mind')
                contexts.append({'file': relative, 'bytes': result['bytes'], 'sha256': result['sha256'],
                                 'life_id': value['life_id'], 'restorable': False,
                                 'manual_locator': value.get('manual'), 'continue_command': value.get('continue_command')})
    if not recordings or not contexts:
        raise ValueError('Prospective Full proof requires a real recording and context export')
    return {'recordings': recordings, 'continuity_contexts': contexts,
            'scope': 'Actual gzip JSONL frames/events and context ZIP; no automatic MP4 or new live execution attributed to replay.'}


def validate_protocol(value):
    if value.get('schema') != 'APD05.exact_full_gui.prospective_protocol.R01' or value.get('status') != 'CLOSED_FOR_EXACT_FULL_APD05_GUI_PROOF':
        raise ValueError('Root must freeze the actual APD05 GUI protocol before execution')
    required = ('personal_life', 'N', 'expected_selection_file', 'expected_selection_sha256',
                'source_snapshot_sha256', 'source_pair_manifest_sha256', 'pending_transport_id',
                'tree_memory_limit_bytes', 'port', 'phases', 'total_wall_limit_seconds')
    if any(key not in value for key in required) or len(value['phases']) < 2:
        raise ValueError('Explicit paired parent, pending ID and at least two owner phases required')
    if not 1024 <= value['port'] <= 65535 or not 60 <= value['total_wall_limit_seconds'] <= 3600:
        raise ValueError('Bounded local port and proof horizon required')
    all_steps = [step for phase in value['phases'] for step in phase['steps']]
    if len({step['id'] for step in all_steps}) != len(all_steps):
        raise ValueError('Every prospective step has a unique auditor ID')
    allowed = {'action', 'frame', 'status', 'view', 'wait_pending', 'wait_result', 'browser_checkpoint'}
    for step in all_steps:
        if step['kind'] not in allowed or not 1 <= step['timeout_seconds'] <= 600:
            raise ValueError('Unknown step or unbounded wait')
        if step['kind'] == 'action' and step['action'] not in {'abrir', 'vivir', 'pausar', 'guardar', 'detener', 'ejecutar', 'ensenar', 'resultado', 'exportar', 'grabar', 'reposo'}:
            raise ValueError('No arbitrary endpoint or shell task permitted')
    actions = {step.get('action') for step in all_steps if step['kind'] == 'action'}
    required_actions = {'abrir', 'vivir', 'pausar', 'guardar', 'detener', 'ejecutar', 'ensenar', 'exportar', 'grabar'}
    if not required_actions <= actions:
        raise ValueError('Full protocol lacks one of the declared application operations')
    for kind in ('frame', 'wait_pending', 'wait_result', 'browser_checkpoint'):
        if not any(step['kind'] == kind for step in all_steps):
            raise ValueError('Missing explicit continuity/view proof: ' + kind)
    pending_submits = [step for step in all_steps if step.get('action') == 'ejecutar' and
                       (step.get('value') or {}).get('id') == value['pending_transport_id']]
    if len(pending_submits) != 1:
        raise ValueError('The exact pending transport ID must have one prospective submission')
    if not any(step.get('expect_no_transport_row') and step.get('expected_job_status') == 'error' for step in all_steps):
        raise ValueError('An invalid or unregistered request with no material insertion must be covered')
    return value


def run(args):
    started = time.monotonic()
    archive = args.zip.resolve(strict=True)
    protocol_path = args.protocol.resolve(strict=True)
    protocol = validate_protocol(read(protocol_path))
    absolute_deadline = datetime.fromisoformat(args.absolute_deadline_utc) if args.absolute_deadline_utc else None
    if absolute_deadline is not None and absolute_deadline.tzinfo is None:
        raise ValueError('Absolute supervision deadline must include UTC offset')
    destination, proof = args.destination.resolve(), args.proof.resolve()
    if destination.exists() or proof.exists() or len(str(destination)) > 120:
        raise ValueError('Fresh short workspace extraction and proof required; no silent reuse')
    if sha(archive) != args.zip_sha256:
        raise ValueError('Not the Root-approved exact Full bytes')
    proof.mkdir(parents=True)
    destination.mkdir(parents=True)
    report = {'schema': 'APD05.exact_full_gui.external_verification.R01',
              'zip': str(archive), 'zip_sha256': args.zip_sha256, 'zip_bytes': archive.stat().st_size,
              'protocol_sha256': sha(protocol_path), 'started_utc': now(), 'phases': [],
              'same_computer_not_other_hardware': True, 'original_Source_modified': False,
              'browser_visual_review_performed_by_this_driver': False,
              'new_native_execution_started': False, 'energy': 'NO_MEDIDA'}
    root = None
    try:
        with zipfile.ZipFile(archive) as zipped:
            members = archive_members(zipped)
            if zipped.testzip() is not None:
                raise ValueError('Full CRC failure')
            zipped.extractall(destination)
        root = safe(destination, 'cognitive sistem').resolve(strict=True)
        report['extracted_root'] = str(root)
        report['zip_members'] = len(members)
        personal = root / 'trabajo_personal'
        preexisting = [p.relative_to(personal).as_posix() for p in personal.rglob('*')
                       if p.is_file() and p.relative_to(personal).as_posix() != 'LEER_PRIMERO.md']
        if preexisting:
            raise ValueError('A fresh Full must not ship another collaborator personal life or pointer: ' + str(preexisting[:4]))
        report['personal_before'] = {'preexisting_personal_files_except_README': preexisting,
                                     'one_explicit_new_whole_pair_copy_expected': True}
        report['managed_before'] = verify_managed(root)
        selection = safe(root, protocol['expected_selection_file'])
        if sha(selection) != protocol['expected_selection_sha256']:
            raise ValueError('The extracted GUI selected another candidate/configuration')
        config = read(selection)
        if config.get('source_snapshot_sha256') != protocol['source_snapshot_sha256']:
            raise ValueError('Selected native parent differs')
        if config.get('paired_export_manifest_sha256') != protocol['source_pair_manifest_sha256']:
            raise ValueError('The selected full-pair identity differs')
        catalog = read(root / 'entes/CATALOGO.json')['cuts']
        selected = [row for row in catalog if row['alias'] == config['source_alias']]
        if len(selected) != 1 or selected[0]['source_life'] != config['source_life'] or selected[0]['snapshot_sha256'] != config['source_snapshot_sha256'] or not selected[0].get('persistent_service'):
            raise ValueError('GUI alias does not identify the selected complete persistent cut')
        report['paired_parent'] = {'selection': config, 'catalog_row': selected[0],
            'scope': 'Original Source pair identity and distributed full-cut membership; the transport bundle manifest is regenerated by declared logistics, not byte-identical to the original Source export manifest.'}
        if sha(root / 'motor' / WHL) != WHL_SHA or not (root / 'motor/python313/site-packages/INSTALACION_DEE.json').is_file():
            raise ValueError('Full does not carry the already prepared official runtime')
        runtime_before = runtime_inventory(root)
        report['included_runtime_import'] = runtime_probe(root)
        original_index = original_transport_index(root, selected[0])
        if protocol['pending_transport_id'] in {row['id'] for row in original_index}:
            raise ValueError('Prospective pending ID already belongs to inherited history')
        for required in ('ABRIR_GENESIS.bat', 'aplicacion/GENESIS/genesis.py', 'aplicacion/GENESIS/propietario_genesis.py', 'sistema/app/process_control.py'):
            if not safe(root, required).is_file():
                raise FileNotFoundError(required)
        pc_spec = importlib.util.spec_from_file_location('apd05_full_owned_job_only', root / 'sistema/app/process_control.py')
        pc = importlib.util.module_from_spec(pc_spec)
        pc_spec.loader.exec_module(pc)
        report['preflight_wall_seconds'] = time.monotonic() - started
        before_transport, final_transport, imports = None, None, 0
        inherited_max_seq = None
        for number, phase in enumerate(protocol['phases']):
            if time.monotonic() - started >= protocol['total_wall_limit_seconds']:
                raise TimeoutError('Absolute proof bound reached before another GUI owner')
            folder = proof / ('PHASE_' + str(number) + '_' + phase['id'])
            folder.mkdir()
            identity = ['--nueva', protocol['personal_life']] if number == 0 else []
            command = ['cmd.exe', '/d', '/c', 'ABRIR_GENESIS.bat', '--sin-navegador',
                       '--puerto', str(protocol['port']), '--seleccion', str(selection), *identity]
            http = HTTP(protocol['port'], folder)
            phase_report = {'id': phase['id'], 'argv': command, 'started_utc': now(), 'steps': []}
            phase_start = time.monotonic()
            process = job = None
            wall_guard = None
            try:
                with (folder / 'STDOUT.txt').open('xb') as stdout, (folder / 'STDERR.txt').open('xb') as stderr:
                    process, job, job_name = pc.spawn_owned(command, cwd=root, stdout=stdout, stderr=stderr,
                                                          memory_limit=protocol['tree_memory_limit_bytes'])
                    report['GUI_process_started'] = True
                    phase_report.update(pid=process.pid, job_name=job_name)
                    http.connect(process, phase.get('startup_timeout_seconds', 60))
                    for endpoint in ('/', '/app.js', '/style.css'):
                        code, content = http.request(endpoint)
                        if code != 200:
                            raise RuntimeError('GUI assets did not load from the extraction')
                    if absolute_deadline is not None:
                        remaining = (absolute_deadline - datetime.now(timezone.utc)).total_seconds()
                        if remaining <= 0:
                            raise TimeoutError('Absolute native-owner closing deadline reached')
                        wall_guard = threading.Timer(remaining, pc.terminate_job, args=(job, 124))
                        wall_guard.daemon = True
                        wall_guard.start()
                    for step in phase['steps']:
                        if time.monotonic() - started >= protocol['total_wall_limit_seconds']:
                            raise TimeoutError('Absolute proof bound reached; material is not resent')
                        if step['kind'] == 'action':
                            if step['action'] == 'abrir':
                                report['native_owner_open_attempted'] = True
                            transport_before = None
                            if step.get('expect_no_transport_row'):
                                code, old_status = http.request('/api/status')
                                transport_before = transport_snapshot(root, old_status, inherited_max_seq)
                            result, state = http.action(step)
                            if state['life_id'] != protocol['personal_life']:
                                raise ValueError('Another personal life silently selected')
                            phase_report['steps'].append({'id': step['id'], 'job': result})
                            if step['action'] == 'abrir':
                                report['new_native_execution_started'] = True
                                final_transport = transport_snapshot(root, state, inherited_max_seq)
                                if before_transport is None:
                                    before_transport = final_transport
                                    inherited_max_seq = before_transport['max_seq']
                                    emit(proof / 'TRANSPORTE_INICIAL.json', before_transport)
                                    if before_transport['transport_index'] != original_index:
                                        raise ValueError('Original queue/request prefix was not preserved by the whole import')
                                    actual_physical = state['record']['physical']
                                    expected_physical = selected[0]['physical']
                                    keys = ('N', 'tick', 'RAW_sha256', 'clocks_sha256')
                                    if any(actual_physical.get(key) != expected_physical.get(key) for key in keys):
                                        raise ValueError('Opening changed the inherited physical state before explicit Vivir')
                                    report['whole_import_boundary'] = {'request_prefix_identical': True,
                                        'original_request_rows': len(original_index),
                                        'physical_fields_identical_before_live': list(keys),
                                        'not_T0': True, 'new_acquisition_attributed_to_import': False}
                                if number == 0 and int(state['record']['physical']['tick']) != int(config['source_tick']):
                                    raise ValueError('Opening did not restore the selected complete cut')
                            if transport_before is not None:
                                transport_after = transport_snapshot(root, state, inherited_max_seq)
                                if transport_before['transport_index'] != transport_after['transport_index']:
                                    raise ValueError('An invalid/unregistered form caused a transport insertion')
                                phase_report['steps'][-1]['no_transport_row_confirmed'] = {
                                    'index_sha256': hashlib.sha256(json.dumps(transport_after['transport_index'], sort_keys=True).encode()).hexdigest(),
                                    'rows': len(transport_after['transport_index']),
                                    'scope': 'No native/transport insertion; this is a parser rejection, not a DEE response.'}
                        elif step['kind'] in ('frame', 'status'):
                            endpoint = '/api/frame' if step['kind'] == 'frame' else '/api/status'
                            deadline = time.monotonic() + step['timeout_seconds']
                            while True:
                                code, value = http.request(endpoint)
                                if code == 200 and (step['kind'] != 'frame' or value.get('available')):
                                    break
                                if time.monotonic() >= deadline:
                                    raise TimeoutError('No coherent passive frame in declared window')
                                time.sleep(.2)
                            result = validate_frame(value, protocol['personal_life'], protocol['N']) if step['kind'] == 'frame' else value
                            phase_report['steps'].append({'id': step['id'], 'result': result})
                        elif step['kind'] == 'view':
                            code, value = http.request('/api/view', step['value'])
                            if code != 200:
                                raise RuntimeError('Passive view control rejected')
                            phase_report['steps'].append({'id': step['id'], 'result': value})
                        elif step['kind'] == 'wait_pending':
                            deadline = time.monotonic() + step['timeout_seconds']
                            while True:
                                code, value = http.request('/api/status')
                                pending = value.get('pending') if code == 200 else None
                                if pending and pending['id'] == protocol['pending_transport_id']:
                                    break
                                if time.monotonic() >= deadline:
                                    raise TimeoutError('The exact prospective pending ID was not preserved')
                                time.sleep(.2)
                            phase_report['steps'].append({'id': step['id'], 'pending': pending})
                        elif step['kind'] == 'wait_result':
                            # Read-only reconciliation of the original transport
                            # ID. This never sends ejecutar or repeats a PUT.
                            deadline = time.monotonic() + step['timeout_seconds']
                            polls = []
                            while True:
                                poll_step = {'id': step['id'] + '_poll_' + str(len(polls)),
                                             'action': 'resultado', 'timeout_seconds': 15}
                                result, state = http.action(poll_step)
                                row = (result.get('result') or {}).get('request')
                                if row is None:
                                    raise ValueError('The same pending ID has no transport row')
                                if row.get('id') != protocol['pending_transport_id']:
                                    raise ValueError('Read-only reconciliation returned another ID')
                                polls.append({'status': row['status'], 'payload_sha': row['payload_sha']})
                                if row['status'] in TERMINAL:
                                    if row['status'] != step.get('expected_transport_status', 'completed'):
                                        raise RuntimeError('Pending request ended outside its declared status criterion')
                                    break
                                if time.monotonic() >= deadline:
                                    raise TimeoutError('Same-ID read-only polling bound reached; no requeue or new life')
                                time.sleep(.5)
                            phase_report['steps'].append({'id': step['id'], 'read_only_polls': polls,
                                                          'new_material_submissions': 0, 'result': result})
                        elif step['kind'] == 'browser_checkpoint':
                            marker = proof / ('BROWSER_READY_' + phase['id'] + '.json')
                            recordings = [row['job']['result']['file'] for row in http.rows
                                          if row.get('event') == 'gui_job_terminal' and
                                          row.get('job', {}).get('action') == 'grabar' and
                                          row['job'].get('result', {}).get('recording') is False]
                            emit(marker, {'url': http.base, 'phase': phase['id'], 'life': protocol['personal_life'],
                                          'frozen_scope': step['scope'], 'browser_ack_required': True,
                                          'closed_recording_files_relative_to_extraction': recordings,
                                          'package_root': str(root),
                                          'no_material_buttons_authorized_by_this_checkpoint': True})
                            ack = proof / ('BROWSER_ACK_' + phase['id'] + '.json')
                            deadline = time.monotonic() + step['timeout_seconds']
                            while not ack.is_file() and time.monotonic() < deadline:
                                time.sleep(.25)
                            if not ack.is_file():
                                raise TimeoutError('Browser proof not provided; HTTP alone is not visual GUI validation')
                            value = read(ack)
                            if value.get('url') != http.base or value.get('life') != protocol['personal_life'] or value.get('scope') != step['scope']:
                                raise ValueError('Browser acknowledgement outside its declared scope')
                            phase_report['steps'].append({'id': step['id'], 'browser_ack': value,
                                                          'ack_sha256': sha(ack)})
                    code, state = http.request('/api/status')
                    if code != 200 or state.get('owned_by_this_app') is not False:
                        raise RuntimeError('Each phase must explicitly stop its own native owner before closing the GUI')
                    final_transport = transport_snapshot(root, state, inherited_max_seq)
                    emit(folder / 'TRANSPORTE_FINAL.json', final_transport)
                    code, response = http.request('/api/shutdown', {})
                    if code != 200:
                        raise RuntimeError('GUI shutdown rejected; no forced favorable continuation')
                    process.wait(timeout=30)
                    phase_report['exit_code'] = process.returncode
                    if process.returncode:
                        raise RuntimeError('GUI launcher returned an error')
                    child_deadline = time.monotonic() + 5
                    while pc.job_resources(job).get('job_active_processes') and time.monotonic() < child_deadline:
                        time.sleep(.05)
                    if pc.job_resources(job).get('job_active_processes'):
                        raise RuntimeError('The owned proof tree still contains a live child after GUI shutdown')
            except BaseException as error:
                phase_report['error'] = {'type': type(error).__name__, 'detail': str(error),
                                         'no_material_retry_or_new_life': True}
                raise
            finally:
                if wall_guard is not None:
                    wall_guard.cancel()
                phase_report['wall_seconds'] = time.monotonic() - phase_start
                phase_report['http_primary'] = http.save('HTTP_PRIMARIO')
                if job is not None:
                    phase_report['resources'] = pc.job_resources(job)
                    phase_report['scope'] = 'Outer GUI/launcher/owner tree, not summed with nested 512MiB owner peak.'
                    if process is not None and process.poll() is None:
                        phase_report['guard_terminated_own_tree'] = True
                        phase_report['complete_native_stop_not_inferred_from_job_kill'] = True
                        pc.terminate_job(job, 124)
                        try: process.wait(timeout=10)
                        except subprocess.TimeoutExpired: pass
                    pc.close_job(job)
                report['phases'].append(phase_report)
        sessions = final_transport['sessions']
        imports = sum(row['event'] == 'explicit_complete_paired_import' for row in sessions)
        material = [row for row in sessions if row.get('event') == 'literal_material_submission' and row.get('id') == protocol['pending_transport_id']]
        transport = [row for row in final_transport['transport_rows'] if row['id'] == protocol['pending_transport_id']]
        if imports != 1:
            raise ValueError('Expected exactly one complete paired import, not a fresh mind on each GUI launch')
        if len(material) != 1 or len(transport) != 1 or transport[0]['status'] != protocol.get('pending_terminal_status', 'completed'):
            raise ValueError('Pending request did not complete from exactly one write-ahead submission')
        if material[0]['payload'] != json.loads(transport[0]['payload']):
            raise ValueError('Pending request payload changed between owner processes')
        if before_transport['world_id'] != final_transport['world_id'] or before_transport['life'] != final_transport['life']:
            raise ValueError('Life/world identity changed across GUI processes')
        if final_transport['protocol'].get('pending_material') or final_transport['protocol'].get('uncertain_preserved'):
            raise ValueError('The final GUI protocol is not a normally continuable complete cut')
        report['pending_exact_once'] = {'id': protocol['pending_transport_id'],
            'literal_material_submissions': len(material), 'transport_rows': len(transport),
            'payload_sha256': transport[0]['payload_sha'], 'terminal_status': transport[0]['status'],
            'same_life': final_transport['life'], 'same_world': before_transport['world_id'] == final_transport['world_id'],
            'scope': 'One API submission and one write-ahead journal entry; no second PUT by the driver.'}
        report['managed_after'] = verify_managed(root)
        if report['managed_after'] != report['managed_before'] or sha(archive) != args.zip_sha256:
            raise ValueError('Exact Full or managed sources changed during personal proof')
        runtime_after = runtime_inventory(root)
        if runtime_before != runtime_after:
            raise ValueError('Opening/reopening wrote or installed into the prepared runtime')
        report['prepared_runtime_unchanged'] = {'files': len(runtime_before), 'same_bytes_and_mtime_ns': True,
                                              'startup_installation_executed': False}
        report['complete_source_pair_imports_from_session_log'] = imports
        report['recording_and_context_exports'] = audit_artifacts(root, protocol, report['phases'])
        report['final_record'] = final_transport['record']
        report['new_native_ticks_observed'] = int(final_transport['record']['physical']['tick']) - int(config['source_tick'])
        if report['new_native_ticks_observed'] <= 0:
            raise ValueError('The Full proof did not advance the inherited native world')
        report['zip_still_exact'] = True
        report['archive_recalculation_not_a_substitute'] = True
        report['native_semantic_decoding'] = 'Separate fixed RAW decoder and prospective criteria required; HTTP success is not semantic correctness.'
    except BaseException as error:
        report['error'] = {'type': type(error).__name__, 'detail': str(error)}
        raise
    finally:
        report['finished_utc'] = now()
        report['total_wall_seconds'] = time.monotonic() - started
        report['driver_sha256'] = sha(Path(__file__).resolve())
        emit(proof / 'VERIFICACION_FULL_GENESIS_EXTERNA.json', report)
    print(json.dumps({'zip_sha256': args.zip_sha256, 'zip_bytes': archive.stat().st_size,
                      'final_life': report['final_record']['life_id'],
                      'final_tick': report['final_record']['physical']['tick'],
                      'scope': 'Exact Full GUI/API and same-life continuity; not a global scientific PASS.'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--zip-sha256', required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--execute-native', action='store_true')
    parser.add_argument('--absolute-deadline-utc', help='Supervision only; never extends the frozen protocol or campaign')
    args = parser.parse_args()
    if not args.execute_native:
        parser.error('Prepared only. Root must freeze the actual protocol and authorize --execute-native.')
    run(args)
