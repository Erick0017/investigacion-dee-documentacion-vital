"""Finite research mechanisms, not a general cognition or control policy.

Operational sources and full states are local to sistema/. No historical
results or laboratory files are read to generate any native response.
"""
from app.native_tools import physical,observe
from . import ic_body as body,ic_external as external,delayed_social as social

def admitted(a):
    if physical(a.world)['N']!=67:raise ValueError('N67 domain required')
    if not hasattr(a,'quantity'):raise ValueError('Existing native quantity owner required; no new world is created')

def state(a):
    admitted(a);p=social.get(a)
    from . import gate_world
    return{'physical':physical(a.world,occupation=True),'body':body.report(a),'external':external.saved(a),'received_relation':p,'gate_environment_instrument_not_native_memory':gate_world.get(a),'quantity_native':observe(a.world,a.quantity.geometry['center']),'reference_native':observe(a.world,a.quantity.geometry['reference_hub']),'scope':'Passive current physical and protocol state. Historical recorded maxima are not current access guarantees. Native neutral is distinct from no qualified response. Prepared actuator/codec/learning law are not attributed as invented by E1.'}

def attach(a,*,record=True):
    original=a.run_until;h=None;frames=[];b=body.get(a)
    if b and a.tick<b['end_tick']:h=body.attach(a,record=record)
    base=a.run_until
    if social.get(a):
        def advance(t):frames.extend(social.advance_until(a,t,base,record=record))
        a.run_until=advance
    return{'body_frames':[]if h is None else h['frames'],'social_frames':frames,'detach':lambda:setattr(a,'run_until',original)}

def advance(a,*,until,record=True):
    admitted(a)
    if until<a.tick:raise ValueError('No rewind; explicitly fork a documented checkpoint')
    h=attach(a,record=record)
    try:a.run_until(until)
    finally:h['detach']()
    return{'physical':physical(a.world,occupation=True),'body_frames':h['body_frames'],'social_frames':h['social_frames'],'environment_not_stepped':True,'warning':'A native-only interval does not step Pendulum; the gap is explicit. Use integrado-externo for a coupled continuation.'}

def experience(a,*,kind,options):
    admitted(a)
    if kind=='adquirir-ruta':
        h=attach(a)
        try:return body.ic.train(a,**options)
        finally:h['detach']()
    if kind=='programar':return body.arm(a,**options)
    if kind=='social':return social.begin(a,**options)
    if kind=='acceso-previo':
        from .recovery import preposition_social_access
        return preposition_social_access(a,**options)
    if kind=='acceso-consultar':
        from .recovery import query_social_access
        return query_social_access(a,**options)
    if kind=='proteger-retorno':
        from . import social_guard
        if 'record_tick'not in options:
            p=social.get(a)
            if not p or p['plan']['source_tick']<=a.tick+3:raise ValueError('Prepare a future social opportunity first; no retrospective timing rescue')
            options={**options,'record_tick':p['plan']['source_tick']-1}
        return social_guard.divert_record(a,**options)
    if kind=='puerta-preparar':
        from . import gate_world
        return gate_world.prepare(a,**options)
    if kind=='proteger-mensaje':
        from . import message_detour
        return message_detour.prepare(a,**options)
    if kind=='preparar-lateral':
        from . import lateral_social
        return lateral_social.prepare(a,**options)
    if kind=='separar-soportes':
        from . import support_separation
        return support_separation.prepare(a,**options)
    if kind=='puerta':
        from . import gate_world
        h=attach(a)
        try:return gate_world.run(a,**options)
        finally:h['detach']()
    raise ValueError('Explicit supported experience required')

def act_external(a,*,steps=1,mode='closed',feedback='cost',reset=False,seed=81017):
    admitted(a)
    if not 1<=steps<=64:raise ValueError('Finite1..64 external steps per explicit operation')
    saved=external.saved(a);readout=saved['readout']if saved else'magnitude';p=social.get(a)
    if readout not in('body','magnitude'):raise ValueError('This explicit command admits magnitude/body codecs only. A motor13 research state needs its separate finite clocked protocol; no silent fallback or clock rescue.')
    ports=saved.get('social_ports')if saved and readout=='magnitude'and saved.get('social_ports')else p['plan']['banks']if p and readout=='magnitude'else None
    h=attach(a)
    try:r=external.run(a,steps=steps,mode=mode,readout=readout,feedback=feedback,codec=2,reader='omit',reset=reset,seed=seed,stop_invalid=3,social_ports=ports)
    finally:h['detach']()
    r['body_frames']=h['body_frames'];r['social_frames']=h['social_frames'];return r
