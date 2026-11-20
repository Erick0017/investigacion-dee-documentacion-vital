"""Directed read-only R08 S01-S04 extraction. No DEE, owner, or tick API.

Only outputs in this directory. Uses the already archived stdlib-only passive
snapshot-v2 observer; exact complete RAW/clock buffers accompany sparse points.
"""
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import base64
import gzip
import hashlib
import importlib.util
import json
import sys

OUT = Path(__file__).resolve().parent
ARCHIVE = OUT.parents[1]
CAMPAIGN = ARCHIVE / "analisis_transversal_cognitivo/ECI02"
SYSTEM = CAMPAIGN / "estados/LAB_P0/sistema"
RESULTS = SYSTEM / "estado/eci02_resultados"
CHECKPOINTS = SYSTEM / "estado/checkpoints"
OBSERVER = ARCHIVE / "analisis_transversal_cognitivo/ECI01/codigo/base_cognitive_R01/sistema/capacidades/observador_causal_retrospectivo_01.py"
PROMPT = Path(r"C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\526B9225-56BC-4B15-904D-75BE040D1BB8\1-PROMPT_CODEX_DEE_R08_GUION_LITERAL_Y_CONTROL_VISUAL.docx")
ZIP = CAMPAIGN / "entrega/DEE_ECI02_RESULTADOS_R01.zip"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_json(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == ".gz" else b)


def dump_new(path, value, compressed=False):
    b = (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    if compressed:
        b = gzip.compress(b, mtime=0)
    with path.open("xb") as handle:
        handle.write(b)
    return {"path": str(path), "sha256": sha(b), "bytes": len(b)}


def receipts(row):
    if "requests" in row:
        return row["requests"]
    if isinstance(row.get("result"), dict):
        return receipts(row["result"])
    if isinstance(row.get("rows"), list):
        return [r for child in row["rows"] for r in receipts(child)]
    return row.get("word", {}).get("requests", []) + (row.get("interaction") or {}).get("requests", [])


def result_row(primary):
    return primary["request"]["result"]["result"].get("rows", [None])[0]


def main():
    sources = {}
    original = {}
    phases = ["IMPORT", "HISTORIA", "USO_COMUN", "DEMORA", "RESERVA", "RET_NARA", "RET_MA", "EXPORT"]
    for branch in ["EDAD", "MINUS", "PLUS"]:
        for phase in phases:
            label = "L_" + branch + "_" + phase
            path = RESULTS / ("ECI02_L_" + branch) / (label + ".json.gz")
            b = path.read_bytes()
            original[label] = read_json(path)
            sources[label] = {"path": str(path), "sha256": sha(b), "bytes": len(b),
                              "pointer": "/request/result/result/rows/0" if phase not in ["IMPORT", "DEMORA", "EXPORT"] and not (branch == "EDAD" and phase == "HISTORIA") else "/"}
    with ZipFile(ZIP) as z:
        for label, source in sources.items():
            member = Path(source["path"]).relative_to(CAMPAIGN).as_posix()
            source["archive_member"] = member
            source["archive_bytes_equal_local"] = sha(z.read(member)) == source["sha256"]
            assert source["archive_bytes_equal_local"], label
    protocol_path = CAMPAIGN / "datos/PROTOCOLO_ACCESO_APRENDIDO_ECI02_R03.json"
    protocol = read_json(protocol_path)
    protocol_sha = sha(protocol_path.read_bytes())
    assert all(x["protocol_sha256"] == protocol_sha for x in original.values())

    # No Native imports: this inspected observer imports only Python stdlib.
    spec = importlib.util.spec_from_file_location("r08_passive_snapshot_stdlib", OBSERVER)
    obs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obs)
    branches = {}
    channel_names = set()
    counts = Counter()
    for branch in ["EDAD", "MINUS", "PLUS"]:
        steps = {}
        for phase in phases:
            label = "L_" + branch + "_" + phase
            d = original[label]
            row = result_row(d) if "request" in d else None
            requests = receipts(row) if row else []
            statuses = Counter(q.get("receipt", {}).get("status", "MISSING") for q in requests)
            counts.update(statuses)
            channel_names.update(q.get("channel", q.get("port", "")) for q in requests)
            step = {"source": label, "source_path": sources[label]["path"], "source_sha256": sources[label]["sha256"],
                    "source_pointer": sources[label]["pointer"], "native_ticks_recorded": d["native_ticks_advanced"],
                    "requested": len(requests), "status_counts": dict(statuses),
                    "before": d.get("before"), "after": d.get("after")}
            if phase == "IMPORT":
                step["import"] = d["import"]
            if "request" in d:
                step["payload"] = d["request"]["payload"]
                step["request_status"] = d["request"]["status"]
                step["request_error"] = d["request"]["error"]
            if row is not None:
                # Exact archived local observations, receipts and empty frames
                # are retained. No dense trajectory is fabricated.
                step["row"] = row
            if phase in ["HISTORIA", "DEMORA"]:
                step["saved"] = d.get("saved")
            steps[phase] = step
        branches[branch] = {"life": "ECI02_L_" + branch, "steps": steps}
    assert counts == {"applied": 119, "rejected_occupied": 1}, counts
    for branch in ["EDAD", "MINUS"]:
        assert branches[branch]["steps"]["USO_COMUN"]["row"]["word"]["input_tick"] == 719915
        assert branches[branch]["steps"]["USO_COMUN"]["row"]["word"]["read_tick"] == 719919
        assert original["L_" + branch + "_DEMORA"]["native_ticks_advanced"] == 67

    snapshots = {}
    loaded = {}
    roi_bounds = {"luma": [[39, 3, 42], [51, 11, 52]],
                  "MA_alfa": [[29, 29, 29], [41, 37, 37]],
                  "MU_current": [[8, 9, 8], [20, 21, 20]]}
    for branch in ["EDAD", "MINUS"]:
        for tick, phase in [(719846, "IMPORT"), (719851, "HISTORIA")]:
            d = original["L_" + branch + "_" + phase]
            locator = d["import"] if phase == "IMPORT" else d["saved"]
            expected_sha = locator["snapshot_sha256"]
            matches = [p for p in CHECKPOINTS.glob(f"ECI02_L_{branch}.T{tick}.*.deetsnap.gz") if sha(p.read_bytes()) == expected_sha]
            assert len(matches) == 1, (branch, tick, "exact primary-pinned checkpoint not found")
            path = matches[0]
            snap = obs.Snapshot(path, verify_checksum=True)
            summary = snap.summary()
            expected = locator["physical"]
            assert all(summary[k] == expected[k] for k in ["N", "tick", "RAW_sha256", "clocks_sha256"])
            key = branch + "_T" + str(tick)
            loaded[key] = snap
            point_rows = [snap.observation(obs.coord(i, snap.N)) for i, value in enumerate(snap.raw) if value != 0]
            roi = {}
            for name, (lo, hi) in roi_bounds.items():
                roi[name] = {"bounds_inclusive": [lo, hi], "points": [snap.observation([x, y, z])
                    for x in range(lo[0], hi[0] + 1) for y in range(lo[1], hi[1] + 1) for z in range(lo[2], hi[2] + 1)],
                    "coverage": "Every site in the rectangular ROI, including RAW0 and RAW-nonzero/state0."}
            buffers = {}
            for name, values in [("RAW", snap.raw), ("clocks", snap.clocks)]:
                b = obs.pbytes(values)
                buffers[name] = {"codec": "uint64_little_endian+gzip+base64", "bytes": len(b),
                                 "sha256": sha(b), "data": base64.b64encode(gzip.compress(b, mtime=0)).decode("ascii")}
            snapshots[key] = {"life": "ECI02_L_" + branch, "N": snap.N, "tick": snap.tick,
                              "source_path": str(path), "source_sha256": snap.encoded_sha256,
                              "primary_source": "L_" + branch + "_" + phase,
                              "primary_pointer": "/import/snapshot_sha256" if phase == "IMPORT" else "/saved/snapshot_sha256",
                              "evidence_type": "A / Visualización de registros",
                              "summary": summary, "complete_buffers": buffers,
                              "points": point_rows, "ROI": roi,
                              "channels": {k: v for k, v in snap.channels.items() if k in channel_names or "luma" in k},
                              "pending": snap.pending,
                              "no_inferred_trajectory": True}
            print(json.dumps({"parsed": key, "checksum": snap.checksum_valid,
                              "RAW_nonzero": len(point_rows), "state0_nonzero": summary["state_zero_raw_nonzero"]}), flush=True)
    diff = {}
    for tick in [719846, 719851]:
        edad = loaded["EDAD_T" + str(tick)]
        minus = loaded["MINUS_T" + str(tick)]
        assert edad.tick == minus.tick and edad.N == minus.N
        rows = [{"site": obs.coord(i, edad.N), "EDAD": edad.observation(obs.coord(i, edad.N)),
                 "MINUS": minus.observation(obs.coord(i, edad.N))} for i, (a, b) in enumerate(zip(edad.raw, minus.raw)) if a != b]
        clock_diff = sum(a != b for a, b in zip(edad.clocks, minus.clocks))
        diff[str(tick)] = {"same_logical_tick": True, "RAW_difference_sites": len(rows), "clock_difference_sites": clock_diff,
                           "points": rows, "scope": "Exact matched-world field differences; not identification of individual memory sites or a unique causal lineage."}
    assert not diff["719846"]["points"] and diff["719846"]["clock_difference_sites"] == 0

    published_path = CAMPAIGN / "datos/PRUEBA_PUBLICACION_P1_ECI02_R01.json"
    published = read_json(published_path)
    verify = published["before_first_use_exact_pair_verification"]
    alias = {"source_path": str(published_path), "source_sha256": sha(published_path.read_bytes()),
             "source_pointer": "/before_first_use_exact_pair_verification",
             "lab_life": verify["candidate_life"], "published_life": published["life"],
             "pair": published["pair"], "source_physical": verify["physical"],
             "restoration": verify["restoration"],
             "subsequent_cycles": [{"index": x["index"], "before_tick": x["before"]["physical"]["tick"],
                                    "after_tick": x["after"]["physical"]["tick"]} for x in published["cycles"]]}
    code = SYSTEM / "capacidades/lexico_generico_apd03_r02.py"
    all_data = {"schema": "DEE.AUDIOVISUAL.R08.central.evidence.v1", "new_Native_ticks": 0,
                "new_experiments": 0, "scope": "S01-S04 only; original complete paired continuations and retained local observations.",
                "source_archive": {"path": str(ZIP), "sha256": sha(ZIP.read_bytes()), "members_checked": len(sources)},
                "sources": sources, "protocol": {"path": str(protocol_path), "sha256": protocol_sha,
                    "auditor_only": protocol["auditor_only"]},
                "passive_parser": {"path": str(OBSERVER), "sha256": sha(OBSERVER.read_bytes()), "stdlib_only": True},
                "branches": branches, "snapshot_panels": snapshots, "matched_RAW_differences": diff,
                "routing": {"source_path": str(code), "source_sha256": sha(code.read_bytes()),
                    "function": "use_relation", "code_lines": [264, 279],
                    "map": {"+1": "mu.current(a, datum)", "-1": "ma.query(a, context)"},
                    "scope": "Fixed host dispatch, opportunity and context prepared externally; acquired physical cue sign supplies the branch condition. Not P2/autonomous routing."},
                "alias_genealogy": alias,
                "denominator": {"requested": sum(counts.values()), "status_counts": dict(counts),
                    "scope": "All3branches history/common/reserve/nara/MA; includes PLUS rejected revision. These are material admissions, not correct-response rate."},
                "limitations": ["No dense frames in archived word.frames or interaction.frames for these common/reserve uses; show retained endpoints/local panels or labelled B stages.",
                    "T719851 is the common host request start; physical luma input is T719915 and lexical reader is T719919.",
                    "Reserved uses each follow67 idle ticks after their own completed use; the different selected protocols have different durations, so reserve absolute ticks differ.",
                    "EDAD inherited a prior positive luma association; it is not an untrained organism.",
                    "PLUS2/3 teacher admissions is not the EDAD control; MINUS3/3.",
                    "State0 can carry nonzero RAW. Every nonzero RAW and every clock buffer is preserved.",
                    "Do not credit the host's fixed if/else as an internally acquired routing policy."]}
    # Normalize four actual reader panels for direct consumption by root's renderer.
    readers = {}
    for branch in ["EDAD", "MINUS"]:
        for phase in ["USO_COMUN", "RESERVA"]:
            row = branches[branch]["steps"][phase]["row"]
            word = row["word"]
            readers[branch + "_" + phase] = {"N": 67, "life": "ECI02_L_" + branch,
                "tick": word["read_tick"], "input_tick": word["input_tick"],
                "input_site": word["requests"][0]["site"], "output": word["reader"]["formed_native_command"],
                "reader_sites": [x["site"] for x in word["reader"]["candidates"]],
                "points": word["reader"]["panel"], "reader_contract": {k: v for k, v in word["reader"].items() if k != "panel"},
                "input_receipts": word["requests"], "source": "L_" + branch + "_" + phase,
                "source_path": sources["L_" + branch + "_" + phase]["path"],
                "source_sha256": sources["L_" + branch + "_" + phase]["sha256"],
                "pointer": "/request/result/result/rows/0/word/reader", "evidence_type": "A / Visualización de registros locales"}
    all_data["reader_panels"] = readers
    metadata = dump_new(OUT / "CENTRAL_R08_DATOS_EXACTOS.json.gz", all_data, True)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(PROMPT) as z:
        body = ET.fromstring(z.read("word/document.xml"))
    paras = ["".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in body.findall("w:body/w:p", ns)]
    text = "\n".join(f"P{i:03d} {paras[i]}" for i in range(58, 142)) + "\n"
    with (OUT / "PROMPT_S01_S04_EXTRAIDO.txt").open("x", encoding="utf-8") as handle:
        handle.write(text)
    print(json.dumps({"output": metadata, "matched_differences": {k: {x: v[x] for x in ["RAW_difference_sites", "clock_difference_sites"]} for k, v in diff.items()},
                      "reader_cuts": {k: [v["input_tick"], v["tick"], v["output"]] for k, v in readers.items()},
                      "denominator": all_data["denominator"], "new_Native_ticks": 0}), flush=True)


if __name__ == "__main__":
    main()
