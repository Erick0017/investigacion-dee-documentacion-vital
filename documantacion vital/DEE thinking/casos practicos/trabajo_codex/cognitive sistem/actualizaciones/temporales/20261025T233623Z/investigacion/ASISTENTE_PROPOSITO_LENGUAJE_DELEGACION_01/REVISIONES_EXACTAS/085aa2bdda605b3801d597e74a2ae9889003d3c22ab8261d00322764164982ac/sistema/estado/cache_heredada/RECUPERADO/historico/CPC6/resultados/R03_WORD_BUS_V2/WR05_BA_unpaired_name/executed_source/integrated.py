"""A single-owner experimental U0 MAIN; all transformations are v27 evolution.

The Python session transports fixed physical requests and makes passive records.
It never obtains an expected answer, selects a correct route or edits a cell.
"""
import json
from copy import deepcopy
from pathlib import Path
from common import put,sha,record,receipt,digest,operational,until,local_context
import order_memory

KEY='cpc6.u0.session.v1'

def create(adapter=True,backend='LAZY',center=(33,25,33),language=True,consolidation=False,consolidation_phase=171):
    import dee_thinking as d
    body=order_memory.prepare_geometry(center=center)
    ps=list(body['placements']);ports=list(body['interfaces'])
    geometry={'schema':'CPC6.U0.geometry.v1','body':body['geometry'],'adapter':None,'language':None}
    if adapter:
        import action_feedback
        component=action_feedback.prepare_geometry(n=67,origin=body['geometry']['emission_site'],emission_tick=5,distance=10)
        ps+=component['placements'];ports+=component['interfaces'];geometry['adapter']=component['geometry']
        if language:
            import language as linguistic
            names=linguistic.prepare_geometry(geometry['adapter']);ports+=names['interfaces'];geometry['language']=names['geometry']
    if consolidation:
        import consolidation as consolidator
        p=consolidator.prepare_geometry(phase=consolidation_phase,landing=consolidation if isinstance(consolidation,str) else 'closed')
        ps+=p['placements'];ports+=p['interfaces'];geometry['consolidation']=p['geometry']
    sites=[(p.site.x,p.site.y,p.site.z) for p in ps]
    if len(set(sites))!=len(sites):raise ValueError('Prepared regions overlap; no last-write-wins permitted')
    if len({p.name for p in ports})!=len(ports):raise ValueError('Duplicate physical interface')
    recipe=d.OrganizationRecipe.research(67,ps,0);recipe.interfaces=ports
    b=getattr(d.Backend,backend);recipe.execution=d.TickOptions(b,2 if backend=='DENSE_PARALLEL' else 1)
    w=d.OrganizationalWorld.create(recipe)
    return Session(w,geometry)

class Session:
    def __init__(self,world,geometry,requests=None,identity='U0'):
        self.world=world;self.geometry=deepcopy(geometry);self.requests=deepcopy(requests or []);self.identity=identity
    def stimulate(self,requests):
        for request in requests:
            port=request['port'];payload=request['payload'];tick=request['tick'];kind=request.get('kind','submit')
            if type(payload) is not int or type(tick) is not int:raise TypeError('Payload and absolute tick must be exact integers, not float/bool')
            if not 0<=payload<=65535 or not 0<=tick<2**64:raise ValueError('Outside representable uint16/uint64 input range')
            if kind not in ('submit','probe'):raise ValueError('Only explicit experience or physical probe')
            result=getattr(self.world,kind)(port,payload,tick)
            self.requests.append({**request,'payload':payload,'tick':tick,'kind':kind,'id':int(result.id),
                                  'call_tick':int(self.world.runtime.current_tick)})
    def advance_to(self,tick):until(self.world,tick)
    def observe(self):
        return {'identity':self.identity,'tick':int(self.world.runtime.current_tick),
                'body':order_memory.observations(self.world,self.geometry['body']),
                'physical':digest(self.world)}
    def receipts(self):return [{**q,'receipt':receipt(self.world,q['id'])} for q in self.requests]
    def save(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        # Only public geometry, operation IDs and progression: no target map or response cache.
        value={'schema':1,'identity':self.identity,'geometry':self.geometry,
               'requests':self.requests,'tick':int(self.world.runtime.current_tick)}
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(value,separators=(',',':')))
        self.world.save_snapshot(str(path))
        return {'path':str(path),'sha256':sha(path),'physical':digest(self.world),'operative':operational(self.world)}
    @classmethod
    def load(cls,path):
        import dee_thinking as d
        w=d.OrganizationalWorld.load_snapshot(str(path));m=dict(w.runtime.snapshot_metadata_entries)
        value=json.loads(m[KEY]);
        if value.get('schema')!=1 or value['tick']!=w.runtime.current_tick:raise ValueError('Unsupported or stale CPC6 session')
        return cls(w,value['geometry'],value['requests'],value['identity'])
    def fork(self,identity):
        return Session(self.world.fork(),self.geometry,self.requests,identity)

def smoke_body(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for order in ('AB','BA'):
        s=create(adapter=False);s.stimulate(order_memory.experience(order))
        s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_READER'}])
        for tick in range(8):
            s.advance_to(tick);rows.append({'history':order,**s.observe()})
        put(output/(order+'.json'),{'observations':rows[-8:],'requests':s.receipts()})
    put(output/'SMOKE.json',rows)
    print(json.dumps([{'history':r['history'],'tick':r['tick'],'delta':r['body']['delta'],
                       'emission':r['body']['emission']} for r in rows if r['tick']==5]))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--smoke-body',type=Path,required=True);a=p.parse_args();smoke_body(a.smoke_body)
