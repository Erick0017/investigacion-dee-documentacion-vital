"""Mocks/AST del guion Full prospectivo: no ZIP, Runtime, owner o S edits."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(root, out):
    here = Path(__file__).resolve().parent
    helper = load('full_apd04_mock_no_native', here / 'probar_full_apd04_entrada_r01.py')
    verifier = load('full_apd04_zip_mock_no_native', here / 'verificar_full_apd04_exacto_r01.py')
    ui = load('full_apd04_existing_parser_no_native', root / 'sistema/app/usar_dee.py')
    checks = []
    for name in ('probar_full_apd04_entrada_r01.py', 'verificar_full_apd04_exacto_r01.py', Path(__file__).name):
        ast.parse((here / name).read_text(encoding='utf8'))
        checks.append({'id': 'AST_' + name, 'ok': True})
    parser = ui.command_parser()
    argv = ['ensenar-ecosistema', 'clasifica', '-1', '--revision', '--docente', 'paired', '--retorno', 'omit']
    expected = [{'modo': 'apd04-docencia', 'texto': 'clasifica', 'senal': -1, 'docente': 'paired', 'revision': True}]
    checks.append({'id': 'LITERAL_SIGNED_LESSON_NO_COMPUTED_ANSWER', 'ok': ui.literal_rows(parser.parse_args(argv)) == expected})
    for name in ('clasifica', 'equilibra'):
        argv = ['palabra-ecosistema', name, '--retorno', 'omit']
        checks.append({'id': 'LITERAL_QUERY_' + name, 'ok': ui.literal_rows(parser.parse_args(argv)) == [{'modo': 'apd04-palabra', 'texto': name}]})
    for n in (12, 28, 32, 36):
        for sign in (-1, 1):
            panel = [{'site': list(site), 'raw': '0'} for site in sorted(helper.gates(n))]
            panel[0]['raw'] = str((1 << 60) | ((sign & 15) << 56) | 1)
            reader = {'panel': panel, 'formed_native_command': sign}
            checks.append({'id': 'SYNTHETIC_RAW_NOT_DEE_' + str(n) + '_' + str(sign),
                           'ok': len(panel) == n and helper.lexical_sign(reader) == sign})
    fake = (here / 'EXTRACCION_FICTICIA_NO_CREAR').resolve()
    argv = verifier.inner_argv(fake, fake / 'protocolo.json', fake / 'resultados')
    checks.append({'id': 'VERIFIER_EXECUTES_INCLUDED_HELPER_ONLY',
                   'ok': argv[0] == str(fake / 'motor/python313/python.exe')
                         and argv[4] == str(fake / 'actualizaciones/probar_full_apd04_entrada_r01.py')})
    template = json.loads((here / 'PROTOCOLO_FULL_APD04_PLANTILLA_R01.json').read_bytes())
    try:
        helper.run(fake, template, fake / 'trabajo_personal/resultados/NO_CREAR')
    except ValueError as error:
        rejected = 'not closed' in str(error)
    else:
        rejected = False
    checks.append({'id': 'DRAFT_REJECTED_BEFORE_ANY_OUTPUT_OR_NATIVE', 'ok': rejected and not fake.exists()})
    report = {'schema': 'APD04.Full_prospective_instrument_mock.N0.R01', 'checks': checks,
              'issues': [x for x in checks if not x['ok']], 'new_native_ticks': 0, 'owners_started': 0,
              'ZIP_extracted': False, 'Full_executed': False, 'system_source_modified': False,
              'scope': 'Parser, exact finite RAW synthetic fixtures, argv and authorisation guard only. Not acquisition or Full execution.'}
    with out.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')
    if report['issues']:
        raise ValueError('N0 prospective instrument check failed; no Native permitted')
    print(json.dumps({'checks': len(checks), 'issues': 0, 'new_native_ticks': 0, 'out': str(out)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.root.resolve(), args.out.resolve())
