"""Reconcile saved primary records; never import/run the simulator or owners.

A record is keyed by its unique primary path. Summaries, snapshots, ticks,
mirrored tables and demonstration transcripts are not new scientific replicas.
Unknown future groups remain pending until their owner provides a closed index.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path): return path.relative_to(ROOT).as_posix()


def classify(path, data):
    parts = path.relative_to(ROOT / 'resultados').parts
    area = parts[0]; family = '/'.join(parts[:2]); case = data.get('case') or {}
    diagnostic = bool(data.get('diagnostic_edits') or data.get('diagnostic_control'))
    if area == 'red':
        if parts[1] in ('discovery01', 'roles_discovery01', 'confirmacion02', 'v3_discovery01',
                        'confirmacion03', 'selective_negative01', 'dual_habitat01', 'fixed_counterflow01'):
            if 'CALIBRATION' in parts:
                return 'INSTRUMENTAL_DIAGNOSTIC', family, {'fresh_empty_calibration_parent': 1,
                    'diagnostic_fixed_policy_forks': len(data['rows']), 'has_diagnostic_intervention': True,
                    'counted_as_fresh_learned_network': False}
            return 'FRESH_PREPARATION', family, {'has_diagnostic_intervention': diagnostic,
                'explicit_diagnostic_child_count': len(data.get('diagnostic_edits', [])),
                'note': 'A fresh world is built for this arm; any subsequent diagnostic child belongs to the SAME primary record, not another independent preparation.'}
        if parts[1] in ('curriculum01', 'curriculum03', 'fixed_counterflow_continuation01'):
            return 'CONTINUATION', family, {'new_experience_episodes': len(data.get('episodes', [])) if parts[1] != 'fixed_counterflow_continuation01' else 1,
                'has_diagnostic_intervention': False, 'new_preparations': data.get('new_preparations'),
                'note': 'One existing431 or437 genealogy, declared new experience episode(s), no reset or merge.'}
        if parts[1] == 'residual425_diagnostic01':
            return 'INSTRUMENTAL_CAUSAL_DIAGNOSTIC', family, {'intact_local_replays': 1,
                'one_site_diagnostic_children': 1, 'native_ticks_across_both_paths': 33,
                'has_diagnostic_intervention': True, 'explicit_diagnostic_child_count': 1,
                'note': 'One primary record covers an intact replay and one RAW-only diagnostic child/rescue. Neither is a fresh acquired network.'}
    if area == 'regulacion' and parts[1] in ('SUSTAINED_DISCOVERY01', 'SUSTAINED_DIRECTION02',
                                            'DUAL_DISCOVERY01', 'DUAL_CONFIRMATION'):
        return 'FRESH_PREPARATION', family, {'has_diagnostic_intervention': False,
            'note': 'Physically co-prepared relation(s); persistent/finite/absent reader is a prepared condition, not learned regulation.'}
    if area == 'continuidad' and parts[1] in ('M1_TEMPORAL_ACCESS', 'M1_RENEWED_CYCLES'):
        return 'CONTINUATION', family, {'has_diagnostic_intervention': False,
            'parent': case.get('parent'), 'parent_sha256': case.get('parent_sha256'),
            'note': 'Continuation from identified previous native language history, not fresh acquisition of a new body.'}
    if area == 'lenguaje' and parts[1] in ('discovery01', 'continuous02', 'direction03'):
        fresh = data.get('new_preparation', False)
        return ('FRESH_PREPARATION' if fresh else 'CONTINUATION'), family, {
            'has_diagnostic_intervention': False, 'parent': case.get('parent'), 'parent_sha256': case.get('parent_sha256'),
            'note': ('Fresh translated world acquired network and curriculum before language, counted only once.' if fresh else
                     'Existing431,1431 or1529 native genealogy. Changed teaching/query protocol is not another independent training origin.')}
    if area == 'auditor':
        if parts[1] == 'R14_PUBLIC_COMPONENT':
            if parts[2] == 'LATE_REPORT_REMOVE':
                return 'CONTINUATION_DIAGNOSTIC_FORK', family, {'has_diagnostic_intervention': True,
                    'explicit_diagnostic_child_count': 1, 'note': 'One RAW report removed after first action; full parent state preserved.'}
            return 'FRESH_PREPARATION', family, {'has_diagnostic_intervention': False,
                'note': 'Finite public R14 prepared retainP/switchQ component, not integrated ABCD or acquired arbitrary utility.'}
        if parts[1] == 'SUSCEPTIBILITY_PILOT':
            return 'CONTINUATION_DIAGNOSTIC_FORK', family, {'has_diagnostic_intervention': True,
                'explicit_diagnostic_child_count': 1, 'manual_RAW_clock_edits': 0,
                'note': 'Full native T520 operative fork with declared input or omission; no child returned to parent.'}
        if parts[1] == 'NATIVE_PREEMPTION_PILOT':
            return 'FRESH_PREPARATION', family, {'has_diagnostic_intervention': False,
                'manual_RAW_clock_edits': 0, 'note': 'Fresh I02 continuation fromT0 with inert upstream interface already prepared.'}
        if parts[1] == 'INHERITED_REFERENCE148_149':
            return 'TECHNICAL_REFERENCE_REPLAY', family, {'native_ticks': data['native_ticks_advanced'],
                'has_diagnostic_intervention': False, 'note': 'Physical one-tick replay of historical data; not new scientific preparation.'}
    if area == 'demo':
        return 'TECHNICAL_PUBLIC_DEMONSTRATION', family, {'has_diagnostic_intervention': False,
            'note': 'Executed interface/demo continuation or reproduction. Kept separate from scientific cohorts and not added as another discovery.'}
    if area in ('reproduccion_limpia', 'technical'):
        return 'TECHNICAL_CLEAN_REPRODUCTION', family, {'has_diagnostic_intervention': False,
            'note': 'Directed reproduction or interface validation of existing finite behavior; not a new scientific finding.'}
    return 'PENDING_OWNER_RECONCILIATION', family, {'has_diagnostic_intervention': None,
        'note': 'New owner output not part of the closed cohort map; do not infer fresh versus continuation from filename.'}


def final_tick(data):
    final = data.get('final') or data.get('after') or data.get('digest') or data.get('canonical437') or {}
    return final.get('tick') if isinstance(final, dict) else None


def run():
    now = datetime.now(timezone.utc).isoformat(); rows = []
    for path in sorted((ROOT / 'resultados').rglob('MEASUREMENTS.json')):
        data = read(path); kind, family, attributes = classify(path, data)
        case = data.get('case') or {}; config = data.get('config') or {}
        initial = data.get('initial') or data.get('before') or data.get('initial_digest') or {}
        if kind == 'FRESH_PREPARATION': start = 0
        elif isinstance(initial, dict): start = initial.get('tick')
        else: start = None
        parent = attributes.get('parent') or config.get('parent_checkpoint') or data.get('source')
        if isinstance(parent, dict): parent = parent.get('path')
        checkpoints = sorted(p.name for p in path.parent.glob('*.deetsnap'))
        rows.append({'key': rel(path), 'sha256': sha(path), 'id': case.get('id', path.parent.name),
            'family': family, 'kind': kind, 'start_tick': start, 'final_tick': final_tick(data),
            'parent_reference': parent, 'attributes': attributes,
            'configuration_files': [rel(p) for p in (path.parent / 'CONFIG.json', path.parent / 'EXPERIMENT_CONFIG.json') if p.exists()],
            'checkpoints_in_primary_folder': checkpoints,
            'modalities': data.get('modality') or data.get('mode') or None,
            'task_profile': data.get('task_profile'),
            'relation_or_response_scope': data.get('scope') or data.get('mechanism_claim')})
    by_kind = Counter(x['kind'] for x in rows); by_family = defaultdict(Counter)
    for x in rows: by_family[x['family']][x['kind']] += 1
    grouped = [{'family': f, 'primary_records': sum(counts.values()), 'kinds': dict(counts)} for f, counts in sorted(by_family.items())]
    scientific = [x for x in rows if x['kind'] in ('FRESH_PREPARATION', 'CONTINUATION', 'CONTINUATION_DIAGNOSTIC_FORK')]
    diagnostic_fresh = [x for x in rows if x['kind'] == 'FRESH_PREPARATION' and x['attributes'].get('has_diagnostic_intervention')]
    duplicates = defaultdict(list)
    for x in rows: duplicates[x['sha256']].append(x['key'])
    network_summary = ROOT / 'resultados/red/NETWORK_MEASUREMENTS_SUMMARY.json'
    network = read(network_summary)
    owner_index_path = ROOT / 'resultados/red/NETWORK_INDEX.json'; owner_index = read(owner_index_path)
    closure_path = ROOT / 'resultados/red/RED_CLOSURE.json'; closure = read(closure_path)
    red_fresh = [x for x in rows if x['family'].startswith('red/') and x['kind'] == 'FRESH_PREPARATION']
    indexed_red = {x['path'] for x in network['rows']}
    indexed_all = {x['key'] for x in rows}
    red_consistent = len(red_fresh) == network['fresh_preparation_records'] and {x['key'] for x in red_fresh} == indexed_red
    all_red_primary = {x['key'] for x in rows if x['family'].startswith('red/')}
    all_owner_red = {x['path'] for x in owner_index['measurement_files']}
    all_red_primary_reconciled = all_red_primary == all_owner_red
    assert red_consistent and all_red_primary_reconciled
    assert closure['fresh_preparation_records'] == len(red_fresh) == 49
    assert closure['continuations'] == 3 and closure['new_experience_episodes'] == 5
    assert closure['native_jobs_owned_by_red_running'] == 0
    technical = []
    for path in (
        ROOT / 'resultados/auditor/ABCD_WINDOW160_161_V2/TECHNICAL_CHECKS.json',
        ROOT / 'resultados/auditor/ABCD_WINDOW93_94/TECHNICAL_CHECKS.json',
        ROOT / 'resultados/lenguaje/TECHNICAL_CHECKS/TECHNICAL_SUMMARY.json',
        ROOT / 'resultados/lenguaje/LOADER_HARDENING/RESULTS.json',
        ROOT / 'resultados/technical/PUBLIC_UI_FINAL01/PUBLIC_UI_CHECKS.json',
        ROOT / 'resultados/auditor/NONTRIVIAL_FORK_ISOLATION.json',
        ROOT / 'resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_RECONSTRUCTION.json',
        ROOT / 'resultados/auditor/TECHNICAL_HOTFIX_AND_BYTE_DIFF.json'):
        if path.exists():
            data = read(path)
            technical.append({'evidence': rel(path), 'sha256': sha(path), 'scientific_samples_added': 0,
                'checks': data.get('technical_checks') or data.get('checks'),
                'continuations': data.get('continuations'), 'replayed_ticks': data.get('replayed_native_ticks'),
                'notes': 'Technical equality, guards, format, interface or replay evidence; not another independently acquired capability.'})
    for path in sorted((ROOT / 'resultados/technical').glob('PUBLIC_UI_*/PUBLIC_UI_CHECKS.json')):
        if any(x['evidence'] == rel(path) for x in technical): continue
        data = read(path)
        technical.append({'evidence': rel(path), 'sha256': sha(path), 'scientific_samples_added': 0,
            'checks': data.get('checks'), 'notes': 'Preserved public-interface validation attempt, not an independent scientific sample or another learned participant.'})
    reread_paths = ['resultados/red/NETWORK_MEASUREMENTS_SUMMARY.json', 'resultados/red/NETWORK_INDEX.json',
        'resultados/red/RED_CLOSURE.json', 'resultados/continuidad/CONTINUITY_SUMMARY.json',
        'resultados/lenguaje/LANGUAGE_SUMMARY.json', 'resultados/auditor/PAIRING_SCOPE_REVIEW.json',
        'resultados/auditor/REGULATION_RETENTION_REVIEW.json', 'resultados/auditor/REGULATION_LOCAL_GATES.json',
        'resultados/auditor/NATIVE_PREEMPTION_RECONSTRUCTION.json', 'resultados/auditor/NETWORK_V3_SCOPE_REVIEW.json',
        'resultados/auditor/LANGUAGE_CONTINUITY_REVIEW.json', 'resultados/auditor/INHERITED_REFERENCE_OP_DIFF.json',
        'resultados/auditor/D_SOCIAL_CONTEXT93_94.json',
        'resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_BRANCH_RECONSTRUCTION.json']
    rereads = [{'evidence': p, 'sha256': sha(ROOT / p), 'new_physical_cases': 0} for p in reread_paths if (ROOT / p).exists()]
    result = {'generated_utc': now, 'scope': 'New A02 section only; saved primary records as of this boundary, not independent replicas or capabilities.',
        'method': 'Unique MEASUREMENTS.json primary paths. Summaries contribute provenance and checks but never add their rows again. Snapshot counts and ticks are not sample counts.',
        'reconciled_primary_records': len(rows), 'counts_by_primary_kind': dict(by_kind),
        'scientific_primary_records': len(scientific),
        'scientific_decomposition': {
            'fresh_preparation_records': by_kind['FRESH_PREPARATION'],
            'continuations_without_explicit_diagnostic_fork_API': by_kind['CONTINUATION'],
            'explicit_continuation_diagnostic_fork_records': by_kind['CONTINUATION_DIAGNOSTIC_FORK'],
            'fresh_records_with_later_diagnostic_child_already_included': len(diagnostic_fresh),
            'diagnostic_child_rows_not_added_twice': [x['key'] for x in diagnostic_fresh],
            'independence_note': 'Fresh deterministic preparations can repeat known geometries; they are not necessarily independent statistical replicates. A restored/copy continuation shares its recorded parental history.'},
        'instrumental_calibration': {
            'record': 'resultados/red/dual_habitat01/CALIBRATION/MEASUREMENTS.json',
            'empty_parent_preparations': network['dual_instrumental_calibration']['empty_preparation_count'],
            'explicit_fixed_policy_diagnostic_forks': network['dual_instrumental_calibration']['diagnostic_fixed_policy_forks'],
            'not_fresh_acquired_networks': True,
            'counting_note': 'One primary calibration record covers16diagnostic forks; report both units without turning them into16independently acquired network worlds.'},
        'tables_by_family': grouped, 'primary_cases': rows,
        'summary_reconciliations': {'red_fresh_index_exact': red_consistent,
            'red_summary_fresh_records': network['fresh_preparation_records'],
            'red_primary_fresh_records': len(red_fresh), 'all_summary_red_paths_are_primary': indexed_red <= indexed_all,
            'all_owner_NETWORK_INDEX_primary_paths_exact': all_red_primary_reconciled,
            'red_closed_index': {'path': rel(owner_index_path), 'sha256': sha(owner_index_path)},
            'red_closed_statement': {'path': rel(closure_path), 'sha256': sha(closure_path)},
            'red_continuations': 3, 'red_new_experience_episodes_in_continuations': 5,
            'red_instrumental_calibration_forks': 16, 'red_intact_causal_replay': 1, 'red_one_site_rescue': 1,
            'same_byte_primary_duplicates': [v for v in duplicates.values() if len(v) > 1],
            'primary_paths_unique': len({x['key'] for x in rows}) == len(rows)},
        'read_only_analytical_reports': rereads, 'technical_evidence_separate': technical,
        'inference_review': [
            {'topic': 'Regulation', 'measured': 'Prepared R14 retainP/switchQ finite component; input/history-dependent native expression under fixed support and an explicit external protocol.',
             'not_demonstrated': 'An acquired arbitrary utility policy or autonomous regulation integrated into ABCD; prepared renewability alone is not acquired self-regulation.'},
            {'topic': 'Retention versus reader', 'measured': 'DUAL relation signs persist through520. NO_READER preserves delta while comparator is absent; finite reader also expresses throughout this horizon.',
             'not_demonstrated': 'The semantic4 source is necessary for all observed retention, or absence/rejected400probe establishes forgetting.'},
            {'topic': 'Matched native experience', 'measured': 'Upstream517input actuallyApplied for both AB/BA, enters different local occupied/empty contexts, changes BA expression while A/B loads stayfixed517-525.',
             'not_demonstrated': 'New differential rewrite, isolated causal sufficiency of scalar delta, or a native learned admission decision.'},
            {'topic': 'ABCD integration', 'measured': 'Eight certified directed segments plus seven empty-target local reducer events. D updates and later serves as a physical source for B.',
             'not_demonstrated': 'All useful outputs require every intended route; V3C_UNPAIRED preserves a B-only later path and no unique full ancestry before70 is certified.'},
            {'topic': 'Fixed counterflow versus learned regulation', 'measured': 'Seven new fixed-protocol worlds show a zero+Z input physically neutralizes the residual5-Z:5/4/4/5/6/6/5; one sameWorld437-937 continuation reuses the fixed input and changes useful bank with new experience.',
             'not_demonstrated': 'Acquired attention, learned neutralizer timing, autonomous utility maximization or a host-free closed habitat. Input0 is a real EXPERIENCE_PROTOCOL event scheduled by an external fixed protocol.'},
            {'topic': 'New forms', 'measured': 'Two task-profile and two direction-class form associations over one continuing genealogy, with finite probes and controls.',
             'not_demonstrated': 'Four simultaneous retained meanings, all65NSM semantics, arbitrary grammar, or unlimited renewal. Older-word extra probes do not reveal a qualified26 signature but do not prove global destruction.'}],
        'pending': [],
        'network_scientific_cut_closed': True,
        'network_resumable_checkpoint': closure['final_resumable_checkpoint'],
        'publication_validation_scope': 'Root-owned UI, demos, clean extraction and packaging can add technical records only; no new scientific preparations are expected after this closed owner index.',
        'no_native_calls_in_indexer': True,
        'closure': 'Reconciled saved finite scientific cut and closed native owner index. Technical reproductions and snapshots are not new learned individuals.'}
    target = ROOT / 'resultados/auditor/FINAL_COVERAGE_INDEX.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'primary': len(rows), 'kinds': dict(by_kind), 'scientific_records': len(scientific),
        'red_index_exact': red_consistent, 'fresh_diagnostic_arms_already_counted': len(diagnostic_fresh)}))


if __name__ == '__main__': run()
