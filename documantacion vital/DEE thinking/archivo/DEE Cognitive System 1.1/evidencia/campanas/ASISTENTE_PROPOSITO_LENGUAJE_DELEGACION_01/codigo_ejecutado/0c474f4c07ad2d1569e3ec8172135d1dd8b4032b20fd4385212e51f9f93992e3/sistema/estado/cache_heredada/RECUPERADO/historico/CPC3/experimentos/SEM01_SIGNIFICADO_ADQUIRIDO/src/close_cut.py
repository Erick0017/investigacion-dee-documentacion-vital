"""External, idempotent evidence indices and pre-publication technical gates.

No scientific trajectory is executed and no result is returned to a MAIN.
The generated aggregate records point to their primary source and are not
counted again as experiments. This tool never publishes or deletes a ZIP.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def aggregate():
    indices = {}
    cohorts = ('confirmacion', 'causal_memory02', 'reversal01', 'reversal02_phase', 'repertorio4')
    for name in ('PREDICCIONES', 'EXPERIENCIAS'):
        target = ROOT / (name + '.jsonl')
        rows = []
        for cohort in cohorts:
            for path in sorted((ROOT / 'resultados' / cohort).rglob(name + '.jsonl')):
                for line, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                    if raw.strip():
                        rows.append({'primary_source': path.relative_to(ROOT).as_posix(),
                                     'primary_line': line, 'record_kind': 'INDEX_NOT_NEW_EXECUTION',
                                     'record': json.loads(raw)})
        target.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows), encoding='utf-8')
        indices[name] = {'records': len(rows), 'scope': list(cohorts)}
    dialogs = []
    for path in sorted((ROOT / 'resultados').rglob('TRANSCRIPCION.jsonl')):
        for line, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if raw.strip():
                dialogs.append({'primary_source': path.relative_to(ROOT).as_posix(), 'primary_line': line,
                                'record_kind': 'UI_OR_TECHNICAL_TRANSCRIPT_NOT_NEW_COHORT',
                                'record': json.loads(raw)})
    (ROOT / 'DIALOGOS.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in dialogs), encoding='utf-8')
    indices['DIALOGOS'] = {'records': len(dialogs), 'scope': 'Executed application and technical-continuation transcripts'}
    return indices


def provenance():
    historical = read('fuentes/PROVENANCE.json')
    immutable = []
    for row in historical['artifacts'][:4]:
        path = Path(row['path'])
        actual = sha(path)
        # The original CPC3 parent is intentionally replaced only after closure;
        # all other referenced originals remain immutable throughout.
        immutable.append({'path': str(path), 'original_sha256': row['sha256'],
                          'current_sha256': actual, 'unchanged_at_closure': actual == row['sha256']})
    wheel = ROOT / 'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    kernel = ROOT / 'fuentes/producto4/source/src/kernel_v27.cpp'
    return {'schema': 1, 'project': 'DEE Universe / INVESTIGACION DEE',
            'project_author': 'Ivan Erick Tlaltecatl Morales',
            'campaign': 'CPC3 SEM01 SIGNIFICADO_ADQUIRIDO', 'instrument': 'DEE thinking4.0.0',
            'kernel': 27, 'wheel_path': wheel.relative_to(ROOT).as_posix(), 'wheel_sha256': sha(wheel),
            'native_sha256': '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066',
            'kernel_source_path': kernel.relative_to(ROOT).as_posix(), 'kernel_source_sha256': sha(kernel),
            'parent_sha256': '75ab357f41f6214c1798efbf69bd0708ab891038d30d770fdfe4a379208f793e',
            'parent_members': 1563, 'inherited_root': 'CPC3/',
            'addition': 'CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/',
            'sources_index': 'fuentes/PROVENANCE.json', 'source_recovery': 'Directed passive extraction; historical runners not executed',
            'source_classes': {'published4': 'Native Runtime/OrganizationalWorld/input contracts/persistence/finite component reference',
                               'historical': 'CORE06/07, I01 R04/R14, I02, ProcessingNative and OBP sources as mechanism maps',
                               'new_research': 'src/memory.py, habitat.py and the frozen SEM01 protocol; not new product APIs'},
            'immutable_originals_at_prepublication': immutable,
            'budget_record': 'BUDGET.json', 'no_budget_reset': True,
            'interpretation': 'Names/utility/absence classification external; acquired directions and native environmental action from v27'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--require-clean-proof', action='store_true')
    a = p.parse_args()
    config = read('configuraciones/EXPERIMENT_CONFIG.json')
    assert sha(ROOT / 'configuraciones/EXPERIMENT_CONFIG.json') == '79719abf24a2d1abf93ec428609b136c9bbe1d013326fec274e7b7103a496576'
    assert all(sha(ROOT / path) == value for path, value in config['source_hashes'].items())
    core = read('resultados/CONFIRMATORY_SUMMARY.json')
    assert len(core['rows']) == 14 and all(x['status'] == 'MEASURED' for x in core['rows'])
    assert all((ROOT / 'resultados/confirmacion' / x['id'] / 'MAIN_FINAL.deetsnap').is_file() for x in config['cases'])
    jobs = [(p, json.loads(p.read_text(encoding='utf-8'))) for p in sorted((ROOT / 'jobs').glob('*/job.json'))]
    active = [p.relative_to(ROOT).as_posix() for p, row in jobs if row['status'] == 'RUNNING']
    # This auditor may itself be supervised by a live closure job. The caller
    # must invoke it after workers stop, not as a native scientific worker.
    assert not active, active
    required = ['ejecutar.py', 'demostracion.py', 'src/app_worker.py', 'src/package_append.py',
                'src/verify_append.py', 'INFORME.md', 'LEEME.md', 'GUIA_DEMOSTRACION.md',
                'resultados/reversal02_phase/SCOPE_AND_ADMISSION.json',
                'resultados/repertorio4/RESTORE_TECHNICAL.json']
    assert all((ROOT / path).is_file() for path in required)
    proof = ROOT / 'resultados/reproduccion_limpia/RESULTS.json'
    if a.require_clean_proof:
        assert proof.is_file() and read(proof.relative_to(ROOT))['completed']
    indices = aggregate()
    prov = provenance()
    assert prov['wheel_sha256'] == '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
    assert prov['kernel_source_sha256'] == 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    assert all(row['unchanged_at_closure'] for row in prov['immutable_originals_at_prepublication'])
    put(ROOT / 'PROVENANCE.json', prov)
    capabilities = {
        'schema': 1, 'instrument': 'DEE thinking4.0.0/v27 frozen', 'project_author': 'Ivan Erick Tlaltecatl Morales',
        'criteria_are_measurements_not_global_cognitive_verdict': True,
        'core': {'evidence': 'resultados/CONFIRMATORY_SUMMARY.json', 'case_records': 14,
                 'query_slots': 28, 'admitted_queries': 26, 'rejected_queries': 2,
                 'matched_histories': core['paired_main'], 'frozen_reserves': core['reserved'],
                 'native_correspondence': 'A:S1U,S2V; B:S1V,S2U, with fixed same physical input/decoder',
                 'native_anticipation_ticks': [87, 115], 'later_event_input_ticks': [88, 116],
                 'functional_read_ticks': [101, 129], 'utility_matched': [5, 5],
                 'utility_always_protect_or_no_action': 4,
                 'fixed_action_utility_coupling_independently_learned': False},
        'modalities': {'acquired_relation_and_action': 'NATIVE_EVOLUTION',
                       'signal_and_current_outcome_packets': 'EXPERIENCE_PROTOCOL',
                       'present_delivery_absence_classification': 'EXTERNAL_FIXED_TRANSDUCER',
                       'counterfactual_cuts_rescue': 'DIAGNOSTIC_FORK',
                       'observer_metrics_and_graph': 'PASSIVE_EXTERNAL_AUDITOR',
                       'words': 'EXTERNAL_TEXT_TO_FIXED_SIGNAL_ID_AND_FIXED_OUTPUT_RENDERING'},
        'causal_panel': {'evidence': 'resultados/causal_memory02/SUMMARY.json',
                         'diagnostic_branches': 3, 'fresh_memory_only_reserved': 2,
                         'selective_memory_cut': 'S1 unresolved and U benefit lost; S2 V and direct actuator preserved',
                         'admission_limit': 'signals_only core and report-omission reversal have rejected queries; not forgetting controls'},
        'deep_extensions': [
            {'id': 'REVISION', 'evidence': 'resultados/reversal02_phase/SCOPE_AND_ADMISSION.json',
             'continuations': 5, 'parent_tick': 129, 'final_tick': 330,
             'later_expression': ['V', 'U'], 'actual_new_sensor_classes': ['V', 'U', 'V', 'U'],
             'earlier_phase_sensor_classes': ['V', 'V', 'V', 'V'],
             'continuous_microcarrier_overwrite_established': False,
             'incremental_utility_after_revision_established': False},
            {'id': 'FOUR_SIGNAL_REPERTOIRE', 'evidence': 'resultados/repertorio4/MECHANISM_REVIEW.json',
             'fresh_cohorts': 4, 'N': 67, 'larger_inventory_than_core': True,
             'paired_assignments': [['U', 'U', 'V', 'V'], ['U', 'V', 'U', 'V']],
             'paired_plus_reserve_resolved_slots': 12, 'unpaired_resolved_slots': 0,
             'all_query_slots': 16, 'all_query_slots_admitted': 16, 'all_requests_applied': 192,
             'final_tick': 252}],
        'communication': {'grammar': 'README_GRAMATICA.md', 'demonstration': 'demostracion.py',
                          'transcripts': 'DIALOGOS.jsonl', 'snapshot_metadata': 'Strict neutral phase/slots/aliases only',
                          'finite_protocol_not_unlimited': True,
                          'revision_command': 'revisar V U: principal MAIN129 to284, physical queries285/313, final330',
                          'revision_technical_evidence': 'resultados/UI_REVISION_QUALIFICATION/RESULTS.json'},
        'reuse': ['Installed native Runtime v27', 'OrganizationalWorld interfaces and operational snapshots',
                  'Mobile directional acquisition and toroidal return', 'Native reducer encounters and fixed environmental consequence paths'],
        'not_evaluated_in_this_cut': ['Flexible consequence devaluation', 'New acquired composition',
                                      'Information selection extension', 'Learned U-to-word emission', 'Renewable unrestricted conversation'],
        'primary_indices': indices,
        'technical_checks': ['resultados/technical_checks01/', 'resultados/UI_TECHNICAL02/RESULTS_REVIEWED.json',
                             'resultados/UI_LOADER_CLOSURE/', 'resultados/UI_QUEUE_HOLE_WITNESS/',
                             'resultados/UI_REVISION_QUALIFICATION/RESULTS.json'],
        'clean_extraction_proof': 'resultados/reproduccion_limpia/RESULTS.json' if proof.exists() else 'PENDING_CANDIDATE_PROOF',
        'closure': 'Finite frozen cases and two bounded deep extensions completed; adverse trajectories and technical attempts preserved'}
    put(ROOT / 'CAPACIDADES.json', capabilities)
    summary = {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
               'frozen_source_hashes_intact': True, 'configuration_sha256': sha(ROOT / 'configuraciones/EXPERIMENT_CONFIG.json'),
               'scientific_completed_cohorts_by_stratum': {'core': 14, 'selective_diagnostic_forks': 3,
                                                          'fresh_memory_only_reserves': 2, 'reversal_continuations': 5, 'repertoire4': 4},
               'technical_jobs_recorded': len(jobs),
               'technical_job_errors_preserved': [p.relative_to(ROOT).as_posix() for p, row in jobs if row.get('exit_code') not in (0, None)],
               'native_workers_running_at_closure': active, 'indices': indices,
               'clean_candidate_proof_available': proof.exists(), 'required_files_present': required,
               'immutable_provenance': 'PROVENANCE.json', 'final_zip_sha256_is_external': True}
    put(ROOT / 'resultados/CLOSURE_TECHNICAL.json', summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
