"""Explicit late in-flight native carrier cut/sham and exact continuation."""
from pathlib import Path
import argparse
import gc
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import load_world_snapshot, save_world_snapshot
from integracion.quantity_core import physical
from transferencia_magnitud.transferencia import move


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def observation(world, site):
    return exact_observation(world.runtime.observe(d.Coordinate(*site)))


def operations(world):
    return {'channels': sorted(world.runtime.channel_names), 'receipts': [exact_receipt(row) for row in world.runtime.receipts]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'resultados/transferencia_magnitud/MT_D01_SOURCE31'
    primary = json.loads((source / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    geometry = primary['geometry']
    base = source / 'T73.deetsnap.gz'
    parent, _ = load_world_snapshot(base)
    pre = physical(parent)
    pre_operations = operations(parent)
    site = [13, 53, 40]
    before = observation(parent, site)
    assert before['active'] and before['s_reg'] == 36 and before['direction'] == [1, 1, 0]
    configuration = {'base': base.relative_to(ROOT).as_posix(), 'base_sha256': sha(base), 'native_carrier_site_T73': site,
                     'conditions': ['restore_unchanged', 'inflight_RAWcut_clock_preserved', 'identical_RAW_sham'],
                     'horizon': 285, 'predictions_frozen_in': 'configuraciones/transferencia_magnitud/CONFIRMACION_CONGELADA.json',
                     'post_restore_new_inputs': 0, 'external_diagnostic_only': True, 'independent_preparations': 0}
    put(args.out / 'CONFIG.json', configuration)
    rows = []
    for condition in configuration['conditions']:
        edits = []
        if condition != 'restore_unchanged':
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*site)
            edit.raw = int(before['raw']) if 'sham' in condition else 0
            edit.clock = None
            edit.label = condition
            edits.append(edit)
        world = parent.diagnostic_fork(edits, True) if edits else parent.fork()
        row = {'condition': condition, 'modality': 'DIAGNOSTIC_FORK' if edits else 'TECHNICAL_RESTORED_CONTINUATION',
               'pre_physical': physical(world), 'clock_preserved': observation(world, site)['clock'] == before['clock'],
               'original_queue_channels_receipts_preserved': operations(world) == pre_operations,
               'pre_Moore27': [observation(world, move(site, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)], 'frames': []}
        for tick in (73, 79, 80, 81, 146, 147, 213, 214, 280, 281, 285):
            world.run_until(tick)
            row['frames'].append({'tick': tick, 'recipient_reference_hub': observation(world, geometry['destination_reference_hub']),
                                  'reference': observation(world, geometry['quantity']['reference_site']),
                                  'current_object': observation(world, geometry['quantity']['object_site']),
                                  'output': observation(world, geometry['quantity']['center'])})
        row.update(final_physical=physical(world), final_operations=operations(world),
                   parent_unchanged=physical(parent) == pre and operations(parent) == pre_operations)
        row['full_final_equal_original'] = row['final_physical'] == primary['final_physical']
        expected_receipts = sorted([item['receipt'] for item in primary['source_requests'] + primary['recipient_requests']], key=lambda item: item['id'])
        row['final_receipts_equal_original'] = row['final_operations']['receipts'] == expected_receipts
        row['snapshot'] = save_world_snapshot(world, args.out / (condition + '_T285.deetsnap.gz'))
        assert row['parent_unchanged'] and row['clock_preserved'] and row['original_queue_channels_receipts_preserved']
        if condition != 'inflight_RAWcut_clock_preserved':
            assert row['full_final_equal_original'] and row['final_receipts_equal_original']
        rows.append(row)
        put(args.out / 'INCREMENTAL.json', rows)
        del world
        gc.collect()
    result = {'schema': 'CPC8R.magnitude.transfer.causal.restore.v1', 'status': 'MEASURED', 'configuration': configuration,
              'source_sha256': sha(Path(__file__)), 'preparations': 0, 'diagnostic_forks': 2, 'technical_continuations': 1,
              'rows': rows, 'parent_unchanged': physical(parent) == pre and operations(parent) == pre_operations,
              'base_file_unchanged': sha(base) == configuration['base_sha256']}
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'conditions': [{'condition': row['condition'], 'full_final_equal': row['full_final_equal_original'],
                      'B_reference_80': next(frame['recipient_reference_hub'] for frame in row['frames'] if frame['tick'] == 80),
                      'outputs': [frame['output'] for frame in row['frames'] if frame['tick'] in (147, 214, 281)]} for row in rows],
                      'parent_unchanged': result['parent_unchanged']}))


if __name__ == '__main__':
    main()
