"""Independent read-only review of the final fixed counterflow cut and indexes."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p): return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}


def main():
    red = ROOT / 'resultados/red'; freeze = read(red / 'RED_SOURCE_FREEZE.json')
    source_checks = [{'path': x['path'], 'equal': sha(ROOT / x['path']) == x['sha256']} for x in freeze['files']]
    config_checks = [{'path': x['path'], 'equal': sha(ROOT / x['path']) == x['sha256']} for x in freeze['frozen_configurations']]
    owner = read(red / 'NETWORK_INDEX.json'); primary_checks = [
        {'path': x['path'], 'equal': sha(ROOT / x['path']) == x['sha256']} for x in owner['measurement_files']]
    assert all(x['equal'] for x in source_checks + config_checks + primary_checks)
    config = read(red / 'fixed_counterflow01/EXPERIMENT_CONFIG.json'); cases = []
    for c in config['cases']:
        p = red / 'fixed_counterflow01' / c['id'] / 'MEASUREMENTS.json'; x = read(p)
        cases.append({'id': c['id'], 'case': c, 'evidence': ref(p), 'utility': x['external_utility'],
            'profiles': x['profiles'], 'receipt_counts': {status: sum(r['status'] == status for r in x['receipts']) for status in {r['status'] for r in x['receipts']}},
            'manual_RAW_clock_edits': x['diagnostic_edits'],
            'native_meeting292': x['local_contexts']['meeting292'],
            'actual_meeting293': x['local_contexts']['meeting293']['center'],
            'actual_meeting294': next(r['regulation_samples']['meeting'] for r in x['trace'] if r['tick'] == 294)})
    continued_path = red / 'fixed_counterflow_continuation01/MEASUREMENTS.json'; continued = read(continued_path)
    panel = {r['tick']: r['samples'] for r in continued['trace']}
    restore_path = continued_path.with_name('RESTORE_CHECK.json')
    reading = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'READ_ONLY_SOURCE_AND_PRIMARY_EVIDENCE_REVIEW',
        'source_checks': source_checks, 'config_checks': config_checks, 'primary_hash_checks': primary_checks,
        'source_files_reconstructed_semantically': [ref(ROOT / p) for p in ('src/red/regulated_session.py',
            'src/red/regulated_habitat.py', 'src/red/regulated_curriculum.py', 'src/assemble_cut.py')],
        'counterflow_cases': cases,
        'continuation': {'evidence': ref(continued_path), 'initial': continued['initial'], 'final': continued['final'],
            'same_world_object': continued['same_world_object'], 'utility': continued['external_utility'],
            'profiles': continued['profiles'], 'new_input_count': len(continued['receipts']),
            'all_new_inputs_applied': all(x['status'] == 'applied' for x in continued['receipts']),
            'D594': panel[594]['D'], 'D661': panel[661]['D'], 'D728': panel[728]['D'],
            'B850': panel[850]['B'], 'B917': panel[917]['B'], 'passive_restore': read(restore_path)},
        'source_review': [
            'Both counterflow/sham interfaces are inert declared ports beforeT0. The counterflow input is a real zero-load+Z record scheduled at0for290 in every designated fixed-protocol arm.',
            'protocol(case) reads only explicit prepared experimental conditions. No decoded action, score, expected response or hidden evaluation state selects a participant response.',
            'External evaluation_only values occur in research allocation: after the first bounded candidate, the remaining six configurations are either run exactly as frozen or skipped. No score is passed to Runtime.',
            'Actual collision and disappearance are v27evolution. MAIN is never cleared/repaired; only the separate previously saved residual diagnostic deletes one RAW.',
            'The second episode submits21new fixed experience/environment events into the SAME437world and preserves its matter. The load0counterflow is supplied again at790, not claimed to regenerate autonomously.',
            'continued_external_episodes metadata records protocol provenance and progress; the field evolution and readout use native state, not this dictionary as a response table.',
            'assemble_cut is a post-trajectory writer/indexer, not imported by participants. Utilities and catalogs do not feed back into physical responses.',
            'The assembled NSM scope is explicitly local/sequential and does not promote registered expressions to mastered meanings.'
        ],
        'assembly_review': {'no_detected_central_response_substitution': True,
            'scope': 'Semantic code review, not an adversarial security proof or a new physical experiment.',
            'minor_recommendations': [
                'MENSAJES links the replay record; also linking MESSAGE_BRANCH_RECONSTRUCTION would make the exact reducer/DEMUX exclusion directly navigable.',
                'When displaying the repeated fixed regulator, retain the fact that a second zero-load experience packet is supplied at790. Do not call the circuit learned regulation or autonomous renewal.'
            ]},
        'closed_owner': ref(red / 'RED_CLOSURE.json'), 'coverage': ref(ROOT / 'resultados/auditor/FINAL_COVERAGE_INDEX.json'),
        'scientific_jobs_added': 0, 'simulator_imported_or_executed_by_this_review': False}
    target = ROOT / 'resultados/auditor/FINAL_RED_ASSEMBLY_REVIEW.json'
    target.write_text(json.dumps(reading, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'counterflow_cases_read': len(cases), 'closed_primary_hashes': len(primary_checks),
        'source_hashes': len(source_checks), 'same_world437_937': continued['same_world_object']}))


if __name__ == '__main__': main()
