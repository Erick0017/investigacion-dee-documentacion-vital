"""Prepared PI08 C: actual STATE -> optional material request -> extra bit.

No engine/world on import. One technical sample register is explicit; it is
NOT Native memory or a fresh measurement at the later release boundary.
The original Native TC, actuator and six-lap outcome apparatus remain literal.
"""
from pathlib import Path
import copy, hashlib, importlib.util, json, os

VERSION = 'DEE.PI08.conditional_sensor_register_access.C.R02'
KEY = 'DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02'
FOLDER = 'PI08_CONSULTA_CONDICIONAL_C_R02'
PREPARE = 'eci01-pi08-c-preparar'
EPISODE = 'eci01-pi08-c-episodio'
STATE = 'eci01-pi08-c-estado'
MODES = {PREPARE, EPISODE, STATE}
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'
PROTOCOL = Path(__file__).with_name('PROTOCOLO_PI08_C_R02.json')
SEAL = Path(__file__).with_name('SELLO_PI08_C_R03.json')
LEGACY = Path(__file__).with_name('pi07_regulacion_R03.py')
LEGACY_SHA = '40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5'
SECOND_SOURCE = Path(__file__).with_name('pi08_consulta_condicional_C_segunda_R02.py')
SECOND_SHA = '500db3042c14bd23bb839de5e2dbf8bb715040dec2c1d740db270ad8026b5f9f'
PREVIEW = (30, 40, 30)
PREVIEW_Z = (30, 40, 29)
PREVIEW_X = (29, 40, 30)
QUESTION = (33, 40, 30)
QUESTION_READER = (34, 40, 30)
SINK = (36, 40, 30)
Z_CHANNEL = 'PI08.C.preview.actual_plusZ.R02'
X_CHANNEL = 'PI08.C.preview.actual_plusX.R02'
QUESTION_CHANNEL = 'PI08.C.material_question_plusX.R02'
SINK_CHANNEL = 'PI08.C.prepared_question_sink.R02'
OLD_B_KEY = 'DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
_PRIVATE = None
INSTRUMENTATION_REVISION = 'R03'


def write_first_stage_witness(home, payload):
    """Write only already captured values; no adapter/world/Native API here.

    Host I/O and one artifact are new. This focused implementation fact is not
    a universal Native with/without-observer passivity claim.
    """
    home = Path(home).resolve(strict=True)
    if not home.is_dir() or type(payload.get('ordinal')) is not int or type(payload.get('query_tick')) is not int:
        raise ValueError('Existing owned first-stage witness home and indices required')
    name = 'primera_C_%02d_q%d.json' % (payload['ordinal'], payload['query_tick'])
    value = {'schema': 'DEE.PI08.C.immediate_first_stage_witness.R03',
             'instrumentation_revision': 'R03', 'new_Native_calls_for_witness': 0,
             'uses_existing_observations_and_receipts_only': True, **payload}
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode('utf8')
    file = home/name
    with file.open('xb') as out:
        out.write(data); out.flush(); os.fsync(out.fileno())
    return {'file': name, 'bytes': len(data), 'sha256': _sha(data),
            'schema': value['schema'], 'new_Native_calls': 0}


def _sha(data): return hashlib.sha256(data).hexdigest()
def _hash(s): return isinstance(s, str) and len(s) == 64 and all(c in '0123456789abcdef' for c in s)


def decode_extra(sample):
    """Fixed RAW codec; no case label, expectation, preferred action or future."""
    state = int(sample['state']); raw = int(sample['raw'])
    if raw == 0:
        return {'valid': True, 'bit': 0, 'kind': 'measured_exact_RAW0_absence'}
    if state > 0 and int(sample['semantic']) == 1:
        if list(sample['direction']) == [0, 0, 1]:
            return {'valid': True, 'bit': 1, 'kind': 'actual_active_SEM1_plusZ'}
        if list(sample['direction']) == [1, 0, 0]:
            return {'valid': True, 'bit': 0, 'kind': 'actual_active_SEM1_plusX'}
    return {'valid': False, 'bit': None, 'kind': 'NULL_unrecognized_or_ambiguous_RAW'}


def protocol(material=False):
    data = PROTOCOL.read_bytes(); p = json.loads(data); ph = _sha(data)
    if p.get('schema') != 'DEE.PI08.conditional_sensor_register_access.protocol.C.R02' or p.get('N') != 67 or p.get('origin') != [8, 40, 50]:
        raise ValueError('Exact inherited C protocol required')
    if p.get('delay_laps') != 6 or p.get('max_ticks_per_episode') != 1300 or len(p.get('schedule', [])) != 6:
        raise ValueError('Six fixed two-stage opportunities and old second-stage timing')
    if p.get('max_ticks_per_C_opportunity') != 2099 or p.get('preparation_ticks') != 3 or p.get('total_C_ticks_bound') != 12600:
        raise ValueError('Preparation plus six bounded opportunities must fit12600')
    for row in p['schedule']:
        if row.get('cue') not in ('threat', 'falsecue', 'none') or row.get('message_payload') not in (None, 5, 8, 11):
            raise ValueError('Only declared environmental inputs')
        if any(type(row.get(k)) is not int for k in ('left', 'right')) or not 0 <= row['right'] < row['left'] <= 20:
            raise ValueError('Fixed positive FI task required; operands are not the selected action')
    if not material: return p, ph
    seal = json.loads(SEAL.read_text('utf-8-sig'))
    if p.get('status') != 'SEALED_BEFORE_C_NATIVE' or seal.get('schema') != 'DEE.PI08.C.prospective_source.seal.R02' or seal.get('protocol_sha256') != ph or seal.get('life_id') != LIFE:
        raise ValueError('Root must prospectively bind the actual source and one C identity')
    source = seal.get('source_prefix', {})
    if not _hash(source.get('manifest_sha256')) or source.get('N') != 67 or not _hash(source.get('snapshot_sha256')):
        raise ValueError('Complete coherent real source required')
    for name, digest in seal.get('files_sha256', {}).items():
        if Path(name).name != name or not _hash(digest) or _sha(Path(__file__).with_name(name).read_bytes()) != digest:
            raise ValueError('C source changed: '+name)
    if not {Path(__file__).name, SECOND_SOURCE.name, LEGACY.name}.issubset(seal.get('files_sha256', {})):
        raise ValueError('Explicit new and literal inherited source fingerprints required')
    return p, ph


def _component():
    global _PRIVATE
    if _PRIVATE is not None: return _PRIVATE
    if _sha(LEGACY.read_bytes()) != LEGACY_SHA or _sha(SECOND_SOURCE.read_bytes()) != SECOND_SHA:
        raise ValueError('Fixed private Native episode source changed')
    spec = importlib.util.spec_from_file_location('capacidades._PI08_C_private_literal_R03', LEGACY)
    c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
    c.KEY, c.FOLDER, c.VERSION = KEY, FOLDER, VERSION
    c.EPISODE, c.STATE = EPISODE, STATE
    c.protocol = protocol; c._identity = _identity; c._old_literals = _old_literals
    c.validate = _validate_second_stage
    c._return = lambda m, failed: bool(failed)
    c._c_second_datum = _second_datum
    exec(compile(SECOND_SOURCE.read_bytes(), str(SECOND_SOURCE), 'exec'), c.__dict__)
    _PRIVATE = c
    return c


def _identity(a):
    c = _component(); _, _, _, decode, _ = c._native()
    identity = decode(dict(a.world.runtime.snapshot_metadata_entries)[c.body.SYSTEM_KEY])
    if identity.get('life_id') != LIFE or identity.get('profile') != 'fisica_directa' or int(a.world.runtime.dimension) != 67:
        raise ValueError('One explicit inherited N67 C diagnostic clone only')
    active = Path(__file__).resolve().parents[1]/'estado/ACTIVO.json'
    if active.is_file() and json.loads(active.read_text('utf-8-sig')).get('life_id') == LIFE:
        raise ValueError('Prepared C is not authorized on a selected principal')
    return identity


def _old_literals(a):
    c = _component(); entries = dict(a.world.runtime.snapshot_metadata_entries)
    keys = [c.body.KEY, c.previous.KEY, 'DEE.Cognitive.PI07.regulation.environment.R03']
    if OLD_B_KEY in entries: keys.append(OLD_B_KEY)
    return {key: entries[key] for key in keys}


def _get(a):
    c = _component(); _, _, _, decode, _ = c._native()
    m = decode(dict(a.world.runtime.snapshot_metadata_entries)[KEY])
    if m.get('version') != VERSION: raise ValueError('Exact new C metadata version required')
    return m


def validate_literal(row):
    if not isinstance(row, dict) or row.get('modo') not in MODES or set(row) != {'modo'}:
        raise ValueError('Fixed C mode only; no action, cue, target, expected bit or timing override')


def validate(a, row):
    validate_literal(row); _identity(a)
    if row['modo'] == STATE: return
    p, ph = protocol(True); seal = json.loads(SEAL.read_text('utf-8-sig'))
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if row['modo'] == PREPARE:
        if KEY in entries: raise ValueError('No C reinstallation or counter reset')
        if OLD_B_KEY in entries:
            inherited_B_seal = json.loads(Path(__file__).with_name('SELLO_PI08_B_R01.json').read_text('utf-8-sig'))
            if inherited_B_seal.get('additional_readonly_life_ids') != [LIFE]:
                raise ValueError('Inherited B metadata needs the prospectively sealed exact C read-only permission')
        if _component()._physical(a) != seal['source_prefix']['physical']:
            raise ValueError('Actual complete source differs or has already advanced')
        _, _, _, decode, _ = _component()._native()
        prior = decode(entries['DEE.Cognitive.PI07.regulation.environment.R03'])
        if prior.get('pending') or prior.get('uncertain') or not prior.get('ready'):
            raise ValueError('Preserve uncertain or incomplete parent; never reset it')
        return
    m = _get(a)
    if m['protocol_sha256'] != ph or not m.get('ready') or m.get('pending') or m.get('uncertain') or m['ordinal'] >= 6:
        raise ValueError('Closed finite C progress required')


def _validate_second_stage(a, row):
    validate_literal(row); _identity(a); _, ph = protocol(True); m = _get(a)
    if row['modo'] != EPISODE or m['protocol_sha256'] != ph or not m.get('ready') or m['ordinal'] >= 6:
        raise ValueError('Only a prepared continuation of this pending C opportunity')
    if m.get('pending', {}).get('phase') != 'C_SECOND_STAGE_PENDING' or not m.get('sample_register'):
        raise ValueError('No invented or repeated first-stage result')


def _second_datum(m):
    register = m.get('sample_register')
    if not isinstance(register, dict) or register.get('ordinal') != m['ordinal']:
        raise ValueError('Actual one-pending-sample register required')
    if register.get('question_applied_and_signature'):
        decoded = decode_extra(register['actual_preview_observation'])
        if not decoded['valid']: raise ValueError('Extra information is NULL; no fallback to expected bit')
        return decoded['bit']
    return 0  # Explicit prepared NoQuery material0, NOT a claimed observation.


def prepare(a, directory):
    validate(a, {'modo': PREPARE}); c = _component(); p, ph = protocol(True); start = int(a.tick)
    old = _old_literals(a); identity = _identity(a)
    _, _, _, decode, _ = c._native()
    inherited_regulation = decode(old['DEE.Cognitive.PI07.regulation.environment.R03'])
    points = {PREVIEW, PREVIEW_Z, PREVIEW_X, QUESTION, QUESTION_READER}
    points |= {(SINK[0]+dx, SINK[1]+dy, SINK[2]+dz) for dx in (-1,0,1) for dy in (-1,0,1) for dz in (-1,0,1)}
    observations = [{'site': list(site), 'observation': c._observe(a, site)} for site in sorted(points)]
    if any(int(row['observation']['raw']) != 0 for row in observations):
        raise ValueError('Proposed C device is not whole-RAW0; refuse without clearing or moving it')
    names = {Z_CHANNEL, X_CHANNEL, QUESTION_CHANNEL, SINK_CHANNEL}
    if names.intersection(set(a.world.runtime.channel_names)) or c._home(directory, identity['life_id']).exists():
        raise ValueError('Fresh C namespace/home required; preserve prior records')
    m = {'version': VERSION, 'life_id': LIFE, 'protocol_sha256': ph, 'ordinal': 0, 'rows': [],
         'role': 'evaluation', 'control': {'arm': 'real', 'from_ordinal': 0, 'max_ordinal': 6},
         'instrumentation': {'global_enabled': False}, 'ready': False, 'admitted': True,
         'pending': {'phase': 'C_DEVICE_PREPARATION'}, 'uncertain': True,
         'log_count': 0, 'log_chain_sha256': '00'*32,
         'old_metadata_sha256': {key:_sha(value.encode('utf8')) for key,value in old.items()},
         'source_prefix_manifest_sha256': json.loads(SEAL.read_text('utf-8-sig'))['source_prefix']['manifest_sha256'],
         'body_P0': copy.deepcopy(inherited_regulation['body_P0']),
         'source_parent_life_id': json.loads(SEAL.read_text('utf-8-sig'))['source_prefix']['life_id'],
         'sample_register': None, 'first_stage_rows': []}
    c._record(a, m, directory, {'kind': 'C_FIXED_TECHNICAL_DEVICE_PREPARATION_INTENT', 'preflight': observations,
              'no_TC_or_bank_or_clock_edit': True, 'sink_is_prepared_environment_not_failure_repair': True})
    c.body._declare(a.world, SINK_CHANNEL, SINK, (0,0,0), 0, 4)
    requests = []; c._submit(a, SINK_CHANNEL, 0, start+2, requests, site=SINK, direction=(0,0,0))
    c.body.SafeAdapter(a).run_until(start+3); requests = c._receipts(a, requests); summary = c._summary(requests, start, int(a.tick))
    ready = summary['applied'] == 1 and summary['all_terminal']
    if ready:
        c.body._declare(a.world, Z_CHANNEL, PREVIEW_Z, (0,0,1))
        c.body._declare(a.world, X_CHANNEL, PREVIEW_X, (1,0,0))
        c.body._declare(a.world, QUESTION_CHANNEL, QUESTION, (1,0,0))
    m.update(ready=ready, pending=None if summary['all_terminal'] else {'phase':'unknown_C_preparation'}, uncertain=not summary['all_terminal'])
    if _old_literals(a) != old: raise RuntimeError('Parent preparation metadata changed')
    c._record(a, m, directory, {'kind': 'C_DEVICE_PREPARED', 'requests': requests, 'Native_inputs': summary, 'ready': ready})
    return {'version': VERSION, 'before_tick': start, 'after_tick': int(a.tick), 'new_native_ticks': int(a.tick)-start,
            'ready': ready, 'requests': requests, 'Native_inputs': summary, 'old_metadata_literal_unchanged': True}


def episode(a, directory):
    validate(a, {'modo': EPISODE}); c = _component(); p, ph = protocol(True); m = _get(a)
    start = int(a.tick); ordinal = m['ordinal']; spec = p['schedule'][ordinal]; old = _old_literals(a)
    refs = [c._observe(a, c.at(v)) for v in ((-1,-1,0),(1,-1,0))]
    if int(refs[0]['clock']) % 782 != int(refs[1]['clock']) % 782: raise ValueError('No phase repair')
    cal1 = c._helper().schedule_trial(start+16, int(refs[0]['clock'])+16, 6); q1 = cal1['query_tick']; seed = q1+7
    m['pending'] = {'phase':'C_FIRST_STAGE_PENDING','ordinal':ordinal}; m['uncertain'] = True
    c._record(a, m, directory, {'kind':'C_OPPORTUNITY_INTENT','ordinal':ordinal,'environment_spec':spec,'first_calendar':cal1})
    requests = []; safety = c.body.SafeAdapter(a)
    try:
        # Preview is a real, independent earlier Native emission. Only STATE
        # reaches query1; its immutable actual RAWsample is a technical register.
        channel, site, direction = (Z_CHANNEL, PREVIEW_Z, (0,0,1)) if spec['cue'] == 'threat' else (X_CHANNEL, PREVIEW_X, (1,0,0))
        if spec['cue'] != 'none': c._submit(a, channel, 0, q1-2, requests, site=site, direction=direction)
        safety.run_until(q1-1); sample = c._observe(a, PREVIEW); datum = int(sample['state'])
        if not 0 <= datum <= 3: raise RuntimeError('Actual preview STATE outside identity codec')
        requests.extend(c._helper().submit_query(a.world, q1, prefix=c.PREFIX))
        c._submit(a, c.PREFIX+'.datum', datum, q1+3, requests, site=c.at((-1,0,1)), direction=(0,0,0))
        safety.run_until(q1+4); reader1 = c._read(a, q1); motor1 = c._motor(reader1['choice']); safety.run_until(q1+6)
        if motor1 is not None: requests.append(c._helper().submit_motor_copy(a.world, motor1, seed, prefix=c.PREFIX))
        question = c._submit(a, QUESTION_CHANNEL, 0, seed, requests, site=QUESTION, direction=(1,0,0)) if motor1 == 1 else None
        safety.run_until(q1+8); question_observation = c._observe(a, QUESTION_READER)
        now_receipts = c._receipts(a, requests); summary1 = c._summary(now_receipts, start, int(a.tick))
        first_stage_witness = write_first_stage_witness(c._home(directory, LIFE), {
            'ordinal': ordinal, 'query_tick': q1, 'observation_tick': int(a.tick), 'before_tick': start,
            'actual_preview_observation': sample, 'first_submitted_STATE': datum,
            'reader': reader1, 'native_motor': motor1, 'question_request_before_final_receipt_lookup': question,
            'question_observation': question_observation, 'requests': now_receipts, 'Native_inputs': summary1,
            'no_extra_sensor_query_or_return': True})
        if not summary1['all_terminal']: raise RuntimeError('Unknown first-stage Native receipt; no second-stage fallback')
        if question is not None: question = next(row for row in now_receipts if row['id'] == question['id'])
        signature = int(question_observation['state']) > 0 and int(question_observation['semantic']) == 1 and list(question_observation['direction']) == [1,0,0]
        applied = bool(question is not None and question['receipt']['status'] == 'applied')
        if applied and not signature:
            raise RuntimeError('Applied question has no fixed physical reader signature; NULL access is not materialzero')
        released = applied and signature
        no_access_kind = 'request_terminally_rejected_material0_no_extra_access' if question is not None else 'declared_NoQuery_material0_not_observation'
        decoded = decode_extra(sample) if released else {'valid':True,'bit':0,'kind':no_access_kind}
        if not decoded['valid']: raise RuntimeError('Actual registered extra direction is NULL; preserve, do not fill')
        register = {'ordinal':ordinal,'sample_site':list(PREVIEW),'sample_tick':q1-1,'actual_preview_observation':sample,
                    'actual_sample_sha256':_sha(json.dumps(sample,sort_keys=True,separators=(',',':')).encode('utf8')),
                    'first_submitted_STATE':datum,'question_scheduled':question is not None,'question_applied':applied,
                    'question_signature':signature,'question_applied_and_signature':released,'released_bit':decoded['bit'],
                    'release_kind':decoded['kind'],'release_tick':q1+8,'technical_register_not_Native_memory':True}
        first = {'ordinal':ordinal,'before_tick':start,'query_tick':q1,'after_question_tick':int(a.tick),
                 'sample_register':register,'reader':reader1,'native_motor':motor1,'question_request':question,
                 'Native_selection_valid':motor1 is not None,'external_immediate_witness':first_stage_witness,
                 'question_observation':question_observation,'requests':now_receipts,'Native_inputs':summary1,
                 'no_generic_return_scheduled_for_first_trace':True}
        m['sample_register'] = register; m['first_stage_rows'].append(first)
        safety.run_until(q1+412)
        refs2 = [c._observe(a,c.at(v)) for v in ((-1,-1,0),(1,-1,0))]
        if int(refs2[0]['clock']) % 782 != int(refs2[1]['clock']) % 782: raise ValueError('Second-stage reference phase changed; no repair')
        cal2 = c._helper().schedule_trial(int(a.tick)+16, int(refs2[0]['clock'])+16, 6)
        if cal2['query_tick'] < q1+782 or cal2['contact_tick']+2-start > p['max_ticks_per_C_opportunity']:
            raise ValueError('Fixed two-stage calendar cannot fit; no adaptive retiming')
        m['pending'] = {'phase':'C_SECOND_STAGE_PENDING','ordinal':ordinal}; m['uncertain'] = True
        c._record(a,m,directory,{'kind':'C_ACTUAL_FIRST_SELECTION_AND_REGISTER_RELEASE','first_stage':first,'second_calendar':cal2,
                   'attribution_limit':'Only second efference has the established six-lap matching; no isolated credit to asking1.'})
        second = c.episode(a, {'modo':EPISODE}, directory)
        whole_requests = c._receipts(a, now_receipts+second['requests']); whole = c._summary(whole_requests,start,int(a.tick))
        after = _get(a); after['sample_register'] = None
        if _old_literals(a) != old: raise RuntimeError('Old R01/R02/R03 metadata changed')
        result = {'version':VERSION,'life_id':LIFE,'ordinal':ordinal,'before_tick':start,'after_tick':int(a.tick),
                  'new_native_ticks':int(a.tick)-start,'first_stage':first,'second_stage':second,'requests':whole_requests,
                  'instrumentation_revision':INSTRUMENTATION_REVISION,'external_immediate_first_stage_witness':first_stage_witness,
                  'Native_inputs':whole,'extra_bit_entered_second_TC':register['released_bit'],
                  'extra_bit_provenance':register['release_kind'],'technical_sample_register':True,
                  'actual_failed':second['actual_failed'],'returned_failed':second['returned_failed'],
                  'old_metadata_literal_unchanged':True,'no_first_trace_credit_claim':True,
                  'scope':'Conditional access to an actual registered sensor detail and second Native use. One shared bank/two queries; no controlled value-of-information or general-strategy claim.'}
        c._record(a,after,directory,{'kind':'C_TWO_STAGE_OPPORTUNITY_COMPLETED','result':result})
        return result
    except BaseException as error:
        # Preserve whichever metadata version is newest, including a completed
        # second Native episode if a subsequent documentary check failed.
        latest = _get(a); latest['uncertain'] = True
        latest['pending'] = {'phase':'preserved_incomplete_C_opportunity','ordinal':ordinal,'tick':int(a.tick),'reason':type(error).__name__,
                             'external_immediate_first_stage_witness':locals().get('first_stage_witness')}
        c._save(a,latest)
        raise


def state(a):
    c = _component(); _identity(a); entries = dict(a.world.runtime.snapshot_metadata_entries)
    return {'version':VERSION,'present':KEY in entries,'progress':_get(a) if KEY in entries else None,
            'physical':c._physical(a),'new_native_ticks':0,'scope':'Read-only; no query, preview, sink or world step.'}


def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if row['modo'] == STATE: return state(a)
    if actuator != 'closed' or directory is None: raise ValueError('Owned explicit bounded diagnostic destination required')
    if row['modo'] == PREPARE: return prepare(a,directory)
    return episode(a,directory)


def uncertain(a):
    return KEY in dict(a.world.runtime.snapshot_metadata_entries) and bool(_get(a).get('uncertain'))


def operational_dependencies(a,directory):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries: return {'version':VERSION,'present':False,'new_native_ticks':0}
    c = _component(); _identity(a); _,ph = protocol(True); m = _get(a)
    if m['protocol_sha256'] != ph or len(m['rows']) != m['ordinal']:
        raise ValueError('C metadata/protocol/rows differ')
    if {key:_sha(value.encode('utf8')) for key,value in _old_literals(a).items()} != m['old_metadata_sha256']:
        raise ValueError('Parent metadata was edited by C')
    home = c._home(directory,LIFE); file = home/'eventos.jsonl'; chain='00'*32; count=0
    with file.open('rb') as lines:
        for line in lines: json.loads(line); chain=_sha(bytes.fromhex(chain)+line); count+=1
    if chain != m['log_chain_sha256'] or count != m['log_count']: raise ValueError('C journal/snapshot mismatch')
    for row in m['rows']:
        artifact = row.get('message_artifact')
        if artifact:
            product=home/artifact['file']
            if artifact['file'] != 'mensaje_%04d.bin'%row['ordinal'] or product.stat().st_size != 64 or _sha(product.read_bytes()) != artifact['sha256']:
                raise ValueError('Actual second-stage message artifact differs')
    return {'version':VERSION,'present':True,'ordinal':m['ordinal'],'remaining':6-m['ordinal'],
            'pending':m['pending'],'uncertain':m['uncertain'],'new_native_ticks':0,'journal_sha256':_sha(file.read_bytes()),
            'technical_register_present':m.get('sample_register') is not None,'old_metadata_literal_unchanged':True}


def code_files():
    return list(dict.fromkeys([Path(__file__),PROTOCOL,SEAL,SECOND_SOURCE,*_component().code_files()]))
