"""Complementary archive-only Full calculation. Stdlib; never imports DEE.

Frozen six RAW gates and finite lexical gates are the shipped helper's readers.
Criteria are Root's PRE-execution JSON, not fitted to observations. Journal
polling duplicates are identified by request ID + typed case + read tick, NOT
by equal charge/position as alleged physical lineage. No missing/NULL -> zero.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def unpack(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            pass
    return value


def walk(value, path='$'):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(unpack(item) if key in ('result', 'result_json') else item, path + '.' + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, path + '[' + str(index) + ']')


def decode(raw):
    if isinstance(raw, bool) or not isinstance(raw, (int, str)):
        raise ValueError('Exact uint64 integer/string required; floats forbidden')
    value = int(raw)
    if not 0 <= value < 2**64:
        raise ValueError('RAW outside uint64')
    return value & 0xffffffff, (value >> 60) & 15, [((value >> k) & 15) - (16 if ((value >> k) & 15) >= 8 else 0) for k in (48, 52, 56)]


def numeric(node):
    trial = node['native_trial']
    reader = trial['reader']
    panel = reader['observations']
    gates = {(15 + 2*x, 17, 15 + 2*z): [x, 1, z] for x in (-1, 0, 1) for z in (0, -1)}
    if len(panel) != 6 or {tuple(x['site']) for x in panel} != set(gates):
        raise ValueError('Six-site reader coverage differs')
    candidates = []
    for item in panel:
        state, semantic, direction = decode(item['raw'])
        if state and semantic == 1 and direction == gates[tuple(item['site'])]:
            candidates.append((item['site'][0] - 15) // 2)
    choice = candidates[0] if len(candidates) == 1 else None
    receipts = {}
    for _, item in walk(trial.get('requests', [])):
        if isinstance(item, dict) and 'id' in item and isinstance(item.get('receipt'), dict) and ('port' in item or 'channel' in item):
            receipts[str(item['id'])] = item['receipt'].get('status')
    return {'kind': node['kind'], 'case': {'value': trial.get('raw_sensor_value'),
            'loads': node.get('public_independent_loads')},
            'read_tick': trial.get('read_tick', reader.get('tick')),
            'query_tick': trial.get('query_tick'), 'sign_RAW': choice,
            'candidates_RAW': candidates, 'formed_unique': len(candidates) == 1,
            'NULL': not candidates, 'ambiguous': len(candidates) > 1,
            'stored_agrees': choice == node.get('physical_choice') == reader.get('choice'),
            'RAW_panel': panel, 'native_requested_distinct_IDs': len(receipts),
            'native_receipt_statuses': dict(Counter(receipts.values()))}


def lexical(reader):
    panel = reader['panel']
    origins = [((33, 33, 33), [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1)])]
    kind = len(panel)
    if kind >= 28:
        origins[0][1].extend([(-1, 0), (0, -1)])
        origins += [((47, 47, 47), [(-1, 0), (0, -1), (1, 0), (0, 1)]), ((47, 17, 47), [(1, 0), (0, 1)])]
    if kind >= 32:
        origins += [((47, 7, 47), [(-1, 0), (0, -1)] + ([(1, 0), (1, 1)] if kind == 36 else []))]
    expected = {((o[0]+4*x)%67, (o[1]+4*y)%67, (o[2]+z)%67) for o, ds in origins for x, y in ds for z in (-1, 1)}
    if kind not in (12, 28, 32, 36) or {tuple(x['site']) for x in panel} != expected:
        raise ValueError('Frozen finite lexical coverage differs')
    candidates = []
    for item in panel:
        state, semantic, direction = decode(item['raw'])
        if state and semantic == 1 and direction in ([0, 0, -1], [0, 0, 1]):
            candidates.append(direction[2])
    sign = candidates[0] if len(candidates) == 1 else None
    return sign, candidates, sign == reader.get('formed_native_command')


def recalculate(events, criteria, protocol):
    submissions = [e for e in events if e.get('event') == 'literal_material_submission']
    submit_ids = [e['id'] for e in submissions]
    results = [e for e in events if e.get('event') in ('literal_material_result', 'same_id_read_only_result')]
    nums, words, teachers, seen, conflicts, references = [], [], [], {}, [], []
    terminal, admission, polls, receipts = {}, {}, Counter(), {}
    for event_index, event in enumerate(results):
        request_id = event['id']
        if event['event'] == 'same_id_read_only_result':
            polls[request_id] += 1
        result = unpack(event.get('result', {}))
        row = result.get('request') or result
        if row.get('status'):
            terminal[request_id] = row['status']
        if result.get('admission'):
            admission[request_id] = result['admission']
        for locator, node in walk(result):
            if not isinstance(node, dict):
                continue
            if isinstance(node.get('receipt'), dict) and 'id' in node and ('port' in node or 'channel' in node):
                key = str(node['id'])
                value = {'status': node['receipt'].get('status'), 'channel': node.get('port', node.get('channel'))}
                if key in receipts and receipts[key] != value:
                    conflicts.append({'type': 'receipt_duplicate_conflict', 'id': key})
                receipts[key] = value
            kind = node.get('kind')
            if kind in ('APD04_candidate_scalar_classification', 'APD04_candidate_native_balance'):
                observation = numeric(node)
                key = (request_id, canon(observation['case']), observation['read_tick'])
                signature = canon(observation)
                if key in seen:
                    if seen[key] != signature:
                        conflicts.append({'type': 'numeric_ID_case_tick_conflict', 'key': key})
                    continue
                seen[key] = signature
                observation.update({'request_id': request_id, 'locator': locator, 'result_event_index': event_index})
                nums.append(observation)
            if kind in ('APD04_explicit_lexical_revision', 'APD04_explicit_lexical_lesson'):
                lesson = {k: node.get(k) for k in ('kind', 'form', 'teacher_sign', 'teacher_mode', 'revision', 'end_tick')}
                lesson['request_id'] = request_id
                lesson['receipts'] = [n['receipt']['status'] for _, n in walk(node.get('requests', [])) if isinstance(n, dict) and isinstance(n.get('receipt'), dict)]
                if lesson not in teachers:
                    teachers.append(lesson)
            reader = node.get('reader')
            if node.get('form') and isinstance(reader, dict) and 'panel' in reader and 'formed_native_command' in reader:
                sign, candidates, agrees = lexical(reader)
                entry = {'type': 'word', 'name': node['form'], 'request_id': request_id,
                         'read_tick': node.get('read_tick', reader.get('tick')), 'sign_RAW': sign,
                         'candidates_RAW': candidates, 'stored_agrees': agrees}
                if entry not in words:
                    words.append(entry)
            if isinstance(node.get('forms'), list) and isinstance(node.get('memories'), list):
                for family, field in (('word', 'forms'), ('memory', 'memories')):
                    for item in node[field]:
                        r = item['result']['reader']
                        sign, candidates, agrees = lexical(r)
                        entry = {'type': family, 'name': item.get('form', item.get('context')), 'request_id': request_id,
                                 'read_tick': item['result'].get('read_tick', r.get('tick')), 'sign_RAW': sign,
                                 'candidates_RAW': candidates, 'stored_agrees': agrees}
                        if entry not in words:
                            words.append(entry)
            # Passive reference readings remain scoped to their recorded tick;
            # they never change nominal expected signs or assert per-probe causes.
            if isinstance(node.get('references'), list):
                refs = node['references']
                bysite = {tuple(x.get('site', [])): x for x in refs if isinstance(x, dict)}
                if {(14,14,15), (16,14,15)} <= set(bysite):
                    pair = [bysite[(14,14,15)], bysite[(16,14,15)]]
                    sr = [(int(x['raw']) >> 32) & 65535 for x in pair]
                    ref = {'request_id': request_id, 'locator': locator, 'tick': [x.get('tick') for x in pair],
                           'raw': [str(x['raw']) for x in pair], 'right_minus_left': sr[1]-sr[0],
                           'nominal_reference_20_retained_at_this_observation': sr[1]-sr[0] == 20}
                    if ref not in references:
                        references.append(ref)
    probes = []
    for criterion in criteria['criteria']:
        matched = [n for n in nums if ((criterion['tipo'] == 'clasifica' and n['kind'] == 'APD04_candidate_scalar_classification' and n['case']['value'] == criterion['valor']) or
                    (criterion['tipo'] == 'equilibra' and n['kind'] == 'APD04_candidate_native_balance' and n['case']['loads'] == criterion['cargas']))]
        if criterion['probe'].startswith('EXACT_PENDING'):
            matched = [n for n in matched if n['request_id'] == protocol['pending_id']]
        states = []
        for node in matched:
            if node['ambiguous']:
                state = 'AMBIGUOUS'
            elif node['NULL']:
                state = 'NULL'
            elif not node['stored_agrees']:
                state = 'RAW_STORED_DISAGREEMENT'
            else:
                state = 'CORRECT_NOMINAL_SIGN' if node['sign_RAW'] == criterion['expected_native_sign'] else 'WRONG_NOMINAL_SIGN'
            states.append(state)
        offered = []
        for submission in submissions:
            if criterion['probe'].startswith('EXACT_PENDING') and submission['id'] != protocol['pending_id']:
                continue
            for _, case in walk(submission.get('payload', {})):
                if not isinstance(case,dict) or case.get('tipo') != criterion['tipo']:
                    continue
                matches = case.get('valor') == criterion.get('valor') if criterion['tipo']=='clasifica' else case.get('cargas') == criterion.get('cargas')
                if matches:
                    offered.append(submission['id'])
                    break
        request_states = {key: {'status':terminal.get(key), 'admission':admission.get(key)} for key in dict.fromkeys(offered)}
        missing = 'UNEXECUTED_NOT_SUBMITTED' if not offered else 'MISSING_RESULT_FOR_SUBMITTED_CASE'
        if offered and any(str(v.get('admission','')).startswith('rejected') or str(v.get('status','')).startswith('rejected') for v in request_states.values()):
            missing = 'REQUEST_REJECTED_NO_NUMERIC_OBSERVATION'
        elif offered and any(v.get('status') in ('pending','processing','queued','uncertain') for v in request_states.values()):
            missing = 'PENDING_OR_UNCERTAIN_NOT_A_NUMERIC_ERROR'
        probes.append({'criterion': criterion, 'distinct_observations': len(matched), 'states': states,
                       'submitted_case_request_IDs':list(dict.fromkeys(offered)), 'request_states':request_states,
                       'outcome': missing if not matched else (states[0] if len(states) == 1 else 'MULTIPLE_DISTINCT_OBSERVATIONS'),
                       'observations': matched})
    lesson = [x for x in teachers if x['form'] == 'clasifica' and x['revision']]
    lesson_end = lesson[0]['end_tick'] if len(lesson) == 1 else None
    word_groups = {}
    for item in words:
        word_groups.setdefault(item['type'] + ':' + item['name'], []).append(item)
    retention = []
    for name, rows in word_groups.items():
        ordered = sorted(rows, key=lambda x: (x['read_tick'] is None, x['read_tick'] or 0))
        first, last = ordered[0], ordered[-1]
        expected = -1 if name == 'word:clasifica' else first['sign_RAW']
        retention.append({'name': name, 'distinct_ID_tick_observations': len(rows), 'first': first, 'last': last,
                          'expected_after_single_revision': expected, 'final_formed_unique': len(last['candidates_RAW']) == 1,
                          'final_matches': len(last['candidates_RAW']) == 1 and last['sign_RAW'] == expected,
                          'scope': 'These ordered material queries only; not arbitrary future order or seed acquisition.'})
    pending_id = protocol['pending_id']
    after_lesson = [x for x in words if x['type']=='word' and x['name']=='clasifica' and lesson_end is not None and x['read_tick'] is not None and x['read_tick'] >= lesson_end]
    first_after = sorted(after_lesson,key=lambda x:x['read_tick'])[0] if after_lesson else None
    return {'schema': 'APD04.Full.complementary_sessions_recalculation.N0.R01', 'native_ticks_executed': 0,
            'not_a_global_PASS': True, 'numeric': probes, 'all_numeric_observations': nums,
            'teacher': {'distinct_lessons': teachers, 'exactly_one_clasifica_revision': len(lesson) == 1,
                        'single_revision_sign_minus': len(lesson) == 1 and lesson[0]['teacher_sign'] == -1,
                        'all_revision_receipts_applied': len(lesson) == 1 and bool(lesson[0]['receipts']) and set(lesson[0]['receipts']) == {'applied'},
                        'end_tick': lesson_end, 'first_clasifica_query_after_lesson':first_after,
                        'first_query_after_lesson_formed_minus': bool(first_after and first_after['sign_RAW']==-1 and len(first_after['candidates_RAW'])==1)}, 'retention_ordered_queries': retention,
            'native_receipts_unique': len(receipts), 'native_receipt_statuses': dict(Counter(x['status'] for x in receipts.values())),
            'transport': {'material_submissions': len(submissions), 'unique_submission_IDs': len(set(submit_ids)),
                          'duplicate_put_IDs': [k for k,v in Counter(submit_ids).items() if v > 1],
                          'pending_ID': pending_id, 'pending_put_count': submit_ids.count(pending_id),
                          'same_ID_read_only_poll_count': polls[pending_id], 'pending_latest_status': terminal.get(pending_id),
                          'complete_imports': sum(e.get('event') == 'explicit_complete_paired_import' for e in events)},
            'passive_reference_readings': references, 'duplicate_conflicts': conflicts,
            'limits': ['Numerical correctness does not imply learned arithmetic or competent autonomous policy.',
                       'Changed passive reference is reported separately; nominal criteria remain unchanged.',
                       'Exact ID/case/tick dedup identifies archived observations, not carrier lineage.',
                       'Full causal transport equality is checked by the independent Full helper, not inferred here.']}


def selftest():
    """Artificial fixtures, expressly NOT empirical DEE or unexecuted Full data."""
    def make(signs):
        panel = []
        for x in (-1,0,1):
            for z in (0,-1):
                raw = 0
                if (x,z) in signs:
                    raw = 1 | (1 << 60) | ((x & 15) << 48) | (1 << 52) | ((z & 15) << 56)
                panel.append({'site':[15+2*x,17,15+2*z], 'raw':str(raw), 'tick':123})
        choices = [x for x,z in signs]
        sign = choices[0] if len(choices)==1 else None
        return {'kind':'APD04_candidate_scalar_classification','physical_choice':sign,
                'native_trial':{'raw_sensor_value':43,'read_tick':123,'reader':{'observations':panel,'choice':sign}}}
    out = []
    for signs, expected in (([(1,-1)],1), ([(0,0)],0),([],None),([(-1,0),(1,0)],None)):
        got = numeric(make(signs))
        assert got['sign_RAW'] == expected
        assert got['formed_unique'] == (len(signs)==1)
        out.append({'synthetic_candidates': signs, 'sign':got['sign_RAW'],'formed_unique':got['formed_unique']})
    bad = make([(1,-1)])
    bad['native_trial']['reader']['observations'][0]['raw'] = 1.0
    try:
        numeric(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('float RAW accepted')
    criterion={'criteria':[{'probe':'DOCENCIA_NUEVA_scalar43','tipo':'clasifica','valor':43,'expected_native_sign':1}]}
    event={'event':'literal_material_result','id':'SYNTHETIC_NOT_DEE','result':{'request':{'status':'completed','result_json':json.dumps({'rows':[make([(1,-1)])]})}}}
    r=recalculate([event,dict(event,event='same_id_read_only_result')],criterion,{'pending_id':'ABSENT'})
    assert len(r['all_numeric_observations'])==1
    assert r['numeric'][0]['outcome']=='CORRECT_NOMINAL_SIGN'
    assert recalculate([],criterion,{'pending_id':'ABSENT'})['numeric'][0]['outcome']=='UNEXECUTED_NOT_SUBMITTED'
    submission={'event':'literal_material_submission','id':'SYNTHETIC_NOT_DEE','payload':{'situaciones':[{'modo':'apd04-calibrar','casos':[{'tipo':'clasifica','valor':43}]}]}}
    rejected={'event':'literal_material_result','id':'SYNTHETIC_NOT_DEE','result':{'admission':'rejected_fixture'}}
    assert recalculate([submission,rejected],criterion,{'pending_id':'ABSENT'})['numeric'][0]['outcome']=='REQUEST_REJECTED_NO_NUMERIC_OBSERVATION'
    uncertain=dict(rejected,result={'request':{'status':'uncertain'}})
    assert recalculate([submission,uncertain],criterion,{'pending_id':'ABSENT'})['numeric'][0]['outcome']=='PENDING_OR_UNCERTAIN_NOT_A_NUMERIC_ERROR'
    return {'all_fixtures_are_fabricated_test_vectors_NOT_Full_results':True,'native_ticks':0,
            'fixture_cases':out,'dedup_same_ID_case_tick':True,'float_rejected':True,'missing_not_zero':True}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sesiones',type=Path);p.add_argument('--criterio',type=Path)
    p.add_argument('--protocolo',type=Path);p.add_argument('--salida',type=Path)
    p.add_argument('--selftest',action='store_true');p.add_argument('--legacy-primary',type=Path)
    a=p.parse_args()
    if a.selftest:
        result=selftest()
    elif a.legacy_primary:
        result={'scope':'EXISTING archived calibration, NOT Full execution', 'native_ticks':0,
                'primary_sha256':sha(a.legacy_primary),'numeric':[numeric(n) for _,n in walk(json.loads(a.legacy_primary.read_bytes())) if isinstance(n,dict) and n.get('kind') in ('APD04_candidate_scalar_classification','APD04_candidate_native_balance')]}
    else:
        if not all((a.sesiones,a.criterio,a.protocolo)):
            p.error('Require --sesiones --criterio --protocolo, or explicitly synthetic --selftest')
        events=[json.loads(line) for line in a.sesiones.read_bytes().splitlines() if line.strip()]
        result=recalculate(events,json.loads(a.criterio.read_bytes()),json.loads(a.protocolo.read_bytes()))
        result['sources']={str(x):sha(x) for x in (a.sesiones,a.criterio,a.protocolo)}
    text=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    if a.salida:
        with a.salida.open('x',encoding='utf8',newline='\n') as f:f.write(text)
    else:print(text)
