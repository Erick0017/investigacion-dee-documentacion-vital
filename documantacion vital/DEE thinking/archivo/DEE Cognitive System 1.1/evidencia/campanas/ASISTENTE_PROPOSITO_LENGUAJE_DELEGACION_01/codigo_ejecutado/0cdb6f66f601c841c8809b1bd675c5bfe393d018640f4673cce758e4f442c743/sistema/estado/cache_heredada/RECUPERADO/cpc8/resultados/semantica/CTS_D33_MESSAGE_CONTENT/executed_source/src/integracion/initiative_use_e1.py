"""Fresh integrated E1 with physical use of a requested learned native answer."""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.initiative_e1 import InitiativeE1Session,prepare_initiative_e1
from integracion.relational_pair import move
from iniciativa_accion.return_use import prepare_return_use
def prepare_initiative_use_e1(**options):
 r,g=prepare_initiative_e1(**options);ports,rx=prepare_return_use(g['initiative']);r.interfaces=list(r.interfaces)+ports
 if len({p.name for p in r.interfaces})!=len(r.interfaces):raise ValueError('Return-use interface collision')
 g['initiative']['return_use']=rx;g['resources']['interfaces']=len(r.interfaces);g['representation_version']='contactRenewalE1+quantityTap1+returnUse1';g['finite_protocol']='CPC8R.initiativeUseE1.0_to549.v1';r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return r,g
class InitiativeUseE1Session(InitiativeE1Session):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.state.setdefault('return_use_observations',[])
 @classmethod
 def create(cls,identifier='INITIATIVE_USE_E1',**options):
  r,g=prepare_initiative_use_e1(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,**options):
  super().curriculum(**options)
  for rx in self.geometry['initiative']['return_use']['items']:self.initiative.submit(rx['port'],rx['load'],rx['requested_tick'],'FIXED_ALL_CANDIDATE_RETURN_USE_RESOURCE_NO_READ_ACT_CALLBACK')
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  for t in sorted(x for x in(87,88,89,90,91)if self.tick<x<=tick):
   super().run_until(t);self.state['return_use_observations'].append({'tick':t,'receivers':[{'source_candidate':rx['source_value_candidate'],'contact':self.observe(rx['meeting_site']),'emission':self.observe(rx['emission_site']),'contact_Moore27':[self.observe(move(rx['meeting_site'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for rx in self.geometry['initiative']['return_use']['items']]})
  super().run_until(tick);return self.view()
 def view(self):
  v=super().view();v['return_use']=[{'source_candidate':rx['source_value_candidate'],'contact':self.observe(rx['meeting_site']),'emission':self.observe(rx['emission_site'])}for rx in self.geometry['initiative']['return_use']['items']];return v
