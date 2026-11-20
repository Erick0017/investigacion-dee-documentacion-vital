"""APD04 prospective sensor: two independent raw bits, SAME APD03 sources.

No Runtime or physical geometry is created on import. No source is added,
cleared, relocated or re-timed by observing an answer. The two raw elementary
properties enter their pre-existing distinct ports, independently. Python does
not compare them or derive a relevance/selection/class bit. Whether the native
response can use their relation is an experimental question, not an assertion.
"""
VERSION = 'APD04.two_independent_raw_bits.same_sources.prospective.R02'
FAMILY = 'balanced_z_left'


def selecciona(adapter, raw_tag, raw_goal_tag, *, detail=False):
    """Common R04 trace window plus one independent bit at each fixed source.

    Both properties are already observable to the participant. Neither may be
    an auditor's computed equality, relevance, right action or hidden target.
    Material return must be committed afterward with finish(), within the
    pre-existing delayed-action contract. Missing output is not replaced.
    """
    from dee_thinking.consolidated import exact_receipt
    from capacidades import ruta_adaptativa_apd02_04 as route
    from capacidades import sensor_balanceado_apd03_r02 as prior
    from capacidades import selector_acrecion_nativo as selector

    if type(raw_tag) is not int or raw_tag not in (0, 1):
        raise ValueError('The first elementary observation must be exact raw0/1')
    if type(raw_goal_tag) is not int or raw_goal_tag not in (0, 1):
        raise ValueError('The second elementary observation must be exact raw0/1')
    metadata = route.get(adapter)
    if metadata['pending_window'] is not None:
        raise ValueError('Complete the existing physical delayed-action window first')
    names = prior.port_names(FAMILY)
    if not set(names) <= set(adapter.world.runtime.channel_names):
        raise ValueError('The actual inherited APD03 sensor interfaces are required')

    k = (adapter.tick + route.DELAY + 5 + 390) // 391
    k = k if k % 2 else k + 1
    boundary = k * 391
    query_tick = boundary - route.DELAY
    sources_before = [prior.observation(adapter, site) for site in prior.sites(FAMILY)]
    # No equality, ranking, aggregate, relevance bit or target-dependent route.
    sensory = [
        route.submit(adapter, names[0], raw_tag, query_tick + 3),
        route.submit(adapter, names[1], raw_goal_tag, query_tick + 3),
    ]
    resources = selector.query(adapter.world, query_tick, 5, route.P)
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
        frame = {
            'tick': int(adapter.tick), 'offset': int(adapter.tick) - query_tick,
            'sources': [prior.observation(adapter, site) for site in prior.sites(FAMILY)],
            'fixed_reader': route.read(adapter),
        }
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
    return {
        'kind': VERSION, 'family': FAMILY,
        'raw_observed_components': [raw_tag, raw_goal_tag],
        'codec': {'port0': 'first already-observable elementary tag0/1',
                  'port1': 'second already-observable elementary goal-property0/1',
                  'injection_offset': 3, 'both_are_material_inputs': True},
        'query_tick': query_tick, 'boundary': boundary,
        'sources_before': sources_before, 'reader': reader,
        'physical_choice': reader['choice'], 'references': references_before,
        'frames': frames,
        'sensory_requests': [dict(row, receipt=exact_receipt(
            adapter.world.runtime.receipt(row['id']))) for row in sensory],
        'generic_resources': route.receipts(adapter, resources),
        'trace_not_reinjected_from_reader': True,
        'component_relation_not_computed_in_python': True,
        'no_new_geometry_or_acquired_content_write': True,
    }


def finish(adapter, category, *, mode='real'):
    """Existing generic R04 consequence; receives no selected action/answer."""
    from capacidades import ruta_adaptativa_apd02_04 as route
    return route.consequence(adapter, category, mode=mode)


def select(adapter, raw_tag, raw_goal_tag, *, detail=False):
    """English alias of the same single physical interaction, not another use."""
    return selecciona(adapter, raw_tag, raw_goal_tag, detail=detail)
