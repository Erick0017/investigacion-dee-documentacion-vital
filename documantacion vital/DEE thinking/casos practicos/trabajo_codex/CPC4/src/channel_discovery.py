"""Finite discovery/runner for the native A->B channel, public DEE4 only."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import channel


def put(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_case(case, output):
    import dee_thinking as d
    if d.__version__ != "4.0.0" or d.kernel_identity()["kernel_version"] != 27:
        raise RuntimeError("Official DEE thinking4/v27 instrument required")
    if sha(d._native.__file__) != channel.NATIVE_SHA256:
        raise RuntimeError("Native artifact differs from the fixed instrument")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    world, spec = channel.prepare(d, tuple(case.get("translation", (0, 0, 0))))
    initial = channel.digest(world)
    world.save_snapshot(str(output / "MAIN_T0.deetsnap"))
    ids = []
    calls = []
    trace = []
    interventions = []
    def register(receipts, label):
        for r in receipts:
            ids.append(r.id)
            calls.append({"operation": "submit", "role": label, "id": r.id,
                          "requested_tick": r.requested_tick, "channels": list(r.channels)})
    register(channel.acquire(world, "A", case.get("A_history", 1), 0), "A_ACQUISITION")
    register(channel.acquire(world, "B", case["B_history"], 12), "B_ACQUISITION")
    # Scheduling a fixed common A query does not inspect its learned response.
    register([world.submit("A.signal", 5, 67)], "A_COMMON_QUERY")
    # Later B query is also fixed before seeing either contact or its result.
    register([world.submit("B.query_z", 5, 146)], "B_POST_CONTACT_COMMON_PHYSICAL_QUERY")
    decisive = {15,66,67,69,70,71,78,79,80,81,82,83,84,100,120,145,146,147,148,149,150,153,156,157,161,163}
    checkpoints = {15:"B_AFTER_ACQUISITION",70:"A_EMITTED",81:"BEFORE_CONTACT",82:"AFTER_CONTACT",148:"BEFORE_COMMON_QUERY",149:"AFTER_COMMON_QUERY",163:"MAIN_FINAL"}
    while world.runtime.current_tick <= 163:
        tick = world.runtime.current_tick
        if tick == 70 and case.get("cut"):
            world, edit = channel.cut_emitted_message(world, spec)
            interventions.append(edit)
        if tick == 149:
            register(channel.input_resources(world, 149), "FIXED_USE_RESOURCES_AFTER_B_RESPONSE")
        if tick == 150:
            register([world.submit("use." + case.get("future_event", "U"), 11, 150)], "ACTUAL_EVENT_AFTER_B_RESPONSE")
        if tick in decisive:
            trace.append(channel.panel(world, spec, tick))
        if tick in checkpoints:
            world.save_snapshot(str(output / (checkpoints[tick] + ".deetsnap")))
        if tick == 163:
            break
        world.advance()
    by_tick = {row["tick"]: row for row in trace}
    resource = by_tick[156]["samples"]["bank_resource_receiver"]
    function = by_tick[163]["samples"]["bank_function_receiver"]
    result = {"case": case, "spec": spec, "initial": initial,
              "instrument": {"version": d.__version__, "kernel": 27, "module": d.__file__, "native_sha256": sha(d._native.__file__)},
              "trace": trace, "A_emission": by_tick[70]["samples"]["A_hub"],
              "B_after_contact": by_tick[82]["samples"]["B_hub"],
              "B_common_query_response": by_tick[149]["samples"]["B_hub"],
              "evaluation": channel.evaluate_bank(resource, function),
              "receipts": [channel.receipt(world, identity) for identity in ids],
              "operation_calls": calls, "interventions": interventions,
              "final": channel.digest(world), "elapsed_seconds": time.monotonic() - start,
              "scope": "Finite acquired mobile functional cores, not two complete basal bodies; native contact and retained state are evaluated by an actual common later query and native finite supply use",
              "source_sha256": {"src/channel.py": sha(ROOT / "src/channel.py"), "src/channel_discovery.py": sha(__file__)}}
    put(output / "MEASUREMENTS.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not (args.case or args.config and args.id) or not args.output:
        parser.error("A fixed case/config+ID and output directory are required; run under CPC4 supervise.py")
    try:
        if args.config:
            selected = [c for c in json.loads(args.config.read_text(encoding="utf-8"))["cases"] if c["id"] == args.id]
            if len(selected) != 1:
                raise ValueError("The fixed configuration must contain this ID exactly once")
            case = selected[0]
        else:
            case = json.loads(args.case.read_text(encoding="utf-8"))
        if case.get("dual"):
            from src.channel_dual import run
            run(case, args.output)
        else:
            run_case(case, args.output)
    except Exception as error:
        put(args.output / "TECHNICAL_ERROR.json", {"type": type(error).__name__, "error": str(error),
                                                   "utc": datetime.now(timezone.utc).isoformat()})
        raise


if __name__ == "__main__":
    main()
