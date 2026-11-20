"""Preserve the exact frozen PI04 Cognitive source capsule in the existing RP.

No motor, world/state copy, Native import, capability evaluation or promotion.
Default only plans. Root applies after freezing its source code/owner changes.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil

P = Path(__file__).resolve().parents[1]
R = P.parent.parent.parent
C = R / 'DEE Cognitive 2.0'
RP = C / 'reproducibilidad'
SOURCE = P / 'estados/candidato_R02/sistema'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def data(v): return (json.dumps(v, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def regular(p):
    for node in [p, *p.parents]:
        if node.is_symlink() or (node.exists() and getattr(node.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('No linked/reparse source')
        if node == SOURCE: break
    if not p.is_file(): raise ValueError('Literal regular source file required')


def source_files():
    selected = set()
    for folder in (SOURCE, SOURCE / 'app', SOURCE / 'capacidades'):
        selected.update(folder.glob('*.py'))
    for folder in (SOURCE, SOURCE / 'contratos', SOURCE / 'capacidades'):
        selected.update(folder.glob('*.json'))
    rows = []
    for p in sorted(selected):
        regular(p)
        rel = p.relative_to(SOURCE).as_posix()
        rows.append({'file': rel, 'bytes': p.stat().st_size, 'sha256': sha(p)})
    needed = {'gestionar.py', 'app/cola_local.py', 'app/servicio_persistente.py',
        'capacidades/pi04_coordinacion_central_C2C.py', 'capacidades/pi04_sensor_central_C2C_R01.py',
        'capacidades/PROTOCOLO_PI04_C2C_R01.json'}
    if not needed <= {r['file'] for r in rows}: raise ValueError('Frozen source lacks required C2C/transport files')
    return rows


def exclusive(path, value):
    with path.open('xb') as f: f.write(value)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capsule-key', required=True)
    ap.add_argument('--aplicar', action='store_true')
    a = ap.parse_args()
    if not re.fullmatch(r'(?:PI04|PI03_PI04)_[A-Z0-9_]{1,70}', a.capsule_key):
        raise ValueError('New explicit PI04 capsule key required')
    resources_file = RP / 'RECURSOS.json'
    resources_bytes = resources_file.read_bytes()
    resources = json.loads(resources_bytes.decode('utf-8-sig'))
    if a.capsule_key in resources.get('code_capsules', {}): raise ValueError('Registered capsule is immutable; use its existing identity')
    dest = RP / 'codigo_preservado' / a.capsule_key
    proof = P / 'control' / ('CAPSULA_' + a.capsule_key + '.json')
    if dest.exists() or proof.exists(): raise ValueError('Do not overwrite a prior capsule/proof')
    rows = source_files()
    result = {'schema': 'PI04.exact_Cognitive_capsule.v1',
        'mode': 'APPLY' if a.aplicar else 'STATIC_PLAN_ONLY', 'source_system': str(SOURCE),
        'destination': str(dest), 'files': len(rows), 'bytes': sum(r['bytes'] for r in rows),
        'Native_ticks': 0, 'DEE_imports': 0, 'state_or_engine_copied': False,
        'Root_precondition': 'Source code frozen after operational guard review; no concurrent source/config writer'}
    if not a.aplicar:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return
    if (RP / 'EJECUCION_MATERIAL.lock').exists(): raise ValueError('No capsule registration while an RP material context is live')
    dest.mkdir(parents=True)
    for row in rows:
        src = SOURCE / row['file']; target = dest / row['file']
        target.parent.mkdir(parents=True, exist_ok=True)
        with src.open('rb') as f, target.open('xb') as g: shutil.copyfileobj(f, g)
        if target.stat().st_size != row['bytes'] or sha(target) != row['sha256']:
            raise ValueError('Source/copy changed; partial capsule preserved, not registered')
    if source_files() != rows: raise ValueError('Source changed during preservation; partial capsule not registered')
    manifest = dest / 'SISTEMA_CODIGO.json'
    exclusive(manifest, data({'schema': 'DEE.reproducibility.shared_code_capsule.v1',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_system': str(SOURCE), 'source_campaign': 'PI04', 'profile': 'fisica_directa', 'files': rows,
        'scope': 'Exact shared Cognitive Python/contracts/protocols, no states and no duplicate engine. Preserving code does not credit a life with a capability.'}))
    entry = {'product_relative': dest.relative_to(C).as_posix(), 'manifest': manifest.name,
        'manifest_sha256': sha(manifest)}
    if resources_file.read_bytes() != resources_bytes:
        raise ValueError('RECURSOS CAS changed; capsule preserved but not registered. Reconcile, do not overwrite')
    before = P / 'control' / ('RECURSOS_ANTES_CAPSULA_' + a.capsule_key + '.json')
    exclusive(before, resources_bytes)
    resources.setdefault('code_capsules', {})[a.capsule_key] = entry
    temp = resources_file.with_name(resources_file.name + '.PI04_CAPSULE_writing')
    exclusive(temp, data(resources)); temp.replace(resources_file)
    result.update(status='PRESERVED_AND_REGISTERED_NOT_NATIVE_VERIFIED', entry=entry,
        previous_resources={'path': str(before), 'sha256': sha(before)},
        current_resources_sha256=sha(resources_file), all_source_members_equal=True)
    exclusive(proof, data(result))
    print(json.dumps({'proof': str(proof), 'sha256': sha(proof), 'capsule': entry, 'files': len(rows),
        'Native_ticks': 0, 'no_operational_selection_changed': True}, ensure_ascii=False))


if __name__ == '__main__': main()
