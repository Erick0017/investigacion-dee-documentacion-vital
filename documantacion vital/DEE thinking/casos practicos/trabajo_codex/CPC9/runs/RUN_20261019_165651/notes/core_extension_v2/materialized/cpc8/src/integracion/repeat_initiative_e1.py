"""A second fixed request-answer-use opportunity in the same fresh E1 life.

No new geometry, interfaces or initial matter. All second-cycle inputs are
queued before evolution, independently of the first/second physical outputs.
The quantitative addition and the new provider experience are external
experiences, not a host-computed relation or a feedback correction.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.initiative_use_e1 import InitiativeUseE1Session,prepare_initiative_use_e1
from integracion.relational_pair import move

def prepare_repeat_initiative_e1(**options):
 r,g=prepare_initiative_use_e1(**options)
 g['repeat_initiative']={'schema':'CPC8R.repeat_initiative.protocol.v1','period_offset':268,
  'source_experience':268,'comparison':338,'request':340,'source':345,'effect':349,'return':354,'use':357,
  'interfaces_added':0,'initial_matter_added':0,
  'scope':'Second predeclared opportunity after new quantity/provider experiences. No learned scheduling policy or indefinite reuse claim.'}
 g['finite_protocol']='CPC8R.repeatInitiativeE1.0_to549.v1'
 r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
 return r,g

class RepeatInitiativeE1Session(InitiativeUseE1Session):
 @classmethod
 def create(cls,identifier='REPEAT_INITIATIVE_E1',**options):
  r,g=prepare_repeat_initiative_e1(**options)
  return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,*,repeat_source=-1,repeat_source_condition='paired',**options):
  if repeat_source not in(-1,1)or repeat_source_condition not in('paired','unpaired','virgin'):
   raise ValueError('Declared current provider-experience domain')
  super().curriculum(**options)
  g=self.geometry['initiative'];offset=self.geometry['repeat_initiative']['period_offset']
  for branch in g['branches']:
   if repeat_source_condition!='virgin':
    source=branch['sources'][str(repeat_source)]
    self.initiative.submit(source['cue_port'],5,offset+int(repeat_source_condition=='unpaired'),'SECOND_PROVIDER_ARBITRARY_CUE')
    self.initiative.submit(source['event_port'],11,offset,'SECOND_ACTUAL_PROVIDER_OBSERVATION_NOT_TARGET')
   self.initiative.submit(branch['request_port'],0,g['ticks']['request']-3+offset,'SECOND_FIXED_NEUTRAL_QUESTION_OPPORTUNITY')
   for effect in branch['effects'].values():
    self.initiative.submit(effect['opportunity_port'],7,g['ticks']['effect']-3+offset,'SECOND_FIXED_ALL_CANDIDATE_EFFECT_RESOURCE')
  for rx in g['return_use']['items']:
   self.initiative.submit(rx['port'],rx['load'],rx['requested_tick']+offset,'SECOND_FIXED_ALL_CANDIDATE_RETURN_USE_RESOURCE')
 # Detailed observations belong to the external auditor, not snapshot metadata.
 # The operational state retains requests/physical queues through the parent.
 def repeat_view(self,moore=False):
  rows=[]
  for b in self.geometry['initiative']['branches']:
   row={'question':self.observe(b['request_site']),'question_in_flight':self.observe(b['request_probe_site']),
    'source':self.observe(b['source_site']),'effects':{p:self.observe(e['site'])for p,e in b['effects'].items()},
    'return':{p:self.observe(e['return_site'])for p,e in b['effects'].items()}}
   if moore:
    centers=[b['request_site'],b['source_site']]+[e['return_site']for e in b['effects'].values()]
    row['Moore_windows']=[{'center':q,'Moore27':[self.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]
   rows.append(row)
  return{'tick':self.tick,'branches':rows,'return_use':super().view()['return_use']}
 def view(self):
  v=super().view();v['repeat_initiative']=self.repeat_view();return v
