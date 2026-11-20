"""Published finite E1 curriculum, all opportunities declared at freshT0.

Order/contact common use and later opaque word; independent native comparison
transmitted A-to-B; material reference used for new quantities and then updated
additively. Same world, monotone ticks, no restoration to favorable physical state.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.complete_e1 import CompleteE1Session,prepare_complete

class LongitudinalE1Session(CompleteE1Session):
 @classmethod
 def create(cls,identifier='LONGITUDINAL_E1',**options):
  r,g=prepare_complete(**options);g['finite_protocol']='CPC8R.longitudinalE1.0_to549.v1';g['prepared_vs_acquired']='Geometry, comparator operations, readers, guards and opportunities are prepared. References and associations are actual later admitted encounters; no general learned comparison rule or learned scheduling policy is claimed.';r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
  return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,addition_mode='paired',addition_value=11,later_quantity_objects=(36,42,31,50),**options):
  if addition_mode not in('paired','unpaired','omitted')or len(later_quantity_objects)!=4:raise ValueError('Finite public addition/quantity protocol')
  super().curriculum(**options)
  if addition_mode!='omitted':
   self.quantity.input('quantity.reference.cue',0,268+int(addition_mode=='unpaired'));self.quantity.input('quantity.reference.resource',addition_value,268)
  for value,index,tick in zip(later_quantity_objects,(4,5,6,7),(337,404,471,538)):
   self.quantity.present_object(value,round_index=index);self.quantity.input('quantity.reader',7,tick,True)
  for q in self.geometry['joint_names'].values():
   self.input(q['query_port'],9,412,'probe','THIRD_OLD_WORD_QUERY_NO_RETEACHING')
   self.input(q['query_port'],11,546,'probe','FOURTH_OLD_WORD_QUERY_AFTER_ADDITIVE_NEW_EXPERIENCE')
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
  for t in sorted(x for x in(270,271,337,338,404,405,471,472,538,539)if self.tick<x<=tick):
   super().run_until(t);self.quantity.capture()
  super().run_until(tick);return self.view()
 def view(self):
  v=super().view();v['quantity']['reference_hub']=self.quantity.observe(self.geometry['quantity']['reference_hub']);return v
