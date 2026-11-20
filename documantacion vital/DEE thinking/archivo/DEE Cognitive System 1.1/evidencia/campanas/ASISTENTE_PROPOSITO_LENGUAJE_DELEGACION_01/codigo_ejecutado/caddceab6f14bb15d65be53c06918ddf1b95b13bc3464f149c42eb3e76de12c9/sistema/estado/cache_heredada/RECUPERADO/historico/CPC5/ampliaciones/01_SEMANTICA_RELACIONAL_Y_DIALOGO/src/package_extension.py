"""Cumulative CPC5 sealing. Reads inherited bytes only from the frozen parent ZIP.

The historic manifest is never rewritten. The new manifest lists archive-root
paths (including CPC5/); HASHES covers only additions and this new manifest.
Publication is separate and requires an exact-candidate clean replay report.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import time
import zipfile

EXT = Path(__file__).resolve().parents[1]
BASE = EXT.parents[1]
PREFIX = 'CPC5/ampliaciones/' + EXT.name + '/'
NAME = 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip'
PARENT_SHA = '26c5b0f207b235b6f5990d85f586a5bd7dde440eeb989c4ae5e7eb47fe54b075'
WHL = 'dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
WHL_SHA = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA = '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
NEW_ROOT_FILES = ('SINTESIS_VIGENTE_AMPLIACION_01.md', 'INDICE_AMPLIACIONES.json')
EXCLUDED_DIRS = {'.venv', '__pycache__', '.git', '.pytest_cache', '_clean_extract',
                 '_repro_env', 'staging', 'build'}
BLOCK = 4 * 1024 * 1024
PROTECTED_EXTERNAL = {
    'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip': '4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
    'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip': '1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(BLOCK), b''): h.update(block)
    return h.hexdigest()


def put(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.pending.' + str(os.getpid()))
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, path)


def stream_sha(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(BLOCK), b''): h.update(block)
    return h.hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    if not name.startswith('CPC5/') or '..' in p.parts or p.is_absolute() or '\\' in name:
        raise ValueError('Unsafe ZIP member: ' + name)


def protected_sources():
    rows=[]
    for name,expected in PROTECTED_EXTERNAL.items():
        path=BASE.parents[1]/name
        if not path.is_file():
            rows.append({'name':name,'available':False,'expected_sha256':expected});continue
        actual=sha(path)
        assert actual==expected,'Protected external source changed: '+str(path)
        rows.append({'name':name,'sha256':actual,'bytes':path.stat().st_size,'unchanged':True})
    return rows


def parent_inventory():
    data = json.loads((EXT / 'PARENT_MEMBERS.json').read_text(encoding='utf-8'))
    assert data['sha256'] == PARENT_SHA
    rows = data['members']
    assert len(rows) == len({r['path'] for r in rows})
    for row in rows: safe_name(row['path'])
    return {r['path']: r for r in rows}


def additions():
    for path in sorted(EXT.rglob('*')):
        if not path.is_file(): continue
        rel = path.relative_to(EXT)
        if path.is_symlink(): raise ValueError('Symlink: ' + str(path))
        if any(part in EXCLUDED_DIRS for part in rel.parts): continue
        if len(rel.parts)>=3 and rel.parts[0]=='resultados'and rel.parts[1].startswith('minimal_app_')and any(part in {'minimal_CPC5','generated'}for part in rel.parts[2:]):
            # Technical copies are proven by retained inventory/digests. They
            # are not new scientific states and must not duplicate the wheel.
            continue
        if len(rel.parts) == 1 and path.name in {'MANIFEST.json', 'HASHES.sha256'}: continue
        if path.suffix in {'.pyc', '.pyo', '.tmp'} or '.pending.' in path.name: continue
        if path.name.endswith(('.zip', '.zip.001', '.zip.002')):
            raise ValueError('Nested archive not permitted: ' + str(path))
        yield path, PREFIX + rel.as_posix()
    for name in NEW_ROOT_FILES:
        path = BASE / name
        if not path.is_file(): raise FileNotFoundError(path)
        yield path, 'CPC5/' + name


def build(parent, candidate):
    if not candidate.name.endswith('.candidate.zip'):
        raise ValueError('Candidate name must end .candidate.zip')
    if candidate.exists(): raise FileExistsError(candidate)
    if sha(parent) != PARENT_SHA: raise ValueError('Parent archive changed; preserve and reconcile')
    originals=protected_sources()
    inherited = parent_inventory()
    files = list(additions())
    assert len(files) == len({name for _, name in files})
    assert not set(inherited).intersection(name for _, name in files), 'No inherited overwrite is permitted'
    rows = [{'path': name, 'bytes': path.stat().st_size, 'sha256': sha(path)} for path, name in files]
    manifest = {'schema': 'CPC5.extension.additions-manifest.v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'parent_sha256': PARENT_SHA, 'inherited_member_count': len(inherited),
        'paths_relative_to': 'ZIP archive root, including the CPC5/ prefix',
        'scope': 'Only newly added extension members and two cumulative index/synthesis files',
        'files': rows, 'self_exclusions': [PREFIX + 'MANIFEST.json', PREFIX + 'HASHES.sha256'],
        'historic_manifests': 'Preserved byte-exact; their original scope is unchanged',
        'excluded_technical_duplicate_subtrees':['resultados/minimal_app_*/minimal_CPC5/','resultados/minimal_app_*/generated/'],
        'technical_duplicate_scope':'Only copied isolation trees and their generated demonstration states are excluded. Their reports, logs and inventories remain; primary scientific states are preserved.',
        'payload_bytes': sum(r['bytes'] for r in rows)}
    put(EXT / 'MANIFEST.json', manifest)
    hashes = [r['sha256'] + '  ' + r['path'] for r in rows]
    hashes.append(sha(EXT / 'MANIFEST.json') + '  ' + PREFIX + 'MANIFEST.json')
    (EXT / 'HASHES.sha256').write_text('\n'.join(hashes) + '\n', encoding='utf-8', newline='\n')
    files += [(EXT / x, PREFIX + x) for x in ('MANIFEST.json', 'HASHES.sha256')]
    candidate.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with zipfile.ZipFile(parent) as old, zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED,
            compresslevel=9, allowZip64=True, strict_timestamps=False) as new:
        assert set(old.namelist()) == set(inherited)
        for info in old.infolist():
            # Preserve uncompressed scientific bytes. Container offsets/compression are not identities.
            target = zipfile.ZipInfo(info.filename, info.date_time)
            target.compress_type = zipfile.ZIP_DEFLATED
            target.external_attr = info.external_attr
            target.create_system = info.create_system
            target.comment = info.comment
            target._compresslevel = 9
            target.file_size = info.file_size
            with old.open(info) as source, new.open(target, 'w', force_zip64=True) as out:
                shutil.copyfileobj(source, out, BLOCK)
        for path, name in files: new.write(path, name)
    report = verify(candidate)
    report['build_seconds'] = time.monotonic() - started
    report['protected_sources']=originals
    return report


def verify(candidate):
    started = time.monotonic(); inherited = parent_inventory()
    manifest_name = PREFIX + 'MANIFEST.json'; hashes_name = PREFIX + 'HASHES.sha256'
    with zipfile.ZipFile(candidate) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'Duplicate members'
        for name in names: safe_name(name)
        assert z.testzip() is None, 'CRC error'
        manifest = json.loads(z.read(manifest_name))
        assert manifest['parent_sha256'] == PARENT_SHA
        assert manifest['paths_relative_to'] == 'ZIP archive root, including the CPC5/ prefix'
        hashes = {}
        for line in z.read(hashes_name).decode('utf-8').splitlines():
            identity, name = line.split('  ', 1)
            assert name not in hashes; safe_name(name); hashes[name] = identity
        payload = {r['path']: r for r in manifest['files']}
        assert set(hashes) == set(payload) | {manifest_name}
        assert not set(inherited).intersection(hashes)
        assert set(names) == set(inherited) | set(hashes) | {hashes_name}
        compressed = Counter(); expanded = Counter()
        for name in names:
            info = z.getinfo(name)
            if name in inherited:
                row = inherited[name]; assert info.file_size == row['bytes']
                expected = row['sha256']
            elif name in hashes:
                expected = hashes[name]
                if name in payload: assert info.file_size == payload[name]['bytes']
            else: expected = None
            with z.open(name) as source: actual = stream_sha(source)
            if expected is not None: assert actual == expected, 'Member differs: ' + name
            category = 'inherited' if name in inherited else name.removeprefix(PREFIX).split('/')[0]
            compressed[category] += info.compress_size; expanded[category] += info.file_size
        assert len([n for n in names if n.endswith(WHL)]) == 1, 'One frozen wheel only'
        assert stream_sha(z.open('CPC5/runtime/' + WHL)) == WHL_SHA
        assert stream_sha(z.open('CPC5/referencias/producto4/kernel_v27.cpp')) == KERNEL_SHA
        required = ('ejecutar.py', 'demostracion.py', 'LEEME.md', 'PROVENANCE.json',
                    'REANUDACION.json', 'revision/INDICE_EVIDENCIA.json',
                    'revision/OBSERVACIONES.jsonl', 'revision/NSM65_EVIDENCIAS.json')
        assert all(PREFIX + p in names for p in required), 'Missing new evidence or runner'
        checkpoints = [n for n in names if n.startswith(PREFIX) and n.endswith('.deetsnap')]
        assert checkpoints, 'No new checkpoints'
    return {'schema': 'CPC5.extension.container-verification.v1', 'status': 'VERIFIED',
        'path': str(candidate.resolve()), 'sha256': sha(candidate),
        'bytes': candidate.stat().st_size, 'expanded_bytes': sum(expanded.values()),
        'members': len(names), 'inherited_members_byte_exact': len(inherited),
        'new_member_count': len(names) - len(inherited), 'new_hashes_verified': len(hashes),
        'new_checkpoint_members': len(checkpoints), 'crc_verified': True,
        'compressed_bytes_by_category': dict(compressed), 'expanded_bytes_by_category': dict(expanded),
        'wheel_sha256': WHL_SHA, 'kernel_source_sha256': KERNEL_SHA,
        'verification_seconds': time.monotonic() - started}


def split_transport(path, destination):
    size = path.stat().st_size
    if size <= 20 * 1024 * 1024:
        return {'split_required': False, 'bytes': size, 'threshold_bytes': 20 * 1024 * 1024}
    names = [NAME + '.001', NAME + '.002', 'PARTES.json']
    for name in names:
        if (destination / name).exists(): raise FileExistsError('Existing transport requires reconciliation: ' + name)
    identity = sha(path); rows = []
    with path.open('rb') as source:
        for number, count in ((1, (size + 1)//2), (2, size//2)):
            target = destination / (NAME + f'.{number:03d}')
            temp = target.with_name(target.name + '.pending.' + str(os.getpid()))
            h = hashlib.sha256(); left = count
            with temp.open('xb') as out:
                while left:
                    block = source.read(min(left, BLOCK))
                    if not block: raise EOFError('ZIP changed during split')
                    out.write(block); h.update(block); left -= len(block)
            os.replace(temp, target)
            rows.append({'order': number, 'name': target.name, 'bytes': count, 'sha256': h.hexdigest()})
        assert source.read(1) == b''
    # Reconstruct actual bytes into a temporary file, then verify the whole digest.
    h = hashlib.sha256()
    with tempfile.TemporaryFile(dir=destination) as assembled:
        for row in rows:
            with (destination / row['name']).open('rb') as source: shutil.copyfileobj(source, assembled, BLOCK)
        assert assembled.tell() == size; assembled.seek(0)
        for block in iter(lambda: assembled.read(BLOCK), b''): h.update(block)
    assert h.hexdigest() == identity == sha(path)
    report = {'schema': 'CPC5.binary-parts.v1', 'zip_name': NAME, 'zip_bytes': size,
        'zip_sha256': identity, 'parts': rows, 'reconstruction_tested': True,
        'reconstruction_sha256': h.hexdigest(), 'split_threshold_bytes': 20 * 1024 * 1024}
    put(destination / 'PARTES.json', report)
    for name in ('REUNIR_CPC5.py', 'INSTRUCCIONES_PARTES.txt'):
        target = destination / name
        if target.exists():
            assert sha(target) == sha(BASE / name), 'Existing transport helper differs'
        else: shutil.copyfile(BASE / name, target)
    return report


def publish(parent, candidate, clean_report, destination):
    report = verify(candidate)
    proof = json.loads(clean_report.read_text(encoding='utf-8'))
    assert proof['status'] == 'VERIFIED' and proof['candidate_sha256'] == report['sha256']
    assert proof.get('explicit_posttrajectory_verification')
    assert proof.get('commands') and all(r['exit_code'] == 0 and r['status'] == 'COMPLETED' for r in proof['commands'])
    assert proof['plan_sha256'] == sha(EXT / 'configuraciones/clean_reproduction_plan.json')
    target = destination / NAME
    originals=protected_sources()
    assert target.resolve() == parent.resolve(), 'Only the named canonical parent may be replaced'
    assert sha(target) == PARENT_SHA, 'Concurrent archive update; candidate retained, publication refused'
    # Transport sidecars are prepared before replacement, so a split failure leaves the last ZIP valid.
    transport = split_transport(candidate, destination)
    small = [('revision/LEER_PRIMERO.md', 'CPC5_AMPLIACION_01_LEER_PRIMERO.md'),
             ('revision/LECTURA_PROVISIONAL.md', 'CPC5_AMPLIACION_01_LECTURA_PROVISIONAL.md')]
    for source, name in small:
        out = destination / name
        if out.exists(): raise FileExistsError(out)
        shutil.copyfile(EXT / source, out)
    assert sha(target) == PARENT_SHA, 'Concurrent update detected immediately before replacement'
    os.replace(candidate, target)
    assert sha(target) == report['sha256']
    assert protected_sources()==originals
    return {'published_utc': datetime.now(timezone.utc).isoformat(), 'canonical': str(target.resolve()),
            **{k: v for k, v in report.items() if k != 'path'}, 'transport': transport,
            'parent_sha256': PARENT_SHA, 'protected_sources':originals,'exact_candidate_clean_report': proof}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('build', 'verify', 'publish'))
    p.add_argument('--parent', type=Path, default=BASE.parents[1] / NAME)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--clean-report', type=Path)
    p.add_argument('--destination', type=Path)
    args = p.parse_args()
    if args.action == 'build': result = build(args.parent.resolve(), args.candidate.resolve())
    elif args.action == 'verify': result = verify(args.candidate.resolve())
    else: result = publish(args.parent.resolve(), args.candidate.resolve(), args.clean_report.resolve(), args.destination.resolve())
    put(args.report, result); print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
