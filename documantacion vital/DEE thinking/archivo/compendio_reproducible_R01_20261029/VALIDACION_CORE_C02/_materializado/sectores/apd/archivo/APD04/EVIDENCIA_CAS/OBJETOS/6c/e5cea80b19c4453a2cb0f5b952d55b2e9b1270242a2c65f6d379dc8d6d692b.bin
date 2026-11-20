"""Prueba instrumental sintética N0; no Native, Word, Full, ZIP ni fuentes S.

El pequeño fixture NO representa un ente DEE ni un hallazgo APD04. Sólo prueba
copias exactas, recálculo portable y rechazo de una dependencia histórica.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


def emit(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def main(out):
    here = Path(__file__).resolve().parent
    out = out.resolve()
    if not out.is_relative_to(here):
        raise ValueError('Fixture must stay in LAB/cierre')
    out.mkdir(parents=True, exist_ok=False)
    checks = []
    for name in ('preparar_entrega_apd04_r01.py', 'recalcular_analisis_apd04_n0_r01.py', Path(__file__).name):
        ast.parse((here / name).read_text(encoding='utf8'))
        checks.append({'id': 'AST_' + name, 'ok': True})
    json.loads((here / 'RESULTADOS_FINAL.schema.json').read_bytes())
    source = out / 'ORIGEN_FIXTURE_NO_DEE'
    source.mkdir()
    (source / 'entrada.txt').write_text('fixture instrumental, no conocimiento\n', encoding='utf8')
    calculator = """import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
v={'fixture_not_DEE':True,'source_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'new_native_ticks':0}
with a.out.open('x',encoding='utf8',newline='\\n')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\\n')
"""
    (source / 'calculador_fixture.py').write_text(calculator, encoding='utf8')
    expected = {'fixture_not_DEE': True, 'source_sha256': hashlib.sha256((source / 'entrada.txt').read_bytes()).hexdigest(), 'new_native_ticks': 0}
    emit(source / 'esperado.json', expected)
    (source / 'dependencia_prohibida.py').write_text(
        "from pathlib import Path\nPath(" + repr(str(source / 'entrada.txt')) + ").read_bytes()\n", encoding='utf8')
    project = here.parents[3]
    files = [{'id': name, 'source': (source / name).relative_to(project).as_posix(), 'destination': name, 'kind': 'SYNTHETIC_INSTRUMENTAL_FIXTURE_NOT_DEE',
              'sha256': hashlib.sha256((source / name).read_bytes()).hexdigest()}
             for name in ('entrada.txt', 'calculador_fixture.py', 'esperado.json', 'dependencia_prohibida.py')]
    config = {'schema': 'APD04.final_analysis_selection.R01', 'status': 'FINAL_RESULTS_APPROVED_FOR_ANALYSIS',
              'native_work_closed': True, 'zip_name': 'FIXTURE_NO_SELLAR_NO_DEE.zip',
              'attempts': [{'id': 'FIXTURE', 'status': 'CLOSED_RESULT', 'scope': 'Synthetic test only, not a DEE attempt', 'source_ids': ['entrada.txt']}],
              'claims': [{'id': 'FIXTURE', 'scope': 'Synthetic test only, not a scientific claim', 'source_ids': ['entrada.txt']}],
              'lives': [{'id': 'NO_DEE_LIFE_SYNTHETIC_FIXTURE'}],
              'executed_revisions': [{'id': 'FIXTURE_R01', 'scope': 'Instrument only', 'source_ids': ['calculador_fixture.py']}],
              'files': files, 'components': [], 'omissions': [],
              'jobs': [{'id': 'FIXTURE_EXACT', 'base': '.', 'script': 'calculador_fixture.py',
                        'args': ['--input', {'input': 'entrada.txt'}, '--out', '{output}'],
                        'expected': 'esperado.json', 'comparison': 'bytes'}]}
    config_path = source / 'SELECCION_FIXTURE.json'
    emit(config_path, config)
    spec = importlib.util.spec_from_file_location('closure_fixture', here / 'preparar_entrega_apd04_r01.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    candidate = out / 'CANDIDATO_SINTETICO_NO_SELLO'
    module.assemble(project, config_path, candidate)
    runner = candidate / 'RECALCULO/recalcular_todo.py'
    command = [sys.executable, '-I', '-B', str(runner), '--root', str(candidate), '--out', str(out / 'RECALCULO_FIXTURE')]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf8', timeout=30)
    checks.append({'id': 'ACTUAL_ARCHIVED_CLI_BYTE_MATCH', 'ok': result.returncode == 0,
                   'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    # Direct worker exercises the exact same fence, deliberately on a new job.
    # No ZIP or scientific package is produced for this negative test.
    plan_path = candidate / 'RECALCULO/PLAN_GLOBAL.json'
    plan = json.loads(plan_path.read_bytes())
    plan['jobs'].append({'id': 'FORBIDDEN_HISTORY', 'base': '.', 'script': 'dependencia_prohibida.py', 'args': []})
    plan_path.write_text(json.dumps(plan), encoding='utf8')
    forbidden_out = out / 'CERCA_NEGATIVA'
    forbidden_out.mkdir()
    bad = subprocess.run([sys.executable, '-I', '-B', str(runner), '--worker', '1', '--root', str(candidate),
                          '--out', str(forbidden_out)], capture_output=True, text=True, encoding='utf8', timeout=30)
    checks.append({'id': 'HISTORICAL_READ_REJECTED', 'ok': bad.returncode != 0 and 'PermissionError' in bad.stderr,
                   'exit_code': bad.returncode, 'stderr': bad.stderr})
    report = {'schema': 'APD04.delivery_tools.synthetic_test.N0.R01', 'checks': checks,
              'issues': [r for r in checks if not r['ok']], 'new_native_ticks': 0,
              'Word_created': False, 'ZIP_created': False, 'Full_updated': False,
              'system_source_modified': False, 'scope': 'SYNTHETIC INSTRUMENT TEST ONLY; no claim about E1 or actual scientific evidence.'}
    emit(out / 'COMPROBACION_HERRAMIENTAS_N0.json', report)
    if report['issues']:
        raise ValueError('Instrumental fixture failed; preserve it and correct a new revision')
    print(json.dumps({'checks': len(checks), 'issues': 0, 'report': str(out / 'COMPROBACION_HERRAMIENTAS_N0.json'), 'ZIP_created': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
