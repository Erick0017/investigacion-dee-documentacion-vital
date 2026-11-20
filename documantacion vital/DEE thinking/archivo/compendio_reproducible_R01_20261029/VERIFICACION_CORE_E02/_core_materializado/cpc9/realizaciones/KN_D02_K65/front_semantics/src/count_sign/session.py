"""Post-function opaque form over the frozen contact-unit geometry.

All branch formatters are prepared and stimulated equally; no output chooses
a correct count bank. The threshold comparison is a prepared native instrument,
not an acquired abstract counting rule or human ONE/TWO semantics.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
from dee_thinking.consolidated import exact_observation,exact_receipt
from relaciones.contact_cardinality import prepare as prepare_count
from integracion.quantity_core import prepare as prepare_quantity
KEY='CPC8R.count_sign.session.v1'

def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def port(name,q,v,state=1):
 c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
 p=d.InterfaceSpec();p.name=name;p.channel=c;return p

def prepare(case):
 opts={k:case[k]for k in('contacts','actor_state','medium_state','actor_load','unit_load')if k in case};opts['regulation']='branch_onpath'
 r,cg=prepare_count(opts);ports=list(r.interfaces);routes=[];c=cg['collector']
 for s in(-1,0,1):
  first=move(c,(s,1,1),3);second=move(first,(0,0,1));v1=(-s,-1,0);v2=(-s,0,0)
  p1='count.route.first.'+str(s);p2='count.route.second.'+str(s)
  ports.extend((port(p1,move(first,v1,-3),v1),port(p2,move(second,v2,-3),v2)))
  routes.append({'axis_candidate':s,'first':first,'second':second,'first_port':p1,'second_port':p2})
 joint=move(c,(0,3,7));turn=move(joint,(0,0,1));turnv=(0,1,-1);ports.append(port('count.route.turn',move(turn,turnv,-3),turnv))
 layout=case.get('layout',1)
 if layout not in(1,2):raise ValueError('Two explicitly versioned layouts')
 reference_steps=6 if layout==2 else 2
 reference_tick=18+reference_steps;comparison_tick=reference_tick+67;form_tick=comparison_tick+3
 reference_hub=move(turn,(0,1,0),reference_steps);center=move(reference_hub,(1,-1,0))
 qr,qg=prepare_quantity(center=center,profile='permanent',guards='on_path')
 for p in qr.interfaces:
  p.name='countQ.'+p.name;ch=p.channel;ch.name='countQ.'+ch.name;p.channel=ch;ports.append(p)
 names=[]
 for v in(0,1):
  comparison_z=1 if layout==2 else -1
  site=move(center,(v,0,comparison_z),3);cue=(-1,1,-comparison_z);prefix='count.form.'+str(v)
  pp=prefix+'.record';qp=prefix+'.read'
  ports.extend((port(pp,move(site,cue,-3),cue,77),port(qp,move(site,(0,0,1),-3),(0,0,1),77)))
  names.append({'candidate_comparator_x':v,'memory_site':site,'record_port':pp,'query_port':qp,'expected_query_direction':[v-1,1,1]})
 placements=list(r.placements)+list(qr.placements)
 sites=[(p.site.x,p.site.y,p.site.z)for p in placements]
 if len(sites)!=len(set(sites)):raise ValueError('Count-sign initial overlap')
 if len({p.name for p in ports})!=len(ports):raise ValueError('Count-sign interface overlap')
 r.placements=placements;r.interfaces=ports
 g={'schema':'CPC8R.count_sign.geometry.v'+str(layout),'layout':layout,'N':67,'count':cg,'routes':routes,'joint17':joint,'turn18':turn,'reference_hub20':reference_hub,'quantity':qg,'names':names,
  'ticks':{'count10':10,'postroute17':17,'reference':reference_tick,'comparison':comparison_tick,'form':form_tick,'queries':[form_tick+67,form_tick+134]},
  'resources':{'initial_material_sites':len(placements),'interfaces':len(ports),'count_unit_media':2,'basic_buffer_bytes':32*67**3},
  'prepared':'Frozen F3 count normalizers unchanged. Three redundant physical formatting branches, permanent-gradient threshold comparator and both form banks declaredT0. Object threshold is actual material1+format5, not a target label.',
  'acquired':'Contact paths determine whether1or2 normalized units reach the native carrier. The opaque cue is presented after the physical comparison, identically at both candidate form banks.',
  'scope':'Auxiliary fixed-dose count-to-form candidate. No general ONE/TWO category, arbitrary grammar, learned comparator or learned routing policy claimed.'}
 r.options={'CPC8R.count_sign.geometry':encode_metadata(g)};r.domain=g['scope'];return r,g

class CountSignSession:
 def __init__(self,world,geometry,state=None,identifier='COUNT_SIGN'):
  self.world=world;self.geometry=deepcopy(geometry);self.state=deepcopy(state)if state is not None else{'requests':[]};self.identifier=identifier
 @classmethod
 def create(cls,case):r,g=prepare(case);return cls(d.OrganizationalWorld.create(r),g,identifier=case['id'])
 @property
 def tick(self):return int(self.world.runtime.current_tick)
 def input(self,name,load,tick,probe=False):
  if type(tick)is not int or tick<self.tick or type(load)is not int or not 0<=load<=65535:raise ValueError('Exact current/future physical input')
  rr=(self.world.probe if probe else self.world.submit)(name,load,tick);self.state['requests'].append({'id':int(rr.id),'port':name,'payload':load,'tick':tick,'kind':'probe'if probe else'experience'});return exact_receipt(rr)
 def curriculum(self,form='paired',route=True,query=True):
  if self.tick!=0 or form not in('paired','unpaired','omitted'):raise ValueError('Fresh finite protocol')
  self.input('counter.cue',5,7)
  for name in('A','B'):self.input('counter.free.guard.'+name,0,6)
  if route:
   for r in self.geometry['routes']:self.input(r['first_port'],0,10);self.input(r['second_port'],0,11)
   self.input('count.route.turn',0,15)
  # Only threshold object is externally provided. No reference input is sent
  # to countQ.quantity.reference.*: the count carrier must become reference.
  ticks=self.geometry['ticks'];reference_time=ticks['reference']-3
  self.input('countQ.quantity.object.cue',5,reference_time+65);self.input('countQ.quantity.object.resource',1,reference_time+65);self.input('countQ.quantity.reader',7,ticks['comparison']-1,True)
  for p in self.geometry['names']:
   if form!='omitted':self.input(p['record_port'],5,ticks['form']-3+(5 if form=='unpaired'else 0))
   if query:
    for t in ticks['queries']:self.input(p['query_port'],7,t-3,True)
  self.input('extra.cue',5,100);self.input('extra.event',11,100);self.input('extra.query',9,167,True)
 def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
 def view(self):
  g=self.geometry;return{'tick':self.tick,'counter':self.observe(g['count']['collector']),'joint17':self.observe(g['joint17']),'reference_hub20':self.observe(g['reference_hub20']),
   'quantity':{k:self.observe(g['quantity'][k])for k in('center','reference_site','object_site')},'names':[{'candidate_comparator_x':p['candidate_comparator_x'],'physical':self.observe(p['memory_site'])}for p in g['names']],'extra':self.observe(g['count']['extra'])}
 def run_until(self,tick):
  if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks')
  self.world.run_until(tick);return self.view()
 def receipts(self):return[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.state['requests']]
 def save(self,path):
  self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'identifier':self.identifier,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
 @classmethod
 def load(cls,path):
  w,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
  if m['tick']!=int(w.runtime.current_tick)or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Operational mismatch')
  return cls(w,m['geometry'],m['state'],m['identifier'])
