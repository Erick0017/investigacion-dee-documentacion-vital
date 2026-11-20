"""Clean-extraction finite reproduction; reference data read only after evolution.

No physical implementation is copied: this invokes the exact frozen session
factory/curriculum, then checks native fields, complete state and receipts.
"""
from pathlib import Path
import argparse
import gc
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from dee_thinking.consolidated import exact_receipt
from integracion.quantity_core import physical
from regulacion_acoplada.mcts import CoupledMagnitudeCTSSession


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--condition', choices=('plus', 'minus'), required=True)
    parser.add_argument('--reference', type=Path, required=True, help='Frozen primary MEASUREMENTS.json; read only after both trajectories')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()
    if args.out.is_relative_to(ROOT) or ROOT.is_relative_to(args.out):
        raise ValueError('Output must be outside and not an ancestor of the read-only extraction')
    args.out.mkdir(parents=True, exist_ok=False)
    # This file declares actual experiences/resources, not expected outputs.
    configuration = json.loads((ROOT / 'configuraciones/transferencia_magnitud/CTS_CONGELADO.json').read_text(encoding='utf-8'))
    case = configuration['cases'][0]
    prepkeys = ('guard_mode', 'actor_mode', 'include_order', 'include_contact', 'event_state_offset', 'medium_load', 'actor_state', 'quantity_guards', 'regulation')
    session = CoupledMagnitudeCTSSession.create(identifier='CLEAN_COUPLED_' + args.condition,
        medium=1 if args.condition == 'plus' else -1, routing='onpath', **{key: value for key, value in case.items() if key in prepkeys})
    session.curriculum(regulation_reference=31, regulation_objects=(16, 45), **{key: value for key, value in case.items() if key not in ('id', *prepkeys)})
    frames = []
    states = {}
    snapshot77 = args.out / 'T77.deetsnap.gz'
    for tick in (4, 5, 9, 10, 11, 15, 53, 54, 69, 70, 77, 78, 79, 136, 137, 147, 206, 214, 281, 428, 549, 554, 559, 563, 616):
        session.run_until(tick)
        frame = session.view()
        frame['mode'].pop('captures', None)
        frame['mode'].pop('social_captures', None)
        frames.append(frame)
        if tick in (77, 616):
            states[str(tick)] = physical(session.world)
        if tick == 77:
            session.save(snapshot77)
    receipts = [exact_receipt(row) for row in session.world.runtime.receipts]
    del session
    gc.collect()
    restored = CoupledMagnitudeCTSSession.load(snapshot77)
    restored.run_until(616)
    restore_equal = physical(restored.world) == states['616']
    restore_receipts_equal = [exact_receipt(row) for row in restored.world.runtime.receipts] == receipts
    del restored
    gc.collect()
    # Evaluation boundary: no participant receives any information below here.
    reference = json.loads(args.reference.read_text(encoding='utf-8'))
    reference_frames = {row['tick']: row for row in reference['frames']}
    frame_comparisons = [{'tick': row['tick'], 'exact_old_and_coupled_fields': row == reference_frames[row['tick']]} for row in frames if row['tick'] in reference_frames]
    reference77 = CoupledMagnitudeCTSSession.load(args.reference.parent / 'T77.deetsnap.gz')
    reference77_state = physical(reference77.world)
    del reference77
    gc.collect()
    expected_receipts = sorted([row['receipt'] for row in reference['requests']], key=lambda row: row['id'])
    checks = {'full_RAW_clocks_tick77': states['77'] == reference77_state,
              'full_RAW_clocks_tick616': states['616'] == reference['final_physical'],
              'all_captured_fields': all(row['exact_old_and_coupled_fields'] for row in frame_comparisons),
              'receipts': receipts == expected_receipts,
              'restore77_to616_full_state': restore_equal, 'restore_receipts': restore_receipts_equal}
    result = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'condition': args.condition, 'checks': checks,
              'physical_states': states, 'frames': frames, 'frame_comparisons': frame_comparisons, 'requests': receipts,
              'reference_read_after_evolution': True, 'reference': str(args.reference),
              'reference_sha256': hashlib.sha256(args.reference.read_bytes()).hexdigest(),
              'preparations': 1, 'technical_restores': 1, 'independent_scientific_reserves': 0,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    put(args.out / 'RESULT.json', result)
    print(json.dumps({'status': result['status'], 'checks': checks}))
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
