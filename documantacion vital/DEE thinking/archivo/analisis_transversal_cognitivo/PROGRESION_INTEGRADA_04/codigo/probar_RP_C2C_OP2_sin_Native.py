"""Fake-boundary tests for opt-in material flag; never opens a DEE world."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import importlib.util
import json
import sys

P = Path(__file__).resolve().parents[1]
H = P / 'codigo'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    before = set(sys.modules)
    file = H / 'RP_C2C_PROPUESTA_OP2/reproducir.py'
    spec = importlib.util.spec_from_file_location('PI04_fake_boundary_RP', file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.config = lambda: {}
    calls = []
    def boundary(value):
        calls.append(value)
        raise RuntimeError('FAKE_DESTINATION_BOUNDARY_NO_WORLD')
    module.fresh_destination = boundary
    args = SimpleNamespace(vida='ECI02_PI03_REPRO_PI04_FAKEONLY', receta='fake', variante='real', destino='FAKE_ONLY', material=False)
    module.recipe = lambda name: {'requires_explicit_material': True, 'variants': {'real': {}}}
    rejected = False
    try: module.run_material(args)
    except ValueError as e: rejected = '--material' in str(e)
    assert rejected and not calls
    args.material = True
    reached_with_opt_in = False
    try: module.run_material(args)
    except RuntimeError as e: reached_with_opt_in = str(e) == 'FAKE_DESTINATION_BOUNDARY_NO_WORLD'
    assert reached_with_opt_in and len(calls) == 1
    args.material = False
    module.recipe = lambda name: {'variants': {'real': {}}}
    old_recipe_unchanged = False
    try: module.run_material(args)
    except RuntimeError as e: old_recipe_unchanged = str(e) == 'FAKE_DESTINATION_BOUNDARY_NO_WORLD'
    assert old_recipe_unchanged and len(calls) == 2
    forbidden = [m for m in set(sys.modules)-before if m == 'app' or m.startswith(('app.', 'dee', 'DEE', 'numpy'))]
    assert not forbidden
    assert (H / 'RP_C2C_PROPUESTA_OP1/ejecutar_diagnostico.py').read_bytes() == (H / 'RP_C2C_PROPUESTA_OP2/ejecutar_diagnostico.py').read_bytes()
    proof = {'schema': 'PI04.C2C.RP.OP2.pure_fake_boundary.v1', 'Native_ticks': 0,
        'proposal_file': str(file), 'proposal_sha256': sha(file),
        'new_recipe_without_material_refused_before_destination': rejected,
        'new_recipe_with_material_reaches_only_fake_boundary': reached_with_opt_in,
        'old_recipe_interface_unchanged': old_recipe_unchanged,
        'diagnostic_runner_identical_to_preceding_proposal': True,
        'forbidden_imports': forbidden, 'RP_deployed_or_material_run': False,
        'scope': 'Fake guard test, not current recipe requirements or a Native replay. The existing F1/E3 RP baseline is preserved.'}
    out = P / 'control/RP_C2C_OP2_PRUEBAS_PURAS.json'
    if out.exists(): raise ValueError('Do not overwrite proof')
    out.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
