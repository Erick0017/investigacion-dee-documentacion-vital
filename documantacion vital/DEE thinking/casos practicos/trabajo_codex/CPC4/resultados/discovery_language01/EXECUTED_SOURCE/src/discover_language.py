"""Two directed lexical discovery continuations, without repeating A/B history."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--child", choices=("LEX_MINUS_FULL", "LEX_PLUS_FULL"))
    args = parser.parse_args()
    output = args.output.resolve()
    config_path = output / "CONFIG.json"
    if args.child:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if any(sha(ROOT / name) != value for name, value in config["source_sha256"].items()):
            raise RuntimeError("Discovery source changed before child start; do not silently relabel a freeze")
        case = next(c for c in config["cases"] if c["id"] == args.child)
        parent = ROOT / case["parent"]
        assert sha(parent) == case["parent_sha256"]
        import dee_thinking as d
        from src import channel
        from src.phase_language import forward
        assert d.__version__ == "4.0.0" and d.kernel_identity()["kernel_version"] == 27
        assert sha(d._native.__file__) == channel.NATIVE_SHA256
        world = d.OrganizationalWorld.load_snapshot(str(parent))
        assert world.runtime.current_tick == 169
        spec = channel.describe_dual()
        initial = channel.digest(world)
        destination = output / case["id"]
        world, measurements = forward(world, spec, case, destination)
        result = {"case": case, "parent_physical_state": initial, "same_genealogy_continuation": True,
                  "not_reconstructed_from_case_history": True, "measurements": measurements,
                  "source_sha256": config["source_sha256"], "config_sha256": sha(config_path),
                  "source_files_unchanged_after_run": all(sha(ROOT / n) == v for n, v in config["source_sha256"].items())}
        put(destination / "MEASUREMENTS.json", result)
        print(json.dumps({"id": case["id"], "classes": [x["resource_class"] for x in measurements["queries"]],
                          "sensors": [x["current_sensor"]["resource_present"] for x in measurements["lessons"]],
                          "available": [x["available"] for x in measurements["queries"]]}))
        return
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        cases = []
        for name, core in (("LEX_MINUS_FULL", "A_MINUS_B_COMPATIBLE_CONTEXT_MINUS"), ("LEX_PLUS_FULL", "A_PLUS_B_COMPATIBLE_CONTEXT_PLUS")):
            parent = ROOT / "resultados/discovery_dual01" / core / "MAIN_FINAL.deetsnap"
            cases.append({"id": name, "parent": parent.relative_to(ROOT).as_posix(), "parent_sha256": sha(parent),
                          "word_order": ["W1", "W2"], "mode": "full", "type": "DISCOVERY_CONTINUATION_OF_MEASURED_NATIVE_PARENT"})
        sources = {name: sha(ROOT / name) for name in ("src/channel.py", "src/phase_language.py", "src/discover_language.py", "src/common.py")}
        config = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": sources, "cases": cases,
                  "teaching_ticks": [169, 197], "queries": [236, 264], "emissions": [239, 267],
                  "actual_current_resource_sensor": True, "same_word_waveform_all_histories": True,
                  "decoder": "load21,direction(-1,+/-1,0), not word-specific", "full_NSM_semantics": False,
                  "scientific_status": "DISCOVERY; no confirmatory holdouts used or fitted"}
        put(config_path, config)
        for name in sources:
            target = output / "EXECUTED_SOURCE" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
    from supervise import run
    results = []
    for case in config["cases"]:
        folder = output / case["id"]
        if not (folder / "MEASUREMENTS.json").exists():
            job = run(ROOT, "language_discovery_" + case["id"].lower(),
                      [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--output", str(output), "--child", case["id"]], 180)
            if job["exit_code"] != 0:
                raise RuntimeError("Finite discovery child failed; preserve job and diagnose once")
        row = json.loads((folder / "MEASUREMENTS.json").read_text(encoding="utf-8"))
        results.append({"id": case["id"], "classes": [x["resource_class"] for x in row["measurements"]["queries"]],
                        "sensors": [x["current_sensor"]["resource_present"] for x in row["measurements"]["lessons"]],
                        "available": [x["available"] for x in row["measurements"]["queries"]], "evidence": str(folder / "MEASUREMENTS.json")})
        put(output / "RESULTS.json", {"config_sha256": sha(config_path), "cases": results})


if __name__ == "__main__":
    main()
