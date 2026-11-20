"""Three declared histories from ONE exact MAIN prefix; no actor policy here.

Existing OriginalBackend/Supervisor administer full-pair imports and all Native
requests. Configuration changes are local to this driver, never written to the
shared selected-cut contract. Each branch receives the fixed same exogenous
changes; its own actions may legitimately change subsequent environmental facts.
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
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_CONSECUENCIAS_AUX_R01'
FROZEN = LAB / 'revisiones/R05_ATENCION_AUX_EJECUTADO'
PAIR = SYSTEM / 'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PAIR_SHA = '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
SNAPSHOT_SHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
BRANCHES = [
    ('A', 'APD04_ATENCION_REAL_AUX', 'independent_balanced', 'real', 'R03'),
    ('B', 'APD04_ATENCION_OMIT_AUX', 'independent_balanced', 'omit', 'R03'),
    ('C', 'APD04_ATENCION_SENSOR02_AUX', 'independent', 'real', 'R02'),
]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    base = load('attention_existing_driver_helpers', Path(__file__).with_name('ejecutar_calibracion_apd04_r01.py'))
    if OUT.exists() or FROZEN.exists():
        raise FileExistsError('Declared contrast already exists; no repeated histories')
    if base.sha(PAIR / 'EXPORTACION_SERVICIO.json') != PAIR_SHA:
        raise ValueError('The exact complete shared prefix differs; no alternative selected')
    verifier = load('existing_complete_pair_verifier_for_attention', SYSTEM / 'app/importacion_emparejada.py')
    _, manifest, proof = verifier.verify_export(PAIR)
    if manifest['snapshot_sha256'] != SNAPSHOT_SHA or manifest['physical']['tick'] != 639374:
        raise ValueError('Native prefix identity differs')
    for _, life, *_ in BRANCHES:
        if (SYSTEM / 'estado/vidas' / life).exists():
            raise FileExistsError('The declared AUX life exists; do not replace its future')
    OUT.mkdir(parents=True)
    FROZEN.mkdir(parents=True)
    control = load('attention_existing_owned_process_control', SYSTEM / 'app/process_control.py')
    control.protect_current(output=OUT / 'RECURSOS_DRIVER.json', memory_limit=536870912)
    ui = load('attention_existing_single_entry_UI', SYSTEM / 'app/usar_dee.py')
    config = ui.read(SYSTEM / 'contratos/ENTRADA_SENCILLA_APD03.json')
    config.update(source_alias='APD04_EXPLORACION_T639374', source_life='APD04_MAIN',
        source_tick=639374, source_snapshot_sha256=SNAPSHOT_SHA,
        paired_export_manifest_sha256=PAIR_SHA,
        source_paired_export_manifest=(PAIR / 'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    base.write(OUT / 'CONFIGURACION_LOCAL_NO_INSTALADA.json', config)
    frozen = []
    for path in sorted(set(list(SYSTEM.rglob('*.py')) + list((SYSTEM / 'contratos').glob('*.json')))):
        if '__pycache__' in path.parts:
            continue
        relative = path.relative_to(SYSTEM)
        destination = FROZEN / 'sistema' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        digest = base.sha(path)
        shutil.copy2(path, destination)
        if base.sha(path) != digest or base.sha(destination) != digest:
            raise ValueError('Shared sources changed during freeze; no AUX owner started')
        frozen.append({'file': relative.as_posix(), 'sha256': digest, 'bytes': path.stat().st_size})
    base.write(FROZEN / 'MANIFEST_FUENTES.json', {'revision': FROZEN.name, 'members': frozen})
    summaries = []
    for branch, life, sensor, feedback, probe_family in BRANCHES:
        folder = OUT / branch
        folder.mkdir()
        plan = [
            ('change_goal0_stale_caches', {'modo': 'apd04-cambio', 'etiqueta_objetivo': 0,
                'palabra': 'clasifica', 'cargas': [7, 3],
                'mutaciones': [{'fuente': 0, 'valor': 18}, {'fuente': 1, 'valor': 24}]}, 'omit'),
            ('goal0_first4', {'modo': 'apd04-vivir', 'oportunidades': 4,
                'lexico': True, 'sensor': sensor}, feedback),
            ('goal0_next2', {'modo': 'apd04-vivir', 'oportunidades': 2,
                'lexico': True, 'sensor': sensor}, feedback),
            ('change_goal1', {'modo': 'apd04-cambio', 'etiqueta_objetivo': 1}, 'omit'),
            ('goal1_first4', {'modo': 'apd04-vivir', 'oportunidades': 4,
                'lexico': True, 'sensor': sensor}, feedback),
            ('goal1_next2', {'modo': 'apd04-vivir', 'oportunidades': 2,
                'lexico': True, 'sensor': sensor}, feedback),
            ('common_probe_no_quality', {'modo': 'apd04-sensor-calibrar', 'familia': probe_family,
                'pares': [[0, 0], [0, 1], [1, 0], [1, 1]]}, 'omit'),
        ]
        base.write(folder / 'PLAN_ANTES_NATIVE.json', {'branch': branch, 'life': life,
            'common_prefix': proof, 'sensor': sensor, 'return': feedback,
            'stale_environment_cache_preserved': True,
            'events': [{'label': label, 'row': row, 'feedback': mode} for label, row, mode in plan],
            'shared_prefix_not_independent_learner': True, 'teachers_or_reseeding': 0})
        backend = ui.OriginalBackend(ROOT, dict(config))
        session = ui.Supervisor(ROOT, life, backend, dict(config))
        begun = time.monotonic()
        results = []
        with ui.SessionLock(backend.protocol_home / life / 'SUPERVISOR.lock'):
            try:
                card = session.open(new=True)
                if card['parent']['encoded_sha256'] != SNAPSHOT_SHA:
                    raise ValueError('Imported AUX does not have the declared exact parent')
                base.write(folder / 'IMPORTACION_COMPLETA.json', card)
                base.write(folder / 'START.json', session.start())
                base.write(folder / 'REANUDAR.json', session.control('reanudar'))
                for serial, (label, row, mode) in enumerate(plan):
                    request_id = 'apd04_attention_' + branch + '_' + str(serial + 1) + '_' + label
                    result = session.material([row], feedback=mode, actuator='closed', request_id=request_id)
                    base.write(folder / (str(serial + 1) + '_' + label + '.json'), result)
                    results.append({'label': label, 'request_id': request_id,
                                    'status': ui.row_of(result).get('status')})
                    if ui.row_of(result).get('status') != 'completed':
                        raise RuntimeError('Material request not completed; preserve same ID, no retry')
                base.write(folder / 'GUARDAR.json', session.control('guardar'))
                base.write(folder / 'STOP.json', session.control('detener'))
            finally:
                session.close()
        record = backend.record(life)
        summary = {'branch': branch, 'life': life, 'sensor': sensor, 'return': feedback,
            'wall_seconds': time.monotonic() - begun, 'results': results,
            'final_tick': record['physical']['tick'], 'snapshot_sha256': record['snapshot_sha256'],
            'source_files_changed_during_run': [r['file'] for r in frozen if base.sha(SYSTEM / r['file']) != r['sha256']],
            'same_history_only_inside_named_branch': True}
        base.write(folder / 'CIERRE.json', summary)
        summaries.append(summary)
        if summary['source_files_changed_during_run']:
            raise ValueError('Shared source changed; do not attribute the run to frozen bytes')
    base.write(OUT / 'CIERRE_CONTRASTES.json', {'branches': summaries,
        'new_T0': False, 'MAIN_or_ACTIVO_mutated_by_driver': False,
        'source_common_prefix': proof,
        'scope': 'Three dependent AUX histories. A/B differ in material consequences, not total dose-matched; '
                 'C changes physical encoding. No universal attention or P2/R2 verdict.'})
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
