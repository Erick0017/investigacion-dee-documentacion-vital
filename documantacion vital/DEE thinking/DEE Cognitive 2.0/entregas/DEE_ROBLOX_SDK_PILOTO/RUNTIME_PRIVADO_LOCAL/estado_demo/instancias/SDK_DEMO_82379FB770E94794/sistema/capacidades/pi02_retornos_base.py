"""PI02 R02: native-return initiated work, fixed bridge and real consequences.

The physical carrier requests work. Periodicity, backpressure, the MA/FI
address map and valence law are prepared. No per-job query or normalizer.
"""
from pathlib import Path
import hashlib,json
from capacidades import pi02_diagnostico_base as diag
from capacidades import pi01_traza_legal_base as trace
from capacidades import progresion_integrada_01 as pi01
from app.native_tools import physical
from dee_thinking.persistence import encode_metadata,decode_metadata
VERSION='PI02.native_return_work.R02B';KEY='DEE.Cognitive.PI02.R02.environment'
N=67;BUSY=4*N+40;FOLDER='PI02_RESOURCE_BANK_R02';SHAM=(0,12,0)
def get(a):
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit PI02environment admission required; never reset on reopening')
    m=decode_metadata(e[KEY])
    if m['version']not in('PI02.native_return_work.R02',VERSION):raise ValueError('PI02 environment version mismatch')
    return m
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def fixtures(series):
    pairs=[(11,3),(15,6),(4,12),(13,2)]if series=='desarrollo'else[(12,5),(18,4),(7,2),(14,3),(17,9),(19,8),(11,3),(16,4),(4,11),(10,3),(18,7),(13,6)]
    return [{'public':{'left':l,'right':r},'private_lock':-1 if i<3 or i>=8 else 1}for i,(l,r)in enumerate(pairs)]
def admit(a,row,directory):
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already lived PI02 environment; no reset')
    trace.get(a);home=Path(directory)/FOLDER
    if home.exists():raise ValueError('Existing operational folder; no unpaired recreation')
    (home/'reservoir').mkdir(parents=True);(home/'collected').mkdir()
    records=[];fs=fixtures(row['serie'])
    for i in range(len(fs)):
        payload=hashlib.sha256(('PI02.R02 resource '+str(i)).encode('ascii')).digest()*2
        p=home/'reservoir'/('%04d.bin'%i);p.write_bytes(payload);records.append({'episode':i,'file':'reservoir/'+p.name,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
    # New sham sources are anatomy only, shared by all experimental arms.
    for k,v in trace.PENALTY.items():
        site=tuple((SHAM[i]-v[i])%N for i in range(3))
        if int(trace.obs(a,site)['raw'])!=0:raise ValueError('Sham port has nonzero causal RAW, including state0')
        trace.declare(a,'PI02.R02.sham'+str(k),site,v,600001+k)
    m={'version':VERSION,'series':row['serie'],'arm':row['brazo'],'episode':0,'fixtures':fs,'resource_folder_relative':FOLDER,'reservoir':records,'resources':0,'committed_resources':[],'uncertain':False,'last_detector_active':False,'last_detector_tick':int(a.tick),'detector_scope':'active SEM1 A/B rising edge at inherited origin; no s_reg/target argument','assistance':'Prepared recurrence,0MA/1FIcodec,busy308,consequence delay268,external lock','in_progress':None}
    save(a,m);return {'version':VERSION,'admitted':True,'tick':int(a.tick),'material_inputs':0,'native_anatomy_added':'Two unused sham interfaces only, no initial carrier installed','new_T0':False,'inherited_PI01_resources':pi01.resources_valid(a,directory)}
class Tap:
    def __init__(self,a,m,events,frames):self.base=a;self.m=m;self.events=events;self.frames=frames;self.latest=None;self.busy=False;self.feedback_tick=None;self.origin=tuple(trace.get(a)['origin'])
    @property
    def world(self):return self.base.world
    @property
    def tick(self):return int(self.base.tick)
    def run_until(self,tick):
        if int(tick)<self.tick:raise ValueError('No rewind')
        for t in range(self.tick+1,int(tick)+1):
            self.base.run_until(t);o=trace.obs(self.base,self.origin);r=diag.route(o)
            active=r is not None;new=active and not self.m['last_detector_active'];self.m['last_detector_active']=active;self.m['last_detector_tick']=t
            self.latest={'tick':t,'route':r,'new_event':new,'center':o}
            if new:self.events.append({'tick':t,'route':r,'busy':self.busy,'center':o})
            if self.feedback_tick is not None and self.feedback_tick-2<=t<=self.feedback_tick+2:
                self.frames.append({'tick':t,'center':o,'context_radius3':trace.roi(self.base,3)})
def effect(m,fixture,response,actuator,directory):
    ep=m['episode'];command=response if actuator=='closed'and m['arm']!='nulled'else None
    if command is not None and(type(command)is not int or command not in(-1,0,1)):raise ValueError('Invalid Native command; no fallback')
    accepted=command is not None and command==fixture['private_lock'];record=None
    if accepted:
        home=Path(directory)/FOLDER;src=home/'reservoir'/('%04d.bin'%ep);payload=src.read_bytes();dst=home/'collected'/src.name
        with dst.open('xb')as f:f.write(payload)
        if dst.read_bytes()!=payload:raise ValueError('Resource copying failed')
        record={'episode':ep,'file':'collected/'+dst.name,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()};m['committed_resources'].append(record);m['resources']+=1
    return {'response':response,'applied_command':command,'accepted':accepted,'private_lock_used_after_action':fixture['private_lock'],'resource':record,'resources_after':m['resources']}
def live(a,ticks,directory,actuator):
    m=get(a)
    if m['uncertain']or m['in_progress']:raise ValueError('Preserved uncertain/incomplete future; no replay')
    before=physical(a.world,occupation=True);target=int(a.tick)+ticks;events=[];frames=[];rows=[];tap=Tap(a,m,events,frames);excluded=[]
    try:
        while tap.tick<target:
            tap.run_until(tap.tick+1);event=tap.latest
            if not event['new_event']:continue
            if m['episode']>=len(m['fixtures']):excluded.append({'tick':tap.tick,'reason':'declared finite work bank exhausted'});continue
            if target-tap.tick<BUSY:excluded.append({'tick':tap.tick,'reason':'fixed end-of-window capacity fence308ticks'});continue
            q=tap.tick;r=event['route'];fixture=m['fixtures'][m['episode']];m['in_progress']={'episode':m['episode'],'start_tick':q,'phase':'native_requested_work'};save(a,m)
            tap.busy=True;tap.feedback_tick=q+4*N
            # Existing fixed physical codecs; no private lock passed to either.
            access=pi01.use_selected_access(tap,r,fixture['public'],directory)
            eff=effect(m,fixture,access['physical_response'],actuator,directory)
            m['in_progress']['phase']='actual_effect_committed';save(a,m)
            receipt=None
            if not eff['accepted']and m['arm']!='omit':
                name=('PI02.R02.sham'if m['arm']=='sham'else trace.get(a)['prefix']+'penalty')+str(r)
                if tap.tick>=tap.feedback_tick-1:raise ValueError('Fixed feedback deadline missed; do not rescue')
                receipt=trace.submit_arrival(a,name,5,tap.feedback_tick)
            tap.run_until(q+BUSY)
            rows.append({'episode':m['episode'],'request_tick':q,'native_route':r,'request_center':event['center'],'selected_access':access,'effect':eff,'feedback_tick':q+4*N,'feedback':None if receipt is None else trace.rr(a,receipt),'sensor_inputs':0,'normalizer_inputs':0,'busy_until':q+BUSY})
            m['episode']+=1;m['in_progress']=None;tap.busy=False;tap.feedback_tick=None;save(a,m)
    except BaseException:
        m['uncertain']=True;save(a,m);raise
    save(a,m)
    return {'version':VERSION,'before':before,'after':physical(a.world,occupation=True),'horizon_tick':target,'rows':rows,'all_detected_returns':events,'busy_discarded':sum(x['busy']for x in events),'capacity_fence_events':excluded,'encounter_frames':frames,'native_requested_work':len(events),'admitted_work':len(rows),'formed_responses':sum(x['selected_access']['physical_response']is not None for x in rows),'actual_resources':sum(x['effect']['accepted']for x in rows),'assistance':'Host supplies elapsed time; native arrivals trigger work. Recurrence,busy and0MA/1FI mapping are prepared. No learned timing or general initiative claim.'}
def validate_literal(row):
    mode=row.get('modo')if isinstance(row,dict)else None
    if mode=='eci01-pi02-iniciar':
        if set(row)!={'modo','serie','brazo'}or row['serie']not in('desarrollo','reservaA')or row['brazo']not in('real','omit','sham','nulled'):raise ValueError('Explicit frozen environment/arm only')
    elif mode=='eci01-pi02-vivir':
        if set(row)!={'modo','ticks'}or type(row['ticks'])is not int or not 400<=row['ticks']<=6000:raise ValueError('Finite generic time window400..6000')
    else:diag.validate_literal(row)
def validate(a,row):
    validate_literal(row);trace.get(a)
    if row['modo']=='eci01-pi02-vivir':get(a)
def dispatch(a,row,*,directory=None,actuator='closed'):
    validate(a,row)
    if row['modo']=='eci01-pi02-iniciar':return admit(a,row,directory)
    if row['modo']=='eci01-pi02-vivir':return live(a,row['ticks'],directory,actuator)
    return diag.dispatch(a,row,directory=directory,actuator=actuator)
def operational_dependencies(a,directory):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return {'PI02_R02_not_admitted':True}
    m=get(a);home=Path(directory)/FOLDER
    for item in m['reservoir']+m['committed_resources']:
        p=home/item['file']
        if not p.is_file()or p.stat().st_size!=item['bytes']or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Missing/altered PI02 operational resource')
    return {'version':VERSION,'episode':m['episode'],'resources':m['resources'],'in_progress':m['in_progress'],'uncertain':m['uncertain']}
def uncertain(a):
    if KEY not in dict(a.world.runtime.snapshot_metadata_entries):return False
    m=get(a);return bool(m['uncertain']or m['in_progress'])
