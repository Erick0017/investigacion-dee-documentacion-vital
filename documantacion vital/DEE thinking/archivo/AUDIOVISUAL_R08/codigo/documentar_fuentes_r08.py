"""Document the frozen R08 montage, without rendering or native execution.

The canonical physical hash covers only the observed displayed cells, N and
tick. It is NOT a whole-world identity, a lineage tag, or a count of DEE events.
Camera, crop, role, labels, progress and source filenames are excluded.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import importlib.abc
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "codigo"))


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"dee_thinking", "sqlite3", "_sqlite3"}:
            raise RuntimeError("Native/SQLite imports prohibited in this mapping")
        return None


sys.meta_path.insert(0, NoNative())
import pipeline_r08 as pipeline

UNKNOWN = "unknown: not stated in the selected frozen evidence"
PHYSICAL_KEYS = ("site", "raw", "clock", "state", "s_reg", "semantic", "direction", "tick", "active")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def unique(values):
    out = {}
    for v in values:
        if v is not None and v != [] and v != {} and v != "":
            out[digest(v)] = v
    return list(out.values())


def walk(value):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from walk(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk(v)


def refs(value):
    out = []
    for d in walk(value):
        path = d.get("source_path", d.get("path", d.get("resolved_source")))
        sha = d.get("source_sha256", d.get("sha256"))
        if isinstance(path, str) and isinstance(sha, str) and len(sha) == 64:
            keep = {"source_path": path, "source_sha256": sha}
            for key in ("pointer", "json_pointer", "source_container", "container_pointer", "RAW_sha256", "clocks_sha256"):
                if key in d:
                    keep[key] = d[key]
            out.append(keep)
    return unique(out)


def stripped_points(points):
    out = []
    for p in points:
        d = {k: p[k] for k in PHYSICAL_KEYS if k in p}
        if "raw" in d:
            d["raw"] = str(d["raw"])
        if "clock" in d:
            d["clock"] = str(d["clock"])
        out.append(d)
    return sorted(unique(out), key=lambda d: canonical(d))


def brief_reader(value):
    if value is None:
        return UNKNOWN
    if not isinstance(value, dict):
        return {"canonical_reader_record_sha256": digest(value), "container_type": type(value).__name__,
                "summary": [brief_reader(v) for v in value] if isinstance(value, list) else value}
    header = {k: v for k, v in value.items() if k not in {"panel", "observations", "frames", "original_result", "social_reads", "physical_social_readings", "contract"}}
    return {"canonical_reader_record_sha256": digest(value), "keys": list(value), "summary": header,
            "observation_count": len(value.get("panel", value.get("observations", []))),
            "nested_contract_sha256": digest(value["contract"]) if "contract" in value else None}


def source_cases(model, infrastructure):
    found = []
    for r in refs(model):
        pointer = r.get("pointer", r.get("json_pointer", ""))
        if pointer.startswith("/cases/"):
            key = pointer.split("/")[2]
            if key in infrastructure["cases"]:
                found.append((key, infrastructure["cases"][key]))
    return list({k: v for k, v in found}.items())


def shallow_case_provenance(case):
    selected = {k: v for k, v in case.items() if k in {
        "source", "original_primary", "selected_essential_source", "original_source", "original_source_sha256",
        "parent_snapshot", "parent_snapshot_sha256", "passive_source"}}
    for group in ("arms", "records"):
        if group in case:
            selected[group] = {k: {n: v for n, v in value.items() if n in {"source", "original_primary", "life", "N"}}
                               for k, value in case[group].items()}
    if isinstance(case.get("original_source"), str) and case.get("original_source_sha256"):
        selected["original_source_record"] = {"path": case["original_source"], "sha256": case["original_source_sha256"]}
    if isinstance(case.get("parent_snapshot"), str) and case.get("parent_snapshot_sha256"):
        selected["parent_snapshot_record"] = {"path": case["parent_snapshot"], "sha256": case["parent_snapshot_sha256"]}
    return selected


def add_run(runs, frame):
    if runs and runs[-1][1] + 1 == frame:
        runs[-1][1] = frame
    else:
        runs.append([frame, frame])


def build():
    script_hash = file_sha(__file__)
    frozen_files = [ROOT / "codigo" / n for n in ["pipeline_r08.py", "render_r08.py", "escenas_centrales_r08.py",
                    "escenas_mecanismos_r08.py", "escenas_principal_r08.py", "escenas_editoriales_r08.py"]]
    frozen = {str(p.relative_to(ROOT)): file_sha(p) for p in frozen_files}
    shotlist = load(ROOT / "guion_fuente/SHOTLIST_R08.json")
    schedule = load(ROOT / "audio/TIEMPOS_ANCLAS_R08.json")
    infrastructure = load(ROOT / "infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json")
    literal = {sh["shot_id"]: (scene, sh) for scene in shotlist["scenes"] for sh in scene["shots"]}
    timelines = {row["shot_id"]: row for row in schedule["rows"]}
    source_registry, receipt_registry, reader_registry, physical_registry, shots = {}, {}, {}, {}, {}

    def register_source(ref):
        key = digest(ref)
        source_registry[key] = ref
        return key

    for frame in range(11700):
        model, timing = pipeline.frame_model(frame)
        shot_id = timing["shot_id"]
        scene, sh = literal[shot_id]
        top = shots.setdefault(shot_id, {"scene_id": scene["scene_id"], "shot_id": shot_id,
             "literal_anchor": sh["anchor_exact"], "literal_anchor_source_paragraph_1based": sh.get("anchor_source_paragraph_1based"),
             "schedule": timelines[shot_id], "variants": {}, "case_id": [], "branch_id": [], "parent_id": [], "N": [],
             "source_path": [], "source_sha256": [], "ticks": [], "input_receipts": [], "reader_contract": [],
             "fields_shown": [], "ROI": [], "evidence_type": [], "replay_status": [],
             "supported_claim": [], "limitations": [], "source_refs": [], "source_case_context": [],
             "physical_observation_sha256": [], "displayed_labels": []})
        case_context = source_cases(model, infrastructure)
        rr = refs(model)
        for key, case in case_context:
            rr += refs(shallow_case_provenance(case))
        source_ids = sorted(register_source(x) for x in unique(rr))
        panels = model.get("panels", [])
        phys_panels, rec_ids, reader_ids = [], [], []
        source_context = pipeline.source_rows(model)
        for panel in panels:
            pp = {"N": panel.get("N"), "tick": panel.get("tick"), "observed_cells": stripped_points(panel.get("points", []))}
            phys_panels.append(pp)
            for entry in panel.get("input_receipts", []):
                key = digest(entry); receipt_registry[key] = entry; rec_ids.append(key)
            reader = panel.get("reader_evidence", panel.get("reader_contract"))
            if reader is not None:
                key = digest(reader); reader_registry[key] = brief_reader(reader); reader_ids.append(key)
        for entry in source_context.get("input_receipts", []) if isinstance(source_context, dict) else []:
            key = digest(entry); receipt_registry[key] = entry; rec_ids.append(key)
        if isinstance(source_context, dict) and source_context.get("reader_contract") is not None:
            reader = source_context["reader_contract"]
            key = digest(reader); reader_registry[key] = brief_reader(reader); reader_ids.append(key)
        physical_hash = digest(phys_panels) if phys_panels else None
        if physical_hash:
            physical_registry.setdefault(physical_hash, {"scope": "Observed displayed subset, not a complete world or a lineage tag",
                "point_count": sum(len(x["observed_cells"]) for x in phys_panels),
                "panel_N_tick": [{"N": x["N"], "tick": x["tick"]} for x in phys_panels],
                "source_ref_ids": []})["source_ref_ids"] = sorted(set(physical_registry.get(physical_hash, {}).get("source_ref_ids", [])) | set(source_ids))
        rois = [p.get("bounds", model.get("bounds", UNKNOWN)) for p in panels]
        known = [model, source_context] + panels + [c for _, c in case_context]
        # Only named IDs from the record are retained. Display labels are not life IDs.
        for field in ("case_id", "branch_id", "parent_id", "N"):
            vals = [d[field] for d in known if isinstance(d, dict) and field in d]
            if field == "case_id":
                vals += [k for k, _ in case_context]
                vals += [d["life"] for d in panels if "life" in d]
            top[field] += vals
        top["ticks"] += [p["tick"] for p in panels if p.get("tick") is not None]
        top["ticks"] += source_context.get("ticks", []) if isinstance(source_context, dict) else []
        top["input_receipts"] += rec_ids; top["reader_contract"] += reader_ids
        top["source_refs"] += source_ids
        top["fields_shown"] += [d["fields_shown"] for d in known if isinstance(d, dict) and "fields_shown" in d]
        top["ROI"] += rois; top["evidence_type"].append(model.get("evidence_type", UNKNOWN))
        top["replay_status"].append(model.get("replay_status", "No new replay or Native evolution; offline projection of archived evidence / explicit schematic"))
        top["supported_claim"] += [d["supported_claim"] for d in known if isinstance(d, dict) and d.get("supported_claim")]
        top["limitations"] += [v for d in known if isinstance(d, dict) for v in d.get("limitations", d.get("limits", []))]
        top["source_case_context"] += [{"case_id": k, "life": c.get("life", UNKNOWN), "N": c.get("N", UNKNOWN),
            "representation": c.get("representation", UNKNOWN), "limits": c.get("limits", [])} for k, c in case_context]
        top["physical_observation_sha256"] += [physical_hash] if physical_hash else []
        top["displayed_labels"] += [model.get("title", "")] + [p.get("label", "") for p in panels]
        variant = {"physical_observation_sha256": physical_hash, "sources": source_ids,
                   "input_receipts": sorted(set(rec_ids)), "reader_contract": sorted(set(reader_ids)),
                   "N": [p.get("N", UNKNOWN) for p in panels], "ticks": [p.get("tick", UNKNOWN) for p in panels],
                   "ROI": rois, "evidence_type": model.get("evidence_type", UNKNOWN),
                   "displayed_outputs": [p.get("output_text") for p in panels],
                   "external_event_canonical_sha256": digest(model["external_event"]) if model.get("external_event") else None}
        key = digest(variant)
        v = top["variants"].setdefault(key, dict(variant, frame_ranges_inclusive=[]))
        add_run(v["frame_ranges_inclusive"], frame)

    rows = []
    for shot_id, top in shots.items():
        scene, sh = literal[shot_id]
        for key, value in list(top.items()):
            if isinstance(value, list): top[key] = unique(value)
        top["source_path"] = unique([source_registry[k]["source_path"] for k in top["source_refs"]])
        top["source_sha256"] = [{"source_path": source_registry[k]["source_path"], "source_sha256": source_registry[k]["source_sha256"]} for k in top["source_refs"]]
        for field in ("case_id", "branch_id", "parent_id", "N", "ticks", "input_receipts", "reader_contract", "fields_shown", "ROI"):
            if not top[field]: top[field] = [UNKNOWN]
        if not top["supported_claim"]:
            top["supported_claim"] = ["Selected archived observations support the bounded literal explanation only; no broader capability is inferred."]
        top["limitations"] = unique(top["limitations"] + [scene.get("prohibitions_exact", ""),
            "A change of displayed subset, camera, marker, label or editorial progress is not itself a DEE physical event.",
            "No missing branch, parent, input receipt or reader contract has been inferred from a display label."])
        top["source_contract_from_literal_document"] = scene.get("source_contract_exact", UNKNOWN)
        top["variants"] = [{"variant_id": k, **v} for k, v in top["variants"].items()]
        top["source_sha256"] = unique(top["source_sha256"])
        if not timelines[shot_id]["explicit_silence"]:
            rows.append({"scene_id": top["scene_id"], "shot_id": shot_id, "start_s": timelines[shot_id]["actual_start_s"],
                "end_s": timelines[shot_id]["actual_end_s"], "afirmacion_literal": sh["anchor_exact"],
                "source_document_paragraph": sh.get("anchor_source_paragraph_1based"),
                "literal_sha256_utf8": hashlib.sha256(sh["anchor_exact"].encode()).hexdigest(),
                "case_id": json.dumps(top["case_id"], ensure_ascii=False),
                "branch_id": json.dumps(top["branch_id"], ensure_ascii=False),
                "fuentes_exactas": json.dumps([{"source_ref_id": k, **source_registry[k]} for k in top["source_refs"]], ensure_ascii=False, separators=(",", ":")),
                "evidence_type": " | ".join(top["evidence_type"]),
                "alcance": " | ".join(top["supported_claim"]),
                "limites": " | ".join(top["limitations"]),
                "visual_mapping": "FUENTES_VISUALES_R08.json#/shots/" + shot_id,
                "fisica_sha256": " | ".join(top["physical_observation_sha256"]),
                "model_timing_not_ASR": True})
    assert len(shots) == 46 and len(rows) == 45
    assert frozen == {str(p.relative_to(ROOT)): file_sha(p) for p in frozen_files}
    assert script_hash == file_sha(__file__)
    output = {"schema": "DEE.R08.sources_by_shot.R01", "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "new_native_ticks": 0, "rendered_frames": 0, "models_enumerated_without_render": 11700,
        "shot_count": len(shots), "spoken_anchor_count": len(rows),
        "inputs": {"shotlist_sha256": file_sha(ROOT / "guion_fuente/SHOTLIST_R08.json"),
                   "schedule_sha256": file_sha(ROOT / "audio/TIEMPOS_ANCLAS_R08.json"),
                   "infrastructure_sha256": file_sha(ROOT / "infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json"),
                   "script_sha256": script_hash, "frozen_visual_source_sha256": frozen},
        "hash_contract": {"serialization": "UTF-8 JSON sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False",
             "physical_observation_sha256": "Canonical list of panels {N,tick,observed_cells}, each cell restricted to site,raw,clock,state,s_reg,semantic,direction,tick,active. RAW/clocks remain exact strings; roles,ROI,cameras,labels,progress,filenames omitted.",
             "scope_limit": "Hash covers displayed retained observations, not a full causal state. Different crops can have different hashes at the same physical tick. Counts of variants/hashes are not counts of physical events, memories or independent experiences.",
             "source_sha256": "Recorded byte hash of each original/container source file, separately from the canonical observed-data hash. No claim that every historical original was rehashed in this mapping.",
             "render_source_data_hash": "Not used as physical identity: renderer source_data_hash can include editorial progress and annotations.",
             "schematic_C": "No native physical observation hash when there are no observed DEE panels; schematic changes are editorial."},
        "shots": shots, "source_registry": source_registry, "receipt_registry": receipt_registry,
        "reader_registry": reader_registry, "physical_observation_registry": physical_registry,
        "unknown_policy": UNKNOWN,
        "limitations": ["No simulation,replay,training,restore or material query was performed.",
            "No new scientific claims;45literal anchors are preserved and linked to bounded archived evidence or explicit explanatory diagrams.",
            "Historical paths remain as recorded; portable extracted evidence containers are additional sources, not invented replacements for missing originals."]}
    jp = ROOT / "FUENTES_VISUALES_R08.json"
    jp.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cp = ROOT / "AFIRMACIONES_R08.csv"
    with cp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"shots": len(shots), "anchors": len(rows), "sources": len(source_registry),
        "physical_subsets": len(physical_registry), "variants": sum(len(s["variants"]) for s in shots.values()),
        "outputs": [{"path": str(p), "bytes": p.stat().st_size, "sha256": file_sha(p)} for p in (jp, cp)],
        "Native_ticks": 0, "rendered_frames": 0}, ensure_ascii=False))


if __name__ == "__main__":
    build()
