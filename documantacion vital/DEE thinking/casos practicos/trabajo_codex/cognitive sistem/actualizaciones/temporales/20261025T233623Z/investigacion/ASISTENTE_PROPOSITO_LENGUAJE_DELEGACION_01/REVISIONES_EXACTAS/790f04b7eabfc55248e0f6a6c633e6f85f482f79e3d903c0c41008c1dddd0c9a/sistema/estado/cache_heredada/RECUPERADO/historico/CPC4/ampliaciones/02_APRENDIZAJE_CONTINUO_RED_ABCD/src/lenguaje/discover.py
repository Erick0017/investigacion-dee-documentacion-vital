"""Freeze two bounded new-content panels before their first measurements."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from lenguaje.protocol import put, sha


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args(); output = ROOT / "resultados/lenguaje/discovery01"
    path = output / "EXPERIMENT_CONFIG.json"
    if path.exists(): config = json.loads(path.read_text(encoding="utf-8"))
    else:
        parent = ROOT / "resultados/red/v3_discovery01/FULL/T431.deetsnap"
        names = ("src/lenguaje/protocol.py", "src/lenguaje/worker.py", "src/lenguaje/discover.py",
                 "src/red/recipe_v3.py", "src/red/session_v3.py", "src/red/common_helpers.py")
        config = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "parent": parent.relative_to(ROOT).as_posix(),
                  "parent_sha256": sha(parent), "sources": {n: sha(ROOT / n) for n in names},
                  "cases": [{"id": "WORD_TO_PROFILE", "query_mode": "word"},
                            {"id": "CURRENT_PROFILE_TO_WORD", "query_mode": "name_role"}],
                  "phase": "Discovery after actual V3 network genealogy; neither branch is an unseen world",
                  "new_forms": ["BUENO", "MALO"], "full_NSM_semantics": False,
                  "physical_protocol": {"lessons": [431, 459], "new_external_episode": [438, 439, 444],
                                        "queries": [498, 526], "reads": [501, 529]},
                  "criterion": "Applied receipts and actual directional load21 (word) or vertical26 (common naming)",
                  "native_workers": 1, "timeout_seconds": 180}
        put(path, config)
        for n in names:
            target = output / "EXECUTED_SOURCE" / n; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / n, target)
    assert all(sha(ROOT / n) == value for n, value in config["sources"].items())
    assert sha(ROOT / config["parent"]) == config["parent_sha256"]
    for case in config["cases"]: put(output / "cases" / (case["id"] + ".json"), case)
    if args.freeze_only: print(json.dumps({"frozen": True, "sha256": sha(path)})); return
    import supervision
    rows = []
    for case in config["cases"]:
        destination = output / case["id"]
        if not (destination / "MEASUREMENTS.json").exists():
            command = [sys.executable, "-I", "-B", str(Path(__file__).with_name("worker.py")),
                       "--case", str(output / "cases" / (case["id"] + ".json")),
                       "--parent", str(ROOT / config["parent"]), "--output", str(destination)]
            job = supervision.run(ROOT, "language_discovery_" + case["id"].lower(), command, 180)
            if job["exit_code"] != 0: raise RuntimeError("Preserved discovery error; no identical retry")
        result = json.loads((destination / "MEASUREMENTS.json").read_text(encoding="utf-8"))
        rows.append({"id": case["id"], "profiles": [x["sensor"]["profile"] for x in result["lessons"]],
                     "readouts": result["readouts"], "evidence": (destination / "MEASUREMENTS.json").relative_to(ROOT).as_posix()})
        put(output / "RUN_SUMMARY.json", {"config_sha256": sha(path), "cases": rows})


if __name__ == "__main__": main()
