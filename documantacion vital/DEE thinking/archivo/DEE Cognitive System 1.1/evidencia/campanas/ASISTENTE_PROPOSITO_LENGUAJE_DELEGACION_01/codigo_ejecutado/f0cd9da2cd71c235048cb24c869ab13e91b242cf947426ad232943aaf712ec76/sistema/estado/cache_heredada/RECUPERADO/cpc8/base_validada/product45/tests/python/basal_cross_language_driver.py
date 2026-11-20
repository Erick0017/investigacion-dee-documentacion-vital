from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import dee_thinking as dt


def _same(actual: dt.BasalWorld, expected: dt.BasalWorld) -> None:
    assert actual.runtime.dimension == expected.runtime.dimension
    assert actual.runtime.current_tick == expected.runtime.current_tick
    assert actual.runtime.raw_copy() == expected.runtime.raw_copy()
    assert actual.runtime.clock_copy() == expected.runtime.clock_copy()
    assert actual.t0_tick == expected.t0_tick
    assert actual.observe().delta == expected.observe().delta
    assert actual.observe().axis_projection == expected.observe().axis_projection


def _create(seed: Path) -> dt.BasalWorld:
    config = dt.BasalConfig.relational_reference(str(seed))
    config.history = dt.BasalHistory.AB
    config.execution = dt.TickOptions(dt.Backend.LAZY, 1)
    world = dt.BasalWorld.create(config)
    world.advance(1)
    assert world.observe().delta == 1
    return world


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.returncode:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        raise RuntimeError(
            f"bridge command failed with exit code {completed.returncode}: {command!r}"
        )


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: basal_cross_language_driver.py CPP_BRIDGE SEED WORK_DIRECTORY"
        )
    bridge = Path(sys.argv[1]).resolve()
    seed = Path(sys.argv[2]).resolve()
    work = Path(sys.argv[3]).resolve()
    if not bridge.is_file() or not seed.is_file():
        raise SystemExit("bridge executable and seed must be regular files")
    work.mkdir(parents=True, exist_ok=True)

    # C++ writes both boundaries; Python resumes the earlier one and compares
    # its continuation with the later C++ boundary.
    cpp_checkpoint = work / "cpp_to_python_t33.deetsnap"
    cpp_future = work / "cpp_to_python_t41.deetsnap"
    _run([str(bridge), "write", str(seed), str(cpp_checkpoint), str(cpp_future)])
    cpp_resumed = dt.BasalWorld.load_snapshot(str(cpp_checkpoint))
    cpp_expected = dt.BasalWorld.load_snapshot(str(cpp_future))
    cpp_resumed.advance(cpp_expected.runtime.current_tick - cpp_resumed.runtime.current_tick)
    _same(cpp_resumed, cpp_expected)
    print("cpp_to_python raw_clock_observation_exact=true")

    # Python writes the same public snapshot schema; the standalone C++
    # consumer resumes it without Python state or sidecar metadata.
    py_checkpoint = work / "python_to_cpp_t33.deetsnap"
    py_future = work / "python_to_cpp_t41.deetsnap"
    py_world = _create(seed)
    py_world.save_snapshot(str(py_checkpoint))
    py_world.advance(8)
    py_world.save_snapshot(str(py_future))
    _run([str(bridge), "check", str(py_checkpoint), str(py_future)])
    print("python_to_cpp raw_clock_observation_exact=true")


if __name__ == "__main__":
    main()
