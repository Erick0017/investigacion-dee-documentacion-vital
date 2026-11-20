"""Fresh E1 with acquired counterflow directions, finite sparse quantity use.

This is a distinct lifetime/profile, not an extension of a saved IUE individual.
Two zero-load interceptors are placed off route beforeT0. Six neutral interfaces
allow physically taught counterflows; the host never chooses them from output.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.complete_e1 import CompleteE1Session,prepare_complete
from regulacion_adquirida import prepare_regulation

class RegulatedFiniteE1Session(LongitudinalE1Session):
 @classmethod
 def create(cls,identifier='R1_FINITE_E1',**options):
  r,g=prepare_complete(quantity_guards='off_path',**options);rr,rg=prepare_regulation(center=(50,35,35))
  added=[p for p in rr.interfaces if p.name.startswith('regulator.')];r.interfaces=list(r.interfaces)+added
  if len({p.name for p in r.interfaces})!=len(r.interfaces):raise ValueError('Regulator interface collision')
  g['acquired_regulation']=rg['regulators'];g['resources']['interfaces']=len(r.interfaces);g['finite_protocol']='CPC8R.regulatedFiniteE1.0_to549.v2'
  g['scope']='Prepared geometry and finite sparse agenda. Regulator direction is taught by admitted physical contacts; no R2utilityselection. No comparison338/405/472: these absent exposures are explicitly part of this distinct profile.'
  r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
  return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,regulation='paired',directions=(-1,1),addition_value=11,late_object=36,maintenance='paired',maintenance_direction=-1,**options):
  if regulation not in('paired','unpaired','omitted')or len(directions)!=2 or any(x not in(-1,1)for x in directions):raise ValueError('Frozen finite regulation conditions')
  CompleteE1Session.curriculum(self,**options)
  if regulation!='omitted':
   for r,sign in zip(self.geometry['acquired_regulation'],directions):
    t=r['teaching_tick'];self.input(r['cue_port'],5,t+int(regulation=='unpaired'),origin='EXTERNAL_REGULATOR_CUE_DECLARED');self.input(r['event_ports'][str(sign)],11,t,origin='ACTUAL_DIRECTIONAL_EVENT_NOT_POLICY_RESULT')
  self.quantity.input('quantity.reference.cue',0,268);self.quantity.input('quantity.reference.resource',addition_value,268)
  # v1 (preserved) failed after a native reader product generated271 returned
  # into the reference337. Here FOUR EXTRA ACTUAL EXPERIENCES supply later
  # counterflows; this is external scheduled re-exposure, not autonomous R2.
  if maintenance not in('paired','unpaired','omitted')or maintenance_direction not in(-1,1):raise ValueError('Declared finite maintenance exposures')
  if maintenance!='omitted':
   r=self.geometry['acquired_regulation'][0]
   for t in(268,335,402,469):
    self.input(r['cue_port'],5,t+int(maintenance=='unpaired'),origin='EXTERNAL_MAINTENANCE_REEXPOSURE_COUNTED');self.input(r['event_ports'][str(maintenance_direction)],11,t,origin='ACTUAL_DIRECTION_EVENT_REEXPOSURE_NOT_NATIVE_POLICY')
  self.quantity.present_object(late_object,round_index=7);self.quantity.input('quantity.reader',7,538,True)
  for q in self.geometry['joint_names'].values():
   self.input(q['query_port'],9,412,'probe','THIRD_OLD_WORD_QUERY_NO_RETEACHING');self.input(q['query_port'],11,546,'probe','FOURTH_OLD_WORD_QUERY_NO_RETEACHING')
