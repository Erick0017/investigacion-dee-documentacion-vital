"""CP02 B: native differential-state forecaster, explicit external gate habitat.

The external gate latches the first physical sensor observation. Its future
packet result is not a function of the DEE forecast. DEE receives the sensor
events, never the latch, random seed, outcome or scenario name.
"""
from array import array
from datetime import datetime,timezone
import hashlib,json,os,time
from pathlib import Path
import dee_thinking as d


def atomic_json(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.tmp')
    q.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');os.replace(q,p)


def observation(o):
    r=o.record
    return {'tick':o.tick,'coordinate':[o.coordinate.x,o.coordinate.y,o.coordinate.z],
            'RAW':o.raw,'clock':o.clock,'state':r.state,'semantic':r.semantic,
            's_reg':r.s_reg,'direction':[r.dx,r.dy,r.dz],'active':r.state>0 and r.semantic!=5}


def receipt(r):
    return {'id':r.id,'status':str(r.status),'requested_tick':r.requested_tick,
            'effective_tick':r.effective_tick,'channels':list(r.channels),'reason':r.reason}


def panel(w):
    p=w.view('body').observe()
    return {'tick':w.runtime.current_tick,'delta':p.delta,'centers_available':p.centers_available,
            'supports_intact':p.supports_intact,'reader_available':p.reader_available,
            'axis_projection':p.axis_projection,'observations':{k:observation(o) for k,o in p.observations.items()}}


def physical(w):
    return {'tick':w.runtime.current_tick,
            'RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}


def build(origin=(15,15,15),event_state=1):
    w=d.create_organization('relational',history=d.BasalHistory.H0,origin=origin)
    spec=w.view('body').spec
    for key,center,off,dr in [('A',spec.a,(0,-1,0),(0,0,-1)),('B',spec.b,(0,1,0),(0,0,1))]:
        i=d.InterfaceSpec();i.name='sensor.'+key;c=d.ChannelSpec();c.name=i.name
        c.injection_site=d.Coordinate(*[(a+b)%47 for a,b in zip((center.x,center.y,center.z),off)])
        c.direction=d.Direction(*dr);c.state=event_state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        i.channel=c;w.declare_interface(i)
    return w


class AuditLog:
    def __init__(self,path):self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
    def append(self,item):
        entry=dict(item);entry['wall_utc']=datetime.now(timezone.utc).isoformat();entry['monotonic_ns']=time.monotonic_ns()
        with self.path.open('a',encoding='utf-8') as f:
            f.write(json.dumps(entry,separators=(',',':'),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
        return entry


class GateHabitat:
    """No access to a native Runtime, predictions, decoder, memory or evaluator.

    This component is the declared EXTERNAL_ENVIRONMENT, not v27. A packet
    reaches a barrier at its target tick. The first sensor A opens it; B closes
    it. Sensor events may be replayed to the organism by its interface. Packet
    arrival is evaluated only when the shared tick reaches its deadline.
    """
    def __init__(self):self.first=None;self.events=[];self.resolved={};self.tick=32
    def event(self,key,tick):
        if key not in ('A','B'):raise ValueError('Unknown physical sensor')
        if tick<self.tick:raise ValueError('Past habitat event')
        self.tick=tick;self.events.append({'sensor':key,'tick':tick})
        if self.first is None:self.first=key
    def advance(self,tick,targets):
        if tick<self.tick:raise ValueError('Habitat cannot rewind')
        self.tick=tick
        for target in targets:
            if target<=tick and str(target) not in self.resolved:
                self.resolved[str(target)]={'tick':target,'arrived':self.first=='A','observable':'packet_arrival_at_barrier_output',
                    'world_law':'first sensor A opens / B blocks; forecast has no connection to gate'}
    def export(self):return {'first':self.first,'events':self.events,'resolved':self.resolved,'tick':self.tick}
    @classmethod
    def restore(cls,x):
        h=cls();h.first=x['first'];h.events=x['events'];h.resolved=x['resolved'];h.tick=x['tick'];return h


class PersistentTransportHabitat:
    """A declared external barrier; only past actual packet outcomes are sensed.

    A hidden mechanical condition is stable until an optional fixed change
    tick. Seed/condition are never supplied to the DEE interfaces or decoder.
    The reference branch inverts the same barrier's mechanical condition;
    two past packets yield the same sensor inventory in opposite order.
    This is an explicit finite-family persistence forecast, not learning an
    arbitrary association or the barrier's unknown transition law.
    """
    kind='EXTERNAL_PERSISTENT_TRANSPORT'
    def __init__(self,open_gate=True,change_tick=None):
        self.open_gate=bool(open_gate);self.change_tick=change_tick;self.tick=32;self.events=[];self.resolved={}
    def state_at(self,tick):return self.open_gate if self.change_tick is None or tick<self.change_tick else not self.open_gate
    def actual_past_result(self,tick,reference=False):
        if tick<self.tick:raise ValueError('Cannot manufacture a past result')
        self.tick=tick;arrived=self.state_at(tick);arrived=not arrived if reference else arrived
        x={'tick':tick,'arrived':arrived,'reference_branch':reference,'observed_after_evolution':True}
        self.events.append(x);return x
    def event(self,key,tick):
        # This is a receipt note, not an input to the world's state.
        self.events.append({'sensor_receipt':key,'tick':tick})
    def advance(self,tick,targets):
        if tick<self.tick:raise ValueError('World time cannot rewind')
        self.tick=tick
        for target in targets:
            if target<=tick and str(target) not in self.resolved:
                self.resolved[str(target)]={'tick':target,'arrived':self.state_at(target),'observable':'packet_arrival_at_barrier_output',
                    'world_law':'packet transmits iff mechanical barrier open; fixed optional flip; no forecast input'}
    def export(self):return {'kind':self.kind,'open_gate':self.open_gate,'change_tick':self.change_tick,'tick':self.tick,'events':self.events,'resolved':self.resolved}
    @classmethod
    def restore(cls,x):
        h=cls(x['open_gate'],x['change_tick']);h.tick=x['tick'];h.events=x['events'];h.resolved=x['resolved'];return h


def restore_habitat(x):
    return PersistentTransportHabitat.restore(x) if x.get('kind')==PersistentTransportHabitat.kind else GateHabitat.restore(x)


class PredictorSession:
    def __init__(self,w,habitat=None):
        self.world=w;self.habitat=habitat or GateHabitat();self.accessible=[];self.emissions=[];self.actions=[]
    @classmethod
    def create(cls,origin=(15,15,15),event_state=1):return cls(build(origin,event_state))
    def present(self,events,start=None):
        start=self.world.runtime.current_tick if start is None else start;ids=[]
        for j,key in enumerate(events):
            tick=start+j;r=self.world.submit('sensor.'+key,0,tick);ids.append(r.id)
            self.habitat.event(key,tick);self.accessible.append({'sensor':key,'tick':tick,'load':0,'receipt_id':r.id})
        self.world.run_until(start+len(events));self.habitat.advance(self.world.runtime.current_tick,[])
        return [receipt(self.world.runtime.receipt(i)) for i in ids]
    def experience_past_results(self,mode='paired',delay=0):
        if not isinstance(self.habitat,PersistentTransportHabitat):raise ValueError('Past-result route requires the transport habitat')
        if mode not in ('paired','unpaired','none'):raise ValueError('Unknown experience treatment')
        start=self.world.runtime.current_tick+delay;ids=[]
        for j in range(2):
            tick=start+j;self.world.run_until(tick);self.habitat.advance(tick,[])
            past=self.habitat.actual_past_result(tick,reference=j==1)
            key='A' if past['arrived'] else 'B'
            if mode=='unpaired':key='B' if key=='A' else 'A'
            if mode!='none':
                r=self.world.submit('sensor.'+key,0,tick);ids.append(r.id)
                self.accessible.append({'sensor':key,'tick':tick,'load':0,'source_past_result_tick':past['tick'],
                    'reference_branch':past['reference_branch'],'source_result_arrived':past['arrived'] if mode=='paired' else None,
                    'receipt_id':r.id,'codec':'past observed arrival -> A, no-arrival -> B; unpaired reverses delivery only'})
            self.world.advance();self.habitat.advance(self.world.runtime.current_tick,[])
        return [receipt(self.world.runtime.receipt(i)) for i in ids]
    def predict(self,targets,log,run_id,payload=7):
        targets=list(targets)
        if not targets or min(targets)<=self.world.runtime.current_tick+3:raise ValueError('Target must remain future after native emission')
        before=panel(self.world);r=self.world.probe('body.common_query',payload,self.world.runtime.current_tick)
        self.world.advance(3);self.habitat.advance(self.world.runtime.current_tick,targets)
        o=observation(self.world.observe('body','comparator'));rr=receipt(self.world.runtime.receipt(r.id))
        # Fixed decoder uses only the emitted native port. No habitat state.
        dr=o['direction'][0] if o['active'] and rr['status']=='applied' else None
        possibilities=[True] if dr is not None and dr>0 else [False] if dr is not None and dr<0 else [False,True]
        entry={'record_type':'EMISSION','run_id':run_id,'emission_tick':self.world.runtime.current_tick,'target_ticks':targets,
            'horizons':[t-self.world.runtime.current_tick for t in targets],
            'observable':'packet_arrival_at_barrier_output','information_cut':list(self.accessible),
            'physical_output':o,'decoder':'direction_x positive -> arrival; negative -> absence; zero/missing -> unresolved set',
            'prediction_set':possibilities,'receipt':rr,'panel_before':before,'panel_after':panel(self.world),
            'action_condition':'forecast does not actuate the barrier','modality':'PHYSICAL_PROBE_ON_MAIN',
            'remaining_limits':'decoder maps a persisted outcome class; precursor->arbitrary outcome correspondence was not learned'}
        logged=log.append(entry);self.emissions.append(logged);return logged
    def evaluate(self,target,log,run_id):
        previous=[e for e in self.emissions if target in e['target_ticks']]
        if not previous:raise ValueError('No registered prediction for target')
        emitted=previous[-1]
        if emitted['emission_tick']>=target:raise ValueError('Prediction is not prospective')
        self.world.run_until(target);self.habitat.advance(target,[target]);out=self.habitat.resolved[str(target)]
        ps=emitted['prediction_set'];resolved=len(ps)==1;correct=out['arrived'] in ps
        item={'record_type':'EVALUATION','run_id':run_id,'emission_tick':emitted['emission_tick'],'target_tick':target,
            'current_tick':self.world.runtime.current_tick,'outcome':out,'prediction_set':ps,
            'correct_when_resolved':ps[0]==out['arrived'] if resolved else None,'coverage':resolved,
            'set_contains_outcome':correct,'absolute_error_binary':int(ps[0]!=out['arrived']) if resolved else None,
            'panel':panel(self.world)}
        return log.append(item)
    def save(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        data={'schema':1,'habitat':self.habitat.export(),'accessible':self.accessible,'emissions':self.emissions,'actions':self.actions}
        self.world.runtime.set_snapshot_metadata('cp02.predictor.v1',json.dumps(data,separators=(',',':')));self.world.save_snapshot(str(path))
    @classmethod
    def load(cls,path):
        w=d.OrganizationalWorld.load_snapshot(str(path));x=json.loads(w.runtime.snapshot_metadata('cp02.predictor.v1'))
        if x.get('schema')!=1:raise ValueError('Unsupported predictor schema')
        s=cls(w,restore_habitat(x['habitat']));s.accessible=x['accessible'];s.emissions=x['emissions'];s.actions=x['actions'];return s
    def fork(self):
        s=PredictorSession(self.world.fork(),restore_habitat(json.loads(json.dumps(self.habitat.export()))))
        s.accessible=json.loads(json.dumps(self.accessible));s.emissions=json.loads(json.dumps(self.emissions));return s


def memory_equalized(s):
    """Explicit diagnostic fork; RAW s_reg of A only, clock unchanged."""
    p=s.world.view('body').spec;old=s.world.runtime.observe(p.a);r=old.record;ref=s.world.runtime.observe(p.b).record.s_reg
    edit=d.ResearchStateEdit();edit.coordinate=p.a;edit.raw=d.pack_record(r.state,ref,r.dx,r.dy,r.dz,r.semantic);edit.label='DIAGNOSTIC: equalize A load to B; preserve clock'
    f=s.fork();f.world=s.world.diagnostic_fork([edit],True)
    f.actions.append({'modality':'DIAGNOSTIC_FORK','site':[p.a.x,p.a.y,p.a.z],'RAW_before':old.raw,'RAW_after':edit.raw,'clock_unchanged':f.world.runtime.observe(p.a).clock==old.clock})
    return f
