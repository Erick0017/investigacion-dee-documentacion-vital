"""Finite coupled-regulation trajectories; all scoring is post-evolution audit."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import sys
import time
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from integracion.quantity_core import physical
from regulacion_acoplada.aparato import CoupledRegulationSession


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', required=True)
    parser.add_argument('--medium', type=int, choices=(-1, 1), required=True)
    parser.add_argument('--reference', type=int, required=True)
    parser.add_argument('--objects', type=int, nargs=2, required=True)
    parser.add_argument('--routing', choices=('onpath', 'offpath'), default='onpath')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), Path(__file__).with_name('aparato.py'), ROOT / 'src/integracion/quantity_core.py',
             ROOT / 'src/regulacion_consecuencia/native_feedback_component.py']
    executed = args.out / 'executed_source'
    executed.mkdir()
    for path in paths:
        shutil.copyfile(path, executed / path.name)
    frozen = {'schema': 'CPC8R.coupled.regulation.frozen.v1', 'case_id': args.case, 'medium': args.medium,
              'actual_reference': args.reference, 'actual_objects': args.objects, 'routing': args.routing,
              'frozen_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': {path.relative_to(ROOT).as_posix(): sha(path) for path in paths},
              'hypothesis_before_evolution': 'V2 currentconsequence selectsP/Q; six neutral initial encounters route selected114 into opposite counterflow at78. With firstgradient+X, P should preserve reference/use137; with firstgradient−X,Q should. Opposite contexts/offpath and latecut/sham distinguish helping from harmful irrelevant matter.',
              'criterion': 'Both actual operands and active native gradient must match at70 and137. A direction alone with damaged/absent reference is not a retained comparison.',
              'host_MAIN_RAW_clock_edits': [], 'component_regulator_inputs_afterT0': 0, 'horizon': 141}
    put(args.out / 'CONFIG.json', frozen)
    started, cpu = time.monotonic(), time.process_time()
    session = CoupledRegulationSession.create(medium=args.medium, routing=args.routing)
    session.curriculum(args.reference, tuple(args.objects))
    snapshots = []
    result = {'case_id': args.case, 'schema': 'CPC8R.coupled.regulation.measurements.v1', 'status': 'RUNNING',
              'configuration': frozen, 'geometry': session.geometry, 'preparations': 1, 'diagnostic_forks': 0, 'continuations': 0,
              'frames': [], 'host_MAIN_RAW_clock_edits': []}
    for tick in (0, 2, 3, 4, 5, 9, 10, 11, 12, 15, 18, 19, 31, 46, 52, 53, 54, 55, 65, 66, 68, 69, 70,
                 71, 72, 76, 77, 78, 79, 80, 85, 86, 87, 90, 100, 130, 135, 136, 137, 138, 141):
        session.run_until(tick)
        result['frames'].append(session.capture())
        if tick in (0, 4, 11, 54, 70, 77, 78, 79, 141):
            snapshots.append(session.save(args.out / ('T' + str(tick) + '.deetsnap.gz')))
        result.update(last_complete_tick=tick, requests=session.receipts(), elapsed_seconds=time.monotonic() - started)
        put(args.out / 'INCREMENTAL.json', result)
    readings = []
    for index, tick in enumerate((70, 137)):
        before = next(frame['quantity'] for frame in result['frames'] if frame['tick'] == tick - 1)
        after = next(frame['quantity'] for frame in result['frames'] if frame['tick'] == tick)
        reference, current, output = before['reference_site'], before['object_site'], after['center']
        er, eo = args.reference + 5, args.objects[index] + 5
        direction = [(er > eo) - (er < eo), 0, 0]
        operands = reference['active'] and reference['s_reg'] == er and current['active'] and current['s_reg'] == eo
        readings.append({'tick': tick, 'reference': reference, 'object': current, 'output': output,
                         'auditor_expected_reference': er, 'auditor_expected_object': eo, 'auditor_expected_direction': direction,
                         'actual_operands_preserved': operands, 'qualified': operands and output['active'] and output['direction'] == direction})
    result.update(status='MEASURED', readings=readings, requests=session.receipts(), snapshots=snapshots,
                  final_physical=physical(session.world), elapsed_seconds=time.monotonic() - started, cpu_seconds=time.process_time() - cpu)
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'case': args.case, 'readings': readings, 'counterflows78': next(frame['counterflows'] for frame in result['frames'] if frame['tick'] == 78), 'seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    main()
