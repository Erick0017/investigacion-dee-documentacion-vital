"""Prueba de herramientas N0 con datos sintéticos, no resultados DEE.

No aprueba una selección científica ni crea Word, ZIP o mundos. Verifica AST,
schema finito, límites de archivos, CLI archivada y cerca de dependencias.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def emit(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(filename, name):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    if not output.is_relative_to(HERE) or output.exists():
        raise ValueError('Fresh fixture below this LAB/cierre required')
    output.mkdir(parents=True)
    checks = []
    for path in sorted(HERE.glob('*.py')):
        ast.parse(path.read_text(encoding='utf8'))
        checks.append({'id': 'AST_' + path.name, 'ok': True})
    validator = module('validar_y_normalizar_seleccion_apd05_n0_r01.py', 'apd05_schema_fixture')
    assembler = module('preparar_entrega_apd05_r01.py', 'apd05_assembler_fixture')
    schema = json.loads((HERE / 'RESULTADOS_FINAL.schema.json').read_bytes())
    package = output / 'PAQUETE_SINTETICO_NO_DEE'
    package.mkdir()
    source = package / 'entrada.txt'
    source.write_text('Fixture instrumental sin conocimiento DEE.\n', encoding='utf8')
    calculator = package / 'calculador.py'
    calculator.write_text(
        "import argparse,hashlib,json\nfrom pathlib import Path\n"
        "p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);"
        "p.add_argument('--out',type=Path,required=True);a=p.parse_args()\n"
        "v={'fixture_not_DEE':True,'sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'new_native_ticks':0}\n"
        "with a.out.open('x',encoding='utf8',newline='\\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\\n')\n",
        encoding='utf8')
    expected = package / 'esperado.json'
    emit(expected, {'fixture_not_DEE': True, 'sha256': sha(source), 'new_native_ticks': 0})
    runner = package / 'RECALCULO/recalcular_todo.py'
    runner.parent.mkdir()
    shutil.copyfile(HERE / 'recalcular_analisis_apd05_n0_r01.py', runner)
    job = {'id': 'SYNTHETIC_EXACT', 'base': '.', 'script': 'calculador.py',
           'args': ['--input', {'input': 'entrada.txt'}, '--out', '{output}'],
           'expected': 'esperado.json', 'comparison': 'bytes',
           'script_sha256': sha(calculator), 'expected_sha256': sha(expected)}
    emit(package / 'RECALCULO/PLAN_GLOBAL.json', {'jobs': [job]})
    inventory = [{'file': path.relative_to(package).as_posix(), 'bytes': path.stat().st_size,
                  'sha256': sha(path)} for path in sorted(package.rglob('*')) if path.is_file()]
    emit(package / 'MANIFIESTO_HASHES.json', {'members': inventory})
    selection = {
        'schema': 'APD05.final_analysis_selection.R01', 'status': 'DRAFT_NOT_APPROVED',
        'native_work_closed': False, 'zip_name': 'FIXTURE_NEVER_PUBLISH.zip',
        'attempts': [{'id': 'FIXTURE', 'life': None, 'role': 'N0_INSTRUMENT',
                      'status': 'CLOSED_RESULT', 'scope': 'Synthetic tool test only', 'source_ids': ['INPUT']}],
        'claims': [{'id': 'FIXTURE', 'text': 'Tool fixture only, not a DEE claim',
                    'level': 'HECHO_COMPUTACIONAL', 'life': None, 'scope': 'Synthetic only',
                    'source_ids': ['INPUT'], 'limits': ['Not a world or scientific result']}],
        'lives': [{'id': 'NO_DEE_SYNTHETIC', 'parent': None, 'N': 0, 'tick': 0,
                   'snapshot_sha256': '0' * 64, 'status': 'NOT_A_DEE_LIFE', 'available': [],
                   'not_currently_proven': ['All DEE functions'], 'continuation': {}}],
        'executed_revisions': [{'id': 'FIXTURE_R01', 'scope': 'Tool only',
                                'source_ids': ['CALC'], 'provenance': 'Synthetic fixture'}],
        'files': [{'id': ident, 'source': name, 'destination': name, 'kind': 'SYNTHETIC_NOT_DEE',
                   'sha256': sha(package / name)}
                  for ident, name in [('INPUT', 'entrada.txt'), ('CALC', 'calculador.py'), ('REF', 'esperado.json')]],
        'components': [], 'jobs': [{k: v for k, v in job.items() if not k.endswith('_sha256')}],
        'omissions': []}
    validator.schema_features(schema)
    validator.validate(selection, schema, schema)
    validator.semantic_checks(selection)
    tests = validator.negative_tests(selection, schema)
    checks.append({'id': 'FINITE_SCHEMA_AND_NEGATIVE_FIXTURES', 'ok': all(x['rejected'] for x in tests),
                   'negative_fixtures': tests})
    try:
        assembler.validate_results(selection, approved=True)
    except ValueError:
        checks.append({'id': 'DRAFT_CANNOT_ASSEMBLE_SCIENTIFIC_PACKAGE', 'ok': True})
    else:
        raise ValueError('An unapproved draft was accepted')
    bad_names = ['../outside', '/absolute', 'C:/absolute', 'NUL/file', 'ends./x', 'a\\b']
    for name in bad_names:
        try:
            assembler.member(name)
        except ValueError:
            checks.append({'id': 'BAD_MEMBER_' + name, 'ok': True})
        else:
            raise ValueError('Unsafe member accepted: ' + name)
    for filename, data in [('forbidden.db', b'x'), ('disguised.txt', b'SQLite format 3\x00')]:
        path = output / filename
        path.write_bytes(data)
        try:
            assembler.check_analysis_file(path)
        except ValueError:
            checks.append({'id': 'FORBIDDEN_INPUT_' + filename, 'ok': True})
        else:
            raise ValueError('Forbidden input accepted')
    command = [sys.executable, '-I', '-B', str(runner), '--root', str(package),
               '--out', str(output / 'RECALCULO_POSITIVO')]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf8', timeout=30)
    checks.append({'id': 'ACTUAL_ARCHIVED_CLI_EXACT_BYTES', 'ok': result.returncode == 0,
                   'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    # Intentional read of a file outside the package; same actual worker fence.
    forbidden = package / 'dependencia_historica.py'
    forbidden.write_text('from pathlib import Path\nPath(' + repr(str(source.resolve())) +
                         ').parent.parent.parent.joinpath("forbidden.db").read_bytes()\n', encoding='utf8')
    plan = {'jobs': [job, {'id': 'FORBIDDEN_HISTORY', 'base': '.',
                         'script': forbidden.name, 'args': []}]}
    (package / 'RECALCULO/PLAN_GLOBAL.json').write_text(json.dumps(plan), encoding='utf8')
    bad_output = output / 'CERCA_NEGATIVA'
    bad_output.mkdir()
    bad = subprocess.run([sys.executable, '-I', '-B', str(runner), '--worker', '1',
                          '--root', str(package), '--out', str(bad_output)],
                         capture_output=True, text=True, encoding='utf8', timeout=30)
    checks.append({'id': 'HISTORICAL_READ_REJECTED',
                   'ok': bad.returncode != 0 and 'PermissionError' in bad.stderr,
                   'exit_code': bad.returncode, 'stderr': bad.stderr})
    report = {'schema': 'APD05.delivery_tools.synthetic_test.N0.R01', 'checks': checks,
              'issues': [x for x in checks if not x['ok']], 'new_native_ticks': 0,
              'Word_created': False, 'ZIP_created': False, 'Full_updated': False,
              'system_source_modified': False,
              'scope': 'Synthetic instrument tests only, not E1 capacities or APD05 scientific results.'}
    emit(output / 'COMPROBACION_HERRAMIENTAS_N0.json', report)
    if report['issues']:
        raise ValueError('Tool fixture failed; preserve the failure')
    print(json.dumps({'checks': len(checks), 'issues': 0, 'new_native_ticks': 0,
                      'scientific_selection_approved': False, 'ZIP_created': False}))


if __name__ == '__main__':
    main()
