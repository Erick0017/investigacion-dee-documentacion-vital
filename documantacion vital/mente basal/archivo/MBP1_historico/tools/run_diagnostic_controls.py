from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def run_case(habitat, name: str, omit_environment: bool, omit_context: bool) -> dict:
    config = habitat.default_config()
    config["threads"] = 1
    runtime, g, _ = habitat.build_x0(config)
    receipts = []
    for channel, load, at_tick, _origin in habitat.INITIAL_INPUTS:
        if omit_environment and channel.startswith("environment."):
            continue
        receipts.append(runtime.experience(channel, at_tick, load))
    started = time.perf_counter_ns()
    readings = {}
    runtime.run_until(30)
    readings["carrier_after_environment"] = habitat.observe_site(runtime, g.update_redirect)
    runtime.run_until(34)
    readings["response_before_revision"] = habitat.observe_site(runtime, g.response1)
    runtime.run_until(38)
    readings["environmental_revision"] = habitat.observe_site(runtime, g.revision1)
    runtime.run_until(40)
    for channel, load, at_tick, _origin in habitat.LATE_INPUTS:
        if omit_context and channel == "context.experience":
            continue
        receipts.append(runtime.experience(channel, at_tick, load))
    runtime.run_until(46)
    readings["response_use_1"] = habitat.observe_site(runtime, g.response2)
    runtime.run_until(48)
    readings["context_merge"] = habitat.observe_site(runtime, g.aux_hub_context)
    runtime.run_until(58)
    readings["response_use_2"] = habitat.observe_site(runtime, g.response3)
    runtime.run_until(64)
    elapsed = time.perf_counter_ns() - started
    return {
        "case": name,
        "modality": "diagnostic independent world",
        "omit_environment_sources": omit_environment,
        "omit_late_context_experience": omit_context,
        "tick": int(runtime.current_tick),
        "requested_inputs": len(receipts),
        "applied_inputs": sum(
            runtime.receipt(item.id).status == habitat.dee.EventStatus.APPLIED
            for item in receipts
        ),
        "wall_ns": elapsed,
        "readings": readings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "app"))
    import habitat

    cases = [
        run_case(habitat, "FULL", False, False),
        run_case(habitat, "ENVIRONMENT_SOURCE_CUT", True, False),
        run_case(habitat, "LATE_CONTEXT_CUT", False, True),
    ]
    by_name = {case["case"]: case for case in cases}
    value = lambda case, key: int(by_name[case]["readings"][key]["s_reg"])
    contrasts = {
        "environment_delta_on_carrier": (
            value("FULL", "carrier_after_environment") -
            value("ENVIRONMENT_SOURCE_CUT", "carrier_after_environment")
        ),
        "environment_delta_on_revision": (
            value("FULL", "environmental_revision") -
            value("ENVIRONMENT_SOURCE_CUT", "environmental_revision")
        ),
        "late_context_delta_at_hub": (
            value("FULL", "context_merge") -
            value("LATE_CONTEXT_CUT", "context_merge")
        ),
    }
    result = {
        "schema": "mente-basal.diagnostic-controls.v1",
        "product": "DEE thinking 2.2.0",
        "kernel": "DEE v27",
        "backend": "Lazy, 1 thread",
        "cases": cases,
        "contrasts": contrasts,
        "interpretation_limit": (
            "These isolated causal controls localize prepared environmental and "
            "late-context contributions. They do not establish autonomous learning."
        ),
    }
    habitat.atomic_json(args.output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
