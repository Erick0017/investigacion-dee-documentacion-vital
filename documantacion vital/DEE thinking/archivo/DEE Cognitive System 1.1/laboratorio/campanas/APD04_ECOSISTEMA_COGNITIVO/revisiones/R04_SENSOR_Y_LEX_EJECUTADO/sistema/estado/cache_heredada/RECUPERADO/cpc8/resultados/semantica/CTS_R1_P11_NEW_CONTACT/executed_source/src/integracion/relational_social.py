"""Fresh one-world order/contact common use plus native MODE A-to-B communication."""
from copy import deepcopy
from integracion.relational_pair_v2 import prepare_v2
from integracion.relational_ensemble import EnsembleSession
from integracion.relational_pair import move
from comunicacion.mode_communication import prepare_social_geometry,ModeCommunicationSession

def prepare_social_ensemble(**options):
 r,g=prepare_v2(**options)
 mr,mg=prepare_social_geometry(dimension=67,origin=(44,42,48),port_prefix='mode.')
 r.interfaces=list(r.interfaces)+list(mr.interfaces);r.organizations=list(r.organizations)+list(mr.organizations)
 if len({x.name for x in r.interfaces})!=len(r.interfaces):raise ValueError('Duplicate social ensemble interface')
 g['mode']=mg;g['representation_version']='2+mode_social1';g['resources']['interfaces']=len(r.interfaces)
 g['ensemble_scope']='Fresh oneRuntime. Order/contact physically join206. Acquired MODE reference is compared against new objects in the same history; its second native product teaches B and B uses a later actual context. No host transport, and no three-way join claim.'
 return r,g

class SocialEnsembleSession(EnsembleSession):
 def __init__(self,w,g,state=None,identifier='SOCIAL_ENSEMBLE'):
  super().__init__(w,g,state,identifier);self.mode=ModeCommunicationSession(w,self.geometry['mode'],self.state.get('mode'));self.state.setdefault('social_windows',[])
 def curriculum(self,*,social_name='paired',social_query=True,social_context=1,**options):
  super().curriculum(**options);self.mode.teach_form(social_name);self.mode.query_receiver(enabled=social_query);self.mode.present_context(social_context)
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  for t in sorted(x for x in(159,160,226,227,231,232,234,235)if self.tick<x<=tick):
   self.mode.run_until(t)
   for r in self.geometry['mode']['communication']['receivers']:
    site=r['memory_site']if t<=227 else r['context_site']
    self.state['social_windows'].append({'tick':t,'receiver':r['id'],'center':site,'Moore27':[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  self.mode.run_until(tick);return self.view()
 def view(self):
  v=super().view();v['mode']['social_captures']=deepcopy(self.mode.state.get('social_captures',[]));return v
