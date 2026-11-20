"""Read existing CPC9 records only; no DEE import, replay, or simulation."""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
THINK = HERE.parents[3]
RUN = THINK / "casos practicos/trabajo_codex/CPC9/runs/RUN_20261019_165651"


def source(path: Path, pointer: str = "") -> dict:
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "pointer": pointer, "bytes": path.stat().st_size}


def main() -> None:
    original_path = RUN / "resultados/vida_integral/EI_D01/MEDICIONES.json"
    audit_path = RUN / "resultados/auditoria/COMPOSICION_E1/MEDICIONES.json"
    original = json.loads(original_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert source(original_path)["sha256"] == "ab12be445184fcf70102d0ce2d6077592f189615d597094d2fb569470a3ade6c"
    assert source(audit_path)["sha256"] == "ce8baacc95001750302ee3826d3dfc8902b1ec691f15bc5b7114b96bc84e2c54"
    frames = {int(f["tick"]): (i, f) for i, f in enumerate(original["frames"])}
    assert all(t in frames for t in (205, 206, 209, 210))
    assert 207 not in frames and 208 not in frames
    selected_stages = []
    for tick in (205, 206, 209, 210):
        i, frame = frames[tick]
        points = [dict(frame["view"]["common_join"]),
                  dict(frame["view"]["joint"]["plus.changed"]["use_site"])]
        if tick == 205:
            points = [dict(p) for p in audit["incoming"]] + points
        for p in points:
            p["raw"] = str(p["raw"])
            p["clock"] = str(p["clock"])
        selected_stages.append({"tick": tick, "N": 67, "points": points,
                                "physical_hashes": frame["physical"],
                                "source": source(original_path, f"/frames/{i}/view"),
                                "coverage": "Only observed nominal sites; not a dense world snapshot."})

    # The 7 is admitted through a prepared port. Do not manufacture its RAW at
    # T207/T208/T209, which were not observed along this route in these records.
    candidates = [(i, r) for i, r in enumerate(original["requests"])
                  if r["port"].startswith("joint.use.") and r["tick"] == 207]
    assert len(candidates) == 4
    admitted = []
    for i, r in candidates:
        key = r["port"].removeprefix("joint.use.")
        geometry = original["geometry"]["joint_names"][key]
        use_site = geometry["use_site"]
        # Literal port formula in the frozen relational_pair_v2.py, lines35-37.
        injection = [use_site[0], (use_site[1] + 3) % 67, use_site[2]]
        assert r["receipt"]["status"] == "applied"
        admitted.append({"source": source(original_path, f"/requests/{i}"),
                         "request": r, "N": 67, "port_definition": {
                             "injection_site": injection, "direction": [0, -1, 0],
                             "state": 1, "semantic": 1, "payload": 7,
                             "use_site": use_site, "raw_observed_at_injection": None,
                             "basis": "Prepared port definition plus applied receipt; not a retained physical frame."}})
    selected_7 = next(x for x in admitted if x["request"]["port"] == "joint.use.plus.changed")
    assert selected_7["port_definition"]["injection_site"] == [24, 15, 18]

    controls = []
    for index, condition in enumerate(audit["rows"]):
        if condition["condition"] not in ("cut_arrival_0", "sham_formed206"):
            continue
        obs = next(f for f in condition["frames"] if f["tick"] == 210)
        point = obs["view"]["joint"]["plus.changed"]["use_site"]
        controls.append({"condition": condition["condition"],
                         "pre_tick": condition["pre_tick"], "victim": condition["victim"],
                         "new_raw": str(condition["new_raw"]),
                         "clock_preserved": condition["clock_preserved"],
                         "parents_unchanged": condition["parents_unchanged"],
                         "full_original884_equal": condition["full_original884_equal"],
                         "consequence210": point,
                         "source": source(audit_path, f"/rows/{index}")})

    code_ranges = {
        "base_validada/cpc8/src/integracion/relational_pair.py": [[16, 28], [58, 74], [107, 110]],
        "base_validada/cpc8/src/integracion/relational_pair_v2.py": [[13, 45], [52, 70]],
        "src/vida_e1.py": [[1, 50]],
        "src/vida_integral.py": [[1, 75]],
        "tools/auditar_composicion_e1.py": [[1, 54]],
    }
    code = []
    for relative, ranges in code_ranges.items():
        path = RUN / relative
        code.append({**source(path), "read_lines_inclusive": ranges,
                     "executed": False})

    out = {
        "schema": "DEE.pilot10s.CPC9.existing_records.v1",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "N": 67, "life": "EI_D01", "run": str(RUN),
        "new_DEE_ticks": 0, "DEE_imports": False, "simulations_or_replays": False,
        "primary_sources": [source(original_path), source(audit_path)],
        "stages": selected_stages,
        "exact_local_composition": {"incoming205": audit["incoming"],
                                    "pre_Moore27": audit["pre_Moore27"],
                                    "formed206": audit["actual_formed206"],
                                    "local_branch_exact_historical_check": audit["local_branch_exact"],
                                    "source": source(audit_path, "/pre_Moore27")},
        "common_use_resource7": selected_7,
        "all_four_common_use_inputs": admitted,
        "controls": controls,
        "coverage": {
            "physical_frame_ticks_near_event": [t for t in frames if 195 <= t <= 216],
            "missing_physical_frame_ticks": [207, 208],
            "T209_exists_but_no_encounter_neighborhood": True,
            "T209_local_window_names": list(next(x for x in original["local_neighborhoods"] if x["tick"] == 209)["windows"]),
            "saved_snapshot_ticks": [int(x["physical"]["tick"]) for x in original["snapshots"]],
            "audit_frame_ticks": sorted({f["tick"] for x in audit["rows"] for f in x["frames"]}),
        },
        "source_code_read_only": code,
        "rendering_constraints": [
            "Use exact observed T205, T206, T209 nominal zeros and T210 states, with explicit stage cuts.",
            "Do not interpolate physical positions or claim measured continuity during T207/T208.",
            "Input7 may be marked as an admitted prepared opportunity at [24,15,18],T207,direction[0,-1,0], not as an observed RAW trajectory.",
            "The first local 26+30 to56 encounter has complete27-cell predecessor context in the historical audit.",
            "The second encounter is supported by functional consequence63 and selective controls, but its intermediate spatial meeting is not retained in these source frames.",
            "Equal loads or a direction-compatible extrapolation do not establish unique material ancestry.",
            "Diagnostic cuts are researcher interventions in copies, not autonomous removal; originals were not changed.",
            "Colour and camera can annotate, but cannot introduce an unobserved particle or path."
        ],
    }
    target = HERE / "COMPOSICION_CPC9_DATOS.json"
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(target), "bytes": target.stat().st_size,
                      "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                      "source_physical207208": False,
                      "T209_encounter_neighborhood": False,
                      "new_DEE_ticks": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
