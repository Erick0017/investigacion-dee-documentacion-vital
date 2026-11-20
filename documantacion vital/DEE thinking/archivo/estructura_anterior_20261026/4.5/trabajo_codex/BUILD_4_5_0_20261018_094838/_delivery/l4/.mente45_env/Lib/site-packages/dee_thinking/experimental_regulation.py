"""EXPERIMENTAL finite CPC5 acquired-direction regulator, N67/T0..437.

Python prepares declared geometry and queues the finite external experiences.
All communication, acquisition, occupied-destination contact and consequences
are evolved by the installed C++ v27 Runtime. No policy, expected result,
historic measurement file, callback or learned answer is consulted.

The pulse direction is acquired by paired zero-load cues, not selected by
reinforcement. This is not the consolidated U0 profile or a renewable regulator.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from . import _native as native
from .persistence import (decode_metadata,encode_metadata,load_world_snapshot,save_world_snapshot)

N=67
KEY="dee_thinking.experimental.cpc5_regulation.v1"
SCOPE="EXPERIMENTAL_RECIPE; acquired directional zero-load pulse, fixed finite external curriculum, native material contact; no learned attention or feedback-selected regulatory policy; N67, horizon437."

def _int(value,name,low,high):
    if type(value) is not int or not low<=value<=high:raise ValueError(name+" outside exact integer domain")
    return value

def _move(site,direction,count=1,translation=(0,0,0)):
    return tuple((site[i]+count*direction[i]+translation[i])%N for i in range(3))

def _lists(value):
    if isinstance(value,(tuple,list)):return [_lists(item) for item in value]
    if isinstance(value,dict):return {key:_lists(item) for key,item in value.items()}
    return value

def _interface(name,site,direction):
    c=native.ChannelSpec();c.name=name;c.injection_site=native.Coordinate(*site);c.direction=native.Direction(*direction);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
    p=native.InterfaceSpec();p.name=name;p.channel=c;return p

def _geometry(translation):
    centers={k:_move(v,(0,0,0),translation=translation) for k,v in {"A":(42,20,12),"B":(30,32,12),"C":(32,36,22),"D":(18,44,16)}.items()}
    def bank(emitter,action,resource,step,emission,resource_read,function_read,vdir):
        cost=_move(emitter,action,step);supply=(0,1,0);intercept=_move(cost,supply,4)
        return {"emitter":emitter,"action":action,"resource_direction":resource,"supply_direction":supply,"cost_meeting":cost,"interception":intercept,
            "resource_source":_move(cost,resource,-step),"resource_receiver":_move(cost,resource,3),"supply_source":_move(cost,supply,-6),"function_receiver":_move(cost,supply,2),
            "U_source":_move(intercept,(0,-1,0),-7),"V_source":_move(intercept,vdir,-7),"emission_tick":emission,"resource_read":resource_read,"function_read":function_read}
    initial=bank(centers['D'],(-1,1,1),(1,0,-1),4,228,235,242,(0,-1,1))
    role=bank(centers['B'],(-1,1,-1),(1,0,1),4,417,424,431,(0,-1,-1))
    turn=_move((22,40,12),(0,0,0),translation=translation);role.update({"turn_site":turn,"turn_input":_move(turn,(0,0,-1),-3),"turn_tick":291,"B_social_tick":350,"B_role_read_tick":417})
    flat=bank(centers['B'],(-1,1,0),(1,0,0),10,417,430,437,(0,-1,1))
    lexical={name:_move(q,(0,0,0),translation=translation) for name,q in (("L1",(30,30,40)),("L2",(30,30,56)),("L3",(50,50,10)),("L4",(50,50,26)))}
    meeting=_move(turn,(0,0,1),-2)
    return _lists({"schema":1,"N":N,"translation":list(translation),"centers":centers,"bank":initial,"role":role,"banks":{"N":role,"Flat":flat},"lexical_hubs":lexical,
        "regulation":{"counterflow_source":_move(turn,(0,0,1),-5),"sham_source":_move(_move(turn,(0,0,1),-5),(1,0,0),10),"meeting":meeting},
        "learned_hub":_move(meeting,(0,0,1),-(292-3)),"scope":SCOPE})

def _interfaces(g,mode):
    ports=[];queries={"A":(-1,0,0),"B":(0,0,1),"C":(-1,0,0),"D":(1,0,0)}
    for name,c in g['centers'].items():
        ports += [_interface(name+'.signal',_move(c,(-1,0,0),-3),(-1,0,0)),_interface(name+'.query',_move(c,queries[name],-3),queries[name])]
        if name=='D':ports.append(_interface('D.query_return',_move(c,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,'plus'),(-1,'minus')):
            direction=(1,sign,0) if name=='A' else (1,0,sign);ports.append(_interface(name+'.report.'+label,_move(c,direction,-3),direction))
    def environment_ports(prefix,b,v):
        for label,key,dr in (('resource','resource_source',b['resource_direction']),('supply','supply_source',b['supply_direction']),('U','U_source',(0,-1,0)),('V','V_source',v)):
            ports.append(_interface(prefix+'.'+label,b[key],dr))
    environment_ports('world',g['bank'],(0,-1,1))
    for name in ('L1','L2'):
        h=g['lexical_hubs'][name];ports.append(_interface('lex.'+name+'.signal',_move(h,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,'plus'),(-1,'minus')):ports.append(_interface('lex.'+name+'.report.'+label,_move(h,(1,sign,0),-3),(1,sign,0)))
    ports.append(_interface('instrument.sham',_move((50,60,60),(0,0,0),translation=g['translation']),(1,0,0)))
    ports += [_interface('B.query_negative',_move(g['centers']['B'],(0,0,-1),-3),(0,0,-1)),_interface('role.turn',g['role']['turn_input'],(0,0,-1))]
    environment_ports('role.world',g['role'],(0,-1,-1));environment_ports('flat.world',g['banks']['Flat'],(0,-1,1))
    for name in ('N','Flat'):ports.append(_interface('instrument.action_'+name+'_out',_move(g['centers']['B'],g['banks'][name]['action']),g['banks'][name]['action']))
    for name in ('L3','L4'):
        h=g['lexical_hubs'][name];ports.append(_interface('lex.'+name+'.signal',_move(h,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,'plus'),(-1,'minus')):ports.append(_interface('lex.'+name+'.report.'+label,_move(h,(1,sign,0),-3),(1,sign,0)))
    for name in ('counterflow','sham'):ports.append(_interface('regulation.'+name,g['regulation']['counterflow_source' if name=='counterflow' else 'sham_source'],(0,0,1)))
    if mode!='absent':
        for label,dr in (('cue',(-1,0,0)),('report',(1,0,-1 if mode=='opposite' else 1))):ports.append(_interface('native_regulator.'+label,_move(g['learned_hub'],dr,-3),dr))
    return ports

def _protocol(mode,a,c):
    rows=[]
    def add(channel,load,tick,role):rows.append({'channel':channel,'load':load,'tick':tick,'role':role})
    add('instrument.sham',13,0,'common_uninformative_inventory')
    for name,sign,tick in (('A',a,0),('C',c,10),('B',1,12),('D',1,24)):
        add(name+'.signal',5,tick,name+'_experience_signal');add(name+'.report.'+('plus' if sign==1 else 'minus'),11,tick,name+'_external_report')
    for name,tick in (('A',67),('C',77),('D',158),('D',225)):add('D.query_return' if name=='D' and tick==225 else name+'.query',5,tick,name+'_physical_common_query')
    add('role.turn',5,288,'prepared_native_directional_relay');add('B.query_negative',5,414,'new_B_common_negative_social_query')
    # Declared synthetic habitat law from present external properties, not a
    # participant policy or a response-dependent callback. It supplies threats.
    event_n='U' if a==1 and c==-1 else 'V';event_f='U' if a==1 and c==1 else 'V'
    for channel,load,tick in (('role.world.resource',3,417),('role.world.supply',7,423),('role.world.'+event_n,11,418),('flat.world.resource',3,417),('flat.world.supply',7,429),('flat.world.'+event_f,11,424)):add(channel,load,tick,'FIXED_EXTERNAL_ENVIRONMENT_LAW')
    if mode!='absent':
        for label in ('cue','report'):add('native_regulator.'+label,0,int(label=='cue' and mode=='unpaired'),'Actual neutral directional-regulator experience')
    return rows

def _record(world,site):
    o=world.runtime.observe(native.Coordinate(*site));r=o.record
    return {'tick':int(o.tick),'site':list(site),'raw':str(o.raw),'clock':str(o.clock),'state':int(r.state),'s_reg':int(r.s_reg),'direction':[int(r.dx),int(r.dy),int(r.dz)],'semantic':int(r.semantic),'active':r.state>0 and r.semantic!=5}

class CPC5RegulationSession:
    """One persistent Runtime, one finite acquisition/communication trajectory."""
    def __init__(self,world,geometry,mode,journal):self.world=world;self.geometry=geometry;self.mode=mode;self.journal=journal
    @classmethod
    def create(cls,*,mode='paired',translation=(0,0,0),a_history=1,c_history=1):
        if mode not in ('paired','unpaired','opposite','absent'):raise ValueError('Unknown finite pulse mode')
        if not isinstance(translation,(tuple,list)) or len(translation)!=3:raise ValueError('Three exact integer translation components required')
        translation=tuple(_int(v,'translation',-2**31,2**31-1) for v in translation)
        for sign in (a_history,c_history):
            if type(sign) is not int or sign not in (-1,1):raise ValueError('External current properties must be +/-1')
        g=_geometry(translation);recipe=native.OrganizationRecipe.research(N,[],0);recipe.interfaces=_interfaces(g,mode);recipe.execution=native.TickOptions(native.Backend.LAZY,1);world=native.OrganizationalWorld.create(recipe);journal=[]
        for item in _protocol(mode,a_history,c_history):
            rr=world.submit(item['channel'],item['load'],item['tick']);journal.append({**item,'receipt_id':int(rr.id),'call_tick':0,'modality':'EXPERIENCE_PROTOCOL'})
        return cls(world,g,mode,journal)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def run_until(self,tick):
        _int(tick,'absolute finite horizon',self.tick,437);self.world.run_until(tick)
        return self.observe()
    def observe(self):
        samples={name:_record(self.world,q) for name,q in self.geometry['centers'].items()};samples['regulation_meeting']=_record(self.world,self.geometry['regulation']['meeting'])
        if self.mode!='absent':samples['nominal_regulator_segment']=_record(self.world,_move(self.geometry['learned_hub'],(0,0,-1 if self.mode=='opposite' else 1),max(0,self.tick-3)))
        banks={name:{'resource':_record(self.world,b['resource_receiver']),'function':_record(self.world,b['function_receiver'])} for name,b in self.geometry['banks'].items()}
        return {'tick':self.tick,'samples':samples,'banks':banks,'scope':SCOPE,'provenance':'PASSIVE_OBSERVATION'}
    def save_snapshot(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'schema':1,'tick':self.tick,'mode':self.mode,'geometry':self.geometry,'journal':self.journal}))
        return save_world_snapshot(self.world,path)
    @classmethod
    def load_snapshot(cls,path):
        world,_=load_world_snapshot(path);text=world.runtime.snapshot_metadata(KEY)
        if text is None:raise ValueError('No supported finite regulation metadata')
        data=decode_metadata(text);g=data['geometry'];mode=data['mode']
        if not isinstance(g,dict) or not isinstance(g.get('translation'),list) or len(g['translation'])!=3:raise ValueError('Invalid stored translation')
        for value in g['translation']:_int(value,'stored translation',-2**31,2**31-1)
        if data.get('schema')!=1 or data['tick']!=world.runtime.current_tick or world.runtime.dimension!=N or world.recipe.placements:raise ValueError('Regulation state/recipe mismatch')
        if mode not in ('paired','unpaired','opposite','absent') or g!=decode_metadata(encode_metadata(_geometry(g['translation']))):raise ValueError('Changed experimental geometry')
        expected=_interfaces(g,mode)
        if set(world.runtime.channel_names)!={p.name for p in expected}:raise ValueError('Changed experimental interfaces')
        def signature(item):
            c=item.channel;q=c.injection_site;d=c.direction
            return (c.name,q.x,q.y,q.z,c.state,d.dx,d.dy,d.dz,c.semantic,c.allow_experience,c.allow_probe)
        if {p.name:signature(p) for p in world.interfaces}!={p.name:signature(p) for p in expected}:raise ValueError('Changed experimental physical interface')
        if not isinstance(data.get('journal'),list) or len(data['journal'])>64:raise ValueError('Invalid finite request journal')
        for item in data['journal']:
            if not isinstance(item,dict):raise ValueError('Invalid request journal entry')
            _int(item['receipt_id'],'stored receipt',0,2**64-1);_int(item['tick'],'stored request tick',0,437)
            rr=world.runtime.receipt(item['receipt_id'])
            if rr is None or rr.requested_tick!=item['tick'] or list(rr.channels)!=[item['channel']]:raise ValueError('Missing pending/applied request')
        return cls(world,g,mode,data['journal'])
    def fork(self):return type(self)(self.world.fork(),deepcopy(self.geometry),self.mode,deepcopy(self.journal))

def create_cpc5_regulation(**options):return CPC5RegulationSession.create(**options)
