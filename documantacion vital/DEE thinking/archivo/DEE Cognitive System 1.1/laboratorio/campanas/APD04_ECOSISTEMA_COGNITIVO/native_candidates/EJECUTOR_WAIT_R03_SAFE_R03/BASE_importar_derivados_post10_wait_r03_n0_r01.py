"""Existing N0 full-pair importer for actual ACT_R03 post10 descendants only.

Never substitutes SAFE, a control's memories or the currently advancing REAL.
The immutable, already sealed complete post10 pair is the sole source. Import
does not start an owner, prepare an actuator, probe knowledge or advance ticks.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = ROOT/'sistema'
EV = ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
CTRL = ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/controles_diseno/PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R05'
BUNDLE = HERE/'EJECUTOR_WAIT_R03_SAFE_R02'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def requests(path):
    con = sqlite3.connect(Path(path).as_uri()+'?mode=ro&immutable=1', uri=True)
    try:
        return con.execute('SELECT id,payload,payload_sha,status,result FROM requests ORDER BY id').fetchall()
    finally:
        con.close()


def imported_descendant(kind, branch):
    if kind == 'semilla' and branch != 'REAL':
        raise ValueError('Collaborator seed is prospectively REAL only, never a score-selected OMIT control.')
    original = EV/f'WAIT_R03_{branch}_ORIGINAL_R02'
    final = read(original/'TRAYECTORIA/RESULTADO.json')
    if final['error'] or not final['owner_stop_confirmed'] or final['final_protocol'].get('pending_material') or final['final_protocol'].get('uncertain_preserved'):
        raise ValueError('The actual original did not finish operationally clean; no replacement prefix is allowed.')
    seal_path = original/'SELLO_POST10_N0/CORTE_COMPLETO_POSTSTOP.json'
    seal = read(seal_path)
    assert seal['new_native_ticks'] == 0 and seal['new_owner_started'] is False
    pair = Path(seal['pair']['directory']).resolve(strict=True)
    if not pair.is_relative_to(S/'estado/fuentes_emparejadas'):
        raise ValueError('Only the existing local full-state repository is accepted.')
    verifier = load('post10_wait_existing_pair_verifier', S/'app/importacion_emparejada.py')
    _, manifest, verified = verifier.verify_export(pair)
    expected = f'APD04_WAIT_R03_{branch}_AUX_R05'
    if manifest['life_id'] != expected or manifest['snapshot_sha256'] != final['final_record']['snapshot_sha256']:
        raise ValueError('Not the exact actual post10 original; SAFE and other futures are rejected.')
    assert manifest['physical']['tick'] == final['final_record']['physical']['tick'] > 639374
    ui = load('post10_wait_existing_ui', S/'app/usar_dee.py')
    observer = load('post10_wait_pure_saved_observer', S/'capacidades/observador_causal_retrospectivo_01.py')
    identity = 'APD04_SEMILLA_COLABORADOR_R01' if kind == 'semilla' else expected+'_PANEL_DIAGNOSTICO'
    out = EV/f'WAIT_R03_{branch}_{kind.upper()}_IMPORTACION_N0_R01'
    if out.exists() or (S/'estado/vidas'/identity).exists() or (S/'estado/entrada_sencilla/vidas'/identity).exists():
        raise FileExistsError('An attempted identity is preserved; no reimport, rewind or fallback.')
    protected_paths = [S/'estado/ACTIVO.json', pair/'EXPORTACION_SERVICIO.json', pair/'VIDA.deetsnap.gz']
    before = {str(p): sha(p) for p in protected_paths}
    source_hashes = {str(p): sha(p) for p in S.rglob('*.py') if '__pycache__' not in p.parts}
    config = dict(ui.read(ui.selected_config_path(ROOT)))
    config.update(source_alias='ACT_R03_ACTUAL_POST10_'+branch, source_life=manifest['life_id'],
        source_tick=manifest['physical']['tick'], source_snapshot_sha256=manifest['snapshot_sha256'],
        paired_export_manifest_sha256=sha(pair/'EXPORTACION_SERVICIO.json'),
        source_paired_export_manifest=(pair/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    out.mkdir()
    shutil.copy2(__file__, out/Path(__file__).name)
    emit(out/'ANTES_N0.json', {'actual_full_pair': str(pair), 'manifest_sha256': sha(pair/'EXPORTACION_SERVICIO.json'),
        'seal_source_sha256': sha(seal_path), 'verification': verified, 'local_config_not_installed': config,
        'protected_hashes': before, 'source_hashes': source_hashes, 'new_native_ticks': 0})
    backend = ui.OriginalBackend(ROOT, config)
    session = ui.Supervisor(ROOT, identity, backend, config)
    with ui.SessionLock(backend.protocol_home/identity/'SUPERVISOR.lock'):
        card = session.open(new=True)
    parent = observer.Snapshot(pair/'VIDA.deetsnap.gz', verify_checksum=False)
    child = observer.Snapshot(S/card['snapshot'], verify_checksum=False)
    assert card['parent']['encoded_sha256'] == manifest['snapshot_sha256']
    assert parent.raw == child.raw and parent.clocks == child.clocks
    assert parent.channels == child.channels and parent.pending == child.pending and parent.receipts == child.receipts
    assert requests(pair/'cola.sqlite3') == requests(S/'estado/servicios_persistentes'/identity/'cola.sqlite3')
    assert backend.process is None and backend.job is None and not session.owned
    assert not session.state.get('pending_material') and not session.state.get('uncertain_preserved')
    assert all(sha(p) == h for p, h in before.items())
    assert all(sha(p) == h for p, h in source_hashes.items())
    proof = {'identity': identity, 'kind': kind, 'branch': branch, 'record': card, 'protocol': session.state,
        'actual_full_pair': str(pair), 'manifest_sha256': sha(pair/'EXPORTACION_SERVICIO.json'),
        'RAW_clocks_channels_pending_receipts_equal': True, 'SQLite_request_rows_equal': True,
        'new_native_ticks': 0, 'owner_started': False, 'material_queries': 0,
        'protected_and_shared_sources_unchanged': True, 'FNV_not_recomputed': True,
        'knowledge_is_inherited_not_new_acquisition': True}
    emit(out/'IMPORTACION_N0.json', proof)
    if kind == 'diagnostico':
        plan = read(CTRL/f'PLAN_WAIT_R03_{branch}_PANEL_DIAGNOSTICO_DRAFT_R05.json')
        plan.update(status='CLOSED_FOR_EXECUTION', life=identity, world_id=card['world_id'],
            initial_snapshot_sha256=card['snapshot_sha256'], initial_tick=card['physical']['tick'],
            proposed_identity_not_yet_imported=False, local_closing_start_seconds=600,
            owner_cleanup_budget_seconds=300, native_GO_still_required=True,
            required_parent_complete_pair=pair.relative_to(ROOT).as_posix(),
            required_parent_snapshot_sha256=manifest['snapshot_sha256'],
            required_parent_tick=manifest['physical']['tick'])
        driver = load('post10_wait_literal_driver_only', BUNDLE/'ejecutar_plan_apd04_r04.py')
        driver.validate_plan(plan)
        emit(out/'PLAN_PANEL_DIAGNOSTICO_CERRADO_R01.json', plan)
    print(json.dumps({'life': identity, 'kind': kind, 'tick': card['physical']['tick'],
        'snapshot_sha256': card['snapshot_sha256'], 'proof': str(out/'IMPORTACION_N0.json'),
        'new_native_ticks': 0, 'owner_started': False}, ensure_ascii=False), flush=True)


def execute_diagnostic(branch):
    for row in read(HERE/'PROPUESTA_ACTUADOR_R03_R02/MANIFIESTO_PROPUESTA_N0.json')['members']:
        if sha(ROOT/row['file']) != row['proposed_sha256']:
            raise ValueError('Root accepted exact R03 source bytes are required before Native.')
    plan = EV/f'WAIT_R03_{branch}_DIAGNOSTICO_IMPORTACION_N0_R01/PLAN_PANEL_DIAGNOSTICO_CERRADO_R01.json'
    out = EV/f'WAIT_R03_{branch}_PANEL_DIAGNOSTICO_R01'
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(BUNDLE/'supervisar_plan_apd04_r04.py'),
        '--root', str(ROOT), '--plan', str(plan), '--out', str(out), '--root-go', 'APD04_LITERAL_PLAN_CLOSED']
    return subprocess.run(command, cwd=Path(sys.executable).parent).returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=('semilla', 'diagnostico'), default='diagnostico')
    parser.add_argument('--branch', choices=('REAL', 'OMIT'), default='REAL')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--validate-n0', action='store_true')
    mode.add_argument('--import-after-go', choices=('ROOT_GO_ACT_R03_ACTUAL_POST10_IMPORT_N0',))
    mode.add_argument('--execute-after-go', choices=('ROOT_GO_ACT_R03_DIAGNOSTIC_NATIVE',))
    args = parser.parse_args()
    if args.validate_n0:
        ast.parse(Path(__file__).read_text(encoding='utf8'))
        print(json.dumps({'AST_valid': True, 'new_native_ticks': 0, 'owner_started': False,
            'post10_pair_not_accessed_yet': True, 'source_sha256': sha(__file__)}))
    elif args.import_after_go:
        imported_descendant(args.kind, args.branch)
    else:
        if args.kind != 'diagnostico':
            parser.error('The collaborator seed never receives material diagnostics.')
        raise SystemExit(execute_diagnostic(args.branch))
