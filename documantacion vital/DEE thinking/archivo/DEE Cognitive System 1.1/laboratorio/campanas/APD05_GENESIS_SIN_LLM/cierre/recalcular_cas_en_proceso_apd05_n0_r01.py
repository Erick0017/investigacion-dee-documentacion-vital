"""CLI portátil CAS compatible con la cerca del recálculo maestro: sin subprocess.

Materializa dentro de la salida nueva del auditor y ejecuta sólo las CLIs
archivadas del plan fijo. No lee rutas originales ni llama al motor.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    package, output = args.package.resolve(), args.out.resolve()
    if output.exists() or output.is_relative_to(package):
        raise ValueError('Fresh proof outside the immutable CAS package required')
    helper = package / 'RESTAURAR_Y_RECALCULAR_CAS.py'
    spec = importlib.util.spec_from_file_location('apd05_cas_materialize_only', helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    work = output.parent / ('CAS_EXTRAIDO_' + output.stem)
    proof = module.materialize(package, work)
    plan = json.loads((work / 'RECALCULO/PLAN_GLOBAL.json').read_bytes())
    rows = []
    old_argv, old_path = sys.argv[:], sys.path[:]
    try:
        for number, job in enumerate(plan['jobs']):
            if job['base'] != '.' or job['comparison'] != 'bytes':
                raise ValueError('Unapproved CAS job shape')
            script = module.safe(work, job['script'])
            expected = module.safe(work, job['expected'])
            if sha(script) != job['script_sha256'] or sha(expected) != job['expected_sha256']:
                raise ValueError('Frozen CAS calculation identity differs')
            result = output.parent / (output.stem + '_' + str(number) + '_' + job['id'] + '.json')
            if result.exists():
                raise ValueError('No calculator output overwrite')
            argv = []
            for item in job['args']:
                if isinstance(item, dict) and set(item) == {'input'}:
                    argv.append(str(module.safe(work, item['input'])))
                elif item == '{output}':
                    argv.append(str(result))
                elif isinstance(item, str) and not Path(item).is_absolute():
                    argv.append(item)
                else:
                    raise ValueError('Forbidden literal or path')
            sys.argv = [str(script), *argv]
            sys.path = [str(script.parent), *old_path]
            runpy.run_path(str(script), run_name='__main__')
            if result.read_bytes() != expected.read_bytes():
                raise ValueError('Archived recalculation is not byte-identical: ' + job['id'])
            rows.append({'id': job['id'], 'script_sha256': sha(script),
                         'expected_sha256': sha(expected), 'actual_sha256': sha(result),
                         'comparison': 'bytes', 'matched': True})
    finally:
        sys.argv, sys.path = old_argv, old_path
    inventory = json.loads((work / 'MANIFIESTO_HASHES.json').read_bytes())
    for row in inventory['members']:
        if sha(module.safe(work, row['file'])) != row['sha256']:
            raise ValueError('Materialized evidence changed while calculating')
    stable = {'schema': 'APD05.CAS.portable_in_process_recalculation.N0.R01',
              **proof, 'jobs': rows, 'jobs_completed': len(rows),
              'all_selected_calculations_match_bytes': True,
              'source_CAS_manifest_sha256': sha(package / 'MANIFIESTO_CAS.json'),
              'external_processes_started': 0,
              'scope': 'Evidence re-materialization and archived calculations, not Native replay or Full use.'}
    with output.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(stable, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'jobs_completed': len(rows), 'restored_source_paths': proof['source_paths_restored'],
                      'new_native_ticks': 0, 'subprocesses': 0}))


if __name__ == '__main__':
    main()
