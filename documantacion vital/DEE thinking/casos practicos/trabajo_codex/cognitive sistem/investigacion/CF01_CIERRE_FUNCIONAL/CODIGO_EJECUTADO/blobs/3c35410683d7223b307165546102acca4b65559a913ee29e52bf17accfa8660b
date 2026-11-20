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
REVISION = 'CF01.R9.protocol.1'


def saved(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY]) if KEY in entries else None


def put(a, value):
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(json.loads(json.dumps(value, allow_nan=False))))


def geometry(a):
    s = native.saved(a)
    if not s or s['schema'] != 'MI02.unified.r9':
        raise ValueError('CF01 requires a real lived unified R9 snapshot; no implicit reconstruction')
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
    return {'physical': physical(a.world,occupation=True), 'service':saved(a),
            'witness':witness(a),
            'attribution': 'Fixed prepared anatomy; acquired own/private/context fields. x0 is default-left AND query, not an exclusive decision to ask.'}


def pulse(a, *, participant, value, delay=1, horizon=48, repeat=1, spacing=2, cut='none'):
    """Finite interface calibration on identified diagnostic copies, no retries."""
    if participant not in ('B_datum','A_left','A_right') or type(value) is not int or not 0<=value<=255:
        raise ValueError('Declared scalar interface and uint8 test sample required')
    if not 1<=delay<=52 or not delay+8<=horizon<=256:
        raise ValueError('Fixed finite delay/horizon required')
    if not 1<=repeat<=32 or not 1<=spacing<=26 or delay+(repeat-1)*spacing+8>horizon or cut not in ('none','minus_bus','plus_bus'):
        raise ValueError('Fixed bounded sample train and predeclared diagnostic branch required')
    g=geometry(a); start=a.tick; before=witness(a)
    if participant=='B_datum':
        site=body.xyz(a,g['B'],(1,-1,1));direction=(0,0,0)
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
