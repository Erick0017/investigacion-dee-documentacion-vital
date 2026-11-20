"""APD04 ACT_R03 SAFE: N0 assembly/import; later explicit Root GO only.

Reuses the existing paired importer, UI Supervisor, literal driver, class8 Job
wrapper and postSTOP sealer. No task decisions or answer-dependent scheduling.
The ten-work original never receives the material diagnostic panel.
"""
import argparse
import ast
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = ROOT/'sistema'
LAB = ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV = ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
CTRL = LAB/'controles_diseno/PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R05'
BUNDLE = HERE/'EJECUTOR_WAIT_R03_SAFE_R01'
PROPOSAL = HERE/'PROPUESTA_ACTUADOR_R03_R02'
PAIR = S/'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PAIR_SHA = '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
SNAP_SHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
CTRL_SHA = '04fde0eb825cf2ecefbfb8df767e696699c65e24530797f6aa4dd2a64c957775'
PROPOSAL_SHA = 'cc097318ed0684274bc6487768cfe65791e2ac7b157c49e8e13ffbc138e09fa4'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_inputs():
    assert sha(CTRL/'MANIFIESTO.json') == CTRL_SHA
    assert sha(PROPOSAL/'MANIFIESTO_PROPUESTA_N0.json') == PROPOSAL_SHA
    assert sha(PAIR/'EXPORTACION_SERVICIO.json') == PAIR_SHA
    assert sha(PAIR/'VIDA.deetsnap.gz') == SNAP_SHA
    for row in read(PROPOSAL/'MANIFIESTO_PROPUESTA_N0.json')['members']:
        assert sha(PROPOSAL/row['file']) == row['proposed_sha256']


def assemble():
    verify_inputs()
    if BUNDLE.exists():
        raise FileExistsError('Preserve the existing assembled revision; no overwrite.')
    BUNDLE.mkdir()
    old_driver = LAB/'ejecucion/ejecutar_plan_apd04_r03.py'
    old_wrapper = LAB/'ejecucion/supervisar_plan_apd04_r03.py'
    driver_text = old_driver.read_text(encoding='utf8')
    old_guard = "    def check_clock():\n        if time.time() >= deadline-closing_reserve:\n            raise TimeoutError('Campaign closing reserve reached; no automatic extension.')\n"
    new_guard = old_guard + "        if time.monotonic()-began >= plan['supervision_wall_limit_seconds']-closing_reserve:\n            raise TimeoutError('Declared local closing reserve reached; preserve the current ID, no extension.')\n"
    assert driver_text.count(old_guard) == 1
    driver_text = driver_text.replace(old_guard, new_guard)
    old_wait = '    def wait_until(offset):\n        target = window_start+offset\n'
    new_wait = '    def wait_until(offset):\n        check_clock()  # Budget applies even when an earlier Native operation made this event late.\n        target = window_start+offset\n'
    assert driver_text.count(old_wait) == 1
    driver_text = driver_text.replace(old_wait, new_wait)
    wrapper_text = old_wrapper.read_text(encoding='utf8').replace("with_name('ejecutar_plan_apd04_r03.py')", "with_name('ejecutar_plan_apd04_r04.py')")
    for name, text in [('ejecutar_plan_apd04_r04.py', driver_text), ('supervisar_plan_apd04_r04.py', wrapper_text)]:
        ast.parse(text)
        with (BUNDLE/name).open('x', encoding='utf8', newline='\n') as stream:
            stream.write(text)
    for source in (old_driver, old_wrapper, Path(__file__)):
        shutil.copy2(source, BUNDLE/('BASE_'+source.name))
    patch = ''.join(difflib.unified_diff(old_driver.read_text(encoding='utf8').splitlines(True), driver_text.splitlines(True), fromfile='existing_driver_R03', tofile='LAB_driver_R04'))
    with (BUNDLE/'DIFF_DRIVER_R04.patch').open('x', encoding='utf8', newline='\n') as stream:
        stream.write(patch)
    proposal_protocol = load('apd04_wait_r03_proposal_literal_only', PROPOSAL/'sistema/app/protocolo_apd04.py')
    for branch in ('REAL', 'OMIT'):
        for kind in ('ORIGINAL', 'PANEL_DIAGNOSTICO'):
            source = CTRL/f'PLAN_WAIT_R03_{branch}_{kind}_DRAFT_R05.json'
            shutil.copy2(source, BUNDLE/source.name)
            plan = read(source)
            # Literal transport validation, not Native admission, physics or cognition.
            for event in plan['events']:
                if event['kind'] == 'material':
                    for row in event['situations']:
                        proposal_protocol.validate_literal(row)
            if kind == 'ORIGINAL':
                works = [e for e in plan['events'] if e.get('situations', [{}])[0].get('modo') == 'apd04-vivir']
                assert len(works) == 10
                assert [e['at_seconds'] for e in works] == list(range(15, 196, 20))
                assert all(e['situations'][0]['sensor'] == 'independent_balanced' for e in works)
                assert not any(e.get('situations', [{}])[0].get('modo') == 'apd03-panel' for e in plan['events'])
    emit(BUNDLE/'VALIDACION_N0.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(), 'new_native_ticks': 0,
        'owner_started': False, 'shared_sistema_modified': False,
        'control_manifest_sha256': CTRL_SHA, 'proposal_manifest_sha256': PROPOSAL_SHA,
        'Root_authorized_only_N0_preparation': True,
        'driver_change': 'Only generic relative closing guard720 and initial clock check on late events; original R03 untouched.',
        'absolute_deadline_unchanged': '2026-10-27T03:30:51+00:00',
        'window_minimum_seconds': 240, 'outer_hard_guard_seconds': 900, 'closing_seconds': 180,
        'main_has_no_material_old_panel': True, 'real_is_prospectively_selected_not_score_selected': True,
        'diagnostic_panel_only_in_new_descendant_of_actual_post10_FULL': True,
        'literal_validation_does_not_establish_Native_admission_or_capability': True})
    members = [{'file': p.relative_to(BUNDLE).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size}
               for p in sorted(BUNDLE.rglob('*')) if p.is_file()]
    emit(BUNDLE/'MANIFIESTO_N0.json', {'schema': 'APD04.WAIT_R03.executor.N0.v1', 'members': members})
    print(json.dumps({'bundle': str(BUNDLE), 'manifest_sha256': sha(BUNDLE/'MANIFIESTO_N0.json'), 'new_native_ticks': 0}))


def request_rows(path):
    connection = sqlite3.connect(Path(path).as_uri()+'?mode=ro&immutable=1', uri=True)
    try:
        return connection.execute('SELECT id,payload,payload_sha,status,result FROM requests ORDER BY id').fetchall()
    finally:
        connection.close()


def import_n0():
    """Existing full pair + UI registration; never calls start/control/material."""
    verify_inputs()
    driver = load('wait_r03_n0_driver_r04', BUNDLE/'ejecutar_plan_apd04_r04.py')
    verifier = load('wait_r03_existing_pair_verifier', S/'app/importacion_emparejada.py')
    _, manifest, proof = verifier.verify_export(PAIR)
    ui = load('wait_r03_existing_ui_N0', S/'app/usar_dee.py')
    observer = load('wait_r03_pure_saved_snapshot_observer', S/'capacidades/observador_causal_retrospectivo_01.py')
    parent = observer.Snapshot(PAIR/'VIDA.deetsnap.gz', verify_checksum=False)
    source_hashes = {str(p): sha(p) for p in S.rglob('*.py') if '__pycache__' not in p.parts}
    protected = {str(S/'estado/ACTIVO.json'): sha(S/'estado/ACTIVO.json'), str(PAIR/'EXPORTACION_SERVICIO.json'): PAIR_SHA}
    config = dict(ui.read(ui.selected_config_path(ROOT)))
    config.update(source_alias='APD04_EXPLORACION_T639374', source_life='APD04_MAIN', source_tick=639374,
        source_snapshot_sha256=SNAP_SHA, paired_export_manifest_sha256=PAIR_SHA,
        source_paired_export_manifest=(PAIR/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    out = EV/'WAIT_R03_IMPORTACIONES_N0_R01'
    if out.exists():
        raise FileExistsError('N0 import attempt exists; preserve it without repeating import.')
    out.mkdir()
    emit(out/'ANTES.json', {'pair_verification': proof, 'config_local_not_installed': config,
        'source_hashes': source_hashes, 'protected': protected, 'new_native_ticks': 0,
        'owner_start_is_not_called': True})
    imported = []
    for branch in ('REAL', 'OMIT'):
        draft = read(CTRL/f'PLAN_WAIT_R03_{branch}_ORIGINAL_DRAFT_R05.json')
        life = draft['life']
        if (S/'estado/vidas'/life).exists() or (S/'estado/entrada_sencilla/vidas'/life).exists():
            raise FileExistsError('Named identity already exists; no replacement or fallback.')
        backend = ui.OriginalBackend(ROOT, dict(config))
        session = ui.Supervisor(ROOT, life, backend, dict(config))
        with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
            card = session.open(new=True)
        assert card['parent']['encoded_sha256'] == SNAP_SHA
        assert card['physical']['tick'] == 639374
        assert backend.process is None and backend.job is None and not session.owned
        child = observer.Snapshot(S/card['snapshot'], verify_checksum=False)
        raw_same = parent.raw == child.raw
        clocks_same = parent.clocks == child.clocks
        assert raw_same and clocks_same
        assert parent.pending == child.pending
        assert parent.receipts == child.receipts
        assert parent.channels == child.channels
        assert request_rows(PAIR/'cola.sqlite3') == request_rows(S/'estado/servicios_persistentes'/life/'cola.sqlite3')
        assert not session.state.get('pending_material') and not session.state.get('uncertain_preserved')
        emit(out/f'{branch}_IMPORTACION.json', {'record': card, 'protocol': session.state,
            'RAW_equal': raw_same, 'clocks_equal': clocks_same, 'channels_pending_receipts_equal': True,
            'SQLite_request_rows_equal': True, 'new_native_ticks': 0, 'owner_started': False,
            'queue_identity_metadata_changes_are_declared_import_mapping_only': True,
            'FNV_internal_not_recomputed': True, 'encoded_SHA_and_manifest_members_verified': True})
        plan = dict(draft)
        plan.update(status='CLOSED_FOR_EXECUTION', initial_snapshot_sha256=card['snapshot_sha256'],
            initial_tick=card['physical']['tick'], world_id=card['world_id'],
            proposed_identity_not_yet_imported=False, native_GO_still_required=True,
            n0_import_proof=(out/f'{branch}_IMPORTACION.json').relative_to(ROOT).as_posix())
        driver.validate_plan(plan)
        emit(BUNDLE/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R01.json', plan)
        imported.append({'life': life, 'snapshot_sha256': card['snapshot_sha256'], 'tick': card['physical']['tick']})
    assert all(sha(path) == value for path, value in source_hashes.items())
    assert all(sha(path) == value for path, value in protected.items())
    emit(out/'CIERRE_N0.json', {'imports': imported, 'new_native_ticks': 0, 'owners_started': 0,
        'shared_source_hashes_unchanged': True, 'protected_unchanged': True,
        'full_pair_not_T0': True, 'actuator_R03_not_yet_prepared': True})
    print(json.dumps({'imports': imported, 'new_native_ticks': 0, 'out': str(out)}, ensure_ascii=False))


def execute(branch):
    """Future explicit GO; never silently imports, retries or runs a panel."""
    verify_inputs()
    for item in read(PROPOSAL/'MANIFIESTO_PROPUESTA_N0.json')['members']:
        if sha(ROOT/item['file']) != item['proposed_sha256']:
            raise ValueError('Accepted exact R03 not installed by Root; no owner starts.')
    plan_path = BUNDLE/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R01.json'
    out = EV/f'WAIT_R03_{branch}_ORIGINAL_R01'
    if out.exists():
        raise FileExistsError('An attempted future is preserved; never repeat automatically.')
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(BUNDLE/'supervisar_plan_apd04_r04.py'),
        '--root', str(ROOT), '--plan', str(plan_path), '--out', str(out), '--root-go', 'APD04_LITERAL_PLAN_CLOSED']
    result = subprocess.run(command, cwd=Path(sys.executable).parent)
    if result.returncode:
        raise RuntimeError('Adverse/incomplete trajectory retained; no seal, fallback or diagnostic replay.')
    final = read(out/'TRAYECTORIA/RESULTADO.json')
    if final['error'] or not final['owner_stop_confirmed'] or final['final_protocol'].get('pending_material') or final['final_protocol'].get('uncertain_preserved'):
        raise ValueError('PostSTOP completeness not established; preserve the actual future.')
    events = [json.loads(line) for line in (out/'TRAYECTORIA/EVENTOS.jsonl').read_text(encoding='utf8').splitlines()]
    work_ids = {e['request_id'] for e in read(plan_path)['events'] if e.get('situations', [{}])[0].get('modo') == 'apd04-vivir'}
    completed = [e for e in events if e['kind'] == 'scheduled_material_result' and e.get('requested_id') in work_ids]
    if len(completed) != 10:
        raise ValueError('Not all ten scheduled work results were recorded; no full-completion claim.')
    card = final['final_record']
    seal_out = out/'SELLO_POST10_N0'
    target = f"{card['life_id']}_T{card['physical']['tick']}_POST10_PRE_PANEL_R01"
    seal_command = [sys.executable, '-I', '-B', '-X', 'utf8', str(LAB/'ejecucion/sellar_corte_poststop_apd04_n0_r01.py'),
        '--root', str(ROOT), '--life', card['life_id'], '--tick', str(card['physical']['tick']),
        '--snapshot-sha256', card['snapshot_sha256'], '--target-name', target, '--out', str(seal_out),
        '--scope', 'ACT_R03 original post10 actual FULL before any material old/new panel; diagnostic descendants only.',
        '--root-go', 'APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
    subprocess.run(seal_command, cwd=Path(sys.executable).parent, check=True)
    print(json.dumps({'branch': branch, 'life': card['life_id'], 'tick': card['physical']['tick'],
        'snapshot_sha256': card['snapshot_sha256'], 'post10_seal': str(seal_out), 'material_panel_in_original': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--assemble-n0', action='store_true')
    modes.add_argument('--import-n0', choices=('ROOT_GO_IMPORT_FULL_ONLY_ZERO_TICKS',))
    modes.add_argument('--execute-after-go', choices=('ROOT_GO_WAIT_R03_NATIVE',))
    parser.add_argument('--branch', choices=('REAL', 'OMIT'))
    args = parser.parse_args()
    if args.assemble_n0:
        assemble()
    elif args.import_n0:
        import_n0()
    else:
        if args.branch is None:
            parser.error('One explicitly selected branch is required; never choose by score.')
        execute(args.branch)


if __name__ == '__main__':
    main()
