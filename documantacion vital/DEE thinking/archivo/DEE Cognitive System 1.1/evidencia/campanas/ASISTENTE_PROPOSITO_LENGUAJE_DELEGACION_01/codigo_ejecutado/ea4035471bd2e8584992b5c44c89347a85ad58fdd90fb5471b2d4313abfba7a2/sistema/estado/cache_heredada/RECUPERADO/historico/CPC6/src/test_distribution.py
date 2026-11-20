"""Finite synthetic transport tests, not DEE experiments or scientific cases."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import package_cpc6 as package


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    checks = []; scratch = package.ROOT / '_distribution_tests'; scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='transport_', dir=scratch) as temp:
        root = Path(temp); destination = root / 'cases'; destination.mkdir()
        old_manifest = b'{"campaign":"CPC5","preserve":true}\n'; old_instructions = b'CPC5 original instructions\n'
        (destination / 'PARTES.json').write_bytes(old_manifest)
        (destination / 'INSTRUCCIONES_PARTES.txt').write_bytes(old_instructions)
        source = root / 'synthetic.candidate.zip'
        with zipfile.ZipFile(source, 'x', compression=zipfile.ZIP_STORED) as z:
            z.writestr('synthetic_payload.bin', bytes(range(256)) * (21 * 1024 * 1024 // 256))
        with zipfile.ZipFile(source) as z: assert z.testzip() is None
        report = package.split_transport(source, destination)
        assert len(report['parts']) == 2 and report['reconstruction_tested']
        metadata = destination / 'transporte_CPC6'
        assert (destination / 'PARTES.json').read_bytes() == old_manifest
        assert (destination / 'INSTRUCCIONES_PARTES.txt').read_bytes() == old_instructions
        assert report['parts_directory'] == '..'
        output = root / 'ACTUALLY_REASSEMBLED.zip'
        command = [sys.executable, '-I', '-B', str(metadata / 'REUNIR_CPC6.py'), '--carpeta', str(metadata), '--salida', str(output)]
        completed = subprocess.run(command, capture_output=True, timeout=60)
        assert completed.returncode == 0, completed.stderr
        assert package.sha(output) == package.sha(source) and output.stat().st_size == source.stat().st_size
        checks.append({'id': 'actual_two_part_reassembly', 'verified': True, 'source_bytes': source.stat().st_size,
            'source_sha256': package.sha(source), 'parts': report['parts'], 'argv': command,
            'stdout_utf8': completed.stdout.decode('utf-8', errors='replace'), 'exit_code': completed.returncode})
        again = subprocess.run(command, capture_output=True, timeout=60)
        assert again.returncode != 0 and package.sha(output) == package.sha(source)
        checks.append({'id': 'existing_output_protected', 'verified': True, 'exit_code': again.returncode,
                       'stderr_utf8': again.stderr.decode('utf-8', errors='replace')})
        first = destination / report['parts'][0]['name']
        with first.open('r+b') as stream: stream.write(b'X')
        corrupt_output = root / 'MUST_NOT_EXIST.zip'
        corrupt = subprocess.run(command[:-1] + [str(corrupt_output)], capture_output=True, timeout=60)
        assert corrupt.returncode != 0 and not corrupt_output.exists()
        checks.append({'id': 'corrupt_part_rejected_before_output', 'verified': True, 'exit_code': corrupt.returncode,
                       'stderr_utf8': corrupt.stderr.decode('utf-8', errors='replace')})
        checks.append({'id': 'existing_CPC5_sidecars_preserved', 'verified': True,
                       'PARTES_sha256': hashlib.sha256(old_manifest).hexdigest(),
                       'INSTRUCCIONES_sha256': hashlib.sha256(old_instructions).hexdigest()})
        for name in ('../escape', '/absolute', 'CPC6/../CPC5', 'CPC6\\escape', 'C:/escape'):
            try: package.safe_relative(name)
            except (AssertionError, ValueError): pass
            else: raise AssertionError('Unsafe archive member accepted: ' + name)
        checks.append({'id': 'unsafe_archive_paths_rejected', 'verified': True})
        small = root / 'small.bin'; small.write_bytes(b'controlled synthetic bytes')
        assert package.split_transport(small, destination)['split_required'] is False
        checks.append({'id': 'twenty_MiB_compressed_threshold', 'verified': True})
    result = {'schema': 'CPC6.distribution-tests.v1', 'verified': all(x['verified'] for x in checks),
        'source_sha256': package.sha(__file__), 'packager_sha256': package.sha(package.__file__), 'checks': checks,
        'scope': 'Synthetic finite engineering tests. No Runtime, no cognitive result, no canonical publication and no modification of historical artifacts.'}
    package.put(a.output, result); print(json.dumps({'verified': result['verified'], 'checks': len(checks)}))


if __name__ == '__main__': main()
