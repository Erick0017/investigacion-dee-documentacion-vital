"""Explicit single-episode MAIN profile: native forecast meets actual consequence.

This profile extends the public CPC3 session; it never clones, restores or
copies native matter to compare. The input device encodes only an actually
observed current packet result. The v27 material gradient produces the marker.
Afterwards that marker is NOT decoded as a new forecast.
"""
import json
from .entity import Entity
from .central_comparison import declare_comparison_channels, present_current_actual_report, decode_current_comparison

PROFILE_SCHEMA='cpc3.central_comparison.profile.v1'
CHANNELS=('actual_report.negative','actual_report.positive')

class CentralComparisonEntity(Entity):
    preferred_horizon=46
    profile_name='comparacion'
    @classmethod
    def _adopt(cls,base):
        e=cls.__new__(cls);e.__dict__.update(base.__dict__);e.comparison_stage='ready';e.pending_expectation=None;e.last_report_tick=None;e.last_comparison_valid=False;e.last_report=None;e.expectation_invalidated=None;return e
    @classmethod
    def create(cls,**kwargs):
        e=cls._adopt(Entity.create(**kwargs));before=e.physical_digest();declare_comparison_channels(e)
        e.operation_calls.extend({'operation':'declare_interface','channel':n,'tick':e.tick,'scope':'INERT_INTERFACE_METADATA_BEFORE_FIRST_EXPERIENCE','physical_write':False} for n in CHANNELS)
        if e.physical_digest()!=before:raise RuntimeError('Inert interface declarations changed native matter')
        e._event('PREPARATION_PROFILE',{'profile':PROFILE_SCHEMA,'channels':list(CHANNELS),'prepared_before_first_experience':True,'physical_preparation_unchanged':True,'scope':'one forecast/consequence encounter; no automatic reuse or native absence detector'})
        return e
    def _limit(self,status,detail):
        p=self.observe();return self._event('INTERFACE_LIMIT',{'status':status,'detail':detail,'prediction_set':[False,True],'physical_output':p['physical_output'],'comparison':p.get('comparison_live'),'modality':'INTERFACE_NOT_NATIVE_ANSWER','profile':self.profile_name})
    def observe(self):
        p=Entity.observe(self);stage=getattr(self,'comparison_stage','ready');o=p['physical_output'];marker=o['active'] and o['direction'][2]!=0
        p['profile']=self.profile_name;p['comparison_stage']=stage
        if stage=='reported' or marker:
            p['prediction_set']=[False,True];p['forecast_domain']='OUTSIDE_FORECAST_DOMAIN_COMPARISON_CONTEXT'
            valid=bool(getattr(self,'last_comparison_valid',False) and self.tick==getattr(self,'last_report_tick',None))
            c=decode_current_comparison(self,True if valid else False)
            if not valid:c['presentation']=None;c['validity']='OUTSIDE_DECLARED_ONE_TICK_COMPARISON_WINDOW'
            p['comparison_live']=c
        else:p['forecast_domain']='SINGLETON_EXPECTATION_ALLOWED_WITHIN_FINITE_DOMAIN'
        return p
    def predict(self,horizon=None):
        if self.comparison_stage=='reported':return self._limit('OUTSIDE_FORECAST_DOMAIN','The current native marker represents a consequence encounter, not a reusable fresh forecast.')
        if self.pending_expectation is not None:return self._limit('ONE_PENDING_EXPECTATION_ALREADY_REGISTERED','Resolve the existing physical episode before requesting another; no hidden recreation occurs.')
        current=self.observe()['physical_output']
        if current['active'] and current['direction'][2]!=0:return self._limit('OUTSIDE_FORECAST_DOMAIN','Current native readout already has a comparison/context marker.')
        em=Entity.predict(self,self.preferred_horizon if horizon is None else horizon)
        self.pending_expectation={'emission_tick':em['emission_tick'],'target_tick':em['target_tick'],'direction':list(em['physical_output']['direction']),'represented':bool(len(em['prediction_set'])==1 and em['physical_output']['active'] and em['physical_output']['direction'][0] in (-1,1) and em['physical_output']['direction'][2]==0)}
        self.expectation_invalidated=None;self.comparison_stage='pending';return em
    def experience(self,symbol):
        if self.pending_expectation is not None:self.expectation_invalidated='INTERVENING_PHYSICAL_EXPERIENCE_REQUEST'
        return Entity.experience(self,symbol)
    def sense(self):
        if self.pending_expectation is not None:return self.compare()
        return Entity.sense(self)
    def compare(self):
        pending=self.pending_expectation
        if pending is None:return self._limit('NO_PENDING_COMPARABLE_EXPECTATION','No new consequence has been injected. The single-episode profile does not recreate an expectation.')
        if self.expectation_invalidated:return self._limit('EXPECTATION_INVALIDATED_BY_EXPERIENCE',self.expectation_invalidated)
        if not pending['represented']:return self._limit('NO_SINGLETON_NATIVE_EXPECTATION','The registered physical output did not represent either singleton; H0 is not assigned a fabricated expectation.')
        if self.tick>pending['target_tick']:return self._limit('MISSED_COMPARISON_WINDOW','The world passed the target. No clock reset, late matched answer or old result is injected.')
        self._advance_to(pending['target_tick']);live=Entity.observe(self)['physical_output']
        if not (live['active'] and live['direction'][0]==pending['direction'][0] and live['direction'][2]==0):
            self.expectation_invalidated='NATIVE_EXPECTATION_REPRESENTATION_CHANGED_BEFORE_ACTUAL';return self._limit('EXPECTATION_CHANGED_IN_NATIVE_EVOLUTION','The original forecast is retained in the audit, but cannot be physically paired by this protocol now.')
        # This helper samples ONLY the actual current consequence. It does not
        # receive the stored prediction set or a computed error as an argument.
        record=present_current_actual_report(self)
        admitted=record['input_receipt']['status']=='applied'
        represented=record['comparison_decoder']['represented_expectation_before_report'] is True
        self.last_comparison_valid=bool(admitted and represented);self.last_report_tick=self.tick;self.last_report=record;self.pending_expectation=None;self.comparison_stage='reported'
        if not self.last_comparison_valid:
            record['comparison_decoder']['presentation']=None;record['comparison_decoder']['validity']='REPORT_NOT_APPLIED_OR_EXPECTATION_OUTSIDE_DOMAIN'
        record['status']='CURRENT_NATIVE_COMPARISON_MEASURED' if self.last_comparison_valid else 'COMPARISON_UNRESOLVED'
        record['episode']={'emission_tick':pending['emission_tick'],'target_tick':pending['target_tick'],'native_readout_tick':self.tick,'matching':'single pending physical expectation and fixed target; no host error-to-memory feedback'}
        # Evaluation is after the physical encounter and is audit-only.
        record['audit_evaluations']=Entity.advance(self,0)['evaluations']
        return record
    def save(self,path):
        profile={'schema':PROFILE_SCHEMA,'profile':self.profile_name,'comparison_stage':self.comparison_stage,'pending_expectation':self.pending_expectation,'last_report_tick':self.last_report_tick,'last_comparison_valid':self.last_comparison_valid,'last_report':self.last_report,'expectation_invalidated':self.expectation_invalidated,'channels':list(CHANNELS),'single_episode_scope':True}
        self.operation_calls.append({'operation':'set_snapshot_metadata','key':PROFILE_SCHEMA,'tick':self.tick,'scope':'OPERATIVE_METADATA_NON_RAW','source':'USER_OR_AUDITOR_PERSISTENCE_REQUEST'})
        self.world.runtime.set_snapshot_metadata(PROFILE_SCHEMA,json.dumps(profile,separators=(',',':')));return Entity.save(self,path)
    @classmethod
    def load(cls,path):
        base=Entity.load(path)
        try:text=base.world.runtime.snapshot_metadata(PROFILE_SCHEMA);profile=json.loads(text)
        except (ValueError,TypeError) as error:raise ValueError('Snapshot has no CPC3 comparison profile; loading never installs missing interfaces or matter.') from error
        if profile.get('schema')!=PROFILE_SCHEMA:raise ValueError('Unsupported comparison profile metadata')
        if not set(CHANNELS).issubset({i.name for i in base.world.interfaces}):raise ValueError('Snapshot is missing its declared operational comparison interfaces; no preparation was silently installed.')
        e=cls._adopt(base)
        for key in ('comparison_stage','pending_expectation','last_report_tick','last_comparison_valid','last_report','expectation_invalidated'):setattr(e,key,profile[key])
        return e
