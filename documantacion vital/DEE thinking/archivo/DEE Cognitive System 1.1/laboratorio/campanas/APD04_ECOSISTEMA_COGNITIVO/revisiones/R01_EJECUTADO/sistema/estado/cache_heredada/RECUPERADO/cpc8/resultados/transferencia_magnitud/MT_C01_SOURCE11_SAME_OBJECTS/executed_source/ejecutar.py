"""Native-only magnitude-transfer discovery/confirmation on a frozen geometry."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import gc
import hashlib
import json
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import save_world_snapshot
from integracion.quantity_core import physical
from transferencia_magnitud.transferencia import prepare_standalone, attach_recipient, schedule_source, move


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def observe(world, site):
    return exact_observation(world.runtime.observe(d.Coordinate(*site)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', required=True)
    parser.add_argument('--value', type=int, required=True)
    parser.add_argument('--objects', type=int, nargs=3, required=True)
    parser.add_argument('--mode', choices=('paired', 'unpaired', 'omitted'), default='paired')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started, cpu = time.monotonic(), time.process_time()
    source_paths = [Path(__file__), Path(__file__).with_name('transferencia.py'), ROOT / 'src/integracion/quantity_core.py']
    executed = args.out / 'executed_source'
    executed.mkdir()
    for path in source_paths:
        shutil.copyfile(path, executed / path.name)
    frozen = {'schema': 'CPC8R.magnitude.transfer.frozen.v1', 'frozen_utc': datetime.now(timezone.utc).isoformat(),
              'case_id': args.case, 'source_actual_value': args.value, 'source_mode': args.mode, 'current_objects': args.objects,
              'source_sha256': {path.relative_to(ROOT).as_posix(): sha(path) for path in source_paths},
              'prediction_before_evolution': 'Source value+5 should survive native zero-load two-turn route, become recipient reference at80, and remain comparable at147/214/281 without any B reference experience call.',
              'criterion': 'Exact actual operands and native active gradient sign: recipient reference equals source+5; currentobject equals actual+5; direction Xsign(reference-object),Y/Z0; reader must be active. A missingoperand is not numericalzero.',
              'horizon': 285, 'host_RAW_clock_edits_on_MAIN': [], 'prepared_geometries': 1}
    put(args.out / 'FROZEN.json', frozen)
    world, geometry = prepare_standalone()
    recipient = attach_recipient(world, geometry)
    requests = schedule_source(world, args.value, args.mode)
    for index, value in enumerate(args.objects):
        recipient.present_object(value, reference_time=77, round_index=index)
    recipient.reader_opportunity(reference_time=77)
    snapshots = []
    frames = []
    for tick in (0, 3, 66, 67, 68, 69, 70, 71, 72, 73, 77, 78, 79, 80, 81, 82, 83, 84,
                 142, 143, 144, 145, 146, 147, 148, 149, 209, 213, 214, 215, 276, 280, 281, 282, 285):
        world.run_until(tick)
        source_site = move(geometry['source'], (0, 1, 0), tick - 3)
        transfer_site = move(geometry['source'], (1, 1, 0), tick - 70)
        row = {'tick': tick, 'source_expected_worldline': observe(world, source_site),
               'transfer_expected_worldline': observe(world, transfer_site), 'source_hub': observe(world, geometry['source']),
               'recipient_reference_hub': observe(world, geometry['destination_reference_hub']),
               'center': recipient.observe(geometry['quantity']['center']),
               'reference_site': recipient.observe(geometry['quantity']['reference_site']),
               'object_site': recipient.observe(geometry['quantity']['object_site'])}
        if tick in (69, 70, 73, 79, 80, 146, 147, 213, 214, 280, 281):
            sites = {'source_hub': geometry['source'], 'recipient_reference_hub': geometry['destination_reference_hub'],
                     'reader': geometry['quantity']['center'], 'in_flight': transfer_site}
            row['Moore27'] = {name: [observe(world, move(site, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)] for name, site in sites.items()}
        frames.append(row)
        if tick in (0, 3, 70, 73, 80, 147, 281, 285):
            snapshots.append(save_world_snapshot(world, args.out / ('T' + str(tick) + '.deetsnap.gz')))
        put(args.out / 'OBSERVACIONES.json', frames)
    readings = []
    for index, tick in enumerate((147, 214, 281)):
        before = next(row for row in frames if row['tick'] == tick - 1)
        after = next(row for row in frames if row['tick'] == tick)
        expected_reference = args.value + 5
        expected_object = args.objects[index] + 5
        expected_direction = [(expected_reference > expected_object) - (expected_reference < expected_object), 0, 0]
        reference, current, result = before['reference_site'], before['object_site'], after['center']
        operands = reference['active'] and reference['s_reg'] == expected_reference and current['active'] and current['s_reg'] == expected_object
        readings.append({'tick': tick, 'reference': reference, 'current_object': current, 'output': result,
                         'auditor_only_expected_reference': expected_reference, 'auditor_only_expected_object': expected_object,
                         'auditor_only_expected_direction': expected_direction, 'actual_operands_preserved': operands,
                         'qualified': operands and result['active'] and result['direction'] == expected_direction})
    result = {'schema': 'CPC8R.magnitude.transfer.measurements.v1', 'status': 'MEASURED', 'case_id': args.case,
              'configuration': frozen, 'geometry': geometry, 'readings': readings,
              'source_requests': [{**row, 'receipt': exact_receipt(world.runtime.receipt(row['id']))} for row in requests],
              'recipient_requests': recipient.receipts(), 'recipient_reference_experience_calls': 0,
              'final_physical': physical(world), 'frames': frames, 'snapshots': snapshots,
              'elapsed_seconds': time.monotonic() - started, 'cpu_seconds': time.process_time() - cpu,
              'host_RAW_clock_edits_on_MAIN': [], 'counting': {'independent_preparations': 1, 'audit_forks': 0}}
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'case_id': args.case, 'readings': readings, 'source_inputs': result['source_requests'], 'recipient_requests': result['recipient_requests'], 'seconds': result['elapsed_seconds']}))
    del world, recipient
    gc.collect()


if __name__ == '__main__':
    main()
