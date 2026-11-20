"""Bounded auxiliary native accumulation of normalized contact units.

ONE/TWO are research questions, not implemented lexical meanings. Two unit
media exist in every world; zero-load actuator routes decide which reaches a
common carrier. Fixed cue/query resources cannot consult the number of contacts.
"""
import argparse
from array import array
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback

from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, save_world_snapshot

ROOT = Path(__file__).resolve().parents[2]


def move(q, v, k=1):
    return [(q[i]+v[i]*k) % 67 for i in range(3)]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.pending')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')
    os.replace(temp, path)


def physical(world):
    r = world.runtime
    return {'tick': int(r.current_tick), 'RAW_sha256': hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clocks_sha256': hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def prepare(case):
    initial=[]; interfaces=[]; branches={}
    offset=case.get('translation',[0,0,0]); delay=case.get('delay',0)
    collector=move([25,25,20],offset)
    def add(q,v,load,state,role):
        p=d.InitialPlacement(); p.site=d.Coordinate(*q); p.raw=d.pack_record(state,load,*v,1); p.clock=0; p.role=role; initial.append(p)
    def port(name,q,v,state=1):
        c=d.ChannelSpec(); c.name=name; c.injection_site=d.Coordinate(*q); c.direction=d.Direction(*v); c.state=state; c.semantic=1; c.allow_probe=True; c.allow_experience=True
        p=d.InterfaceSpec(); p.name=name; p.channel=c; interfaces.append(p)
    for name,sign in [('A',1),('B',-1)]:
        base=move([20 if sign==1 else 30,20,20],offset); join=move(base,(0,0,-1))
        actor=move(join,(sign,0,0),-4-delay)
        if name not in case['contacts']: actor=move(actor,(0,1,0),12)
        opportunity=move(join,(-sign,0,1),-4-delay)
        medium=move(base,(sign,1,-1),-5-delay)
        state=case.get('actor_state',1)+(0 if name=='A' else 1)
        add(actor,(sign,0,0),case.get('actor_load',0),state,'Current zero-load actor '+name)
        add(opportunity,(-sign,0,1),0,1,'Identical physical opportunity '+name)
        add(medium,(sign,1,-1),case.get('unit_load',1),case.get('medium_state',1),'Normalized unit medium '+name)
        branches[name]={'base':base,'join':join,'sign':sign,'actor_initial':actor,'opportunity_initial':opportunity,'medium_initial':medium,
                        'post_contact_tick':5+delay,'post_contact_site':base,'collector_site':collector}
    # Same current cue and same future probes in all worlds. No class-specific bank.
    for label,tick,vector,lead in [('cue',10+delay,(0,0,1),3),('query1',77+delay,(0,0,-1),3),('query2',144+delay,(0,0,1),3)]:
        port('counter.'+label,move(collector,vector,-lead),vector)
    if case.get('regulation')in('onpath','offpath'):
        guard=move(collector,(0,0,-5))
        if case['regulation']=='offpath':guard=move(guard,(0,12,0))
        port('counter.free.guard',move(guard,(0,0,1),-3),(0,0,1))
    if case.get('regulation')in('branch_onpath','branch_offpath'):
        for name,b in branches.items():
            guard=move(b['base'],(b['sign'],1,-1),4)
            if case['regulation']=='branch_offpath':guard=move(guard,(0,12,0))
            port('counter.free.guard.'+name,move(guard,(0,0,1),-3),(0,0,1))
    extra=move([50,42,45],offset)
    port('extra.cue',move(extra,(-1,0,0),-3),(-1,0,0))
    port('extra.event',move(extra,(1,-1,0),-3),(1,-1,0))
    port('extra.query',move(extra,(-1,0,0),-3),(-1,0,0))
    sites=[(p.site.x,p.site.y,p.site.z) for p in initial]
    if len(sites)!=len(set(sites)): raise ValueError('Initial material collision: '+repr(sites))
    g={'N':67,'branches':branches,'collector':collector,'free_collector':move(collector,(0,0,-5)), 'extra':extra,
       'ticks':{'contact':5+delay,'collector':10+delay,'query1':77+delay,'other_acquisition':100+delay,'query2':144+delay},
       'resources':{'initial_materials':len(initial),'interfaces':len(interfaces),'normalized_units':2,'basic_buffer_bytes':32*67**3},
       'scope':'Prepared two-contact normalized-unit accumulation, not acquired cardinality or lexical ONE/TWO. Unit medium load is fixed1 in main cases. No hidden count enters a channel.'}
    r=d.OrganizationRecipe.research(67,initial,0);r.execution=d.TickOptions(d.Backend.LAZY,1);r.interfaces=interfaces;r.domain=g['scope'];r.options={'CPC8R.contact_cardinality':encode_metadata(g)}
    return r,g


def run(case,out,config_sha):
    out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__); dst=out/'executed_source'/'contact_cardinality.py';dst.parent.mkdir(parents=True);shutil.copyfile(source,dst)
    m={'schema':'CPC8R.contact_cardinality.measurements.v1','case':deepcopy(case),'configuration_sha256':config_sha,'source_sha256':sha(dst),
       'preparations':0,'diagnostic_forks':0,'continuations':0,'status':'RUNNING','frames':[],'snapshots':[], 'host_RAW_clock_edits_on_MAIN':[]}
    start=time.monotonic();requests=[]
    try:
        recipe,g=prepare(case);w=d.OrganizationalWorld.create(recipe);m['preparations']=1;m['geometry']=g
        def inp(port,load,tick,probe=False):
            rr=(w.probe if probe else w.submit)(port,load,tick);requests.append({'id':int(rr.id),'port':port,'payload':load,'requested_tick':tick,'kind':'probe' if probe else'experience','origin':'FIXED_OBSERVER_OPPORTUNITY_NOT_COUNT'})
        delay=case.get('delay',0)
        inp('counter.cue',5,7+delay);inp('counter.query1',7,74+delay,True);inp('counter.query2',7,141+delay,True)
        if case.get('regulation')in('onpath','offpath'):inp('counter.free.guard',0,7+delay)
        if case.get('regulation')in('branch_onpath','branch_offpath'):
            for name in('A','B'):inp('counter.free.guard.'+name,0,6+delay)
        inp('extra.cue',5,100+delay);inp('extra.event',11,100+delay);inp('extra.query',9,167+delay,True)
        def obs(q):return exact_observation(w.runtime.observe(d.Coordinate(*q)))
        boundary=[0]+[x+delay for x in(3,4,5,6,9,10,11,76,77,78,99,100,103,143,144,145,170)]
        for t in sorted(set(boundary)):
            w.run_until(t);frame={'tick':t,'physical':physical(w),'collector':obs(g['collector']),'free_collector':obs(g['free_collector']),
                'branches':{k:{'join':obs(v['join']),'base':obs(v['base'])}for k,v in g['branches'].items()},'extra':obs(g['extra'])}
            if t in [x+delay for x in(4,5,9,10,76,77,143,144)]:
                centers=[g['collector']] if t not in (4+delay,5+delay) else [v['join' if t==4+delay else'base'] for v in g['branches'].values()]
                frame['Moore27']=[{'center':q,'observations':[obs(move(q,(x,y,z))) for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]
            m['frames'].append(frame)
            if t in(0,10+delay,77+delay,144+delay):
                path=out/('T'+str(t)+'.deetsnap.gz'); storage=save_world_snapshot(w,path,compress=True);m['snapshots'].append({'path':path.name,'sha256':sha(path),'tick':t,'physical':physical(w),'storage':storage})
            m['last_complete_tick']=t;m['requests']=[{**x,'receipt':exact_receipt(w.runtime.receipt(x['id']))}for x in requests];m['elapsed_seconds']=time.monotonic()-start;put(out/'MEASUREMENTS.json',m)
        m.update(status='MEASURED',final_physical=physical(w),requests=[{**x,'receipt':exact_receipt(w.runtime.receipt(x['id']))}for x in requests])
    except BaseException as e:
        m.update(status='TECHNICAL_ERROR',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());raise
    finally:
        m['elapsed_seconds']=time.monotonic()-start;put(out/'MEASUREMENTS.json',m)
    summary={'id':case['id'],'contacts':case['contacts'],'readings':[{k:f[k]for k in('tick','collector','free_collector')}for f in m['frames']if f['tick']in(10+delay,77+delay,144+delay)]}
    print(json.dumps(summary,ensure_ascii=False));return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8')); cases=[c for c in cfg['cases'] if not a.case or c['id']==a.case]
    if not cases:raise ValueError('Unknown case')
    summaries=[run(c,a.out/c['id'],sha(a.config))for c in cases]
    put(a.out/'INDEX.json',{'schema':'CPC8R.contact_cardinality.index.v1','configuration_sha256':sha(a.config),'cases':summaries})
