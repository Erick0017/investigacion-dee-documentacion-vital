"""Instrumented effect-fingerprint context, explicitly NOT causal identity.

Both local preparations acquire material calibrations and receive identical
current material effects. Actor labels are NEVER inputs. Thus actor exchange
with equal physical fingerprints must be indistinguishable; the experiment
does not claim an action of E1, proprioception, selfhood, or YO/TU semantics.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, decode_metadata, save_world_snapshot, load_world_snapshot
from integracion.quantity_core import prepare as quantity_recipe

KEY = 'CPC9.perspective.effect_calibration.instrumented.v1'


def prepare():
    recipes = []
    geometries = {}
    ports = []
    initial = []
    for name, center in (('A', (15, 15, 15)), ('B', (45, 45, 45))):
        recipe, geometry = quantity_recipe(center, profile='transient', guards='on_path')
        initial += list(recipe.placements)
        for p in recipe.interfaces:
            p.name = name + '.' + p.name
            c = p.channel
            c.name = name + '.' + c.name
            p.channel = c
            ports.append(p)
        geometries[name] = geometry
        recipes.append(recipe)
    positions = [(p.site.x, p.site.y, p.site.z) for p in initial]
    if len(positions) != len(set(positions)):
        raise ValueError('Prepared site overlap')
    recipe = recipes[0]
    recipe.placements = initial
    recipe.interfaces = ports
    recipe.domain = 'Instrumented contextual matching of acquired effect fingerprints, not own/other causal identity.'
    geometry = {'schema': KEY, 'N': 67, 'observers': geometries,
        'resources': {'initial_materials': len(initial), 'interfaces': len(ports), 'basic_buffers_bytes': 32 * 67**3},
        'sensor_contract': 'Generator presents actual material calibration and current material effect. It never sends actor label or the resolved relation. This is a sensory calibration task, NOT an action initiated by the organism.',
        'identity_limit': 'Equal effect signatures from different actor labels are physically indistinguishable under this interface. Observer and organism knowledge are not identified.'}
    recipe.options = {KEY: encode_metadata(geometry)}
    return recipe, geometry


class EffectContextSession:
    def __init__(self, world, geometry, requests=None):
        self.world = world
        self.geometry = deepcopy(geometry)
        self.requests = deepcopy(requests) if requests is not None else []

    @classmethod
    def create(cls):
        recipe, geometry = prepare()
        return cls(d.OrganizationalWorld.create(recipe), geometry)

    @property
    def tick(self):
        return int(self.world.runtime.current_tick)

    def input(self, port, value, tick, probe=False):
        rr = (self.world.probe if probe else self.world.submit)(port, value, tick)
        self.requests.append({'id': int(rr.id), 'port': port, 'payload': value, 'tick': tick, 'probe': probe})

    def curriculum(self, references, effects, association='paired', omit_reference=None):
        if self.tick != 0 or len(references) != 2 or len(effects) != 3:
            raise ValueError('Fresh two-context finite curriculum')
        for name, value in zip(('A', 'B'), references):
            if name != omit_reference:
                self.input(name + '.quantity.reference.cue', 5, int(association == 'unpaired'))
                self.input(name + '.quantity.reference.resource', value, 0)
            for index, current_effect in enumerate(effects):
                at = 65 + 67 * index
                self.input(name + '.quantity.object.cue', 5, at)
                self.input(name + '.quantity.object.resource', current_effect, at)
                self.input(name + '.quantity.reader', 7, at + 4, True)
            self.input(name + '.quantity.other.cue', 5, 110)
            self.input(name + '.quantity.other.event', 11, 110)
            self.input(name + '.quantity.other.cue', 9, 177, True)

    def observe(self, site):
        return exact_observation(self.world.runtime.observe(d.Coordinate(*site)))

    def run_until(self, tick):
        self.world.run_until(tick)
        return {'tick': self.tick, 'observers': {name: {
            'reference': self.observe(g['reference_site']), 'current_effect': self.observe(g['object_site']),
            'response': self.observe(g['center'])} for name, g in self.geometry['observers'].items()}}

    def receipts(self):
        return [{**r, 'receipt': exact_receipt(self.world.runtime.receipt(r['id']))} for r in self.requests]

    def save(self, path):
        self.world.runtime.set_snapshot_metadata(KEY, encode_metadata({'geometry': self.geometry, 'requests': self.requests, 'tick': self.tick}))
        return save_world_snapshot(self.world, path, compress=True)

    @classmethod
    def load(cls, path):
        world, _ = load_world_snapshot(path, max_bytes=512 * 1024**2)
        m = decode_metadata(dict(world.runtime.snapshot_metadata_entries)[KEY])
        if m['tick'] != int(world.runtime.current_tick):
            raise ValueError('Tick mismatch')
        return cls(world, m['geometry'], m['requests'])
