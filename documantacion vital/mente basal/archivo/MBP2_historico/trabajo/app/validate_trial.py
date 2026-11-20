"""Targeted validations required before the two-hour MBP2 campaign.

This module never edits the sealed A/B/C trial lineages.  Replay and
restore/continue outputs are written below validation/, and writer exclusion is
tested on a fresh disposable (but preserved) validation lineage.
"""

from __future__ import annotations

from array import array
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import mbp2


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TRIAL = ROOT / "test_campaign"
OUTPUT = ROOT / "validation" / "TRIAL_TARGETED_VALIDATION.json"


def snapshot_digest(path: Path) -> dict[str, Any]:
    runtime = mbp2.dee.Runtime.load_snapshot(str(path))

    def digest(values: Any) -> str:
        packed = array("Q", values)
        return hashlib.sha256(packed.tobytes()).hexdigest()

    raw_sha = digest(runtime.raw_copy())
    clock_sha = digest(runtime.clock_copy())
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "tick": int(runtime.current_tick),
        "raw_sha256_uint64_le": raw_sha,
        "clock_sha256_uint64_le": clock_sha,
        "receipt_count": len(runtime.receipts),
    }


def only(pattern: str, base: Path) -> Path:
    matches = list(base.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {pattern!r} below {base}, got {len(matches)}")
    return matches[0]


def replay_validation() -> dict[str, Any]:
    world = TRIAL / "worlds" / "A"
    start = world / "world" / "checkpoints" / "X0_MBP2_A.deetsnap"
    segment = only("segment_000_t0_t*.jsonl", world / "history" / "segments")
    expected = only("*collect_FINAL*.deetsnap", world / "world" / "checkpoints")
    output = ROOT / "validation" / "trial_replay_A_t608.deetsnap"
    output.unlink(missing_ok=True)
    result = mbp2.base.replay(world, start, segment, 608, output, None)
    got = snapshot_digest(output)
    wanted = snapshot_digest(expected)
    exact = (
        got["tick"] == wanted["tick"]
        and got["raw_sha256_uint64_le"] == wanted["raw_sha256_uint64_le"]
        and got["clock_sha256_uint64_le"] == wanted["clock_sha256_uint64_le"]
        and got["receipt_count"] == wanted["receipt_count"]
    )
    return {"operation": result, "replayed": got, "expected": wanted, "exact": exact}


def restore_continue_validation() -> dict[str, Any]:
    world = TRIAL / "worlds" / "B"
    start = only("tick_000000000144_common_tick_144_*.deetsnap",
                 world / "world" / "checkpoints")
    expected = only("*collect_FINAL*.deetsnap", world / "world" / "checkpoints")
    output = ROOT / "validation" / "trial_restore_continue_B_t608.deetsnap"
    output.unlink(missing_ok=True)
    runtime = mbp2.dee.Runtime.load_snapshot(str(start))
    runtime.resume()
    runtime.run_until(608)
    runtime.save_snapshot(str(output))
    del runtime
    got = snapshot_digest(output)
    wanted = snapshot_digest(expected)
    exact = (
        got["tick"] == wanted["tick"]
        and got["raw_sha256_uint64_le"] == wanted["raw_sha256_uint64_le"]
        and got["clock_sha256_uint64_le"] == wanted["clock_sha256_uint64_le"]
        and got["receipt_count"] == wanted["receipt_count"]
    )
    return {"start": str(start.relative_to(ROOT)).replace("\\", "/"),
            "continued": got, "expected": wanted, "exact": exact}


def wait_status(world: Path, wanted: set[str], timeout: float = 30.0) -> dict[str, Any]:
    status_path = world / "world" / "status.json"
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        if status_path.exists():
            try:
                last = json.loads(status_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                last = {}
            if str(last.get("state")) in wanted:
                return last
        time.sleep(0.1)
    raise RuntimeError(f"world did not reach {sorted(wanted)}; last={last}")


def writer_exclusion_validation() -> dict[str, Any]:
    # v1 and v2 are retained as evidence of two instrumental path/key mistakes.
    # v3 is a fresh lineage; nothing is erased or relabelled as a continuation.
    world = ROOT / "validation" / "writer_exclusion_world_v3"
    if world.exists():
        raise RuntimeError(f"refusing to reuse writer-exclusion lineage: {world}")
    cfg_path = ROOT / "validation" / "writer_exclusion_config.json"
    cfg = dict(mbp2.default_config(), campaign_id="MBP2-VALIDATE-WRITER",
               world_id="MBP2-VALIDATE-WRITER-A", condition="A",
               start_paused=True, max_autonomous_hours=0.05)
    mbp2.base.atomic_json(cfg_path, cfg)
    mbp2.initialize(world, cfg_path)
    first_stdout = (ROOT / "validation" / "writer_first.stdout.log").open("w", encoding="utf-8")
    first_stderr = (ROOT / "validation" / "writer_first.stderr.log").open("w", encoding="utf-8")
    first = subprocess.Popen(
        [sys.executable, str(ROOT / "app" / "mbp2.py"), "worker", "--root", str(world)],
        cwd=str(ROOT), stdout=first_stdout, stderr=first_stderr, text=True)
    try:
        running = wait_status(world, {"RUNNING", "PAUSED"})
        second = subprocess.run(
            [sys.executable, str(ROOT / "app" / "mbp2.py"), "worker", "--root", str(world)],
            cwd=str(ROOT), capture_output=True, text=True, timeout=20.0)
        rejected = (second.returncode != 0 and
                    "another writer owns this lineage" in second.stderr)
        stop = mbp2.base.submit_command(
            world, "collect_stop", {"request_id": "VALIDATE_WRITER_EXCLUSION"}, 60.0)
        first.wait(timeout=30.0)
        terminal = wait_status(world, {"STOPPED_SAFE"})
        with mbp2.base.WriterLock(mbp2.base.root_paths(world)["lock"]):
            lock_free_after = True
    finally:
        if first.poll() is None:
            first.terminate()
            first.wait(timeout=10.0)
        first_stdout.close()
        first_stderr.close()
    return {
        "first_pid": first.pid,
        "first_state_when_contested": running.get("state"),
        "second_returncode": second.returncode,
        "second_stdout": second.stdout,
        "second_stderr": second.stderr,
        "second_writer_rejected": rejected,
        "collect_stop_ok": bool(stop.get("ok")),
        "terminal_state": terminal.get("state"),
        "first_returncode": first.returncode,
        "writer_lock_free_after": lock_free_after,
    }


def main() -> int:
    mbp2.install_hooks()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        print(OUTPUT.read_text(encoding="utf-8"))
        return 0
    result: dict[str, Any] = {
        "schema": "mbp2.trial-targeted-validation.v1",
        "created_utc": mbp2.base.iso_utc(),
        "sealed_trial_unchanged": True,
        "replay": replay_validation(),
        "restore_continue": restore_continue_validation(),
        "writer_exclusion": writer_exclusion_validation(),
    }
    result["checks"] = {
        "replay_exact": result["replay"]["exact"],
        "restore_continue_exact": result["restore_continue"]["exact"],
        "second_writer_rejected": result["writer_exclusion"]["second_writer_rejected"],
        "test_world_stopped_safe": result["writer_exclusion"]["terminal_state"] == "STOPPED_SAFE",
        "writer_lock_free_after": result["writer_exclusion"]["writer_lock_free_after"],
    }
    result["all_passed"] = all(result["checks"].values())
    mbp2.base.atomic_json(OUTPUT, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
