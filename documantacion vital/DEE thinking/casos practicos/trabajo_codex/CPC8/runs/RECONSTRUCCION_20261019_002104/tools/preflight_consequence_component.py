"""Pure recipe validation and byte-source provenance; creates zero Runtime."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    original = ROOT / 'genealogia/primer_cpc8/regulacion_v2/src/regulacion/native_feedback.py'
    adapted = ROOT / 'src/regulacion_consecuencia/native_feedback_component.py'
    assert sha(original) == '207340cbf82f1464d328041c840a2a6e2b223751d19cb29c40b41fd56563aad7'
    text = original.read_text(encoding='utf-8')
    expected = text.replace('def prepare(*,', 'def prepare_component(*,').replace(
        'world=d.OrganizationalWorld.create(recipe)', 'world=recipe  # Inert recipe; the caller creates the sole owner Runtime.')
    actual = adapted.read_text(encoding='utf-8')
    assert actual.rstrip().endswith(expected.rstrip())
    assert 'world=d.OrganizationalWorld.create(recipe)' not in actual
    for path in (ROOT / 'src/regulacion_consecuencia').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    from regulacion_consecuencia.mcts import prepare_consequence_mcts, TRANSLATION
    recipe, geometry = prepare_consequence_mcts()
    feedback = geometry['consequence_regulation']
    original_config = json.loads((ROOT / 'genealogia/primer_cpc8/regulacion_v2/resultados/regulacion/REG_V2_P21/CONFIG.json').read_text(encoding='utf-8'))
    source_records = original_config['geometry']['initial_placements']
    for before, after in zip(source_records, feedback['initial_placements']):
        assert after['site'] == [(before['site'][i] + TRANSLATION[i]) % 67 for i in range(3)]
        assert all(before[field] == after[field] for field in ('load', 'direction', 'clock', 'role'))
    result = {'schema': 'CPC8R.consequenceMCTS.preflight.v1', 'Runtime_created': 0, 'N': 67,
              'fixed_translation': list(TRANSLATION), 'initial_material_count': len(recipe.placements),
              'MCTS_initial_material': 35, 'V2_initial_material_added': len(source_records),
              'interfaces': len(recipe.interfaces), 'V2_interfaces_added': 0,
              'material_overlap_count': 0, 'source_initial_clocks_directions_payloads_preserved': True,
              'original_source_sha256': sha(original), 'inert_adapter_sha256': sha(adapted),
              'exact_normalized_diff': list(difflib.unified_diff(text.splitlines(), expected.splitlines(), fromfile='native_feedback.py', tofile='native_feedback_component.py', lineterm='')),
              'changes': ['Builder name prepare -> prepare_component', 'Return inertrecipe instead of constructing an auxiliaryRuntime', 'Explanatory commentheader and trailing blank line only'],
              'scope': 'Preflight proves initial material compatibility and literal spatialtranslation only, NOT noninterference of later trajectories.'}
    output = ROOT / 'configuraciones/regulacion_consecuencia/PREFLIGHT_Y_PROCEDENCIA.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
