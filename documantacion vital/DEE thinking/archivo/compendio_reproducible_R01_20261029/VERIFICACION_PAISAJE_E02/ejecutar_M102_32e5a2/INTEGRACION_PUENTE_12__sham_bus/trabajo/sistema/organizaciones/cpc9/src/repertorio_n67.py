"""New N67 physical repertoire scout, not65semantic meanings or CPC5 port.

All forms/ports are prepared before T0. The participant has no teaching map;
it only submits actual events, records receipts and evolves official v27.
Each direction is acquired from an actual cue/event encounter after creation.
No initial material, no clearing, no clock edits, no world-to-world copying.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC9.repertoire.N67.scout.v1'
def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def prepare(k=65):
    if not 1<=k<=65:raise ValueError('Finite prepared N67 repertoire domain1–65')
    ports=[];forms=[]
    for index in range(k):
        hub=[1+index,20,(3*index+7)%67];entry={'id':'F%02d'%index,'hub':hub,'ports':{}}
        for role,v in(('cue',(-1,0,0)),('event.plus',(1,1,0)),('event.minus',(1,-1,0)),('read.plus',(0,0,1)),('read.minus',(0,0,-1))):
            name='physical.'+entry['id']+'.'+role;channel=d.ChannelSpec();channel.name=name
            channel.injection_site=d.Coordinate(*move(hub,v,-3));channel.direction=d.Direction(*v)
            channel.state=1;channel.semantic=1;channel.allow_experience=True;channel.allow_probe=True
            p=d.InterfaceSpec();p.name=name;p.channel=channel;ports.append(p);entry['ports'][role]=name
        forms.append(entry)
    recipe=d.OrganizationRecipe.research(67,[],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    g={'schema':KEY,'N':67,'forms':forms,'resources':{'initial_material':0,'interfaces':len(ports),'basic_buffer_bytes':32*67**3},
       'prepared':'Distinct fixed X/Z lines, common Y history carriers, five ports per opaque form. Query signs and timing belong to the external finite protocol, not learned native access.',
       'acquired':'Actual post-T0 cue/event meetings yield ±Y material memory. No current target relation is present in initial matter.',
       'scope':'Physical directional correspondences only; not65NSM meanings, no native contextual selector, and not integratedE1 until the actual same-world extension is separately validated.'}
    recipe.options={KEY:encode_metadata(g)};return recipe,g
class N67RepertoireSession:
    def __init__(self,world,g,state=None):self.world=world;self.geometry=deepcopy(g);self.state=deepcopy(state)if state is not None else{'requests':[]}
    @classmethod
    def create(cls,k=65):recipe,g=prepare(k);return cls(d.OrganizationalWorld.create(recipe),g)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,port,payload,tick,probe=False):
        receipt=(self.world.probe if probe else self.world.submit)(port,payload,tick)
        self.state['requests'].append({'id':int(receipt.id),'port':port,'payload':payload,'tick':tick,'probe':probe});return exact_receipt(receipt)
    def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
    def run_until(self,tick):self.world.run_until(tick)
    def receipts(self):return[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.state['requests']]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        world,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(world.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(world.runtime.current_tick)or m['channels']!=sorted(world.runtime.channel_names):raise ValueError('Repertoire continuity mismatch')
        return cls(world,m['geometry'],m['state'])
