"""Passive synthesis of already saved measurements; never runs a Runtime."""
import json
from pathlib import Path
from .common import ROOT, put


def summarize():
    root = ROOT / "resultados/continuidad"; rows = []
    for family in ("M1_TEMPORAL_ACCESS", "M1_RENEWED_CYCLES"):
        config = json.loads((root / family / "EXPERIMENT_CONFIG.json").read_text(encoding="utf-8"))
        for case in config["cases"]:
            file = root / family / case["id"] / "MEASUREMENTS.json"
            data = json.loads(file.read_text(encoding="utf-8")); windows = []
            for window in data["windows"]:
                windows.append({"input_tick": window["input_tick"], "read_tick": window["read_tick"],
                                "cycle": window.get("cycle", 0),
                                "actual_sensor": window.get("actual_sensor", window.get("sensor")),
                                "physical_panel": {form: {"load": item["physical_output"]["s_reg"],
                                                           "direction": item["physical_output"]["direction"],
                                                           "active": item["physical_output"]["active"],
                                                           "receipts": [r["status"] for r in item["receipts"]],
                                                           "emitted_form": item["emitted_form"]}
                                                   for form, item in window["observations"].items()}})
            rows.append({"id": family + "/" + case["id"], "modality": "PHYSICAL_PROBE_WITH_EXTERNAL_CURRENT_SENSOR",
                         "evidence": file.relative_to(ROOT).as_posix(), "initial": data["initial"],
                         "final": data["final"], "windows": windows,
                         "not_independent_samples": "Windows and renewed cycles belong to one deterministic trajectory"})
    summary = {"measured_trajectories": len(rows), "architecture_family": "Inherited mobile directional relation",
               "native_state_edits_in_these_trajectories": [], "matrix": rows,
               "acquired_state_vs_access": "Real inherited acquired16 participates in new26vertical, then36/46; the new access acts before old destructive later interference.",
               "retained_matched_function": {"HAY": [239, 306, 373], "NO": [267, 334, 401]},
               "controls": ["Report omitted", "No acquired word signals", "Physical arrival one tick late", "Class switched"],
               "limitations": ["Reader and actual-class report are supplied by a fixed external protocol, not learned self-regulation.",
                               "Stable matched context preserved one function; the mismatching form can be consumed.",
                               "Known translated world is not relabelled as an unseen fresh holdout.",
                               "New access does not prove restoration after complete causal-state destruction.",
                               "Class absence is an external finite packet-window transduction, not native absence perception.",
                               "No universal NSM semantics or unbounded conversation is inferred."]}
    put(root / "CONTINUITY_SUMMARY.json", summary)
    return summary


if __name__ == "__main__": summarize()
