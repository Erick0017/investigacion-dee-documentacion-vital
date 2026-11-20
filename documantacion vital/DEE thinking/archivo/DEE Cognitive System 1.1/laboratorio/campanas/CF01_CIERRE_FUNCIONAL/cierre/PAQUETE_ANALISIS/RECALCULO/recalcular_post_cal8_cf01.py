"""Recalculate archived POST and CAL8 CF01 paired histories; zero native ticks.

Requires the adjacent recalcular_servicio_v3_cf01.py; optional read-only full
snapshot comparison also uses observador_snapshot_existente.py. No DEE imports.
"""
from pathlib import Path
from collections import Counter
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


base = module("cf01_fixed_window_recalculator", HERE / "recalcular_servicio_v3_cf01.py")


def native_row(n):
    checked = sum(base.witness(w) for w in [n["before"], *n["frames"], n["after"]])
    decoded = base.decode(n)
    critical = n["row"]["critical_tick"]
    frame = lambda tick: next(w for w in n["frames"] if w["tick"] == tick)
    roles = decoded["samples"][-1]["material_roles"]
    assert roles == n["row"]["emitted"]
    native_useful = [r for r in roles if (1 if r >= 0 else -1) == n["row"]["availability"]]
    native_wrong = [r for r in roles if (1 if r >= 0 else -1) != n["row"]["availability"]]
    assert native_useful == n["row"]["useful"]
    assert native_wrong == n["row"]["wrong"]
    assert n["row"]["private_B_raw"] is None
    receipts = {}
    for request in n["requests"]:
        receipt = request["receipt"]
        assert receipt["id"] == request["id"]
        assert receipt["requested_tick"] == request["tick"]
        if receipt["id"] in receipts:
            assert receipts[receipt["id"]] == receipt
        receipts[receipt["id"]] = receipt
    all_w = [n["before"], *n["frames"], n["after"]]
    row = {"start_tick": n["before"]["tick"], "critical_tick": critical, "end_tick": n["after"]["tick"],
      "raw_measurements": n["row"]["public_raw"], "native_environment_availability": n["row"]["availability"],
      "feedback": n["row"]["mode"], "reader": decoded,
      "decoded_action_useful_for_native_condition": decoded["command"] == n["row"]["availability"],
      "own_before": base.loads(n["before"], "own"), "own_pre_contact": base.loads(frame(critical - 16), "own"),
      "own_at_contact": base.loads(frame(critical - 15), "own"),
      "own_post3": base.loads(frame(critical + 3), "own"), "own_after": base.loads(n["after"], "own"),
      "delta_before": base.delta(n["before"]), "delta_pre_contact": base.delta(frame(critical - 16)),
      "delta_post3": base.delta(frame(critical + 3)), "delta_after": base.delta(n["after"]),
      "context_before": base.loads(n["before"], "context_A"), "context_after": base.loads(n["after"], "context_A"),
      "context_7_5_in_all_samples": all(base.loads(w, "context_A") == [7, 5] for w in all_w),
      "B_private_61_19_in_all_samples": all(base.loads(w, "private_B") == [61, 19] for w in all_w),
      "requests_unique": len(receipts), "receipts": dict(Counter(q["status"] for q in receipts.values())),
      "packed_observations_checked": checked}
    return row


def parse(path, evidence):
    d = base.read(path)
    assert d["returncode"] == 0
    envelope = d["result"]; result = envelope["result"]
    rows = []
    sequence = result["rows"] if "rows" in result else [{"native": result}]
    previous = None
    for outer in sequence:
        n = outer["native"]
        row = native_row(n)
        row["revision"] = n["revision"]
        if "environment_before" in outer:
            before, after = outer["environment_before"], outer["environment_after"]
            pair, reference = outer["raw_measurements"], outer["environment_reference_not_injected"]
            gate = 1 if pair[0] + reference >= pair[1] else -1
            assert gate == outer["available_gate"] == n["row"]["availability"]
            assert pair == n["row"]["public_raw"]
            assert row["reader"] == outer["fixed_output_sampling"]
            if previous is not None:
                assert previous == before
            command = row["reader"]["command"] if outer["actuator_mode"] == "closed" else None
            passed = command == gate
            assert command == outer["executed_external_command"] and passed == outer["job_passed"]
            expected = dict(before)
            expected["attempts"] += 1; expected["passed"] += int(passed)
            expected["backlog"] = list(before["backlog"]) + ([] if passed else [pair])
            expected["last_native_tick"] = row["end_tick"]; expected["last_command"] = command
            assert expected == after
            assert before["reference"] == reference
            if "feedback_mode" in outer:
                assert outer["feedback_mode"] == n["row"]["mode"]
            row.update(environment_before=before, environment_after=after, environment_reference=reference,
                       environment_gate=gate, executed_command=command, external_job_passed=passed)
            previous = after
        rows.append(row)
    code = evidence / "codigo_ejecutado" / d["code_revision_sha256"] / "sistema/capacidades/cierre_funcional_cf01.py"
    assert code.is_file()
    return {"case": d["case"], "source": str(path), "source_bytes": path.stat().st_size,
      "source_sha256": base.sha(path), "code_revision_sha256": d["code_revision_sha256"],
      "archived_service_code": {"path": str(code), "sha256": base.sha(code)},
      "instrument": envelope["INSTRUMENTO"], "physical_endpoint": envelope["physical"], "rows": rows}


def paired(left, right):
    out = []
    for a, b in zip(left, right):
        assert a["critical_tick"] == b["critical_tick"]
        assert a["raw_measurements"] == b["raw_measurements"]
        assert a["native_environment_availability"] == b["native_environment_availability"]
        out.append({"same_age_critical_tick": a["critical_tick"], "same_raw_measurements": a["raw_measurements"],
                    "same_native_condition": a["native_environment_availability"], "intact": a, "return_omitted": b})
    return out


def fork_check(evidence, folder, name, parent_trial):
    path = evidence / (name + ".json.gz")
    d = base.read(path)
    assert d["returncode"] == 0
    record = d["result"]
    assert record["parent"]["snapshot_sha256"] == parent_trial["instrument"]["snapshot_sha256"]
    assert record["parent"]["tick"] == parent_trial["instrument"]["tick"]
    assert all(record["physical"][k] == parent_trial["physical_endpoint"][k] for k in ("N", "tick", "RAW_sha256", "clocks_sha256"))
    out = {"source": str(path), "source_sha256": base.sha(path), "parent": record["parent"],
           "branch_life": record["life_id"], "physical": record["physical"]}
    if folder:
        observer = module("cf01_readonly_snapshot_for_fork", HERE / "observador_snapshot_existente.py")
        parent = parent_trial["instrument"]
        parents = list(folder.glob(parent["life_id"] + ".T" + str(parent["tick"]) + ".*.deetsnap.gz"))
        parents = [observer.Snapshot(p) for p in parents]
        left = next(q for q in parents if parent["snapshot_sha256"] in (q.encoded_sha256, q.decoded_sha256))
        right = observer.Snapshot(folder.parent.parent / record["snapshot"])
        cmp = observer.compare(left, right)
        assert cmp["prefix_through_execution_before_metadata_equal"]
        assert cmp["RAW_different_sites"] == cmp["clock_different_sites"] == 0
        out.update(parent_snapshot=left.summary(), fork_snapshot=right.summary(), full_snapshot_comparison=cmp)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=ROOT / "evidencia/campanas/CF01_CIERRE_FUNCIONAL")
    p.add_argument("--snapshots", type=Path)
    p.add_argument("--out", type=Path, default=HERE / "RECALCULO_POST_CAL8_CF01.json")
    a = p.parse_args()
    names = ("POST_CAMBIO_MAIN", "POST_CAMBIO_OMIT", "POST_PRIMER_USO_MAIN", "POST_PRIMER_USO_OMIT",
             "POST_SEGUNDO_USO_MAIN", "POST_SEGUNDO_USO_OMIT", "CAL8_MAIN", "CAL8_OMIT")
    trials = [parse(a.evidence / (name + ".json.gz"), a.evidence) for name in names]
    index = {q["case"]: q for q in trials}
    post_intact = [index[q]["rows"][0] for q in ("POST_CAMBIO_MAIN", "POST_PRIMER_USO_MAIN", "POST_SEGUNDO_USO_MAIN")]
    post_omitted = [index[q]["rows"][0] for q in ("POST_CAMBIO_OMIT", "POST_PRIMER_USO_OMIT", "POST_SEGUNDO_USO_OMIT")]
    for group in (post_intact, post_omitted):
        for first, second in zip(group, group[1:]):
            assert first["end_tick"] == second["start_tick"]
            assert first["own_after"] == second["own_before"]
    baseline = base.read(a.evidence / "SERVICIO_CF01_MAIN_V3.json.gz")
    base_trial = {"instrument": baseline["result"]["INSTRUMENTO"], "physical_endpoint": baseline["result"]["physical"]}
    forks = [fork_check(a.evidence, a.snapshots, "POST_OMIT_FORK", base_trial),
             fork_check(a.evidence, a.snapshots, "CAL8_OMIT_FORK", index["POST_SEGUNDO_USO_MAIN"])]
    cal_left = index["CAL8_MAIN"]["rows"]; cal_right = index["CAL8_OMIT"]["rows"]
    assert cal_left[0]["own_before"] == cal_right[0]["own_before"] == post_intact[-1]["own_after"]
    result = {"schema": "CF01.post_and_calibration8.recalculation.v1", "new_native_ticks": 0,
      "trials": trials, "matched_POST_history_and_two_uses": paired(post_intact, post_omitted),
      "matched_calibration8_five_opportunities": paired(cal_left, cal_right), "exact_fork_checks": forks,
      "read_only_endpoint_snapshots": base.snapshots(trials, a.snapshots),
      "summary": {
        "POST_history_intact_delta": [post_intact[0]["delta_before"], post_intact[0]["delta_after"]],
        "POST_history_omitted_delta": [post_omitted[0]["delta_before"], post_omitted[0]["delta_after"]],
        "POST_first_common_use_intact_vs_omit_commands": [post_intact[1]["reader"]["command"], post_omitted[1]["reader"]["command"]],
        "POST_first_common_use_intact_vs_omit_passed": [post_intact[1]["external_job_passed"], post_omitted[1]["external_job_passed"]],
        "POST_second_common_use_intact_vs_omit_passed": [post_intact[2]["external_job_passed"], post_omitted[2]["external_job_passed"]],
        "CAL8_intact_passed": sum(q["external_job_passed"] for q in cal_left),
        "CAL8_omitted_passed": sum(q["external_job_passed"] for q in cal_right),
        "CAL8_opportunities_each": len(cal_left),
        "CAL8_intact_first_error_delta": [cal_left[0]["delta_before"], cal_left[0]["delta_after"]],
        "CAL8_omitted_first_error_delta": [cal_right[0]["delta_before"], cal_right[0]["delta_after"]],
        "CAL8_second_common_gap8_intact_vs_omit_commands": [cal_left[1]["reader"]["command"], cal_right[1]["reader"]["command"]],
        "CAL8_final_intact_own": cal_left[-1]["own_after"], "CAL8_final_omitted_own": cal_right[-1]["own_after"],
        "CAL8_final_intact_delta": cal_left[-1]["delta_after"], "CAL8_final_omitted_delta": cal_right[-1]["delta_after"],
        "all_context_7_5_and_B_61_19_retained_in_samples": all(q["context_7_5_in_all_samples"] and q["B_private_61_19_in_all_samples"] for t in trials for q in t["rows"])},
      "limits": [
        "POST's first contradictory consequence changes relative reference 3 to 2 and makes the first common gate7 job incorrect; this is a real adverse history effect, not an omitted failure.",
        "The first POST evaluation itself supplies native consequences: MAIN readquires delta3 by its end and its second success is therefore not intact retention of the disturbed reference.",
        "CAL8 changes only the external calibration from7 to8 with an explicit external reset; DEE continues the exact MAIN state atT63813. First error is preserved.",
        "CAL8 native failure return changes delta3 to4; same-age omitted-return control stays delta3. A later new raw pair with the same gap8 yields + versus -, followed by useful gap9/7/8 cases. This supports limited consequence-dependent action improvement.",
        "Return omission removes prepared resources, not a post-formation selective cut. The reader/anatomy/experience schedule remain externally prepared; no learned reader choice, exclusive query policy or R2 general regulation is established.",
        "One paired lineage is not independent statistical replication. A changed arithmetic threshold with these integer observations is not acquisition of an abstract numeric concept.",
        "Raw pairs, clocks and source hashes are exact; sparse temporal coverage and full endpoint checks do not imply complete lineage tracking of every encounter."]}
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"output": str(a.out), "sha256": base.sha(a.out), "new_native_ticks": 0, "summary": result["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
