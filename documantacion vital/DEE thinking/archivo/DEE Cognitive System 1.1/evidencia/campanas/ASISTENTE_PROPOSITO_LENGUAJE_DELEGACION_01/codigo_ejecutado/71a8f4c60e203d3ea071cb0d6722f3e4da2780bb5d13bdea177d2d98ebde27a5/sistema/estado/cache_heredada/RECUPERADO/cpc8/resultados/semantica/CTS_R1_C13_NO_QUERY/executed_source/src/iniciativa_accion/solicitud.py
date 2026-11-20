"""Acquired reference -> native discrepancy question -> learned source -> effect.

The finite comparator/routing apparatus is prepared, not learned curiosity.
History supplies the reference and separately acquired source content. Every
candidate opportunity is scheduled independently of the actual comparison.
The component factory below allocates no Runtime and copies no learned state.
"""
from array import array
from copy import deepcopy
import hashlib
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC8R.initiative.finite.session.v1'
def move(q,v,k=1):return[(int(q[i])+int(v[i])*k)%67 for i in range(3)]
def phys(world):
 r=world.runtime
 return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
  'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def interface(name,site,vector,state=1):
 c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*vector);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
 p=d.InterfaceSpec();p.name=name;p.channel=c;return p

def prepare_component(*,comparison_sites,comparison_tick=70,prefix='initiative.',source_epoch=0):
 """Inert interfaces/geometry to add to a fresh same-N67 E1 recipe.

 comparison_sites maps each possible reference sign to its physical comparison
 site. An actual marker(a,0,+1) asks; marker(a,a,+1) follows another ray.
 This factory does not inspect the world or choose a site from observed data.
 """
 if set(comparison_sites)!= {-1,1}:raise ValueError('Both physical comparison possibilities must be declared')
 if type(comparison_tick)is not int or comparison_tick<20 or type(source_epoch)is not int or source_epoch<0 or source_epoch+3>=comparison_tick:
  raise ValueError('Finite source teaching must precede comparison')
 if not isinstance(prefix,str)or not prefix or len(prefix)>80:raise ValueError('Explicit interface namespace required')
 ports=[];branches=[];signatures={}
 def port(name,q,v,state=1):
  name=prefix+name;ports.append(interface(name,q,v,state));signatures[name]={'site':q,'direction':list(v),'state':state,'semantic':1};return name
 for a in(-1,1):
  h=list(comparison_sites[a]);rq=move(h,(a,0,1),3);source=move(rq,(0,1,0),5)
  request_port=port('request_opportunity.'+str(a),move(rq,(-a,1,-1),-3),(-a,1,-1))
  sources={};effects={}
  for p in(-1,1):
   vector=(p,-1,0);hub=move(source,vector,-(comparison_tick+8-(source_epoch+3)))
   sources[str(p)]={'value':p,'hub':hub,'source_contact':source,'direction':list(vector),
    'cue_port':port('source.'+str(a)+'.'+str(p)+'.cue',move(hub,(0,-1,0),-3),(0,-1,0)),
    'event_port':port('source.'+str(a)+'.'+str(p)+'.event',move(hub,(p,0,0),-3),(p,0,0),31)}
   effect=move(source,(p,0,0),4)
   effects[str(p)]={'site':effect,'opportunity_port':port('effect.'+str(a)+'.'+str(p),move(effect,(0,-1,-1),-3),(0,-1,-1),43),
    'return_site':move(effect,(p,-1,-1),5),'return_direction':[p,-1,-1]}
  branches.append({'reference_candidate':a,'comparison_site':h,'request_site':rq,'request_port':request_port,
   'request_direction':[0,1,0],'request_probe_site':move(rq,(0,1,0)), 'source_site':source,'sources':sources,'effects':effects})
 g={'schema':'CPC8R.initiative.component.v1','N':67,'prefix':prefix,'branches':branches,'signatures':signatures,'source_epoch':source_epoch,
  'ticks':{'comparison':comparison_tick,'request':comparison_tick+3,'question_in_flight':comparison_tick+4,'source':comparison_tick+8,'effect':comparison_tick+12,'return':comparison_tick+17},
  'prepared':'Fixed symmetric request and effect opportunities; geometry and the local comparator operation are prepared. No host reads a comparison to decide whether to ask.',
  'acquired':'Reference sign and source sign come from separately admitted postT0experiences. Provider duplicates are separately exposed physical memories, not free clones.',
  'scope':'One finite question conditioned on mismatch of a declared directional component, not general curiosity, free attention or a learned question policy.',
  'resources':{'initial_material_sites':0,'interfaces':len(ports),'request_opportunities':2,'effect_opportunities':4,'provider_copies_separately_exposed':2,'basic_buffers_bytes':32*67**3}}
 return ports,g

def prepare_standalone(*,origin=(8,50,5),comparison_tick=70,source_epoch=0,prefix='initiative.',backend='LAZY'):
 if comparison_tick!=70 or source_epoch!=0:raise ValueError('Standalone reference currently validated only for one67-tick return')
 h=move(origin,(0,0,0));ports,g=prepare_component(comparison_sites={-1:h,1:h},comparison_tick=comparison_tick,prefix=prefix,source_epoch=source_epoch)
 def port(name,q,v,state=1):
  name=prefix+name;ports.append(interface(name,q,v,state));g['signatures'][name]={'site':q,'direction':list(v),'state':state,'semantic':1};return name
 ref={'hub':h,'cue_port':port('reference.cue',move(h,(0,0,1),-3),(0,0,1)),'event_ports':{},'object_ports':{}}
 for a in(-1,1):ref['event_ports'][str(a)]=port('reference.event.'+str(a),move(h,(a,a,-1),-3),(a,a,-1),17)
 for b in(-1,1):ref['object_ports'][str(b)]=port('object.'+str(b),move(h,(0,b,1),-3),(0,b,1),83)
 g['reference']=ref;g['resources']['interfaces']=len(ports)
 if backend not in('LAZY','DENSE_SEQUENTIAL','DENSE_PARALLEL'):raise ValueError('Published native backend name required')
 r=d.OrganizationRecipe.research(67,[],0);r.execution=d.TickOptions(getattr(d.Backend,backend),1);r.interfaces=ports
 r.options={'CPC8R.initiative.geometry':encode_metadata(g)};r.domain=g['scope']
 org=d.OrganizationSpec();org.id='INITIATIVE';org.recipe_id='CPC8R.initiative.v1';org.ports={'reference':d.Coordinate(*h)};r.organizations=[org]
 return r,g

def prepare_gradient_tap(*,question_site=(52,35,35),question_tick=72,source_epoch=0,prefix='initiative.quantity.',question_direction=(0,1,1)):
 """Inert extension for an existing native +X comparator output.

 A +X marker physically reaching question_site meets a fixed(-X,+Y,0/+Z)
 opportunity. Opposite/zero outputs are not reclassified by the host. No
 comparator or trained source is installed; all provider knowledge must be
 experienced afterT0. Joint compatibility is an experiment, not an API claim.
 """
 if tuple(question_direction)not in((0,1,0),(0,1,1)):raise ValueError('Two explicit prepared question routes only')
 if type(question_tick)is not int or type(source_epoch)is not int or question_tick<=source_epoch+12:
  raise ValueError('Source experience must precede finite contact')
 q=move(question_site,(0,0,0));qd=tuple(question_direction);source=move(q,qd,5);ports=[];signatures={}
 def port(name,site,vector,state=1):
  name=prefix+name;ports.append(interface(name,site,vector,state));signatures[name]={'site':site,'direction':list(vector),'state':state,'semantic':1};return name
 turn=(-1,qd[1],qd[2]);request=port('request_opportunity',move(q,turn,-3),turn)
 sources={};effects={}
 for p in(-1,1):
  vector=(p,-qd[1],-qd[2]);cue=(0,-qd[1],-qd[2]);hub=move(source,vector,-(question_tick+5-(source_epoch+3)))
  sources[str(p)]={'value':p,'hub':hub,'source_contact':source,'direction':list(vector),
   'cue_port':port('source.'+str(p)+'.cue',move(hub,cue,-3),cue),
   'event_port':port('source.'+str(p)+'.event',move(hub,(p,0,0),-3),(p,0,0),31)}
  effect=move(source,(p,0,0),4)
  effects[str(p)]={'site':effect,'opportunity_port':port('effect.'+str(p),move(effect,(0,-1,-1),-3),(0,-1,-1),43),
   'return_site':move(effect,(p,-1,-1),5),'return_direction':[p,-1,-1]}
 branch={'reference_candidate':1,'incoming_candidate':'+X_NATIVE_COMPARATOR_OUTPUT','comparison_site':move(q,(1,0,0),-2),
  'request_site':q,'request_port':request,'request_direction':list(qd),'request_probe_site':move(q,qd),
  'source_site':source,'sources':sources,'effects':effects}
 g={'schema':'CPC8R.initiative.gradient_tap.v1','N':67,'prefix':prefix,'branches':[branch],'signatures':signatures,'source_epoch':source_epoch,
  'ticks':{'comparison':question_tick-2,'request':question_tick,'question_in_flight':question_tick+1,'source':question_tick+5,'effect':question_tick+9,'return':question_tick+14},
  'prepared':'One fixed conditional geometric tap and both symmetric effect resources. Does not prepare or classify the upstream comparison.',
  'acquired':'Source directional content only through postT0cue/event experiences. Upstream reference acquisition remains the owningE1protocol.',
  'scope':'A native positive-X comparator output can trigger a finite information request; negative/zero outputs are measured separately. No general need-for-information claim.',
  'resources':{'initial_material_sites':0,'interfaces':len(ports),'request_opportunities':1,'effect_opportunities':2,'provider_copies_separately_exposed':1,'basic_buffers_bytes':'Shared with owningN67Runtime, not allocated by factory'}}
 return ports,g

class InitiativeSession:
 def __init__(self,world,geometry,state=None):
  self.world=world;self.geometry=deepcopy(geometry);self.state=deepcopy(state)if state is not None else{'requests':[],'captures':[]}
 @classmethod
 def create(cls,**options):r,g=prepare_standalone(**options);return cls(d.OrganizationalWorld.create(r),g)
 @property
 def tick(self):return int(self.world.runtime.current_tick)
 def submit(self,port,load,tick,origin,probe=False):
  if type(load)is not int or not 0<=load<=65535 or type(tick)is not int or tick<self.tick:raise ValueError('Exact admitted-current/future input required')
  if port not in self.geometry['signatures']:raise ValueError('Undeclared interface')
  rr=getattr(self.world,'probe'if probe else'submit')(port,load,tick)
  self.state['requests'].append({'id':int(rr.id),'port':port,'load':load,'requested_tick':tick,'origin':origin,'call_tick':self.tick,'kind':'probe'if probe else'submit'})
  return exact_receipt(rr)
 def acquire_reference(self,a,mode='paired',load=11):
  if a not in(-1,1)or mode not in('paired','unpaired','virgin'):raise ValueError('Reference experience domain')
  g=self.geometry['reference']
  self.submit(g['cue_port'],0,int(mode=='unpaired'),'REFERENCE_RECORDING_CUE')
  if mode!='virgin':self.submit(g['event_ports'][str(a)],load,0,'ACTUAL_REFERENCE_OBSERVATION')
 def acquire_source(self,p,mode='paired',cue=5,event=11):
  if p not in(-1,1)or mode not in('paired','unpaired','virgin'):raise ValueError('Source experience domain')
  if mode=='virgin':return
  for branch in self.geometry['branches']:
   source=branch['sources'][str(p)];t=self.geometry['source_epoch']
   self.submit(source['cue_port'],cue,t+int(mode=='unpaired'),'PROVIDER_OPAQUE_CUE')
   self.submit(source['event_port'],event,t,'PROVIDER_CURRENT_OBSERVATION_NOT_TARGET')
 def present_object(self,b,load=7):
  if b not in(-1,1):raise ValueError('Current object direction domain')
  self.submit(self.geometry['reference']['object_ports'][str(b)],load,self.geometry['ticks']['comparison']-3,'CURRENT_NOVEL_OBJECT_NOT_MATCH_LABEL',True)
 def opportunities(self,request=True,effect_load=7,effect=True):
  if type(request)is not bool or type(effect)is not bool:raise TypeError('Explicit opportunity switches')
  for branch in self.geometry['branches']:
   if request:self.submit(branch['request_port'],0,self.geometry['ticks']['request']-3,'FIXED_SYMMETRIC_ZERO_LOAD_QUESTION_OPPORTUNITY')
   if effect:
    for item in branch['effects'].values():self.submit(item['opportunity_port'],effect_load,self.geometry['ticks']['effect']-3,'FIXED_ALL_CANDIDATE_RETURN_EFFECT_RESOURCE')
 def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
 def capture(self):
  g=self.geometry;row={'tick':self.tick,'branches':[],'modality':'PASSIVE_OBSERVATION_OF_NATIVE_TRANSITIONS'}
  if 'reference'in g:row['reference']=self.observe(g['reference']['hub'])
  for b in g['branches']:
   row['branches'].append({'reference_candidate':b['reference_candidate'],
    'question':self.observe(b['request_site']),'question_in_flight':self.observe(b['request_probe_site']),
    'source':self.observe(b['source_site']),
    'effects':{p:self.observe(e['site'])for p,e in b['effects'].items()},
    'return':{p:self.observe(e['return_site'])for p,e in b['effects'].items()}})
  self.state['captures'].append(row);return row
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone integer ticks')
  self.world.run_until(tick)
 def receipts(self):return[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.state['requests']]
 def save(self,path):
  self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}))
  return save_world_snapshot(self.world,path,compress=True)
 @classmethod
 def load(cls,path):
  world,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(world.runtime.snapshot_metadata_entries)[KEY])
  if m['tick']!=int(world.runtime.current_tick)or m['channels']!=sorted(world.runtime.channel_names):raise ValueError('Operative state differs')
  return cls(world,m['geometry'],m['state'])
