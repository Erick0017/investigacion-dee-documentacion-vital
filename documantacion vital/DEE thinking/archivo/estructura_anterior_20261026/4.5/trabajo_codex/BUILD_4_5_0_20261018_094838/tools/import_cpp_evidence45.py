"""Copy only final C++ observations/checkpoints, retaining byte identities."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    a = p.parse_args()
    source = a.source.resolve(); target = ROOT / 'evidence/CPP_FINAL'
    if not source.is_dir():
        raise FileNotFoundError(source)
    target.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in source.iterdir() if path.is_file() and path.suffix.lower() in {'.deetsnap', '.jsonl'})
    if not files or not (source / 'OBSERVATIONS_CPP.jsonl').is_file():
        raise ValueError('Missing final C++ primary observations')
    rows = []
    for path in files:
        if path.is_symlink():
            raise ValueError('No links')
        digest = sha(path); destination = target / path.name
        if destination.exists():
            if sha(destination) != digest:
                raise FileExistsError('Different previous evidence preserved: ' + str(destination))
        else:
            shutil.copyfile(path, destination)
        if sha(destination) != digest or destination.stat().st_size != path.stat().st_size:
            raise ValueError('Evidence copy mismatch: ' + path.name)
        rows.append({'path': path.name, 'bytes': destination.stat().st_size, 'sha256': digest, 'copied_byte_exact': True})
    provenance = {'schema': 'DEE45.cpp-primary-copy.v1', 'source_directory': str(source), 'files': rows,
                  'scope': 'Measured C++ observations and causal boundary snapshots only; no build tree/toolchain included. Original files are unmodified.'}
    report = target / 'PROVENANCE.json'
    if report.exists():
        old = json.loads(report.read_text(encoding='utf-8'))
        if old != provenance:
            raise FileExistsError('Previous provenance preserved')
    else:
        report.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'byte_exact': True}))


if __name__ == '__main__':
    main()
