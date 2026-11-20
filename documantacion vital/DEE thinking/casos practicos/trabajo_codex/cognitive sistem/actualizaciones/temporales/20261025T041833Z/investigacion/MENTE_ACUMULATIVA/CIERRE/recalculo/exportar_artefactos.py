"""Exporta bytes reales de trabajadores ya ejecutados; cero decisiones y ticks."""
from pathlib import Path
import argparse, gzip, hashlib, json, re, shutil


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def local_rows(value):
    if isinstance(value, dict):
        if value.get('worker_receipt') and isinstance(value.get('before'), dict):
            yield value
        for k, v in value.items():
            if k != 'worker_receipt': yield from local_rows(v)
    elif isinstance(value, list):
        for v in value: yield from local_rows(v)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--primarios', type=Path, required=True)
    p.add_argument('--sistema', type=Path, required=True)
    p.add_argument('--destino', type=Path, required=True)
    p.add_argument('--indice', type=Path, required=True)
    a = p.parse_args()
    if a.indice.exists(): raise FileExistsError('El índice anterior se conserva; use un corte nuevo.')
    base = (a.sistema/'estado/servicios_locales').resolve(strict=True)
    rows, issues = [], []
    for primary in sorted(a.primarios.glob('*.json.gz')):
        if not re.match(r'^\d+[A-Za-z]*_', primary.name): continue
        record = json.loads(gzip.decompress(primary.read_bytes()))
        manager = record.get('result', {})
        instrument = manager.get('INSTRUMENTO', {}) if isinstance(manager, dict) else {}
        life = instrument.get('life_id') if isinstance(instrument, dict) else None
        if not life: continue
        seen = set()
        for ordinal, local in enumerate(local_rows(manager)):
            receipt = local['worker_receipt']; before = local['before']
            epoch = before.get('storage_epoch', before['domain']); name = receipt['output_name']
            if (epoch,name) in seen: continue
            seen.add((epoch,name))
            if any(Path(x).name != x for x in (life, epoch, name)): raise ValueError('Ruta de artefacto no segura.')
            source = (base/life/epoch/name).resolve()
            if not source.is_relative_to(base): raise ValueError('El artefacto sale del servicio declarado.')
            row = {'primary': primary.name, 'ordinal': ordinal, 'life': life, 'source': str(source),
                   'operation': receipt['operation'], 'accepted': receipt['accepted'],
                   'worker_revision': receipt['schema'], 'expected_sha256': receipt['output_sha256'],
                   'expected_bytes': receipt['output_bytes']}
            if not source.is_file(): row['status'] = 'SOURCE_NOT_FOUND'; issues.append(row.copy())
            else:
                row.update(actual_sha256=sha(source), actual_bytes=source.stat().st_size)
                if row['actual_sha256'] != row['expected_sha256'] or row['actual_bytes'] != row['expected_bytes']:
                    row['status'] = 'SOURCE_DIFFERS'; issues.append(row.copy())
                else:
                    target = a.destino/life/epoch/name; target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists() and target.read_bytes() != source.read_bytes(): raise FileExistsError('Se conserva una variante previa.')
                    if not target.exists(): shutil.copyfile(source, target)
                    row.update(status='BYTE_IDENTICAL_EXPORTED', export_member=target.relative_to(a.destino).as_posix())
            rows.append(row)
    report = {'schema': 'MENTE_ACUMULATIVA.actual_worker_bytes.v1', 'files_referenced': len(rows),
              'issues': issues, 'rows': rows, 'new_DEE_ticks': 0, 'new_worker_executions': 0,
              'scope': 'Sólo lectura y copia sin pérdidas de outputs cerrados cotejados contra sus recibos originales.'}
    a.indice.parent.mkdir(parents=True, exist_ok=True)
    a.indice.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'files_referenced': len(rows), 'issues': issues, 'index': str(a.indice)}, ensure_ascii=False))
    return bool(issues)


if __name__ == '__main__': raise SystemExit(main())
