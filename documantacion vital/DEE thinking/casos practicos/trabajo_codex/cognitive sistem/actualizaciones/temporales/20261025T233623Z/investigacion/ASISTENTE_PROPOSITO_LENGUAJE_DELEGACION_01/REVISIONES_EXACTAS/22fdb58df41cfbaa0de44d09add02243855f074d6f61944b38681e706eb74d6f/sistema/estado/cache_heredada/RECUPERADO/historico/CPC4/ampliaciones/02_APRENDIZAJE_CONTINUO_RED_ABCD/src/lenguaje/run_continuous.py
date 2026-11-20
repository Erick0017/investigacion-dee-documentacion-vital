"""Freeze controls and two genuinely new translated worlds before measurement."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from lenguaje.protocol import put, sha


def freeze(output):
    parent = ROOT / "resultados/red/curriculum03/T1431.deetsnap"
    variants = [("MAIN_NEW_FORMS", {}), ("NAMES_INVERTED", {"word_order": ["L2", "L1"]}),
                ("SIGNALS_OMITTED", {"teaching": "signal_omitted"}), ("REPORTS_OMITTED", {"teaching": "report_omitted"}),
                ("UNPAIRED_PLUS1", {"teaching": "unpaired"}), ("SECOND_WORLD_EPISODE_OMITTED", {"second_episode": False}),
                ("COMMON_NAME_CURRENT_ROLE", {"query_mode": "role"}), ("COMMON_NAME_CURRENT_SECOND", {"query_mode": "second"}),
                ("RESERVED_TRANSLATION_A", {"fresh": True, "translation": [17, 7, 5]}),
                ("RESERVED_ORDER_TRANSLATION_B", {"fresh": True, "translation": [9, 13, 2], "word_order": ["L2", "L1"]})]
    cases = [{"id": name, **params} for name, params in variants]
    names = ("src/lenguaje/protocol.py", "src/lenguaje/session.py", "src/lenguaje/continuous_worker.py", "src/lenguaje/run_continuous.py",
             "src/red/recipe_v3.py", "src/red/session_v3.py", "src/red/curriculum_v3.py", "src/red/common_helpers.py")
    config = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "parent": parent.relative_to(ROOT).as_posix(),
              "parent_sha256": sha(parent), "sources": {n: sha(ROOT / n) for n in names}, "cases": cases,
              "readouts": [1501, 1529], "query_ticks": [1498, 1526], "lesson_ticks": [1431, 1459],
              "new_external_episode": [1438, 1439, 1444], "native_workers": 1, "timeout_seconds": 240,
              "reserved_ids": [c["id"] for c in cases if c.get("fresh")],
              "criterion": "Word: actual21diagonal+Applied. Common name: local actual26vertical+both own receiptsApplied, evaluated independently per region.",
              "new_meaning_scope": "Two acquired mappings to task-relative current F7/R3 profiles, not general good/bad; all65full_NSM_semanticsFalse",
              "new_worlds": "Reserved worlds createT0 then0→431→931→1431→1529 in oneNativeinstance; controls restore one real1431 genealogy and never merge back."}
    put(output / "EXPERIMENT_CONFIG.json", config)
    for n in names:
        target = output / "EXECUTED_SOURCE" / n; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / n, target)
    for case in cases: put(output / "cases" / (case["id"] + ".json"), case)
    return config


def main():
    p = argparse.ArgumentParser(); p.add_argument("--freeze-only", action="store_true"); a = p.parse_args()
    output = ROOT / "resultados/lenguaje/continuous02"; path = output / "EXPERIMENT_CONFIG.json"
    config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else freeze(output)
    if a.freeze_only: print(json.dumps({"frozen": True, "sha256": sha(path), "cases": len(config["cases"])})); return
    assert all(sha(ROOT / n) == value for n, value in config["sources"].items())
    assert sha(ROOT / config["parent"]) == config["parent_sha256"]
    import supervision
    rows = []
    for case in config["cases"]:
        destination = output / case["id"]; file = destination / "MEASUREMENTS.json"
        if not file.exists():
            command = [sys.executable, "-I", "-B", str(Path(__file__).with_name("continuous_worker.py")), "--case",
                       str(output / "cases" / (case["id"] + ".json")), "--output", str(destination)]
            if not case.get("fresh"): command += ["--parent", str(ROOT / config["parent"])]
            job = supervision.run(ROOT, "language_continuous_" + case["id"].lower(), command, 240)
            if job["exit_code"] != 0:
                rows.append({"id": case["id"], "status": "TECHNICAL_ERROR", "job": job}); put(output / "RUN_SUMMARY.json", {"cases": rows})
                raise RuntimeError("Preserved error; no identical deterministic rerun")
        data = json.loads(file.read_text(encoding="utf-8"))
        rows.append({"id": case["id"], "status": "MEASURED", "new_preparation": data["new_preparation"],
                     "profiles": [x["sensor"]["profile"] for x in data["experiences"]], "readouts": data["readouts"],
                     "evidence": file.relative_to(ROOT).as_posix()})
        put(output / "RUN_SUMMARY.json", {"config_sha256": sha(path), "cases": rows})


if __name__ == "__main__": main()
