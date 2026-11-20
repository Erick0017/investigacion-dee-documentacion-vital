"""Fresh MCTS plus the unchanged F3 contact counter, not a snapshot union.

This candidate tests coexistence. It does not claim a semantic join of the count
with the previous relations. The selected app and MCTS preparations are intact.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession,prepare_magnitude_cts
from relaciones.contact_cardinality import prepare as prepare_count

def prepare_coexist(*,count_contacts=('A',),count_translation=(0,0,0),count_actor_state=1,count_medium_state=1,**options):
 recipe,g=prepare_magnitude_cts(**options)
 count_case={'contacts':list(count_contacts),'translation':list(count_translation),'actor_state':count_actor_state,'medium_state':count_medium_state,'regulation':'branch_onpath'}
 cr,cg=prepare_count(count_case);material=list(recipe.placements)+list(cr.placements);ports=list(recipe.interfaces)+list(cr.interfaces)
 sites=[(p.site.x,p.site.y,p.site.z)for p in material]
 if len(sites)!=len(set(sites)):raise ValueError('Fresh MCTS/COUNT initial overlap; no support overwritten')
 if len({p.name for p in ports})!=len(ports):raise ValueError('Fresh MCTS/COUNT duplicate port')
 recipe.placements=material;recipe.interfaces=ports;g['count_coexistence']={'geometry':cg,'preparation':count_case,'scope':'Same fresh Runtime, separate native counting apparatus; no count-to-MCTS semantic composition claimed. All six original count records exposed atT0, no trained-state insertion.'}
 g['resources']['initial_material_sites']=len(material);g['resources']['interfaces']=len(ports);g['finite_protocol']='CPC8R.magnitudeCTS_countF3.0_to616.v1';g['representation_version']+='+COUNT_F3_coexist'
 recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return recipe,g

class MCTSCountSession(MagnitudeCTSSession):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.state.setdefault('count_observations',[])
 @classmethod
 def create(cls,identifier='MCTS_COUNT_FRESH',**options):r,g=prepare_coexist(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
 def curriculum(self,**options):
  super().curriculum(**options)
  self.input('counter.cue',5,7,origin='FROZEN_F3_SAME_POST_CONTACT_CUE')
  for name in('A','B'):self.input('counter.free.guard.'+name,0,6,origin='FROZEN_F3_BRANCH_NORMALIZER_NO_POLICY')
  self.input('counter.query1',7,74,'probe','FROZEN_F3_FIRST_COUNT_QUERY');self.input('counter.query2',7,141,'probe','FROZEN_F3_SECOND_COUNT_QUERY')
  self.input('extra.cue',5,100,origin='COUNT_ADDITIONAL_CUE');self.input('extra.event',11,100,origin='COUNT_ADDITIONAL_EVENT');self.input('extra.query',9,167,'probe','COUNT_ADDITIONAL_QUERY')
 def capture_count(self):
  cg=self.geometry['count_coexistence']['geometry'];self.state['count_observations'].append({'tick':self.tick,'collector':self.observe(cg['collector']),'free_collector':self.observe(cg['free_collector']),'branches':{name:{'base':self.observe(b['base']),'join':self.observe(b['join'])}for name,b in cg['branches'].items()},'extra':self.observe(cg['extra'])})
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone shared world')
  for t in sorted(x for x in(4,5,9,10,76,77,99,100,103,143,144,170)if self.tick<x<=tick):super().run_until(t);self.capture_count()
  return super().run_until(tick)
 def view(self):
  v=super().view();cg=self.geometry['count_coexistence']['geometry'];v['count_current']={'collector':self.observe(cg['collector']),'free_collector':self.observe(cg['free_collector']),'extra':self.observe(cg['extra'])};return v
