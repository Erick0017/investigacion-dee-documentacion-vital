"""Immutable external view from a safe owner boundary. No tick or input API.

The original uint64 values are decimal strings. Sampling only affects the view;
global counts and exact buffer hashes cover the entire copied lattice.
"""
from array import array
from datetime import datetime, timezone
import hashlib
import json
import math
import time


def stamp():
    return datetime.now(timezone.utc).isoformat()


def fields(value):
    def signed(shift):
        item = (value >> shift) & 15
        return item - 16 if item & 8 else item
    return {"raw": str(value), "state": value & 0xffffffff,
            "s_reg": (value >> 32) & 65535, "semantic": (value >> 60) & 15,
            "direction": [signed(k) for k in (48, 52, 56)]}


def make_frame(world, queue, config=None, previous=None):
    """Called only synchronously by the one physical owner, between operations."""
    config = config or {}
    begin = time.perf_counter()
    rt = world.a.world.runtime
    tick = int(rt.current_tick)
    n = int(rt.dimension)
    raw, clocks = rt.raw_copy(), rt.clock_copy()
    if tick != int(rt.current_tick):
        raise RuntimeError("Non-coherent viewer capture; no frame published.")
    if len(raw) != n ** 3 or len(clocks) != len(raw):
        raise ValueError("Physical buffers do not match N.")
    coordinate_checks = []
    if hasattr(rt, 'observe'):
        # Cross-check the flattening against the official coordinate accessor,
        # not against a second copy of the same Python indexing formula.
        from dee_thinking import Coordinate
        witnesses = sorted(set([0, len(raw)-1, len(raw)//2,
            *[i for i, v in enumerate(raw) if v != 0][:5]]))
        for i in witnesses:
            xyz = [i // (n*n), (i//n) % n, i % n]
            official = rt.observe(Coordinate(*xyz))
            if int(official.raw) != raw[i] or int(official.clock) != clocks[i]:
                raise ValueError('Flat buffer/official coordinate disagreement; no 3D map published.')
            coordinate_checks.append({'index': i, 'xyz': xyz, 'raw': str(official.raw),
                'clock': str(official.clock), 'official_observe_matches': True})
    raw_bytes, clock_bytes = array('Q', raw).tobytes(), array('Q', clocks).tobytes()
    mode = config.get("universe", "raw_nonzero")
    if mode not in ("raw_nonzero", "clock_nonzero", "all"):
        mode = "raw_nonzero"
    candidates = [i for i, v in enumerate(raw) if mode == "all" or
                  (mode == "clock_nonzero" and clocks[i] != 0) or
                  (mode == "raw_nonzero" and v != 0)]
    cap = max(256, min(20000, int(config.get("max_points", 12000))))
    stride = max(1, math.ceil(len(candidates) / cap))
    selected = candidates[::stride]
    coordinate = config.get("coordinate")
    if isinstance(coordinate, list) and len(coordinate) == 3 and all(type(x) is int and 0 <= x < n for x in coordinate):
        wanted = (coordinate[0] * n + coordinate[1]) * n + coordinate[2]
        if wanted not in selected:
            selected.append(wanted)
    cells = []
    for i in selected:
        cell = {"index": i, "xyz": [i // (n * n), (i // n) % n, i % n],
                **fields(raw[i]), "clock": str(clocks[i])}
        # Change is an observed endpoint difference, not an inferred trajectory.
        if previous is not None:
            cell["changed"] = raw[i] != previous[0][i] or clocks[i] != previous[1][i]
        cells.append(cell)
    regions = []
    for interface in world.a.world.interfaces:
        # Official InterfaceSpec owns a ChannelSpec; its injection_site is the
        # declared fixed coordinate. R01 incorrectly used InterfaceSpec.site;
        # that instrument failure is preserved with no frame fabricated.
        c = interface.channel.injection_site
        regions.append({"name": str(interface.name), "site": [int(c.x), int(c.y), int(c.z)],
                        "source": "official currently declared InterfaceSpec; not a moving body"})
    outstanding = queue.outstanding()
    counts = {"sites": len(raw), "raw_nonzero": sum(v != 0 for v in raw),
              "present_state_positive": sum((v & 0xffffffff) > 0 for v in raw),
              "active_state_positive_semantic_not_5": sum((v & 0xffffffff) > 0 and (v >> 60) != 5 for v in raw),
              "clock_nonzero": sum(v != 0 for v in clocks), "max_s_reg": max((v >> 32) & 65535 for v in raw)}
    result = {"schema": "GENESIS.passive_owner_frame.R01", "life_id": world.life,
              "tick": str(tick), "N": n, "captured_utc": stamp(), "coherent_tick": True,
              "RAW_sha256": hashlib.sha256(raw_bytes).hexdigest(),
              "clocks_sha256": hashlib.sha256(clock_bytes).hexdigest(),
              "coordinate_proof": {"formula": "((x*N)+y)*N+z", "official_observe_samples": coordinate_checks,
                  "scope": "Same-owner passive official coordinate access compared with copied flat arrays; no lineage claim."},
              "counts": counts, "cells": cells, "regions": regions,
              "coverage": {"mode": mode, "eligible_sites": len(candidates), "displayed_sites": len(cells),
                           "deterministic_stride": stride, "sampled": stride > 1,
                           "not_a_complete_operational_snapshot": True},
              "transport": {"outstanding_ids": [r['id'] for r in outstanding],
                            "outstanding_sha256": hashlib.sha256(json.dumps(outstanding, sort_keys=True,
                                separators=(',', ':'), ensure_ascii=False).encode()).hexdigest(),
                            "counters": queue.counters()},
              "attribution": "INSTRUMENTO: passive external buffer copies; never a DEE sensor or answer source.",
              "trajectory_scope": "Endpoint changes only; no particle lineage reconstructed."}
    result['capture_seconds'] = time.perf_counter() - begin
    return result, (raw, clocks)
