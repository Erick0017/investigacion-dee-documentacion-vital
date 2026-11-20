"""Offline checks of the finished R05 editorial model; never loads DEE."""
from pathlib import Path
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from pipeline_r05 import model, SCENE_SECONDS, visual_fingerprint

def main():
    started = time.monotonic()
    rows = []
    for n, seconds in enumerate(SCENE_SECONDS, 1):
        scene = f'S{n:02d}'
        representations = set()
        cases = set()
        changes = []
        previous = None
        for frame in range(seconds * 30):
            value = model(scene, frame)
            provenance = value['provenance']
            representation = provenance['representation']
            assert representation in ('Registros DEE', 'Reconstrucción', 'Ilustración del mecanismo')
            representations.add(representation)
            case = provenance.get('case', '')
            assert case
            cases.add(case)
            current = (representation, case)
            if current != previous:
                changes.append({'local_frame': frame, 'representation': representation, 'case': case})
                previous = current
        rows.append({'scene': scene, 'validated_models': seconds * 30,
                     'representations': sorted(representations), 'cases': sorted(cases),
                     'editorial_provenance_changes': changes})
    result = {'kind': 'offline_editorial_model_validation', 'native_ticks': 0,
              'total_models': sum(row['validated_models'] for row in rows),
              'visual_source_sha256': visual_fingerprint(),
              'host_seconds': round(time.monotonic() - started, 3),
              'scenes': rows,
              'limits': 'Model validity does not certify rendered visual quality, causal lineage, or listening.'}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)

if __name__ == '__main__':
    main()
