"""Fresh E1 plus conditional native quantity question and learned-source return.

Only inert interfaces are added beforeT0. A positive native comparator product
may physically meet a neutral turn opportunity; no Python observation chooses
whether to ask or copies a source response into another participant.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.contact_renewal_e1 import ContactRenewalE1Session,prepare_contact_renewal
from integracion.relational_pair import move
from iniciativa_accion.solicitud import prepare_gradient_tap,InitiativeSession
def prepare_initiative_e1(**options):
 r,g=prepare_contact_renewal(**options);ports,ig=prepare_gradient_tap(question_site=(52,35,35),question_tick=72,question_direction=(0,1,1),prefix='initiative.quantity.')
 r.interfaces=list(r.interfaces)+ports
 if len({p.name for p in r.interfaces})!=len(r.interfaces):raise ValueError('InitiativeE1 duplicate interface')
 g['initiative']=ig;g['resources']['interfaces']=len(r.interfaces);g['representation_version']='contactRenewalE1+quantityTap1';g['finite_protocol']='CPC8R.initiativeE1.0_to549.v1';g['initiative_scope']='A fixed conditional tap on a native +X quantity comparison; separately acquired source content returns through native interactions. Not a general learned question policy.';r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return r,g
class InitiativeE1Session(ContactRenewalE1Session):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.initiative=InitiativeSession(self.world,self.geometry['initiative'],self.state.get('initiative'));self.state.setdefault('initiative_windows',[])
 @classmethod
 def create(cls,identifier='INITIATIVE_E1',**options):
  r,g=prepare_initiative_e1(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,initiative_source=1,initiative_condition='paired',initiative_request=True,initiative_effect=True,**options):
  super().curriculum(**options);self.initiative.acquire_source(initiative_source,initiative_condition);self.initiative.opportunities(request=initiative_request,effect=initiative_effect)
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  for t in sorted(x for x in(3,69,70,71,72,73,76,77,80,81,85,86)if self.tick<x<=tick):
   super().run_until(t);self.initiative.capture();centers=[]
   for b in self.geometry['initiative']['branches']:
    if t==3:centers.extend(s['hub']for s in b['sources'].values())
    elif t<=73:centers.extend((b['request_site'],b['request_probe_site']))
    elif t<=77:centers.append(b['source_site'])
    elif t<=81:centers.extend(e['site']for e in b['effects'].values())
    else:centers.extend(e['return_site']for e in b['effects'].values())
   self.state['initiative_windows'].append({'tick':t,'windows':[{'center':q,'Moore27':[self.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]})
  super().run_until(tick);return self.view()
 def view(self):
  v=super().view();v['initiative']=[{'question':self.initiative.observe(b['request_site']),'question_in_flight':self.initiative.observe(b['request_probe_site']),'source':self.initiative.observe(b['source_site']),'return':{p:self.initiative.observe(e['return_site'])for p,e in b['effects'].items()}}for b in self.geometry['initiative']['branches']];return v
 def receipts(self):return super().receipts()+self.initiative.receipts()
 def save(self,path):self.state['initiative']=deepcopy(self.initiative.state);return super().save(path)
