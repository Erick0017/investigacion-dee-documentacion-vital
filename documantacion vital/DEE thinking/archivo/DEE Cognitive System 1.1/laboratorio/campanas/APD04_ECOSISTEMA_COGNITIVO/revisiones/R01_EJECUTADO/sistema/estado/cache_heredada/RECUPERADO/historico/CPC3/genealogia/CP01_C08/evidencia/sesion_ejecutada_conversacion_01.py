"""Finite communicative session: fixed physical wires, native history, external habitat.

No decoder or environment policy consults training targets. The environment
uses the measured DEE output directly as an action, and supplies its resource
state as a later sensory event. It never edits native memory or clocks.
"""
import json
from pathlib import Path
import dee_thinking as d
from laboratorio import reading,receipt,physical


class Session:
    schema=1
    def __init__(self,world,state):self.world=world;self.state=state
    @classmethod
    def create(cls,origin=(0,0,0),slots=16,resource=3,feedback=False):
        if not 2<=slots<=32 or not 0<=resource<31:raise ValueError('slots2..32; resource0..30')
        w=d.create_organization('mobile_pair',origin=origin);n=w.runtime.dimension;targets=[]
        for k in range(slots):
            pair=[]
            for j in range(2):
                base=w.view('q'+str(j)).spec.ports['response'];q=d.Coordinate((base.x-5*k)%n,(base.y+5*k)%n,base.z)
                i=d.InterfaceSpec();i.name=f'slot{k}.wire{j}';ch=d.ChannelSpec();ch.name=i.name;ch.injection_site=d.Coordinate((q.x+5)%n,q.y,q.z);ch.state=1;ch.direction=d.Direction(-1,0,0);ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;i.channel=ch;w.declare_interface(i);pair.append([q.x,q.y,q.z])
            targets.append(pair)
        state={'schema':1,'recipe':'mobile_pair.v1','origin':list(origin),'slots':slots,'targets':targets,'signals':{'s0':13,'s1':17},'pending':{},'frames':[],
               'environment':{'kind':'EXTERNAL_SANDBOX_MOD31','resource':resource,'auto_feedback':feedback,'action_rule':'resource_next=(resource+measured_wire0_load)%31','not_reward_or_target':True},
               'events':[],'instance_restarts':0}
        return cls(w,state)
    def experience(self,cue,ref0,ref1):
        if self.world.runtime.current_tick!=0:raise ValueError('Initial paired calibration is admissible at tick0 only; later contacts use encounter/return, not hidden re-preparation')
        receipts=[]
        for j,r in enumerate((ref0,ref1)):
            receipts += [self.world.submit(f'l{j}.cue',cue,0),self.world.submit(f'l{j}.teacher',r,0)]
        self.state['events'].append({'operation':'paired_experience','tick':0,'inputs':[cue,ref0,ref1],'receipt_ids':[r.id for r in receipts],'modality':'EXPERIENCE_PROTOCOL'})
        return [receipt(r) for r in receipts]
    def schedule(self,value,slot=None,kind='signal',offpath=False):
        tick=self.world.runtime.current_tick
        if slot is None:slot=max(0,(max(6,tick)-6+4)//5)
        if not 0<=slot<self.state['slots']:raise ValueError('Finite prepared interface exhausted; no automatic reset')
        if str(slot) in self.state['pending'] or any(f['slot']==slot for f in self.state['frames']):raise ValueError('Slot already used')
        at=6+5*slot
        if at<tick:raise ValueError('Prepared slot is in the past')
        ids=[]
        for j in range(2):
            name=f'slot{slot}.wire{j}'
            if offpath:
                # These comparison wires are declared before T0 by the case
                # builder, never by an adaptive correction.
                name=f'offpath{slot}.wire{j}'
            r=self.world.probe(name,value,at) if kind=='signal' else self.world.submit(name,value,at);ids.append(r.id)
        self.state['pending'][str(slot)]={'slot':slot,'input':value,'at':at,'read':at+5,'kind':kind,'ids':ids,'offpath':offpath}
        self.state['events'].append({'operation':kind,'slot':slot,'tick':tick,'scheduled_tick':at,'input':value,'receipt_ids':ids,'modality':'PHYSICAL_PROBE' if kind=='signal' else 'EXPERIENCE_PROTOCOL'})
        return [receipt(self.world.runtime.receipt(i)) for i in ids]
    def signal(self,symbol,slot=None):
        if symbol not in self.state['signals']:raise ValueError('Unknown opaque signal; use s0 or s1')
        return self.schedule(self.state['signals'][symbol],slot,'signal')
    def advance_to(self,target):
        if target<self.world.runtime.current_tick or target-self.world.runtime.current_tick>2048:raise ValueError('Advance must be future and at most2048 ticks per call')
        while True:
            pending=[p for p in self.state['pending'].values() if p['read']<=target]
            boundary=min([p['read'] for p in pending]+[target]);before=self.world.runtime.current_tick
            self.world.run_until(boundary)
            if boundary>before and self.world.runtime.current_tick==before:raise RuntimeError('Runtime made no progress; paused or blocked')
            ready=sorted([p for p in self.state['pending'].values() if p['read']<=self.world.runtime.current_tick],key=lambda p:p['slot'])
            for p in ready:
                outputs=[reading(self.world.runtime.observe(d.Coordinate(*q))) for q in self.state['targets'][p['slot']]]
                frame={'slot':p['slot'],'input':p['input'],'kind':p['kind'],'tick':self.world.runtime.current_tick,'outputs':outputs,'receipts':[receipt(self.world.runtime.receipt(i)) for i in p['ids']],
                       'historical_capture_not_cached_answer':True,'response_has_admitted_input':all(self.world.runtime.receipt(i).status==d.EventStatus.APPLIED for i in p['ids']),
                       'physical_query_consumption_contract':'An admitted encounter can change the carrier; causal differences are checked in matched future panels'}
                self.state['frames'].append(frame);del self.state['pending'][str(p['slot'])]
                if outputs[0]['active'] and frame['response_has_admitted_input']:
                    env=self.state['environment'];old=env['resource'];action=outputs[0]['s_reg'];env['resource']=(old+action)%31
                    frame['consequence']={'old_resource':old,'native_action_load':action,'new_resource':env['resource'],'modality':'EXTERNAL_ACTUATION_SANDBOX'}
                    if env['auto_feedback'] and p['slot']+1<self.state['slots']:
                        self.schedule(env['resource'],p['slot']+1,'environment_return')
            if self.world.runtime.current_tick>=target:break
        return ready
    def advance(self,n):return self.advance_to(self.world.runtime.current_tick+n)
    def observe(self):
        if not self.state['frames']:return {'tick':self.world.runtime.current_tick,'response_available':False,'reason':'No evaluated physical encounter yet','environment':self.state['environment']}
        frame=self.state['frames'][-1];now=self.world.runtime.current_tick
        return {'tick':now,'last_response':frame,'historical_if_tick_differs':now!=frame['tick'],'environment':self.state['environment'],'memory_relation_gap':frame['outputs'][1]['s_reg']-frame['outputs'][0]['s_reg'] if all(o['active'] for o in frame['outputs']) else None}
    def save(self,path):
        self.world.runtime.set_snapshot_metadata('cp01.session.v1',json.dumps(self.state,separators=(',',':')));self.world.save_snapshot(str(path))
    @classmethod
    def load(cls,path):
        w=d.OrganizationalWorld.load_snapshot(str(path));s=w.runtime.snapshot_metadata('cp01.session.v1')
        if not s:raise ValueError('Snapshot has no communicative-session protocol metadata')
        data=json.loads(s)
        if data.get('schema')!=1:raise ValueError('Unsupported session metadata')
        return cls(w,data)
    def fork(self):return Session(self.world.fork(),json.loads(json.dumps(self.state)))


def install_offpath(s):
    if s.world.runtime.current_tick!=0:raise ValueError('Off-path control preparation before T0 only')
    for k in range(s.state['slots']):
        for j in range(2):
            q=s.state['targets'][k][j];i=d.InterfaceSpec();i.name=f'offpath{k}.wire{j}';ch=d.ChannelSpec();ch.name=i.name;ch.injection_site=d.Coordinate((q[0]+5)%34,q[1],(q[2]+5)%34);ch.direction=d.Direction(-1,0,0);ch.allow_experience=True;ch.allow_probe=True;i.channel=ch;s.world.declare_interface(i)
