"""N0 portable evidence extraction/recalculation for frozen APD04 R03 view trials.

N0 revision R08 fixes ledger association for data first returned in same-ID polls.
R07 was an N0 draft; its wrong ledger was detected before any final export/claim.
N0 revision R07 added literal plan-vs-actual coverage and explicit world/window scope.
N0 revision R06 separates the three explicitly declared sensory IDs from resources.
N0 revision R05 adds complete per-row Native ID/terminal-FULL admission scope.
N0 revision R04 made the recalculation entrypoint safe at shallow paths.
Scientific extraction R03 includes late outbox results during generic closing.
Prior inspection/denominator revisions remain *_pre_dosis_r01/*_pre_late_r02.py.
No Runtime construction, evolution, SQLite writes, feedback or actor decisions.
Unclean endings retain their exact journal and last committed snapshot; they are
never described as a complete current operational future.
"""
import argparse
from array import array
from collections import Counter
import csv
from datetime import datetime, timedelta
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE
EV = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
QUALITY = 'APD04.posteffect_quality.relevant_gain_or_irrelevant_formed_wait.R03.v1'


def sha(b): return hashlib.sha256(b).hexdigest()
def read(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
def emit(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')
def walk(value, loc='$'):
    yield loc, value
    if isinstance(value, dict):
        for k, v in value.items():
            if k in ('result', 'result_json') and isinstance(v, str):
                try: v = json.loads(v)
                except json.JSONDecodeError: pass
            yield from walk(v, loc + '.' + k)
    elif isinstance(value, list):
        for i, v in enumerate(value): yield from walk(v, loc + '[' + str(i) + ']')
def raw_fields(value):
    n = int(value)
    if not 0 <= n < 2**64: raise ValueError('Exact uint64 required')
    return n & 0xffffffff, (n >> 60) & 15, [((n >> k) & 15) - (16 if ((n >> k) & 15) >= 8 else 0) for k in (48, 52, 56)]
def decode(reader, kind):
    expected = ({(25 + 2*s, 15, 53): (s, [s, 1, 0]) for s in (-1, 0, 1)} if kind == 'selector' else
        {(15 + 2*s, 17, 15 + 2*z): (s, [s, 1, z]) for s in (-1, 0, 1) for z in (0, -1)})
    obs = reader['observations']
    if len(obs) != len(expected) or {tuple(o['site']) for o in obs} != set(expected):
        raise ValueError('Frozen RAW reader coverage differs: ' + kind)
    candidates = []
    for o in obs:
        state, semantic, direction = raw_fields(o['raw'])
        sign, required = expected[tuple(o['site'])]
        if state and semantic == 1 and direction == required: candidates.append(sign)
    return (candidates[0] if len(candidates) == 1 else None), len(candidates)
def ID(x):
    return x if type(x) is int else int(x) if isinstance(x, str) and x.isdecimal() else None


def scan(data):
    rows = {}; checks = []; errors = []; receipts = {}; requests = {}; events = []; submitted_work = {}
    for line, b in enumerate(data.splitlines(), 1):
        try: top = json.loads(b)
        except json.JSONDecodeError:
            errors.append({'line': line, 'incomplete_line_preserved': True}); continue
        if top.get('kind') in ('scheduled_material_result', 'scheduled_material_before_submission', 'preserved_failure'):
            events.append({'line': line, 'kind': top['kind'], 'requested_id': top.get('requested_id'),
                'wall_utc': top.get('wall_utc'), 'window_seconds': top.get('window_seconds'),
                'lateness_seconds': top.get('lateness_seconds'), 'event': top.get('event'), 'error': top.get('error')})
        if top.get('kind') == 'scheduled_material_before_submission':
            situations = top.get('literal_situations', (top.get('event') or {}).get('situations', []))
            count_requested = sum(int(r.get('oportunidades', 0)) for r in situations if r.get('modo') == 'apd04-vivir')
            if count_requested:
                submitted_work[top['requested_id']] = {'line': line, 'opportunities_requested': count_requested,
                    'wall_utc': top.get('wall_utc'), 'window_seconds': top.get('window_seconds')}
        for loc, n in walk(top, 'line' + str(line)):
            if not isinstance(n, dict): continue
            if isinstance(n.get('receipt'), dict):
                rid = ID(n['receipt'].get('id'))
                if rid is not None:
                    receipts.setdefault(rid, []).append({'locator': loc, 'receipt': n['receipt'],
                        'wrapper': 'port' if 'port' in n else 'channel' if 'channel' in n else 'other',
                        'channel': n.get('channel', n.get('port'))})
            if {'id', 'status', 'is_control', 'payload_sha'} <= set(n):
                requests.setdefault(str(n['id']), []).append({'line': line, 'status': n['status'],
                    'is_control': n['is_control'], 'started_utc': n.get('started_utc'),
                    'finished_utc': n.get('finished_utc'), 'payload_sha': n['payload_sha']})
            if not {'public_before', 'committed_effect', 'selection'} <= set(n): continue
            key = (n['episode'], n['selection'].get('query_tick'))
            if key in rows: continue
            locbase = {'locator': loc, 'episode': key[0], 'tick': key[1]}
            def check(name, ok): checks.append({**locbase, 'check': name, 'ok': bool(ok)})
            selected = n['selection']; sign, count = decode(selected['reader'], 'selector')
            action = {-1: 'INSPECT', 0: 'WAIT', 1: 'USE'}.get(sign)
            check('RAW_unique_selector', sign == selected['physical_choice'])
            check('R03_fixed_action_codec', action == n['physical_action'])
            effect = n['committed_effect']; public = n['public_before']; q = n['posteffect_quality']
            check('fixed_quality_contract', q['contract'] == QUALITY)
            eligible = public['tag'] == public['goal_tag']
            before, after = q['task_env_before'], q['task_env_after']
            old_gain = False; native_sign = None; actual_tool = None
            if action == 'INSPECT' and effect['actuator'] == 'closed':
                sid = public['source_id']
                bo = next(o for o in before['objects'] if o['id'] == sid)
                ao = next(o for o in after['objects'] if o['id'] == sid)
                new_fact = bo['observed'] != ao['observed']
                check('INSPECT_environment_cache_change', new_fact == effect['new_fact'])
                old_gain = eligible and new_fact
            prim = n.get('native_operation')
            if prim is not None:
                native_sign, _ = decode(prim['native_trial']['reader'], 'numeric')
                check('RAW_numeric', native_sign == prim['physical_choice'])
            if action == 'USE' and effect['actuator'] == 'closed':
                if 'actual_bin' in effect:
                    actual_tool = 'clasifica'; audit = n['auditor_only_after_effect']
                    expected = (audit['actual_source_value'] > audit['criterion']) - (audit['actual_source_value'] < audit['criterion'])
                    correct = native_sign == expected and audit['observed_version'] == audit['source_version']
                    check('classification_content_and_freshness', correct == effect['correct'])
                    old_gain = eligible and correct and effect['previous_bin'] != native_sign
                elif 'loads_before' in effect:
                    actual_tool = 'equilibra'; lb, la = effect['loads_before'], effect['loads_after']
                    expected_loads = list(lb)
                    if native_sign == 1 and lb[0] > 0 and lb[1] < 20: expected_loads = [lb[0]-1, lb[1]+1]
                    elif native_sign == -1 and lb[1] > 0 and lb[0] < 20: expected_loads = [lb[0]+1, lb[1]-1]
                    check('fixed_numeric_to_load_units', la == expected_loads)
                    old_gap, new_gap = abs(lb[0]-lb[1]), abs(la[0]-la[1])
                    old_gain = eligible and (new_gap < old_gap or (native_sign == 0 and old_gap == 0))
            quality = False
            if count == 1 and effect['actuator'] == 'closed':
                quality = (sign == 0 and not eligible and before == after) if action == 'WAIT' else bool(old_gain) if action in ('INSPECT', 'USE') else False
            check('old_environmental_gain_unchanged', old_gain == effect['useful'] == effect['old_work_gain'])
            check('new_R03_quality_separate', quality == q['new_quality'] == effect['new_quality'])
            policy = n.get('view_policy', 'circular_R01')
            cursor_before = n.get('cursor_before', public['source_id'])
            cursor_expected = cursor_before if policy == 'inspeccion_persistente' and action == 'INSPECT' and count == 1 and effect['actuator'] == 'closed' else (cursor_before + 1) % len(before['objects'])
            if 'cursor_after' in n: check('fixed_P0_cursor_rule', n['cursor_after'] == cursor_expected)
            expected_feedback = 'SUCCESS' if quality else 'FAILURE'
            native_return = n.get('native_return') or {}
            if n['feedback']['modality'] == 'real': check('posteffect_feedback_not_target', native_return.get('category') == expected_feedback)
            rows[key] = {**locbase, 'public': public, 'selector_RAW': selected['reader']['observations'],
                'RAW_sign': sign, 'candidate_count': count, 'action': action,
                'actual_numeric_tool': actual_tool, 'RAW_numeric_sign': native_sign,
                'requested_tool_agrees_with_effect_tool': None if actual_tool is None else public['word'] == actual_tool,
                'effect': effect, 'quality_witness': q, 'eligible': eligible, 'recalculated_old_gain': old_gain,
                'recalculated_new_quality': quality, 'correct_formed_WAIT': action == 'WAIT' and quality,
                'view_policy': policy, 'cursor_before': cursor_before, 'cursor_after': n.get('cursor_after'),
                'expected_cursor_after': cursor_expected, 'feedback': n['feedback'],
                'auditor_only_after_effect': n.get('auditor_only_after_effect'),
                'Native_receipt_IDs_referenced_by_row': sorted({ID(node['receipt']['id'])
                    for _, node in walk(n) if isinstance(node, dict) and isinstance(node.get('receipt'), dict)
                    and ID(node['receipt'].get('id')) is not None}),
                'sensory_IDs_declared_in_frozen_sensor': sorted({ID(v['id']) for v in selected.get('sensory_requests', []) if ID(v.get('id')) is not None}),
                'generic_only_IDs_declared_in_frozen_sensor': sorted({ID(v['id']) for v in selected.get('generic_only_requests', []) if ID(v.get('id')) is not None}),
                'no_claim_INSPECT_cache_is_Native_learning': True}
    rr = list(rows.values())
    return {'rows': rr, 'checks': checks, 'issues': errors + [c for c in checks if not c['ok']],
        'completed_work': len(rr), 'action_counts': dict(Counter(str(r['action']) for r in rr)),
        'eligible_work': sum(r['eligible'] for r in rr), 'old_gain': sum(r['recalculated_old_gain'] for r in rr),
        'new_quality': sum(r['recalculated_new_quality'] for r in rr),
        'correct_formed_WAIT': sum(r['correct_formed_WAIT'] for r in rr),
        'distinct_source_ids': sorted({r['public']['source_id'] for r in rr}),
        'distinct_source_scope': 'Environmentally presented source IDs. Not proof that the Native sensor admitted the associated cues or that Native inspected all current values.',
        'work_requested_in_actual_submissions': sum(r['opportunities_requested'] for r in submitted_work.values()),
        'work_request_IDs_actually_submitted': submitted_work,
        'formed_valid_actions': sum(r['action'] is not None for r in rr),
        'NULL_or_ambiguous_completed_actions': sum(r['action'] is None for r in rr),
        'not_useful_completed_actions': sum(not r['recalculated_new_quality'] for r in rr),
        'receipt_witnesses': receipts, 'transport_request_status_witnesses': requests,
        'scheduled_events_seen': events,
        'scope': 'Exact RAW and frozen R03 maps; task cache/cursor are host-environment state, not Native acquired numbers. A completed row is not an independent learner; NULL is not WAIT. Unreturned operations are not assigned a cognitive answer.'}


def buffer_summary(rb, cb, N):
    raw = array('Q'); raw.frombytes(rb); clocks = array('Q'); clocks.frombytes(cb)
    if sys.byteorder != 'little': raw.byteswap(); clocks.byteswap()
    if len(raw) != N**3 or len(clocks) != N**3: raise ValueError('Wrong exact array lengths')
    return {'sites': len(raw), 'occupied': sum(bool(n & 0xffffffff) for n in raw),
        'raw_nonzero': sum(bool(n) for n in raw), 'state0_raw_nonzero': sum(bool(n) and not (n & 0xffffffff) for n in raw),
        'max_s_reg': max((n >> 32) & 65535 for n in raw),
        'state_counts': dict(Counter(str(n & 0xffffffff) for n in raw)),
        'clock_min': min(clocks), 'clock_max': max(clocks),
        'RAW_SHA': sha(rb), 'clock_SHA': sha(cb)}


def plan_and_world_ledger(plan, journal, result, case):
    """All planned work remains visible, including never sent and late results."""
    tops = [json.loads(line) for line in journal.splitlines()]
    before = {e['requested_id']: e for e in result['scheduled_events_seen']
        if e['kind'] == 'scheduled_material_before_submission'}
    returned = {e['requested_id']: e for e in result['scheduled_events_seen']
        if e['kind'] == 'scheduled_material_result'}
    late = {e['request_id']: e for e in case.get('late_archived_results', [])}
    workIDs = {e['request_id'] for e in plan['events']
        if any(v.get('modo') == 'apd04-vivir' for v in e.get('situations', []))}
    by_request = {}
    # The first occurrence of a result is often the read-only poll, not the
    # later scheduled_material_result copy. Associate by explicit request ID.
    for top in tops:
        rid = top.get('requested_id', top.get('request_id'))
        if rid not in workIDs: continue
        for _, node in walk(top):
            if not isinstance(node, dict) or not {'public_before', 'committed_effect', 'selection'} <= set(node): continue
            key = (node['episode'], node['selection'].get('query_tick'))
            by_request.setdefault(rid, set()).add(key)
    rows = []
    terminal_priority = {'queued': 1, 'processing': 2, 'uncertain': 3,
        'failed_preserved': 4, 'rejected_invalid': 4, 'completed': 5}
    for event in plan['events']:
        n = sum(int(v.get('oportunidades', 0)) for v in event.get('situations', []) if v.get('modo') == 'apd04-vivir')
        if not n: continue
        rid = event['request_id']; observed = result['transport_request_status_witnesses'].get(rid, [])
        status = max(observed, key=lambda x: terminal_priority.get(x['status'], 0))['status'] if observed else None
        rr = [r for r in result['rows'] if (r['episode'], r['tick']) in by_request.get(rid, set())]
        if rid in late:
            rr += [r for r in result['rows'] if r['locator'].startswith(late[rid]['export'] + '::')]
        keys = {(r['episode'], r['tick']): r for r in rr}; rr = list(keys.values())
        if rr: state = 'NATIVE_RESULT_ARCHIVED'
        elif status in ('rejected_invalid', 'failed_preserved', 'uncertain'): state = 'FAILED_OR_REJECTED_WITHOUT_COMPLETE_NATIVE_ROW'
        elif rid in before: state = 'SUBMITTED_NO_COMPLETE_NATIVE_RESULT_ARCHIVED'
        else: state = 'NOT_SENT'
        rows.append({'request_id': rid, 'at_seconds_planned': event['at_seconds'],
            'opportunities_planned': n, 'state': state, 'submitted_before_log': rid in before,
            'Native_results_in_driver_journal': len(rr) if rid not in late else 0,
            'late_Native_result_archived': rid in late,
            'Native_results_total_unique': len(rr), 'UI_transport_status_observed': status,
            'UI_status_scope': 'Only observed journal status. Late committed outbox can prove Native completion despite a stale pending operator marker; never resubmit the ID.',
            'episodes': [r['episode'] for r in rr], 'actual_query_ticks': [r['tick'] for r in rr],
            'old_gain': sum(r['recalculated_old_gain'] for r in rr),
            'new_quality': sum(r['recalculated_new_quality'] for r in rr),
            'formed_actions': sum(r['action'] is not None for r in rr),
            'NULL_or_ambiguous': sum(r['action'] is None for r in rr)})
    starts = [t for t in tops if t.get('kind') == 'owner_started_paused']
    clocks = [t for t in tops if isinstance(t.get('window_seconds'), (int, float))]
    failures = [t for t in tops if t.get('kind') == 'preserved_failure']
    first_clock = clocks[0] if clocks else None
    window_start = None
    if first_clock:
        window_start = (datetime.fromisoformat(first_clock['wall_utc']) - timedelta(seconds=first_clock['window_seconds'])).isoformat()
    environmental = read_environment = None
    environment_literal = result.get('environment_metadata_exact_string')
    if environment_literal is not None:
        read_environment = json.loads(environment_literal)
        environmental = {k: read_environment.get(k) for k in ('cursor', 'goal_tag', 'word', 'loads', 'criterion_auditor_only', 'action_codec', 'view_policy', 'episode')}
        environmental['sources'] = len(read_environment['objects'])
    counts = Counter(r['state'] for r in rows)
    if sum(r['Native_results_total_unique'] for r in rows) != result['completed_work']:
        raise ValueError('Plan ledger does not account for every archived Native result exactly once')
    return {'planned_work_opportunities': sum(r['opportunities_planned'] for r in rows),
        'completed_Native_work_results_archived': sum(r['Native_results_total_unique'] for r in rows),
        'submitted_pending_or_unresolved': counts['SUBMITTED_NO_COMPLETE_NATIVE_RESULT_ARCHIVED'],
        'failed_or_rejected_without_complete_Native_row': counts['FAILED_OR_REJECTED_WITHOUT_COMPLETE_NATIVE_ROW'],
        'not_sent': counts['NOT_SENT'],
        'partition_scope': 'Exactly one Native opportunity per frozen work event here; Native NULL is an archived result, not a formed WAIT. No unseen work is imputed.',
        'all_work_events': rows,
        'world_and_window': {
            'owner_started_paused_UTC': None if not starts else starts[0]['wall_utc'],
            'window_start_UTC_inferred_from_existing_clock': window_start,
            'last_journal_event_UTC': None if not tops else tops[-1].get('wall_utc'),
            'last_observed_window_clock_seconds_including_closing': None if not clocks else max(t['window_seconds'] for t in clocks),
            'exposure_abort_window_clock_seconds': None if not failures else failures[0].get('window_seconds'),
            'abort_error': None if not failures else failures[0].get('error'),
            'minimum_window_seconds_planned': plan['duration_seconds'],
            'clock_above_3600_does_not_mean_integrated_program_completed': True,
            'actually_clean_STOP': case['actual_clean_STOP'], 'endpoint_scope': case['endpoint_scope'],
            'unresolved_operator_ID': case.get('unresolved_ID'),
            'actual_source_phase_at_exported_commit': environmental,
            'source_phase_is_external_environment_not_Native_N': True,
        }}


def recalc(folder):
    index = read(folder / 'INDICE.json'); result = {'Native_ticks': 0, 'cases': [], 'checks': [], 'issues': []}
    for case in index['cases']:
        journal = gzip.decompress((folder / case['journal_export']).read_bytes())
        if sha(journal) != case['journal_original_SHA']: raise ValueError('Journal no longer byte exact')
        s = scan(journal)
        driver_returned = s['completed_work']
        known = {(r['episode'], r['tick']) for r in s['rows']}
        late_sources = []
        for archive in case.get('late_archived_results', []):
            b = gzip.decompress((folder / archive['export']).read_bytes())
            if sha(b) != archive['original_SHA']: raise ValueError('Late result bytes differ')
            # A serialized N0 parse is NOT an original event journal. Locator is explicit below.
            other = scan(json.dumps(json.loads(b), ensure_ascii=False, separators=(',', ':')).encode('utf8') + b'\n')
            for row in other['rows']:
                key = (row['episode'], row['tick'])
                if key in known: continue
                row['locator'] = archive['export'] + '::$parsed_original_JSON::' + row['locator']
                row['late_result_arrived_during_close_not_returned_to_driver'] = True
                s['rows'].append(row); known.add(key)
                late_sources.append({'request_id': archive['request_id'], 'episode': row['episode'],
                    'query_tick': row['tick'], 'source': archive['export']})
            s['checks'] += [{**c, 'late_archived_source': archive['export']} for c in other['checks']]
            s['issues'] += [{**c, 'late_archived_source': archive['export']} for c in other['issues']]
            for rid, witnesses in other['receipt_witnesses'].items():
                s['receipt_witnesses'].setdefault(rid, []).extend([{**w, 'late_archived_source': archive['export']} for w in witnesses])
        rr = sorted(s['rows'], key=lambda r: (r['tick'], r['episode']))
        s.update(rows=rr, completed_work=len(rr), driver_returned_work=driver_returned,
            late_additional_work_results=late_sources,
            action_counts=dict(Counter(str(r['action']) for r in rr)),
            eligible_work=sum(r['eligible'] for r in rr), old_gain=sum(r['recalculated_old_gain'] for r in rr),
            new_quality=sum(r['recalculated_new_quality'] for r in rr),
            correct_formed_WAIT=sum(r['correct_formed_WAIT'] for r in rr),
            formed_valid_actions=sum(r['action'] is not None for r in rr),
            NULL_or_ambiguous_completed_actions=sum(r['action'] is None for r in rr),
            not_useful_completed_actions=sum(not r['recalculated_new_quality'] for r in rr),
            distinct_source_ids=sorted({r['public']['source_id'] for r in rr}))
        physical = read(folder / case['physical_witness'])
        rb = gzip.decompress((folder / physical['raw_file']).read_bytes())
        cb = gzip.decompress((folder / physical['clock_file']).read_bytes())
        measured = buffer_summary(rb, cb, physical['N'])
        c = {'check': 'all_exact_RAW_clock_counters', 'case': case['case'], 'ok': measured == physical['measured']}
        result['checks'] += [c] + s['checks']
        result['issues'] += s['issues'] + ([] if c['ok'] else [c])
        delta = read(folder / case['receipt_delta'])
        terminal = {r['id']: r for r in delta['new_committed_receipts']}
        for row in s['rows']:
            refs = row['Native_receipt_IDs_referenced_by_row']
            witnessed = [terminal[rid] for rid in refs if rid in terminal]
            row['terminal_FULL_receipts_for_row'] = witnessed
            row['row_IDs_without_terminal_FULL_witness'] = [rid for rid in refs if rid not in terminal]
            row['row_Native_dose_counts'] = {
                'referenced_unique_IDs': len(refs), 'terminal_witnesses': len(witnessed),
                'applied': sum(r['status'] == 2 for r in witnessed),
                'rejected_occupied': sum(r['status'] == 5 for r in witnessed),
                'other_status_enum_counts': dict(Counter(str(r['status']) for r in witnessed if r['status'] not in (2, 5))),
                'unknown_not_imputed_zero': len(refs) - len(witnessed)}
            si = row['sensory_IDs_declared_in_frozen_sensor']
            gi = row['generic_only_IDs_declared_in_frozen_sensor']
            if set(si) & set(gi): raise ValueError('Sensor double-counted sensory and generic roles')
            row['sensory_terminal_FULL_receipts'] = [terminal[rid] for rid in si if rid in terminal]
            row['generic_only_terminal_FULL_receipts'] = [terminal[rid] for rid in gi if rid in terminal]
            row['sensory_admission_scope'] = {
                'declared_elementary_variables': 2, 'expected_material_signals': 3,
                'sensory_unique_IDs': len(si),
                'applied': sum(terminal[rid]['status'] == 2 for rid in si if rid in terminal),
                'rejected_occupied': sum(terminal[rid]['status'] == 5 for rid in si if rid in terminal),
                'unknown_IDs': [rid for rid in si if rid not in terminal],
                'all_three_applied': len(si) == 3 and all(rid in terminal and terminal[rid]['status'] == 2 for rid in si),
                'scope': 'Two elementary properties, encoded by two matched tag signals and one affine goal-bearing query. Admission is not semantic comprehension. A presented source whose cues were rejected is not counted as perceived.'}
        native_statuses = dict(Counter(str(r['status']) for r in delta['new_committed_receipts']))
        s.update(case=case['case'], life=case['life'], physical=measured,
            snapshot_tick=physical['tick'], actual_clean_STOP=case['actual_clean_STOP'],
            endpoint_scope=case['endpoint_scope'], new_committed_Native_IDs=len(delta['new_committed_receipts']),
            committed_Native_status_enum_counts=native_statuses, full_local_pair=case.get('full_local_pair'),
            unresolved_ID=case.get('unresolved_ID'),
            planned_work_opportunities=case['planned_work_opportunities'],
            submitted_but_not_returned_to_driver=s['work_requested_in_actual_submissions'] - driver_returned,
            submitted_without_any_archived_native_result=s['work_requested_in_actual_submissions'] - s['completed_work'],
            Native_inputs_applied_in_last_committed_scope=sum(r['status'] == 2 for r in delta['new_committed_receipts']),
            Native_inputs_rejected_occupied_in_last_committed_scope=sum(r['status'] == 5 for r in delta['new_committed_receipts']),
            no_status_assumed_for_uncommitted_future=not case['actual_clean_STOP'])
        s['environment_metadata_exact_string'] = physical['environment_metadata_exact_string']
        planfile = case.get('plan_export', 'EVIDENCIA/' + case['case'] + '/PLAN_REAL_CERRADO_ORIGINAL.json.gz')
        s['coverage_ledger'] = plan_and_world_ledger(read(folder / planfile), journal, s, case)
        result['cases'].append(s)
    result['attribution'] = {
        'DEE': 'Material two-bit inputs, existing selector history, Native encounters and frozen RAW readers yield an emission. USE may invoke Native lexicon and comparison.',
        'P0_host': 'Generic view/codec configuration, external objects/versions, environment cache/cursor, tool pipeline, fixed cadence and posteffect quality are prepared. New quality does not redefine old work gain.',
        'history': 'Same post10 common prefix for view arms, separate SAFE prefix for early reserve. Never sum diverged histories into MAIN.',
        'failure': 'Unclean STOP/process guard leaves a last committed observation plus unresolved operation, not a proven final complete future, content erasure or cognitive death.',
        'sample': 'Repeated opportunities/forks of a common prefix are dependent; source counts do not equal simultaneous inputs or acquired semantics.',
    }
    return result


def export(out, group):
    if out.exists(): raise FileExistsError('Create a new evidence revision, never overwrite')
    if group == 'views':
        defs = [(a, EV / ('VISTA_POST10_' + a + '_R02')) for a in ('CIRCULAR_REAL', 'PERSISTENTE_REAL', 'PERSISTENTE_OMIT')]
        parentpath = ROOT / 'sistema/estado/fuentes_emparejadas/APD04_WAIT_R03_REAL_AUX_R05_T654959_POST10_PRE_PANEL_R01/VIDA.deetsnap.gz'
        parentSHA = 'ff923a38f22fb510df2852455c2161d881d91f2a09bc27b6faf92488eb9c7291'
        codebase = HERE / 'EJECUTOR_TRES_VISTAS_REAL_POST10_N0_R02'
    else:
        defs = [('EARLY_PERSISTENT_REAL', EV / 'RESERVA60_PERSISTENCIA_TEMPRANA_REAL_R01')]
        parentpath = ROOT / 'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01/VIDA.deetsnap.gz'
        parentSHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
        codebase = HERE / 'RESERVA60_PERSISTENCIA_TEMPRANA_CERRADA_R01'
    for _, d in defs:
        if not (d / 'RESULTADO_SUPERVISION.json').is_file() or not (d / 'TRAYECTORIA/RESULTADO.json').is_file():
            raise ValueError('Trial not closed; no archive of a live future: ' + str(d))
        if read(d / 'RESULTADO_SUPERVISION.json')['final_total_job']['job_active_processes'] != 0:
            raise ValueError('Owner tree not closed')
    observerpath = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    spec = importlib.util.spec_from_file_location('exact_snapshot_parser_N0_no_Runtime', observerpath)
    obs = importlib.util.module_from_spec(spec); spec.loader.exec_module(obs)
    parent = obs.Snapshot(parentpath, verify_checksum=False)
    if parent.encoded_sha256 != parentSHA: raise ValueError('Declared common parent bytes differ')
    before = {r['id']: r for r in parent.receipts}
    out.mkdir(parents=True); originals = []
    def original(path, target):
        b = path.read_bytes(); z = gzip.compress(b, compresslevel=9, mtime=0)
        dest = out / target; dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as f: f.write(z)
        if gzip.decompress(dest.read_bytes()) != b: raise ValueError('Not byte-exact compression')
        originals.append({'source': str(path), 'source_SHA': sha(b), 'source_bytes': len(b),
            'export': target, 'export_SHA': sha(z), 'regenerates_exact_source_bytes': True})
        return target, sha(b)
    index = {'schema': 'APD04.view_and_reserve.R03.essential.N0.R08', 'group': group, 'cases': [],
        'parent_local': str(parentpath), 'parent_snapshot_SHA': parentSHA, 'parent_tick': parent.tick,
        'originals': originals, 'omissions': [
            'Complete snapshots, transport SQLite, worker queues and all live-operation in-memory futures remain local. Exported RAW/clocks/interfaces are not a full continuable state.',
            'The last committed snapshot of an unclean trial predates its unresolved operation; it is not a proven exact final future.',
            'Gzip CRC and encoded snapshot SHA verified; FNV not repeated here. Native import proof remains indexed.']}
    original(observerpath, 'CODIGO/observador_snapshot_N0.py.gz')
    for path in sorted(codebase.rglob('*')):
        if path.is_file(): original(path, 'CODIGO/EJECUTADO/' + path.relative_to(codebase).as_posix() + '.gz')
    for name, d in defs:
        final = read(d / 'TRAYECTORIA/RESULTADO.json'); sup = read(d / 'RESULTADO_SUPERVISION.json')
        command = sup['command']
        actual_plan_path = Path(command[command.index('--plan') + 1])
        plan = read(actual_plan_path)
        original(actual_plan_path, 'EVIDENCIA/' + name + '/PLAN_REAL_CERRADO_ORIGINAL.json.gz')
        planned_work = sum(int(sit.get('oportunidades', 0)) for ev in plan['events']
            for sit in ev.get('situations', []) if sit.get('modo') == 'apd04-vivir')
        card = final['final_record']; snap = obs.Snapshot(ROOT / 'sistema' / card['snapshot'], verify_checksum=False)
        if snap.encoded_sha256 != card['snapshot_sha256']: raise ValueError('Archived committed snapshot changed')
        clean = bool(final['owner_stop_confirmed'])
        endpoint_scope = 'Current exact final commit after confirmed STOP; operational FULL pair still needs its own seal.' if clean else 'LAST_COMMITTED_ONLY; unresolved operation future is not captured or proven identical.'
        stem = 'EVIDENCIA/' + name
        workIDs = {ev['request_id'] for ev in plan['events'] if any(sit.get('modo') == 'apd04-vivir' for sit in ev.get('situations', []))}
        late_archived = []
        sidecar = ROOT / 'sistema/estado' / card['persistent_service']['sidecar_directory']
        journal_scan = scan((d / 'TRAYECTORIA/EVENTOS.jsonl').read_bytes())
        driver_finished_ids = {ev['requested_id'] for ev in journal_scan['scheduled_events_seen']
            if ev['kind'] == 'scheduled_material_result'}
        for operation in card.get('operations', []):
            rid = operation.get('transport_id')
            if rid not in workIDs or rid in driver_finished_ids or 'result_file' not in operation: continue
            src = sidecar / operation['result_file']
            if sha(src.read_bytes()) != operation['result_sha256']: raise ValueError('Late Native result differs from committed authoritative record')
            target, digest = original(src, stem + '/RESULTADOS_TARDIOS/' + src.name + '.gz')
            late_archived.append({'request_id': rid, 'source': str(src), 'export': target,
                'original_SHA': digest, 'committed_record_result_SHA': operation['result_sha256'],
                'N0_only_no_GET_PUT_resume_or_pending_consumption': True})
        journalfile, journalSHA = original(d / 'TRAYECTORIA/EVENTOS.jsonl', stem + '/EVENTOS.jsonl.gz')
        original(d / 'TRAYECTORIA/RESULTADO.json', stem + '/RESULTADO_ORIGINAL.json.gz')
        original(d / 'RESULTADO_SUPERVISION.json', stem + '/SUPERVISION_ORIGINAL.json.gz')
        closure = d / 'CIERRE_BRAZO_Y_RESUMEN_N0.json'
        closed = read(closure) if closure.is_file() else None
        if closure.is_file(): original(closure, stem + '/CIERRE_BRAZO_ORIGINAL.json.gz')
        full = closed.get('postSTOP_seal') if closed else None
        raw = obs.pbytes(snap.raw); clock = obs.pbytes(snap.clocks)
        rf = stem + '/RAW_u64le.bin.gz'; cf = stem + '/CLOCK_u64le.bin.gz'
        for target, b in ((rf, raw), (cf, clock)):
            p = out / target; p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as f: f.write(gzip.compress(b, compresslevel=9, mtime=0))
        physical = {'N': snap.N, 'tick': snap.tick, 'snapshot_local': str(snap.path),
            'snapshot_encoded_SHA': snap.encoded_sha256, 'raw_file': rf, 'clock_file': cf,
            'measured': buffer_summary(raw, clock, snap.N), 'endpoint_scope': endpoint_scope,
            'interfaces': snap.channels, 'Native_pending': snap.pending,
            'environment_metadata_exact_string': snap.metadata.get('DEE.Cognitive.System.1.1.APD04.ecosystem.R01'),
            'complete_operational_snapshot_exported': False}
        pf = stem + '/TESTIGO_FISICO_ULTIMO_COMMIT.json'; emit(out / pf, physical)
        new = [r for r in snap.receipts if r['id'] not in before]
        inherited = {r['id']: r for r in snap.receipts if r['id'] in before}
        if inherited != before: raise ValueError('Inherited authoritative receipt history differs')
        df = stem + '/RECIBOS_FULL_ULTIMO_COMMIT_DELTA.json'
        emit(out / df, {'source_snapshot_SHA': snap.encoded_sha256, 'parent_SHA': parentSHA,
            'new_committed_receipts': new, 'inherited_receipts_exact_equal': True,
            'authority': 'Terminal status from this exact complete Native snapshot, union of every Native port/channel ID. Not a journal traversal heuristic.',
            'uncommitted_processing_future_not_counted': not clean})
        index['cases'].append({'case': name, 'life': card['life_id'], 'journal_export': journalfile,
            'journal_original_SHA': journalSHA, 'physical_witness': pf, 'receipt_delta': df,
            'actual_clean_STOP': clean, 'endpoint_scope': endpoint_scope,
            'unresolved_ID': (final['final_protocol'].get('pending_material') or {}).get('id'),
            'planned_work_opportunities': planned_work,
            'plan_export': 'EVIDENCIA/' + name + '/PLAN_REAL_CERRADO_ORIGINAL.json.gz',
            'late_archived_results': late_archived,
            'full_local_pair': full, 'frozen_sources_unchanged': final.get('frozen_sources_unchanged'),
            'wrapper_exit': sup.get('exit_code'), 'resource_accounting': sup['final_total_job'],
            'actual_wrapper_wall_seconds': sup.get('actual_wall_seconds')})
    emit(out / 'INDICE.json', index)
    shutil.copy2(Path(__file__), out / Path(__file__).name)
    result = recalc(out); emit(out / 'RECALCULO_CIENTIFICO.json', result)
    flat = []
    for case in result['cases']:
        for r in case['rows']:
            flat.append({'case': case['case'], 'life': case['life'], 'episode': r['episode'], 'query_tick': r['tick'],
                'source_id': r['public']['source_id'], 'tag': r['public']['tag'], 'goal': r['public']['goal_tag'],
                'action_RAW': r['RAW_sign'], 'action': r['action'], 'numeric_RAW': r['RAW_numeric_sign'],
                'requested_word': r['public']['word'], 'actual_numeric_tool': r['actual_numeric_tool'],
                'eligible': r['eligible'], 'old_gain': r['recalculated_old_gain'], 'new_quality': r['recalculated_new_quality'],
                'correct_formed_WAIT': r['correct_formed_WAIT'], 'cursor_before': r['cursor_before'], 'cursor_after': r['cursor_after'],
                'feedback': r['feedback']['modality'], 'primary_locator': r['locator']})
    if flat:
        with (out / 'OPORTUNIDADES.csv').open('x', encoding='utf8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(flat[0])); w.writeheader(); w.writerows(flat)
    emit(out / 'MANIFIESTO.json', {'self_hash_excluded': True, 'members': [
        {'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
        for p in sorted(out.rglob('*')) if p.is_file()]})
    if any(k.startswith('dee_thinking') for k in sys.modules): raise RuntimeError('Unexpected Native import')
    return result


def main():
    a = argparse.ArgumentParser(description=__doc__)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument('--inspect-journal', type=Path)
    g.add_argument('--export', type=Path)
    g.add_argument('--recalc', type=Path)
    a.add_argument('--group', choices=('views', 'early_reserve'), default='views')
    a.add_argument('--output', type=Path)
    args = a.parse_args()
    if args.inspect_journal:
        r = scan(args.inspect_journal.read_bytes())
        short = {k: r[k] for k in ('completed_work', 'action_counts', 'old_gain', 'new_quality', 'correct_formed_WAIT', 'eligible_work', 'distinct_source_ids', 'issues')}
        short['last_completed'] = None if not r['rows'] else {k: r['rows'][-1][k] for k in ('episode', 'tick', 'action', 'public', 'view_policy', 'cursor_before', 'cursor_after')}
    else:
        r = export(args.export, args.group) if args.export else recalc(args.recalc)
        short = {'cases': [{k: c[k] for k in ('case', 'completed_work', 'action_counts', 'old_gain', 'new_quality', 'correct_formed_WAIT', 'eligible_work', 'distinct_source_ids', 'actual_clean_STOP', 'new_committed_Native_IDs', 'committed_Native_status_enum_counts', 'unresolved_ID')} for c in r['cases']],
            'checks': len(r['checks']), 'issues': r['issues'], 'Native_ticks': 0}
    if args.output: emit(args.output, r)
    print(json.dumps(short, ensure_ascii=False))


if __name__ == '__main__': main()
