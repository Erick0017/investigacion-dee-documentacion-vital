"""Frozen five-trajectory inverse-access extension, one supervised worker at a time."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--child")
    args = parser.parse_args()
    output = args.output.resolve()
    config_path = output / "INVERSE_CONFIG.json"
    if args.child:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        for name, expected in config["sources"].items():
            if sha(ROOT / name) != expected: raise RuntimeError("Frozen inverse source changed")
        case = next(x for x in config["cases"] if x["id"] == args.child)
        parent = ROOT / config["parent"]
        assert sha(parent) == config["parent_sha256"]
        import dee_thinking as d
        from src import channel
        from src.inverse_language import inverse
        assert d.__version__ == "4.0.0" and sha(d._native.__file__) == channel.NATIVE_SHA256
        world = d.OrganizationalWorld.load_snapshot(str(parent))
        child, result = inverse(world, channel.describe_dual(), case, output / case["id"])
        assert child.runtime.current_tick == 334
        print(json.dumps({"id": case["id"], "symbols": result["emitted_symbols"], "available": result["available"], "parent_unchanged": result["parent_unchanged"]}))
        return
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        parent = ROOT / "resultados/confirmacion/MAIN_MINUS/LENGUAJE/MAIN_FINAL267.deetsnap"
        cases = [{"id": "PLUS_FULL", "bank": "plus", "mode": "full"},
                 {"id": "MINUS_FULL", "bank": "minus", "mode": "full"},
                 {"id": "PLUS_MEMORY_CUT_W1", "bank": "plus", "mode": "memory_cut"},
                 {"id": "MINUS_MEMORY_CUT_W1", "bank": "minus", "mode": "memory_cut"},
                 {"id": "PLUS_SHAM_DUMMY", "bank": "plus", "mode": "sham"}]
        names = ("src/channel.py", "src/common.py", "src/phase_language.py", "src/inverse_language.py", "src/run_inverse.py")
        sources = {name: sha(ROOT / name) for name in names}
        config = {"schema": "CPC4.INVERSE_EXTENSION.v1", "frozen_utc": datetime.now(timezone.utc).isoformat(),
                  "parent": parent.relative_to(ROOT).as_posix(), "parent_sha256": sha(parent),
                  "sources": sources, "cases": cases, "inputs": [303, 331], "readouts": [306, 334],
                  "decoder": "Physical responding region with load26 and diagonal(-1,+/-1,0); no class-to-word map",
                  "class_sensor": "Actual current resource path, fixed external presence/absence window; SAME probe5 to BOTH lexical regions",
                  "modality": "EXPLICIT_DIAGNOSTIC_FORK_AND_PHYSICAL_PROBE", "full_NSM_semantics": False,
                  "selection_before_new_readouts": True, "native_workers": 1, "timeout_per_trajectory_seconds": 180}
        put(config_path, config)
        for name in names:
            target = output / "EXECUTED_SOURCE" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
    from supervise import run
    rows = []
    for case in config["cases"]:
        measurement = output / case["id"] / "MEASUREMENTS.json"
        if not measurement.exists():
            job = run(ROOT, "inverse_" + case["id"].lower(), [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--output", str(output), "--child", case["id"]], 180)
            if job["exit_code"] != 0:
                rows.append({"id": case["id"], "status": "TECHNICAL_ERROR", "job": job})
                put(output / "RESULTS.json", {"config_sha256": sha(config_path), "cases": rows})
                raise RuntimeError("Preserved inverse child error; do not repeat identically")
        result = json.loads(measurement.read_text(encoding="utf-8"))
        rows.append({"id": case["id"], "symbols": result["emitted_symbols"], "available": result["available"],
                     "parent_unchanged": result["parent_unchanged"],
                     "observed_classes": [x["sensor"]["resource_present"] for x in result["windows"]],
                     "evidence": measurement.relative_to(ROOT).as_posix()})
        put(output / "RESULTS.json", {"config_sha256": sha(config_path), "cases": rows})


if __name__ == "__main__":
    main()
