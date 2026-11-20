"""PostSTOP-only N0 seal for the actual early persistent reserve.

Does not run an owner, Native query, new experience, retry, or favorable restore.
All actual partial/adverse states remain identified. A full capture is not a
certificate of useful access, completed sixty minutes, or successful promotion.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'sistema/gestionar.py').is_file())
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/RESERVA60_PERSISTENCIA_TEMPRANA_REAL_R01'
CLOSED = LAB / 'controles_diseno/RESERVA60_PERSISTENCIA_TEMPRANA_CERRADA_R01'
LIFE = 'APD04_PERSISTENCIA_TEMPRANA_RESERVA_R01'
SEALER = LAB / 'ejecucion/sellar_corte_poststop_apd04_n0_r01.py'


def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p, value):
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def main():
    a = argparse.ArgumentParser(description=__doc__)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument('--validate-n0', action='store_true')
    g.add_argument('--seal-after-actual-STOP', choices=('ROOT_GO_EARLY_RESERVE_ACTUAL_CLOSURE_N0',))
    args = a.parse_args()
    if args.validate_n0:
        ast.parse(Path(__file__).read_text(encoding='utf8'))
        print(json.dumps({'Native_ticks': 0, 'owners_started': 0, 'closure_not_read_or_assumed': True,
            'source_SHA': sha(Path(__file__)), 'existing_sealer_SHA': sha(SEALER)}))
        return
    if (EV / 'CIERRE_BRAZO_Y_RESUMEN_N0.json').exists(): raise FileExistsError('Already closed; preserve bytes')
    final = read(EV / 'TRAYECTORIA/RESULTADO.json')
    sup = read(EV / 'RESULTADO_SUPERVISION.json')
    if sup['final_total_job']['job_active_processes'] != 0:
        raise ValueError('Owner tree not stopped; do not inspect/save a fictional full future')
    card = final['final_record']
    if card['life_id'] != LIFE: raise ValueError('Wrong actual life; no fallback')
    frozen = read(CLOSED / 'CIERRE_PROSPECTIVO_N0.json')['freeze_sources']
    source_unchanged = all(sha(ROOT / rel) == value for rel, value in frozen.items())
    seal = None; error = None
    if final['owner_stop_confirmed']:
        tick = card['physical']['tick']
        command = [sys.executable, '-I', '-B', '-X', 'utf8', str(SEALER), '--root', str(ROOT),
            '--life', LIFE, '--tick', str(tick), '--snapshot-sha256', card['snapshot_sha256'],
            '--target-name', LIFE + '_T' + str(tick) + '_RESERVA_PLAN60_CORTE_R01',
            '--out', str(EV / 'SELLO_FINAL_N0'), '--scope',
            'Exact reached early persistent reserve future, including failure, partial coverage and pending protocol. Not a certificate of sixty completed minutes or useful cognition.',
            '--root-go', 'APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
        try:
            subprocess.run(command, cwd=Path(sys.executable).parent, check=True)
            seal = read(EV / 'SELLO_FINAL_N0/CORTE_COMPLETO_POSTSTOP.json')
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc), 'no_state_or_pending_ID_replaced': True}
    else:
        error = {'scope': 'Unclean STOP: last committed snapshot plus unresolved transport retained, not a complete captured in-memory future. No operational FULL claim.'}
    emit(EV / 'CIERRE_BRAZO_Y_RESUMEN_N0.json', {
        'arm': 'EARLY_PERSISTENT_REAL', 'actual_final': final, 'supervision': sup,
        'postSTOP_seal': seal, 'seal_error': error, 'source_hashes_unchanged': source_unchanged,
        'no_new_Native_ticks_or_owner_or_retry': True,
        'actual_plan_SHA': sha(CLOSED / 'PLAN_RESERVA60_PERSISTENCIA_TEMPRANA_CERRADO_R01.json'),
        'actual_last_committed_snapshot_SHA': card['snapshot_sha256'],
        'pending_ID_preserved': (final['final_protocol'].get('pending_material') or {}).get('id'),
        'not_a_promotion_certificate_or_query_result': True,
    })
    print(json.dumps({'Native_ticks': 0, 'life': LIFE, 'actual_tick': card['physical']['tick'],
        'actual_clean_STOP': final['owner_stop_confirmed'], 'full_seal': seal is not None,
        'source_hashes_unchanged': source_unchanged, 'error': error}))


if __name__ == '__main__': main()
