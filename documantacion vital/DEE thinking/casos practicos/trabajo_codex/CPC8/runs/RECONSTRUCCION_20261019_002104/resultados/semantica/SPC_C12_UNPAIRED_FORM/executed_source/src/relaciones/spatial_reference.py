"""Actual local position -> native gradient -> acquired reusable spatial reference.

No query supplies b or a match bit as a beam direction. All query objects have
the same Z- velocity and differ in actual occupied neighbor position. A fixed
array of equal sensor opportunities transports the native gradient products.
Reference and current objects use different planes/states and positions.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
from dee_thinking.consolidated import exact_observation,exact_receipt
from relaciones.mode_reference import prepare_geometry as prepare_mode,ModeReferenceSession,move,physical
from relaciones.spatial_gradient import sensor
KEY='CPC8R.spatial_reference.session.v1'
def prepare_spatial_geometry(reference_state=17,object_states=(99,171),origin=(20,20,20),port_prefix=''):
 n=67;r=list(origin);initial=sensor(r,[[-1,-1,0],[1,1,0]]);interfaces=[];mode_geometry={};references={};sensors=[]
 def port(name,q,v,state=1):
  name=port_prefix+name
  c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
  p=d.InterfaceSpec();p.name=name;p.channel=c;interfaces.append(p);return name
 for a,label in((-1,'minus'),(1,'plus')):
  h=move(r,(a,a,1),10);recipe,mg=prepare_mode(origin=h,cleanup=True,port_prefix=port_prefix+'space.'+label+'.',first_query_tick=78);interfaces+=list(recipe.interfaces);mode_geometry[label]=mg
  record=port('space.record.'+label,move(h,(0,0,-1),-1),(0,0,-1))
  refobject=port('space.reference.object.'+label,move(r,(-a,-a,0)),(0,0,-1),reference_state)
  references[label]={'axis':a,'hub':h,'record_port':record,'object_port':refobject,'actual_object_offset':[-a,-a,0],'capture_tick':11}
  for q in mg['queries']:
   for candidate_b in(-1,1):
    center=move(q['parent']['hub'],(0,candidate_b,1),-10);key=label+'.stage'+str(q['stage'])+'.'+q['parent']['id']+'.b'+str(candidate_b)
    initial+=sensor(center,[[0,-1,-1],[0,1,-1]])
    ports={}
    for actual_b in(-1,1):ports[str(actual_b)]=port('space.object.'+key+'.'+str(actual_b),move(center,(0,-actual_b,-1)),(0,0,-1),object_states[q['stage']-1])
    sensors.append({'id':key,'reference_candidate':label,'stage':q['stage'],'route_candidate_b':candidate_b,'center':center,'query_tick':q['parent']['query_tick'],'object_input_tick':q['parent']['query_tick']-11,'ports':ports,'expected_gradient_scope':'Actual position Y sign measured natively; no target bit supplied.'})
 seen={}
 for p in initial:
  q=(p.site.x,p.site.y,p.site.z);key=(int(p.raw),int(p.clock))
  if q in seen and seen[q]!=key:raise ValueError('Conflicting initial native sensor supports at '+str(q))
  seen[q]=key
 unique=[];done=set()
 for p in initial:
  q=(p.site.x,p.site.y,p.site.z)
  if q not in done:unique.append(p);done.add(q)
 g={'schema':'CPC8R.spatial_reference.geometry.v1','N':67,'reference_sensor':r,'references':references,'modes':mode_geometry,'sensors':sensors,'resources':{'initial_material':len(unique),'interfaces':len(interfaces),'sensor_count':1+len(sensors),'query_object_copies_per_stage':{str(k):sum(s['stage']==k for s in sensors)for k in(1,2)}},'prepared':'Six-axis passive supports with fixed Z-gradient bias, physical sensing opportunities, transport array, comparison and normalization. No spatial semantic classification is calculated in Python.','acquired':'Reference X/Y comes from first actual object position, transformed by native gradient. New object positions create native gradients transported to reference; no answer label or corrective feedback.','scope':'Same/opposite Y-side relative to a physically acquired directional reference in a fixed sensor frame. Not persistent referent identity, human-space universality or a learned universal comparator.'}
 recipe=d.OrganizationRecipe.research(n,unique,0);recipe.interfaces=interfaces;recipe.execution=d.TickOptions(d.Backend.LAZY,1);recipe.options={'CPC8R.spatial_reference.geometry':encode_metadata(g)}
 org=d.OrganizationSpec();org.id='SPATIAL_REFERENCE';org.recipe_id='CPC8R.spatial_reference.v1';org.ports={'reference_sensor':d.Coordinate(*r)};recipe.organizations=[org];return recipe,g
class SpatialReferenceSession:
 def __init__(self,w,g,state=None):
  self.world=w;self.geometry=deepcopy(g);self.state=deepcopy(state)if state else{'requests':[],'modes':{}}
  self.modes={key:ModeReferenceSession(w,mg,self.state['modes'].get(key))for key,mg in g['modes'].items()}
 @classmethod
 def create(cls,**options):r,g=prepare_spatial_geometry(**options);return cls(d.OrganizationalWorld.create(r),g)
 @property
 def tick(self):return int(self.world.runtime.current_tick)
 def input(self,port,payload,tick,origin):
  x=self.world.submit(port,payload,tick);self.state['requests'].append({'id':int(x.id),'port':port,'payload':payload,'tick':tick,'origin':origin,'kind':'submit'});return exact_receipt(x)
 def curriculum(self,a,b1,b2,reference='paired',loads=(11,11,19),current_stages=(1,2),normalization_stages=(1,2)):
  if a not in(-1,1)or b1 not in(-1,1)or b2 not in(-1,1)or reference not in('paired','unpaired','virgin','record_omitted'):raise ValueError('Frozen spatial family')
  if reference!='virgin':self.input(self.geometry['references']['plus'if a>0 else'minus']['object_port'],loads[0],0,'ACTUAL_REFERENCE_OBJECT_AT_PHYSICAL_POSITION_NOT_DIRECTION_LABEL')
  if reference!='record_omitted':
   for ref in self.geometry['references'].values():self.input(ref['record_port'],0,10+(5 if reference=='unpaired'else 0),'FIXED_RECORDING_INTERACTION')
  for m in self.modes.values():m.prepare_normalizers(stages=normalization_stages);m.acquire_other(1)
  for s in self.geometry['sensors']:
   if s['stage'] in current_stages:
    b=b1 if s['stage']==1 else b2;self.input(s['ports'][str(b)],loads[s['stage']],s['object_input_tick'],'ACTUAL_CURRENT_OBJECT_POSITION_BROADCAST_TO_FIXED_SENSOR_ARRAY_NOT_CLASSIFICATION')
 def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
 def critical_ticks(self):
  critical=set()
  for m in self.modes.values():
   critical.update(q['parent']['query_tick']for q in m.geometry['queries']);critical.update(b[k]for b in m.geometry['branches']for k in('first_tick','second_tick'))
  return sorted(critical)
 def capture(self,tick):
  for m in self.modes.values():m.capture(tick)
 def run_until(self,tick):
  for t in sorted(x for x in self.critical_ticks() if self.tick<x<=tick):
   self.world.run_until(t)
   self.capture(t)
  self.world.run_until(tick)
 def receipts(self):
  out=[{**x,'receipt':exact_receipt(self.world.runtime.receipt(x['id']))}for x in self.state['requests']]
  for m in self.modes.values():out+=m.receipts()
  return out
 def save(self,path):
  self.state['modes']={key:deepcopy(m.state)for key,m in self.modes.items()}
  self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
 @classmethod
 def load(cls,path):
  w,_=load_world_snapshot(path,max_bytes=1024**3);meta=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY]);assert meta['tick']==int(w.runtime.current_tick)and meta['channels']==sorted(w.runtime.channel_names);return cls(w,meta['geometry'],meta['state'])
