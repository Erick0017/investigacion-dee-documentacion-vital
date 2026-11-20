"""Build and execute the independent consumer against this extracted C++ install.

Uses the delivered build45.ps1 compiler discovery, flags and Ninja configuration;
does not compile the library again or search an earlier product installation.
Run under clean45's owned process JobObject so descendants share its deadline.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

LEGACY_SOURCE_SHA = '6da09a24dbdf6fbb3b6736196e9eb3354295c8ea2d330491890446cde5987550'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def put(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(label, argv, directory, timeout):
    started = time.monotonic()
    try:
        result = subprocess.run([str(x) for x in argv], cwd=directory, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        (directory / (label + '.stdout.log')).write_bytes(exc.stdout or b'')
        (directory / (label + '.stderr.log')).write_bytes(exc.stderr or b'')
        put(directory / (label + '.COMMAND.json'), {'argv': [str(x) for x in argv], 'exit_code': None, 'status': 'TIMEOUT',
            'elapsed_seconds': time.monotonic() - started, 'timeout_seconds': timeout, 'direct_child_killed_and_waited_by_subprocess': True,
            'descendants_scope': 'Outer clean45 owned JobObject closes the complete worker tree on return'})
        raise
    (directory / (label + '.stdout.log')).write_bytes(result.stdout)
    (directory / (label + '.stderr.log')).write_bytes(result.stderr)
    put(directory / (label + '.COMMAND.json'), {'argv': [str(x) for x in argv], 'exit_code': result.returncode,
        'elapsed_seconds': time.monotonic() - started, 'timeout_seconds': timeout, 'waited': True})
    if result.returncode:
        raise RuntimeError(label + ' failed; see binary stdout/stderr logs')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(); output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    if output.is_relative_to(root):
        raise ValueError('Consumer build/output must be outside extracted product source')
    output.mkdir(parents=True, exist_ok=False)
    report = {'schema': 'DEE45.extracted-cpp-consumer.v1', 'status': 'FAILED'}
    try:
        source = root / 'validation/tests/external_consumer'
        library = root / 'install_cpp/lib/dee_thinking.lib'
        legacy_source = source / 'legacy40_consumer.cpp'
        legacy_original = root / 'source/examples/independent_consumer.cpp'
        needed = [source / 'CMakeLists.txt', source / 'main.cpp', legacy_source, legacy_original, library, root / 'tools/build45.ps1',
                  root / 'install_cpp/lib/cmake/dee_thinking/dee_thinkingConfig.cmake']
        if not all(path.is_file() for path in needed):
            raise ValueError('Missing independent consumer or installed C++ configuration')
        if sha(legacy_source) != LEGACY_SOURCE_SHA or sha(legacy_original) != LEGACY_SOURCE_SHA:
            raise ValueError('Historical independent consumer must remain byte-exact')
        powershell = Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
        build = output / 'build'
        run('BUILD', [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', root / 'tools/build45.ps1',
                      '-SourcePath', root / 'source', '-BuildRoot', build, '-ProductRoot', root, '-Stage', 'consumer',
                      '-ConsumerSource', source, '-PythonExecutable', sys.executable], output, 480)
        exe = build / 'consumer/dee45_external_consumer.exe'
        if not exe.is_file():
            raise ValueError('Independent consumer executable missing')
        execution = run('EXECUTE', [exe, output / 'native_states'], output, 180)
        text = execution.stdout.decode('utf-8-sig').strip()
        primary = json.loads(text)
        if primary.get('status') != 'PASS' or primary.get('version') != '4.5.0' or primary.get('kernel') != 27:
            raise AssertionError(('Consumer failed its finite public contract', primary))
        legacy_exe = build / 'consumer/legacy40_consumer.exe'
        if not legacy_exe.is_file():
            raise ValueError('Historical consumer executable missing')
        legacy_state = output / 'legacy40.deetsnap'
        legacy_execution = run('EXECUTE_LEGACY40', [legacy_exe, legacy_state], output, 180)
        legacy_text = legacy_execution.stdout.decode('utf-8-sig').strip()
        if not legacy_state.is_file() or 'response_s_reg=25' not in legacy_text or 'restored_future_exact=true control_distinct=true' not in legacy_text:
            raise AssertionError(('Historical consumer did not complete its published assertions', legacy_text))
        report.update({'status': 'VERIFIED', 'primary_stdout': primary, 'executable_sha256': sha(exe),
                       'legacy40_source_byte_exact': True, 'legacy40_source_sha256': LEGACY_SOURCE_SHA,
                       'legacy40_execution': {'exit_code': legacy_execution.returncode, 'stdout': legacy_text,
                           'executable_sha256': sha(legacy_exe), 'snapshot_sha256': sha(legacy_state), 'snapshot_bytes': legacy_state.stat().st_size},
                       'inputs': [{'path': str(p.relative_to(root)), 'sha256': sha(p)} for p in needed],
                       'installed_library_sha256': sha(library), 'build_provenance': json.loads((root / 'BUILD_consumer.json').read_text(encoding='utf-8-sig')),
                       'native_checkpoints': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted((output / 'native_states').glob('*.deetsnap'))],
                       'scope': 'Independent executable compiled from the exact extracted source and linked to that ZIP install_cpp via find_package(dee_thinking 4.5 CONFIG REQUIRED) / DEE::thinking.'})
    except BaseException as exc:
        report['error'] = repr(exc)
        put(output / 'CPP_CONSUMER_REPORT.json', report)
        raise
    put(output / 'CPP_CONSUMER_REPORT.json', report)
    print(json.dumps({'status': report['status'], 'output': str(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
