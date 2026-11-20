#!/usr/bin/env python3
"""NRD04 stages A/B plus frozen hierarchical halves on the closed RAW difference set."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ENGINEERING = ROOT.parent
BUNDLED = ROOT / "DEPENDENCIES"
ING02_RUNNERS = BUNDLED / "INGENIERIA_02_RUNNERS" if (BUNDLED / "INGENIERIA_02_RUNNERS").is_dir() else ENGINEERING / "INGENIERIA_02" / "RUNNERS"
if BUNDLED.is_dir():
    os.environ.setdefault("DEE_V27_TESTS_ROOT", str(BUNDLED))
NRD01 = ROOT / "INPUTS" / "NRD01_CHECKPOINTS.npz" if (ROOT / "INPUTS" / "NRD01_CHECKPOINTS.npz").is_file() else ENGINEERING / "NATIVE_REACHABILITY_DEE_V27" / "TELEMETRY" / "NRD01_CHECKPOINTS.npz"
NRD03 = ROOT / "INPUTS" / "NRD03_FACTORIAL_TRAJECTORIES.npz" if (ROOT / "INPUTS" / "NRD03_FACTORIAL_TRAJECTORIES.npz").is_file() else ENGINEERING / "INGENIERIA_05_CONTINUACION_CLOCK_RESIDUE" / "TELEMETRY" / "NRD03_FACTORIAL_TRAJECTORIES.npz"
sys.path.insert(0, str(ING02_RUNNERS))

from ing02_common import NativeWorld, fields, load_kernel, pack, seal, write_json  # noqa: E402

HORIZONS = (32, 64)
PULSE_Q = (11, 11, 8)
PULSE_RAW = pack(8000, 0, (0, 0, 1), 1)


def sha_array(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def make_state(base, target_raw, positions, subset):
    raw = base[0].copy()
    for index in subset:
        q = positions[index]
        raw[q] = target_raw[q]
    return raw, base[1].copy()


def run(kernel, state, challenged):
    world = NativeWorld(kernel, state[0], state[1])
    if challenged:
        world.inject(PULSE_Q, PULSE_RAW, 0)
    out = {0: (world.raw_a.copy(), world.clock_a.copy())}
    for tick in range(1, 65):
        world.tick()
        if tick in HORIZONS:
            out[tick] = (world.raw_a.copy(), world.clock_a.copy())
    return out


def response(c3, c0):
    return np.bitwise_xor(c3[0], c0[0]), np.bitwise_xor(c3[1], c0[1])


def compare(left, right):
    raw_diff = left[0] != right[0]
    clock_diff = left[1] != right[1]
    lf, rf = fields(left[0]), fields(right[0])
    return {
        "equal": bool(not np.any(raw_diff) and not np.any(clock_diff)),
        "raw_diff_positions": int(np.count_nonzero(raw_diff)),
        "clock_diff_positions": int(np.count_nonzero(clock_diff)),
        "raw_diff_mask_sha256": sha_array(raw_diff),
        "clock_diff_mask_sha256": sha_array(clock_diff),
        "field_diff_positions": {key: int(np.count_nonzero(lf[key] != rf[key])) for key in lf},
    }


def exact_at_all(candidate, reference):
    return all(compare(candidate[h], reference[h])["equal"] for h in HORIZONS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    kernel, runtime = load_kernel(args.threads)
    nrd01 = np.load(NRD01)
    nrd03 = np.load(NRD03)
    base = (nrd01["H0_t4_raw_a"], nrd01["H0_t4_clock_a"])
    telemetry, cases = {}, []

    for history in ("H1", "H2"):
        target_raw = nrd01[f"{history}_t4_raw_a"]
        positions = [tuple(int(v) for v in q) for q in np.argwhere(target_raw != base[0])]
        size = len(positions)
        full_key = tuple(range(size))
        half_a = tuple(range((size + 1) // 2))
        half_b = tuple(range((size + 1) // 2, size))
        subsets = {tuple(), full_key, half_a, half_b}
        subsets.update((i,) for i in range(size))
        subsets.update(tuple(j for j in range(size) if j != i) for i in range(size))

        states = {subset: make_state(base, target_raw, positions, subset) for subset in sorted(subsets, key=lambda s: (len(s), s))}
        expected_raw = nrd03[f"{history}_RAW_ONLY_C0_NONE_h0_raw_a"]
        expected_clock = nrd03[f"{history}_RAW_ONLY_C0_NONE_h0_clock_a"]
        if not (np.array_equal(states[full_key][0], expected_raw) and np.array_equal(states[full_key][1], expected_clock)):
            raise RuntimeError(f"{history} FULL_RAW does not reproduce NRD03 RAW_ONLY")

        trajectories = {}
        responses = {}
        for subset, state in states.items():
            c0 = run(kernel, state, False)
            c3 = run(kernel, state, True)
            trajectories[(subset, "C0")] = c0
            trajectories[(subset, "C3")] = c3
            responses[subset] = {h: response(c3[h], c0[h]) for h in HORIZONS}
            label = "_".join(map(str, subset)) if subset else "EMPTY"
            for h in HORIZONS:
                telemetry[f"{history}_S_{label}_response_h{h}_raw_xor"] = responses[subset][h][0]
                telemetry[f"{history}_S_{label}_response_h{h}_clock_xor"] = responses[subset][h][1]

        base_response, full_response = responses[tuple()], responses[full_key]
        if exact_at_all(base_response, full_response):
            raise RuntimeError(f"{history} BASE and FULL_RAW response fingerprints are identical")

        individual = []
        for i, q in enumerate(positions):
            singleton = (i,)
            ablated = tuple(j for j in range(size) if j != i)
            transplant_equals_full = exact_at_all(responses[singleton], full_response)
            transplant_equals_base = exact_at_all(responses[singleton], base_response)
            ablate_equals_full = exact_at_all(responses[ablated], full_response)
            ablate_equals_base = exact_at_all(responses[ablated], base_response)
            if ablate_equals_base:
                necessity = "NECESSARY_STRONG"
            elif not ablate_equals_full:
                necessity = "NECESSARY_PARTIAL"
            elif not transplant_equals_base:
                necessity = "REDUNDANT_OR_CONTEXTUAL"
            else:
                necessity = "NO_DETECTED_EFFECT"
            individual.append({
                "index": i,
                "position": list(q),
                "base_raw": int(base[0][q]),
                "history_raw": int(target_raw[q]),
                "necessity_class": necessity,
                "singleton_exact_full": transplant_equals_full,
                "singleton_exact_base": transplant_equals_base,
                "ablate_exact_full": ablate_equals_full,
                "ablate_exact_base": ablate_equals_base,
                "singleton_distance_to_full": {str(h): compare(responses[singleton][h], full_response[h]) for h in HORIZONS},
                "singleton_distance_to_base": {str(h): compare(responses[singleton][h], base_response[h]) for h in HORIZONS},
                "ablate_distance_to_full": {str(h): compare(responses[ablated][h], full_response[h]) for h in HORIZONS},
                "ablate_distance_to_base": {str(h): compare(responses[ablated][h], base_response[h]) for h in HORIZONS},
            })

        hierarchy = []
        for name, subset, removed in (
            ("HALF_A", half_a, half_b),
            ("HALF_B", half_b, half_a),
        ):
            hierarchy.append({
                "name": name,
                "indices": list(subset),
                "transplant_exact_full": exact_at_all(responses[subset], full_response),
                "transplant_exact_base": exact_at_all(responses[subset], base_response),
                "ablate_indices": list(removed),
                "ablate_exact_full": exact_at_all(responses[removed], full_response),
                "ablate_exact_base": exact_at_all(responses[removed], base_response),
                "transplant_distance_to_full": {str(h): compare(responses[subset][h], full_response[h]) for h in HORIZONS},
                "ablate_distance_to_full": {str(h): compare(responses[removed][h], full_response[h]) for h in HORIZONS},
            })

        singleton_sufficient = [row["index"] for row in individual if row["singleton_exact_full"]]
        exact_half = [row["name"] for row in hierarchy if row["transplant_exact_full"]]
        cases.append({
            "history": history,
            "R_size": size,
            "R_positions": [list(q) for q in positions],
            "full_raw_reproduces_nrd03": True,
            "individual_tests": individual,
            "hierarchical_halves": hierarchy,
            "adjudication": {
                "singleton_sufficient_indices": singleton_sufficient,
                "exact_sufficient_halves": exact_half,
                "individual_strong_necessary_indices": [row["index"] for row in individual if row["necessity_class"] == "NECESSARY_STRONG"],
                "individual_partial_necessary_indices": [row["index"] for row in individual if row["necessity_class"] == "NECESSARY_PARTIAL"],
                "exhaustive_search_justified": not singleton_sufficient and not exact_half,
            },
        })

    np.savez_compressed(ROOT / "TELEMETRY" / "NRD04_STAGE_AB_RESPONSES.npz", **telemetry)
    exhaustive = any(case["adjudication"]["exhaustive_search_justified"] for case in cases)
    result = seal({
        "experiment_id": "NRD04_RAW_CAUSAL_MINIMUM_STAGE_AB",
        "status": "EXHAUSTIVE_SUBSET_SEARCH_JUSTIFIED" if exhaustive else "SMALL_SUPPORT_ISOLATED",
        "runtime": runtime,
        "checkpoint": 4,
        "challenges": ["C0_NONE", "C3_BLIND_PULSE"],
        "horizons": list(HORIZONS),
        "cases": cases,
        "next_gate": "Run closed exhaustive subset enumeration only for unresolved histories." if exhaustive else "Freeze the isolated candidate and characterize values/positions.",
        "telemetry": "TELEMETRY/NRD04_STAGE_AB_RESPONSES.npz"
    })
    out = ROOT / "RESULTS" / "NRD04_STAGE_AB.json"
    write_json(out, result)
    print(json.dumps({"result": str(out), "status": result["status"], "cases": [{"history": c["history"], **c["adjudication"]} for c in cases]}, indent=2))


if __name__ == "__main__":
    main()
