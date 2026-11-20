"""Explicit, non-mutating CPC9 candidate selection and sealed ZIP construction.

No scientific source is edited. MANIFEST/HASHES and selection are virtual ZIP
members. A separately supplied seal must match the current byte selection.
Atomic candidate publication requires hardlink support (tested on NTFS).
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import stat
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ('src', 'app', 'base_validada', 'runtime', 'genealogia',
               'configuraciones', 'revision', 'resultados', 'checkpoints', 'jobs')
FRONT_SUBDIRECTORIES = ('src', 'resultados', 'revision', 'configuraciones', 'checkpoints')
TOOLS = ('preparar_entorno.py', 'recalcular_cpc9.py', 'indexar_evidencia.py',
         'auditar_descubrimientos.py', 'check_instrument.py', 'pack_cpc9.py',
         'verify_cpc9_clean.py', 'dividir_verificar_entrega.py', 'reconciliar_e1.py',
         'redactar_matriz_nsm.py', 'auditar_ocupacion_y_restauracion.py',
         'investigar_crecimiento_ocupacion.py', 'auditar_memorias_tardias.py',
         'auditar_composicion_e1.py', 'sintesis_cpc9.py', 'supervisor.py')
FRONT_ROOT_PY = ('front_semantics',)
FRONT_AUDITORS = ('front_semantics/analyze_front.py', 'front_semantics/adjudicar_front.py',
                  'front_semantics/build_nsm_plan.py')
FRONT_REFERENCES = ('front_semantics/referencias/NSM65_CATALOGO_4_5.json',
                    'front_semantics/referencias/CPC8_NSM65_ESTADOS_HISTORICOS.json')
VIRTUAL = {'MANIFEST.json', 'HASHES.sha256', 'PACK_SELECTION.json'}
ROOT_SUFFIXES = {'.py', '.ps1', '.json', '.md', '.csv', '.txt', '.sha256'}
OMITTED_NAMES = {'__pycache__', '.git', '.pytest_cache', '.mypy_cache', '.ruff_cache',
                 'node_modules', '.venv', 'venv', 'notes', 'core'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')


def fingerprint(rows):
    h = hashlib.sha256()
    for row in rows:
        h.update((row['path'] + '\0' + str(row['bytes']) + '\0' + row['sha256'] + '\n').encode('utf-8'))
    return h.hexdigest()


def choose(root):
    root = Path(root).resolve(strict=True)
    selected = {}
    excluded = []

    def add(path):
        rel = path.relative_to(root).as_posix()
        mode = path.lstat()
        if stat.S_ISLNK(mode.st_mode) or getattr(mode, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Reparse point/symlink is not admitted: ' + rel)
        path.resolve(strict=True).relative_to(root)
        if not path.is_file():
            return
        lower = path.name.lower()
        if lower.endswith(('.pyc', '.pyo', '.zip', '.zip.001', '.zip.002')) or '.zip.' in lower:
            excluded.append({'path': rel, 'reason': 'cache or separate archive, never nested'})
            return
        if path.suffix.lower() in {'.whl', '.pyd'} and rel != 'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl':
            raise ValueError('Unexpected duplicate/external binary; review before packaging: ' + rel)
        selected[rel] = {'path': rel, 'bytes': mode.st_size, 'sha256': digest(path)}

    def walk(folder):
        if not folder.exists():
            return
        for current, dirs, files in os.walk(folder, followlinks=False):
            retained = []
            for name in sorted(dirs):
                q = Path(current) / name
                if name in OMITTED_NAMES or name.lower().startswith('_cpc9_runtime'):
                    excluded.append({'path': q.relative_to(root).as_posix() + '/', 'reason': 'cache, historical package, notes or environment; subtree not traversed'})
                elif q.is_symlink() or getattr(q.lstat(), 'st_file_attributes', 0) & 0x400:
                    raise ValueError('Reparse directory not admitted: ' + str(q))
                else:
                    retained.append(name)
            dirs[:] = retained
            for name in sorted(files):
                add(Path(current) / name)

    for name in DIRECTORIES:
        if name != 'jobs':
            walk(root / name)
            continue
        if not (root / 'jobs').exists():
            continue
        for folder in sorted((root / 'jobs').iterdir()):
            if not folder.is_dir():
                add(folder)
            elif folder.name.casefold().startswith('core_clean_'):
                excluded.append({'path': folder.relative_to(root).as_posix() + '/',
                    'reason': 'Core clean verification is a separate external receipt; possibly mutable and never a CPC9 operational dependency.'})
            elif folder.name.casefold().startswith('core_'):
                command = folder / 'COMMAND.json'
                if command.is_file():
                    add(command)
                    error = folder / 'stderr.log'
                    if error.is_file() and error.stat().st_size:
                        add(error)
                excluded.append({'path': folder.relative_to(root).as_posix() + '/(other files)',
                    'reason': 'Scientific Core adverse evidence/source is preserved in the standalone Core package. CPC9 keeps closed COMMAND cost metadata and nonempty stderr only.'})
            else:
                walk(folder)
    for front in sorted(root.glob('front_*')):
        if front.is_dir():
            for sub in FRONT_SUBDIRECTORIES:
                walk(front / sub)
    for name in FRONT_ROOT_PY:
        for path in sorted((root / name).glob('*.py')):
            add(path)
    for name in TOOLS:
        path = root / 'tools' / name
        if not path.is_file():
            raise FileNotFoundError('Required operational tool missing: ' + str(path))
        add(path)
    for name in FRONT_AUDITORS + FRONT_REFERENCES:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError('Required reference auditor missing: ' + name)
        add(path)
    for path in sorted(root.iterdir()):
        if path.is_file() and path.suffix.lower() in ROOT_SUFFIXES and path.name not in VIRTUAL:
            add(path)
    rows = [selected[k] for k in sorted(selected)]
    by_hash = defaultdict(list)
    for row in rows:
        by_hash[(row['sha256'], row['bytes'])].append(row['path'])
    duplicates = [{'sha256': key[0], 'bytes_each': key[1], 'paths': paths}
                  for key, paths in sorted(by_hash.items()) if len(paths) > 1]
    return {'schema': 'CPC9.pack.selection.v1', 'archive_prefix': 'CPC9/',
            'selection_sha256': fingerprint(rows), 'files': rows,
            'expanded_payload_bytes': sum(x['bytes'] for x in rows),
            'selection_rules': {'directories': list(DIRECTORIES), 'front_subdirectories': list(FRONT_SUBDIRECTORIES),
                                'tools': list(TOOLS), 'root_suffixes': sorted(ROOT_SUFFIXES),
                                'front_reference_auditors': list(FRONT_AUDITORS),
                                'front_root_python_sources': list(FRONT_ROOT_PY),
                                'front_reference_inputs': list(FRONT_REFERENCES),
                                'adjudication_policy': 'Auditors are preserved for review; packaging never executes manual adjudications or changes evidence states.',
                                'core_job_policy': 'Exclude all core_CLEAN_* external proof directories; other core_* retain only closed COMMAND.json and nonempty stderr. Core scientific evidence belongs to the standalone Core archive.',
                                'historical_supervisor_contract': 'tools/supervisor.py is preserved only as the original campaign instrument, with its immutable budget. Future app/clean verification does not import it or restart its deadline; src/lote_* remain original-campaign orchestration, as documented in LEEME.',
                                'not_traversed': ['notes/', 'core/', 'venvs/caches'],
                                'deduplication': 'No path substitutions; identical hashes are reported and bytes preserved to avoid breaking scientific dependencies.'},
            'duplicate_groups': duplicates, 'excluded_encountered': excluded,
            'limitations': ['Historical metadata may preserve its original documentary paths. Operational imports and clean proof must not depend on those paths.',
                            'Construction-only tools, historical archive bytes, notes and virtual environments are not operational CPC9 payload.']}


def zip_entry(archive, name, data=None, path=None):
    info = zipfile.ZipInfo('CPC9/' + name, (2026, 10, 19, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info._compresslevel = 9
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    if path is not None:
        with path.open('rb') as src, archive.open(info, 'w', force_zip64=True) as dst:
            for block in iter(lambda: src.read(1024 * 1024), b''):
                dst.write(block)
    else:
        archive.writestr(info, data)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['plan', 'build'])
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--plan', required=True, type=Path)
    p.add_argument('--seal', type=Path)
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    root = a.root.resolve(strict=True)
    if a.plan.resolve().is_relative_to(root) or (a.seal is not None and a.seal.resolve().is_relative_to(root)):
        raise ValueError('Selection plan and candidate seal must be outside source tree, to avoid self-selection')
    current = choose(root)
    if a.operation == 'plan':
        if a.plan.exists():
            raise FileExistsError('Protect existing selection; use another plan filename')
        a.plan.parent.mkdir(parents=True, exist_ok=True)
        with a.plan.open('xb') as f:
            f.write(encoded(current))
        print(json.dumps({'selection_sha256': current['selection_sha256'], 'files': len(current['files']), 'bytes': current['expanded_payload_bytes']}))
        return
    if a.seal is None or a.out is None:
        p.error('build requires --seal and --out')
    expected = json.loads(a.plan.read_text(encoding='utf-8'))
    seal = json.loads(a.seal.read_text(encoding='utf-8'))
    if seal.get('status') != 'SEALED' or seal.get('selection_sha256') != current['selection_sha256']:
        raise ValueError('Seal missing, unsealed or does not match current sources')
    if expected['selection_sha256'] != current['selection_sha256'] or expected['files'] != current['files']:
        raise ValueError('Payload changed after selection; preserve this plan and create another candidate')
    out = a.out.resolve()
    if out.is_relative_to(root):
        raise ValueError('Candidate archive must be outside source tree')
    if out.exists():
        raise FileExistsError('Candidate exists; never overwrite a valid archive')
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_name(out.name + '.building.' + str(os.getpid()))
    if temporary.exists():
        raise FileExistsError(str(temporary))
    started = time.monotonic()
    selection_data = encoded(current)
    manifest_rows = current['files'] + [{'path': 'PACK_SELECTION.json', 'bytes': len(selection_data), 'sha256': hashlib.sha256(selection_data).hexdigest()}]
    manifest = {'schema': 'CPC9.manifest.v1', 'algorithm': 'SHA-256',
                'excluded_from_own_manifest': ['MANIFEST.json', 'HASHES.sha256'],
                'files': manifest_rows, 'expanded_bytes_without_manifest_hashes': sum(x['bytes'] for x in manifest_rows),
                'source_selection_sha256': current['selection_sha256']}
    manifest_data = encoded(manifest)
    hash_rows = manifest_rows + [{'path': 'MANIFEST.json', 'sha256': hashlib.sha256(manifest_data).hexdigest()}]
    hashes = ''.join(x['sha256'] + '  ' + x['path'] + '\n' for x in sorted(hash_rows, key=lambda x: x['path'])).encode('utf-8')
    with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
        for row in current['files']:
            zip_entry(archive, row['path'], path=root / row['path'])
        zip_entry(archive, 'PACK_SELECTION.json', selection_data)
        zip_entry(archive, 'MANIFEST.json', manifest_data)
        zip_entry(archive, 'HASHES.sha256', hashes)
    if choose(root)['selection_sha256'] != current['selection_sha256']:
        raise ValueError('Source changed during build; unvalidated .building candidate retained')
    with zipfile.ZipFile(temporary) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError('CRC failure: ' + bad)
        expanded = sum(x.file_size for x in archive.infolist())
        count = len(archive.infolist())
    # Atomic fail-if-exists; never overwrite a concurrent valid candidate.
    os.link(temporary, out)
    temporary.unlink()
    receipt = {'schema': 'CPC9.pack.receipt.v1', 'zip_name': out.name, 'zip_sha256': digest(out),
               'compressed_bytes': out.stat().st_size, 'expanded_bytes': expanded, 'members': count,
               'selection_sha256': current['selection_sha256'], 'crc_all_members': True,
               'status': 'BUILT_NOT_YET_CLEAN_VERIFIED', 'elapsed_seconds': time.monotonic() - started,
               'publication_contract': 'Atomic fail-if-exists hardlink in same directory; requires hardlink-capable filesystem, NTFS tested.',
               'seal': seal, 'unchanged_sources_after_build': True}
    receipt_path = out.with_name(out.name + '.BUILD.json')
    if receipt_path.exists():
        raise FileExistsError(str(receipt_path))
    with receipt_path.open('xb') as f:
        f.write(encoded(receipt))
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
