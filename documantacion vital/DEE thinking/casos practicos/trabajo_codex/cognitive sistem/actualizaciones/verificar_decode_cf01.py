"""Recalcula con AST/stdlib el contrato target-blind de decode_window, cero ticks."""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json


def decoder(source):
    content = source.read_bytes()
    tree = ast.parse(content, filename=str(source))
    found = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'decode_window']
    if len(found) != 1: raise ValueError('Se requiere exactamente decode_window de la revisión distribuida.')
    function = found[0]
    if function.decorator_list: raise ValueError('No se ejecutan decoradores ni imports al extraer el lector.')
    allowed_calls = {'next', 'reversed', 'len', 'str'}
    for node in ast.walk(function):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)):
            raise ValueError('La función dejó de ser un lector puro acotado.')
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in allowed_calls or isinstance(node.func, ast.Attribute) and node.func.attr == 'append'):
            raise ValueError('La función contiene una llamada nueva; revisar su frontera antes de recalcular.')
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {}
    exec(compile(module, str(source) + '::decode_window-only', 'exec'), namespace)
    return namespace['decode_window'], hashlib.sha256(content).hexdigest(), ast.dump(function, include_attributes=False)


def frame(tick, roles):
    contacts = {str(role): {'state': 0, 'semantic': 0, 'direction': [0, 0, 0]} for role in (-1, 0, 1)}
    for role in roles: contacts[str(role)] = {'state': 9, 'semantic': 1, 'direction': [role, -1, -1]}
    return {'tick': tick, 'contacts': contacts}


def case(early, deadline):
    return {'row': {'critical_tick': 100, 'availability': 1}, 'frames': [frame(84, early), frame(85, deadline)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fuente', type=Path, default=Path(__file__).resolve().parents[1] / 'sistema/capacidades/cierre_funcional_cf01.py')
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    source = args.fuente.resolve(strict=True)
    decode, digest, normalized_ast = decoder(source)
    cases = [('latest_unique', (-1,), (1,), 1, 85, 'current'),
             ('fixed_hold1', (-1,), (), -1, 84, 'fixed_hold_one_tick'),
             ('deadline_conflict', (-1,), (-1, 1), None, None, 'deadline_conflict'),
             ('early_conflict_then_unique', (-1, 1), (-1,), -1, 85, 'current'),
             ('no_output', (), (), None, None, 'no_native_output'),
             ('role0_fixed_transduction', (), (0,), 1, 85, 'current')]
    rows = []
    for name, early, deadline, command, tick, reason in cases:
        data = case(early, deadline); before = copy.deepcopy(data)
        observed = decode(data)
        assert (observed['command'], observed['source_tick'], observed['reason']) == (command, tick, reason), name
        assert data == before, 'El lector modificó su entrada: ' + name
        variants = []
        for availability in (-1, 1):
            for reference in (-64, 7, 64):
                varied = copy.deepcopy(data)
                varied['row']['availability'] = availability
                varied['row']['useful'] = reference != 7
                varied['target'] = {'reference': reference, 'optimal_action': -availability}
                varied['environment_reference_not_injected'] = reference
                variants.append(decode(varied))
        assert all(result == observed for result in variants), 'El lector consultó un target: ' + name
        rows.append({'case': name, 'observed': observed, 'target_variants_equal': len(variants), 'input_unchanged': True})
    # Las apariencias no admitidas no se rescatan como una salida válida.
    invalid = case((), (1,)); invalid['frames'][1]['contacts']['1']['semantic'] = 4
    assert decode(invalid)['command'] is None
    wrong_direction = case((), (-1,)); wrong_direction['frames'][1]['contacts']['-1']['direction'] = [1, 1, 1]
    assert decode(wrong_direction)['command'] is None
    report = {'schema': 'CF01.fixed_decoder.target_blind.v1', 'source': str(source), 'source_sha256': digest,
              'function_ast_sha256': hashlib.sha256(normalized_ast.encode()).hexdigest(), 'native_imports': 0, 'native_ticks': 0,
              'cases': rows, 'invalid_semantic_rejected': True, 'invalid_direction_rejected': True,
              'target_variant_comparisons': sum(row['target_variants_equal'] for row in rows),
              'scope': 'Pure output-transduction verification only; not native learning, causality of whole environment, or an independent cognition experiment.',
              'calibration': 'External world law stored with the external environment, not learned or selected by this decoder; P0 fixed two-tick sampling.'}
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True); args.salida.write_text(text, encoding='utf8')
    print(text)
    return 0


if __name__ == '__main__': raise SystemExit(main())
