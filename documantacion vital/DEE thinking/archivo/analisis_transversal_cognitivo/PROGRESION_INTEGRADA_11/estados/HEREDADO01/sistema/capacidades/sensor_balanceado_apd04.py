"""APD04 R03 sensory-representation candidate, no new physical anatomy.

The two old opposite-Z ports carry the SAME independently observed raw tag.
The other elementary property, raw_goal_tag, independently changes only the
existing query payload through the frozen affine codec5+2*goal. No equality,
relevance, source recommendation or expected action is computed by Python.

Four combinations of TWO elementary bits are available through THREE material
input signals; this is not four independent observed variables. The former R02
sensor remains intact. Importing creates no Runtime or new Native ticks.
"""
VERSION = 'APD04.balanced_tag_and_affine_goal.existing_sources.prospective.R03'
FAMILY = 'balanced_z_left'
QUERY_BASE = 5
QUERY_GOAL_STEP = 2


def diagnostic_gates9(adapter):
    """Passive nine-class observation, NEVER the action decoder for R03.

    The fixed actor still uses route.read's three historical Z0 gates. This
    broader diagnostic can identify out-of-reader material but cannot replace
    a missing historical action retrospectively or guide the next stimulus.
    """
    from capacidades import ruta_adaptativa_apd02_04 as route
    observations = []
    matches = []
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            observation = route.obs(adapter, route.at((2*x, 2, 2*z)))
            observations.append(observation)
            if (observation['state'] > 0 and observation['semantic'] == 1
                    and observation['direction'] == [x, 1, z]):
                matches.append({'x': x, 'z': z, 'observation': observation})
    return {'tick': int(adapter.tick), 'observations': observations,
        'coherent_direction_matches': matches,
        'scope': 'AUDITOR ONLY; not an alternative action decoder or an acquired faculty.'}


def selecciona(adapter, raw_tag, raw_goal_tag, *, detail=False):
    from dee_thinking.consolidated import exact_receipt
    from capacidades import ruta_adaptativa_apd02_04 as route
    from capacidades import sensor_balanceado_apd03_r02 as prior
    from capacidades import selector_acrecion_nativo as selector

    if type(raw_tag) is not int or raw_tag not in (0, 1):
        raise ValueError('An independently observable exact raw tag0/1 is required')
    if type(raw_goal_tag) is not int or raw_goal_tag not in (0, 1):
        raise ValueError('An independently observable exact objective property0/1 is required')
    metadata = route.get(adapter)
    if metadata['pending_window'] is not None:
        raise ValueError('A physical R04 delayed-action window is pending; do not replace it')
    names = prior.port_names(FAMILY)
    if not set(names) <= set(adapter.world.runtime.channel_names):
        raise ValueError('The exact two inherited APD03 sensor interfaces are required')
    k = (adapter.tick + route.DELAY + 5 + 390) // 391
    k = k if k % 2 else k + 1
    boundary = k * 391
    query_tick = boundary - route.DELAY
    sources_before = [prior.observation(adapter, site) for site in prior.sites(FAMILY)]

    # Two matched tag signals, plus one independently affinely coded goal signal.
    # The action decoder below never receives any of these scalar arguments.
    tag_requests = [route.submit(adapter, name, raw_tag, query_tick + 3)
                    for name in names]
    query_payload = QUERY_BASE + QUERY_GOAL_STEP * raw_goal_tag
    resources = selector.query(adapter.world, query_tick, query_payload, route.P)
    goal_query_request = resources[0]
    for x in (-1, 0, 1):
        label = str(x)
        resources += [
            route.submit(adapter, route.P + '.divert.' + label, 0, query_tick + 7),
            route.submit(adapter, route.P + '.flatten.' + label, 0, query_tick + 9),
            route.submit(adapter, route.P + '.clear.' + label, 0, boundary + 10),
        ]
    references_before = route.refs(adapter)
    frames = []
    for tick in range(query_tick - 1, query_tick + 7):
        adapter.run_until(tick)
        frame = {'tick': int(adapter.tick), 'offset': int(adapter.tick) - query_tick,
            'sources': [prior.observation(adapter, site) for site in prior.sites(FAMILY)],
            'historical_fixed_reader': route.read(adapter),
            'auditor_only_gates9': diagnostic_gates9(adapter)}
        if detail:
            frame['references'] = route.refs(adapter)
        frames.append(frame)
    reader = route.read(adapter)
    metadata['pending_window'] = {
        'query_tick': query_tick, 'boundary': boundary, 'deadline': boundary - 3,
        'generic_resource_requests': resources,
    }
    metadata['uses'] += 1
    route.save(adapter, metadata)
    def receipt(row):
        return dict(row, receipt=exact_receipt(adapter.world.runtime.receipt(row['id'])))
    return {'kind': VERSION, 'family': FAMILY,
        'raw_observed_components': [raw_tag, raw_goal_tag],
        'codec': {'tag_port0': 'raw_tag', 'tag_port1': 'raw_tag',
            'goal_query': '5+2*raw_goal_tag', 'query_base': QUERY_BASE,
            'query_goal_step': QUERY_GOAL_STEP, 'tag_injection_offset': 3,
            'elementary_variables': 2, 'possible_bit_pairs': 4,
            'material_sensory_signals': 3,
            'signal_count_and_payloads_are_not_equal_to_R02': True},
        'query_tick': query_tick, 'boundary': boundary,
        'sources_before': sources_before, 'reader': reader,
        'physical_choice': reader['choice'], 'references': references_before,
        'frames': frames,
        # Disjoint roles: the goal-bearing query is not counted a second time
        # among generic-only inputs. pending_window retains the exact full list.
        'sensory_requests': [receipt(row) for row in tag_requests + [goal_query_request]],
        'generic_only_requests': [receipt(row) for row in resources[1:]],
        'all_scheduled_requests': [receipt(row) for row in tag_requests + resources],
        'original_action_reader_unchanged': True,
        'diagnostic_9gates_never_used_for_action': True,
        'component_relation_not_computed_by_python': True,
        'no_new_geometry_or_acquired_content_write': True,
        'scope': 'Prepared sensory repair candidate. Neither contextual understanding '
                 'nor learned attention follows from changing the query payload.'}


def finish(adapter, category, *, mode='real'):
    from capacidades import ruta_adaptativa_apd02_04 as route
    return route.consequence(adapter, category, mode=mode)


def select(adapter, raw_tag, raw_goal_tag, *, detail=False):
    return selecciona(adapter, raw_tag, raw_goal_tag, detail=detail)
