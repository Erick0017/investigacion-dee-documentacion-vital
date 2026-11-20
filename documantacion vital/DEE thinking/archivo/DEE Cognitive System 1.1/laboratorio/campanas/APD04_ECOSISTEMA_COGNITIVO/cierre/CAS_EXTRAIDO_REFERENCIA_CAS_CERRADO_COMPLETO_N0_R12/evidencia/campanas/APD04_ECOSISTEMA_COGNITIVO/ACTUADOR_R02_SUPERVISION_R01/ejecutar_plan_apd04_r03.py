"""Literal APD04 schedule through the existing single-entry Supervisor.

The plan schedules opportunities, never answers, choices or result-dependent
retries. It cannot import a life, construct a Runtime or edit scientific state.
Run with --root-go only after Root closes the literal plan.
"""
import argparse
import ctypes
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emit(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode('utf8')
    with path.open('xb') as stream:
        stream.write(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def job_measure(pc, handle):
    """Class 8 supplies actual job-wide I/O; no nested-job summation."""
    if not handle:
        return None
    result = pc.job_resources(handle)

    class BasicAndIo(ctypes.Structure):
        _fields_ = [('basic', pc.Accounting), ('io', pc.IO)]

    value = BasicAndIo()
    if not pc.K.QueryInformationJobObject(handle, 8, ctypes.byref(value), ctypes.sizeof(value), None):
        raise ctypes.WinError(ctypes.get_last_error())
    result['job_io_class8'] = {key: int(getattr(value.io, key)) for key, _ in pc.IO._fields_}
    result['scope'] = 'This owned Job and descendants, not additive to an outer total Job; energy NO MEDIDA.'
    return result


def validate_plan(plan):
    if plan.get('schema') != 'APD04.literal_supervisor_schedule.v1' or plan.get('status') != 'CLOSED_FOR_EXECUTION':
        raise ValueError('Root must close this exact literal schedule before Native execution.')
    if not isinstance(plan.get('events'), list):
        raise ValueError('events must be a literal list.')
    duration = plan['duration_seconds']
    if type(duration) not in (int, float) or not 0 < duration <= 7200:
        raise ValueError('A finite declared window, at most the existing owner horizon, is required.')
    prior = -1
    ids = []
    for event in plan['events']:
        offset = event['at_seconds']
        if type(offset) not in (int, float) or not 0 <= offset <= duration or offset < prior:
            raise ValueError('Offsets must be finite, ordered and inside the declared horizon.')
        prior = offset
        if event['kind'] not in ('material', 'command', 'checkpoint', 'status'):
            raise ValueError('Only fixed material opportunities, literal commands and passive/checkpoint events are accepted.')
        if event['kind'] in ('material', 'command'):
            ids.append(event['request_id'])
        if event['kind'] == 'material' and (not isinstance(event['situations'], list) or not 1 <= len(event['situations']) <= 16):
            raise ValueError('Literal material payload must retain the Supervisor limits.')
        if event['kind'] == 'command' and (not isinstance(event.get('argv'), list) or not event['argv'] or any(not isinstance(x, str) for x in event['argv'])):
            raise ValueError('command argv must contain only literal strings.')
    if len(set(ids)) != len(ids):
        raise ValueError('Never reuse or re-put a material ID within a plan.')
    queued = plan.get('after_window_pending')
    if queued:
        if queued['request_id'] in ids or not isinstance(queued['situations'], list) or not 1 <= len(queued['situations']) <= 16:
            raise ValueError('The queued continuation needs its own new ID and literal payload.')
    datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00'))
    for key, default, maximum in (('material_wait_seconds',30,30), ('result_limit_seconds',1200,7200),
                                ('stop_control_wait_seconds',120,240), ('stop_process_wait_seconds',120,240),
                                ('poll_heartbeat_seconds',5,5)):
        value = plan.get(key, default)
        if type(value) not in (int,float) or not 0 < value <= maximum:
            raise ValueError('Finite generic bounded transport parameter required: '+key)
    return plan


def run(root, plan_path, out):
    plan = validate_plan(read(plan_path))
    deadline = datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00')).timestamp()
    closing_reserve = plan.get('closing_reserve_seconds', 180)
    if time.time()+plan['duration_seconds']+closing_reserve >= deadline:
        raise ValueError('Insufficient remaining campaign budget; no owner started.')
    if out.exists():
        raise FileExistsError('Every attempted trajectory directory is preserved; no silent retry.')
    ui_path = root/'sistema/app/usar_dee.py'
    ui = load('apd04_existing_single_entry', ui_path)
    if any(name.startswith('dee_thinking') for name in sys.modules):
        raise RuntimeError('The host driver must not import the engine.')
    config_path = ui.selected_config_path(root)
    config = dict(read(config_path))
    source_material_wait = config['material_wait_seconds']
    config['material_wait_seconds'] = plan.get('material_wait_seconds',30)
    if config['memory_limit_bytes'] != 536870912:
        raise ValueError('Existing Native owner limit must remain 512 MiB.')
    if config['owner_max_seconds'] < plan['duration_seconds']+closing_reserve:
        raise ValueError('The existing owner horizon does not cover the declared window.')
    backend = ui.OriginalBackend(root, config)
    life = ui.identifier(plan['life'])
    session = ui.Supervisor(root, life, backend, config)
    initial = backend.record(life)
    if initial['snapshot_sha256'] != plan['initial_snapshot_sha256'] or initial['physical']['tick'] != plan['initial_tick']:
        raise ValueError('Selected complete current state differs. No import, fallback or rewind is permitted.')
    if initial['world_id'] != plan.get('world_id', life):
        raise ValueError('World identity differs from the closed plan.')
    if not session.state_path.is_file() or session.state.get('world_id') != initial['world_id']:
        raise ValueError('Root must register the existing paired life using the actual UI protocol.')
    pending = session.state.get('pending_material')
    if pending and pending['id'] != plan.get('resume_pending_id'):
        raise ValueError('Existing pending ID is preserved; a closed same-ID continuation is required.')
    if session.state.get('uncertain_preserved'):
        raise ValueError('Existing uncertainty is preserved, never replayed.')
    event_files = []
    for event in plan['events']:
        if event['kind'] in ('command', 'material'):
            ui.identifier(event['request_id'])
        if event['kind'] == 'command':
            options = ui.command_parser().parse_args(event['argv'])
            ui.literal_rows(options)  # Reject controls and validate literal material only.
            if options.action == 'evento':
                event_file = options.archivo.resolve(strict=True)
                if not event_file.is_relative_to(root):
                    raise ValueError('A literal event file must be declared inside the current source root.')
                event_files.append(event_file)
    out.mkdir(parents=True)
    frozen_paths = [Path(__file__), plan_path, ui_path, config_path, root/'sistema/gestionar.py',
                    root/'sistema/app/process_control.py', root/'sistema/app/protocolo_apd03.py']
    frozen_paths += [root/value for value in plan.get('freeze_source_paths', [])]
    frozen_paths += event_files
    frozen = []
    for index, path in enumerate(dict.fromkeys(p.resolve(strict=True) for p in frozen_paths)):
        if path != Path(__file__).resolve() and path != plan_path and not path.is_relative_to(root):
            raise ValueError('Only explicit local source paths can be frozen.')
        target = out/'FUENTES_ANTES_DE_NATIVE'/(str(index).zfill(3)+'_'+path.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        frozen.append({'source': str(path), 'copy': target.relative_to(out).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size})
    emit(out/'ANTES_DE_NATIVE.json', {'plan': plan, 'plan_sha256': sha(plan_path), 'config': config,
         'record': initial, 'protocol': session.state, 'sources': frozen, 'new_native_ticks_yet': 0,
         'schedule_is_host_preparation': True, 'host_does_not_read_answers_to_choose': True,
         'generic_transport_override_only': {'source_material_wait_seconds':source_material_wait,
            'effective_material_wait_seconds':config['material_wait_seconds'],
            'same_id_result_limit_seconds':plan.get('result_limit_seconds',1200),
            'stop_control_wait_seconds':plan.get('stop_control_wait_seconds',120),
            'stop_process_wait_seconds':plan.get('stop_process_wait_seconds',120)}})
    protected_paths = [root/'sistema/estado/ACTIVO.json']
    protected = [{'path': str(path), 'sha256': sha(path)} for path in protected_paths]
    pc = None
    handle = None
    start = None
    stop = None
    stop_attempted = False
    owner_process = None
    error = None
    count = 0
    heartbeat_at = -float('inf')
    began = time.monotonic()
    window_start = None
    cpu_start = time.process_time_ns()
    journal = out/'EVENTOS.jsonl'

    def append(kind, **fields):
        nonlocal count
        value = {'seq': count, 'kind': kind, 'wall_utc': now(), 'driver_seconds': time.monotonic()-began,
                 'window_seconds': None if window_start is None else time.monotonic()-window_start, **fields}
        with journal.open('a', encoding='utf8', newline='\n') as stream:
            stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n')
            stream.flush()
        count += 1
        return value

    def metrics():
        result = job_measure(pc, handle) if handle else None
        if result is not None:
            result['owned_owner_pid'] = None if owner_process is None else owner_process.pid
            result['owned_owner_exit_code'] = None if owner_process is None else owner_process.poll()
            result['exit_code_scope'] = 'Exact owned Popen owner PID; descendant exit codes are not inferred.'
        return result

    def stop_once():
        nonlocal stop_attempted
        if stop_attempted:
            raise RuntimeError('STOP was already attempted. Preserve its actual ID; never replay a new STOP.')
        stop_attempted = True
        previous_control = config['control_wait_seconds']
        previous_process = config['stop_wait_seconds']
        config['control_wait_seconds'] = plan.get('stop_control_wait_seconds',120)
        config['stop_wait_seconds'] = plan.get('stop_process_wait_seconds',120)
        try:
            return session.control('detener')
        finally:
            config['control_wait_seconds'] = previous_control
            config['stop_wait_seconds'] = previous_process

    def check_clock():
        if time.time() >= deadline-closing_reserve:
            raise TimeoutError('Campaign closing reserve reached; no automatic extension.')

    def heartbeat(force=False):
        nonlocal heartbeat_at
        if force or time.monotonic()-heartbeat_at >= plan.get('heartbeat_seconds', 30):
            t = time.monotonic_ns()
            status = session.status()
            append('passive_status', result=status, native_job=metrics(), observer_elapsed_ns=time.monotonic_ns()-t)
            heartbeat_at = time.monotonic()
            print(json.dumps({'life': life, 'window_seconds': None if window_start is None else heartbeat_at-window_start,
                  'cached_tick': ui.observation(status['ESTADO_PUBLICADO']).get('tick')}, ensure_ascii=False), flush=True)

    def wait_until(offset):
        target = window_start+offset
        while time.monotonic() < target:
            check_clock()
            heartbeat()
            time.sleep(min(1, max(0, target-time.monotonic())))

    def resolve_same_id(request_id, value):
        limit = time.monotonic()+plan.get('result_limit_seconds',1200)
        while ui.row_of(value).get('status') not in ui.TERMINAL:
            if str(value.get('admission', '')).startswith('rejected'):
                return value
            check_clock()
            if time.monotonic() >= limit:
                raise TimeoutError('Same pending ID preserved without re-put: '+request_id)
            if time.monotonic()-heartbeat_at >= plan.get('poll_heartbeat_seconds',5):
                heartbeat(force=True)
            if owner_process is not None and owner_process.poll() is not None:
                raise RuntimeError('Owned owner process exited while its same material ID remained pending; actual exit code preserved.')
            time.sleep(.25)
            try:
                value = session.result(request_id)
                append('same_id_read_only_poll', request_id=request_id, result=value, native_job=metrics())
            except subprocess.TimeoutExpired as caught:
                append('same_id_read_only_poll_timeout', request_id=request_id, error=str(caught),
                       native_job=metrics(), no_requeue=True)
        return value

    try:
        with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
            session.open(new=False)
            start = session.start()
            owner_process = backend.process
            pc = backend.pc
            handle = pc.K.OpenJobObjectW(0x0004, False, start['job_name'])
            if not handle:
                raise RuntimeError('Cannot retain a read-only query handle for this owned Native Job.')
            append('owner_started_paused', result=start, protocol=session.state, native_job=metrics())
            append('control', operation='reanudar', result=session.control('reanudar'))
            window_start = time.monotonic()
            emit(out/'INICIO_VENTANA.json', {'wall_utc': now(), 'monotonic': window_start,
                 'declared_seconds': plan['duration_seconds'], 'owner': start, 'plan_sha256': sha(plan_path)})
            if pending:
                append('same_pending_id_after_reopen', request_id=pending['id'],
                       result=resolve_same_id(pending['id'], session.result(pending['id'])))
            for event in plan['events']:
                wait_until(event['at_seconds'])
                if not all(sha(row['source']) == row['sha256'] for row in frozen):
                    raise RuntimeError('Frozen source changed during the declared trajectory.')
                before = metrics()
                t = time.monotonic_ns()
                if event['kind'] == 'status':
                    heartbeat(force=True)
                    continue
                if event['kind'] == 'checkpoint':
                    value = session.control('guardar')
                    append('scheduled_checkpoint', tag=event.get('tag'), result=value, record=backend.record(life), native_job=metrics())
                    continue
                if event['kind'] == 'command':
                    options = ui.command_parser().parse_args(event['argv'])
                    situations = ui.literal_rows(options)
                    feedback, actuator = options.retorno, options.actuador
                else:
                    situations = event['situations']
                    feedback, actuator = event.get('feedback', 'real'), event.get('actuator', 'closed')
                request_id = event['request_id']
                append('scheduled_material_before_submission', event=event, literal_situations=situations,
                       requested_id=request_id, native_job=before)
                value = session.material(situations, feedback=feedback, actuator=actuator, request_id=request_id)
                value = resolve_same_id(request_id, value)
                append('scheduled_material_result', requested_id=request_id, event=event, result=value,
                       protocol=session.state, elapsed_ns=time.monotonic_ns()-t, native_job_before=before, native_job_after=metrics())
                if ui.row_of(value).get('status') in ('uncertain', 'failed_preserved'):
                    raise RuntimeError('Adverse/uncertain request preserved; no automatic retry or redesign.')
            wait_until(plan['duration_seconds'])
            end = time.monotonic()
            emit(out/'FIN_VENTANA.json', {'wall_utc': now(), 'monotonic': end,
                 'actual_evolving_window_seconds': end-window_start, 'same_owner': start, 'native_job': metrics(),
                 'sources_unchanged': all(sha(row['source']) == row['sha256'] for row in frozen),
                 'not_a_global_cognitive_verdict': True})
            if plan.get('after_window_pending'):
                queued = plan['after_window_pending']
                ui.identifier(queued['request_id'])
                append('control', operation='pausar', result=session.control('pausar'))
                previous_wait = session.config['material_wait_seconds']
                session.config['material_wait_seconds'] = plan.get('queueing_wait_seconds', .25)
                try:
                    value = session.material(queued['situations'], feedback=queued.get('feedback', 'real'),
                         actuator=queued.get('actuator', 'closed'), request_id=queued['request_id'])
                finally:
                    session.config['material_wait_seconds'] = previous_wait
                same = session.result(queued['request_id'])
                append('intentional_pending_after_full_window', result=value, same_id_result=same,
                       pending_protocol=session.state, no_re_put=True)
                if ui.row_of(same).get('status') != 'queued':
                    raise ValueError('Expected queued ID while paused; actual result preserved, no replacement.')
            append('control', operation='guardar', result=session.control('guardar'))
            stop = stop_once()
            append('control', operation='detener', result=stop, record=backend.record(life),
                   protocol=session.state, native_job=metrics())
    except BaseException as caught:
        error = {'type': type(caught).__name__, 'message': str(caught)}
        append('preserved_failure', error=error, protocol=session.state)
    finally:
        if session.owned and not stop_attempted:
            try:
                stop = stop_once()
                append('finally_own_stop', result=stop, native_job=metrics())
            except BaseException as caught:
                append('own_stop_not_confirmed', error=repr(caught), no_replacement_owner=True)
                error = error or {'type': type(caught).__name__, 'message': str(caught)}
        elif session.owned:
            append('stop_already_attempted_not_replayed', native_job=metrics(),
                   protocol=session.state, no_clean_stop_claim=True)
        final_metrics = metrics()
        if handle:
            pc.K.CloseHandle(handle)
    final = {'schema': 'APD04.literal_supervisor_schedule.execution.v1', 'life': life,
             'world_id': initial['world_id'], 'start': start, 'stop': stop, 'error': error,
             'events': count, 'driver_wall_seconds': time.monotonic()-began,
             'driver_cpu_ns': time.process_time_ns()-cpu_start, 'final_record': backend.record(life),
             'final_protocol': session.state, 'final_native_job': final_metrics,
             'stop_attempted_once':stop_attempted,'owner_stop_confirmed':not session.owned and stop is not None,
             'frozen_sources_unchanged': all(sha(row['source']) == row['sha256'] for row in frozen),
             'protected_files_unchanged': all(sha(row['path']) == row['sha256'] for row in protected),
             'no_new_import_no_T0_no_automatic_retry': True, 'energy': 'NO MEDIDA'}
    emit(out/'RESULTADO.json', final)
    print(json.dumps(final, ensure_ascii=False), flush=True)
    return 1 if error or not final['protected_files_unchanged'] else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--root-go', choices=('APD04_LITERAL_PLAN_CLOSED',), required=True)
    args = parser.parse_args()
    return run(args.root.resolve(strict=True), args.plan.resolve(strict=True), args.out.resolve())


if __name__ == '__main__':
    raise SystemExit(main())
