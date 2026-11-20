"""Acquired directional reference applied to new physical carriers.

Acquisition stores(a,a,0). A new object carries only(0,b,+1), not a match bit.
v27 produces(a,sign(a+b),+1). Fixed symmetric resources restore the reference
without selecting a branch from a host readout. The comparator is prepared;
the reference is acquired. This is similarity of a declared motion component,
not identity of an object or universal semantic equivalence.
"""
from copy import deepcopy
from array import array
import hashlib
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC8R.mode_reference.session.v1'
def move(q,v,k=1,n=67):return [(q[i]+v[i]*k)%n for i in range(3)]
def physical(w):
    r=w.runtime;return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def prepare_geometry(*,dimension=67,origin=(20,20,20),object_states=(31,83),reference_state=17,cleanup=False,port_prefix='',first_query_tick=70):
    if dimension!=67 or len(object_states)!=2:raise ValueError('Frozen N67 two-object prototype')
    n=dimension;h=list(origin);interfaces=[];signatures={};branches=[];parents=[{'id':'root','hub':h,'query_tick':first_query_tick,'a':None}];queries=[]
    def port(name,q,v,state=1):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;interfaces.append(p);signatures[name]=[list(q),list(v),state,1]
    port('reference.record',move(h,(0,0,1),-3),(0,0,1))
    for a,label in((-1,'minus'),(1,'plus')):port('reference.object.'+label,move(h,(a,a,-1),-3),(a,a,-1),reference_state)
    for stage in(1,2):
        children=[]
        for parent in parents:
            for b,label in((-1,'minus'),(1,'plus')):port('object'+str(stage)+'.'+parent['id']+'.'+label,move(parent['hub'],(0,b,1),-3),(0,b,1),object_states[stage-1])
            queries.append({'stage':stage,'parent':deepcopy(parent),'ports':{str(b):'object'+str(stage)+'.'+parent['id']+'.'+('plus' if b>0 else'minus') for b in(-1,1)}})
            for a in((-1,1) if parent['a'] is None else(parent['a'],)):
                for y in(0,a):
                    tag=parent['id']+'.a'+str(a)+'.y'+str(y);first_gap=8;second_gap=12 if y==0 else 20
                    first=move(parent['hub'],(a,y,1),first_gap,n);second=move(first,(a,0,0),second_gap,n)
                    p1='normalizer1.'+tag;p2='normalizer2.'+tag
                    port(p1,move(first,(0,-y,-1),-3,n),(0,-y,-1));port(p2,move(second,(0,a,0),-3,n),(0,a,0))
                    cleanup_port='cleanup.'+tag
                    cleanup_site=move(second,(0,a,0),4,n)
                    if cleanup:port(cleanup_port,move(cleanup_site,(0,-a,0),-1,n),(0,-a,0))
                    branch={'id':tag,'stage':stage,'a_axis':a,'comparison_y':y,'query_site':parent['hub'],'query_tick':parent['query_tick'],
                        'first_site':first,'first_tick':parent['query_tick']+first_gap,'first_port':p1,'second_site':second,'second_tick':parent['query_tick']+first_gap+second_gap,'second_port':p2,
                        'cleanup_port':cleanup_port if cleanup else None,'cleanup_tick':parent['query_tick']+first_gap+second_gap+4,'cleanup_site':cleanup_site,
                        'normalizer_scope':'All candidate branches scheduled independently of actual reference/object; no host lookup of matching result.'}
                    branches.append(branch)
                    if not cleanup or y==0:children.append({'id':tag,'hub':second,'query_tick':branch['second_tick']+n,'a':a})
        parents=children
    aux=move(h,(-15,30,35),1,n);port('other.signal',move(aux,(-1,0,0),-3),(-1,0,0))
    for v,label in((-1,'minus'),(1,'plus')):port('other.event.'+label,move(aux,(1,v,0),-3),(1,v,0))
    if port_prefix:
        for spec in interfaces:
            name=spec.name;spec.name=port_prefix+name;c=spec.channel;c.name=port_prefix+name;spec.channel=c
        signatures={port_prefix+name:sig for name,sig in signatures.items()}
        for branch in branches:
            for key in('first_port','second_port','cleanup_port'):
                if branch[key] is not None:branch[key]=port_prefix+branch[key]
        for query in queries:query['ports']={key:port_prefix+name for key,name in query['ports'].items()}
    recipe=d.OrganizationRecipe.research(n,[],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);recipe.interfaces=interfaces
    g={'schema':'CPC8R.mode_reference.geometry.v2' if cleanup else 'CPC8R.mode_reference.geometry.v1','N':n,'reference_hub':h,'queries':queries,'branches':branches,'signatures':signatures,'other_hub':aux,'cleanup':cleanup,'port_prefix':port_prefix,
        'resources':{'initial_material':0,'interfaces':len(interfaces),'base_buffer_bytes':32*n**3,'normalizer_packets_logical':2*len(branches)},
        'prepared':'Fixed physical comparator, redundant source direction representation and branch-normalization apparatus. The general rule of similarity is not claimed acquired.',
        'acquired':'Actual reference directiona comes only from an admitted object experience. New carrierb is not accompanied by a correct-match label or teaching exposure.',
        'identity_scope':'Shared operational Y-motion component, not identity of a persistent referent.',
        'generalization_scope':'Different new physical carriers in the SAME MAIN after initial reference experience; no new reference/object pairing or feedback on match.'}
    recipe.options={'CPC8R.mode_reference.geometry':encode_metadata(g)}
    org=d.OrganizationSpec();org.id='MODE_REFERENCE';org.recipe_id='CPC8R.mode_reference.v1';org.ports={'reference':d.Coordinate(*h),'other':d.Coordinate(*aux)};recipe.organizations=[org]
    return recipe,g
class ModeReferenceSession:
    def __init__(self,w,g,state=None):self.world=w;self.geometry=deepcopy(g);self.state=deepcopy(state) if state is not None else{'requests':[],'captures':[],'aliases':[]}
    @classmethod
    def create(cls,**kw):r,g=prepare_geometry(**kw);return cls(d.OrganizationalWorld.create(r),g)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,port,payload,tick,origin,kind='submit'):
        if type(payload) is not int or not 0<=payload<=65535 or type(tick) is not int or tick<self.tick:raise ValueError('Exact current/future request required')
        if port not in self.geometry['signatures']:port=self.geometry.get('port_prefix','')+port
        r=getattr(self.world,kind)(port,payload,tick);self.state['requests'].append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'origin':origin,'kind':kind,'call_tick':self.tick});return exact_receipt(r)
    def acquire_reference(self,a,mode='paired',load=11):
        if a not in(-1,1) or mode not in('paired','unpaired','virgin'):raise ValueError('Reference experience domain')
        if mode!='virgin':self.input('reference.object.'+('plus' if a>0 else'minus'),load,0,'ACTUAL_REFERENCE_OBJECT_DIRECTION')
        self.input('reference.record',0,int(mode=='unpaired'),'UNCONDITIONAL_ZERO_LOAD_RECORDING_INTERACTION_NOT_WORD')
    def prepare_normalizers(self,stages=(1,2)):
        seen={}
        for b in self.geometry['branches']:
            if b['stage'] not in stages:continue
            for which in(('first','second','cleanup') if self.geometry.get('cleanup') else ('first','second')):
                port=b[which+'_port'];tick=b[which+'_tick']-(1 if which=='cleanup' else 3);sig=self.geometry['signatures'][port];key=(tuple(sig[0]),tuple(sig[1]),sig[2],sig[3],tick,0)
                if key in seen:self.state['aliases'].append({'port':port,'same_physical_request_as':seen[key],'criterion':'Declared site/direction/state/semantic/tick/payload only; no RAW/state inspection'})
                else:self.input(port,0,tick,'FIXED_ALL_CANDIDATE_NORMALIZATION_RESOURCE');seen[key]=port
    def query_object(self,stage,b,payload):
        if stage not in(1,2) or b not in(-1,1):raise ValueError('Current new object domain')
        for q in self.geometry['queries']:
            if q['stage']==stage:self.input(q['ports'][str(b)],payload,q['parent']['query_tick']-3,'CURRENT_OBJECT_DIRECTION_NOT_MATCH_TARGET')
    def acquire_other(self,v):
        if v not in(-1,1):raise ValueError('Actual other event')
        self.input('other.signal',5,110,'ADDITIONAL_OPAQUE_CUE')
        self.input('other.event.'+('plus' if v>0 else'minus'),11,110,'ADDITIONAL_CURRENT_EVENT')
        self.input('other.signal',9,177,'QUERY_ADDITIONAL_RELATION','probe')
    def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
    def capture(self,tick):
        for q in self.geometry['queries']:
            if q['parent']['query_tick']!=tick:continue
            r=self.observe(q['parent']['hub']);v=r['direction'];covered=r['active'] and r['semantic']==1 and v[0] in(-1,1) and v[2]==1 and v[1] in(0,v[0])
            self.state['captures'].append({'tick':tick,'stage':q['stage'],'parent_route':q['parent']['id'],'physical':r,'covered':covered,
                'relation':('DIFFERENT_MODE' if v[1]==0 else'LIKE_REFERENCE_MODE') if covered else None,
                'provenance':'ENTE_NATIVE_COMPARISON_MARKER; decoder does not inspect reference/query teaching values'})
    def run_until(self,tick):
        critical={3,110,180};critical.update(q['parent']['query_tick'] for q in self.geometry['queries']);critical.update(b[k] for b in self.geometry['branches'] for k in('first_tick','second_tick'))
        for t in sorted(x for x in critical if self.tick<x<=tick):self.world.run_until(t);self.capture(t)
        self.world.run_until(tick)
    def receipts(self):return [{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))} for r in self.state['requests']]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,proof=load_world_snapshot(path,max_bytes=1024**3);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY]);
        if m['tick']!=int(w.runtime.current_tick) or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Mode-reference snapshot mismatch')
        return cls(w,m['geometry'],m['state'])
