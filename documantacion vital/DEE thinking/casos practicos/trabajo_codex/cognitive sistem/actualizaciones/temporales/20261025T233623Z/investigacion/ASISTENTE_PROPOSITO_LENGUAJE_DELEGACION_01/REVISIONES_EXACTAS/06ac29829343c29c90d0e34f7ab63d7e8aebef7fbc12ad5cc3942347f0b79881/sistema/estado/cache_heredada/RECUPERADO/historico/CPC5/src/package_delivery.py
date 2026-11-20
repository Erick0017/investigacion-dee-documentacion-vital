"""Seal, validate and atomically publish CPC5. Never runs scientific cases.

MANIFEST lists payload except itself and HASHES. HASHES covers payload and
MANIFEST, except HASHES itself. ZIP identity is external, avoiding cycles.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip'
WHL = 'dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
WHL_SHA = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA = '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
EXCLUDED_DIRS = {'.venv', '__pycache__', '.git', '.pytest_cache', 'documantacion vital',
                 'clean_reproduction', '_clean_extract', '_repro_env'}
EXCLUDED_NAMES = {'MANIFEST.json', 'HASHES.sha256'}
PROTECTED = {
    'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip':
        '4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
    'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip':
        '1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def put(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.pending.' + str(os.getpid()))
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)


def selected(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for name in sorted(files):
            p = Path(base) / name
            rel = p.relative_to(root)
            if p.is_symlink():
                raise ValueError('Symlink not permitted: ' + str(rel))
            if len(rel.parts) == 1 and name in EXCLUDED_NAMES:
                continue
            if name.endswith(('.pyc', '.pyo', '.tmp', '.pending')) or '.pending.' in name:
                continue
            if name.endswith(('.zip', '.zip.001', '.zip.002')):
                raise ValueError('Nested historical/generated ZIP is not permitted: ' + str(rel))
            yield p, rel.as_posix()


def protected_sources(root):
    rows = []
    for name, expected in PROTECTED.items():
        p = root.parents[1] / name
        if not p.is_file():
            rows.append({'name': name, 'available': False, 'expected_sha256': expected})
            continue
        actual = sha(p)
        if actual != expected:
            raise ValueError('Protected source differs; do not overwrite: ' + str(p))
        rows.append({'name': name, 'available': True, 'bytes': p.stat().st_size,
                     'sha256': actual, 'unchanged': True})
    return rows


def inventory(root):
    rows = []
    category = Counter()
    for p, rel in selected(root):
        size = p.stat().st_size
        rows.append({'path': rel, 'bytes': size, 'sha256': sha(p)})
        category[rel.split('/')[0]] += size
    return {'schema': 'CPC5.payload-manifest.v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
            'root': 'CPC5/', 'files': rows, 'payload_bytes': sum(r['bytes'] for r in rows),
            'category_bytes': dict(category),
            'excluded_directories': sorted(EXCLUDED_DIRS),
            'self_exclusions': ['MANIFEST.json', 'HASHES.sha256'],
            'integer_preservation': 'RAW/clocks remain exact strings or binary uint64 in payload; no recoding',
            'original_sources': protected_sources(root)}


def check_runtime(root):
    p = root / 'runtime' / WHL
    if sha(p) != WHL_SHA:
        raise ValueError('Incorrect frozen wheel')
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        pyd = [x for x in z.namelist() if x.endswith('.pyd')]
        assert len(pyd) == 1
        assert hashlib.sha256(z.read(pyd[0])).hexdigest() == PYD_SHA
    k = root / 'referencias/producto4/kernel_v27.cpp'
    assert sha(k) == KERNEL_SHA
    return {'wheel_sha256': WHL_SHA, 'pyd_sha256': PYD_SHA, 'kernel_source_sha256': KERNEL_SHA}


def build(root, candidate):
    if not candidate.name.endswith('.candidate.zip'):
        raise ValueError('Build target must end .candidate.zip; publication is a separate command')
    started = time.monotonic()
    engine = check_runtime(root)
    manifest = inventory(root)
    put(root / 'MANIFEST.json', manifest)
    lines = [f"{r['sha256']}  {r['path']}" for r in manifest['files']]
    lines.append(sha(root / 'MANIFEST.json') + '  MANIFEST.json')
    (root / 'HASHES.sha256').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    paths = [(root / r['path'], r['path']) for r in manifest['files']]
    paths += [(root / x, x) for x in ('MANIFEST.json', 'HASHES.sha256')]
    candidate.parent.mkdir(parents=True, exist_ok=True)
    if candidate.exists():
        raise FileExistsError(candidate)
    with zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9,
                         allowZip64=True, strict_timestamps=False) as z:
        for p, rel in paths:
            z.write(p, 'CPC5/' + rel)
    result = verify(candidate)
    result.update({'engine': engine, 'build_seconds': time.monotonic() - started})
    return result


def verify(candidate):
    started = time.monotonic()
    with zipfile.ZipFile(candidate) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), 'Duplicate ZIP members'
        for n in names:
            p = PurePosixPath(n)
            assert n.startswith('CPC5/') and '..' not in p.parts and not p.is_absolute()
            assert not any(x in EXCLUDED_DIRS for x in p.parts)
        assert z.testzip() is None, 'ZIP CRC error'
        manifest = json.loads(z.read('CPC5/MANIFEST.json'))
        hashes = {}
        for line in z.read('CPC5/HASHES.sha256').decode('utf-8').splitlines():
            h, rel = line.split('  ', 1)
            assert rel not in hashes
            hashes[rel] = h
        payload = {r['path']: r for r in manifest['files']}
        assert set(hashes) == set(payload) | {'MANIFEST.json'}
        assert set(names) == {'CPC5/' + n for n in hashes} | {'CPC5/HASHES.sha256'}
        category = Counter()
        for rel, expected in hashes.items():
            h = hashlib.sha256()
            with z.open('CPC5/' + rel) as source:
                for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
                    h.update(block)
            assert h.hexdigest() == expected, 'Hash mismatch: ' + rel
            info = z.getinfo('CPC5/' + rel)
            category[rel.split('/')[0]] += info.compress_size
            if rel in payload:
                assert payload[rel]['sha256'] == expected and payload[rel]['bytes'] == info.file_size
        required = ['ejecutar.py', 'demostracion.py', 'LEEME.md', 'revision/LEER_PRIMERO.md',
                    'revision/LECTURA_PROVISIONAL.md', 'revision/OBSERVACIONES.jsonl',
                    'revision/NSM65_EVIDENCIAS.json', 'runtime/' + WHL]
        assert all('CPC5/' + name in names for name in required), 'Missing runner/review/runtime'
        checkpoints = [n for n in names if n.endswith('.deetsnap')]
        assert checkpoints, 'No checkpoints'
        expanded = sum(x.file_size for x in z.infolist())
    return {'schema': 'CPC5.container-verification.v1', 'path': str(candidate.resolve()),
            'bytes': candidate.stat().st_size, 'expanded_bytes': expanded, 'members': len(names),
            'checkpoint_members': len(checkpoints), 'sha256': sha(candidate),
            'crc_verified': True, 'manifest_member_hashes_verified': len(hashes),
            'compressed_bytes_by_category': dict(category),
            'verification_seconds': time.monotonic() - started}


def split_transport(path, destination):
    """Exactly two sequential binary parts, with actual streaming reconstruction."""
    identity = sha(path)
    size = path.stat().st_size
    if size <= 20 * 1024 * 1024:
        return {'split_required': False, 'bytes': size, 'threshold_bytes': 20 * 1024 * 1024}
    destination.mkdir(parents=True, exist_ok=True)
    for name in ('PARTES.json', NAME + '.001', NAME + '.002'):
        if (destination / name).exists():
            raise FileExistsError('Transport artifact already exists; preserve and reconcile: ' + str(destination / name))
    rows = []
    with path.open('rb') as source:
        for number, count in ((1, (size + 1)//2), (2, size//2)):
            target = destination / (NAME + f'.{number:03d}')
            temporary = target.with_name(target.name + '.pending.' + str(os.getpid()))
            if target.exists() or temporary.exists():
                raise FileExistsError(target)
            h = hashlib.sha256()
            with temporary.open('xb') as out:
                left = count
                while left:
                    block = source.read(min(left, 4 * 1024 * 1024))
                    if not block:
                        raise EOFError('Source changed during split')
                    out.write(block); h.update(block); left -= len(block)
            os.replace(temporary, target)
            rows.append({'order': number, 'name': target.name, 'bytes': count, 'sha256': h.hexdigest()})
        assert source.read(1) == b''
    reconstructed = hashlib.sha256()
    with tempfile.TemporaryFile(dir=destination) as reconstructed_file:
        for item in rows:
            with (destination / item['name']).open('rb') as source:
                for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
                    reconstructed_file.write(block)
        assert reconstructed_file.tell() == size
        reconstructed_file.seek(0)
        for block in iter(lambda: reconstructed_file.read(4 * 1024 * 1024), b''):
            reconstructed.update(block)
    assert reconstructed.hexdigest() == identity == sha(path)
    result = {'schema': 'CPC5.binary-parts.v1', 'zip_name': NAME, 'zip_bytes': size,
              'zip_sha256': identity, 'parts': rows, 'reconstruction_tested': True,
              'reconstruction_sha256': reconstructed.hexdigest(), 'split_threshold_bytes': 20 * 1024 * 1024}
    put(destination / 'PARTES.json', result)
    return result


def publish(root, candidate, destination, verification_report):
    report = verify(candidate)
    assert verification_report.is_file(), 'Clean independent reproduction report required'
    proof = json.loads(verification_report.read_text(encoding='utf-8'))
    assert proof.get('status') == 'VERIFIED' and proof.get('candidate_sha256') == report['sha256']
    assert proof.get('explicit_posttrajectory_verification'), 'Missing actual state/trajectory checks'
    assert proof.get('commands') and all(x['exit_code'] == 0 and x['status'] == 'COMPLETED' for x in proof['commands'])
    assert proof['plan_sha256'] == sha(root / 'configuraciones/clean_reproduction_plan.json')
    originals = protected_sources(root)
    target = destination / NAME
    if target.exists():
        raise FileExistsError('A CPC5 delivery already exists; preserve and reconcile, do not overwrite blindly: ' + str(target))
    smalls = ['CPC5_LEER_PRIMERO.md', 'CPC5_LECTURA_PROVISIONAL.md']
    transport_names = ['PARTES.json', NAME+'.001', NAME+'.002', 'REUNIR_CPC5.py', 'INSTRUCCIONES_PARTES.txt']
    for name in smalls + (transport_names if report['bytes'] > 20 * 1024 * 1024 else []):
        if (destination / name).exists():
            raise FileExistsError('Existing sidecar is protected: ' + str(destination / name))
    # Windows rename is atomic and refuses an independently created target;
    # do not use replace here because CPC5 has no previous authorized release.
    os.rename(candidate, target)
    assert sha(target) == report['sha256']
    transport = split_transport(target, destination)
    for name in ('REUNIR_CPC5.py', 'INSTRUCCIONES_PARTES.txt'):
        if transport.get('split_required') is not False:
            sidecar = destination / name
            if sidecar.exists():
                raise FileExistsError(sidecar)
            shutil.copyfile(root / name, sidecar)
    for name in ('LEER_PRIMERO.md', 'LECTURA_PROVISIONAL.md'):
        target_small = destination / ('CPC5_' + name)
        if target_small.exists():
            raise FileExistsError(target_small)
        shutil.copyfile(root / 'revision' / name, target_small)
    assert protected_sources(root) == originals
    return {'published_utc': datetime.now(timezone.utc).isoformat(), 'canonical': str(target.resolve()),
            **{k: v for k, v in report.items() if k != 'path'}, 'transport': transport,
            'protected_sources': originals, 'clean_reproduction': proof,
            'clean_reproduction_report_source': str(verification_report)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['inventory', 'build', 'verify', 'publish'])
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--candidate', type=Path)
    p.add_argument('--destination', type=Path)
    p.add_argument('--clean-report', type=Path)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    root = args.root.resolve()
    if args.action == 'inventory': result = inventory(root)
    elif args.action == 'build': result = build(root, args.candidate.resolve())
    elif args.action == 'verify': result = verify(args.candidate.resolve())
    else:
        result = publish(root, args.candidate.resolve(), args.destination.resolve(), args.clean_report.resolve())
    if args.report: put(args.report, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
