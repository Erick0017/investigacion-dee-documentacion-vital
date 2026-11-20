"""One P0 admission on the same stopped CALIB_R02; no word lessons/queries."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import importlib.util
import json
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
SYSTEM = ROOT / 'sistema'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ADMISION_LEXICA_R01'
FROZEN = LAB / 'revisiones/R03_LEX_ADMISION_EJECUTADO'
LIFE = 'APD04_CALIB_R02'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-go', required=True, choices=['APD04_LEX_P0_ONLY_REVIEWED'])
    parser.parse_args()
    base = load('calibration_driver_helpers', Path(__file__).with_name('ejecutar_calibracion_apd04_r01.py'))
    if OUT.exists() or FROZEN.exists():
        raise FileExistsError('Admission attempt exists; preserve it, no retry')
    before_record = json.loads((SYSTEM / 'estado/vidas' / LIFE / 'VIDA.json').read_text(encoding='utf8'))
    if before_record['physical']['tick'] != 605489:
        raise ValueError('Another continuation exists; do not rewind to the calibration cut')
    OUT.mkdir(parents=True)
    FROZEN.mkdir(parents=True)
    base.write(OUT / 'VIDA_ANTES.json', before_record)
    files = list(SYSTEM.rglob('*.py')) + list((SYSTEM / 'contratos').glob('*.json'))
    frozen = []
    for path in sorted(set(files)):
        if '__pycache__' in path.parts:
            continue
        relative = path.relative_to(SYSTEM)
        copied = FROZEN / 'sistema' / relative
        copied.parent.mkdir(parents=True, exist_ok=True)
        digest = base.sha(path)
        shutil.copy2(path, copied)
        if base.sha(path) != digest or base.sha(copied) != digest:
            raise ValueError('Source changed while freezing, no Native admission started')
        frozen.append({'file': relative.as_posix(), 'sha256': digest, 'bytes': path.stat().st_size})
    base.write(FROZEN / 'MANIFEST_FUENTES.json', {'revision': FROZEN.name,
        'members': frozen, 'captured_before_native': True})
    event = OUT / 'EVENTO_ADMISION_P0.json'
    base.write(event, {'modo': 'apd04-lex-admitir'})
    script = OUT / 'GUION.json'
    base.write(script, [['estado'], ['reanudar'],
        ['evento', str(event), '--retorno', 'omit'], ['guardar'], ['detener'], ['salir']])
    argv = [sys.executable, '-I', '-B', '-X', 'utf8', str(SYSTEM / 'app/usar_dee.py'),
        '--raiz', str(ROOT), '--vida', LIFE, '--guion', str(script)]
    base.write(OUT / 'COMANDO_ANTES_NATIVE.json', {'argv': argv,
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'classification': 'Prepared P0 extension only, no acquired signs',
        'teaching_or_word_queries': 0, 'physical_retries': 0})
    process_control = load('admission_owned_processes', SYSTEM / 'app/process_control.py')
    began = time.monotonic()
    with (OUT / 'UI_STDOUT.txt').open('xb') as stdout, (OUT / 'UI_STDERR.txt').open('xb') as stderr:
        process, job, name = process_control.spawn_owned(argv,
            cwd=Path(sys.executable).parent, stdout=stdout, stderr=stderr,
            memory_limit=536870912)
        try:
            process.wait(timeout=300)
            for _ in range(100):
                resources = process_control.job_resources(job)
                if not resources.get('job_active_processes'):
                    break
                time.sleep(.05)
            if resources.get('job_active_processes'):
                raise RuntimeError('Owned processes remain; not a closed cut')
        except BaseException:
            process_control.terminate_job(job, 124)
            raise
        finally:
            process_control.close_job(job)
    changed = [row['file'] for row in frozen if base.sha(SYSTEM / row['file']) != row['sha256']]
    base.write(OUT / 'EJECUCION.json', {'exit_code': process.returncode,
        'pid': process.pid, 'job_name': name, 'wall_seconds': time.monotonic() - began,
        'resources': resources, 'source_files_changed_during_run': changed,
        'classification': 'P0 preparation, not teaching or acquired Spanish'})
    if process.returncode or changed:
        raise RuntimeError('Preserved admission/source failure; no automatic retry or export as success')
    prior = load('existing_poststop_sealer', ROOT / 'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    ui = load('actual_existing_ui_for_N0_export', SYSTEM / 'app/usar_dee.py')
    sealed = prior.stopped_pair(ROOT, ui, LIFE, OUT / 'PREFIJO_LEX_P0_POSTSTOP',
        allow_queued=False,
        scope='Exact same CALIB_R02 after P0 two-slot same-K extension, zero word lessons or word queries. Common source for future separate causal histories; not MAIN acquired memory.')
    base.write(OUT / 'PAR_COMPLETO_POSTSTOP.json', sealed)
    print(json.dumps({'life': LIFE, 'tick': sealed['record']['physical']['tick'],
        'snapshot_sha256': sealed['record']['snapshot_sha256'],
        'pair_manifest_sha256': sealed['manifest_sha256'],
        'paired_members': sealed['verification']['members_verified'],
        'new_native_ticks_in_sealing': sealed['new_native_ticks_in_sealing'],
        'classification': 'Prepared P0 only; no teaching or word use'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
