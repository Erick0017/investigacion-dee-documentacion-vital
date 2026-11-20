"""CPC9 count-to-form: fixed symmetric access prepared before experience.

The count sensor calibration and comparison are prepared instruments. Contact
history, comparison product, and opaque form memory evolve in official v27.
No observed state chooses a bank, reader, output, or later experience.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, decode_metadata, save_world_snapshot, load_world_snapshot
from count_sign.branch_session import prepare_branch
from count_sign.session import port, move

KEY = 'CPC9.count_access.symmetric.v2'


def prepare_component(case):
    """Return an untrained recipe and all-fixed geometry; N67 only."""
    if case.get('delay', 0) or case.get('translation', [0, 0, 0]) != [0, 0, 0]:
        raise ValueError('This revision has no unvalidated translation/time adaptation')
    spec = dict(case, readout='transient_gap', bridge_guard=case.get('bridge_guard', 'onpath'), unit_load=2)
    recipe, geometry = prepare_branch(spec)
    old_reads = {n[k] for n in geometry['names'] for k in ('query1_port', 'query2_port')}
    ports = [p for p in recipe.interfaces if p.name not in old_reads]
    readers = []
    unique = {}
    for n in geometry['names']:
        for heading in (-1, 0, 1):
            q1 = move(n['memory_site'], (heading, 1, 0), 20)
            q2 = move(q1, (heading, 1, 1), 34)
            row = {'route_axis_candidate': n['route_axis_candidate'],
                   'candidate_comparator_x': n['candidate_comparator_x'],
                   'heading': heading, 'memory_site': n['memory_site']}
            for index, q, v, tick in ((1, q1, (0, 0, 1), 114), (2, q2, (0, 0, -1), 148)):
                injection = move(q, v, -3)
                key = (*injection, *v, 77, 1, tick)
                if key not in unique:
                    name = 'count.access.fixed.' + str(len(unique))
                    unique[key] = {'port': name, 'tick': tick - 3, 'payload': 7, 'kind': 'probe'}
                    ports.append(port(name, injection, v, 77))
                row['query' + str(index)] = {'site': q, 'port': unique[key]['port'], 'tick': tick,
                    'expected_direction': [heading, 1, 1 if index == 1 else 0]}
            readers.append(row)
    recipe.interfaces = ports
    geometry.update(schema=KEY, fixed_readers=readers, fixed_reader_requests=list(unique.values()),
                    old_reader_ports_removed=sorted(old_reads),
                    criterion='Active semantic1 s_reg>7 and physical direction equals fixed heading,+Y,+Z at114, heading,+Y,0 at148; no truth consulted for routing',
                    prepared='Inherited unit2 contact normalization, threshold8, all three comparison routes; both signed memory trajectories receive equal fixed probes fromT0. No learned cardinality rule or policy is claimed.',
                    change_from_CPC8='V1 replaced zero-X by+/-X and lost B-only access. V2 preserves zero-X AND both signed X trajectories atT0. All histories receive identical interfaces and probe schedule; V1 adverses remain.')
    geometry['resources']['interfaces'] = len(ports)
    geometry['resources']['fixed_probe_requests'] = len(unique)
    recipe.options = {KEY: encode_metadata(geometry)}
    recipe.domain = 'Finite calibrated normalized-contact-to-form association with symmetric prepared access, N67/T0-171.'
    return recipe, geometry


def curriculum(session, form='paired', route=True, query=True):
    """Fixed environmental events; all candidate banks stimulated equally."""
    if session.tick != 0 or form not in ('paired', 'unpaired', 'omitted'):
        raise ValueError('Fresh finite protocol or declared form control required')
    session.input('counter.cue', 5, 7)
    for name in ('A', 'B'):
        session.input('counter.free.guard.' + name, 0, 6)
    for b in session.geometry['branches']:
        if route:
            session.input(b['formatter_port'], 0, 17)
        for suffix, load, tick in (('quantity.object.cue', 5, 86), ('quantity.object.resource', 3, 86), ('quantity.reader', 7, 90)):
            session.input(b['prefix'] + suffix, load, tick, suffix.endswith('reader'))
    for bank in session.geometry['names']:
        if form != 'omitted':
            session.input(bank['record_port'], 5, 90 + (5 if form == 'unpaired' else 0))
        session.input(bank['normalizer_port'], 0, 91)
    if query:
        for reader in session.geometry['fixed_reader_requests']:
            session.input(reader['port'], reader['payload'], reader['tick'], True)
    session.input('extra.cue', 5, 100)
    session.input('extra.event', 11, 100)
    session.input('extra.query', 9, 167, True)


class CountAccessSession:
    def __init__(self, world, geometry, state=None, identifier='COUNT_ACCESS'):
        self.world = world
        self.geometry = deepcopy(geometry)
        self.state = deepcopy(state) if state is not None else {'requests': []}
        self.identifier = identifier

    @classmethod
    def create(cls, case):
        recipe, geometry = prepare_component(case)
        return cls(d.OrganizationalWorld.create(recipe), geometry, identifier=case['id'])

    @property
    def tick(self):
        return int(self.world.runtime.current_tick)

    def input(self, name, payload, tick, probe=False):
        if type(payload) is not int or not 0 <= payload <= 65535 or type(tick) is not int or tick < self.tick:
            raise ValueError('Exact current/future inputs only')
        rr = (self.world.probe if probe else self.world.submit)(name, payload, tick)
        self.state['requests'].append({'id': int(rr.id), 'port': name, 'payload': payload,
                                      'tick': tick, 'kind': 'probe' if probe else 'experience'})
        return exact_receipt(rr)

    def observe(self, q):
        return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))

    def view(self):
        g = self.geometry
        return {'tick': self.tick, 'counter': self.observe(g['count']['collector']),
                'branches': [{'route_axis_candidate': b['route_axis_candidate'],
                              'reference': self.observe(b['quantity']['reference_site']),
                              'object': self.observe(b['quantity']['object_site']),
                              'comparison': self.observe(b['quantity']['center'])} for b in g['branches']],
                'form_banks': [{'route_axis_candidate': n['route_axis_candidate'],
                               'candidate_comparator_x': n['candidate_comparator_x'],
                               'physical': self.observe(n['memory_site'])} for n in g['names']],
                'readers': [{**r, 'reading1': self.observe(r['query1']['site']),
                            'reading2': self.observe(r['query2']['site'])} for r in g['fixed_readers']],
                'extra': self.observe(g['count']['extra'])}

    def run_until(self, tick):
        if type(tick) is not int or tick < self.tick:
            raise ValueError('Monotone time')
        self.world.run_until(tick)
        return self.view()

    def receipts(self):
        return [{**r, 'receipt': exact_receipt(self.world.runtime.receipt(r['id']))}
                for r in self.state['requests']]

    def save(self, path):
        self.world.runtime.set_snapshot_metadata(KEY, encode_metadata({
            'geometry': self.geometry, 'state': self.state, 'identifier': self.identifier,
            'tick': self.tick, 'channels': sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world, path, compress=True)

    @classmethod
    def load(cls, path):
        world, _ = load_world_snapshot(path, max_bytes=512 * 1024**2)
        meta = decode_metadata(dict(world.runtime.snapshot_metadata_entries)[KEY])
        if meta['tick'] != int(world.runtime.current_tick) or meta['channels'] != sorted(world.runtime.channel_names):
            raise ValueError('Physical/operational snapshot mismatch')
        return cls(world, meta['geometry'], meta['state'], meta['identifier'])


def mount_component(base_recipe, component_recipe, prefix='C9COUNT.'):
    """Prepared-fromT0 merge only, no snapshot/material transplant.

    Native collisions at equal initial sites or duplicate public names reject the
    preparation. Later route compatibility remains an experiment, not inferred.
    """
    placements = list(base_recipe.placements) + list(component_recipe.placements)
    sites = [(p.site.x, p.site.y, p.site.z) for p in placements]
    if len(sites) != len(set(sites)):
        raise ValueError('Prepared initial material overlap')
    ports = list(base_recipe.interfaces)
    aliases = {}
    for interface in component_recipe.interfaces:
        old = interface.name
        interface.name = prefix + old
        channel = interface.channel
        channel.name = prefix + channel.name
        interface.channel = channel
        ports.append(interface)
        aliases[old] = interface.name
    if len({p.name for p in ports}) != len(ports):
        raise ValueError('Prepared interface name overlap')
    base_recipe.placements = placements
    base_recipe.interfaces = ports
    return base_recipe, aliases
