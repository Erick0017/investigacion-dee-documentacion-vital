"""Read-only source runtime and synthetic logistics checks; no updater run."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    out = args.out.resolve()
    if out.exists() or not out.is_relative_to(HERE):
        raise ValueError('Fresh test folder inside the proposal required')
    out.mkdir(parents=True)
    updater = load('apd05_proposed_updater_read_only', 'actualizar.py')
    opener = load('apd05_proposed_opener_read_only', 'arrancar.py')
    for name in ('actualizar.py', 'arrancar.py', Path(__file__).name):
        ast.parse((HERE / name).read_text(encoding='utf8'))
    checks = [{'id': 'AST_ONLY', 'ok': True}]
    runtime = source / 'motor/python313'
    files = [path for path in runtime.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    before = {path.relative_to(source).as_posix(): sha(path) for path in files}
    # Collect the exact selected bytes in memory; Build.add/finish are not run.
    collector = object.__new__(updater.Build)
    collector.source = source
    collected = {}
    def add(name, value, origin=None, source_digest=None):
        if name in collected and collected[name]['sha256'] != hashlib.sha256(value).hexdigest():
            raise ValueError('Duplicate collected target differs')
        collected[name] = {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest(), 'origin': origin}
    def copy(path, name, origin=None):
        add(name, updater.source_bytes(path), origin or str(path.relative_to(source)))
    def emit(name, value, origin=None):
        add(name, updater.encoded(value), origin)
    collector.add, collector.copy, collector.json = add, copy, emit
    started = time.monotonic()
    collector.prepared_runtime313()
    checks.append({'id': 'SOURCE_PREPARED_RUNTIME_EXACT_WHEEL_MEMBERS', 'ok': True,
                   'selected_members': len(collected), 'bytes': sum(x['bytes'] for x in collected.values()),
                   'wall_seconds': time.monotonic() - started})
    opener.ROOT = source
    opener.WHEEL = source / 'sistema/runtime' / updater.WHEEL_NAME
    ready = opener.verify_prepared_runtime()
    checks.append({'id': 'READ_ONLY_STARTUP_VERIFICATION_SOURCE', 'ok': ready['startup_writes'] == 0,
                   'result': ready})
    # An incomplete extracted runtime must fail, not install or make directories.
    absent = out / 'MISSING_RUNTIME_NO_INSTALL'
    opener.ROOT = absent
    try:
        opener.verify_prepared_runtime()
    except RuntimeError as error:
        checks.append({'id': 'MISSING_MARKER_FAILS_WITHOUT_INSTALLATION', 'ok': not absent.exists(),
                       'error': str(error)})
    else:
        raise ValueError('Missing runtime wrongly accepted')
    # A staged managed library uses the normal transactional conflict rule.
    fake = out / 'SYNTHETIC_COLLABORATION_NO_DEE'
    fake.mkdir()
    updater.ROOT = fake
    updater.OWNER = fake / 'actualizaciones/ARCHIVOS_GESTIONADOS.json'
    personal = fake / 'trabajo_personal/user.txt'
    personal.parent.mkdir()
    personal.write_text('Personal experiment must remain byte-identical.', encoding='utf8')
    target = fake / 'motor/python313/site-packages/fixture.py'
    target.parent.mkdir(parents=True)
    target.write_bytes(b'original_local\n')
    build = updater.Build(source)
    build.release = 'SYNTHETIC_NO_SOURCE_UPDATE'
    build.add('motor/python313/site-packages/fixture.py', b'original_local\n', 'fixture_same')
    checks.append({'id': 'EXACT_UNMANAGED_PREPARED_BYTES_ADOPTED_WITHOUT_REWRITE',
                   'ok': not build.staged and target.read_bytes() == b'original_local\n'})
    try:
        build.add('motor/python313/site-packages/fixture.py', b'new_upstream\n', 'fixture_changed')
    except RuntimeError:
        checks.append({'id': 'UNMANAGED_LOCAL_LIBRARY_CHANGE_CONFLICT_PRESERVED',
                       'ok': target.read_bytes() == b'original_local\n'})
    else:
        raise ValueError('An unmanaged local modification was overwritten')
    try:
        build.add('trabajo_personal/user.txt', b'overwrite', 'FORBIDDEN')
    except ValueError:
        checks.append({'id': 'PERSONAL_TREE_STILL_PROTECTED',
                       'ok': personal.read_text(encoding='utf8') == 'Personal experiment must remain byte-identical.'})
    else:
        raise ValueError('Personal directory accepted as managed')
    after = {path.relative_to(source).as_posix(): sha(path) for path in files}
    checks.append({'id': 'SOURCE_RUNTIME_UNCHANGED', 'ok': before == after,
                   'source_files_compared': len(before)})
    report = {'schema': 'APD05.logistics_prepared_runtime.N0.tests.R01',
              'checks': checks, 'issues': [row for row in checks if not row['ok']],
              'runtime_export_selection': collected,
              'proposed_updater_sha256': sha(HERE / 'actualizar.py'),
              'proposed_opener_sha256': sha(HERE / 'arrancar.py'),
              'source_updater_executed': False, 'Full_created_or_updated': False,
              'Word_created': False, 'Native_imports': 0, 'new_native_ticks': 0,
              'scope': 'Real source bytes checked read-only plus explicitly synthetic transaction conflicts; not an operative Full or GUI proof.'}
    with (out / 'PRUEBA_PROPUESTA_N0.json').open('x', encoding='utf8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')
    if report['issues']:
        raise ValueError('Proposal tests failed; preserve and diagnose')
    print(json.dumps({'checks': len(checks), 'issues': 0, 'selected_files': len(collected),
                      'Full_updated': False, 'new_native_ticks': 0}))


if __name__ == '__main__':
    main()
