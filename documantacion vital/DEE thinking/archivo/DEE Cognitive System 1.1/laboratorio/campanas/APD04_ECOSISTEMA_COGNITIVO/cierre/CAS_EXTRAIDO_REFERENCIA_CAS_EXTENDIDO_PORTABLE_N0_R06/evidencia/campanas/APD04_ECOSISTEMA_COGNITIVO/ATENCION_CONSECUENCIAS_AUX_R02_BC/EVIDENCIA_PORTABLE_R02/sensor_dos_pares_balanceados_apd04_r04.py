"""R04 candidate: two balanced physical scalar pairs, constant native query.

Two elementary bits remain independent: tag enters the inherited left pair,
goal enters one newly declared right pair. No equality, difference, relevance,
right action or target-dependent port selection is computed by Python. The
spatial coupling is external P0 design, not acquired contextual knowledge.

Only this one additional prospective sensory design is specified. Importing
creates no Runtime, interface, placement or tick. Current RAW vacancy and actual
functional behavior are separate questions; no memory or clock is overwritten.
"""
VERSION = 'APD04.two_balanced_raw_pairs.constant_query.prospective.R04'
KEY = 'DEE.Cognitive.System.1.1.APD04.two_balanced_raw_pairs.R04'
N = 67
ORIGIN = (25, 13, 53)
QUERY_PAYLOAD = 5
GOAL_NAMES = ['APD04.sensor.R04.right_goal.' + str(i) for i in range(2)]


def at(offset):
    return tuple((ORIGIN[i] + offset[i]) % N for i in range(3))


def specification():
    return {'version': VERSION, 'origin': list(ORIGIN),
        'inherited_tag_sources': [list(at((-1, 0, z))) for z in (1, -1)],
        'new_goal_sources': [list(at((1, 0, z))) for z in (1, -1)],
        'new_names': GOAL_NAMES, 'direction': [0, 0, 0],
        'state': 1, 'semantic': 1, 'input_offset': 3,
        'query_payload': QUERY_PAYLOAD,
        'elementary_variables': 2, 'sensory_material_signals': 4,
        'all_input_signals_including_query_and_generic': 16,
        'no_new_supports_or_learned_reference_values': True}


def static_compatibility():
    """Finite address overlap check, not local causal independence."""
    design = specification()
    new = {tuple(p) for p in design['new_goal_sources']}
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
        direction = (0, 0, 1) if x else (-1, 0, 1)
        source = tuple(target[i] - direction[i] for i in range(3))
        ports.add(source)
        ports.add((source[0], source[1], source[2] + 8))
    prepared = {at(p) for p in frame}
    interfaces = {at(p) for p in ports}
    readers = {at((2*x, 2, 0)) for x in (-1, 0, 1)}
    loops = {at((x*k, k, -2)) for x in (-1, 0, 1) for k in range(N)}
    old_tag = {tuple(p) for p in design['inherited_tag_sources']}
    intersections = {name: [list(p) for p in sorted(new & points)] for name, points in (
        ('R04_prepared_supports', prepared), ('R04_declared_interfaces', interfaces),
        ('R04_historical_readers', readers), ('R04_three_trace_loops', loops),
        ('inherited_tag_sources', old_tag))}
    return {'intersections': intersections,
        'no_listed_address_overlap': not any(intersections.values()),
        'scope': 'Declared exact address intersections only. New sources intentionally '
                 'change the nearby causal context; no assertion of isolation or useful processing.'}


def _get(adapter):
    from dee_thinking.persistence import decode_metadata
    from capacidades import ruta_adaptativa_apd02_04 as route
    route.get(adapter)
    entries = dict(adapter.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError('Explicit P0 right-pair interface admission is required')
    value = decode_metadata(entries[KEY])
    if value['version'] != VERSION:
        raise ValueError('Another sensory contract is present; no silent migration')
    return value


def preflight(adapter):
    from capacidades import ruta_adaptativa_apd02_04 as route
    from capacidades import sensor_balanceado_apd03_r02 as prior
    route.get(adapter)
    if int(adapter.world.runtime.dimension) != N:
        raise ValueError('The existing N67 world is indispensable')
    design = specification()
    old_names = prior.port_names('balanced_z_left')
    missing_old = sorted(set(old_names) - set(adapter.world.runtime.channel_names))
    observations = [route.obs(adapter, tuple(p)) for p in
        design['inherited_tag_sources'] + design['new_goal_sources']]
    raw_conflicts = [row for row in observations if int(row['raw']) != 0]
    existing_new_sources = []
    for interface in adapter.world.interfaces:
        channel = interface.channel
        site = [channel.injection_site.x, channel.injection_site.y, channel.injection_site.z]
        if site in design['new_goal_sources']:
            existing_new_sources.append({'name': interface.name, 'site': site})
    static = static_compatibility()
    return {'version': VERSION, 'tick': int(adapter.tick), 'design': design,
        'source_observations': observations, 'nonzero_RAW_conflicts': raw_conflicts,
        'missing_inherited_names': missing_old,
        'existing_interfaces_at_new_sources': existing_new_sources,
        'static': static, 'admissible': not raw_conflicts and not missing_old
            and not existing_new_sources and static['no_listed_address_overlap'],
        'state0_is_not_assumed_vacant': True,
        'scope': 'Actual present full RAW/interfaces only; not a future functional guarantee.'}


def prepare(adapter):
    from dee_thinking import _native as native
    from dee_thinking.persistence import encode_metadata
    if KEY in dict(adapter.world.runtime.snapshot_metadata_entries):
        raise ValueError('Right pair is already admitted; do not reinstall or reset')
    screen = preflight(adapter)
    if not screen['admissible']:
        return {'kind': 'APD04_R04_sensory_P0_admission_rejected', 'admitted': False,
                'preflight': screen, 'new_native_ticks': 0}
    for name, site in zip(GOAL_NAMES, screen['design']['new_goal_sources']):
        channel = native.ChannelSpec()
        channel.name = name
        channel.injection_site = native.Coordinate(*site)
        channel.direction = native.Direction(0, 0, 0)
        channel.state = 1
        channel.semantic = 1
        channel.allow_experience = True
        channel.allow_probe = False
        interface = native.InterfaceSpec()
        interface.name = name
        interface.channel = channel
        adapter.world.declare_interface(interface)
    adapter.world.runtime.set_snapshot_metadata(KEY, encode_metadata({
        'version': VERSION, 'prepared_tick': int(adapter.tick),
        'declared_new_interfaces': GOAL_NAMES, 'contains_learned_values': False}))
    return {'kind': 'APD04_R04_explicit_P0_peripheral_interfaces', 'admitted': True,
        'preflight': screen, 'declared_new_interfaces': GOAL_NAMES,
        'placements': [], 'new_native_ticks': 0,
        'scope': 'Two new physical opportunities only; no acquired content or contextual policy.'}


def selecciona(adapter, raw_tag, raw_goal_tag, *, detail=False):
    from dee_thinking.consolidated import exact_receipt
    from capacidades import ruta_adaptativa_apd02_04 as route
    from capacidades import sensor_balanceado_apd03_r02 as prior
    from capacidades import selector_acrecion_nativo as selector
    from capacidades import sensor_balanceado_apd04 as diagnostic
    _get(adapter)
    if type(raw_tag) is not int or raw_tag not in (0, 1):
        raise ValueError('Independent observable raw tag0/1 required')
    if type(raw_goal_tag) is not int or raw_goal_tag not in (0, 1):
        raise ValueError('Independent observable raw goal-property0/1 required')
    metadata = route.get(adapter)
    if metadata['pending_window'] is not None:
        raise ValueError('A real delayed-action window is pending; never replace it')
    names = prior.port_names('balanced_z_left')
    if not set(names + GOAL_NAMES) <= set(adapter.world.runtime.channel_names):
        raise ValueError('The declared exact four sensory interfaces are required')
    k = (adapter.tick + route.DELAY + 5 + 390) // 391
    k = k if k % 2 else k + 1
    boundary = k * 391
    query_tick = boundary - route.DELAY
    source_sites = specification()['inherited_tag_sources'] + specification()['new_goal_sources']
    sources_before = [route.obs(adapter, tuple(p)) for p in source_sites]
    sensory = ([route.submit(adapter, name, raw_tag, query_tick + 3) for name in names]
               + [route.submit(adapter, name, raw_goal_tag, query_tick + 3) for name in GOAL_NAMES])
    resources = selector.query(adapter.world, query_tick, QUERY_PAYLOAD, route.P)
    for x in (-1, 0, 1):
        label = str(x)
        resources += [route.submit(adapter, route.P + '.divert.' + label, 0, query_tick + 7),
            route.submit(adapter, route.P + '.flatten.' + label, 0, query_tick + 9),
            route.submit(adapter, route.P + '.clear.' + label, 0, boundary + 10)]
    references = route.refs(adapter)
    frames = []
    for tick in range(query_tick - 1, query_tick + 7):
        adapter.run_until(tick)
        frame = {'tick': int(adapter.tick), 'offset': int(adapter.tick) - query_tick,
            'sources': [route.obs(adapter, tuple(p)) for p in source_sites],
            'historical_fixed_reader': route.read(adapter),
            'auditor_only_gates9': diagnostic.diagnostic_gates9(adapter)}
        if detail:
            frame['references'] = route.refs(adapter)
        frames.append(frame)
    reader = route.read(adapter)
    metadata['pending_window'] = {'query_tick': query_tick, 'boundary': boundary,
        'deadline': boundary - 3, 'generic_resource_requests': resources}
    metadata['uses'] += 1
    route.save(adapter, metadata)
    def receipt(row):
        return dict(row, receipt=exact_receipt(adapter.world.runtime.receipt(row['id'])))
    return {'kind': VERSION, 'raw_observed_components': [raw_tag, raw_goal_tag],
        'codec': {'left_pair': 'raw_tag duplicated', 'right_pair': 'raw_goal_tag duplicated',
            'query_payload': QUERY_PAYLOAD, 'sensory_signals': 4, 'all_scheduled_inputs': 16,
            'relation_or_right_action_computed_by_host': False},
        'query_tick': query_tick, 'boundary': boundary, 'sources_before': sources_before,
        'reader': reader, 'physical_choice': reader['choice'], 'references': references,
        'sensory_requests': [receipt(row) for row in sensory],
        'generic_resources': [receipt(row) for row in resources], 'frames': frames,
        'historical_action_decoder_unchanged': True,
        'no_contextual_understanding_or_attention_claim': True}


def finish(adapter, category, *, mode='real'):
    from capacidades import ruta_adaptativa_apd02_04 as route
    return route.consequence(adapter, category, mode=mode)


def select(adapter, raw_tag, raw_goal_tag, *, detail=False):
    return selecciona(adapter, raw_tag, raw_goal_tag, detail=detail)
