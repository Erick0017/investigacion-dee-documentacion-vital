"""A finite native recurrent comparison with an acquired material reference.

The v27 gradient is a prepared operation, not an algorithm learned here. The
reference is acquired through post-T0 cue/resource contact; new quantities are
actual inputs, never already compared labels. All target scoring is external.
"""
from copy import deepcopy
import hashlib
from array import array
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC8R.quantity.transient.v3g'
def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def prepare(center=(30,30,30),profile='transient',guards='on_path'):
 c=list(center);ref=move(c,(-1,1,0));obj=move(c,(1,-3,0));initial=[];interfaces=[]
 def put(q,load,role):
  p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(1,load,0,0,0,4);p.clock=0;p.role=role;initial.append(p)
 for x in(-1,1):
  for y,z in(((-1,-1),(1,1))if profile=='transient'else((-1,-1),(-1,1),(1,1))):put(move(c,(x,y,z)),0,'Prepared zero-load native reader support')
 if profile!='transient':put(move(c,(0,0,-1)),1,'Prepared permanent gradient Z bias; absorbs circulating reader products')
 put(move(c,(1,10,0)),0,'Prepared current-object downstream absorber; not learned attention')
 if guards not in('on_path','off_path'):raise ValueError('Guard control must preserve resources')
 for side in(-1,1):put(move(c,(4*side,0 if guards=='on_path'else 5,0)),0,'Prepared reader-product interceptor four steps away; previous distance2 perturbed operand neighborhood, preserved as Q5')
 def port(name,q,v):
  ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*q);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=True
  p=d.InterfaceSpec();p.name=name;p.channel=ch;interfaces.append(p)
 for prefix,q in(('quantity.reference',ref),('quantity.object',obj)):
  lead=1 if prefix=='quantity.object'else 3
  port(prefix+'.cue',move(q,(-1,0,0),-lead),(-1,0,0));port(prefix+'.resource',move(q,(1,1,0),-lead),(1,1,0))
 port('quantity.reader',c,(0,0,1))
 aux=move(c,(21,-15,-22));port('quantity.other.cue',move(aux,(-1,0,0),-3),(-1,0,0));port('quantity.other.event',move(aux,(1,1,0),-3),(1,1,0))
 r=d.OrganizationRecipe.research(67,initial,0);r.interfaces=interfaces;r.execution=d.TickOptions(d.Backend.LAZY,1)
 g={'schema':'CPC8R.quantity.transient.geometry.v3g','profile':profile,'guards':guards,'object_input_lead':1,'repair':'F1 object path crossed reference; F2 permanent reader traffic later occupied data routes. F3 uses four supports: reader survives only during two material operands, then dies natively. F3g intercepts its first X-directed product before its toroidal return into the reference after67ticks; same-count off-path control. Identical three reader opportunities are externally declared; no autonomous access selection. Earlier states/results preserved.','N':67,'center':c,'reference_hub':ref,'object_hub':obj,'auxiliary_hub':aux,
  'reference_site':move(c,(-1,0,0)),'object_site':move(c,(1,0,0)),'initial_material':len(initial),'interfaces':len(interfaces),
  'prepared':'Four supports and object absorber in transient profile; three externally supplied identical readers. No magnitude or answer in initial material.',
  'learned':'Reference carrier from actual prior quantity plus fixed format cue5. The native gradient responds to new object magnitude.',
  'basic_buffer_bytes':32*67**3,'finite_domain':'N67, reference quantities11/17/31, three current objects, comparison times70+67k relative to a fixed reference-experience time'}
 g['schema']='CPC8R.quantity.transient.geometry.v3g4';g['guard_distance']=4
 return r,g
def physical(w):
 r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
class QuantitySession:
 def __init__(self,w,g,state=None):self.world=w;self.geometry=deepcopy(g);self.state=deepcopy(state)if state is not None else{'requests':[],'observations':[]}
 @classmethod
 def create(cls,**kw):r,g=prepare(**kw);return cls(d.OrganizationalWorld.create(r),g)
 @property
 def tick(self):return int(self.world.runtime.current_tick)
 def input(self,port,payload,tick,probe=False):
  if type(payload)is not int or not 0<=payload<=65535 or type(tick)is not int or tick<self.tick:raise ValueError('Input outside exact integer contract')
  r=getattr(self.world,'probe'if probe else'submit')(port,payload,tick)
  self.state['requests'].append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'kind':'probe'if probe else'submit'});return exact_receipt(r)
 def experience_reference(self,value,tick=0,mode='paired'):
  if mode not in('paired','unpaired','no_cue'):raise ValueError('Declared experience control')
  if mode!='no_cue':self.input('quantity.reference.cue',5,tick+int(mode=='unpaired'))
  self.input('quantity.reference.resource',value,tick)
 def present_object(self,value,reference_time=0,round_index=0):
  t=reference_time+65+67*round_index
  self.input('quantity.object.cue',5,t);self.input('quantity.object.resource',value,t)
 def reader_opportunity(self,reference_time=0):
  return[self.input('quantity.reader',7,reference_time+69+67*k,True)for k in range(3)]
 def acquire_other(self,tick=110):
  self.input('quantity.other.cue',5,tick);self.input('quantity.other.event',11,tick);self.input('quantity.other.cue',9,tick+67,True)
 def observe(self,site):return exact_observation(self.world.runtime.observe(d.Coordinate(*site)))
 def capture(self):
  c=self.geometry['center'];row={'tick':self.tick,'physical':physical(self.world),'center':self.observe(c),'reference':self.observe(self.geometry['reference_site']),'object':self.observe(self.geometry['object_site']),
   'Moore27':[self.observe(move(c,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],'origin':'INSTRUMENTO_PASSIVE_VIEW_OF_NATIVE_FIELDS'}
  self.state['observations'].append(row);return row
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotonic tick required')
  self.world.run_until(tick)
 def receipts(self):return[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.state['requests']]
 def save(self,path):
  self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
 @classmethod
 def load(cls,path):
  w,_=load_world_snapshot(path,max_bytes=1024**3);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY]);assert m['tick']==int(w.runtime.current_tick)and m['channels']==sorted(w.runtime.channel_names)
  return cls(w,m['geometry'],m['state'])
