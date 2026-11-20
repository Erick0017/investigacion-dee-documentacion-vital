"""RBX01 async Native apparatus. Import is stdlib only and creates no world.

The caller is the existing official single owner in a complete RBX descendant.
Only local physical marker contact and a paid fresh station sample enter the inherited
physical apparatus. All graph, inventory, task and action animation are prepared.
No Python action policy, bank choice, RAW/clock edit, or historical offer use.
"""
from pathlib import Path
import hashlib, json, os, re, time

VERSION = 'DEE.RBX01.async_native.INTEGRAL.V3.R01'
KEY = 'DEE.Cognitive.RBX01.async_native.INTEGRAL.V3.R01'
CODE_SCOPE_KEY = 'DEE.Cognitive.RBX01.CODE_SCOPE_INTEGRAL_V3'
FOLDER = 'RBX07_NATIVE_INTEGRAL_V3'
SCOPE = Path(__file__).with_name('RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
Q1 = 'eci01-rbx01-decision'
Q2 = 'eci01-rbx01-query-sensor'
FEEDBACK = 'eci01-rbx01-feedback'
STATE = 'eci01-rbx01-estado'
FUNCTION = 'eci01-rbx01-function'
MODES = {Q1, Q2, FEEDBACK, STATE, FUNCTION}
SYSTEM_KEY = 'DEE.Cognitive.System.1.1.life.v1'
PROTECTED = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf8')).hexdigest()


def scope():
    c = json.loads(SCOPE.read_text('utf-8-sig'))
    need(c.get('schema') == 'DEE.RBX01.fixed_native_scope.INTEGRAL.V3.R01', 'Exact C02 R02 RBX scope')
    need(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_(MAIN|CTRL[0-9]?|LOAD[123]|PILOT)', c.get('life_id', '')), 'C02 descendant identity only')
    role_limits = {'main': 24, 'control': 6, 'load': 3, 'pilot': 3}
    need(c.get('role') in role_limits and c.get('max_cycles') == role_limits[c['role']]
         and c.get('max_ticks_per_cycle') == 4096, 'Prospective finite C02 role budget')
    need(c.get('max_total_ticks') == c['max_cycles'] * 4096 and c.get('max_raw_support') == 10000 and c.get('monitor_tick_block') == 16 and c.get('max_permission_stock') == 200,
         'Fixed Native and host safety bounds')
    need(c.get('source_tick') == 991187 and c.get('source_snapshot_sha256') ==
         'b3163197548980355c45c6ffd57d2785b3a5e75cf71d8de3afb6b6ffdd4722d1', 'Exact complete reached PAR28 source')
    need(type(c.get('native_cutoff_utc_epoch')) in (int, float) and
         c['native_cutoff_utc_epoch'] == 1794884820, 'Finite prospective integral cutoff03:07UTCNov17')
    need(c.get('last_new_cycle_utc_epoch') == 1794880800, 'No new integral Q1 after02:00UTCNov17')
    need(c.get('sealed') is True and c.get('sensor_codec') == 'products_v1' and c.get('parent_completed_opportunities') == 28, 'Root must seal prospective product sensor and exact DEV4 continuation')
    need(re.fullmatch(r'[0-9a-f]{64}', c.get('code_scope_manifest_sha256', '')), 'Frozen common C02 source manifest required')
    need(c.get('feedback_arm') in ('real', 'noaversive') and
         c.get('teacher_mode') in ('paired', 'desync', 'omitted'), 'Prospective feedback and teacher arms')
    need(set(c.get('sources_sha256', {})) ==
         {'rbx07_native_v3.py', 'rbx07_identity_v3.py', 'rbx07_funciones_v3.py'}, 'Complete pinned C02 source set')
    for name, expected in c.get('sources_sha256', {}).items():
        source = Path(__file__).with_name(name)
        if name == 'rbx07_funciones_v3.py' and not source.exists():
            source = Path(__file__).resolve().parents[1] / 'capacidades' / name
        need(Path(name).name == name and hashlib.sha256(source.read_bytes()).hexdigest() == expected,
             'Changed RBX pinned dependency: ' + name)
    return c


def identity(a):
    c = scope()
    root = Path(__file__).resolve().parents[1]
    need(not (root / 'estado/ACTIVO.json').exists(), 'RBX must remain unselected')
    from capacidades import pi10_transporte_ancestral_R01 as t
    i = t.identity(a)
    need(i['life_id'] == c['life_id'] and i['life_id'] != PROTECTED and
         i['profile'] == 'fisica_directa' and int(a.world.runtime.dimension) == 67,
         'Exact Root-owned N67 RBX descendant')
    return i


def ancestors(a):
    from capacidades import pi10_consulta_adaptativa_R02 as b
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return {key: entries[key] for key in (*b.PARENT_KEYS, b.KEY, 'DEE.Cognitive.RBX01.async_native.C02.R01', 'DEE.Cognitive.RBX01.CODE_SCOPE_C02_R01', 'DEE.Cognitive.RBX01.async_native.INTEGRAL.V2.R01', 'DEE.Cognitive.RBX01.CODE_SCOPE_INTEGRAL_V2') if key in entries}


def home(directory, a):
    base = Path(directory).resolve(strict=True)
    need(base.is_dir() and base.name == identity(a)['life_id'], 'Exact owned artifact home')
    for part in (base, *base.parents):
        need(not part.is_symlink() and not (getattr(part.lstat(), 'st_file_attributes', 0) & 1024), 'No linked artifact paths')
    return base / FOLDER


def get(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        return None
    value = json.loads(entries[KEY])
    need(value['version'] == VERSION, 'Exact RBX metadata')
    need(value.get('code_scope') == code_scope(), 'Frozen C02 code/role/scope changed')
    need(entries.get(CODE_SCOPE_KEY) == canonical(code_scope()), 'Native C02 source witness differs')
    return value


def save(a, m):
    text = canonical(m)
    need(len(text.encode('utf8')) <= 65536, 'RBX own metadata exceeds64KB')
    a.world.runtime.set_snapshot_metadata(KEY, text)


def record(a, directory, m, event):
    folder = home(directory, a)
    folder.mkdir(exist_ok=True)
    row = {'index': m['log_count'], 'tick': int(a.tick), **event}
    data = (canonical(row) + '\n').encode('utf8')
    proposed = dict(m, log_count=m['log_count'] + 1,
                    log_chain_sha256=hashlib.sha256(bytes.fromhex(m['log_chain_sha256']) + data).hexdigest())
    need(len(canonical(proposed).encode('utf8')) <= 65536, 'Metadata budget before journal')
    with (folder / 'events.jsonl').open('ab') as out:
        out.write(data); out.flush(); os.fsync(out.fileno())
    m.update(proposed)
    save(a, m)


def validate_literal(row):
    need(isinstance(row, dict) and row.get('modo') in MODES, 'Closed RBX mode')
    if row['modo'] == STATE:
        need(set(row) == {'modo'}, 'State only')
        return
    need(set(row) == {'modo', 'payload', 'context'}, 'Exact RBX literal')
    p, c = row['payload'], row['context']
    need(isinstance(p, dict) and isinstance(c, dict) and
         set(c) == {'session_id', 'sequence', 'observation_id', 'operation_id', 'mode'}, 'Exact correlation context')
    for key in ('session_id', 'observation_id', 'operation_id'):
        need(isinstance(c[key], str) and re.fullmatch(r'[A-Za-z0-9_-]{1,96}', c[key]), 'Finite correlation identifier')
    need(type(c['sequence']) is int and 0 <= c['sequence'] <= 1000 and c['mode'] == 'LIVE_NATIVE', 'Native session/sequence')
    need(len(canonical(row).encode('utf8')) <= 7168, 'Finite Native payload')
    if row['modo'] == FUNCTION:
        need(set(p) == {'tool'}, 'Only visible environmental tool experience')
        validate_tool(p['tool'])
        return
    if row['modo'] in (Q1, Q2):
        need(set(p) == {'observation'}, 'Observation only')
        o = p['observation']
        need(isinstance(o, dict) and set(o) == {'observationId', 'seq', 'phase', 'worldTimeMs', 'sampleTimeMs', 'previousActionId', 'sensors'}, 'Fixed observation fields')
        need(o['observationId'] == c['observation_id'] and o['seq'] == c['sequence'], 'Observation correlation')
        need(o['phase'] == ('QUERY_CHOICE' if row['modo'] == Q1 else 'ROUTE_CHOICE'), 'Phase mismatch')
        need(type(o['worldTimeMs']) is int and type(o['sampleTimeMs']) is int and
             0 <= o['sampleTimeMs'] <= o['worldTimeMs'] <= 86400000, 'World sample clock')
        s = o['sensors']
        need(isinstance(s, dict) and set(s) == {'station', 'stage', 'contact', 'inventoryKey', 'inventoryResource', 'queryAvailable', 'stationSignal', 'permissionStock', 'publicContactCode', 'lastFailure', 'numberAPresent', 'codeBPresent', 'numberAVersion', 'codeBCurrent', 'goalDelivery'}, 'Fixed integral product sensor vocabulary')
        for key, low, high in (('station', 0, 5), ('stage', 0, 3), ('contact', 0, 4), ('permissionStock', 0, 200), ('stationSignal', -1, 2)):
            need(type(s[key]) is int and low <= s[key] <= high, 'Finite sensor: ' + key)
        need(type(s['publicContactCode']) is int and 0 <= s['publicContactCode'] <= 5, 'Finite local zone contact0..5')
        need(all(type(s[key]) is bool for key in ('inventoryKey', 'inventoryResource', 'queryAvailable', 'lastFailure', 'numberAPresent', 'codeBPresent', 'codeBCurrent', 'goalDelivery')), 'Boolean sensors')
        need(type(s['numberAVersion']) is int and 0 <= s['numberAVersion'] <= 31, 'Actual A version0..31')
        need(s['goalDelivery'] is True, 'Prepared fixed delivery goal flag')
        need(not s['codeBCurrent'] or s['codeBPresent'] and s['numberAPresent'], 'B freshness requires real A/B presence')
        if row['modo'] == Q1:
            need(s['stationSignal'] == -1, 'No hidden station content in Q1')
    else:
        need(set(p) == {'actionId', 'seq', 'observationId', 'worldTimeMs', 'durationMs',
                       'outcome', 'collision', 'resourceCollected', 'resourceDelivered',
                       'permissionSpent', 'materialConsequence', 'lastObservation'}, 'Closed actual feedback fields')
        need(type(p.get('materialConsequence')) is bool, 'Actual generic material consequence bool')
        need(isinstance(p.get('actionId'), str) and re.fullmatch(r'[A-Za-z0-9_-]{1,91}', p['actionId']), 'Exact actual action acknowledgement')
        need(p['seq'] == c['sequence'] and p['observationId'] == c['observation_id'], 'Feedback observation correlation')
        need(all(type(p[key]) is bool for key in ('collision', 'resourceCollected', 'resourceDelivered')), 'Finite actual feedback bits')
        need(type(p['permissionSpent']) is int and 0 <= p['permissionSpent'] <= 3, 'Actual permission cost')
        need(all(type(p[key]) is int and 0 <= p[key] <= 86400000 for key in ('worldTimeMs', 'durationMs')), 'Finite actual feedback times')
        need(isinstance(p['outcome'], str) and len(p['outcome']) <= 64, 'Finite actual outcome label')
        need(isinstance(p['lastObservation'], dict), 'Exact last permitted observation required')
        prior = p['lastObservation']
        validate_literal({'modo': Q1 if prior.get('phase') == 'QUERY_CHOICE' else Q2,
                          'payload': {'observation': prior}, 'context': c})


def validate(a, row):
    validate_literal(row)
    identity(a)
    prior = json.loads(dict(a.world.runtime.snapshot_metadata_entries).get('DEE.Cognitive.RBX01.async_native.INTEGRAL.V2.R01', '{}'))
    need(prior.get('cycles') == 24 and prior.get('last_sequence') == 56 and prior.get('phase') == 'IDLE' and prior.get('uncertain') is False, 'Exact exhausted inherited R06 apparatus must remain intact')
    if row['modo'] == STATE:
        return
    m = get(a)
    if m is None:
        need(row['modo'] == Q1 and int(a.tick) == scope()['source_tick'], 'First integral input at exact PAR28 source, not T0')
        need(time.time() < scope()['last_new_cycle_utc_epoch'], 'Prospective first-Q1 deadline reached')
        need(row['context']['sequence'] > 56, 'New epoch continues the inherited seq56; never replay prior opportunities')
        return
    need(not m['uncertain'], 'Preserved uncertainty: no retry/repair')
    c = row['context']
    need(c['session_id'] == m['session_id'], 'One session for this life')
    need(m['phase'] == {Q1: 'IDLE', Q2: 'AWAIT_ROUTE_SENSOR', FUNCTION: 'AWAIT_WORLD_CONSEQUENCE', FEEDBACK: 'AWAIT_WORLD_CONSEQUENCE'}[row['modo']], 'Durable phase mismatch')
    if row['modo'] == Q1:
        need(m['cycles'] < scope()['max_cycles'], 'Finite RBX supply exhausted')
        need(time.time() < scope()['last_new_cycle_utc_epoch'], 'Prospective last new-Q1 deadline reached')
        need(c['sequence'] > m['last_sequence'], 'New observation sequence must advance')
    else:
        need(c['sequence'] >= m['pending']['context']['sequence'], 'Stale phase observation')
    if row['modo'] == FUNCTION:
        need('q2_reader' in m['pending'] and not m['pending'].get('function_used'),
             'One function only after actual Q2 in this opportunity')


class HostSafetyStop(RuntimeError):
    pass


class BoundedTime:
    """Owner/agenda advances in <=16ticks, RAW-support checked each block."""
    def __init__(self, a, initial, cycle_start):
        self.a, self.initial, self.cycle_start, self.samples = a, initial, cycle_start, []

    def run_until(self, end):
        c = scope()
        need(int(end) >= int(self.a.tick), 'No rewind')
        need(int(end) - self.initial <= c['max_total_ticks'], 'Total Native budget')
        need(int(end) - self.cycle_start <= c['max_ticks_per_cycle'], 'Prospective whole-cycle Native budget')
        need(time.time() < c['native_cutoff_utc_epoch'], 'Finite Native wall cutoff')
        while int(self.a.tick) < int(end):
            need(time.time() < c['native_cutoff_utc_epoch'], 'Finite Native wall cutoff')
            self.a.run_until(min(int(end), int(self.a.tick) + 16))
            support = sum(int(x) != 0 for x in self.a.world.runtime.raw_copy())
            self.samples.append({'tick': int(self.a.tick), 'RAW_nonzero_support': support})
            if support > c['max_raw_support']:
                raise HostSafetyStop('HOST_SAFETY_STOP RAWsupport>10000; preserve')


def result(a, start, action=None, **fields):
    return {'version': VERSION, 'nativeTick': int(a.tick),
            'nativeTicks': int(a.tick) - start, 'action': action, **fields}


def execute(a, row, directory):
    validate(a, row)
    if row['modo'] == STATE:
        return result(a, int(a.tick), progress=get(a))
    from capacidades import pi10_consulta_adaptativa_R02 as b
    h, g, d, exact, receipt = b.native()
    start = int(a.tick)
    m = get(a)
    if m is None:
        a.world.runtime.set_snapshot_metadata(CODE_SCOPE_KEY, canonical(code_scope()))
        m = {'version': VERSION, 'code_scope': code_scope(), 'session_id': row['context']['session_id'], 'initial_tick': start,
             'cycles': 0, 'last_sequence': 56, 'parent_completed_opportunities': 28, 'phase': 'IDLE', 'pending': None,
             'uncertain': False, 'log_count': 0, 'log_chain_sha256': '00' * 32}
    old = ancestors(a)
    cycle_start = int(a.tick) if row['modo'] == Q1 else m['pending']['start_tick']
    timer = BoundedTime(a, m['initial_tick'], cycle_start)
    m['uncertain'] = True
    record(a, directory, m, {'kind': 'PHASE_INTENT', 'mode': row['modo'], 'payload': row['payload'], 'context': row['context']})
    try:
        if row['modo'] == Q1:
            out = first(a, row, m, timer, b, h, g, d, exact)
        elif row['modo'] == Q2:
            out = second(a, row, m, timer, b, h, g, d, exact, receipt)
        elif row['modo'] == FUNCTION:
            out = function(a, row, directory, m, timer, b)
        else:
            out = feedback(a, row, m, timer, b, h, g, d, exact)
        need(ancestors(a) == old, 'Acquired ancestor progress changed')
        need(int(a.tick) - m['initial_tick'] <= scope()['max_total_ticks'], 'Total budget exceeded')
        m['uncertain'] = False
        record(a, directory, m, {'kind': 'PHASE_COMPLETED', 'mode': row['modo'], 'result': out,
                                 'monitor_samples': timer.samples, 'ancestor_metadata_literal': True})
        return out
    except BaseException as exc:
        m['uncertain'] = True
        m['failure'] = {'type': type(exc).__name__, 'tick': int(a.tick), 'no_automatic_retry': True}
        save(a, m)
        raise


def contact_datum(sensors):
    code = sensors['publicContactCode']
    need(type(code) is int and 0 <= code <= 5, 'Fixed local physical contact0..5')
    need(all(type(sensors[k]) is bool for k in ('inventoryKey', 'inventoryResource', 'lastFailure')),
         'Literal C02 local percept bits')
    need(all(type(sensors[k]) is bool for k in ('numberAPresent','codeBPresent','codeBCurrent','goalDelivery')), 'Exact product/goal sensor bits')
    need(type(sensors['numberAVersion']) is int and 0 <= sensors['numberAVersion'] <= 31, 'Actual A version0..31')
    return (1 + code + 8*int(sensors['inventoryKey']) + 16*int(sensors['inventoryResource']) + 32*int(sensors['lastFailure'])
            +64*int(sensors['numberAPresent'])+128*int(sensors['codeBPresent'])+256*int(sensors['codeBCurrent'])
            +512*sensors['numberAVersion']+16384*int(sensors['goalDelivery']))


def station_datum(signal, queried, actual_tag):
    need(type(queried) is bool and type(signal) is int, 'Literal paid-sample admission')
    need(type(actual_tag) is int and 0 <= actual_tag <= 5, 'Actual local public contact0..5')
    if queried:
        need(signal in (0, 1, 2), 'Actual local price signal0/1/2')
        c = scope(); arm = c['q2_sensor_arm']
        need(c['q2_sensor_codec'] == 'price_tag_v1' and arm in ('local_tag','constant_tag2'), 'Frozen Q2 cue contract')
        submitted_tag = actual_tag if arm == 'local_tag' else 2
        return signal + 3*submitted_tag
    need(signal == -1, 'NoQuery retains absent signal')
    return None


def require_applied(rows, label):
    need(all(r['receipt']['id'] == r['id'] and r['receipt']['status'] == 'applied' for r in rows),
         label + ': not every requested pulse applied; preserve partial future, no retry')


def code_scope():
    c = scope()
    return {'schema': 'DEE.RBX01.CODE_SCOPE_INTEGRAL_V3', 'life_id': c['life_id'],
            'scope_sha256': hashlib.sha256(SCOPE.read_bytes()).hexdigest(),
            'code_scope_manifest_sha256': c['code_scope_manifest_sha256'],
            'sources_sha256': c['sources_sha256'], 'feedback_arm': c['feedback_arm'],
            'teacher_mode': c['teacher_mode'],
            'input_codec': c['input_codec'], 'max_raw_support': c['max_raw_support'], 'sensor_codec': c['sensor_codec'], 'q2_sensor_codec': c['q2_sensor_codec'], 'q2_sensor_arm': c['q2_sensor_arm'], 'parent_completed_opportunities': 28,
            'source_tick': c['source_tick'], 'source_snapshot_sha256': c['source_snapshot_sha256']}


def first(a, row, m, timer, b, h, g, d, exact):
    start = int(a.tick)
    observation = row['payload']['observation']
    r1 = g.bank_observations(a, d, exact, (24, 12, 12))
    r2 = g.bank_observations(a, d, exact, g.OLD_ORIGIN)
    need(r1['reference_clocks'][0] % 782 == r1['reference_clocks'][1] % 782 and
         r2['reference_clocks'][0] % 782 == r2['reference_clocks'][1] % 782, 'Phase mismatch; no clock repair')
    calendar = g.two_selector_calendar(start, r1['reference_clocks'][0], r2['reference_clocks'][0])
    one = calendar['first']; q1 = one['query_tick']; requests = []
    p = {'context': row['context'], 'calendar': calendar, 'start_tick': start,
         'initial_observation': observation, 'requests': requests,
         'q1_references_before': r1, 'q2_references_before': r2}
    m['pending'] = p
    # Fixed physical contact transduction, not a target/action/route label.
    datum = contact_datum(observation['sensors'])
    timer.run_until(q1 - 1)
    requests.extend(h.submit_query(a.world, q1, prefix='PI10.Q1.TC.R01'))
    b.submit(a, 'PI10.Q1.TC.R01.datum', datum, q1 + 3, requests)
    timer.run_until(q1 + 4)
    reader = g.read_central(a, d, exact, (24, 12, 12), q1)
    motor = g.actual_motor(reader['choice'])
    if motor is not None:
        requests.append(h.submit_motor_copy(a.world, motor, one['seed_tick'], prefix='PI10.Q1.TC.R01'))
    available = observation['sensors']['queryAvailable'] and observation['sensors']['permissionStock'] > 0
    question = b.submit(a, b.QUESTION_CHANNEL, 0, one['seed_tick'], requests) if motor == 1 and available else None
    timer.run_until(q1 + 8)
    question_sample = b.observe(a, b.QUESTION_READER)
    completed = b.receipts(a, requests)
    require_applied(completed, 'Q1 requested input')
    question_receipt = next((r for r in completed if question is not None and r['id'] == question['id']), None)
    released = bool(question_receipt and question_receipt['receipt']['status'] == 'applied' and
                    int(question_sample['state']) > 0 and int(question_sample['semantic']) == 1 and list(question_sample['direction']) == [1, 0, 0])
    action = 'SAFE_WAIT' if motor is None else 'ASK_STATION' if released else 'SKIP_STATION'
    p.update(q1_reader=reader, q1_motor=motor, question_released=released,
             public_contact_datum=datum, question_observation=question_sample,
             requests=completed, q1_action=action)
    m['phase'] = 'AWAIT_ROUTE_SENSOR' if motor is not None else 'AWAIT_WORLD_CONSEQUENCE'
    return result(a, start, action, null=motor is None, reader='PI10 fixed central q+4',
                  codec='Q1 +1 -> paid ASK if actual question applies; -1/0 -> SKIP; NULL -> SAFE_WAIT',
                  evidence={'calendar': calendar, 'reader': reader, 'question_receipt': question_receipt,
                            'question_observation': question_sample,
                            'input': {'publicContactCode': observation['sensors']['publicContactCode'],
                                      'physical_datum_state': datum},
                            'Native_inputs': b.summary(completed), 'all_requested_applied': True,
                            'sensor_scope': 'Fixed prepared scalar zone/inventory/failure/A-B-presence/B-freshness/A-version/delivery-goal. No expected numeric value or optimal route. Scalar discrimination is not proof of native bit parsing.'})


def second(a, row, m, timer, b, h, g, d, exact, receipt):
    start = int(a.tick); p = m['pending']; observation = row['payload']['observation']
    original = p['initial_observation']; signal = observation['sensors']['stationSignal']
    need(observation['sensors']['station'] == original['sensors']['station'], 'Station changed before route')
    need(observation['sampleTimeMs'] >= original['worldTimeMs'], 'Fresh post-Q1 station sample')
    datum = station_datum(signal, p['question_released'], observation['sensors']['publicContactCode'])
    expected_stock = original['sensors']['permissionStock'] - int(p['question_released'])
    need(observation['sensors']['permissionStock'] == expected_stock,
         'Real station query consumes exactly one environmental permit')
    calendar = p['calendar']; two = calendar['second']; q2 = two['query_tick']; requests = p['requests']
    requests.extend(h.submit_query(a.world, q2, prefix=g.OLD_PREFIX))
    # Absence is physical omission, never an invented zero or NULL decision.
    datum_request = None
    if datum is not None:
        datum_request = b.submit(a, g.OLD_PREFIX + '.datum', datum, q2 + 3, requests)
    timer.run_until(q2 + 4)
    reader = g.read_central(a, d, exact, g.OLD_ORIGIN, q2); motor = g.actual_motor(reader['choice'])
    copied = None
    if motor is not None:
        copied = h.submit_motor_copy(a.world, motor, two['seed_tick'], prefix=g.OLD_PREFIX); requests.append(copied)
    timer.run_until(q2 + 8)
    copy_receipt = receipt(a.world.runtime.receipt(copied['id'])) if copied else None
    completed = b.receipts(a, requests)
    require_applied(completed, 'Q2 requested input')
    action = 'SAFE_WAIT' if motor is None else 'EXIT_1' if motor == 1 else 'EXIT_0'
    p.update(route_observation=observation, q2_reader=reader, q2_motor=motor, q2_action=action,
             q2_copy_receipt=copy_receipt, requests=completed, action_id=row['context']['operation_id'])
    m['phase'] = 'AWAIT_WORLD_CONSEQUENCE'
    return result(a, start, action, null=motor is None, reader='PI07 fixed central q+4',
                  codec='Q2 +1->EXIT_1; -1/0->EXIT_0; NULL->SAFE_WAIT',
                  evidence={'reader': reader, 'copy_receipt': copy_receipt,
                            'station_sample': observation, 'physical_datum': datum, 'q2_sensor_codec': scope()['q2_sensor_codec'], 'q2_sensor_arm': scope()['q2_sensor_arm'], 'raw_price': signal, 'actual_tag': observation['sensors']['publicContactCode'], 'submitted_tag': (observation['sensors']['publicContactCode'] if scope()['q2_sensor_arm']=='local_tag' else 2) if p['question_released'] else None,
                            'datum_request': datum_request, 'datum_omitted': datum is None,
                            'Native_inputs': b.summary(completed), 'all_requested_applied': True,
                            'input_scope': 'Only fresh paid local stationSignal0/1/2 direct datum; NoQuery omits datum, no goal/route/inventory/coordinate input'})


def validate_tool(tool):
    need(isinstance(tool, dict) and tool.get('kind') in ('LESSON', 'CALCULATE'),
         'Only physically visible lesson or calculation; NONE has no function RPC')
    if tool['kind'] == 'LESSON':
        need(set(tool) == {'kind', 'items'} and isinstance(tool['items'], list)
             and 1 <= len(tool['items']) <= 2, 'One or two environmental experiences')
        forms = []
        for item in tool['items']:
            need(isinstance(item, dict) and set(item) == {'form', 'observedSign'}
                 and item['form'] in ('luma', 'nara') and type(item['observedSign']) is int
                 and item['observedSign'] in (-1, 1), 'Actual visible signed experience only')
            forms.append(item['form'])
        need(len(set(forms)) == len(forms), 'Distinct forms per lesson opportunity')
    else:
        need(set(tool) == {'kind', 'slot', 'form', 'left', 'right'}
             and tool['slot'] in ('A', 'B') and tool['form'] in ('luma', 'nara'),
             'Fixed prepared calculation tool; no expected result')
        need(tool['left'] is None or type(tool['left']) is int and 0 <= tool['left'] <= 32,
             'Actual left operand0..32 or explicit absent None; never zero fill')
        need(type(tool['right']) is int and 0 <= tool['right'] <= 32,
             'Independent visible right operand0..32')
    return tool


class TimedAdapter:
    """Forward the existing owner; route every helper advance through safety."""
    def __init__(self, adapter, timer):
        self._adapter, self._timer = adapter, timer

    def __getattr__(self, name):
        return getattr(self._adapter, name)

    def run_until(self, tick):
        return self._timer.run_until(tick)


def normalized_requests(value):
    """Normalize legacy receipts without treating missing fields as zero.

    The full source tree remains byte-for-byte represented in the primary.
    Aliases are deduplicated by actual owner receipt ID, never counted twice.
    """
    found = {}
    def visit(v):
        if isinstance(v, list):
            for item in v:
                visit(item)
        elif isinstance(v, dict):
            if 'id' in v and ('channel' in v or 'port' in v):
                channel = v.get('channel', v.get('port'))
                payload = v['payload'] if 'payload' in v else v.get('value')
                tick = v['requested_tick'] if 'requested_tick' in v else v.get('tick')
                need(type(v['id']) is int and isinstance(channel, str)
                     and type(payload) is int and type(tick) is int,
                     'Exact receipt ID/channel/payload/tick required; no zero fill')
                row = {'id': v['id'], 'channel': channel, 'payload': payload,
                       'requested_tick': tick}
                need(v['id'] not in found or found[v['id']] == row,
                     'Conflicting aliases of one Native request')
                found[v['id']] = row
            for item in v.values():
                visit(item)
    visit(value)
    return [found[key] for key in sorted(found)]


def function(a, row, directory, m, timer, b):
    from capacidades import rbx07_funciones_v3 as tools
    start = int(a.tick); p = m['pending']; tool = row['payload']['tool']
    deadline = p['calendar']['second']['outcome_injection_tick'] - 1
    need(start >= p['calendar']['second']['query_tick'] + 8 and start < deadline,
         'Function only inside prospectively fixed post-Q2 gap')
    owned = TimedAdapter(a, timer); life = identity(a)['life_id']
    missing_operand = tool['kind'] == 'CALCULATE' and tool['left'] is None
    if missing_operand:
        # Uniform environment precondition, not a Native abstention/decision.
        # The missing actual intermediate cannot be replaced by an answer or0.
        outputs = {'kind': 'C02_environment_precondition', 'reason': 'MISSING_OPERAND',
                   'no_memory_query': True, 'no_numeric_experience': True,
                   'Native_ticks': 0, 'requests': []}
        compact = {'kind': 'CALCULATE', 'slot': tool['slot'], 'form': tool['form'],
                   'memory_value': None, 'operation': None, 'numeric_result': None,
                   'inputs': [None, tool['right']], 'formed': False,
                   'capability_execution_admitted': False, 'reason': 'MISSING_OPERAND'}
    elif tool['kind'] == 'LESSON':
        predicted = start
        for item in tool['items']:
            predicted = tools.next_lexical_tick(predicted) + (11 if scope()['teacher_mode'] == 'desync' else 0) + 3
        need(predicted < deadline, 'Both lessons must fit before any lesson input; no return retiming')
        outputs = [tools.lesson(owned, item['form'], item['observedSign'],
                    expected_life_id=life, revision=True, teacher_mode=scope()['teacher_mode'],
                    deadline_tick=deadline) for item in tool['items']]
        compact = {'kind': 'LESSON', 'memory_value': None, 'operation': None,
                   'numeric_result': None, 'formed': False,
                   'updates': [{'form': item['form'], 'observedSign': item['observedSign']}
                               for item in tool['items']],
                   'reason': 'EXPERIENCE_ADMITTED_NOT_YET_RECALLED'}
    else:
        outputs = tools.solve(owned, tool['form'], tool['left'], tool['right'],
                              expected_life_id=life, deadline_tick=deadline)
        compact = {'kind': 'CALCULATE', 'slot': tool['slot'], 'form': tool['form'],
                   'memory_value': outputs['recall']['native_sign'],
                   'operation': outputs['operation'], 'numeric_result': outputs['numeric_result'],
                   'inputs': [tool['left'], tool['right']], 'reason': outputs['status'],
                   'formed': outputs['numeric_result'] is not None,
                   'capability_execution_admitted': True}
    requested = normalized_requests(outputs)
    completed = b.receipts(a, requested)
    counts = b.summary(completed)
    need(requested or missing_operand, 'Function produced no material requests; preserve future')
    all_applied = all(r['receipt']['id'] == r['id'] and r['receipt']['status'] == 'applied'
                      for r in completed)
    if not all_applied:
        # This is a known terminal admission result, not an unknown execution.
        # Preserve every actual Native observation below; the World receives
        # an explicit NO_RESULT and its real consequence returns by the same
        # generic hubs. Never clear RAW, retry a pulse or substitute an answer.
        compact = dict(compact, formed=False, numeric_result=None,
                       capability_execution_admitted=False,
                       reason='NATIVE_PARTIAL_ADMISSION')
    primary = {'schema': 'DEE.RBX01.C02.function_primary.R02', 'life_id': life,
               'context': row['context'], 'visible_tool': tool, 'teacher_mode': scope()['teacher_mode'],
               'before_tick': start, 'after_tick': int(a.tick), 'fixed_deadline_tick': deadline,
               'native_function': outputs, 'requests_normalized': completed,
               'Native_inputs': counts, 'prepared_order': True,
               'input_admission_complete': all_applied, 'public_tool_result': compact,
               'no_host_arithmetic_or_expected_value': True}
    folder = home(directory, a) / 'functions'; folder.mkdir(exist_ok=True)
    path = folder / (row['context']['operation_id'] + '.json')
    need(not path.exists(), 'No function-primary overwrite/replay')
    data = (canonical(primary) + '\n').encode('utf8')
    with path.open('xb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    locator = {'path': str(path.relative_to(Path(directory).resolve())),
               'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    p.update(function_used=True, tool_value=compact, tool_primary=locator)
    return result(a, start, accepted=True, null=(not all_applied or tool['kind'] == 'CALCULATE' and compact['numeric_result'] is None),
                  toolResult=compact,
                  evidence={'primary': locator, 'Native_inputs': counts,
                            'all_requested_applied': all_applied, 'fixed_return_tick_unchanged': True,
                            'native_calls_persisted_outside_metadata': True})


def feedback(a, row, m, timer, b, h, g, d, exact):
    start = int(a.tick); p = m['pending']; one = p['calendar']['first']; two = p['calendar']['second']
    expected_action = p.get('action_id', p['context']['operation_id'])
    need(row['payload']['actionId'] == expected_action, 'Actual consequence must acknowledge exact output ID')
    actual_failed = row['payload']['materialConsequence']
    need(type(actual_failed) is bool, 'Actual physical failure must be bool')
    arm = scope()['feedback_arm']
    applied_failed = actual_failed if arm == 'real' else False
    requests = p['requests']
    # Identical generic APIs, timing and pulse quantity in main/control.
    # No selected-bank argument: only Native efference/eligibility chooses a bank.
    timer.run_until(two['outcome_injection_tick'] - 1)
    q2_before = {'banks': g.bank_observations(a, d, exact, g.OLD_ORIGIN),
                 'trace': g.trace_stencil(a, d, exact, g.OLD_ORIGIN)}
    q2_return = h.submit_generic_outcome(a.world, applied_failed, two['outcome_injection_tick'], prefix=g.OLD_PREFIX)
    requests.append(q2_return)
    timer.run_until(two['settled_after_tick'])
    q2_after = {'banks': g.bank_observations(a, d, exact, g.OLD_ORIGIN),
                'trace': g.trace_stencil(a, d, exact, g.OLD_ORIGIN)}
    timer.run_until(one['outcome_injection_tick'] - 1)
    q1_before = {'banks': g.bank_observations(a, d, exact, (24, 12, 12)),
                 'trace': g.trace_stencil(a, d, exact, (24, 12, 12))}
    q1_return = h.submit_generic_outcome(a.world, applied_failed, one['outcome_injection_tick'], prefix='PI10.Q1.TC.R01')
    requests.append(q1_return)
    timer.run_until(one['settled_after_tick'])
    q1_after = {'banks': g.bank_observations(a, d, exact, (24, 12, 12)),
                'trace': g.trace_stencil(a, d, exact, (24, 12, 12))}
    completed = b.receipts(a, requests); counts = b.summary(completed)
    require_applied(completed, 'Whole-cycle requested input/return')
    return_ids = (q1_return['id'], q2_return['id'])
    returned = [r for r in completed if r['id'] in return_ids]
    need(len(returned) == 2 and all(r['receipt']['status'] == 'applied' for r in returned),
         'Both exact generic outcome receipts must be applied; preserve without retry')
    need(int(a.tick) - p['start_tick'] <= scope()['max_ticks_per_cycle'], 'Whole-cycle prospective bound')
    out = result(a, start, accepted=True, null=False,
                 evidence={'actual_consequence': row['payload'], 'feedback_arm': arm,
                           'actual_physical_failed': actual_failed, 'applied_generic_failed': applied_failed,
                           'q1_actual_motor': p.get('q1_motor'), 'q2_actual_motor': p.get('q2_motor'),
                           'q2_decision_observed': 'q2_reader' in p, 'acknowledged_action_id': expected_action,
                           'requests': completed, 'Native_inputs': counts, 'all_requested_applied': True,
                           'outcome_receipts': returned, 'generic_return_pulses': 2,
                           'bank_observations_at_return': {'q1_before': q1_before, 'q1_after': q1_after,
                                                          'q2_before': q2_before, 'q2_after': q2_after},
                           'references_before_cycle': {'q1': p['q1_references_before'], 'q2': p['q2_references_before']},
                           'whole_cycle_ticks': int(a.tick) - p['start_tick'],
                           'tool_result': p.get('tool_value'), 'tool_primary': p.get('tool_primary'),
                           'return_rule': 'Same measured codeRejected/collision/invalid failure to both generic hubs; toll alone is not failure; noaversive uses False twice; no host-selected bank'})
    m['cycles'] += 1; m['last_sequence'] = row['context']['sequence']
    m['phase'] = 'IDLE'; m['pending'] = None
    return out


def dispatch(a, row, *, actuator='closed', directory=None):
    need(actuator == 'closed' and directory is not None, 'Fixed owned closed actuator')
    return execute(a, row, directory)


def operational_dependencies(a, directory):
    identity(a)
    m = get(a)
    if m is not None:
        need((home(directory, a) / 'events.jsonl').is_file(), 'Durable RBX journal missing')
    return {'version': VERSION, 'present': m is not None, 'progress': m, 'new_native_ticks': 0}


def uncertain(a):
    m = get(a)
    return bool(m and m['uncertain'])


def code_files():
    return (Path(__file__), SCOPE)
