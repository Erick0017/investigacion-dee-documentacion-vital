"""PI02 R01: controlled passive observation and direct-return calibration.

No T0, raw/clock writes or policy table. All material contributions use the
inherited interfaces. Calibration's imposed negative consequence is explicitly
researcher supplied and is not scored as useful autonomous action.
"""
from capacidades import pi01_traza_legal_base as trace
from app.native_tools import physical
VERSION='PI02.direct_return_calibration.R01'
N=67
DIRECT={0:(1,0,0),1:(0,1,0)}
def route(o):
    if o['state']<=0 or o['semantic']!=1:return None
    return next((k for k,v in DIRECT.items()if tuple(o['direction'])==v),None)
def observe(a,ticks,record):
    m=trace.get(a);origin=tuple(m['origin']);before=physical(a.world,occupation=True)
    frames=[]
    if record:
        for t in range(int(a.tick)+1,int(a.tick)+ticks+1):
            a.run_until(t);o=trace.obs(a,origin)
            frames.append({'tick':t,'center':o,'direct_route':route(o)})
    else:a.run_until(int(a.tick)+ticks)
    return {'version':VERSION,'mode':'observation_control','record_enabled':record,'before':before,'after':physical(a.world,occupation=True),'frames':frames,'material_inputs':[],'scope':'Whole owned OrganizationalWorld advances identically. One arm reads a fixed point every tick; the other does not. No material query or auditor signal.'}
def calibrate(a,ticks,penalty,delay):
    m=trace.get(a);origin=tuple(m['origin']);before=physical(a.world,occupation=True)
    end=int(a.tick)+ticks;first=None;feedback_tick=None;r=None;events=[];frames=[]
    for t in range(int(a.tick)+1,end+1):
        a.run_until(t);o=trace.obs(a,origin);selected=route(o)
        if selected is not None:events.append({'tick':t,'route':selected,'center':o})
        if first is None and selected is not None:
            first={'tick':t,'route':selected};feedback_tick=t+delay*N
            if penalty:
                if feedback_tick>end-2:raise ValueError('Frozen calibration horizon too short for admitted feedback')
                r=trace.submit_arrival(a,m['prefix']+'penalty'+str(selected),5,feedback_tick)
        if feedback_tick is not None and feedback_tick-2<=t<=feedback_tick+2:
            frames.append({'tick':t,'center':o,'context_radius3':trace.roi(a,3)})
    return {'version':VERSION,'mode':'direct_return_calibration','before':before,'after':physical(a.world,occupation=True),'first_native_return':first,'events':events,'fixed_feedback_tick':feedback_tick,'negative_receipt':None if r is None else trace.rr(a,r),'frames':frames,'sensor_inputs':0,'normalizer_inputs':0,'external_calibration_valence':penalty,'scope':'Development only: an imposed generic valence tests physical A/B transformation. Not learned timing, device discovery or useful task score.'}
def validate_literal(row):
    mode=row.get('modo')if isinstance(row,dict)else None
    if mode=='eci01-pi02-observar':
        if set(row)!={'modo','ticks','registro'}or type(row['registro'])is not bool:raise ValueError('Exact passive observation control fields required')
    elif mode=='eci01-pi02-calibrar-directo':
        if set(row)!={'modo','ticks','valencia','demora_periodos'}or type(row['valencia'])is not bool or type(row['demora_periodos'])is not int or not 1<=row['demora_periodos']<=3:raise ValueError('Exact declared calibration fields required')
    elif mode=='eci01-pi02-estado':
        if set(row)!={'modo'}:raise ValueError('No target or alternative answer field')
        return
    else:raise ValueError('Unknown PI02R01 literal')
    if type(row['ticks'])is not int or not 1<=row['ticks']<=500:raise ValueError('Bounded calibration1..500ticks')
def validate(a,row):validate_literal(row);trace.get(a)
def dispatch(a,row,*,directory=None,actuator='closed'):
    validate(a,row)
    if row['modo']=='eci01-pi02-observar':return observe(a,row['ticks'],row['registro'])
    if row['modo']=='eci01-pi02-calibrar-directo':return calibrate(a,row['ticks'],row['valencia'],row['demora_periodos'])
    return {'version':VERSION,'physical':physical(a.world),'origin':trace.get(a)['origin'],'center':trace.obs(a,tuple(trace.get(a)['origin'])),'scope':'External observer, not accessible Native memory'}
def operational_dependencies(a,directory):return {'version':VERSION,'environment_admitted':False,'scope':'Calibration-only code; no new external pending action'}
def uncertain(a):return False
