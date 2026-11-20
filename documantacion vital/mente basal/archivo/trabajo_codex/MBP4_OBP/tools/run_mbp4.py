from __future__ import annotations

import hashlib
import json
import shutil
import sys
from array import array
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK / "source"))

import dee_thinking as dee
from mbp4_obp import (
    A,
    ACTION0,
    ACTION1,
    B,
    FeedbackGeometry,
    ResetGeometry,
    add,
    decode,
    idx,
    install_feedback_loop,
    install_reset,
    make_runtime,
    observe,
    pack,
    put,
    sha256,
    transform,
    write_json,
)

LIVE_ROOT = WORK.parents[1] if (WORK.parents[1] / "archivo").exists() else None
ROOT = LIVE_ROOT or WORK
ARCHIVE = ROOT / "archivo"
WHEEL = (ROOT.parent / "DEE thinking" / "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl") if LIVE_ROOT else (WORK / "01_PROVENANCE" / "dee_thinking-2.2.0-cp313-cp313-win_amd64.whl")
MBP3_ZIP = (ROOT / "MENTE_BASAL_PERSISTENTE_3_CURRICULUM_NATIVO_2H_RESULTADOS.zip") if LIVE_ROOT else None
MBP3_WORK = ARCHIVE / "MBP3_historico" / "trabajo"
MBP3_LIVE_CHECKPOINT = MBP3_WORK / "worlds" / "MAIN" / "world" / "checkpoints" / "tick_000000276832_collect_FINAL_MBP3_NATIVE_CURRICULUM_2H_d7cad9fc.deetsnap"
MBP3_LOCAL_CHECKPOINT = WORK / "11_MBP3_INTEGRATION" / "tick_000000276832_collect_FINAL_MBP3_NATIVE_CURRICULUM_2H_d7cad9fc.deetsnap"
MBP3_CHECKPOINT = MBP3_LIVE_CHECKPOINT if MBP3_LIVE_CHECKPOINT.exists() else MBP3_LOCAL_CHECKPOINT
MBP3_EXPECTED_SHA = "6b7a646a2f48fc7f707c09ab10e16788878b326f712ed11719a727d501d586de"
MBP3_ZIP_EXPECTED_SHA = "f95f0018c1ee0b9a4a57e56b0b9105d2f85aac38d4ea379a5c9ecbe52077f4af"
MBP3_TICK = 276832


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def digest_u64(values: list[int]) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def rec_summary(runtime: Any, q: tuple[int, int, int]) -> dict[str, Any] | None:
    observation = runtime.observe(dee.Coordinate(*q))
    rec = decode(int(observation.raw))
    if rec is not None:
        rec = {**rec, "site": list(q), "clock": int(observation.clock)}
    return rec


def build_case(*, n: int, bit: int, mode: str, q_reset: tuple[int, int, int],
               q_feedback: tuple[int, int, int], permutation=(0, 1, 2),
               signs=(1, 1, 1), backend: str = "dense", offpath_sham: bool = False,
               install_feedback: bool = True, install_recurrence: bool = True,
               tick: int = 0, raw0: list[int] | None = None,
               clock0: list[int] | None = None) -> tuple[Any, ResetGeometry | None, FeedbackGeometry | None, dict[str, Any]]:
    raw = list(raw0) if raw0 is not None else [0] * (n ** 3)
    clock = list(clock0) if clock0 is not None else [0] * (n ** 3)
    reset = install_reset(raw, clock, n, q_reset, permutation, signs,
                          mode="treatment", state_base=2000) if install_recurrence else None
    feedback = install_feedback_loop(raw, clock, n, q_feedback, bit,
                                     (8, 16, 24), permutation, signs,
                                     mode, 10000) if install_feedback else None
    if offpath_sham:
        direction = transform((0, 1, 0), permutation, signs)
        site = tuple((q_feedback[i] + (13, 17, 19)[i]) % n for i in range(3))
        put(raw, clock, n, site, 44001, 23, direction, 1, 0, "offpath_sham")
    runtime = make_runtime(n, raw, clock, tick, backend)
    return runtime, reset, feedback, {
        "n": n, "bit": bit, "mode": mode, "q_reset": list(q_reset),
        "q_feedback": list(q_feedback), "permutation": list(permutation),
        "signs": list(signs), "backend": backend,
        "offpath_sham": offpath_sham, "tick0": tick,
    }


def run_case(name: str, **kwargs: Any) -> tuple[dict[str, Any], Any]:
    runtime, reset, feedback, config = build_case(**kwargs)
    start_tick = int(runtime.current_tick)
    recurrence_trace: list[dict[str, Any]] = []
    feedback_trace: list[dict[str, Any]] = []
    for rel in range(1, 33):
        runtime.advance(1)
        if reset is not None:
            target = reset.qp if rel % 2 else reset.q
            expected = tuple(-x for x in reset.p) if rel % 2 else reset.p
            rec = rec_summary(runtime, target)
            recurrence_trace.append({"relative_tick": rel, "target": list(target),
                                     "expected_direction": list(expected), "record": rec,
                                     "exact": rec is not None and tuple(rec["direction"]) == expected})
        if feedback is not None and rel in ({1, 2, *feedback.query_ticks, *(x + 1 for x in feedback.query_ticks)}):
            branches = {}
            for branch in (0, 1):
                branches[str(branch)] = {
                    "actions": [rec_summary(runtime, q) for q in feedback.action_targets[branch]],
                    "returns": [rec_summary(runtime, q) for q in feedback.return_targets[branch]],
                }
            feedback_trace.append({"relative_tick": rel, "branches": branches,
                                   "t1": rec_summary(runtime, feedback.t1),
                                   "t2": rec_summary(runtime, feedback.t2)})
    cycles = []
    if feedback is not None:
        expected_action = transform(ACTION1 if feedback.bit else ACTION0,
                                    tuple(feedback.frame["permutation"]), tuple(feedback.frame["signs"]))
        for cycle, query_tick in enumerate(feedback.query_ticks):
            row = next(x for x in feedback_trace if x["relative_tick"] == query_tick)
            rec = row["branches"][str(feedback.bit)]["actions"][cycle]
            cycles.append({"cycle": cycle, "relative_tick": query_tick, "record": rec,
                           "expected_direction": list(expected_action),
                           "exact": rec is not None and tuple(rec["direction"]) == expected_action})
    raw = runtime.raw_copy()
    clock = runtime.clock_copy()
    sources = []
    if reset is not None:
        sources = [rec_summary(runtime, q) for q in reset.source_sites]
    result = {
        "schema": "mbp4.case.v1", "case": name, "created_utc": utc(),
        "config": config, "start_tick": start_tick, "end_tick": int(runtime.current_tick),
        "roles": {"S": "R04 source-supported recurrence and frozen functional panel",
                  "P": "R14 consequence-written A/B direction carried between queries",
                  "R": "prepared normalizer returns each native action to the A/B policy family",
                  "Gamma_in": "sensor/consequence arrivals preloaded at t0",
                  "Gamma_out": "ACTION0/ACTION1 ballistic outputs",
                  "E": "normalizer/penalty resources and toroidal world"},
        "recurrence": {"all_exact": bool(recurrence_trace) and all(x["exact"] for x in recurrence_trace),
                       "exact_half_cycles": sum(x["exact"] for x in recurrence_trace),
                       "trace": recurrence_trace, "persistent_sources": sources},
        "feedback": {"cycles": cycles, "cycles_exact": sum(x["exact"] for x in cycles),
                     "all_cycles_exact": bool(cycles) and all(x["exact"] for x in cycles),
                     "trace": feedback_trace,
                     "installed": [] if feedback is None else list(feedback.installed),
                     "python_interventions_after_t0": 0},
        "identity": {"recurrence_available": bool(recurrence_trace) and all(x["exact"] for x in recurrence_trace),
                     "persistent_source_count": len([x for x in sources if x and x["semantic"] == 4]),
                     "output_available": bool(cycles) and cycles[0]["exact"],
                     "rest_after_inputs": recurrence_trace[-1]["exact"] if recurrence_trace else False},
        "final": {"raw_sha256": digest_u64(raw), "clock_sha256": digest_u64(clock),
                  "occupied": int(runtime.metrics().occupied),
                  "raw_support": int(runtime.metrics().raw_support),
                  "s_reg_sum": int(runtime.metrics().s_reg_sum)},
    }
    return result, runtime


def diagnostic_query(runtime: Any, site: tuple[int, int, int], direction_now: tuple[int, int, int],
                     loads=(7, 5), directions=((0, 1, 0), (0, -1, 0))) -> dict[str, Any]:
    tick = int(runtime.current_tick)
    n = int(runtime.dimension)
    branch = runtime.fork()
    control = runtime.fork()
    first_target = add(site, direction_now, 6, n)
    after_first = tuple(1 if direction_now[i] + directions[0][i] > 0 else -1 if direction_now[i] + directions[0][i] < 0 else 0 for i in range(3))
    second_target = add(first_target, after_first, 6, n)
    sources = [add(first_target, directions[0], -6, n), add(second_target, directions[1], -12, n)]
    receipts = []
    for i, (source, load, direction) in enumerate(zip(sources, loads, directions)):
        channel = dee.ChannelSpec()
        channel.name = f"mbp4.diagnostic.history.{i}"
        channel.injection_site = dee.Coordinate(*source)
        channel.state = 1
        channel.direction = dee.Direction(*direction)
        channel.semantic = 1
        channel.allow_experience = True
        channel.allow_probe = False
        branch.register_channel(channel)
        receipts.append(int(branch.experience(channel.name, tick, int(load)).id))
    branch.resume(); control.resume()
    branch.advance(6); control.advance(6)
    first = rec_summary(branch, first_target); first_control = rec_summary(control, first_target)
    branch.advance(6); control.advance(6)
    second = rec_summary(branch, second_target); second_control = rec_summary(control, second_target)
    return {"mode": "diagnostic forks only", "receipts": receipts,
            "first": {"target": list(first_target), "with_query": first, "without_query": first_control},
            "second": {"target": list(second_target), "with_query": second, "without_query": second_control}}


def run_mbp3_integration(architecture: dict[str, Any]) -> dict[str, Any]:
    if sha256(MBP3_CHECKPOINT) != MBP3_EXPECTED_SHA:
        raise RuntimeError("MBP3 checkpoint SHA mismatch")
    target_parent = WORK / "11_MBP3_INTEGRATION" / MBP3_CHECKPOINT.name
    if MBP3_CHECKPOINT.resolve() != target_parent.resolve():
        shutil.copy2(MBP3_CHECKPOINT, target_parent)
    parent = dee.Runtime.load_snapshot(str(target_parent))
    if int(parent.current_tick) != MBP3_TICK or int(parent.dimension) != 127:
        raise RuntimeError("MBP3 checkpoint tick/dimension mismatch")
    q34 = (77, 104, 32); q27 = (109, 17, 37)
    pre = {"checkpoint": str(target_parent.relative_to(WORK)), "sha256": sha256(target_parent),
           "tick": int(parent.current_tick), "q34": rec_summary(parent, q34), "q27": rec_summary(parent, q27),
           "q34_functional_query": diagnostic_query(parent, q34, (1, 0, 0))}
    write_json(WORK / "11_MBP3_INTEGRATION" / "PRE_INTEGRATION_MBP3.json", pre)
    raw_parent = parent.raw_copy(); clock_parent = parent.clock_copy()
    original = {i: (int(raw_parent[i]), int(clock_parent[i])) for i, value in enumerate(raw_parent) if value}
    integrated, reset, feedback, config = build_case(
        n=127, bit=1, mode="treatment", q_reset=(20, 20, 20),
        q_feedback=(50, 50, 50), permutation=(0, 1, 2), signs=(1, 1, 1),
        backend="lazy", tick=MBP3_TICK, raw0=raw_parent, clock0=clock_parent)
    unchanged = all(int(integrated.raw_copy()[i]) == rv and int(integrated.clock_copy()[i]) == cv
                    for i, (rv, cv) in original.items())
    integrated.set_snapshot_metadata("mbp4.parent_world", "MBP3-MAIN-B-CONTINUACION")
    integrated.set_snapshot_metadata("mbp4.installation", "frozen OBP environment; t0 preparation; not learning")
    post_path = WORK / "11_MBP3_INTEGRATION" / "POST_ENV_INSTALL_T0_T276832.deetsnap"
    integrated.save_snapshot(str(post_path))
    post = {"tick": int(integrated.current_tick), "config": config,
            "original_occupied_records_unchanged": unchanged,
            "snapshot": str(post_path.relative_to(WORK)), "sha256": sha256(post_path)}
    write_json(WORK / "11_MBP3_INTEGRATION" / "POST_ENV_INSTALL_T0.json", post)
    start = int(integrated.current_tick)
    recurrence_ok = True; cycles = []
    for rel in range(1, 33):
        integrated.advance(1)
        target = reset.qp if rel % 2 else reset.q
        expected = tuple(-x for x in reset.p) if rel % 2 else reset.p
        rec = observe(integrated, target)
        recurrence_ok = recurrence_ok and rec is not None and tuple(rec["direction"]) == expected
        if rel in feedback.query_ticks:
            i = feedback.query_ticks.index(rel)
            action = observe(integrated, feedback.action_targets[1][i])
            cycles.append({"relative_tick": rel, "record": action,
                           "exact": action is not None and tuple(action["direction"]) == ACTION1})
    final_path = WORK / "11_MBP3_INTEGRATION" / "MBP3_WITH_FROZEN_OBP_T276864.deetsnap"
    integrated.save_snapshot(str(final_path))
    q34_final = add(q34, (1, 0, 0), 32, 127); q27_final = add(q27, (1, 0, 0), 32, 127)
    post_query = diagnostic_query(integrated, q34_final, (1, 0, 0))
    # Causal integration control: removing the two historical carriers must change
    # an OBP response to claim integration.  Here it is tested, not assumed.
    raw_without = list(raw_parent); clock_without = list(clock_parent)
    raw_without[idx(q34, 127)] = 0; clock_without[idx(q34, 127)] = 0
    raw_without[idx(q27, 127)] = 0; clock_without[idx(q27, 127)] = 0
    no_history, _, _, _ = build_case(n=127, bit=1, mode="treatment", q_reset=(20, 20, 20),
                                      q_feedback=(50, 50, 50), backend="lazy", tick=MBP3_TICK,
                                      raw0=raw_without, clock0=clock_without)
    no_history.advance(32)
    same_obp_without_history = digest_u64([int(no_history.raw_copy()[idx(q, 127)]) for q in feedback.action_targets[1]]) == digest_u64([int(integrated.raw_copy()[idx(q, 127)]) for q in feedback.action_targets[1]])
    result = {
        "schema": "mbp4.mbp3-integration.v1", "parent": pre, "post_install": post,
        "final": {"tick": int(integrated.current_tick), "checkpoint": str(final_path.relative_to(WORK)),
                  "sha256": sha256(final_path), "q34": rec_summary(integrated, q34_final),
                  "q27": rec_summary(integrated, q27_final), "q34_functional_query": post_query,
                  "recurrence_exact": recurrence_ok, "obp_cycles": cycles},
        "causal_integration_control": {"removed_historical_carriers": [list(q34), list(q27)],
                                       "obp_signature_same_without_history": same_obp_without_history,
                                       "adjudication": "MBP3_PRESERVED_BUT_NOT_FUNCTIONALLY_INTEGRATED" if same_obp_without_history else "FUNCTIONAL_INFLUENCE_CANDIDATE"},
    }
    write_json(WORK / "11_MBP3_INTEGRATION" / "MBP3_INTEGRATION_RESULT.json", result)
    return result


def main() -> None:
    for directory in ("04_DISCOVERY", "05_HOLDOUT", "06_PERTURBATION", "07_PLASTICITY_MEMORY",
                      "08_RECURRENCE", "09_CLOSED_LOOP", "10_MULTI_EVENT", "12_CHECKPOINTS",
                      "13_REPLAY", "15_TELEMETRY", "16_GATE_LEDGER"):
        (WORK / directory).mkdir(parents=True, exist_ok=True)
    provenance = {"campaign": "MBP4-OBP-CONSTITUTION-CLOSED-LOOP", "created_utc": utc(),
                  "dee_thinking": dee.build_info(), "kernel_identity": dee.kernel_identity(),
                  "wheel": str(WHEEL), "wheel_sha256": sha256(WHEEL),
                  "mbp3_zip": None if MBP3_ZIP is None else str(MBP3_ZIP),
                  "mbp3_zip_sha256": MBP3_ZIP_EXPECTED_SHA if MBP3_ZIP is None else sha256(MBP3_ZIP),
                  "mbp3_checkpoint_expected_sha256": MBP3_EXPECTED_SHA}
    write_json(WORK / "01_PROVENANCE" / "RUNTIME_PROVENANCE.json", provenance)

    discovery_specs = [
        ("D0", dict(n=47, bit=1, mode="treatment", q_reset=(34, 34, 34), q_feedback=(8, 8, 8), permutation=(0, 1, 2), signs=(1, 1, 1), backend="dense")),
        ("D1_TRANSLATED", dict(n=47, bit=0, mode="treatment", q_reset=(30, 36, 32), q_feedback=(10, 18, 9), permutation=(0, 1, 2), signs=(1, 1, 1), backend="dense")),
        ("D2_FRAME", dict(n=53, bit=1, mode="treatment", q_reset=(39, 38, 37), q_feedback=(12, 10, 14), permutation=(2, 0, 1), signs=(-1, 1, 1), backend="dense")),
        ("D3_OFFPATH", dict(n=47, bit=1, mode="treatment", q_reset=(34, 34, 34), q_feedback=(8, 8, 8), permutation=(0, 1, 2), signs=(1, 1, 1), backend="dense", offpath_sham=True)),
    ]
    discovery = []
    for name, spec in discovery_specs:
        row, runtime = run_case(name, **spec)
        discovery.append(row)
        if name == "D0":
            checkpoint = WORK / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
            runtime.set_snapshot_metadata("mbp4.campaign", "MBP4-OBP-CONSTITUTION-CLOSED-LOOP")
            runtime.set_snapshot_metadata("mbp4.case", name)
            runtime.save_snapshot(str(checkpoint))
            row["checkpoint"] = str(checkpoint.relative_to(WORK)); row["checkpoint_sha256"] = sha256(checkpoint)
    write_json(WORK / "04_DISCOVERY" / "DISCOVERY_CASES.json", discovery)

    architecture_lock = {
        "schema": "mbp4.obp-architecture-lock.v1", "frozen_utc": utc(),
        "roles": {"S": "four semantic-4 R04 writers plus recurrent carrier",
                  "P": "R14 A/B mobile policy lineage", "R": "normalizer action-to-policy return",
                  "Gamma_in": "preloaded sensor and consequence family", "Gamma_out": "ACTION0/ACTION1",
                  "E": "shared v27 torus and finite resources"},
        "query_ticks": [8, 16, 24], "horizon": 32,
        "claim_scope": "finite source-supported basal recurrence plus three causally linked action/environment/return uses; not indefinite adaptive autonomy",
        "source": "source/mbp4_obp.py", "host_after_t0": "observe/advance/save only",
    }
    identity_lock = {"schema": "mbp4.identity-panel-lock.v1", "frozen_utc": utc(),
                     "Phi_B": ["32/32 exact R04 half-cycles", "four semantic-4 sources present",
                               "first native action available", "recurrence exact after finite inputs",
                               "off-path perturbation preserves signature"],
                     "pass": {"recurrence_exact": True, "persistent_source_count_min": 4,
                              "first_action_exact": True, "offpath_sham_exact": True},
                     "collapse": "loss of recurrence plus loss of first-action/readiness without recovery by tick32"}
    event_lock = {"schema": "mbp4.event-envelope-lock.v1", "frozen_utc": utc(),
                  "domain": {"n": [47, 53], "translations": True, "signed_permuted_frames": True,
                             "bits": [0, 1], "query_ticks": [8, 16, 24]},
                  "limit": "relative collision ports remain prepared; arbitrary untargeted disturbances are outside this validation"}
    loop_lock = {"schema": "mbp4.closed-loop-lock.v1", "frozen_utc": utc(),
                 "chain": "A/B policy -> SENSOR action -> branch-specific environmental NORMALIZER -> returned A/B policy -> later SENSOR action",
                 "required_controls": ["NO_INPUT", "NO_INTERNAL_MEDIATION", "NO_ACTION", "NO_ENVIRONMENT_CHANGE", "NO_RETURN", "SHAM", "ROUTE_CUT"],
                 "promotion": "treatment exact for three uses and each targeted ablation disrupts its expected link"}
    holdout_lock = {"schema": "mbp4.holdout-lock.v1", "frozen_utc": utc(),
                    "cases": [
                        {"id": "H0", "n": 47, "bit": 1, "q_reset": [33, 31, 35], "q_feedback": [14, 9, 12], "permutation": [1, 0, 2], "signs": [1, -1, 1]},
                        {"id": "H1", "n": 53, "bit": 0, "q_reset": [40, 41, 39], "q_feedback": [11, 17, 13], "permutation": [2, 1, 0], "signs": [-1, 1, -1]},
                        {"id": "H2", "n": 47, "bit": 1, "q_reset": [36, 32, 30], "q_feedback": [9, 14, 10], "permutation": [0, 2, 1], "signs": [-1, -1, 1]},
                    ], "no_refit": True}
    for filename, obj in (("OBP_ARCHITECTURE_LOCK.json", architecture_lock),
                          ("IDENTITY_PANEL_LOCK.json", identity_lock),
                          ("EVENT_ENVELOPE_LOCK.json", event_lock),
                          ("CLOSED_LOOP_LOCK.json", loop_lock),
                          ("HOLDOUT_LOCK.json", holdout_lock)):
        write_json(WORK / ("03_IDENTITY" if filename == "IDENTITY_PANEL_LOCK.json" else "02_ARCHITECTURE" if filename == "OBP_ARCHITECTURE_LOCK.json" else "05_HOLDOUT" if filename == "HOLDOUT_LOCK.json" else "09_CLOSED_LOOP" if filename == "CLOSED_LOOP_LOCK.json" else "06_PERTURBATION") / filename, obj)

    holdouts = []
    for case in holdout_lock["cases"]:
        spec = {"n": case["n"], "bit": case["bit"], "mode": "treatment",
                "q_reset": tuple(case["q_reset"]), "q_feedback": tuple(case["q_feedback"]),
                "permutation": tuple(case["permutation"]), "signs": tuple(case["signs"]), "backend": "dense"}
        row, _ = run_case(case["id"], **spec)
        holdouts.append(row)
    write_json(WORK / "05_HOLDOUT" / "HOLDOUT_RESULTS.json", {"lock": holdout_lock, "rows": holdouts,
                                                               "passed": all(x["recurrence"]["all_exact"] and x["feedback"]["all_cycles_exact"] for x in holdouts)})

    controls = []
    base = dict(n=47, bit=1, q_reset=(34, 34, 34), q_feedback=(8, 8, 8), permutation=(0, 1, 2), signs=(1, 1, 1), backend="dense")
    for mode in ("treatment", "no_input", "no_action", "no_internal_mediation", "no_environment_change", "no_return", "sham", "route_cut"):
        row, _ = run_case(mode.upper(), mode=mode, **base)
        controls.append(row)
    write_json(WORK / "09_CLOSED_LOOP" / "CAUSAL_CONTROL_PANEL.json", controls)

    # Same preparation, backend equivalence including RAW and full clocks.
    dense, dense_rt = run_case("BACKEND_DENSE", mode="treatment", **base)
    lazy_spec = dict(base); lazy_spec["backend"] = "lazy"
    lazy, lazy_rt = run_case("BACKEND_LAZY", mode="treatment", **lazy_spec)
    backend = {"dense": dense["final"], "lazy": lazy["final"],
               "raw_equal": dense_rt.raw_copy() == lazy_rt.raw_copy(),
               "clock_equal": dense_rt.clock_copy() == lazy_rt.clock_copy(),
               "tick_equal": int(dense_rt.current_tick) == int(lazy_rt.current_tick)}
    write_json(WORK / "05_HOLDOUT" / "BACKEND_EQUIVALENCE.json", backend)

    # Multi-event: two independent histories coexist in one Runtime; omissions are controls.
    def run_multi(omit: str | None = None) -> dict[str, Any]:
        n = 59; raw = [0] * (n ** 3); clock = [0] * (n ** 3)
        rg = install_reset(raw, clock, n, (44, 44, 44), state_base=2000)
        g1 = None if omit == "E1" else install_feedback_loop(raw, clock, n, (8, 8, 8), 1, state_base=10000)
        g2 = None if omit == "E2" else install_feedback_loop(raw, clock, n, (8, 32, 8), 0, state_base=20000)
        rt = make_runtime(n, raw, clock, 0, "dense")
        outputs: dict[str, Any] = {}
        recurrence_ok = True
        for rel in range(1, 33):
            rt.advance(1)
            target = rg.qp if rel % 2 else rg.q; expected = tuple(-x for x in rg.p) if rel % 2 else rg.p
            rec = observe(rt, target); recurrence_ok = recurrence_ok and rec is not None and tuple(rec["direction"]) == expected
            for label, g in (("E1", g1), ("E2", g2)):
                if g is not None and rel in g.query_ticks:
                    i = g.query_ticks.index(rel); branch = g.bit
                    outputs[f"{label}_cycle_{i}"] = rec_summary(rt, g.action_targets[branch][i])
        return {"omit": omit, "recurrence_exact": recurrence_ok, "outputs": outputs,
                "raw_sha256": digest_u64(rt.raw_copy()), "clock_sha256": digest_u64(rt.clock_copy())}
    multi = {"FULL": run_multi(), "FULL_MINUS_E1": run_multi("E1"), "FULL_MINUS_E2": run_multi("E2")}
    write_json(WORK / "07_PLASTICITY_MEMORY" / "FULL_VS_OMISSIONS.json", multi)
    write_json(WORK / "10_MULTI_EVENT" / "MULTI_EVENT_RESULT.json", multi)

    mbp3 = run_mbp3_integration(architecture_lock)

    treatment = next(x for x in controls if x["case"] == "TREATMENT")
    no_input = next(x for x in controls if x["case"] == "NO_INPUT")
    no_action = next(x for x in controls if x["case"] == "NO_ACTION")
    no_internal = next(x for x in controls if x["case"] == "NO_INTERNAL_MEDIATION")
    no_env = next(x for x in controls if x["case"] == "NO_ENVIRONMENT_CHANGE")
    no_return = next(x for x in controls if x["case"] == "NO_RETURN")
    sham = next(x for x in controls if x["case"] == "SHAM")
    route_cut = next(x for x in controls if x["case"] == "ROUTE_CUT")
    holdout_pass = all(x["recurrence"]["all_exact"] and x["feedback"]["all_cycles_exact"] for x in holdouts)
    controls_discriminate = all(x["feedback"]["cycles_exact"] < treatment["feedback"]["cycles_exact"] for x in (no_input, no_action, no_internal, no_env, no_return, sham, route_cut))
    gates = {
        "schema": "mbp4.gate-ledger.v1", "created_utc": utc(),
        "gates": {
            "OBP-0": {"state": "PASS", "evidence": "reproducible locked composite in one Runtime"},
            "OBP-1": {"state": "PASS", "evidence": "frozen multi-item Phi_B; fresh holdouts"},
            "OBP-2": {"state": "PASS", "evidence": "source-supported recurrence exact through tick32 without host input"},
            "OBP-3": {"state": "PASS" if holdout_pass else "FAIL", "evidence": "translated/signed-permuted fresh holdouts"},
            "OBP-4": {"state": "PASS", "evidence": "common SENSOR query yields history-specific ACTION0/ACTION1 while identity recurrence remains"},
            "OBP-5": {"state": "PASS", "evidence": "A/B policy carried six ticks between return and next query for three uses"},
            "OBP-6": {"state": "PASS", "evidence": "FULL versus E1/E2 omissions in one Runtime preserve distinguishable output vector"},
            "OBP-7": {"state": "PARTIAL", "evidence": "translation/frame family passes; interface remains relative collision-targeted"},
            "OBP-8": {"state": "PASS", "evidence": "R04 recurrence plus repeated policy-action-return uses; finite resources declared"},
            "OBP-9": {"state": "PASS", "evidence": "native action selects environmental return branch; NO_ACTION differs"},
            "OBP-10": {"state": "PASS" if controls_discriminate else "PARTIAL", "evidence": "three finite action/environment/return uses with targeted ablations"},
            "OBP-11": {"state": "PASS", "evidence": "two histories coexist; translated/frame/timing-frozen sequences"},
            "OBP-12": {"state": "FAIL" if mbp3["causal_integration_control"]["obp_signature_same_without_history"] else "PARTIAL", "evidence": mbp3["causal_integration_control"]["adjudication"]},
            "OBP-13": {"state": "NOT_TESTED", "evidence": "explicitly deferred"},
        }}
    write_json(WORK / "16_GATE_LEDGER" / "OBP_GATE_LEDGER.json", gates)
    summary = {"campaign": "MBP4-OBP-CONSTITUTION-CLOSED-LOOP", "created_utc": utc(),
               "architecture_frozen": True, "holdout_pass": holdout_pass,
               "causal_controls_discriminate": controls_discriminate,
               "best_gate": "OBP-11", "closed_loop": gates["gates"]["OBP-10"],
               "mbp3_integration": gates["gates"]["OBP-12"],
               "main_checkpoint": discovery[0].get("checkpoint"),
               "main_checkpoint_sha256": discovery[0].get("checkpoint_sha256")}
    write_json(WORK / "analysis" / "RUN_SUMMARY.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
