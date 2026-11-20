from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGED = HERE.parent.name == "18_NATIVE_PERSISTENT_LEARNING"
CONT = HERE.parent if PACKAGED else HERE.parent / "18_NATIVE_PERSISTENT_LEARNING"
WORK = CONT.parent if PACKAGED else HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WORK / "source"))

import dee_thinking as dee
from mbp4_obp import sha256, write_json


def digest(values: list[int]) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def signature(runtime):
    return {
        "tick": int(runtime.current_tick),
        "raw_sha256": digest(runtime.raw_copy()),
        "clock_sha256": digest(runtime.clock_copy()),
        "occupied": int(runtime.metrics().occupied),
        "raw_support": int(runtime.metrics().raw_support),
        "s_reg_sum": int(runtime.metrics().s_reg_sum),
    }


def main() -> None:
    t0_path = CONT / "CHECKPOINTS" / "MBP4_NATIVE_MAIN_T000032_NATIVE_WORLD_T0.deetsnap"
    final_path = CONT / "CHECKPOINTS" / "MBP4_NATIVE_MAIN_FINAL.deetsnap"
    delivered = dee.Runtime.load_snapshot(str(final_path))
    t0_dense = dee.Runtime.load_snapshot(str(t0_path))
    t0_lazy = dee.Runtime.load_snapshot(str(t0_path))
    t0_lazy.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)

    before = signature(t0_dense)
    _ = t0_dense.observe(dee.Coordinate(34, 34, 34))
    observe_passive = signature(t0_dense) == before
    t0_dense.advance(46)
    t0_lazy.advance(46)
    dense = signature(t0_dense)
    lazy = signature(t0_lazy)
    final = signature(delivered)

    payload = bytearray(final_path.read_bytes())
    payload[len(payload) // 2] ^= 0x01
    invalid_rejected = False
    invalid_error = None
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".deetsnap", delete=False) as handle:
            handle.write(payload)
            tmp_name = handle.name
        try:
            dee.Runtime.load_snapshot(tmp_name)
        except Exception as exc:
            invalid_rejected = True
            invalid_error = f"{type(exc).__name__}: {exc}"
    finally:
        if tmp_name:
            Path(tmp_name).unlink(missing_ok=True)

    atlas = json.loads((CONT / "LANDSCAPE_ATLAS" / "CAUSAL_LANDSCAPE_ATLAS.json").read_text(encoding="utf-8"))
    gates = json.loads((CONT / "TELEMETRY" / "MBP4_NATIVE_LEARNING_GATE_LEDGER.json").read_text(encoding="utf-8"))
    result = {
        "schema": "mbp4.native-learning-validation.v1",
        "t0": {"path": str(t0_path.relative_to(CONT)), "sha256": sha256(t0_path), **before},
        "delivered": {"path": str(final_path.relative_to(CONT)), "sha256": sha256(final_path), **final},
        "replay_dense": dense,
        "replay_lazy": lazy,
        "replay_exact_delivered": dense == final,
        "dense_lazy_exact": dense == lazy,
        "observe_passive": observe_passive,
        "invalid_snapshot_rejected": invalid_rejected,
        "invalid_snapshot_error": invalid_error,
        "atlas_all_exact": bool(atlas["all_exact"]),
        "best_gate": "MBP4-NL7" if gates["gates"]["MBP4-NL7"]["state"] == "PASS" else "MBP4-NL6",
    }
    result["pass"] = all((result["replay_exact_delivered"], result["dense_lazy_exact"],
                          result["observe_passive"], result["invalid_snapshot_rejected"],
                          result["atlas_all_exact"]))
    write_json(CONT / "TELEMETRY" / "VALIDATION_RESULTS.json", result)
    if not result["pass"]:
        raise SystemExit(json.dumps(result, sort_keys=True))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
