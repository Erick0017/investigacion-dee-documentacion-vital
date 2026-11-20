#!/usr/bin/env python3
"""PROCESOS 02: passive pre-existing degree and event-aligned consequences.

The runner makes measurements only.  All physical component records exist at t0;
after HOST_STOP the main worlds expose only tick/read/checkpoint/hash operations.
Diagnostic clones are built from copied checkpoints and are kept separate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
KERNEL_FILE = ROOT / "dee_kernel_v27.cp313-win_amd64.pyd"
WHEEL_FILE = ROOT / "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
STATE_MASK = np.uint64((1 << 32) - 1)
SREG_MASK = np.uint64(0xFFFF)
SEM_MASK = np.uint64(0xF)
PATTERN_A = ((-1, 0, 0), (-1, 1, 1), (0, 0, 1), (0, 1, 0))
PATTERN_B = ((0, -1, 0), (0, 0, -1), (1, -1, -1), (1, 0, 0))
OPPORTUNITIES = {"P1": (-13, 13, 0), "P2": (0, 13, 0), "P3": (13, 13, 0)}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def hash_array(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def load_kernel(config):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError(f"DEE v27 requires CPython 3.13; observed {sys.version}")
    if sha256_file(KERNEL_FILE) != config["kernel_sha256"]:
        raise RuntimeError("kernel hash mismatch")
    sys.path.insert(0, str(ROOT))
    importlib.invalidate_caches()
    kernel = importlib.import_module("dee_kernel_v27")
    return kernel, {
        "kernel_sha256": sha256_file(KERNEL_FILE),
        "wheel_sha256": sha256_file(WHEEL_FILE),
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "kernel_path": str(KERNEL_FILE),
    }


def pack(state: int, sreg: int, direction, semantic: int = 1) -> np.uint64:
    return np.uint64(
        (int(state) & 0xFFFFFFFF)
        | ((int(sreg) & 0xFFFF) << 32)
        | ((int(direction[0]) & 0xF) << 48)
        | ((int(direction[1]) & 0xF) << 52)
        | ((int(direction[2]) & 0xF) << 56)
        | ((int(semantic) & 0xF) << 60)
    )


def signed_nibble(raw: np.ndarray, shift: int) -> np.ndarray:
    value = ((np.asarray(raw, dtype=np.uint64) >> np.uint64(shift)) & np.uint64(0xF)).astype(np.int16)
    return np.where(value >= 8, value - 16, value)


def fields(raw: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "state": (raw & STATE_MASK).astype(np.uint32),
        "sreg": ((raw >> np.uint64(32)) & SREG_MASK).astype(np.uint16),
        "dx": signed_nibble(raw, 48),
        "dy": signed_nibble(raw, 52),
        "dz": signed_nibble(raw, 56),
        "semantic": ((raw >> np.uint64(60)) & SEM_MASK).astype(np.uint8),
    }


def transform(vector, permutation, signs):
    return tuple(int(signs[i]) * int(vector[permutation[i]]) for i in range(3))


def inverse_transform(vector, permutation, signs):
    out = [0, 0, 0]
    for i in range(3):
        out[int(permutation[i])] = int(signs[i]) * int(vector[i])
    return tuple(out)


def add(q, d, k, n):
    return tuple((int(q[i]) + int(k) * int(d[i])) % int(n) for i in range(3))


class World:
    def __init__(self, kernel, raw, clock, name, threads=1):
        self.kernel = kernel
        self.n = int(raw.shape[0])
        self.threads = int(threads)
        self.name = name
        self.raw_a = np.ascontiguousarray(raw, dtype=np.uint64).copy()
        self.raw_b = self.raw_a.copy()
        self.clock_a = np.ascontiguousarray(clock, dtype=np.uint64).copy()
        self.clock_b = self.clock_a.copy()
        self.host_stopped = False
        self.post_host_calls = Counter()

    def tick(self):
        if self.host_stopped:
            self.post_host_calls["tick"] += 1
        return dict(self.kernel.tick_universo_lazy(
            self.raw_a, self.raw_b, self.clock_a, self.clock_b, self.n, self.threads
        ))

    def inject(self, q, raw, clock=0):
        if self.host_stopped:
            raise RuntimeError(f"post-HOST physical write prohibited: {self.name}")
        q = tuple(int(x) % self.n for x in q)
        self.raw_a[q] = np.uint64(raw)
        self.raw_b[q] = np.uint64(raw)
        self.clock_a[q] = np.uint64(clock)
        self.clock_b[q] = np.uint64(clock)

    def host_stop(self):
        self.host_stopped = True

    def checkpoint(self):
        if self.host_stopped:
            self.post_host_calls["checkpoint"] += 1
        return self.raw_a.copy(), self.clock_a.copy()

    def read(self):
        if self.host_stopped:
            self.post_host_calls["read"] += 1
        return self.raw_a, self.clock_a


def put(raw, clock, q, state, sreg, direction=(0, 0, 0), semantic=1, phase=0):
    if int(raw[q]):
        raise RuntimeError(f"apparatus overlap at {q}")
    raw[q] = pack(state, sreg, direction, semantic)
    clock[q] = np.uint64(phase)


def construct_temporal(kernel, config, mode, origin):
    n = int(config["world"]["N"])
    permutation, signs = config["configurations"][config["active_configuration"]]
    tf = lambda v: transform(v, permutation, signs)
    c = tuple(origin)
    axis = tf((1, 0, 0))
    a = add(c, tf((-1, 0, 0)), 1, n)
    b = add(c, axis, 1, n)
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    put(raw, clock, a, 1000, 100, phase=260)
    put(raw, clock, b, 2000, 100, phase=260)
    for i, offset in enumerate(PATTERN_A):
        put(raw, clock, add(a, tf(offset), 1, n), 3000 + i, 0, semantic=4, phase=31 + i)
    for i, offset in enumerate(PATTERN_B):
        put(raw, clock, add(b, tf(offset), 1, n), 4000 + i, 0, semantic=4, phase=41 + i)
    schedule = {"AB": ("early", "late"), "BA": ("late", "early")}[mode]
    targets = ((a, tf((0, -1, 0)), tf((0, 0, -1)), 5000), (b, tf((0, 1, 0)), tf((0, 0, 1)), 5001))
    for when, (memory, target_offset, direction, state_base) in zip(schedule, targets):
        target = add(memory, target_offset, 1, n)
        if when == "early":
            put(raw, clock, target, state_base, 0, direction, 1, 17)
        else:
            source = add(target, direction, -1, n)
            put(raw, clock, source, 0, 0, direction, 1, 19)
    reader_source = add(c, tf((0, -2, 0)), 1, n)
    put(raw, clock, reader_source, 6000, 7, tf((0, 1, 0)), 4, 23)
    return raw, clock


def merge(raw, clock, other_raw, other_clock):
    occupied = other_raw != 0
    if np.any((raw != 0) & occupied):
        raise RuntimeError("apparatus overlap")
    raw[occupied] = other_raw[occupied]
    clock[occupied] = other_clock[occupied]


def parent_arrays(kernel, config, history, omit):
    n = int(config["world"]["N"])
    origin = tuple(config["world"]["origin"])
    raw = np.zeros((n, n, n), np.uint64)
    clock = np.zeros_like(raw)
    history_mode = {"H0": None, "HA": "AB", "HB": "BA"}[history]
    if history_mode:
        r, c = construct_temporal(kernel, config, history_mode, origin)
        merge(raw, clock, r, c)
    permutation, signs = config["configurations"][config["active_configuration"]]
    for name, offset in OPPORTUNITIES.items():
        if name == omit:
            continue
        moved = transform(offset, permutation, signs)
        center = tuple((origin[i] + moved[i]) % n for i in range(3))
        r, c = construct_temporal(kernel, config, "AB", center)
        merge(raw, clock, r, c)
    return raw, clock


def component_geometry(config):
    n = int(config["world"]["N"])
    origin = tuple(config["world"]["origin"])
    canonical_center = tuple(config["component"]["canonical_center_A"])
    permutation, signs = config["configurations"][config["active_configuration"]]
    signed_delta = tuple(((canonical_center[i] - origin[i] + n // 2) % n) - n // 2 for i in range(3))
    center_a = tuple((origin[i] + transform(signed_delta, permutation, signs)[i]) % n for i in range(3))
    offsets = []
    for x in (-1, 1, 3):
        for y in (-1, 1):
            for z in (-1, 1):
                offsets.append((x, y, z))
    transformed_offsets = [transform(v, permutation, signs) for v in offsets]
    scaffold = [add(center_a, v, 1, n) for v in transformed_offsets]
    center_b = add(center_a, transform((2, 0, 0), permutation, signs), 1, n)
    return {
        "center_A": center_a,
        "center_B": center_b,
        "scaffold": scaffold,
        "all": scaffold + [center_a, center_b],
    }


def install_component(raw, clock, config):
    geometry = component_geometry(config)
    rng = np.random.default_rng(int(config["component"]["source_seed"]))
    for q in geometry["scaffold"]:
        put(
            raw, clock, q,
            int(rng.integers(1, 2**32)),
            int(rng.integers(1, 19665)),
            (0, 0, 0), 4,
            int(rng.bit_generator.random_raw()),
        )
    return geometry


def world_metrics(world):
    raw, clock = world.read()
    f = fields(raw)
    occupied = raw != 0
    world.post_host_calls["hash"] += 2 if world.host_stopped else 0
    return {
        "occupied": int(np.count_nonzero(occupied)),
        "state_nonzero": int(np.count_nonzero(f["state"])),
        "sreg_nonzero": int(np.count_nonzero(f["sreg"])),
        "direction_nonzero": int(np.count_nonzero((f["dx"] != 0) | (f["dy"] != 0) | (f["dz"] != 0))),
        "semantic_1": int(np.count_nonzero(f["semantic"] == 1)),
        "semantic_4": int(np.count_nonzero(f["semantic"] == 4)),
        "raw_sha256": hash_array(raw),
        "clock_sha256": hash_array(clock),
    }


def component_metrics(world, geometry, baseline_raw):
    raw, clock = world.read()
    idx = tuple(np.asarray(geometry["all"], dtype=np.int64).T)
    scaffold_idx = tuple(np.asarray(geometry["scaffold"], dtype=np.int64).T)
    values = np.ascontiguousarray(raw[idx])
    clocks = np.ascontiguousarray(clock[idx])
    f = fields(values)
    return {
        "raw": values,
        "clock": clocks,
        "changed_from_host_stop": int(np.count_nonzero(values != baseline_raw)),
        "occupied": int(np.count_nonzero(values)),
        "scaffold_occupied": int(np.count_nonzero(raw[scaffold_idx])),
        "centers_occupied": int(raw[geometry["center_A"]] != 0) + int(raw[geometry["center_B"]] != 0),
        "semantic_4": int(np.count_nonzero(f["semantic"] == 4)),
        "direction_nonzero": int(np.count_nonzero((f["dx"] != 0) | (f["dy"] != 0) | (f["dz"] != 0))),
        "raw_sha256": hash_array(values),
        "clock_sha256": hash_array(clocks),
    }


def canonical_raw(raw, config):
    permutation, signs = config["configurations"][config["active_configuration"]]
    if permutation == [0, 1, 2] and signs == [1, 1, 1]:
        return np.ascontiguousarray(raw)
    n = raw.shape[0]
    origin = np.asarray(config["world"]["origin"], dtype=np.int64)
    grid = np.indices(raw.shape, dtype=np.int64).reshape(3, -1).T
    delta = ((grid - origin + n // 2) % n) - n // 2
    moved = np.asarray([transform(tuple(v), permutation, signs) for v in delta], dtype=np.int64)
    target = (origin + moved) % n
    sampled = raw[tuple(target.T)].reshape(raw.shape)
    f = fields(sampled)
    dirs = np.stack((f["dx"], f["dy"], f["dz"]), axis=-1).reshape(-1, 3)
    inv = np.asarray([inverse_transform(tuple(v), permutation, signs) for v in dirs], dtype=np.int16).reshape(raw.shape + (3,))
    out = (
        f["state"].astype(np.uint64)
        | (f["sreg"].astype(np.uint64) << np.uint64(32))
        | ((inv[..., 0].astype(np.uint64) & np.uint64(0xF)) << np.uint64(48))
        | ((inv[..., 1].astype(np.uint64) & np.uint64(0xF)) << np.uint64(52))
        | ((inv[..., 2].astype(np.uint64) & np.uint64(0xF)) << np.uint64(56))
        | (f["semantic"].astype(np.uint64) << np.uint64(60))
    )
    return np.ascontiguousarray(out)


def diagnostic_center_restoration(kernel, snapshot, geometry, threads):
    raw, clock = (snapshot[0].copy(), snapshot[1].copy())
    for q in (geometry["center_A"], geometry["center_B"]):
        raw[q] = np.uint64(0)
        clock[q] = np.uint64(0)
    clone = World(kernel, raw, clock, "DIAGNOSTIC_CENTER_RESTORATION", threads)
    clone.host_stop()
    clone.tick()
    values = [int(clone.raw_a[q]) for q in (geometry["center_A"], geometry["center_B"])]
    decoded = []
    for value in values:
        arr = np.asarray([value], dtype=np.uint64)
        f = fields(arr)
        decoded.append({
            "raw": value,
            "state": int(f["state"][0]),
            "sreg": int(f["sreg"][0]),
            "direction": [int(f["dx"][0]), int(f["dy"][0]), int(f["dz"][0])],
            "semantic": int(f["semantic"][0]),
        })
    return {
        "centers_occupied_after_one_tick": int(sum(v != 0 for v in values)),
        "records": decoded,
        "clone_post_host_calls": dict(clone.post_host_calls),
    }


def run_configuration(name: str):
    config = read_json(CONFIG_PATH)
    config["active_configuration"] = name
    kernel, runtime = load_kernel(config)
    n = int(config["world"]["N"])
    horizon = int(config["world"]["horizon"])
    threads = int(config["world"]["threads"])
    geometry = component_geometry(config)
    pairs = {}
    for branch, (history, omit) in config["branches"].items():
        p_raw, p_clock = parent_arrays(kernel, config, history, omit)
        a_raw, a_clock = p_raw.copy(), p_clock.copy()
        installed = install_component(a_raw, a_clock, config)
        if installed != geometry:
            raise RuntimeError("component geometry instability")
        pairs[branch] = {
            "parent": World(kernel, p_raw, p_clock, f"{name}_{branch}_PARENT", threads),
            "augmented": World(kernel, a_raw, a_clock, f"{name}_{branch}_AUGMENTED", threads),
        }

    host_stop_tick = int(config["world"]["host_stop_tick"])
    for _ in range(host_stop_tick):
        for pair in pairs.values():
            pair["parent"].tick()
            pair["augmented"].tick()
    for pair in pairs.values():
        pair["parent"].host_stop()
        pair["augmented"].host_stop()

    baseline = {}
    for branch, pair in pairs.items():
        p_raw, _ = pair["parent"].read()
        a_raw, _ = pair["augmented"].read()
        mask = a_raw != p_raw
        idx = tuple(np.asarray(geometry["all"], dtype=np.int64).T)
        baseline[branch] = {
            "initial_difference_mask": mask.copy(),
            "component_raw": np.ascontiguousarray(a_raw[idx]).copy(),
        }

    metric_names = [
        "parent_occupied", "augmented_occupied", "raw_difference_total",
        "difference_outside_initial_footprint", "component_difference_vs_parent",
        "component_changed_from_host_stop", "component_occupied", "component_scaffold_occupied",
        "component_centers_occupied", "component_semantic_4", "component_direction_nonzero",
    ]
    telemetry = {branch: {key: [] for key in metric_names} for branch in pairs}
    telemetry["ticks"] = []
    component_vectors = {branch: [] for branch in pairs}
    snapshots = {}
    full_snapshot_ticks = set(config["snapshot_ticks"] if name == "MAIN_S0" else [0, 127, 458, 512])
    transitions = {branch: {"parent_tau50": None, "parent_tau99": None, "augmented_tau50": None, "augmented_tau99": None} for branch in pairs}
    response = {branch: {"component_first_change": None, "external_consequence_first_change": None} for branch in pairs}

    started = time.perf_counter()
    for tick in range(horizon + 1):
        telemetry["ticks"].append(tick)
        for branch, pair in pairs.items():
            parent = pair["parent"]
            augmented = pair["augmented"]
            pm = world_metrics(parent)
            am = world_metrics(augmented)
            p_raw, _ = parent.read()
            a_raw, _ = augmented.read()
            diff = a_raw != p_raw
            initial_mask = baseline[branch]["initial_difference_mask"]
            comp = component_metrics(augmented, geometry, baseline[branch]["component_raw"])
            comp_idx = tuple(np.asarray(geometry["all"], dtype=np.int64).T)
            values = {
                "parent_occupied": pm["occupied"],
                "augmented_occupied": am["occupied"],
                "raw_difference_total": int(np.count_nonzero(diff)),
                "difference_outside_initial_footprint": int(np.count_nonzero(diff & ~initial_mask)),
                "component_difference_vs_parent": int(np.count_nonzero(a_raw[comp_idx] != p_raw[comp_idx])),
                "component_changed_from_host_stop": comp["changed_from_host_stop"],
                "component_occupied": comp["occupied"],
                "component_scaffold_occupied": comp["scaffold_occupied"],
                "component_centers_occupied": comp["centers_occupied"],
                "component_semantic_4": comp["semantic_4"],
                "component_direction_nonzero": comp["direction_nonzero"],
            }
            for key, value in values.items():
                telemetry[branch][key].append(value)
            component_vectors[branch].append(comp["raw"])

            if response[branch]["component_first_change"] is None and tick > 0 and comp["changed_from_host_stop"] > 0:
                response[branch]["component_first_change"] = tick
            if response[branch]["external_consequence_first_change"] is None and tick > 0 and values["difference_outside_initial_footprint"] > 0:
                response[branch]["external_consequence_first_change"] = tick
            for label, key, threshold in (
                ("parent_tau50", "parent_occupied", config["frozen_measurements"]["transition_thresholds"]["tau50_occupied"]),
                ("parent_tau99", "parent_occupied", config["frozen_measurements"]["transition_thresholds"]["tau99_occupied"]),
                ("augmented_tau50", "augmented_occupied", config["frozen_measurements"]["transition_thresholds"]["tau50_occupied"]),
                ("augmented_tau99", "augmented_occupied", config["frozen_measurements"]["transition_thresholds"]["tau99_occupied"]),
            ):
                if transitions[branch][label] is None and values[key] >= int(threshold):
                    transitions[branch][label] = tick

            if tick in full_snapshot_ticks:
                snapshots[f"{branch}_PARENT_t{tick}_raw"] = p_raw.copy()
                snapshots[f"{branch}_PARENT_t{tick}_clock"] = parent.clock_a.copy()
                snapshots[f"{branch}_AUGMENTED_t{tick}_raw"] = a_raw.copy()
                snapshots[f"{branch}_AUGMENTED_t{tick}_clock"] = augmented.clock_a.copy()
                snapshots[f"{branch}_diffmask_t{tick}"] = np.packbits(diff.reshape(-1))
        if tick < horizon:
            for pair in pairs.values():
                pair["parent"].tick()
                pair["augmented"].tick()
    elapsed = time.perf_counter() - started

    for branch in pairs:
        for key in metric_names:
            telemetry[branch][key] = np.asarray(telemetry[branch][key], dtype=np.int64)
        telemetry[branch]["component_raw_vectors"] = np.asarray(component_vectors[branch], dtype=np.uint64)
    telemetry["ticks"] = np.asarray(telemetry["ticks"], dtype=np.int64)

    # Diagnostic clones use copied MAIN checkpoints only and never feed the main worlds.
    diagnostics = {}
    if name == "MAIN_S0":
        for branch, ticks in {"HB_OMIT_P2": (121, 127), "HB_FULL": (450, 458)}.items():
            diagnostics[branch] = {}
            for tick in ticks:
                key = f"{branch}_AUGMENTED_t{tick}"
                snap = (snapshots[key + "_raw"], snapshots[key + "_clock"])
                diagnostics[branch][str(tick)] = diagnostic_center_restoration(kernel, snap, geometry, threads)

    terminal = {}
    for branch, pair in pairs.items():
        p_raw, p_clock = pair["parent"].checkpoint()
        a_raw, a_clock = pair["augmented"].checkpoint()
        terminal[branch] = {
            "parent_raw_sha256": hash_array(p_raw),
            "augmented_raw_sha256": hash_array(a_raw),
            "parent_clock_sha256": hash_array(p_clock),
            "augmented_clock_sha256": hash_array(a_clock),
            "augmented_canonical_raw_sha256": hash_array(canonical_raw(a_raw, config)),
            "post_host_calls": {
                "parent": dict(pair["parent"].post_host_calls),
                "augmented": dict(pair["augmented"].post_host_calls),
            },
        }

    output = {
        "schema": "dee.v27.processes02.passive_degree_measurements.v1",
        "administrative_state": "MEASUREMENT_AVAILABLE",
        "configuration": name,
        "runtime": runtime,
        "elapsed_seconds": elapsed,
        "component": {
            "mechanism": config["component"]["mechanism"],
            "geometry": {k: [list(q) for q in v] if k in {"scaffold", "all"} else list(v) for k, v in geometry.items()},
            "installed_before_host_stop": True,
            "host_stop_tick": host_stop_tick,
        },
        "transitions": transitions,
        "responses": response,
        "initial_difference_footprint": {branch: int(np.count_nonzero(v["initial_difference_mask"])) for branch, v in baseline.items()},
        "terminal": terminal,
        "diagnostic_clones": diagnostics,
        "measurement_definitions": config["frozen_measurements"],
        "main_world_post_host_allowed_calls": ["tick", "read", "checkpoint", "hash", "log", "stop"],
    }
    write_json(ROOT / f"run_{name}.json", output)
    flat_npz = {"ticks": telemetry["ticks"]}
    for branch in pairs:
        for key, array in telemetry[branch].items():
            flat_npz[f"{branch}__{key}"] = array
    flat_npz.update(snapshots)
    np.savez_compressed(ROOT / f"telemetry_{name}.npz", **flat_npz)
    print(json.dumps({
        "configuration": name,
        "elapsed_seconds": elapsed,
        "transitions": transitions,
        "responses": response,
        "initial_difference_footprint": output["initial_difference_footprint"],
    }, indent=2))


def combine():
    configs = ["MAIN_S0", "FRESH_V1", "FRESH_V2"]
    runs = {name: read_json(ROOT / f"run_{name}.json") for name in configs if (ROOT / f"run_{name}.json").exists()}
    base_config = read_json(CONFIG_PATH)
    kernel, _ = load_kernel(base_config)
    diagnostic_covariance = {}
    component_measurements = {}

    def value_runs(values):
        values = [int(x) for x in values]
        runs = []
        start = 0
        for i in range(1, len(values) + 1):
            if i == len(values) or values[i] != values[start]:
                runs.append({"start": start, "end": i - 1, "value": values[start]})
                start = i
        return runs

    for name in runs:
        active = dict(base_config)
        active["active_configuration"] = name
        geometry = component_geometry(active)
        with np.load(ROOT / f"telemetry_{name}.npz", allow_pickle=False) as z:
            diagnostic_covariance[name] = {}
            for label, branch, tick in (
                ("BASELINE", "HB_FULL", 0),
                ("EARLY_STABLE", "HB_OMIT_P2", 127),
                ("LATE_STABLE", "HB_FULL", 458),
            ):
                raw = z[f"{branch}_AUGMENTED_t{tick}_raw"]
                clock = z[f"{branch}_AUGMENTED_t{tick}_clock"]
                diagnostic_covariance[name][label] = diagnostic_center_restoration(
                    kernel, (raw, clock), geometry, int(active["world"]["threads"])
                )
            component_measurements[name] = {}
            for branch in ("H0_FULL", "HA_FULL", "HB_OMIT_P2", "HB_FULL"):
                vectors = z[f"{branch}__component_raw_vectors"]
                changed = np.flatnonzero(np.any(vectors != vectors[0], axis=1))
                first = None if not len(changed) else int(changed[0])
                stable = None
                if first is not None:
                    for tick in range(first, vectors.shape[0]):
                        if np.all(vectors[tick:] == vectors[tick]):
                            stable = tick
                            break
                changed_records = np.flatnonzero(vectors[-1] != vectors[0])
                component_measurements[name][branch] = {
                    "first_change": first,
                    "stable_from": stable,
                    "changed_record_indices": [int(x) for x in changed_records],
                    "terminal_records": [decode_record(int(vectors[-1, x])) for x in changed_records],
                    "center_A_state_runs": value_runs(vectors[:, 12] & np.uint64(0xFFFFFFFF)),
                    "center_B_state_runs": value_runs(vectors[:, 13] & np.uint64(0xFFFFFFFF)),
                }
    canonical = {
        branch: {
            name: runs[name]["terminal"][branch]["augmented_canonical_raw_sha256"]
            for name in runs
        }
        for branch in ("H0_FULL", "HA_FULL", "HB_FULL", "HB_OMIT_P2")
    }
    write_json(ROOT / "results.json", {
        "schema": "dee.v27.processes02.passive_degree_integrated_measurements.v1",
        "administrative_state": "MEASUREMENT_AVAILABLE",
        "configurations": runs,
        "component_measurements": component_measurements,
        "diagnostic_clone_evidence": diagnostic_covariance,
        "canonical_terminal_hashes": canonical,
        "canonical_terminal_hashes_equal_across_spatial_transforms": {
            branch: len(set(by_config.values())) == 1 for branch, by_config in canonical.items()
        },
        "main_detailed_analysis": read_json(ROOT / "analysis_MAIN_S0.json") if (ROOT / "analysis_MAIN_S0.json").exists() else None,
        "observer_measurement_map": {
            "X_FULL": "two center RAW records change; surrounding world remains part of the causal state",
            "configuration": "component occupancy remains 14 and therefore fuses pre/post center-state changes",
            "geometry": "12 scaffold positions and two center positions remain occupied; geometry fuses the measured change",
            "relation": "joint center-restoration response changes across event-aligned checkpoints",
            "phase": "component clock-residual vector remains unchanged at the sampled checkpoints",
            "history": "EARLY and LATE produce different stable center states and different restoration futures",
            "function": "diagnostic center removal yields 2/0/2 restorations for baseline/EARLY/LATE stable organizations",
            "competence": "the shared interface loses restoration in EARLY but retains it in LATE",
            "resource": "the component keeps 14 occupied positions; support count hides the response",
            "reachability": "frozen one-tick diagnostic clones separate the stable organizations",
            "R0": "OUTSIDE_VALIDATED_SCOPE for this apparatus",
            "R1": "first component-state change occurs at tau99-8 in both transition realizations",
            "R2": "task-relative shared-interface restoration distinguishes the resulting organizations",
            "R3": "coarse occupancy does not distinguish the resulting organizations"
        },
        "fresh_semantics": "FRESH_V1/FRESH_V2 are spatial covariance checks, not population samples.",
    })
    arrays = {}
    for name in runs:
        with np.load(ROOT / f"telemetry_{name}.npz", allow_pickle=False) as z:
            for key in z.files:
                arrays[f"{name}__{key}"] = z[key]
    np.savez_compressed(ROOT / "telemetry.npz", **arrays)
    print(json.dumps({"combined": list(runs), "arrays": len(arrays)}, indent=2))


def decode_record(value: int):
    arr = np.asarray([value], dtype=np.uint64)
    f = fields(arr)
    return {
        "raw": int(value),
        "state": int(f["state"][0]),
        "sreg": int(f["sreg"][0]),
        "direction": [int(f["dx"][0]), int(f["dy"][0]), int(f["dz"][0])],
        "semantic": int(f["semantic"][0]),
    }


def analyze_main():
    config = read_json(CONFIG_PATH)
    config["active_configuration"] = "MAIN_S0"
    kernel, _ = load_kernel(config)
    run = read_json(ROOT / "run_MAIN_S0.json")
    geometry = component_geometry(config)
    with np.load(ROOT / "telemetry_MAIN_S0.npz", allow_pickle=False) as z:
        branches = {}
        function_ticks = {
            "HB_OMIT_P2": [96, 112, 121, 127],
            "HB_FULL": [420, 442, 450, 458],
        }
        for branch in config["branches"]:
            vectors = z[f"{branch}__component_raw_vectors"]
            changed_counts = np.count_nonzero(vectors != vectors[0], axis=1)
            changed_ticks = np.flatnonzero(changed_counts)
            first = None if not len(changed_ticks) else int(changed_ticks[0])
            stable = None
            if first is not None:
                for t in range(first, vectors.shape[0]):
                    if np.all(vectors[t:] == vectors[t]):
                        stable = t
                        break
            comparison_tick = stable if stable is not None else vectors.shape[0] - 1
            indices = np.flatnonzero(vectors[comparison_tick] != vectors[0])
            changes = []
            for i in indices:
                role = "scaffold" if int(i) < len(geometry["scaffold"]) else ("center_A" if int(i) == 12 else "center_B")
                changes.append({
                    "index": int(i),
                    "role": role,
                    "coordinate": list(geometry["all"][int(i)]),
                    "host_stop": decode_record(int(vectors[0, i])),
                    "stable": decode_record(int(vectors[comparison_tick, i])),
                })
            transition = run["transitions"][branch]
            function = {}
            for tick in function_ticks.get(branch, []):
                raw = z[f"{branch}_AUGMENTED_t{tick}_raw"]
                clock = z[f"{branch}_AUGMENTED_t{tick}_clock"]
                function[str(tick)] = diagnostic_center_restoration(kernel, (raw, clock), geometry, int(config["world"]["threads"]))
            branches[branch] = {
                "component_first_change": first,
                "component_stable_from": stable,
                "changed_component_records": changes,
                "persistence_through": int(config["world"]["horizon"]) if stable is not None else None,
                "relative_timing": {
                    "minus_parent_tau50": None if first is None or transition["parent_tau50"] is None else first - transition["parent_tau50"],
                    "minus_parent_tau99": None if first is None or transition["parent_tau99"] is None else first - transition["parent_tau99"],
                },
                "instantaneous_observers": {
                    "occupancy_at_host_stop": int(z[f"{branch}__component_occupied"][0]),
                    "occupancy_at_terminal": int(z[f"{branch}__component_occupied"][-1]),
                    "semantic4_at_host_stop": int(z[f"{branch}__component_semantic_4"][0]),
                    "semantic4_at_terminal": int(z[f"{branch}__component_semantic_4"][-1]),
                    "direction_nonzero_at_host_stop": int(z[f"{branch}__component_direction_nonzero"][0]),
                    "direction_nonzero_at_terminal": int(z[f"{branch}__component_direction_nonzero"][-1]),
                },
                "diagnostic_function": function,
            }
    analysis = {
        "schema": "dee.v27.processes02.passive_degree_main_analysis.v1",
        "administrative_state": "MEASUREMENT_AVAILABLE",
        "frozen_component": config["component"],
        "branches": branches,
        "measurement_notes": [
            "Component response is defined from RAW records, not occupancy.",
            "Center-restoration measurements occur only in diagnostic clones copied from frozen checkpoints.",
            "A main-world external-difference onset is not used as a downstream marker because H0 also develops such differences while its component RAW remains unchanged."
        ],
    }
    write_json(ROOT / "analysis_MAIN_S0.json", analysis)
    print(json.dumps({
        branch: {
            "component_first_change": data["component_first_change"],
            "component_stable_from": data["component_stable_from"],
            "relative_timing": data["relative_timing"],
            "changed_records": len(data["changed_component_records"]),
            "diagnostic_function": {t: v["centers_occupied_after_one_tick"] for t, v in data["diagnostic_function"].items()},
        }
        for branch, data in branches.items()
    }, indent=2))


def package_official():
    config = read_json(CONFIG_PATH)
    tests = ROOT.parents[2]
    official_dir = tests / "documantacion vital" / "procesos" / "PROCESOS_02"
    official_name = "PROCESOS_02_DEE_V27_CONTINUIDAD_CAUSAL_POST_TRANSICION_RESULTADOS.zip"
    target = official_dir / official_name
    parent = tests / "documantacion vital" / "procesos" / "PROCESOS_01_DEE_V27_CONTINUIDAD_ENDOGENA_ATLAS_MULTIOBSERVADOR_RESULTADOS.zip"
    if not official_dir.is_dir():
        raise RuntimeError(f"existing official directory not found: {official_dir}")
    if sha256_file(parent) != config["parent_process01_sha256"]:
        raise RuntimeError("Processes 01 parent hash mismatch")
    if not target.is_file():
        raise RuntimeError("existing Processes 02 official ZIP not found")
    if sha256_file(target) != config["prior_process02_sha256"]:
        raise RuntimeError("current Processes 02 archive is not the frozen predecessor")
    siblings = [p.name for p in official_dir.iterdir() if p.is_file()]
    if siblings != [official_name]:
        raise RuntimeError(f"official directory is not clean: {siblings}")

    primary_names = [
        "runner_procesos02.py",
        "config.json",
        "results.json",
        "telemetry.npz",
        "SCIENTIFIC_REPORT.md",
        "dee_kernel_v27.cp313-win_amd64.pyd",
        "dee_kernel_v27.cpp",
        "dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl",
    ]
    primary = [ROOT / name for name in primary_names]
    missing = [p.name for p in primary if not p.is_file()]
    if missing:
        raise RuntimeError(f"package inputs missing: {missing}")
    manifest = {
        "schema": "dee.v27.processes02.flat_manifest.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "archive_name": official_name,
        "parent_process01_sha256": config["parent_process01_sha256"],
        "predecessor_process02_sha256": config["prior_process02_sha256"],
        "kernel_sha256": config["kernel_sha256"],
        "flat_structure": True,
        "files": [
            {"name": p.name, "size": p.stat().st_size, "sha256": sha256_file(p)}
            for p in primary
        ],
    }
    write_json(ROOT / "MANIFEST.json", manifest)
    hash_inputs = primary + [ROOT / "MANIFEST.json"]
    (ROOT / "HASHES.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.name}\n" for p in hash_inputs),
        encoding="utf-8",
    )
    archive_inputs = hash_inputs + [ROOT / "HASHES.sha256"]
    tmp = ROOT / (official_name + ".tmp")
    if tmp.exists():
        tmp.unlink()
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in archive_inputs:
            zf.write(path, path.name)
    with zipfile.ZipFile(tmp, "r") as zf:
        bad = zf.testzip()
        members = zf.infolist()
        roots_flat = all("/" not in item.filename.rstrip("/") for item in members)
    if bad is not None or not roots_flat:
        raise RuntimeError(f"archive integrity problem: bad={bad}, flat={roots_flat}")
    target.unlink()
    tmp.replace(target)
    with zipfile.ZipFile(target, "r") as zf:
        internal = zf.read("HASHES.sha256").decode("utf-8").splitlines()
        hash_errors = []
        for line in internal:
            expected, name = line.split("  ", 1)
            observed = hashlib.sha256(zf.read(name)).hexdigest()
            if observed != expected:
                hash_errors.append(name)
        bad = zf.testzip()
        member_count = len(zf.infolist())
        uncompressed = sum(x.file_size for x in zf.infolist())
    if bad is not None or hash_errors:
        raise RuntimeError(f"final archive verification error: crc={bad}, hashes={hash_errors}")
    print(json.dumps({
        "path": str(target),
        "size": target.stat().st_size,
        "sha256": sha256_file(target),
        "members": member_count,
        "uncompressed_size": uncompressed,
        "crc_error": bad,
        "internal_hash_errors": hash_errors,
        "flat_structure": roots_flat,
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", choices=["MAIN_S0", "FRESH_V1", "FRESH_V2"])
    parser.add_argument("--combine", action="store_true")
    parser.add_argument("--analyze-main", action="store_true")
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()
    if args.combine:
        combine()
    elif args.analyze_main:
        analyze_main()
    elif args.package:
        package_official()
    elif args.configuration:
        run_configuration(args.configuration)
    else:
        parser.error("use --configuration or --combine")


if __name__ == "__main__":
    main()
