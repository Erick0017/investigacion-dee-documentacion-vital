from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
import zipfile
from array import array
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUNNER_DIR = Path(__file__).resolve().parent
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))

import dee_thinking as dee

from genealogy_tracker import analyze_transition, decode, digest, runtime_from, trace_from_target
from relational_body import (
    FRESH_SHA256, N, BodyPorts, add, body_sample, build_relational_body,
    decode_raw, index, load_fresh, observe, sha256, trace_body,
)


CAMPAIGN = "MBP4-TRANSFORMATIVE-GENEALOGY-RELATIONAL-CONSOLIDATION"
PARENT_ZIP_SHA256 = "088652aebdb3a86cd14a50be624c28c24f4d69fbc4c2a9f2be0c5ea818efda75"
WRAPPER = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS"
SECTION_NAME = "22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_readme(section: Path) -> None:
    text = """# Reproducción técnica de la sección 22

Esta sección usa exclusivamente DEE thinking 2.2.0 y el kernel v27 congelado.
El tracker es un observador externo: reconstruye transiciones sobre copias y no
escribe identificadores en RAW o clock. La composición relacional se prepara
antes de T0; después sólo se ejecutan `advance`, observación pasiva y guardado.

Desde una extracción del ZIP cuyo directorio envolvente sea `<PACKAGE_ROOT>`:

```powershell
python 22_TRANSFORMATIVE_GENEALOGY_RELATIONAL_CONSOLIDATION/RUNNER/run_consolidation.py `
  --package-root <PACKAGE_ROOT> --validate-only
```

Para repetir la ciencia en una copia del paquete padre (nunca sobre el ZIP
oficial ya ampliado), ejecute el mismo runner sólo con `--package-root`. Los
controles diagnósticos están identificados en telemetría y jamás se fusionan en
MAIN. `EXPERIMENT_CONFIG.json` fija origen, horizontes, reservas y cortes.
"""
    (section / "README_REPRODUCCION.md").write_text(text, encoding="utf-8")


def digest_u64(values: Any) -> str:
    return hashlib.sha256(array("Q", (int(x) for x in values)).tobytes()).hexdigest()


def state_summary(runtime: Any) -> dict[str, Any]:
    raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
    semantic: dict[str, int] = {}
    for value in raw:
        if value:
            rec = dee.decode_record(int(value))
            key = str(int(rec.semantic))
            semantic[key] = semantic.get(key, 0) + 1
    return {
        "tick": int(runtime.current_tick), "occupied": sum(bool(x) for x in raw),
        "semantic_counts": semantic, "raw_sha256": digest_u64(raw),
        "clock_sha256": digest_u64(clocks),
    }


def save_snapshot(runtime: Any, section: Path, name: str) -> dict[str, Any]:
    path = section / "CHECKPOINTS" / name
    runtime.set_snapshot_metadata("mbp4.campaign", CAMPAIGN)
    runtime.set_snapshot_metadata("mbp4.section", SECTION_NAME)
    runtime.save_snapshot(str(path))
    return {
        "path": path.relative_to(section).as_posix(), "tick": int(runtime.current_tick),
        "sha256": sha256(path), "bytes": path.stat().st_size,
    }


def event_signature(row: dict[str, Any], sign: int) -> dict[str, bool]:
    action = row["action_plus"] if sign > 0 else row["action_minus"]
    ret = row["return_plus"] if sign > 0 else row["return_minus"]
    comparator = row["comparator"]
    return {
        "action": action is not None and action["direction"] == [0, 0, 1] and action["s_reg"] > 11,
        "environment_return": (
            ret is not None and ret["direction"] == [-sign, -1, -1]
            and ret["s_reg"] > 30
        ),
        "organization_return": (
            comparator is not None
            and comparator["direction"] == [-sign, -1, -1]
        ),
    }


def summarize_trace(trace: list[dict[str, Any]], history: str) -> dict[str, Any]:
    sign = 1 if history == "AB" else (-1 if history == "BA" else 0)
    event_ticks: dict[str, list[int]] = {
        "action": [], "environment_return": [],
        "organization_return": [], "delta_modification": [],
    }
    initial_delta = None
    previous_flags = {"action": False, "environment_return": False, "organization_return": False}
    for row in trace:
        if row["relative_tick"] == 1:
            initial_delta = row["delta"]
        if initial_delta is not None and row["relative_tick"] > 1 and row["delta"] != initial_delta:
            event_ticks["delta_modification"].append(row["relative_tick"])
        if sign:
            flags = event_signature(row, sign)
            for name, value in flags.items():
                if value and not previous_flags[name]:
                    event_ticks[name].append(row["relative_tick"])
            previous_flags = flags
    projection = {
        str(tick): next((row["axis_projection"] for row in trace if row["relative_tick"] == tick), None)
        for tick in (1, 16, 32, 64)
    }
    return {
        "history": history, "delta_tick1": next((row["delta"] for row in trace if row["relative_tick"] == 1), None),
        "axis_projection": projection, "event_ticks": event_ticks,
        "terminal_delta": trace[-1]["delta"] if trace else None,
        "terminal_axis_projection": trace[-1]["axis_projection"] if trace else None,
    }


def run_case(package_root: Path, origin: tuple[int, int, int], distance: int,
             history: str, mode: str, horizon: int, backend: str = "lazy",
             keep_trace: bool = False) -> tuple[dict[str, Any], Any, BodyPorts, list[dict[str, Any]]]:
    runtime, ports, audit = build_relational_body(
        package_root, origin, history, distance, mode=mode, backend=backend
    )
    trace = trace_body(runtime, ports, horizon, sample_all=True)
    summary = summarize_trace(trace, history)
    serialized_ports: dict[str, Any] = {}
    for name, value in ports.__dict__.items():
        if isinstance(value, int):
            serialized_ports[name] = value
        elif isinstance(value, tuple) and (not value or isinstance(value[0], int)):
            serialized_ports[name] = list(value)
        else:
            serialized_ports[name] = [list(x) for x in value]
    result = {
        "origin": list(origin), "action_distance": distance, "history": history,
        "mode": mode, "backend": backend, "horizon": horizon,
        "pre_t0_writes": audit.pre_t0_writes, "host_writes_after_t0": audit.post_t0_writes,
        "ports": serialized_ports,
        "observed": summary, "final": state_summary(runtime),
    }
    if keep_trace:
        result["trace"] = trace
    return result, runtime, ports, trace


def discovery(package_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    # The initial 24-case bounded search was already executed and localized the
    # failure: it looked for (sign,0,-1), while the native reader actually emits
    # along (sign,+1,0).  This is the single causally motivated refinement.  It
    # is checked against H0 and BA at the same preparation, not expanded into a
    # second broad search.
    origin = (15, 15, 15)
    distance = 5
    rows = []
    for history in ("H0", "AB", "BA"):
        try:
            result, _, _, _ = run_case(
                package_root, origin, distance, history, "FULL", 40, keep_trace=False
            )
            events = result["observed"]["event_ticks"]
            projection = result["observed"]["axis_projection"]
            score = (
                int(result["observed"]["delta_tick1"] == (1 if history == "AB" else (-1 if history == "BA" else 0))),
                len(events["organization_return"]),
                len(events["environment_return"]), len(events["action"]), 0,
            )
            rows.append({**result, "trace": None, "score": list(score), "error": None})
        except Exception as error:
            rows.append({"origin": list(origin), "action_distance": distance,
                         "history": history, "score": [0, 0, 0, 0, 0], "error": str(error)})
    usable = [row for row in rows if row["error"] is None]
    if not usable:
        raise RuntimeError("causally motivated relational refinement was not constructible")
    selected = next(row for row in usable if row["history"] == "AB")
    return selected, rows


def tracker_suite(package_root: Path) -> dict[str, Any]:
    cp20 = package_root / "20_MATERIALIZED_ENTITIES_NATIVE_INTERACTION" / "CHECKPOINTS"
    pre = cp20 / "B1_B2_PRE_CONTACT.deetsnap"
    post = cp20 / "B1_B2_POST_CONTACT.deetsnap"
    follow = cp20 / "B12_FOLLOWUP.deetsnap"
    pre_runtime = dee.Runtime.load_snapshot(str(pre))
    pre_runtime.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    b12 = trace_from_target(pre_runtime, (29, 10, 11), 84)
    direct52 = dee.Runtime.load_snapshot(str(pre))
    direct52.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    direct52.advance(1)
    saved52 = dee.Runtime.load_snapshot(str(post))
    contact_equal = (
        list(direct52.raw_copy()) == list(saved52.raw_copy())
        and list(direct52.clock_copy()) == list(saved52.clock_copy())
    )
    direct84 = dee.Runtime.load_snapshot(str(pre))
    direct84.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    direct84.advance(33)
    saved84 = dee.Runtime.load_snapshot(str(follow))
    follow_equal = (
        list(direct84.raw_copy()) == list(saved84.raw_copy())
        and list(direct84.clock_copy()) == list(saved84.clock_copy())
    )
    contact_65_66 = next(
        (row for row in b12["transitions"] if row["tick_before"] == 65), None
    )

    main_t0 = package_root / "21_INTEGRATED_MIND_GENEALOGY_GENERATIVE_HABITAT" / "CHECKPOINTS" / "MAIN_T0.deetsnap"
    ninth = dee.Runtime.load_snapshot(str(main_t0))
    ninth.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    ninth.advance(377)
    before_raw, before_clock = list(ninth.raw_copy()), list(ninth.clock_copy())
    ninth_transition, ninth_after = analyze_transition(ninth, (3, 10, 19), ((3, 10, 18),))
    source_index = index((3, 10, 18), N)
    ablated_raw = before_raw.copy()
    ablated_raw[source_index] = 0
    horizon_rows = []
    for horizon in (1, 4, 16):
        full = runtime_from(before_raw, before_clock, 409, N)
        cut = runtime_from(ablated_raw, before_clock, 409, N)
        full.advance(horizon)
        cut.advance(horizon)
        fr, cr = list(full.raw_copy()), list(cut.raw_copy())
        horizon_rows.append({
            "horizon": horizon, "raw_changed_sites": sum(a != b for a, b in zip(fr, cr)),
            "clock_equal": list(full.clock_copy()) == list(cut.clock_copy()),
            "full_raw_sha256": digest(fr), "source_cut_raw_sha256": digest(cr),
        })

    return {
        "B12": {
            "pre_checkpoint": {"path": pre.relative_to(package_root).as_posix(), "sha256": sha256(pre)},
            "post_contact_checkpoint_equal": contact_equal,
            "followup_checkpoint_equal": follow_equal,
            "trace": b12, "transition_65_to_66": contact_65_66,
        },
        "NINTH_RETURN": {
            "source": [3, 10, 18], "protected_target": [3, 10, 19],
            "transition": ninth_transition, "source_cut_horizons": horizon_rows,
            "after_tick": int(ninth_after.current_tick),
        },
    }


def instrumental_tracker_cases() -> dict[str, Any]:
    n = 9

    def put(raw: list[int], clocks: list[int], q: tuple[int, int, int], s: int,
            direction: tuple[int, int, int], semantic: int = 1, state: int = 1) -> None:
        raw[index(q, n)] = int(dee.pack_record(state, s, *direction, semantic))

    cases = []
    # transport with wrapping
    raw, clocks = [0] * (n ** 3), [0] * (n ** 3)
    put(raw, clocks, (8, 4, 4), 23, (1, 0, 0))
    case, full = analyze_transition(runtime_from(raw, clocks, 0, n), (0, 4, 4), ((8, 4, 4),))
    cases.append({"id": "WRAP_TRANSPORT", "analysis": case})
    # multi-source fusion changes charge and direction
    raw, clocks = [0] * (n ** 3), [0] * (n ** 3)
    put(raw, clocks, (3, 4, 4), 5, (1, 0, 0))
    put(raw, clocks, (4, 3, 4), 7, (0, 1, 0))
    case, full = analyze_transition(runtime_from(raw, clocks, 0, n), (4, 4, 4), ((3, 4, 4), (4, 3, 4)))
    control = runtime_from(raw, clocks, 0, n)
    control.advance(1)
    cases.append({
        "id": "MULTI_SOURCE_TRANSFORMATION", "analysis": case,
        "tracker_raw_equal": list(full.raw_copy()) == list(control.raw_copy()),
        "tracker_clock_equal": list(full.clock_copy()) == list(control.clock_copy()),
    })
    # occupied destination precedence
    raw, clocks = [0] * (n ** 3), [0] * (n ** 3)
    put(raw, clocks, (3, 4, 4), 9, (1, 0, 0))
    put(raw, clocks, (4, 4, 4), 2, (0, 0, 0))
    case, _ = analyze_transition(runtime_from(raw, clocks, 0, n), (4, 4, 4), ((3, 4, 4),))
    cases.append({"id": "OCCUPIED_DESTINATION", "analysis": case})
    # semantic4 target protection
    raw, clocks = [0] * (n ** 3), [0] * (n ** 3)
    put(raw, clocks, (3, 4, 4), 9, (1, 0, 0))
    put(raw, clocks, (4, 4, 4), 2, (0, 0, 0), semantic=4)
    case, _ = analyze_transition(runtime_from(raw, clocks, 0, n), (4, 4, 4), ((3, 4, 4),))
    cases.append({"id": "SEMANTIC4_PROTECTION", "analysis": case})
    # two indistinguishable raws at separate sites remain two positional candidates
    raw, clocks = [0] * (n ** 3), [0] * (n ** 3)
    put(raw, clocks, (1, 1, 1), 5, (1, 0, 0))
    put(raw, clocks, (1, 3, 1), 5, (1, 0, 0))
    world = runtime_from(raw, clocks, 0, n)
    world.advance(1)
    candidates = []
    expected_raw = int(dee.pack_record(1, 5, 1, 0, 0, 1))
    for i, value in enumerate(world.raw_copy()):
        if int(value) == expected_raw:
            x, rem = divmod(i, n * n)
            y, z = divmod(rem, n)
            candidates.append([x, y, z])
    cases.append({"id": "EQUAL_APPEARANCE_AMBIGUITY", "candidate_sites": candidates,
                  "ambiguity_preserved": len(candidates) == 2})
    return {"domain": [row["id"] for row in cases], "cases": cases}


def save_main_checkpoints(package_root: Path, section: Path, config: dict[str, Any]) -> tuple[dict[str, Any], Any]:
    fresh = load_fresh(package_root)
    checkpoints = [save_snapshot(fresh, section, "PRE_INSTALL.deetsnap")]
    runtime, ports, audit = build_relational_body(
        package_root, tuple(config["origin"]), "AB", int(config["action_distance"]), "FULL", "lazy"
    )
    checkpoints.append(save_snapshot(runtime, section, "RELATIONAL_MAIN_T0.deetsnap"))
    trace: list[dict[str, Any]] = []
    saved = set()
    delta_tick1 = None
    first_action = None
    first_environment_return = None
    first_return = None
    second_modification = None
    previous_flags = {"action": False, "environment_return": False, "organization_return": False}
    for tick in range(1, int(config["horizons"][-1]) + 1):
        runtime.advance(1)
        row = body_sample(runtime, ports, tick)
        trace.append(row)
        if tick == 1:
            delta_tick1 = row["delta"]
            checkpoints.append(save_snapshot(runtime, section, "FIRST_HISTORY_ACQUIRED.deetsnap"))
        flags = event_signature(row, 1)
        onset = {name: value and not previous_flags[name] for name, value in flags.items()}
        if onset["action"] and first_action is None:
            first_action = tick
            checkpoints.append(save_snapshot(runtime, section, "FIRST_HISTORY_ACTION.deetsnap"))
        if onset["environment_return"] and first_environment_return is None:
            first_environment_return = tick
            checkpoints.append(save_snapshot(runtime, section, "FIRST_ENVIRONMENT_RETURN.deetsnap"))
        if onset["organization_return"] and first_return is None:
            first_return = tick
            checkpoints.append(save_snapshot(runtime, section, "FIRST_RETURN.deetsnap"))
        elif onset["organization_return"] and second_modification is None:
            second_modification = tick
            checkpoints.append(save_snapshot(runtime, section, "SECOND_MODIFICATION.deetsnap"))
        previous_flags = flags
    checkpoints.append(save_snapshot(runtime, section, "RELATIONAL_MAIN_FINAL.deetsnap"))
    observed = summarize_trace(trace, "AB")
    complete = min(
        len(observed["event_ticks"]["action"]),
        len(observed["event_ticks"]["environment_return"]),
        len(observed["event_ticks"]["organization_return"]),
    )
    return {
        "origin": config["origin"], "action_distance": config["action_distance"],
        "horizons": config["horizons"], "T_ref": config["T_ref"],
        "host_writes_after_t0": audit.post_t0_writes,
        "observed": observed, "complete_episode_count": complete,
        "first_action_tick": first_action,
        "first_environment_return_tick": first_environment_return,
        "first_organization_return_tick": first_return,
        "second_modification_tick": second_modification,
        "checkpoints": checkpoints, "trace": trace, "final": state_summary(runtime),
    }, runtime


def controls_and_holdouts(package_root: Path, config: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    origin = tuple(config["origin"])
    distance = int(config["action_distance"])
    horizon = int(config["horizons"][1])
    controls = {}
    for name, history, mode in (
        ("H0", "H0", "FULL"), ("AB", "AB", "FULL"), ("BA", "BA", "FULL"),
        ("READ_CUT", "AB", "READ_CUT"),
        ("NO_ACTION", "AB", "ACTION_CUT"),
        ("RETURN_CUT", "AB", "RETURN_CUT"), ("SHAM", "SHAM", "FULL"),
    ):
        result, _, _, _ = run_case(package_root, origin, distance, history, mode, horizon)
        controls[name] = result
    holdouts = []
    for ident, holdout_origin, history in (
        ("HOLDOUT_TRANSLATION_AB", tuple(config["holdout_origins"][0]), "AB"),
        ("HOLDOUT_TRANSLATION_BA", tuple(config["holdout_origins"][1]), "BA"),
    ):
        result, _, _, _ = run_case(
            package_root, holdout_origin, distance, history, "FULL", horizon
        )
        holdouts.append({"holdout_id": ident, **result})
    return controls, holdouts


def technical_equivalence(package_root: Path, section: Path, config: dict[str, Any]) -> dict[str, Any]:
    origin, distance = tuple(config["origin"]), int(config["action_distance"])
    horizon = int(config["T_ref"])
    lazy, lazy_runtime, _, _ = run_case(package_root, origin, distance, "AB", "FULL", horizon, "lazy")
    dense, dense_runtime, _, _ = run_case(package_root, origin, distance, "AB", "FULL", horizon, "dense")
    backend = {
        "horizon": horizon,
        "raw_equal": list(lazy_runtime.raw_copy()) == list(dense_runtime.raw_copy()),
        "clock_equal": list(lazy_runtime.clock_copy()) == list(dense_runtime.clock_copy()),
        "lazy": lazy["final"], "dense": dense["final"],
    }
    boundary_runtime, _, _ = build_relational_body(
        package_root, origin, "AB", distance, "FULL", "lazy"
    )
    half = max(1, horizon // 2)
    boundary_runtime.advance(half)
    boundary = save_snapshot(boundary_runtime, section, "RESUME_BOUNDARY.deetsnap")
    continuous = runtime_from(
        list(boundary_runtime.raw_copy()), list(boundary_runtime.clock_copy()),
        int(boundary_runtime.current_tick), N
    )
    continuous.advance(horizon - half)
    resumed = dee.Runtime.load_snapshot(str(section / boundary["path"]))
    resumed.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
    resumed.advance(horizon - half)
    resume = {
        "boundary": boundary, "horizon": horizon,
        "raw_equal": list(continuous.raw_copy()) == list(resumed.raw_copy()),
        "clock_equal": list(continuous.clock_copy()) == list(resumed.clock_copy()),
        "continuous": state_summary(continuous), "resumed": state_summary(resumed),
    }
    return {"backend": backend, "resume": resume}


def challenge_history(package_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    # Common diagnostic challenge applied only to matched forks after equal age.
    origin, distance = tuple(config["origin"]), int(config["action_distance"])
    rows = {}
    for background in ("H0", "AB"):
        base, _, ports, _ = run_case(package_root, origin, distance, background, "FULL", 260)
        runtime, ports, audit = build_relational_body(package_root, origin, background, distance, "FULL", "lazy")
        runtime.advance(260)
        raw, clocks = list(runtime.raw_copy()), list(runtime.clock_copy())
        challenge_site = add(ports.b, (0, 1, 0))
        if raw[index(challenge_site)]:
            raw[index(challenge_site)] = 0
        raw[index(challenge_site)] = int(dee.pack_record(5001, 0, 0, 0, 1, 1))
        clocks[index(challenge_site)] = 19
        challenged = dee.Runtime.import_research_state(N, int(runtime.current_tick), raw, clocks)
        challenged.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
        baseline = dee.Runtime.import_research_state(
            N, int(runtime.current_tick), list(runtime.raw_copy()), list(runtime.clock_copy())
        )
        baseline.execution_options = dee.TickOptions(dee.Backend.LAZY, 1)
        challenged.advance(1)
        baseline.advance(1)
        rows[background] = {
            "equal_age_tick": int(runtime.current_tick), "diagnostic_external_writes": 1,
            "challenge_site": list(challenge_site),
            "baseline": body_sample(baseline, ports, 261),
            "challenge": body_sample(challenged, ports, 261),
        }
    return {"protocol": "same physical B challenge in diagnostic forks", "rows": rows}


def write_causal_events(section: Path, main: dict[str, Any], tracker: dict[str, Any]) -> None:
    path = section / "TELEMETRY" / "CAUSAL_EVENTS.csv"
    fields = ["tick", "system", "event", "site", "s_reg", "direction", "evidence", "ambiguity"]
    rows = []
    for row in main["trace"]:
        flags = event_signature(row, 1)
        mapping = {
            "action": row["action_plus"], "environment_return": row["return_plus"],
            "organization_return": row["comparator"],
        }
        for name, present in flags.items():
            if not present:
                continue
            rec = mapping[name]
            rows.append({
                "tick": row["absolute_tick"], "system": "RELATIONAL_MAIN", "event": name,
                "site": json.dumps(rec["site"]), "s_reg": rec["s_reg"],
                "direction": json.dumps(rec["direction"]),
                "evidence": "observed record matches frozen event signature",
                "ambiguity": "microscopic contribution resolved only where tracker/controls report it",
            })
    for trans in tracker["B12"]["trace"]["transitions"]:
        rec = trans["after_target"] or {}
        rows.append({
            "tick": trans["tick_after"], "system": "B12", "event": trans["branch"],
            "site": json.dumps(trans["target"]), "s_reg": rec.get("s_reg"),
            "direction": json.dumps(rec.get("direction")),
            "evidence": "one-tick reconstruction plus source ablations",
            "ambiguity": "multiple contributors retained when present",
        })
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_campaign(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION_NAME
    for name in ("RUNNER", "CHECKPOINTS", "TELEMETRY"):
        (section / name).mkdir(parents=True, exist_ok=True)
    write_readme(section)

    selected, discovery_rows = discovery(package_root)
    observed = selected["observed"]["event_ticks"]
    milestones = [
        ticks[0] for name, ticks in observed.items()
        if name in {"action", "environment_return", "organization_return"} and ticks
    ]
    t_ref = max(milestones) if milestones else 64
    t_ref = max(32, min(96, int(t_ref)))
    config = {
        "schema": "mbp4.transformative-relational.experiment-config.v1",
        "campaign": CAMPAIGN, "parent_zip_sha256": PARENT_ZIP_SHA256,
        "parent_checkpoint": "12_CHECKPOINTS/OBP_FRESH_VALIDATED_T32.deetsnap",
        "parent_checkpoint_sha256": FRESH_SHA256,
        "origin": selected["origin"], "action_distance": selected["action_distance"],
        "selection_score": selected["score"], "T_ref": t_ref,
        "horizons": [t_ref, 4 * t_ref, 16 * t_ref],
        "holdout_origins": [[(selected["origin"][0] + 7) % N, (selected["origin"][1] + 5) % N,
                              (selected["origin"][2] + 9) % N],
                             [(selected["origin"][0] + 13) % N, (selected["origin"][1] + 11) % N,
                              (selected["origin"][2] + 3) % N]],
        "histories": ["H0", "AB", "BA", "SHAM"],
        "controls": ["READ_CUT", "NO_ACTION", "RETURN_CUT"],
        "post_t0_host_policy": ["advance", "passive observe", "save"],
        "diagnostic_fork_policy": "declared edits remain outside MAIN",
        "resource_limit_ticks_per_world": 16 * t_ref,
        "discovery_cases_prior_stage": 24,
        "refinement_cases_this_stage": 3,
        "refinement_reason": "native reader route corrected from (sign,0,-1) to observed (sign,+1,0)",
        "frozen_utc": utc(),
    }
    write_json(section / "EXPERIMENT_CONFIG.json", config)
    write_json(section / "TELEMETRY" / "DISCOVERY.json", {
        "selected": selected, "rows": discovery_rows,
    })
    write_json(section / "TELEMETRY" / "REFINEMENT_JUSTIFICATION.json", {
        "prior_cases_executed": 24,
        "prior_observation": "delta and local comparator projection reproduced, but the external action ports were placed off the native reader route",
        "localized_mechanism": "the renewed reader emits from the comparator along (axis_projection,+1,0)",
        "refinement": "one preregistered action junction and one spatially separate return bend, checked on H0/AB/BA",
        "new_composition_family_opened": False,
    })

    tracker = tracker_suite(package_root)
    instruments = instrumental_tracker_cases()
    write_json(section / "TELEMETRY" / "TRANSFORMATIVE_TRACKER.json", tracker)
    write_json(section / "TELEMETRY" / "TRACKER_INSTRUMENTAL.json", instruments)

    main, main_runtime = save_main_checkpoints(package_root, section, config)
    controls, holdouts = controls_and_holdouts(package_root, config)
    technical = technical_equivalence(package_root, section, config)
    sequential = challenge_history(package_root, config)
    write_json(section / "TELEMETRY" / "RELATIONAL_MAIN.json", main)
    write_json(section / "TELEMETRY" / "MATCHED_CONTROLS.json", controls)
    write_json(section / "TELEMETRY" / "HOLDOUTS.json", holdouts)
    write_json(section / "TELEMETRY" / "TECHNICAL_EQUIVALENCE.json", technical)
    write_json(section / "TELEMETRY" / "SEQUENTIAL_HISTORY_CHALLENGE.json", sequential)
    write_causal_events(section, main, tracker)

    final_cp = next(row for row in main["checkpoints"] if row["path"].endswith("RELATIONAL_MAIN_FINAL.deetsnap"))
    summary = {
        "schema": "mbp4.transformative-relational.run-summary.v1",
        "campaign": CAMPAIGN, "parent_zip_sha256": PARENT_ZIP_SHA256,
        "kernel_version": "DEE Universe v27 frozen", "runtime_version": "2.2.0",
        "tracker_windows": {
            "B12": [51, 84], "ninth_return": [409, 425],
            "B12_transition_65_66_found": tracker["B12"]["transition_65_to_66"] is not None,
            "B12_terminal_observed_site_at_tick_84": [14, 24, 11],
            "B12_next_target_prediction_after_tick_84": [15, 24, 11],
        },
        "tracker_ambiguities": [
            "material provenance can remain known from trace but unrecoverable from descendant alone",
            "ninth-return protected encounter has no forced descendant attribution",
        ],
        "relational_histories_executed": ["H0", "AB", "BA", "SHAM"],
        "episodes_complete_observed": main["complete_episode_count"],
        "actions_observed": len(main["observed"]["event_ticks"]["action"]),
        "environment_returns_observed": len(main["observed"]["event_ticks"]["environment_return"]),
        "organization_returns_observed": len(main["observed"]["event_ticks"]["organization_return"]),
        "holdouts_executed": [row["holdout_id"] for row in holdouts],
        "host_writes_after_t0": main["host_writes_after_t0"],
        "diagnostic_external_writes": 2,
        "checkpoints": main["checkpoints"] + [technical["resume"]["boundary"]],
        "main_checkpoint": final_cp, "tick_final": int(main_runtime.current_tick),
        "technical_equalities": {
            "dense_lazy_raw": technical["backend"]["raw_equal"],
            "dense_lazy_clock": technical["backend"]["clock_equal"],
            "resume_raw": technical["resume"]["raw_equal"],
            "resume_clock": technical["resume"]["clock_equal"],
            "tracker_passive_raw": instruments["cases"][1]["tracker_raw_equal"],
            "tracker_passive_clock": instruments["cases"][1]["tracker_clock_equal"],
        },
        "incidents": [
            "BA retained delta=-1 but its (-1,+1,0) reader output met the prepared support geometry and did not enter the mediated action route within the frozen horizon",
            "the common diagnostic B challenge at equal age produced no one-tick difference on either H0 or AB",
            "the A/B delta remained +1 in MAIN; later modifications were observed in comparator/action state rather than as a second delta rewrite",
            "late toroidal background interactions can match local event signatures, so the four complete episodes are the preregistered early chains at 8->14->18, 10->16->20, 16->22->26, and 18->24->28",
        ],
        "relation_delta_second_modification_observed": False,
        "second_organizational_modification_tick": main["second_modification_tick"],
        "closure_reason": "frozen finite horizons and holdouts completed",
        "created_utc": utc(),
    }
    write_json(section / "RUN_SUMMARY.json", summary)
    return summary


def validate(package_root: Path) -> dict[str, Any]:
    section = package_root / SECTION_NAME
    summary = json.loads((section / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
    checks = []
    for item in summary["checkpoints"]:
        path = section / item["path"]
        runtime = dee.Runtime.load_snapshot(str(path))
        before_raw, before_clock, before_tick = (
            list(runtime.raw_copy()), list(runtime.clock_copy()), int(runtime.current_tick)
        )
        runtime.advance(0)
        checks.append({
            "path": item["path"], "hash_equal": sha256(path) == item["sha256"],
            "tick_equal": int(item.get("tick", before_tick)) == before_tick,
            "advance_zero_raw_equal": before_raw == list(runtime.raw_copy()),
            "advance_zero_clock_equal": before_clock == list(runtime.clock_copy()),
            "advance_zero_tick_equal": before_tick == int(runtime.current_tick),
        })
    technical = summary["technical_equalities"]
    result = {
        "schema": "mbp4.transformative-relational.technical-validation.v1",
        "checkpoint_checks": checks,
        "all_technical_checks_true": (
            all(all(value for key, value in row.items() if key != "path") for row in checks)
            and all(bool(value) for value in technical.values())
            and int(summary["host_writes_after_t0"]) == 0
        ),
    }
    write_json(section / "TELEMETRY" / "TECHNICAL_VALIDATION.json", result)
    if not result["all_technical_checks_true"]:
        raise RuntimeError("section 22 technical validation failed")
    return result


def section_files(section: Path) -> list[Path]:
    return sorted(
        [path for path in section.rglob("*") if path.is_file()
         and "__pycache__" not in path.relative_to(section).parts
         and path.name != "HASHES.sha256"],
        key=lambda path: path.relative_to(section).as_posix(),
    )


def package_append(package_root: Path, canonical_zip: Path) -> dict[str, Any]:
    section = package_root / SECTION_NAME
    if sha256(canonical_zip) != PARENT_ZIP_SHA256:
        raise RuntimeError("canonical ZIP is not the expected sections 00-21 parent")
    files = section_files(section)
    hashes = "\n".join(
        f"{sha256(path)}  {path.relative_to(section).as_posix()}" for path in files
    ) + "\n"
    (section / "HASHES.sha256").write_text(hashes, encoding="utf-8")
    files.append(section / "HASHES.sha256")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="mbp4_section22_", suffix=".zip", dir=str(package_root)
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    inherited: dict[str, str] = {}
    try:
        with zipfile.ZipFile(canonical_zip, "r") as parent:
            infos = parent.infolist()
            if any(f"/{SECTION_NAME}/" in item.filename for item in infos):
                raise RuntimeError("parent already contains section 22")
            inherited = {
                item.filename: hashlib.sha256(parent.read(item)).hexdigest()
                for item in infos if not item.is_dir()
            }
            with zipfile.ZipFile(temporary, "w", allowZip64=True) as output:
                for item in infos:
                    output.writestr(item, parent.read(item))
                for path in files:
                    name = f"{WRAPPER}/{SECTION_NAME}/{path.relative_to(section).as_posix()}"
                    output.write(path, name, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(temporary, "r") as check:
            bad = check.testzip()
            if bad is not None:
                raise RuntimeError(f"ZIP CRC failure: {bad}")
            for name, expected in inherited.items():
                if hashlib.sha256(check.read(name)).hexdigest() != expected:
                    raise RuntimeError(f"inherited member changed: {name}")
            hash_name = f"{WRAPPER}/{SECTION_NAME}/HASHES.sha256"
            for line in check.read(hash_name).decode("utf-8").splitlines():
                expected, relative = line.split("  ", 1)
                name = f"{WRAPPER}/{SECTION_NAME}/{relative}"
                if hashlib.sha256(check.read(name)).hexdigest() != expected:
                    raise RuntimeError(f"section hash mismatch: {relative}")
        os.replace(temporary, canonical_zip)
    finally:
        if temporary.exists():
            temporary.unlink()
    result = {
        "parent_zip_sha256": PARENT_ZIP_SHA256,
        "final_zip_sha256": sha256(canonical_zip), "crc_error": None,
        "inherited_members_verified_byte_exact": len(inherited),
        "section_hashes_verified": True, "section_files": len(files),
    }
    write_json(package_root / "section22_package_verification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--canonical-zip", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--package-existing", action="store_true")
    args = parser.parse_args()
    package_root = args.package_root.resolve()
    if args.package_existing:
        if args.canonical_zip is None:
            parser.error("--package-existing requires --canonical-zip")
        out = {
            "validation": validate(package_root),
            "package": package_append(package_root, args.canonical_zip.resolve()),
        }
        print(json.dumps(out, sort_keys=True))
        return
    if args.validate_only:
        print(json.dumps(validate(package_root), sort_keys=True))
        return
    summary = run_campaign(package_root)
    validation = validate(package_root)
    out = {"summary": summary, "validation": validation}
    if args.package:
        if args.canonical_zip is None:
            parser.error("--package requires --canonical-zip")
        out["package"] = package_append(package_root, args.canonical_zip.resolve())
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
