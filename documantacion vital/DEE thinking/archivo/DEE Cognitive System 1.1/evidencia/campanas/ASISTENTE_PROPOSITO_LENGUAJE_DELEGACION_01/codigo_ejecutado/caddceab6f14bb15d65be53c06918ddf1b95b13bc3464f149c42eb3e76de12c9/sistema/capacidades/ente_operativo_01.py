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

def task(a,*,jobs=None,steps=1,reference=None,reset=False,actuator='closed',feedback='real'):
    """A fixed external FIFO offers the same pending job until it is completed.

    This is environmental scheduling, not an acquired retry policy. Native
    commands and actual contact effects remain exactly the existing core.
    """
    if type(steps)is not int or not 1<=steps<=32:raise ValueError('Fixed1..32 attempts required')
    if jobs is not None and(not 1<=len(jobs)<=64 or any(len(p)!=2 or any(type(v)is not int or not 0<=v<=64 for v in p)for p in jobs)):
        raise ValueError('1..64 raw two-scalar jobs0..64 required')
    s=saved(a)or{'revision':REVISION,'attempts':0,'completed':0,'native_valid':0,'wrong':0,'silence':0,'environments':[]}
    q=s.get('queue')
    if jobs is not None:
        if q is not None and not reset:raise ValueError('Existing FIFO: continue it or explicitly reset the external queue only')
        if q is not None:s.setdefault('closed_queues',[]).append(q)
        q={'law':'EO01.raw_FIFO_actual_action.v1','jobs':[list(p)for p in jobs],'cursor':0,'attempts':0,'completed':0,'first_attempt_completed':0,'current_job_attempts':0,'created_at_native_tick':int(a.tick),'schedule':'One fixed opportunity per attempt; no host action policy and no native retry-initiative claim'}
        s['queue']=q;put(a,s)
    if q is None:raise ValueError('Declare an initial raw FIFO, never create a favourable implicit task')
    rows=[]
    for i in range(steps):
        if q['cursor']>=len(q['jobs']):break
        job=list(q['jobs'][q['cursor']]);before=json.loads(json.dumps(q))
        result=classify(a,measurements=[job],reference=reference if i==0 else None,reset=reset if i==0 else False,actuator=actuator,feedback=feedback)
        native=result['rows'][0];q['attempts']+=1;q['current_job_attempts']+=1
        if native['job_completed']:
            q['first_attempt_completed']+=int(q['current_job_attempts']==1);q['completed']+=1;q['cursor']+=1;q['current_job_attempts']=0
        q['last_tick']=int(a.tick);s=saved(a);s['queue']=q;put(a,s)
        rows.append({'queue_before':before,'native':native,'queue_after':json.loads(json.dumps(q))})
    return{'rows':rows,'queue':q,'final':state(a),'attribution':'FIFO progress and repeated opportunities belong to the external environment. Native signals choose actions; only actual executed action can complete a job. Completion with retries is not first-attempt accuracy.'}
