"""Passive integer-field and toroidal graph observers; no native evolution.

RAW/clocks remain Python integers. Orphan/inactive nonzero records remain in
context. Graphs and kinematic proposals are external descriptions, not native
perception, certified genealogy, causal necessity or persistent homology.
"""
from collections import Counter
import hashlib
import json


def rt(world):return world.runtime if hasattr(world,"runtime") else world


def record(value):
    r=value.record
    return {"tick":int(value.tick),"site":[value.coordinate.x,value.coordinate.y,value.coordinate.z],
            "raw":int(value.raw),"clock":int(value.clock),"state":int(r.state),"semantic":int(r.semantic),
            "s_reg":int(r.s_reg),"direction":[int(r.dx),int(r.dy),int(r.dz)],
            "active":r.state>0 and r.semantic!=5,"nonzero_raw":value.raw!=0}


def o1_ports(world,ports):
    import dee_thinking as d
    return {name:record(rt(world).observe(d.Coordinate(*site))) for name,site in ports.items()}


def o2_fields(world,sites=None,max_nonzero=4096):
    import dee_thinking as d
    runtime=rt(world);n=runtime.dimension;records=[];truncated=False
    if sites is not None:
        records=[record(runtime.observe(d.Coordinate(*site))) for site in sites]
    else:
        raw=runtime.raw_copy();clocks=runtime.clock_copy()
        for i,value in enumerate(raw):
            if value==0:continue
            if len(records)>=max_nonzero:truncated=True;break
            v=d.decode_record(value)
            records.append({"tick":int(runtime.current_tick),"site":[i//(n*n),(i//n)%n,i%n],
                "raw":int(value),"clock":int(clocks[i]),"state":int(v.state),"semantic":int(v.semantic),
                "s_reg":int(v.s_reg),"direction":[int(v.dx),int(v.dy),int(v.dz)],
                "active":v.state>0 and v.semantic!=5,"nonzero_raw":True})
    return {"observer":"O2_INTEGER_FIELDS","tick":int(runtime.current_tick),"N":n,"records":records,
            "truncated":truncated,"max_nonzero":max_nonzero,"raw_clock_float_conversion":False,
            "counts":{"sampled":len(records),"active":sum(x["active"] for x in records),
                      "orphan":sum(x["semantic"]==5 for x in records),
                      "inactive_nonzero":sum(x["raw"]!=0 and not x["active"] for x in records)}}


def patch_sites(center,n,radius=1):
    return sorted({tuple((center[i]+v)%n for i,v in enumerate((x,y,z)))
                   for x in range(-radius,radius+1) for y in range(-radius,radius+1) for z in range(-radius,radius+1)})


def moore_context(world,target):
    import dee_thinking as d
    runtime=rt(world);n=runtime.dimension;target=tuple(target)
    cells=o2_fields(world,patch_sites(target,n,1))["records"]
    center=next(x for x in cells if tuple(x["site"])==target)
    neighbors=[x for x in cells if tuple(x["site"])!=target]
    proposals=[]
    # This is the directional-source predicate used by the void reducer. In
    # particular its sources are not prefiltered by active/orphan labels.
    for source in neighbors:
        direction=source["direction"]
        if any(direction) and tuple((source["site"][j]+direction[j])%n for j in range(3))==target:
            proposals.append(source)
    return {"observer":"O3_LOCAL_ENCOUNTER_CONTEXT","tick":runtime.current_tick,"center":center,
            "neighbors":neighbors,"directional_proposals":proposals,
            "n_active":sum(x["active"] for x in neighbors),
            "active_direction_sum":[sum(x["direction"][j] for x in neighbors if x["active"]) for j in range(3)],
            "scope":"Observed state and possible directional proposals; occupied-target precedence and other guard branches still require the actual transition"}


def torus_distance(a,b,n):
    return max(min((x-y)%n,(y-x)%n) for x,y in zip(a,b))


def _component_features(nodes,edges):
    parent=list(range(len(nodes)));size=[1]*len(nodes)
    def find(i):
        while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b in edges:
        a,b=find(a),find(b)
        if a!=b:parent[b]=a;size[a]+=size[b]
    components=Counter(find(i) for i in range(len(nodes)))
    return {"nodes":len(nodes),"edges":len(edges),"components":len(components),
            "largest_component":max(components.values(),default=0),
            "graph_cycle_rank":len(edges)-len(nodes)+len(components)}


def o4_torus(frame,scales=(1,2,4),anchors=None):
    """Finite spatial1-skeletons, direction counts and port-anchored context.

    The cycle rank is a GRAPH quantity, not H1 of a filled Rips complex.
    Coordinates are integers on the actual torus, never a Euclidean unwrap.
    """
    n=frame["N"];nodes=[x for x in frame["records"] if x["raw"]!=0]
    result={"observer":"O4_TOROIDAL_MULTISCALE_GRAPH","tick":frame["tick"],"N":n,
            "truncated":frame["truncated"],"node_predicate":"RAW!=0 including inactive/orphan context",
            "coverage":frame.get("scope","All nonzero records up to the explicit capture budget"),
            "scales":{},"directions":dict(Counter(",".join(map(str,x["direction"])) for x in nodes)),
            "semantic_counts":dict(Counter(str(x["semantic"]) for x in nodes)),
            "persistent_homology":"NOT_EXECUTED_NETWORK_PERMISSION; graph connectivity is not a substitute PH result"}
    for scale in scales:
        edges=[(i,j) for i in range(len(nodes)) for j in range(i+1,len(nodes))
               if torus_distance(nodes[i]["site"],nodes[j]["site"],n)<=scale]
        stats=_component_features(nodes,edges)
        directed=[]
        for i,x in enumerate(nodes):
            direction=x["direction"]
            if not any(direction):continue
            ray={tuple((x["site"][k]+step*direction[k])%n for k in range(3)) for step in range(1,scale+1)}
            directed.extend((i,j) for j,y in enumerate(nodes) if j!=i and tuple(y["site"]) in ray)
        stats.update(direction_compatible_ray_edges=len(directed),
                     scope="Spatial adjacency and declared directional rays, not proven native communication")
        result["scales"][str(scale)]=stats
    result["anchors"]={}
    for name,site in (anchors or {}).items():
        selected=[x for x in frame["records"] if tuple(x["site"])==tuple(site)]
        result["anchors"][name]={"site":list(site),"current":selected[0] if selected else None,
            "near_nonzero_by_scale":{str(s):sum(torus_distance(site,x["site"],n)<=s for x in nodes) for s in scales},
            "relative_records":[{"relative_modular":[(x["site"][j]-site[j])%n for j in range(3)],
                "relative_signed_minimum":[((x["site"][j]-site[j]+n//2)%n)-n//2 for j in range(3)],
                "distance":torus_distance(site,x["site"],n),"direction":x["direction"],"clock":x["clock"],
                "state":x["state"],"semantic":x["semantic"],"active":x["active"]} for x in nodes]}
    support=sorted(tuple(x["site"]) for x in nodes)
    result["support_sha256"]=hashlib.sha256(json.dumps(support,separators=(",",":")).encode()).hexdigest()
    result["integer_direction_clock_signature_sha256"]=hashlib.sha256(json.dumps(
        sorted((x["site"],x["direction"],x["clock"],x["state"],x["semantic"]) for x in nodes),
        separators=(",",":")).encode()).hexdigest()
    return result


def o3_segments(frames,segments,n):
    """Compare observed mobile segments with frozen kinematics, flag ambiguity."""
    rows=[]
    for segment in segments:
        start=segment["start_site"];born=segment["start_tick"];direction=segment["direction"]
        for frame in frames:
            tick=frame["tick"]
            if tick<born:continue
            dt=tick-born;unwrapped=[start[j]+dt*direction[j] for j in range(3)]
            site=tuple(q%n for q in unwrapped)
            found=next((r for r in frame["records"] if tuple(r["site"])==site),None)
            matches=bool(found and found["active"] and found["direction"]==list(direction)
                         and ("s_reg" not in segment or found["s_reg"]==segment["s_reg"]))
            rows.append({"segment":segment["id"],"tick":tick,"expected_site":site,"unwrapped":unwrapped,
                         "observation":found,"matches_declared_segment":matches,
                         "coverage":"CURRENT_COMPATIBLE_STATE_NOT_UNIQUE_PARENTAGE" if matches else "UNRECONSTRUCTED_TRANSFORMATION_OR_ABSENCE"})
    return rows


def temporal_proposals(frames,n):
    rows=[]
    for before,after in zip(frames,frames[1:]):
        gap=after["tick"]-before["tick"]
        if gap<=0:continue
        index={tuple(x["site"]):x for x in after["records"]}
        for source in before["records"]:
            direction=source["direction"]
            if source["raw"]==0 or not any(direction):continue
            target=tuple((source["site"][j]+gap*direction[j])%n for j in range(3))
            rows.append({"source_tick":before["tick"],"target_tick":after["tick"],
                "source":source,"target_site":target,"observed_target":index.get(target),
                "scope":"ONE_TICK_DIRECTIONAL_PROPOSAL_NOT_CAUSAL_NECESSITY" if gap==1 else "BALLISTIC_HYPOTHESIS_OVER_UNOBSERVED_INTERVAL_NOT_CERTIFIED_GENEALOGY"})
    return rows
