#!/usr/bin/env python3
"""Independent Python specification of the executed v27 local/destination operator.

This is analysis code, not a replacement kernel. It is used only to predict the
hash-pinned binary and to expose the incumbent/incoming branch structure.
"""
from __future__ import annotations

import itertools
from collections import Counter

import numpy as np

P_KERNEL = 19665
SEM_VOID = 0
SEM_NORMAL = 1
SEM_OBSERVER = 4
SEM_ORPHAN = 5
SEM_XNOR = 7
TTL_ORPHAN = 194422
MOORE = tuple((x, y, z) for x, y, z in itertools.product((-1, 0, 1), repeat=3) if (x, y, z) != (0, 0, 0))
XNOR_PAIRS = ((1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,-1,0),(1,0,1),(1,0,-1),(0,1,1),(0,1,-1),(1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1))
TETRA = (
    ((1,0,0),(0,1,0),(0,0,1),(1,1,1)),
    ((-1,0,0),(0,1,0),(0,0,1),(-1,1,1)),
    ((1,0,0),(0,-1,0),(0,0,1),(1,-1,1)),
    ((1,0,0),(0,1,0),(0,0,-1),(1,1,-1)),
    ((-1,0,0),(0,-1,0),(0,0,1),(-1,-1,1)),
    ((-1,0,0),(0,1,0),(0,0,-1),(-1,1,-1)),
    ((1,0,0),(0,-1,0),(0,0,-1),(1,-1,-1)),
    ((-1,0,0),(0,-1,0),(0,0,-1),(-1,-1,-1)),
)


def signed4(value: int) -> int:
    value &= 0xF
    return value - 16 if value >= 8 else value


def unpack(value: int) -> dict:
    value = int(value)
    return {
        "state": value & 0xFFFFFFFF,
        "sreg": (value >> 32) & 0xFFFF,
        "dx": signed4(value >> 48),
        "dy": signed4(value >> 52),
        "dz": signed4(value >> 56),
        "semantic": (value >> 60) & 0xF,
    }


def pack(state: int, sreg: int, direction: tuple[int, int, int], semantic: int) -> np.uint64:
    return np.uint64(
        (int(state) & 0xFFFFFFFF)
        | ((int(sreg) & 0xFFFF) << 32)
        | ((int(direction[0]) & 0xF) << 48)
        | ((int(direction[1]) & 0xF) << 52)
        | ((int(direction[2]) & 0xF) << 56)
        | ((int(semantic) & 0xF) << 60)
    )


def add(q, d, n):
    return tuple((q[i] + d[i]) % n for i in range(3))


def alive(value: int) -> bool:
    f = unpack(value)
    return f["state"] > 0 and f["semantic"] != SEM_ORPHAN


def exists(value: int) -> bool:
    return unpack(value)["state"] > 0


def tetrahedral(raw: np.ndarray, q) -> bool:
    n = raw.shape[0]
    return any(all(alive(raw[add(q, d, n)]) for d in pattern) for pattern in TETRA)


def xnor_birth(raw: np.ndarray, q) -> bool:
    n = raw.shape[0]
    symmetric = 0
    active = 0
    for d in XNOR_PAIRS:
        p = alive(raw[add(q, d, n)])
        m = alive(raw[add(q, tuple(-v for v in d), n)])
        symmetric += int(p == m)
        active += int(p) + int(m)
    return symmetric == 13 and active >= 8


def incoming(raw: np.ndarray, q) -> tuple[int, list[dict], int]:
    n = raw.shape[0]
    sources = []
    for d in MOORE:
        source_q = add(q, d, n)
        f = unpack(raw[source_q])
        direction = (f["dx"], f["dy"], f["dz"])
        if direction == (0, 0, 0):
            continue
        if add(source_q, direction, n) == q:
            sources.append({"q": source_q, "raw": int(raw[source_q]), **f})
    if not sources:
        return 0, sources, 0
    if len(sources) == 1:
        return int(sources[0]["raw"]), sources, 1
    sreg = min(P_KERNEL - 1, sum(item["sreg"] for item in sources))
    direction_sum = [sum(item[key] for item in sources) for key in ("dx", "dy", "dz")]
    direction = tuple(1 if v > 0 else -1 if v < 0 else 0 for v in direction_sum)
    return int(pack(1, sreg, direction, SEM_NORMAL)), sources, len(sources)


def neighborhood_statistics(raw: np.ndarray, q) -> dict:
    n = raw.shape[0]
    n_active = 0
    direction_sum = [0, 0, 0]
    grad = [0, 0, 0]
    orphan_neighbor = False
    for d in MOORE:
        f = unpack(raw[add(q, d, n)])
        orphan_neighbor |= f["semantic"] == SEM_ORPHAN
        if f["state"] > 0 and f["semantic"] != SEM_ORPHAN:
            n_active += 1
            direction_sum[0] += f["dx"]
            direction_sum[1] += f["dy"]
            direction_sum[2] += f["dz"]
        if f["state"] > 0:
            grad[0] -= d[0] * f["sreg"]
            grad[1] -= d[1] * f["sreg"]
            grad[2] -= d[2] * f["sreg"]
    inc_raw, sources, inc_count = incoming(raw, q)
    return {
        "n_active": n_active,
        "direction_sum": direction_sum,
        "gradient": grad,
        "tetrahedral": tetrahedral(raw, q),
        "orphan_neighbor": orphan_neighbor,
        "incoming_count": inc_count,
        "incoming_reduced_raw": inc_raw,
        "incoming_sources": sources,
    }


def local_pre_demux(raw: np.ndarray, clock: np.ndarray, q) -> tuple[int, int, dict, tuple | None]:
    """Return predicted raw, clock, diagnostics and optional fusion destination."""
    n = raw.shape[0]
    current = unpack(raw[q])
    tick = int(clock[q])
    stats = neighborhood_statistics(raw, q)
    diagnostics = {"incumbent": current, **{k: v for k, v in stats.items() if k != "incoming_sources"}}
    if current["semantic"] == SEM_OBSERVER:
        diagnostics["branch"] = "SEMANTIC4_FIXED"
        return int(raw[q]), (tick + 1) & ((1 << 64) - 1), diagnostics, None
    if current["state"] == 0:
        if xnor_birth(raw, q):
            diagnostics["branch"] = "EMPTY_XNOR_BIRTH"
            return int(pack(1, 1, (0, 0, 0), SEM_XNOR)), (tick + 1) & ((1 << 64) - 1), diagnostics, None
        reduced, sources, count = incoming(raw, q)
        if count:
            f = unpack(reduced)
            diagnostics["branch"] = "EMPTY_INCOMING_REDUCER"
            return int(pack(1, f["sreg"], (f["dx"], f["dy"], f["dz"]), SEM_NORMAL)), (tick + 1) & ((1 << 64) - 1), diagnostics, None
        diagnostics["branch"] = "EMPTY_REMAINS_VOID"
        return 0, (tick + 1) & ((1 << 64) - 1), diagnostics, None

    n_active = stats["n_active"]
    strong = stats["tetrahedral"] and n_active < 7
    tension = 16.0 if strong else 2.5
    rule_value = int(np.floor((n_active * tension / 26.0) + 0.5))
    diagnostics.update({"branch": "INCUMBENT_MATTER_RULE", "tension": tension, "rule_value": rule_value})
    if rule_value == 0:
        return 0, (tick + 1) & ((1 << 64) - 1), diagnostics, None
    write_protected = n_active >= 7 and stats["direction_sum"] == [0, 0, 0]
    prov_total = current["sreg"]
    if not write_protected:
        missing = 8 - n_active
        if 0 < missing <= 8:
            period = max(1, 782 // missing)
            if tick % period == 0:
                prov_total += 1
    fusion_destination = None
    if prov_total >= P_KERNEL:
        best_sreg = 2**31 - 1
        for d in MOORE:
            candidate = add(q, d, n)
            candidate_fields = unpack(raw[candidate])
            if candidate_fields["semantic"] == SEM_ORPHAN:
                continue
            candidate_degree = sum(int(alive(raw[add(candidate, e, n)])) for e in MOORE)
            if candidate_degree < 8 and candidate_fields["sreg"] < best_sreg:
                best_sreg = candidate_fields["sreg"]
                fusion_destination = candidate
        if fusion_destination is not None:
            prov_total = 0
    if (current["dx"], current["dy"], current["dz"]) != (0, 0, 0) or current["semantic"] == SEM_ORPHAN:
        direction = tuple(1 if v > 0 else -1 if v < 0 else 0 for v in stats["gradient"])
    else:
        direction = (0, 0, 0)
    out = int(pack(rule_value, prov_total, direction, current["semantic"] or SEM_NORMAL))
    return out, (tick + 1) & ((1 << 64) - 1), diagnostics, fusion_destination


def predict_tick(raw: np.ndarray, clock: np.ndarray):
    if raw.shape != clock.shape or raw.ndim != 3 or len(set(raw.shape)) != 1:
        raise ValueError("raw/clock must be matching cubes")
    out = np.zeros_like(raw, dtype=np.uint64)
    out_clock = np.zeros_like(clock, dtype=np.uint64)
    delta = Counter()
    diagnostics = {}
    for q in np.ndindex(raw.shape):
        value, clk, diag, destination = local_pre_demux(raw, clock, q)
        out[q] = np.uint64(value)
        out_clock[q] = np.uint64(clk)
        diagnostics[q] = diag
        if destination is not None:
            delta[destination] += 1
    for q, count in delta.items():
        cur = unpack(out[q])
        if cur["semantic"] == SEM_OBSERVER:
            continue
        if cur["semantic"] == SEM_ORPHAN:
            out[q] = pack(TTL_ORPHAN, 0, (0, 0, 0), SEM_ORPHAN)
        elif cur["state"] == 0:
            out[q] = pack(1, 0, (0, 0, 0), SEM_NORMAL)
        else:
            out[q] = pack(cur["state"], min(P_KERNEL - 1, cur["sreg"] + count), (cur["dx"], cur["dy"], cur["dz"]), cur["semantic"])
    return out, out_clock, diagnostics, dict(delta)

