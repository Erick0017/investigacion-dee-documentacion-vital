"""Fresh one-Runtime candidate: MCTS plus finite native consequence-policy V2."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import shutil
import sys
import time
import traceback
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from regulacion_consecuencia.mcts import ConsequenceMagnitudeCTSSession as MagnitudeCTSSession
from integracion.relational_pair import physical, move
from comunicacion.run_contact_social_regulated import SOURCES


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    configuration = ROOT / 'configuraciones/regulacion_consecuencia/MCTS_V2_CONGELADO.json'
    cfg = json.loads(configuration.read_text(encoding='utf-8'))
    case = next(item for item in cfg['cases'] if item['id'] == args.case)
    sources = SOURCES + ['src/transferencia_magnitud/' + name for name in ('transferencia.py', 'cts_integrado.py', 'run_cts.py')] + ['src/regulacion_consecuencia/' + name for name in ('native_feedback_component.py', 'mcts.py', 'run.py')]
    hashes = {}
    for relative in sources:
        target = args.out / 'executed_source' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
        hashes[relative] = sha(target)
    put(args.out / 'CONFIG.json', cfg)
    started, cpu = time.monotonic(), time.process_time()
    result = {'schema': 'CPC8R.consequenceMagnitudeCTS.measurements.v1', 'case': case, 'status': 'RUNNING', 'source_sha256': hashes,
              'configuration_sha256': sha(configuration), 'preparations': 0, 'diagnostic_forks': 0, 'continuations': 0,
              'frames': [], 'snapshots': [], 'host_RAW_clock_edits_on_MAIN': [], 'recipient_reference_experience_calls': 0}
    prepkeys = ('guard_mode', 'actor_mode', 'include_order', 'include_contact', 'event_state_offset', 'medium_load', 'actor_state', 'quantity_guards', 'regulation', 'consequence_medium')
    try:
        session = MagnitudeCTSSession.create(identifier=case['id'], **{key: value for key, value in case.items() if key in prepkeys})
        result['preparations'] = 1
        result['geometry'] = session.geometry
        session.curriculum(**{key: value for key, value in case.items() if key not in ('id', *prepkeys)})
        boundaries = {0, 3, 31, 69, 70, 73, 76, 79, 80, 86, 89, 110, 137, 143, 146, 147, 165, 170, 204, 206,
                      213, 214, 268, 271, 280, 281, 338, 340, 344, 348, 405, 411, 415, 417, 428, 472, 478, 484,
                      486, 487, 499, 500, 539, 549, 553, 554, 558, 559, 563, 616}
        boundaries.update((1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15, 18))
        for tick in sorted(boundaries):
            session.run_until(tick)
            frame = session.view()
            frame['mode'].pop('captures', None)
            frame['mode'].pop('social_captures', None)
            result['frames'].append(frame)
            if tick in (0, 4, 15, 18, 73, 80, 147, 281, 549, 616):
                path = args.out / ('T' + str(tick) + '.deetsnap.gz')
                storage = session.save(path)
                result['snapshots'].append({'path': path.name, 'physical': physical(session.world), 'storage': storage})
            result.update(last_complete_tick=tick, requests=session.receipts(), elapsed_seconds=time.monotonic() - started)
            put(args.out / 'MEASUREMENTS.json', result)
        readings = []
        for index, tick in enumerate((147, 214, 281)):
            pre = next(frame['magnitude_transfer'] for frame in result['frames'] if frame['tick'] == tick - 1)
            post = next(frame['magnitude_transfer'] for frame in result['frames'] if frame['tick'] == tick)
            reference, current, output = pre['reference_site'], pre['object_site'], post['center']
            expected_reference, expected_object = case['magnitude_value'] + 5, case['magnitude_objects'][index] + 5
            direction = [(expected_reference > expected_object) - (expected_reference < expected_object), 0, 0]
            operands = reference['active'] and reference['s_reg'] == expected_reference and current['active'] and current['s_reg'] == expected_object
            readings.append({'tick': tick, 'reference': reference, 'object': current, 'output': output,
                             'auditor_expected_reference': expected_reference, 'auditor_expected_object': expected_object,
                             'auditor_expected_direction': direction, 'operands_preserved': operands,
                             'qualified': operands and output['active'] and output['direction'] == direction})
        result.update(status='MEASURED', final_physical=physical(session.world), magnitude_readings=readings,
                      quantity_observations=session.quantity.state['observations'], magnitude_observations=session.state['magnitude_observations'],
                      contact_social_observations=session.state['contact_social_observations'], consequence_policy_observations=session.state['consequence_policy_observations'], initiative_captures=session.initiative.state['captures'],
                      return_use_observations=session.state['return_use_observations'], renewal_observations=session.state['renewal_observations'],
                      mode_captures=session.mode.state['captures'], social_captures=session.mode.state.get('social_captures', []),
                      receipt_statuses=dict(Counter(row['receipt']['status'] for row in session.receipts())),
                      cpu_seconds=time.process_time() - cpu, elapsed_seconds=time.monotonic() - started)
    except BaseException as error:
        result.update(status='TECHNICAL_ERROR', error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'case': args.case, 'magnitude': readings, 'old_word616': result['frames'][-1]['joint'],
                      'social_contact': [(row['receiver'], row.get('covered'), row.get('content')) for row in result['contact_social_observations'] if row['tick'] == 554],
                      'seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    main()

