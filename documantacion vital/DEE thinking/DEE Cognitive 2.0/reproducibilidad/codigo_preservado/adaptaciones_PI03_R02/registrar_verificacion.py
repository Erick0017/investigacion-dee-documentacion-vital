"""Register one actual completed diagnostic run, without executing/promoting DEE.

The evidence registry augments the catalogue; it never turns a local criterion
into a global PASS, changes a recipe's decoder, or selects ACTIVO. Negative
completed results are preserved and are as registrable as positive ones.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def describe(p, root): return {'file': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
def safe(root, name):
    p = root / name
    for q in (p, *p.parents):
        if q.is_symlink() or getattr(q.lstat(), 'st_file_attributes', 0) & 1024: raise ValueError('Linked evidence refused')
        if q == root: break
    p = p.resolve(strict=True)
    if not p.is_relative_to(root): raise ValueError('Evidence path escapes diagnostic root')
    return p

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--resultado', required=True, type=Path)
    p.add_argument('--nota', default=''); a = p.parse_args()
    target = a.resultado.resolve(strict=True)
    if target.name != 'RESULTADO_REPRODUCCION.json': raise ValueError('Exact completed diagnostic summary required')
    root = target.parent; result = read(target); context_path = safe(root, 'CONTEXTO_EJECUCION.json'); c = read(context_path)
    if not result['life'].startswith('ECI02_PI03_REPRO_') or result['life'] != c['life']:
        raise ValueError('No registrar principal ni identidad distinta')
    if result['recipe'] != c['recipe'] or result['variant'] != c['variant']:
        raise ValueError('Recipe/variant identity differs')
    if result.get('status') != 'COMPLETED' or result.get('owner_closed_coherently') is not True:
        raise ValueError('No registrar una ejecución interrumpida/propietario no cerrado como comprobación completa')
    if not isinstance(result.get('criteria_met'), bool): raise ValueError('No fixed-criterion result')
    imported_path = safe(root, 'IMPORTACION_DIAGNOSTICA.json'); imported = read(imported_path)
    comparison = imported['comparison']
    if imported['new_native_ticks'] != 0 or not comparison['physical_equal'] or not comparison['causal_prefix_equal']:
        raise ValueError('Initial complete-state import not demonstrated')
    # Source prefix must still be the exact full coherent pair used, not a
    # conveniently substituted acquired state with the same tick label.
    prefix_manifest = Path(c['prefix']) / 'EXPORTACION_SERVICIO.json'
    if sha(prefix_manifest) != c['prefix_manifest_sha256'] or result['source_manifest_sha256'] != c['prefix_manifest_sha256']:
        raise ValueError('Source complete-prefix identity differs')
    evidence = [describe(target, root), describe(context_path, root), describe(imported_path, root)]
    for row in result['rows']:
        primary = safe(root, row['primary']); receipt = read(primary)
        if receipt['status'] != 'completed' or receipt['id'] != row['transport_id']:
            raise ValueError('Primary terminal request differs from result')
        evidence.append(describe(primary, root))
    registry = HERE / 'verificaciones' / c['recipe']; registry.mkdir(parents=True, exist_ok=True)
    record_path = registry / (c['life'] + '.json')
    record = {'schema': 'DEE.reproduction.completed_run.evidence.v1', 'registered_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'recipe': c['recipe'], 'variant': c['variant'], 'life': c['life'], 'diagnostic_root': str(root),
              'source_prefix_manifest_sha256': c['prefix_manifest_sha256'], 'recipe_sha256_at_run': c['recipe_sha256'],
              'actual_native_execution_completed': True, 'owner_closed_coherently': True,
              'fixed_local_criteria_met': result['criteria_met'], 'denominators': result.get('denominators'),
              'native_receipts': result.get('native_receipts'), 'initial_tick': imported['result']['physical']['tick'],
              'final_tick': result.get('last_tick'), 'evidence': evidence, 'note': a.nota,
              'not_a_promotion': True, 'not_an_acquisition_claim_beyond_recipe': True,
              'scope': 'One actual descendant/prefix/variant, with shared past. Fixed local result only; no global cognitive PASS or automatic principal update.'}
    if record_path.exists():
        old = read(record_path)
        compare_keys = ('recipe','variant','life','source_prefix_manifest_sha256','recipe_sha256_at_run','evidence')
        if any(old.get(k) != record.get(k) for k in compare_keys): raise FileExistsError('Existing distinct verification protected')
        print(json.dumps({'existing_identical_evidence_reused': str(record_path)}, ensure_ascii=False)); return 0
    with record_path.open('x', encoding='utf-8') as f: json.dump(record, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'verification_recorded': str(record_path), 'local_criteria_met': record['fixed_local_criteria_met'],
                      'principal_modified': False, 'new_native_ticks_in_registration': 0}, ensure_ascii=False))
    return 0

if __name__ == '__main__': raise SystemExit(main())
