"""Finite native query inhibition and social acquisition, not general curiosity.

Identical external opportunities in every history. A local acquired response
opposes the opportunity at a physical gate. An uninhibited zero-load carrier
can query B; a B carrier can return and change later local inhibition.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC9.acquired_query.v1'

def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def prepare(origin=(12,8,55)):
    h=list(origin);gate=move(h,(-1,1,0),6)
    turns=[('question_turn',move(h,(-1,1,0),4),78,(-1,1,1)),
           ('return_Y',move(h,(-1,1,6)),84,(-1,0,-1)),
           ('return_Zup',move(h,(-1,-7,6)),92,(0,1,1)),
           ('return_Yup',move(h,(-1,-7,22)),108,(0,1,-1)),
           ('return_Zdown',move(h,(-1,-1,22)),114,(0,-1,-1)),
           ('return_home',move(h,(-1,-1,0)),136,(1,1,1))]
    b=move(h,(-4,4,3));ports=[];signatures={}
    def port(name,target,v):
        injection=move(target,v,-3);c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*injection)
        c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p)
        signatures[name]={'site':injection,'direction':list(v),'target':target}
    for name,target,v in [('local.cue',h,(-1,0,0)),('local.event',h,(1,1,0)),('local.reader',h,(-1,0,0)),
                          ('gate.opportunity',gate,(1,-1,0)),('B.cue',b,(1,0,1)),('B.event.minus',b,(0,-1,-1)),
                          ('B.event.plus',b,(0,1,-1))]:port(name,target,v)
    for name,target,tick,v in turns:port('route.'+name,target,v)
    recipe=d.OrganizationRecipe.research(67,[],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);recipe.interfaces=ports
    g={'schema':KEY,'N':67,'origin':h,'gate':gate,'B':b,'turns':[{'id':name,'site':q,'tick':t,'direction':list(v)}for name,q,t,v in turns],
       'signatures':signatures,'question_ticks':[76,143,210,277],'local_query_ticks':[70,137,204,271],
       'prepared':'Empty initial material, fixed channels/zero-load route turns, periodic external opportunities and readers. The gate operation is prepared, not a learned question policy.',
       'learned':'Paired local experience may supply Y in the opposing gate response; otherwise a B history can supply that component through actual native return137.',
       'information_scope':'One acquired content/return channel; no general source choice, uncertainty estimator or semantic KNOW/YO/TU assumed',
       'resources':{'initial_material':0,'interfaces':len(ports),'basic_buffer_bytes':32*67**3}}
    recipe.options={KEY:encode_metadata(g)};recipe.domain=g['information_scope'];return recipe,g


class QuerySession:
    def __init__(self,world,g,state=None):self.world=world;self.geometry=deepcopy(g);self.state=deepcopy(state)if state is not None else{'requests':[]}
    @classmethod
    def create(cls,**options):r,g=prepare(**options);return cls(d.OrganizationalWorld.create(r),g)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,port,load,tick,probe=False):
        rr=(self.world.probe if probe else self.world.submit)(port,load,tick)
        self.state['requests'].append({'id':int(rr.id),'port':port,'payload':load,'requested_tick':tick,'probe':probe})
        return exact_receipt(rr)
    def curriculum(self,local='unknown',remote='known',delay=0,local_load=11,remote_load=11):
        if self.tick!=0 or local not in('known','unknown','blank','unpaired')or remote not in('known','unknown','wrong','unpaired'):
            raise ValueError('Fresh explicit experience histories only')
        self.geometry['delay']=delay
        if local!='blank':self.input('local.cue',5,delay)
        if local in('known','unpaired'):self.input('local.event',local_load,delay+int(local=='unpaired'))
        self.input('B.cue',5,11+delay)
        if remote!='unknown':self.input('B.event.plus'if remote=='wrong'else'B.event.minus',remote_load,11+delay+int(remote=='unpaired'))
        for tick in self.geometry['local_query_ticks']:self.input('local.reader',7,tick-3+delay,True)
        for tick in self.geometry['question_ticks']:self.input('gate.opportunity',0,tick-3+delay)
        for turn in self.geometry['turns']:self.input('route.'+turn['id'],0,turn['tick']-3+delay)
    def observe(self,site):return exact_observation(self.world.runtime.observe(d.Coordinate(*site)))
    def view(self):
        g=self.geometry
        return {'tick':self.tick,'local':self.observe(g['origin']),'gate':self.observe(g['gate']),'B':self.observe(g['B']),
                'turns':{t['id']:self.observe(t['site'])for t in g['turns']}}
    def run_until(self,tick):self.world.run_until(tick)
    def receipts(self):return[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.state['requests']]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(w.runtime.current_tick)or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Query state mismatch')
        return cls(w,m['geometry'],m['state'])
