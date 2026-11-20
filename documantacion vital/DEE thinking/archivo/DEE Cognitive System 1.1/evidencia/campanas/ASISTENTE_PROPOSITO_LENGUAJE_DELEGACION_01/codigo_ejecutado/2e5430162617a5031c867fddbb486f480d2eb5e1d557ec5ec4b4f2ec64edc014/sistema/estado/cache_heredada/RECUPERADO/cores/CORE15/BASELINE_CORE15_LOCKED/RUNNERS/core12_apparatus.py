"""Neutral apparatus for CORE12 phase, ensemble, and interface interrogations."""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core12_common import NativeWorld, fields, pack, unpack_scalar


def add(q, d, k, n):
    return tuple((q[i] + k * d[i]) % n for i in range(3))


def read(raw, q):
    return None if int(raw[q]) == 0 else unpack_scalar(raw[q])


def summarize(raw):
    fs = fields(raw)
    occ = raw != 0
    return {
        "support": int(np.count_nonzero(occ)),
        "sreg_sum": int(fs["sreg"][occ].astype(np.uint64).sum()),
        "semantic_counts": {str(i): int(np.count_nonzero(occ & (fs["semantic"] == i))) for i in range(1, 16) if np.any(occ & (fs["semantic"] == i))},
        "direction_sum": [int(fs[k][occ].sum()) for k in ("dx", "dy", "dz")],
    }


def source_train_trial(kernel, n=43, source=None, direction=(1, 0, 0), sreg=137, horizon=24,
                       detector_distance=9, mode="baseline", clock_value=987654321, threads=1):
    source = tuple(source or (n // 3, n // 2, n // 2))
    direction = tuple(direction)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    raw[source] = pack(0, sreg, direction, 4)
    clock[source] = np.uint64(clock_value)
    mouth = add(source, direction, 1, n)
    offpath = list(mouth)
    transverse = next((i for i, x in enumerate(direction) if x == 0), 0)
    offpath[transverse] = (offpath[transverse] + 3) % n
    offpath = tuple(offpath)
    if mode == "mouth_block":
        raw[mouth] = pack(1, 29, (0, 0, 0), 1)
    elif mode == "offpath_sham":
        raw[offpath] = pack(1, 29, (0, 0, 0), 1)
    elif mode != "baseline":
        raise ValueError(mode)
    detector = add(source, direction, detector_distance, n)
    world = NativeWorld(kernel, raw, clock, threads)
    trace = []
    for tick in range(horizon + 1):
        normal_distances = []
        for k in range(1, min(horizon + 2, n // 2)):
            rec = read(world.raw, add(source, direction, k, n))
            if rec is not None and rec["semantic"] == 1 and rec["direction"] == list(direction):
                normal_distances.append(k)
        detector_rec = read(world.raw, detector)
        trace.append({
            "tick": tick,
            "source": read(world.raw, source),
            "mouth": read(world.raw, mouth),
            "offpath": read(world.raw, offpath),
            "normal_distances": normal_distances,
            "front": max(normal_distances) if normal_distances else None,
            "detector": detector_rec,
            "summary": summarize(world.raw),
        })
        if tick < horizon:
            world.tick()
    arrival_ticks = [row["tick"] for row in trace if row["detector"] is not None and row["detector"]["semantic"] == 1]
    mouth_ticks = [row["tick"] for row in trace if row["mouth"] is not None and row["mouth"]["semantic"] == 1 and row["mouth"]["direction"] == list(direction)]
    gaps = [b - a for a, b in zip(arrival_ticks, arrival_ticks[1:])]
    return {
        "n": n, "source": list(source), "direction": list(direction), "sreg": sreg,
        "horizon": horizon, "detector_distance": detector_distance, "mode": mode,
        "post_t0_python": "NATIVE_AFTER_T0", "mouth": list(mouth), "offpath": list(offpath),
        "detector": list(detector), "arrival_ticks": arrival_ticks, "arrival_gaps": gaps,
        "mouth_ticks": mouth_ticks, "source_persistent": all(row["source"] is not None and row["source"]["semantic"] == 4 for row in trace),
        "period_two_at_detector": len(arrival_ticks) >= 4 and all(g == 2 for g in gaps),
        "trace": trace,
    }


def convergent_phase_paths(kernel, n=43, path_length=7, mode="AB_coherent", center=None,
                           sregs=(101, 211), horizon=24, frame=(0, 1, 2), threads=1):
    """Two semantic-4 trains converge on one destination through equal diagonal paths."""
    center = tuple(center or (n // 2, n // 2, n // 2))
    dl = [0, 0, 0]; dt = [0, 0, 0]
    dl[frame[0]] = 1; dt[frame[1]] = 1
    d_a = tuple(dl[i] + dt[i] for i in range(3))
    d_b = tuple(dl[i] - dt[i] for i in range(3))
    source_a = add(center, d_a, -path_length, n)
    source_b = add(center, d_b, -path_length, n)
    raw = np.zeros((n, n, n), dtype=np.uint64); clock = np.zeros_like(raw)
    include_a = mode not in {"B_only", "B_phase_shifted", "closed"}
    include_b = mode not in {"A_only", "closed"}
    if include_a:
        raw[source_a] = pack(0, sregs[0], d_a, 4); clock[source_a] = np.uint64(111111)
    if include_b:
        raw[source_b] = pack(0, sregs[1], d_b, 4); clock[source_b] = np.uint64(222222)
    b_mouth = add(source_b, d_b, 1, n)
    offpath = list(b_mouth); offpath[frame[2]] = (offpath[frame[2]] + 3) % n; offpath = tuple(offpath)
    if mode in {"AB_phase_shifted", "B_phase_shifted"}:
        raw[b_mouth] = pack(1, 29, (0, 0, 0), 1)
    elif mode == "AB_offpath_sham":
        raw[offpath] = pack(1, 29, (0, 0, 0), 1)
    elif mode not in {"AB_coherent", "A_only", "B_only", "closed"}:
        raise ValueError(mode)
    world = NativeWorld(kernel, raw, clock, threads)
    trace = []
    for tick in range(horizon + 1):
        rec = read(world.raw, center)
        trace.append({"tick": tick, "detector": rec, "support": int(np.count_nonzero(world.raw)), "source_a": read(world.raw, source_a), "source_b": read(world.raw, source_b)})
        if tick < horizon: world.tick()
    events = [row for row in trace if row["detector"] is not None and row["detector"]["semantic"] == 1]
    return {
        "mode": mode, "n": n, "path_length": path_length, "frame": list(frame), "center": list(center),
        "directions": [list(d_a), list(d_b)], "sources": [list(source_a), list(source_b)],
        "b_mouth": list(b_mouth), "offpath": list(offpath), "sregs": list(sregs), "horizon": horizon,
        "post_t0_python": "NATIVE_AFTER_T0", "detector_event_ticks": [row["tick"] for row in events],
        "detector_event_sregs": [row["detector"]["sreg"] for row in events],
        "detector_event_directions": [row["detector"]["direction"] for row in events],
        "event_count": len(events), "trace": trace,
    }


def static_ensemble_contact(kernel, n=23, horizon=8, contact=True, threads=1):
    """Two closed, persistent semantic-1 arrays; contact is a vacant or occupied separating plane."""
    raw = np.zeros((n, n, n), dtype=np.uint64)
    centers = ((n // 2 - 3, n // 2, n // 2), (n // 2 + 3, n // 2, n // 2))
    regions = []
    for side, center in enumerate(centers):
        cells = []
        for dy, dz in itertools.product((-1, 0, 1), repeat=2):
            q = (center[0], center[1] + dy, center[2] + dz)
            raw[q] = pack(0x1000 + side * 100 + len(cells), 17 + side * 20, (0, 0, 0), 1)
            cells.append(q)
        regions.append(cells)
    interface = (n // 2, n // 2, n // 2)
    if contact:
        raw[interface] = pack(0x7777, 23, (0, 0, 0), 1)
    world = NativeWorld(kernel, raw, threads=threads)
    rows = []
    for tick in range(horizon + 1):
        rows.append({"tick": tick, "A_support": sum(int(world.raw[q] != 0) for q in regions[0]), "B_support": sum(int(world.raw[q] != 0) for q in regions[1]), "interface": read(world.raw, interface), "global": summarize(world.raw)})
        if tick < horizon: world.tick()
    return {"mechanism_class": "closed_static_persistent_ensembles", "contact": contact, "centers": [list(x) for x in centers], "rows": rows}


def joint_scaffold_contact(kernel, n=23, cycles=4, mode="AB", axis=0, seed=12, threads=1):
    """Two closed semantic-4 scaffolds sharing a four-cell guard interface."""
    rng = np.random.default_rng(seed); raw = np.zeros((n, n, n), dtype=np.uint64); clock = np.zeros_like(raw)
    base = [n // 2] * 3; center_a = tuple(base); base[axis] += 2; center_b = tuple(base)
    other = [i for i in range(3) if i != axis]
    def plane(center, side):
        cells=[]
        for u, v in itertools.product((-1, 1), repeat=2):
            q=list(center); q[axis]=(q[axis]+side)%n; q[other[0]]=(q[other[0]]+u)%n; q[other[1]]=(q[other[1]]+v)%n; cells.append(tuple(q))
        return cells
    outer_a, shared, outer_b = plane(center_a,-1), plane(center_a,1), plane(center_b,1)
    selected = outer_a + shared + outer_b if mode == "AB" else (outer_a + shared if mode == "A_only" else shared + outer_b if mode == "B_only" else [])
    for i,q in enumerate(selected):
        raw[q]=pack(int(rng.integers(1,2**32)), 50+i, (0,0,0), 4); clock[q]=np.uint64(rng.bit_generator.random_raw())
    world=NativeWorld(kernel,raw,clock,threads); rows=[]
    for cycle in range(cycles):
        for center in (center_a, center_b):
            world.raw_a[center]=0; world.raw_b[center]=0; world.clock_a[center]=0; world.clock_b[center]=0
        stats=world.tick(); rows.append({"cycle":cycle,"A_restored":read(world.raw,center_a),"B_restored":read(world.raw,center_b),"summary":summarize(world.raw),"stats":stats})
    return {"mechanism_class":"closed_semantic4_joint_scaffolds","mode":mode,"n":n,"centers":[list(center_a),list(center_b)],"selected_support":len(selected),"shared_interface_cells":len(shared),"cycles":rows}


def facing_source_ensembles(kernel, n=43, separation=14, sregs=(73, 311), mode="contact", horizon=28, threads=1):
    center=(n//2,n//2,n//2); da=(1,0,0); db=(-1,0,0)
    sa=add(center,da,-separation//2,n); sb=add(center,db,-separation//2,n)
    raw=np.zeros((n,n,n),dtype=np.uint64); clock=np.zeros_like(raw)
    raw[sa]=pack(0,sregs[0],da,4); raw[sb]=pack(0,sregs[1],db,4)
    if mode=="isolated":
        raw[center]=pack(1,19,(0,0,0),1)
    world=NativeWorld(kernel,raw,clock,threads); rows=[]
    for tick in range(horizon+1):
        rows.append({"tick":tick,"source_A":read(world.raw,sa),"source_B":read(world.raw,sb),"interface":read(world.raw,center),"summary":summarize(world.raw)})
        if tick<horizon: world.tick()
    interface_events=[r for r in rows if r["interface"] is not None]
    return {"mechanism_class":"source_supported_facing_trains","mode":mode,"sources":[list(sa),list(sb)],"sregs":list(sregs),"separation":separation,"rows":rows,"interface_event_ticks":[r["tick"] for r in interface_events],"source_A_persistent":all(r["source_A"] is not None for r in rows),"source_B_persistent":all(r["source_B"] is not None for r in rows)}


def regenerative_interface_trial(kernel, n=47, source_distance=11, downstream_distance=7, horizon=30,
                                 mode="semantic4_full", direction=(1,0,0), center=None, source_sreg=137,
                                 threads=1, semantic4_indices=None):
    """A period-two train interrogates a local interface with or without the semantic-4 guard."""
    center=tuple(center or (n//2,n//2,n//2)); direction=tuple(direction); source=add(center,direction,-source_distance,n)
    raw=np.zeros((n,n,n),dtype=np.uint64); clock=np.zeros_like(raw)
    raw[source]=pack(0,source_sreg,direction,4); clock[source]=np.uint64(919191)
    axes=[i for i,v in enumerate(direction) if v==0]
    if len(axes)<2: raise ValueError("interface requires axis-aligned direction")
    corners=[]
    for sx,sy,sz in itertools.product((-1,1),repeat=3):
        q=((center[0]+sx)%n,(center[1]+sy)%n,(center[2]+sz)%n); corners.append(q)
    if mode != "empty":
        raw[center]=pack(0x12345678,19,(0,0,0),1)
    if mode in {"semantic4_full","semantic4_missing_corner"}:
        selected=corners[:-1] if mode=="semantic4_missing_corner" else corners
        semantic=4
    elif mode == "semantic4_custom":
        selected=[corners[i] for i in semantic4_indices or []]; semantic=4
    elif mode == "semantic4_shuffled":
        selected=[tuple((center[i]+2*s[i])%n for i in range(3)) for s in itertools.product((-1,1),repeat=3)]; semantic=4
    elif mode=="semantic1_same_inventory":
        selected=corners; semantic=1
    elif mode=="static_center_only":
        selected=[]; semantic=1
    elif mode=="empty":
        selected=[]; semantic=1
    else: raise ValueError(mode)
    for i,q in enumerate(selected): raw[q]=pack(0xA000+i,31+i,(0,0,0),semantic)
    world=NativeWorld(kernel,raw,clock,threads); rows=[]
    probes=[add(center,direction,k,n) for k in range(0,downstream_distance+1)]
    for tick in range(horizon+1):
        rows.append({"tick":tick,"center":read(world.raw,center),"downstream":[read(world.raw,q) for q in probes],"source":read(world.raw,source),"corner_support":sum(int(world.raw[q]!=0) for q in corners),"summary":summarize(world.raw)})
        if tick<horizon: world.tick()
    downstream_events={str(k):[r["tick"] for r in rows if r["downstream"][k] is not None and r["downstream"][k]["direction"]==list(direction)] for k in range(1,downstream_distance+1)}
    incident_expected=[t for t in range(source_distance,horizon+1,2)]
    return {"mechanism_class":"period2_train_x_local_interface","mode":mode,"n":n,"center":list(center),"source":list(source),"direction":list(direction),"source_distance":source_distance,"downstream_distance":downstream_distance,"horizon":horizon,"incident_expected_ticks":incident_expected,"downstream_event_ticks":downstream_events,"rows":rows}


def guard_truth_table(kernel, n=15, center=None, semantic=4, threads=1, sreg_base=31, state_base=0xA000):
    """Exhaust the eight-corner local guard truth table in one tick."""
    center=tuple(center or (n//2,n//2,n//2))
    corners=[((center[0]+dx)%n,(center[1]+dy)%n,(center[2]+dz)%n) for dx,dy,dz in itertools.product((-1,1),repeat=3)]
    rows=[]
    for initial_center in (False,True):
        for mask in range(256):
            raw=np.zeros((n,n,n),dtype=np.uint64)
            if initial_center: raw[center]=pack(0x1234,19,(0,0,0),1)
            indices=[i for i in range(8) if mask&(1<<i)]
            for i in indices: raw[corners[i]]=pack(state_base+i,min(19664,sreg_base+i),(0,0,0),semantic)
            world=NativeWorld(kernel,raw,threads=threads); world.tick(); rec=read(world.raw,center)
            rows.append({"initial_center":initial_center,"mask":mask,"indices":indices,"count":len(indices),"center_after":rec,"center_present":rec is not None})
    return {"n":n,"center":list(center),"corner_coordinates":[list(q) for q in corners],"semantic":semantic,"rows":rows}


def convergent_phase_trace(kernel, n=43, path_length=7, mode="AB_phase_shifted", center=None,
                           sregs=(101,211), horizon=None, frame=(0,1,2), threads=1,
                           reset_center_clock_tick=None, reset_offpath_clock_tick=None,
                           remove_center_record_tick=None, remove_offpath_record_tick=None):
    """Sparse causal trace for the convergent-path apparatus."""
    center=tuple(center or (n//2,n//2,n//2)); horizon=horizon or path_length+4
    dl=[0,0,0]; dt=[0,0,0]; dl[frame[0]]=1; dt[frame[1]]=1
    da=tuple(dl[i]+dt[i] for i in range(3)); db=tuple(dl[i]-dt[i] for i in range(3))
    sa=add(center,da,-path_length,n); sb=add(center,db,-path_length,n)
    raw=np.zeros((n,n,n),dtype=np.uint64); clock=np.zeros_like(raw)
    if mode!="B_phase_shifted": raw[sa]=pack(0,sregs[0],da,4)
    raw[sb]=pack(0,sregs[1],db,4)
    mouth=add(sb,db,1,n); raw[mouth]=pack(1,29,(0,0,0),1)
    world=NativeWorld(kernel,raw,clock,threads); rows=[]
    for tick in range(horizon+1):
        records=[]
        for q in np.argwhere(world.raw!=0):
            qt=tuple(int(x) for x in q); rec=read(world.raw,qt)
            records.append({"coordinate":list(qt),**rec})
        expected_a=[{"distance":k,"coordinate":list(add(sa,da,k,n)),"record":read(world.raw,add(sa,da,k,n))} for k in range(path_length+1)]
        expected_b=[{"distance":k,"coordinate":list(add(sb,db,k,n)),"record":read(world.raw,add(sb,db,k,n))} for k in range(path_length+1)]
        rows.append({"tick":tick,"detector":read(world.raw,center),"detector_clock":int(world.clock[center]),"expected_A_path":expected_a,"expected_B_path":expected_b,"records":records})
        if tick<horizon:
            if reset_center_clock_tick == tick:
                world.clock_a[center]=0; world.clock_b[center]=0
            if reset_offpath_clock_tick == tick:
                q=list(center); q[frame[2]]=(q[frame[2]]+5)%n; q=tuple(q)
                world.clock_a[q]=0; world.clock_b[q]=0
            if remove_center_record_tick == tick:
                world.raw_a[center]=0; world.raw_b[center]=0
            if remove_offpath_record_tick == tick:
                q=list(center); q[frame[2]]=(q[frame[2]]+5)%n; q=tuple(q)
                world.raw_a[q]=0; world.raw_b[q]=0
            world.tick()
    return {"mode":mode,"n":n,"path_length":path_length,"frame":list(frame),"center":list(center),"sources":[list(sa),list(sb)],"directions":[list(da),list(db)],"mouth":list(mouth),"reset_center_clock_tick":reset_center_clock_tick,"reset_offpath_clock_tick":reset_offpath_clock_tick,"remove_center_record_tick":remove_center_record_tick,"remove_offpath_record_tick":remove_offpath_record_tick,"rows":rows}
