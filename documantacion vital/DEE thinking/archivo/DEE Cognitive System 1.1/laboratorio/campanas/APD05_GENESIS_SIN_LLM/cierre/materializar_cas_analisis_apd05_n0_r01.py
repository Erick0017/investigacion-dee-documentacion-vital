"""Materializa evidencia CAS exacta y verifica recálculos archivados, sin motor.

Las rutas históricas son localizadores/documentación. Ninguna se lee: todas las
entradas proceden de OBJETOS dentro de este paquete. No sirve para abrir vidas.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(base, name):
    value = Path(name)
    if value.is_absolute() or '..' in value.parts:
        raise ValueError('Absolute or traversing package member')
    target = (base / value).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError('Path escaped selected evidence')
    return target


def write_json(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def materialize(package, out):
    package, out = package.resolve(), out.resolve()
    if out.exists() or out.is_relative_to(package) or package.is_relative_to(out):
        raise ValueError('Choose a fresh directory disjoint from the CAS package')
    manifest = json.loads((package / 'MANIFIESTO_CAS.json').read_bytes())
    for row in manifest['members']:
        data = safe(package, row['file']).read_bytes()
        if len(data) != row['bytes'] or digest(data) != row['sha256']:
            raise ValueError('CAS package input differs: ' + row['file'])
    index = json.loads((package / 'RUTAS_Y_HASHES.json').read_bytes())
    out.mkdir(parents=True, exist_ok=False)
    checked, restored, count_bytes = set(), [], 0
    for row in index['sources']:
        data = safe(package, row['object']).read_bytes()
        if len(data) != row['bytes'] or digest(data) != row['sha256']:
            raise ValueError('CAS object differs: ' + row['object'])
        target = safe(out, row['source_original'])
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
        if digest(target.read_bytes()) != row['sha256']:
            raise ValueError('Materialized member differs')
        restored.append({'file': row['source_original'], 'bytes': row['bytes'], 'sha256': row['sha256']})
        count_bytes += row['bytes']
        checked.add(row['object'])
    plan = json.loads((package / 'PLAN_GLOBAL_CAS.json').read_bytes())
    runner = package / 'recalcular_todo_CONGELADO.py'
    destination = out / 'RECALCULO/recalcular_todo.py'
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(runner, destination)
    write_json(out / 'RECALCULO/PLAN_GLOBAL.json', plan)
    for rel in ('RECALCULO/recalcular_todo.py', 'RECALCULO/PLAN_GLOBAL.json'):
        data = safe(out, rel).read_bytes()
        restored.append({'file': rel, 'bytes': len(data), 'sha256': digest(data)})
    write_json(out / 'MANIFIESTO_HASHES.json', {'schema': 'APD05.materialized_exact_CAS.members.N0.R01', 'members': restored})
    proof = {'schema': 'APD05.CAS.materialization_proof.N0.R01',
             'source_paths_restored': len(index['sources']), 'unique_objects_verified': len(checked),
             'source_bytes_restored': count_bytes, 'all_source_bytes_exact': True,
             'original_historical_reads': 0, 'Native_runtime_imports': 0, 'new_Native_ticks': 0,
             'scope': 'Evidence tree only; RAW arrays are not continuable snapshots or actor memory.'}
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--recalculate', action='store_true')
    args = parser.parse_args()
    if args.proof.exists():
        raise ValueError('No proof overwrite')
    result = materialize(args.package, args.out)
    if args.recalculate:
        calc_out = args.out.parent / (args.out.name + '_RECALCULO')
        command = [sys.executable, '-I', '-B', str(args.out / 'RECALCULO/recalcular_todo.py'),
                   '--root', str(args.out), '--out', str(calc_out)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding='utf8', timeout=1800)
        result['archived_recalculation'] = {'command': command, 'exit_code': completed.returncode,
                                           'stdout': completed.stdout, 'stderr': completed.stderr,
                                           'new_Native_ticks': 0}
        if completed.returncode != 0:
            write_json(args.proof, result)
            raise ValueError('Portable archived calculation failed; originals remain intact')
        result['archived_result'] = json.loads((calc_out / 'RESULTADO_GLOBAL.json').read_bytes())
    write_json(args.proof, result)
    print(json.dumps({key: value for key, value in result.items() if key not in ('archived_recalculation', 'archived_result')}))


if __name__ == '__main__':
    main()
