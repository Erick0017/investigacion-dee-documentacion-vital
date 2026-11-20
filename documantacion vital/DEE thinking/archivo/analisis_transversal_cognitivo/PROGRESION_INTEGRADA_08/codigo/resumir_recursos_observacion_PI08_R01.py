"""Metadatos cerrados de observación y recursos; no Native/DEE ni buffers reconstruidos."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parents[1]
LIMIT = 536870912


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))


def ref(p):
    return {"path": str(p), "bytes": p.stat().st_size, "sha256": sha(p)}


def body_rows(doc):
    result = doc.get("result")
    if isinstance(result, str): result = json.loads(result)
    if not isinstance(result, dict): return []
    if isinstance(result.get("result"), dict): result = result["result"]
    return result.get("rows", [])


def captures(row):
    """Sólo etapas y envoltorios explícitos; nunca progress/operational_dependencies."""
    value = row.get("external_global_capture")
    if isinstance(value, dict) and value.get("directory"): yield value
    for key in ("original_result", "first_stage", "second_stage", "FI"):
        value = row.get(key)
        if isinstance(value, dict): yield from captures(value)
    value = row.get("result")
    if isinstance(value, dict) and isinstance(value.get("rows"), list):
        for inner in value["rows"]: yield from captures(inner)


def main():
    close = P / "control/CIERRE_CIENTIFICO_PI08_R01.json"
    assert read(close)["all_scoped_Native_writers_closed"]
    sources = {}
    capture_refs = {}
    for name in ("PI08_B_REAL_R02.json", "PI08_B_NONE_R01.json", "PI08_B_YOKED_R01.json", "PI08_B_REFERENCE_R01.json"):
        q = P / "control" / name
        d = read(q)
        assert d["closed"]
        sources[str(q)] = ref(q)
        for row in d["rows"]:
            for cap in captures(row): capture_refs.setdefault(cap["directory"], []).append({"source": str(q), "ordinal": row["B_ordinal"], "metadata": cap})
    # C y A actuales, sólo primarios de esta campaña y sin recorrer su historia anidada.
    names = []
    for q in (P / "ensayos").iterdir():
        if q.is_file() and q.suffix == ".json" and q.name.startswith(("PI08_A2_", "PI08_A3_", "PI08_USO_PUBLICO_", "PI08_C_EVALUAR_R04_EP")):
            names.append(q)
    names.append(P / "estados/RP_A01/ensayos/ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01_R03_OP04.json")
    for q in names:
        d = read(q)
        for row in body_rows(d):
            for cap in captures(row): capture_refs.setdefault(cap["directory"], []).append({"source": str(q), "metadata": cap})
    # El F1 interrumpido no devolvió fila completa; su directorio observador conocido es acotado.
    f1_root = P / "estados/F1_CUT_R03/sistema/estado/observacion_pasiva/ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_F1_CUT_01"
    f1_dirs = []
    if f1_root.is_dir():
        children = list(f1_root.iterdir())
        assert len(children) <= 4
        for q in children:
            if q.is_dir() and (q / "INDEX.json").is_file():
                capture_refs.setdefault(str(q), []).append({"source": "F1 known closed observer directory; complete result row absent"})
                f1_dirs.append(str(q))
    actual = []
    for name, witnesses in sorted(capture_refs.items()):
        directory = Path(name).resolve(strict=True)
        assert directory.is_relative_to(P / "estados") and not directory.is_symlink()
        index_path = directory / "INDEX.json"
        plan_path = directory / "CAPTURA.json"
        index, plan = read(index_path), read(plan_path)
        frames = index["frames"]
        assert len(frames) == index["captured_frames"]
        anchors = sum(frame["kind"] == "anchor" for frame in frames)
        assert anchors == index["anchors"]
        payload_bytes = 0
        for frame in frames:
            name = frame["file"]
            assert Path(name).name == name
            q = directory / name
            assert q.is_file() and not q.is_symlink()
            assert q.stat().st_size == frame["compressed_bytes"] and sha(q) == frame["compressed_sha256"]
            payload_bytes += q.stat().st_size
        assert payload_bytes == index["compressed_payload_bytes"]
        for witness in witnesses:
            cap = witness.get("metadata")
            if cap:
                assert cap["index_sha256"] == sha(index_path)
                assert cap["captured_frames"] == len(frames)
        captured_ticks = {frame["tick"] for frame in frames}
        actual.append({"directory": str(directory), "provenance": plan.get("provenance"),
                       "index": ref(index_path), "capture_contract": ref(plan_path),
                       "actual_frames": len(frames), "actual_anchors": anchors,
                       "actual_delta_frames": len(frames)-anchors, "actual_compressed_payload_bytes": payload_bytes,
                       "planned_frames": len(plan["ticks"]),
                       "missing_planned_ticks": sorted(set(plan["ticks"])-captured_ticks),
                       "first_actual_tick": min(captured_ticks), "last_actual_tick": max(captured_ticks),
                       "sources": witnesses, "compressed_member_SHA_and_size_checked": True,
                       "RAW_clocks_reconstructed_by_this_summary": False})
    log = P / "ENSAYOS.jsonl"
    kind_counts, runs = Counter(), defaultdict(list)
    errors = []
    with log.open(encoding="utf-8-sig") as f:
        for ordinal, line in enumerate(f, 1):
            try: row = json.loads(line)
            except Exception as e:
                errors.append({"line": ordinal, "error": str(e)}); continue
            kind_counts[row.get("kind", "MISSING")] += 1
            if row.get("kind") == "OWNED_PROCESS_RESOURCES": runs[(row.get("run"), row.get("pid"))].append((ordinal, row))
    def summarize(rows):
        keys = ("peak_job_committed_bytes", "peak_process_committed_bytes", "working_set_bytes", "peak_working_set_bytes", "private_bytes", "cpu_user_seconds", "cpu_kernel_seconds", "elapsed_seconds")
        output = {"sample_count": len(rows), "maxima": {}, "missing_fields_all_samples": []}
        for key in keys:
            values = [(i, r[key]) for i, r in rows if type(r.get(key)) in (int, float)]
            if values:
                at, value = max(values, key=lambda x: x[1])
                output["maxima"][key] = {"value": value, "sample_ordinal": at}
            else: output["missing_fields_all_samples"].append(key)
        return output
    resource_rows = [{"run": run, "pid": pid, **summarize(rows),
                      "recorded_job_limits": sorted({r["job_memory_limit"] for _, r in rows if "job_memory_limit" in r})}
                     for (run, pid), rows in runs.items()]
    rp_path = P / "control/SUPERVISION_RP_A_PANEL12_PI08_R01.json"
    rp = read(rp_path)
    assert rp["closed"]
    rp_summary = {"source": ref(rp_path), "closed": rp["closed"], "exit_code": rp["exit_code"],
                  "actual_RP_supervisor_separate_from_ENSAYOS": True,
                  "memory_limit_bytes": rp["memory_limit_bytes"],
                  **summarize(list(enumerate(rp["samples"], 1)))}
    all_summaries = [*resource_rows, rp_summary]
    peaks = [r["maxima"]["peak_job_committed_bytes"]["value"] for r in all_summaries if "peak_job_committed_bytes" in r["maxima"]]
    anchors, deltas = sum(r["actual_anchors"] for r in actual), sum(r["actual_delta_frames"] for r in actual)
    out = {"schema": "DEE.PI08.final_resource_and_observation_readonly_summary.R01",
           "at_utc": datetime.now(timezone.utc).isoformat(), "new_Native_ticks": 0, "DEE_imports": 0,
           "closure": ref(close), "observation": {"capture_directories": len(actual),
               "actual_frames": anchors+deltas, "actual_anchors": anchors, "actual_delta_frames": deltas,
               "limits": {"anchors": 100, "delta_frames": 2000}, "anchors_within_limit": anchors <= 100,
               "delta_frames_within_limit": deltas <= 2000, "captures": actual,
               "F1_actual_incomplete_directories": f1_dirs,
               "scope": "Actual indexed compressed frames only, including interrupted F1. Native save/fork snapshots are operational diagnostics, not observer anchor frames. Fixed ROI reads and q1+8 small witnesses are different instruments. No planned frame is counted as captured."},
           "resources": {"ENSAYOS": ref(log), "kind_counts": dict(kind_counts), "invalid_lines": errors,
               "unique_resource_run_pid_groups": len(resource_rows), "groups": resource_rows,
               "RP_frontend_supervisor": rp_summary, "fixed_job_limit_bytes": LIMIT,
               "maximum_recorded_peak_job_committed_bytes": max(peaks) if peaks else None,
               "all_recorded_job_committed_peaks_within_limit": bool(peaks) and all(x <= LIMIT for x in peaks),
               "scope": "Committed Job/process memory, working set and private bytes are reported separately. These are sampled host-resource observations; absent fields and unsampled peaks are not reconstructed. They do not measure Native cognitive memory or demonstrate a leak."}}
    destination = P / "control/RECURSOS_Y_OBSERVACION_FINAL_PI08_R01.json"
    if destination.exists(): raise FileExistsError(destination)
    destination.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(destination), "sha256": sha(destination),
                      "frames": anchors+deltas, "anchors": anchors, "deltas": deltas,
                      "max_job_committed": max(peaks) if peaks else None,
                      "Native": 0, "buffers_reconstructed": False}, ensure_ascii=False))


if __name__ == "__main__": main()
