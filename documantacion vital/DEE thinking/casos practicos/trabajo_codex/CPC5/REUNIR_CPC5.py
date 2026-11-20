"""Verify and join exactly two CPC5 binary parts, without overwriting files."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carpeta', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    folder = args.carpeta.resolve()
    data = json.loads((folder / 'PARTES.json').read_text(encoding='utf-8'))
    parts = data['parts']
    assert [p['order'] for p in parts] == [1, 2]
    for p in parts:
        assert Path(p['name']).name == p['name'], 'Nombre no seguro'
        source = folder / p['name']
        assert source.stat().st_size == p['bytes'], 'Tamaño de parte diferente'
        assert file_hash(source) == p['sha256'], 'SHA-256 de parte diferente'
    default_name = data['zip_name'].removesuffix('.zip') + '_REUNIDO.zip'
    target = (args.salida or (folder / default_name)).resolve()
    if target.exists():
        raise FileExistsError('No se sobrescribe el archivo existente: ' + str(target))
    temp = target.with_name(target.name + '.pending.' + str(os.getpid()))
    h = hashlib.sha256(); size = 0
    try:
        with temp.open('xb') as out:
            for p in parts:
                with (folder / p['name']).open('rb') as source:
                    for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
                        out.write(block); h.update(block); size += len(block)
        assert size == data['zip_bytes'], 'Tamaño reconstruido diferente'
        assert h.hexdigest() == data['zip_sha256'], 'SHA-256 reconstruido diferente'
        if target.exists(): raise FileExistsError(target)
        os.rename(temp, target)
    except BaseException:
        if temp.exists(): temp.unlink()  # only this process's new partial output
        raise
    print('Reconstrucción íntegra:', target)
    print('Bytes:', size)
    print('SHA-256:', h.hexdigest())


if __name__ == '__main__': main()
