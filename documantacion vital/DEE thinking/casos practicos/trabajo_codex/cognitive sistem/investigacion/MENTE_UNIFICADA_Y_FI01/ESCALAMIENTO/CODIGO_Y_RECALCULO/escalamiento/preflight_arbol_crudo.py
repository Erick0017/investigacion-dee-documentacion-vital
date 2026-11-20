"""Offline geometry only: no DEE import, no world creation, no physical ticks.

The script does NOT simulate v27 and does not evaluate values or choose an
action. It expands fixed source/zero-turn coordinates and planned join times.
Each raw scalar has its own physical interface. All raw leaves of a frame have
the same injection tick. Native validation and a learned downstream relation
are mandatory before claiming a capacity.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

FACTORS={8:[4],16:[4,2],32:[4,4],64:[4,4,2],128:[4,4,4]}
ROOTS={'left':(16,16,16),'right':(50,50,16)}

def add(p,v,k=1):return tuple(p[i]+k*v[i] for i in range(3))

def forest(count,N=67):
    if count not in FACTORS:raise ValueError('Declared levels8/16/32/64/128 only')
    factors=FACTORS[count];nodes=[];leaves=[];turns=[];segments=[];opened=set();edges=[]
    def visit(side,p,t,level,path):
        name=side+'.'+path
        node={'id':name,'site':list(p),'join_tick_relative':t,'arity':factors[level]}
        nodes.append(node);opened.add(p)
        if level==0:
            vectors=[(-1,-1),( -1,1),(1,-1),(1,1)]
            for j,(sx,sy) in enumerate(vectors):
                origin=add(p,(sx,sy,1));v=(-sx,-sy,-1)
                leaf={'id':name+'.raw.'+str(j),'side':side,'site':list(origin),'direction':list(v),'injection_tick_relative':t-1,'head':list(p),'head_tick_relative':t}
                leaves.append(leaf);opened.add(origin)
                segments.append({'id':leaf['id'],'kind':'raw_input','from':list(origin),'to':list(p),'start_tick':t-1,'end_tick':t,'direction':list(v),'join':name})
            return
        spacing=3**level+1
        offsets=[(-1,-1),(-1,1),(1,-1),(1,1)] if factors[level]==4 else[(-1,0),(1,0)]
        for j,(sx,sy) in enumerate(offsets):
            child=(p[0]+sx*spacing,p[1]+sy*spacing,p[2]+spacing+2)
            ct=t-spacing-2
            visit(side,child,ct,level-1,path+'.'+str(j))
            junction=add(child,(0,0,-1),2);turn_origin=add(junction,(sx,sy,1));v=(-sx,-sy,-1)
            turns.append({'id':name+'.turn.'+str(j),'site':list(turn_origin),'direction':list(v),'injection_tick_relative':ct+1,'payload':0,'purpose':'Fixed direction resource, never a relevant scalar'})
            opened.add(turn_origin)
            for k in range(3):opened.add(add(child,(0,0,-1),k))
            for k in range(spacing+1):opened.add(add(junction,v,k))
            segments.extend([
              {'id':name+'.child.'+str(j)+'.vertical','kind':'intermediate_product','from':list(child),'to':list(junction),'start_tick':ct,'end_tick':ct+2,'direction':[0,0,-1],'join':name+'.turnjoin.'+str(j)},
              {'id':name+'.turn.'+str(j),'kind':'zero_turn','from':list(turn_origin),'to':list(junction),'start_tick':ct+1,'end_tick':ct+2,'direction':list(v),'join':name+'.turnjoin.'+str(j)},
              {'id':name+'.child.'+str(j)+'.diagonal','kind':'redirected_product','from':list(junction),'to':list(p),'start_tick':ct+2,'end_tick':t,'direction':list(v),'join':name},
            ])
            edges.append({'parent':name,'child':side+'.'+path+'.'+str(j),'spacing':spacing,'planned_delay':spacing+2})
    for side,p in ROOTS.items():visit(side,p,0,len(factors)-1,'root')
    if len(leaves)!=count:raise AssertionError((len(leaves),count))
    # Canonical independent indices: left even, right odd. No value aggregation.
    for side,parity in [('left',0),('right',1)]:
        local=[x for x in leaves if x['side']==side]
        for j,q in enumerate(local):q['component_index']=2*j+parity
    assert sorted(x['component_index']for x in leaves)==list(range(count))
    times=sorted(set(x['injection_tick_relative']for x in leaves));assert len(times)==1
    invalid=[list(p)for p in opened if any(v<0 or v>=N for v in p)]
    sources=leaves+turns;interfaces={};duplicates=[]
    for q in sources:
        k=(tuple(q['site']),q['injection_tick_relative'])
        if k in interfaces:duplicates.append([interfaces[k],q['id']])
        interfaces[k]=q['id']
    left={tuple(x['site'])for x in leaves if x['side']=='left'}
    right={tuple(x['site'])for x in leaves if x['side']=='right'}
    # This checks direct planned crossings only, not Moore/context dependencies.
    visits={}
    for seg in segments:
        for tick in range(seg['start_tick'],seg['end_tick']+1):
            site=add(seg['from'],seg['direction'],tick-seg['start_tick'])
            visits.setdefault((tick,site),[]).append(seg['id'])
    intended={(n['join_tick_relative'],tuple(n['site']))for n in nodes}
    intended.update((s['end_tick'],tuple(s['to']))for s in segments if s['kind']=='zero_turn')
    extra_crossings=[{'tick':t,'site':list(p),'segments':ids}for(t,p),ids in sorted(visits.items())if len(ids)>1 and(t,p)not in intended]
    return {'schema':'MUFI01.geometry_preflight.v1','classification':'OFFLINE_PREPARATION_NOT_NATIVE_EXECUTION','native_ticks':0,'worlds_created':0,
      'variables':count,'N':N,'factors_bottom_up':factors,'raw_injection_ticks':times,'root_join_tick':0,
      'planned_sensor_latency_ticks':-times[0],'independent_raw_interfaces':len(leaves),'generic_zero_turn_resources':len(turns),
      'tree_join_nodes':len(nodes),'opened_corridor_positions':len(opened),'invalid_coordinates':invalid,'duplicate_injection_sites_and_ticks':duplicates,
      'unintended_direct_spacetime_crossings':extra_crossings,'direct_spacetime_check_does_not_cover_neighborhood_physics':True,
      'disjoint_raw_source_sets':not(left&right),'new_world_required':True,'R10_N26_history_not_imported':True,
      'basic_native_buffer_estimate_bytes':32*N**3,'buffer_estimate_not_total_RAM':True,
      'RAM_gate':'Do not instantiate unless measured process RSS stays below512MiB and host free headroom is adequate; dense Python placements are additional.',
      'decoder':'NOT_YET_DEFINED: freeze learned downstream comparator and its common reader after blockA before native B reserves.',
      'scope':'Source geometry and nominal timings only. Does not verify transport, reducer output, recurrence, acquired reference, usefulness or128-variable capability.',
      'nodes':nodes,'raw_sources':leaves,'zero_resources':turns,'segments':segments,'edges':edges,'opened':list(map(list,sorted(opened)))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--N',type=int,default=67);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    rows=[forest(k,args.N)for k in FACTORS]
    data={'schema':'MUFI01.scaling_preflight.v1','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'physics_executed':False,'rows':rows,
      'N_buffer_bytes':{str(N):32*N**3 for N in(26,67,101,127,131)},
      'dense_recipe_warning':'Existing compile_geometry loops overN³ and materializes a Python InitialPlacement per non-open position. Do not treat32N³ as process peak; profile preparation separately.'}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{k:r[k] for k in('variables','N','planned_sensor_latency_ticks','independent_raw_interfaces','generic_zero_turn_resources','tree_join_nodes','opened_corridor_positions','invalid_coordinates','duplicate_injection_sites_and_ticks','basic_native_buffer_estimate_bytes')}for r in rows]))
if __name__=='__main__':main()
