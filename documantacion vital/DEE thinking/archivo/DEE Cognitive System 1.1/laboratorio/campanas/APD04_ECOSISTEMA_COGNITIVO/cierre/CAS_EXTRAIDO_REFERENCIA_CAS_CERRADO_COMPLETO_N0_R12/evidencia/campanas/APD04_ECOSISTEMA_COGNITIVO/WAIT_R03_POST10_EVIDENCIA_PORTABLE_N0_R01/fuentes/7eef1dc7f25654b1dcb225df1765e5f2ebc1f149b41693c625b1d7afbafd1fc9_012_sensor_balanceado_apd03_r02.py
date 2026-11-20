"""APD03 candidate: one raw fact, a symmetric pair, existing R04 action trace.

Importing this module creates no Runtime and advances no tick.  The family is
selected prospectively for the entire candidate, never from an expected answer.
No teacher, correct action, hidden operand or learned choice enters this codec.
"""
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from capacidades import ruta_adaptativa_apd02_04 as route
from capacidades import selector_acrecion_nativo as selector

VERSION = 'APD03.balanced_raw_context.prospective.R02'
FAMILIES = {
    'balanced_z_left': {'offsets': [(-1, 0, 1), (-1, 0, -1)], 'direction': (0, 0, 0)},
}


def sites(family):
    return [route.at(offset) for offset in FAMILIES[family]['offsets']]


def observation(adapter, coordinate):
    return exact_observation(adapter.world.runtime.observe(d.Coordinate(*coordinate)))


def port_names(family):
    return ['APD03.balanced_context.R02.' + family + '.raw_fact.' + str(index) for index in range(2)]


def preflight(adapter, family):
    if family not in FAMILIES:
        raise ValueError('A prospectively selected physical family is required')
    route.get(adapter)
    source = [observation(adapter, coordinate) for coordinate in sites(family)]
    return {
        'family': family, 'specification': FAMILIES[family],
        'sources_before': source, 'admissible': all(int(row['raw']) == 0 for row in source),
        'no_matter_removed_or_relocated': True,
        'scope': 'Current exact input RAW0, not a future isolation proof',
    }


def declare(adapter, family):
    screen = preflight(adapter, family)
    if not screen['admissible']:
        raise ValueError('Sensor source is nonzero RAW; no cleanup or relocation')
    names = port_names(family)
    if set(names) & set(adapter.world.runtime.channel_names):
        raise ValueError('New candidate channel already exists; no silent replacement')
    for name, coordinate in zip(names, sites(family)):
        channel = d.ChannelSpec()
        channel.name = name
        channel.injection_site = d.Coordinate(*coordinate)
        channel.direction = d.Direction(*FAMILIES[family]['direction'])
        channel.state = 1
        channel.semantic = 1
        channel.allow_experience = True
        channel.allow_probe = False
        interface = d.InterfaceSpec()
        interface.name = name
        interface.channel = channel
        adapter.world.declare_interface(interface)
    return screen


def use(adapter, raw_fact, *, family, capture=None):
    """Duplicate the exact raw0/1 on a fixed symmetric pair at q+3.

    The environment decides which fact is currently observable. Both values
    produce material input at the same fixed symmetric sites and scheduled phase.
    Two raw samples, not a Python-computed gradient, reach the native kernel.
    Capture is an auditor-only passive callback; its values cannot select action.
    """
    if type(raw_fact) is not int or raw_fact not in (0, 1):
        raise ValueError('Exact public raw bit0/1 only, not an action or answer')
    if family not in FAMILIES:
        raise ValueError('Unknown prospectively fixed sensor family')
    meta = route.get(adapter)
    if meta['pending_window'] is not None:
        raise ValueError('Complete actual pending action trace first; never overwrite')
    names = port_names(family)
    if not set(names) <= set(adapter.world.runtime.channel_names):
        raise ValueError('Explicit candidate sensor declaration is required')
    k = (adapter.tick + route.DELAY + 5 + 390) // 391
    k = k if k % 2 else k + 1
    boundary = k * 391
    q = boundary - route.DELAY
    source_before = [observation(adapter, coordinate) for coordinate in sites(family)]
    sensory = [route.submit(adapter, name, raw_fact, q + 3) for name in names]
    resources = selector.query(adapter.world, q, 5, route.P)
    for x in (-1, 0, 1):
        label = str(x)
        resources += [
            route.submit(adapter, route.P + '.divert.' + label, 0, q + 7),
            route.submit(adapter, route.P + '.flatten.' + label, 0, q + 9),
            route.submit(adapter, route.P + '.clear.' + label, 0, boundary + 10),
        ]
    references = route.refs(adapter)
    frames = []
    for tick in range(q - 1, q + 7):
        adapter.run_until(tick)
        frame = {
            'tick': adapter.tick, 'offset': adapter.tick - q,
            'sources': [observation(adapter, coordinate) for coordinate in sites(family)],
            'fixed_reader': route.read(adapter),
            'references': route.refs(adapter),
        }
        if capture is not None:
            frame['passive_capture'] = capture(adapter)
        frames.append(frame)
    reader = route.read(adapter)
    meta['pending_window'] = {
        'query_tick': q, 'boundary': boundary, 'deadline': boundary - 3,
        'generic_resource_requests': resources,
    }
    meta['uses'] += 1
    route.save(adapter, meta)
    return {
        'kind': VERSION, 'family': family, 'raw_observed_fact': raw_fact,
        'query_tick': q, 'boundary': boundary, 'sources_before': source_before,
        'reader': reader, 'references': references, 'frames': frames,
        'sensory_requests': [dict(row, receipt=exact_receipt(adapter.world.runtime.receipt(row['id']))) for row in sensory],
        'generic_resources': route.receipts(adapter, resources),
        'trace_not_reinjected_from_reader': True,
        'fixed_decoder_not_selected_by_fact': True,
        'raw_fact_is_not_a_teacher': True,
    }


def finish_without_feedback(adapter):
    """Finish predeclared resources with no material environmental consequence."""
    result = route.consequence(adapter, 'SUCCESS', mode='omit')
    return {'kind': 'calendar_only_no_quality_feedback', 'native_cleanup': result}
