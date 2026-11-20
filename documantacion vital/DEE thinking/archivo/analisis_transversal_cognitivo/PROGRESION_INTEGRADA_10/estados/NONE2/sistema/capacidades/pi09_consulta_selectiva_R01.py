"""PI09 fixed consultation controls over the literal PI08 C mechanism.

No DEE import or world access on module import. Old C/B/R03 metadata and
physical banks are retained. New metadata is an explicit environmental lot,
not a reset of physical learning. Only the declared reference can override
query1's actuator. Query2, FI and its generic return remain literal.
"""
from pathlib import Path
import ast, copy, hashlib, importlib.util, json

VERSION = 'DEE.PI09.selective_registered_consultation.R01'
KEY = 'DEE.Cognitive.PI09.selective_registered_consultation.R01'
FOLDER = 'PI09_CONSULTA_SELECTIVA_R01'
PREPARE = 'eci01-pi09-preparar'
EPISODE = 'eci01-pi09-episodio'
STATE = 'eci01-pi09-estado'
MODES = {PREPARE, EPISODE, STATE}
ARMS = {'native_real', 'always_real', 'never', 'always_desacoplado', 'native_desacoplado'}
DECOUPLED = {'always_desacoplado', 'native_desacoplado'}
OLD_C_KEY = 'DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02'
PROTOCOL = Path(__file__).with_name('PROTOCOLO_PI09_CONSULTA_R01.json')
SEAL = Path(__file__).with_name('SELLO_PI09_CONSULTA_R01.json')
SOURCE = Path(__file__).with_name('pi08_consulta_condicional_C_R03.py')
SOURCE_SHA = '07072d230c33f75eccd3cd46751e404bfb24745756e1575e50705c0c76f8870f'
_PRIVATE = None

def _sha(data): return hashlib.sha256(data).hexdigest()
def _require(ok, reason):
    if not ok: raise ValueError(reason)
def _canon(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8')
def _hash(value): return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)

def _protocol(material=False):
    data = PROTOCOL.read_bytes(); p = json.loads(data); ph = _sha(data)
    _require(p.get('schema') == 'DEE.PI09.selective_consultation.protocol.R01' and p.get('N') == 67, 'Exact PI09 protocol required')
    _require(p.get('origin') == [8,40,50] and p.get('delay_laps') == 6, 'Inherited anatomy/calendar required')
    _require(len(p.get('schedule', [])) == 18 and p.get('max_ticks_per_episode') == 1300 and p.get('max_ticks_per_C_opportunity') == 2110, 'Twelve evaluated plus six explicit future opportunities required')
    _require([r.get('stage') for r in p['schedule']] == ['development']*6+['reserved']*6+['operational_prepared']*6, 'Fixed development/reserve/future split')
    for r in p['schedule']:
        _require(r.get('cue') in {'threat','falsecue','none'} and r.get('message_payload') in (None,5,8,11), 'Only public environmental material')
        _require(type(r.get('left')) is int and type(r.get('right')) is int and 0 <= r['right'] < r['left'] <= 20, 'Positive FI operands only')
        _require(type(r.get('wait_ticks')) is int and 0 <= r['wait_ticks'] <= 11, 'Prepared finite wait only')
    _require(p.get('yoke_permutation') == [(i+5)%12 for i in range(12)], 'Prospective source_plus_5 permutation must remain literal')
    if material:
        seal = json.loads(SEAL.read_text('utf-8-sig'))
        _require(p.get('status') == 'SEALED_BEFORE_PI09_NATIVE' and seal.get('schema') == 'DEE.PI09.selective_consultation.source_seal.R01' and seal.get('protocol_sha256') == ph, 'Prospectively sealed PI09 source required')
        _require(seal.get('source_prefix', {}).get('tick') == 884835 and _hash(seal['source_prefix'].get('manifest_sha256')), 'Actual complete C884835 source required')
        arms = seal.get('arms', {})
        _require({'native_real','always_real','never','always_desacoplado'} <= set(arms) <= ARMS and len(set(arms.values())) == len(arms), 'Exact separate diagnostic identities per arm')
        for role, life in arms.items():
            _require(isinstance(life,str) and 'PI09' in life and life.startswith('ECI02_PI03_REPRO_'), 'Strict PI09 diagnostic identity')
        _require(seal.get('operational_native_id') == arms['native_real'], 'Only the native-real life can ever become operational')
        repro = seal.get('native_reproduction_ids',[]); readonly = seal.get('diagnostic_readonly_ids',[])
        _require(isinstance(repro,list) and isinstance(readonly,list) and len(set([*arms.values(),*repro,*readonly])) == len(arms)+len(repro)+len(readonly), 'Separate exact reproduction/read-only identities required')
        for life in [*repro,*readonly]:
            _require(isinstance(life,str) and life.startswith('ECI02_PI03_REPRO_') and 'PI09' in life, 'Explicit PI09 transport identity only')
        for name, value in seal.get('files_sha256', {}).items():
            _require(Path(name).name == name and _hash(value) and _sha(Path(__file__).with_name(name).read_bytes()) == value, 'Sealed source changed: '+name)
        _require({Path(__file__).name,PROTOCOL.name,SOURCE.name} <= set(seal.get('files_sha256',{})), 'Explicit wrapper/protocol/literal C pins required')
    return p, ph

def _transformed_episode(source):
    """Small source-local adapter, never change the on-disk PI08 source."""
    tree = ast.parse(source); node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'episode')
    text = ast.get_source_segment(source,node)
    changes = [
      ("reader1 = c._read(a, q1); motor1 = c._motor(reader1['choice']); safety.run_until(q1+6)", "reader1 = c._read(a, q1); native_motor1 = c._motor(reader1['choice']); motor1 = _question_motor(m, native_motor1); safety.run_until(q1+6)"),
      ("'native_motor': motor1, 'question_request_before_final_receipt_lookup'", "'native_motor': native_motor1, 'actual_query_motor': motor1, 'query_control': m['control']['query_policy'], 'question_request_before_final_receipt_lookup'"),
      ("decoded = decode_extra(sample) if released else {'valid':True,'bit':0,'kind':no_access_kind}", "decoded = _released_decode(m, sample, released, no_access_kind)"),
      ("'release_kind':decoded['kind'],'release_tick':q1+8", "'release_kind':decoded['kind'],'release_source':decoded.get('source'),'release_tick':q1+8"),
      ("'reader':reader1,'native_motor':motor1,'question_request':question", "'reader':reader1,'native_motor':native_motor1,'actual_query_motor':motor1,'query_control':m['control']['query_policy'],'question_request':question"),
      ("'Native_selection_valid':motor1 is not None", "'Native_selection_valid':native_motor1 is not None"),
      ("'no_generic_return_scheduled_for_first_trace':True", "'no_generic_return_scheduled_for_first_trace':True, 'operator_reference_not_candidate_policy':m['control']['query_policy'] != 'native'"),
      ("'extra_bit_provenance':register['release_kind']", "'extra_bit_provenance':register['release_kind'],'extra_bit_source':register.get('release_source'),'query_control':m['control']['query_policy'],'information_control':m['control']['information_policy']"),
    ]
    for before, after in changes:
        _require(text.count(before) == 1, 'Literal C adapter anchor changed: '+before)
        text = text.replace(before,after)
    return text, len(changes)

def _C():
    global _PRIVATE
    if _PRIVATE is not None: return _PRIVATE
    data = SOURCE.read_bytes(); _require(_sha(data) == SOURCE_SHA, 'Literal PI08 C source changed')
    spec = importlib.util.spec_from_file_location('capacidades._PI09_literal_C_adapter_R01', SOURCE)
    c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    c.KEY,c.FOLDER,c.VERSION = KEY,FOLDER,VERSION
    c.PREPARE,c.EPISODE,c.STATE,c.MODES = PREPARE,EPISODE,STATE,MODES
    c.PROTOCOL,c.SEAL = PROTOCOL,SEAL
    c.protocol,c._identity,c._old_literals = _protocol,_identity,_old_literals
    c.validate,c._validate_second_stage,c._second_datum = validate,_validate_second,_second_datum
    c._question_motor,c._released_decode = _question_motor,_released_decode
    source, _ = _transformed_episode(data.decode('utf-8-sig'))
    exec(compile(source, str(SOURCE)+':PI09_explicit_adapter', 'exec'), c.__dict__)
    _PRIVATE = c
    return c

def _core(): return _C()._component()
def _identity(a):
    c = _core(); _,_,_,decode,_ = c._native()
    identity = decode(dict(a.world.runtime.snapshot_metadata_entries)[c.body.SYSTEM_KEY])
    seal = json.loads(SEAL.read_text('utf-8-sig')); life = identity.get('life_id')
    permitted = [*seal['arms'].values(),*seal.get('native_reproduction_ids',[]),*seal.get('diagnostic_readonly_ids',[])]
    _require(life in permitted and identity.get('profile') == 'fisica_directa' and int(a.world.runtime.dimension) == 67, 'Exact sealed PI09 N67 diagnostic clone only')
    active = Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
    if active.is_file() and json.loads(active.read_text('utf-8-sig')).get('life_id') == life:
        _operational_permission(a, identity, seal)
    _C().LIFE = life
    return identity

def _operational_permission(a,identity,seal):
    """Dormant exact administrative permission; never changes Native policy."""
    life = identity['life_id']; entries = dict(a.world.runtime.snapshot_metadata_entries)
    _require(life == seal['arms']['native_real'] == seal['operational_native_id'] and KEY in entries, 'No reference arm or unprepared life may become selected')
    m = _get(a); _require(m['control']['arm'] == 'native_real' and m['control']['query_policy'] == 'native' and m['control']['information_policy'] == 'real', 'Only actual Native real-information policy is operational')
    file = Path(__file__).resolve().parents[1]/'contratos/PI09_CONSULTA_OPERATIVA_R01.json'
    contract = json.loads(file.read_text('utf-8-sig')); _,ph = _protocol(False)
    _require(contract.get('schema') == 'DEE.PI09.exact_native_consultation_permission.v1' and contract.get('status') == 'COMMITTED' and contract.get('life_id') == life and contract.get('profile') == 'fisica_directa' and contract.get('protocol_sha256') == ph and contract.get('allowed_modes') == [EPISODE,STATE] and contract.get('all_adoption_gates_met') is True and _hash(contract.get('adoption_decision_sha256')), 'Actual exact COMMITTED permission required before selected use')
    return contract

def _old_literals(a):
    c = _core(); entries = dict(a.world.runtime.snapshot_metadata_entries)
    keys = [c.body.KEY,c.previous.KEY,'DEE.Cognitive.PI07.regulation.environment.R03',OLD_C_KEY]
    if _C().OLD_B_KEY in entries: keys.append(_C().OLD_B_KEY)
    return {k:entries[k] for k in keys}

def _get(a): return _C()._get(a)
def _question_motor(m,native):
    policy = m['control']['query_policy']
    _require(native in (None,-1,1), 'Actual motor must be decoded, never expected-filled')
    return native if policy == 'native' else 1 if policy == 'always' else -1

def _checked_RAW(s):
    raw = int(s['raw']); _require(0 <= raw < 2**64, 'Actual uint64 RAW required')
    ds = [(raw >> shift) & 15 for shift in (48,52,56)]
    fields = {'state':raw & 0xffffffff,'s_reg':(raw >> 32) & 65535,'semantic':raw >> 60,'direction':[v-16 if v&8 else v for v in ds]}
    _require(all(s.get(k) == v for k,v in fields.items()) and s.get('active') is (fields['state'] > 0), 'Source fields must decode exactly from RAW, never a case label')
    return fields

def validate_plan(value, p=None):
    _require(isinstance(value,str) and len(value.encode('utf8')) <= 6500, 'Bounded JSON plan string only; no file paths or executable codec')
    plan = json.loads(value); p = _protocol()[0] if p is None else p
    _require(set(plan) == {'schema','permutation','source_arm','source_evidence_sha256','samples'} and plan['schema'] == 'DEE.PI09.actual_RAW_sample_yoke.v1', 'Exact external source-sample plan schema')
    _require(plan['source_arm'] == 'always_real' and _hash(plan['source_evidence_sha256']) and plan['permutation'] == p['yoke_permutation'] and len(plan['samples']) == 12, 'Fixed full always-real source required')
    for i, item in enumerate(plan['samples']):
        _require(set(item) == {'ordinal','observation','observation_sha256','primary_sha256'} and item['ordinal'] == i and _hash(item['primary_sha256']) and _sha(_canon(item['observation'])) == item['observation_sha256'], 'Actual immutable sample provenance differs')
        s = item['observation']
        _require(set(s) == {'raw','state','s_reg','semantic','direction','site','tick','clock','active'} and s['site'] == [30,40,30] and type(s['tick']) is int, 'Fixed actual preview observation only')
        _checked_RAW(s)
        _require(_C().decode_extra(s)['valid'], 'Source RAW is NULL/ambiguous; no expected-bit fallback')
    return plan

def _released_decode(m,sample,released,no_access_kind):
    if not released: return {'valid':True,'bit':0,'kind':no_access_kind,'source':None}
    if m['control']['information_policy'] == 'real':
        decoded = _C().decode_extra(sample)
        return {**decoded,'source':{'kind':'current_actual_registered_RAW','observation':sample,'observation_sha256':_sha(_canon(sample))}}
    plan = m['control']['sample_plan']; j = plan['permutation'][m['ordinal']]; item = plan['samples'][j]
    decoded = _C().decode_extra(item['observation'])
    return {**decoded,'kind':'external_desynchronized_actual_RAW_source_plus_5','source':{'kind':'external_frozen_always_real_RAW','source_ordinal':j,**item,'source_evidence_sha256':plan['source_evidence_sha256']}}

def _second_datum(m):
    r = m.get('sample_register')
    _require(isinstance(r,dict) and r['ordinal'] == m['ordinal'], 'One current pending sample required')
    if not r['question_applied_and_signature']:
        _require(r['released_bit'] == 0, 'No-query data must remain explicit material0')
        return 0
    _require(r['released_bit'] in (0,1) and r.get('release_source'), 'Actual source provenance required before second Native query')
    return r['released_bit']

def validate_literal(row):
    _require(isinstance(row,dict) and row.get('modo') in MODES, 'Fixed PI09 mode only')
    if row['modo'] != PREPARE:
        _require(set(row) == {'modo'}, 'No action/cue/target/expected/timing arguments')
        return
    arm = row.get('brazo'); _require(arm in ARMS, 'Explicit experimental arm only at admission')
    _require(set(row) == ({'modo','brazo','plan'} if arm in DECOUPLED else {'modo','brazo'}), 'Exact admission fields; no arbitrary source path')
    if arm in DECOUPLED: validate_plan(row['plan'])

def validate(a,row):
    validate_literal(row); identity = _identity(a)
    if row['modo'] == STATE: return
    p,ph = _protocol(True); entries = dict(a.world.runtime.snapshot_metadata_entries); seal = json.loads(SEAL.read_text('utf-8-sig'))
    _require(identity['life_id'] not in seal.get('diagnostic_readonly_ids',[]), 'Conservation clone allows only state/dependencies; no PI09 preparation or episode')
    if row['modo'] == PREPARE:
        exact_arm = seal['arms'].get(row['brazo']) == identity['life_id']
        reproduction = row['brazo'] == 'native_real' and identity['life_id'] in seal.get('native_reproduction_ids',[])
        _require(KEY not in entries and (exact_arm or reproduction), 'Fresh metadata and prospectively assigned arm/reproduction identity required')
        _require(_core()._physical(a) == seal['source_prefix']['physical'], 'Actual inherited source has already advanced or differs')
        old = _old_literals(a); _,_,_,decode,_ = _core()._native(); inherited = decode(old[OLD_C_KEY])
        _require(inherited.get('ordinal') == 6 and len(inherited.get('rows',[])) == 6 and inherited.get('ready') and not inherited.get('pending') and not inherited.get('uncertain') and inherited.get('sample_register') is None, 'Closed coherent C6 parent required; no reset of an adverse future')
        return
    m = _get(a)
    _require(m['protocol_sha256'] == ph and m.get('ready') and not m.get('pending') and not m.get('uncertain') and m['ordinal'] < 18 and (m['control']['arm'] == 'native_real' or m['ordinal'] < 12), 'Closed unexhausted PI09 progress required; references are evaluation-only12')

def _validate_second(a,row):
    validate_literal(row); identity = _identity(a); _,ph = _protocol(True); m = _get(a)
    _require(identity['life_id'] not in json.loads(SEAL.read_text('utf-8-sig')).get('diagnostic_readonly_ids',[]), 'No PI09 second-stage action in a read-only conservation clone')
    _require(row['modo'] == EPISODE and m['protocol_sha256'] == ph and m.get('ready') and m['ordinal'] < 18 and (m['control']['arm'] == 'native_real' or m['ordinal'] < 12) and m.get('pending',{}).get('phase') == 'C_SECOND_STAGE_PENDING' and m.get('sample_register'), 'One actual preserved second-stage continuation only')

def prepare(a,row,directory):
    validate(a,row); c = _core(); p,ph = _protocol(True); old = _old_literals(a); identity = _identity(a)
    _,_,_,decode,_ = c._native(); inherited = decode(old[OLD_C_KEY]); arm = row['brazo']
    _require(not c._home(directory,identity['life_id']).exists(), 'Fresh PI09 journal home required')
    sink = c._observe(a,_C().SINK)
    _require(int(sink['raw']) == (4 << 60), 'Inherited C SEM4 sink must exist; no repair or reinstall')
    for channel in (_C().Z_CHANNEL,_C().X_CHANNEL,_C().QUESTION_CHANNEL,_C().SINK_CHANNEL):
        _require(channel in set(a.world.runtime.channel_names), 'Inherited physical C interface missing')
    control = {'arm':arm,'query_policy':'always' if arm.startswith('always') else 'never' if arm == 'never' else 'native', 'information_policy':'desynchronized' if arm in DECOUPLED else 'real', 'from_ordinal':0,'max_ordinal':18,'evaluation_horizon':12}
    if arm in DECOUPLED: control['sample_plan'] = validate_plan(row['plan'],p)
    m = {'version':VERSION,'life_id':identity['life_id'],'protocol_sha256':ph,'ordinal':0,'rows':[], 'role':'evaluation','control':control,'instrumentation':{'global_enabled':False},'ready':True,'admitted':True,'pending':None,'uncertain':False,'log_count':0,'log_chain_sha256':'00'*32,
         'old_metadata_sha256':{k:_sha(v.encode('utf8')) for k,v in old.items()},'body_P0':copy.deepcopy(inherited['body_P0']),'sample_register':None,'first_stage_rows':[], 'source_parent_life_id':inherited['life_id'],'source_parent_C_ordinal':6,
         'environmental_supply':{'new_opportunities':18,'evaluation_horizon':12,'operational_future':6,'old_C_ordinal_preserved':6,'physical_bank_reset':False,'new_Native_inputs':0,'new_Native_ticks':0}}
    c._record(a,m,directory,{'kind':'PI09_ENVIRONMENT18_ADMITTED_ZERO_NATIVE','control':control,'new_environment_schedule':p['schedule'],'inherited_sink':sink,'old_metadata_literal_unchanged':True,'no_reinstallation_or_bank_clock_RAW_edit':True})
    _require(_old_literals(a) == old, 'Parent C/B/old R03 metadata changed')
    return {'version':VERSION,'life_id':identity['life_id'],'before_tick':int(a.tick),'after_tick':int(a.tick),'new_native_ticks':0,'ready':True,'arm':arm,'new_environment_opportunities':18,'evaluation_horizon':12,'operational_future':6,'old_C_ordinal_preserved':6,'old_metadata_literal_unchanged':True}

def episode(a,directory):
    validate(a,{'modo':EPISODE}); c = _core(); m = _get(a); p,_ = _protocol(True); initial = int(a.tick); wait = p['schedule'][m['ordinal']]['wait_ticks']
    if wait:
        c._record(a,m,directory,{'kind':'PROSPECTIVE_ENVIRONMENT_WAIT','ticks':wait,'before_tick':initial,'no_birth_or_repair':True})
        c.body.SafeAdapter(a).run_until(initial+wait)
    result = _C().episode(a,directory)
    return {**result,'prepared_wait_ticks':wait,'before_prepared_wait':initial,'whole_new_native_ticks':int(a.tick)-initial,'wait_scope':'Actual query/reference clocks retained; nominal wait is not a claim of independent effective phase.'}

def state(a):
    _identity(a); entries = dict(a.world.runtime.snapshot_metadata_entries)
    return {'version':VERSION,'present':KEY in entries,'progress':_get(a) if KEY in entries else None,'physical':_core()._physical(a),'new_native_ticks':0}

def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if row['modo'] == STATE: return state(a)
    _require(actuator == 'closed' and directory is not None, 'Closed actuator and explicit owned directory required')
    return prepare(a,row,directory) if row['modo'] == PREPARE else episode(a,directory)

def uncertain(a):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries): return False
    return bool(_get(a).get('uncertain'))

def operational_dependencies(a,directory):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries): return {'version':VERSION,'present':False,'new_native_ticks':0}
    identity = _identity(a); c = _core(); _,ph = _protocol(True); m = _get(a)
    _require(m['protocol_sha256'] == ph and len(m['rows']) == m['ordinal'] <= 18, 'New environmental metadata/protocol mismatch')
    _require({k:_sha(v.encode('utf8')) for k,v in _old_literals(a).items()} == m['old_metadata_sha256'], 'Inherited parent metadata changed')
    file = c._home(directory,identity['life_id'])/'eventos.jsonl'; chain = '00'*32; count = 0
    with file.open('rb') as lines:
        for line in lines: json.loads(line); chain = _sha(bytes.fromhex(chain)+line); count += 1
    _require(chain == m['log_chain_sha256'] and count == m['log_count'], 'PI09 journal/snapshot mismatch')
    for row in m['rows']:
        item = row.get('message_artifact')
        if item:
            name = 'mensaje_%04d.bin' % row['ordinal']; product = file.parent/name
            _require(item['file'] == name and product.stat().st_size == 64 and _sha(product.read_bytes()) == item['sha256'], 'Actual Native product changed')
    return {'version':VERSION,'present':True,'ordinal':m['ordinal'],'remaining':18-m['ordinal'],'evaluation_remaining':max(0,12-m['ordinal']),'pending':m['pending'],'uncertain':m['uncertain'],'new_native_ticks':0,'journal_sha256':_sha(file.read_bytes()),'old_metadata_literal_unchanged':True}

def code_files():
    return list(dict.fromkeys([Path(__file__),PROTOCOL,SEAL,SOURCE,*_C().code_files()]))
