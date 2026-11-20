"""Try the closed GUI primary calculator inside the existing strict N0 fence.

Copies immutable evidence only, not executable Cognitive state. No scientific
selection is approved and no analysis ZIP, Native, GUI or Word is opened.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    root, out = a.root.resolve(strict=True), a.out.resolve()
    if out.exists() or not out.is_relative_to(HERE):
        raise ValueError('Fresh LAB diagnostic output required')
    sources = root / 'aplicacion/GENESIS/pruebas'
    component = sources / 'EXPORT_GUI_ESENCIAL_N0_R01'
    before = {p.relative_to(component).as_posix(): sha(p) for p in component.rglob('*') if p.is_file()}
    out.mkdir(parents=True)
    package = out / 'EVIDENCIA_Y_RECALCULO_SIN_ESTADOS'
    package.mkdir()
    shutil.copytree(component, package / 'EVIDENCIA_GUI')
    for name in ('recalcular_export_gui_portable_n0_r01.py', 'RESULTADO_PORTABLE_GUI_N0_R01.json'):
        shutil.copyfile(sources / name, package / name)
    runner = package / 'RECALCULO/recalcular_todo.py'
    runner.parent.mkdir()
    shutil.copyfile(HERE / 'recalcular_analisis_apd05_n0_r01.py', runner)
    job = {'id': 'GUI_CLOSED_PRIMARIES', 'base': '.',
           'script': 'recalcular_export_gui_portable_n0_r01.py',
           'script_sha256': sha(package / 'recalcular_export_gui_portable_n0_r01.py'),
           'args': ['--root', {'input': 'EVIDENCIA_GUI'}, '--out', '{output}'],
           'expected': 'RESULTADO_PORTABLE_GUI_N0_R01.json',
           'expected_sha256': sha(package / 'RESULTADO_PORTABLE_GUI_N0_R01.json'),
           'comparison': 'bytes', 'timeout_seconds': 120}
    emit(package / 'RECALCULO/PLAN_GLOBAL.json', {'jobs': [job]})
    members = [{'file': p.relative_to(package).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
               for p in sorted(package.rglob('*')) if p.is_file()]
    emit(package / 'MANIFIESTO_HASHES.json', {'members': members, 'excludes_own_hash': True})
    command = [sys.executable, '-I', '-B', str(runner), '--root', str(package), '--out', str(out / 'RECALCULO_CERCA_REAL')]
    run = subprocess.run(command, cwd=out, capture_output=True, text=True, encoding='utf8', timeout=150)
    unchanged = before == {p.relative_to(component).as_posix(): sha(p) for p in component.rglob('*') if p.is_file()}
    report = {'schema': 'APD05.GUI_closed_export.actual_fence.N0.R01',
              'command': command, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
              'source_manifest_sha256': before['MANIFIESTO.json'],
              'source_calculator_sha256': sha(sources / 'recalcular_export_gui_portable_n0_r01.py'),
              'source_golden_sha256': sha(sources / 'RESULTADO_PORTABLE_GUI_N0_R01.json'),
              'source_files_unchanged': unchanged, 'source_component_files': len(before),
              'new_native_ticks': 0, 'new_native_imports': 0,
              'Full_GUI_or_Word_executed': False,
              'scope': 'Archived exact GUI primaries recalculated by their portable CLI in the strict master fence; not an additional learning sample or another GUI execution.'}
    emit(out / 'PRUEBA_CERCA_GUI_N0.json', report)
    if run.returncode or not unchanged:
        raise ValueError('Closed component did not replay in the master fence')
    print(json.dumps({'archived_jobs': 1, 'matched_exact_bytes': True,
                      'source_files_unchanged': True, 'new_native_ticks': 0}))


if __name__ == '__main__':
    main()
