"""Late formed-regulator cut/sham on two complete fresh-world histories."""
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
from integracion.quantity_core import physical
from regulacion_acoplada.aparato import move
from regulacion_acoplada.mcts import CoupledMagnitudeCTSSession


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def operations(session):
    return {'channels': sorted(session.world.runtime.channel_names),
            'receipts': [exact_receipt(item) for item in session.world.runtime.receipts],
            'protocol_count': len(session.world.protocols)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    rows = []
    for case_id, policy, reference in [('RCAM_D02_CONTINUED_FROM4', 'P', 31), ('RCAM_H02_MINUS_LOW', 'Q', 11)]:
        directory = ROOT / 'resultados/regulacion_acoplada' / case_id
        primary = json.loads((directory / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        base = directory / 'T77.deetsnap.gz'
        parent = CoupledMagnitudeCTSSession.load(base)
        parent_physical, parent_ops = physical(parent.world), operations(parent)
        site = parent.geometry['coupled_regulation']['counterflows'][policy]['pre_interception_site']
        before = parent.observe(site)
        assert parent.tick == 77 and before['active'] and before['s_reg'] == 114
        pre_neighborhood = [parent.observe(move(site, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]
        for kind in ('RAWcut', 'RAWsham'):
            condition = 'formed_counterflow_' + kind + '_T77'
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*site)
            edit.raw = int(before['raw']) if kind == 'RAWsham' else 0
            edit.clock = None
            edit.label = condition
            world = parent.world.diagnostic_fork([edit], True)
            session = CoupledMagnitudeCTSSession(world, parent.geometry, deepcopy(parent.state), parent.identifier)
            row = {'case_id': case_id, 'condition': condition, 'modality': 'DIAGNOSTIC_FORK',
                   'base': base.relative_to(ROOT).as_posix(), 'base_sha256': sha(base), 'new_inputs': 0,
                   'intervention': {'before': before, 'after': session.observe(site), 'clock_preserved': before['clock'] == session.observe(site)['clock'], 'pre_Moore27': pre_neighborhood},
                   'original_operation_preserved': operations(session) == parent_ops, 'frames': []}
            for tick in (77, 78, 79, 80, 86, 89, 136, 137, 141, 146, 147, 170, 204, 206, 213, 214, 271, 280, 281, 338, 348, 405, 411, 415, 417, 428, 472, 478, 484, 487, 539, 549, 554, 559, 563, 616):
                session.run_until(tick)
                frame = session.view()
                frame['mode'].pop('captures', None)
                frame['mode'].pop('social_captures', None)
                row['frames'].append(frame)
            pre = next(frame['coupled_regulation']['quantity'] for frame in row['frames'] if frame['tick'] == 136)
            post = next(frame['coupled_regulation']['quantity'] for frame in row['frames'] if frame['tick'] == 137)
            er, eo = reference + 5, 50
            row['later_reading'] = {'reference': pre['reference_site'], 'object': pre['object_site'], 'output': post['center'],
                                    'qualified': pre['reference_site']['active'] and pre['reference_site']['s_reg'] == er
                                    and pre['object_site']['active'] and pre['object_site']['s_reg'] == eo
                                    and post['center']['active'] and post['center']['direction'] == [(er > eo) - (er < eo), 0, 0]}
            row.update(final_physical=physical(world), final_operation=operations(session), parent_unchanged=physical(parent.world) == parent_physical and operations(parent) == parent_ops,
                       full_final_equal_original=physical(world) == primary['final_physical'], base_file_unchanged=sha(base) == row['base_sha256'])
            expected_receipts = sorted([item['receipt'] for item in primary['requests']], key=lambda item: item['id'])
            row['receipts_equal_original'] = row['final_operation']['receipts'] == expected_receipts
            row['snapshot'] = session.save(args.out / (case_id + '_' + condition + '_T616.deetsnap.gz'))
            assert row['intervention']['clock_preserved'] and row['original_operation_preserved'] and row['parent_unchanged'] and row['base_file_unchanged']
            if kind == 'RAWsham':
                assert row['full_final_equal_original'] and row['receipts_equal_original']
            rows.append(row)
            put(args.out / 'INCREMENTAL.json', rows)
            del session, world
            gc.collect()
        del parent
        gc.collect()
        restored = CoupledMagnitudeCTSSession.load(base)
        restored.run_until(616)
        restore = {'case_id': case_id, 'condition': 'restore77_to616', 'modality': 'TECHNICAL_CONTINUATION', 'new_inputs': 0,
                   'base': base.relative_to(ROOT).as_posix(), 'base_sha256': sha(base),
                   'full_final_equal_original': physical(restored.world) == primary['final_physical'],
                   'receipts_equal_original': operations(restored)['receipts'] == expected_receipts}
        assert restore['full_final_equal_original'] and restore['receipts_equal_original']
        rows.append(restore)
        put(args.out / 'INCREMENTAL.json', rows)
        del restored
        gc.collect()
    result = {'schema': 'CPC8R.coupledRegulationMCTS.causal.v1', 'status': 'MEASURED', 'preparations': 0, 'diagnostic_forks': 4,
              'technical_continuations': 2, 'source_sha256': sha(Path(__file__)),
              'frozen_configuration_sha256': sha(ROOT / 'configuraciones/regulacion_acoplada/MCTS_FACTORIAL_CONGELADO.json'), 'rows': rows}
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'rows': [{key: row[key] for key in ('case_id', 'condition', 'full_final_equal_original')} for row in rows]}))


if __name__ == '__main__':
    main()
