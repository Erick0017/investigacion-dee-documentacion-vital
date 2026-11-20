"""Root-authorized logistics only; existing FULL import, UI and bounded driver.

Four sequential same-prefix AUX futures. No Native API, actor policy, source
edit, reset, adaptive schedule, material retry or protected-state replacement.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
S = ROOT / 'sistema'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/NIVELES_BREVES_AUX_R02'
PROPOSAL = HERE / 'PROPUESTA_NIVELES_BREVE_N0_R02'
PAIR = S / 'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PAIR_SHA = '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
SNAP = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_bytes())
def load(name, p):
    x = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(x); x.loader.exec_module(m); return m
def write(p, v):
    with p.open('x', encoding='utf8', newline='\n') as f: json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root-go', choices=('APD04_FOUR_SHORT_AUX_AUTHORIZED',), required=True); ap.parse_args()
    if sys.version_info[:2] != (3, 13): raise ValueError('Use the existing compatible CPython3.13')
    if OUT.exists(): raise FileExistsError('Never repeat/rewrite a prior four-arm attempt')
    if sha(PAIR / 'EXPORTACION_SERVICIO.json') != PAIR_SHA: raise ValueError('Predeclared full source pair differs')
    manifest = read(PROPOSAL / 'MANIFIESTO.json')
    for item in manifest['members']:
        if sha(PROPOSAL / item['file']) != item['sha256']: raise ValueError('Pre-GO brief proposal changed')
    ui = load('authorized_existing_single_UI', S / 'app/usar_dee.py')
    driver = load('authorized_existing_literal_validator', LAB / 'ejecucion/ejecutar_plan_apd04_r03.py')
    sealer = load('existing_stopped_paired_export_only', ROOT / 'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    config = ui.read(ui.selected_config_path(ROOT))
    config.update(source_alias='APD04_EXPLORACION_T639374', source_life='APD04_MAIN', source_tick=639374,
                  source_snapshot_sha256=SNAP, paired_export_manifest_sha256=PAIR_SHA,
                  source_paired_export_manifest=(PAIR / 'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    if config['memory_limit_bytes'] != 536870912: raise ValueError('Keep existing512MiB Native owner contract')
    for n in (2, 5, 10, 20):
        p = read(PROPOSAL / ('PLAN_BREVE_N' + str(n) + '_DRAFT_R02.json'))
        if (S / 'estado/vidas' / p['life']).exists(): raise FileExistsError('Proposed AUX identity already exists: ' + p['life'])
    OUT.mkdir(); frozen = OUT / 'FUENTES_LOGISTICA_EJECUTADA'; frozen.mkdir()
    source_paths = [Path(__file__), LAB / 'ejecucion/ejecutar_plan_apd04_r03.py', LAB / 'ejecucion/supervisar_plan_apd04_r03.py',
                    S / 'app/usar_dee.py', S / 'app/process_control.py', S / 'app/importacion_emparejada.py']
    first = read(PROPOSAL / 'PLAN_BREVE_N2_DRAFT_R02.json')
    source_paths += [ROOT / p for p in first['freeze_source_paths']]
    sources = []
    for i, p in enumerate(dict.fromkeys(source_paths)):
        q = frozen / (str(i).zfill(2) + '_' + p.name); b = p.read_bytes()
        with q.open('xb') as f: f.write(b)
        sources.append({'source': str(p), 'copy': q.relative_to(OUT).as_posix(), 'sha256': hashlib.sha256(b).hexdigest()})
    write(OUT / 'PLAN_LOGISTICO_CERRADO_ANTES_IMPORT.json', {'root_authorization': 'APD04_FOUR_SHORT_AUX_AUTHORIZED',
          'parent_pair_sha256': PAIR_SHA, 'parent_snapshot_sha256': SNAP, 'parent_tick': 639374,
          'same_prefix_dependent_forks_not_independent_learners': True, 'four_sequential_only': True,
          'proposal_manifest_sha256': sha(PROPOSAL / 'MANIFIESTO.json'), 'sources': sources,
          'config_local_not_installed': config, 'total_guard_seconds': 2400,
          'per_branch_nominal_window180_outer480': True, 'driver_runs_late_events_without_rescheduling_offsets': True})
    started = time.monotonic(); summaries = []; protected = sha(S / 'estado/ACTIVO.json')
    env = dict(os.environ); env.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    for n in (2, 5, 10, 20):
        if time.monotonic() - started >= 2400 - 510: raise TimeoutError('No new arm without its original480s budget and import margin')
        if any(sha(Path(x['source'])) != x['sha256'] for x in sources): raise ValueError('Frozen source changed; no next import')
        p = read(PROPOSAL / ('PLAN_BREVE_N' + str(n) + '_DRAFT_R02.json')); life = p['life']
        folder = OUT / ('N' + str(n)); folder.mkdir(); backend = ui.OriginalBackend(ROOT, dict(config))
        session = ui.Supervisor(ROOT, life, backend, dict(config))
        with ui.SessionLock(backend.protocol_home / life / 'SUPERVISOR.lock'):
            card = session.open(new=True)
            if card['parent']['encoded_sha256'] != SNAP or card['physical']['tick'] != 639374 or card['physical']['N'] != 67:
                raise ValueError('Imported full past differs; preserve without starting an owner')
            write(folder / 'IMPORTACION_FULL_Y_REGISTRO_UI.json', {'record': card, 'protocol': session.state,
                  'same_complete_parent_SHA': SNAP, 'no_new_native_tick_in_import': True})
        p.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256=card['snapshot_sha256'], initial_tick=card['physical']['tick'])
        p['scope'] += ' Here2/5/10/20count external sources, not Native lattice N(always67). Closed after this actual complete import and UI registration.'
        driver.validate_plan(p); plan_path = folder / 'PLAN_CERRADO_CON_ESTADO_REAL.json'; write(plan_path, p)
        command = [sys.executable, '-I', '-B', '-X', 'utf8', str(LAB / 'ejecucion/supervisar_plan_apd04_r03.py'),
                   '--root', str(ROOT), '--plan', str(plan_path), '--out', str(folder / 'SUPERVISION'),
                   '--root-go', 'APD04_LITERAL_PLAN_CLOSED']
        write(folder / 'ANTES_WRAPPER.json', {'command': command, 'plan_sha256': sha(plan_path),
                  'logistics_code_sha256': sha(Path(__file__)), 'only_one_AUX_owner_may_run': True,
                  'Native_owner_limit': 536870912, 'outer_whole_tree_limit_existing': 1073741824,
                  'OMP_NUM_THREADS': '1', 'wall_utc': datetime.now(timezone.utc).isoformat()})
        print(json.dumps({'ARM_STARTED': n, 'life': life, 'parent_tick': 639374,
                         'initial_snapshot_sha256': card['snapshot_sha256'], 'plan_sha256': sha(plan_path),
                         'nominal_window': 180, 'outer_wall_guard': 480}, ensure_ascii=False), flush=True)
        with (folder / 'WRAPPER_STDOUT.txt').open('xb') as stdout, (folder / 'WRAPPER_STDERR.txt').open('xb') as stderr:
            process = subprocess.run(command, cwd=Path(sys.executable).parent, env=env, stdout=stdout, stderr=stderr)
        supervision_path = folder / 'SUPERVISION/RESULTADO_SUPERVISION.json'
        if not supervision_path.exists(): raise RuntimeError('Wrapper did not publish owned-tree closure; stop sequence without replacement')
        supervision = read(supervision_path)
        active = supervision.get('final_total_job', {}).get('job_active_processes')
        if active != 0: raise RuntimeError('No proof all previous AUX descendants stopped; never start next')
        final = backend.record(life); paired = None; seal_error = None
        try:
            target = S / 'estado/fuentes_emparejadas' / (life + '_T' + str(final['physical']['tick']) + '_BREVE_R02')
            paired = sealer.stopped_pair(ROOT, ui, life, target, allow_queued=True,
                    scope='Actual reached brief source-count AUX future. May contain preserved pending operations after wall guard; not MAIN or a successful-capability certificate.')
            write(folder / 'PAR_POSTSTOP.json', paired)
        except BaseException as exc:
            seal_error = {'type': type(exc).__name__, 'message': str(exc), 'local_full_state_and_journal_preserved': True}
            write(folder / 'ERROR_SELLO_POSTSTOP.json', seal_error)
        result = {'sources': n, 'life': life, 'parent_snapshot_sha256': SNAP, 'initial_record': card,
                  'final_record': final, 'wrapper_returncode': process.returncode, 'supervision': supervision,
                  'paired': paired, 'seal_error': seal_error, 'same_prefix_not_independent_learner': True,
                  'no_automatic_retry_or_rewind': True, 'shared_sources_unchanged': all(sha(Path(x['source'])) == x['sha256'] for x in sources),
                  'protected_ACTIVO_unchanged': sha(S / 'estado/ACTIVO.json') == protected}
        write(folder / 'CIERRE_RAMA.json', result); summaries.append(result)
        print(json.dumps({'ARM_CLOSED': n, 'tick': final['physical']['tick'], 'wrapper_exit': process.returncode,
                          'all_owned_processes_stopped': active == 0, 'sealed_pair': paired is not None,
                          'seal_error': seal_error}, ensure_ascii=False), flush=True)
        if not result['shared_sources_unchanged'] or not result['protected_ACTIVO_unchanged']:
            raise ValueError('Sources/protected active changed; stop next arm')
    write(OUT / 'CIERRE_CUATRO_RAMOS.json', {'branches': summaries, 'total_wall_seconds': time.monotonic() - started,
          'Native_physical_replays': 0, 'same_full_prefix_forks': 4,
          'no_MAIN_learning_merge_no_ACTIVO_replacement': True})
    print(json.dumps({'FOUR_ARMS_FINISHED': len(summaries), 'wall_seconds': time.monotonic() - started}), flush=True)


if __name__ == '__main__': main()
