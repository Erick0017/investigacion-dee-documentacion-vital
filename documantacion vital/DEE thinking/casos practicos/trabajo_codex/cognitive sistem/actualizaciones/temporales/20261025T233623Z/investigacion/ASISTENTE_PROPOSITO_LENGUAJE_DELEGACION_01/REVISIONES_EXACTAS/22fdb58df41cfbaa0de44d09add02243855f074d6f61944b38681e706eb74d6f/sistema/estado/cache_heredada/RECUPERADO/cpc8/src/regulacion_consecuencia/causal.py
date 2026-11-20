"""Current formed-return cut/sham in each complete composed-world history."""
from pathlib import Path
from copy import deepcopy
import argparse
import gc
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from integracion.relational_pair import physical, move
from regulacion_consecuencia.mcts import ConsequenceMagnitudeCTSSession


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def operations(session):
    return {'channels': sorted(session.world.runtime.channel_names),
            'receipts': [exact_receipt(row) for row in session.world.runtime.receipts],
            'protocol_count': len(session.world.protocols)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    config = json.loads((ROOT / 'configuraciones/regulacion_consecuencia/MCTS_V2_CONGELADO.json').read_text(encoding='utf-8'))
    rows = []
    for case in config['cases']:
        directory = ROOT / 'resultados/regulacion_consecuencia_integrada' / case['id']
        base = directory / 'T4.deetsnap.gz'
        primary = json.loads((directory / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        parent = ConsequenceMagnitudeCTSSession.load(base)
        parent_physical, parent_operation = physical(parent.world), operations(parent)
        site = parent.geometry['consequence_regulation']['ports']['actual_before_merge.1']
        before = parent.observe(site)
        assert parent.tick == 4 and before['active'] and before['s_reg'] == 1
        base_hash = sha(base)
        for condition in ('actual_formed_return_RAWcut_T4', 'actual_formed_return_RAWsham_T4'):
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*site)
            edit.raw = int(before['raw']) if 'sham' in condition else 0
            edit.clock = None
            edit.label = condition
            world = parent.world.diagnostic_fork([edit], True)
            session = ConsequenceMagnitudeCTSSession(world, parent.geometry, deepcopy(parent.state), parent.identifier)
            row = {'case_id': case['id'], 'condition': condition, 'modality': 'DIAGNOSTIC_FORK',
                   'base': base.relative_to(ROOT).as_posix(), 'base_sha256': base_hash,
                   'pre_physical': physical(world), 'intervention': {'before': before, 'after': session.observe(site),
                   'clock_preserved': before['clock'] == session.observe(site)['clock'],
                   'pre_Moore27': [session.observe(move(site, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]},
                   'original_operation_preserved': operations(session) == parent_operation, 'new_inputs': 0, 'frames': []}
            for tick in (4, 5, 9, 10, 12, 15, 18, 31, 70, 76, 89, 137, 143, 146, 147, 165, 204, 206, 213, 214,
                         280, 281, 338, 411, 415, 417, 428, 472, 478, 484, 487, 539, 549, 554, 559, 563, 616):
                session.run_until(tick)
                frame = session.view()
                frame['mode'].pop('captures', None)
                frame['mode'].pop('social_captures', None)
                row['frames'].append(frame)
            row.update(final_physical=physical(world), final_operation=operations(session),
                       parent_unchanged=physical(parent.world) == parent_physical and operations(parent) == parent_operation,
                       full_final_equal_original=physical(world) == primary['final_physical'],
                       base_file_unchanged=sha(base) == base_hash)
            expected = sorted([item['receipt'] for item in primary['requests']], key=lambda item: item['id'])
            row['receipts_equal_original'] = row['final_operation']['receipts'] == expected
            row['snapshot'] = session.save(args.out / (case['id'] + '_' + condition + '_T616.deetsnap.gz'))
            assert row['intervention']['clock_preserved'] and row['original_operation_preserved'] and row['parent_unchanged'] and row['base_file_unchanged']
            if 'sham' in condition:
                assert row['full_final_equal_original'] and row['receipts_equal_original']
            rows.append(row)
            put(args.out / 'INCREMENTAL.json', rows)
            del session, world
            gc.collect()
        del parent
        gc.collect()
    result = {'schema': 'CPC8R.consequenceMagnitudeCTS.causal.v1', 'status': 'MEASURED', 'preparations': 0,
              'diagnostic_forks': 4, 'technical_continuations': 0, 'source_sha256': sha(Path(__file__)),
              'frozen_configuration_sha256': sha(ROOT / 'configuraciones/regulacion_consecuencia/MCTS_V2_CONGELADO.json'), 'rows': rows}
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'status': 'MEASURED', 'forks': [{'case_id': row['case_id'], 'condition': row['condition'],
                      'full_final_equal': row['full_final_equal_original'], 'parent_unchanged': row['parent_unchanged']} for row in rows]}))


if __name__ == '__main__':
    main()
