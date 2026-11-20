"""Physical arrival from different starting positions, not an order-bit sensor."""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC8R.spatial_arrival.session.v1'
def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def prepare_geometry():
 n=67;c=[33,33,33];a=move(c,(-1,0,0));b=move(c,(1,0,0));q=move(c,(0,-1,0));initial=[];ports=[]
 def put(site,state,load,sem,clock,v=(0,0,0)):
  p=d.InitialPlacement();p.site=d.Coordinate(*site);p.raw=d.pack_record(state,load,*v,sem);p.clock=clock;p.role='Prepared native relative sensor';initial.append(p)
 def port(name,site,v,state):
  ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*v);ch.state=state;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
  p=d.InterfaceSpec();p.name=name;p.channel=ch;ports.append(p)
 put(a,1000,100,1,260);put(b,2000,100,1,260)
 for site,pattern,state,clock in((a,((-1,0,0),(-1,1,1),(0,0,1),(0,1,0)),3000,31),(b,((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0)),4000,41)):
  for i,v in enumerate(pattern):put(move(site,v),state+i,0,4,clock+i)
 put(move(c,(0,0,1)),6100,0,4,19)
 sources=[]
 for epoch in range(3):
  for who,body,v in [('A',a,(0,1,0)),('B',b,(0,-1,0))]:
   for distance in (2,3,4,6,7):
    site=move(body,v,-distance-1);name='traveller.'+str(epoch)+'.'+who+'.'+str(distance);port(name,site,v,5000+100*epoch+(who=='B'));sources.append({'epoch':epoch,'participant':who,'distance_to_sensor_neighbor':distance,'port':name,'start':site,'direction':list(v),'body':body})
 port('read',q,(0,1,0),1)
 recipe=d.OrganizationRecipe.research(67,initial,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
 g={'schema':'CPC8R.spatial_arrival.geometry.v1','N':67,'body':{'center':c,'A':a,'B':b,'emission':q},'sources':sources,'initial_material':len(initial),'interfaces':len(ports),'sensor_scope':'Relative physical access by equal-speed incoming travelers. Distance is an auditor coordinate; participant receives only native encounters. Not universal above/below or Euclidean distance concept.'};recipe.options={'geometry':encode_metadata(g)}
 return recipe,g
class SpatialSession:
 def __init__(self,w,g,state=None):self.world=w;self.geometry=g;self.state=deepcopy(state) if state else {'requests':[],'captures':[]}
 @classmethod
 def create(cls):r,g=prepare_geometry();return cls(d.OrganizationalWorld.create(r),g)
 @property
 def tick(self):return int(self.world.runtime.current_tick)
 def input(self,name,payload,tick,origin,kind='submit'):
  x=getattr(self.world,kind)(name,payload,tick);self.state['requests'].append({'id':int(x.id),'port':name,'payload':payload,'tick':tick,'origin':origin,'kind':kind});return exact_receipt(x)
 def episode(self,epoch,base,da,db):
  for who,distance in [('A',da),('B',db)]:self.input('traveller.'+str(epoch)+'.'+who+'.'+str(distance),3,base,'ACTUAL_TRAVELER_AT_DECLARED_STARTING_POSITION')
  self.input('read',7,base+10,'FIXED_COMMON_READER_NOT_NEAR_FAR_TARGET','probe')
 def run_until(self,tick):self.world.run_until(tick)
 def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
 def receipts(self):return[{**x,'receipt':exact_receipt(self.world.runtime.receipt(x['id']))}for x in self.state['requests']]
 def save(self,path):
  self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
