"""Causal correction1: fixed native counterflow for identified residual readers.

No source memory or recipient is edited. Both zero-load counterflows are fixed
beforeT0, regardless of contact class. This is programmed regulation, not a
policy learned from utility or a data-dependent cleanup callback.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.relational_pair import move
from comunicacion.contact_social_e1 import prepare_contact_social_e1,ContactSocialE1Session

def prepare_regulated_contact_social(*,regulation='onpath',**options):
    if regulation not in('onpath','offpath','omitted'):raise ValueError('Frozen regulator modes')
    recipe,g=prepare_contact_social_e1(**options);ports=list(recipe.interfaces);items=[]
    for kind in('changed','free'):
        p=g['contact']['left.'+kind];target=move(p['renewed_site'],(1,0,0),500-478);programmed=move(target,(0,1,0),5 if regulation=='offpath'else 0);site=move(programmed,(-1,0,0),-3);name='contact_social.regulator.'+kind
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(-1,0,0);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True;spec=d.InterfaceSpec();spec.name=name;spec.channel=c;ports.append(spec)
        items.append({'id':kind,'port':name,'input_site':site,'requested_tick':497,'intercept_tick':500,'target_on_observed_old_flow':target,'programmed_intercept_site':programmed,'fixed_payload':0,'direction':[-1,0,0]})
    recipe.interfaces=ports;g['resources']['interfaces']=len(ports);g['contact_regulation']={'schema':'CPC8R.contact_social.fixed_counterflow.v1','mode':regulation,'items':items,'causal_diagnosis':'Unregulated reference packet is observed along its entire unperturbed route until544; at545 it encounters an older +X load5 stream occupying the next destination. Fixed intercept500 is22steps after original late-reader478 and45before the failure, not a response-dependent phase selection.','prepared_not_learned':True,'initial_material_added':0};g['finite_protocol']='CPC8R.contactSocialE1.counterflow1.0_to616.v1'
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return recipe,g
class RegulatedContactSocialE1Session(ContactSocialE1Session):
    def __init__(self,*args,**kw):super().__init__(*args,**kw);self.state.setdefault('contact_regulation_observations',[])
    @classmethod
    def create(cls,identifier='CONTACT_SOCIAL_REGULATED_E1',**options):
        r,g=prepare_regulated_contact_social(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
    def curriculum(self,**options):
        super().curriculum(**options)
        if self.geometry['contact_regulation']['mode']!='omitted':
            for p in self.geometry['contact_regulation']['items']:self.input(p['port'],0,p['requested_tick'],origin='FIXED_ZERO_LOAD_COUNTERFLOW_IDENTICAL_ACROSS_HISTORIES_NOT_LEARNED_ATTENTION')
    def run_until(self,tick):
        for t in sorted(x for x in(499,500)if self.tick<x<=tick):
            super().run_until(t)
            self.state['contact_regulation_observations'].append({'tick':t,'items':[{'id':p['id'],'old_flow_site':self.observe(p['target_on_observed_old_flow']),'programmed_site':self.observe(p['programmed_intercept_site']),'Moore27':[self.observe(move(p['programmed_intercept_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for p in self.geometry['contact_regulation']['items']]})
        return super().run_until(tick)
