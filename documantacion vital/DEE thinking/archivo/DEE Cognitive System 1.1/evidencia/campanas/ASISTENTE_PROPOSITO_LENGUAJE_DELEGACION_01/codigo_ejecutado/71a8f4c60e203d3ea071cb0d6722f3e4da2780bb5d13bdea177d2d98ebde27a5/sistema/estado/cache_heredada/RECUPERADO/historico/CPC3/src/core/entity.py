"""CPC3 persistent MAIN entity. The interface never restores a favorable body.

Evolution, relative writes and current physical readout use frozen DEE 3.5/v27.
The finite barrier is a declared external habitat. Its observed *past* packet
outcomes are encoded as zero-load native events. No error or future result is
sent back. Fixed phase scheduling is an external interface, not acquired timing.
No operational fork exists in this module.
"""
from array import array
from datetime import datetime, timezone
import hashlib, json, os, time
from pathlib import Path
import dee_thinking as d

SCHEMA='cpc3.entity.v1'
SAMPLE_SLOTS=(163,292,554,812,945)

def atomic_json(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(q,p)
def xyz(q):return (q.x,q.y,q.z)
def add(q,v,n=47):return tuple((a+b)%n for a,b in zip(q,v))
def observation(o):
    r=o.record
    return {'tick':o.tick,'site':[o.coordinate.x,o.coordinate.y,o.coordinate.z],'raw':o.raw,'clock':o.clock,'state':r.state,'s_reg':r.s_reg,'semantic':r.semantic,'direction':[r.dx,r.dy,r.dz],'active':r.state>0 and r.semantic!=5}
def receipt(r):return {'id':r.id,'status':str(r.status),'reason':r.reason,'requested_tick':r.requested_tick,'effective_tick':r.effective_tick}
def write_gate(rt,q,neighbors=False):
    g=d.inspect_write_gate(rt,q,neighbors)
    return {'absolute_tick':g.absolute_tick,'clock':g.local_clock,'n_active':g.n_active,'direction_sum':[g.direction_sum.dx,g.direction_sum.dy,g.direction_sum.dz],'tetra_pattern':g.tetra_pattern,'hadron':g.hadron,'rule_value':g.rule_value,'survives':g.survives_material_rule,'protected':g.write_protected,'k':g.k,'period':g.period,'phase_remainder':g.phase_remainder,'ordinary_increment_condition':g.ordinary_increment_condition,'branch':g.branch,'demux':g.demux_status}
def fixed_decode(o):
    # No history log, habitat, target, label or evaluator enters this function.
    x=o['direction'][0] if o['active'] else 0
    return [True] if x>0 else [False] if x<0 else [False,True]

class BarrierHabitat:
    """Independent external packet barrier; samples resolve only at present time."""
    def __init__(self,initial_open=False,change_tick=80):
        self.initial_open=bool(initial_open);self.change_tick=change_tick;self.tick=32;self.samples=[];self.outcomes={}
    def advance(self,tick):
        if tick<self.tick:raise ValueError('External habitat cannot rewind')
        self.tick=tick
    def _condition(self,tick):return self.initial_open if self.change_tick is None or tick<self.change_tick else not self.initial_open
    def sample(self,reference=False):
        value=self._condition(self.tick);value=not value if reference else value
        x={'tick':self.tick,'arrived':value,'reference_branch':reference,'observable':'packet_arrival_at_barrier_output','modality':'OBSERVED_EXTERNAL_ENVIRONMENT'};self.samples.append(x);return x
    def resolve(self,target):
        if target>self.tick:raise ValueError('Outcome is still in the future')
        if str(target) not in self.outcomes:self.outcomes[str(target)]={'tick':target,'arrived':self._condition(target),'observable':'packet_arrival_at_barrier_output'}
        return self.outcomes[str(target)]
    def export(self):return {'initial_open':self.initial_open,'change_tick':self.change_tick,'tick':self.tick,'samples':self.samples,'outcomes':self.outcomes,'world_law':'one packet per integer tick, barrier condition flips at fixed declared tick; independent of prediction'}
    @classmethod
    def load(cls,x):
        h=cls(x['initial_open'],x['change_tick']);h.tick=x['tick'];h.samples=x['samples'];h.outcomes=x['outcomes'];return h

class Entity:
    def __init__(self,world,habitat,origin):
        self.world=world;self.habitat=habitat;self.origin=tuple(origin);self.events=[];self.predictions=[];self.reader_primed=False;self.past_pair_presented=False;self.slot_index=0;self.operation_calls=[];self.event_sink=None
    @classmethod
    def create(cls,origin=(15,15,15),initial_open=False,change_tick=80,backend='LAZY',event_state=1):
        recipe=d.OrganizationRecipe.relational(d.reference_seed_path(),d.BasalHistory.H0,False,d.Coordinate(*origin))
        opts=d.TickOptions();opts.backend=getattr(d.Backend,backend);opts.threads=1;recipe.execution=opts
        w=d.OrganizationalWorld.create(recipe);spec=w.view('body').spec
        for key,center,off,dr in [('A',spec.a,(0,-1,0),(0,0,-1)),('B',spec.b,(0,1,0),(0,0,1))]:
            i=d.InterfaceSpec();i.name='sensor.'+key;c=d.ChannelSpec();c.name=i.name;c.injection_site=d.Coordinate(*add(xyz(center),off));c.direction=d.Direction(*dr);c.state=event_state;c.semantic=1;c.allow_experience=True;c.allow_probe=True;i.channel=c;w.declare_interface(i)
        e=cls(w,BarrierHabitat(initial_open,change_tick),origin)
        e._event('PREPARATION',{'recipe':'relational.v1/H0','reader':'finite zero-load MAIN query, subsequent live native output','host_setup_finished_at_tick':32,'backend':backend,'event_state':event_state,'external_phase_slots':list(SAMPLE_SLOTS)})
        return e
    @property
    def tick(self):return self.world.runtime.current_tick
    def _event(self,kind,item):
        x={'kind':kind,'tick':self.tick,'monotonic_ns':time.monotonic_ns(),'wall_utc':datetime.now(timezone.utc).isoformat(),**item};self.events.append(x)
        if self.event_sink:
            p=Path(self.event_sink);p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('a',encoding='utf-8') as f:f.write(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        return x
    def observe(self):
        s=self.world.view('body').spec;p=self.world.view('body').observe();a=observation(self.world.runtime.observe(s.a));b=observation(self.world.runtime.observe(s.b));o=observation(self.world.runtime.observe(s.comparator))
        return {'tick':self.tick,'delta':p.delta,'centers_available':p.centers_available,'supports_intact':p.supports_intact,'reader_available':p.reader_available,'physical_output':o,'prediction_set':fixed_decode(o),'a':a,'b':b,'axis_projection':p.axis_projection,'modality':'PASSIVE_OBSERVATION','write_gates':{'A':write_gate(self.world.runtime,s.a),'B':write_gate(self.world.runtime,s.b)},'domain_status':'WITHIN_FINITE_TESTED_HORIZON' if self.tick<=1032 else 'OUTSIDE_TESTED_HORIZON_MEASUREMENT_ONLY','limits':'current direction may reflect reader context as well as relative memory; see controls; no native timeout-based absence detector'}
    def _advance_to(self,tick):
        if tick<self.tick:raise ValueError('Cannot rewind MAIN')
        start=self.tick;self.operation_calls.append({'operation':'world.run_until','from':start,'to':tick});self.world.run_until(tick);self.habitat.advance(tick)
    def advance(self,ticks=1):
        if not isinstance(ticks,int) or ticks<0:raise ValueError('ticks must be a nonnegative integer')
        self._advance_to(self.tick+ticks);evaluations=[]
        for p in self.predictions:
            if p['target_tick']<=self.tick and not p.get('evaluated'):
                # Evaluation is audit-only. It never supplies an input to DEE.
                outcome=self.habitat.resolve(p['target_tick']);ps=p['prediction_set'];x=self._event('EVALUATION',{'emission_tick':p['emission_tick'],'target_tick':p['target_tick'],'outcome':outcome,'prediction_set':ps,'coverage':len(ps)==1,'error':int(ps[0]!=outcome['arrived']) if len(ps)==1 else None,'modality':'ANALISIS_EXTERNO'});p['evaluated']=True;evaluations.append(x)
        return {'observation':self.observe(),'evaluations':evaluations}
    def _input(self,key,tick,source):
        if key not in ('A','B'):raise ValueError('Only physical sensor A or B is supported')
        self._advance_to(tick);pre=self.observe();r=self.world.submit('sensor.'+key,0,tick);self.operation_calls.append({'operation':'submit','channel':'sensor.'+key,'value':0,'tick':tick,'receipt_id':r.id,'source':source});self._advance_to(tick+1);rr=receipt(self.world.runtime.receipt(r.id));return self._event('EXPERIENCE',{'sensor':key,'receipt':rr,'before':pre,'after':self.observe(),'source':source,'modality':'EXPERIENCE_PROTOCOL'})
    def _next_slot(self):
        while self.slot_index<len(SAMPLE_SLOTS) and SAMPLE_SLOTS[self.slot_index]<self.tick:self.slot_index+=1
        if self.tick<=33:return self.tick
        if self.slot_index>=len(SAMPLE_SLOTS):return None
        t=SAMPLE_SLOTS[self.slot_index];self.slot_index+=1;return t
    def experience(self,symbol):
        key=str(symbol).upper()
        if key not in ('A','B'):raise ValueError('Supported sensor symbols are A and B')
        t=self._next_slot()
        if t is None:return self._event('INTERFACE_LIMIT',{'status':'NO_FURTHER_PHASE_SLOTS_IN_PUBLISHED_DOMAIN','modality':'INTERFACE'})
        return self._input(key,t,{'kind':'USER_REQUEST','symbol':key,'timing':'fixed external phase schedule, not acquired adaptation'})
    def sense(self):
        if not self.past_pair_presented and self.tick==32:
            rows=[]
            for reference in (False,True):
                past=self.habitat.sample(reference);rows.append(self._input('A' if past['arrived'] else 'B',self.tick,{'kind':'ACTUAL_OBSERVED_PACKET','past':past}))
            self.past_pair_presented=True
            return {'kind':'INITIAL_PAST_PAIR','events':rows,'modality':'EXPERIENCE_PROTOCOL','observable':'packet_arrival_at_barrier_output','reference_branch_is_declared':True}
        t=self._next_slot()
        if t is None:return self._event('INTERFACE_LIMIT',{'status':'NO_FURTHER_PHASE_SLOTS_IN_PUBLISHED_DOMAIN','modality':'INTERFACE'})
        self._advance_to(t);past=self.habitat.sample();return self._input('A' if past['arrived'] else 'B',t,{'kind':'ACTUAL_OBSERVED_PACKET','past':past,'timing':'fixed external phase schedule'})
    def predict(self,horizon=30):
        if not isinstance(horizon,int) or horizon<1:raise ValueError('horizon must be a positive integer')
        rr=None
        if not self.reader_primed:
            r=self.world.probe('body.common_query',0,self.tick);self.operation_calls.append({'operation':'probe','channel':'body.common_query','value':0,'tick':self.tick,'receipt_id':r.id,'source':'USER_QUERY'});self._advance_to(self.tick+3);rr=receipt(self.world.runtime.receipt(r.id));self.reader_primed=rr['status']=='applied'
        p=self.observe();o=p['physical_output'];ps=fixed_decode(o) if rr is None or rr['status']=='applied' else [False,True]
        em=self._event('EMISSION',{'emission_tick':self.tick,'target_tick':self.tick+horizon,'horizon':horizon,'prediction_set':ps,'physical_output':o,'receipt':rr,'observable':'packet_arrival_at_barrier_output','decoder':'live MAIN dx sign: positive arrival, negative absence, zero/missing unresolved','modality':'PHYSICAL_PROBE_ON_MAIN' if rr else 'PASSIVE_OBSERVATION_OF_RENEWED_MAIN_OUTPUT','operational_forks':0,'information_cut':[x for x in self.events if x['kind']=='EXPERIENCE'],'memory_panel':{'delta':p['delta'],'centers_available':p['centers_available'],'supports_intact':p['supports_intact']},'limits':'finite persistence predictor, current readout may be context-sensitive; no arbitrary future dynamics learned'})
        self.predictions.append(dict(em));return em
    def physical_digest(self):return {'tick':self.tick,'raw_sha256':hashlib.sha256(array('Q',self.world.runtime.raw_copy()).tobytes()).hexdigest(),'clock_sha256':hashlib.sha256(array('Q',self.world.runtime.clock_copy()).tobytes()).hexdigest()}
    def save(self,path):
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
        self.operation_calls.append({'operation':'set_snapshot_metadata','tick':self.tick,'scope':'OPERATIVE_METADATA_NON_RAW','key':SCHEMA,'source':'USER_OR_AUDITOR_PERSISTENCE_REQUEST'})
        self.operation_calls.append({'operation':'save_snapshot','tick':self.tick,'scope':'FILESYSTEM_OPERATIVE_PERSISTENCE','path':str(p),'source':'USER_OR_AUDITOR_PERSISTENCE_REQUEST'})
        data={'schema':SCHEMA,'origin':self.origin,'habitat':self.habitat.export(),'events':self.events,'predictions':self.predictions,'reader_primed':self.reader_primed,'past_pair_presented':self.past_pair_presented,'slot_index':self.slot_index,'operation_calls':self.operation_calls}
        self.world.runtime.set_snapshot_metadata(SCHEMA,json.dumps(data,separators=(',',':')));self.world.save_snapshot(str(p))
        return {'path':str(p),'tick':self.tick,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'physical':self.physical_digest(),'metadata_is_external_not_native_memory':True}
    @classmethod
    def load(cls,path):
        w=d.OrganizationalWorld.load_snapshot(str(path));x=json.loads(w.runtime.snapshot_metadata(SCHEMA))
        if x['schema']!=SCHEMA:raise ValueError('Unsupported session version')
        e=cls(w,BarrierHabitat.load(x['habitat']),x['origin']);e.events=x['events'];e.predictions=x['predictions'];e.reader_primed=x['reader_primed'];e.past_pair_presented=x['past_pair_presented'];e.slot_index=x['slot_index'];e.operation_calls=x['operation_calls'];return e
