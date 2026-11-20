"""Lossless storage for native snapshots; never prepares or edits a world.

Logical paths and SHA-256 remain those of the original native byte streams.
Gzip is only a transport/storage encoding. Workspace originals are not deleted.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
BLOCK = 4 * 1024 * 1024
MAP_NAME = 'LOGICAL_STATES.json'
SCHEMA = 'CPC6.logical-native-states.v1'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(BLOCK), b''): h.update(block)
    return h.hexdigest()


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + '.pending.' + str(os.getpid()))
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(pending, path)


def safe(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or any(':' in x for x in p.parts):
        raise ValueError('Unsafe logical/encoded path: ' + name)
    return p


def logical_open(path):
    """Open logical bytes. An explicit .gz path also means decoded bytes here."""
    path = Path(path)
    if path.is_file(): return gzip.open(path, 'rb') if path.name.endswith('.gz') else path.open('rb')
    encoded = path.with_name(path.name + '.gz')
    if not encoded.is_file(): raise FileNotFoundError(path)
    return gzip.open(encoded, 'rb')


def logical_sha(path):
    h = hashlib.sha256()
    with logical_open(path) as stream:
        for block in iter(lambda: stream.read(BLOCK), b''): h.update(block)
    return h.hexdigest()


@contextmanager
def materialized(path, max_bytes=8 * 1024**3):
    """Yield original plain path, or an owned short-lived exact decoded file.

    Gzip CRC is checked through EOF before yielding to the native reader. The
    original (plain or encoded) is never replaced. No physical fields change.
    """
    path = Path(path)
    if path.is_file() and not path.name.endswith('.gz'):
        yield path; return
    with tempfile.TemporaryDirectory(prefix='cpc6_decode_') as temporary:
        target = Path(temporary) / 'native.deetsnap'; count = 0
        with logical_open(path) as source, target.open('xb') as output:
            for block in iter(lambda: source.read(BLOCK), b''):
                count += len(block)
                if count > max_bytes: raise ValueError('Decoded snapshot exceeds explicit storage bound')
                output.write(block)
        yield target


def inspect_encoded(path, logical_sha256, logical_bytes, original=None):
    """Read through gzip EOF (CRC), hash bytes and optionally compare every byte."""
    h = hashlib.sha256(); count = 0; reference = Path(original).open('rb') if original else None
    try:
        with gzip.open(path, 'rb') as source:
            for block in iter(lambda: source.read(BLOCK), b''):
                if reference is not None and reference.read(len(block)) != block:
                    raise AssertionError('Decoded bytes differ from original')
                h.update(block); count += len(block)
            if reference is not None: assert not reference.read(1)
    finally:
        if reference is not None: reference.close()
    assert count == logical_bytes and h.hexdigest() == logical_sha256
    return {'gzip_CRC_verified': True, 'decoded_bytes': count, 'decoded_sha256': h.hexdigest(),
            'byte_for_byte_original_comparison': reference is not None}


def stage_states(root, stage):
    # Import only for the engineering file selection, not the runtime adapter.
    from package_cpc6 import selected
    root, stage = Path(root).resolve(), Path(stage).resolve(); started = time.monotonic()
    stage.mkdir(parents=True, exist_ok=True); old_path = stage / MAP_NAME
    previous = json.loads(old_path.read_text(encoding='utf-8')) if old_path.exists() else {'schema': SCHEMA, 'states': []}
    assert previous['schema'] == SCHEMA
    old = {x['logical_path']: x for x in previous['states']}; rows = []; reused = 0
    states = [(path, rel) for path, rel in selected(root) if rel.startswith('resultados/') and rel.endswith('.deetsnap')]
    assert set(old).issubset({rel for _, rel in states}), 'A previously staged state vanished from the selection'
    for index, (source, rel) in enumerate(states):
        safe(rel); encoded_rel = rel + '.gz'; target = stage / encoded_rel
        before = (source.stat().st_size, source.stat().st_mtime_ns); logical_identity = sha(source)
        if rel in old:
            row = old[rel]
            assert row['logical_sha256'] == logical_identity and row['logical_bytes'] == before[0], 'Previously staged logical source changed'
            assert target.stat().st_size == row['encoded_bytes'] and sha(target) == row['encoded_sha256']; reused += 1
        else:
            if target.exists(): raise FileExistsError('Unindexed encoding preserved: ' + str(target))
            target.parent.mkdir(parents=True, exist_ok=True); pending = target.with_name(target.name + '.pending.' + str(os.getpid()))
            try:
                with source.open('rb') as plain, pending.open('xb') as sink:
                    with gzip.GzipFile(filename='', mode='wb', compresslevel=9, mtime=0, fileobj=sink) as encoded:
                        shutil.copyfileobj(plain, encoded, BLOCK)
                assert before == (source.stat().st_size, source.stat().st_mtime_ns), 'Writer changed snapshot while encoding'
                proof = inspect_encoded(pending, logical_identity, before[0], original=source)
                os.rename(pending, target)
            except BaseException:
                if pending.exists(): pending.unlink()  # only this newly-created process-owned partial
                raise
            row = {'logical_path': rel, 'logical_bytes': before[0], 'logical_sha256': logical_identity,
                   'encoded_path': encoded_rel, 'encoded_bytes': target.stat().st_size, 'encoded_sha256': sha(target),
                   'encoding': 'gzip; level9; mtime0; no embedded filename', 'proof': proof}
        # Also verify reused files: no regeneration is merely assumed.
        if rel in old: inspect_encoded(target, logical_identity, before[0], original=source)
        rows.append(row)
        if index % 100 == 0: print(json.dumps({'states_encoded_and_byte_verified': index + 1, 'total': len(states)}), flush=True)
    value = {'schema': SCHEMA, 'root_in_zip': 'CPC6/', 'paths_relative_to': 'CPC6 package root',
             'created_utc': previous.get('created_utc', datetime.now(timezone.utc).isoformat()),
             'updated_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Only resultados/**/*.deetsnap; genealogy fixtures remain plain.',
             'original_workspace_states_deleted_or_changed': False, 'states': rows,
             'logical_bytes': sum(x['logical_bytes'] for x in rows), 'encoded_bytes': sum(x['encoded_bytes'] for x in rows),
             'states_count': len(rows), 'reused_encodings_verified_again': reused,
             'elapsed_seconds': time.monotonic() - started}
    put(stage / MAP_NAME, value); put(root / MAP_NAME, value)
    return value


def mapped_files(root, stage, files):
    root, stage = Path(root), Path(stage)
    mapping = json.loads((root / MAP_NAME).read_text(encoding='utf-8')); assert mapping['schema'] == SCHEMA
    assert sha(root / MAP_NAME) == sha(stage / MAP_NAME)
    rows = {x['logical_path']: x for x in mapping['states']}
    raw = {rel: path for path, rel in files if rel.startswith('resultados/') and rel.endswith('.deetsnap')}
    assert set(rows) == set(raw), 'Snapshot staging is stale: finish writers and stage again'
    result = []
    for source, rel in files:
        if rel not in rows: result.append((source, rel)); continue
        row = rows[rel]; safe(row['encoded_path']); path = stage / row['encoded_path']
        assert source.stat().st_size == row['logical_bytes'] and sha(source) == row['logical_sha256']
        assert path.stat().st_size == row['encoded_bytes'] and sha(path) == row['encoded_sha256']
        result.append((path, row['encoded_path']))
    return result


def verify_tree(root):
    root = Path(root); data = json.loads((root / MAP_NAME).read_text(encoding='utf-8')); assert data['schema'] == SCHEMA
    for row in data['states']:
        safe(row['logical_path']); safe(row['encoded_path']); path = root / row['encoded_path']
        assert path.stat().st_size == row['encoded_bytes'] and sha(path) == row['encoded_sha256']
        inspect_encoded(path, row['logical_sha256'], row['logical_bytes'])
    return {'schema': 'CPC6.logical-state-check.v1', 'verified': True, 'count': len(data['states']),
            'logical_bytes': data['logical_bytes'], 'encoded_bytes': data['encoded_bytes'],
            'every_gzip_CRC_and_decoded_SHA_verified': True}


def materialize_all(root):
    root = Path(root); data = json.loads((root / MAP_NAME).read_text(encoding='utf-8')); assert data['schema'] == SCHEMA
    restored = 0; existing = 0
    for row in data['states']:
        safe(row['logical_path']); safe(row['encoded_path']); target = root / row['logical_path']; encoded = root / row['encoded_path']
        if target.exists():
            assert target.stat().st_size == row['logical_bytes'] and sha(target) == row['logical_sha256']; existing += 1; continue
        assert encoded.stat().st_size == row['encoded_bytes'] and sha(encoded) == row['encoded_sha256']
        target.parent.mkdir(parents=True, exist_ok=True); pending = target.with_name(target.name + '.pending.' + str(os.getpid()))
        try:
            h = hashlib.sha256(); count = 0
            with gzip.open(encoded, 'rb') as source, pending.open('xb') as out:
                for block in iter(lambda: source.read(BLOCK), b''): out.write(block); h.update(block); count += len(block)
            assert count == row['logical_bytes'] and h.hexdigest() == row['logical_sha256']
            os.rename(pending, target); restored += 1
        except BaseException:
            if pending.exists(): pending.unlink()
            raise
    return {'verified': True, 'restored': restored, 'already_present_and_byte_identity_verified': existing,
            'scope': 'Explicit technical decompression for direct legacy readers; no simulation, preparation or RAW/clock edit.'}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('action', choices=('stage', 'verify', 'materialize-all'))
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1]); p.add_argument('--stage', type=Path)
    p.add_argument('--report', type=Path, required=True); a = p.parse_args()
    if a.action == 'stage': result = stage_states(a.root, a.stage)
    elif a.action == 'verify': result = verify_tree(a.root)
    else: result = materialize_all(a.root)
    put(a.report, result); print(json.dumps({key: value for key, value in result.items() if key != 'states'}, indent=2))


if __name__ == '__main__': main()
