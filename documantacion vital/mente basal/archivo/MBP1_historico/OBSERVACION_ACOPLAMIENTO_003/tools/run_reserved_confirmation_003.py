from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_runner(path: Path):
    spec = importlib.util.spec_from_file_location("observation_coupling_003", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load experiment runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    tool = Path(__file__).with_name("run_observation_coupling_003.py")
    runner = load_runner(tool)
    sys.path.insert(0, str(root / "app"))
    import habitat
    dee = habitat.dee
    checkpoint = args.checkpoint.resolve()
    output_dir = args.output.resolve().parent
    result = {
        "schema": "mente-basal.observation-coupling-003.reserved.v1",
        "checkpoint": str(checkpoint),
        "same_lineage_not_independent_replication": True,
        "purpose": "same frozen protocol applied after the primary run to the earlier CUT_002 checkpoint; covariant same-lineage evidence, not an independent replicate",
        "functional_40_intact": runner.functional_40_case(
            dee, checkpoint, output_dir, "INTACT", "lazy", False),
        "coupling_intact": runner.coupling_case(
            dee, checkpoint, output_dir, "INTACT", "lazy", False),
        "coupling_subthreshold": runner.coupling_case(
            dee, checkpoint, output_dir, "SUBTHRESHOLD", "lazy", False),
    }
    habitat.atomic_json(args.output.resolve(), result)
    print(json.dumps({"output": str(args.output.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
