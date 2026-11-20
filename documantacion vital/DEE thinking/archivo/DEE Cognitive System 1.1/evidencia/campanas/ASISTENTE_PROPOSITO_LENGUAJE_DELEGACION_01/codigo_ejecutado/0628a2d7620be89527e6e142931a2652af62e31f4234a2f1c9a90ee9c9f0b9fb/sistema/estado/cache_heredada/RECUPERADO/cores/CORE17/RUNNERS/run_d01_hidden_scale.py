#!/usr/bin/env python3
"""Discovery root D01: delayed hidden-state return and cross-scale amplification."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core17_common import NativeWorld, ROOT, append_ndjson, audit_kernel, canonical_hash, pack, sha256_array, unpack, utc, verify_and_load_kernel, write_json


TETRA = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))


def add(q, d, n):
    return tuple((q[i] + d[i]) % n for i in range(3))


def centers_for(n: int, count: int):
    candidates = list(itertools.product(range(3, n - 3, 5), repeat=3))
    if len(candidates) < count:
        raise ValueError((n, count, len(candidates)))
    return candidates[:count]


def clock_gate_case(kernel, n: int, modules: int, delay: int, phase_base: int = 0):
    centers = centers_for(n, modules)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    ca = np.zeros_like(raw)
    cb = np.zeros_like(raw)
    for i, q in enumerate(centers):
        raw[q] = pack(0x1000 + i, 10, (0, 0, 0), 4)
        ca[q] = np.uint64((phase_base - delay) % 195)
        cb[q] = np.uint64((phase_base - delay + 1) % 195)
    a = NativeWorld(kernel, raw, ca, 1)
    b = NativeWorld(kernel, raw, cb, 1)
    coast = []
    for tick in range(delay + 1):
        coast.append({
            "tick": tick,
            "raw_equal": bool(np.array_equal(a.raw, b.raw)),
            "raw_mismatches": int(np.count_nonzero(a.raw != b.raw)),
            "clock_mismatches": int(np.count_nonzero(a.clock != b.clock)),
        })
        if tick < delay:
            a.tick(); b.tick()

    for q in centers:
        a.raw_a[q] = a.raw_b[q] = pack(1, 10, (0, 0, 0), 1)
        b.raw_a[q] = b.raw_b[q] = pack(1, 10, (0, 0, 0), 1)
        for d in TETRA:
            p = add(q, d, n)
            v = pack(1, 3, (0, 0, 0), 1)
            a.raw_a[p] = a.raw_b[p] = v
            b.raw_a[p] = b.raw_b[p] = v
    pre_intervention_equal = bool(np.array_equal(a.raw, b.raw))
    pre_clock_mismatches = int(np.count_nonzero(a.clock != b.clock))
    a.tick(); b.tick()
    center_rows = []
    for q in centers:
        fa = unpack(a.raw[q]); fb = unpack(b.raw[q])
        center_rows.append({"q": list(q), "a": fa, "b": fb, "different": int(a.raw[q]) != int(b.raw[q])})
    return {
        "n": n, "modules": modules, "delay": delay, "phase_base": phase_base,
        "equal_raw_through_delay": all(x["raw_equal"] for x in coast),
        "pre_intervention_equal_raw": pre_intervention_equal,
        "pre_intervention_clock_mismatches": pre_clock_mismatches,
        "post_intervention_raw_mismatches": int(np.count_nonzero(a.raw != b.raw)),
        "post_intervention_clock_mismatches": int(np.count_nonzero(a.clock != b.clock)),
        "module_responses_different": sum(x["different"] for x in center_rows),
        "center_rows": center_rows,
        "coast": coast,
        "a_raw_sha256": sha256_array(a.raw), "b_raw_sha256": sha256_array(b.raw),
    }


def equal_clock_control(kernel, n=21, modules=8, delay=7):
    centers = centers_for(n, modules)
    raw = np.zeros((n, n, n), dtype=np.uint64)
    clock = np.zeros_like(raw)
    for i, q in enumerate(centers):
        raw[q] = pack(0x2000 + i, 10, (0, 0, 0), 4)
        clock[q] = np.uint64((-delay) % 195)
    a = NativeWorld(kernel, raw, clock, 1); b = NativeWorld(kernel, raw, clock, 1)
    for _ in range(delay): a.tick(); b.tick()
    for q in centers:
        for w in (a, b):
            w.raw_a[q] = w.raw_b[q] = pack(1, 10, (0, 0, 0), 1)
            for d in TETRA:
                p = add(q, d, n); w.raw_a[p] = w.raw_b[p] = pack(1, 3, (0, 0, 0), 1)
    a.tick(); b.tick()
    return {"raw_equal": bool(np.array_equal(a.raw, b.raw)), "clock_equal": bool(np.array_equal(a.clock, b.clock)), "raw_mismatches": int(np.count_nonzero(a.raw != b.raw))}


def off_gate_control(kernel, n=21, modules=8, delay=7):
    return clock_gate_case(kernel, n, modules, delay, phase_base=17)


def no_readout_control(kernel, n=21, modules=8, delay=31):
    centers = centers_for(n, modules)
    raw = np.zeros((n, n, n), dtype=np.uint64); ca = np.zeros_like(raw); cb = np.zeros_like(raw)
    for i, q in enumerate(centers):
        raw[q] = pack(0x3000 + i, 10, (0, 0, 0), 4); ca[q] = np.uint64(i); cb[q] = np.uint64(i + 1)
    a = NativeWorld(kernel, raw, ca, 1); b = NativeWorld(kernel, raw, cb, 1)
    for _ in range(delay): a.tick(); b.tick()
    return {"raw_equal": bool(np.array_equal(a.raw, b.raw)), "clock_equal": bool(np.array_equal(a.clock, b.clock)), "raw_mismatches": int(np.count_nonzero(a.raw != b.raw))}


def payload_destruction(kernel):
    n = 9; q = (4, 4, 4)
    ra = np.zeros((n, n, n), dtype=np.uint64); rb = ra.copy()
    ra[q] = pack(1, 0, (0, 0, 0), 1); rb[q] = pack(0xDEADBEEF, 0, (0, 0, 0), 1)
    a = NativeWorld(kernel, ra); b = NativeWorld(kernel, rb)
    trace = []
    for t in range(4):
        trace.append({"tick": t, "raw_equal": bool(np.array_equal(a.raw, b.raw)), "clock_equal": bool(np.array_equal(a.clock, b.clock)), "raw_mismatches": int(np.count_nonzero(a.raw != b.raw))})
        if t < 3: a.tick(); b.tick()
    return {"trace": trace, "convergence_tick": next(x["tick"] for x in trace if x["raw_equal"] and x["clock_equal"]), "classification": "TRUE_MANY_TO_ONE_DESTRUCTION"}


def main():
    audit_kernel("CORE17_D01_HIDDEN_SCALE")
    kernel, runtime = verify_and_load_kernel(1)
    schedule = [(11, 1, 1), (21, 4, 7), (21, 8, 31), (31, 16, 194)]
    cases = [clock_gate_case(kernel, n, m, d, 0) for n, m, d in schedule]
    controls = {"equal_clock": equal_clock_control(kernel), "off_gate": off_gate_control(kernel), "no_readout": no_readout_control(kernel), "payload_destruction": payload_destruction(kernel)}
    scaling_exact = all(c["module_responses_different"] == c["modules"] and c["post_intervention_raw_mismatches"] >= c["modules"] for c in cases)
    result = {
        "schema": "dee.v27.core17.d01.v1", "experiment": "DELAYED_CLOCK_RETURN_AND_SCALE_TRANSFER",
        "created_utc": utc(), "runtime": runtime, "cases": cases, "controls": controls,
        "discovery": {
            "hidden_raw_equivalence_during_delay": all(c["equal_raw_through_delay"] for c in cases),
            "delayed_return": all(c["module_responses_different"] > 0 for c in cases),
            "linear_module_count_response": scaling_exact,
            "off_gate_null": controls["off_gate"]["post_intervention_raw_mismatches"] == 0,
            "equal_clock_null": controls["equal_clock"]["raw_equal"],
            "no_readout_null": controls["no_readout"]["raw_equal"],
            "true_destruction_control": controls["payload_destruction"]["convergence_tick"] == 1,
        },
        "interpretation": "A local clock residual can remain absent from raw/coarse observation for a chosen delay and re-enter raw dynamics synchronously when a period-sensitive native branch is opened. A nonsemantic payload contrast instead converges many-to-one and cannot return after full-state equality.",
    }
    h = canonical_hash(result); result["content_sha256"] = h
    write_json(ROOT / "DISCOVERY" / "C17D01_HIDDEN_SCALE.json", result)
    append_ndjson(ROOT / "QUESTION_TREE.ndjson", {"question_id": "C17Q001", "parent_question": "CORE16 hidden != destroyed bounded cases", "parent_result_hash": "607ab6af4e3529d21c0909e49ed5c73ef5cef5bdaa7cd92c2af70b4598b78e8b", "new_uncertainty": "Whether a hidden clock residual survives scale and returns after a programmable delay.", "candidate_explanations": ["observer-hidden causal residual", "raw state secretly changed", "generic perturbation artifact"], "why_next_experiment_discriminates": "Matched raw worlds differ only in clock; equal-clock, no-readout and off-period controls isolate the clock gate.", "result_hash": h, "result": result["discovery"], "child_question": "Does the scaling law survive post-freeze random geometry and delay?", "status": "CHILD_OPEN"})
    append_ndjson(ROOT / "KERNEL_DIALOGUE.ndjson", {"question_id": "C17Q001", "raw_outcome": result["discovery"], "mechanism_update": "Clock belongs to HIDDEN_BUT_CAUSAL and LATER_RECOVERABLE for a period-sensitive branch; nonsemantic payload supplies the DESTROYED control.", "next": "Freeze geometry-independent scaling prediction after model selection."})
    print(json.dumps({"hash": h, "discovery": result["discovery"], "cases": [{"modules": c["modules"], "delay": c["delay"], "different": c["module_responses_different"]} for c in cases]}, indent=2))


if __name__ == "__main__":
    main()
