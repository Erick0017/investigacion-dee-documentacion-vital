"""One declared UI/complete-pair Native calibration, never a physical retry."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
SYSTEM = ROOT / 'sistema'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CALIBRACION_R01'
FROZEN = LAB / 'revisiones/R01_EJECUTADO'
LIFE = 'APD04_CALIB_R01'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    if OUT.exists() or FROZEN.exists() or (SYSTEM / 'estado/vidas' / LIFE).exists():
        raise FileExistsError('R01 exists: inspect it; no repeated import or physical trial')
    OUT.mkdir(parents=True)
    FROZEN.mkdir(parents=True)
    files = [path for path in SYSTEM.rglob('*.py') if '__pycache__' not in path.parts]
    files += list((SYSTEM / 'contratos').glob('*.json'))
    frozen = []
    for path in sorted(set(files)):
        rel = path.relative_to(SYSTEM)
        target = FROZEN / 'sistema' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        before = sha(path)
        shutil.copy2(path, target)
        if sha(target) != before or sha(path) != before:
            raise RuntimeError('Source changed during freeze; no Native calibration started')
        frozen.append({'file': str(rel).replace('\\', '/'), 'sha256': before,
                       'bytes': path.stat().st_size})
    write(FROZEN / 'MANIFEST_FUENTES.json', {'schema': 'APD04.executed_sources.v1',
        'revision': 'R01_EJECUTADO', 'members': frozen,
        'captured_before_native': True})
    event = {'modo': 'apd04-calibrar', 'casos': [
        {'tipo': 'clasifica', 'valor': 19},
        {'tipo': 'clasifica', 'valor': 20},
        {'tipo': 'clasifica', 'valor': 21},
        {'tipo': 'equilibra', 'cargas': [6, 4]},
        {'tipo': 'equilibra', 'cargas': [4, 6]},
        {'tipo': 'equilibra', 'cargas': [6, 6]},
    ]}
    event_path = OUT / 'EVENTO_CALIBRACION.json'
    write(event_path, event)
    script_path = OUT / 'GUION_CALIBRACION.json'
    write(script_path, [['estado'], ['reanudar'],
        ['evento', str(event_path), '--retorno', 'omit'],
        ['guardar'], ['detener'], ['salir']])
    spec = importlib.util.spec_from_file_location('owned_processes', SYSTEM / 'app/process_control.py')
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    argv = [sys.executable, '-I', '-B', '-X', 'utf8',
        str(SYSTEM / 'app/usar_dee.py'), '--raiz', str(ROOT),
        '--nueva', LIFE, '--guion', str(script_path)]
    command = {'argv': argv, 'life': LIFE, 'started_utc': datetime.now(timezone.utc).isoformat(),
        'memory_limit_bytes': 536870912, 'threads': 1,
        'native_parent_pair': 'APD03_MAIN_T604825_R01',
        'native_physical_retries': 0}
    write(OUT / 'COMANDO_ANTES_NATIVE.json', command)
    began = time.monotonic()
    with (OUT / 'UI_STDOUT.txt').open('xb') as stdout, (OUT / 'UI_STDERR.txt').open('xb') as stderr:
        process, job, name = control.spawn_owned(argv, cwd=Path(sys.executable).parent,
            stdout=stdout, stderr=stderr, memory_limit=536870912)
        try:
            process.wait(timeout=420)
            samples = []
            for _ in range(100):
                resources = control.job_resources(job)
                samples.append(resources)
                if not resources.get('job_active_processes'):
                    break
                time.sleep(.05)
            if resources.get('job_active_processes'):
                raise RuntimeError('Owned processes remain after UI exit')
        except BaseException:
            # Only this driver's own complete Job is terminated on safety timeout.
            control.terminate_job(job, 124)
            raise
        finally:
            control.close_job(job)
    changed = [row['file'] for row in frozen if sha(SYSTEM / row['file']) != row['sha256']]
    result = {**command, 'pid': process.pid, 'job': name,
        'exit_code': process.returncode, 'wall_seconds': time.monotonic() - began,
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'resources': resources, 'job_grace_samples': samples,
        'source_files_changed_during_run': changed,
        'no_global_ACTIVO_promotion': True}
    write(OUT / 'EJECUCION.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if process.returncode or changed:
        raise RuntimeError('Calibration run/source stability failed; preserve result, no automatic retry')


if __name__ == '__main__':
    main()
