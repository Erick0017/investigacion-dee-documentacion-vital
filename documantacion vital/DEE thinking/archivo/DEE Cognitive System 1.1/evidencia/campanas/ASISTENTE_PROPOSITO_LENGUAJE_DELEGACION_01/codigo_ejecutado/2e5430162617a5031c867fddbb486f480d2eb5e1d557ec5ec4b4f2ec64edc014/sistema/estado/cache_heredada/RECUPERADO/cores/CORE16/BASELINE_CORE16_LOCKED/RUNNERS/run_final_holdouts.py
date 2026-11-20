#!/usr/bin/env python3
"""Execute frozen CORE16 final untouched holdouts and causal canaries."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core16_common import ROOT, audit_kernel, canonical_hash, read_json, sha, update_state, utc, write_json
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import convergent_phase_paths, regenerative_interface_trial
from core10_apparatus import run_learned_policy_transfer
from run_discovery_roots import DIRECTIONS, LAMBDA, add, bell_trial, entropy, sparse_world, unpack
from run_adaptive_children import sequential_order_trial
from run_adaptive_grandchildren import bell_summary, internal_bell_trial, setting_independence_summary


def verify_freeze():
    freeze = read_json(ROOT / "SOURCE_FREEZE.json")
    mismatches = []
    for item in freeze["files"]:
        path = ROOT / item["path"]
        if not path.is_file() or sha(path) != item["sha256"]:
            mismatches.append(item["path"])
    if mismatches:
        raise RuntimeError(f"source freeze mismatch at final execution: {mismatches}")
    manifest = ROOT / "FINAL_HOLDOUTS" / "FINAL_CHALLENGE_MANIFEST.json"
    if not manifest.is_file():
        raise RuntimeError("final challenges do not exist")
    if sha(ROOT / "SOURCE_FREEZE.json") != read_json(manifest)["source_freeze_sha256"]:
        raise RuntimeError("challenge/source-freeze lineage mismatch")


def transform(v, permutation, signs):
    return tuple(signs[i] * v[permutation[i]] for i in range(3))


def h01_fiber(kernel, seeds):
    cases = []
    for index, seed in enumerate(seeds):
        rng = np.random.default_rng(seed); n = (19, 25, 31)[index % 3]; count = int(rng.integers(6, 40))
        raw, _, destinations = sparse_world(rng, n, count)
        expected = len(set(destinations)); world = NativeWorld(kernel, raw); world.tick(); actual = int(np.count_nonzero(world.raw))
        cases.append({"index": index, "n": n, "expected": expected, "actual": actual, "pass": expected == actual})
    canaries = []
    for n in (19, 25, 31):
        c = (n // 2,) * 3; raw = np.zeros((n, n, n), dtype=np.uint64)
        raw[add(c, (1, 0, 0), -1, n)] = pack(1, 31, (1, 0, 0), 1); raw[c] = pack(2, 43, (0, 0, 0), 1)
        naive = 1; world = NativeWorld(kernel, raw); world.tick(); actual = int(np.count_nonzero(world.raw))
        canaries.append({"n": n, "naive": naive, "actual": actual, "scope_break_detected": actual != naive})
    return {"claim_id": "C16C001", "positive_pass": sum(c["pass"] for c in cases), "positive_total": len(cases), "canary_correct": sum(c["scope_break_detected"] for c in canaries), "canary_total": len(canaries), "cases": cases, "canaries": canaries, "status": "PASS" if all(c["pass"] for c in cases) and all(c["scope_break_detected"] for c in canaries) else "FAIL"}


def h02_resurrection(kernel, seeds):
    cases = []
    for index, seed in enumerate(seeds):
        rng = np.random.default_rng(seed); n = (25, 31, 37)[index % 3]
        direction = ((1, 0, 0), (0, -1, 0), (0, 0, 1), (1, 0, -1))[index % 4]
        axis = next(i for i, value in enumerate(direction) if value == 0); origin = [n // 3] * 3
        lanes = []
        for lane in range(4): q = origin.copy(); q[axis] += 3 * lane; lanes.append(tuple(q))
        p = [int(x) for x in rng.choice(np.arange(13, 1500), 4, replace=False)]; order = [1, 2, 3, 0]; qvals = [p[i] for i in order]
        lane = index % 4; counter = int(rng.integers(1, 600)); arms = []
        for assignment in (p, qvals):
            raw = np.zeros((n, n, n), dtype=np.uint64); clock = np.zeros_like(raw)
            for i, (pos, sreg) in enumerate(zip(lanes, assignment, strict=True)):
                raw[pos] = pack(int(rng.integers(1, 2**32)), sreg, direction, 1); clock[pos] = np.uint64(rng.bit_generator.random_raw())
            target = add(lanes[lane], direction, 1, n); reverse = tuple(-x for x in direction); port = add(target, reverse, -1, n)
            raw[port] = pack(int(rng.integers(1, 2**32)), counter, reverse, 1); world = NativeWorld(kernel, raw, clock); world.tick(); rec = unpack(world.raw[target])
            arms.append({"assignment_at_lane": assignment[lane], "observed": rec, "expected": min(assignment[lane] + counter, 19664), "pass": rec is not None and rec["sreg"] == min(assignment[lane] + counter, 19664)})
        cases.append({"index": index, "coarse_equal": sorted(p) == sorted(qvals), "responses_diverge": arms[0]["observed"] != arms[1]["observed"], "arms": arms, "pass": all(a["pass"] for a in arms) and arms[0]["observed"] != arms[1]["observed"]})
    # Canary uses the wrong (sorted-only) prediction: it must fail whenever lane assignments differ.
    canary_correct = sum(c["responses_diverge"] for c in cases)
    return {"claim_id": "C16C002", "positive_pass": sum(c["pass"] for c in cases), "positive_total": len(cases), "canary_correct": canary_correct, "canary_total": len(cases), "cases": cases, "status": "PASS" if all(c["pass"] for c in cases) and canary_correct == len(cases) else "FAIL"}


def h03_probability(kernel, seeds):
    n = 19; count = 110; directions0 = [(1, 0, 0)] * 55 + [(-1, 0, 0)] * 55; rows = []
    for seed in seeds:
        rng = np.random.default_rng(seed); directions = list(directions0); rng.shuffle(directions)
        raw, _, destinations = sparse_world(rng, n, count, directions=directions, sregs=[31] * count)
        world = NativeWorld(kernel, raw); world.tick(); observed = int(np.count_nonzero(world.raw)); predicted = len(set(destinations))
        rows.append({"observed": observed, "fiber_predicted": predicted, "fiber_pass": observed == predicted})
    outcomes = [r["observed"] for r in rows]; distribution = {str(k): v / len(rows) for k, v in sorted(Counter(outcomes).items())}; h = entropy(outcomes)
    passed = len(distribution) >= 3 and h >= 0.5 and all(r["fiber_pass"] for r in rows)
    return {"claim_id": "C16C003", "worlds": len(rows), "distribution": distribution, "entropy_bits": h, "fiber_pass": sum(r["fiber_pass"] for r in rows), "fiber_total": len(rows), "status": "PASS" if passed else "FAIL", "rows": rows}


def h04_classical(kernel, seeds):
    levels = []
    for index, n in enumerate((10, 14, 18, 22)):
        rng = np.random.default_rng(seeds[index]); count = max(12, int(round(0.04 * n ** 3))); ratios = []
        for _ in range(96):
            ds = [DIRECTIONS[int(i)] for i in rng.integers(0, len(DIRECTIONS), size=count)]
            raw, _, _ = sparse_world(rng, n, count, directions=ds, sregs=[37] * count, require_empty_destinations=False)
            world = NativeWorld(kernel, raw); world.tick(); ratios.append(int(np.count_nonzero(world.raw)) / count)
        mean = float(np.mean(ratios)); sd = float(np.std(ratios, ddof=1)); levels.append({"n": n, "components": count, "mean": mean, "sd": sd, "cv": sd / mean, "ratios": ratios})
    x = np.log([r["components"] for r in levels]); y = np.log([r["cv"] for r in levels]); slope, intercept = np.polyfit(x, y, 1); ratio = levels[-1]["cv"] / levels[0]["cv"]
    passed = -0.8 <= slope <= -0.2 and ratio <= 0.65
    return {"claim_id": "C16C004", "levels": levels, "alpha": float(slope), "largest_to_smallest_cv": ratio, "status": "PASS" if passed else "FAIL"}


def h05_order(kernel, seeds):
    cases = []
    for index, seed in enumerate(seeds):
        rng = np.random.default_rng(seed); permutation = tuple(int(x) for x in rng.permutation(3)); signs = tuple(int(x) for x in rng.choice((-1, 1), 3))
        d0 = transform((1, 0, 0), permutation, signs); a = transform((-1, 1, 0), permutation, signs); b = transform((1, -1, 0), permutation, signs)
        ab = sequential_order_trial(kernel, d0, a, b, n=(31, 35, 39)[index % 3]); ba = sequential_order_trial(kernel, d0, b, a, n=(31, 35, 39)[index % 3]); control1 = sequential_order_trial(kernel, d0, a, a); control2 = sequential_order_trial(kernel, d0, a, a)
        cases.append({"permutation": permutation, "signs": signs, "order_differs": ab.get("final") != ba.get("final"), "identical_control_equal": control1 == control2, "AB": ab, "BA": ba})
    return {"claim_id": "C16C005", "positive_pass": sum(c["order_differs"] for c in cases), "positive_total": len(cases), "canary_correct": sum(c["identical_control_equal"] for c in cases), "canary_total": len(cases), "cases": cases, "status": "PASS" if all(c["order_differs"] and c["identical_control_equal"] for c in cases) else "FAIL"}


def h06_phase(kernel, seeds):
    cases = []
    for index, seed in enumerate(seeds):
        rng = np.random.default_rng(seed); path = (6, 9, 12)[index % 3]; payloads = (int(rng.integers(50, 500)), int(rng.integers(501, 1200))); n = 47
        coherent = convergent_phase_paths(kernel, n=n, path_length=path, mode="AB_coherent", sregs=payloads, horizon=path + 10)
        shifted = convergent_phase_paths(kernel, n=n, path_length=path, mode="AB_phase_shifted", sregs=payloads, horizon=path + 10)
        closed = convergent_phase_paths(kernel, n=n, path_length=path, mode="closed", sregs=payloads, horizon=path + 10)
        cases.append({"path": path, "payloads": payloads, "count_equal": coherent["event_count"] == shifted["event_count"], "payload_distinguishes": coherent["detector_event_sregs"] != shifted["detector_event_sregs"], "closed_negative": closed["event_count"] == 0})
    return {"claim_id": "C16C006", "positive_pass": sum(c["count_equal"] and c["payload_distinguishes"] for c in cases), "positive_total": len(cases), "canary_correct": sum(c["closed_negative"] for c in cases), "canary_total": len(cases), "cases": cases, "status": "PASS" if all(c["count_equal"] and c["payload_distinguishes"] and c["closed_negative"] for c in cases) else "FAIL"}


def h07_transfer(kernel, seeds):
    frames = [((0, 1, 2), (1, 1, 1)), ((1, 2, 0), (1, -1, 1)), ((2, 0, 1), (-1, 1, 1)), ((0, 2, 1), (-1, -1, 1))]
    cases = []
    for index, seed in enumerate(seeds):
        permutation, signs = frames[index]; n = (29, 31, 35, 37)[index]
        for mode in ("trained", "offpath_cut", "untrained", "no_relay", "corridor_cut", "receiver_none", "wrong_receiver", "memory_ablation"):
            r = run_learned_policy_transfer(kernel, seed=seed, n=n, distance=7 + index, mode=mode, permutation=permutation, signs=signs)
            expected = mode in {"trained", "offpath_cut"}
            cases.append({"frame": index, "mode": mode, "functional": r["functional_policy_reinstantiated"], "expected": expected, "correct": r["functional_policy_reinstantiated"] == expected, "source_depleted": r["source_depleted_after_launch"], "corridor": r["corridor_all_intermediate_ticks_observed"]})
    positive = [c for c in cases if c["expected"]]; negative = [c for c in cases if not c["expected"]]
    passed = all(c["correct"] and c["source_depleted"] and c["corridor"] for c in positive) and all(c["correct"] for c in negative)
    return {"claim_id": "C16C007", "positive_pass": sum(c["correct"] for c in positive), "positive_total": len(positive), "canary_correct": sum(c["correct"] for c in negative), "canary_total": len(negative), "cases": cases, "status": "PASS" if passed else "FAIL"}


def h08_amplification(kernel, seeds):
    # This apparatus is defined only for axis-aligned incidence (two zero axes).
    directions = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)); cases = []
    for index, seed in enumerate(seeds):
        rng = np.random.default_rng(seed); n = (35, 39, 43)[index % 3]; d = directions[index]; sreg = int(rng.integers(1, 19665)); arms = []
        for count in (5, 6):
            r = regenerative_interface_trial(kernel, n=n, source_distance=7, downstream_distance=5, horizon=24, mode="semantic4_custom", direction=d, center=(n // 2,) * 3, source_sreg=sreg, semantic4_indices=list(range(count)))
            events = r["downstream_event_ticks"]["5"]; arms.append({"guard_cells": count, "events": events, "event_count": len(events)})
        cases.append({"n": n, "direction": d, "sreg": sreg, "k5_transmits": arms[0]["event_count"] > 0, "k6_blocks": arms[1]["event_count"] == 0, "arms": arms})
    return {"claim_id": "C16C008", "positive_pass": sum(c["k5_transmits"] and c["k6_blocks"] for c in cases), "positive_total": len(cases), "canary_correct": sum(c["k5_transmits"] for c in cases), "canary_total": len(cases), "cases": cases, "status": "PASS" if all(c["k5_transmits"] and c["k6_blocks"] for c in cases) else "FAIL"}


def h09_bell(kernel, cells):
    n = 67; hubs = ((17, 31, 29), (50, 31, 29)); external = []; internal = []
    for cell in cells:
        li, a, b = cell["lambda_index"], cell["a"], cell["b"]; lam = LAMBDA[li]
        external.append(bell_trial(kernel, n, hubs, lam, li, a, b)); internal.append(internal_bell_trial(kernel, n, hubs, lam, li, a, b))
    es = bell_summary(external); ins = bell_summary(internal); ei = setting_independence_summary(external); ii = setting_independence_summary(internal)
    # Frozen causal/assumption canary: settings are deterministic functions of lambda,
    # so the measurement-independence audit must reject the schedule.
    dependent_schedule = []
    for _ in range(16):
        for li, lam in enumerate(LAMBDA):
            dependent_schedule.append({"lambda_index": li, "a": 0 if lam[0] < 0 else 1, "b": 0 if lam[1] < 0 else 1})
    dependence_audit = setting_independence_summary(dependent_schedule)
    dependence_detected = not dependence_audit["all_cells_nonzero"]
    passed = abs(es["CHSH"]) <= 2 and abs(ins["CHSH"]) <= 2 and all(t["generators_valid"] and t["local_records_valid"] for t in internal) and ei["max_fractional_cell_deviation"] == 0 and ii["max_fractional_cell_deviation"] == 0 and dependence_detected
    return {"claim_id": "C16C009", "external": {"summary": es, "measurement_independence": ei, "retained": len(external)}, "internal": {"summary": ins, "measurement_independence": ii, "retained": len(internal), "generators_valid": sum(t["generators_valid"] for t in internal), "records_valid": sum(t["local_records_valid"] for t in internal)}, "measurement_dependence_canary": {"trials": len(dependent_schedule), "audit": dependence_audit, "detected": dependence_detected}, "no_postselection": True, "status": "PASS" if passed else "FAIL"}


def main():
    checkpoint = ROOT / "CHECKPOINTS" / "CP06_FINAL_HOLDOUTS.json"
    if checkpoint.exists(): print(checkpoint.read_text(encoding="utf-8")); return
    verify_freeze(); audit_kernel("CORE16_BEFORE_FINAL_UNTOUCHED_HOLDOUT")
    kernel, _ = verify_and_load_kernel(1); manifest = read_json(ROOT / "FINAL_HOLDOUTS" / "FINAL_CHALLENGE_MANIFEST.json"); started = time.perf_counter()
    functions = [
        ("H01", h01_fiber, manifest["seeds"]["fiber"]), ("H02", h02_resurrection, manifest["seeds"]["resurrection"]),
        ("H03", h03_probability, manifest["seeds"]["probability"]), ("H04", h04_classical, manifest["seeds"]["classical"]),
        ("H05", h05_order, manifest["seeds"]["order"]), ("H06", h06_phase, manifest["seeds"]["phase"]),
        ("H07", h07_transfer, manifest["seeds"]["transfer"]), ("H08", h08_amplification, manifest["seeds"]["amplification"]),
        ("H09", h09_bell, manifest["bell_balanced_random_order"]),
    ]
    results = []
    for hid, function, data in functions:
        result = function(kernel, data); result["holdout_id"] = hid; result["partition"] = "FINAL_UNTOUCHED_HOLDOUT"; result["challenge_manifest_sha256"] = sha(ROOT / "FINAL_HOLDOUTS" / "FINAL_CHALLENGE_MANIFEST.json"); result["content_sha256"] = canonical_hash(result)
        path = ROOT / "FINAL_HOLDOUTS" / f"{hid}_{result['claim_id']}.json"; write_json(path, result); results.append({"holdout_id": hid, "claim_id": result["claim_id"], "status": result["status"], "path": str(path.relative_to(ROOT)), "sha256": sha(path)})
    summary = {"status": "PASS" if all(r["status"] == "PASS" for r in results) else "MIXED", "holdouts": results, "pass_count": sum(r["status"] == "PASS" for r in results), "total": len(results), "elapsed_seconds": time.perf_counter() - started, "utc": utc()}
    write_json(ROOT / "LEVEL_SELECTION_HOLDOUTS.json", summary); write_json(checkpoint, summary)
    update_state(status="FINAL_HOLDOUTS_COMPLETE_PENDING_SYNTHESIS", phase="PHASE_K_TO_M", completed_checkpoints=["PARENT_AUDIT", "DISCOVERY_ROOTS", "MODEL_LEVEL_SELECTION", "ADAPTIVE_GRANDCHILDREN", "SOURCE_FREEZE", "FINAL_CHALLENGES_GENERATED", "FINAL_HOLDOUTS"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()
