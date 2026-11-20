"""New recipe: native comparison of two separately acquired circulating operands.

The comparator operation and three opportunities are prepared. Neither operand
is present in initial material or injected as a solved relation. Moving the
old current-object absorber is a new T0 recipe, not a runtime repair.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.quantity_core import QuantitySession, prepare as prepare_quantity, move


def prepare():
    recipe, g = prepare_quantity(center=(30,30,30), profile='transient', guards='on_path')
    placements = list(recipe.placements)
    original = move(g['center'], (1,10,0))
    relocated = move(g['center'], (10,10,10))
    matched = []
    for p in placements:
        q = [p.site.x, p.site.y, p.site.z]
        if q == original:
            p.site = d.Coordinate(*relocated)
            p.role = 'Same zero-load material off current-operand path; newT0 recipe for persistent second operand'
            matched.append(q)
    if len(matched) != 1:
        raise ValueError('Historical absorber identity not found uniquely')
    recipe.placements = placements
    g.update(schema='CPC9.two_memory.comparison.recipe.v1',
             absorber_original=original, absorber_relocated=relocated,
             prepared='Same transient native comparator and Xguards4; object absorber moved offpath beforeT0 so both acquired operands can circulate. Operation not learned.',
             acquired='R andO material quantities separately paired with formatcue5 afterT0; no targetrelation in initialstate. Three later readers receive no new quantity or correct output.',
             finite_domain='FreshN67, Oexperience0/Rexperience2, fixedreaders71/138/205; auxiliary recipe, not integratedE1 until revalidated.')
    recipe.options = {'CPC9.two_memory.geometry.v1': encode_metadata(g)}
    return recipe, g


class TwoMemorySession(QuantitySession):
    @classmethod
    def create(cls):
        recipe, g = prepare()
        return cls(d.OrganizationalWorld.create(recipe), g)

    def curriculum(self, reference, remembered_object, omit=None, unpaired=False):
        if self.tick != 0:
            raise ValueError('Fresh fixed two-experience curriculum')
        if omit != 'O':
            self.input('quantity.object.cue', 5, int(unpaired))
            self.input('quantity.object.resource', remembered_object, 0)
        if omit != 'R':
            self.input('quantity.reference.cue', 5, 2 + int(unpaired))
            self.input('quantity.reference.resource', reference, 2)
        for tick in (71,138,205):
            self.input('quantity.reader', 7, tick, True)
        self.acquire_other(110)
