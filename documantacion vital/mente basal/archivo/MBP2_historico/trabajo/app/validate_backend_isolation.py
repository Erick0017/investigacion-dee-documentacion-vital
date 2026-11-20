"""Sequential, memory-bounded backend and A/B/C isolation validation."""

from __future__ import annotations

from array import array
import hashlib
import json
from pathlib import Path
from typing import Any

import mbp2


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "validation" / "TRIAL_BACKEND_AND_ISOLATION.json"


def digest(values: Any) -> str:
    return hashlib.sha256(array("Q", values).tobytes()).hexdigest()


def run_backend(backend: Any, name: str) -> dict[str, Any]:
    cfg = dict(mbp2.default_config(), campaign_id="MBP2-BACKEND-VALIDATION",
               world_id=f"MBP2-BACKEND-{name}", condition="B")
    runtime, _, _ = mbp2.build_x0(cfg)
    runtime.execution_options = mbp2.dee.TickOptions(backend, 1)
    runtime.advance(17)
    result = {
        "tick": int(runtime.current_tick),
        "raw_sha256_uint64_le": digest(runtime.raw_copy()),
        "clock_sha256_uint64_le": digest(runtime.clock_copy()),
    }
    return result


def main() -> int:
    mbp2.install_hooks()
    dense = run_backend(mbp2.dee.Backend.DENSE_SEQUENTIAL, "DENSE")
    lazy = run_backend(mbp2.dee.Backend.LAZY, "LAZY")
    instances: dict[str, Any] = {}
    roots: list[str] = []
    pids: list[int] = []
    locks: list[str] = []
    for condition in ("A", "B", "C"):
        world = ROOT / "test_campaign" / "worlds" / condition
        instance = mbp2.base.load_json(world / "world" / "instance.json")
        status = mbp2.base.load_json(world / "world" / "status.json")
        roots.append(str(world.resolve()))
        pids.append(int(status["pid"]))
        locks.append(str((world / "world" / "writer.lock").resolve()))
        instances[condition] = {
            "world_id": instance["world_id"],
            "condition": instance["condition"],
            "root": roots[-1],
            "pid": pids[-1],
            "writer_lock": locks[-1],
        }
    checks = {
        "dense_lazy_raw_exact_t17": dense["raw_sha256_uint64_le"] == lazy["raw_sha256_uint64_le"],
        "dense_lazy_clock_exact_t17": dense["clock_sha256_uint64_le"] == lazy["clock_sha256_uint64_le"],
        "three_distinct_roots": len(set(roots)) == 3,
        "three_distinct_worker_pids": len(set(pids)) == 3,
        "three_distinct_writer_locks": len(set(locks)) == 3,
        "world_ids_exact": [instances[c]["world_id"] for c in ("A", "B", "C")] == [
            "MBP2-A-AISLAMIENTO", "MBP2-B-INTERACTIVO", "MBP2-C-CONTROL"],
    }
    result = {
        "schema": "mbp2.backend-isolation-validation.v1",
        "created_utc": mbp2.base.iso_utc(),
        "dense": dense,
        "lazy": lazy,
        "instances": instances,
        "checks": checks,
        "all_passed": all(checks.values()),
    }
    mbp2.base.atomic_json(OUT, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
