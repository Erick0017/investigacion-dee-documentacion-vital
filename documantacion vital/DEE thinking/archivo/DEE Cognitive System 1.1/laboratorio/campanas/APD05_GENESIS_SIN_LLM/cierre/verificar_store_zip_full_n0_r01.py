"""Read exact already-sealed Full members; no extraction, import or Native."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--zip', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.out.exists(): raise FileExistsError('Fresh witness output required')
targets = {
    'sistema/app/lives.py': '974913719bf1a17833e1cf0425cfdc69d680cf657979fe5fbb1c4c0917dc757f',
    'aplicacion/GENESIS/propietario_genesis.py': '76efce1aa61b240931ba246e6506c8931eb73956d93a68d3b8388cc324bd29dc',
    'aplicacion/GENESIS/app.js': 'b632d37fe69ba2f1d8ac25a1e732df6c7f43822b6821bc2642618c3d92dfa78c'
}
rows = []
with zipfile.ZipFile(args.zip) as archive:
    for suffix, expected in targets.items():
        matches = [name for name in archive.namelist() if name in (suffix, 'cognitive sistem/' + suffix)]
        if len(matches) != 1: raise ValueError('No unique operational ZIP member: ' + suffix)
        data = archive.read(matches[0])  # ZipFile verifies this member's CRC.
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected: raise ValueError('Sealed operational bytes differ: ' + matches[0])
        row = {'member': matches[0], 'bytes': len(data), 'sha256': actual, 'member_CRC_verified_by_read': True}
        if suffix.endswith('lives.py'):
            lines = data.decode('utf8').splitlines()
            witness = [line for line in lines if "self.state=(self.root/'../trabajo_personal/estado').resolve()" in line]
            if len(witness) != 1: raise ValueError('No unique declared distribution Store relocation')
            row['exact_Store_constructor_line'] = witness[0]
        rows.append(row)
report = {'schema': 'APD05.exact_Full_Store_GUI_members.N0.R01', 'archive': str(args.zip),
    'archive_bytes': args.zip.stat().st_size, 'native_ticks_added': 0, 'members': rows,
    'scope': 'Only three operational members read from exact ZIP with member CRC and SHA. Not all-member integrity, startup, Native functionality or another computer proof.'}
args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps(report, ensure_ascii=True, indent=2))
