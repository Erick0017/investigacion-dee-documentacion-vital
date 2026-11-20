"""Archived arithmetic and optional exact Pendulum replay. Never imports DEE.

Input: result JSONs produced by external_trial; --replay starts only the
published external environment and repeats the archived executed torques.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_result(path):
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(obj, dict) and "advance" in obj and isinstance(obj["advance"], dict):
        obj = obj["advance"]["result"]
    while isinstance(obj, dict) and "result" in obj and isinstance(obj["result"], dict):
        obj = obj["result"]
    if "rows" not in obj:
        raise ValueError(str(path) + ": no archived result.rows")
    return obj


def decoded_command(read):
    if int(read.get("state", 0)) == 1 and int(read.get("semantic", -1)) == 1:
        direction = list(read.get("direction", []))
        if direction == [1, 0, 0]:
            return 2.0
        if direction == [-1, 0, 0]:
            return -2.0
    return 0.0


def replay(result, worker, deps, executable):
    command = [str(executable), "-I", "-B", "-u", str(worker), "--deps", str(deps)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding="utf-8")
    def request(obj):
        process.stdin.write(json.dumps(obj, allow_nan=False) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if not line:
            raise RuntimeError("worker exit: " + process.stderr.read())
        response = json.loads(line)
        if not response["ok"]:
            raise RuntimeError(response["error"])
        return response
    try:
        initial = result["initial_environment"]
        if "snapshot" in initial:
            initialized = request({"op": "restore", "snapshot": initial["snapshot"]})
        else:
            initialized = request({"op": "reset", "seed": int(initial["seed"]), "g": float(initial.get("g", 10.0))})
        actual_identity = request({"op": "info"})["identity"]
        mismatches = []
        for i, row in enumerate(result["rows"]):
            actual = request({"op": "step", "torque": float(row["executed_torque"])})
            expected = row["environment_response"]
            for key, expected_value in expected.items():
                if actual.get(key) != expected_value:
                    mismatches.append({"index": i, "field": key, "archived": expected_value, "replayed": actual.get(key)})
        snapshot = request({"op": "snapshot"})["snapshot"]
        archived_final = result.get("final_environment", {})
        if isinstance(archived_final, str):
            archived_final = json.loads(archived_final)
        archived_snapshot = archived_final.get("environment", archived_final.get("snapshot", archived_final))
        snapshot_match = None if not archived_snapshot else snapshot == archived_snapshot
        state_match = None if not archived_snapshot else ({k: v for k, v in snapshot.items() if k != "identity"}
                     == {k: v for k, v in archived_snapshot.items() if k != "identity"})
        return {"kind": "EXTERNAL_ENVIRONMENT_REPLAY_NOT_NATIVE_REPRODUCTION", "identity": actual_identity,
                "steps": len(result["rows"]), "response_mismatches": mismatches,
                "all_responses_exact": not mismatches, "final_environment_snapshot_exact": snapshot_match,
                "final_physical_rng_wrapper_state_exact": state_match}
    finally:
        if process.poll() is None:
            request({"op": "close"})
            process.wait(timeout=10)


def calculate(result):
    rows = result["rows"]
    codec_errors, decoder_errors = [], []
    request_final = {}
    reward = []
    commands, torques, statuses = Counter(), Counter(), Counter()
    observations = [r["observation_before"] for r in rows]
    for i, row in enumerate(rows):
        response = row["environment_response"]
        reward.append(float(response["reward"]))
        delay = int(row["codec"].get("delay", 0))
        source = observations[max(0, i - delay)]
        q = max(1, min(145, round(73 + 40 * float(source[1]))))
        value = row["codec"].get("value", row["codec"].get("q"))
        if q != value:
            codec_errors.append({"index": i, "computed": q, "archived": value, "delay": delay})
        decoded = decoded_command(row["native_read"])
        archived = float(row["actuator"]["command"])
        if decoded != archived:
            decoder_errors.append({"index": i, "computed": decoded, "archived": archived})
        commands[str(archived)] += 1
        torques[str(float(row["executed_torque"]))] += 1
        statuses[row["actuator"].get("status", "UNSPECIFIED")] += 1
        for j, receipt in enumerate(row.get("requests", [])):
            request_final[str(receipt.get("id", f"row{i}_request{j}"))] = receipt
    receipt_statuses = Counter(r.get("status", "UNSPECIFIED") for r in request_final.values())
    channel_statuses = Counter(("|".join(r.get("channels", ["UNSPECIFIED"])) + ":" + r.get("status", "UNSPECIFIED")) for r in request_final.values())
    count = len(rows)
    return {"rows": count, "reward_sum": math.fsum(reward),
            "reward_mean": None if not count else math.fsum(reward) / count,
            "reward_min": min(reward) if count else None, "reward_max": max(reward) if count else None,
            "simulated_seconds": count * 0.05, "native_command_counts": dict(commands),
            "executed_torque_counts": dict(torques), "actuator_statuses": dict(statuses),
            "nonzero_native_commands": sum(n for k, n in commands.items() if float(k) != 0),
            "nonzero_executed_torques": sum(n for k, n in torques.items() if float(k) != 0),
            "requests_unique": len(request_final), "request_final_statuses": dict(receipt_statuses),
            "request_statuses_by_channel": dict(channel_statuses),
            "codec_mismatches": codec_errors, "decoder_mismatches": decoder_errors,
            "scope": "Arithmetic checks fixed codec and actuator only; rewards do not establish native learning or useful control. Native reproduction is not performed."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--worker", type=Path, default=Path(__file__).with_name("pendulum_worker.py"))
    parser.add_argument("--deps", type=Path, default=Path(__file__).with_name("deps"))
    parser.add_argument("--external-python", type=Path, default=Path(sys.executable))
    args = parser.parse_args()
    report = {"schema": "external-archived-recalculation-1", "trials": [], "matched_environment_comparisons": []}
    loaded = []
    for path in args.sources:
        result = load_result(path)
        loaded.append((path, result))
        trial = {"source": path.name, "source_sha256": sha(path), "metrics": calculate(result)}
        if args.replay:
            trial["replay"] = replay(result, args.worker, args.deps, args.external_python)
        report["trials"].append(trial)
    for i, (path_a, a) in enumerate(loaded):
        for path_b, b in loaded[i + 1:]:
            initial_a = a["initial_environment"].get("snapshot", {})
            initial_b = b["initial_environment"].get("snapshot", {})
            same_state = bool(initial_a) and initial_a.get("state_float64_hex") == initial_b.get("state_float64_hex")
            same_g = initial_a.get("gravity_hex") == initial_b.get("gravity_hex")
            if not (same_state and same_g):
                continue
            pairs = list(zip(a["rows"], b["rows"]))
            deltas = [[float(x) - float(y) for x, y in zip(ra["environment_response"]["observation"], rb["environment_response"]["observation"])] for ra, rb in pairs]
            first = next((k for k, d in enumerate(deltas) if any(v != 0 for v in d)), None)
            native_a, native_b = a.get("initial_native", {}), b.get("initial_native", {})
            report["matched_environment_comparisons"].append({
                "a": path_a.name, "b": path_b.name, "same_initial_pendulum_state": True,
                "same_gravity": True, "same_environment_rng": initial_a.get("np_random_state") == initial_b.get("np_random_state"),
                "same_initial_native_raw": native_a.get("RAW_sha256") == native_b.get("RAW_sha256"),
                "same_initial_native_clocks": native_a.get("clocks_sha256") == native_b.get("clocks_sha256"),
                "compared_steps": len(pairs), "first_different_observation_index": first,
                "observation_deltas_first_difference": None if first is None else deltas[first],
                "steps_with_different_torque": sum(ra["executed_torque"] != rb["executed_torque"] for ra, rb in pairs),
                "scope": "Action-dependent future may diverge; observation differences do not establish learned control competence or independent acquisition."
            })
    totals = {"archived_steps": 0, "produced_nonzero_native_commands": 0, "executed_nonzero_torques": 0,
              "requests_unique_within_trials": 0, "receipt_statuses": {}, "receipt_statuses_by_channel": {}}
    statuses, by_channel = Counter(), Counter()
    for trial in report["trials"]:
        metrics = trial["metrics"]
        totals["archived_steps"] += metrics["rows"]
        totals["produced_nonzero_native_commands"] += metrics["nonzero_native_commands"]
        totals["executed_nonzero_torques"] += metrics["nonzero_executed_torques"]
        totals["requests_unique_within_trials"] += metrics["requests_unique"]
        statuses.update(metrics["request_final_statuses"])
        by_channel.update(metrics["request_statuses_by_channel"])
    totals["receipt_statuses"] = dict(statuses)
    totals["receipt_statuses_by_channel"] = dict(by_channel)
    totals["scope"] = "Counts across identified trials/forks and continuations, not independent learning samples or one uninterrupted life."
    report["totals"] = totals
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "trials": len(report["trials"])}))


if __name__ == "__main__":
    main()
