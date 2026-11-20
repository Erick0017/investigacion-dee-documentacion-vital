"""Compact index of auditor-owned evidence, without repeating any simulation."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / 'resultados/auditor'


def main():
    def load(p): return json.loads((OUT / p).read_text(encoding='utf-8'))
    names = ['SOURCE_REVIEW.json', 'R14_PUBLIC_COMPONENT/RUN_SUMMARY.json',
        'ABCD_WINDOW160_161_V2/TECHNICAL_CHECKS.json', 'ABCD_WINDOW93_94/TECHNICAL_CHECKS.json',
        'TECHNICAL_HOTFIX_AND_BYTE_DIFF.json', 'NONTRIVIAL_FORK_ISOLATION.json',
        'D_SOCIAL_CONTEXT93_94.json', 'INHERITED_REFERENCE148_149/MEASUREMENTS.json',
        'INHERITED_REFERENCE_OP_DIFF.json', 'PAIRING_SCOPE_REVIEW.json',
        'REGULATION_RETENTION_REVIEW.json', 'REGULATION_LOCAL_GATES.json',
        'SUSCEPTIBILITY_PILOT/RUN_SUMMARY.json', 'SUSCEPTIBILITY_PILOT/SHAM_FOLLOWUP_RESULT.json',
        'NATIVE_PREEMPTION_PILOT/RUN_SUMMARY.json', 'NATIVE_PREEMPTION_RECONSTRUCTION.json',
        'NETWORK_V3_SCOPE_REVIEW.json', 'LANGUAGE_CONTINUITY_REVIEW.json',
        'V3_MESSAGE_RECONSTRUCTION/MESSAGE_RECONSTRUCTION.json',
        'V3_MESSAGE_RECONSTRUCTION/MESSAGE_BRANCH_RECONSTRUCTION.json']
    references = [{'path': (OUT / x).relative_to(ROOT).as_posix(),
        'sha256': hashlib.sha256((OUT / x).read_bytes()).hexdigest()} for x in names]
    replay = load('V3_MESSAGE_RECONSTRUCTION/MESSAGE_RECONSTRUCTION.json')
    language = load('LANGUAGE_CONTINUITY_REVIEW.json')
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'EXTERNAL_AUDIT_INDEX_NO_NEW_PHYSICAL_CASE',
        'evidence': references,
        'auditor_owned_scientific_preparations': {'fresh': 9,
            'decomposition': [{'family': 'R14_PUBLIC_COMPONENT', 'fresh': 5, 'explicit_diagnostic_forks': 1, 'max_tick': 14},
                {'family': 'SUSCEPTIBILITY_PILOT', 'fresh': 0, 'full_operative_T520_forks': 4,
                 'conditional_exploratory_T520_sham_fork': 1, 'ticks_per_fork': 5},
                {'family': 'NATIVE_PREEMPTION_PILOT', 'fresh': 4, 'forks': 0, 'max_tick': 525}],
            'scope': 'Do not add read-only references, ticks or technical continuations to this fresh count. Root-owned DUAL/network/lexical worlds are only referenced here.'},
        'technical_continuations_separate': {
            'successful_new_network_window_continuations': 8,
            'continued_before_old_container_assert_failed': 4,
            'nontrivial_RAW_only_fork_isolation_without_advance': 2,
            'inherited_reference_replay_ticks': 1,
            'message_replay_trajectories': 1, 'message_replay_ticks': replay['replayed_native_ticks'],
            'message_replay_source': 'Historical confirmed FULL_U/T70, no new preparation or intervention',
            'not_independent_scientific_replicates': True},
        'reviewed_other_owned_cases_not_new_by_auditor': {
            'continuous_language_saved_cases': len(language['cases']),
            'continuous_language_fresh_reserved_worlds': sum(x.get('new_preparation', False) for x in language['cases']),
            'continuous_language_existing1431_genealogy_continuations': sum(not x.get('new_preparation', True) for x in language['cases']),
            'DUAL_confirmation_worlds': 8,
            'scope': 'References to those owners primary evidence; never added again as auditor-created worlds.'},
        'mechanisms_and_limits': [
            'Relative histories retain under common drift; absent reader is not absent relation; rejected400 input is not forgetting.',
            'Equal upstream Applied exposures produce different native local effects by history, with no A/B rewrite in517-525.',
            'R14 is a finite prepared retainP/switchQ component, not acquired arbitrary utility or integration into ABCD.',
            'V3 message replay certifies eight directed segments and seven local reducer encounters, not counterfactual necessity or all earlier ancestry.',
            'Continuous lexical forms are two acquired task-relative F7/R3 mappings, externally transduced, with finite probes and local admission differences.',
            'No hidden native policy, timeout-as-absence, RAW/clock repair or expected-answer table introduced by these auditor tools.'],
        'closed_reason': 'Assigned finite cohorts, local reconstruction, read-only scope reviews and technical windows complete; no new search pending.'}
    (OUT / 'CLOSURE_INDEX.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'indexed_reports': len(references), 'auditor_owned_fresh': 9, 'status': 'SAVED'}))


if __name__ == '__main__': main()
