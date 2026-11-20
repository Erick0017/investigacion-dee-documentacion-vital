"""Root: continue the EXISTING admitted link-cut life once; no clone or prepare.

The failed prequeue CLI attempt is preserved. New explicit IDs are proved unused
before opening the sole owner; any ambiguity stops without a retry.
"""
from pathlib import Path
import json
import sys

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = P / 'estados/candidato_R02/sistema'
PY = C / 'motor/python313/python.exe'
LIFE = 'ECI02_PI03_REPRO_PI04_C2C_LINK_CUT_01'
TAG = 'PI04_C2C_LINK_CUT1_OP3_R01'


def main():
    sys.path.insert(0, str(P / 'codigo'))
    from pi04_verificacion_cli_publica_R01 import read, sha, fresh_queue_ids, cli_request, recorded_row
    out = P / 'control' / (TAG + '.json')
    if out.exists(): raise ValueError('Existing LINK result preserved; no second use')
    if (C / 'reproducibilidad/EJECUCION_MATERIAL.lock').exists() or list((S / 'estado/locks').glob('*.lock')):
        raise ValueError('Another known Native owner may be active; no parallel writer')
    if read(S / 'estado/vidas' / LIFE / 'VIDA.json')['physical']['tick'] != 800379:
        raise ValueError('Continue the exact existing 0-tick prepared/admitted LINK prefix, no restoration')
    identifiers = [TAG + '_CLI_STATE', TAG + '_OP_0', TAG + '_CLI_FINAL']
    old = 'PI04_C2C_LINK_CUT1_R01_CLI_STATE'
    preflight = fresh_queue_ids(S, LIFE, identifiers, absent_historical=(old,))
    from servicio_ensayo_R02 import Owner
    with Owner(LIFE, TAG, S) as owner:
        state = cli_request(PY, S, LIFE, 'pi04-coordinacion-estado', identifiers[0], P / 'ensayos', diagnostic=True)
        initial = state['result']['native_result']; progress = initial['result']['rows'][0]['progress']
        if initial['before_tick'] != initial['after_tick'] or initial['after_tick'] != 800379:
            raise ValueError('The public state command unexpectedly advanced Native time')
        if progress['ordinal'] != 0 or progress['arm'] != 'link_cut' or not progress['admitted'] or any(progress.get(k) for k in ('pending', 'uncertain', 'halted_reason')):
            raise ValueError('The existing LINK is not the coherent admitted ordinal0 future')
        use = cli_request(PY, S, LIFE, 'pi04-coordinacion-oportunidad', identifiers[1], P / 'ensayos', diagnostic=True, material=True)
        q = owner.q.get(identifiers[1]); assert q['status'] == 'completed'
        primary = P / 'ensayos' / (identifiers[1] + '.json')
        with primary.open('x', encoding='utf8') as f: json.dump(q, f, ensure_ascii=False, indent=2); f.write('\n')
        actual = json.loads(q['result']); r = actual['result']['rows'][0]; row = recorded_row(actual, primary)
        # Evaluation only AFTER the actual Native operation/effect completed.
        assert r['arm'] == 'link_cut' and r['ordinal'] == 0
        assert r['first_reader']['choice'] == -1 and r['selected_operation'] == 'diferencia'
        assert r['actual_numeric_result'] == 7 and r['second_native_use']['second_sensor_called'] is False
        assert r['applied_route'] is None and r['useful_product'] is False
        assert row['Native_inputs']['unique_requested'] == row['Native_inputs']['applied'] == 182
        assert row['Native_inputs']['rejected_or_other'] == 0
        assert actual['after_tick'] - actual['before_tick'] == 782
        final_cli = cli_request(PY, S, LIFE, 'pi04-coordinacion-estado', identifiers[2], P / 'ensayos', diagnostic=True)
        final = final_cli['result']['native_result']; assert final['before_tick'] == final['after_tick'] == actual['after_tick']
        owner.sample(force=True)
    proof = {'schema': 'DEE.PI04.C2C.actual_batch.R01', 'life': LIFE, 'arm': 'link_cut', 'tag': TAG,
        'start_ordinal': 0, 'stop_exclusive': 1, 'offered': 1, 'completed': 1, 'products': 0,
        'arithmetic_correct': 1, 'arithmetic_attempted': 1, 'rows': [row], 'initial': initial, 'final': final,
        'owner_closed': True, 'new_native_ticks': 782, 'source_world_or_control_histories_not_merged': True,
        'original_principal_modified': False, 'status': 'COMPLETED_REQUESTED_BATCH', 'stop_reason': None,
        'public_manager_CLI_test': {'state': state, 'use': use, 'final_state': final_cli},
        'continuation_without_clone_prepare_or_admit': True, 'read_only_preflight': preflight,
        'prior_failed_attempt': {'id': old, 'proved_absent_from_queue_before_resume': True,
            'stderr_path': str(P / 'ensayos' / (old + '.stderr.txt')), 'stderr_sha256': sha(P / 'ensayos' / (old + '.stderr.txt'))},
        'scope': 'Existing link-cut future resumed via fixed public CLI. An omitted second input is not measured NULL or arithmetic failure; the actual negative effect is retained. No retry of the old prequeue ID.'}
    with out.open('x', encoding='utf8') as f: json.dump(proof, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'proof': str(out), 'sha256': sha(out), 'Native_ticks': 782, 'products': 0, 'public_CLI_actual': True}))


if __name__ == '__main__': main()
