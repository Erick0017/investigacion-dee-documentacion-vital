"""Bounded Windows sharing contrasts in the authorized workspace, zero ticks."""
from pathlib import Path
import importlib.util
import json
import os
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('genesis_share_r03', HERE.parent / 'genesis.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)


def main():
    home = HERE / 'FIXTURES_SHARE_N0_R02'
    home.mkdir(exist_ok=False)
    cases = []
    for name in ('closed', 'regular_reader', 'shared_delete_reader', 'closed_delayed'):
        path = home / (name + '.json')
        replacement = home / (name + '.new.json')
        path.write_text('{"old":1}', encoding='utf8')
        replacement.write_text('{"new":2}', encoding='utf8')
        error = None
        try:
            if name == 'regular_reader':
                with path.open('rb'): os.replace(replacement, path)
            elif name == 'shared_delete_reader':
                with g.shared_read_handle(path): os.replace(replacement, path)
            else:
                if name == 'closed_delayed': time.sleep(.5)
                os.replace(replacement, path)
        except OSError as e:
            error = {'type': type(e).__name__, 'winerror': getattr(e, 'winerror', None), 'detail': str(e)}
        cases.append({'case': name, 'replace_succeeded': error is None, 'error': error,
                      'remaining_old_or_new': path.read_text(encoding='utf8')})
    result = {'schema': 'GENESIS.host_sharing.N0.R02', 'native_ticks': 0, 'cases': cases,
        'interpretation_limit': 'Do not call the GUI reader the demonstrated unique cause if closed-handle or shared-delete controls also fail.'}
    target = HERE / 'PRUEBA_ATOMIC_REPLACE_N0_R02.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()
