"""Verifica CAS con el ejecutor maestro real, sin Native ni creación de ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', type=Path, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--cas', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    args = parser.parse_args()
    assert not args.proof.exists()
    source = args.lab / 'cierre'
    task = Path(tempfile.mkdtemp(prefix='apd04_cas_fence_n0_'))
    package = task / 'paquete'
    package.mkdir()
    shutil.copytree(args.cas, package / 'EVIDENCIA_CAS')
    shutil.copyfile(source / 'recalcular_cas_en_proceso_apd04_n0_r01.py', package / 'recalcular_CAS.py')
    shutil.copyfile(args.reference, package / 'REFERENCIA_CAS.json')
    (package / 'RECALCULO').mkdir()
    shutil.copyfile(source / 'recalcular_analisis_apd04_n0_r01.py', package / 'RECALCULO/recalcular_todo.py')
    dump(package / 'RECALCULO/PLAN_GLOBAL.json', {'jobs': [{'id': 'CAS_BYTE_EXACT_AND_ARCHIVED_CLIS',
         'base': '.', 'script': 'recalcular_CAS.py', 'script_sha256': sha(package / 'recalcular_CAS.py'),
         'args': ['--package', {'input': 'EVIDENCIA_CAS'}, '--out', '{output}'],
         'expected': 'REFERENCIA_CAS.json', 'expected_sha256': sha(package / 'REFERENCIA_CAS.json'),
         'comparison': 'bytes', 'timeout_seconds': 900}]})
    members = [{'file': path.relative_to(package).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)}
               for path in sorted(package.rglob('*')) if path.is_file()]
    dump(package / 'MANIFIESTO_HASHES.json', {'members': members})
    proof_out = task / 'salida_cerca'
    run = subprocess.run([sys.executable, '-I', '-B', str(package / 'RECALCULO/recalcular_todo.py'),
                          '--root', str(package), '--out', str(proof_out)],
                         capture_output=True, text=True, encoding='utf8', timeout=1200)
    result = {'schema': 'APD04.CAS.actual_master_fence_proof.N0.R02', 'temporary': str(task),
              'new_native_ticks': 0, 'created_zip_count': 0, 'source_components_changed': False,
              'input_cas': str(args.cas), 'input_manifest_sha256': sha(args.cas / 'MANIFIESTO_CAS.json'),
              'actual_fenced_master': {'returncode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr},
              'reference_sha256': sha(package / 'REFERENCIA_CAS.json'),
              'portable_CAS_reference': json.loads((package / 'REFERENCIA_CAS.json').read_bytes())}
    if run.returncode == 0:
        result['master_result'] = json.loads((proof_out / 'RESULTADO_GLOBAL.json').read_bytes())
    dump(args.proof, result)
    if run.returncode != 0:
        raise ValueError('CAS failed real master fence; source evidence preserved')
    print(json.dumps({'source_paths': result['portable_CAS_reference']['source_paths_restored'],
                      'archived_CLIs': result['portable_CAS_reference']['jobs_completed'],
                      'fenced_master_jobs': result['master_result']['jobs_completed'],
                      'reference_sha256': result['reference_sha256'], 'new_native_ticks': 0}))


if __name__ == '__main__':
    main()
