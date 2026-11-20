"""New recipe: native comparison of two separately acquired circulating operands.

The comparator operation and three opportunities are prepared. Neither operand
is present in initial material or injected as a solved relation. Moving the
old current-object absorber is a new T0 recipe, not a runtime repair.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.quantity_core import QuantitySession, prepare as prepare_quantity, move


def prepare(center=(30,30,30), absorber='off_path'):
    if absorber not in ('off_path', 'on_path'):
        raise ValueError('Only matched on/off original absorber placement')
    recipe, g = prepare_quantity(center=center, profile='transient', guards='on_path')
    placements = list(recipe.placements)
    original = move(g['center'], (1,10,0))
    relocated = move(g['center'], (10,10,10))
    matched = []
    for p in placements:
        q = [p.site.x, p.site.y, p.site.z]
        if q == original:
            p.site = d.Coordinate(*(relocated if absorber == 'off_path' else original))
            p.role = 'Same zero-load material off current-operand path; newT0 recipe for persistent second operand'
            matched.append(q)
    if len(matched) != 1:
        raise ValueError('Historical absorber identity not found uniquely')
    recipe.placements = placements
    g.update(schema='CPC9.two_memory.comparison.recipe.v2', absorber=absorber,
             absorber_original=original, absorber_relocated=relocated,
             prepared='Same transient native comparator and Xguards4; object absorber moved offpath beforeT0 so both acquired operands can circulate. Operation not learned.',
             acquired='R andO material quantities separately paired with formatcue5 afterT0; no targetrelation in initialstate. Three later readers receive no new quantity or correct output.',
             finite_domain='FreshN67, Oexperience0/Rexperience2, fixedreaders71/138/205; auxiliary recipe, not integratedE1 until revalidated.')
    recipe.options = {'CPC9.two_memory.geometry.v1': encode_metadata(g)}
    return recipe, g


class TwoMemorySession(QuantitySession):
    @classmethod
    def create(cls, **kwargs):
        recipe, g = prepare(**kwargs)
        return cls(d.OrganizationalWorld.create(recipe), g)

    def curriculum(self, reference, remembered_object, omit=None, unpaired=False, order='O_first'):
        if self.tick != 0:
            raise ValueError('Fresh fixed two-experience curriculum')
        if order not in ('O_first', 'R_first'):
            raise ValueError('Two exact prevalidated schedules only')
        rt, ot, readers = (2, 0, (71,138,205)) if order == 'O_first' else (0, 65, (69,136,203))
        self.geometry['protocol'] = {'R_experience':rt, 'O_experience':ot, 'readers':list(readers), 'outputs':[t+1 for t in readers], 'order':order}
        if omit != 'O':
            self.input('quantity.object.cue', 5, ot + int(unpaired))
            self.input('quantity.object.resource', remembered_object, ot)
        if omit != 'R':
            self.input('quantity.reference.cue', 5, rt + int(unpaired))
            self.input('quantity.reference.resource', reference, rt)
        for tick in readers:
            self.input('quantity.reader', 7, tick, True)
        self.acquire_other(110)
