"""Auxiliary candidate: a native reader survives one update, then becomes empty.

Persistent learned scalar fields are distinct from that consumable reader.
Later generic probes reuse the same geometry without any host clearing.
"""
import json
from types import SimpleNamespace
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import arquitectura_distribuida_mi02_r8 as n
from capacidades.geometria_distribuida_mi02 import compile_geometry
from app.native_tools import physical
KEY='DEE.Cognitive.System.1.1.MI02.ephemeral_reader.v1'

def saved(a):
    m=dict(a.world.runtime.snapshot_metadata_entries);return decode_metadata(m[KEY])if KEY in m else None

def recipe():
    N=17;C=[8,8,8];f=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=N)))
    def p(v):return tuple(n.xyz(f,C,v))
    anchors={p((-1,0,1)):(2,(0,0,0)),p((0,0,1)):(0,(0,0,0)),p((1,0,1)):(0,(0,0,0))}
    for r in(-1,1):
        for v in((2*r,1,1),(2*r,2,1),(r,2,1),(0,2,1)):anchors[p(v)]=(0,(0,0,0))
    M=[list(p(v))for v in[(-1,1,1),(1,1,1)]];data=list(p((1,-1,1)));opened={tuple(C),tuple(data),*map(tuple,M)}
    for r in(-1,0,1):opened.add(p((r,-1,-1)))
    g={'schema':'MI02.ephemeral_reader.r1','N':N,'Q':C,'memories':M,'datum_site':data,'anchors':[{'site':list(k),'load':v[0],'direction':list(v[1])}for k,v in sorted(anchors.items())],'opened':[list(v)for v in sorted(opened)],'prepared':'Five coplanar alive neighbours aroundQ when memories acquired; sixth neighbour supplied by the current datum. Persistent memory support outside Q neighbourhood. Frame bias2 is prepared, not learned.','hypothesis':'Generic moving probe plus datum permits one native comparative update. Q then decays below its support condition, restoring input availability without deleting learned fields.','not_claimed':'General comparison, exact unbiased equality, self-initiated reading or integration into MAIN. Output cone and magnitude domain must be checked.'}
    return compile_geometry(N,opened,anchors),g

def acquire(a,*,geometry,values=(32,10)):
    if saved(a):raise ValueError('Already prepared, use current learned fields')
    g=json.loads(json.dumps(geometry));rr=[];t=a.tick+4
    for i,v in enumerate(values):
        if v is not None:rr.append(n.send(a,'MI02.ephemeral.memory.'+str(i),g['memories'][i],(0,0,0),t+4*i,int(v)))
    a.run_until(t+12);s={'geometry':g,'history_raw_samples':list(values),'reads':0};a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(s));return{'requests':n.receipts(a,rr),'after':state(a)}

def state(a):
    s=saved(a)
    if not s:raise ValueError('No lived ephemeral reader')
    g=s['geometry'];return{'physical':physical(a.world,occupation=True),'Q':n.obs(a,g['Q']),'memories':[n.obs(a,p)for p in g['memories']],'datum':n.obs(a,g['datum_site']),'reads':s['reads'],'scope':'Auxiliary new life, no inherited MAIN knowledge or word meanings.'}

def teach_empty(a,*,values):
    """Explicit later learning, never replacement of a nonempty memory."""
    s=saved(a)
    if not s or len(values)!=2 or any(type(v)is not int or not 0<=v<=160 for v in values):raise ValueError('Two explicit scalar experiences required')
    g=s['geometry']
    if any(n.obs(a,p)['raw']!='0'for p in g['memories']):raise ValueError('No overwriting or silent reteaching of a lived reference')
    before=state(a);rr=[];t=a.tick+4
    for i,v in enumerate(values):rr.append(n.send(a,'MI02.ephemeral.memory.'+str(i),g['memories'][i],(0,0,0),t+4*i,v))
    a.run_until(t+12);s['history_raw_samples']=list(values);s['explicit_late_acquisition']=True;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(s))
    return{'before':before,'requests':n.receipts(a,rr),'after':state(a),'explicit_new_learning_not_recovery':True}


def read(a,*,objects,spacings=(17,19,23),probe=True):
    if not 1<=len(objects)<=32 or any(v is not None and(type(v)is not int or not 0<=v<=160)for v in objects)or any(v<6 for v in spacings):raise ValueError('Finite declared raw scalar observations required')
    s=saved(a)
    if not s:raise ValueError('Untrained preparation must be explicit, never rebuilt')
    g=s['geometry'];rows=[]
    for j,value in enumerate(objects):
        start=a.tick;t=start+2;before=state(a);rr=[n.send(a,'MI02.ephemeral.probe',g['Q'],(0,0,-1),t,0)]if probe else[]
        if value is not None:rr.append(n.send(a,'MI02.ephemeral.current_datum',g['datum_site'],(0,0,0),t,int(value)))
        frames=[]
        for at in range(t,t+5):
            a.run_until(at);frames.append({'tick':at,'Q':n.obs(a,g['Q']),'datum':n.obs(a,g['datum_site']),'outputs':[n.obs(a,n.xyz(a,g['Q'],(r,-1,-1)))for r in(-1,0,1)],'memories':[n.obs(a,p)for p in g['memories']]})
        response=frames[1]['Q'];code=response['direction'][0]if n.qualified(response)else None
        a.run_until(start+spacings[j%len(spacings)]);s['reads']+=1
        rows.append({'index':s['reads'],'raw_current_observation':value,'before':before,'frames':frames,'native_class':code,'requests':n.receipts(a,rr),'after_Q':n.obs(a,g['Q']),'no_memory_or_clock_reset':True,'no_expected_result_supplied':True})
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(s));return{'rows':rows,'final':state(a),'probe_present':probe,'assistance':'One generic probe and one current scalar packet per read. Same fixed ports and frame; no per-answer banks, no host comparison or cleanup.'}
