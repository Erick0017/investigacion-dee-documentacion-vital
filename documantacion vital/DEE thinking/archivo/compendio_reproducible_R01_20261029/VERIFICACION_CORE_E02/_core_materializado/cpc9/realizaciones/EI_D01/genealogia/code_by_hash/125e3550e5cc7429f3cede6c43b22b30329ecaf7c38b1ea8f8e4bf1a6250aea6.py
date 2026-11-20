"""Final bounded repair: fixed native counterflow arrests -Y reader products.

The R1 stationary support did not intercept the recurrent carrier. All six
zero +Y opportunities now meet a possible -Y reader two sites away; if they
meet, reducer makes a stationary7 record. Offpath preserves the dose/schedule.
This explicitly supplied R0 maintenance is not an acquired regulation policy.
"""
from consulta_referencia_y_r1 import prepare as previous_prepare,GuardedReferenceQuerySession
from consulta_adquirida import move
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
def prepare(counterflow='onpath',**options):
    recipe,g=previous_prepare(**options)
    if counterflow not in('onpath','offpath'):raise ValueError('Matched counterflow')
    target=move(g['center'],(0,-2,0)if counterflow=='onpath'else(6,-2,0))
    vector=(0,1,0);site=move(target,vector,-3)
    channel=d.ChannelSpec();channel.name='reader.counterflow';channel.injection_site=d.Coordinate(*site)
    channel.direction=d.Direction(*vector);channel.state=1;channel.semantic=1
    channel.allow_probe=True;channel.allow_experience=True
    port=d.InterfaceSpec();port.name=channel.name;port.channel=channel
    recipe.interfaces=list(recipe.interfaces)+[port]
    g.update(schema='CPC9.query.reference_Y.v3.r2',counterflow=counterflow,counterflow_target=target,
        repair2='Fixed +Y zero meets possible -Y7 reader at distance2. Same zero dose and schedule offpath. Last repair of candidate.')
    g['resources']['interfaces']=len(recipe.interfaces)
    recipe.options={'CPC9.query.preserved.geometry':encode_metadata(g)}
    return recipe,g
class CounterflowReferenceQuerySession(GuardedReferenceQuerySession):
    @classmethod
    def create(cls,**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g)
    def curriculum(self,*args,**options):
        super().curriculum(*args,**options);delay=self.geometry['delay']
        for tick in self.geometry['local_query_ticks']:self.input('reader.counterflow',0,tick-1+delay)
