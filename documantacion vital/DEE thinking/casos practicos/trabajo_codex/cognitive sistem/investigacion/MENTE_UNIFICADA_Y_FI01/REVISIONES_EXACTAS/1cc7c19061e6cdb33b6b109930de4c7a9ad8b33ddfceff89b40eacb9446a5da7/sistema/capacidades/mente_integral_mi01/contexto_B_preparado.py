"""Explicit P0 B comparator context, not learned content or host policy.

The former contextual43 contribution was consumed before a second question.
This candidate installs an invariant43 scalar frame at that hub, plus equal
zero-load matter opportunities for EVERY possible B query. Private raw data
are never inspected to decide a route/sign. Inputs retain normal admission.
"""
from capacidades.integracion_situada_01 import ic_native_core as n
from . import saved,put
from .preparacion_compartida import prepare as base_prepare

def prepare(a,*,b_context='fixed43',**options):
    if b_context not in('fixed43','zero','sham43'):raise ValueError('Declared P0 reference contrast')
    result=base_prepare(a,**options);cfg=saved(a);body=cfg['native_habitats'][options['name']];B=list(a.transferred_quantity.geometry['center']);site=n.move(B,(-1,1,0));requests=[]
    if b_context=='sham43':site=n.move(site,(0,0,1),19)
    before=n.obs(a,site);requests.append(n.submit(a,'MI01.B_context.'+options['name']+'.fixed_frame',site,(0,0,0),a.tick,0 if b_context=='zero'else 43,4))
    names={z['query_name']for z in body['plans']}
    names.update(z['query_name']for z in body.get('direct_failure',{}).get('opportunities',[]))
    for i,name in enumerate(sorted(names)):
        qp=cfg['material_queries'][name];T=qp['comparison_arrival'];requests.append(n.arrive(a,'MI01.B_context.'+options['name']+'.matter_opportunity.'+str(i),n.move(B,(0,-1,0)),(0,0,1),T,0))
    body['prepared_B_context']={'mode':b_context,'frame_site':site,'pre':before,'requests':requests,'threshold':0 if b_context=='zero'else 43,'attribution':'Fixed scalar comparison frame and zero-load survival opportunity, external P0 preparation; NOT a B learned reference, no correct sign is provided. All private B samples and both response paths remain unchanged.'}
    put(a,cfg);result['prepared_B_context']=body['prepared_B_context'];return result
