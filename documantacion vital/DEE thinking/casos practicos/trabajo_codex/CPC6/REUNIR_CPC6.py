"""Verify and join CPC6's two sequential binary parts without overwriting."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--carpeta', type=Path, default=Path(__file__).resolve().parent)
    p.add_argument('--salida', type=Path); a = p.parse_args(); folder = a.carpeta.resolve()
    info = json.loads((folder / 'PARTES.json').read_text(encoding='utf-8'))
    assert info['schema'] == 'CPC6.binary-parts.v1'
    relative = info.get('parts_directory', '.')
    assert relative in ('.', '..'), 'Sólo se admite esta carpeta o su padre declarado'
    parts_folder = (folder / relative).resolve(); parts = info['parts']
    assert [x['order'] for x in parts] == [1, 2]
    for row in parts:
        assert Path(row['name']).name == row['name']
        path = parts_folder / row['name']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'Parte diferente'
    target = (a.salida or parts_folder / (info['zip_name'].removesuffix('.zip') + '_REUNIDO.zip')).resolve()
    if target.exists(): raise FileExistsError('Se conserva el archivo existente: ' + str(target))
    temporary = target.with_name(target.name + '.pending.' + str(os.getpid())); h = hashlib.sha256(); count = 0
    try:
        with temporary.open('xb') as out:
            for row in parts:
                with (parts_folder / row['name']).open('rb') as source:
                    for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
                        out.write(block); h.update(block); count += len(block)
        assert count == info['zip_bytes'] and h.hexdigest() == info['zip_sha256'], 'Reconstrucción diferente'
        os.rename(temporary, target)
    except BaseException:
        if temporary.exists(): temporary.unlink()  # only this new process-owned partial output
        raise
    print('CPC6 reconstruido íntegramente:', target)
    print('Bytes:', count); print('SHA-256:', h.hexdigest())


if __name__ == '__main__': main()
