"""Sella el análisis MENTE_ACUMULATIVA después de probar el ZIP completo exacto."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, gzip, hashlib, io, json, os, subprocess, tempfile, zipfile
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verificacion-completa', type=Path, required=True)
    p.add_argument('--python', type=Path, required=True)
    p.add_argument('--colaborador', type=Path, required=True)
    p.add_argument('--stage', type=Path, required=True)
    p.add_argument('--verificacion-adicional', type=Path, action='append', default=[])
    a = p.parse_args()
    fullproof = a.verificacion_completa.resolve(strict=True)
    d = json.loads(fullproof.read_bytes())
    if d.get('schema') != 'DEE.independent_delivery.v2' or d.get('campaign') != 'MENTE_ACUMULATIVA':
        raise ValueError('La prueba debe corresponder exactamente al nuevo cierre MA.')
    if d.get('status') != 'COMPLETED_WITH_RECORDED_SCOPE' or not d.get('originals_unchanged') or not d.get('zip_unchanged'):
        raise ValueError('La distribución todavía no superó su prueba independiente.')
    if not d.get('commands') or any(c.get('exit_code') != 0 for c in d['commands']) or d.get('archive', {}).get('crc') != 'verified':
        raise ValueError('Falta una operación de distribución o su CRC válido.')
    fullzip = Path(d['zip']).resolve(strict=True)
    if sha(fullzip) != d['zip_sha256'] or fullzip.stat().st_size != d['zip_bytes']:
        raise ValueError('El ZIP completo cambió después de probarlo.')
    stage = a.stage.resolve(strict=True)
    if not stage.is_relative_to(HERE) or not stage.name.startswith('PAQUETE_ANALISIS_'):
        raise ValueError('Use un staging explícito nuevo, sin modificar un análisis sellado.')
    target = ROOT / 'entregas/DEE_MENTE_ACUMULATIVA_ANALISIS.zip'
    candidate = target.with_suffix('.candidato.zip')
    external = ROOT / 'entregas/VERIFICACION_MENTE_ACUMULATIVA_ANALISIS_EXTERNA.json'
    if any(f.exists() for f in (target, candidate, external)):
        raise FileExistsError('Un archivo sellado anterior no se sobreescribe; requiere revisión identificada.')
    sources = {f.relative_to(stage).as_posix(): f for f in stage.rglob('*') if f.is_file()}
    sources['VERIFICACION_PAQUETE_COMPLETO_EXTERNA.json'] = fullproof
    extra_proofs = []
    for path in a.verificacion_adicional:
        path = path.resolve(strict=True); additional = json.loads(path.read_bytes())
        if (additional.get('schema') != 'DEE.independent_delivery.v2'
            or additional.get('campaign') != 'MENTE_ACUMULATIVA'
            or additional.get('status') != 'COMPLETED_WITH_RECORDED_SCOPE'
            or not additional.get('originals_unchanged') or not additional.get('zip_unchanged')
            or additional.get('zip_sha256') != d['zip_sha256']
            or additional.get('zip_bytes') != d['zip_bytes']
            or any(c.get('exit_code') != 0 for c in additional.get('commands', []))):
            raise ValueError('La comprobación complementaria no corresponde al mismo ZIP completo exacto.')
        sources['VERIFICACIONES_COMPLEMENTARIAS/' + path.name] = path
        extra_proofs.append({'path': str(path), 'sha256': sha(path)})
    manifest = {'schema': 'MENTE_ACUMULATIVA.analysis.members.v1', 'members': [],
                'self_hash_intentionally_absent': True, 'not_a_complete_operating_snapshot_backup': True}
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, source in sorted(sources.items()):
            q = PurePosixPath(name)
            if q.is_absolute() or '..' in q.parts or ':' in name: raise ValueError('Ruta ZIP insegura.')
            z.write(source, name)
            manifest['members'].append({'path': name, 'bytes': source.stat().st_size,
                                        'compressed_bytes': z.getinfo(name).compress_size, 'sha256': sha(source)})
        z.writestr('MANIFIESTO_HASHES.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    if candidate.stat().st_size > 16000000: raise ValueError('Límite estricto16,000,000B excedido; candidato conservado sin publicar.')
    extraction = Path(tempfile.mkdtemp(prefix='MA-analisis-final-')).resolve()
    readability = {'json': 0, 'json_gz': 0, 'text': 0, 'docx': 0, 'other': 0}
    with zipfile.ZipFile(candidate) as z:
        if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())): raise ValueError('CRC o miembros duplicados.')
        for row in manifest['members']:
            data = z.read(row['path'])
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']: raise ValueError('Hash miembro no coincide.')
            name = row['path']
            if name.endswith('.json.gz'): json.loads(gzip.decompress(data)); readability['json_gz'] += 1
            elif name.endswith('.json'): json.loads(data); readability['json'] += 1
            elif name.endswith('.docx'):
                with zipfile.ZipFile(io.BytesIO(data)) as word:
                    if word.testzip() is not None: raise ValueError('DOCX CRC no válido.')
                    ElementTree.fromstring(word.read('word/document.xml'))
                readability['docx'] += 1
            elif name.endswith(('.md', '.py', '.csv', '.txt', '.jsonl')): data.decode('utf8'); readability['text'] += 1
            else: readability['other'] += 1
        z.extractall(extraction)
    command = [str(a.python), '-I', '-B', '-X', 'utf8', str(extraction/'RECALCULO/verificar_analisis_final.py'),
               '--prohibir-raiz', str(ROOT), '--prohibir-raiz', str(a.colaborador.resolve())]
    r = subprocess.run(command, cwd=extraction, capture_output=True, text=True, encoding='utf8', timeout=300)
    receipt = extraction / 'RECALCULADO_DESDE_ZIP/VERIFICACION_RECALCULO_DESDE_ZIP.json'
    if r.returncode or not receipt.is_file(): raise RuntimeError('Recálculo del ZIP final falló: '+r.stdout+'\n'+r.stderr)
    proof = json.loads(receipt.read_bytes())
    if not proof.get('all_byte_identical') or proof.get('denied_attempts'): raise ValueError('Recálculo portable rechazado.')
    before = sha(candidate); os.rename(candidate, target)
    if sha(target) != before: raise ValueError('Cambió al sellar.')
    report = {'schema': 'MENTE_ACUMULATIVA.analysis.final.external.v1', 'closed_utc': datetime.now(timezone.utc).isoformat(),
              'zip': str(target), 'bytes': target.stat().st_size, 'sha256': sha(target), 'files': len(manifest['members'])+1,
              'strict_limit_bytes': 16000000, 'crc_verified': True, 'member_hashes_verified': True, 'readability': readability,
              'extracted_to': str(extraction), 'recalculation_command': command, 'returncode': r.returncode,
              'stdout': r.stdout, 'stderr': r.stderr, 'archived_recalculation': proof,
              'full_distribution_proof': str(fullproof), 'full_distribution_proof_sha256': sha(fullproof),
              'additional_distribution_proofs': extra_proofs,
              'full_distribution_exact_zip_checked': {'path': str(fullzip), 'bytes': fullzip.stat().st_size, 'sha256': sha(fullzip)},
              'same_machine_not_second_computer': True, 'new_native_ticks': 0, 'new_worker_executions': 0, 'no_upload': True}
    external.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__': main()
