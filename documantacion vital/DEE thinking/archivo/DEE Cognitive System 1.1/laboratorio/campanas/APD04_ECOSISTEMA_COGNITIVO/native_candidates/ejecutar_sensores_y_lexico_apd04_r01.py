"""Two shared-prefix AUX sensory calibrations, then same CALIB_R02 P0 admission.

No expected action is passed to either actor. SOURCE R02/R03 is selected once
per AUX, not after its responses. Generic SUCCESS/omit completes traces without
task feedback. Original failed AUX and protected lives are never overwritten.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
SYSTEM = ROOT / 'sistema'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/SENSORES_Y_LEXICO_R01'
FROZEN = LAB / 'revisiones/R04_SENSOR_Y_LEX_EJECUTADO'
FORWARD = [[0, 0], [0, 1], [1, 0], [1, 1]]
REVERSED = list(reversed(FORWARD))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    base = load('native_pilot_helpers', Path(__file__).with_name('ejecutar_calibracion_apd04_r01.py'))
    if OUT.exists() or FROZEN.exists():
        raise FileExistsError('Declared R01 exists: no physical retry or overwrite')
    for family in ('R02', 'R03'):
        if (SYSTEM / 'estado/vidas' / ('APD04_SENSOR_' + family + '_AUX')).exists():
            raise FileExistsError('Sensor AUX already exists; no re-import or favorable rewind')
    old = json.loads((SYSTEM / 'estado/vidas/APD04_CALIB_R02/VIDA.json').read_text(encoding='utf8'))
    if old['physical']['tick'] != 605501:
        raise ValueError('The CALIB_R02 life continued elsewhere; do not substitute its earlier cut')
    sys.path.insert(0, str(SYSTEM))
    from app.cola_local import validate_request
    events = {family: [dict(modo='apd04-sensor-calibrar', familia=family, pares=pairs)
                       for pairs in (FORWARD, REVERSED)] for family in ('R02', 'R03')}
    for rows in events.values():
        for row in rows:
            validate_request({'operacion': 'sesion', 'situaciones': [row], 'retorno': 'omit', 'actuador': 'closed'})
    validate_request({'operacion': 'sesion', 'situaciones': [{'modo': 'apd04-lex-admitir'}],
                      'retorno': 'omit', 'actuador': 'closed'})
    OUT.mkdir(parents=True)
    FROZEN.mkdir(parents=True)
    frozen = []
    paths = list(SYSTEM.rglob('*.py')) + list((SYSTEM / 'contratos').glob('*.json'))
    for path in sorted(set(paths)):
        if '__pycache__' in path.parts:
            continue
        relative = path.relative_to(SYSTEM)
        target = FROZEN / 'sistema' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = base.sha(path)
        shutil.copy2(path, target)
        if base.sha(path) != digest or base.sha(target) != digest:
            raise ValueError('Source changed while freezing; no Native owner started')
        frozen.append({'file': relative.as_posix(), 'sha256': digest, 'bytes': path.stat().st_size})
    base.write(FROZEN / 'MANIFEST_FUENTES.json', {'revision': FROZEN.name, 'members': frozen})
    control = load('sensor_owned_process_control', SYSTEM / 'app/process_control.py')
    summaries = []

    def run(life, rows, *, new, label):
        folder = OUT / label
        folder.mkdir()
        tokens = [['estado'], ['reanudar']]
        for index, row in enumerate(rows):
            event_path = folder / ('EVENTO_' + str(index + 1) + '.json')
            base.write(event_path, row)
            tokens.append(['evento', str(event_path), '--retorno', 'omit'])
        tokens += [['guardar'], ['detener'], ['salir']]
        script = folder / 'GUION.json'
        base.write(script, tokens)
        argv = [sys.executable, '-I', '-B', '-X', 'utf8', str(SYSTEM / 'app/usar_dee.py'),
            '--raiz', str(ROOT), '--nueva' if new else '--vida', life, '--guion', str(script)]
        base.write(folder / 'COMANDO_ANTES_NATIVE.json', {'argv': argv,
            'started_utc': datetime.now(timezone.utc).isoformat(), 'threads': 1,
            'native_job_memory_bytes': 536870912, 'shared_prefix_not_independent_learners': True,
            'new_T0': False, 'physical_retries': 0})
        began = time.monotonic()
        with (folder / 'UI_STDOUT.txt').open('xb') as stdout, (folder / 'UI_STDERR.txt').open('xb') as stderr:
            process, job, name = control.spawn_owned(argv, cwd=Path(sys.executable).parent,
                stdout=stdout, stderr=stderr, memory_limit=536870912)
            try:
                process.wait(timeout=600)
                for _ in range(100):
                    resources = control.job_resources(job)
                    if not resources.get('job_active_processes'):
                        break
                    time.sleep(.05)
                if resources.get('job_active_processes'):
                    raise RuntimeError('Owned processes remain after UI close')
            except BaseException:
                control.terminate_job(job, 124)
                raise
            finally:
                control.close_job(job)
        record = json.loads((SYSTEM / 'estado/vidas' / life / 'VIDA.json').read_text(encoding='utf8'))
        summary = {'label': label, 'life': life, 'pid': process.pid, 'job': name,
            'exit_code': process.returncode, 'wall_seconds': time.monotonic() - began,
            'resources': resources, 'final_tick': record['physical']['tick'],
            'snapshot_sha256': record['snapshot_sha256'],
            'source_files_changed_during_run': [r['file'] for r in frozen if base.sha(SYSTEM / r['file']) != r['sha256']]}
        base.write(folder / 'EJECUCION.json', summary)
        summaries.append(summary)
        if process.returncode or summary['source_files_changed_during_run']:
            raise RuntimeError('Preserved sensor/admission failure; no automatic retry')
        return record

    for family in ('R02', 'R03'):
        run('APD04_SENSOR_' + family + '_AUX', events[family], new=True, label='SENSOR_' + family)
    record = run('APD04_CALIB_R02', [{'modo': 'apd04-lex-admitir'}], new=False, label='LEX_DIAGONAL_P0')
    operation = [row for row in record['operations'] if row['kind'] == 'PERSISTENT_SESION'][-1]
    raw = json.loads((SYSTEM / 'estado/servicios_persistentes/APD04_CALIB_R02' / operation['result_file']).read_text(encoding='utf8'))
    outcome = raw['result']['rows'][0]
    admitted = outcome['kind'] == 'APD04_explicit_shared_lexical_P0_extension'
    sealer = load('existing_exact_poststop_sealer', ROOT / 'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    ui = load('existing_actual_ui_for_N0_pair', SYSTEM / 'app/usar_dee.py')
    target = OUT / ('LEX_DIAGONAL_ADMITTED_POSTSTOP' if admitted else 'LEX_DIAGONAL_REJECTED_POSTSTOP')
    pair = sealer.stopped_pair(ROOT, ui, 'APD04_CALIB_R02', target, allow_queued=False,
        scope='Exact stopped CALIB_R02 after diagonal lexical admission attempt. '
              'admitted=' + str(admitted) + '; zero lessons and zero word queries. '
              'No auxiliary state transferred into MAIN.')
    base.write(OUT / 'PAR_LEXICO_POSTSTOP.json', pair)
    result = {'runs': summaries, 'lexical_P0_admitted': admitted,
        'lexical_result_primary': operation, 'postSTOP_pair': {
            'directory': str(target), 'manifest_sha256': pair['manifest_sha256'],
            'snapshot_sha256': record['snapshot_sha256'],
            'verification': pair['verification']},
        'word_teaching_and_queries': 0, 'no_ACTIVO_change': True}
    base.write(OUT / 'CIERRE.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
