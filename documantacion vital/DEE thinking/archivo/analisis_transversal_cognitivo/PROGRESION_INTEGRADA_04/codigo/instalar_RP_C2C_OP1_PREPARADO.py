"""Prepare/apply the reviewed C2C recipe and two bounded RP tool adaptations.

Default is a static plan only. Root must supply a registered exact final code
capsule and explicitly --aplicar after closing any RP material run. This tool
never imports DEE, starts an owner, changes ACTIVO, executes a recipe or promotes.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import shutil

P = Path(__file__).resolve().parents[1]
R = P.parent.parent.parent
C = R / 'DEE Cognitive 2.0'
RP = C / 'reproducibilidad'
H = P / 'codigo'
RECIPE_ID = 'pi04_c2c_adquisicion_20_R01'
MATERIAL = 'PI04_C2C_ANALISIS_REAL20_R01'
TOOLS = ('reproducir.py', 'ejecutar_diagnostico.py')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def encoded(v): return (json.dumps(v, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def bounded(root, relative):
    q = Path(relative)
    if q.is_absolute() or '..' in q.parts: raise ValueError('Relative regular path only')
    p = root / q
    if not p.resolve().is_relative_to(root.resolve()): raise ValueError('Escaping material')
    for node in [p, *p.parents]:
        if node.exists() and (node.is_symlink() or (getattr(node.lstat(), 'st_file_attributes', 0) & 0x400)):
            raise ValueError('No linked/reparse material')
        if node == root: break
    return p


def verified_files(root, manifest, expected_hash=None):
    m = bounded(root, manifest)
    if expected_hash and sha(m) != expected_hash: raise ValueError('Manifest identity changed')
    rows = read(m)['files']
    for r in rows:
        f = bounded(root, r['file'])
        if not f.is_file() or f.stat().st_size != r['bytes'] or sha(f) != r['sha256']:
            raise ValueError('Preserved member mismatch: ' + r['file'])
    return {'manifest': str(m), 'sha256': sha(m), 'files': len(rows), 'bytes': sum(r['bytes'] for r in rows)}


def exclusive(path, data):
    with path.open('xb') as f: f.write(data)


def replace_literal(path, data):
    temp = path.with_name(path.name + '.PI04_C2C_writing')
    exclusive(temp, data)
    temp.replace(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capsule-key', required=True)
    ap.add_argument('--receta-preparada', type=Path,
        default=H / 'REPRODUCIBILIDAD_C2C_REAL20_ANALISIS_PREPARADA_R01' / (RECIPE_ID + '.json'))
    ap.add_argument('--aplicar', action='store_true')
    a = ap.parse_args()
    if (RP / 'EJECUCION_MATERIAL.lock').exists():
        raise ValueError('RP material guard exists. Preserve/reconcile it with its real owner; this installer never removes a guard')
    resources = read(RP / 'RECURSOS.json')
    capsule = resources['code_capsules'][a.capsule_key]
    capsule_root = bounded(C, capsule['product_relative'])
    code_check = verified_files(capsule_root, capsule.get('manifest', 'SISTEMA_CODIGO.json'), capsule.get('manifest_sha256'))
    names = {r['file'] for r in read(capsule_root / capsule.get('manifest', 'SISTEMA_CODIGO.json'))['files']}
    required_code = {'capacidades/pi04_coordinacion_central_C2C.py',
        'capacidades/pi04_sensor_central_C2C_R01.py', 'capacidades/PROTOCOLO_PI04_C2C_R01.json'}
    if not required_code <= names:
        raise ValueError('The final capsule does not preserve the C2C module, fixed sensor and protocol')
    recipe_source = a.receta_preparada.resolve(strict=True)
    if not recipe_source.is_relative_to(H.resolve()) or recipe_source.is_symlink():
        raise ValueError('Only an explicit prepared PI04 code recipe may be installed')
    recipe = read(recipe_source)
    if recipe.get('id') != RECIPE_ID or recipe.get('schema') != 'DEE.reproduction.recipe.v1':
        raise ValueError('Only the reviewed C2C20 recipe schema/identity')
    if recipe['verification']['original_histories']['real']['opportunities'] != 20:
        raise ValueError('Only the genuine completed real20 reference is accepted')
    if recipe['verification']['original_histories']['real']['exact_direct_receipts'] != {
            'unique_requested': 3720, 'applied': 3720, 'rejected': 0, 'pending_or_other': 0}:
        raise ValueError('Direct original denominator differs; preserve and review, do not relax it')
    if recipe['prefix'] not in resources['pairs']: raise ValueError('Complete pre-C2C prefix is not registered')
    tool_proposal = H / 'RP_C2C_PROPUESTA_OP2'
    revision = read(tool_proposal / 'PROPUESTA_Y_BASELINES.json')
    before = {}
    for name in TOOLS:
        before[name] = sha(RP / name)
        if before[name] != revision['source_baselines'][name]: raise ValueError('RP tool CAS failed: ' + name)
        if sha(tool_proposal / name) != revision['proposals'][name]: raise ValueError('Proposed RP tool changed')
        ast.parse((tool_proposal / name).read_text(encoding='utf8'))
    material_source = H / 'ANALISIS_RP_C2C_REAL20_PROPUESTA_R01' / MATERIAL
    entry = read(material_source.parent / 'ANALYSIS_ENTRY.json')
    material_check = verified_files(material_source, entry['manifest'], entry['manifest_sha256'])
    destination = RP / 'materiales' / MATERIAL
    recipe_destination = RP / 'recetas' / (RECIPE_ID + '.json')
    backup = RP / 'instrumentacion_preservada/PI04_C2C_ANTES_OP1'
    for target in (destination, recipe_destination, backup):
        if target.exists(): raise ValueError('A target already exists; preserve it rather than overwrite: ' + str(target))
    recipe['code_capsule_key'] = a.capsule_key
    pending_variants = [name for name, variant in recipe['variants'].items()
        if variant.get('not_yet_executed_original_reference') or not variant.get('final_checks')]
    recipe['verification']['prepared_but_not_enabled_variants'] = pending_variants
    recipe['variants'] = {name: variant for name, variant in recipe['variants'].items() if name not in pending_variants}
    if 'real' not in recipe['variants']: raise ValueError('The genuine original real20 reference must remain executable')
    recipe['reproduction_enabled'] = True
    recipe['revision'] = 'R01_PREPARADA_REPLAY_NATIVE_PENDIENTE'
    recipe['verification']['state'] = 'PREPARADA_REPLAY_NATIVE_PENDIENTE'
    recipe['requires_explicit_material'] = True
    recipe['usage']['reproducir'] += ' --material'
    recipe['blockers'] = []
    recipe_bytes = encoded(recipe)
    plan = {'schema': 'PI04.C2C.RP.installation.OP1', 'mode': 'APPLY' if a.aplicar else 'STATIC_PLAN_ONLY',
        'Native_ticks': 0, 'code_capsule_key': a.capsule_key, 'capsule': code_check,
        'complete_prefix': resources['pairs'][recipe['prefix']], 'analysis_material': material_check,
        'before_tool_hashes': before, 'after_tool_hashes': revision['proposals'],
        'recipe_source': str(recipe_source), 'recipe_source_sha256': sha(recipe_source),
        'recipe_destination': str(recipe_destination), 'recipe_sha256': hashlib.sha256(recipe_bytes).hexdigest(),
        'material_destination': str(destination), 'backup': str(backup), 'originals_unchanged': not a.aplicar,
        'Native_RP_replay_verified': False, 'no_selection_or_state_changes': True}
    if not a.aplicar:
        print(json.dumps(plan, ensure_ascii=False, indent=2)); return
    proof = P / 'control/INSTALACION_RP_C2C_OP1.json'
    if proof.exists(): raise ValueError('A prior installation proof exists; no repeat')
    backup.mkdir(parents=True)
    for name in TOOLS:
        shutil.copyfile(RP / name, backup / name)
        if sha(backup / name) != before[name]: raise ValueError('Literal tool preservation failed')
    exclusive(backup / 'ORIGEN_Y_PLAN.json', encoded(plan))
    shutil.copytree(material_source, destination)
    verified_files(destination, entry['manifest'], entry['manifest_sha256'])
    # No material execution can begin while the recipe is absent. Install the
    # tools first, then expose the reviewed recipe as the final atomic step.
    for name in TOOLS: replace_literal(RP / name, (tool_proposal / name).read_bytes())
    exclusive(recipe_destination, recipe_bytes)
    if any(sha(RP / name) != revision['proposals'][name] for name in TOOLS):
        raise ValueError('Installed tool verification failed; preserved originals remain available')
    plan['installed_recipe_sha256'] = sha(recipe_destination)
    plan['installed_analysis_manifest_sha256'] = sha(destination / entry['manifest'])
    plan['status'] = 'INSTALLED_PENDING_ROOT_NATIVE_REPLAY'
    exclusive(proof, encoded(plan))
    print(json.dumps({'proof': str(proof), 'sha256': sha(proof), 'Native_ticks': 0,
        'recipe': str(recipe_destination), 'next': 'Root verifies requirements, then executes one explicit fresh diagnostic clone'}, ensure_ascii=False))


if __name__ == '__main__': main()
