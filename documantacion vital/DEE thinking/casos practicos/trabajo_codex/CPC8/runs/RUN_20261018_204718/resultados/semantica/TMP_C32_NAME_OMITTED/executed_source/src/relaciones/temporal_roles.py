"""Native event-order acquisition, later opaque cue and prepared role queries.

The evaluator never injects an order bit. Actual A/B sensory events, a common
reader, opaque paired pulses and fixed all-candidate opportunities are inputs.
The inverse-role operator is designer-prepared; its rule is not claimed learned.
"""
from copy import deepcopy
from array import array
import hashlib
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot

KEY='CPC8.temporal_roles.session.v1'
def move(q,v,k=1,n=131):return [(q[i]+v[i]*k)%n for i in range(3)]
def physical(w):
    r=w.runtime
    return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}

def prepare(*,gap=1,event_state_offset=0,query_delay=20,reader_mode='format',guard_mode='none'):
    if gap not in(1,2,3) or event_state_offset not in(0,100,400) or query_delay not in(20,23):raise ValueError('Frozen finite temporal domain')
    if reader_mode not in('format','preserve'):raise ValueError('Frozen temporal reader family')
    if guard_mode not in('none','cue','sham'):raise ValueError('Frozen unused-cue regulator family')
    n=131;c=[35,70,70];a=move(c,(-1,0,0));b=move(c,(1,0,0));origin=move(c,(0,-1,0));placements=[];ports=[]
    def put(q,state,load,semantic,clock,role):
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,0,0,0,semantic);p.clock=clock;p.role=role;placements.append(p)
    def port(name,q,v,state=1):
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*q);ch.direction=d.Direction(*v);ch.state=state;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;ports.append(p)
    put(a,1000,100,1,260,'Fresh relative order body A');put(b,2000,100,1,260,'Fresh relative order body B')
    pa=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0));pb=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))
    for q,pattern,state,clock in((a,pa,3000,31),(b,pb,4000,41)):
        for i,v in enumerate(pattern):put(move(q,v),state+i,0,4,clock+i,'Prepared asymmetric local guide')
    put(move(c,(0,0,1)),6100,0,4,19,'Fresh source0 declaration')
    port('event.A',move(a,(0,-1,0)),(0,-1,0),5000+event_state_offset)
    port('event.B',move(b,(0,1,0)),(0,1,0),5001+event_state_offset)
    port('order.read',origin,(0,1,0))
    emission=gap+4;teach=emission+6;read=teach+query_delay;role_read=read+n;lanes={}
    for s,label in((-1,'minus'),(1,'plus')):
        hub=move(origin,(s,-1,0),6);cue=(0,0,1);q=move(hub,(s,-1,1),query_delay)
        after_role=move(q,(0,-1,1),4)
        port('name.'+label,move(hub,cue,-3),cue)
        reader=(0,1,0) if reader_mode=='format' else(0,0,1)
        port('query.'+label,move(q,reader,-3),reader)
        port('roles.first.'+label,move(q,(-s,-1,0),-3),(-s,-1,0))
        port('roles.second.'+label,move(after_role,(-s,1,0),-3),(-s,1,0))
        lanes[label]={'axis':s,'teaching_hub':hub,'query_site':q,'role_normalizer_site':after_role,
            'teach_port':'name.'+label,'query_port':'query.'+label,'role_first_port':'roles.first.'+label,'role_second_port':'roles.second.'+label}
    guards=[]
    if guard_mode!='none':
        for label,p in lanes.items():
            q=move(p['teaching_hub'],(0,0,1),8)
            if guard_mode=='sham':q=move(q,(0,1,0),12)
            put(q,1,0,4,0,'Prepared unused opaque cue interception '+label)
            guards.append({'site':q,'semantic':4,'load':0,'clock':'0','role':'BOTH_LANES_UNUSED_CUE_NOT_TRANSFORMED_BY_EXPERIENCE'})
    aux=[90,90,10]
    port('new.signal',move(aux,(-1,0,0),-3),(-1,0,0))
    for v,label in((-1,'minus'),(1,'plus')):port('new.event.'+label,move(aux,(1,v,0),-3),(1,v,0))
    r=d.OrganizationRecipe.research(n,placements,0);r.execution=d.TickOptions(d.Backend.LAZY,1);r.interfaces=ports
    g={'schema':'CPC8.temporal_roles.geometry.v1','N':n,'body':{'center':c,'A':a,'B':b,'emission':origin},'lanes':lanes,'auxiliary_hub':aux,
       'gap':gap,'event_state_offset':event_state_offset,'query_delay':query_delay,'reader_mode':reader_mode,'guard_mode':guard_mode,'guards':guards,
       'ticks':{'reader_input':gap+1,'emission':emission,'teach':teach,'teach_input':teach-3,'query':read,'query_input':read-3,'role_first':role_read,'role_second':role_read+4,'auxiliary_experience':100,'auxiliary_query_input':231,'auxiliary_query':234},
       'prepared':'Relative asymmetric body, fixed all-candidate cue paths and inverse-role operator. New states are actual sensory packet changes, not answer labels.',
       'acquired':'Event order changes body by actual event experiences. The later cue-to-mobile-response path requires physical pairing. The inverse role transformation is prepared, not learned grammar.',
       'resources':{'initial_material':len(placements),'interfaces':len(ports),'buffer_estimate':32*n**3}}
    r.options={'CPC8.temporal_roles.geometry':encode_metadata(g)};r.domain=g['prepared']+' '+g['acquired']
    org=d.OrganizationSpec();org.id='TEMPORAL_ROLES';org.recipe_id='CPC8.temporal_roles.v1';org.ports={k:d.Coordinate(*v) for k,v in g['body'].items()};r.organizations=[org]
    return r,g

class TemporalSession:
    def __init__(self,w,g,state=None,identifier='TEMPORAL'):
        self.world=w;self.geometry=deepcopy(g);self.state=deepcopy(state) if state is not None else{'requests':[],'captures':[]};self.identifier=identifier
    @classmethod
    def create(cls,**kw):
        identifier=kw.pop('identifier','TEMPORAL');r,g=prepare(**kw);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,port,payload,tick,kind='submit',origin='EXPLICIT_INPUT'):
        if type(tick) is not int or tick<self.tick or type(payload) is not int or not 0<=payload<=65535:raise ValueError('Invalid exact input')
        r=getattr(self.world,kind)(port,payload,tick);self.state['requests'].append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'kind':kind,'origin':origin,'call_tick':self.tick});return exact_receipt(r)
    def events(self,order,event_load=3):
        if self.tick!=0 or order not in('AB','BA'):raise ValueError('Fresh events required')
        self.input('event.'+order[0],event_load,0,origin='ACTUAL_FIRST_SENSORY_EVENT')
        self.input('event.'+order[1],event_load,self.geometry['gap'],origin='ACTUAL_SECOND_SENSORY_EVENT')
        self.input('order.read',7,self.geometry['ticks']['reader_input'],'probe','COMMON_READER_NOT_ORDER_BIT')
    def teach(self,mode='paired',payload=5):
        if mode not in('paired','unpaired','omitted'):raise ValueError('Declared temporal name condition')
        if mode!='omitted':
            for p in self.geometry['lanes'].values():self.input(p['teach_port'],payload,self.geometry['ticks']['teach_input']+int(mode=='unpaired'),origin='OPAQUE_EQUAL_CANDIDATE_CUES_AFTER_ORDER_EXPERIENCE')
    def query(self,payload=7,role_inverse=True,repeat_preserving=False):
        t=self.geometry['ticks']
        self.state['query_mode']={'role_inverse':bool(role_inverse),'repeat_preserving':bool(repeat_preserving)}
        for p in self.geometry['lanes'].values():
            self.input(p['query_port'],payload,t['query_input'],'probe','OPAQUE_SIGNAL_ONLY_ALL_CANDIDATES')
            if repeat_preserving:
                if self.geometry.get('reader_mode')!='preserve' or role_inverse:raise ValueError('Preserving repeat has its own frozen reader, without inverse operator')
                self.input(p['query_port'],payload,t['query_input']+131,'probe','SAME_OPAQUE_QUERY_AFTER_NEW_EXPERIENCE_NO_RETEACHING')
            if role_inverse:
                self.input(p['role_first_port'],payload,t['role_first']-3,'probe','PREPARED_INVERSE_ROLE_ACCESS')
                self.input(p['role_second_port'],payload,t['role_second']-3,'probe','PREPARED_INVERSE_ROLE_NORMALIZER')
    def acquire_new(self,value=1,payload=11):
        if type(value) is not int or value not in(-1,1):raise ValueError('Current consequence sign')
        self.input('new.signal',5,100,origin='ADDITIONAL_OPAQUE_CUE_AFTER_OLD_USE')
        self.input('new.event.'+('plus' if value>0 else'minus'),payload,100,origin='ADDITIONAL_CURRENT_EVENT_AFTER_OLD_USE')
        self.input('new.signal',9,231,'probe','ADDITIONAL_RELATION_RETENTION_QUERY')
    def observe(self,site):return exact_observation(self.world.runtime.observe(d.Coordinate(*site)))
    def capture(self):
        t=self.geometry['ticks'];now=self.tick;g=self.geometry;rows={};decoder='none';decoded=[]
        if now==t['emission']:rows={'emission':self.observe(g['body']['emission'])};decoder='native_order_emission'
        elif now in(t['teach']-1,t['teach']):rows={k:self.observe(p['teaching_hub']) for k,p in g['lanes'].items()}
        elif now==t['role_first'] and g.get('reader_mode')=='preserve':
            rows={k:self.observe(p['query_site']) for k,p in g['lanes'].items()};decoder='retained_order_direction'
        elif now==t['role_second'] and not self.state.get('query_mode',{}).get('role_inverse',True):
            rows={k:self.observe(p['role_normalizer_site']) for k,p in g['lanes'].items()};decoder='not_requested_inverse_role_window'
        elif now==t['query'] or now==t['role_second']:
            key='query_site' if now==t['query'] else'role_normalizer_site';rows={k:self.observe(p[key]) for k,p in g['lanes'].items()};decoder='first_event_direction' if now==t['query'] else'inverse_role_direction'
        elif now==t['role_first']:rows={k:self.observe(p['query_site']) for k,p in g['lanes'].items()}
        elif now==234:rows={'additional':self.observe(g['auxiliary_hub'])};decoder='additional_relation_direction'
        for key,r in rows.items():
            v=r['direction'];valid=r['active'] and r['semantic']==1
            if decoder=='native_order_emission':valid=valid and v[0] in(-1,1) and v[1:]==[-1,0]
            elif decoder in('first_event_direction','inverse_role_direction','retained_order_direction'):
                expected_y=-1 if g.get('reader_mode')=='preserve' else 0
                valid=valid and v[0] in(-1,1) and v[1:]==[expected_y,1]
            elif decoder=='additional_relation_direction':valid=valid and v[0]==-1 and v[1] in(-1,1) and v[2]==0
            else:valid=False
            if valid:decoded.append({'location':key,'value':v[1] if decoder=='additional_relation_direction' else v[0],'physical':r})
        out={'tick':now,'decoder':decoder,'observations':rows,'decoded':decoded,'provenance':'ENTE' if decoder!='none' else'INSTRUMENTO'}
        self.state['captures'].append(out);return out
    def run_until(self,tick):
        if type(tick) is not int or tick<self.tick:raise ValueError('Monotone tick')
        t=self.geometry['ticks'];critical={t['emission'],t['teach']-1,t['teach'],t['query'],99,100,t['role_first'],t['role_second'],234}
        for boundary in sorted(v for v in critical if self.tick<v<=tick):self.world.run_until(boundary);self.capture()
        self.world.run_until(tick)
    def receipts(self):return [{**deepcopy(x),'receipt':exact_receipt(self.world.runtime.receipt(x['id']))} for x in self.state['requests']]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'identifier':self.identifier,'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,proof=load_world_snapshot(path,max_bytes=1024**3);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(w.runtime.current_tick) or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Invalid temporal state')
        return cls(w,m['geometry'],m['state'],m['identifier'])
