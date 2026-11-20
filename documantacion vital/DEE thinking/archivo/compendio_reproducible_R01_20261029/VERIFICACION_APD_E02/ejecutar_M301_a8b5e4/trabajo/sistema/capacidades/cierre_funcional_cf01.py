"""CF01 fixed environmental protocols over an existing complete R9 life.

No constructor, target-dependent reader, memory write, host action selector or
fallback policy. The environmental availability is exogenous. Raw scalar
measurements are optional; they are not translated into a desired action.
"""
import json
from dee_thinking.persistence import encode_metadata, decode_metadata
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import integracion_distribuida_mi02_r6 as native
from app.native_tools import physical

KEY = 'DEE.Cognitive.System.1.1.CF01.service.v1'
REVISION = 'CF01.R9.protocol.4'


def saved(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY]) if KEY in entries else None


def put(a, value):
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(json.loads(json.dumps(value, allow_nan=False))))


def geometry(a):
    s = native.saved(a)
    if not s or s['schema'] != 'MI02.unified.r9':
        raise ValueError('CF01 requires a real lived unified R9 snapshot; no implicit reconstruction')
    if int(a.world.runtime.dimension)!=26 or s['geometry']['N']!=26 or s['geometry']['A']!=[6,14,14]or s['geometry']['B']!=[19,14,14]:
        raise ValueError('Outside the measured CF01 R9 geometry domain; do not silently reuse coordinates in another architecture')
    return s['geometry']


def witness(a):
    g = geometry(a)
    return {
        'tick': int(a.tick), 'A': body.obs(a, g['A']), 'B': body.obs(a, g['B']),
        'own': [body.obs(a, body.xyz(a, g['A'],v)) for v in ((-1,1,1),(1,1,1))],
        'private_B': [body.obs(a, body.xyz(a,g['B'],v)) for v in ((-1,1,1),(1,1,1))],
        'context_A': [body.obs(a,body.xyz(a,g['A'],v)) for v in ((-1,1,-1),(1,1,-1))],
        'B_datum': body.obs(a, body.xyz(a,g['B'],(1,-1,1))),
        'query_gate': body.obs(a,g['query'][-1]['head']),
    }


def message_witness(a):
    # Explicit R9 N26 waypoint coverage, not an asserted unique lineage.
    sites={'minus':((18,13,13),(17,12,12),(16,11,11),(14,11,11),(14,13,9),(14,19,9),(12,19,9),(9,19,9),(8,18,10),(7,17,11),(6,16,12),(5,15,13)),
           'plus':((20,13,13),(21,12,12),(22,11,11),(24,11,11),(24,13,9),(24,19,9),(0,19,9),(3,19,9),(4,18,10),(5,17,11),(6,16,12),(7,15,13))}
    return {k:[body.obs(a,p)for p in v]for k,v in sites.items()}


def state(a):
    return {'protocol_code_revision':REVISION,'physical': physical(a.world,occupation=True), 'service':saved(a),
            'witness':witness(a),
            'attribution': 'Fixed prepared anatomy; acquired own/private/context fields. x0 is default-left AND query, not an exclusive decision to ask.'}


def pulse(a, *, participant, value, delay=1, horizon=48, repeat=1, spacing=2, cut='none'):
    """Finite interface calibration on identified diagnostic copies, no retries."""
    if participant not in ('B_datum','B_incoming','A_left','A_right') or type(value) is not int or not 0<=value<=255:
        raise ValueError('Declared scalar interface and uint8 test sample required')
    if not 1<=delay<=52 or not delay+8<=horizon<=256:
        raise ValueError('Fixed finite delay/horizon required')
    if not 1<=repeat<=32 or not 1<=spacing<=26 or delay+(repeat-1)*spacing+8>horizon or cut not in ('none','minus_bus','plus_bus'):
        raise ValueError('Fixed bounded sample train and predeclared diagnostic branch required')
    g=geometry(a); start=a.tick; before=witness(a)
    if participant=='B_datum':
        site=body.xyz(a,g['B'],(1,-1,1));direction=(0,0,0)
    elif participant=='B_incoming':
        site=body.xyz(a,g['B'],(0,-2,0));direction=(1,1,1)
    else:
        spec=next(v for v in body.get(a)['external_sensors'] if v['name']==('sin' if participant=='A_left' else 'cos'))
        site=spec['origin'];direction=spec['direction']
    requests=[body.send(a,'CF01.pulse.'+participant,site,direction,start+delay+i*spacing,value)for i in range(repeat)]
    if cut!='none':
        p=[12,19,9]if cut=='minus_bus'else[0,19,9]
        requests.append(body.send(a,'CF01.diagnostic.'+cut,p,(0,0,0),start+7,0,sem=4))
    frames=[]
    for tick in range(start+1,start+horizon+1):
        a.run_until(tick);f=witness(a);f['message_waypoints']=message_witness(a);frames.append(f)
    return {'revision':REVISION,'before':before,'request':body.receipts(a,requests)[0],'requests':body.receipts(a,requests),
            'frames':frames,'after':witness(a), 'no_retry_or_forced_admission':True}


def episode(a, *, availability, mode='intact', public=None, private=None, offset=0, trace=False):
    """One fixed native contact/return opportunity; state continues between calls.

    Availability is a world condition, never an action instruction. The host
    installs both potential return paths before observing the native action.
    Action arises from material present at the contact sites. Consequences
    return through v27, not a host update of learned fields.
    """
    if availability not in (-1,1) or mode not in ('intact','omit_return'):
        raise ValueError('Exogenous availability +/-1 and declared return mode required')
    if type(offset) is not int or not 0<=offset<=52:
        raise ValueError('Fixed sensor phase offset0..52 required')
    if public is not None and (len(public)!=2 or any(type(v)is not int or not 0<=v<=255 for v in public)):
        raise ValueError('Two raw public scalar measurements, not an action label')
    if private is not None and (type(private)is not int or not 0<=private<=255):
        raise ValueError('Private B raw scalar measurement required')
    g=geometry(a);start=a.tick;before=witness(a)
    crit=391+782*max(0,(a.tick+90-391+781)//782)
    plan=body.cycle_plan(a,{'Q':g['A']},availability,crit)
    requests=[]
    if mode=='intact':
        for v in plan['sources']:
            requests.append(body.send(a,v['name'],v['site'],v['direction'],v['tick'],v['payload']))
    if public is not None:
        for name,value in zip(('sin','cos'),public):
            sensor=next(v for v in body.get(a)['external_sensors'] if v['name']==name)
            requests.append(body.send(a,'CF01.public.'+name,sensor['origin'],sensor['direction'],crit-22-offset,value))
    if private is not None:
        requests.append(body.send(a,'CF01.private.B',body.xyz(a,g['B'],(1,-1,1)),(0,0,0),crit-70-offset,private))
    frames=[]
    times=range(crit-75-offset,crit+81) if trace else sorted(set((crit-71-offset,crit-69-offset,crit-24-offset,crit-17-offset,crit-16,crit-15,crit,crit+3,crit+40,crit+80)))
    for tick in times:
        a.run_until(tick);f=witness(a)
        f['contacts']={str(r):body.obs(a,body.xyz(a,g['A'],(r,-1,-1))) for r in (-1,0,1)}
        frames.append(f)
    contact=next(f for f in frames if f['tick']==crit-15)['contacts']
    emitted=[];useful=[];wrong=[]
    for r in (-1,0,1):
        v=contact[str(r)]
        if v['state']>0 and v['semantic']==1 and v['direction'] in ([r,-1,-1],[r,-1,0]):
            emitted.append(r)
            (useful if (1 if r>=0 else -1)==availability else wrong).append(r)
    s=saved(a)or{'revision':REVISION,'episodes':0,'native_queries':0,'useful':0,'wrong':0,'silence':0}
    row={'episode':s['episodes'],'start_tick':start,'critical_tick':crit,'end_tick':a.tick,
         'availability':availability,'mode':mode,'public_raw':public,'private_B_raw':private,'phase_offset':offset,
         'emitted':emitted,'useful':useful,'wrong':wrong,'silence':not emitted,'conflict':bool(useful and wrong),
         'query_at_contact':bool(contact['0']['state']>0 and contact['0']['semantic']==1 and contact['0']['direction']==[0,-1,-1])}
    s['episodes']+=1;s['native_queries']+=int(row['query_at_contact']);s['useful']+=int(bool(useful));s['wrong']+=int(bool(wrong));s['silence']+=int(not emitted)
    s['last_episode']=row;put(a,s)
    ns=native.saved(a);ns['index']+=1;native.put(a,ns)
    view=body.get(a);view['index']=ns['index'];body.put(a,view)
    return {'revision':REVISION,'before':before,'plan':plan,'requests':body.receipts(a,requests),'row':row,
            'frames':frames,'after':witness(a),
            'attribution':'Resources and exogenous conditions fixed before output. No host reads a target to select a reader, action or memory update. Metrics remain auditor-only.'}


def task(a, *, opportunities=None, steps=1, reset=False, actuator='closed', feedback='intact', measurements=None):
    """Fixed two-gate work queue, external to v27; no policy inside the bridge.

    A job passes only if a unique native motor command reaches the currently
    available gate. A failed attempt leaves that job in place. The next gate
    is the next exogenous job, never chosen from the agent's expected answer.
    The environmental contact and native return remain the existing v27
    experiment. The external actuator-null arm tests useful external effects,
    NOT removal of that native return (a separate feedback arm does the latter).
    """
    if not 1<=steps<=32 or actuator not in ('closed','nulled') or feedback not in ('intact','omit_return'):
        raise ValueError('Bounded steps and explicit actuator/feedback modes required')
    if measurements is not None and (not 1<=len(measurements)<=64 or any(len(pair)!=2 or any(type(v)is not int or not 0<=v<=255 for v in pair)for pair in measurements)):
        raise ValueError('Finite sequence of two raw public scalar measurements required')
    s=saved(a)or{'revision':REVISION,'episodes':0,'native_queries':0,'useful':0,'wrong':0,'silence':0}
    env=s.get('external_gate_queue')
    if opportunities is not None:
        if not 1<=len(opportunities)<=64 or any(v not in(-1,1)for v in opportunities):
            raise ValueError('Finite exogenous +/-1 gate job list required')
        if env is not None and not reset:
            raise ValueError('External environment exists: continue it or declare an explicit reset; DEE never resets')
        history=list(s.get('closed_environment_records',[]))
        if env is not None:history.append(env)
        s['closed_environment_records']=history
        env={'law':'CF01.two_gate_work_queue.v1','jobs':list(opportunities),'cursor':0,'attempts':0,
             'completed':0,'external_resets':len(history),'created_at_native_tick':a.tick,
             'public_measurements':measurements,'sensor_index':0,
             'neutral_rule':'No external action for silence, invalid or conflicting outputs. Neutral is the bridge, not a native decision.',
             'state_owner':'External environment; not participant memory or a source of desired actions.'}
        s['external_gate_queue']=env;put(a,s)
    elif measurements is not None:
        raise ValueError('A measurement sequence belongs to the declared external world; change it only with explicit external reset')
    if env is None:raise ValueError('Declare an initial external gate queue, not an implicit favourable world')
    rows=[]
    for _ in range(steps):
        if env['cursor']>=len(env['jobs']):break
        available=env['jobs'][env['cursor']]
        before_env=json.loads(json.dumps(env))
        samples=env.get('public_measurements')
        current_measurement=None if samples is None else samples[env.get('sensor_index',0)%len(samples)]
        result=episode(a,availability=available,mode=feedback,public=current_measurement,trace=False)
        material=result['row']['emitted']
        native_command=(1 if material[0]>=0 else -1)if len(material)==1 else None
        command=native_command if actuator=='closed' else None
        completed=bool(command==available)
        env['attempts']+=1
        env['sensor_index']=env.get('sensor_index',0)+1
        if completed:env['cursor']+=1;env['completed']+=1
        env['last_command']=command;env['last_native_command']=native_command;env['last_native_tick']=a.tick
        s=saved(a);s['external_gate_queue']=env;put(a,s)
        rows.append({'environment_before':before_env,'native':result,'formed_native_command':native_command,
                     'executed_external_command':command,'actuator_mode':actuator,'feedback_mode':feedback,
                     'job_completed':completed,'environment_after':json.loads(json.dumps(env)),
                     'annulment_point':'After native material output decoding, only external actuation is nulled.'if actuator=='nulled'else None})
    return{'rows':rows,'final':state(a),'bridge':'Fixed directional transduction, no solver or target-dependent routing.',
           'scope':'Simple external discrete task, not an industrial simulator or learned Pendulum control. Job progress changes future opportunities; native fields are never written by the host.'}


def decode_window(result):
    """Target-blind fixed one-tick sample-and-hold at the same motor sites.

    This is an instrument/actuator contract, NOT learned recovery. It never
    examines availability, utility, memories, previous verdicts or a target.
    A simultaneous conflict invalidates that sample, not a choice of winner.
    """
    critical=result['row']['critical_tick'];samples=[]
    for tick in (critical-16,critical-15):
        frame=next(f for f in result['frames']if f['tick']==tick);values=[]
        for r in (-1,0,1):
            q=frame['contacts'][str(r)]
            if q['state']>0 and q['semantic']==1 and q['direction']in([r,-1,-1],[r,-1,0]):values.append(r)
        samples.append({'tick':tick,'material_roles':values,'command':(1 if values[0]>=0 else -1)if len(values)==1 else None,'simultaneous_conflict':len(values)>1})
    # A conflict at the deadline is not repaired using an older sample.
    if samples[-1]['simultaneous_conflict']:return {'rule':'latest_unique_with_max_hold1tick.v1','samples':samples,'command':None,'source_tick':None,'reason':'deadline_conflict'}
    chosen=next((s for s in reversed(samples)if s['command']is not None),None)
    return {'rule':'latest_unique_with_max_hold1tick.v1','samples':samples,'command':None if chosen is None else chosen['command'],
            'source_tick':None if chosen is None else chosen['tick'],'reason':'no_native_output'if chosen is None else'current'if chosen['tick']==critical-15 else'fixed_hold_one_tick'}


def classify(a, *, measurements, reference=None, actuator='closed', feedback='intact', reset=False):
    """External calibrated gate, fixed physics-facing codec, no action policy.

    `reference` belongs ONLY to the environment's gate law. Its computed gate
    sets material contact conditions and scores the actually executed command;
    neither reference nor desired command is injected into A. Only the two raw
    measurements are submitted through the previously fixed peripheral ports.
    The native acquired spatial relation may match or fail that world law.
    """
    if not 1<=len(measurements)<=32 or any(len(p)!=2 or any(type(v)is not int or not 0<=v<=64 for v in p)for p in measurements):
        raise ValueError('1..32 raw two-scalar jobs, values0..64 required')
    if reference is not None and(type(reference)is not int or not -64<=reference<=64)or actuator not in ('closed','nulled')or feedback not in ('intact','omit_return'):
        raise ValueError('Declared external calibration, actuator and feedback modes required')
    geometry(a);rows=[]
    s=saved(a)or{'revision':REVISION,'episodes':0,'native_queries':0,'useful':0,'wrong':0,'silence':0}
    prior=s.get('calibrated_gate')
    reference=(prior['reference']if prior is not None else 7)if reference is None else reference
    if reset:
        if prior is not None:s.setdefault('closed_calibrated_gates',[]).append(prior)
        prior=None
    env=prior or{'law':'CF01.calibrated_gate.v1','attempts':0,'passed':0,'backlog':[],'reference':reference,'created_at_native_tick':a.tick}
    if env['reference']!=reference:
        raise ValueError('This existing external gate has another calibration; declare an explicit external reset, never silently change its law')
    s['calibrated_gate']=env;put(a,s)
    for pair in measurements:
        # The environment determines its own gate; this result is NOT an E1 action.
        available=1 if pair[0]+reference>=pair[1] else -1
        before=json.loads(json.dumps(env))
        result=episode(a,availability=available,public=list(pair),mode=feedback,trace=False)
        decoded=decode_window(result)
        command=decoded['command']if actuator=='closed'else None
        passed=bool(command==available)
        env['attempts']+=1;env['passed']+=int(passed)
        if not passed:env['backlog'].append(list(pair))
        env['last_native_tick']=a.tick;env['last_command']=command
        s=saved(a);s['calibrated_gate']=env;put(a,s)
        rows.append({'environment_before':before,'raw_measurements':list(pair),'available_gate':available,
                     'environment_reference_not_injected':reference,'native':result,'fixed_output_sampling':decoded,
                     'executed_external_command':command,'actuator_mode':actuator,'feedback_mode':feedback,'job_passed':passed,
                     'environment_after':json.loads(json.dumps(env))})
    return {'rows':rows,'final':state(a),
            'attribution':'ENVIRONMENT computes its calibrated gate and consequences. ENTE supplies native material directions. INSTRUMENT samples the same two fixed ticks target-blind, holds at most1tick, and maps direction to command. The host never chooses an E1 response.',
            'scope':'Prepared calibrated comparison/application, not acquisition of an abstract numeric concept, learned reader selection or general policy. Old single-tick failures remain separate results.'}
