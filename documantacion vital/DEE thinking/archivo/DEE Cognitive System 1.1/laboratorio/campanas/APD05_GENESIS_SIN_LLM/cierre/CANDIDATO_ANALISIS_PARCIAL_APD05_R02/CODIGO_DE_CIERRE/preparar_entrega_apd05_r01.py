"""Ensamblado/sello APD05 explícito, reutiliza el cierre APD04.

No Native, no selección de vidas ni actualización Full/Word. Sólo una selección
cerrada y aprobada por Root permite copiar bytes; sellar requiere otro GO.
Los fallos se conservan y nunca se reemplaza un candidato o ZIP existente.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

LIMIT = 16_000_000
DENIED = ('.whl', '.pyd', '.dll', '.exe', '.zip', '.sqlite', '.sqlite3', '.db',
          '.deetsnap', '.deetsnap.gz', '.npy', '.npz', '.pyc')
RESERVED = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)), *(f'lpt{i}' for i in range(1, 10))}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def emit(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def member(name):
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Use relative POSIX member names')
    p = PurePosixPath(name)
    if p.is_absolute() or not p.parts or any(x in ('', '.', '..') for x in p.parts):
        raise ValueError('Unsafe member: ' + name)
    for part in p.parts:
        if part.endswith((' ', '.')) or part.split('.')[0].casefold() in RESERVED:
            raise ValueError('Not a portable Windows member: ' + name)
    return p.as_posix()


def safe(root, relative):
    result = (root / member(relative)).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Path escapes supplied root')
    return result


def check_analysis_file(path):
    if path.is_symlink() or path.name.casefold().endswith(DENIED) or '__pycache__' in path.parts:
        raise ValueError('Engine/archive/full checkpoint/database forbidden in analysis: ' + str(path))
    with path.open('rb') as stream:
        if stream.read(16) == b'SQLite format 3\x00':
            raise ValueError('Database disguised as evidence text')


def validate_results(value, approved):
    if value.get('schema') != 'APD05.final_analysis_selection.R01':
        raise ValueError('Wrong selection schema')
    required = ('attempts', 'claims', 'lives', 'executed_revisions', 'files', 'components', 'jobs', 'omissions')
    if any(not isinstance(value.get(k), list) for k in required):
        raise ValueError('Explicit result/source/job/omission arrays required')
    if not all(value[k] for k in ('attempts', 'claims', 'lives', 'executed_revisions', 'jobs')):
        raise ValueError('No empty scientific tables or recalculation slot')
    if approved and (value.get('status') != 'FINAL_RESULTS_APPROVED_FOR_ANALYSIS' or value.get('native_work_closed') is not True):
        raise ValueError('Root must close physical work and approve actual final results first')
    ids = [x['id'] for x in value['files'] + value['components']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate source IDs')
    known = set(ids)
    for kind in ('attempts', 'claims', 'executed_revisions'):
        for row in value[kind]:
            if not row.get('id') or not row.get('scope') or not isinstance(row.get('source_ids'), list):
                raise ValueError('Each assertion/attempt/revision needs identity, scope and source IDs')
            if row.get('status') != 'NOT_EXECUTED' and not row['source_ids']:
                raise ValueError('An executed or scientific assertion cannot cite no evidence')
            if not set(row['source_ids']) <= known:
                raise ValueError('Unresolved evidence reference in ' + row['id'])
    for row in value['files'] + value['components']:
        digest = row.get('sha256', row.get('manifest_sha256', ''))
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Every selected file/component must already have its exact closed hash')
    for row in value['omissions']:
        if not row.get('locator') or not row.get('reason') or not row.get('scientific_consequence'):
            raise ValueError('Omissions need a real locator, reason and effect on coverage')
    return value


def assemble(root, results_path, out):
    value = validate_results(read(results_path), approved=True)
    root, out = root.resolve(), out.resolve()
    closing = Path(__file__).resolve().parent
    if not out.is_relative_to(closing):
        raise ValueError('Candidate must remain under this LAB/cierre, not the live system')
    out.mkdir(parents=True, exist_ok=False)
    copied, duplicates, targets, sources = [], [], {}, []

    def copy_one(source, relative, kind, source_id, expected, compress=False):
        check_analysis_file(source)
        digest, size = sha(source), source.stat().st_size
        if digest != expected:
            raise ValueError('Source changed after selection closed: ' + str(source))
        name = member(relative)
        target = safe(out, name)
        if name.casefold() in targets:
            if targets[name.casefold()] != digest or compress:
                raise ValueError('Destination collision: ' + name)
            duplicates.append({'source_id': source_id, 'destination': name, 'sha256': digest})
            return
        targets[name.casefold()] = digest
        target.parent.mkdir(parents=True, exist_ok=True)
        if compress:
            with source.open('rb') as inp, target.open('xb') as raw:
                with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=9, mtime=0) as encoded:
                    shutil.copyfileobj(inp, encoded)
            h = hashlib.sha256()
            count = 0
            with gzip.open(target, 'rb') as inp:
                for block in iter(lambda: inp.read(1048576), b''):
                    h.update(block)
                    count += len(block)
            if h.hexdigest() != digest or count != size:
                raise ValueError('Gzip did not preserve original source bytes')
        else:
            shutil.copyfile(source, target)
            if sha(target) != digest:
                raise ValueError('Copied file hash mismatch')
        if sha(source) != digest or source.stat().st_size != size:
            raise ValueError('Live source changed while exporting; never seal this candidate')
        sources.append((source, digest))
        copied.append({'source_id': source_id, 'source': source.relative_to(root).as_posix(),
                       'file': name, 'source_bytes': size, 'source_sha256': digest,
                       'exported_bytes': target.stat().st_size, 'exported_sha256': sha(target),
                       'lossless_gzip': compress, 'kind': kind})

    for row in value['files']:
        copy_one(safe(root, row['source']), row['destination'], row['kind'], row['id'], row['sha256'],
                 row.get('compress_gzip', False))
    component_checks = []
    for component in value['components']:
        folder = safe(root, component['source'])
        manifest_path = safe(folder, component.get('manifest', 'MANIFIESTO.json'))
        if sha(manifest_path) != component['manifest_sha256']:
            raise ValueError('Closed component manifest differs: ' + component['id'])
        data = read(manifest_path)
        rows = data.get('members', data.get('files'))
        if not isinstance(rows, list) or not rows:
            raise ValueError('A closed component needs a nonempty actual member list')
        prefix = member(component['destination'])
        for row in rows:
            name = row.get('file', row.get('path'))
            source = safe(folder, name)
            if source.stat().st_size != row['bytes']:
                raise ValueError('Component member byte count differs')
            copy_one(source, prefix + '/' + member(name), 'closed_component', component['id'], row['sha256'])
        copy_one(manifest_path, prefix + '/' + member(component.get('manifest', 'MANIFIESTO.json')),
                 'closed_component_manifest', component['id'], component['manifest_sha256'])
        component_checks.append({'id': component['id'], 'members': len(rows),
                                 'manifest_sha256': component['manifest_sha256']})
    copy_one(results_path.resolve(), 'RESULTADOS_FINAL.json', 'root_approved_closed_result_selection',
             'ROOT_SELECTION', sha(results_path))
    for path in (Path(__file__).resolve(), closing / 'recalcular_analisis_apd05_n0_r01.py'):
        copy_one(path, 'CODIGO_DE_CIERRE/' + path.name, 'N0_analysis_instrument_not_an_ente', path.name, sha(path))
    portable = closing / 'recalcular_analisis_apd05_n0_r01.py'
    copy_one(portable, 'RECALCULO/recalcular_todo.py', 'N0_portable_entrypoint', 'N0_RECALC', sha(portable))
    jobs = []
    for row in value['jobs']:
        base = out if row.get('base', '.') == '.' else safe(out, row['base'])
        script, expected = safe(base, row['script']), safe(base, row['expected'])
        jobs.append({**row, 'script_sha256': sha(script), 'expected_sha256': sha(expected)})
    emit(out / 'RECALCULO/PLAN_GLOBAL.json', {'schema': 'APD05.archived_recalculation_plan.R01', 'jobs': jobs,
                                           'new_native_ticks': 0, 'full_status': value.get('full_status', 'NOT_ASSERTED_BY_ANALYSIS')})
    emit(out / 'INDICE_FUENTES_Y_OMISIONES.json', {'schema': 'APD05.essential_export.source_index.R01',
         'copied': copied, 'exact_duplicate_destinations_reused': duplicates, 'components': component_checks,
         'omissions': value['omissions'], 'operational_backup': False,
         'scope': 'Selected primary bytes/closed code revisions; all attempts retained, not the complete historical corpus or continuable snapshots.'})
    emit(out / 'ENSAYOS_Y_CONTROLES.json', {'attempts': value['attempts'], 'claims': value['claims'],
                                          'lives': value['lives'], 'executed_revisions': value['executed_revisions']})
    (out / 'LEER_PRIMERO.md').write_text(
        '# APD05 Génesis sin LLM — análisis esencial\n\n'
        'Entrega de cierre parcial de resultados ya producidos: no es un nuevo Full operativo. '
        'En este corte no se completaron la actualización Word 1.19, la actualización y prueba exacta '
        'del Full APD05 ni una promoción global. El bloqueo externo y el exceso del plazo quedan '
        'declarados en CIERRE_POR_BLOQUEO_DEL_NAVEGADOR.json; no se cuentan como actividad Native.\n\n'
        'Este paquete contiene evidencia cerrada positiva y negativa, revisiones ejecutadas y recálculo archivado. '
        'No incluye motor ni mundos completos y no permite continuar las vidas por sí solo.\n\n'
        'Desde una extracción nueva: `python -I -B RECALCULO/recalcular_todo.py --out RUTA_NUEVA_FUERA_DEL_PAQUETE`. '
        'El recálculo no ejecuta Native, no aprende y no prueba el Full. Cada job declara comparación por bytes '
        'o por valores JSON sin confundir ambas. Las omisiones/localizadores están en el índice.\n', encoding='utf8')
    if any(sha(path) != digest for path, digest in sources):
        raise ValueError('An original source changed before completion')
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
               for p in sorted(out.rglob('*')) if p.is_file()]
    emit(out / 'MANIFIESTO_HASHES.json', {'schema': 'APD05.analysis_members.R01', 'members': members,
                                        'excludes_own_hash': True, 'contains_no_own_archive_hash': True})
    print(json.dumps({'candidate': str(out), 'members_including_manifest': len(members) + 1,
                      'expanded_bytes_excluding_manifest': sum(r['bytes'] for r in members),
                      'status': 'UNSEALED_NO_ZIP', 'new_native_ticks': 0}, ensure_ascii=False))


def seal(candidate, delivery, proof):
    candidate, delivery, proof = candidate.resolve(), delivery.resolve(), proof.resolve()
    results = validate_results(read(candidate / 'RESULTADOS_FINAL.json'), approved=True)
    if candidate.is_relative_to(proof) or proof.is_relative_to(candidate):
        raise ValueError('Proof must be outside the candidate')
    proof.mkdir(parents=True, exist_ok=False)
    delivery.mkdir(parents=True, exist_ok=True)
    name = member(results['zip_name'])
    if '/' in name or not name.casefold().endswith('.zip'):
        raise ValueError('Explicit final ZIP basename required')
    final = delivery / name
    staged = proof / ('CANDIDATO_' + name)
    if final.exists():
        raise FileExistsError('Never replace a previously published analysis ZIP')
    manifest = read(candidate / 'MANIFIESTO_HASHES.json')
    expected = {r['file']: r for r in manifest['members']}
    expected['MANIFIESTO_HASHES.json'] = {'file': 'MANIFIESTO_HASHES.json',
                                        'bytes': (candidate / 'MANIFIESTO_HASHES.json').stat().st_size,
                                        'sha256': sha(candidate / 'MANIFIESTO_HASHES.json')}
    actual = {p.relative_to(candidate).as_posix() for p in candidate.rglob('*') if p.is_file()}
    if actual != set(expected):
        raise ValueError('Unexpected/unmanifested/missing candidate members')
    folded = set()
    for filename, row in expected.items():
        member(filename)
        if filename.casefold() in folded:
            raise ValueError('Case-insensitive duplicate member')
        folded.add(filename.casefold())
        path = safe(candidate, filename)
        check_analysis_file(path)
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Candidate changed after assembly')
    with zipfile.ZipFile(staged, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=False) as archive:
        for filename in sorted(expected):
            info = zipfile.ZipInfo(filename, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with safe(candidate, filename).open('rb') as inp, archive.open(info, 'w') as out:
                shutil.copyfileobj(inp, out)
    if staged.stat().st_size > LIMIT:
        raise ValueError('Analysis exceeds 16,000,000 bytes; preserve candidate, revise explicit omissions without hiding failures')
    extracted = proof / 'EXTRACCION_ZIP_EXACTO'
    extracted.mkdir()
    with zipfile.ZipFile(staged) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(expected):
            raise ValueError('CRC/member set mismatch')
        for info in archive.infolist():
            if info.flag_bits & 1 or info.is_dir() or ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError('Encrypted/directory/symlink member not expected')
            target = safe(extracted, info.filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as inp, target.open('xb') as out:
                shutil.copyfileobj(inp, out)
            row = expected[info.filename]
            if target.stat().st_size != row['bytes'] or sha(target) != row['sha256']:
                raise ValueError('Exact extraction changed member bytes')
    command = [sys.executable, '-I', '-B', str(extracted / 'RECALCULO/recalcular_todo.py'),
               '--root', str(extracted), '--out', str(proof / 'RECALCULO_DESDE_ZIP')]
    run = subprocess.run(command, cwd=tempfile.gettempdir(), capture_output=True, text=True,
                         encoding='utf8', timeout=results.get('recalculation_timeout_seconds', 900))
    emit(proof / 'RECIBO_RECALCULO_ZIP.json', {'command': command, 'exit_code': run.returncode,
                                             'stdout': run.stdout, 'stderr': run.stderr})
    if run.returncode:
        raise ValueError('Exact extracted ZIP recalculation failed; no publication')
    if any(sha(safe(candidate, name)) != row['sha256'] for name, row in expected.items()):
        raise ValueError('Candidate changed during final verification')
    digest = sha(staged)
    shutil.copyfile(staged, final)
    if sha(final) != digest:
        raise ValueError('Published bytes differ from tested ZIP')
    emit(proof / 'VERIFICACION_FINAL_EXTERNA.json', {'schema': 'APD05.analysis_exact_zip_verification.R01',
         'zip': str(final), 'bytes': final.stat().st_size, 'sha256': digest, 'files': len(expected),
         'limit_bytes': LIMIT, 'CRC_and_all_members_verified': True, 'archived_recalculation_exit_code': run.returncode,
         'extraction': str(extracted), 'new_native_ticks': 0, 'Full_and_native_replay_verified_by_this_tool': False,
         'scope': 'Exact final ZIP/member bytes and archived selected calculations. Scientific attribution remains limited by evidence and sample.'})
    print(json.dumps({'zip': str(final), 'bytes': final.stat().st_size, 'sha256': digest,
                      'files': len(expected), 'proof': str(proof)}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('check-selection')
    p.add_argument('--results', required=True, type=Path)
    p = sub.add_parser('assemble')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--results', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--root-go', required=True, choices=['APD05_ANALYSIS_CLOSED_APPROVED'])
    p = sub.add_parser('seal')
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--delivery', required=True, type=Path)
    p.add_argument('--proof', required=True, type=Path)
    p.add_argument('--root-go', required=True, choices=['APD05_SEAL_EXACT_ANALYSIS_APPROVED'])
    args = parser.parse_args()
    if args.operation == 'check-selection':
        value = validate_results(read(args.results), approved=False)
        print(json.dumps({'schema_valid': True, 'status': value.get('status'), 'no_files_copied': True,
                          'new_native_ticks': 0}))
    elif args.operation == 'assemble':
        assemble(args.root, args.results, args.out)
    else:
        seal(args.candidate, args.delivery, args.proof)
