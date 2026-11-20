"""Directed forward replay of already measured V3 message segments.

Passive observations are distinct from causal interventions. The recipe below
predicts a segment, never manufactures its RAW, direction, receipt or endpoint.
Certification stops at the first unmatched field and is not resumed by load
coincidence. Local encounters preserve all26neighbors, including inactivity.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, sys, time

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.auditor.passive import record, neighborhood, digest, receipt


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def put(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
def moved(q, dr, dt): return tuple((q[i] + dr[i] * dt) % 67 for i in range(3))
def dirsum(records): return [max(-1, min(1, sum(r['direction'][i] for r in records))) for i in range(3)]


def main():
    import dee_thinking as d
    source = ROOT / 'resultados/red/confirmacion03/FULL_U'
    out = ROOT / 'resultados/auditor/V3_MESSAGE_RECONSTRUCTION'; out.mkdir(parents=True, exist_ok=False)
    segments = [
        {'id': 'A70_B82', 'start': 70, 'end': 81, 'site': [42, 20, 12], 'direction': [-1, 1, 0], 'load': 21, 'event': 'A_B82'},
        {'id': 'B82_H86', 'start': 82, 'end': 85, 'site': [30, 32, 12], 'direction': [-1, 1, 1], 'load': 37, 'event': 'BC_H86'},
        {'id': 'C80_H86', 'start': 80, 'end': 85, 'site': [32, 36, 22], 'direction': [-1, 0, -1], 'load': 21, 'event': 'BC_H86'},
        {'id': 'H86_D94', 'start': 86, 'end': 93, 'site': [26, 36, 16], 'direction': [-1, 1, 0], 'load': 58, 'event': 'H_D94'},
        {'id': 'D94_D161', 'start': 94, 'end': 160, 'site': [18, 44, 16], 'direction': [-1, 1, 1], 'load': 74, 'event': 'D_READ161'},
        {'id': 'D161_D228', 'start': 161, 'end': 227, 'site': [18, 44, 16], 'direction': [0, 1, 1], 'load': 79, 'event': 'D_READ228'},
        {'id': 'D228_R291', 'start': 228, 'end': 290, 'site': [18, 44, 16], 'direction': [-1, 1, 1], 'load': 84, 'event': 'D_RELAY291'},
        {'id': 'R291_B350', 'start': 291, 'end': 349, 'site': [22, 40, 12], 'direction': [-1, 1, 0], 'load': 89, 'event': 'RELAY_B350'}]
    events = [
        {'id': 'A_B82', 'pre': 81, 'post': 82, 'site': [30, 32, 12], 'incoming_segments': ['A70_B82'], 'expected_loads': [21, 16]},
        {'id': 'BC_H86', 'pre': 85, 'post': 86, 'site': [26, 36, 16], 'incoming_segments': ['B82_H86', 'C80_H86'], 'expected_loads': [37, 21]},
        {'id': 'H_D94', 'pre': 93, 'post': 94, 'site': [18, 44, 16], 'incoming_segments': ['H86_D94'], 'expected_loads': [58, 16]},
        {'id': 'D_READ161', 'pre': 160, 'post': 161, 'site': [18, 44, 16], 'incoming_segments': ['D94_D161'], 'expected_loads': [74, 5]},
        {'id': 'D_READ228', 'pre': 227, 'post': 228, 'site': [18, 44, 16], 'incoming_segments': ['D161_D228'], 'expected_loads': [79, 5]},
        {'id': 'D_RELAY291', 'pre': 290, 'post': 291, 'site': [22, 40, 12], 'incoming_segments': ['D228_R291'], 'expected_loads': [84, 5]},
        {'id': 'RELAY_B350', 'pre': 349, 'post': 350, 'site': [30, 32, 12], 'incoming_segments': ['R291_B350'], 'expected_loads': [89]}]
    checkpoints = [70, 80, 82, 85, 86, 93, 94, 160, 161, 227, 228, 242, 290, 291, 349, 350]
    config = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'RETROSPECTIVE_FORWARD_REPLAY_OF_EXISTING_DATA',
        'source_snapshot': str((source / 'T70.deetsnap').relative_to(ROOT)), 'source_sha256': sha(source / 'T70.deetsnap'),
        'source_measurements_sha256': sha(source / 'MEASUREMENTS.json'), 'runner_sha256': sha(Path(__file__)),
        'segments': segments, 'events': events, 'full_physical_comparison_ticks': checkpoints,
        'new_fresh_cases': 0, 'new_scientific_interventions': 0, 'diagnostic_forks': 0,
        'replay_tick_window': [70, 350], 'capture_budget': {'segment_records': 286, 'event_contexts26': 7},
        'stop_rule': 'First mismatch terminates certification of that segment; later matching records are not relabeled as descendants. No replanning, new geometry or ablation.',
        'claim_limits': 'Certifies observed local directed evolution and empty-destination proposals, not intervention necessity, semantics, or unique ancestry before source70.'}
    put(out / 'EXPERIMENT_CONFIG.json', config); started = time.monotonic()
    w = d.OrganizationalWorld.load_snapshot(str(source / 'T70.deetsnap'))
    states = {x['id']: {'configuration': x, 'prefix_certified': True, 'first_mismatch': None, 'samples': []} for x in segments}
    current_events = {}; comparisons = []
    for tick in range(70, 351):
        assert w.runtime.current_tick == tick
        for segment in segments:
            if not segment['start'] <= tick <= segment['end']: continue
            q = moved(segment['site'], segment['direction'], tick - segment['start'])
            observed = record(w.runtime.observe(d.Coordinate(*q)))
            matches = (observed['active'] and observed['state'] == 1 and observed['semantic'] == 1
                       and observed['s_reg'] == segment['load'] and observed['direction'] == segment['direction'])
            state = states[segment['id']]
            if not matches and state['first_mismatch'] is None:
                state['first_mismatch'] = {'tick': tick, 'actual': observed,
                    'expected': {'load': segment['load'], 'direction': segment['direction'], 'state': 1, 'semantic': 1}}
                state['prefix_certified'] = False
            state['samples'].append({'tick': tick, 'actual': observed, 'matches_segment': bool(matches),
                                     'prefix_certified_through_here': state['prefix_certified']})
        for event in events:
            if tick == event['pre']:
                before = digest(w); context = neighborhood(w, event['site'])
                g = d.inspect_write_gate(w.runtime, d.Coordinate(*event['site']), False)
                gate = {k: getattr(g, k) for k in ('local_clock', 'center_available', 'n_active', 'hadron', 'rule_value',
                    'survives_material_rule', 'semantic_protected', 'write_protected', 'k', 'period', 'phase_remainder',
                    'ordinary_increment_condition', 'branch', 'demux_status')}
                assert digest(w) == before
                current_events[event['id']] = {'configuration': event, 'pre_context': context, 'pre_gate': gate,
                    'observer_passivity_full_RAW_clock_checked': True}
            if tick == event['post']:
                row = current_events[event['id']]; post = record(w.runtime.observe(d.Coordinate(*event['site'])))
                proposals = row['pre_context']['directional_proposals_without_activity_prefilter']
                row.update(post=post, proposal_count=len(proposals), proposed_loads=[x['s_reg'] for x in proposals],
                    reconstructed_local_load_sum=sum(x['s_reg'] for x in proposals),
                    reconstructed_local_direction=dirsum(proposals),
                    center_was_RAW_empty=row['pre_context']['center']['raw'] == 0,
                    source_segments_certified={name: states[name]['prefix_certified'] for name in event['incoming_segments']})
                row['observed_post_matches_local_proposal_sum_and_direction'] = (
                    row['center_was_RAW_empty'] and post['state'] == 1 and post['semantic'] == 1
                    and post['s_reg'] == row['reconstructed_local_load_sum'] and post['direction'] == row['reconstructed_local_direction'])
                row['attribution_scope'] = 'Directed sources identified by exact pre-sites, fields and certified forward segments. Context retains all presences/absences; no causal-necessity ablation was executed.'
        if tick in checkpoints:
            expected = d.OrganizationalWorld.load_snapshot(str(source / f'T{tick}.deetsnap'))
            actual_digest, expected_digest = digest(w), digest(expected)
            actual_receipts, expected_receipts = [receipt(x) for x in w.runtime.receipts], [receipt(x) for x in expected.runtime.receipts]
            comparison = {'tick': tick, 'historical_snapshot': str((source / f'T{tick}.deetsnap').relative_to(ROOT)),
                'historical_sha256': sha(source / f'T{tick}.deetsnap'), 'full_RAW_clock_tick_equal': actual_digest == expected_digest,
                'operative_receipts_equal': actual_receipts == expected_receipts, 'actual': actual_digest, 'expected': expected_digest,
                'metadata_scope': 'This is a physics/receipt replay. The custom NetworkSession neutral capture cursor is not updated by plain observer replay and is not equated with operational UI metadata.'}
            comparisons.append(comparison); assert comparison['full_RAW_clock_tick_equal'] and comparison['operative_receipts_equal']
            put(out / 'PROGRESS.json', {'tick': tick, 'comparisons': comparisons,
                'segment_prefixes': {name: v['prefix_certified'] for name, v in states.items()}})
        if tick < 350: w.advance()
    result = {'config_sha256': sha(out / 'EXPERIMENT_CONFIG.json'), 'mode': config['mode'],
        'source_snapshot_unchanged': sha(source / 'T70.deetsnap') == config['source_sha256'],
        'new_fresh_cases': 0, 'replayed_native_ticks': 280, 'new_interventions': 0,
        'segments': list(states.values()), 'encounters': list(current_events.values()), 'full_comparisons': comparisons,
        'segment_record_count': sum(len(x['samples']) for x in states.values()),
        'all_segments_certified': all(x['prefix_certified'] for x in states.values()),
        'local_encounters_matching_recorded_proposals': sum(x['observed_post_matches_local_proposal_sum_and_direction'] for x in current_events.values()),
        'elapsed_seconds': time.monotonic() - started,
        'source_code_sha256': sha(Path(__file__)), 'coverage_limits': [
            'Source70 already contains the acquired A/B/C/D history and queued external finite queries. This replay does not create or newly validate their pre70 acquisition.',
            'All observations are passive. Rule participation and exact directed continuations are not equivalent to counterfactual necessity.',
            'The B and D memory components arriving at the first social contacts are recorded as real local proposals; their complete earlier lineage is outside these eight tracked segments.',
            'No labels, observations, source ancestry or evaluation outputs are written into RAW or clocks.',
            'Finite closed geometry and prepared timing determine the public domain; no unrestricted semantic or biological inference is made.']}
    put(out / 'MESSAGE_RECONSTRUCTION.json', result)
    print(json.dumps({'segment_records': result['segment_record_count'], 'all_segments_certified': result['all_segments_certified'],
        'encounters_matching': result['local_encounters_matching_recorded_proposals'], 'full_physics_checks': len(comparisons),
        'first_mismatches': {name: x['first_mismatch'] for name, x in states.items() if x['first_mismatch'] is not None}}))


if __name__ == '__main__': main()
