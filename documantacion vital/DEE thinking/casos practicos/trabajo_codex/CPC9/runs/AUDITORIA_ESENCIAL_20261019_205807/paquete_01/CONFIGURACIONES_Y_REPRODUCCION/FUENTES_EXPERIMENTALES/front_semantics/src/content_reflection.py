"""Prepared active material operator on native comparisons of acquired operands.

This is a test of directional contrariety, NOT a claimed implementation of the
semantic primitive NO. Reflection is prepared and its participants are material
outputs, not host-decoded answers. Exact pre/post content is recorded.
"""
from dee_thinking import _native as d
from two_memory import TwoMemorySession,prepare as prepare_memory
from integracion.quantity_core import move

def prepare(*,reflectors='on_path',center=(30,30,30)):
    if reflectors not in ('on_path','off_path'):raise ValueError('Matched frozen reflector location only')
    recipe,g=prepare_memory(center=center);placements=list(recipe.placements);points=[]
    # V2 is a new T0 preparation. V1's nearby supports transformed earlier
    # teachers before the first comparison, invalidating its content premise.
    # Route only emitted products into distant operators; equal old guard
    # resources remain present offpath rather than being removed at runtime.
    for p in placements:
        q=[p.site.x,p.site.y,p.site.z]
        if q in (move(center,(-4,0,0)),move(center,(4,0,0))):
            p.site=d.Coordinate(*move(q,(0,10,0)));p.role='Historical product guard relocated offpath beforeT0 for remote reflection recipe'
    occupied={(p.site.x,p.site.y,p.site.z) for p in placements}
    def put(q,load,role):
        q=tuple(q)
        if q in occupied:raise ValueError('Reflection overlaps '+str(q))
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(1,load,0,0,0,4);p.clock=0;p.role=role;placements.append(p)
    for side in (-1,1):
        site=move(center,(side,0,0),9)
        for y in (-1,1):
            for z in (-1,1):put(move(site,(0,y,z)),0,'Prepared passive reflection support')
        for z in (-1,1):put(move(site,(side,0,z)),0,'Prepared passive reflection support')
        reflector=move(site,(side,0,0));actual=reflector if reflectors=='on_path' else move(reflector,(0,10,0))
        put(actual,21,'Prepared same-load gradient reflector '+reflectors)
        points.append({'side':side,'site':site,'reflector_onpath':reflector,'actual_reflector':actual})
    recipe.placements=placements;g.update(schema='CPC9.content_reflection.v2_remote',reflectors=reflectors,reflection_sites=points,
                                        initial_material=len(placements),attribution='Prepared contrariety operator on experience-acquired material content, not learned negation.')
    return recipe,g

class ContentReflectionSession(TwoMemorySession):
    @classmethod
    def create(cls,**kwargs):
        r,g=prepare(**kwargs);return cls(d.OrganizationalWorld.create(r),g)
    def capture(self):
        f=super().capture()
        f['reflection']=[{'side':p['side'],'material':self.observe(p['site']),
                          'Moore27':[self.observe(move(p['site'],(x,y,z))) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]}
                         for p in self.geometry['reflection_sites']]
        return f
