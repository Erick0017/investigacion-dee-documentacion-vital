"""Finite native policy session; no laboratory fixtures, forks or output tables.

This is a distinct prepared N67 individual/component, not an installation in
the continuous basal MAIN. Geometry contains the update rule; experience
physically selects its policy state and subsequent source action.
"""
from array import array
from datetime import datetime,timezone
import hashlib,json,os,time
from pathlib import Path
import dee_thinking as d
from .revisable_selection import prepare,A,B,ACTION0,ACTION1
from .comparison import observed

SCHEMA='cpc3.finite_policy_session.v1'
class FinitePolicySession:
    preferred_horizon=None
    profile_name='politica'
    def __init__(self,world,metadata):
        self.world=world;self.metadata=metadata;self.actual_submitted=False;self.operation_calls=[];self.events=[];self.event_sink=None
    @classmethod
    def create(cls,*,roles='Q_INFORMATIVE',truth=1,origin=(30,30,30),n=67):
        w,m=prepare(roles=roles,truth=truth,origin=origin,n=n);s=cls(w,m);s._event('PREPARATION',{'profile':SCHEMA,'native_update_rule':'finite prepared preserveP_on_match/switchQ_on_discrepancy','initial_policy':'P','environment_resources':m['resources'],'scope':'one consumed-resource revision and future source use; no learned general utility rule or repeated reversals'});return s
    @property
    def tick(self):return self.world.runtime.current_tick
    def _event(self,kind,item):
        x={'kind':kind,'tick':self.tick,'monotonic_ns':time.monotonic_ns(),'wall_utc':datetime.now(timezone.utc).isoformat(),**item};self.events.append(x)
        if self.event_sink:
            p=Path(self.event_sink);p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('a',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
        return x
    def _physical_inputs(self):
        if self.tick==2 and not self.actual_submitted and self.metadata['actual_enabled']:
            # Independent environment's current explicit class, not a forecast,
            # error, route choice or history-dependent desired output.
            actual={'tick':2,'observed_explicit_class':self.metadata['truth'],'modality':'DECLARED_EXTERNAL_ENVIRONMENT_SENSOR'}
            for tag in ('negative','positive'):
                name='actual.'+tag+'.'+str(actual['observed_explicit_class']);r=self.world.submit(name,1,2);self.operation_calls.append({'operation':'submit','tick':2,'channel':name,'value':1,'receipt_id':r.id,'source_actual':actual,'two_fixed_encodings_of_one_observation':True})
            self.actual_submitted=True;self._event('EXTERNAL_CURRENT_ACTUAL_REPORT',{'actual':actual,'comparison_error_not_computed':True})
    def _until(self,tick):
        if not isinstance(tick,int) or tick<self.tick:raise ValueError('Cannot rewind the native policy session')
        while self.tick<tick:
            self._physical_inputs();start=self.tick;self.world.advance();self.operation_calls.append({'operation':'advance','from':start,'to':self.tick})
    def _receipts(self):
        return [{'id':c['receipt_id'],'channel':c['channel'],'status':str(self.world.runtime.receipt(c['receipt_id']).status),'reason':self.world.runtime.receipt(c['receipt_id']).reason,'effective_tick':self.world.runtime.receipt(c['receipt_id']).effective_tick} for c in self.operation_calls if c['operation']=='submit']
    def observe(self):
        ports=self.world.view('selection').spec.ports;tick=self.tick;comparison=[];policy=[];actions=[];info=[];physical=[]
        if tick==6:
            for tag in ('negative','positive'):
                o=observed(self.world.runtime.observe(ports[tag+'_comparison']));physical.append(o)
                if o['active'] and o['direction'][1:]==[1,1]:comparison.append({'physical_output':o,'presentation':'coincidencia' if o['direction'][0]==0 else 'discrepancia','port':tag})
        if tick==10:
            for key in self.metadata['branches']:
                o=observed(self.world.runtime.observe(ports[key+'_policy']));physical.append(o)
                if o['active'] and tuple(o['direction']) in (A,B):policy.append({'physical_output':o,'policy':'P' if tuple(o['direction'])==A else 'Q','port':key})
        if tick==11:
            for key in self.metadata['branches']:
                for source,direction in [('P',ACTION0),('Q',ACTION1)]:
                    o=observed(self.world.runtime.observe(ports[key+'_'+source+'_action']));physical.append(o)
                    if o['active'] and tuple(o['direction'])==direction:actions.append({'physical_output':o,'source':source,'port':key+'_'+source})
        if tick==14:
            for key in self.metadata['branches']:
                for source in ('P','Q'):
                    o=observed(self.world.runtime.observe(ports[key+'_'+source+'_information']));physical.append(o)
                    if o['active'] and o['direction'][1:]==[1,0] and o['direction'][0] in (-1,1):info.append({'physical_output':o,'source_route':source,'observed_explicit_class':o['direction'][0],'port':key+'_'+source})
        return {'tick':tick,'profile':self.profile_name,'current_comparisons':comparison,'current_policy_products':policy,'current_source_actions':actions,'current_information_products':info,'physical_outputs':physical,'receipts':self._receipts(),'operational_forks':0,'modality':'PASSIVE_OBSERVATION_OF_CURRENT_NATIVE_RECORDS','domain_status':'CURRENT_DECLARED_FUNCTIONAL_WINDOW' if tick in (6,10,11,14) else 'NO_PUBLISHED_READOUT_AT_THIS_TICK','limits':'Fixed designed update rule; finite consumed resources. Absence here is missing emission, not a numeric false report. No optimal/general/indefinitely revisable utility claimed.'}
    def advance(self,ticks=1):
        if not isinstance(ticks,int) or ticks<0:raise ValueError('Nonnegative integer ticks required')
        self._until(self.tick+ticks);return self.observe()
    def source(self):
        if self.tick>11:return self._event('INTERFACE_LIMIT',{'status':'OUTSIDE_CURRENT_SOURCE_ACTION_WINDOW','detail':'The earlier choice is historical; this operation does not return a cached answer.','current_observation':self.observe(),'modality':'INTERFACE_NOT_NATIVE_ANSWER'})
        self._until(11);o=self.observe();c=o['current_source_actions'];sources=sorted({x['source'] for x in c});source=sources[0] if len(c)==1 and len(sources)==1 else None
        return self._event('NATIVE_SOURCE_SELECTION',{'source':source,'emission_tick':self.tick,'physical_output':c[0]['physical_output'] if len(c)==1 and source else None,'physical_outputs':c,'status':'CURRENT_NATIVE_SOURCE_ACTION' if source else 'UNRESOLVED_OR_MULTIPLE_NATIVE_ACTIONS','modality':'NATIVE_EVOLUTION_THEN_FIXED_CURRENT_READOUT','scope':'one experience-conditioned policy revision; not an optimal or repeated utility estimate'})
    def sense(self):
        if self.tick<=2:
            self._until(3);return self._event('EXTERNAL_ACTUAL_EXPERIENCE',{'receipts':self._receipts(),'modality':'EXPERIENCE_PROTOCOL','scope':'actual explicit environment report at2, not Python-computed discrepancy'})
        if self.tick<=14:
            self._until(14);o=self.observe();return self._event('NATIVE_INFORMATION_RECEIVED',{'information':o['current_information_products'],'emission_tick':14,'modality':'NATIVE_EVOLUTION_THEN_FIXED_CURRENT_READOUT','scope':'content actually arriving through the selected geometric source route'})
        return self._event('INTERFACE_LIMIT',{'status':'FINITE_RESOURCE_PROTOCOL_COMPLETED','current_observation':self.observe(),'modality':'INTERFACE_NOT_NATIVE_ANSWER'})
    def compare(self):
        if self.tick>6:return self._event('INTERFACE_LIMIT',{'status':'OUTSIDE_CURRENT_COMPARISON_WINDOW','current_observation':self.observe(),'modality':'INTERFACE_NOT_NATIVE_ANSWER'})
        self._until(6);o=self.observe();return self._event('NATIVE_COMPARISON',{'comparisons':o['current_comparisons'],'emission_tick':6,'modality':'NATIVE_EVOLUTION_THEN_FIXED_CURRENT_READOUT','scope':'physical comparison of received P content and actual later consequence'})
    def predict(self,horizon=None):return self._event('INTERFACE_LIMIT',{'status':'FORECAST_NOT_IMPLEMENTED_IN_POLICY_PROFILE','detail':'This individual revises source access, not a reusable future predictor.','modality':'INTERFACE_NOT_NATIVE_ANSWER'})
    def experience(self,symbol):return self._event('INTERFACE_LIMIT',{'status':'ARBITRARY_EXPERIENCE_NOT_IMPLEMENTED_IN_FINITE_POLICY_PROFILE','detail':'Only the declared actual environment report at2 is an input in this prepared finite apparatus.','modality':'INTERFACE_NOT_NATIVE_ANSWER'})
    def physical_digest(self):return {'tick':self.tick,'raw_sha256':hashlib.sha256(array('Q',self.world.runtime.raw_copy()).tobytes()).hexdigest(),'clock_sha256':hashlib.sha256(array('Q',self.world.runtime.clock_copy()).tobytes()).hexdigest()}
    def save(self,path):
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);self.operation_calls.append({'operation':'set_snapshot_metadata','key':SCHEMA,'tick':self.tick,'scope':'OPERATIVE_METADATA_NON_RAW'});self.operation_calls.append({'operation':'save_snapshot','path':str(p),'tick':self.tick,'scope':'FILESYSTEM_OPERATIONAL_PERSISTENCE'});x={'schema':SCHEMA,'metadata':self.metadata,'actual_submitted':self.actual_submitted,'operation_calls':self.operation_calls,'events':self.events};self.world.runtime.set_snapshot_metadata(SCHEMA,json.dumps(x,separators=(',',':')));self.world.save_snapshot(str(p));return {'path':str(p),'tick':self.tick,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'physical':self.physical_digest()}
    @classmethod
    def load(cls,path):
        w=d.OrganizationalWorld.load_snapshot(str(path))
        try:x=json.loads(w.runtime.snapshot_metadata(SCHEMA))
        except (TypeError,ValueError) as error:raise ValueError('Not a saved finite policy session; no physical preparation is installed while loading') from error
        if x.get('schema')!=SCHEMA:raise ValueError('Unsupported finite policy session schema')
        if 'selection' not in w.organization_ids:raise ValueError('Snapshot lacks its native selection view')
        s=cls(w,x['metadata']);s.actual_submitted=x['actual_submitted'];s.operation_calls=x['operation_calls'];s.events=x['events'];return s
