"""Seal an explicitly approved APD02 analysis ZIP and recalculate its exact bytes.

External packaging proof only. No DEE import, native continuation, new lesson,
source-system edit or modification of the independent Full collaboration ZIP.
"""
import argparse, hashlib, json, subprocess, sys, time, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
RESERVED={'CON','PRN','AUX','NUL',*(f'COM{i}'for i in range(1,10)),*(f'LPT{i}'for i in range(1,10))}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    if not name or '\\' in name or ':' in name or p.is_absolute() or p.as_posix()!=name or any(k in ('', '.', '..')or k.endswith((' ','.'))or k.split('.')[0].upper()in RESERVED for k in p.parts):
        raise ValueError('Unsafe archive member')
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('stage', 'zip', 'extraction', 'results', 'proof'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--expected-cases',type=int,required=True)
    parser.add_argument('--autorizado-por-raiz',action='store_true',help='Only after explicit final Root approval; never set for preparation')
    a = parser.parse_args(); stage = a.stage.resolve(strict=True)
    archive = a.zip.resolve(); extraction = a.extraction.resolve(); results = a.results.resolve(); proof_path = a.proof.resolve()
    if any(p.exists() for p in (archive, extraction, results, proof_path)):
        raise FileExistsError('Fresh ZIP, extraction, result and external proof required')
    if any(p.is_relative_to(stage) or stage.is_relative_to(p) for p in (archive, extraction, results, proof_path)):
        raise ValueError('Keep outputs outside immutable analysis stage')
    if extraction.is_relative_to(results) or results.is_relative_to(extraction):
        raise ValueError('Keep immutable extraction and calculation outputs separate')
    plan = json.loads((stage/'PLAN_GLOBAL.json').read_bytes())
    if not a.autorizado_por_raiz or a.expected_cases<1 or plan['status'] != 'CLOSED_APPROVED_FOR_ANALYSIS' or plan.get('pending_components') or len(plan['cases']) != a.expected_cases or plan.get('expected_case_count')!=a.expected_cases:
        raise ValueError('Explicit Root-approved complete plan and pinned actual case count required')
    files = {}
    for p in sorted(stage.rglob('*')):
        if p.is_symlink() or getattr(p.stat(follow_symlinks=False), 'st_file_attributes', 0) & 0x400:
            raise ValueError('No symbolic/reparse members')
        if p.is_file():
            name = safe_name(p.relative_to(stage).as_posix())
            files[name] = {'bytes': p.stat().st_size, 'sha256': sha(p)}
    manifest = json.loads((stage/'MANIFIESTO_HASHES.json').read_bytes())
    expected = {row['path']: {'bytes': row['bytes'], 'sha256': row['sha256']} for row in manifest['members']}
    if len(expected)!=len(manifest['members']):raise ValueError('Duplicate stage manifest member')
    if set(files) != set(expected)|{'MANIFIESTO_HASHES.json'} or any(files[k] != v for k,v in expected.items()):
        raise ValueError('Original final stage manifest disagrees')
    archive.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
        for name in sorted(files):
            data = (stage/name).read_bytes()
            if hashlib.sha256(data).hexdigest() != files[name]['sha256']:
                raise ValueError('Source changed during seal')
            info = zipfile.ZipInfo(name, (2026,10,26,0,0,0)); info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3; info.external_attr = 0o100600 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    if archive.stat().st_size > 16000000:
        raise ValueError('ZIP exceeds16,000,000bytes: preserve it and ask Root before any omission')
    zip_sha = sha(archive); extraction.mkdir(parents=True)
    crc_bad = None
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != set(files):
            raise ValueError('ZIP member set differs from sealed final stage')
        crc_bad = z.testzip()
        if crc_bad is not None:
            raise ValueError('ZIP CRC failure: '+crc_bad)
        for name in names:
            safe_name(name); data = z.read(name)
            if len(data) != files[name]['bytes'] or hashlib.sha256(data).hexdigest() != files[name]['sha256']:
                raise ValueError('Exact ZIP member hash differs: '+name)
            target = extraction/name; target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as handle:
                handle.write(data)
            if sha(target) != files[name]['sha256']:
                raise ValueError('Extracted member differs: '+name)
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(extraction/'REPETIR_TODO.py'), '--salida', str(results)]
    run = subprocess.run(command, cwd=extraction, capture_output=True, text=True, encoding='utf8', errors='replace', timeout=1200)
    recalculation_path = results/'VERIFICACION_RECALCULOS.json'
    recalculation = json.loads(recalculation_path.read_bytes()) if recalculation_path.is_file() else {}
    exact = run.returncode == 0 and len(recalculation.get('cases', [])) == a.expected_cases and recalculation.get('all_selected_cases_exact') is True and not recalculation.get('issues') and recalculation.get('engine_imports_blocked') is True
    unchanged = sha(archive) == zip_sha
    record = {'schema': 'APD02.exact_analysis_ZIP_and_portable_recalculation.v1',
              'status': 'VERIFIED_EXACT_ARCHIVE_ALL_CASES_BYTE_IDENTICAL' if exact and unchanged else 'FAILED_PRESERVED_NO_RESEAL',
              'verified_utc': datetime.now(timezone.utc).isoformat(), 'native_ticks': 0,
              'Runtime_imported': False, 'archive': {'file': str(archive), 'bytes': archive.stat().st_size,
                  'sha256': zip_sha, 'absolute_limit_bytes': 16000000, 'member_count': len(files),
                  'CRC_all_members_valid': crc_bad is None, 'all_member_sizes_and_SHA256_verified': True,
                  'unchanged_after_extraction_and_recalculation': unchanged},
              'immutable_extraction': str(extraction), 'source_stage': str(stage),
              'source_manifest_sha256': sha(stage/'MANIFIESTO_HASHES.json'),
              'command': command, 'cwd': str(extraction), 'returncode': run.returncode,
              'stdout': run.stdout, 'stderr': run.stderr,
              'recalculation_report': {'file': str(recalculation_path), 'sha256': sha(recalculation_path) if recalculation_path.is_file() else None,
                  'case_count': len(recalculation.get('cases', [])), 'expected_case_count':a.expected_cases,'all_selected_cases_byte_exact': exact,
                  'issues': recalculation.get('issues', ['Report absent']),
                  'restored_logical_files': recalculation.get('restored_logical_files'),
                  'restored_logical_bytes': recalculation.get('restored_logical_bytes'),
                  'unique_content_objects': recalculation.get('unique_content_objects'),
                  'engine_imports_blocked': recalculation.get('engine_imports_blocked')},
              'assembly_event_scope': 'ESTADO_PREPARACION.json ZIP_generated:false records the assembly event before archive creation, not the later sealed state. Its CLOSED status/campaign_final:true/pending[] describe the completed evidence assembly. This external exact-ZIP proof is the authority for sealing and archive identity.',
              'no_lossless_evidence_omitted_for_size': True,
              'scientific_scope': 'Archived numerical/RAW/reader/artifact recalculation from restored exact bytes, not native replay, a new acquisition or a new simulator interaction. All scientific positive/negative references and original gzip/code bytes remain unchanged.',
              'elapsed_packaging_and_proof_seconds': time.monotonic()-started,
              'packaging_verifier_sha256': sha(Path(__file__))}
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    with proof_path.open('x', encoding='utf8',newline='\n') as handle:
        json.dump(record, handle, ensure_ascii=False, sort_keys=True, indent=2); handle.write('\n')
    print(json.dumps({'proof': str(proof_path), 'proof_sha256': sha(proof_path),
                      'status': record['status'], 'archive': record['archive'],
                      'cases': len(recalculation.get('cases', [])), 'exact': exact,
                      'elapsed_seconds': record['elapsed_packaging_and_proof_seconds']}))
    return not (exact and unchanged)


if __name__ == '__main__':
    raise SystemExit(main())
