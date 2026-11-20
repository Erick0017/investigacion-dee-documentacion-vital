"""Observational perspective-limit experiment, actor metadata never in organism."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from run_count_access import put, physical, sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    config = json.loads(a.config.read_text(encoding='utf8'))
    a.out.mkdir(parents=True, exist_ok=False)
    frozen = a.out / 'executed_source'
    for source in ('src/perspective_aux.py', 'src/integracion/quantity_core.py', 'run_perspective.py', 'run_count_access.py'):
        target = frozen / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
    sys.path.insert(0, str(frozen / 'src'))
    from perspective_aux import EffectContextSession
    index = []
    for case in config['cases']:
        out = a.out / case['id']
        out.mkdir()
        start = time.monotonic()
        session = EffectContextSession.create()
        session.curriculum(case['references'], case['effects'], case.get('association', 'paired'), case.get('omit_reference'))
        data = {'schema': 'CPC9.perspective.instrumented.primary.v1', 'case': case,
            'preparations': 1, 'forks': 0, 'continuations': 0,
            'independent_new_physical_preparation': case.get('modality') is None,
            'configuration_sha256': sha(a.config),
            'source_sha256': {str(p.relative_to(frozen)): sha(p) for p in frozen.rglob('*.py')},
            'geometry': session.geometry, 'frames': [], 'snapshots': [], 'host_RAW_clock_edits': [],
            'status': 'RUNNING', 'actor_labels_are_auditor_only': True,
            'coverage': 'Local operands, response and Moore27 at decisive comparison windows; no complete carrier genealogy'}
        for tick in (0, 2, 3, 4, 68, 69, 70, 71, 103, 110, 113, 135, 136, 137, 138, 177, 180, 202, 203, 204, 205):
            frame = session.run_until(tick)
            frame['physical'] = physical(session.world)
            if tick in (69, 70, 136, 137, 203, 204):
                from integracion.quantity_core import move
                frame['Moore27'] = {name: [session.observe(move(g['center'], (x, y, z)))
                    for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]
                    for name,g in session.geometry['observers'].items()}
            data['frames'].append(frame)
            if tick in (0, 103, 205):
                path = out / ('T'+str(tick)+'.deetsnap.gz')
                data['snapshots'].append({'path': path.name, 'storage': session.save(path), 'sha256': sha(path), 'physical': physical(session.world)})
            data['last_complete_tick'] = tick
            data['requests'] = session.receipts()
            put(out / 'MEASUREMENTS.json', data)
        data.update(status='MEASURED', elapsed_seconds=time.monotonic()-start)
        put(out / 'MEASUREMENTS.json', data)
        summary = {'id': case['id'], 'sha256': sha(out / 'MEASUREMENTS.json'),
            'responses': {str(t): {n: f['observers'][n]['response']['direction'] for n in ('A','B')}
                for f in data['frames'] if (t:=f['tick']) in (70,137,204)},
            'physical205': data['frames'][-1]['physical']}
        index.append(summary)
        put(a.out / 'INDEX.json', {'cases': index})
        print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
