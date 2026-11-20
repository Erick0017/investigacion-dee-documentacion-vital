"""Recalculate 12 closed CF01 protocol-3 primaries with stdlib; zero DEE ticks.

The external gate law scores/materializes an opportunity, never selects E1's
command. The decoder below uses only contact RAW, fixed times and a fixed rule.
Fixed/random references are separate arithmetic external actors, not E1 inputs.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import importlib.util
import json
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARMS = ("MAIN", "B_SHAM", "B_CUT", "SERVICIO_ANULADO")
SEEDS = (101, 202, 303, 404, 505, 606, 707, 808)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with gzip.open(path, "rt", encoding="utf8") as stream:
        return json.load(stream)


def observation(q):
    assert isinstance(q["raw"], str) and q["raw"].isdecimal()
    assert isinstance(q["clock"], str) and q["clock"].isdecimal()
    v = int(q["raw"])
    assert 0 <= v < 2**64
    def signed(shift):
        k = (v >> shift) & 15
        return k - 16 if k & 8 else k
    decoded = {"state": v & 0xffffffff, "s_reg": (v >> 32) & 65535,
               "semantic": (v >> 60) & 15,
               "direction": [signed(i) for i in (48, 52, 56)]}
    for key, value in decoded.items():
        assert q[key] == value, (key, q[key], value)
    return decoded


def witness(w):
    checked = 0
    for key in ("A", "B", "B_datum", "query_gate"):
        if key in w:
            observation(w[key]); checked += 1
    for key in ("own", "private_B", "context_A"):
        for q in w.get(key, []):
            observation(q); checked += 1
    for q in w.get("contacts", {}).values():
        observation(q); checked += 1
    return checked


def loads(w, key):
    return [q["s_reg"] for q in w[key]]


def delta(w):
    left, right = loads(w, "own")
    return left - right


def decode(native):
    """Target-blind reader: neither gate nor expected answer is an argument."""
    critical = native["row"]["critical_tick"]
    samples = []
    for tick in (critical - 16, critical - 15):
        f = next(q for q in native["frames"] if q["tick"] == tick)
        roles = []
        for r in (-1, 0, 1):
            q = f["contacts"][str(r)]
            v = observation(q)
            if v["state"] > 0 and v["semantic"] == 1 and v["direction"] in ([r, -1, -1], [r, -1, 0]):
                roles.append(r)
        samples.append({"tick": tick, "material_roles": roles,
                        "command": (1 if roles[0] >= 0 else -1) if len(roles) == 1 else None,
                        "simultaneous_conflict": len(roles) > 1})
    if samples[-1]["simultaneous_conflict"]:
        return {"rule": "latest_unique_with_max_hold1tick.v1", "samples": samples,
                "command": None, "source_tick": None, "reason": "deadline_conflict"}
    chosen = next((s for s in reversed(samples) if s["command"] is not None), None)
    return {"rule": "latest_unique_with_max_hold1tick.v1", "samples": samples,
            "command": None if chosen is None else chosen["command"],
            "source_tick": None if chosen is None else chosen["tick"],
            "reason": "no_native_output" if chosen is None else
                      "current" if chosen["tick"] == critical - 15 else "fixed_hold_one_tick"}


def parse(path, evidence):
    document = read(path)
    assert document["returncode"] == 0
    envelope = document["result"]
    data = envelope["result"]
    rows = []; receipts = {}; checked = 0; last_env = None
    for i, outer in enumerate(data["rows"]):
        native = outer["native"]
        assert native["revision"] == "CF01.R9.protocol.3"
        pair = outer["raw_measurements"]
        reference = outer["environment_reference_not_injected"]
        expected_gate = 1 if pair[0] + reference >= pair[1] else -1
        assert expected_gate == outer["available_gate"] == native["row"]["availability"]
        assert pair == native["row"]["public_raw"]
        assert native["row"]["private_B_raw"] is None
        assert native["row"]["mode"] == "intact"
        all_witnesses = [native["before"], *native["frames"], native["after"]]
        checked += sum(witness(w) for w in all_witnesses)
        decoded = decode(native)
        assert decoded == outer["fixed_output_sampling"]
        executed = decoded["command"] if outer["actuator_mode"] == "closed" else None
        passed = executed == expected_gate
        assert executed == outer["executed_external_command"]
        assert passed == outer["job_passed"]
        before, after = outer["environment_before"], outer["environment_after"]
        assert before["law"] == "CF01.calibrated_gate.v1"
        assert before["reference"] == reference == 7
        if last_env is not None:
            assert before == last_env
        recalculated_env = dict(before)
        recalculated_env["attempts"] += 1
        recalculated_env["passed"] += int(passed)
        recalculated_env["backlog"] = list(before["backlog"]) + ([] if passed else [pair])
        recalculated_env["last_native_tick"] = native["after"]["tick"]
        recalculated_env["last_command"] = executed
        assert recalculated_env == after
        last_env = after
        for request in native["requests"]:
            receipt = request["receipt"]
            assert receipt["requested_tick"] == request["tick"]
            assert receipt["id"] == request["id"]
            if receipt["id"] in receipts:
                assert receipts[receipt["id"]] == receipt
            receipts[receipt["id"]] = receipt
        old_roles = decoded["samples"][-1]["material_roles"]
        assert native["row"]["emitted"] == old_roles
        critical = native["row"]["critical_tick"]
        old_contact = next(w for w in native["frames"] if w["tick"] == critical - 15)
        q = old_contact["contacts"]["0"]
        old_query = bool(q["state"] > 0 and q["semantic"] == 1 and q["direction"] == [0, -1, -1])
        assert old_query == native["row"]["query_at_contact"]
        post3 = next(w for w in native["frames"] if w["tick"] == critical + 3)
        rows.append({"case_row": i, "attempt_global": before["attempts"] + 1,
          "start_tick": native["before"]["tick"], "critical_tick": critical,
          "end_tick": native["after"]["tick"], "measurements": pair,
          "environment_gate": expected_gate, "native_command": decoded["command"],
          "executed_command": executed, "external_job_passed": passed,
          "native_correct_for_gate": decoded["command"] == expected_gate,
          "reader": decoded, "old_deadline_roles": old_roles,
          "old_deadline_silence": not old_roles, "deadline_query_material": old_query,
          "own_start": loads(native["before"], "own"), "own_end": loads(native["after"], "own"),
          "own_delta_start": delta(native["before"]), "own_delta_post3": delta(post3),
          "own_delta_end": delta(native["after"]),
          "context_start": loads(native["before"], "context_A"),
          "context_end": loads(native["after"], "context_A"),
          "context_constant_in_all_recorded_samples": all(loads(w, "context_A") == loads(native["before"], "context_A") for w in all_witnesses),
          "private_B_start": loads(native["before"], "private_B"),
          "private_B_61_19_in_all_recorded_samples": all(loads(w, "private_B") == [61, 19] for w in all_witnesses)})
    code = evidence / "codigo_ejecutado" / document["code_revision_sha256"] / "sistema/capacidades/cierre_funcional_cf01.py"
    assert code.is_file()
    return {"case": document["case"], "source": str(path), "source_bytes": path.stat().st_size,
      "source_sha256": sha(path), "code_revision_sha256": document["code_revision_sha256"],
      "archived_service_code": {"path": str(code), "sha256": sha(code)},
      "instrument": envelope["INSTRUMENTO"], "physical_endpoint": envelope["physical"],
      "initial_environment": data["rows"][0]["environment_before"],
      "final_environment": data["rows"][-1]["environment_after"],
      "receipts": dict(Counter(q["status"] for q in receipts.values())),
      "requests_unique": len(receipts), "observations_checked": checked, "rows": rows}


def metrics(rows):
    return {"attempts": len(rows), "native_correct": sum(q["native_correct_for_gate"] for q in rows),
      "external_passed": sum(q["external_job_passed"] for q in rows),
      "valid_native": sum(q["native_command"] is not None for q in rows),
      "external_commands": sum(q["executed_command"] is not None for q in rows),
      "reader_reasons": dict(Counter(q["reader"]["reason"] for q in rows)),
      "deadline_silence": sum(q["old_deadline_silence"] for q in rows),
      "deadline_query_material_samples": sum(q["deadline_query_material"] for q in rows),
      "own_start": rows[0]["own_start"], "own_end": rows[-1]["own_end"],
      "own_delta_start": rows[0]["own_delta_start"], "own_delta_end": rows[-1]["own_delta_end"],
      "context_start": rows[0]["context_start"], "context_end": rows[-1]["context_end"],
      "private_B_retained_in_all_samples": all(q["private_B_61_19_in_all_recorded_samples"] for q in rows)}


def snapshots(trials, folder):
    if not folder or not folder.is_dir():
        return {"scope": "No full snapshots supplied to this exported-primary recalculation."}
    spec = importlib.util.spec_from_file_location("cf01_existing_snapshot_reader", HERE / "observador_snapshot_existente.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    out = []
    for trial in trials:
        instrument = trial["instrument"]
        candidates = sorted(folder.glob(instrument["life_id"] + ".T" + str(instrument["tick"]) + ".*.deetsnap.gz"))
        matches = []
        for path in candidates:
            snap = mod.Snapshot(path)
            summary = snap.summary()
            if all(summary[key] == trial["physical_endpoint"][key] for key in ("N", "tick", "RAW_sha256", "clocks_sha256")):
                matches.append({"snapshot": summary,
                  "instrument_snapshot_hash_identical": instrument["snapshot_sha256"] in (summary["encoded_sha256"], summary["native_sha256"]),
                  "own": [snap.observation(p) for p in ([5, 15, 15], [7, 15, 15])],
                  "context": [snap.observation(p) for p in ([5, 15, 13], [7, 15, 13])],
                  "private_B": [snap.observation(p) for p in ([18, 15, 15], [20, 15, 15])]})
        assert matches, trial["case"]
        out.append({"case": trial["case"], "matching_full_local_checkpoints": matches})
    return {"scope": "Full native-v2 snapshots parsed read-only including channels, agenda, receipts and owner metadata. Physical endpoint hashes compared, not falsely equated with a documentary snapshot digest.", "results": out}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=ROOT / "evidencia/campanas/CF01_CIERRE_FUNCIONAL")
    parser.add_argument("--snapshots", type=Path)
    parser.add_argument("--out", type=Path, default=HERE / "RECALCULO_SERVICIO_V3_CF01.json")
    args = parser.parse_args()
    trials = [parse(args.evidence / ("SERVICIO_CF01_" + arm + "_V" + str(i) + ".json.gz"), args.evidence) for arm in ARMS for i in (1, 2, 3)]
    by_arm = {}
    for arm in ARMS:
        group = [q for q in trials if q["case"].startswith("SERVICIO_CF01_" + arm + "_V")]
        for first, second in zip(group, group[1:]):
            assert first["final_environment"] == second["initial_environment"]
            assert first["instrument"]["tick"] == second["rows"][0]["start_tick"]
        rows = [r for q in group for r in q["rows"]]
        by_arm[arm] = {"summary": metrics(rows), "first_in_each_sequence": metrics([q["rows"][0] for q in group]),
                      "later_in_each_sequence": metrics([r for q in group for r in q["rows"][1:]])}
    main_rows = [r for q in trials if q["case"].startswith("SERVICIO_CF01_MAIN_V") for r in q["rows"]]
    references = []
    for policy in ("fixed_left", "fixed_right", "random"):
        for seed in SEEDS if policy == "random" else (None,):
            rng = random.Random(seed) if seed is not None else None
            choices = [1 if policy == "fixed_left" else -1 if policy == "fixed_right" else rng.choice((-1, 1)) for _ in main_rows]
            outcomes = [{"attempt": r["attempt_global"], "measurements": r["measurements"], "environment_gate": r["environment_gate"],
                         "command": command, "passed": command == r["environment_gate"]} for r, command in zip(main_rows, choices)]
            references.append({"policy": policy, "seed": seed, "attempts": len(outcomes), "passed": sum(q["passed"] for q in outcomes),
                               "new_native_ticks": 0, "scope": "Independent external actors; no outputs supplied to DEE. Single RNG stream across all 18 opportunities.", "rows": outcomes})
    main_group = [q for q in trials if q["case"].startswith("SERVICIO_CF01_MAIN_V")]
    annulled_group = [q for q in trials if q["case"].startswith("SERVICIO_CF01_SERVICIO_ANULADO_V")]
    physical_equality = [{"sequence": i + 1, "RAW_equal": a["physical_endpoint"]["RAW_sha256"] == b["physical_endpoint"]["RAW_sha256"],
                         "clocks_equal": a["physical_endpoint"]["clocks_sha256"] == b["physical_endpoint"]["clocks_sha256"]} for i, (a, b) in enumerate(zip(main_group, annulled_group))]
    result = {"schema": "CF01.calibrated_service.protocol3.recalculation.v1", "new_native_ticks": 0,
      "trials": trials, "totals_by_arm": by_arm, "external_only_references": references,
      "MAIN_vs_external_action_annulled_physical_endpoints": physical_equality,
      "local_full_snapshot_read_only_validation": snapshots(trials, args.snapshots),
      "limits": [
        "The two-sample reader is a prepared instrument fixed before these reserves, not a learned recovery strategy. Old protocol-2 1/4 outcomes remain unchanged.",
        "CUT is not an isolated equal-own-reference social contrast: prior failed compound episodes changed its own relative reference from 3 to 7; within this panel it changes from 7 to 9. Compensation must not be credited as intact social context.",
        "MAIN/SHAM combine current public measurements, own acquired scalar history and retained social context; B's private 61/19 is retained but not newly updated by these opportunities.",
        "Gate reference 7 belongs only to the fixed external law and is not injected as a target. Raw public pairs and native environmental resources are admitted; decoder uses only contact RAW and fixed times.",
        "External action annulment does not annul native contact/return. Physical endpoint equality is an action-path control, not evidence of a learned closed external-return policy.",
        "The environment requests every episode. A sampled query branch does not establish autonomous initiation or exclusive act-versus-query selection.",
        "Three consecutive sequences per arm are one life continuation, not independent learners. Opposite sampled commands at two times are resolved by the fixed latest-sample rule, not target selection.",
        "Sparse witnesses prove only their recorded times/regions. Optional full endpoint parsing does not create unrecorded trajectories."]}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"output": str(args.out), "sha256": sha(args.out), "native_ticks": 0,
                      "totals": {arm: value["summary"] for arm, value in by_arm.items()},
                      "references": [{k: q[k] for k in ("policy", "seed", "attempts", "passed")} for q in references]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
