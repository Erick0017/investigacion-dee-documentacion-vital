"""Verify and reconstruct the two sequential DEE thinking 4.5 delivery parts."""
import argparse
import hashlib
import json
import os
from pathlib import Path

BLOCK = 4 * 1024 * 1024


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(BLOCK), b''):
            h.update(block)
    return h.hexdigest()


def join(metadata, output=None):
    metadata = Path(metadata).resolve()
    data = json.loads(metadata.read_text(encoding='utf-8-sig'))
    if data['schema'] != 'DEE45.binary-parts.v1' or len(data['parts']) != 2 or [r['order'] for r in data['parts']] != [1, 2]:
        raise ValueError('Expected exactly two ordered 4.5 binary parts')
    if data.get('parts_directory') != '.':
        raise ValueError('Place both parts next to PARTES.json')
    sources = []
    for row in data['parts']:
        if Path(row['name']).name != row['name'] or any(c in row['name'] for c in ('\\', '/', ':')):
            raise ValueError('Unsafe part name')
        path = metadata.parent / row['name']
        if path.is_symlink() or not path.is_file() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Part identity failed: ' + row['name'])
        sources.append(path)
    output = Path(output).resolve() if output else metadata.parent / (data['zip_name'].removesuffix('.zip') + '_RECONSTRUIDO.zip')
    if output.exists():
        raise FileExistsError('Existing output preserved: ' + str(output))
    temporary = output.with_name(output.name + '.pending.' + str(os.getpid()))
    output.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(); count = 0
    with temporary.open('xb') as target:
        for path in sources:
            with path.open('rb') as source:
                for block in iter(lambda: source.read(BLOCK), b''):
                    target.write(block); h.update(block); count += len(block)
    if count != data['zip_bytes'] or h.hexdigest() != data['zip_sha256']:
        raise ValueError('Reconstruction mismatch; partial output preserved')
    os.rename(temporary, output)
    if sha(output) != data['zip_sha256']:
        raise ValueError('Published reconstruction changed')
    return {'output': str(output), 'bytes': count, 'sha256': h.hexdigest(), 'verified': True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', type=Path, default=Path(__file__).with_name('PARTES.json'))
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    print(json.dumps(join(args.metadata, args.output), ensure_ascii=False, indent=2))
