"""Build prospective protocol copies in LAB only; do not install in sistema."""
from pathlib import Path
import ast
import difflib
import hashlib
import importlib.util
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE / 'PROPUESTA_SENSOR_R04_R01'


def main():
    if OUT.exists():
        raise FileExistsError('The prospective patch is frozen; create a declared new revision if needed')
    OUT.mkdir()
    members = []

    def proposed(relative, replacements):
        source = ROOT / 'sistema' / relative
        original = source.read_text(encoding='utf8')
        changed = original
        for old, new in replacements:
            if changed.count(old) != 1:
                raise ValueError('Patch base is not exact: ' + relative + ' / ' + old[:60])
            changed = changed.replace(old, new)
        ast.parse(changed)
        destination = OUT / 'sistema' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(changed, encoding='utf8', newline='\n')
        difference = ''.join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
            fromfile='sistema/' + relative, tofile='sistema/' + relative))
        members.append({'file': 'sistema/' + relative, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'proposed_sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
        return difference

    patches = []
    patches.append(proposed('app/protocolo_apd04.py', [
        ("      'apd04-lex-admitir':({'modo'},{'modo'}),", "      'apd04-lex-admitir':({'modo'},{'modo'}),\n      'apd04-r04-admitir':({'modo'},{'modo'}),"),
        ("('independent','independent_balanced','tag_only','zero')", "('independent','independent_balanced','independent_two_pairs','tag_only','zero')"),
        ("('R02','R03')", "('R02','R03','R04')"),
    ]))
    patches.append(proposed('capacidades/ecosistema_apd04.py', [
        ('from capacidades import sensor_balanceado_apd04 as balanced_sensor',
         'from capacidades import sensor_balanceado_apd04 as balanced_sensor\nfrom capacidades import sensor_dos_pares_apd04 as two_pair_sensor'),
        ("'apd04-sensor-calibrar','apd04-calibrar'", "'apd04-r04-admitir','apd04-sensor-calibrar','apd04-calibrar'"),
        ("    if mode=='apd04-sensor-calibrar':return", "    if mode=='apd04-r04-admitir':return\n    if mode=='apd04-sensor-calibrar':\n        if row['familia']=='R04':two_pair_sensor._get(a)\n        return"),
        ("    m=get(a)\n    if m.get('in_progress'):",
         "    if mode=='apd04-vivir' and row.get('sensor')=='independent_two_pairs':two_pair_sensor._get(a)\n    m=get(a)\n    if m.get('in_progress'):"),
        ("('independent','independent_balanced','tag_only','zero')", "('independent','independent_balanced','independent_two_pairs','tag_only','zero')"),
        ("sensor_mode in('independent','independent_balanced')", "sensor_mode in('independent','independent_balanced','independent_two_pairs')"),
        ("(balanced_sensor if sensor_mode=='independent_balanced'else sensor).selecciona(a,bit0,bit1,detail=detailed)",
         "{'independent_balanced':balanced_sensor,'independent_two_pairs':two_pair_sensor}.get(sensor_mode,sensor).selecciona(a,bit0,bit1,detail=detailed)"),
        ("(sensor if row['familia']=='R02'else balanced_sensor).selecciona(a,*bits,detail=detailed)",
         "{'R02':sensor,'R03':balanced_sensor,'R04':two_pair_sensor}[row['familia']].selecciona(a,*bits,detail=detailed)"),
        ("    if mode=='apd04-calibrar':\n        return {'kind':'explicit_auxiliary_native_calibration'",
         "    if mode=='apd04-r04-admitir':\n        screen=two_pair_sensor.preflight(a)\n        if not screen['admissible']:\n            return {'kind':'APD04_R04_P0_admission_rejected_without_material_write','admitted':False,'preflight':screen,'new_native_ticks_in_operation':0}\n        return two_pair_sensor.prepare(a)\n    if mode=='apd04-calibrar':\n        return {'kind':'explicit_auxiliary_native_calibration'"),
    ]))
    patches.append(proposed('app/usar_dee.py', [
        ('("independent", "independent_balanced", "tag_only", "zero")', '("independent", "independent_balanced", "independent_two_pairs", "tag_only", "zero")'),
        ('    eco_word = sub.add_parser("palabra-ecosistema",',
         '    eco_r04 = sub.add_parser("admitir-sensor-r04", help="Preparacion P0 explicita de dos puertos; no ensena contenido")\n    eco_sensor = sub.add_parser("calibrar-sensor-ecosistema", help="Entradas elementales literales; no retorno de calidad de tarea")\n    eco_sensor.add_argument("--familia", choices=("R02", "R03", "R04"), required=True)\n    eco_sensor.add_argument("pares", nargs="+", choices=("00", "01", "10", "11"))\n    eco_word = sub.add_parser("palabra-ecosistema",'),
        ('eco_start, eco_live, eco_change, eco_teach, eco_word):', 'eco_start, eco_live, eco_change, eco_teach, eco_word, eco_r04, eco_sensor):'),
        ('    if a == "ecosistema-vivir":',
         '    if a == "admitir-sensor-r04": return [{"modo": "apd04-r04-admitir"}]\n    if a == "calibrar-sensor-ecosistema": return [{"modo": "apd04-sensor-calibrar", "familia": options.familia,\n        "pares": [[int(pair[0]), int(pair[1])] for pair in options.pares]}]\n    if a == "ecosistema-vivir":'),
    ]))
    sensor = HERE / 'sensor_dos_pares_balanceados_apd04_r04.py'
    target = OUT / 'sistema/capacidades/sensor_dos_pares_apd04.py'
    shutil.copy2(sensor, target)
    members.append({'file': 'sistema/capacidades/sensor_dos_pares_apd04.py', 'source_sha256': None,
        'proposed_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    (OUT / 'PARCHE_PROPUESTO.diff').write_text(''.join(patches), encoding='utf8', newline='\n')
    namespace = {'__name__': 'prospective_literal_validation_only'}
    exec(compile((OUT / 'sistema/app/protocolo_apd04.py').read_text(encoding='utf8'), '<prospective_protocol>', 'exec'), namespace)
    positive = [{'modo': 'apd04-r04-admitir'},
        {'modo': 'apd04-sensor-calibrar', 'familia': 'R04', 'pares': [[0,0],[0,1],[1,0],[1,1]]},
        {'modo': 'apd04-vivir', 'oportunidades': 4, 'sensor': 'independent_two_pairs', 'lexico': True}]
    for row in positive:
        namespace['validate_literal'](row)
    negative = [{'modo': 'apd04-r04-admitir', 'target': 1},
        {'modo': 'apd04-sensor-calibrar', 'familia': 'R05', 'pares': [[0,0]]},
        {'modo': 'apd04-vivir', 'oportunidades': 4, 'sensor': 'answer_selected'}]
    for row in negative:
        try:
            namespace['validate_literal'](row)
        except ValueError:
            continue
        raise ValueError('Prospective literal validator admitted forbidden target/family/sensor')
    plan = {'schema': 'APD04.prospective_R04_single_AUX_plan.v1',
        'parent': 'APD04_MAIN_T639374_EXPLORACION_R01',
        'stages': [
            {'row': {'modo': 'apd04-r04-admitir'}, 'feedback': 'omit', 'scope': 'P0, reject rather than clean occupied source'},
            {'row': positive[1], 'feedback': 'omit', 'scope': 'Four fixed pairs, SUCCESS/omit only; no task-quality learning claim'},
            {'row': {'modo': 'apd04-cambio', 'etiqueta_objetivo': 0, 'palabra': 'clasifica', 'cargas': [7,3],
                'mutaciones': [{'fuente': 0, 'valor': 18}, {'fuente': 1, 'valor': 24}]}, 'feedback': 'omit'},
            {'row': positive[2], 'feedback': 'real', 'scope': 'First four live opportunities, same decoder and stale-cache treatment'}],
        'fixed_choice_codec': {'-1': 'USE', '0': 'INSPECT', '1': 'INSPECT'},
        'diagnostic9_not_an_action_reader': True, 'no_other_geometric_candidates': True,
        'no_native_execution_by_this_builder': True}
    for name, value in (('PLAN_AUX_R04_CONGELADO.json', plan),
                        ('MANIFIESTO_PROPUESTA_N0.json', {'members': members, 'AST_files': 4,
                         'positive_literal_cases': len(positive), 'negative_literal_cases_rejected': len(negative),
                         'shared_sistema_modified': False, 'Runtime_created': False, 'native_ticks': 0})):
        with (OUT / name).open('x', encoding='utf8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps({'folder': str(OUT), 'members': members, 'native_ticks': 0}, indent=2))


if __name__ == '__main__':
    main()
