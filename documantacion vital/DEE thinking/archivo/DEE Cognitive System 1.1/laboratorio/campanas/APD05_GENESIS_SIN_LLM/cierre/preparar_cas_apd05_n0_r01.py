"""CAS esencial APD05 de fuentes cerradas explícitas, sin elegir resultados.

Reutiliza la materialización y el ejecutor archivado APD04/APD05. La selección
contiene files(path,bytes,sha256) y jobs relativos; no lee históricos implícitos.
No Native, Word, Full, reserva ni aprobación científica al construir un CAS.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import zlib

HERE = Path(__file__).resolve().parent
DENIED = ('.whl', '.pyd', '.dll', '.exe', '.zip', '.sqlite', '.sqlite3', '.db',
          '.deetsnap', '.deetsnap.gz', '.npy', '.npz', '.pyc')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(base, name):
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Only portable POSIX relative source paths are admitted')
    part = PurePosixPath(name)
    if part.is_absolute() or not part.parts or any(x in ('.', '..') for x in part.parts):
        raise ValueError('Unsafe source or package path')
    target = (base / name).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError('Path escapes the explicit source root')
    return target


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(strict=True), args.out.resolve()
    selection_bytes = args.selection.read_bytes()
    selection = json.loads(selection_bytes)
    if selection.get('schema') != 'APD05.CAS.explicit_closed_sources.N0.R01':
        raise ValueError('Explicit APD05 CAS source selection required')
    if not out.is_relative_to(HERE) or out.exists() or args.report.exists():
        raise ValueError('Choose a fresh CAS below this LAB/cierre and a new report')
    files, jobs = selection['files'], selection['jobs']
    if not files or not jobs:
        raise ValueError('No empty evidence or recalculation success')
    if len({x['path'] for x in files}) != len(files):
        raise ValueError('Duplicate logical source paths')
    out.mkdir(parents=True, exist_ok=False)
    unique, sources, original_ids = {}, [], {}
    for row in files:
        source = safe(root, row['path'])
        if source.is_symlink() or source.name.lower().endswith(DENIED) or '__pycache__' in source.parts:
            raise ValueError('Engine, checkpoint, archive or DB cannot be disguised as an analysis object')
        before = source.stat()
        data = source.read_bytes()
        after = source.stat()
        sha = digest(data)
        if data.startswith(b'SQLite format 3\x00'):
            raise ValueError('Disguised SQLite input rejected')
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('A source changed during export')
        if row['bytes'] != len(data) or row['sha256'] != sha:
            raise ValueError('Source identity changed after selection: ' + row['path'])
        name = 'OBJETOS/' + sha[:2] + '/' + sha[2:] + '.bin'
        if sha not in unique:
            target = safe(out, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
            unique[sha] = {'object': name, 'bytes': len(data), 'sha256': sha}
        sources.append({'source_original': row['path'], 'object': name,
                        'bytes': len(data), 'sha256': sha,
                        'component': row.get('component', 'EXPLICIT_CLOSED_PRIMARY')})
        original_ids[row['path']] = row
    closed_jobs = []
    for job in jobs:
        if job.get('base', '.') != '.' or job.get('comparison') != 'bytes':
            raise ValueError('CAS jobs require relative root and exact archived byte comparison')
        if job['script'] not in original_ids or job['expected'] not in original_ids:
            raise ValueError('A job source/reference is not included in the explicit file selection')
        for name in (job['script'], job['expected']):
            safe(root, name)
        closed_jobs.append({**job, 'base': '.',
                            'script_sha256': original_ids[job['script']]['sha256'],
                            'expected_sha256': original_ids[job['expected']]['sha256']})
    dump(out / 'RUTAS_Y_HASHES.json', {
        'schema': 'APD05.exact_content_addressed_evidence.N0.R01',
        'status': 'EXPLICIT_EXTRACTION_NOT_SCIENTIFIC_APPROVAL',
        'selection_locator': args.selection.resolve().relative_to(root).as_posix(),
        'selection_sha256': digest(selection_bytes), 'sources': sources,
        'source_count': len(sources), 'unique_object_count': len(unique),
        'omitted_selected_source_paths': [], 'new_native_ticks': 0})
    dump(out / 'PLAN_GLOBAL_CAS.json', {
        'schema': 'APD05.CAS.selected_archived_recalculations.N0.R01', 'jobs': closed_jobs,
        'scope': 'Archived byte-exact recalculation, not native replay or Full/GUI execution.'})
    for source_name, destination in (
        ('materializar_cas_analisis_apd05_n0_r01.py', 'RESTAURAR_Y_RECALCULAR_CAS.py'),
        ('recalcular_analisis_apd05_n0_r01.py', 'recalcular_todo_CONGELADO.py')):
        shutil.copyfile(HERE / source_name, out / destination)
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size,
                'sha256': digest(p.read_bytes())} for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out / 'MANIFIESTO_CAS.json', {'schema': 'APD05.CAS.members.N0.R01', 'members': members,
         'source_count': len(sources), 'unique_objects': len(unique), 'no_selected_source_bytes_omitted': True})
    estimate = 22
    for path in (p for p in out.rglob('*') if p.is_file()):
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        raw = path.read_bytes()
        estimate += len(compressor.compress(raw) + compressor.flush())
        estimate += 98 + 2 * (len(path.relative_to(out).as_posix().encode('utf8')) + 20)
    report = {'schema': 'APD05.exact_CAS_size.N0.R01',
              'manifest_sha256': digest((out / 'MANIFIESTO_CAS.json').read_bytes()),
              'source_paths': len(sources), 'unique_objects': len(unique),
              'source_bytes': sum(x['bytes'] for x in sources),
              'unique_source_bytes': sum(x['bytes'] for x in unique.values()),
              'estimated_compressed_bytes_with_headers': estimate,
              'new_native_ticks': 0, 'ZIPs_created': 0, 'source_modified': False,
              'scope': 'CAS extraction only; size is estimate until the exact final ZIP is sealed.'}
    dump(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
