"""Añade sólo componentes cerrados explícitos a otra revisión CAS, sin modificar base."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zlib


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def safe(root, name):
    p = Path(name)
    assert not p.is_absolute() and '..' not in p.parts
    return root / p


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True); p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True); p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    assert not a.out.exists() and not a.report.exists()
    selection = json.loads(a.spec.read_bytes())
    base = safe(a.root, selection['base'])
    base_manifest_bytes = (base / 'MANIFIESTO_CAS.json').read_bytes()
    assert sha(base_manifest_bytes) == selection['base_manifest_sha256']
    for row in json.loads(base_manifest_bytes)['members']:
        data = safe(base, row['file']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    index = json.loads((base / 'RUTAS_Y_HASHES.json').read_bytes())
    sources = {x['source_original']: dict(x) for x in index['sources']}
    a.out.mkdir(parents=True)
    shutil.copytree(base / 'OBJETOS', a.out / 'OBJETOS')
    for name in ('RESTAURAR_Y_RECALCULAR_CAS.py', 'recalcular_todo_CONGELADO.py', 'LEER_CAS.md'):
        shutil.copyfile(base / name, a.out / name)
    def add(source_name, expected_sha, expected_bytes, component):
        source = safe(a.root, source_name)
        before = source.stat()
        data = source.read_bytes()
        after = source.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        digest = sha(data)
        assert digest == expected_sha and len(data) == expected_bytes, source_name
        object_name = 'OBJETOS/' + digest[:2] + '/' + digest[2:] + '.bin'
        target = a.out / object_name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
        if source_name in sources:
            assert sources[source_name]['sha256'] == digest, 'Two revisions claimed under one source route'
        else:
            sources[source_name] = {'source_original': source_name, 'object': object_name,
                                   'bytes': len(data), 'sha256': digest, 'component': component}
    closed = []
    for component in selection['components']:
        folder = safe(a.root, component['source'])
        manifest_path = folder / component['manifest']
        data = manifest_path.read_bytes()
        assert sha(data) == component['manifest_sha256']
        manifest = json.loads(data)
        for row in manifest.get('members', manifest.get('files', [])):
            rel = row.get('file', row.get('path'))
            add(component['source'] + '/' + rel, row['sha256'], row['bytes'], component['id'])
        add(component['source'] + '/' + component['manifest'], sha(data), len(data), component['id'])
        closed.append(component)
    for row in selection.get('files', []):
        add(row['source'], row['sha256'], row['bytes'], row['id'])
    values = list(sources.values())
    dump(a.out / 'RUTAS_Y_HASHES.json', {'schema': 'APD04.exact_content_addressed_evidence.N0.R02',
         'status': 'DRAFT_CLOSED_COMPONENTS_NOT_FINAL_ANALYSIS', 'base_manifest_sha256': selection['base_manifest_sha256'],
         'source_count': len(values), 'unique_object_count': len({x['sha256'] for x in values}), 'sources': values,
         'closed_additional_components': closed, 'pending_not_included': selection['pending_not_included'],
         'omitted_selected_source_paths': [], 'new_native_ticks': 0})
    plan = json.loads((base / 'PLAN_GLOBAL_CAS.json').read_bytes())
    for job in selection['jobs']:
        job = dict(job)
        job['script_sha256'] = sources[job['script']]['sha256']
        job['expected_sha256'] = sources[job['expected']]['sha256']
        plan['jobs'].append(job)
    dump(a.out / 'PLAN_GLOBAL_CAS.json', plan)
    members = [{'file': path.relative_to(a.out).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes())}
               for path in sorted(a.out.rglob('*')) if path.is_file()]
    dump(a.out / 'MANIFIESTO_CAS.json', {'schema': 'APD04.CAS.members.N0.R02', 'members': members,
         'source_count': len(values), 'unique_objects': len({x['sha256'] for x in values}), 'no_source_bytes_omitted': True})
    estimate = 22
    for path in a.out.rglob('*'):
        if not path.is_file():
            continue
        data = path.read_bytes()
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        estimate += len(compressor.compress(data) + compressor.flush()) + 98 + 2 * (len(path.relative_to(a.out).as_posix().encode()) + 20)
    result = {'schema': 'APD04.CAS.extension_size.N0.R02', 'source_paths': len(values),
         'unique_objects': len({x['sha256'] for x in values}), 'source_bytes': sum(x['bytes'] for x in values),
         'estimated_zip_bytes': estimate, 'analysis_limit_bytes': 16000000,
         'remaining_estimated_headroom': 16000000 - estimate, 'jobs': len(plan['jobs']),
         'status': 'DRAFT_NOT_FINAL_APPROVED', 'pending_not_included': selection['pending_not_included'],
         'new_Native_ticks': 0, 'created_zip_count': 0, 'original_components_changed': False}
    dump(a.report, result)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
