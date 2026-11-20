"""A second real contact episode, old knowledge retained in the same fresh life.

Only four neutral interfaces are added beforeT0. Actual actuator/opportunity/
medium packets later form or omit a contact by their routes; no contact bit is
injected. B's first query is deliberately deferred by3N, retaining real memory.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.complete_e1 import prepare_complete
from integracion.relational_pair import move

def prepare_contact_renewal(**options):
 r,g=prepare_complete(**options);ports=list(r.interfaces);join=g['contact_join'];base=g['contact_base'];signatures={}
 def port(name,site,v,state):
  c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p);signatures[name]={'site':site,'direction':list(v),'state':state,'semantic':1}
 actor=move(join,(1,0,0),-3);port('late.contact.actor.onpath',actor,(1,0,0),17);port('late.contact.actor.offpath',move(actor,(0,1,0),12),(1,0,0),17)
 port('late.contact.opportunity',move(join,(-1,0,1),-3),(-1,0,1),23);port('late.contact.medium',move(base,(1,1,-1),-4),(1,1,-1),31)
 for q in g['mode']['communication']['receivers']:q.update(query_tick=428,context_tick=433,delivery_tick=436)
 g['mode']['communication']['deferred_query']='First query delayed from227to428=160+4N, declaredbeforeT0. Same learned physical carrier, cue and receiver site; no re-teaching.'
 g['contact_renewal']={'schema':'CPC8R.contact_renewal.geometry.v1','signatures':signatures,'actual_packet_input_tick':336,'actuator_opportunity_encounter_tick':339,'new_medium_contact_tick':340,'teaching_contact_tick':344,'first_query_tick':411,'first_use_tick':417,'second_query_tick':478,'second_use_tick':484,'same_interfaces':'Original contact name/query/use/renew/reuse surfaces; no answer map or acquired memory cloned.','comparison_scope':'New actual packet states/dose and actuatorroute after prior function; acquired current consequence must be accessed twice without re-teaching while old composite word and quantity remain usable.'}
 r.interfaces=ports;g['resources']['interfaces']=len(ports);g['representation_version']='longitudinalE1+contactRenewal1+deferredB';g['finite_protocol']='CPC8R.contactRenewalE1.0_to549.v1';r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return r,g

class ContactRenewalE1Session(LongitudinalE1Session):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.state.setdefault('renewal_observations',[])
 @classmethod
 def create(cls,identifier='CONTACT_RENEWAL_E1',**options):
  r,g=prepare_contact_renewal(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,late_actor_mode='offpath',late_medium_load=9,late_contact_name='paired',**options):
  if late_actor_mode not in('onpath','offpath')or late_contact_name not in('paired','unpaired','omitted'):raise ValueError('Declared new actual contact episode')
  super().curriculum(**options);self.input('late.contact.actor.'+late_actor_mode,0,336,origin='NEW_CURRENT_ZERO_LOAD_ACTUATOR_ROUTE');self.input('late.contact.opportunity',0,336,origin='NEW_CURRENT_ZERO_LOAD_OPPORTUNITY');self.input('late.contact.medium',late_medium_load,336,origin='NEW_CURRENT_MEDIUM_PAYLOAD_NOT_CONTACT_BIT')
  for p in self.geometry['contact'].values():
   if late_contact_name!='omitted':self.input(p['name_port'],5,341+int(late_contact_name=='unpaired'),origin='POST_NEW_CONTACT_SAME_OPAQUE_CUE')
   self.input(p['query_port'],5,408,'probe','NEW_CONSEQUENCE_SAME_CONTACT_SIGNAL_QUERY');self.input(p['use_port'],7,414,'probe','NEW_CONTACT_FIRST_USE_RESOURCE');self.input(p['renew_port'],5,477,'probe','NEW_CONSEQUENCE_SECOND_RENEWED_QUERY');self.input(p['reuse_port'],7,481,'probe','NEW_CONTACT_SECOND_USE_RESOURCE')
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  targets=(338,339,340,343,344,410,411,416,417,427,428,432,433,435,436,477,478,483,484)
  for t in sorted(x for x in targets if self.tick<x<=tick):
   super().run_until(t)
   if t in(428,433,436):self.mode.capture(t)
   if t<=340:centers=[self.geometry['contact_join'],self.geometry['contact_base']]
   elif t in(343,344,410,411):centers=[p['hub']for p in self.geometry['contact'].values()]
   elif t in(416,417):centers=[p['effect_site']for p in self.geometry['contact'].values()]
   elif t in(477,478):centers=[p['renewed_site']for p in self.geometry['contact'].values()]
   elif t in(483,484):centers=[p['renewed_effect']for p in self.geometry['contact'].values()]
   else:centers=[r['memory_site'if t<=428 else'context_site']for r in self.geometry['mode']['communication']['receivers']]
   self.state['renewal_observations'].append({'tick':t,'view':self.view(),'windows':[{'center':q,'Moore27':[self.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]})
  super().run_until(tick);return self.view()
