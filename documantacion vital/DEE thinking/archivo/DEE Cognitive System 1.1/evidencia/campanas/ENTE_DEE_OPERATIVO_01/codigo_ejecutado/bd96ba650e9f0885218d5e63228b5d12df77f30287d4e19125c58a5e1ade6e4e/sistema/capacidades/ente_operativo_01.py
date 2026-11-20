"""EO01: servicio operativo con consecuencia externa posterior a la acción.
La geometría es R9 heredada; no reconstruye vidas ni escribe campos físicos.
El puente interpreta sólo el lector fijo y ejecuta su comando. La calibración
es una propiedad privada del mundo externo, no entrada del participante.
"""
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import cierre_funcional_cf01 as cf
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.EO01.service.v1'
REVISION='EO01.external_contact.protocol.3'
def saved(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY]) if KEY in entries else None
def put(a,s):
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(json.loads(json.dumps(s,allow_nan=False))))
def state(a):
    cf.geometry(a)
    return {'protocol_code_revision':REVISION,'physical':physical(a.world,occupation=True),'service':saved(a),'witness':cf.witness(a),
            'assistance':'Prepared R9 anatomy; fixed two-sample reader with hold<=1tick; external laws and generic supplies. No host action policy.','legacy_cf01_is_not_the_new_feedback':True}
def classify(a,*,measurements,reference=None,actuator='closed',feedback='real',reset=False,trace=False,offset=0,cut='none',private_B=None,message_cut='none',social_valve=None,B_actuator='closed'):
    """Continue one life. Explicit environmental reset never resets DEE."""
    if not 1<=len(measurements)<=32 or any(len(p)!=2 or any(type(v)is not int or not 0<=v<=64 for v in p)for p in measurements):
        raise ValueError('1..32 pairs of raw scalars 0..64 required')
    if reference is not None and(type(reference)is not int or not -64<=reference<=64):raise ValueError('External reference outside declared domain')
    if actuator not in('closed','nulled')or feedback not in('real','omit','decoupled')or cut not in('none','path','sham'):raise ValueError('Explicit fixed control mode required')
    cf.geometry(a)
    s=saved(a)or{'revision':REVISION,'attempts':0,'completed':0,'native_valid':0,'wrong':0,'silence':0,'environments':[]}
    env=s.get('environment')
    if env is None or reset:
        if env is not None:s['environments'].append(env)
        legacy=cf.saved(a)or{}
        default=legacy.get('calibrated_gate',{}).get('reference',8)
        env={'law':'EO01.calibrated_tactile_gate.v1','reference':default if reference is None else reference,
             'created_at_native_tick':int(a.tick),'attempts':0,'completed':0,'backlog':[],
             'boundary':'External environmental state, never used by native reader.','last_actuator_posture':None}
    elif reference is not None and reference!=env['reference']:
        raise ValueError('Declare reset=True to change environmental calibration; DEE itself continues')
    if social_valve is not None and type(social_valve)is not bool:raise ValueError('Explicit valve construction flag required')
    if B_actuator not in('closed','nulled'):raise ValueError('Explicit B actuator control required')
    env['social_valve_enabled']=env.get('social_valve_enabled',False)if social_valve is None else social_valve
    s['environment']=env;put(a,s);rows=[]
    # Import only operative system code, never laboratory, verdicts or targets.
    from capacidades.ente_operativo_01_core import external_episode
    for pair in measurements:
        result=external_episode(a,public=list(pair),reference=env['reference'],actuator=actuator,feedback=feedback,trace=trace,offset=offset,cut=cut,private_B=private_B,message_cut=message_cut,social_valve=env['social_valve_enabled'],B_actuator=B_actuator)
        env['attempts']+=1;s['attempts']+=1
        command=result['formed_native_command'];ok=bool(result['job_completed'])
        s['native_valid']+=int(command is not None);s['silence']+=int(command is None);s['wrong']+=int(command is not None and not ok)
        s['completed']+=int(ok);env['completed']+=int(ok)
        if not ok:env['backlog'].append(list(pair))
        env['last_actuator_posture']=result.get('observed_result',{}).get('actuator_posture')
        env['last_native_tick']=int(a.tick)
        if result.get('social_actuation')is not None:
            env['reference']=result['social_actuation']['reference_after']
            env['last_social_actuation']=result['social_actuation']
        # This queue is an external record only: no choice of retry or input.
        s['environment']=env;s['last_episode']=result['row'];put(a,s);rows.append(result)
    return {'revision':REVISION,'rows':rows,'totals_this_call':{'requested_jobs':len(rows),'native_valid':sum(r['formed_native_command']is not None for r in rows),'completed':sum(bool(r['job_completed'])for r in rows)},
            'final':state(a),'attribution':'Inputs are raw scalar observations. Material consequences describe measured post-action contact/pose. No target, calibration or correct next command is injected; all acquired field changes use v27.'}
def social(a,*,value,cut='none'):
    """A private B observation using the fixed inherited channel; not a solved message."""
    return cf.pulse(a,participant='B_incoming',value=value,delay=1,horizon=80,cut=cut)
