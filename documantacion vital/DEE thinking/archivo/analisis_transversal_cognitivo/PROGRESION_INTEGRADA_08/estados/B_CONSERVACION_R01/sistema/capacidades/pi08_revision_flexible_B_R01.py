"""PI08 B: bounded reversals on the inherited Native TC, research clones only.

Importing this module opens no world.  The preserved PI07 R03 component is loaded
into a PRIVATE namespace.  Its literal Native episode is reused with two explicit
reference-only hooks; no candidate action is chosen by the external benchmark.
The new protocol remains unusable materially until a separate A-adoption seal.
"""
from pathlib import Path
import copy, hashlib, importlib.util, json, os, types

VERSION = 'DEE.PI08.successive_contextual_regulation.B.R01'
KEY = 'DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'
FOLDER = 'PI08_REGULACION_FLEXIBLE_B_R01'
START = 'eci01-pi08-b-iniciar'
EPISODE = 'eci01-pi08-b-episodio'
STATE = 'eci01-pi08-b-estado'
MODES = {START, EPISODE, STATE}
PROTOCOL = Path(__file__).with_name('PROTOCOLO_PI08_B_R01.json')
SEAL = Path(__file__).with_name('SELLO_PI08_B_R01.json')
LEGACY = Path(__file__).with_name('pi07_regulacion_R03.py')
EPISODE_SOURCE = Path(__file__).with_name('pi08_revision_flexible_B_episodio_R01.py')
LEGACY_SHA = '40648fd81c5b1f278ee9c18d0d464c5a4b5e9fd808054afe6ff072a10fda0ac5'
LEGACY_PROTOCOL_SHA = 'f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'
EPISODE_SHA = 'a110b1de0953d86b1488f62a623f9623fad686885bd30d446c5f5a3deb44ab6f'
ROLES = ('real', 'none', 'yoked', 'reference')
_PRIVATE = None


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _json(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _validate_schedule(p):
    if p.get('N') != 67 or p.get('origin') != [8, 40, 50] or p.get('delay_laps') != 6:
        raise ValueError('Inherited N67 TC and six-lap temporal coupling required')
    if p.get('initial_reference_payloads') != {'A': 0, 'B': 2} or p.get('max_ticks_per_episode') != 1300:
        raise ValueError('No new TC, ref preparation or adaptive calendar')
    if p.get('start_ordinal') != 12 or p.get('evaluated_opportunities') != 18 or len(p.get('schedule', [])) != 32:
        raise ValueError('Exactly12 preserved offers,18 evaluated B offers and2 future resources')
    for row in p['schedule']:
        if row.get('cue') not in ('none', 'threat', 'falsecue') or row.get('message_payload') not in (None, 5, 8, 11):
            raise ValueError('Only unchanged physical cue/packet codecs')
        if any(type(row.get(k)) is not int or not 0 <= row[k] <= 20 for k in ('left', 'right')):
            raise ValueError('Public operands remain in the admitted FI domain')
    permutation = p.get('controls', {}).get('yoke_permutation')
    if not isinstance(permutation, list) or sorted(permutation) != list(range(18)):
        raise ValueError('Exactly one precommitted permutation of18 actual returns')
    if any(i == v for i, v in enumerate(permutation)) or len({(v-i) % 18 for i, v in enumerate(permutation)}) == 1:
        raise ValueError('A noncyclic derangement is required; no retrospective search')
    if p.get('physical_environment', {}).get('pulse', {}).get('site') != [53, 48, 56]:
        raise ValueError('Inherited perpendicular tool only')
    if p.get('physical_environment', {}).get('legitimate_packet', {}).get('reader_site') != [54, 48, 56]:
        raise ValueError('Inherited exact message reader only')
    physical = p['physical_environment']
    if physical['pulse'].get('direction') != [-1, 0, 0] or physical['legitimate_packet'].get('direction') != [1, 0, 0]:
        raise ValueError('No actuator or packet direction remapping')
    return p


def protocol(material=False):
    data = PROTOCOL.read_bytes()
    p = _validate_schedule(json.loads(data))
    ph = _sha(data)
    if p.get('schema') != 'DEE.PI08.successive_contextual_regulation.protocol.B.R01':
        raise ValueError('Explicit new PI08 B contract required')
    if not material:
        return p, ph
    seal = json.loads(SEAL.read_text('utf-8-sig'))
    if p.get('status') != 'SEALED_BEFORE_B_NATIVE' or seal.get('schema') != 'DEE.PI08.B.after_A_adoption.seal.R01':
        raise ValueError('B is blocked until actual A adoption and prospective sealing')
    if seal.get('protocol_sha256') != ph or seal.get('A_adopted') is not True or not _hash(seal.get('A_adoption_proof_sha256')):
        raise ValueError('Actual protected A adoption proof and exact protocol required')
    source = seal.get('source_prefix', {})
    if source.get('N') != 67 or not _hash(source.get('manifest_sha256')) or not _hash(source.get('snapshot_sha256')):
        raise ValueError('Actual complete coherent A prefix is required')
    if set(source.get('physical', {})) != {'N', 'tick', 'RAW_sha256', 'clocks_sha256'}:
        raise ValueError('Exact source physical fingerprint is required')
    if source['physical']['N'] != 67 or source['physical']['tick'] != source.get('T') or any(not _hash(source['physical'][k]) for k in ('RAW_sha256', 'clocks_sha256')):
        raise ValueError('Source physical fingerprint invalid')
    ids = seal.get('research_life_ids', {})
    if set(ids) != set(ROLES) or len(set(ids.values())) != 4:
        raise ValueError('Four explicit distinct diagnostic identities required')
    for life in ids.values():
        if not isinstance(life, str) or not life.startswith('ECI02_PI03_REPRO_') or 'PI08_B_' not in life:
            raise ValueError('No principal, broad identity allowlist or hidden world')
    conservation = seal.get('conservation_life_id')
    if conservation != 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01' or conservation in ids.values():
        raise ValueError('One separate read/conservation-only clone must be explicit')
    if seal.get('additional_readonly_life_ids') != ['ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01']:
        raise ValueError('Only one explicit following C clone may read inherited B metadata')
    expected = seal.get('files_sha256', {})
    needed = {Path(__file__).name, EPISODE_SOURCE.name, LEGACY.name, 'PROTOCOLO_PI07_R03.json'}
    if not needed.issubset(expected):
        raise ValueError('New and preserved source fingerprints must be explicit')
    for name, digest in expected.items():
        if Path(name).name != name or not _hash(digest) or _sha(Path(__file__).with_name(name).read_bytes()) != digest:
            raise ValueError('B dependency changed: ' + name)
    if expected[LEGACY.name] != LEGACY_SHA or expected['PROTOCOLO_PI07_R03.json'] != LEGACY_PROTOCOL_SHA:
        raise ValueError('Published scientific source must remain literal')
    for name, digest in p['dependencies_sha256'].items():
        if Path(name).name != name or not _hash(digest) or _sha(Path(__file__).with_name(name).read_bytes()) != digest:
            raise ValueError('Inherited dependency changed: ' + name)
    return p, ph


def _component():
    global _PRIVATE
    if _PRIVATE is not None:
        return _PRIVATE
    if _sha(LEGACY.read_bytes()) != LEGACY_SHA:
        raise ValueError('Literal PI07 R03 Native component changed')
    if _sha(EPISODE_SOURCE.read_bytes()) != EPISODE_SHA:
        raise ValueError('Declared local episode/reference hooks changed before loading')
    spec = importlib.util.spec_from_file_location('capacidades._PI08_B_private_preserved_R03', LEGACY)
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    # All modifications below affect this isolated namespace, never the imported
    # public R03 component nor any Native RAW, clocks, channels or memory.
    c.KEY, c.FOLDER, c.VERSION = KEY, FOLDER, VERSION
    c.EPISODE, c.STATE = EPISODE, STATE
    c.protocol = protocol
    c._identity = lambda a: _identity(a)
    c.validate = validate
    c._old_literals = lambda a: _old_literals(a)
    c._return = _return
    c._b_choose_action = _choose_action
    c._b_after_actual_outcome = _after_actual_outcome
    # Fixed local audited Python source, not caller-provided code or policy.
    episode_namespace = c.__dict__
    exec(compile(EPISODE_SOURCE.read_bytes(), str(EPISODE_SOURCE), 'exec'), episode_namespace)
    _PRIVATE = c
    return c


def _identity(a):
    c = _component()
    _, _, _, decode, _ = c._native()
    identity = decode(dict(a.world.runtime.snapshot_metadata_entries)[c.body.SYSTEM_KEY])
    life = identity['life_id']
    if int(a.world.runtime.dimension) != 67 or identity.get('profile') != 'fisica_directa':
        raise ValueError('Actual inherited N67 fisica_directa identity required')
    if not life.startswith('ECI02_PI03_REPRO_') or 'PI08_B_' not in life:
        raise ValueError('B only accepts an explicit diagnostic clone')
    if SEAL.is_file():
        seal = json.loads(SEAL.read_text('utf-8-sig'))
        allowed = set(seal.get('research_life_ids', {}).values()) | {seal.get('conservation_life_id')} | set(seal.get('additional_readonly_life_ids', []))
        if life not in allowed:
            raise ValueError('Only the four sealed arms and one explicit conservation clone')
    active = Path(__file__).resolve().parents[1] / 'estado/ACTIVO.json'
    if active.is_file() and json.loads(active.read_text('utf-8-sig')).get('life_id') == life:
        raise ValueError('B research module refuses the selected principal')
    return identity


def _old_literals(a):
    c = _component()
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return {key: entries[key] for key in (c.body.KEY, c.previous.KEY, 'DEE.Cognitive.PI07.regulation.environment.R03')}


def _get(a):
    c = _component()
    _, _, _, decode, _ = c._native()
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError('Explicit zero-Native B admission is required')
    m = decode(entries[KEY])
    if m.get('version') != VERSION:
        raise ValueError('Exact B metadata version required')
    return m


def _plan(text, digest, p):
    if not isinstance(text, str) or len(text.encode('utf8')) > 8192 or not _hash(digest) or _sha(text.encode('utf8')) != digest:
        raise ValueError('Bounded literal yoked plan and exact SHA required')
    plan = json.loads(text)
    required = {'schema', 'permutation', 'source_failed', 'values', 'source_evidence_sha256'}
    if set(plan) != required or plan['schema'] != 'DEE.PI08.B.noncyclic_yoked_return.v1':
        raise ValueError('One exact control-only yoked plan required')
    if plan['permutation'] != p['controls']['yoke_permutation'] or not _hash(plan['source_evidence_sha256']):
        raise ValueError('Yoke permutation cannot be chosen after seeing results')
    for key in ('source_failed', 'values'):
        if not isinstance(plan[key], list) or len(plan[key]) != 18 or any(type(v) is not bool for v in plan[key]):
            raise ValueError('18 actual boolean returns, no solution or action fields')
    if plan['values'] != [plan['source_failed'][i] for i in plan['permutation']]:
        raise ValueError('Yoked values do not match the prospectively frozen permutation')
    return plan


def validate_literal(row):
    if not isinstance(row, dict) or row.get('modo') not in MODES:
        raise ValueError('Explicit PI08 B operation required')
    if row['modo'] == START:
        expected = {'modo', 'brazo', 'prefijo_sha256', 'registro_global'}
        if row.get('brazo') == 'yoked':
            expected |= {'plan', 'plan_sha256'}
        if set(row) != expected or row.get('brazo') not in ROLES or not _hash(row.get('prefijo_sha256')) or type(row.get('registro_global')) is not bool:
            raise ValueError('Only declared role, complete prefix and recorder choice')
        if row['brazo'] == 'yoked':
            p, _ = protocol(False)
            _plan(row['plan'], row['plan_sha256'], p)
    elif set(row) != {'modo'}:
        raise ValueError('No answer, environment, action, force or timing override')


def validate(a, row):
    validate_literal(row)
    identity = _identity(a)
    if row['modo'] == STATE:
        return
    p, ph = protocol(True)
    seal = json.loads(SEAL.read_text('utf-8-sig'))
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if row['modo'] == START:
        if KEY in entries or identity['life_id'] != seal['research_life_ids'][row['brazo']]:
            raise ValueError('No re-admission or role inferred from an unrestricted ID')
        if row['prefijo_sha256'] != seal['source_prefix']['manifest_sha256']:
            raise ValueError('All arms must use the same complete adopted-A prefix')
        c = _component(); _, _, _, decode, _ = c._native()
        old = decode(entries['DEE.Cognitive.PI07.regulation.environment.R03'])
        if old.get('ordinal') != 12 or len(old.get('rows', [])) != 12 or not old.get('ready') or old.get('pending') or old.get('uncertain'):
            raise ValueError('Actual closed A history12 is required; no reset or fabricated prefix')
        if int(a.tick) != seal['source_prefix']['T']:
            raise ValueError('Admission must precede any additional Native exposure')
        if _component()._physical(a) != seal['source_prefix']['physical']:
            raise ValueError('Source physical state differs; no age or branch substitution')
        return
    m = _get(a)
    if m.get('protocol_sha256') != ph or not m.get('ready') or not m.get('admitted') or m.get('pending') or m.get('uncertain'):
        raise ValueError('Closed coherent B progress required')
    if identity['life_id'] != seal['research_life_ids'][m['control']['arm']]:
        raise ValueError('B role/identity mismatch')
    if m['ordinal'] >= m['control']['max_ordinal']:
        raise ValueError('Explicit finite B environment exhausted')


def _return(m, actual_failed):
    arm = m['control']['arm']
    if arm == 'none':
        return False
    if arm == 'yoked':
        return m['control']['yoked_values'][m['ordinal'] - m['control']['from_ordinal']]
    return bool(actual_failed)


def _choose_action(m, datum, native_motor):
    if m['control']['arm'] != 'reference':
        return native_motor
    # This table exists ONLY in the declared external material reference clone.
    # No cue label, block, future, target or expected action enters this function.
    return m['reference_policy'][str(datum)]


def _after_actual_outcome(m, datum, motor, actual_failed):
    if m['control']['arm'] == 'reference' and actual_failed:
        m['reference_policy'][str(datum)] = -motor


def initialize(a, row, directory):
    validate(a, row)
    c = _component(); identity = _identity(a); p, ph = protocol(True)
    _, _, _, decode, _ = c._native()
    old_literal = _old_literals(a); before = c._physical(a)
    old = decode(old_literal['DEE.Cognitive.PI07.regulation.environment.R03'])
    home = c._home(directory, identity['life_id'])
    if home.exists():
        raise ValueError('Existing B home is never reused')
    plan = _plan(row['plan'], row['plan_sha256'], p) if row['brazo'] == 'yoked' else None
    m = copy.deepcopy(old)
    m.update(version=VERSION, life_id=identity['life_id'], protocol_sha256=ph,
             ordinal=12, ready=True, admitted=True, role='evaluation', forced_action=None,
             pending=None, uncertain=False, log_count=0, log_chain_sha256='00'*32,
             source_prefix_manifest_sha256=row['prefijo_sha256'],
             old_metadata_sha256={key: _sha(value.encode('utf8')) for key, value in old_literal.items()},
             inherited_row_count=12, inherited_rows_sha256=_sha(_json(old['rows']).encode('utf8')),
             control={'arm': row['brazo'], 'from_ordinal': 12,
                      'max_ordinal': 32 if row['brazo'] == 'real' else 30,
                      'yoked_values': plan['values'] if plan else None,
                      'plan_sha256': row.get('plan_sha256'),
                      'source_evidence_sha256': plan['source_evidence_sha256'] if plan else None},
             instrumentation={'global_enabled': row['registro_global']})
    # The candidate and Native controls have no external policy table.
    if row['brazo'] == 'reference':
        m['reference_policy'] = {str(i): -1 for i in range(4)}
    else:
        m.pop('reference_policy', None)
    c._record(a, m, directory, {'kind': 'PI08_B_EXPLICIT_CONTRACT_CONTINUATION_ZERO_NATIVE',
              'source_manifest_sha256': row['prefijo_sha256'], 'preserved_old_metadata_sha256': m['old_metadata_sha256'],
              'consumed_rows_preserved': 12, 'new_evaluated_resources': 18,
              'future_resources_real_only': 2, 'control': m['control'],
              'plan_literal_auditor_only': row.get('plan'), 'no_new_bank_or_clock_or_interface': True,
              'reference_policy_location': 'external_reference_clone_only' if row['brazo'] == 'reference' else None})
    if c._physical(a) != before or _old_literals(a) != old_literal:
        raise RuntimeError('Administrative B continuation changed Native state or old history')
    return {'version': VERSION, 'life_id': identity['life_id'], 'before_tick': int(a.tick), 'after_tick': int(a.tick),
            'new_native_ticks': 0, 'requests': [], 'admitted': True, 'control': m['control'],
            'old_R01_R02_R03_metadata_literal_unchanged': True, 'physical_unchanged': True}


def state(a):
    c = _component(); entries = dict(a.world.runtime.snapshot_metadata_entries)
    return {'version': VERSION, 'present': KEY in entries, 'progress': _get(a) if KEY in entries else None,
            'physical': c._physical(a), 'new_native_ticks': 0,
            'scope': 'Read-only progress; no supply, query, bank write or world advance.'}


def dispatch(a, row, *, actuator='closed', directory=None):
    validate(a, row)
    if row['modo'] == STATE:
        return state(a)
    if directory is None or actuator != 'closed':
        raise ValueError('Owned explicit home and closed bounded actuator required')
    if row['modo'] == START:
        return initialize(a, row, directory)
    return _component().episode(a, row, directory)


def uncertain(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return KEY in entries and bool(_get(a).get('uncertain'))


def operational_dependencies(a, directory):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        return {'version': VERSION, 'present': False, 'new_native_ticks': 0}
    c = _component(); identity = _identity(a); p, ph = protocol(True); m = _get(a)
    if m['protocol_sha256'] != ph or m['version'] != VERSION or len(m['rows']) != m['ordinal']:
        raise ValueError('B progress/version/rows incoherent')
    old = _old_literals(a)
    if {key: _sha(value.encode('utf8')) for key, value in old.items()} != m['old_metadata_sha256']:
        raise ValueError('Old R01/R02/R03 metadata must remain literal throughout B')
    if _sha(_json(m['rows'][:12]).encode('utf8')) != m['inherited_rows_sha256']:
        raise ValueError('Consumed A rows changed or were reset')
    home = c._home(directory, identity['life_id']); journal = home/'eventos.jsonl'
    chain = '00'*32; count = 0
    with journal.open('rb') as lines:
        for line in lines:
            json.loads(line); chain = _sha(bytes.fromhex(chain)+line); count += 1
    if chain != m['log_chain_sha256'] or count != m['log_count']:
        raise ValueError('B journal and snapshot metadata disagree')
    prior_home = c.body._home(directory, identity['life_id']).with_name('PI07_REGULACION_ENV_R03')
    artifacts = 0
    for row in m['rows']:
        art = row.get('message_artifact')
        if art is None:
            continue
        if art.get('file') != 'mensaje_%04d.bin' % row['ordinal']:
            raise ValueError('Fixed message artifact name required')
        file = (prior_home if row['ordinal'] < 12 else home)/art['file']
        if not file.is_file() or file.stat().st_size != 64 or art.get('bytes') != 64 or _sha(file.read_bytes()) != art.get('sha256'):
            raise ValueError('Actual message content unavailable or changed')
        artifacts += 1
    if (m['control']['arm'] == 'reference') != ('reference_policy' in m):
        raise ValueError('An external policy may exist only in the declared benchmark clone')
    return {'version': VERSION, 'present': True, 'ordinal': m['ordinal'], 'B_completed': m['ordinal']-12,
            'remaining': m['control']['max_ordinal']-m['ordinal'], 'journal_sha256': _sha(journal.read_bytes()),
            'old_R01_R02_R03_metadata_literal_unchanged': True, 'message_artifacts_checked': artifacts,
            'pending': m.get('pending'), 'uncertain': bool(m.get('uncertain')), 'new_native_ticks': 0}


def code_files():
    return list(dict.fromkeys([Path(__file__), PROTOCOL, SEAL, EPISODE_SOURCE, *_component().code_files()]))
