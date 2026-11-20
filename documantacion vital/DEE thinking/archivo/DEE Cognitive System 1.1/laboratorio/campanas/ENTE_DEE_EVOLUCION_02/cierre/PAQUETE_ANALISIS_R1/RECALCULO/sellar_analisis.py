"""Seal and independently verify the exact EO02 scientific analysis ZIP."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, gzip, hashlib, json, os, subprocess, tempfile, zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STAGE = HERE / 'PAQUETE_ANALISIS'


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--verificacion-completa', type=Path, required=True)
    p.add_argument('--python', type=Path, required=True)
    p.add_argument('--colaborador', type=Path, required=True)
    p.add_argument('--stage', type=Path, required=True)
    a = p.parse_args()
    fullproof = a.verificacion_completa.resolve(strict=True)
    fullproof_data = json.loads(fullproof.read_bytes())
    # The evidence attached here must certify the exact current full archive,
    # not merely be a parseable historical receipt with a reassuring name.
    fullzip = Path(fullproof_data['zip']).resolve(strict=True)
    if fullproof_data.get('schema') != 'DEE.independent_delivery.v2':
        raise ValueError('Unsupported full-distribution verification schema')
    if (fullproof_data.get('campaign') != 'ENTE_DEE_EVOLUCION_02'
            or fullproof_data.get('status') != 'COMPLETED_WITH_RECORDED_SCOPE'
            or fullproof_data.get('originals_unchanged') is not True
            or fullproof_data.get('zip_unchanged') is not True):
        raise ValueError('Full-distribution proof is incomplete or records changed originals/archive')
    commands = fullproof_data.get('commands', [])
    if not commands or any(c.get('exit_code') != 0 for c in commands):
        raise ValueError('Full-distribution operational command failed or is missing')
    if fullproof_data.get('archive', {}).get('crc') != 'verified':
        raise ValueError('Full-distribution CRC was not verified')
    if (sha(fullzip) != fullproof_data['zip_sha256']
            or fullzip.stat().st_size != fullproof_data['zip_bytes']):
        raise ValueError('The current full archive differs from its completed verification')
    stage = a.stage.resolve(strict=True)
    if not stage.is_relative_to(HERE) or not stage.name.startswith('PAQUETE_ANALISIS_'):
        raise ValueError('Use one explicitly prepared analysis staging revision')
    target = ROOT / 'entregas/DEE_ENTE_EVOLUCION_02_ANALISIS.zip'
    candidate = target.with_suffix('.candidato.zip')
    verification = ROOT / 'entregas/VERIFICACION_ENTE_EVOLUCION_02_ANALISIS_EXTERNA.json'
    if any(q.exists() for q in (target, candidate, verification)):
        raise FileExistsError('A previously sealed candidate is protected; use an explicit new revision')
    if not stage.is_dir():
        raise FileNotFoundError('Prepare the closed analysis stage first')
    sources = {f.relative_to(stage).as_posix(): f for f in stage.rglob('*') if f.is_file()}
    sources['VERIFICACION_PAQUETE_COMPLETO_EXTERNA.json'] = fullproof
    manifest = {'schema': 'EO02.analysis.members.v1', 'members': [],
                'self_hash_intentionally_absent': True, 'analysis_is_not_full_native_backup': True}
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, source in sorted(sources.items()):
            if name.startswith('/') or '..' in Path(name).parts:
                raise ValueError('Unsafe ZIP member')
            z.write(source, name)
            info = z.getinfo(name)
            manifest['members'].append({'path': name, 'bytes': source.stat().st_size,
                                        'compressed_bytes': info.compress_size, 'sha256': sha(source)})
        z.writestr('MANIFIESTO_HASHES.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    if candidate.stat().st_size > 16000000:
        raise ValueError('Strict analysis size limit exceeded; candidate retained, not published')
    extract = Path(tempfile.mkdtemp(prefix='EO02-analisis-final-')).resolve()
    readable = {'json': 0, 'gzip_json': 0, 'text': 0, 'docx': 0, 'binary': 0}
    with zipfile.ZipFile(candidate) as z:
        if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('ZIP CRC or duplicate-member failure')
        for row in manifest['members']:
            data = z.read(row['path'])
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('ZIP member hash mismatch')
            name = row['path']
            if name.endswith('.json.gz'):
                json.loads(gzip.decompress(data)); readable['gzip_json'] += 1
            elif name.endswith('.json'):
                json.loads(data); readable['json'] += 1
            elif name.endswith(('.md', '.py', '.txt', '.csv', '.jsonl')):
                data.decode('utf8'); readable['text'] += 1
            elif name.endswith('.docx'):
                import io
                with zipfile.ZipFile(io.BytesIO(data)) as word:
                    if word.testzip() is not None:
                        raise ValueError('DOCX CRC failure')
                    from xml.etree import ElementTree
                    ElementTree.fromstring(word.read('word/document.xml'))
                readable['docx'] += 1
            else:
                readable['binary'] += 1
        z.extractall(extract)
    command = [str(a.python), '-I', '-B', '-X', 'utf8',
               str(extract / 'RECALCULO/verificar_analisis_final.py'),
               '--prohibir-raiz', str(ROOT), '--prohibir-raiz', str(a.colaborador.resolve())]
    r = subprocess.run(command, cwd=extract, capture_output=True, text=True, encoding='utf8', timeout=300)
    receipt = extract / 'RECALCULADO_DESDE_ZIP/VERIFICACION_RECALCULO_DESDE_ZIP.json'
    if r.returncode or not receipt.exists():
        raise RuntimeError('Exact final ZIP recalculation failed: ' + r.stdout + '\n' + r.stderr)
    proof = json.loads(receipt.read_bytes())
    if not proof['all_three_byte_identical'] or proof['denied_attempts']:
        raise ValueError('Recalculation verification rejected')
    before = sha(candidate)
    os.rename(candidate, target)
    if sha(target) != before:
        raise ValueError('Sealing changed ZIP bytes')
    report = {'schema': 'EO02.analysis.final.external.v1',
              'closed_utc': datetime.now(timezone.utc).isoformat(), 'zip': str(target),
              'bytes': target.stat().st_size, 'sha256': sha(target),
              'files': len(manifest['members']) + 1, 'strict_limit_bytes': 16000000,
              'member_hashes_verified': True, 'crc_verified': True, 'readability': readable,
              'extracted_to': str(extract), 'recalculation_command': command,
              'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr,
              'archived_recalculation': proof,
              'full_distribution_verification_source': str(fullproof),
              'full_distribution_verification_sha256': sha(fullproof),
              'full_distribution_verification_schema': fullproof_data.get('schema'),
              'full_distribution_exact_zip_checked': {'path': str(fullzip),
                  'bytes': fullzip.stat().st_size, 'sha256': sha(fullzip)},
              'same_machine_not_second_computer': True,
              'no_engine_or_all_snapshots_in_analysis': True,
              'new_native_ticks': 0, 'new_worker_executions': 0, 'private_no_remote_upload': True}
    verification.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
