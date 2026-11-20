#!/usr/bin/env python3
"""Discovery: paired supported cells as a relative, organization-level memory."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ing02_common import NativeWorld, ROOT, add, load_kernel, pack, read, seal, summarize, write_json


SUPPORT = ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 1, 1))
EVENT_OFFSET = (0, -1, 0)
EVENT_DIRECTION = (0, -1, 0)


def put(raw, clock, q, state, sreg, direction=(0, 0, 0), semantic=4, phase=0):
    if int(raw[q]):
        raise RuntimeError(f"overlap at {q}")
    raw[q] = pack(state, sreg, direction, semantic)
    clock[q] = np.uint64(phase)


def install_memory(raw, clock, center, state_base, n, phase=260):
    put(raw, clock, center, state_base, 100, semantic=1, phase=phase)
    for index, offset in enumerate(SUPPORT):
        put(raw, clock, add(center, offset, 1, n), state_base + 100 + index, 0, semantic=4, phase=31 + index)


def make_world(kernel, n, mode):
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    a = (n // 4, n // 2, n // 2)
    b = (3 * n // 4, n // 2, n // 2)
    phase_a = 261 if mode == "wrong_phase" else 260
    install_memory(raw, clock, a, 1000, n, phase_a)
    install_memory(raw, clock, b, 2000, n, 260)
    if mode in {"experience_a", "experience_both", "wrong_phase"}:
        put(raw, clock, add(a, EVENT_OFFSET, 1, n), 3000, 3, EVENT_DIRECTION, 1, 17)
    if mode == "experience_both":
        put(raw, clock, add(b, EVENT_OFFSET, 1, n), 4000, 3, EVENT_DIRECTION, 1, 19)
    return NativeWorld(kernel, raw, clock), a, b


def run_case(kernel, n, mode, horizon):
    world, a, b = make_world(kernel, n, mode)
    initial = {"a": read(world.raw, a), "b": read(world.raw, b)}
    first_delta_loss = None
    first_center_loss = None
    first_direction_change = None
    expected_delta = 1 if mode == "experience_a" else 0
    samples = {1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, horizon}
    telemetry = []
    for tick in range(1, horizon + 1):
        info = world.tick()
        ra, rb = read(world.raw, a), read(world.raw, b)
        if ra is None or rb is None:
            if first_center_loss is None:
                first_center_loss = tick
            delta = None
        else:
            delta = ra["sreg"] - rb["sreg"]
            if delta != expected_delta and first_delta_loss is None:
                first_delta_loss = tick
            if (ra["direction"] != [0, 0, 0] or rb["direction"] != [0, 0, 0]) and first_direction_change is None:
                first_direction_change = tick
        if tick in samples or tick in {first_delta_loss, first_center_loss, first_direction_change}:
            telemetry.append(
                {
                    "tick": tick,
                    "a": ra,
                    "b": rb,
                    "sreg_delta_a_minus_b": delta,
                    "support": int(np.count_nonzero(world.raw)),
                    "kernel": {str(k): int(v) if isinstance(v, (int, np.integer)) else v for k, v in info.items()},
                }
            )
    return {
        "n": n,
        "mode": mode,
        "horizon": horizon,
        "initial": initial,
        "first_delta_loss": first_delta_loss,
        "first_center_loss": first_center_loss,
        "first_direction_change": first_direction_change,
        "terminal_a": read(world.raw, a),
        "terminal_b": read(world.raw, b),
        "terminal": summarize(world.raw, world.clock_a),
        "telemetry": telemetry,
        "python_interventions_after_t0": 0,
    }


def main():
    kernel, runtime = load_kernel(1)
    rows = []
    for n in (17, 23, 29):
        for mode in ("experience_a", "no_experience", "experience_both", "wrong_phase"):
            rows.append(run_case(kernel, n, mode, 5000))
    result = seal(
        {
            "schema": "dee.v27.ing02.discovery.relative_memory.v1",
            "question": "Can experience be stored as a persistent relation between two identically supported mutable cells rather than an absolute scalar threshold?",
            "prediction": "Matched autonomous drift cancels; one extra experience at A creates delta s_reg=1 while no-experience and both-experienced controls remain delta=0.",
            "apparatus": "Two spatially separated semantic1 cells, each supported by the same four semantic4 sites and initialized at equal phase; transient event touches A only in treatment.",
            "rows": rows,
            "summary": {
                "experience_a_exact": sum(r["mode"] == "experience_a" and r["first_delta_loss"] is None for r in rows),
                "experience_a_worlds": sum(r["mode"] == "experience_a" for r in rows),
                "symmetric_controls_exact": sum(r["mode"] in {"no_experience", "experience_both"} and r["first_delta_loss"] is None for r in rows),
                "symmetric_control_worlds": sum(r["mode"] in {"no_experience", "experience_both"} for r in rows),
            },
            "runtime": runtime,
        }
    )
    output = ROOT / "DISCOVERY" / "ING02_D06_RELATIVE_MEMORY.json"
    write_json(output, result)
    print(json.dumps({"output": str(output), "summary": result["summary"], "hash": result["content_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
