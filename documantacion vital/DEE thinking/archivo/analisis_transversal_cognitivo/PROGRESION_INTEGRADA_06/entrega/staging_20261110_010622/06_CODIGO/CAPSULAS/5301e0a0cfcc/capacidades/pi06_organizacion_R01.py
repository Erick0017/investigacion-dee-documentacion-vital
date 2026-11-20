"""PI06 legal transient inputs and bounded evolution on a diagnostic continuation.

Import is stdlib-only. No answer policy, repair, field/clock write, new body or
selected-world operation. A zero packet remains a material intervention.
"""
from pathlib import Path
import hashlib
import json
import uuid

VERSION = 'DEE.PI06.legal_transient_organization.R01'
FIPLUS = 'eci01-pi06-fiplus'
EVOLUTION = 'eci01-pi06-evolucion'
MODES = {FIPLUS, EVOLUTION}
PROTOCOL = Path(__file__).with_name('PROTOCOLO_PI06_ORGANIZACION_R01.json')
SYSTEM_KEY = 'DEE.Cognitive.System.1.1.life.v1'
SITES = {'izq': [52, 48, 56], 'der': [19, 53, 23], 'sham': [60, 48, 56]}
CONDITIONS = {'intacto': None, 'izq0': ('izq', 0), 'der0': ('der', 0),
              'sham0': ('sham', 0), 'izq7': ('izq', 7), 'izq32': ('izq', 32)}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def protocol():
    data = PROTOCOL.read_bytes()
    p = json.loads(data)
    if p.get('schema') != 'DEE.PI06.organization.protocol.R01' or p.get('status') != 'SEALED':
        raise ValueError('Root must freeze the finite PI06 protocol before Native')
    if p.get('N') != 67 or p.get('sites') != SITES:
        raise ValueError('Fixed N67 geometry only; no payload-selected site')
    if p.get('birth') != {'state': 1, 'semantic': 1, 'direction': [0, 0, 1],
                          'delay_from_input_tick': 4, 'offset_from_query_tick': -50}:
        raise ValueError('Fixed legal SEM1 carrier only; no SEM4 or replacement')
    if p.get('conditions') != {k: None if v is None else {'site_key': v[0], 'payload': v[1]}
                                for k, v in CONDITIONS.items()}:
        raise ValueError('Frozen finite load family required')
    for name, expected in p['dependencies_sha256'].items():
        if Path(name).name != name or _sha(Path(__file__).with_name(name).read_bytes()) != expected:
            raise ValueError('Fixed PI06 dependency changed: ' + name)
    return p, _sha(data)


def validate_literal(row):
    if not isinstance(row, dict) or row.get('modo') not in MODES:
        raise ValueError('Explicit bounded PI06 mode required')
    if row['modo'] == FIPLUS:
        if set(row) != {'modo', 'condicion', 'izquierda', 'derecha', 'captura'}:
            raise ValueError('Public operands and predeclared intervention only; no answer or path')
        if row['condicion'] not in CONDITIONS:
            raise ValueError('No retrospective new condition')
        if any(type(row[k]) is not int or not 0 <= row[k] <= 20 for k in ('izquierda', 'derecha')):
            raise ValueError('Original independent FI comparison domain 0..20')
    elif set(row) != {'modo', 'ticks', 'captura'} or type(row['ticks']) is not int or not 1 <= row['ticks'] <= 2000:
        raise ValueError('Explicit evolution of 1..2000 legal ticks only')
    if row['captura'] not in ('normal', 'global'):
        raise ValueError('Only prospective normal/global observation')
    return row


def _identity(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if SYSTEM_KEY not in entries or int(a.world.runtime.dimension) != 67:
        raise ValueError('Existing complete N67 world required')
    m = json.loads(entries[SYSTEM_KEY])
    life = m.get('life_id', '')
    if not life.startswith('ECI02_PI03_REPRO_') or 'PI05_' not in life or 'PI06_' not in life:
        raise ValueError('Explicit PI05/PI06 diagnostic namespace required')
    if m.get('profile') != 'fisica_directa':
        raise ValueError('Inherited direct physical profile only')
    return m


def _diagnostic(a):
    identity = _identity(a)
    system = Path(__file__).resolve().parents[1]
    active = system / 'estado' / 'ACTIVO.json'
    if active.exists():
        selected = json.loads(active.read_text(encoding='utf-8-sig'))
        if selected.get('life_id') == identity['life_id'] or selected.get('world_id') == identity['life_id']:
            raise ValueError('The selected principal is never a PI06 diagnostic target')
    return identity


def validate(a, row):
    validate_literal(row)
    _diagnostic(a)
    protocol()
    return True


def evolution_ticks(start, count):
    if type(start) is not int or start < 0 or type(count) is not int or not 1 <= count <= 2000:
        raise ValueError('Bounded prospective calendar only')
    end = start + count
    ticks = sorted({start + x for x in range(min(count, 10) + 1)} |
                   set(range(start + 67, end + 1, 67)) | {end})
    return ticks, {start, end}


def _declare(a, name, site):
    old = next((x for x in a.world.interfaces if x.name == name), None)
    if old is not None:
        c = old.channel
        actual = ([c.injection_site.x, c.injection_site.y, c.injection_site.z],
                  [c.direction.dx, c.direction.dy, c.direction.dz], int(c.state), int(c.semantic),
                  bool(c.allow_experience), bool(c.allow_probe))
        if actual != (list(site), [0, 0, 1], 1, 1, True, False):
            raise ValueError('Immutable PI06 transient source differs; never replace it')
        return False
    from dee_thinking import _native as d
    c = d.ChannelSpec()
    c.name = name
    c.injection_site = d.Coordinate(*site)
    c.direction = d.Direction(0, 0, 1)
    c.state = 1
    c.semantic = 1
    c.allow_experience = True
    c.allow_probe = False
    i = d.InterfaceSpec()
    i.name = name
    i.channel = c
    a.world.declare_interface(i)
    return True


def _counts(requests, expected):
    ids = {}
    for request in requests:
        rid = request['id']
        if rid in ids and ids[rid] != request:
            raise ValueError('Contradictory Native request alias')
        ids[rid] = request
    states = [x['receipt']['status'] for x in ids.values()]
    if len(ids) != expected:
        raise RuntimeError('Actual unique Native input count differs; preserve future')
    return {'unique_requested': len(ids), 'applied': sum(x == 'applied' for x in states),
            'rejected_or_other': sum(x != 'applied' for x in states),
            'expected_old_protocol_count': 176, 'expected_total': expected,
            'extra_transient_count': expected - 176}


def _fiplus(a, row, directory, identity, ph):
    from capacidades import pi05_transito_causal_R01 as baseline
    from app.native_tools import physical, observe
    from dee_thinking.consolidated import exact_receipt
    calendar = baseline._calendar(a)
    before = physical(a.world)
    spec = CONDITIONS[row['condicion']]
    transient = None
    if spec is not None:
        key, payload = spec
        site = SITES[key]
        tick = calendar['input_tick'] + 4
        if tick != calendar['query_tick'] - 50 or tick <= int(a.tick):
            raise ValueError('Unchanged FI calendar is incompatible; no retiming')
        pre = observe(a.world, site)
        if int(pre['raw']) != 0:
            raise ValueError('Source contains RAW, including state0; preserve it without repair')
        name = 'PI06.transient.' + key + '.SEM1.plusZ.R01'
        created = _declare(a, name, site)
        receipt = a.world.submit(name, payload, tick)
        request = {'id': int(receipt.id), 'port': name, 'site': list(site), 'direction': [0, 0, 1],
                   'tick': tick, 'payload': payload, 'declared_state': 1, 'declared_semantic': 1}
        scheduled = physical(a.world)
        if before != scheduled:
            raise RuntimeError('Scheduling changed physical buffers/age; preserve actual future')
        transient = {'request': request, 'source_before': pre, 'channel_created': created,
                     'physical_before_scheduling': before, 'physical_after_scheduling': scheduled,
                     'expected_parent_site': [52, 48, 58] if key == 'izq' else [19, 53, 25] if key == 'der' else [60, 48, 58],
                     'predicted_parent_frame_tick': tick + 2,
                     'prediction_not_a_measured_trajectory': True,
                     'no_RAW_clock_or_support_writes': True}
    result = baseline._fiplus(a, {'modo': baseline.FIPLUS, 'izquierda': row['izquierda'],
                                'derecha': row['derecha'], 'captura': row['captura']}, directory)
    if result['calendar'] != calendar:
        raise RuntimeError('Scheduling perturbed the fixed old calendar; retain the failure')
    requests = result['requests']
    if transient is not None:
        transient['request']['receipt'] = exact_receipt(a.world.runtime.receipt(transient['request']['id']))
        transient['source_after'] = observe(a.world, transient['request']['site'])
        requests = [transient['request'], *requests]
    result.update({'version': VERSION, 'PI06_protocol_sha256': ph, 'condition': row['condicion'],
                   'life_id': identity['life_id'], 'transient': transient, 'requests': requests,
                   'Native_inputs': _counts(requests, 176 if spec is None else 177),
                   'scope': 'Original FI128 function and readers; one legal transient SEM1 input or intact control. No new guard, clearing, target-aware action, repair or inferred regulation.'})
    return result


def _evolve(a, row, identity, ph):
    from capacidades import pi05_transito_causal_R01 as baseline
    from app.native_tools import physical
    start = int(a.tick)
    ticks, anchors = evolution_ticks(start, row['ticks'])
    before = physical(a.world)
    recorder = None
    used = a
    if row['captura'] == 'global':
        capture = baseline._capture_module()
        system = Path(__file__).resolve().parents[1]
        target = system / 'estado/observacion_pasiva' / identity['life_id'] / ('PI06_' + uuid.uuid4().hex)
        recorder = capture.GlobalRecorder(target, N=67, ticks=ticks, anchor_ticks=anchors,
            provenance={'life_id': identity['life_id'], 'PI06_protocol_sha256': ph,
                        'module_version': VERSION, 'operation': 'evolution_without_input',
                        'before_tick': start, 'legal_ticks': row['ticks'], 'actor_receives_recording': False},
            max_frames=42, max_compressed_bytes=67108864)
        used = capture.CapturingAdapter(a, ticks=ticks, recorder=recorder)
    used.run_until(start + row['ticks'])
    recording = None if recorder is None else recorder.close()
    after = physical(a.world)
    if int(a.tick) != start + row['ticks']:
        raise RuntimeError('Legal evolution horizon differs; preserve future')
    return {'version': VERSION, 'PI06_protocol_sha256': ph, 'life_id': identity['life_id'],
            'before_tick': start, 'after_tick': int(a.tick), 'new_native_ticks': row['ticks'],
            'new_inputs_scheduled': 0, 'physical_before': before, 'physical_after': after,
            'requests': [], 'external_global_capture': recording,
            'prospective_capture_ticks': ticks if recorder is not None else [],
            'scope': 'Existing world scheduler only. Existing pending inputs may still be admitted; no new packet, guard, cleaning, repair, observation selected after outcome, or claim of spontaneous regulation.'}


def dispatch(a, row, *, actuator='closed', directory=None):
    validate(a, row)
    if actuator != 'closed' or directory is None:
        raise ValueError('Existing owned diagnostic directory and closed actuator only')
    identity = _diagnostic(a)
    _, ph = protocol()
    if row['modo'] == FIPLUS:
        return _fiplus(a, row, directory, identity, ph)
    return _evolve(a, row, identity, ph)


def operational_dependencies(a, directory):
    return {'version': VERSION, 'present': False, 'new_native_ticks': 0,
            'scope': 'No new cognitive metadata; transient inputs/interfaces are preserved by existing full-world and queue contracts. External arrays are not actor memory or a runtime decision dependency.'}


def uncertain(a):
    return False


def code_files():
    return [Path(__file__), PROTOCOL]
