from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
PARENT_ZIP_SHA = "d39c260e20a5a3bfe9775afc7b31031a36293df095b9adec40518ad4d57aaab6"
FRESH = WORK / "12_CHECKPOINTS" / "OBP_FRESH_VALIDATED_T32.deetsnap"
FRESH_SHA = "cd09a4d94f72e00d9a5163c8dfd1d62e1528f1d146e4cb44ae23d261b3da09e6"
PRE_CONTACT = WORK / "20_MATERIALIZED_ENTITIES_NATIVE_INTERACTION" / "CHECKPOINTS" / "B1_B2_PRE_CONTACT.deetsnap"
PRE_CONTACT_SHA = "ce5621203d2c972c60cb4eddca9a22810e41594fc013b768a85aaa3e7691bec4"

CAMPAIGN = "MBP4-INTEGRATED-MIND-GENEALOGY-GENERATIVE-HABITAT"
N = 47
CAP = 19664
A = (1, 0, 0)
B = (0, 1, 0)
C = (0, 0, 1)
SENSOR_A = (-1, 0, 1)
ACTION_A = (0, 0, 1)
NORMALIZER_A = (1, 0, -1)
SENSOR_B = (1, -1, 0)
ACTION_B = (1, 0, 0)
NORMALIZER_B = (-1, 1, 0)
SENSOR_C = (1, 0, -1)
ACTION_C = (1, 0, 0)
NORMALIZER_C = (-1, 0, 1)
SOURCE_OFFSET = 8
SENSOR_LOAD = 4000
NORMALIZER_LOAD = 3000
T_REF = 49
HORIZONS = (4 * T_REF, 16 * T_REF, 64 * T_REF)

TOTAL_TICKS = 0


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


def add(q: tuple[int, int, int], d: tuple[int, int, int], k: int = 1,
        n: int = N) -> tuple[int, int, int]:
    return tuple((q[i] + d[i] * k) % n for i in range(3))  # type: ignore[return-value]


def translate(q: tuple[int, int, int], delta: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((q[i] + delta[i]) % N for i in range(3))  # type: ignore[return-value]


def ix(q: tuple[int, int, int], n: int = N) -> int:
    return (q[0] * n + q[1]) * n + q[2]


def decode(value: int, clock: int | None = None,
           site: tuple[int, int, int] | None = None) -> dict[str, Any] | None:
    if not value:
        return None
    rec = dee.decode_record(int(value))
    out: dict[str, Any] = {
        "raw": int(value), "state": int(rec.state), "s_reg": int(rec.s_reg),
        "direction": [int(rec.dx), int(rec.dy), int(rec.dz)],
        "semantic": int(rec.semantic),
    }
    if clock is not None:
        out["clock"] = int(clock)
    if site is not None:
        out["site"] = list(site)
    return out


def observe(runtime: Any, q: tuple[int, int, int]) -> dict[str, Any] | None:
    item = runtime.observe(dee.Coordinate(*q))
    return decode(int(item.raw), int(item.clock), q)


def matches_lineage_phase(record: dict[str, Any] | None,
                          expected_direction: tuple[int, int, int]) -> bool:
    """Frozen, passive event reader; rejects unrelated matter at the predicted site."""
    return bool(
        record is not None
        and int(record["semantic"]) == 1
        and tuple(int(x) for x in record["direction"]) == expected_direction
    )


class MutationAudit:
    def __init__(self) -> None:
        self.pre_t0_writes = 0
        self.post_t0_writes = 0
        self.frozen = False

    def write(self) -> None:
        if self.frozen:
            self.post_t0_writes += 1
            raise RuntimeError("host mutation attempted after T0")
        self.pre_t0_writes += 1


def put(raw: list[int], clocks: list[int], q: tuple[int, int, int], state: int,
        sreg: int, direction: tuple[int, int, int], semantic: int,
        clock_value: int, label: str, audit: MutationAudit) -> None:
    audit.write()
    i = ix(q)
    if raw[i]:
        raise RuntimeError(f"preparation overlap {label!r} at {q}")
    raw[i] = int(dee.pack_record(int(state), int(sreg), *direction, int(semantic)))
    clocks[i] = int(clock_value) & ((1 << 64) - 1)


def runtime_from(raw: list[int], clocks: list[int], tick: int,
                 backend: str = "lazy") -> Any:
    runtime = dee.Runtime.import_research_state(N, int(tick), raw, clocks)
    selected = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    runtime.execution_options = dee.TickOptions(selected, 1)
    return runtime


def load_fresh(backend: str = "lazy") -> Any:
    if sha256(FRESH) != FRESH_SHA:
        raise RuntimeError("fresh checkpoint provenance mismatch")
    runtime = dee.Runtime.load_snapshot(str(FRESH))
    selected = dee.Backend.DENSE_SEQUENTIAL if backend == "dense" else dee.Backend.LAZY
    runtime.execution_options = dee.TickOptions(selected, 1)
    if int(runtime.dimension) != N or int(runtime.current_tick) != 32:
        raise RuntimeError("unexpected fresh checkpoint boundary")
    return runtime


def advance(runtime: Any, ticks: int) -> None:
    global TOTAL_TICKS
    runtime.advance(int(ticks))
    TOTAL_TICKS += int(ticks)


def state_summary(runtime: Any) -> dict[str, Any]:
    raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
    occupied = 0
    semantics: dict[str, int] = {}
    for value in raw:
        if value:
            occupied += 1
            rec = dee.decode_record(int(value))
            key = str(int(rec.semantic))
            semantics[key] = semantics.get(key, 0) + 1
    return {
        "tick": int(runtime.current_tick), "occupied": occupied,
        "semantic_counts": semantics,
        "raw_sha256": digest_u64(raw), "clock_sha256": digest_u64(clocks),
    }


def save_snapshot(runtime: Any, name: str) -> dict[str, Any]:
    path = SECTION / "CHECKPOINTS" / name
    runtime.set_snapshot_metadata("mbp4.campaign", CAMPAIGN)
    runtime.set_snapshot_metadata("mbp4.section", "21_INTEGRATED_MIND_GENEALOGY_GENERATIVE_HABITAT")
    runtime.save_snapshot(str(path))
    return {"path": str(path.relative_to(SECTION)).replace("\\", "/"),
            "tick": int(runtime.current_tick), "sha256": sha256(path),
            "bytes": path.stat().st_size}


@dataclass(frozen=True)
class HabitatGeometry:
    q: tuple[int, int, int]
    sensor_source: tuple[int, int, int]
    normalizer_seed: tuple[int, int, int]
    normalizer_source: tuple[int, int, int]
    sensor_load: int
    normalizer_load: int

    def action_tick(self, cycle: int) -> int:
        return 1 + cycle * N

    def return_tick(self, cycle: int) -> int:
        return 2 + cycle * N

    def action_site(self, cycle: int) -> tuple[int, int, int]:
        return add(add(self.q, A), SENSOR_A, cycle)

    def return_site(self, cycle: int) -> tuple[int, int, int]:
        return add(self.action_site(cycle), ACTION_A)


def install_habitat(raw: list[int], clocks: list[int], q: tuple[int, int, int],
                    sensor_load: int, normalizer_load: int, mode: str,
                    audit: MutationAudit, prefix: str) -> HabitatGeometry:
    action0 = add(q, A)
    return0 = add(action0, ACTION_A)
    sensor_source = add(action0, SENSOR_A, -1)
    normalizer_seed = add(return0, NORMALIZER_A, -2)
    normalizer_source = add(return0, NORMALIZER_A, -SOURCE_OFFSET)
    put(raw, clocks, q, 1, 7, A, 1, 11, f"{prefix}.mobile_policy", audit)
    if mode not in {"NO_EXPERIENCE", "NO_ACTION"}:
        sensor_direction = (0, -1, 0) if mode == "SHAM" else SENSOR_A
        load = 0 if mode == "NO_PLASTIC_EFFECT" else sensor_load
        put(raw, clocks, sensor_source, 2, load, sensor_direction, 4, 31,
            f"{prefix}.persistent_input", audit)
    if mode != "NO_RETURN":
        put(raw, clocks, normalizer_seed, 3, normalizer_load, NORMALIZER_A, 1, 37,
            f"{prefix}.return_seed", audit)
        put(raw, clocks, normalizer_source, 4, normalizer_load, NORMALIZER_A, 4, 41,
            f"{prefix}.persistent_return", audit)
    return HabitatGeometry(q, sensor_source, normalizer_seed, normalizer_source,
                           sensor_load, normalizer_load)


def build_habitat(q: tuple[int, int, int], sensor_load: int = SENSOR_LOAD,
                  normalizer_load: int = NORMALIZER_LOAD, mode: str = "FULL",
                  backend: str = "lazy") -> tuple[Any, HabitatGeometry, MutationAudit]:
    parent = load_fresh(backend)
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    audit = MutationAudit()
    geometry = install_habitat(raw, clocks, q, sensor_load, normalizer_load,
                               mode, audit, f"HABITAT.{mode}")
    audit.frozen = True
    return runtime_from(raw, clocks, int(parent.current_tick), backend), geometry, audit


def run_habitat(q: tuple[int, int, int], horizon: int, mode: str = "FULL",
                sensor_load: int = SENSOR_LOAD, normalizer_load: int = NORMALIZER_LOAD,
                backend: str = "lazy", checkpoint_prefix: str | None = None,
                checkpoint_ticks: Iterable[int] = ()) -> tuple[dict[str, Any], Any, HabitatGeometry]:
    runtime, g, audit = build_habitat(q, sensor_load, normalizer_load, mode, backend)
    checkpoints: list[dict[str, Any]] = []
    if checkpoint_prefix:
        checkpoints.append(save_snapshot(runtime, f"{checkpoint_prefix}_T0.deetsnap"))
    requested = set(int(x) for x in checkpoint_ticks)
    events: list[dict[str, Any]] = []
    cycle = 0
    current = 0
    boundaries = set(requested)
    while g.action_tick(cycle) <= horizon:
        boundaries.add(g.action_tick(cycle))
        if g.return_tick(cycle) <= horizon:
            boundaries.add(g.return_tick(cycle))
        cycle += 1
    for rel in sorted(x for x in boundaries if 0 < x <= horizon):
        advance(runtime, rel - current)
        current = rel
        if rel in requested and checkpoint_prefix:
            checkpoints.append(save_snapshot(runtime, f"{checkpoint_prefix}_R{rel:04d}.deetsnap"))
        if (rel - 1) % N == 0:
            k = (rel - 1) // N
            site = g.action_site(k)
            rec = observe(runtime, site)
            matched = matches_lineage_phase(rec, ACTION_A)
            events.append({"cycle": k + 1, "phase": "action", "relative_tick": rel,
                           "absolute_tick": int(runtime.current_tick), "site": list(site),
                           "record": rec,
                           "matches_frozen_lineage_phase": matched,
                           "configured_influences": ["mobile_policy", "persistent_input_support"],
                           "genealogy_certainty": "configured route plus observed record"})
        elif (rel - 2) % N == 0:
            k = (rel - 2) // N
            site = g.return_site(k)
            rec = observe(runtime, site)
            matched = matches_lineage_phase(rec, A)
            events.append({"cycle": k + 1, "phase": "return", "relative_tick": rel,
                           "absolute_tick": int(runtime.current_tick), "site": list(site),
                           "record": rec,
                           "matches_frozen_lineage_phase": matched,
                           "configured_influences": ["action_lineage", "environmental_return"],
                           "genealogy_certainty": "configured route plus observed record"})
    if current < horizon:
        advance(runtime, horizon - current)
    pairs = []
    for k in range((horizon - 2) // N + 1 if horizon >= 2 else 0):
        action = next((x for x in events if x["cycle"] == k + 1 and x["phase"] == "action"), None)
        ret = next((x for x in events if x["cycle"] == k + 1 and x["phase"] == "return"), None)
        if (action and ret and action["matches_frozen_lineage_phase"]
                and ret["matches_frozen_lineage_phase"]):
            pairs.append({"cycle": k + 1, "input_observed": True, "action": action,
                          "environment_change": "return carrier consumed into updated mobile lineage",
                          "return": ret, "same_lineage_anchor": "route/load continuity"})
    result = {
        "mode": mode, "backend": backend, "q": list(q), "horizon": horizon,
        "T_ref": T_REF, "host_writes_after_t0": audit.post_t0_writes,
        "pre_t0_writes": audit.pre_t0_writes,
        "sensor_load": sensor_load, "normalizer_load": normalizer_load,
        "geometry": {"sensor_source": list(g.sensor_source),
                     "normalizer_seed": list(g.normalizer_seed),
                     "normalizer_source": list(g.normalizer_source)},
        "events": events, "complete_episodes": pairs,
        "complete_episode_count": len(pairs), "checkpoints": checkpoints,
        "supports_at_end": {"input": observe(runtime, g.sensor_source),
                            "return": observe(runtime, g.normalizer_source)},
        "final": state_summary(runtime),
    }
    return result, runtime, g


def tracker_existing_contact() -> dict[str, Any]:
    if sha256(PRE_CONTACT) != PRE_CONTACT_SHA:
        raise RuntimeError("section-20 pre-contact checkpoint mismatch")
    tracked = dee.Runtime.load_snapshot(str(PRE_CONTACT))
    control = dee.Runtime.load_snapshot(str(PRE_CONTACT))
    for runtime in (tracked, control):
        runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    target = (29, 10, 11)
    direction = (1, 1, 0)
    expected_load = 12014
    rows = []
    current_site = target
    current_direction = direction
    current_load = expected_load
    first_nonballistic = None
    for rel in range(1, 34):
        advance(tracked, 1)
        predicted = current_site if rel == 1 else add(current_site, current_direction)
        rec = observe(tracked, predicted)
        status = "predicted_site_match"
        candidates = []
        if rec is None or rec["direction"] != list(current_direction) or rec["s_reg"] != current_load:
            raw, clocks = list(tracked.raw_copy()), list(tracked.clock_copy())
            for i, value in enumerate(raw):
                if not value:
                    continue
                decoded = decode(value, clocks[i], (i // (N * N), (i // N) % N, i % N))
                if decoded and decoded["s_reg"] == current_load:
                    candidates.append(decoded)
            if len(candidates) == 1:
                rec = candidates[0]
                status = "relocated_or_direction_changed"
                current_direction = tuple(rec["direction"])
                predicted = tuple(rec["site"])
            elif len(candidates) > 1:
                status = "ambiguous_multiple_candidates"
            else:
                status = "not_identifiable_by_frozen_signature"
            if first_nonballistic is None:
                first_nonballistic = {"relative_tick": rel, "status": status,
                                      "predicted_site": list(predicted),
                                      "candidate_count": len(candidates)}
        if rec is not None and "site" in rec:
            current_site = tuple(rec["site"])
        else:
            current_site = predicted
        rows.append({"relative_tick": rel, "absolute_tick": int(tracked.current_tick),
                     "predicted_site": list(predicted), "record": rec,
                     "status": status, "candidate_count": len(candidates)})
    advance(control, 33)
    return {
        "source_checkpoint": str(PRE_CONTACT.relative_to(WORK)).replace("\\", "/"),
        "source_sha256": PRE_CONTACT_SHA, "window_ticks": 33,
        "first_nonballistic_or_lost_event": first_nonballistic,
        "trace": rows,
        "tracker_vs_unobserved_raw_equal": list(tracked.raw_copy()) == list(control.raw_copy()),
        "tracker_vs_unobserved_clock_equal": list(tracked.clock_copy()) == list(control.clock_copy()),
    }


def instrumental_cases() -> dict[str, Any]:
    n = 7
    size = n ** 3

    def make(items: list[tuple[tuple[int, int, int], int, tuple[int, int, int], int]]) -> Any:
        raw, clocks = [0] * size, [0] * size
        for k, (q, load, direction, semantic) in enumerate(items):
            i = ix(q, n)
            raw[i] = int(dee.pack_record(1, load, *direction, semantic))
            clocks[i] = 100 + k
        r = dee.Runtime.import_research_state(n, 0, raw, clocks)
        r.execution_options = dee.TickOptions(dee.Backend.DENSE_SEQUENTIAL, 1)
        return r

    wrap = make([((6, 0, 0), 7, (1, 0, 0), 1)])
    wrap.advance(1)
    collision = make([((6, 0, 0), 7, (1, 0, 0), 1), ((0, 6, 0), 11, (0, 1, 0), 1)])
    collision.advance(1)
    occupied = make([((6, 0, 0), 7, (1, 0, 0), 1), ((0, 0, 0), 13, (0, 0, 1), 1)])
    occupied.advance(1)
    protected = make([((0, 0, 0), 17, (1, 0, 0), 4)])
    raw0 = int(protected.raw_copy()[0])
    protected.advance(2)
    return {
        "transport_wrapping": decode(int(wrap.raw_copy()[ix((0, 0, 0), n)]),
                                     int(wrap.clock_copy()[ix((0, 0, 0), n)]), (0, 0, 0)),
        "collision": decode(int(collision.raw_copy()[ix((0, 0, 0), n)]),
                            int(collision.clock_copy()[ix((0, 0, 0), n)]), (0, 0, 0)),
        "occupied_target": decode(int(occupied.raw_copy()[ix((0, 0, 0), n)]),
                                  int(occupied.clock_copy()[ix((0, 0, 0), n)]), (0, 0, 0)),
        "protected_source_raw_unchanged": int(protected.raw_copy()[0]) == raw0,
        "protected_source_after": decode(int(protected.raw_copy()[0]), int(protected.clock_copy()[0]), (0, 0, 0)),
    }


def factorial_history() -> dict[str, Any]:
    rows = {}
    for name, history, challenge in (("W00", False, False), ("W10", True, False),
                                     ("W01", False, True), ("W11", True, True)):
        row, _, _ = run_habitat((10, 10, 10), HORIZONS[0], mode="FULL",
                                sensor_load=SENSOR_LOAD if history else 0,
                                normalizer_load=NORMALIZER_LOAD if challenge else 0)
        rows[name] = row
    y = {name: row["complete_episodes"][-1]["return"]["record"]["s_reg"]
         if row["complete_episodes"] else None for name, row in rows.items()}
    return {"rows": rows, "Y_terminal_return_s_reg": y,
            "effect_without_history": None if None in (y["W01"], y["W00"]) else y["W01"] - y["W00"],
            "effect_with_history": None if None in (y["W11"], y["W10"]) else y["W11"] - y["W10"]}


def controls() -> dict[str, Any]:
    result = {}
    for mode in ("NO_EXPERIENCE", "NO_PLASTIC_EFFECT", "NO_ACTION", "NO_RETURN", "SHAM"):
        row, _, _ = run_habitat((10, 10, 10), HORIZONS[0], mode=mode)
        result[mode] = row
    return result


def holdouts() -> list[dict[str, Any]]:
    rows = []
    for identifier, q in (("HOLDOUT_TRANSLATION_1", (16, 12, 18)),
                          ("HOLDOUT_TRANSLATION_2", (24, 32, 8))):
        row, _, _ = run_habitat(q, HORIZONS[0], mode="FULL")
        row["holdout_id"] = identifier
        rows.append(row)
    return rows


def retention_panel(source_checkpoint: Path, g: HabitatGeometry) -> dict[str, Any]:
    base = dee.Runtime.load_snapshot(str(source_checkpoint))
    rows = {}
    for name, cut_input, cut_return in (("PRACTICE", False, False),
                                        ("NO_USE_ACTIVE", True, False),
                                        ("IDLE", True, True)):
        raw, clocks = list(base.raw_copy()), list(base.clock_copy())
        edits = []
        if cut_input:
            raw[ix(g.sensor_source)] = 0
            edits.append("sensor_source_removed_in_diagnostic_fork")
        if cut_return:
            raw[ix(g.normalizer_source)] = 0
            edits.append("normalizer_source_removed_in_diagnostic_fork")
        runtime = runtime_from(raw, clocks, int(base.current_tick), "lazy")
        advance(runtime, HORIZONS[0])
        rows[name] = {"diagnostic_edits": edits, "final": state_summary(runtime),
                      "input_support": observe(runtime, g.sensor_source),
                      "return_support": observe(runtime, g.normalizer_source)}
    return rows


def atlas(checkpoints: list[dict[str, Any]], g: HabitatGeometry) -> dict[str, Any]:
    panel = []
    for cp in checkpoints:
        if cp["path"] not in {"CHECKPOINTS/MAIN_T0.deetsnap",
                              "CHECKPOINTS/MAIN_AFTER_FIRST_RETURN.deetsnap",
                              "CHECKPOINTS/MAIN_AFTER_THREE_RETURNS.deetsnap"}:
            continue
        base_path = SECTION / cp["path"]
        for mode in ("FULL", "INPUT_CUT", "RETURN_CUT"):
            base = dee.Runtime.load_snapshot(str(base_path))
            raw, clocks = list(base.raw_copy()), list(base.clock_copy())
            edits = []
            if mode == "INPUT_CUT":
                raw[ix(g.sensor_source)] = 0
                edits.append("input support removed in diagnostic fork")
            if mode == "RETURN_CUT":
                raw[ix(g.normalizer_source)] = 0
                raw[ix(g.normalizer_seed)] = 0
                edits.append("return sources removed in diagnostic fork")
            runtime = runtime_from(raw, clocks, int(base.current_tick), "lazy")
            before = state_summary(runtime)
            advance(runtime, T_REF)
            after = state_summary(runtime)
            panel.append({"checkpoint": cp, "mode": mode, "diagnostic_edits": edits,
                          "horizon": T_REF, "before": before, "after": after})
    return {"panel_definition": {"modes": ["FULL", "INPUT_CUT", "RETURN_CUT"],
                                 "horizon": T_REF}, "rows": panel}


def backend_equivalence() -> dict[str, Any]:
    lazy, lr, _ = run_habitat((10, 10, 10), 96, backend="lazy")
    dense, dr, _ = run_habitat((10, 10, 10), 96, backend="dense")
    return {"horizon": 96,
            "raw_equal": list(lr.raw_copy()) == list(dr.raw_copy()),
            "clock_equal": list(lr.clock_copy()) == list(dr.clock_copy()),
            "lazy_final": lazy["final"], "dense_final": dense["final"]}


def resume_equivalence() -> dict[str, Any]:
    first, runtime, _ = run_habitat((10, 10, 10), HORIZONS[0], mode="FULL")
    temp = SECTION / "CHECKPOINTS" / "RESUME_EQUIVALENCE_BOUNDARY.deetsnap"
    runtime.save_snapshot(str(temp))
    resumed = dee.Runtime.load_snapshot(str(temp))
    resumed.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    advance(resumed, HORIZONS[1] - HORIZONS[0])
    continuous, continuous_runtime, _ = run_habitat((10, 10, 10), HORIZONS[1], mode="FULL")
    return {"boundary_tick": first["final"]["tick"], "end_relative_tick": HORIZONS[1],
            "raw_equal": list(resumed.raw_copy()) == list(continuous_runtime.raw_copy()),
            "clock_equal": list(resumed.clock_copy()) == list(continuous_runtime.clock_copy()),
            "resumed": state_summary(resumed), "continuous": continuous["final"],
            "checkpoint": {"path": str(temp.relative_to(SECTION)).replace("\\", "/"),
                           "sha256": sha256(temp), "bytes": temp.stat().st_size}}


def install_loop(raw: list[int], clocks: list[int], q: tuple[int, int, int],
                 policy: tuple[int, int, int], sensor: tuple[int, int, int],
                 action: tuple[int, int, int], normalizer: tuple[int, int, int],
                 sensor_load: int, normalizer_load: int, prefix: str,
                 audit: MutationAudit) -> None:
    action0 = add(q, policy)
    return0 = add(action0, action)
    put(raw, clocks, q, 1, 7, policy, 1, 11, f"{prefix}.policy", audit)
    put(raw, clocks, add(action0, sensor, -1), 2, sensor_load, sensor, 4, 31,
        f"{prefix}.sensor", audit)
    put(raw, clocks, add(return0, normalizer, -2), 3, normalizer_load, normalizer, 1, 37,
        f"{prefix}.seed", audit)
    put(raw, clocks, add(return0, normalizer, -SOURCE_OFFSET), 4, normalizer_load,
        normalizer, 4, 41, f"{prefix}.return", audit)


def mediated_two_body(offset: tuple[int, int, int], route_cut: bool) -> dict[str, Any]:
    parent = load_fresh("lazy")
    raw, clocks = list(parent.raw_copy()), list(parent.clock_copy())
    audit = MutationAudit()
    t1 = translate((24, 20, 20), offset)
    t2 = add(t1, (1, 1, 0), 10)
    b1_return0 = add(t1, A, -18)
    q1 = add(add(b1_return0, A, -1), ACTION_A, -1)
    b2_return0 = add(t2, C, -28)
    q2 = add(add(b2_return0, C, -1), ACTION_C, -1)
    install_loop(raw, clocks, q1, A, SENSOR_A, ACTION_A, NORMALIZER_A,
                 SENSOR_LOAD, NORMALIZER_LOAD, "B1", audit)
    install_loop(raw, clocks, q2, C, SENSOR_C, ACTION_C, NORMALIZER_C,
                 2000, 3000, "B2", audit)
    if not route_cut:
        relay_source = add(t1, B, -20)
        put(raw, clocks, relay_source, 9, 500, B, 1, 53, "environment.relay", audit)
    audit.frozen = True
    runtime = runtime_from(raw, clocks, int(parent.current_tick), "lazy")
    advance(runtime, 20)
    m1 = observe(runtime, t1)
    advance(runtime, 10)
    b2_effect = observe(runtime, t2)
    advance(runtime, 32)
    return {"offset": list(offset), "route_cut": route_cut,
            "host_writes_after_t0": audit.post_t0_writes,
            "B1_q": list(q1), "B2_q": list(q2), "M1_site": list(t1),
            "B2_effect_site": list(t2), "M1": m1, "B2_effect": b2_effect,
            "B1_return_observed_after_B2": None,
            "final": state_summary(runtime)}


def write_genealogy(main: dict[str, Any], two_body: list[dict[str, Any]]) -> None:
    path = SECTION / "TELEMETRY" / "GENEALOGY_EVENTS.csv"
    fields = ["tick", "entity", "event", "source", "target", "site",
              "s_reg", "direction", "matches_frozen_lineage_phase",
              "certainty", "ambiguity"]
    rows = []
    for event in main["events"]:
        rec = event["record"] or {}
        matched = bool(event["matches_frozen_lineage_phase"])
        rows.append({"tick": event["absolute_tick"],
                     "entity": "B_MAIN" if matched else "PREDICTED_SITE_OBSERVATION",
                     "event": event["phase"],
                     "source": "+".join(event["configured_influences"]),
                     "target": "mobile_policy_lineage", "site": json.dumps(event["site"]),
                     "s_reg": rec.get("s_reg"), "direction": json.dumps(rec.get("direction")),
                     "matches_frozen_lineage_phase": matched,
                     "certainty": (event["genealogy_certainty"] if matched else
                                   "observation at predicted coordinate only"),
                     "ambiguity": ("microscopic parent necessity assigned only by matched controls"
                                   if matched else "frozen lineage signature not matched")})
    for index, row in enumerate(two_body):
        for name, rec, target in (("mediator", row["M1"], row["M1_site"]),
                                  ("B2_effect", row["B2_effect"], row["B2_effect_site"])):
            rows.append({"tick": 52 if name == "mediator" else 62,
                         "entity": f"B1_B2_{index}", "event": name,
                         "source": "B1/environment" if name == "mediator" else "M1/B2",
                         "target": "environment" if name == "mediator" else "B2",
                         "site": json.dumps(target), "s_reg": None if rec is None else rec["s_reg"],
                         "direction": json.dumps(None if rec is None else rec["direction"]),
                         "matches_frozen_lineage_phase": "not_applicable",
                         "certainty": "observed at preregistered site",
                         "ambiguity": "no return to B1 identified in frozen horizon"})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def campaign() -> None:
    for name in ("CHECKPOINTS", "TELEMETRY", "RUNNER"):
        (SECTION / name).mkdir(parents=True, exist_ok=True)
    if sha256(PARENT_ZIP) != PARENT_ZIP_SHA:
        raise RuntimeError("canonical parent ZIP mismatch")

    discovery = []
    for sensor_load, normalizer_load in ((1000, 1000), (2000, 1000),
                                         (3000, 2000), (4000, 3000)):
        row, _, _ = run_habitat((10, 10, 10), 96, sensor_load=sensor_load,
                                normalizer_load=normalizer_load)
        discovery.append({"sensor_load": sensor_load, "normalizer_load": normalizer_load,
                          "complete_episode_count": row["complete_episode_count"],
                          "events": row["events"], "final": row["final"]})
    write_json(SECTION / "TELEMETRY" / "DISCOVERY.json", discovery)

    config = {
        "schema": "mbp4.integrated-mind.experiment-config.v1",
        "campaign": CAMPAIGN, "frozen_utc": utc(), "parent_zip_sha256": PARENT_ZIP_SHA,
        "parent_checkpoint": "12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap",
        "parent_checkpoint_sha256": FRESH_SHA, "dimension": N,
        "classification": "source-supported/driven",
        "MAIN_q": [10, 10, 10], "sensor_load": SENSOR_LOAD,
        "normalizer_load": NORMALIZER_LOAD, "source_offset": SOURCE_OFFSET,
        "T_ref": T_REF, "horizons": list(HORIZONS),
        "holdout_q": [[16, 12, 18], [24, 32, 8]],
        "controls": ["NO_EXPERIENCE", "NO_PLASTIC_EFFECT", "NO_ACTION", "NO_RETURN", "SHAM"],
        "factorial": ["W00", "W10", "W01", "W11"],
        "atlas": {"states": [0, 2, 96], "modes": ["FULL", "INPUT_CUT", "RETURN_CUT"],
                  "horizon": T_REF},
        "post_t0_host_policy": ["advance", "observe", "save", "diagnostic forks"],
        "tracker": "passive external relational/genealogical observer",
        "event_reader": {
            "action": {"semantic": 1, "direction": list(ACTION_A)},
            "return": {"semantic": 1, "direction": list(A)},
            "policy": "predicted coordinate alone is insufficient for lineage attribution",
        },
    }
    write_json(SECTION / "EXPERIMENT_CONFIG.json", config)

    main, main_runtime, geometry = run_habitat(
        (10, 10, 10), HORIZONS[-1], mode="FULL", checkpoint_prefix="MAIN",
        checkpoint_ticks=(2, 96, HORIZONS[0], HORIZONS[1], HORIZONS[2]))
    renamed = {
        32: "MAIN_T0.deetsnap", 34: "MAIN_AFTER_FIRST_RETURN.deetsnap",
        128: "MAIN_AFTER_THREE_RETURNS.deetsnap",
        32 + HORIZONS[0]: "MAIN_H4.deetsnap",
        32 + HORIZONS[1]: "MAIN_H16.deetsnap",
        32 + HORIZONS[2]: "MAIN_FINAL.deetsnap",
    }
    checkpoints = []
    for cp in main["checkpoints"]:
        old = SECTION / cp["path"]
        name = renamed.get(int(cp["tick"]), old.name)
        new = old.with_name(name)
        if new != old:
            old.replace(new)
        cp = {**cp, "path": str(new.relative_to(SECTION)).replace("\\", "/"),
              "sha256": sha256(new), "bytes": new.stat().st_size}
        checkpoints.append(cp)
    main["checkpoints"] = checkpoints
    main_final = next(cp for cp in checkpoints if cp["path"] == "CHECKPOINTS/MAIN_FINAL.deetsnap")
    write_json(SECTION / "TELEMETRY" / "MAIN_CONTINUITY.json", main)

    control_rows = controls()
    factorial = factorial_history()
    holdout_rows = holdouts()
    write_json(SECTION / "TELEMETRY" / "CAUSAL_CONTROLS.json", control_rows)
    write_json(SECTION / "TELEMETRY" / "HISTORY_FACTORIAL.json", factorial)
    write_json(SECTION / "TELEMETRY" / "HOLDOUTS.json", holdout_rows)

    after_three = SECTION / "CHECKPOINTS" / "MAIN_AFTER_THREE_RETURNS.deetsnap"
    retention = retention_panel(after_three, geometry)
    atlas_rows = atlas(checkpoints, geometry)
    write_json(SECTION / "TELEMETRY" / "RETENTION.json", retention)
    write_json(SECTION / "TELEMETRY" / "ATLAS.json", atlas_rows)

    tracker = tracker_existing_contact()
    instruments = instrumental_cases()
    backends = backend_equivalence()
    resume = resume_equivalence()
    write_json(SECTION / "TELEMETRY" / "GENEALOGY_TRACKER_VALIDATION.json", tracker)
    write_json(SECTION / "TELEMETRY" / "INSTRUMENTAL_CASES.json", instruments)
    write_json(SECTION / "TELEMETRY" / "BACKEND_EQUIVALENCE.json", backends)
    write_json(SECTION / "TELEMETRY" / "RESUME_EQUIVALENCE.json", resume)

    two_body = []
    for offset in ((0, 0, 0), (5, 7, 9)):
        two_body.append(mediated_two_body(offset, False))
        two_body.append(mediated_two_body(offset, True))
    write_json(SECTION / "TELEMETRY" / "TWO_BODY_EXTENSION.json", two_body)
    write_genealogy(main, two_body)

    episodes = int(main["complete_episode_count"])
    actions = sum(bool(x["matches_frozen_lineage_phase"])
                  for x in main["events"] if x["phase"] == "action")
    returns = sum(bool(x["matches_frozen_lineage_phase"])
                  for x in main["events"] if x["phase"] == "return")
    summary = {
        "schema": "mbp4.integrated-mind.run-summary.v1", "campaign": CAMPAIGN,
        "parent_zip_sha256": PARENT_ZIP_SHA, "kernel_version": "DEE Universe v27 frozen",
        "runtime_version": str(getattr(dee, "__version__", "2.2.0")),
        "branch": "MBP4_INTEGRATED_MAIN_FROM_OBP_FRESH_T32",
        "parent_checkpoint": {"path": "12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap",
                              "sha256": FRESH_SHA, "tick": 32},
        "tick_initial": 32, "tick_final": int(main_runtime.current_tick),
        "T_ref": T_REF, "horizons": list(HORIZONS),
        "episodes_observed": episodes, "actions_observed": actions,
        "returns_observed": returns, "host_writes_after_t0": main["host_writes_after_t0"],
        "tracker": {"first_nonballistic_or_lost_event": tracker["first_nonballistic_or_lost_event"],
                    "raw_equal_enabled_disabled": tracker["tracker_vs_unobserved_raw_equal"],
                    "clock_equal_enabled_disabled": tracker["tracker_vs_unobserved_clock_equal"]},
        "controls_executed": list(control_rows),
        "factorial_effects": {"without_history": factorial["effect_without_history"],
                              "with_history": factorial["effect_with_history"]},
        "holdouts": [row["holdout_id"] for row in holdout_rows],
        "two_body_worlds": len(two_body),
        "two_body_mediated_records": sum(row["B2_effect"] is not None and not row["route_cut"] for row in two_body),
        "two_body_return_to_B1_records": sum(row["B1_return_observed_after_B2"] is not None for row in two_body),
        "main_checkpoint": main_final,
        "checkpoints": checkpoints + [resume["checkpoint"]],
        "technical_equalities": {"backend_raw": backends["raw_equal"],
                                 "backend_clock": backends["clock_equal"],
                                 "resume_raw": resume["raw_equal"],
                                 "resume_clock": resume["clock_equal"]},
        "tracker_ambiguities": [tracker["first_nonballistic_or_lost_event"]],
        "incidents": [], "closure_reason": "predeclared 64*T_ref horizon reached",
        "total_ticks_executed_all_worlds": TOTAL_TICKS, "created_utc": utc(),
    }
    write_json(SECTION / "RUN_SUMMARY.json", summary)


def resume(snapshot: Path, ticks: int, output: Path) -> None:
    runtime = dee.Runtime.load_snapshot(str(snapshot))
    runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    runtime.advance(int(ticks))
    runtime.save_snapshot(str(output))
    print(json.dumps({"input": str(snapshot), "ticks": ticks, "output": str(output),
                      "tick": int(runtime.current_tick), "sha256": sha256(output)}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--ticks", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.resume:
        if args.output is None or args.ticks < 0:
            parser.error("--resume requires --output and nonnegative --ticks")
        resume(args.resume, args.ticks, args.output)
    else:
        campaign()


if __name__ == "__main__":
    main()
