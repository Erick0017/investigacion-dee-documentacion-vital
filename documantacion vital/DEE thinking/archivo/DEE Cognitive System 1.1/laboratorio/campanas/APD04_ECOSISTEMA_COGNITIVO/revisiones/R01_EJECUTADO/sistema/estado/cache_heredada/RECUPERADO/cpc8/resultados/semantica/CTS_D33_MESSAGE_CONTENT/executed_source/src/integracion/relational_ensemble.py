"""Fresh shared-world preparation: F2 order/contact plus acquired mode reference.

No learned state is copied. The comparison/normalization apparatus is prepared;
the reference and each current query object are actual admitted experiences.
"""
from copy import deepcopy
from dee_thinking import _native as d
from integracion.relational_pair_v2 import PairV2,prepare_v2
from relaciones.mode_reference import ModeReferenceSession,prepare_geometry

def prepare_ensemble(**options):
 r,g=prepare_v2(**options)
 mr,mg=prepare_geometry(dimension=67,origin=(44,42,48),cleanup=True,port_prefix='mode.')
 r.interfaces=list(r.interfaces)+list(mr.interfaces);r.organizations=list(r.organizations)+list(mr.organizations)
 if len({x.name for x in r.interfaces})!=len(r.interfaces):raise ValueError('Duplicate ensemble interface')
 g['mode']=mg;g['representation_version']='2+mode1';g['resources']['interfaces']=len(r.interfaces)
 g['ensemble_scope']='Fresh oneRuntime. Order/contact join uses F2 common physical consequence; acquired mode reference shares world and curriculum, not yet an input to that join. No three-way integrated inference claim.'
 return r,g

class EnsembleSession(PairV2):
 def __init__(self,w,g,state=None,identifier='ENSEMBLE'):
  super().__init__(w,g,state,identifier);self.mode=ModeReferenceSession(w,self.geometry['mode'],self.state.get('mode'))
 @classmethod
 def create(cls,identifier='ENSEMBLE',**options):
  r,g=prepare_ensemble(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,mode_reference=1,mode_condition='paired',mode_object1=1,mode_object2=-1,**options):
  super().curriculum(**options)
  self.mode.acquire_reference(mode_reference,mode_condition,11);self.mode.prepare_normalizers()
  self.mode.query_object(1,mode_object1,7);self.mode.query_object(2,mode_object2,13);self.mode.acquire_other(-1)
  for p in self.geometry['joint_names'].values():self.input(p['query_port'],7,345,'probe','LATER_REPEAT_JOINT_SIGNAL_WITHOUT_RETEACHING')
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  self.mode.run_until(tick);return self.view()
 def view(self):
  v=super().view();v['mode']={'reference':self.mode.observe(self.geometry['mode']['reference_hub']),'captures':deepcopy(self.mode.state['captures']),'other':self.mode.observe(self.geometry['mode']['other_hub'])};return v
 def receipts(self):return super().receipts()+self.mode.receipts()
 def save(self,path):self.state['mode']=deepcopy(self.mode.state);return super().save(path)
