"""Fresh N67 order/contact preparation with a native common-use encounter.

New adaptation: temporal source wasN131; contact wasN67/ticks2..4. This
candidate revalidates both atN67/contact5, without historical imports or states.
All candidate paths and interfaces are defined before current experiences.
"""
from array import array
from copy import deepcopy
import hashlib
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC8R.relational_pair.session.v1'


def move(q,v,k=1,n=67):return[(q[i]+v[i]*k)%n for i in range(3)]
def physical(w):
    r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def prepare(*,actor_mode='contact',include_order=True,include_contact=True,event_state_offset=0,medium_load=1,actor_state=1):
    if actor_mode not in('contact','offpath','omitted')or event_state_offset not in(0,100,400)or medium_load not in(1,3,5)or actor_state not in(1,17):raise ValueError('Frozen candidate parameters')
    n=67;c=[20,35,20];a=move(c,(-1,0,0));b=move(c,(1,0,0));origin=move(c,(0,-1,0));initial=[];interfaces=[]
    def put(q,state,load,semantic,clock,role,v=(0,0,0)):
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,*v,semantic);p.clock=clock;p.role=role;initial.append(p)
    def port(name,q,v,state=1):
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*q);ch.direction=d.Direction(*v);ch.state=state;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;interfaces.append(p)
    if include_order:
        put(a,1000,100,1,260,'Fresh relative body A');put(b,2000,100,1,260,'Fresh relative body B')
        patterns=((a,((-1,0,0),(-1,1,1),(0,0,1),(0,1,0)),3000,31),(b,((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0)),4000,41))
        for q,pattern,state,clock in patterns:
            for i,v in enumerate(pattern):put(move(q,v),state+i,0,4,clock+i,'Prepared relative guide')
        put(move(c,(0,0,1)),6100,0,4,19,'Prepared source0')
    port('order.A',move(a,(0,-1,0)),(0,-1,0),5000+event_state_offset);port('order.B',move(b,(0,1,0)),(0,1,0),5001+event_state_offset)
    port('order.read',origin,(0,1,0));order={}
    for sign,label in((-1,'minus'),(1,'plus')):
        hub=move(origin,(sign,-1,0),6);target=move(hub,(sign,-1,1),20)
        port('order.name.'+label,move(hub,(0,0,1),-3),(0,0,1));port('order.query.'+label,move(target,(0,0,1),-3),(0,0,1))
        if include_order:put(move(hub,(0,0,1),8),1,0,4,0,'Prepared unused temporal cue interception')
        order[label]={'axis':sign,'hub':hub,'query_site':target,'name_port':'order.name.'+label,'query_port':'order.query.'+label}
    # After two6-tick contact query/use circuits: X shifts4-6-6=-8.
    base=move(origin,(8,0,-6));join=move(base,(0,0,-1));contact={}
    if include_contact:
        actor=move(join,(1,0,0),-4)
        if actor_mode=='offpath':actor=move(actor,(0,1,0),12)
        if actor_mode!='omitted':put(actor,actor_state,0,1,0,'Current zero-load actuator',(1,0,0))
        put(move(join,(-1,0,1),-4),1,0,1,0,'Common zero-load opportunity',(-1,0,1))
        put(move(base,(1,1,-1),-5),1,medium_load,1,0,'Current medium',(1,1,-1))
    for axis,label in((-1,'left'),(1,'right')):
        for z,kind in((0,'changed'),(-1,'free')):
            key=label+'.'+kind;hub=move(base,(axis,1,z),4);cue=(-axis,0,0);q=hub;effect=move(q,(-axis,1,z),6)
            renewed=move(q,(-axis,0,0),6);renewed_effect=move(renewed,(-axis,1,z),6)
            for role,target,vector,lead in(('name',hub,cue,3),('query',q,cue,3),('use',effect,(axis,0,0),3),('renew',renewed,cue,1),('reuse',renewed_effect,(axis,0,0),3)):
                port('contact.'+role+'.'+key,move(target,vector,-lead),vector)
            contact[key]={'axis':axis,'consequence_z':z,'hub':hub,'query_site':q,'effect_site':effect,'renewed_site':renewed,'renewed_effect':renewed_effect,
                'name_port':'contact.name.'+key,'query_port':'contact.query.'+key,'use_port':'contact.use.'+key,'renew_port':'contact.renew.'+key,'reuse_port':'contact.reuse.'+key}
    common=move(origin,(0,0,-6));names={}
    for sign,label in((-1,'minus'),(1,'plus')):
        for z,kind in((0,'free'),(1,'changed')):
            key=label+'.'+kind;v=(sign,0,z);use=move(common,v,4);delivery=move(use,(sign,1,z),4);cue=(-sign,0,-z)
            port('joint.use.'+key,move(use,(0,1,0),-3),(0,1,0));port('joint.name.'+key,move(delivery,cue,-3),cue)
            port('joint.query.'+key,move(delivery,(0,0,1),-3),(0,0,1))
            names[key]={'order_axis':sign,'consequence_component':z,'use_site':use,'delivery_site':delivery,'name_port':'joint.name.'+key,'query_port':'joint.query.'+key,'use_port':'joint.use.'+key}
    aux=[52,12,45];port('extra.signal',move(aux,(-1,0,0),-3),(-1,0,0))
    for sign,label in((-1,'minus'),(1,'plus')):port('extra.event.'+label,move(aux,(1,sign,0),-3),(1,sign,0))
    sites=[(p.site.x,p.site.y,p.site.z)for p in initial]
    if len(sites)!=len(set(sites)):raise ValueError('Initial material collision in fresh geometry')
    if len({p.name for p in interfaces})!=len(interfaces):raise ValueError('Duplicate interface name')
    g={'schema':'CPC8R.relational_pair.geometry.v1','N':n,'body':{'center':c,'A':a,'B':b,'emission':origin},'order':order,'contact_base':base,'contact_join':join,'contact':contact,
        'common_join':common,'joint_names':names,'auxiliary_hub':aux,'ticks':{'order_emission':5,'order_association':11,'order_queries':[31,165],
            'contact':5,'contact_association':9,'contact_queries':[76,143],'contact_uses':[82,149],'extra_acquisition':100,'extra_query':170,
            'common_join':206,'common_use':210,'joint_name':214,'joint_query':281},
        'resources':{'initial_material_sites':len(initial),'interfaces':len(interfaces),'basic_buffer_bytes':32*n**3},
        'modality':'Fresh singleRuntime research geometry; native preservation of orderX and contactZ, followed by native common use. No previously trained body or lookup table.',
        'adaptation':'Order reference wasN131; thisN67/contact5 preparation and its coupling are new and require their own controls. Fixed guards, readers, cues and resource opportunities are prepared, not learned policies.'}
    r=d.OrganizationRecipe.research(n,initial,0);r.execution=d.TickOptions(d.Backend.LAZY,1);r.interfaces=interfaces;r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};r.domain=g['modality']
    org=d.OrganizationSpec();org.id='RELATIONAL_PAIR';org.recipe_id='CPC8R.relational_pair.v1';org.ports={k:d.Coordinate(*v)for k,v in g['body'].items()};r.organizations=[org]
    return r,g


class PairSession:
    def __init__(self,w,g,state=None,identifier='PAIR'):
        self.world=w;self.geometry=deepcopy(g);self.state=deepcopy(state)if state is not None else{'requests':[],'captures':[]};self.identifier=identifier
    @classmethod
    def create(cls,identifier='PAIR',**options):r,g=prepare(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,port,payload,tick,kind='submit',origin='DECLARED_CURRENT_INPUT'):
        if type(tick)is not int or tick<self.tick or type(payload)is not int or not 0<=payload<=65535:raise ValueError('Invalid exact input')
        r=getattr(self.world,kind)(port,payload,tick);self.state['requests'].append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'kind':kind,'origin':origin,'call_tick':self.tick});return exact_receipt(r)
    def curriculum(self,*,order='AB',order_name='paired',contact_name='paired',joint_name='paired',include_order=True,include_contact=True,extra_value=1):
        if self.tick!=0 or order not in('AB','BA')or extra_value not in(-1,1):raise ValueError('Fresh declared curriculum required')
        for mode in(order_name,contact_name,joint_name):
            if mode not in('paired','unpaired','omitted'):raise ValueError('Explicit cue condition')
        if include_order:
            self.input('order.'+order[0],3,0,origin='FIRST_CURRENT_EVENT');self.input('order.'+order[1],3,1,origin='SECOND_CURRENT_EVENT');self.input('order.read',7,2,'probe','COMMON_ORDER_READER')
            for p in self.geometry['order'].values():
                if order_name!='omitted':self.input(p['name_port'],5,8+int(order_name=='unpaired'),origin='POST_ORDER_OPAQUE_CUE')
                for tick in(28,162):self.input(p['query_port'],7,tick,'probe','FIXED_PRESERVING_ORDER_QUERY')
        if include_contact:
            for p in self.geometry['contact'].values():
                if contact_name!='omitted':self.input(p['name_port'],5,6+int(contact_name=='unpaired'),origin='POST_CONTACT_OPAQUE_CUE')
                self.input(p['query_port'],5,73,'probe','CONTACT_SIGNAL_QUERY');self.input(p['use_port'],7,79,'probe','FIXED_CONTACT_USE_RESOURCE')
                self.input(p['renew_port'],5,142,'probe','RENEWED_CONTACT_QUERY');self.input(p['reuse_port'],7,146,'probe','FIXED_SECOND_CONTACT_USE_RESOURCE')
        self.input('extra.signal',5,100,origin='ADDITIONAL_RELATION_CUE');self.input('extra.event.'+('plus'if extra_value==1 else'minus'),11,100,origin='ADDITIONAL_CURRENT_EVENT');self.input('extra.signal',9,167,'probe','ADDITIONAL_RELATION_QUERY')
        for p in self.geometry['joint_names'].values():
            self.input(p['use_port'],7,207,'probe','ALL_CANDIDATE_COMMON_USE_OPPORTUNITIES')
            if joint_name!='omitted':self.input(p['name_port'],5,211+int(joint_name=='unpaired'),origin='LATER_ALL_CANDIDATE_JOINT_OPAQUE_CUE')
            self.input(p['query_port'],7,278,'probe','ALL_CANDIDATE_JOINT_SIGNAL_QUERY')
    def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
    def view(self):
        g=self.geometry
        return{'tick':self.tick,'body':{k:self.observe(q)for k,q in g['body'].items()},'order':{k:{f:self.observe(p[f])for f in('hub','query_site')}for k,p in g['order'].items()},
            'contact_base':self.observe(g['contact_base']),'contact':{k:{f:self.observe(p[f])for f in('hub','query_site','effect_site','renewed_site','renewed_effect')}for k,p in g['contact'].items()},
            'common_join':self.observe(g['common_join']),'joint':{k:{f:self.observe(p[f])for f in('use_site','delivery_site')}for k,p in g['joint_names'].items()},'extra':self.observe(g['auxiliary_hub'])}
    def run_until(self,tick):
        if type(tick)is not int or tick<self.tick:raise ValueError('Monotone ticks required')
        self.world.run_until(tick);return self.view()
    def receipts(self):return[{**x,'receipt':exact_receipt(self.world.runtime.receipt(x['id']))}for x in self.state['requests']]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'identifier':self.identifier,'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(w.runtime.current_tick)or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Stored operational mismatch')
        return cls(w,m['geometry'],m['state'],m['identifier'])
