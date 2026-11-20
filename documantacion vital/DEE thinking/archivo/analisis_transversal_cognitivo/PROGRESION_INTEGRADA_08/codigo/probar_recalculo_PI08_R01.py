"""Pure tests plus six literal historical PI07 primaries. No Native execution."""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
P8 = HERE.parent
P7 = P8.parent/'PROGRESION_INTEGRADA_07'
sys.path.insert(0, str(HERE))
from auditoria_documental_PI08 import count_request_ledger, digest, interval_union, receipt_map, safe_name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--destino', type=Path, required=True)
    a = ap.parse_args()
    dest = a.destino.resolve()
    if not dest.is_relative_to(HERE) or dest.exists():
        raise ValueError('Fresh P8/codigo-only test destination required')
    dest.mkdir(parents=True)
    checks = []
    for name in ('auditoria_documental_PI08.py', 'RECALCULAR_PRIMARIOS_PI08.py'):
        ast.parse((HERE/name).read_text('utf-8'))
    checks.append({'name': 'stdlib_tools_AST', 'passed': True})
    r = {'id': 1, 'receipt': {'id': 1, 'status': 'applied'}}
    _, s = receipt_map([r, r])
    assert s['unique_requested'] == 1 and s['aliases_not_new_events'] == 1
    checks.append({'name': 'aliases_not_new_Native_inputs', 'passed': True})
    try:
        receipt_map([r, {'id': 1, 'receipt': {'id': 1, 'status': 'rejected_occupied'}}])
    except ValueError:
        checks.append({'name': 'contradictory_alias_rejected', 'passed': True})
    else:
        raise AssertionError('Contradictory aliases were accepted')
    scoped = count_request_ledger([{'source': 'A', 'world_key': 'cloneA', 'requests': [r]},
                                   {'source': 'B', 'world_key': 'cloneB', 'requests': [r]}])
    assert scoped['unique_current_Native_requests'] == 2
    checks.append({'name': 'same_Native_ID_in_two_clones_not_merged', 'passed': True})
    union = interval_union([(0, 10), (5, 15), (15, 15)])
    assert union['unique_recorded_tick_advancements'] == 15 and union['raw_interval_sum'] == 20
    checks.append({'name': 'overlap_and_zero_tick_windows_not_inflated', 'passed': True})
    for bad in ('../escape', '/absolute', 'C:/absolute', '\\server\\share', 'x\\y'):
        try:
            safe_name(bad)
        except ValueError:
            continue
        raise AssertionError('Unsafe path accepted: ' + bad)
    checks.append({'name': 'portable_path_rejections', 'passed': True})
    index = {'schema': 'DEE.PI08.portable_primary_index.v1', 'primaries': [], 'products': [],
             'scope': 'Historical PI07 documentary test fixtures only; not PI08 experiences.'}
    for folder in ('PRUEBA_PORTABLE_PRIMARIOS_PI07_R01', 'PRUEBA_PORTABLE_C2C_28_29_R01'):
        root = P7/'control'/folder
        old = json.loads((root/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI07.json').read_text('utf-8'))
        for kind in ('primaries', 'products'):
            for entry in old[kind]:
                source = root/entry['file']
                data = source.read_bytes()
                assert len(data) == entry['bytes'] and digest(data) == entry['sha256']
                target = dest/entry['file']
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    assert target.read_bytes() == data
                else:
                    target.write_bytes(data)
                assert source.read_bytes() == data
                copy = dict(entry, modality='HISTORICAL_RECORDED_EXECUTION_NOT_PI08_NATIVE')
                copy['source_reference_for_packager_only'] = str(source.resolve())
                index[kind].append(copy)
    ip = dest/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json'
    ip.write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    tool = runpy.run_path(str(HERE/'RECALCULAR_PRIMARIOS_PI08.py'), run_name='pure_pi08_test')
    result = tool['recalculate'](dest)
    assert result['all_checks_passed'] and result['episodes_recalculated'] == 4
    assert len(result['C2C_chain_witnesses_recalculated_separately']) == 2
    assert result['new_Native_ticks'] == 0 and result['DEE_imports'] == 0
    checks.append({'name': 'six_literal_PI07_primaries_recognized_without_actor_execution', 'passed': True,
                   'episodes': 4, 'C2C_chains': 2, 'checks': len(result['checks'])})
    output = dest/'RECALCULO_HISTORICO.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    # Hash-only empty evidence cannot be declared a functional verification.
    empty = dest/'empty';(empty/'04_EVIDENCIAS/PRIMARIOS').mkdir(parents=True)
    (empty/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json').write_text(
        json.dumps({'schema': 'DEE.PI08.portable_primary_index.v1', 'primaries': [], 'products': []}), encoding='utf-8')
    assert tool['recalculate'](empty)['all_checks_passed'] is False
    checks.append({'name': 'empty_evidence_is_not_functional_PASS', 'passed': True})
    proof = {'schema': 'DEE.PI08.documentary_tools_test.v1',
             'at': datetime.datetime.now().astimezone().isoformat(), 'checks': checks,
             'all_checks_passed': all(c['passed'] for c in checks),
             'historical_fixture_recalculation': str(output),
             'historical_fixture_result_sha256': digest(output.read_bytes()),
             'new_Native_ticks': 0, 'DEE_imports': 0, 'product_modified': False,
             'scope': 'Pure helper tests and documentary recalculation of six already published PI07 primaries; '
                      'not new experiences, independent replicas or validation of future PI08 behavior.'}
    pp = dest/'PRUEBA.json';pp.write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'proof': str(pp), 'sha256': digest(pp.read_bytes()), 'all_checks_passed': proof['all_checks_passed'],
                      'new_Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
