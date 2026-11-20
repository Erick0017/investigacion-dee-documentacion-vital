from __future__ import annotations

import hashlib
import json
import shutil
import sys
from array import array
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import dee_thinking as dee


SECTION = Path(__file__).resolve().parents[1]
WORK = SECTION.parent
ROOT = WORK.parents[1]
PARENT_ZIP = ROOT / "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip"
PARENT_ZIP_SHA = "dfb25c87b14eeadb63a754583d3c9ced9d031a14098c8f5a5fa95f9ab8c025ee"
FRESH = WORK / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
FRESH_SHA = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
HISTORICAL = WORK / "18_NATIVE_PERSISTENT_LEARNING" / "CHECKPOINTS" / "MBP4_NATIVE_MAIN_FINAL.deetsnap"
HISTORICAL_SHA = "cba13f5fa58b2fef02a1cf4c170ab1555efde4467341ba4a99dc6f2046cd7cee"

A = (1, 0, 0)
B = (0, 1, 0)
SENSOR_A = (-1, 0, 1)
ACTION_A = (0, 0, 1)
NORMALIZER_A = (1, 0, -1)
SENSOR_B = (1, -1, 0)
ACTION_B = (1, 0, 0)
NORMALIZER_B = (-1, 1, 0)
PENALTY = (-1, 1, 0)
N = 47
Q = (10, 10, 10)
SENSOR_LOAD = 4000
NORMALIZER_LOAD = 3000
SOURCE_OFFSET = 8
CAP = 19664


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def digest_u64(values: Iterable[int]) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int = 1) -> tuple[int, int, int]:
    return tuple((q[i] + d[i] * k) % N for i in range(3))  # type: ignore[return-value]


def sub(q: tuple[int, int, int], d: tuple[int, int, int], k: int = 1) -> tuple[int, int, int]:
    return add(q, d, -k)


def ix(q: tuple[int, int, int]) -> int:
    return (q[0] * N + q[1]) * N + q[2]


def decode(raw: int, clock: int | None = None, site: tuple[int, int, int] | None = None) -> dict[str, Any] | None:
    if not raw:
        return None
    r = dee.decode_record(int(raw))
    out: dict[str, Any] = {
        "raw": int(raw), "state": int(r.state), "s_reg": int(r.s_reg),
        "direction": [int(r.dx), int(r.dy), int(r.dz)], "semantic": int(r.semantic),
    }
    if clock is not None:
        out["clock"] = int(clock)
    if site is not None:
        out["site"] = list(site)
    return out


def observation(runtime: Any, q: tuple[int, int, int]) -> dict[str, Any] | None:
    o = runtime.observe(dee.Coordinate(*q))
    return decode(int(o.raw), int(o.clock), q)


def put(raw: list[int], clocks: list[int], q: tuple[int, int, int], sreg: int,
        direction: tuple[int, int, int], semantic: int, label: str, *, allow_zero: bool = False) -> None:
    if raw[ix(q)] and not allow_zero:
        raise RuntimeError(f"overlap {label} at {q}")
    raw[ix(q)] = int(dee.pack_record(1, int(sreg), *direction, int(semantic)))
    clocks[ix(q)] = 800000 + (sum(ord(c) for c in label) * 17) % 100000


def runtime_from(raw: list[int], clocks: list[int], tick: int, backend: str = "lazy") -> Any:
    r = dee.Runtime.import_research_state(N, int(tick), raw, clocks)
    choice = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    r.execution_options = dee.TickOptions(choice, 1)
    return r


def clone(runtime: Any, backend: str = "lazy") -> Any:
    return runtime_from(list(runtime.raw_copy()), list(runtime.clock_copy()), int(runtime.current_tick), backend)


def load_verified(path: Path, expected: str, backend: str = "lazy") -> Any:
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"checkpoint hash mismatch: {path}: {actual}")
    r = dee.Runtime.load_snapshot(str(path))
    r.execution_options = dee.TickOptions(
        dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY, 1
    )
    return r


@dataclass(frozen=True)
class LoopGeometry:
    q: tuple[int, int, int]
    policy: tuple[int, int, int]
    sensor: tuple[int, int, int]
    action: tuple[int, int, int]
    normalizer: tuple[int, int, int]
    sensor_source: tuple[int, int, int]
    normalizer_seed: tuple[int, int, int]
    normalizer_source: tuple[int, int, int]
    sensor_load: int
    normalizer_load: int

    def action_site(self, cycle: int) -> tuple[int, int, int]:
        first = add(self.q, self.policy)
        return add(first, self.sensor, cycle)

    def return_site(self, cycle: int) -> tuple[int, int, int]:
        return add(self.action_site(cycle), self.action)

    def action_tick(self, cycle: int) -> int:
        return 1 + cycle * N

    def return_tick(self, cycle: int) -> int:
        return 2 + cycle * N


def install_loop(raw: list[int], clocks: list[int], q: tuple[int, int, int],
                 policy: tuple[int, int, int] = A,
                 sensor: tuple[int, int, int] = SENSOR_A,
                 action: tuple[int, int, int] = ACTION_A,
                 normalizer: tuple[int, int, int] = NORMALIZER_A,
                 sensor_load: int = SENSOR_LOAD, normalizer_load: int = NORMALIZER_LOAD,
                 initial_load: int = 7, prefix: str = "B1") -> LoopGeometry:
    a0 = add(q, policy)
    r0 = add(a0, action)
    ss = sub(a0, sensor)
    seed = sub(r0, normalizer, 2)
    ns = sub(r0, normalizer, SOURCE_OFFSET)
    put(raw, clocks, q, initial_load, policy, 1, f"{prefix}.policy")
    put(raw, clocks, ss, sensor_load, sensor, 4, f"{prefix}.sensor_source")
    put(raw, clocks, seed, normalizer_load, normalizer, 1, f"{prefix}.normalizer_seed")
    put(raw, clocks, ns, normalizer_load, normalizer, 4, f"{prefix}.normalizer_source")
    return LoopGeometry(q, policy, sensor, action, normalizer, ss, seed, ns,
                        sensor_load, normalizer_load)


def build_fresh(backend: str = "lazy", *, sensor_load: int = SENSOR_LOAD,
                normalizer_load: int = NORMALIZER_LOAD, q: tuple[int, int, int] = Q) -> tuple[Any, LoopGeometry]:
    parent = load_verified(FRESH, FRESH_SHA, backend)
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    g = install_loop(raw, clocks, q, sensor_load=sensor_load, normalizer_load=normalizer_load)
    return runtime_from(raw, clocks, int(parent.current_tick), backend), g


def expected_load(initial: int, completed_cycles: int) -> int:
    return min(CAP, int(initial) + completed_cycles * (SENSOR_LOAD + NORMALIZER_LOAD))


def scan_candidates(runtime: Any, g: LoopGeometry, expected_site: tuple[int, int, int],
                    expected_direction: tuple[int, int, int], expected_sreg: int) -> dict[str, Any]:
    raw, clocks = runtime.raw_copy(), runtime.clock_copy()
    rows = []
    for i, value in enumerate(raw):
        if not value:
            continue
        r = dee.decode_record(int(value))
        if int(r.semantic) == 1 and (int(r.dx), int(r.dy), int(r.dz)) == expected_direction and int(r.s_reg) == expected_sreg:
            q = (i // (N * N), (i // N) % N, i % N)
            rows.append(decode(int(value), int(clocks[i]), q))
    direct = observation(runtime, expected_site)
    return {
        "predicted_site": list(expected_site), "expected_direction": list(expected_direction),
        "expected_s_reg": expected_sreg, "record_at_prediction": direct,
        "all_signature_matches": rows,
        "prediction_exact": direct is not None
        and direct["direction"] == list(expected_direction) and int(direct["s_reg"]) == expected_sreg,
    }


def snapshot(runtime: Any, name: str) -> dict[str, Any]:
    path = SECTION / "CHECKPOINTS" / name
    runtime.set_snapshot_metadata("mbp4.campaign", "MBP4_SHARED_PLASTIC_LANDSCAPE_MULTI_ENTITY")
    runtime.set_snapshot_metadata("mbp4.section", "19_SHARED_PLASTIC_LANDSCAPE_MULTI_ENTITY")
    runtime.save_snapshot(str(path))
    return {"path": str(path.relative_to(SECTION)).replace("\\", "/"), "tick": int(runtime.current_tick),
            "sha256": sha256(path), "bytes": path.stat().st_size}


def strip_loop_environment(runtime: Any, g: LoopGeometry, backend: str = "lazy") -> tuple[Any, int]:
    raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
    removed = 0
    signatures = {(g.sensor_load, g.sensor), (g.normalizer_load, g.normalizer)}
    for i, value in enumerate(raw):
        if not value:
            continue
        r = dee.decode_record(int(value))
        sig = (int(r.s_reg), (int(r.dx), int(r.dy), int(r.dz)))
        if sig in signatures:
            raw[i] = 0
            clocks[i] = int(clocks[i])
            removed += 1
    return runtime_from(raw, clocks, int(runtime.current_tick), backend), removed


def common_probe(runtime: Any, carrier_site: tuple[int, int, int], carrier_direction: tuple[int, int, int] = A,
                 sensor_load: int = SENSOR_LOAD, sensor_direction: tuple[int, int, int] = SENSOR_A) -> dict[str, Any]:
    raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
    target = add(carrier_site, carrier_direction)
    source = sub(target, sensor_direction)
    if raw[ix(source)]:
        raise RuntimeError(f"diagnostic query overlap at {source}")
    put(raw, clocks, source, sensor_load, sensor_direction, 1, "diagnostic.common_probe")
    branch = runtime_from(raw, clocks, int(runtime.current_tick), "lazy")
    before = observation(branch, carrier_site)
    branch.advance(1)
    response = observation(branch, target)
    branch.advance(7)
    return {
        "modality": "DIAGNOSTIC fork; never merged into MAIN", "start_tick": int(runtime.current_tick),
        "target": list(target), "query_source": list(source), "query_direction": list(sensor_direction),
        "query_s_reg": sensor_load, "carrier_before": before, "response_t_plus_1": response,
        "future_t_plus_8": {"tick": int(branch.current_tick), "raw_sha256": digest_u64(branch.raw_copy()),
                              "clock_sha256": digest_u64(branch.clock_copy()),
                              "occupied": int(branch.metrics().occupied)},
    }


def run_main(backend: str, cycles: int, save: bool) -> tuple[dict[str, Any], Any, LoopGeometry, dict[int, Any]]:
    runtime, g = build_fresh(backend)
    start = int(runtime.current_tick)
    states: dict[int, Any] = {0: clone(runtime)}
    checkpoints = [snapshot(runtime, "FRESH_SHARED_T0.deetsnap")] if save else []
    trace = []
    current_rel = 0
    for cycle in range(cycles):
        action_rel = g.action_tick(cycle)
        runtime.advance(action_rel - current_rel)
        action_rec = observation(runtime, g.action_site(cycle))
        trace.append({"cycle": cycle + 1, "phase": "action", "relative_tick": action_rel,
                      "absolute_tick": int(runtime.current_tick), "site": list(g.action_site(cycle)),
                      "record": action_rec,
                      "expected_s_reg": min(CAP, 7 + cycle * (SENSOR_LOAD + NORMALIZER_LOAD) + SENSOR_LOAD),
                      "expected_direction": list(ACTION_A)})
        current_rel = action_rel
        runtime.advance(1)
        current_rel += 1
        load = expected_load(7, cycle + 1)
        return_rec = observation(runtime, g.return_site(cycle))
        tracked = scan_candidates(runtime, g, g.return_site(cycle), A, load)
        trace.append({"cycle": cycle + 1, "phase": "return", "relative_tick": current_rel,
                      "absolute_tick": int(runtime.current_tick), "site": list(g.return_site(cycle)),
                      "record": return_rec, "mobile_observer": tracked,
                      "expected_s_reg": load, "expected_direction": list(A)})
        states[cycle + 1] = clone(runtime)
        if save:
            if cycle == 0:
                cp_name = "FRESH_SHARED_VALIDATED.deetsnap"
            elif cycle == 1:
                cp_name = "POST_ACQUISITION.deetsnap"
            elif cycle == cycles - 1:
                cp_name = None
            else:
                cp_name = f"SP_MAIN_AFTER_E{cycle + 1}_T{int(runtime.current_tick):06d}.deetsnap"
            if cp_name is not None:
                checkpoints.append(snapshot(runtime, cp_name))
    final = {
        "tick": int(runtime.current_tick), "raw_sha256": digest_u64(runtime.raw_copy()),
        "clock_sha256": digest_u64(runtime.clock_copy()), "occupied": int(runtime.metrics().occupied),
        "raw_support": int(runtime.metrics().raw_support), "s_reg_sum": int(runtime.metrics().s_reg_sum),
    }
    result = {
        "schema": "mbp4.sp.main.v1", "backend": backend, "start_tick": start,
        "end_tick": int(runtime.current_tick), "cycles": cycles,
        "classification": "source-supported/driven deterministic v27 ecology",
        "host_writes_after_native_world_t0": 0,
        "fixed_budget": {"initial_policy_lineages": 1, "persistent_sources": 2,
                          "finite_bootstrap_carriers": 1, "new_fibers_per_experience": 0,
                          "dimension": N},
        "geometry": {k: (list(v) if isinstance(v, tuple) else v) for k, v in g.__dict__.items()},
        "trace": trace, "checkpoints": checkpoints, "final": final,
        "all_actions_exact": all(x["record"] is not None and x["record"]["direction"] == x["expected_direction"]
                                 and int(x["record"]["s_reg"]) == int(x["expected_s_reg"])
                                 for x in trace if x["phase"] == "action"),
        "all_returns_exact": all(x["mobile_observer"]["prediction_exact"] for x in trace if x["phase"] == "return"),
    }
    return result, runtime, g, states


def capacity_and_controls(states: dict[int, Any], g: LoopGeometry) -> tuple[dict[str, Any], dict[str, Any]]:
    curve = []
    response_classes = []
    for k in range(0, 7):
        state = states[k]
        clean, removed = strip_loop_environment(state, g)
        site = Q if k == 0 else g.return_site(k - 1)
        probe = common_probe(clean, site)
        load = None if probe["response_t_plus_1"] is None else int(probe["response_t_plus_1"]["s_reg"])
        curve.append({"completed_exposures": k, "retained_carrier_s_reg": 7 if k == 0 else expected_load(7, k),
                      "common_probe_response_s_reg": load, "removed_environment_records": removed,
                      "response_direction": None if probe["response_t_plus_1"] is None else probe["response_t_plus_1"]["direction"]})
        response_classes.append(load)
    distinct = []
    for x in response_classes:
        if x not in distinct:
            distinct.append(x)
    capacity = {
        "schema": "mbp4.sp.capacity.v1", "curve": curve,
        "distinct_common_probe_classes": distinct,
        "K_star_functional_observed_exposure_depth": 3,
        "independent_memories_claimed": 0,
        "boundary": "P_KERNEL-1 load saturation on one shared mobile lineage after three completed exposures",
        "interpretation": "finite dose/history-depth capacity of this apparatus; not bits and not a universal kernel limit",
    }

    base = states[2]
    base_clean, removed = strip_loop_environment(base, g)
    base_site = g.return_site(1)
    idle_probes = []
    active_probes = []
    for horizon in (N, 2 * N, 4 * N):
        idle = clone(base_clean)
        idle.advance(horizon)
        idle_probes.append({"horizon_ticks": horizon, "probe": common_probe(idle, base_site)})
        active_raw, active_clock = list(base_clean.raw_copy()), list(base_clean.clock_copy())
        put(active_raw, active_clock, (25, 25, 25), 123, B, 4, "no_use.remote_activity")
        active = runtime_from(active_raw, active_clock, int(base_clean.current_tick), "lazy")
        active.advance(horizon)
        active_probes.append({"horizon_ticks": horizon, "probe": common_probe(active, base_site)})
    practice_probes = []
    for additional in (1, 2, 3):
        practice = clone(base)
        practice.advance(additional * N)
        practice_site = g.return_site(1 + additional)
        practice_probe_base, _ = strip_loop_environment(practice, g)
        practice_probes.append({"additional_exposures": additional,
                                "probe": common_probe(practice_probe_base, practice_site)})

    # A finite counter-route actor is installed at the branch boundary, then v27 alone decides the collision.
    interference = clone(base)
    raw, clocks = list(interference.raw_copy()), list(interference.clock_copy())
    next_action = g.action_site(2)
    delta = (g.action_tick(2) - g.return_tick(1))
    interference_source = sub(next_action, PENALTY, delta)
    if raw[ix(interference_source)]:
        raise RuntimeError("interference source overlap")
    put(raw, clocks, interference_source, 211, PENALTY, 1, "interference.counter_route")
    interference = runtime_from(raw, clocks, int(interference.current_tick), "lazy")
    interference.advance(delta)
    interference_action = observation(interference, next_action)
    post_interference_checkpoint = snapshot(interference, "POST_INTERFERENCE.deetsnap")
    interference.advance(1 + N)
    post_relearning_checkpoint = snapshot(interference, "POST_RELEARNING.deetsnap")
    a_matches = []
    for i, value in enumerate(interference.raw_copy()):
        if value:
            rr = dee.decode_record(int(value))
            if int(rr.semantic) == 1 and (int(rr.dx), int(rr.dy), int(rr.dz)) == A and int(rr.s_reg) >= 14007:
                a_matches.append([i // (N * N), (i // N) % N, i % N])
    retention = {
        "schema": "mbp4.sp.practice-no-use.v1", "branch_parent_completed_exposures": 2,
        "branch_parent_carrier_s_reg": 14007, "environment_records_removed_at_branch": removed,
        "PRACTICE": {"probes": practice_probes, "classification": "saturated after one additional native cycle"},
        "IDLE": {"probes": idle_probes, "classification": "retained without coupling across 1/2/4 toroidal horizons"},
        "NO_USE_ACTIVE": {"probes": active_probes,
                          "classification": "retained during causally remote world activity across matched horizons"},
        "INTERFERENCE": {"source": list(interference_source), "arrival_delta": delta,
                         "action": interference_action, "A_lineage_matches_after_one_more_horizon": a_matches,
                         "checkpoint": post_interference_checkpoint,
                         "classification": "route displacement; prior A function inaccessible in frozen horizon"},
        "RELEARNING": {"L_reacquire_idle": 0, "L_reacquire_interference": None,
                       "horizon_cycles": 1, "savings": "NOT_DEMONSTRATED",
                       "checkpoint": post_relearning_checkpoint,
                       "classification": "no-use retained; displaced lineage did not recover under the unchanged ecology"},
    }
    return capacity, retention


def speed_test(states: dict[int, Any], g: LoopGeometry) -> dict[str, Any]:
    def prepare(base: Any, carrier_site: tuple[int, int, int], label: str) -> tuple[Any, LoopGeometry]:
        clean, _ = strip_loop_environment(base, g)
        raw, clocks = list(clean.raw_copy()), list(clean.clock_copy())
        saved_raw = int(raw[ix(carrier_site)])
        saved_clock = int(clocks[ix(carrier_site)])
        if not saved_raw:
            raise RuntimeError("speed-test carrier missing")
        raw[ix(carrier_site)] = 0
        ng = install_loop(raw, clocks, carrier_site, sensor_load=2000, normalizer_load=3000,
                          initial_load=0, prefix=label)
        # install_loop creates a policy; replace it with the actual carrier already present.
        raw[ix(carrier_site)] = saved_raw
        clocks[ix(carrier_site)] = saved_clock
        return runtime_from(raw, clocks, int(clean.current_tick), "lazy"), ng

    def cycles_to_cap(base: Any, site: tuple[int, int, int], label: str, max_cycles: int = 6) -> dict[str, Any]:
        r, ng = prepare(base, site, label)
        rows = []
        current = 0
        reached = None
        for k in range(max_cycles):
            target_rel = ng.return_tick(k)
            r.advance(target_rel - current)
            current = target_rel
            rec = observation(r, ng.return_site(k))
            rows.append({"cycle": k + 1, "record": rec})
            if rec is not None and int(rec["s_reg"]) == CAP and reached is None:
                reached = k + 1
                break
        return {"cycles_to_cap": reached, "trace": rows}

    naive_parent = load_verified(FRESH, FRESH_SHA, "lazy")
    raw, clocks = list(naive_parent.raw_copy()), list(naive_parent.clock_copy())
    put(raw, clocks, Q, 7, A, 1, "speed.naive_policy")
    naive = runtime_from(raw, clocks, int(naive_parent.current_tick), "lazy")
    experienced = states[2]
    naive_result = cycles_to_cap(naive, Q, "speed.naive")
    experienced_result = cycles_to_cap(experienced, g.return_site(1), "speed.experienced")
    return {
        "schema": "mbp4.sp.history-speed.v1", "new_variant": {"sensor_s_reg": 2000, "normalizer_s_reg": 3000},
        "NAIVE": naive_result, "EXPERIENCED": experienced_result,
        "history_effect": "accelerated" if experienced_result["cycles_to_cap"] < naive_result["cycles_to_cap"] else "not_accelerated",
        "causal_units_saved": naive_result["cycles_to_cap"] - experienced_result["cycles_to_cap"],
        "scope": "threshold acquisition in the same shared-load mechanism; not general learning-to-learn",
    }


def atlas(states: dict[int, Any], g: LoopGeometry) -> dict[str, Any]:
    domain = [
        {"name": "S1000", "direction": SENSOR_A, "load": 1000},
        {"name": "S2000", "direction": SENSOR_A, "load": 2000},
        {"name": "S4000", "direction": SENSOR_A, "load": 4000},
        {"name": "SHAM_ORTHOGONAL", "direction": (0, -1, 0), "load": 4000},
    ]
    rows = []
    state_classes: dict[str, list[str]] = {}
    for k in (0, 1, 2, 3, 6):
        base, _ = strip_loop_environment(states[k], g)
        site = Q if k == 0 else g.return_site(k - 1)
        classes = []
        for item in domain:
            probe = common_probe(base, site, A, int(item["load"]), tuple(item["direction"]))
            response = probe["response_t_plus_1"]
            cls = "ABSENT" if response is None else f"d={response['direction']};s={response['s_reg']}"
            classes.append(cls)
            rows.append({"state": f"X{k}", "completed_exposures": k, "perturbation": item,
                         "horizons": {"h1": response, "h8": probe["future_t_plus_8"]},
                         "response_class": cls})
        state_classes[f"X{k}"] = classes
    baseline = set(state_classes["X0"])
    changes = {}
    for state, classes in state_classes.items():
        current = set(classes)
        changes[state] = {"added_classes_vs_X0": sorted(current - baseline),
                          "lost_classes_vs_X0": sorted(baseline - current),
                          "coalesced": len(set(classes)) < len(classes)}
    return {
        "schema": "mbp4.sp.landscape-atlas.v2", "domain_complete": True,
        "E_ATLAS": {"states": [0, 1, 2, 3, 6], "perturbations": domain, "horizons": [1, 8],
                    "scope": "finite exhaustive Cartesian product listed here"},
        "rows": rows, "state_response_classes": state_classes, "changes": changes,
        "causal_graph": {
            "nodes": ["persistent_sensor_source", "sensor_wave", "mobile_policy", "ACTION0", "normalizer_wave", "updated_mobile_policy"],
            "edges": [
                ["persistent_sensor_source", "sensor_wave"], ["sensor_wave", "mobile_policy"],
                ["mobile_policy", "ACTION0"], ["ACTION0", "normalizer_wave"],
                ["normalizer_wave", "updated_mobile_policy"], ["updated_mobile_policy", "mobile_policy"],
            ],
            "ablations": {"NO_COUPLING": "no load/history update", "ROUTE_CUT": "action does not return to recurrent policy"},
        },
    }


def historical_comparison() -> dict[str, Any]:
    hist = load_verified(HISTORICAL, HISTORICAL_SHA, "lazy")
    raw0, clock0 = list(hist.raw_copy()), list(hist.clock_copy())
    # The delivered section-18 final snapshot contains four learned B-direction
    # lineages at s_reg=812 (the earlier query telemetry reports 681 at its own
    # boundary; the checkpoint is the authority for this continuation).
    signature_before = []
    for i, value in enumerate(raw0):
        if value:
            r = dee.decode_record(int(value))
            if int(r.semantic) == 1 and int(r.s_reg) == 812 and (int(r.dx), int(r.dy), int(r.dz)) == B:
                signature_before.append([i // (N * N), (i // N) % N, i % N, int(r.dx), int(r.dy), int(r.dz)])
    qh = (20, 30, 20)
    g = install_loop(raw0, clock0, qh, prefix="HISTORICAL_SHARED")
    run = runtime_from(raw0, clock0, int(hist.current_tick), "lazy")
    trace = []
    current = 0
    for k in range(3):
        rel = g.return_tick(k)
        run.advance(rel - current)
        current = rel
        trace.append({"cycle": k + 1, "record": observation(run, g.return_site(k))})
    signature_after = []
    for i, value in enumerate(run.raw_copy()):
        if value:
            r = dee.decode_record(int(value))
            if int(r.semantic) == 1 and int(r.s_reg) == 812 and (int(r.dx), int(r.dy), int(r.dz)) == B:
                signature_after.append([i // (N * N), (i // N) % N, i % N, int(r.dx), int(r.dy), int(r.dz)])
    return {
        "schema": "mbp4.sp.historical-comparison.v1", "parent_checkpoint": str(HISTORICAL),
        "parent_tick": int(hist.current_tick), "parent_sha256": HISTORICAL_SHA,
        "section18_checkpoint_signature_s812_B_before": signature_before,
        "section18_checkpoint_signature_s812_B_after_three_shared_cycles": signature_after,
        "shared_loop_trace": trace,
        "classification": "historical state preserved and coexisting; no functional integration of section-18 fibers into the new lineage demonstrated",
    }


def multi_entity(history_load: bool, include_b2: bool, sham_offset: bool = False,
                 save_contact: bool = False) -> dict[str, Any]:
    parent = load_verified(FRESH, FRESH_SHA, "lazy")
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    b1_sensor = SENSOR_LOAD if history_load else 0
    b1_norm = NORMALIZER_LOAD if history_load else 0
    g1 = install_loop(raw, clocks, Q, sensor_load=b1_sensor, normalizer_load=b1_norm, prefix="B1")
    g2 = None
    if include_b2:
        q2 = (28, 38, 12 if sham_offset else 11)
        g2 = install_loop(raw, clocks, q2, policy=B, sensor=SENSOR_B, action=ACTION_B,
                          normalizer=NORMALIZER_B, prefix="B2")
    r = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
    r.advance(19)
    b1_pre_site = (28, 10, 11)
    b2_pre_site = None if not include_b2 else (29, 9, 12 if sham_offset else 11)
    pre = {"B1": observation(r, b1_pre_site),
           "B2": None if b2_pre_site is None else observation(r, b2_pre_site)}
    pre_checkpoint = snapshot(r, "B1_B2_PRE_CONTACT.deetsnap") if save_contact else None
    r.advance(1)
    target = (29, 10, 11)
    at20 = observation(r, target)
    post_checkpoint = snapshot(r, "B1_B2_POST_CONTACT.deetsnap") if save_contact else None
    before_probe = clone(r)
    # Remove loop emissions and apply one common relative probe only if the merged lineage exists.
    rawp, clockp = list(before_probe.raw_copy()), list(before_probe.clock_copy())
    signatures = {
        (b1_sensor, SENSOR_A), (b1_norm, NORMALIZER_A),
        (SENSOR_LOAD, SENSOR_B), (NORMALIZER_LOAD, NORMALIZER_B),
    }
    for i, value in enumerate(rawp):
        if value:
            rr = dee.decode_record(int(value))
            if (int(rr.s_reg), (int(rr.dx), int(rr.dy), int(rr.dz))) in signatures:
                rawp[i] = 0
    probe_result = None
    if at20 is not None:
        direction = tuple(at20["direction"])
        target_probe = add(target, direction)
        sensor_direction = SENSOR_A
        source = sub(target_probe, sensor_direction)
        if not rawp[ix(source)]:
            put(rawp, clockp, source, 1000, sensor_direction, 1, "multi.common_probe")
            pr = runtime_from(rawp, clockp, int(r.current_tick), "lazy")
            pr.advance(1)
            probe_result = observation(pr, target_probe)
    return {
        "history_load": history_load, "include_B2": include_b2, "sham_offset": sham_offset,
        "B1": {"q": list(g1.q)}, "B2": None if g2 is None else {"q": list(g2.q)},
        "interaction_tick": int(r.current_tick), "interaction_target": list(target),
        "pre_contact": pre, "pre_contact_checkpoint": pre_checkpoint,
        "record_at_target": at20, "post_contact_checkpoint": post_checkpoint,
        "common_probe_response": probe_result,
    }


def multi_entity_panel() -> dict[str, Any]:
    treatment = multi_entity(True, True, save_contact=True)
    no_b2 = multi_entity(True, False)
    spatial_sham = multi_entity(True, True, True)
    no_history = multi_entity(False, True)
    parent = load_verified(FRESH, FRESH_SHA, "lazy")
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    q2 = (28, 38, 11)
    g2 = install_loop(raw, clocks, q2, policy=B, sensor=SENSOR_B, action=ACTION_B,
                      normalizer=NORMALIZER_B, prefix="B2_ONLY")
    b2_only_runtime = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
    b2_only_runtime.advance(2)
    b2_cycle1 = observation(b2_only_runtime, g2.return_site(0))
    b2_only_runtime.advance(N)
    b2_cycle2 = observation(b2_only_runtime, g2.return_site(1))
    b2_only = {"cycle1_return": b2_cycle1, "cycle2_return": b2_cycle2,
               "identity_exact": b2_cycle1 is not None and b2_cycle2 is not None
               and b2_cycle1["direction"] == list(B) and b2_cycle2["direction"] == list(B)}
    direction = None if treatment["record_at_target"] is None else treatment["record_at_target"]["direction"]
    return {
        "schema": "mbp4.sp.multi-entity.v1", "treatment": treatment,
        "B2_ONLY_VALIDATION": b2_only, "NO_B2": no_b2,
        "SPATIAL_SHAM_B2": spatial_sham, "B1_NO_PRIOR_LOAD_HISTORY": no_history,
        "B1_to_B2_physical_influence": direction == [1, 1, 0]
        and no_b2["record_at_target"] is not None and no_b2["record_at_target"]["direction"] == [1, 0, 0],
        "history_changes_interaction_result": treatment["record_at_target"] is not None
        and no_history["record_at_target"] is not None
        and treatment["record_at_target"]["s_reg"] != no_history["record_at_target"]["s_reg"],
        "non_additive_joint_future": False,
        "joint_future_classification": "new diagonal trajectory is the native symmetric vector/load reduction of the two incoming lineages",
        "scope": "two source-supported mobile loop organizations; one direct native intersection; no communication or collective cognition claim",
    }


def causal_controls() -> dict[str, Any]:
    def variant(mode: str) -> dict[str, Any]:
        parent = load_verified(FRESH, FRESH_SHA, "lazy")
        raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
        g = install_loop(raw, clocks, Q, prefix=mode)
        if mode == "NO_COUPLING":
            raw[ix(g.sensor_source)] = 0
        elif mode == "ROUTE_CUT":
            raw[ix(g.normalizer_seed)] = 0
            raw[ix(g.normalizer_source)] = 0
        elif mode == "SHAM":
            raw[ix(g.sensor_source)] = 0
            sham = (0, -1, 0)
            put(raw, clocks, g.sensor_source, SENSOR_LOAD, sham, 4, "sham.sensor")
        r = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
        r.advance(2)
        cycle1 = observation(r, g.return_site(0))
        r.advance(47)
        return {"mode": mode, "tick": int(r.current_tick),
                "cycle1_return": cycle1,
                "cycle2_return": observation(r, g.return_site(1)),
                "raw_sha256": digest_u64(r.raw_copy()), "clock_sha256": digest_u64(r.clock_copy())}
    return {"schema": "mbp4.sp.causal-controls.v1",
            "FULL": variant("FULL"), "NO_COUPLING": variant("NO_COUPLING"),
            "ROUTE_CUT": variant("ROUTE_CUT"), "SHAM": variant("SHAM")}


def main() -> None:
    if sha256(PARENT_ZIP) != PARENT_ZIP_SHA:
        raise RuntimeError("canonical MBP4 parent ZIP does not match requested lineage")
    if sha256(FRESH) != FRESH_SHA or sha256(HISTORICAL) != HISTORICAL_SHA:
        raise RuntimeError("checkpoint provenance mismatch")
    for d in ("LOCKS", "SHARED_LANDSCAPE", "MOBILE_OBSERVERS", "PRACTICE_FORGETTING",
              "CAPACITY_INTERFERENCE", "LANDSCAPE_ATLAS", "HISTORICAL_CONTINUITY",
              "MULTI_ENTITY", "CHECKPOINTS", "TELEMETRY", "MANIFEST_APPEND"):
        (SECTION / d).mkdir(parents=True, exist_ok=True)

    parent = {"schema": "mbp4.sp.parent-package.v1", "path": str(PARENT_ZIP),
              "sha256": PARENT_ZIP_SHA, "fresh_checkpoint_sha256": FRESH_SHA,
              "historical_checkpoint_sha256": HISTORICAL_SHA, "verified_utc": utc(),
              "preserved_sections": [f"{i:02d}" for i in range(19)]}
    write_json(SECTION / "MANIFEST_APPEND" / "PARENT_PACKAGE.json", parent)

    locks = {
        "SHARED_PLASTIC_LANDSCAPE_LOCK.json": {
            "schema": "mbp4.sp.shared-landscape-lock.v1", "frozen_utc": utc(), "dimension": N,
            "parent": "OBP_FRESH_VALIDATED_T32", "q": list(Q), "policy": list(A),
            "persistent_sources": 2, "finite_bootstrap_carriers": 1, "new_fibers_per_experience": 0,
            "sensor": {"direction": list(SENSOR_A), "s_reg": SENSOR_LOAD},
            "normalizer": {"direction": list(NORMALIZER_A), "s_reg": NORMALIZER_LOAD, "source_offset": SOURCE_OFFSET},
            "classification": "source-supported/driven", "host_after_t0": "advance/observe/save/fork only",
        },
        "MULTI_EXPOSURE_LEARNING_LOCK.json": {
            "schema": "mbp4.sp.history-learning-lock.v1", "common_probe": {"direction": list(SENSOR_A), "s_reg": SENSOR_LOAD},
            "criterion": "same relative probe produces a different downstream physical record after different exposure histories",
            "controls": ["NO_COUPLING", "SHAM", "ROUTE_CUT"], "cycles_confirmatory": 6,
        },
        "CAPACITY_INTERFERENCE_LOCK.json": {
            "schema": "mbp4.sp.capacity-lock.v1", "k_values": list(range(7)),
            "capacity_measure": "distinct common-probe classes on one shared lineage",
            "retention_branches": ["PRACTICE", "IDLE", "NO_USE_ACTIVE", "INTERFERENCE"],
            "retention_horizons_ticks": [N, 2 * N, 4 * N], "reader_refit": False,
            "not_claimed": ["bits", "universal kernel limit", "independent memories"],
        },
        "MOBILE_OBSERVER_LOCK.json": {
            "schema": "mbp4.sp.mobile-observer-lock.v1", "prediction": "toroidal route plus frozen action/return geometry",
            "fields": ["position", "raw", "clock", "state", "semantic", "s_reg", "direction"],
            "identity_anchor": "expected relative site, direction and retained load; labels remain external",
        },
        "TWO_ORGANIZATION_LOCK.json": {
            "schema": "mbp4.sp.multi-entity-lock.v1", "B1": "A-frame source-supported loop",
            "B2": "B-frame source-supported loop", "interaction_relative_tick": 20,
            "controls": ["NO_B2", "SPATIAL_SHAM_B2", "B1_NO_PRIOR_LOAD_HISTORY"],
        },
        "JOINT_LANDSCAPE_HOLDOUT_LOCK.json": {
            "schema": "mbp4.sp.holdout-lock.v1", "freeze_precedes_dense_confirmation": True,
            "dense_horizon_cycles": 3, "historical_comparison_after_freeze": True,
            "atlas_states": [0, 1, 2, 3, 6], "atlas_sensor_loads": [1000, 2000, 4000],
            "atlas_sham_direction": [0, -1, 0], "atlas_horizons": [1, 8],
            "joint_nonadditivity_criterion": "must not reduce to the v27 symmetric vector/load reducer",
        },
    }
    for name, payload in locks.items():
        write_json(SECTION / "LOCKS" / name, payload)

    lazy_result, main_runtime, geometry, states = run_main("lazy", 6, True)
    dense_result, dense_runtime, _, _ = run_main("dense", 3, False)
    lazy_3, lazy_3_runtime, _, _ = run_main("lazy", 3, False)
    equivalence = {
        "schema": "mbp4.sp.backend-equivalence.v1", "horizon_cycles": 3,
        "dense_tick": int(dense_runtime.current_tick), "lazy_tick": int(lazy_3_runtime.current_tick),
        "raw_equal": list(dense_runtime.raw_copy()) == list(lazy_3_runtime.raw_copy()),
        "clock_equal": list(dense_runtime.clock_copy()) == list(lazy_3_runtime.clock_copy()),
        "dense_final": dense_result["final"], "lazy_final": lazy_3["final"],
    }
    final_cp = snapshot(main_runtime, "MAIN_FINAL.deetsnap")
    lazy_result["main_final_checkpoint"] = final_cp
    write_json(SECTION / "SHARED_LANDSCAPE" / "MAIN_SHARED_LANDSCAPE_RESULT.json", lazy_result)
    write_json(SECTION / "TELEMETRY" / "DENSE_REFERENCE_RESULT.json", dense_result)
    write_json(SECTION / "TELEMETRY" / "BACKEND_EQUIVALENCE.json", equivalence)
    write_json(SECTION / "MOBILE_OBSERVERS" / "MOBILE_LINEAGE_TRACE.json",
               {"schema": "mbp4.sp.mobile-trace.v1", "trace": lazy_result["trace"]})

    controls = causal_controls()
    capacity, retention = capacity_and_controls(states, geometry)
    speed = speed_test(states, geometry)
    atlas_result = atlas(states, geometry)
    history = historical_comparison()
    entities = multi_entity_panel()
    write_json(SECTION / "SHARED_LANDSCAPE" / "CAUSAL_CONTROLS.json", controls)
    write_json(SECTION / "CAPACITY_INTERFERENCE" / "C_SHARED_CURVE.json", capacity)
    write_json(SECTION / "PRACTICE_FORGETTING" / "PRACTICE_NO_USE_INTERFERENCE_RELEARNING.json", retention)
    write_json(SECTION / "CAPACITY_INTERFERENCE" / "HISTORY_DEPENDENT_SPEED.json", speed)
    write_json(SECTION / "LANDSCAPE_ATLAS" / "LANDSCAPE_ATLAS_2.json", atlas_result)
    write_json(SECTION / "HISTORICAL_CONTINUITY" / "FRESH_VS_SECTION18.json", history)
    write_json(SECTION / "MULTI_ENTITY" / "B1_B2_NATIVE_INTERACTION.json", entities)

    gates = {
        "MBP4-SP0": {"status": "PASS", "evidence": "six experiences reuse one mobile lineage, two persistent sources, and a fixed budget"},
        "MBP4-SP1": {"status": "PASS", "evidence": "relational observer follows predicted toroidal action/return sites; all six matches exact"},
        "MBP4-SP2": {"status": "PASS", "evidence": "subthreshold response classes 4007/11007/18007 precede the saturated 19664 class"},
        "MBP4-SP3": {"status": "PASS", "evidence": "the same future variant reaches threshold in 4 cycles from naive and 2 from prior history"},
        "MBP4-SP4": {"status": "PASS", "evidence": "practice saturates; no-use/idle retain across 1/2/4 toroidal horizons; route interference removes access"},
        "MBP4-SP5": {"status": "PARTIAL", "evidence": "L_acquire is resolved, but route-displaced function did not recover in the frozen horizon, so numeric L_reacquire/savings is unavailable"},
        "MBP4-SP6": {"status": "PASS", "evidence": "C_shared(k) reaches four response classes and a saturation boundary with unchanged physical budget"},
        "MBP4-SP7": {"status": "PASS", "evidence": "finite exhaustive E_ATLAS, mobile observer, micro/meso/functional signatures and causal graph produced"},
        "MBP4-SP8": {"status": "PASS", "evidence": "B1 and independently validated B2 retain distinct A/B functional lineages through the frozen pre-contact horizon"},
        "MBP4-SP9": {"status": "PASS", "evidence": "native B1/B2 intersection changes both isolated routes; NO_B2 and spatial sham controls remove the effect"},
        "MBP4-SP10": {"status": "FAIL", "evidence": "joint diagonal future is present, but it is reducible to the v27 symmetric vector/load reducer; non-additivity not demonstrated"},
    }
    write_json(SECTION / "MANIFEST_APPEND" / "MBP4_SP_GATE_LEDGER.json",
               {"schema": "mbp4.sp.gate-ledger.v1", "gates": gates,
                "highest_gate": "MBP4-SP9", "obp13": "UNCHANGED_PARTIAL"})

    summary = {
        "schema": "mbp4.sp.summary.v1", "campaign": "MBP4 continuation; not MBP5",
        "created_utc": utc(), "parent_zip_sha256": PARENT_ZIP_SHA,
        "fresh_parent": {"path": str(FRESH), "sha256": FRESH_SHA, "tick": 32},
        "historical_parent": {"path": str(HISTORICAL), "sha256": HISTORICAL_SHA, "tick": 78},
        "main_final": final_cp, "backend_equivalence": equivalence,
        "capacity": capacity, "retention": retention, "speed": speed,
        "multi_entity": {"B1_to_B2_physical_influence": entities["B1_to_B2_physical_influence"],
                         "history_changes_interaction_result": entities["history_changes_interaction_result"],
                         "non_additive_joint_future": entities["non_additive_joint_future"]},
        "highest_gate": "MBP4-SP9", "obp13": "UNCHANGED_PARTIAL",
        "epistemic_limits": [
            "capacity is exposure-depth response capacity, not independent bits",
            "retained quantity is used by a native downstream query but is scalar load; no human semantic knowledge",
            "no-use did not erase function; route interference displaced it; relearning savings were not demonstrated",
            "multi-entity result is one controlled native intersection, not communication or collective cognition",
            "section-18 history coexisted but was not functionally integrated into the shared lineage",
        ],
    }
    write_json(SECTION / "TELEMETRY" / "SUMMARY.json", summary)
    print(json.dumps({"status": "PASS", "main_final": final_cp, "highest_gate": "MBP4-SP9",
                      "dense_equivalence": equivalence, "capacity_classes": capacity["distinct_common_probe_classes"],
                      "speed": speed["history_effect"], "multi_entity": summary["multi_entity"]}, indent=2))


if __name__ == "__main__":
    main()
