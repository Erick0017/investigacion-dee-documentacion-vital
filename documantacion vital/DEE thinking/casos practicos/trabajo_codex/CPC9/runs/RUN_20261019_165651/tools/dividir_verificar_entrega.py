"""Split private canonical ZIPs into <=16,000,000-byte verified segments.

Canonicals remain unchanged. Every reconstruction is actually written, hashed
and compared byte-for-byte before the transport manifest is issued. Atomic
no-clobber publication requires hardlink support in the destination filesystem
(tested on NTFS); unsupported filesystems fail without replacing any target.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

MAX_BYTES = 16_000_000


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def dump(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if path.exists():
        if path.read_bytes() == data:
            return
        raise FileExistsError('Protect existing delivery metadata: ' + str(path))
    with path.open('xb') as f:
        f.write(data)


def publish_noclobber(temporary, target):
    """Atomic destination creation, including when another writer wins a race."""
    if temporary.parent.resolve() != target.parent.resolve():
        raise ValueError('No-clobber publication requires the same directory/filesystem')
    os.link(temporary, target)
    temporary.unlink()


def equal_bytes(first, second):
    if first.stat().st_size != second.stat().st_size:
        return False
    with first.open('rb') as a, second.open('rb') as b:
        for block in iter(lambda: a.read(1024 * 1024), b''):
            if block != b.read(len(block)):
                return False
        return not b.read(1)


MERGER = r'''"""Join and verify numbered segments. No-clobber hardlink publication requires NTFS or equivalent filesystem hardlink support."""
import argparse,hashlib,json,os
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def leaf(s):
    if not isinstance(s,str) or not s or Path(s).name!=s or '/' in s or '\\' in s or ':' in s or s in('.','..'):raise ValueError('Unsafe leaf name')
    return s

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=Path(__file__).with_name('PARTES.json'));p.add_argument('--archivo');p.add_argument('--out',type=Path);a=p.parse_args()
    source=a.manifest.resolve(strict=True);data=json.loads(source.read_text(encoding='utf-8'));folder=source.parent;out=(a.out or folder).resolve();out.mkdir(parents=True,exist_ok=True)
    selected=[x for x in data['archives'] if a.archivo is None or x['name']==a.archivo]
    if not selected:raise ValueError('Archive not found in transport manifest')
    for entry in selected:
        target=out/leaf(entry['name'])
        if target.exists():
            if target.stat().st_size==entry['bytes'] and sha(target)==entry['sha256']:print('YA VERIFICADO: '+str(target));continue
            raise FileExistsError('Existing canonical does not match; preserved: '+str(target))
        if not entry['parts']:raise FileNotFoundError('This small canonical was not divided; obtain '+entry['name'])
        parts=entry['parts']
        if [x['index']for x in parts]!=list(range(1,len(parts)+1)):raise ValueError('Incorrect segment order')
        temporary=target.with_name(target.name+'.joining.'+str(os.getpid()))
        if temporary.exists():raise FileExistsError(str(temporary))
        with temporary.open('xb') as dst:
            for part in parts:
                path=folder/leaf(part['name'])
                if path.stat().st_size!=part['bytes'] or part['bytes']>data['maximum_part_bytes'] or sha(path)!=part['sha256']:raise ValueError('Part size/hash mismatch: '+path.name)
                with path.open('rb') as src:
                    for block in iter(lambda:src.read(1048576),b''):dst.write(block)
        if temporary.stat().st_size!=entry['bytes'] or sha(temporary)!=entry['sha256']:raise ValueError('Full reconstruction failed; evidence retained')
        # Atomic fail-if-exists: a concurrent writer cannot be overwritten.
        # Both names are in the same folder. Unsupported hardlinks fail safely.
        os.link(temporary,target);temporary.unlink();print('RECONSTRUIDO Y VERIFICADO: '+str(target))
if __name__=='__main__':main()
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archives', nargs='+', type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--max-part-bytes', type=int, default=MAX_BYTES)
    p.add_argument('--force-split', action='store_true')
    a = p.parse_args()
    if not 1_000_000 <= a.max_part_bytes <= MAX_BYTES:
        p.error('Part size must be1,000,000..16,000,000 bytes')
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources = [x.resolve(strict=True) for x in a.archives]
    if len({x.name.casefold() for x in sources}) != len(sources):
        raise ValueError('Archive leaf names must be unique')
    result = {'schema': 'DEE.private.segment.transport.v1', 'maximum_part_bytes': a.max_part_bytes,
              'segment_kind': 'Sequential binary segments, NOT independent ZIP archives',
              'publication_contract': 'Atomic fail-if-exists via hardlinks in the same directory. Destination filesystem must support hardlinks (NTFS tested); unsupported filesystems fail without overwriting.',
              'canonical_archives_retained': True, 'archives': []}
    started = time.monotonic()
    for source in sources:
        if source.suffix.lower() != '.zip':
            raise ValueError('Only explicit canonical ZIPs may be divided')
        size = source.stat().st_size
        entry = {'name': source.name, 'bytes': size, 'sha256': sha(source), 'parts': [],
                 'reconstruction_verified': False, 'byte_comparison_verified': False}
        result['archives'].append(entry)
        if size <= a.max_part_bytes and not a.force_split:
            entry.update(reconstruction_verified=True, byte_comparison_verified=True,
                         verification_kind='Canonical below transfer limit, no segmentation required')
            continue
        count = (size + a.max_part_bytes - 1) // a.max_part_bytes
        # Approximately equal pieces, never above the hard transfer limit.
        part_size = (size + count - 1) // count
        width = max(3, len(str(count)))
        with source.open('rb') as src:
            for index in range(1, count + 1):
                data = src.read(part_size)
                name = source.name + '.' + str(index).zfill(width)
                path = out / name
                digest = hashlib.sha256(data).hexdigest()
                if path.exists():
                    if path.stat().st_size != len(data) or sha(path) != digest:
                        raise FileExistsError('Protect conflicting existing segment: ' + str(path))
                else:
                    temporary = path.with_name(path.name + '.building.' + str(os.getpid()))
                    with temporary.open('xb') as f:
                        f.write(data)
                    publish_noclobber(temporary, path)
                entry['parts'].append({'index': index, 'name': name, 'bytes': len(data), 'sha256': digest})
            if src.read(1):
                raise AssertionError('Segmentation failed to consume canonical')
        reconstructed = out / (source.name + '.verification-reconstructed.' + str(os.getpid()))
        if reconstructed.exists():
            raise FileExistsError(str(reconstructed))
        with reconstructed.open('xb') as dst:
            for part in entry['parts']:
                with (out / part['name']).open('rb') as src:
                    for block in iter(lambda: src.read(1024 * 1024), b''):
                        dst.write(block)
        entry['reconstruction_verified'] = sha(reconstructed) == entry['sha256'] and reconstructed.stat().st_size == size
        entry['byte_comparison_verified'] = equal_bytes(source, reconstructed)
        if not entry['reconstruction_verified'] or not entry['byte_comparison_verified'] or sha(source) != entry['sha256']:
            raise AssertionError('Reconstruction or unchanged-canonical check failed; verification file retained')
        entry['verification_kind'] = 'Actual reconstructed file, SHA-256, length and complete byte comparison'
        # Only this explicit verified scratch file, never source/canonical/parts.
        reconstructed.resolve(strict=True).relative_to(out)
        reconstructed.unlink()
    result['elapsed_seconds'] = time.monotonic() - started
    # Omit volatile elapsed time from protected transport manifest for reruns.
    metadata = {k: v for k, v in result.items() if k != 'elapsed_seconds'}
    dump(out / 'PARTES.json', metadata)
    merger = out / 'REUNIR_ENTREGA.py'
    encoded_merger = MERGER.encode('utf-8')
    if merger.exists() and merger.read_bytes() != encoded_merger:
        raise FileExistsError('Protect existing union script')
    if not merger.exists():
        with merger.open('xb') as f:
            f.write(encoded_merger)
    instructions = ('ENTREGA PRIVADA DEE\n\nCada archivo .001, .002, etc. es un segmento binario, no un ZIP independiente.\n'
        'Descargue PARTES.json, REUNIR_ENTREGA.py y TODAS las partes del ZIP elegido en la misma carpeta.\n'
        'Cada parte mide como máximo ' + str(a.max_part_bytes) + ' bytes (16 MB decimales como máximo).\n'
        'Con Python3, ejecute: python REUNIR_ENTREGA.py\n'
        'Para seleccionar uno: python REUNIR_ENTREGA.py --archivo NOMBRE_COMPLETO.zip\n'
        'El script verifica orden, tamaños, SHA-256 de cada parte y SHA-256 del ZIP reconstruido.\n'
        'No sobrescribe archivos distintos ya existentes. Un ZIP canónico ya correcto se verifica sin cambiarlo.\n'
        'La publicación sin sobrescritura usa enlaces físicos atómicos en la misma carpeta: requiere NTFS u otro sistema de archivos con hardlinks.\n'
        'Si el destino no admite hardlinks, el programa falla conservando el temporal; no usa un reemplazo que pueda sobrescribir datos.\n'
        'Los ZIP pequeños no se dividen; deben descargarse directamente. Conserve los ZIP canónicos originales.\n')
    target = out / 'INSTRUCCIONES_PARTES.txt'
    if target.exists() and target.read_text(encoding='utf-8') != instructions:
        raise FileExistsError('Protect existing instructions')
    if not target.exists():
        with target.open('xb') as f:
            f.write(instructions.encode('utf-8'))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
