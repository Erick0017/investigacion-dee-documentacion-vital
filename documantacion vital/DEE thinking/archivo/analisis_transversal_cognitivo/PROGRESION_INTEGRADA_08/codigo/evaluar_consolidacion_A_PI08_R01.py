"""Recalculate the fixed A2/A3 gates from closed actual primaries. Native0.

This witness is evidence for a Root decision, never a promotion or approval.
No scientific criterion, source protocol, response or original is modified.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, importlib.util, json

P = Path(__file__).resolve().parents[1]
P7 = P.with_name('PROGRESION_INTEGRADA_07')
S = P/'estados/RP_A01/sistema'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def primary(path):
    raw = read(path)
    require(raw['status'] == 'completed' and not raw.get('error'), 'Unclosed primary: '+str(path))
    value = json.loads(raw['result']) if isinstance(raw['result'], str) else raw['result']
    return value['result']['rows'][0]


def main():
    target = P/'control/EVALUACION_CONSOLIDACION_A_PI08_R01.json'
    require(not target.exists(), 'Preserve existing gate witness')
    evidence = []
    def witness(path):
        path = Path(path)
        evidence.append({'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)})
        return read(path)
    proofnames = ['RP_A01_REAL_PI08_R01.json', 'PI08_A2_PREVIAS_R01.json',
                  'PI08_A1_PRECONTROL_REAL_R01.json', 'PI08_A2_SUMINISTRO_R01.json',
                  'PI08_A1_POSTCONTROL_REAL_R02.json', 'PI08_A3_CONSUMIDOR32_R01.json',
                  'PI08_A2_REAPERTURA_R02.json']
    proofs = {name: witness(P/'control'/name) for name in proofnames}
    rp, prev, pre1, supply, post1, a3, reopen = (proofs[name] for name in proofnames)
    life = prev['life_id']
    require(all(proof.get('life_id', proof.get('life')) == life for proof in proofs.values()), 'Mixed life evidence')
    require(all(proof.get('closed', proof.get('coherent_closed')) is True for proof in proofs.values()), 'At least one actual phase is not coherently closed')
    require(all(v.get('error') is None for v in (prev, supply, a3, reopen)), 'Preserved phase error blocks A')
    require(prev['initial_tick'] == rp['actual_physical']['tick'] and prev['final_tick'] == supply['initial_tick']
            == supply['final_tick'] == a3['initial_tick'] and a3['final_tick'] == reopen['initial_tick'],
            'A trajectory is not one continuous coherent future')
    require(prev['all_planned_steps_executed'] and supply['all_planned_steps_executed'] and reopen['all_planned_steps_executed'], 'Incomplete fixed phase')
    for proof in (prev, supply, reopen):
        require(proof['protected_before'] == proof['protected_after'], 'Protected original principal changed')
        witness(proof['plan'])
    witness(a3['plan'])
    loader = importlib.util.spec_from_file_location('PI08_A_pure_collectors', P/'codigo/ejecutar_consolidacion_A2_PI08_R02.py')
    helper = importlib.util.module_from_spec(loader); loader.loader.exec_module(helper)
    unique = {}; counts = Counter(); summaries = []; rows_r3 = {}
    def add(label, path, kind):
        witness(path); row = primary(path)
        if kind == 'C2C':
            group, aliases, groups = helper.c2c_inputs(row)
        else:
            inner = row['result']['rows'][0] if kind == 'memory' else row
            group, aliases = helper.receipt_group(inner['requests']); groups = {'direct': len(group)}
        require(not set(unique).intersection(group), 'A prior Native ID was counted as a new event')
        unique.update(group); statuses = Counter(r['status'] for r in group.values()); counts.update(statuses)
        require(all(status == 'applied' or status.startswith('rejected') for status in statuses), 'Pending/unknown Native receipt')
        summaries.append({'label': label, 'primary': str(path), 'sha256': sha(path), 'group_counts': groups,
                          'unique_requested': len(group), 'status_counts': dict(statuses), 'aliases_not_new_events': aliases})
        return row
    rppath = P/'estados/RP_A01/ensayos'/rp['life']
    rppath = rppath.with_name(rp['life']+'_R03_OP04.json')
    rows_r3[4] = add('RP_R03_OP04', rppath, 'R03')
    data = {}
    for proof in (prev, reopen):
        for item in proof['rows']:
            kind = item.get('kind')
            if kind not in ('R03', 'C2C', 'public_FI', 'word', 'memory'):
                continue
            row = add(item['label'], item['primary'], kind); data[item['label']] = row
            if kind == 'R03':
                rows_r3[row['ordinal']] = row
    a3row = add('A3_C2C30', P/'ensayos/PI08_A3_CONSUMIDOR32_R01_C2C30.json', 'C2C')
    require(sorted(rows_r3) == list(range(4, 12)), 'All actual OP4..11 required')
    regulation = [{'ordinal': i, 'joint_useful': not row['actual_failed'],
                   'sensor_STATE': row['sensor']['actual_state_datum'], 'Native_choice': row['reader']['choice'],
                   'actual_motor': row['actual_motor'], 'pulse_scheduled': row['pulse_scheduled'],
                   'pulse_applied': row['pulse_applied'], 'FI_q4': row['FI']['early_physical_choice'],
                   'FI_q6': row['FI']['old_q6_choice'], 'message_offered': row['message']['required_payload'] is not None,
                   'message_delivered': row['message']['delivered_exact'], 'actual_failed': row['actual_failed']}
                  for i, row in sorted(rows_r3.items())]
    acquisition = sum(not rows_r3[i]['actual_failed'] for i in range(4, 8))
    finalrelation = sum(not rows_r3[i]['actual_failed'] for i in range(8, 12))
    usefulpulse = any(row['pulse_applied'] and not row['actual_failed'] for row in rows_r3.values())
    usefulmsg = any(row['message']['required_payload'] is not None and row['message']['delivered_exact'] and not row['pulse_scheduled'] for row in rows_r3.values())
    FI = []
    for label, left, right in [('FI_positive', 17, 6), ('FI_negative', 3, 14), ('FI_zero', 10, 10)]:
        row = data[label]; expected = (left > right)-(left < right)
        require(row['public_operands'] == {'izquierda': left, 'derecha': right} or row['public_operands'] == {'left': left, 'right': right}, 'Public operands differ')
        FI.append({'label': label, 'actual': row['early_physical_choice'], 'expected_evaluator_only': expected,
                   'correct': row['early_physical_choice'] == expected, 'material_zero_not_NULL': row['early_physical_choice'] == 0 if expected == 0 else None,
                   'explicit_new_public_contract': 'generic_return_failed' in row})
    memory = []
    for label, expected in [('word_luma', 1), ('word_nara', -1), ('memory_alfa', -1), ('memory_alfa_final', -1)]:
        row = data[label]; inner = row if label.startswith('word') else row['result']['rows'][0]
        observed = inner['reader']['formed_native_command']
        memory.append({'label': label, 'actual': observed, 'expected_evaluator_only': expected, 'correct': observed == expected})
    products = []
    for ordinal, row in [(28, data['C2C28']), (29, data['C2C29']), (30, a3row)]:
        product = row['actual_effect'].get('product')
        valid = False; artifact = None
        if row['useful_product'] and product is not None:
            folder = 'PI08_C2C_INTEGRACION_R01/dispositivo32' if ordinal == 30 else 'PI04_C2C_COORDINACION_R01/dispositivo'
            artifact = S/'estado/servicios_locales'/life/folder/product['path']
            content = artifact.read_bytes()
            valid = len(content) == product['bytes'] == 64 and sha(artifact) == product['sha256'] and int.from_bytes(content[:2], 'little') == row['actual_numeric_result']
            witness(artifact) if False else evidence.append({'path': str(artifact), 'bytes': len(content), 'sha256': sha(artifact)})
        products.append({'ordinal': ordinal, 'actual_Native_number': row['actual_numeric_result'], 'selected_operation': row['selected_operation'],
                         'second_motor': row['second_motor'], 'useful_product': row['useful_product'], 'actual_64B_product_valid': valid,
                         'expected_number_fed': False, 'path': str(artifact) if artifact else None})
    final_r3 = reopen['states']['post']['R03']['progress']; final_c2 = reopen['states']['post']['C2C']
    stable = final_r3['ordinal'] == 12 and not final_r3['pending'] and not final_r3['uncertain'] and final_c2['progress']['ordinal'] == final_c2['device']['ordinal'] == 31 and len(final_c2['device']['resources']) == 32 and not any(final_c2['device'].get(k) for k in ('pending', 'feedback_pending', 'uncertain'))
    causalpaths = [P7/'control/COMPARACION_R03_REAL_NOFAIL_YOKE_Y_CORTES_PI07_R02.json', P7/'control/GATES_R03_A_B_RECALCULADOS_PI07.json']
    for path in causalpaths:
        witness(path)
    def gate(criterion, result, paths):
        return {'criterion': criterion, 'result': bool(result), 'evidence': [{'path': str(path), 'sha256': sha(path)} for path in paths]}
    gates = {
      'functional_gain': gate('Fixed OP4..7 >=3/4joint, >=1 admitted useful pulse and >=1 actual message without pulse; bounded costs retained.', acquisition >= 3 and usefulpulse and usefulmsg, [P/'control/PI08_A2_PREVIAS_R01.json', P/'control/PI08_A2_REAPERTURA_R02.json']),
      'conservation': gate('New public FI+/−/material0 all3, named memory4/4, >=1/2oldC2C and mandatory actual new32product.', all(r['correct'] for r in FI+memory) and sum(r['actual_64B_product_valid'] for r in products[:2]) >= 1 and products[2]['actual_64B_product_valid'], [P/'control/PI08_A3_CONSUMIDOR32_R01.json', P/'control/PI08_A2_REAPERTURA_R02.json']),
      'causal_controls': gate('Reuse measured PI07 material controls; actual A1 queue PRE/POST prove real consumer/interrupt/idempotence, not claims of another new acquisition.', pre1['criteria_met'] and post1['criteria_met'] and all(pre1['full_Native_field_equalities'].values()) and all(post1['full_Native_field_equalities'].values()), causalpaths+[P/'control/PI08_A1_PRECONTROL_REAL_R01.json', P/'control/PI08_A1_POSTCONTROL_REAL_R02.json']),
      'source_reopening': gate('One continuous candidate, all actual phases closed, mandatory new32use, final coherent counters and finite remaining resource.', stable and a3['criteria_met'], [P/'control/PI08_A3_CONSUMIDOR32_R01.json', P/'control/PI08_A2_REAPERTURA_R02.json']),
      'new_function_at_final_cut': gate('After real close/reopen: OP8..11 >=3/4joint, real admitted pulse earlier and finalalpha; exact checked cuts stated, no complete panel atfinalTick.', finalrelation >= 3 and memory[-1]['correct'] and stable, [P/'control/PI08_A2_REAPERTURA_R02.json']),
      'decisive_recipe_replay': gate('Actual public RP frontdoor normal_op4 from complete learnedPOST4, completed/coherentlyclosed, exact prescribed physical and184applied.', rp['actual_Native_run'] and rp['local_criteria_met'] and rp['physical_coincidence'] and rp['coherent_closed'] and rp['Native_receipts']['applied'] == 184 and rp['Native_receipts']['unique_requested'] == 184, [P/'control/RP_A01_REAL_PI08_R01.json'])}
    output = {'schema': 'DEE.PI08.A.combined_actual_gates.R01', 'utc': datetime.now(timezone.utc).isoformat(),
       'life_id': life, 'N': 67, 'T': reopen['final_tick'], 'new_Native_ticks_executed_by_this_recalculation': 0,
       'gates': gates, 'all_fixed_evidence_gates_met': all(v['result'] for v in gates.values()),
       'approval': False, 'adoption_performed': False, 'Root_decision_required': True,
       'regulation_OP4_7_joint': {'correct': acquisition, 'total': 4}, 'regulation_OP8_11_joint': {'correct': finalrelation, 'total': 4},
       'regulation_actual_rows': regulation, 'public_FI': FI, 'named_memory': memory, 'C2C_products': products,
       'current_final_R03_ordinal': final_r3['ordinal'], 'current_final_C2C_ordinal': final_c2['progress']['ordinal'],
       'remaining': {'R03_offers': 18-final_r3['ordinal'], 'C2C_resources': 32-final_c2['device']['ordinal']},
       'Native_inputs_actual_deduplicated': {'unique_requested': len(unique), 'status_counts': dict(counts)},
       'Native_ticks_this_candidate_fromPOST4': reopen['final_tick']-849645,
       'actual_primary_denominators': summaries, 'evidence': evidence,
       'scope': 'Functional consolidation with explicit migrated public FI access and preserved real history. OP8 cost remains an error; no new12/12panel atfinalTick, no general agency, no learned sequence initiation, no false equality of old/new APIs.'}
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'path': str(target), 'sha256': sha(target), 'all_fixed_evidence_gates_met': output['all_fixed_evidence_gates_met'], 'gates': {k:v['result'] for k,v in gates.items()}, 'T': output['T']}, indent=2))


if __name__ == '__main__':
    main()
