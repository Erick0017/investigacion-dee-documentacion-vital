"""Passive, portable R06 comparison/AI-contract audit from CLOSED explicit files.

Reads an R03 report and the reference's own journals. No DEE, SQL, model,
Studio, HTTP, replay or inference. Output must be absent. No historical paths
inside input documents are opened. This is documentary recalculation only.
"""
from pathlib import Path
import argparse, csv, datetime, hashlib, json, math, statistics

ARMS = ('LIVE_NATIVE', 'PROGRAMMED', 'CONVENTIONAL_AI')
PERIODS = (('TOTAL', 5, 28), ('P1_ASISTIDO_RETENCION', 5, 10),
           ('P2_ASISTIDO_RESERVA', 11, 16), ('P3_ASISTIDO_CAMBIO', 17, 22),
           ('P4_Q2_SIN_SUSTITUCION', 23, 28))

def read(path, sources):
    p = Path(path).resolve(strict=True); before = p.stat(); raw = p.read_bytes()
    if (before.st_size, before.st_mtime_ns) != (p.stat().st_size, p.stat().st_mtime_ns):
        raise RuntimeError('Input changed during read')
    sources.append({'path': str(p), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    text = raw.decode('utf-8-sig')
    return [json.loads(s) for s in text.splitlines() if s.strip()] if p.suffix == '.jsonl' else json.loads(text)

def numeric(v):
    return type(v) in (int, float) and math.isfinite(v)

def summary(values):
    v = sorted(x for x in values if numeric(x))
    return {'n': len(v), 'sum': sum(v) if v else None,
            'p50': statistics.median(v) if v else None,
            'p95': v[max(0, math.ceil(.95 * len(v)) - 1)] if v else None,
            'max': v[-1] if v else None}

def write_csv(path, rows):
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open('x', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False, separators=(',', ':')) if isinstance(v, (dict, list)) else v for k, v in row.items()})

def audit_ai(policy, history):
    completed = {}
    for row in policy:
        if row.get('kind') != 'COMPLETED':
            continue
        key = row['operation_id']
        if key in completed and completed[key] != row:
            raise ValueError('Conflicting own-policy completion: ' + key)
        completed[key] = row
    responses = {}
    for row in history:
        if row.get('kind') != 'RESPONSE':
            continue
        key = row['call']
        if key in responses and responses[key] != row:
            raise ValueError('Conflicting model response call')
        responses[key] = row
    linked = []
    for identifier, row in completed.items():
        result = row['result']; call = result.get('evidence', {}).get('model_call')
        if call is None:
            continue
        if call not in responses:
            raise ValueError('Own completed inference has no raw model response')
        raw = responses[call]
        try:
            parsed = json.loads(raw['response_content'])
            json_valid = True
        except (KeyError, TypeError, ValueError):
            parsed = None; json_valid = False
        linked.append({'operation_id': identifier, 'model_call': call,
                       'backend_result': result, 'raw_choice': raw.get('choice'),
                       'response_content': raw.get('response_content'),
                       'json_syntax_valid': json_valid, 'raw_JSON': parsed,
                       'rejection_by_client': raw.get('rejection'),
                       'context_near_limit': raw.get('context_near_limit'),
                       'wall_seconds': raw.get('wall_seconds'),
                       'semantic_correction': raw.get('semantic_correction')})
    if len({r['model_call'] for r in linked}) != len(linked):
        raise ValueError('A model call was attributed to multiple operations')
    used = {r['model_call'] for r in linked}
    actions = [r for r in linked if r['operation_id'].endswith(('_DECISION', '_QUERY_SENSOR'))]
    funcs = [r for r in linked if r['operation_id'].endswith('_FUNCTION')]
    waits = [r for r in actions if r['backend_result'].get('action') == 'SAFE_WAIT']
    numeric_rows = [r for r in funcs if r['backend_result'].get('toolResult', {}).get('kind') == 'CALCULATE']
    ack = [r for r in funcs if r['backend_result'].get('toolResult', {}).get('kind') == 'LESSON']
    audit = {'schema': 'DEE.R06.closed_AI_contract_audit.R01',
             'backend_completed_unique_ids': len(completed), 'model_responses': len(responses),
             'linked_completed_inferences': len(linked),
             'unattributed_response_call_numbers': sorted(set(responses) - used),
             'feedback_without_inference': sum(k.endswith('_FEEDBACK') for k in completed),
             'action_inferences': len(actions), 'function_inferences': len(funcs),
             'world_SAFE_WAIT_outputs': len(waits),
             'voluntary_valid_world_waits': sum(r['backend_result'].get('voluntary_wait') is True and r['backend_result'].get('invalid') is False for r in waits),
             'world_wait_fallbacks_after_invalid_output': sum(r['backend_result'].get('invalid') is True for r in waits),
             'calculate_inferences': len(numeric_rows),
             'formed_integer_calculations': sum(type(r['backend_result'].get('toolResult', {}).get('numeric_result')) is int and r['backend_result']['toolResult'].get('formed') is not False for r in numeric_rows),
             'calculate_out_of_contract_SAFE_WAIT_null': sum(r['raw_choice'] == {'action': 'SAFE_WAIT', 'value': None} and r['backend_result'].get('invalid') is True for r in numeric_rows),
             'valid_visible_lesson_ACKs': sum(r['raw_choice'] == {'action': 'ACK', 'value': None} and r['backend_result'].get('invalid') is False for r in ack),
             'invalid_outputs_for_present_kind': sum(r['backend_result'].get('invalid') is True for r in linked),
             'JSON_syntax_errors_among_linked_responses': sum(not r['json_syntax_valid'] for r in linked),
             'linked_rows': linked,
             'interpretation': ['A global JSON action can still be invalid for the present phase.',
              'SAFE_WAIT/null at CALCULATE produced no integer and is an out-of-contract abstention, not a wrong arithmetic integer.',
              'A resulting World SAFE_WAIT after an invalid Q1 action is not a voluntary valid wait.',
              'A visible-lesson ACK is not proof of subsequent functional recall.'],
             'Native_model_or_Studio_executed_by_this_audit': False}
    return audit, completed

def comparison(report, completed):
    result = []
    for arm in ARMS:
        all_rows = sorted((r for r in report['new_opportunity_rows'] if r['participant'] == arm), key=lambda r: r['global_cycle'])
        for label, first, last in PERIODS:
            own = [r for r in all_rows if first <= r['global_cycle'] <= last]
            before = next((r['state_after_literal'] for r in reversed(all_rows) if r['global_cycle'] < first), None)
            before = before or {'permissionStock': 196, 'tollSpent': 0, 'worldTime': 40.75}
            after = own[-1]['state_after_literal'] if own else {}
            values = [r['numeric'] for r in own if r['numeric']]
            evaluable = [n for n in values if n['correct_for_actual_opcode'] is not None]
            wall = summary(v for r in own for v in r['operation_wall_seconds'].values())
            queries = sum(r['native_Q1_action'] == 'ASK_STATION' for r in own)
            deliveries = sum(r['resource_delivered'] for r in own)
            inherited = sum(r['resource_delivered'] and r['global_cycle'] == next((x['global_cycle'] for x in all_rows if x['resource_delivered']), None) for r in own) if report['parent_DEV4_exact_world_verified'] else None
            own_ids = {p for r in own for p in r['Native_phase_operation_ids']}
            ai_rows = [v['result'] for k, v in completed.items() if any(k.startswith('R06_' + str(r['session']) + '_' + str(r['global_cycle']).zfill(2) + '_') for r in own)] if arm == 'CONVENTIONAL_AI' else []
            toll = after.get('tollSpent', 0) - before.get('tollSpent', 0)
            spent = before.get('permissionStock', 0) - after.get('permissionStock', 0)
            result.append({'participant': arm, 'period': label, 'first_global_cycle': first,
              'last_global_cycle': last, 'offered_completed_opportunities': len(own),
              'planned_opportunities_in_period': last - first + 1,
              'Native_ticks_unique_completed_phase_ids': sum(r['Native_phase_ticks_unique'] for r in own),
              'Native_unique_phase_count': len(own_ids),
              'Q1_ASK': queries, 'Q1_SKIP': sum(r['native_Q1_action'] == 'SKIP_STATION' for r in own),
              'Q1_NULL_or_invalid_fallback': sum(r['native_Q1_NULL'] is True for r in own),
              'Q2_NULL': sum(r['native_Q2_NULL'] is True for r in own),
              'effective_route_overrides': sum(r['native_route_overridden'] for r in own),
              'prepared_assistance_contract_opportunities': sum(r['host_order_prepared'] is True for r in own),
              'numeric_opportunities': len(values), 'formed_numeric_results': sum(n['formed'] for n in values),
              'numeric_zero_valid': sum(n['zero_valid'] for n in values),
              'numeric_absent_or_NULL': sum(n['absent_or_NULL'] for n in values),
              'correct_for_actual_opcode': sum(n['correct_for_actual_opcode'] is True for n in values),
              'wrong_for_actual_opcode': sum(n['correct_for_actual_opcode'] is False for n in values),
              'arithmetic_evaluable_denominator': len(evaluable),
              'arithmetic_accuracy_evaluable': sum(n['correct_for_actual_opcode'] is True for n in evaluable) / len(evaluable) if evaluable else None,
              'formed_integer_fraction_of_numeric_opportunities': sum(n['formed'] for n in values) / len(values) if values else None,
              'lesson_opportunities': sum(r['function_kind'] == 'LESSON' for r in own),
              'partial_Native_lessons': sum(r['lesson_partial_admission'] for r in own),
              'new_resources_collected': sum(r['resource_collected'] for r in own),
              'delivered_total_in_continuation': deliveries, 'delivered_inherited_resource': inherited,
              'delivered_new_resources': deliveries - inherited if inherited is not None else None,
              'code_checks_accepted': sum(r['codes_accepted'] for r in own),
              'code_checks_rejected': sum(r['codes_rejected'] for r in own),
              'actual_generic_failures': sum(r['actual_material_failure'] is True for r in own),
              'permission_stock_before': before.get('permissionStock'), 'permission_stock_after': after.get('permissionStock'),
              'permission_cost': spent, 'query_cost_count': queries, 'toll_cost': toll,
              'cost_identity_queries_plus_toll': spent == queries + toll,
              'world_logical_seconds_delta': after.get('worldTime', 0) - before.get('worldTime', 0),
              'phase_wall_count': wall['n'], 'phase_wall_seconds_sum': wall['sum'],
              'phase_wall_seconds_p50': wall['p50'], 'phase_wall_seconds_p95_nearest': wall['p95'],
              'phase_wall_seconds_max': wall['max'],
              'AI_valid_voluntary_world_waits': sum(x.get('action') == 'SAFE_WAIT' and x.get('voluntary_wait') is True and x.get('invalid') is False for x in ai_rows) if arm == 'CONVENTIONAL_AI' else None,
              'AI_world_wait_invalid_fallbacks': sum(x.get('action') == 'SAFE_WAIT' and x.get('invalid') is True for x in ai_rows) if arm == 'CONVENTIONAL_AI' else None,
              'scope': 'One continued history per arm. Dynamic input projection matched, semantic/architectural preparation differs. Wall phases are not CPU, energy or equal-load efficiency. S.latency and legacy CUE_CONTINGENCY labels are not used as current measurements.'})
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('facts', 'policy-events', 'model-history', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError('New absent output required')
    sources = []; report = read(a.facts, sources)
    if report.get('schema') != 'DEE.RBX01.INTEGRAL.V2.passive_recalculation.R03':
        raise ValueError('Exact R03 passive report expected')
    policy = read(a.policy_events, sources); history = read(a.model_history, sources)
    audit, completed = audit_ai(policy, history); audit['sources'] = sources
    table = comparison(report, completed)
    if any(not r['cost_identity_queries_plus_toll'] for r in table):
        raise ValueError('Recorded resource cost mismatch')
    a.output.mkdir(parents=True)
    write_csv(a.output / 'COMPARACION_TRES_BRAZOS.csv', table)
    (a.output / 'AUDITORIA_SALIDAS_AI_R01.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (a.output / 'FUENTES_Y_LIMITES.json').write_text(json.dumps({'sources': sources, 'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'Native_model_Studio_executed': False, 'source_R03_issues': report['issues'],
      'limits': ['S.latency is inherited stale UI data, not an R06 latency measurement.',
       'Legacy CUE_CONTINGENCY8/14 labels are retained; structured frozen protocol and actual encounters/gate records define R06 timing.',
       'No strong efficiency/intelligence ranking follows from different priors, assistance and overlapping host work.',
       'One shared-prefix descendant per Native arm; no independent-n inference from pulses or deterministic copies.']}, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'output': str(a.output), 'comparison_rows': len(table), 'AI_backend_completed': audit['backend_completed_unique_ids'],
      'AI_model_inferences': audit['linked_completed_inferences'], 'Native_executed': False}))

if __name__ == '__main__':
    main()
