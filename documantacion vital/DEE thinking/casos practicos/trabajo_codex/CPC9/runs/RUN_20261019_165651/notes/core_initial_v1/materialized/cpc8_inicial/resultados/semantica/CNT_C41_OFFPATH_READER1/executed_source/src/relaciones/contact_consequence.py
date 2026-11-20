"""Native zero-load intervention -> medium consequence -> later opaque memory.

No Python sensor computes contact. An actor and an opportunity produce a real
carrier, which meets the current medium. Two direction components conserve the
measured consequence. Fixed all-candidate cues/readers act only after contact.
"""
from copy import deepcopy
from array import array
import hashlib
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
KEY='CPC8.contact_consequence.session.v1'
def move(q,v,k=1,n=67):return [(q[i]+v[i]*k)%n for i in range(3)]
def physical(w):
    r=w.runtime;return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def build(*,mode='contact',medium_direction=1,medium_load=1,contact_tick=2,actor_direction=1,actor_state=1,query_offset=0,association_mode='instrumental',use_gap=4,renew_lead=3):
    if mode not in('contact','omitted','offpath') or medium_direction not in(-1,1) or actor_direction not in(-1,1):raise ValueError('Frozen contact preparation')
    if contact_tick not in(2,3,4) or medium_load not in(1,3,5) or actor_state not in(1,17) or query_offset not in(0,4):raise ValueError('Frozen contact domain')
    if association_mode not in('instrumental','same_cue'):raise ValueError('Declared contact association/readout family')
    if type(use_gap) is not int or use_gap not in(4,6):raise ValueError('Two frozen material-use geometries')
    if type(renew_lead) is not int or renew_lead not in(1,3):raise ValueError('Frozen renewed-reader launch lead')
    n=67;base=[30,30,30];join=move(base,(0,0,-1));teach=contact_tick+4;read=teach+n+query_offset;use=read+use_gap;delivery=use+4
    initial=[];interfaces=[]
    def put(q,load,v,role,state=1,semantic=1):
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(state,load,*v,semantic);p.clock=0;p.role=role;initial.append(p)
    def port(name,q,v):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        i=d.InterfaceSpec();i.name=name;i.channel=c;interfaces.append(i)
    actor=move(join,(actor_direction,0,0),-(contact_tick-1))
    if mode=='offpath':actor=move(actor,(0,1,0),12)
    if mode!='omitted':put(actor,0,(actor_direction,0,0),'Current zero-load actuator',actor_state)
    put(move(join,(-actor_direction,0,1),-(contact_tick-1)),0,(-actor_direction,0,1),'Common zero-load opportunity')
    put(move(base,(medium_direction,1,-1),-contact_tick),medium_load,(medium_direction,1,-1),'Current physical medium, not a target class')
    parts={}
    for c,label in((-1,'left'),(1,'right')):
        for z,kind in((0,'changed'),(-1,'free')):
            same=association_mode=='same_cue';key=label+'.'+kind;hub=move(base,(c,1,z),4);cue=(-c,0,0) if same else(-c,0,1);memory=(0,1,z) if same else(0,1,z+1)
            reader=cue if same else(-1,0,0);response=(-c,1,z) if same else(-1,1,z+1);resource=(c,0,0) if same else(0,0,-1);after=(0,1,z) if same else(-1,1,z)
            q=move(hub,memory,n+query_offset);effect=move(q,response,use_gap);target=move(effect,after,4)
            port('contact.name.'+key,move(hub,cue,-3),cue)
            port('contact.query.'+key,move(q,reader,-3),reader)
            port('contact.use.'+key,move(effect,resource,-3),resource)
            renewed=move(q,(-c,0,0) if same else(0,0,1),use_gap);renewed_effect=move(renewed,response,use_gap)
            port('contact.renew.'+key,move(renewed,cue if same else(-1,0,1),-renew_lead),cue if same else(-1,0,1))
            port('contact.reuse.'+key,move(renewed_effect,resource,-3),resource)
            parts[key]={'hub':hub,'memory_direction':list(memory),'cue_direction':list(cue),'query_site':q,'effect_site':effect,'delivery_site':target,
                'medium_axis':c,'native_consequence_component':z,'query_direction':list(reader),'resource_direction':list(resource),
                'renewed_site':renewed,'renewed_effect':renewed_effect,'renewed_delivery':move(renewed_effect,after,4),
                'name_port':'contact.name.'+key,'query_port':'contact.query.'+key,'use_port':'contact.use.'+key,'renew_port':'contact.renew.'+key,'reuse_port':'contact.reuse.'+key}
    aux=[52,15,9];port('new.signal',move(aux,(-1,0,0),-3),(-1,0,0))
    for v,label in((-1,'minus'),(1,'plus')):port('new.event.'+label,move(aux,(1,v,0),-3),(1,v,0))
    recipe=d.OrganizationRecipe.research(n,initial,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);recipe.interfaces=interfaces
    g={'schema':'CPC8.contact_consequence.geometry.v1','N':n,'contact':base,'actor_opportunity_join':join,'parts':parts,'auxiliary_hub':aux,'association_mode':association_mode,'use_gap':use_gap,'renew_lead':renew_lead,
        'ticks':{'contact':contact_tick,'before_contact':contact_tick-1,'teaching':teach,'teaching_input':teach-3,'query':read,'query_input':read-3,'effect':use,'effect_input':use-3,'delivery':delivery,
                 'renewed_query':read+n,'renewed_input':read+n-renew_lead,'renewed_effect':use+n,'renewed_effect_input':use+n-3,'renewed_delivery':delivery+n,'new_acquisition':90,'new_query_input':157,'new_query':160},
        'resources':{'initial_material':len(initial),'interfaces':len(interfaces),'basic_buffer_bytes':32*n**3},
        'preparation_scope':'Fixed local actor/opportunity/medium apparatus. Actor identity is its causal role and path, not a learned personal pronoun. All outcome routes have fixed cues/readers beforeT0.',
        'acquisition_scope':'Post-encounter product itself meets the later cue. Decoder examines native vectors; no host bit contact/target/utility is injected.',
        'audit_separation':'Actual scenario mode/medium sign/actor choice remain in the external case/config, not in this operational geometry.'}
    recipe.options={'CPC8.contact_consequence.geometry':encode_metadata(g)}
    org=d.OrganizationSpec();org.id='CONTACT_LEARNER';org.recipe_id='CPC8.contact_consequence.v1';org.ports={'contact':d.Coordinate(*base),'actor_join':d.Coordinate(*join)};recipe.organizations=[org]
    return recipe,g
class ContactSession:
    def __init__(self,w,g,state=None):self.world=w;self.geometry=deepcopy(g);self.state=deepcopy(state) if state is not None else{'requests':[],'captures':[]}
    @classmethod
    def create(cls,**kw):r,g=build(**kw);return cls(d.OrganizationalWorld.create(r),g)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,port,payload,tick,kind='submit',origin='USER'):
        r=getattr(self.world,kind)(port,payload,tick);self.state['requests'].append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'kind':kind,'origin':origin,'call_tick':self.tick});return exact_receipt(r)
    def teach(self,mode='paired',payload=5):
        if mode not in('paired','unpaired','omitted'):raise ValueError('Name association condition')
        if mode!='omitted':
            for p in self.geometry['parts'].values():self.input(p['name_port'],payload,self.geometry['ticks']['teaching_input']+int(mode=='unpaired'),origin='POST_EXPERIENCE_OPAQUE_CUE_ALL_CANDIDATES')
    def query(self,payload=7,use_payload=7,repeat=False):
        t=self.geometry['ticks']
        self.state['query_repeat_requested']=bool(repeat)
        for p in self.geometry['parts'].values():
            self.input(p['query_port'],payload,t['query_input'],'probe','OPAQUE_CUE_ONLY_QUERY')
            self.input(p['use_port'],use_payload,t['effect_input'],'probe','COMMON_MATERIAL_TEST_RESOURCE')
            if repeat:
                self.input(p['renew_port'],payload,t['renewed_input'],'probe','RENEWED_ALL_CANDIDATE_ACCESS_AFTER_ADDITIONAL_EXPERIENCE')
                self.input(p['reuse_port'],use_payload,t['renewed_effect_input'],'probe','SECOND_COMMON_MATERIAL_TEST_RESOURCE')
    def acquire_other(self,value=1):
        if value not in(-1,1):raise ValueError('Actual new event')
        self.input('new.signal',5,90,origin='NEW_OPAQUE_EXPERIENCE')
        self.input('new.event.'+('plus' if value>0 else'minus'),11,90,origin='NEW_CURRENT_DIRECTIONAL_EVENT')
        self.input('new.signal',9,157,'probe','QUERY_ADDITIONAL_RELATION')
    def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
    def record(self,stage):
        t=self.geometry['ticks'];fields={'query':'query_site','effect':'effect_site','delivery':'delivery_site','renewed_query':'renewed_site','renewed_effect':'renewed_effect','renewed_delivery':'renewed_delivery'}
        observations={k:self.observe(p[fields[stage]]) for k,p in self.geometry['parts'].items()};decoded=[];seen=set()
        same=self.geometry.get('association_mode')=='same_cue'
        expected=(-1,0) if same else(0,1) if stage in('query','renewed_query') else(-1,0)
        for key,r in observations.items():
            v=r['direction']
            dx_valid=v[0] in(-1,1) if same and stage in('query','renewed_query') else v[0]==0 if same else v[0]==-1
            if r['active'] and r['semantic']==1 and dx_valid and v[1]==1 and v[2] in expected and tuple(r['site']) not in seen:
                seen.add(tuple(r['site']));decoded.append({'location':key,'consequence_component':v[2],'physical':r})
        self.state['captures'].append({'tick':self.tick,'stage':stage,'requested':not stage.startswith('renewed') or self.state.get('query_repeat_requested',False),'observations':observations,'decoded':decoded,'provenance':'ENTE_NATIVE_DIRECTION_COMPONENT'})
    def run_until(self,tick):
        t=self.geometry['ticks'];critical={t['before_contact'],t['contact'],t['teaching']-1,t['teaching'],90,160};critical.update(t[k] for k in('query','effect','delivery','renewed_query','renewed_effect','renewed_delivery'))
        for q in sorted(v for v in critical if self.tick<v<=tick):
            self.world.run_until(q)
            for stage in('query','effect','delivery','renewed_query','renewed_effect','renewed_delivery'):
                if t[stage]==q:self.record(stage)
        self.world.run_until(tick)
    def receipts(self):return [{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))} for r in self.state['requests']]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'state':self.state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}));return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,proof=load_world_snapshot(path,max_bytes=1024**3);v=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY]);
        if v['tick']!=int(w.runtime.current_tick) or v['channels']!=sorted(w.runtime.channel_names):raise ValueError('Contact snapshot operational mismatch')
        return cls(w,v['geometry'],v['state'])
