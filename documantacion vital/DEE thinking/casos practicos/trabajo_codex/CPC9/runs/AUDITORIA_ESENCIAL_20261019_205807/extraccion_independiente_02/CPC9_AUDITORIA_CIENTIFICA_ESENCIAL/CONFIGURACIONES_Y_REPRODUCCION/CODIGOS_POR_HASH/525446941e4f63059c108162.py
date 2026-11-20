"""Explicit diagnostic forks or a new-process exact continuation; never MAIN."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from run_count_access import physical, audit_frame, put, sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--mode', choices=('cut', 'sham', 'restore'), required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    sources = a.parent.parent / 'executed_source'
    sys.path.insert(0, str(sources / 'src'))
    from count_access import CountAccessSession
    from dee_thinking import _native as d
    expected = json.loads((a.parent / 'MEASUREMENTS.json').read_text(encoding='utf8'))
    start = time.monotonic()
    parent = CountAccessSession.load(a.parent / 'T94.deetsnap.gz')
    before = physical(parent.world)
    interventions = []
    if a.mode == 'restore':
        session = parent
    else:
        edits = []
        for bank in parent.geometry['names']:
            q = bank['memory_site']
            obs = parent.observe(q)
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*q)
            edit.raw = 0 if a.mode == 'cut' else int(obs['raw'])
            edit.label = 'ALL_FIXED_FORM_BANKS_' + a.mode.upper()
            edits.append(edit)
            interventions.append({'site': q, 'before': obs, 'requested_RAW': str(edit.raw), 'clock_edit': None})
        world = parent.world.diagnostic_fork(edits, True)
        session = CountAccessSession(world, parent.geometry, deepcopy(parent.state), a.out.name)
    frames = []
    for tick in (94, 100, 103, 113, 114, 115, 147, 148, 149, 170, 171):
        frame = session.run_until(tick)
        frame['physical'] = physical(session.world)
        frames.append(frame)
    final = physical(session.world)
    qualified = {str(t): audit_frame(next(f for f in frames if f['tick'] == t), 1 if t == 114 else 2) for t in (114, 148)}
    expected_final = next(f['physical'] for f in expected['frames'] if f['tick'] == 171)
    expected_receipts = expected['requests']
    data = {'schema': 'CPC9.count_access.causal_or_restore.v1', 'id': a.out.name, 'mode': a.mode,
            'preparations': 0, 'forks': int(a.mode != 'restore'), 'continuations': int(a.mode == 'restore'),
            'parent': {'case_id': expected['case']['id'], 'snapshot': 'T94.deetsnap.gz',
                       'sha256': sha(a.parent / 'T94.deetsnap.gz'), 'primary_sha256': sha(a.parent / 'MEASUREMENTS.json')},
            'parent_physical_before': before, 'parent_physical_after': physical(parent.world),
            'parent_unchanged_for_fork': a.mode == 'restore' or before == physical(parent.world),
            'interventions': interventions, 'new_requests': [], 'geometry': session.geometry,
            'frames': frames, 'requests': session.receipts(), 'qualified': qualified,
            'final_physical': final, 'final_physical_equal_reference': final == expected_final,
            'receipts_equal_reference': session.receipts() == expected_receipts,
            'state_preserved': 'RAW/clocks, queue, channels and protocolmetadata loaded without re-teaching; explicit all-bank diagnostic RAW cut only on cutfork',
            'diagnostic_source_sha256': sha(__file__), 'status': 'MEASURED',
            'elapsed_seconds': time.monotonic() - start}
    path = a.out / 'T171.deetsnap.gz'
    data['snapshot'] = {'path': path.name, 'storage': session.save(path), 'sha256': sha(path)}
    put(a.out / 'MEASUREMENTS.json', data)
    print(json.dumps({'id': a.out.name, 'mode': a.mode, 'qualified': {k: len(v) for k, v in qualified.items()},
                      'physical_equal_reference': data['final_physical_equal_reference'],
                      'receipts_equal_reference': data['receipts_equal_reference']}), flush=True)
    if a.mode != 'cut' and not (data['final_physical_equal_reference'] and data['receipts_equal_reference']):
        raise AssertionError('Exact sham/restore mismatch; primary retained')


if __name__ == '__main__':
    main()
