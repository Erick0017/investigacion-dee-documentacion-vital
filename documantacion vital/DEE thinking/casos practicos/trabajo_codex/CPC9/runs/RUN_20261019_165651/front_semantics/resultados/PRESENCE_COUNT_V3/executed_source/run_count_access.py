"""Bounded runner; preparation/curriculum are separate from post-hoc metrics."""
import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
SOURCES = ['src/count_access.py', 'src/count_sign/session.py', 'src/count_sign/branch_session.py',
           'src/relaciones/contact_cardinality.py', 'src/integracion/quantity_core.py', 'run_count_access.py']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.pending')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    os.replace(tmp, path)


def physical(world):
    runtime = world.runtime
    return {'tick': int(runtime.current_tick),
            'RAW_sha256': hashlib.sha256(array('Q', runtime.raw_copy()).tobytes()).hexdigest(),
            'clocks_sha256': hashlib.sha256(array('Q', runtime.clock_copy()).tobytes()).hexdigest()}


def audit_frame(frame, index):
    out = []
    for row in frame['readers']:
        observation = row['reading' + str(index)]
        expected = row['query' + str(index)]['expected_direction']
        if observation['active'] and observation['semantic'] == 1 and observation['s_reg'] > 7 and observation['direction'] == expected:
            out.append({'route_axis_candidate': row['route_axis_candidate'],
                        'candidate_comparator_x': row['candidate_comparator_x'],
                        'heading': row['heading'], 'physical': observation})
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf8'))
    args.out.mkdir(parents=True, exist_ok=True)
    source_dir = args.out / 'executed_source'
    source_dir.mkdir(exist_ok=False)
    sources = {}
    for source in SOURCES:
        target = source_dir / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
        sources[source] = sha(target)
    sys.path.insert(0, str(source_dir / 'src'))
    from count_access import CountAccessSession, curriculum
    from count_sign.session import move
    selected = [c for c in config['cases'] if not args.case or c['id'] == args.case]
    if not selected:
        raise ValueError('Requested case absent')
    index = []
    for case in selected:
        out = args.out / case['id']
        out.mkdir(exist_ok=False)
        start = time.monotonic()
        data = {'schema': 'CPC9.count_access.primary.v1', 'case': case, 'status': 'RUNNING',
                'preparations': 0, 'forks': 0, 'continuations': 0,
                'source_sha256': sources, 'source_directory': '../executed_source',
                'configuration_sha256': sha(args.config), 'frames': [], 'snapshots': [],
                'host_RAW_clock_edits_on_participant': [], 'started_utc': datetime.now(timezone.utc).isoformat(),
                'coverage': 'Fixed sites and decisive Moore neighborhoods only; not a complete carrier genealogy'}
        try:
            session = CountAccessSession.create(case)
            data['preparations'] = 1
            data['geometry'] = session.geometry
            curriculum(session, case.get('form', 'paired'), case.get('route', True))
            for tick in (0, 4, 5, 9, 10, 23, 24, 89, 90, 91, 92, 93, 94, 99, 100, 103, 113, 114, 115, 147, 148, 149, 167, 170, 171):
                frame = session.run_until(tick)
                frame['physical'] = physical(session.world)
                if tick in (93, 94, 113, 114, 147, 148):
                    centers = [n['memory_site'] for n in session.geometry['names']]
                    frame['Moore27'] = [{'center': q, 'readings': [session.observe(move(q, (x, y, z)))
                        for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]} for q in centers]
                data['frames'].append(frame)
                if tick in (0, 94, 171):
                    path = out / ('T' + str(tick) + '.deetsnap.gz')
                    storage = session.save(path)
                    data['snapshots'].append({'path': path.name, 'sha256': sha(path),
                                              'physical': physical(session.world), 'storage': storage})
                data['last_complete_tick'] = tick
                data['requests'] = session.receipts()
                data['elapsed_seconds'] = time.monotonic() - start
                put(out / 'MEASUREMENTS.json', data)
            data['auditor_calculations'] = {
                'qualified114': audit_frame(next(f for f in data['frames'] if f['tick'] == 114), 1),
                'qualified148': audit_frame(next(f for f in data['frames'] if f['tick'] == 148), 2),
                'formula': 'Each fixed reader independently: active AND semantic=1 AND s_reg>probe7 AND direction=declared direction. All readings retained; no expected answer enters preparation.'}
            data['status'] = 'MEASURED'
        except BaseException as error:
            data.update(status='TECHNICAL_ERROR', error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
            raise
        finally:
            data['elapsed_seconds'] = time.monotonic() - start
            put(out / 'MEASUREMENTS.json', data)
        summary = {'id': case['id'], 'status': data['status'],
                   'qualified114': len(data['auditor_calculations']['qualified114']),
                   'qualified148': len(data['auditor_calculations']['qualified148']),
                   'primary': case['id'] + '/MEASUREMENTS.json', 'sha256': sha(out / 'MEASUREMENTS.json')}
        index.append(summary)
        put(args.out / 'INDEX.json', {'schema': 'CPC9.count_access.index.v1', 'cases': index})
        print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
