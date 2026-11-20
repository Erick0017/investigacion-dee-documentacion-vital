"""Exact, passive field/canal/functional descriptions, never native policies.

This module contains no advance, submit, edit, probe, timeout-as-absence or
physical-answer table. Missing samples remain missing. RAW and clock are ints.
"""
from array import array
import hashlib


def runtime(world):
    return world.runtime if hasattr(world,'runtime') else world


def record(value):
    r=value.record
    return {'tick':int(value.tick),'site':[value.coordinate.x,value.coordinate.y,value.coordinate.z],
        'raw':int(value.raw),'clock':int(value.clock),'state':int(r.state),
        'semantic':int(r.semantic),'s_reg':int(r.s_reg),'direction':[int(r.dx),int(r.dy),int(r.dz)],
        'active':r.state>0 and r.semantic!=5,'raw_present':value.raw!=0}


def fields(world,ports):
    import dee_thinking as d
    rt=runtime(world)
    return {name:record(rt.observe(d.Coordinate(*site))) for name,site in ports.items()}


def digest(world):
    rt=runtime(world)
    return {'tick':int(rt.current_tick),'N':int(rt.dimension),
        'raw_sha256':hashlib.sha256(array('Q',rt.raw_copy()).tobytes()).hexdigest(),
        'clock_sha256':hashlib.sha256(array('Q',rt.clock_copy()).tobytes()).hexdigest()}


def torus_displacement(source,target,n):
    return [((target[i]-source[i]+n//2)%n)-n//2 for i in range(3)]


def neighborhood(world,center):
    n=runtime(world).dimension;sites={}
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for dz in (-1,0,1):
                sites[','.join(map(str,(dx,dy,dz)))]=[(center[i]+q)%n for i,q in enumerate((dx,dy,dz))]
    current=fields(world,sites);neighbors=[v for k,v in current.items() if k!='0,0,0']
    proposals=[v for v in neighbors if any(v['direction']) and
               [(v['site'][i]+v['direction'][i])%n for i in range(3)]==list(center)]
    return {'center':current['0,0,0'],'moore26':{k:v for k,v in current.items() if k!='0,0,0'},
        'n_active':sum(v['active'] for v in neighbors),
        'active_direction_sum':[sum(v['direction'][i] for v in neighbors if v['active']) for i in range(3)],
        'directional_proposals_without_activity_prefilter':proposals,
        'scope':'Current field/context/proposals only. Does not infer occupied-center branch, unique parentage or necessity.'}


def signature(samples,fields=('state','semantic','s_reg','direction','clock')):
    return {name:None if value is None else {key:value.get(key) for key in fields}
            for name,value in samples.items()}


def compare_signatures(left,right):
    names=sorted(set(left)|set(right));rows=[]
    for name in names:
        a,b=left.get(name),right.get(name)
        different=[] if a==b else ['missing'] if a is None or b is None else [k for k in set(a)|set(b) if a.get(k)!=b.get(k)]
        rows.append({'component':name,'different_fields':sorted(different),'left':a,'right':b})
    return {'equal':left==right,'differences':[x for x in rows if x['different_fields']],
            'scope':'External panel comparison, not an information-bit or identity verdict'}


def receipt(value):
    return {'id':int(value.id),'kind':str(value.kind),'status':str(value.status),
        'requested_tick':int(value.requested_tick),
        'effective_tick':None if value.effective_tick is None else int(value.effective_tick),
        'channels':list(value.channels),'reason':value.reason}


def operation_state(world):
    rt=runtime(world)
    value={'physics':digest(world),'channels':list(rt.channel_names),
        'receipts':[receipt(x) for x in rt.receipts],
        'metadata':dict(rt.snapshot_metadata_entries),'protocol_phase':rt.protocol_phase,'paused':rt.paused}
    if hasattr(world,'interfaces'):
        value['interfaces']=[{'name':x.name,'channel':x.channel.name,
            'site':[x.channel.injection_site.x,x.channel.injection_site.y,x.channel.injection_site.z],
            'direction':[x.channel.direction.dx,x.channel.direction.dy,x.channel.direction.dz],
            'state':int(x.channel.state),'semantic':int(x.channel.semantic),
            'experience':x.channel.allow_experience,'probe':x.channel.allow_probe} for x in world.interfaces]
        value['external_operations']=list(world.external_operations)
        value['protocols']=[{'id':x.id,'kind':x.kind,'next_capture':int(x.next_capture),
            'steps':[{'input_tick':int(s.input_tick),'read_tick':int(s.read_tick),'input':int(s.input),
                'receipt_ids':list(s.receipt_ids),'targets':[[q.x,q.y,q.z] for q in s.targets],
                'captured':[record(r) for r in s.captured]} for s in x.steps]} for x in world.protocols]
    return value


def capture(world,ports,context_sites=()):
    rt=runtime(world)
    samples=fields(world,ports)
    return {'tick':int(rt.current_tick),'N':int(rt.dimension),'ports':samples,
        'signature':signature(samples),'contexts':{str(tuple(q)):neighborhood(world,q) for q in context_sites},
        'receipts':[receipt(x) for x in rt.receipts],
        'scope':'PASSIVE_OBSERVATION, no world advance/edit/probe; orphan/nonactive fields retained'}

