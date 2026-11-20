"""Another-process public continuation of a saved T105 individual to T170.

Only the saved state is loaded. Fixed renewed queries are requested on every
declared non-original store, never routed according to an expected answer.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import time
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
from app import Console
from common import put, digest, operational, identity, sha
from snapshot_storage import logical_sha


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--snapshot', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--operation', choices=('forma1', 'consolidada'), default='forma1'); a = p.parse_args()
    snapshot = a.snapshot.resolve(); output = a.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic(); console = Console(); previous_cwd = Path.cwd(); rows = []
    try:
        # Exercise the actual public cargar grammar with a relative basename,
        # rather than relying on shell quoting inside its structured commands.
        os.chdir(snapshot.parent)
        loaded = console.execute('cargar ' + snapshot.name); rows.append({'command': 'cargar ' + snapshot.name, 'result': loaded})
        assert console.session.world.runtime.current_tick == 105, 'This published continuation starts at T105'
        initial = digest(console.session.world)
        commands = ('preguntar FORMA_01', 'avanzar 162', 'observar', 'avanzar 170', 'observar') if a.operation == 'forma1' else ('consultar consolidada', 'avanzar 164', 'observar', 'avanzar 170', 'observar')
        for command in commands:
            rows.append({'command': command, 'result': console.execute(command)})
        os.chdir(output); rows.append({'command': 'guardar FINAL_T170.deetsnap', 'result': console.execute('guardar FINAL_T170.deetsnap')})
    finally: os.chdir(previous_cwd)
    final = digest(console.session.world); assert final['tick'] == 170
    (output / 'DIALOGOS.jsonl').write_text('\n'.join(json.dumps(x, ensure_ascii=False) for x in rows) + '\n', encoding='utf-8')
    put(output / 'CONTINUATION.json', {'schema': 'CPC6.public-continuation.v1',
        'classification': 'TECHNICAL_PUBLIC_OTHER_PROCESS_CONTINUATION', 'engine': identity(),
        'continuation_completed': True, 'parent_logical_sha256': logical_sha(snapshot),
        'requested_operation': a.operation,
        'initial_physical': initial, 'final_physical': final,
        'requests_and_receipts': console.session.receipts(), 'final_operative': operational(console.session.world),
        'snapshot': {'file': 'FINAL_T170.deetsnap', 'logical_sha256': sha(output / 'FINAL_T170.deetsnap')},
        'source_sha256': {'app.py': sha(ROOT / 'app.py'), 'public_demo_continuation.py': sha(Path(__file__))},
        'elapsed_seconds': time.monotonic() - started,
        'scope': 'Same loaded world T105→170. No creation, reset, memory transplant, evaluator file or teaching map. Responses and rejections remain in the dialogue; completion is a continuity check, not a global functional-success verdict.'})
    print(json.dumps({'continuation_completed': True, 'initial_tick': initial['tick'], 'final_tick': final['tick']}))


if __name__ == '__main__': main()
