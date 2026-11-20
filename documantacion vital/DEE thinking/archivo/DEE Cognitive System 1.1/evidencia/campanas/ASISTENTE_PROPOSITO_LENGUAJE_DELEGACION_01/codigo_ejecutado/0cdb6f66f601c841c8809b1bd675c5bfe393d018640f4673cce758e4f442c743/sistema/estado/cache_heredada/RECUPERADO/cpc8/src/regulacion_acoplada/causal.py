"""Explicit diagnostic forks and operative restores; never returned to MAIN."""
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
from regulacion_acoplada.aparato import CoupledRegulationSession, move


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
    for case_id, policy, reference, current in [('RCA_D01_PLUS_HIGH', 'P', 31, 45), ('RCA_H02_MINUS_LOW', 'Q', 11, 45)]:
        directory = ROOT / 'resultados/regulacion_acoplada' / case_id
        primary = json.loads((directory / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
        for tick, target_name, expected_load in [(4, 'actual_return', 1), (9, 'selected_policy', 97), (11, 'selected_action', 114), (77, 'formed_counterflow', 114)]:
            base = directory / ('T' + str(4 if tick == 9 else tick) + '.deetsnap.gz')
            parent = CoupledRegulationSession.load(base)
            if tick == 9:
                parent.run_until(9)
            parent_physical, parent_ops = physical(parent.world), operations(parent)
            if tick == 4:
                site = parent.geometry['feedback']['ports']['actual_before_merge.1']
            elif tick == 9:
                site = parent.geometry['feedback']['ports']['policy.' + ('1_0' if policy == 'P' else '1_1')]
            elif tick == 11:
                site = parent.geometry['policy_after_escape'][policy]['site']
            else:
                site = parent.geometry['counterflows'][policy]['pre_interception_site']
            before = parent.observe(site)
            assert parent.tick == tick and before['active'] and before['s_reg'] == expected_load
            pre_neighborhood = [parent.observe(move(site, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]
            for kind in ('RAWcut', 'RAWsham'):
                condition = target_name + '_' + kind + '_T' + str(tick)
                edit = d.ResearchStateEdit()
                edit.coordinate = d.Coordinate(*site)
                edit.raw = int(before['raw']) if kind == 'RAWsham' else 0
                edit.clock = None
                edit.label = condition
                world = parent.world.diagnostic_fork([edit], True)
                session = CoupledRegulationSession(world, parent.geometry, deepcopy(parent.state))
                row = {'case_id': case_id, 'condition': condition, 'modality': 'DIAGNOSTIC_FORK',
                       'base': base.relative_to(ROOT).as_posix(), 'base_sha256': sha(base), 'parent_advanced_before_fork': [4, 9] if tick == 9 else None, 'new_inputs': 0,
                       'intervention': {'before': before, 'after': session.observe(site), 'clock_preserved': before['clock'] == session.observe(site)['clock'],
                                        'pre_Moore27': pre_neighborhood},
                       'original_operation_preserved': operations(session) == parent_ops, 'frames': []}
                for target in (4, 5, 9, 10, 11, 12, 15, 19, 46, 53, 54, 69, 70, 77, 78, 79, 85, 86, 87, 136, 137, 141):
                    if target < tick:
                        continue
                    session.run_until(target)
                    row['frames'].append(session.capture())
                before_comparison = next(frame['quantity'] for frame in row['frames'] if frame['tick'] == 136)
                after_comparison = next(frame['quantity'] for frame in row['frames'] if frame['tick'] == 137)
                er, eo = reference + 5, current + 5
                dr = [(er > eo) - (er < eo), 0, 0]
                row['later_reading'] = {'reference': before_comparison['reference_site'], 'object': before_comparison['object_site'],
                                        'output': after_comparison['center'], 'expected_reference': er, 'expected_object': eo,
                                        'qualified': before_comparison['reference_site']['active'] and before_comparison['reference_site']['s_reg'] == er
                                        and before_comparison['object_site']['active'] and before_comparison['object_site']['s_reg'] == eo
                                        and after_comparison['center']['active'] and after_comparison['center']['direction'] == dr}
                row.update(final_physical=physical(world), final_operation=operations(session), parent_unchanged=physical(parent.world) == parent_physical and operations(parent) == parent_ops,
                           full_final_equal_original=physical(world) == primary['final_physical'], base_file_unchanged=sha(base) == row['base_sha256'])
                expected_receipts = sorted([item['receipt'] for item in primary['requests']], key=lambda item: item['id'])
                row['receipts_equal_original'] = row['final_operation']['receipts'] == expected_receipts
                row['snapshot'] = session.save(args.out / (case_id + '_' + condition + '_T141.deetsnap.gz'))
                assert row['intervention']['clock_preserved'] and row['original_operation_preserved'] and row['parent_unchanged'] and row['base_file_unchanged']
                if kind == 'RAWsham':
                    assert row['full_final_equal_original'] and row['receipts_equal_original']
                rows.append(row)
                put(args.out / 'INCREMENTAL.json', rows)
                del session, world
                gc.collect()
            del parent
            gc.collect()
        # This load uses the complete operative snapshot including pending inputs;
        # no curriculum or factory is called, and no input is submitted after load.
        base = directory / 'T77.deetsnap.gz'
        restored = CoupledRegulationSession.load(base)
        restored.run_until(141)
        expected_receipts = sorted([item['receipt'] for item in primary['requests']], key=lambda item: item['id'])
        restore = {'case_id': case_id, 'condition': 'restore77_to141', 'modality': 'TECHNICAL_CONTINUATION',
                   'base': base.relative_to(ROOT).as_posix(), 'base_sha256': sha(base), 'new_inputs': 0,
                   'full_final_equal_original': physical(restored.world) == primary['final_physical'],
                   'receipts_equal_original': operations(restored)['receipts'] == expected_receipts}
        assert restore['full_final_equal_original'] and restore['receipts_equal_original']
        rows.append(restore)
        put(args.out / 'INCREMENTAL.json', rows)
        del restored
        gc.collect()
    result = {'schema': 'CPC8R.coupled.regulation.causal.v1', 'status': 'MEASURED', 'preparations': 0, 'diagnostic_forks': 16,
              'diagnostic_parent_advances': 2,
              'technical_continuations': 2, 'source_sha256': sha(Path(__file__)),
              'frozen_configuration_sha256': sha(ROOT / 'configuraciones/regulacion_acoplada/FACTORIAL_CONGELADO.json'), 'rows': rows}
    put(args.out / 'MEASUREMENTS.json', result)
    print(json.dumps({'status': 'MEASURED', 'rows': [{key: row[key] for key in ('case_id', 'condition', 'modality', 'full_final_equal_original')} for row in rows]}))


if __name__ == '__main__':
    main()
