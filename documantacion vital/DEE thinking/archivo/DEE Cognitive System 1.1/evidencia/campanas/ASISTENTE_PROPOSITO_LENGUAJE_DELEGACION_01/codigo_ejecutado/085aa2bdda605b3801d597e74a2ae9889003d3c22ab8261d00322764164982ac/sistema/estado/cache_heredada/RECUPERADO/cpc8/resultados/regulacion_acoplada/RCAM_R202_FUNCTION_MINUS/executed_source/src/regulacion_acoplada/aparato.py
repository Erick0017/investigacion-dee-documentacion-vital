"""Native consequence -> finite P/Q -> opposed residue interception.

One freshN67 owner Runtime, no callback, future rollout, policy-target input,
state graft, RAW cleanup or clock reset. All six route opportunities exist atT0.
The R14 update rule and routing are PREPARED; actual consequence selects state.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, decode_metadata, save_world_snapshot, load_world_snapshot
from integracion.quantity_core import prepare as prepare_quantity, QuantitySession, physical
from regulacion_consecuencia.native_feedback_component import prepare_component as prepare_feedback

KEY = 'CPC8R.consequence.coupled.regulation.v1'


def move(site, vector, count=1):
    return [(int(site[i]) + int(vector[i]) * count) % 67 for i in range(3)]


def prepare(*, medium=1, routing='onpath'):
    if medium not in (-1, 1) or routing not in ('onpath', 'offpath'):
        raise ValueError('Frozen finite medium/routing domain only')
    recipe, feedback = prepare_feedback(medium=medium, mode='intact', translation=(0, 0, 0), n=67, lanes=(1,))
    quantity, qg = prepare_quantity(center=(2, 12, 36), profile='transient', guards='off_path')
    placements = list(recipe.placements) + list(quantity.placements)
    # Each zero-load opportunity is independent of the selected policy. These
    # constants solve the two piecewise native routes, not the task's answer.
    turns = [('P.escape', [35, 37, 36], 11, [0, 1, -1]),
             ('P.counterflow', [35, 12, 36], 53, [-1, -1, 0]),
             ('Q.escape', [37, 39, 36], 11, [1, -1, 0]),
             ('Q.downY', [37, 39, 44], 19, [0, -1, -1]),
             ('Q.downZ', [37, 12, 44], 46, [0, 1, -1]),
             ('Q.counterflow', [37, 12, 36], 54, [1, 0, 1])]
    records = []
    for name, target, tick, direction in turns:
        programmed = move(target, (0, 1, 0), 12) if routing == 'offpath' else target
        site = move(programmed, direction, -tick)
        placement = d.InitialPlacement()
        placement.site = d.Coordinate(*site)
        placement.raw = d.pack_record(1, 0, *direction, 1)
        placement.clock = 0
        placement.role = 'Fixed neutral consequence-policy route ' + name
        placements.append(placement)
        records.append({'id': name, 'target_onpath': target, 'programmed_target': programmed, 'tick': tick,
                        'direction': direction, 'source_site': site, 'payload': 0, 'clock': '0'})
    sites = [(placement.site.x, placement.site.y, placement.site.z) for placement in placements]
    if len(sites) != len(set(sites)):
        raise ValueError('Frozen coupled recipe has initial material overlap')
    recipe.placements = placements
    recipe.interfaces = list(quantity.interfaces)
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    geometry = {'schema': 'CPC8R.consequence.coupled.regulation.geometry.v1', 'N': 67, 'medium': medium,
                'routing': routing, 'feedback': feedback, 'quantity': qg, 'neutral_turns': records,
                'policy_after_escape': {'P': {'site': [35, 37, 36], 'tick': 11, 'direction': [0, 1, 0]},
                                        'Q': {'site': [37, 39, 36], 'tick': 11, 'direction': [0, 0, 1]}},
                'counterflows': {'P': {'source': [35, 12, 36], 'formed_tick': 53, 'direction': [-1, 0, 0],
                                       'pre_interception_site': [11, 12, 36], 'interception_site': [10, 12, 36]},
                                'Q': {'source': [37, 12, 36], 'formed_tick': 54, 'direction': [1, 0, 0],
                                       'pre_interception_site': [60, 12, 36], 'interception_site': [61, 12, 36]}},
                'ticks': {'consequence': 2, 'actual_return': 4, 'comparison': 5, 'policy': 9, 'action': 10,
                          'first_quantity': 70, 'residue_before_interception': 77, 'interception': 78,
                          'later_quantity': 137, 'horizon': 141},
                'resources': {'V2_initial_material': 24, 'quantity_initial_material': 7, 'neutral_routes_initial_material': 6,
                              'total_initial_material': len(placements), 'interfaces': len(recipe.interfaces), 'basic_buffers_bytes': 32 * 67 ** 3},
                'prepared': 'Finite retainP/switchQ law, expectation, six fixed route opportunities and gradient comparator. Opposite counterflows are not selected by Python.',
                'experience': 'Current native world medium changes V2 actualreturn; quantity reference receives its own actual cue/value. No error, reward, desiredroute or targetcomparison is submitted.',
                'scope': 'Finite consequence-updated regulation under a prepared rule, not learned general attention, utility rule acquisition or R2general.'}
    recipe.options = {'CPC8R.coupledRegulation.geometry': encode_metadata(geometry)}
    recipe.domain = geometry['scope']
    return recipe, geometry


class CoupledRegulationSession:
    def __init__(self, world, geometry, state=None):
        self.world = world
        self.geometry = deepcopy(geometry)
        self.state = deepcopy(state) if state is not None else {'frames': []}
        self.quantity = QuantitySession(world, self.geometry['quantity'], self.state.get('quantity'))

    @classmethod
    def create(cls, **options):
        recipe, geometry = prepare(**options)
        return cls(d.OrganizationalWorld.create(recipe), geometry)

    @property
    def tick(self):
        return int(self.world.runtime.current_tick)

    def curriculum(self, reference=31, objects=(16, 45)):
        if self.tick != 0 or len(objects) != 2:
            raise ValueError('Fresh finite actual quantity curriculum only')
        self.quantity.experience_reference(reference)
        for index, value in enumerate(objects):
            self.quantity.present_object(value, round_index=index)
        for tick in (69, 136):
            self.quantity.input('quantity.reader', 7, tick, True)

    def run_until(self, tick):
        if type(tick) is not int or tick < self.tick:
            raise ValueError('Monotone ticks required')
        self.world.run_until(tick)

    def observe(self, site):
        return exact_observation(self.world.runtime.observe(d.Coordinate(*site)))

    def capture(self):
        feedback = {key: self.observe(site) for key, site in self.geometry['feedback']['ports'].items()}
        quantity = {key: self.observe(self.geometry['quantity'][key]) for key in ('center', 'reference_site', 'object_site', 'reference_hub')}
        flows = {}
        for name, flow in self.geometry['counterflows'].items():
            site = move(flow['source'], flow['direction'], self.tick - flow['formed_tick'])
            flows[name] = {'candidate_site': site, 'physical': self.observe(site),
                           'pre_interception_site': self.observe(flow['pre_interception_site']), 'interception_site': self.observe(flow['interception_site'])}
        row = {'tick': self.tick, 'feedback': feedback, 'quantity': quantity, 'counterflows': flows}
        if self.tick in (4, 5, 9, 10, 11, 53, 54, 69, 70, 77, 78, 79, 85, 86, 136, 137):
            centers = {'quantity': self.geometry['quantity']['center']}
            if self.tick in (77, 78, 79):
                centers.update({key: flow['interception_site'] for key, flow in self.geometry['counterflows'].items()})
            if self.tick == 11:
                centers.update({key: flow['site'] for key, flow in self.geometry['policy_after_escape'].items()})
            row['Moore27'] = {key: [self.observe(move(site, (x, y, z))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)] for key, site in centers.items()}
        self.state['frames'].append(row)
        return row

    def receipts(self):
        return self.quantity.receipts()

    def save(self, path):
        self.state['quantity'] = deepcopy(self.quantity.state)
        self.world.runtime.set_snapshot_metadata(KEY, encode_metadata({'geometry': self.geometry, 'state': self.state, 'tick': self.tick,
                                                                      'channels': sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world, path)

    @classmethod
    def load(cls, path):
        world, _ = load_world_snapshot(path)
        metadata = decode_metadata(dict(world.runtime.snapshot_metadata_entries)[KEY])
        if metadata['tick'] != int(world.runtime.current_tick) or metadata['channels'] != sorted(world.runtime.channel_names):
            raise ValueError('Operative snapshot identity mismatch')
        return cls(world, metadata['geometry'], metadata['state'])
