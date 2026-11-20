"""Pure-data calculations for remote-current-contact trials; no engine import."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    problems = []
    for path in sorted(args.results.glob("*/MEASUREMENTS.json")):
        value = json.loads(path.read_text(encoding="utf8"))
        geometry = value.get("geometry", {}).get("remote_contact", {})
        surfaces = {item["id"]: item for item in geometry.get("surfaces", [])}
        stages = []
        for index, observation in enumerate(value.get("remote_contact_observations", [])):
            if observation["stage"].startswith("pre_"):
                continue
            observations = []
            for item in observation["surfaces"]:
                state = item["physical"]
                for key in ("raw", "clock"):
                    if not isinstance(state[key], str) or not state[key].isdigit():
                        problems.append({"path": str(path), "problem": "inexact integer", "field": key})
                surface = surfaces[item["id"]]
                axis, z = surface["axis"], surface["z"]
                expected_direction = [0,1,z] if observation["stage"] in ("record", "use", "reuse") else [-axis,1,z]
                qualified = bool(state["active"] and state["semantic"] == 1
                    and state["direction"] == expected_direction and state["s_reg"] > 5)
                observations.append({"bank": item["id"], "raw": state["raw"], "clock": state["clock"],
                    "load": state["s_reg"], "direction": state["direction"],
                    "expected_physical_direction": expected_direction,
                    "qualified_current_content": qualified})
            stages.append({"tick": observation["tick"], "stage": observation["stage"],
                "observations": observations,
                "primary_locator": "remote_contact_observations/" + str(index)})
        trajectories = []
        initial = next((row for row in stages if row["stage"] == "record"), None)
        if initial:
            for item in initial["observations"]:
                if not item["qualified_current_content"]:
                    continue
                bank = item["bank"]
                previous = None
                first = None
                for index, route in enumerate(value.get("nominal_route_coverage", [])):
                    state = next(row for row in route["banks"] if row["id"] == bank)["Moore27"][13]
                    if state["raw"] != item["raw"]:
                        first = {"tick": route["tick"], "observed": state,
                            "primary_locator": "nominal_route_coverage/" + str(index),
                            "previous_covered_tick": previous}
                        break
                    previous = route["tick"]
                trajectories.append({"bank": bank, "association_tick": initial["tick"],
                    "acquired_raw": item["raw"], "first_unperturbed_route_deviation": first,
                    "qualification": "No unique lineage inferred after the first deviation. Later current routes require their own local evidence."})
        original_411 = next((frame for frame in value.get("frames", []) if frame["tick"] == 411), None)
        final_word = next((frame for frame in value.get("frames", []) if frame["tick"] == 616), None)
        rows.append({"directory": path.parent.name, "case": value["case"], "status": value["status"],
            "primary": str(path.relative_to(args.results)), "sha256": sha(path),
            "preparations": value.get("preparations",0), "continuations": value.get("continuations",0),
            "diagnostic_forks": value.get("diagnostic_forks",0), "parent": value.get("parent"),
            "stages": stages, "trace_diagnostics": trajectories,
            "receipt_statuses": value.get("receipt_statuses"),
            "original_contact_411": original_411.get("contact") if original_411 else None,
            "old_composite_word_616": final_word.get("joint") if final_word else None,
            "final_physical": value.get("final_physical"), "parent_unchanged": value.get("parent_unchanged"),
            "edits": value.get("edits"), "snapshots": value.get("snapshots",[])})
    output = {"schema": "CPC9.remote_contact.analysis.v1", "engine_imported": False,
        "classification": "These are exact-data observable calculations, not automatic attribution of TOUCH/learning/semantic mastery.",
        "formula": "qualified = active AND semantic1 AND acquiredload>probe5 AND direction matches frozen native expected vector. Separate first/second readers and action consequences.",
        "cases": rows, "problems": problems}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({"cases":len(rows),"problems":len(problems),"output":str(args.out)},ensure_ascii=False))


if __name__ == "__main__":
    main()
