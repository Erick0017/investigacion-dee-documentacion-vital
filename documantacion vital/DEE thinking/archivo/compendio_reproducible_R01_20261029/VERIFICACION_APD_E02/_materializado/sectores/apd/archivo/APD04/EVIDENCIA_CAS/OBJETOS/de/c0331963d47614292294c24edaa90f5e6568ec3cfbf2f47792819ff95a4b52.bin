"""Prueba prospectiva APD04 en el Full exacto; preparada, NO ejecutada.

Reutiliza INICIAR.bat -> arrancar.py -> usar_dee.py y su Supervisor para un
pendiente exacto. Sólo se instala como instrumento en actualizaciones/ del Full
al cierre autorizado. No selecciona otro padre, no crea T0 y no calcula acciones.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def emit(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, ensure_ascii=False, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def walk(value, path='$'):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('result', 'result_json') and isinstance(item, str):
                try:
                    item = json.loads(item)
                except ValueError:
                    pass
            yield from walk(item, path + '.' + key)
    elif isinstance(value, list):
        for number, item in enumerate(value):
            yield from walk(item, path + '[' + str(number) + ']')


def gates(kind):
    origins = [((33, 33, 33), [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1)])]
    if kind >= 28:
        origins[0][1].extend([(-1, 0), (0, -1)])
        origins += [((47, 47, 47), [(-1, 0), (0, -1), (1, 0), (0, 1)]),
                    ((47, 17, 47), [(1, 0), (0, 1)])]
    if kind >= 32:
        origins += [((47, 7, 47), [(-1, 0), (0, -1)] + ([(1, 0), (1, 1)] if kind == 36 else []))]
    return {((o[0] + 4*x) % 67, (o[1] + 4*y) % 67, (o[2] + z) % 67): z
            for o, directions in origins for x, y in directions for z in (-1, 1)}


def decode(raw):
    value = int(raw)
    if not 0 <= value < 2**64:
        raise ValueError('Exact uint64 RAW required')
    return value & 0xffffffff, (value >> 60) & 15, [((value >> k) & 15) - (16 if ((value >> k) & 15) >= 8 else 0) for k in (48, 52, 56)]


def lexical_sign(reader):
    panel = reader['panel']
    if len(panel) not in (12, 28, 32, 36) or {tuple(x['site']) for x in panel} != set(gates(len(panel))):
        raise ValueError('Frozen finite lexical reader coverage differs')
    candidates = []
    for observation in panel:
        state, semantic, direction = decode(observation['raw'])
        if state and semantic == 1 and direction in ([0, 0, -1], [0, 0, 1]):
            candidates.append(direction[2])
    sign = candidates[0] if len(candidates) == 1 else None
    if sign != reader['formed_native_command']:
        raise ValueError('RAW does not support formed_native_command')
    return sign


def observations(value):
    words, memories, numeric, teachers = [], [], [], []
    for locator, node in walk(value):
        if not isinstance(node, dict):
            continue
        reader = node.get('reader')
        if isinstance(reader, dict) and 'formed_native_command' in reader and 'panel' in reader:
            sign = lexical_sign(reader)
            name = node.get('form')
            if name:
                words.append({'name': name, 'sign_RAW': sign, 'read_tick': node.get('read_tick'), 'locator': locator})
        if isinstance(node.get('forms'), list) and isinstance(node.get('memories'), list):
            for item in node['forms']:
                words.append({'name': item['form'], 'sign_RAW': lexical_sign(item['result']['reader']),
                              'locator': locator + '.forms'})
            for item in node['memories']:
                memories.append({'name': item['context'], 'sign_RAW': lexical_sign(item['result']['reader']),
                                 'locator': locator + '.memories'})
        if node.get('kind') in ('APD04_explicit_lexical_revision', 'APD04_explicit_lexical_lesson'):
            teachers.append({'form': node['form'], 'sign': node['teacher_sign'], 'mode': node['teacher_mode'],
                             'revision': node['revision'], 'end_tick': node['end_tick'],
                             'requests': node['requests'], 'locator': locator})
        if node.get('kind') in ('APD04_candidate_scalar_classification', 'APD04_candidate_native_balance'):
            trial = node['native_trial']
            panel = trial['reader']['observations']
            expected = {(15 + 2*x, 17, 15 + 2*z): [x, 1, z] for x in (-1, 0, 1) for z in (0, -1)}
            if len(panel) != 6 or {tuple(x['site']) for x in panel} != set(expected):
                raise ValueError('Six-site numeric reader differs')
            candidates = []
            for item in panel:
                state, semantic, direction = decode(item['raw'])
                if state and semantic == 1 and direction == expected[tuple(item['site'])]:
                    candidates.append((item['site'][0] - 15) // 2)
            sign = candidates[0] if len(candidates) == 1 else None
            if sign != node.get('physical_choice') or sign != trial['reader'].get('choice'):
                raise ValueError('Numeric physical result differs from exact RAW')
            numeric.append({'kind': node['kind'], 'raw_sensor_value': trial.get('raw_sensor_value'),
                            'loads': node.get('public_independent_loads'), 'sign_RAW': sign,
                            'candidates': len(candidates), 'locator': locator, 'observations': panel})
    return {'words': words, 'memories': memories, 'numeric': numeric, 'teachers': teachers}


def fingerprint(record):
    return {key: record['physical'][key] for key in ('N', 'tick', 'RAW_sha256', 'clocks_sha256')}


def phase(root, protocol, output, name):
    """Two sessions not expressible as a fixed CLI list: queue/poll same ID.

    Transport waiting never computes a sign or retries a material insertion.
    """
    ui = load('apd04_full_existing_ui', root / 'sistema/app/usar_dee.py')
    config = dict(read(root / 'sistema/contratos/ENTRADA_SENCILLA_APD03.json'))
    if name == 'pending':
        config['material_wait_seconds'] = 0.25
    backend = ui.DistributionBackend(root, config)
    life = protocol['personal_life']
    report = {'phase': name, 'life': life, 'new_import': False, 'events': [], 'issues': []}
    with ui.SessionLock(backend.protocol_home / life / 'SUPERVISOR.lock'):
        session = ui.Supervisor(root, life, backend, config)
        report['before'] = session.open(new=False)
        stop_attempted = False
        try:
            if name == 'reopen':
                pending = session.state.get('pending_material')
                if not pending or pending['id'] != protocol['pending_id']:
                    raise ValueError('Expected exact pending ID not preserved; no substitute or replay')
                report['pending_before_start'] = dict(pending)
                report['same_id_before_start'] = session.result(protocol['pending_id'])
            report['start'] = session.start()
            if fingerprint(report['before']) != report['start']['observation']['physical']:
                # Passive status contains exactly the four fingerprint keys in
                # current UI; if extended later, compare the declared keys only.
                physical = report['start']['observation']['physical']
                if any(physical[k] != v for k, v in fingerprint(report['before']).items()):
                    raise ValueError('Paused owner opened another physical state')
            if name == 'pending':
                if session.state.get('pending_material'):
                    raise ValueError('Preexisting pending must be resolved, not overwritten')
                result = session.material(protocol['pending_situations'], 'omit', 'closed', request_id=protocol['pending_id'])
                report['events'].append({'operation': 'one_material_put_while_paused', 'result': result})
                pending = session.state.get('pending_material')
                if not pending or pending['id'] != protocol['pending_id']:
                    raise ValueError('Paused pending was not conserved as planned')
                report['pending_preserved'] = dict(pending)
            else:
                session.control('reanudar')
                deadline = time.monotonic() + protocol['same_id_result_limit_seconds']
                while True:
                    result = session.result(protocol['pending_id'])
                    row = ui.row_of(result)
                    report['events'].append({'operation': 'same_id_read_only_poll', 'result': result})
                    if row.get('status') in ui.TERMINAL:
                        if row['status'] != 'completed':
                            raise ValueError('Pending finished negatively, preserved without retry')
                        break
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Same ID remains pending; no second put or reimport')
                    time.sleep(5)
                for argv in (['palabra-ecosistema', 'clasifica', '--retorno', 'omit'],
                             ['palabra-ecosistema', 'equilibra', '--retorno', 'omit'],
                             ['panel', '--nuevas', '--memorias', '--retorno', 'omit']):
                    result = ui.execute(session, argv)
                    report['events'].append({'literal_argv': argv, 'result': result})
                    if ui.row_of(result).get('status') != 'completed':
                        raise ValueError('New literal query not complete; preserve its ID, no replay')
            report['saved'] = session.control('guardar')
            stop_attempted = True
            report['stop'] = session.control('detener')
            report['after'] = backend.record(life)
            report['protocol_after'] = dict(session.state)
        except BaseException as error:
            report['error'] = {'type': type(error).__name__, 'message': str(error), 'no_retry_no_reimport': True}
            raise
        finally:
            if session.owned and not stop_attempted:
                stop_attempted = True
                try:
                    report['cleanup_STOP_once'] = session.control('detener')
                except BaseException as error:
                    report['cleanup_STOP_not_confirmed'] = repr(error)
            emit(output / ('FASE_' + name + '.json'), report)


def run(root, protocol, output):
    root, output = root.resolve(), output.resolve()
    if protocol['status'] != 'CLOSED_FOR_EXACT_FULL_APD04_PROOF':
        raise ValueError('Prospective protocol not closed by Root')
    if not (root / 'actualizaciones/arrancar.py').is_file():
        raise ValueError('Only the exact extracted collaborator distribution is admissible, not canonical Source S')
    if protocol.get('source_pending_request_ids') != []:
        raise ValueError('This prospective proof requires a clean stopped selected source; declare a pending-source revision instead of ignoring inherited requests')
    if not output.is_relative_to(root / 'trabajo_personal/resultados'):
        raise ValueError('Test only in the extracted personal workspace')
    config = read(root / 'sistema/contratos/ENTRADA_SENCILLA_APD03.json')
    if config['memory_limit_bytes'] != protocol['native_memory_limit_bytes']:
        raise ValueError('Declared Native memory limit differs from the actual UI contract')
    source = next((x for x in read(root / 'entes/CATALOGO.json')['cuts'] if x['alias'] == protocol['source_alias']), None)
    if not source or not source.get('persistent_service') or config['source_alias'] != source['alias']:
        raise ValueError('Exact selected APD04 alias/complete pair missing; no APD03 fallback')
    if (source['source_life'], source['tick'], source['snapshot_sha256']) != (
            protocol['source_life'], protocol['source_tick'], protocol['source_snapshot_sha256']):
        raise ValueError('Closed parent differs; no favorable alternative selected')
    if config['source_snapshot_sha256'] != protocol['source_snapshot_sha256']:
        raise ValueError('UI contract differs from distributed parent')
    if protocol['baseline_new_forms'] != {'clasifica': 1, 'equilibra': -1} or protocol['new_teacher'] != {'form': 'clasifica', 'sign': -1}:
        raise ValueError('Prospective finite sign revision changed; declare another revision before execution')
    life = protocol['personal_life']
    record_path = root / 'trabajo_personal/estado/vidas' / life / 'VIDA.json'
    if record_path.exists():
        raise FileExistsError('Existing personal life preserved, no repeated proof in it')
    output.mkdir(parents=True, exist_ok=False)
    pc = load('apd04_full_owned_job', root / 'sistema/app/process_control.py')
    journal = root / 'trabajo_personal/entrada_sencilla/vidas' / life / 'SESIONES.jsonl'
    report = {'schema': 'APD04.exact_full.single_entry.execution.R01', 'protocol': protocol,
              'issues': [], 'runs': [], 'cuts': [], 'one_personal_life': life,
              'native_execution_not_archived_recalculation': True,
              'source_and_original_personal_work_never_modified': True}
    emit(output / 'PROTOCOLO_CONGELADO.json', protocol)

    def execute(label, argv):
        before_record = read(record_path) if record_path.is_file() else None
        start = time.monotonic()
        failure = None
        with (output / (label + '_STDOUT.txt')).open('xb') as stdout, (output / (label + '_STDERR.txt')).open('xb') as stderr:
            process, job, _ = pc.spawn_owned(argv, cwd=root, stdout=stdout, stderr=stderr,
                                             memory_limit=protocol['proof_tree_memory_limit_bytes'])
            try:
                process.wait(timeout=protocol['session_wall_limit_seconds'])
                resources = pc.job_resources(job)
                until = time.monotonic() + 5
                while resources.get('job_active_processes') and time.monotonic() < until:
                    time.sleep(.05)
                    resources = pc.job_resources(job)
                if resources.get('job_active_processes'):
                    raise RuntimeError('Owned proof tree did not close')
            except BaseException as error:
                failure = {'type': type(error).__name__, 'message': str(error)}
            finally:
                resources = pc.job_resources(job)
                pc.close_job(job)
        row = {'label': label, 'argv': argv, 'pid': process.pid, 'exit_code': process.returncode,
               'wall_seconds': time.monotonic() - start, 'resources_before_job_close': resources,
               'supervision_error': failure,
               'scope': 'Own extracted proof process tree. An interrupted operation is not a cognitive crash or a clean-stop claim.'}
        report['runs'].append(row)
        emit(output / (label + '_EJECUCION.json'), row)
        if failure or process.returncode:
            raise RuntimeError('Actual Full entry failed, preserved without retry: ' + label)
        after = read(record_path)
        if after['life_id'] != life or after['world_id'] != life or after['parent']['encoded_sha256'] != source['snapshot_sha256']:
            raise ValueError('Personal life identity or physical parent differs')
        report['cuts'].append({'label': label, 'before': before_record, 'after': after})

    def cli(label, commands, new=False):
        script = output / (label + '_GUION.json')
        emit(script, commands)
        execute(label, ['cmd.exe', '/d', '/c', 'INICIAR.bat', 'usar', '--nueva' if new else '--vida', life, '--guion', str(script)])

    def events():
        return [json.loads(line) for line in journal.read_bytes().splitlines() if line]

    def material_observations():
        return observations([x for x in events() if x['event'] in ('literal_material_result', 'same_id_read_only_result')])

    try:
        cli('BASELINE', [['estado'], ['reanudar'], ['palabra-ecosistema', 'clasifica', '--retorno', 'omit'],
                        ['palabra-ecosistema', 'equilibra', '--retorno', 'omit'],
                        ['panel', '--nuevas', '--memorias', '--retorno', 'omit'], ['guardar'], ['detener'], ['salir']], True)
        baseline = material_observations()
        report['baseline_RAW'] = baseline
        for name, expected in protocol['baseline_new_forms'].items():
            found = {x['sign_RAW'] for x in baseline['words'] if x['name'] == name}
            if found != {expected}:
                raise ValueError('Declared inherited new association not available; no retargeted teacher or fallback')
        lesson = ['ensenar-ecosistema', 'clasifica', '-1', '--revision', '--docente', 'paired', '--retorno', 'omit']
        calibration = output / 'MEDICIONES_NUEVAS.json'
        emit(calibration, [{'modo': 'apd04-calibrar', 'casos': [{'tipo': 'clasifica', 'valor': 43}, {'tipo': 'equilibra', 'cargas': [9, 3]}]}])
        cli('DOCENCIA_NUEVA', [['estado'], ['reanudar'], lesson, ['palabra-ecosistema', 'clasifica', '--retorno', 'omit'],
             ['palabra-ecosistema', 'equilibra', '--retorno', 'omit'], ['evento', str(calibration), '--retorno', 'omit'],
             ['panel', '--nuevas', '--memorias', '--retorno', 'omit'], ['guardar'], ['detener'], ['salir']])
        after_teacher = material_observations()
        report['immediate_after_teacher_RAW'] = after_teacher
        revision_rows = [x for x in after_teacher['teachers'] if x['form'] == 'clasifica' and x['revision']]
        if len(revision_rows) != 1:
            raise ValueError('One explicit opposite lesson required, not covert reteaching')
        first_new = [x for x in after_teacher['words'] if x['name'] == 'clasifica'
                     and x['read_tick'] is not None and x['read_tick'] >= revision_rows[0]['end_tick']]
        if not first_new or first_new[0]['sign_RAW'] != -1:
            report['issues'].append('First query after the single new lesson did not emit the new association')
        for name in ('pending', 'reopen'):
            execute('PENDIENTE' if name == 'pending' else 'REAPERTURA_MISMO_ID',
                    [str(root / 'motor/python313/python.exe'), '-I', '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                     '--raiz', str(root), '--protocolo', str(output / 'PROTOCOLO_CONGELADO.json'),
                     '--salida', str(output), '--fase', name, '--ejecutar-native'])
        pending = read(output / 'FASE_pending.json')
        reopened = read(output / 'FASE_reopen.json')
        if pending['pending_preserved'] != reopened['pending_before_start']:
            raise ValueError('Pending protocol changed between processes')
        if fingerprint(pending['after']) != fingerprint(reopened['before']):
            raise ValueError('Physical state changed outside declared continuation')
        all_events = events()
        submissions = [e for e in all_events if e['event'] == 'literal_material_submission']
        if len({e['id'] for e in submissions}) != len(submissions) or sum(e['id'] == protocol['pending_id'] for e in submissions) != 1:
            raise ValueError('A material request was re-put or exact pending ID was replaced')
        post = observations(reopened)
        report['after_reopen_RAW'] = post
        for name, expected in {'clasifica': -1, 'equilibra': -1}.items():
            if {x['sign_RAW'] for x in post['words'] if x['name'] == name} != {expected}:
                report['issues'].append('New explicit association/retention differs: ' + name)
        initial_words = {x['name']: x['sign_RAW'] for x in baseline['words'] if x['name'] not in ('clasifica', 'equilibra')}
        final_words = {x['name']: x['sign_RAW'] for x in post['words']}
        for name, sign in initial_words.items():
            if final_words.get(name) != sign:
                report['issues'].append('Inherited signal lost or changed: ' + name)
        initial_memory = {x['name']: x['sign_RAW'] for x in baseline['memories']}
        final_memory = {x['name']: x['sign_RAW'] for x in post['memories']}
        for name, sign in initial_memory.items():
            if final_memory.get(name) != sign:
                report['issues'].append('Inherited memory access differs: ' + name)
        final = material_observations()
        report['all_observations_RAW'] = final
        revisions = [x for x in final['teachers'] if x['form'] == 'clasifica' and x['revision']]
        if len(revisions) != 1 or revisions[0]['sign'] != -1 or any(x['receipt']['status'] != 'applied' for x in revisions[0]['requests']):
            report['issues'].append('Single declared opposite lesson not completely applied')
        if not final['numeric']:
            report['issues'].append('New raw numerical inputs produced no archived numeric observation')
        report['continuity'] = {'one_import_no_T0': sum(x['event'] == 'explicit_complete_paired_import' for x in all_events) == 1,
             'one_pending_put': True, 'exact_pending_protocol_equal': True,
             'physical_equal_before_reopen': True, 'final_record': read(record_path)}
        if not report['continuity']['one_import_no_T0']:
            report['issues'].append('Unexpected number of complete imports')
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    except BaseException as error:
        report['error'] = {'type': type(error).__name__, 'message': str(error), 'no_retry_no_fallback': True}
        raise
    finally:
        if journal.is_file():
            (output / 'SESIONES_ORIGINALES.jsonl').write_bytes(journal.read_bytes())
        emit(output / 'RESULTADOS_FULL_APD04.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raiz', type=Path, required=True)
    parser.add_argument('--protocolo', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--fase', choices=('pending', 'reopen'))
    parser.add_argument('--ejecutar-native', action='store_true')
    args = parser.parse_args()
    if not args.ejecutar_native:
        raise SystemExit('Root GO required; this preparation has executed no Native')
    if args.fase:
        phase(args.raiz.resolve(), read(args.protocolo), args.salida.resolve(), args.fase)
    else:
        value = run(args.raiz, read(args.protocolo), args.salida)
        print(json.dumps({'issues': value['issues'], 'runs': len(value['runs']), 'life': value['one_personal_life']}))
        raise SystemExit(bool(value['issues']))
