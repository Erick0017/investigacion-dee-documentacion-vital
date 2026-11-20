"""Check the prepared recipe against CLOSED original records, not a DEE replay."""
from pathlib import Path
import ast
import hashlib
import json

P = Path(__file__).resolve().parents[1]
R = P.parent.parent.parent
RP = R / 'DEE Cognitive 2.0/reproducibilidad'


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def at(v, path):
    for key in path: v = v[key]
    return v


def main():
    file = P / 'codigo/REPRODUCIBILIDAD_C2C_REAL20_ANALISIS_PREPARADA_R01/pi04_c2c_adquisicion_20_R01.json'
    recipe = read(file)
    summaries = [read(P / 'control' / name) for name in ('PI04_C2C_REAL_DEV_R01.json', 'PI04_C2C_REAL_RES_R01.json')]
    result = {}
    for batch in summaries:
        assert batch['owner_closed'] is True
        for row in batch['rows']:
            raw = read(Path(row['primary']))
            result['opportunity_%02d' % row['ordinal']] = json.loads(raw['result']) if isinstance(raw['result'], str) else raw['result']
    result['final_state'] = summaries[-1]['final']
    checks = []
    for c in recipe['variants']['real']['final_checks']:
        assert c['operation'] == 'value'
        v = at(result[c['values'][0]['step']], c['values'][0]['path'])
        checks.append({'label': c['label'], 'observed': v, 'recorded_expected': c['expected'],
            'same_type_and_value': type(v) is type(c['expected']) and v == c['expected']})
    assert all(c['same_type_and_value'] for c in checks)
    steps = [s for b in recipe['variants']['real']['batches'] for s in b]
    assert len(steps) == 23 and sum(s['literal']['modo'].endswith('-oportunidad') for s in steps) == 20
    assert all(set(s['literal']) <= {'modo', 'brazo'} for s in steps)
    assert recipe['reproduction_enabled'] is False
    proposal = P / 'codigo/RP_C2C_PROPUESTA_OP1'
    baselines = read(proposal / 'PROPUESTA_Y_BASELINES.json')['source_baselines']
    original_rp_unchanged = {name: sha(RP / name) == h for name, h in baselines.items()}
    assert all(original_rp_unchanged.values())
    adapter = P / 'codigo/recalcular_C2C_interfaz_RP_R01.py'
    ast.parse(adapter.read_text(encoding='utf8'))
    original_report = P / 'ensayos/EVIDENCIA_C2C_REAL20_PORTABLE_R01/RECALCULO_C2C.json'
    adapter_report = P / 'control/RECALCULO_INTERFAZ_RP_C2C_REAL20_R01/RECALCULO_C2C.json'
    assert adapter_report.read_bytes() == original_report.read_bytes()
    proof = {'schema': 'PI04.C2C.prepared_recipe.documentary_check.R01',
        'mode': 'PASSIVE_COMPARISON_OF_CLOSED_ORIGINALS_NOT_NATIVE_REPLAY', 'Native_ticks': 0,
        'recipe': str(file), 'recipe_sha256': sha(file), 'original20_checks': checks,
        'all46_checks_match_original': len(checks) == 46 and all(c['same_type_and_value'] for c in checks),
        'material_transport_steps': len(steps), 'actual_opportunities': 20,
        'original_direct_receipt_expectations': recipe['variants']['real']['native_receipt_expectations'],
        'literal_has_no_expected_answers': True, 'RP_original_code_unchanged': original_rp_unchanged,
        'adapter_recalculation_identical': {'sha256': sha(adapter_report), 'bytes': adapter_report.stat().st_size},
        'Native_RP_replay_executed': False, 'installed_in_Cognitive': False,
        'limits': 'Capsule pending; controls pending. Checking recipe expectations against their original source is not an independent validation or Native reproduction.'}
    out = P / 'control/RP_C2C_REAL20_PREPARACION_VERIFICADA_R01.json'
    if out.exists(): raise ValueError('Do not overwrite a prior documentary proof')
    out.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'proof': str(out), 'sha256': sha(out), 'checks': len(checks),
        'all_match': all(c['same_type_and_value'] for c in checks), 'Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
