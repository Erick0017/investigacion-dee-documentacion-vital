"""Prepare a static, manifested C2C analysis asset. Does NOT modify Cognitive.

The original portable evidence remains byte-identical; an adapter and a separate
outer manifest are added to a new proposal for later Root review and movement.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import shutil

P = Path(__file__).resolve().parents[1]
MEMBER = 'PI04_C2C_ANALISIS_REAL20_R01'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--destino', type=Path, required=True)
    a = ap.parse_args()
    source = a.evidence.resolve(strict=True)
    dest = a.destino.resolve()
    if not source.is_relative_to(P / 'ensayos') or source.is_symlink():
        raise ValueError('Directed PI04 portable evidence only')
    if not dest.is_relative_to(P / 'codigo') or dest.exists():
        raise ValueError('A NEW PI04 code proposal directory is required')
    manifest = read(source / 'MANIFEST.json')
    rows = manifest['files']
    expected = {r['file']: r for r in rows}
    actual = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
    derived = {'MANIFEST.json', 'PLAN_C2C_YOKED20_AUDITORIA.json',
        'PLAN_C2C_YOKED20_E3.json', 'PLAN_C2C_YOKED20_ENCODED.json', 'RECALCULO_C2C.json'}
    if set(actual) != set(expected) | derived:
        raise ValueError('The portable source has unmanifested or missing content')
    for name, row in expected.items():
        p = actual[name]
        if p.is_symlink() or not p.resolve().is_relative_to(source):
            raise ValueError('No linked source is allowed')
        if p.stat().st_size != row['bytes'] or sha(p) != row['sha256']:
            raise ValueError('Portable member mismatch: ' + name)
    adapter = P / 'codigo/recalcular_C2C_interfaz_RP_R01.py'
    ast.parse(adapter.read_text(encoding='utf8'))
    dest.mkdir(parents=True)
    material = dest / MEMBER
    shutil.copytree(source, material)
    shutil.copyfile(adapter, material / adapter.name)
    all_rows = [{'file': p.relative_to(material).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                for p in sorted(material.rglob('*')) if p.is_file()]
    out_manifest = material / 'MANIFIESTO_ESTABLE.json'
    out_manifest.write_text(json.dumps({'schema': 'DEE.PI04.C2C.stable_documentary_analysis.R01',
        'source_manifest_sha256': sha(source / 'MANIFEST.json'), 'files': all_rows},
        ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    entry = {'product_relative': 'reproducibilidad/materiales/' + MEMBER,
        'interface': 'DEE.recalculation.root_outdir.v1', 'manifest': out_manifest.name,
        'manifest_sha256': sha(out_manifest), 'recalculation_script': adapter.name}
    (dest / 'ANALYSIS_ENTRY.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    proof = {'schema': 'PI04.C2C.static_analysis_proposal.R01', 'status': 'PREPARED_NOT_INSTALLED',
        'source': str(source), 'source_manifest_sha256': sha(source / 'MANIFEST.json'),
        'proposal': str(material), 'analysis_entry': entry, 'members': len(all_rows),
        'bytes': sum(r['bytes'] for r in all_rows), 'Native_ticks': 0,
        'source_core_manifest_members': len(expected),
        'separately_preserved_source_derived_files': sorted(derived - {'MANIFEST.json'}),
        'original_members_identical': all(sha(p) == sha(material / name) for name, p in actual.items()),
        'Cognitive_modified': False}
    (dest / 'PREPARACION_SIN_NATIVE.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
