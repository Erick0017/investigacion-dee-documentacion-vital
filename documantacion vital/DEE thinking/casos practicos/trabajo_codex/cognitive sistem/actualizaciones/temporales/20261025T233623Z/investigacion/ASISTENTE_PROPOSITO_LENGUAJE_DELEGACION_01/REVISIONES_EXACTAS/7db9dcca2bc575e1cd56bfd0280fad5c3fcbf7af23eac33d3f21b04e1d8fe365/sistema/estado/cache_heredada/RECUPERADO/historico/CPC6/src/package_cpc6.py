"""Seal and publish only CPC6. Technical integrity is not a cognition verdict.

The one manifest is relative to the CPC6 package root. It excludes itself and
HASHES; HASHES covers the payload and MANIFEST, never the ZIP's own identity.
Publication is separate and requires an exact-candidate clean native replay.
"""
from __future__ import annotations
import argparse
from collections import Counter
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
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
NAME = 'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip'
WHL = 'dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
WHL_SHA = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA = '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
BLOCK = 4 * 1024 * 1024
EXCLUDED = {'.venv', '__pycache__', '.git', '.pytest_cache', '_distribution_tests'}
PROTECTED = {
 'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip': '1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6',
 'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip': '4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip': 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
}
PRODUCT_ZIP_SHA = 'c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf'


def sha(path):
    with Path(path).open('rb') as stream: return stream_sha(stream)


def stream_sha(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(BLOCK), b''): h.update(block)
    return h.hexdigest()


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending.' + str(os.getpid()))
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)


def safe_relative(name):
    p = PurePosixPath(name)
    assert name and not p.is_absolute() and '\\' not in name
    assert '..' not in p.parts and all(':' not in item for item in p.parts)
    return p


def protected_sources(root):
    # Only a development/publication check; clean portable replay does not need
    # any historical delivery or private directory to be available.
    cases = root.parents[1]; rows = []
    if not all((cases / name).is_file() for name in PROTECTED):
        raise FileNotFoundError('Protected source identity checks require the original publication directory')
    targets = [(cases / name, identity) for name, identity in PROTECTED.items()]
    product = cases.parent / '4.0'
    targets += [(product / 'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip', PRODUCT_ZIP_SHA),
                (product / WHL, WHL_SHA)]
    for path, expected in targets:
        actual = sha(path)
        assert actual == expected, 'Protected original differs: ' + str(path)
        rows.append({'name': path.name, 'bytes': path.stat().st_size, 'sha256': actual, 'unchanged': True})
    return rows


def selected(root):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in EXCLUDED)
        for name in sorted(files):
            path = Path(directory) / name; rel = path.relative_to(root)
            if path.is_symlink(): raise ValueError('No symlink in standalone payload: ' + str(path))
            if len(rel.parts) == 1 and name in {'MANIFEST.json', 'HASHES.sha256'}: continue
            if name.endswith(('.pyc', '.pyo', '.tmp')) or '.pending.' in name: continue
            if name.endswith(('.zip', '.zip.001', '.zip.002')): raise ValueError('No nested delivery ZIP: ' + str(path))
            # Explicitly technical copied/extracted trees only, never a generic
            # exclusion of scientific states or unfavorable measurements.
            if len(rel.parts) > 2 and rel.parts[0] == 'resultados' and rel.parts[1].startswith(('clean_', 'minimal_app_')) and any(x in {'extracted', 'isolated_env', 'minimal_payload', 'generated'} for x in rel.parts[2:]): continue
            safe_relative(rel.as_posix()); yield path, rel.as_posix()


def engine(root):
    wheel = root / 'runtime' / WHL
    assert sha(wheel) == WHL_SHA
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        names = [x for x in z.namelist() if x.endswith('.pyd')]
        assert len(names) == 1 and hashlib.sha256(z.read(names[0])).hexdigest() == PYD_SHA
    assert sha(root / 'genealogia/kernel_v27.cpp') == KERNEL_SHA
    return {'wheel_sha256': WHL_SHA, 'native_sha256': PYD_SHA, 'kernel_source_sha256': KERNEL_SHA}


def build(root, candidate, storage_stage=None):
    assert root.name == 'CPC6', 'Never package another campaign under CPC6'
    if not candidate.name.endswith('.candidate.zip') or candidate.exists(): raise FileExistsError(candidate)
    started = time.monotonic(); identities = engine(root); originals = protected_sources(root)
    files = list(selected(root))
    if (root / 'LOGICAL_STATES.json').exists():
        if storage_stage is None: raise ValueError('LOGICAL_STATES requires --storage-stage; do not package raw duplicates')
        from snapshot_storage import mapped_files
        files = mapped_files(root, storage_stage, files)
    elif storage_stage is not None: raise FileNotFoundError(root / 'LOGICAL_STATES.json')
    rows = [{'path': rel, 'bytes': path.stat().st_size, 'sha256': sha(path)} for path, rel in files]
    assert len(rows) == len({r['path'] for r in rows})
    put(root / 'MANIFEST.json', {'schema': 'CPC6.payload-manifest.v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'paths_relative_to': 'CPC6 package root; omit CPC6/ prefix', 'root_in_zip': 'CPC6/',
        'files': rows, 'payload_bytes': sum(r['bytes'] for r in rows), 'engine': identities,
        'protected_originals': originals, 'self_exclusions': ['MANIFEST.json', 'HASHES.sha256'],
        'scope': 'New CPC6 only. No historical ZIPs, virtualenvs, caches, toolchains or postpublication ZIP identity.'})
    lines = [r['sha256'] + '  ' + r['path'] for r in rows]
    lines.append(sha(root / 'MANIFEST.json') + '  MANIFEST.json')
    (root / 'HASHES.sha256').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True, strict_timestamps=False) as z:
        for path, rel in files: z.write(path, 'CPC6/' + rel)
        for name in ('MANIFEST.json', 'HASHES.sha256'): z.write(root / name, 'CPC6/' + name)
    report = verify(candidate); report['build_seconds'] = time.monotonic() - started
    return report


def verify(candidate):
    started = time.monotonic()
    with zipfile.ZipFile(candidate) as z:
        names = z.namelist(); assert len(names) == len(set(names))
        for name in names:
            assert name.startswith('CPC6/'); safe_relative(name)
            assert not any(x in EXCLUDED for x in PurePosixPath(name).parts)
        assert z.testzip() is None, 'CRC failure'
        manifest = json.loads(z.read('CPC6/MANIFEST.json'))
        assert manifest['schema'] == 'CPC6.payload-manifest.v1'
        assert manifest['paths_relative_to'] == 'CPC6 package root; omit CPC6/ prefix'
        payload = {r['path']: r for r in manifest['files']}; hashes = {}
        for line in z.read('CPC6/HASHES.sha256').decode('utf-8').splitlines():
            identity, rel = line.split('  ', 1); safe_relative(rel); assert rel not in hashes; hashes[rel] = identity
        assert set(hashes) == set(payload) | {'MANIFEST.json'}
        assert set(names) == {'CPC6/' + x for x in hashes} | {'CPC6/HASHES.sha256'}
        expanded = Counter(); compressed = Counter()
        for name in names:
            info = z.getinfo(name); rel = name.removeprefix('CPC6/'); category = rel.split('/')[0]
            expanded[category] += info.file_size; compressed[category] += info.compress_size
            if rel in hashes:
                with z.open(name) as stream: assert stream_sha(stream) == hashes[rel], 'Member SHA differs: ' + name
                if rel in payload: assert info.file_size == payload[rel]['bytes'] and payload[rel]['sha256'] == hashes[rel]
        assert [x for x in names if x.endswith(WHL)] == ['CPC6/runtime/' + WHL]
        assert hashlib.sha256(z.read('CPC6/runtime/' + WHL)).hexdigest() == WHL_SHA
        assert hashlib.sha256(z.read('CPC6/genealogia/kernel_v27.cpp')).hexdigest() == KERNEL_SHA
        required = ('ejecutar.py', 'app.py', 'LEEME.md', 'revision/LEER_PRIMERO.md', 'revision/LECTURA_PROVISIONAL.md', 'revision/OBSERVACIONES.jsonl')
        assert all('CPC6/' + name in names for name in required), 'Missing public runner or scientific review'
        snapshots = [x for x in names if x.endswith('.deetsnap')]
        plain_snapshot_bytes = sum(z.getinfo(x).file_size for x in snapshots)
        encoded_states = [x for x in names if x.endswith('.deetsnap.gz')]
        logical_states = None
        if 'CPC6/LOGICAL_STATES.json' in names:
            from snapshot_storage import SCHEMA
            logical_states = json.loads(z.read('CPC6/LOGICAL_STATES.json')); assert logical_states['schema'] == SCHEMA
            states = logical_states['states']; assert len(states) == len({x['logical_path'] for x in states})
            assert set(encoded_states) == {'CPC6/' + x['encoded_path'] for x in states}
            for row in states:
                safe_relative(row['logical_path']); safe_relative(row['encoded_path'])
                assert row['logical_path'].startswith('resultados/') and row['logical_path'].endswith('.deetsnap')
                assert row['encoded_path'] == row['logical_path'] + '.gz'
                assert 'CPC6/' + row['logical_path'] not in names, 'Raw duplicate in compact delivery'
                assert payload[row['encoded_path']]['bytes'] == row['encoded_bytes']
                assert payload[row['encoded_path']]['sha256'] == row['encoded_sha256']
                count = 0; logical_sha = hashlib.sha256()
                with z.open('CPC6/' + row['encoded_path']) as stored:
                    with gzip.GzipFile(fileobj=stored, mode='rb') as decoded:
                        for block in iter(lambda: decoded.read(BLOCK), b''):
                            count += len(block); logical_sha.update(block)
                assert count == row['logical_bytes'] and logical_sha.hexdigest() == row['logical_sha256']
                assert row['proof']['gzip_CRC_verified'] and row['proof']['byte_for_byte_original_comparison']
        else: assert not encoded_states, 'Encoded states need their logical identity manifest'
        assert snapshots or encoded_states, 'No physical/operative checkpoint'
    return {'schema': 'CPC6.container-verification.v1', 'status': 'VERIFIED', 'path': str(candidate.resolve()),
        'sha256': sha(candidate), 'bytes': candidate.stat().st_size, 'expanded_bytes': sum(expanded.values()),
        'members': len(names), 'manifest_hashes_verified': len(hashes), 'checkpoint_members': len(snapshots) + len(encoded_states),
        'plain_checkpoint_members': len(snapshots), 'encoded_checkpoint_members': len(encoded_states),
        'logical_snapshot_bytes': (logical_states['logical_bytes'] if logical_states else 0) + plain_snapshot_bytes,
        'encoded_snapshot_bytes': logical_states['encoded_bytes'] if logical_states else 0,
        'all_encoded_gzip_CRC_and_logical_SHA_verified': bool(logical_states),
        'crc_verified': True, 'engine': {'wheel_sha256': WHL_SHA, 'native_sha256': PYD_SHA, 'kernel_source_sha256': KERNEL_SHA},
        'expanded_bytes_by_category': dict(expanded), 'compressed_bytes_by_category': dict(compressed),
        'verification_seconds': time.monotonic() - started}


def split_transport(path, destination):
    size = path.stat().st_size
    if size <= 20 * 1024 * 1024: return {'split_required': False, 'threshold_compressed_bytes': 20 * 1024 * 1024}
    # CPC5 owns the generic PARTES.json and instructions already in cases
    # practicos. Never overwrite them: keep CPC6's parts beside the canonical
    # ZIP, and its conflicting generic metadata/helpers in transporte_CPC6.
    conflict = any((destination / name).exists() for name in ('PARTES.json', 'INSTRUCCIONES_PARTES.txt', 'REUNIR_CPC6.py'))
    metadata = destination / 'transporte_CPC6' if conflict else destination
    for path_name in (NAME + '.001', NAME + '.002'):
        if (destination / path_name).exists(): raise FileExistsError(destination / path_name)
    for name in ('PARTES.json', 'INSTRUCCIONES_PARTES.txt', 'REUNIR_CPC6.py'):
        if (metadata / name).exists(): raise FileExistsError(metadata / name)
    metadata.mkdir(parents=True, exist_ok=True); rows = []; identity = sha(path)
    with path.open('rb') as stream:
        for order, count in ((1, (size + 1) // 2), (2, size // 2)):
            target = destination / (NAME + f'.{order:03d}'); temporary = target.with_name(target.name + '.pending.' + str(os.getpid()))
            h = hashlib.sha256(); left = count
            with temporary.open('xb') as out:
                while left:
                    block = stream.read(min(BLOCK, left)); assert block; out.write(block); h.update(block); left -= len(block)
            os.rename(temporary, target)
            rows.append({'order': order, 'name': target.name, 'bytes': count, 'sha256': h.hexdigest()})
        assert not stream.read(1)
    with tempfile.TemporaryFile(dir=metadata) as joined:
        for row in rows:
            with (destination / row['name']).open('rb') as source: shutil.copyfileobj(source, joined, BLOCK)
        assert joined.tell() == size; joined.seek(0); actual = stream_sha(joined)
    assert actual == identity == sha(path)
    report = {'schema': 'CPC6.binary-parts.v1', 'zip_name': NAME, 'zip_bytes': size, 'zip_sha256': identity,
        'parts_directory': '..' if conflict else '.', 'parts': rows, 'reconstruction_tested': True,
        'reconstruction_sha256': actual, 'metadata_directory': str(metadata.resolve()),
        'scope': 'Exactly two sequential binary partitions, not independent ZIPs. Existing CPC5 transport metadata is untouched.'}
    put(metadata / 'PARTES.json', report)
    for name in ('REUNIR_CPC6.py', 'INSTRUCCIONES_PARTES.txt'): shutil.copyfile(ROOT / name, metadata / name)
    return report


def publish(root, candidate, destination, clean_report):
    report = verify(candidate); proof = json.loads(clean_report.read_text(encoding='utf-8'))
    assert proof['status'] == 'VERIFIED' and proof['candidate_sha256'] == report['sha256']
    assert proof.get('explicit_posttrajectory_verification')
    assert proof.get('commands') and all(x['status'] == 'COMPLETED' and x['exit_code'] == 0 for x in proof['commands'])
    assert proof['plan_sha256'] == sha(root / 'configuraciones/clean_reproduction_plan.json')
    originals = protected_sources(root); target = destination / NAME
    if target.exists(): raise FileExistsError('New CPC6 must not overwrite an existing release: ' + str(target))
    small = [('LEER_PRIMERO.md', 'CPC6_LEER_PRIMERO.md'), ('LECTURA_PROVISIONAL.md', 'CPC6_LECTURA_PROVISIONAL.md')]
    for _, name in small:
        if (destination / name).exists(): raise FileExistsError(destination / name)
    transport = split_transport(candidate, destination)
    for source, name in small: shutil.copyfile(root / 'revision' / source, destination / name)
    # Windows rename refuses a concurrently-created target. No existing CPC6,
    # CPC5 or other release is destroyed to publish a new campaign.
    os.rename(candidate, target); assert sha(target) == report['sha256']
    assert protected_sources(root) == originals
    return {'published_utc': datetime.now(timezone.utc).isoformat(), 'canonical': str(target.resolve()),
        **{k: v for k, v in report.items() if k != 'path'}, 'transport': transport,
        'protected_originals': originals, 'exact_candidate_clean_reproduction': proof}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('action', choices=('build', 'verify', 'publish', 'protected'))
    p.add_argument('--root', type=Path, default=ROOT); p.add_argument('--candidate', type=Path)
    p.add_argument('--storage-stage', type=Path)
    p.add_argument('--destination', type=Path); p.add_argument('--clean-report', type=Path); p.add_argument('--report', type=Path, required=True)
    a = p.parse_args(); root = a.root.resolve()
    if a.action == 'build': result = build(root, a.candidate.resolve(), a.storage_stage.resolve() if a.storage_stage else None)
    elif a.action == 'verify': result = verify(a.candidate.resolve())
    elif a.action == 'protected': result = {'protected_originals': protected_sources(root), 'engine': engine(root)}
    else: result = publish(root, a.candidate.resolve(), a.destination.resolve(), a.clean_report.resolve())
    put(a.report, result); print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
