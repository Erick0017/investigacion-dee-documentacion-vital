"""Host filesystem test only. No native world or tick is constructed."""
from pathlib import Path
import importlib.util
import json
import os
import tempfile
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('genesis_n0', HERE.parent / 'genesis.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)


def main():
    cases = []
    with tempfile.TemporaryDirectory(prefix='genesis-share-n0-') as temp:
        path, replacement = Path(temp) / 'record.json', Path(temp) / 'replacement.json'
        path.write_bytes(b'{"version":"old"}')
        replacement.write_bytes(b'{"version":"new"}')
        with path.open('rb') as regular:
            try:
                os.replace(replacement, path)
                cases.append({'case': 'regular_python_read_handle', 'replace_succeeded': True})
            except OSError as error:
                cases.append({'case': 'regular_python_read_handle', 'replace_succeeded': False,
                    'type': type(error).__name__, 'winerror': getattr(error, 'winerror', None), 'detail': str(error)})
        if not replacement.exists(): replacement.write_bytes(b'{"version":"new"}')
        with g.shared_read_handle(path):
            os.replace(replacement, path)
            cases.append({'case': 'FILE_SHARE_READ_WRITE_DELETE_handle', 'replace_succeeded': True,
                          'new_file_exact': path.read_bytes() == b'{"version":"new"}'})
        cases.append({'case': 'shared_passive_json_reader', 'decoded': g.read(path)})
    out = {'schema': 'GENESIS.host_atomic_replace.N0.R01', 'native_ticks': 0, 'cases': cases,
        'interpretation': 'This demonstrates the Windows sharing hazard and the safe reader contract. It does not by itself identify which overlapping read caused the earlier WinError5.'}
    target = HERE / 'PRUEBA_ATOMIC_REPLACE_N0_R01.json'
    if target.exists(): raise FileExistsError('Preserve the original N0 test.')
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__': main()
