"""Fresh oneRuntime: common-use order/contact, social MODE, and native quantity.

No part is loaded from a trained snapshot. Seven quantity supports and four
posterior-cue guards are designed resources, not learned policies. Each memory
reference is acquired from actual admitted experiences after creation.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.relational_guarded_v2 import GuardedV2Session,prepare_guarded_v2
from integracion.quantity_core import QuantitySession,prepare as prepare_quantity

def prepare_complete(*,guard_mode='onpath',quantity_guards='on_path',**options):
 r,g=prepare_guarded_v2(guard_mode=guard_mode,**options);qr,qg=prepare_quantity(center=(50,35,35),profile='transient',guards=quantity_guards)
 placements=list(r.placements)+list(qr.placements);sites=[(x.site.x,x.site.y,x.site.z)for x in placements]
 if len(sites)!=len(set(sites)):raise ValueError('CompleteE1 initial material overlap')
 interfaces=list(r.interfaces)+list(qr.interfaces)
 if len({x.name for x in interfaces})!=len(interfaces):raise ValueError('CompleteE1 duplicate interface')
 r.placements=placements;r.interfaces=interfaces;g['quantity']=qg;g['representation_version']='2+mode_social1+guard2+quantity_v3g4';g['resources']['initial_material_sites']=len(placements);g['resources']['interfaces']=len(interfaces)
 g['ensemble_scope']='One fresh N67 Runtime. Order/contact physically compose206; MODE acquired reference is applied to novel objects and communicated A-to-B; acquired quantity is used with three novel magnitudes. MODE and quantity are not claimed part of the order/contact join merely by sharing this world.'
 r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return r,g

class CompleteE1Session(GuardedV2Session):
 def __init__(self,w,g,state=None,identifier='COMPLETE_E1'):
  super().__init__(w,g,state,identifier);self.quantity=QuantitySession(w,self.geometry['quantity'],self.state.get('quantity'))
 @classmethod
 def create(cls,identifier='COMPLETE_E1',guard_mode='onpath',quantity_guards='on_path',**options):
  r,g=prepare_complete(guard_mode=guard_mode,quantity_guards=quantity_guards,**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,quantity_reference=31,quantity_condition='paired',quantity_objects=(16,45,31),**options):
  if len(quantity_objects)!=3:raise ValueError('Three actual quantity opportunities')
  super().curriculum(**options);self.quantity.experience_reference(quantity_reference,mode=quantity_condition);self.quantity.reader_opportunity()
  for i,value in enumerate(quantity_objects):self.quantity.present_object(value,round_index=i)
  self.quantity.acquire_other(110)
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  for t in sorted(x for x in(3,69,70,110,136,137,180,203,204)if self.tick<x<=tick):super().run_until(t);self.quantity.capture()
  super().run_until(tick);return self.view()
 def view(self):
  v=super().view();g=self.geometry['quantity'];v['quantity']={k:self.quantity.observe(g[k])for k in('center','reference_site','object_site')};return v
 def receipts(self):return super().receipts()+self.quantity.receipts()
 def save(self,path):self.state['quantity']=deepcopy(self.quantity.state);return super().save(path)
