#!/usr/bin/env python3
"""Generate immutable differential fixtures with the official v27 WHL.

This is a development/validation tool only.  The native product never imports
Python or the WHL.  Each fixture contains its initial and final four-buffer
state so the C++ test can compare complete RAW and clock arrays bit-for-bit.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import struct
import sys

import numpy as np


WHEEL = Path(r"D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\dist\dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl")
PACKAGE = Path(r"D:\Descargas\ANACONDA MINICONDA\Lib\site-packages\dee_universe_v27\__init__.py")
BINARY = Path(r"D:\Descargas\ANACONDA MINICONDA\Lib\site-packages\dee_universe_v27\dee_kernel_v27.cp313-win_amd64.pyd")
EXPECTED = {
    "wheel_sha256": "69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939",
    "package_sha256": "7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4",
    "binary_sha256": "0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff",
}
MAGIC = b"DTRV2701"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pack(state: int, sreg: int, direction=(0, 0, 0), semantic: int = 1) -> np.uint64:
    value = ((state & 0xFFFFFFFF) | ((sreg & 0xFFFF) << 32)
             | ((direction[0] & 0xF) << 48) | ((direction[1] & 0xF) << 52)
             | ((direction[2] & 0xF) << 56) | ((semantic & 0xF) << 60))
    return np.uint64(value)


def put(raw, clock, q, state, sreg, direction=(0, 0, 0), semantic=1, phase=0):
    raw[q] = pack(state, sreg, direction, semantic)
    clock[q] = np.uint64(phase)


def empty(n: int):
    return np.zeros((n, n, n), dtype=np.uint64), np.zeros((n, n, n), dtype=np.uint64)


def cases():
    result = []

    raw, clock = empty(5)
    result.append(("empty_three_ticks", raw, clock, 3, "empty lattice and uniform clock progression"))

    raw, clock = empty(7)
    put(raw, clock, (0, 3, 3), 1, 2, (-1, 0, 0), 1, 9)
    result.append(("transport_toroidal_wrap", raw, clock, 3, "directional transport across x wrap"))

    raw, clock = empty(7)
    put(raw, clock, (2, 3, 3), 0, 12, (1, 0, 0), 1, 17)
    result.append(("state_zero_raw_nonzero", raw, clock, 2, "RAW-present record with state zero"))

    raw, clock = empty(7)
    put(raw, clock, (3, 3, 3), 77, 5, (1, -1, 0), 4, (1 << 64) - 2)
    result.append(("semantic4_modular_clock", raw, clock, 3, "observer semantic and uint64 clock wrap"))

    raw, clock = empty(7)
    put(raw, clock, (2, 3, 3), 77, 5, (1, 0, 0), 1, 4)
    put(raw, clock, (3, 3, 3), 88, 3, (0, 0, 0), 1, 11)
    result.append(("occupied_destination", raw, clock, 1, "occupied versus empty destination branch"))

    raw, clock = empty(9)
    target = (4, 4, 4)
    corners = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    for j, d in enumerate(corners):
        source = tuple(target[k] - d[k] for k in range(3))
        put(raw, clock, source, 100 + j, 10, d, 1, j)
    result.append(("simultaneous_xnor_eight", raw, clock, 1, "eight simultaneous corner proposals"))

    raw, clock = empty(9)
    target = (4, 4, 4)
    directions = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1),
                  (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
    for j, d in enumerate(directions):
        source = tuple(target[k] - d[k] for k in range(3))
        put(raw, clock, source, 200 + j, 10, d, 1, 20 + j)
    result.append(("simultaneous_non_xnor", raw, clock, 1, "eight simultaneous non-XNOR proposals"))

    raw, clock = empty(11)
    target = (5, 5, 5)
    for j, (d, load) in enumerate((((1, 0, 0), 7), ((0, 1, 0), 11))):
        source = tuple(target[k] - d[k] for k in range(3))
        put(raw, clock, source, 300 + j, load, d, 1, 0)
    stage_two = (6, 6, 5)
    third_direction = (0, 0, 1)
    third_source = tuple(stage_two[k] - 2 * third_direction[k] for k in range(3))
    put(raw, clock, third_source, 302, 13, third_direction, 1, 0)
    result.append(("staged_directional_composition", raw, clock, 2,
                   "two-proposal reduction followed by a later third proposal"))

    raw, clock = empty(6)
    # A fully non-uniform clock field catches accidental global normalization.
    clock.flat[:] = np.arange(clock.size, dtype=np.uint64) * np.uint64(0x100000001)
    put(raw, clock, (1, 2, 3), 15, 65535, (-8, 7, -1), 1, int(clock[1, 2, 3]))
    put(raw, clock, (4, 5, 0), 9, 19664, (0, -8, 7), 4, int(clock[4, 5, 0]))
    result.append(("nonuniform_clocks_direction_edges", raw, clock, 2, "signed direction boundaries and clocks"))

    raw, clock = empty(7)
    put(raw, clock, (3, 3, 3), 1, 19665, (1, 0, 0), 1, 0)
    put(raw, clock, (4, 3, 3), 2, 1, (-1, 0, 0), 4, 0)
    result.append(("reachable_demux_overflow", raw, clock, 1,
                   "historical overflow attempt; survival guard yields zero overflow"))

    # The historical fixture above is retained byte-for-byte, but its occupied
    # observer neighbour leaves the material cell below the survival branch and
    # therefore records zero overflows.  This six-neighbour preparation reaches
    # the actual prov_total>=UMBRAL_FUSION path and applies one DEMUX delta in
    # the postpass.  It is a backend regression fixture, not a new physical law.
    raw, clock = empty(7)
    center = (3, 3, 3)
    put(raw, clock, center, 1, 19664, (0, 0, 0), 1, 0)
    for offset in ((1, 0, 0), (-1, 0, 0), (0, 1, 0),
                   (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        site = tuple(center[axis] + offset[axis] for axis in range(3))
        put(raw, clock, site, 1, 1, (0, 0, 0), 1, 0)
    result.append(("demux_overflow_six_neighbors", raw, clock, 1,
                   "reachable material overflow with one postpass DEMUX delta"))

    # Two overflow sites in different x slabs select one shared target.  A
    # separate directional support births that target with s_reg=10 during the
    # base pass, so the two atomic DEMUX deltas remain observable as s_reg=12.
    raw, clock = empty(7)
    center_a, center_b, target = (3, 3, 3), (4, 3, 3), (3, 2, 2)
    put(raw, clock, center_a, 1, 19664, (0, 0, 0), 1, 0)
    put(raw, clock, center_b, 1, 19664, (0, 0, 0), 1, 0)
    supports = [
        ((3, 2, 3), 10, (0, 0, -1)),
        ((3, 3, 4), 1, (0, 0, 0)),
        ((3, 4, 3), 1, (0, 0, 0)),
        ((4, 3, 4), 1, (0, 0, 0)),
        ((4, 4, 3), 1, (0, 0, 0)),
    ]
    for site, load, direction in supports:
        put(raw, clock, site, 1, load, direction, 1, 0)
    # For center_a the x=-1 Moore plane precedes target offset (0,-1,-1).
    # Orphans are explicitly skipped by the overflow destination scan.
    for y in (2, 3, 4):
        for z in (2, 3, 4):
            put(raw, clock, (2, y, z), 9, 0, (0, 0, 0), 5, 0)
    result.append(("demux_atomic_shared_target", raw, clock, 1,
                   "two x-slab overflows atomically accumulate on one born target"))

    return result


def write_fixture(path: Path, n: int, ticks: int, arrays):
    total = n ** 3
    with path.open("wb") as stream:
        stream.write(struct.pack("<8sIIQ", MAGIC, n, ticks, total))
        for array in arrays:
            flat = np.asarray(array, dtype="<u8").reshape(-1)
            assert flat.size == total
            stream.write(flat.tobytes(order="C"))


def main() -> int:
    observed = {
        "wheel_sha256": sha256(WHEEL),
        "package_sha256": sha256(PACKAGE),
        "binary_sha256": sha256(BINARY),
    }
    if observed != EXPECTED:
        raise RuntimeError(f"official v27 identity mismatch: {observed}")
    sys.path.insert(0, str(PACKAGE.parent.parent))
    importlib.invalidate_caches()
    package = importlib.import_module("dee_universe_v27")
    kernel = importlib.import_module("dee_universe_v27.dee_kernel_v27")
    if Path(package.__file__).resolve() != PACKAGE.resolve() or Path(kernel.__file__).resolve() != BINARY.resolve():
        raise RuntimeError("unexpected v27 import location")

    output = Path(__file__).resolve().parents[1] / "fixtures" / "whl_v27"
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": "DTRV2701 little-endian: header + initial RAW/clock + expected RAW/clock",
        "oracle": {**observed, "wheel_path": str(WHEEL), "binary_path": str(BINARY)},
        "generator": Path(__file__).name,
        "python": sys.version,
        "numpy": np.__version__,
        "cases": [],
    }
    for name, initial_raw, initial_clock, ticks, purpose in cases():
        n = int(initial_raw.shape[0])
        raw_a = np.ascontiguousarray(initial_raw.copy())
        raw_b = np.ascontiguousarray(initial_raw.copy())
        clock_a = np.ascontiguousarray(initial_clock.copy())
        clock_b = np.ascontiguousarray(initial_clock.copy())
        stats = []
        for _ in range(ticks):
            stats.append({str(k): int(v) for k, v in dict(
                kernel.tick_universo(raw_a, raw_b, clock_a, clock_b, n, 1)).items()})
        if not np.array_equal(raw_a, raw_b) or not np.array_equal(clock_a, clock_b):
            raise RuntimeError(f"WHL copy-back contract failed in {name}")
        fixture = output / f"{name}.dtr"
        write_fixture(fixture, n, ticks, (initial_raw, initial_clock, raw_a, clock_a))
        manifest["cases"].append({
            "name": name, "file": fixture.name, "sha256": sha256(fixture),
            "n": n, "ticks": ticks, "purpose": purpose, "tick_stats": stats,
        })
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"fixtures": len(manifest["cases"]), "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    raise SystemExit(main())
