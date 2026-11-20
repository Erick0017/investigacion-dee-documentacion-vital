from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def state_equal(left: dict[str, Any], right: dict[str, Any]) -> dict[str, bool]:
    return {
        "tick_equal": left["tick"] == right["tick"],
        "raw_length_equal": left["raw"]["length"] == right["raw"]["length"],
        "raw_sha256_equal": left["raw"]["sha256"] == right["raw"]["sha256"],
        "clock_length_equal": left["clock"]["length"] == right["clock"]["length"],
        "clock_sha256_equal": left["clock"]["sha256"] == right["clock"]["sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v22", type=Path, required=True)
    parser.add_argument("--v30", type=Path, required=True)
    parser.add_argument("--wheel22", type=Path, required=True)
    parser.add_argument("--wheel30", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    v22, v30 = load(args.v22), load(args.v30)
    channel = state_equal(
        v22["cases"]["legacy_channel_protocol"],
        v30["cases"]["legacy_channel_protocol"],
    )
    snapshot_start = state_equal(
        v22["cases"]["legacy_snapshot_seed"]["start"],
        v30["cases"]["legacy_snapshot_seed"]["start"],
    )
    snapshot_end = state_equal(
        v22["cases"]["legacy_snapshot_seed"]["end"],
        v30["cases"]["legacy_snapshot_seed"]["end"],
    )
    checks = {
        "versions_are_2_2_0_and_3_0_0": (
            v22["runtime_version"] == "2.2.0" and v30["runtime_version"] == "3.0.0"
        ),
        "kernel_constants_equal": (
            v22["kernel_modulus"] == v30["kernel_modulus"]
            and v22["reducer_cap"] == v30["reducer_cap"]
        ),
        "same_snapshot_bytes_loaded": (
            v22["cases"]["legacy_snapshot_seed"]["snapshot_sha256"]
            == v30["cases"]["legacy_snapshot_seed"]["snapshot_sha256"]
        ),
        "channel_protocol_raw_clock_exact": all(channel.values()),
        "snapshot_start_raw_clock_exact": all(snapshot_start.values()),
        "snapshot_after_32_ticks_raw_clock_exact": all(snapshot_end.values()),
    }
    report = {
        "schema": "dee_thinking.compatibility_comparison.v1",
        "scope": (
            "Bounded 2.2.0-to-3.0.0 behavioral comparison: one inherited channel "
            "protocol and one identical legacy snapshot seed, Lazy backend, one thread."
        ),
        "v22_result": str(args.v22.resolve()),
        "v30_result": str(args.v30.resolve()),
        "versions": {"v22": v22["runtime_version"], "v30": v30["runtime_version"]},
        "wheel_provenance": {
            "v22": {
                "path": str(args.wheel22.resolve()),
                "sha256": sha256(args.wheel22),
            },
            "v30": {
                "path": str(args.wheel30.resolve()),
                "sha256": sha256(args.wheel30),
            },
        },
        "checks": checks,
        "details": {
            "legacy_channel_protocol": channel,
            "legacy_snapshot_seed_start": snapshot_start,
            "legacy_snapshot_seed_after_32_ticks": snapshot_end,
        },
        "all_checks_passed": all(checks.values()),
        "limitations": [
            "This is a bounded regression, not a universal equivalence proof.",
            "The comparison does not exercise new 3.0-only basal APIs.",
            "Snapshot container bytes after execution are not compared because version metadata may differ; full RAW and clock uint64 arrays are compared by length and SHA-256.",
        ],
    }
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"all_checks_passed": report["all_checks_passed"]}))
    if not report["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
