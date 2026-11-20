#!/usr/bin/env python3
"""Longevity and causal controls for the paired relative-memory readout."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ing02_common import ROOT, load_kernel, read, seal, summarize, write_json
from paired_relative_apparatus_v2 import construct


PATTERN_A = ((-1, 0, 0), (-1, 1, 1), (0, 0, 1), (0, 1, 0))
PATTERN_B = ((0, -1, 0), (0, 0, -1), (1, -1, -1), (1, 0, 0))


def run_case(kernel, n, mode, horizon=2000):
    world, ports = construct(kernel, {
        "n": n, "origin": (n // 2,) * 3, "mode": mode,
        "support_pattern_a": PATTERN_A, "support_pattern_b": PATTERN_B,
    })
    expected_delta = 1 if mode == "experience_a" else 0
    expect_positive_x = mode == "experience_a"
    first_delta_failure = None
    first_policy_failure = None
    first_center_loss = None
    routed_hits = 0
    samples = {1,2,3,4,8,16,32,64,128,256,512,1024,horizon}
    telemetry = []
    previous_direction = None
    previous_output = None
    for tick in range(1, horizon + 1):
        info = world.tick()
        a, b, c = (read(world.raw, ports[key]) for key in ("a", "b", "comparator"))
        if a is None or b is None:
            if first_center_loss is None:
                first_center_loss = tick
            delta = None
        else:
            delta = a["sreg"] - b["sreg"]
            if delta != expected_delta and first_delta_failure is None:
                first_delta_failure = tick
        x = None if c is None else c["direction"][0]
        functional = (x is not None and x > 0) if expect_positive_x else (x == 0)
        if tick >= 2 and not functional and first_policy_failure is None:
            first_policy_failure = tick
        if previous_output is not None:
            record = read(world.raw, previous_output)
            if record is not None and previous_direction is not None and record["direction"] == previous_direction:
                routed_hits += 1
        if c is not None and c["direction"] != [0,0,0]:
            previous_direction = list(c["direction"])
            previous_output = tuple((ports["comparator"][i] + c["direction"][i]) % n for i in range(3))
        else:
            previous_direction = None
            previous_output = None
        if tick in samples or tick in {first_delta_failure, first_policy_failure, first_center_loss}:
            telemetry.append({
                "tick": tick, "a": a, "b": b, "delta": delta, "comparator": c,
                "functional": functional, "support": int(np.count_nonzero(world.raw)),
                "kernel": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k,v in info.items()},
            })
    return {
        "n": n, "mode": mode, "horizon": horizon,
        "first_delta_failure": first_delta_failure, "first_policy_failure": first_policy_failure,
        "first_center_loss": first_center_loss, "routed_output_hits": routed_hits,
        "terminal_a": read(world.raw, ports["a"]), "terminal_b": read(world.raw, ports["b"]),
        "terminal_comparator": read(world.raw, ports["comparator"]),
        "terminal": summarize(world.raw, world.clock_a), "telemetry": telemetry,
        "python_interventions_after_t0": 0,
    }


def main():
    kernel, runtime = load_kernel(1)
    rows = []
    for n in (17,23,29):
        for mode in ("experience_a", "no_experience", "experience_both", "wrong_phase", "no_reader"):
            rows.append(run_case(kernel, n, mode))
    result = seal({
        "schema": "dee.v27.ing02.discovery.relative_readout_longevity.v1",
        "question": "How long can the same organization preserve and functionally use an experience-written relative state without host intervention?",
        "selected_pattern_source": "ING02_D08 pattern 7; selected before longevity run.",
        "safety_horizon": 2000,
        "rows": rows,
        "summary": {
            "treatment_exact": sum(r["mode"] == "experience_a" and r["first_delta_failure"] is None and r["first_policy_failure"] is None for r in rows),
            "treatment_worlds": sum(r["mode"] == "experience_a" for r in rows),
            "symmetric_controls_exact": sum(r["mode"] in {"no_experience","experience_both"} and r["first_delta_failure"] is None and r["first_policy_failure"] is None for r in rows),
        },
        "runtime": runtime,
    })
    output = ROOT / "DISCOVERY" / "ING02_D09_RELATIVE_READOUT_LONGEVITY.json"
    write_json(output, result)
    print(json.dumps({"output": str(output), "summary": result["summary"], "hash": result["content_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
