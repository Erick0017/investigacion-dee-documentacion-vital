"""Declared repair1: route the zero turn away from the prepared corner guard.

No MAIN edits. A new T0 preparation changes the last zero-load direction to
XYZ. The B carrier then becomes XY at the native reference site136; both
acquired operand magnitudes remain available for the gradient, irrespective
of the moving reference's heading. This is a testable preparation, not a claim.
"""
from consulta_conservada import PreservedQuerySession,prepare as base_prepare
from consulta_adquirida import move
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata

def prepare(**options):
    recipe,g=base_prepare(**options)
    for port in recipe.interfaces:
        if port.name=='route.return_home':
            channel=port.channel
            target=g['signatures'][port.name]['target'];v=(1,1,1)
            channel.injection_site=d.Coordinate(*move(target,v,-3))
            channel.direction=d.Direction(*v);port.channel=channel
            g['signatures'][port.name].update(site=move(target,v,-3),direction=list(v))
    for turn in g['turns']:
        if turn['id']=='return_home':turn['direction']=[1,1,1]
    g.update(schema='CPC9.query.preserved.v2.r1',repair='Last +Y+Z turn reached a stationary reader support135. XYZ avoids it from newT0. Predict native XY reference16@136, gradient+X@204 and inhibited gate209/276/343/410.')
    recipe.options={'CPC9.query.preserved.geometry':encode_metadata(g)}
    return recipe,g

class PreservedQueryR1Session(PreservedQuerySession):
    @classmethod
    def create(cls,**options):
        recipe,g=prepare(**options)
        return cls(d.OrganizationalWorld.create(recipe),g)
