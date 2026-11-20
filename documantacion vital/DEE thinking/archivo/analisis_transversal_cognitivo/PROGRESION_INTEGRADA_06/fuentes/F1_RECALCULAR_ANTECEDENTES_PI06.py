"""Read-only extraction or portable recalculation of recorded historical data.

No DEE, NumPy, network, executable capsule or engine import is used.
Export copies selected JSON records, source excerpts and provenance; replay is
not implied. Recalculate reads only the exported evidence JSON.
"""
from __future__ import annotations
import argparse
import ast
import base64
import hashlib
import io
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record(blob: bytes, locator: str) -> dict:
    return {"locator": locator, "bytes": len(blob), "sha256": sha(blob)}


def functions(text: str, names: set[str]) -> list[dict]:
    lines = text.splitlines()
    return [{"name": a.name, "first_line": a.lineno, "last_line": a.end_lineno,
             "source": "\n".join(lines[a.lineno - 1:a.end_lineno])}
            for a in ast.parse(text).body
            if isinstance(a, ast.FunctionDef) and a.name in names]


def export(corpus: Path, native_book: Path) -> dict:
    result = {"schema": "DEE.PI06.F1.recorded_antecedents.v1",
              "scope": "SELECTED_PRIMARY_RECORDS_AND_SOURCE_EXCERPTS; no Native reproduction",
              "native_ticks_executed": 0, "sources": [], "experiments": {}}
    cb = corpus.read_bytes()
    result["sources"].append(record(cb, str(corpus.resolve())))
    with zipfile.ZipFile(io.BytesIO(cb)) as doc:
        bundle_name = "word/embeddings/DEE_V25_VOLUME2_FORENSIC_BUNDLE.zip"
        bundle = doc.read(bundle_name)
        result["sources"].append(record(bundle, str(corpus.resolve()) + "!" + bundle_name))
        with zipfile.ZipFile(io.BytesIO(bundle)) as z:
            specs = [
                ("sources/DEE_V25_NATIVE_FOUNDATIONAL_ENGINEERING_V20_PART_A.json",
                 "sources/dee_v25_native_foundational_engineering_v20_part_a.py",
                 ["HOLISTICREPAIR20X"], {"module_holisticrepair20", "_lean_macro20"}),
                ("sources/DEE_V25_NATIVE_CAPABILITY_EXPANSION_V21_PART_B.json",
                 "sources/dee_v25_native_capability_expansion_v21_part_b.py",
                 ["TRAINEDREPAIR21X", "HOMEOSTATICMEMBRANE21X"],
                 {"module_trainedrepair21", "_damage_route21", "_rehab_branch21", "module_homeostaticmembrane21"}),
            ]
            for primary, code, keys, fn in specs:
                b = z.read(primary)
                c = z.read(code)
                result["sources"].extend([record(b, bundle_name + "!" + primary), record(c, bundle_name + "!" + code)])
                d = json.loads(b)
                for key in keys:
                    result["experiments"][key] = {
                        "source_locator": bundle_name + "!" + primary,
                        "json_pointer": "/experiments/" + key,
                        "environment": d["environment"],
                        "record": d["experiments"][key],
                        "source_excerpts": functions(c.decode("utf-8"), fn),
                    }
        v5name = "word/embeddings/DEE_ORIGINAL_VOLUME_5.docx"
        v5 = doc.read(v5name)
        result["sources"].append(record(v5, str(corpus.resolve()) + "!" + v5name))
        with zipfile.ZipFile(io.BytesIO(v5)) as v:
            cname = "dee_reproduction/ETAPA_E_CIERRE_COMPACTO.zip"
            capsule = v.read(cname)
            result["sources"].append(record(capsule, v5name + "!" + cname))
            with zipfile.ZipFile(io.BytesIO(capsule)) as z:
                # Existing derived summary is explicitly marked as such. It is
                # not a recalculation from omitted NPZ data in this script.
                b = z.read("derived.json")
                d = json.loads(b)
                result["sources"].append(record(b, v5name + "!" + cname + "!derived.json"))
                result["EA3_followup_existing_derived"] = {
                    "modality": "EXISTING_DERIVED_SUMMARY_INSPECTED; not newly recomputed from full E1 telemetry or NPZ",
                    "rows": d["E1_resilience"], "by_world": d["E1_resilience_by_world"],
                }
                c = z.read("E1/dee_v27_e1_basin_resilience_hidden_state_v1.py")
                result["sources"].append(record(c, v5name + "!" + cname + "!E1/dee_v27_e1_basin_resilience_hidden_state_v1.py"))
                result["EA3_followup_existing_derived"]["source_excerpts"] = functions(c.decode("utf-8"), {"ea3", "macro_vector", "macro_distance"})
    del cb
    nb = native_book.read_bytes()
    result["sources"].append(record(nb, str(native_book.resolve())))
    with zipfile.ZipFile(io.BytesIO(nb)) as doc:
        xmlname = "customXml/dee_processing_capsule.xml"
        xb = doc.read(xmlname)
        root = ET.fromstring(xb)
        capsule = base64.b64decode(next(iter(root)).text)
        assert sha(capsule) == root.attrib["sha256"]
        result["sources"].extend([record(xb, str(native_book.resolve()) + "!" + xmlname),
                                  record(capsule, xmlname + "!base64:DEE_PN_CAPSULA_v1.zip")])
        with zipfile.ZipFile(io.BytesIO(capsule)) as z:
            name = "fuentes/C01/INPUTS/historical/DEE_V27_SPONTANEOUS_MORPHOGENESIS_AND_MULTISCALE_GEOMETRY_PART_D_V1.json"
            b = z.read(name)
            result["sources"].append(record(b, xmlname + "!base64:DEE_PN_CAPSULA_v1.zip!" + name))
            d = json.loads(b)
            code = d["runner"]["source_utf8"]
            assert sha(code.encode("utf-8")) == d["runner"]["sha256"]
            result["experiments"]["D7_EMERGENT_BASIN_ROBUSTNESS_27X"] = {
                "json_pointer": "/modules/D7_EMERGENT_BASIN_ROBUSTNESS_27X",
                "source_locator": name, "environment": d["environment"],
                "parameters": d["parameters"],
                "record": d["modules"]["D7_EMERGENT_BASIN_ROBUSTNESS_27X"],
                "runner_sha256": d["runner"]["sha256"],
                "source_excerpts": functions(code, {"_descriptor_distance", "_damage_masks", "_module_d7_basin_robustness"}),
            }
    return result


def d7vector(a: dict) -> list[float]:
    box = a["box_lacunarity"]["box_fit"]
    return [float(a["fast"]["density"]), math.log1p(float(a["fast"]["sreg_max"])),
            float(a["surface"]["surface_fraction"]), float(a["surface"]["face_per_voxel"]),
            float(box.get("dimension_slope", 0)) if box.get("available") else 0.0]


def recalculate(data: dict) -> dict:
    exp = data["experiments"]
    hol = exp["HOLISTICREPAIR20X"]["record"]["trials"]
    free = [r for r in hol if r["mode"] == "free_relax"]
    cues = [r for r in hol if r["mode"] == "same_class_cue"]
    strip = lambda r: {k: v for k, v in r.items() if k != "tick"}
    comparisons = []
    for row in exp["D7_EMERGENT_BASIN_ROBUSTNESS_27X"]["record"]["rows"]:
        control = {x["tick"]: x for x in row["traces"]["control"]}
        for kind, observed in row["comparison"].items():
            trace = {x["tick"]: x for x in row["traces"][kind]}
            for r in observed:
                tick = r["tick"]
                x = d7vector(trace[tick]["analysis"])
                y = d7vector(control[tick]["analysis"])
                distance = math.sqrt(sum(((a - b) / scale) ** 2
                                         for a, b, scale in zip(x, y, (1, 10, 1, 6, 3))))
                equals = trace[tick]["combined_sha256"] == control[tick]["combined_sha256"]
                comparisons.append({"world": row["world_id"], "condition": kind, "tick": tick,
                                    "recalculated_distance": distance,
                                    "recorded_distance": r["descriptor_distance_to_undamaged_control"],
                                    "abs_error": abs(distance - r["descriptor_distance_to_undamaged_control"]),
                                    "hash_equality_matches_record": equals == r["exact_full_state_equal"]})
    trained = exp["TRAINEDREPAIR21X"]["record"]["trials"]
    membrane = exp["HOMEOSTATICMEMBRANE21X"]["record"]["trials"]
    ea3 = data["EA3_followup_existing_derived"]["rows"]
    eprobe = [r for r in ea3 if r["function_interpretable"] is not None]
    return {
        "schema": "DEE.PI06.F1.historical_recalculation.v1", "native_ticks_executed": 0,
        "mode": "PASSIVE_RECALCULATION_FROM_EXPORTED_RECORDED_METRICS",
        "HOLISTICREPAIR20X": {
            "conditions": len(hol), "free_conditions": len(free), "cue_conditions": len(cues),
            "free_all_recorded_metrics_constant_t0_to1024": all(all(strip(r["trace"][0]) == strip(x) for x in r["trace"]) for r in free),
            "cue_matches_corresponding_damaged_free_from64": all(
                all(strip(x) == strip(next(f for f in free if f["n"] == r["n"] and f["label"] == r["label"])["trace"][0])
                    for x in r["trace"] if x["tick"] >= 64) for r in cues),
            "does_not_measure": "Functional recovery or unrecorded voxel identity is not inferred from macro equality."},
        "TRAINEDREPAIR21X": {"conditions": len(trained), "rows": trained,
            "rehab4_rehab16_sham16_same_gain_and_distance": len({(r["functional_gain"], r["distance_to_pre_damage_trained_state"]) for r in trained if r["mode"] != "no_rehab"}) == 1,
            "limitation": "No_rehab has0rehabcycles; no universal superiority or time-matched causal claim follows from its higher gain."},
        "HOMEOSTATICMEMBRANE21X": {"conditions": len(membrane), "cycles_per_condition": [len(r["cycles"]) for r in membrane],
            "open_aperture_stays0_all48": all(x["open_aperture_occupancy"] == 0 for r in membrane for x in r["cycles"]),
            "closed_aperture_stays9_all48": all(x["closed_aperture_occupancy"] == 9 for r in membrane for x in r["cycles"]),
            "limitation": "Fixed preparations did not show state-dependent aperture control; this is not a general impossibility result."},
        "D7": {"worlds": len(exp["D7_EMERGENT_BASIN_ROBUSTNESS_27X"]["record"]["rows"]),
            "metric_comparisons": len(comparisons), "max_abs_error": max(x["abs_error"] for x in comparisons),
            "all28_match_at1e_12": len(comparisons) == 28 and all(x["abs_error"] <= 1e-12 and x["hash_equality_matches_record"] for x in comparisons),
            "comparisons": comparisons,
            "limitation": "A5component macro return is distinct from functional recovery; the secondworld is alreadyempty. NoNPZ or engine replay is performed."},
        "EA3_existing_derived_coverage": {"conditions": len(ea3), "functional_probe_conditions": len(eprobe),
            "function_interpretable_true": sum(bool(r["function_interpretable"]) for r in eprobe),
            "modality": data["EA3_followup_existing_derived"]["modality"],
            "not_a_new_recalculation_of_E1_raw_or_fulltelemetry": True},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    a = sub.add_parser("export")
    a.add_argument("--corpus", type=Path, required=True)
    a.add_argument("--native-book", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("recalculate")
    a.add_argument("--evidence", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    arg = ap.parse_args()
    if arg.out.exists():
        raise SystemExit("Refusing to overwrite existing output")
    if arg.mode == "export":
        result = export(arg.corpus, arg.native_book)
    else:
        raw = arg.evidence.read_bytes()
        result = recalculate(json.loads(raw))
        result["input"] = record(raw, str(arg.evidence.resolve()))
    arg.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(arg.out), "bytes": arg.out.stat().st_size, "sha256": sha(arg.out.read_bytes()), "native_ticks": 0}))


if __name__ == "__main__":
    main()
