"""Root: one predeclared crossed opportunity23 through the ACTUAL product CLI.

Requires an already COMMITTED PI04 principal. Opens only its existing bounded
owner, then uses the public manager state/opportunity commands and closes it.
No cloning, preparation, teaching, selection, promotion, retry or hidden policy.
"""
from pathlib import Path
import datetime
import json
import sys

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
PY = C / 'motor/python313/python.exe'
LIFE = 'ECI02_PI03_REPRO_PI04_MAIN_02'
TAG = 'PI04_PRINCIPAL_PUBLICO_CROSS23_R01'


def main():
    sys.path.insert(0, str(P / 'codigo'))
    from pi04_verificacion_cli_publica_R01 import read, sha, fresh_queue_ids, cli_request, recorded_row
    out = P / 'control/USO_PRINCIPAL_PI04_POR_GESTOR.json'
    stage = P / 'control/USO_PRINCIPAL_PI04_POR_GESTOR_EN_CURSO.json'
    if out.exists() or stage.exists(): raise ValueError('An earlier attempt is preserved. Inspect its SAME IDs; never rerun')
    if (C / 'reproducibilidad/EJECUCION_MATERIAL.lock').exists() or list((S / 'estado/locks').glob('*.lock')):
        raise ValueError('Another known material owner may be active; no second writer')
    active = read(S / 'estado/ACTIVO.json'); project = read(C / 'PROYECTO.json')
    personal = read(S / 'estado/genesis/SELECCION_PERSONAL.json')
    card = read(S / 'estado/vidas' / LIFE / 'VIDA.json')
    if active['life_id'] != LIFE or project['selected_life'] != LIFE or personal['life_id'] != LIFE or card['life_id'] != LIFE or card['physical']['N'] != 67:
        raise ValueError('Use only the actually selected N67 principal; this script never changes any selector')
    promotions = [json.loads(line) for line in (S / 'estado/PROMOCIONES.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
    commit = next((r for r in reversed(promotions) if r.get('phase') == 'COMMITTED' and r.get('life_id') == LIFE), None)
    if commit is None or commit['snapshot_sha256'] != card['snapshot_sha256']:
        raise ValueError('The exact current adopted cut must have a Native COMMITTED witness before this one new use')
    ids = [TAG + '_STATE', TAG + '_USE', TAG + '_FINAL']
    preflight = fresh_queue_ids(S, LIFE, ids)
    record = {'schema': 'DEE.PI04.actual_principal_public_CLI_use.v1', 'status': 'STARTING',
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'life_id': LIFE,
        'prior_card': {'path': str(S / 'estado/vidas' / LIFE / 'VIDA.json'), 'sha256': sha(S / 'estado/vidas' / LIFE / 'VIDA.json'),
            'physical': card['physical'], 'snapshot_sha256': card['snapshot_sha256']},
        'Native_COMMITTED': commit, 'read_only_preflight': preflight, 'explicit_ids': ids,
        'automatic_retry': False, 'selectors_modified_by_this_script': False}
    with stage.open('x', encoding='utf8') as f: json.dump(record, f, ensure_ascii=False, indent=2); f.write('\n')
    try:
        from servicio_ensayo_R02 import Owner
        with Owner(LIFE, TAG, S) as owner:
            state = cli_request(PY, S, LIFE, 'pi04-coordinacion-estado', ids[0], P / 'ensayos')
            initial = state['result']['native_result']; v = initial['result']['rows'][0]
            progress, device = v['progress'], v['device']
            if initial['before_tick'] != initial['after_tick'] or initial['after_tick'] != card['physical']['tick']:
                raise ValueError('Public state must be0 Native ticks at the actual current adopted cut')
            if progress['ordinal'] != 23 or progress['arm'] != 'real' or not progress['admitted'] or any(progress.get(k) for k in ('pending', 'uncertain', 'halted_reason')):
                raise ValueError('Only the coherent predeclared real opportunity23 may be used')
            if device['ordinal'] != 23 or len(device['resources']) != 26 or any(device.get(k) for k in ('pending', 'feedback_pending', 'uncertain')):
                raise ValueError('Exact finite26-resource device with three offers remaining is required; no replenishment')
            use = cli_request(PY, S, LIFE, 'pi04-coordinacion-oportunidad', ids[1], P / 'ensayos', material=True)
            q = owner.q.get(ids[1]); assert q['status'] == 'completed'
            primary = P / 'ensayos' / (ids[1] + '.json')
            with primary.open('x', encoding='utf8') as f: json.dump(q, f, ensure_ascii=False, indent=2); f.write('\n')
            actual = json.loads(q['result']); r = actual['result']['rows'][0]; row = recorded_row(actual, primary)
            # All values below are evaluator-only, after the actual output.
            assert r['ordinal'] == 23 and r['arm'] == 'real'
            assert r['spec']['context'] == 6 and [r['spec']['left'], r['spec']['right']] == [6, 5]
            assert r['first_reader']['choice'] == 1 and r['selected_operation'] == 'suma'
            assert r['actual_numeric_result'] == 11 and r['second_native_use']['reader']['choice'] == -1
            assert r['applied_route'] == -1 and r['useful_product'] is True
            assert not r['first_NULL_preserved'] and not r['first_rejected_preserved']
            assert row['Native_inputs']['unique_requested'] == row['Native_inputs']['applied'] == 186
            assert row['Native_inputs']['rejected_or_other'] == 0
            assert actual['after_tick'] - actual['before_tick'] == 782
            product = r['actual_effect']['product']
            file = S / 'estado/servicios_locales' / LIFE / 'PI04_C2C_COORDINACION_R01/dispositivo' / product['path']
            content = file.read_bytes()
            assert len(content) == product['bytes'] == 64 and sha(file) == product['sha256'] and int.from_bytes(content[:2], 'little') == 11
            final_cli = cli_request(PY, S, LIFE, 'pi04-coordinacion-estado', ids[2], P / 'ensayos')
            final = final_cli['result']['native_result']; fv = final['result']['rows'][0]
            assert final['before_tick'] == final['after_tick'] == actual['after_tick']
            assert fv['progress']['ordinal'] == fv['device']['ordinal'] == 24 and len(fv['device']['resources']) == 26
            assert len(fv['device']['products']) == len(device['products']) + 1
            owner.sample(force=True)
        final_card = read(S / 'estado/vidas' / LIFE / 'VIDA.json')
        assert final_card['physical']['tick'] == actual['after_tick']
        assert read(S / 'estado/ACTIVO.json')['life_id'] == LIFE and read(C / 'PROYECTO.json')['selected_life'] == LIFE
        record.update(status='COMPLETED_ACTUAL_PRODUCT_CLI_USE', owner_closed=True,
            initial=initial, final=final, public_CLI={'state': state, 'use': use, 'final_state': final_cli},
            row=row, new_native_ticks=782, actual_new_inputs_unique=186, actual_new_inputs_applied=186,
            actual_new_product={'path': str(file), 'bytes': len(content), 'sha256': sha(file), 'actual_integer': 11},
            remaining_offers=2, final_cut={'life_id': LIFE, 'N':67, 'T':actual['after_tick'],
                'snapshot_sha256': final_card['snapshot_sha256'], 'physical':final_card['physical']},
            finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            scope='Operator-triggered public CLI use of the one committed continuation. Native first choice selects SUM and its actual11 selects the negative Native route. Prepared sequence/codecs/finite environment; no new initiative or general planning claim.')
        with out.open('x', encoding='utf8') as f: json.dump(record, f, ensure_ascii=False, indent=2); f.write('\n')
        print(json.dumps({'proof':str(out), 'sha256':sha(out), 'life_id':LIFE,
            'final_tick':actual['after_tick'], 'Native_ticks':782, 'products':1, 'remaining_offers':2},ensure_ascii=False))
    except BaseException as e:
        failure = P / 'control/USO_PRINCIPAL_PI04_POR_GESTOR_FALLO_PRESERVADO.json'
        with failure.open('x', encoding='utf8') as f:
            json.dump({'status':'FAILED_ATTEMPT_PRESERVED','error':repr(e),'life_id':LIFE,'ids':ids,
                'automatic_retry':False,'no_queue_or_pending_cleanup':True,
                'instruction':'Inspect the existing SAME transport IDs and actual current card before any continuation; never invoke this runner again to repeat an ambiguous material request.'},f,ensure_ascii=False,indent=2);f.write('\n')
        raise


if __name__ == '__main__': main()
