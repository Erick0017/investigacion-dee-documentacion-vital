"""Late carrier causal forks of the fresh integrated CTS profile.

Loads the complete native/operative snapshot, never reruns the curriculum.
No edited diagnostic state is returned to the original owner world.
"""
from pathlib import Path
import argparse
import gc
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from integracion.relational_pair import physical, move
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def operation(session):
    return {'channels': sorted(session.world.runtime.channel_names),
            'receipts': [exact_receipt(row) for row in session.world.runtime.receipts],
            'protocol_count': len(session.world.protocols)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'resultados/transferencia_magnitud/MCTS_P01_SOURCE31'
    primary = json.loads((source / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    base = source / 'T73.deetsnap.gz'
    parent = MagnitudeCTSSession.load(base)
    pre, operation_before = physical(parent.world), operation(parent)
    location = [13, 53, 40]
    before = parent.observe(location)
    assert parent.tick == 73 and before['active'] and before['s_reg'] == 36 and before['direction'] == [1, 1, 0]
    config = {'schema': 'CPC8R.magnitudeCTS.causal.frozen.v1', 'base': base.relative_to(ROOT).as_posix(),
              'base_sha256': sha(base), 'formed_native_carrier': before,
              'conditions': ['restore_unchanged', 'inflight_carrier_RAWcut', 'inflight_carrier_RAWsham'],
              'prediction_before_fork_evolution': 'Removing only native36XY at73 prevents the new B reference and its qualified comparisons; sham conserves fullphysical616. Previous CTS functions are measured independently, not assumed destroyed or preserved.',
              'horizon': 616, 'new_external_inputs': 0, 'preparations': 0, 'forks': 2, 'technical_restored_continuations': 1}
    put(args.out / 'CONFIG.json', config)
    rows = []
    for condition in config['conditions']:
        edits = []
        if condition != 'restore_unchanged':
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*location)
            edit.raw = int(before['raw']) if 'sham' in condition else 0
            edit.clock = None
            edit.label = condition
            edits.append(edit)
        world = parent.world.diagnostic_fork(edits, True) if edits else parent.world.fork()
        session = MagnitudeCTSSession(world, parent.geometry, deepcopy(parent.state), parent.identifier)
        row = {'condition': condition, 'modality': 'DIAGNOSTIC_FORK' if edits else 'TECHNICAL_RESTORED_CONTINUATION',
               'pre_physical': physical(world), 'intervention': {'location': location, 'before': before, 'after': session.observe(location),
               'clock_preserved': before['clock'] == session.observe(location)['clock'],
               'pre_Moore27': [session.observe(move(location, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]},
               'original_operation_preserved': operation(session) == operation_before, 'frames': []}
        for tick in (73, 80, 86, 89, 146, 147, 165, 204, 206, 213, 214, 280, 281, 338, 344, 411, 415, 417, 428,
                     472, 478, 484, 487, 539, 549, 554, 559, 563, 616):
            session.run_until(tick)
            frame = session.view()
            frame['mode'].pop('captures', None)
            frame['mode'].pop('social_captures', None)
            row['frames'].append(frame)
        row.update(final_physical=physical(world), final_operation=operation(session),
                   parent_unchanged=physical(parent.world) == pre and operation(parent) == operation_before,
                   full_final_equal_original=physical(world) == primary['final_physical'])
        expected = sorted([item['receipt'] for item in primary['requests']], key=lambda item: item['id'])
        row['full_receipts_equal_original'] = row['final_operation']['receipts'] == expected
        row['snapshot'] = session.save(args.out / (condition + '_T616.deetsnap.gz'))
        assert row['parent_unchanged'] and row['intervention']['clock_preserved'] and row['original_operation_preserved']
        if condition != 'inflight_carrier_RAWcut':
            assert row['full_final_equal_original'] and row['full_receipts_equal_original']
        rows.append(row)
        put(args.out / 'INCREMENTAL.json', rows)
        del session, world
        gc.collect()
    result = {'schema': 'CPC8R.magnitudeCTS.causal.restore.v1', 'status': 'MEASURED', 'configuration': config,
              'source_sha256': sha(Path(__file__)), 'preparations': 0, 'diagnostic_forks': 2, 'technical_continuations': 1,
              'rows': rows, 'parent_unchanged': physical(parent.world) == pre and operation(parent) == operation_before,
              'base_file_unchanged': sha(base) == config['base_sha256']}
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'rows': [{'condition': row['condition'], 'full_final_equal': row['full_final_equal_original'],
                      'B147': next(frame['magnitude_transfer'] for frame in row['frames'] if frame['tick'] == 147),
                      'word616': row['frames'][-1]['joint']} for row in rows], 'parent_unchanged': result['parent_unchanged']}))


if __name__ == '__main__':
    main()
