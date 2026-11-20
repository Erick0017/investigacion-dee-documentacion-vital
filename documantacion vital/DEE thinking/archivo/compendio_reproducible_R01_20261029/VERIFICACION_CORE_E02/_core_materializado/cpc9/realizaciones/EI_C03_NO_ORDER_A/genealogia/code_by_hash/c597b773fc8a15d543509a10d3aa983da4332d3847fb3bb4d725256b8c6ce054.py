"""New T0 guard for the experimentally observed recurrent -Y reader product.

Repair1 of the return-Y candidate. The old unanswered reader produced -Y7,
then revisited the gradient from +Y67 ticks later and biased it. A prepared
zero support intercepts that route four steps away. Offpath has equal matter.
This is R0 regulation, not a learned attention policy.
"""
from consulta_referencia_y import prepare as previous_prepare,ReferenceQuerySession
from consulta_adquirida import move
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
def prepare(query_guard='onpath',**options):
    recipe,g=previous_prepare(**options)
    if query_guard not in('onpath','offpath'):raise ValueError('Matched guard control')
    site=move(g['center'],(0,-4,0)if query_guard=='onpath'else(6,-4,0))
    placement=d.InitialPlacement();placement.site=d.Coordinate(*site)
    placement.raw=d.pack_record(1,0,0,0,0,4);placement.clock=0
    placement.role='Prepared -Y query-reader return interceptor, not learned attention'
    recipe.placements=list(recipe.placements)+[placement]
    g.update(schema='CPC9.query.reference_Y.v3.r1',query_guard=query_guard,query_guard_site=site,
        repair1='Observed unknown-reader -Y7 return causes extra -Y gradient203. Fixed zero interceptor at distance4, equal-matter offpath control.')
    g['resources']['initial_material']=len(recipe.placements)
    recipe.options={'CPC9.query.preserved.geometry':encode_metadata(g)}
    return recipe,g
class GuardedReferenceQuerySession(ReferenceQuerySession):
    @classmethod
    def create(cls,**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g)
