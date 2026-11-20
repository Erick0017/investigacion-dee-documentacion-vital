"""Compile declared fixed native transport opportunities, never a learned policy.

Every turn uses ordinary v27 arriving carriers. The participant, not this
compiler, determines whether a command is present. No field is read here.
"""
from itertools import product,combinations

VECTORS=[q for q in product((-1,0,1),repeat=3)if any(q)]
def sign(q):return tuple((x>0)-(x<0)for x in q)
def move(q,d,k,n=67):return[(q[i]+d[i]*k)%n for i in range(3)]

def turning_inputs(incoming,outgoing):
    incoming=tuple(incoming);outgoing=tuple(outgoing)
    if incoming==outgoing:return []
    candidates=[]
    for u,v in combinations(VECTORS,2):
        if incoming in(u,v):continue
        if sign(tuple(incoming[i]+u[i]+v[i]for i in range(3)))!=outgoing:continue
        ghost=sign(tuple(u[i]+v[i]for i in range(3)))
        if ghost==outgoing:continue
        difference=sum(ghost[i]!=outgoing[i]for i in range(3));candidates.append((-difference,sum(abs(x)for x in u+v),u,v,ghost))
    if not candidates:raise ValueError('No distinct-source two-carrier turn for '+str((incoming,outgoing)))
    _,_,u,v,ghost=min(candidates)
    return [{'direction':list(u),'payload':0},{'direction':list(v),'payload':0}]

def path_variants(start,endpoint,final_direction,n=67):
    tail=move(endpoint,final_direction,-5,n);options=[]
    for axis in range(3):
        delta=(tail[axis]-start[axis])%n;choices=[]
        if delta==0:choices=[(0,0)]
        else:
            if delta>=5:choices.append((1,delta))
            if n-delta>=5:choices.append((-1,n-delta))
        options.append(choices)
    for choices in product(*options):
        segments=[]
        for axis in (1,0,2):
            orientation,length=choices[axis]
            if length:
                d=[0,0,0];d[axis]=orientation;segments.append((d,length))
        segments.append((list(final_direction),5));yield segments

def routes_for_common_arrival(starts,endpoints,start_tick,*,phase=6,n=67):
    variants={key:list(path_variants(starts[key]['site'],endpoints[key]['site'],endpoints[key]['direction'],n))for key in starts}
    minimum=max(min(sum(k for d,k in option)for option in rows)for rows in variants.values())+20
    first=phase+n*max(0,(start_tick+minimum-phase+n-1)//n)
    for arrival in range(first,first+8*n,n):
        selected={}
        for key,options in variants.items():
            candidates=[]
            for path in options:
                base=sum(k for d,k in path);perimeter=arrival-start_tick-base
                if perimeter<20 or perimeter>264 or perimeter%2:continue
                for height in range(5,67):
                    width=perimeter//2-height
                    if not 5<=width<=66:continue
                    # Closed rectangle has no segment of length N: an absent
                    # command's ghost cannot match merely by a full N lap.
                    if tuple(starts[key]['direction'])==(0,0,-1):
                        prefix=[([1,0,0],width),([0,0,1],height),([-1,0,0],width),([0,0,-1],height)]
                    else:prefix=[([0,0,1],height),([1,0,0],width),([0,0,-1],height),([-1,0,0],width)]
                    full_path=prefix+path;incoming=list(starts[key]['direction'])
                    try:
                        for outgoing,length in full_path:
                            turning_inputs(incoming,outgoing);incoming=list(outgoing)
                    except ValueError:continue
                    candidates.append((max(height,width),abs(height-width),base,full_path))
            if not candidates:break
            selected[key]=min(candidates,key=lambda q:q[:3])[-1]
        if len(selected)==len(starts):
            result={}
            for key,path in selected.items():
                site=list(starts[key]['site']);direction=list(starts[key]['direction']);tick=start_tick;turns=[];travel=[]
                for outgoing,length in path:
                    pulses=turning_inputs(direction,outgoing)
                    if pulses:turns.append({'site':site[:],'tick':tick,'incoming':direction[:],'outgoing':list(outgoing),'pulses':pulses,'without_command_direction':list(sign(tuple(sum(p['direction'][i]for p in pulses)for i in range(3))))})
                    site=move(site,outgoing,length,n);tick+=length;direction=list(outgoing);travel.append({'site_after':site[:],'tick_after':tick,'direction':direction[:],'steps':length})
                if site!=endpoints[key]['site']or tick!=arrival:raise AssertionError('Compiled geometry/time mismatch')
                result[key]={'turns':turns,'travel':travel,'destination':site,'arrival_tick':arrival,'last_direction':direction,'prepared_not_a_learned_routing_algorithm':True}
            return result
    raise ValueError('No bounded common phase/transport recipe')
