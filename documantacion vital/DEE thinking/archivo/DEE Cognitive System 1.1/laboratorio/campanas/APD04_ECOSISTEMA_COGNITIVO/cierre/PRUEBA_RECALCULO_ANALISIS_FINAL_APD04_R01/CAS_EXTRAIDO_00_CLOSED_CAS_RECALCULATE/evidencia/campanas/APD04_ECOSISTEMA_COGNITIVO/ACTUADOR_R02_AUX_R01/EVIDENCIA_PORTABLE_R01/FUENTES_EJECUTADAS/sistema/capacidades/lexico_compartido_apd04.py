"""APD04 R02 finite lexical extension at the SAME inherited K hub.

R01 positive-Y admission was rejected by physical preflight, without lessons.
This second and final declared design changes only equilibra to positive-XY.
The change is external engineering selected by compatibility/vacancy, never by
teaching accuracy. Preserve R01 source, its rejected state and all primaries.

No Runtime is created on import. New directions at K enable two additional
experience-dependent associations without replacing luma/nara or using one
independent organization per word. Terminators, teachers, restorative resources
and the common36-site reader are prepared apparatus, not acquired semantics.
The selected function and any transfer/generalization require separate physical
evidence. Metadata contains contracts/counters, never acquired signs/answers.
"""
KEY = 'DEE.Cognitive.System.1.1.APD04.shared_lexicon.R02'
VERSION = 'APD04.shared_lexicon.R02.sameK.diagonal.common36'
N = 67
I = (33, 33, 33)
J = (47, 47, 47)
H = (47, 17, 47)
K = (47, 7, 47)
LEGACY_I = {'alfa': (1, 0, 0), 'beta': (0, 1, 0),
            'gamma': (1, 1, 0), 'delta': (-1, 1, 0),
            'epsilon': (1, -1, 0), 'zeta': (-1, -1, 0),
            'suma': (-1, 0, 0), 'diferencia': (0, -1, 0)}
LEGACY_J = {'agrega': (-1, 0, 0), 'resta': (0, -1, 0),
            'total': (1, 0, 0), 'quita': (0, 1, 0)}
LEGACY_H = {'compara': (1, 0, 0), 'recuerda': (0, 1, 0)}
LEGACY_K = {'luma': (-1, 0, 0), 'nara': (0, -1, 0)}
NEW_FORMS = {'clasifica': (1, 0, 0), 'equilibra': (1, 1, 0)}
OLD_CODEC = {**{f: (I, v) for f, v in LEGACY_I.items()},
             **{f: (J, v) for f, v in LEGACY_J.items()},
             **{f: (H, v) for f, v in LEGACY_H.items()},
             **{f: (K, v) for f, v in LEGACY_K.items()}}
FORM_CODEC = {**OLD_CODEC, **{f: (K, v) for f, v in NEW_FORMS.items()}}


def pos(origin, direction, k, z=0):
    return tuple((origin[i] + k * direction[i] + (z if i == 2 else 0)) % N
                 for i in range(3))


def _add(site, direction, k=1):
    return tuple((site[i] + k * direction[i]) % N for i in range(3))


def _inventory(codec):
    preparations = []
    ports = []
    hubs = []
    readers = []
    for form, (origin, v) in codec.items():
        ports.append({'form': form, 'role': 'cue', 'site': list(origin),
                      'direction': list(v)})
        hubs.append({'form': form, 'role': 'hub',
                     'site': list(pos(origin, v, 3))})
        for sign in (-1, 1):
            for k, z in ((2, 1), (2, 2), (5, 3)):
                preparations.append({'form': form, 'sign_arm': sign,
                    'role': 'prepare_terminator',
                    'site': list(pos(origin, v, k, z * sign)),
                    'prepared_state': 0, 'prepared_semantic': 4,
                    'prepared_value': 0})
            teacher = (-v[0], -v[1], sign)
            hub = pos(origin, v, 3)
            ports.append({'form': form, 'role': 'teacher', 'sign_arm': sign,
                'site': list(_add(hub, teacher, -3)),
                'direction': list(teacher)})
            revision = (0, 0, sign)
            ports.append({'form': form, 'role': 'revision', 'sign_arm': sign,
                'site': list(_add(hub, revision, -3)),
                'direction': list(revision)})
            for stage, k, z, di, arrival in (
                ('select', 4, 1, -1, 4),
                ('back', 4, 2, -1, 5),
                ('restore', 3, 3, 1, 6)):
                dv = (di * v[0], di * v[1], 0)
                destination = pos(origin, v, k, z * sign)
                ports.append({'form': form, 'role': stage, 'sign_arm': sign,
                    'site': list(_add(destination, dv, -2)),
                    'direction': list(dv), 'arrival_offset': arrival})
            readers.append({'form': form, 'role': 'output_gate',
                'sign_arm': sign, 'site': list(pos(origin, v, 4, sign))})
    return {'preparations': preparations, 'ports': ports,
            'hubs': hubs, 'readers': readers}


def geometry():
    new = _inventory({f: (K, v) for f, v in NEW_FORMS.items()})
    old = _inventory(OLD_CODEC)
    pre_sites = {tuple(row['site']) for row in new['preparations']}
    port_sites = {tuple(row['site']) for row in new['ports']}
    all_readers = old['readers'] + new['readers']
    return {'version': VERSION, 'N': N, 'origin': list(K),
        'new_forms': list(NEW_FORMS), 'preparation_sites': new['preparations'],
        'new_ports': new['ports'], 'new_hubs': new['hubs'],
        'common_reader': all_readers, 'reader_sites': len(all_readers),
        'unique_reader_sites': len({tuple(x['site']) for x in all_readers}),
        'preparation_duplicates': len(new['preparations']) - len(pre_sites),
        'preparation_injection_overlap': [list(x) for x in sorted(pre_sites & port_sites)],
        'physical_vacancy_not_established_by_geometry': True}


def compatibility_geometry():
    """Exact finite listed-geometry checks, not a dynamic-isolation claim."""
    new = _inventory({f: (K, v) for f, v in NEW_FORMS.items()})
    old = _inventory(OLD_CODEC)
    new_rows = sum(new.values(), [])
    old_rows = sum(old.values(), [])
    new_points = {tuple(row['site']) for row in new_rows}
    old_points = {tuple(row['site']) for row in old_rows}
    old_overlap = new_points & old_points
    # One inherited cue hub is intentionally shared by four directions.
    shared_k = tuple(K)
    allowed = []
    forbidden = []
    for point in sorted(old_overlap):
        nr = [r for r in new_rows if tuple(r['site']) == point]
        pr = [r for r in old_rows if tuple(r['site']) == point]
        item = {'site': list(point), 'new_roles': [r['role'] for r in nr],
                'old_roles': [r['role'] for r in pr]}
        intentional = point == shared_k and all(r['role'] == 'cue' for r in nr + pr)
        (allowed if intentional else forbidden).append(item)
    origin = (25, 13, 53)
    def at(offset):
        return _add(origin, offset)
    frame = {(-1, -1, 0), (1, -1, 0), (0, 1, 1), (0, 1, -1),
             (0, 0, 1), (-1, -3, 0), (1, -3, 0), (-1, -2, 1),
             (1, -2, 1), (2, 1, 2), (-2, 0, 0), (-1, -2, -1)}
    frame.update((x, y, z) for x in (-2, 2) for y in (-2, -1) for z in (-1, 0, 1))
    ports = {(-1, -1, -4), (1, -1, -4), (0, 0, -3), (-2, 1, -2), (2, 4, 0)}
    for x in (-1, 0, 1):
        frame.update(((5*x, 5, 0), (4*x, 4, -3), (6*x, 6, 0),
                      (11*x, 11, -1), (10*x, 10, 0), (10*x, 10, 10)))
        ports.update(((4*x, 4, 1), (6*x, 6, -3), (10*x, 10, -3)))
        target = (2*x, -2, -2)
        dv = (0, 0, 1) if x else (-1, 0, 1)
        source = tuple(target[i] - dv[i] for i in range(3))
        ports.add(source)
        ports.add((source[0], source[1], source[2] + 8))
    r04 = {at(x) for x in frame | ports}
    r04.update(at((2*x, 2, 0)) for x in (-1, 0, 1))
    loops = {at((x*k, k, -2)) for x in (-1, 0, 1) for k in range(N)}
    sensor = {at((-1, 0, 1)), at((-1, 0, -1))}
    intersections = {
        'APD03_R04_preparation_ports_readers': [list(x) for x in sorted(new_points & r04)],
        'APD03_R04_three_trace_loops': [list(x) for x in sorted(new_points & loops)],
        'APD03_balanced_sensor_sources': [list(x) for x in sorted(new_points & sensor)],
    }
    return {'intentional_old_K_cue_sharing': allowed,
        'forbidden_old_lexical_intersections': forbidden,
        'intersections': intersections,
        'admissible_static_design': not forbidden and not any(intersections.values()),
        'scope': 'Listed lexical preparation, ALL cue/teacher/revision/resource sources, hubs and gates; '
                 'R04 declared preparation/ports/readers/three loops and sensor sources. '
                 'No proof of full causal isolation, present RAW vacancy or future retention.'}


def _libraries():
    from dee_thinking import _native as d
    from dee_thinking.persistence import encode_metadata, decode_metadata
    from capacidades import mente_acumulativa_r02 as memory
    from capacidades import lexico_generico_apd03_r02 as prior
    from app.native_tools import physical
    if prior.FORM_CODEC != OLD_CODEC:
        raise ValueError('Inherited APD03 codec changed; no silent migration')
    return d, encode_metadata, decode_metadata, memory, prior, physical


def get(adapter):
    _, _, decode, _, prior, _ = _libraries()
    prior.get(adapter)
    entries = dict(adapter.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError('Explicit APD04 shared-slot admission is required')
    result = decode(entries[KEY])
    if result['version'] != VERSION or int(adapter.world.runtime.dimension) != N:
        raise ValueError('Frozen APD04 lexical domain differs')
    return result


def _save(adapter, state):
    _, encode, _, _, _, _ = _libraries()
    adapter.world.runtime.set_snapshot_metadata(KEY, encode(state))


def preflight(adapter):
    _, _, _, memory, prior, _ = _libraries()
    prior.get(adapter)
    if int(adapter.world.runtime.dimension) != N:
        raise ValueError('The SAME N67 world is required; no replacement')
    design = geometry()
    static = compatibility_geometry()
    rows = []
    for row in design['preparation_sites'] + design['new_ports'] + design['new_hubs']:
        rows.append({**row, 'requires_RAW_zero': True})
    for row in design['common_reader']:
        rows.append({**row, 'requires_RAW_zero': row['form'] in NEW_FORMS,
            'historical_read_only': row['form'] not in NEW_FORMS})
    for row in rows:
        row['observation'] = memory.view(adapter, row['site'])
    conflicts = [row for row in rows if row['requires_RAW_zero'] and int(row['observation']['raw'])]
    design_ok = (static['admissible_static_design'] and not design['preparation_duplicates']
                 and not design['preparation_injection_overlap']
                 and design['reader_sites'] == design['unique_reader_sites'] == 36)
    return {'version': VERSION, 'tick': int(adapter.tick), 'geometry': design,
        'static_compatibility': static, 'all_sources_hubs_gates': rows,
        'required_RAW_zero_conflicts': conflicts,
        'admissible': design_ok and not conflicts,
        'state_zero_is_not_vacancy': True,
        'no_favorable_relocation_or_clearing': True}


def prepare(adapter):
    d, _, _, memory, prior, physical = _libraries()
    prior.get(adapter)
    if KEY in dict(adapter.world.runtime.snapshot_metadata_entries):
        raise ValueError('Shared slots already admitted; no resetting acquired history')
    screen = preflight(adapter)
    if not screen['admissible']:
        raise ValueError('APD04 same-K preflight rejected; preserve state, no alternate hub/cleanup')
    tick = int(adapter.tick) + 2
    requests = []
    rows = screen['geometry']['preparation_sites']
    for index, row in enumerate(rows):
        name = 'APD04.LEX.R02.prepare.' + str(index)
        if name in set(adapter.world.runtime.channel_names):
            raise ValueError('Preparation interface exists; no duplicate admission')
        channel = d.ChannelSpec()
        channel.name = name
        channel.injection_site = d.Coordinate(*row['site'])
        channel.direction = d.Direction(0, 0, 0)
        channel.state = 0
        channel.semantic = 4
        channel.allow_experience = True
        channel.allow_probe = False
        interface = d.InterfaceSpec()
        interface.name = name
        interface.channel = channel
        adapter.world.declare_interface(interface)
        receipt = adapter.world.submit(name, 0, tick)
        requests.append({'id': int(receipt.id), 'channel': name, 'site': row['site'],
            'direction': [0, 0, 0], 'state': 0, 'semantic': 4,
            'value': 0, 'tick': tick})
    adapter.run_until(tick + 1)
    receipts = memory.receipts(adapter, requests)
    if any(row['receipt']['status'] != 'applied' for row in receipts):
        raise ValueError('Incomplete P0 admission preserved; no retry or overwrite')
    state = {'version': VERSION, 'prepared_tick': tick, 'origin': list(K),
        'forms': {form: list(v) for form, v in NEW_FORMS.items()},
        'teaching_episodes': 0, 'query_episodes': 0, 'reader_sites': 36,
        'same_hub_as_luma_nara': True,
        'acquired_signs_answers_or_targets_in_metadata': False,
        'scope': 'Finite two-slot P0 extension of the SAME common lexical hub; '
                 'signed associations require actual subsequent experience.'}
    _save(adapter, state)
    return {'kind': 'APD04_explicit_shared_lexical_P0_extension',
        'preflight': screen, 'requests': receipts,
        'post_preparation': [memory.view(adapter, row['site']) for row in rows],
        'physical': physical(adapter.world), 'metadata': state,
        'installation_is_not_acquisition': True}


def fixed_read(adapter):
    _, _, _, memory, _, _ = _libraries()
    get(adapter)
    panel = []
    candidates = []
    for origin, v in FORM_CODEC.values():
        for sign in (-1, 1):
            row = memory.view(adapter, pos(origin, v, 4, sign))
            panel.append(row)
            if row['state'] > 0 and row['semantic'] == 1 and row['direction'] == [0, 0, sign]:
                candidates.append({'site': row['site'], 'sign': sign, 's_reg': row['s_reg']})
    return {'panel': panel, 'candidates': candidates,
        'formed_native_command': candidates[0]['sign'] if len(candidates) == 1 else None,
        'ambiguous': len(candidates) > 1, 'reader_sites': 36,
        'reader_uses_token_target_or_expected_sign': False}


def teach(adapter, form, sign, *, mode='paired', revision=False):
    _, _, _, memory, _, physical = _libraries()
    state = get(adapter)
    if form not in NEW_FORMS or type(sign) is not int or sign not in (-1, 1):
        raise ValueError('Explicit signed teaching for one admitted APD04 cue is required')
    if mode not in ('paired', 'omitted', 'desync') or type(revision) is not bool:
        raise ValueError('Declared teacher mode and explicit revision flag are required')
    origin, v = FORM_CODEC[form]
    tick = memory.phase(adapter.tick)
    teacher_tick = tick + (11 if mode == 'desync' else 0)
    before = physical(adapter.world)
    requests = []
    memory.submit(adapter, 'APD04.LEX.R02.cue.' + form, origin, v, 5, tick, requests)
    if mode != 'omitted':
        hub = pos(origin, v, 3)
        direction = (-v[0], -v[1], sign)
        memory.submit(adapter, 'APD04.LEX.R02.teacher.' + form + '.' + str(sign),
            _add(hub, direction, -3), direction, 11, teacher_tick, requests)
        if revision:
            direction = (0, 0, sign)
            memory.submit(adapter, 'APD04.LEX.R02.revision.' + form + '.' + str(sign),
                _add(hub, direction, -3), direction, 11, teacher_tick, requests)
    adapter.run_until(teacher_tick + 3)
    state['teaching_episodes'] += 1
    _save(adapter, state)
    return {'kind': 'APD04_explicit_lexical_revision' if revision else 'APD04_explicit_lexical_lesson',
        'form': form, 'teacher_sign': sign, 'teacher_mode': mode,
        'revision': revision, 'input_tick': tick,
        'teacher_tick': None if mode == 'omitted' else teacher_tick,
        'end_tick': int(adapter.tick), 'before': before,
        'after': physical(adapter.world), 'hub': memory.view(adapter, pos(origin, v, 3)),
        'requests': memory.receipts(adapter, requests),
        'lesson_is_explicit_external_experience': True}


def query(adapter, form, *, detailed=False):
    _, _, _, memory, _, physical = _libraries()
    state = get(adapter)
    if form not in FORM_CODEC:
        raise ValueError('No parser for an unadmitted literal cue')
    origin, v = FORM_CODEC[form]
    tick = memory.phase(adapter.tick)
    before = physical(adapter.world)
    requests = []
    memory.submit(adapter, 'APD04.LEX.R02.cue.' + form, origin, v, 5, tick, requests)
    for sign in (-1, 1):
        for stage, k, z, di, arrival in (
            ('select', 4, 1, -1, 4), ('back', 4, 2, -1, 5), ('restore', 3, 3, 1, 6)):
            direction = (di*v[0], di*v[1], 0)
            destination = pos(origin, v, k, z*sign)
            memory.submit(adapter, 'APD04.LEX.R02.generic.' + form + '.' + stage + '.' + str(sign),
                _add(destination, direction, -2), direction, 7, tick + arrival - 2, requests)
    frames = []
    answer = None
    for current in range(tick, tick + 8):
        adapter.run_until(current)
        if detailed:
            frames.append({'tick': current, 'gates': [
                memory.view(adapter, pos(o, w, 4, sign))
                for o, w in FORM_CODEC.values() for sign in (-1, 1)]})
        if current == tick + 4:
            answer = fixed_read(adapter)
    state['query_episodes'] += 1
    _save(adapter, state)
    return {'kind': 'APD04_common36_lexical_query', 'form': form,
        'input_tick': tick, 'read_tick': tick + 4, 'end_tick': int(adapter.tick),
        'before': before, 'after': physical(adapter.world), 'reader': answer,
        'requests': memory.receipts(adapter, requests), 'frames': frames,
        'teacher_correct_function_or_expected_sign_supplied': False}


