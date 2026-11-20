"""New fresh auxiliary candidate: unchanged MCTS plus the coupled regulator.

This is not the selected MCTS MAIN and never loads/grafts its trained state.
The seven additional input names have only a fixed R. namespace change.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.quantity_core import QuantitySession
from transferencia_magnitud.cts_integrado import prepare_magnitude_cts, MagnitudeCTSSession
from regulacion_acoplada.aparato import prepare, CoupledRegulationSession


class PrefixedQuantitySession(QuantitySession):
    def input(self, port, payload, tick, probe=False):
        return super().input('R.' + port, payload, tick, probe)


def prepare_coupled_mcts(*, medium=1, routing='onpath', **options):
    recipe, geometry = prepare_magnitude_cts(**options)
    aux, auxiliary = prepare(medium=medium, routing=routing)
    placements = list(recipe.placements) + list(aux.placements)
    sites = [(item.site.x, item.site.y, item.site.z) for item in placements]
    if len(sites) != len(set(sites)):
        raise ValueError('Initial material overlap; no silent replacement allowed')
    ports = []
    for item in aux.interfaces:
        item.name = 'R.' + item.name
        channel = item.channel
        channel.name = 'R.' + channel.name
        item.channel = channel
        ports.append(item)
    interfaces = list(recipe.interfaces) + ports
    if len({item.name for item in interfaces}) != len(interfaces):
        raise ValueError('Interface collision')
    recipe.placements, recipe.interfaces = placements, interfaces
    geometry['coupled_regulation'] = auxiliary
    geometry['resources']['initial_material_sites'] = len(placements)
    geometry['resources']['interfaces'] = len(interfaces)
    geometry['representation_version'] += '+ConsequenceCoupledRegulation1'
    geometry['finite_protocol'] = 'CPC8R.coupledRegulationMCTS.0_to616.v1'
    recipe.options = {'CPC8R.relational_pair.geometry': encode_metadata(geometry)}
    return recipe, geometry


class CoupledMagnitudeCTSSession(MagnitudeCTSSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coupled_regulation = CoupledRegulationSession(self.world, self.geometry['coupled_regulation'], self.state.get('coupled_regulation'))
        self.coupled_regulation.quantity = PrefixedQuantitySession(self.world, self.geometry['coupled_regulation']['quantity'], self.coupled_regulation.state.get('quantity'))

    @classmethod
    def create(cls, identifier='COUPLED_MAGNITUDE_CTS_AUX', **options):
        recipe, geometry = prepare_coupled_mcts(**options)
        return cls(d.OrganizationalWorld.create(recipe), geometry, identifier=identifier)

    def curriculum(self, *, regulation_reference=31, regulation_objects=(16, 45), **options):
        super().curriculum(**options)
        self.coupled_regulation.curriculum(regulation_reference, tuple(regulation_objects))

    def view(self):
        result = super().view()
        # The passive coupled observer has no input/advance side effects.
        if hasattr(self, 'coupled_regulation'):
            result['coupled_regulation'] = self.coupled_regulation.capture()
            # Detailed passive frames are exported by the runner, not necessary
            # protocol state. Keep this optional trace bounded rather than
            # duplicating it into the product's bounded metadata every view.
            self.coupled_regulation.state['frames'] = []
        return result

    def receipts(self):
        return super().receipts() + self.coupled_regulation.receipts()

    def save(self, path):
        self.coupled_regulation.state['quantity'] = deepcopy(self.coupled_regulation.quantity.state)
        self.coupled_regulation.state['frames'] = []
        self.state['coupled_regulation'] = deepcopy(self.coupled_regulation.state)
        return super().save(path)
