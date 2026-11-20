"""One fresh MCTS world plus the original finite V2 consequence-policy device.

The single translation is fixed before either current-medium trajectory. No
postT0 native-feedback input, host classification, cleanup or clock edit occurs.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession, prepare_magnitude_cts
from regulacion_consecuencia.native_feedback_component import prepare_component

TRANSLATION = (-25, -25, -20)


def prepare_consequence_mcts(*, consequence_medium=1, **options):
    recipe, geometry = prepare_magnitude_cts(**options)
    component, feedback = prepare_component(medium=consequence_medium, mode='intact', translation=TRANSLATION, n=67, lanes=(1,))
    placements = list(recipe.placements) + list(component.placements)
    sites = [(placement.site.x, placement.site.y, placement.site.z) for placement in placements]
    if len(sites) != len(set(sites)):
        raise ValueError('One frozen translated V2 preparation overlaps initial MCTS material; no overwrite or coordinate search authorized')
    interfaces = list(recipe.interfaces) + list(component.interfaces)
    if len({port.name for port in interfaces}) != len(interfaces):
        raise ValueError('Prepared V2 interface collision')
    recipe.placements = placements
    recipe.interfaces = interfaces
    organizations = list(recipe.organizations)
    for organization in component.organizations:
        organization.id = 'CONSEQUENCE_V2'
        organizations.append(organization)
    recipe.organizations = organizations
    geometry['consequence_regulation'] = feedback
    geometry['resources']['initial_material_sites'] = len(placements)
    geometry['resources']['interfaces'] = len(interfaces)
    geometry['finite_protocol'] = 'CPC8R.consequenceMagnitudeCTS.0_to616.v1'
    geometry['representation_version'] += '+finiteNativeConsequenceV2'
    recipe.options = {'CPC8R.relational_pair.geometry': encode_metadata(geometry)}
    return recipe, geometry


class ConsequenceMagnitudeCTSSession(MagnitudeCTSSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.setdefault('consequence_policy_observations', [])

    @classmethod
    def create(cls, identifier='CONSEQUENCE_MAGNITUDE_CTS', **options):
        recipe, geometry = prepare_consequence_mcts(**options)
        return cls(d.OrganizationalWorld.create(recipe), geometry, identifier=identifier)

    def capture_consequence(self):
        ports = self.geometry['consequence_regulation']['ports']
        self.state['consequence_policy_observations'].append({'tick': self.tick, 'panel': {key: self.observe(site) for key, site in ports.items()}})

    def run_until(self, tick):
        if type(tick) is not int or tick < self.tick:
            raise ValueError('Monotone tick required')
        for boundary in sorted(value for value in (1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15, 18) if self.tick < value <= tick):
            super().run_until(boundary)
            self.capture_consequence()
        return super().run_until(tick)

    def view(self):
        value = super().view()
        value['consequence_policy'] = {key: self.observe(site) for key, site in self.geometry['consequence_regulation']['ports'].items()}
        return value
