"""N0 timing-only close of ACT_R03 executor: local600, hard900, no Native.

Preserves the earlier720s revision exactly. Requires the actual N0 imported
child identities and closed literal plans, never imports another life itself.
"""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = HERE/'EJECUTOR_WAIT_R03_SAFE_R01'
TARGET = HERE/'EJECUTOR_WAIT_R03_SAFE_R02'
EV = ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def close_n0():
    proof = read(EV/'WAIT_R03_IMPORTACIONES_N0_R01/CIERRE_N0.json')
    assert proof['new_native_ticks'] == 0 and proof['owners_started'] == 0
    if TARGET.exists():
        raise FileExistsError('Preserve the existing closed executor; no overwrite.')
    TARGET.mkdir()
    source = BASE/'ejecutar_plan_apd04_r04.py'
    before = source.read_text(encoding='utf8')
    assert before.count("plan['supervision_wall_limit_seconds']-closing_reserve") == 1
    after = before.replace("plan['supervision_wall_limit_seconds']-closing_reserve", "plan['local_closing_start_seconds']")
    for path in BASE.iterdir():
        if path.is_file() and path.name not in ('MANIFIESTO_N0.json', 'ejecutar_plan_apd04_r04.py') and not path.name.endswith('_CERRADO_R01.json'):
            shutil.copy2(path, TARGET/path.name)
    with (TARGET/source.name).open('x', encoding='utf8', newline='\n') as stream:
        stream.write(after)
    ast.parse(after)
    with (TARGET/'DIFF_GUARD_720_A_600_N0.patch').open('x', encoding='utf8', newline='\n') as stream:
        stream.write(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='LAB720_NOT_EXECUTED', tofile='LAB600_NOT_EXECUTED')))
    for branch in ('REAL', 'OMIT'):
        plan = read(BASE/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R01.json')
        plan.update(local_closing_start_seconds=600,
            local_closing_hard_guard_seconds=900,
            owner_cleanup_budget_seconds=300,
            prior_720_guard_revision='Preserved N0 only; never executed Native.',
            native_GO_still_required=True)
        assert plan['duration_seconds'] == 240
        assert plan['supervision_wall_limit_seconds'] == 900
        assert plan['deadline_utc'] == '2026-10-27T03:30:51+00:00'
        emit(TARGET/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R02.json', plan)
    shutil.copy2(__file__, TARGET/Path(__file__).name)
    emit(TARGET/'CIERRE_PROSPECTIVO_N0_R02.json', {
        'new_native_ticks': 0, 'owners_started': 0, 'shared_sistema_modified': False,
        'local_closing_start_seconds': 600, 'hard_guard_seconds': 900,
        'nominal_window_seconds': 240, 'maximum_shutdown_allowance_seconds': 300,
        'deadline_utc_unchanged': '2026-10-27T03:30:51+00:00',
        'changes_do_not_depend_on_Native_outcomes': True,
        'old720_revision_preserved': str(BASE), 'same_imported_children_no_reimport': proof['imports'],
        'main_original_has_no_material_panel': True,
        'scope': 'Host supervision revision only; no physical protocol, decoder, target or experience change.'})
    emit(TARGET/'MANIFIESTO_N0.json', {'members': [
        {'file': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size}
        for p in sorted(TARGET.iterdir()) if p.is_file()]})
    print(json.dumps({'bundle': str(TARGET), 'manifest_sha256': sha(TARGET/'MANIFIESTO_N0.json'), 'new_native_ticks': 0}))


def execute(branch):
    # Root will call only after installing its exact accepted three-file patch.
    proposal = read(HERE/'PROPUESTA_ACTUADOR_R03_R02/MANIFIESTO_PROPUESTA_N0.json')
    for row in proposal['members']:
        if sha(ROOT/row['file']) != row['proposed_sha256']:
            raise ValueError('Accepted R03 source bytes are not installed; no Native.')
    out = EV/f'WAIT_R03_{branch}_ORIGINAL_R02'
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(TARGET/'supervisar_plan_apd04_r04.py'),
        '--root', str(ROOT), '--plan', str(TARGET/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R02.json'),
        '--out', str(out), '--root-go', 'APD04_LITERAL_PLAN_CLOSED']
    code = subprocess.run(command, cwd=Path(sys.executable).parent).returncode
    if code:
        return code  # Preserve every actual pending/adverse future; no replay.
    final = read(out/'TRAYECTORIA/RESULTADO.json')
    if (final['error'] or not final['owner_stop_confirmed'] or final['final_protocol'].get('pending_material')
            or final['final_protocol'].get('uncertain_preserved') or not final['frozen_sources_unchanged']):
        raise ValueError('Actual clean stopped continuation is not established; no favorable substitute.')
    plan = read(TARGET/f'PLAN_WAIT_R03_{branch}_ORIGINAL_CERRADO_R02.json')
    work_ids = {e['request_id'] for e in plan['events'] if e.get('situations', [{}])[0].get('modo') == 'apd04-vivir'}
    events = [json.loads(line) for line in (out/'TRAYECTORIA/EVENTOS.jsonl').read_text(encoding='utf8').splitlines()]
    results = [e for e in events if e['kind'] == 'scheduled_material_result' and e.get('requested_id') in work_ids]
    if len(results) != 10 or any(e['result'].get('request', e['result']).get('status') != 'completed' for e in results):
        raise ValueError('Not all ten work requests completed; retain actual trajectory without a ten-work claim.')
    card = final['final_record']
    target = f"{card['life_id']}_T{card['physical']['tick']}_POST10_PRE_PANEL_R01"
    seal = ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/sellar_corte_poststop_apd04_n0_r01.py'
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(seal), '--root', str(ROOT),
        '--life', card['life_id'], '--tick', str(card['physical']['tick']), '--snapshot-sha256', card['snapshot_sha256'],
        '--target-name', target, '--out', str(out/'SELLO_POST10_N0'),
        '--scope', 'Actual ACT_R03 post10 original before any material old22/new2 panel. REAL prospectively selected; OMIT control.',
        '--root-go', 'APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
    subprocess.run(command, cwd=Path(sys.executable).parent, check=True)
    print(json.dumps({'branch': branch, 'life': card['life_id'], 'tick': card['physical']['tick'],
        'snapshot_sha256': card['snapshot_sha256'], 'seal': str(out/'SELLO_POST10_N0'),
        'material_panel_in_original': False}, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--close-n0', action='store_true')
    modes.add_argument('--execute-after-go', choices=('ROOT_GO_WAIT_R03_NATIVE_R02',))
    parser.add_argument('--branch', choices=('REAL', 'OMIT'))
    args = parser.parse_args()
    if args.close_n0:
        close_n0()
    else:
        if args.branch is None:
            parser.error('Select one explicit branch, not the favorable result.')
        raise SystemExit(execute(args.branch))
