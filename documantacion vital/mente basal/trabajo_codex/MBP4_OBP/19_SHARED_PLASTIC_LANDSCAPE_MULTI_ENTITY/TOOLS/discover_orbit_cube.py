from __future__ import annotations

import json
from pathlib import Path

import dee_thinking as dee


OUT = Path(__file__).resolve().parents[1] / "DISCOVERY" / "orbit_cube_scan.json"
N = 23
CUBE = tuple((10 + x, 10 + y, 10 + z) for x in (0, 1) for y in (0, 1) for z in (0, 1))


def index(q: tuple[int, int, int]) -> int:
    return (q[0] * N + q[1]) * N + q[2]


def record(raw: int) -> dict[str, object] | None:
    if not raw:
        return None
    r = dee.decode_record(int(raw))
    return {
        "state": int(r.state),
        "s_reg": int(r.s_reg),
        "direction": [int(r.dx), int(r.dy), int(r.dz)],
        "semantic": int(r.semantic),
    }


def run(axis: int, transverse_a: int, transverse_b: int) -> dict[str, object]:
    raw = [0] * (N ** 3)
    clocks = [0] * (N ** 3)
    for i, q in enumerate(CUBE):
        raw[index(q)] = int(dee.pack_record(1, 20 + i, 0, 0, 0, 1))
        clocks[index(q)] = 1000 + i
    direction = [0, 0, 0]
    direction[axis] = 1
    start = [0, 0, 0]
    start[axis] = 0
    others = [i for i in range(3) if i != axis]
    start[others[0]] = transverse_a
    start[others[1]] = transverse_b
    q0 = tuple(start)
    raw[index(q0)] = int(dee.pack_record(7, 500, *direction, 1))
    clocks[index(q0)] = 777
    runtime = dee.Runtime.import_research_state(N, 0, raw, clocks)
    runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    runtime.advance(4 * N)
    samples: list[dict[str, object]] = []
    current = runtime.raw_copy()
    orbit = []
    for i, value in enumerate(current):
        if value:
            r = dee.decode_record(int(value))
            if int(r.s_reg) >= 450:
                orbit.append({
                    "site": [i // (N * N), (i // N) % N, i % N],
                    "record": record(int(value)),
                })
    samples.append({"tick": 4 * N, "orbit_candidates": orbit})
    final_raw = runtime.raw_copy()
    cube_final = [record(int(final_raw[index(q)])) for q in CUBE]
    return {
        "axis": axis,
        "transverse": [transverse_a, transverse_b],
        "initial_cube_s_reg": list(range(20, 28)),
        "final_cube": cube_final,
        "cube_intact": all(x is not None and int(x["state"]) == 1 for x in cube_final),
        "cube_changed": [None if x is None else int(x["s_reg"]) - (20 + i) for i, x in enumerate(cube_final)],
        "occupied_final": int(runtime.metrics().occupied),
        "samples": samples,
    }


def main() -> None:
    rows = []
    for axis in range(3):
        for a in range(8, 14):
            for b in range(8, 14):
                rows.append(run(axis, a, b))
    payload = {
        "schema": "mbp4.sp.discovery.orbit-cube.v1",
        "kernel": "DEE v27",
        "cases": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    candidates = [r for r in rows if r["cube_intact"] and any((x or 0) != 0 for x in r["cube_changed"])]
    persistent = [r for r in candidates if bool(r["samples"][-1]["orbit_candidates"])]
    print(json.dumps({"cases": len(rows), "changed_intact": len(candidates), "persistent_candidates": len(persistent), "examples": persistent[:8]}, indent=2))


if __name__ == "__main__":
    main()
