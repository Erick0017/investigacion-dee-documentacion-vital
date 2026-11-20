"""Finite M1 calibration on installed4.0.0; no historical runner is imported."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memory


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def execute(root, case, history, mode):
    import dee_thinking as d
    folder = root / case
    folder.mkdir(parents=True, exist_ok=True)
    world = memory.create_world(d)
    initial = memory.digest(world)
    world.save_snapshot(str(folder / "T0.deetsnap"))
    ids = []
    inputs = []
    for signal, outcome in zip(("S1", "S2"), history):
        tick = memory.DEFAULT_TRAINING_TICKS[signal]
        if mode != "outcomes_only":
            r = memory.present_signal(world, signal, tick)
            ids.append(r.id)
            inputs.append({"operation": "SIGNAL", "identity": signal, "tick": tick, "receipt_id": r.id})
        if mode != "signals_only":
            teacher_tick = tick + (1 if mode == "unpaired" else 0)
            for r in memory.broadcast_outcome(world, outcome, teacher_tick):
                ids.append(r.id)
                inputs.append({"operation": "OUTCOME_BROADCAST_DIAGNOSTIC_CALIBRATION", "identity": outcome,
                               "tick": teacher_tick, "receipt_id": r.id})
    samples = []
    # No queried consequence or future event is scheduled during this calibration.
    for t in (3, 11, 66):
        world.run_until(t)
        samples.append({"tick": t, "hubs": {s: memory.read_emission(world, s) for s in memory.HUBS}})
    world.save_snapshot(str(folder / "BEFORE_SIGNAL_ONLY.deetsnap"))
    emissions = {}
    for signal, submit_tick, emit_tick in (("S1", 67, 70), ("S2", 75, 78)):
        world.run_until(submit_tick)
        r = memory.present_signal(world, signal, submit_tick)
        ids.append(r.id)
        inputs.append({"operation": "SIGNAL_ONLY_QUERY_SAME_PHYSICAL_PORT", "identity": signal,
                       "tick": submit_tick, "receipt_id": r.id})
        world.run_until(emit_tick - 1)
        samples.append({"tick": emit_tick - 1, "hubs": {s: memory.read_emission(world, s) for s in memory.HUBS}})
        world.run_until(emit_tick)
        emissions[signal] = memory.read_emission(world, signal)
        samples.append({"tick": emit_tick, "hubs": {s: memory.read_emission(world, s) for s in memory.HUBS}})
        world.save_snapshot(str(folder / (signal + "_EMISSION.deetsnap")))
        world.run_until(emit_tick + 1)
        samples.append({"tick": emit_tick + 1, "hubs": {s: memory.read_emission(world, s) for s in memory.HUBS}})
    world.save_snapshot(str(folder / "MAIN_FINAL.deetsnap"))
    result = {"id": case, "method": memory.CONFIG["method"], "mode": mode,
              "history_generator_only": list(history), "initial_digest": initial,
              "inputs": inputs, "emissions": emissions, "samples": samples,
              "receipts": [memory.receipt(world.runtime, x) for x in ids],
              "final_digest": memory.digest(world), "future_consequences_during_query": [],
              "external_edits_after_t0": [], "operational_forks": 0,
              "scope": "DIAGNOSTIC_CALIBRATION: outcome direction is supplied directly; confirmation must derive it from a present physical outcome sensor"}
    put(folder / "MEASUREMENTS.json", result)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--wheel", required=True, type=Path)
    a = p.parse_args()
    import dee_thinking as d
    started = time.monotonic()
    identity = {"version": d.__version__, "kernel": d.kernel_identity(), "module": d.__file__,
                "native": d._native.__file__,
                "native_sha256": hashlib.sha256(Path(d._native.__file__).read_bytes()).hexdigest(),
                "wheel": str(a.wheel.resolve()), "wheel_sha256": hashlib.sha256(a.wheel.read_bytes()).hexdigest()}
    assert identity["version"] == "4.0.0"
    assert identity["kernel"]["kernel_version"] == 27
    assert identity["native_sha256"] == "20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066"
    assert identity["wheel_sha256"] == "17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623"
    a.output.mkdir(parents=True, exist_ok=True)
    put(a.output / "CONFIG.json", memory.CONFIG)
    put(a.output / "IDENTITY.json", identity)
    cases = [("paired_A", ("U", "V"), "paired"), ("paired_B", ("V", "U"), "paired"),
             ("unpaired_A", ("U", "V"), "unpaired"), ("signals_only", ("U", "V"), "signals_only"),
             ("outcomes_only", ("U", "V"), "outcomes_only")]
    results = []
    for case, history, mode in cases:
        result = execute(a.output, case, history, mode)
        results.append({"id": case, "mode": mode, "initial_digest": result["initial_digest"],
                        "emissions": result["emissions"], "final_digest": result["final_digest"]})
        put(a.output / "RESULTS.json", {"identity": identity, "cases": results,
                                      "elapsed_seconds": time.monotonic() - started})
    print(json.dumps({"output": str(a.output), "cases": len(results), "elapsed_seconds": time.monotonic() - started}))


if __name__ == "__main__":
    main()
