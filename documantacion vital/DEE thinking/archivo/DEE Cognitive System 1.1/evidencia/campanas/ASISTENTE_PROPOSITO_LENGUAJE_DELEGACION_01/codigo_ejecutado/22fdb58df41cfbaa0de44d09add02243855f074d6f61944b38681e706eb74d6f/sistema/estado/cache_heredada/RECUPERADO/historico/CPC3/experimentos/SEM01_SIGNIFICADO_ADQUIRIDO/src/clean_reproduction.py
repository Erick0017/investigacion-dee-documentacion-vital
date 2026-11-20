"""Clean extracted-package proof. Evaluation occurs only AFTER new evolution.

This is an external technical auditor, never the participant or its decoder.
It creates no product, edits no fixture and does not reuse terminal outputs as
answers. Subprocesses are bounded by the campaign's immutable supervisor.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha
from supervise import run


def bounded(name, argv, cwd, timeout=240):
    row = run(ROOT, name, [str(x) for x in argv], timeout, str(cwd))
    if row['exit_code'] != 0:
        raise RuntimeError('Preserved failed clean-proof job: ' + name)
    return row


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--base-python', required=True, type=Path)
    p.add_argument('--output', type=Path, default=ROOT / 'resultados/reproduccion_limpia')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    temp = Path(tempfile.mkdtemp(prefix='sem01proof_'))
    state = {'candidate_sha256': sha(a.candidate), 'temporary_root': str(temp),
             'scope': 'Technical replays; not independent scientific cohorts', 'jobs': []}
    put(a.output / 'PLAN.json', state)
    with zipfile.ZipFile(a.candidate) as z:
        assert z.testzip() is None
        for name in z.namelist():
            q = PurePosixPath(name)
            if q.is_absolute() or '..' in q.parts or ':' in name:
                raise ValueError('Unsafe extraction member: ' + name)
        z.extractall(temp / 'extracted')
    section = temp / 'extracted/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO'
    wheel = section / 'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    python = temp / 'venv/Scripts/python.exe'
    state['jobs'].append(bounded('clean_venv01', [a.base_python, '-I', '-m', 'venv', temp / 'venv'], temp))
    state['jobs'].append(bounded('clean_install01', [python, '-I', '-m', 'pip', 'install', '--no-index', '--no-deps', wheel], temp))
    reproduced = temp / 'new_complete_case'
    state['jobs'].append(bounded('clean_complete_case01', [python, '-I', '-B', section / 'ejecutar.py',
        '--child', section / 'configuraciones/casos/A_future_UV.json', '--output', reproduced,
        '--wheel', wheel], temp))
    # Only now open the historical reference for comparison.
    actual = json.loads((reproduced / 'MEASUREMENTS.json').read_text(encoding='utf-8'))
    expected = json.loads((section / 'resultados/confirmacion/A_future_UV/MEASUREMENTS.json').read_text(encoding='utf-8'))
    checks = {'initial_full_raw_clock_tick': actual['initial'] == expected['initial'],
              'final_full_raw_clock_tick': actual['final'] == expected['final'],
              'teaching_and_actual_receipts': actual['teaching'] == expected['teaching'],
              'uses_emissions_profiles_receipts': actual['uses'] == expected['uses'],
              'installed_official_version': actual['identity']['version'] == '4.0.0',
              'installed_official_wheel': actual['identity']['wheel_sha256'] == '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623',
              'native_site_packages_in_clean_venv': Path(actual['identity']['module']).is_relative_to(temp / 'venv'),
              'no_hidden_old_imports': not actual['identity']['hidden_old_implementation_imports']}
    put(a.output / 'COMPLETE_CASE_CHECKS.json', checks)
    if not all(checks.values()):
        raise AssertionError(checks)
    # The public UI creates, teaches, queries, saves/loads, observes and continues.
    # Its query worker sees only the physical snapshot, S1/S2 and neutral cursor.
    session = temp / 'public_demo'
    state['jobs'].append(bounded('clean_public_demo01', [python, '-I', '-B', section / 'demostracion.py',
        '--python', python, '--eventos', section / 'configuraciones/DEMO_A.txt', '--directorio', session], temp))
    # Exercise new-process restoration from the first already-emitted MAIN.
    resumed = temp / 'restored_public_session'
    resumed.mkdir()
    events = a.output / 'CONTINUE_AFTER_EMISSION.txt'
    events.write_text('revelar U\nseñal pako\nrevelar V\nobserva\nsalir\n', encoding='utf-8')
    state['jobs'].append(bounded('clean_public_restore01', [python, '-I', '-B', section / 'demostracion.py',
        '--python', python, '--cargar', session / 'EMISION1.deetsnap', '--eventos', events,
        '--directorio', resumed], temp))
    def results(folder):
        return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(folder.glob('llamada_*/RESULT.json'))]
    main = results(session)
    more = results(resumed)
    emissions = [r['query'] for r in main if 'query' in r]
    restored = [r['query'] for r in more if 'query' in r]
    ui_checks = {'all_operations_completed': all(r['completed'] for r in main + more),
                 'first_and_second_admitted': all(q['receipt']['status'] == 'applied' for q in emissions),
                 'native_classes_U_V': [q['emission']['anticipated_class'] for q in emissions] == ['U', 'V'],
                 'new_query_after_restoration_V': len(restored) == 1 and restored[0]['emission']['anticipated_class'] == 'V',
                 'restored_emission_equals_continued': restored == emissions[1:],
                 'final_tick129_both': main[-1]['after']['tick'] == more[-1]['after']['tick'] == 129}
    put(a.output / 'PUBLIC_RESTORE_CHECKS.json', ui_checks)
    if not all(ui_checks.values()):
        raise AssertionError(ui_checks)
    revised = temp / 'public_revision'
    state['jobs'].append(bounded('clean_public_revision01', [python, '-I', '-B', section / 'demostracion.py',
        '--python', python, '--cargar', session / 'MAIN_FINAL.deetsnap',
        '--eventos', section / 'configuraciones/DEMO_REVISION_CONTINUAR.txt', '--directorio', revised], temp))
    revision_results = results(revised)
    revised_queries = [r for r in revision_results if 'query' in r]
    revision_expected = json.loads((section / 'resultados/reversal02_phase/FULL_REVERSE/MEASUREMENTS.json').read_text(encoding='utf-8'))
    revision_checks = {'all_operations_completed': all(r['completed'] for r in revision_results),
                       'new_query_classes_V_U': [r['query']['emission']['anticipated_class'] for r in revised_queries] == ['V', 'U'],
                       'both_queries_admitted': len(revised_queries) == 2 and all(r['query_admitted'] for r in revised_queries),
                       'same_lineage_final330_physics': revision_results[-1]['after']['physical_digest'] == revision_expected['final'],
                       'no_generator_import_in_queries': all(not any(x in r['query_isolation']['imported_local_modules'] for x in ('src.experiment', 'src.app_revision')) for r in revised_queries)}
    put(a.output / 'PUBLIC_REVISION_CHECKS.json', revision_checks)
    if not all(revision_checks.values()):
        raise AssertionError(revision_checks)
    # Copy only evidence, never the new venv or complete extracted parent.
    import shutil
    for name in ('MEASUREMENTS.json', 'MAIN_T0.deetsnap', 'MAIN_FINAL.deetsnap'):
        shutil.copyfile(reproduced / name, a.output / name)
    for label, folder in [('PUBLIC_DEMO', session), ('PUBLIC_RESTORED', resumed), ('PUBLIC_REVISION', revised)]:
        shutil.copytree(folder, a.output / label, ignore=shutil.ignore_patterns('SOURCE_VERSIONS'))
    payload = {}
    for path in section.rglob('*'):
        rel = path.relative_to(section)
        if path.is_file() and (rel.parts[0] in ('src', 'runtime', 'configuraciones') or rel.as_posix() in ('ejecutar.py', 'demostracion.py', 'supervise.py')) and '__pycache__' not in rel.parts:
            payload[rel.as_posix()] = sha(path)
    state.update(complete_case_checks=checks, public_restore_checks=ui_checks, public_revision_checks=revision_checks,
                 executed_payload_sha256=payload, completed=True,
                 physical_final=actual['final'], clean_install_identity=actual['identity'],
                 actual_case_measurement_sha256=sha(reproduced / 'MEASUREMENTS.json'),
                 source_reference_access='Reference JSON opened only after the complete new trajectory',
                 input_fixture_is_a_recipe_not_terminal_response=True)
    put(a.output / 'RESULTS.json', state)
    print('CLEAN_INSTALL_FULL_NEW_TRAJECTORY_AND_PUBLIC_RESTORE_VERIFIED')


if __name__ == '__main__':
    main()
