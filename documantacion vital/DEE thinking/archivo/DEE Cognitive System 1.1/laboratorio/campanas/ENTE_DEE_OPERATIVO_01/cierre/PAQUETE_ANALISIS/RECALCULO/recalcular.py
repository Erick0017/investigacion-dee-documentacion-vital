"""Recalculo archivado EO01. Solo stdlib; no carga DEE ni avanza vidas.

Uso: python recalcular.py --evidencia EVIDENCIA_CAUSAL --salida RECALCULADO
Los veredictos del servicio se cotejan, no se usan para elegir acciones.
RAW y clocks permanecen enteros exactos (strings JSON originales conservados).
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    with gzip.open(path, "rt", encoding="utf8") if path.suffix == ".gz" else path.open(encoding="utf8") as f:
        return json.load(f)


def exact_observations(value):
    """Check redundant RAW/state/register fields without any float conversion."""
    total = 0
    if isinstance(value, dict):
        if all(k in value for k in ("raw", "clock", "state", "s_reg")):
            raw, clock = value["raw"], value["clock"]
            if type(raw) not in (str, int) or type(clock) not in (str, int):
                raise ValueError("RAW/clock was not stored exactly")
            r, c = int(raw), int(clock)
            if not 0 <= r < 2**64 or not 0 <= c < 2**64:
                raise ValueError("Not an exact uint64")
            if (r & 0xffffffff) != value["state"] or ((r >> 32) & 0xffff) != value["s_reg"]:
                raise ValueError("Redundant RAW state/s_reg disagrees")
            total += 1
        for v in value.values():
            total += exact_observations(v)
    elif isinstance(value, list):
        for v in value:
            total += exact_observations(v)
    return total


def decoder(frames, critical):
    samples = []
    for tick in (critical - 16, critical - 15):
        matching = [f for f in frames if f.get("tick") == tick]
        if len(matching) != 1:
            raise ValueError("Missing or duplicated fixed motor sample at " + str(tick))
        contacts = matching[0]["contacts"]
        roles = []
        for role in (-1, 0, 1):
            q = contacts[str(role)]
            if q["state"] > 0 and q["semantic"] == 1 and q["direction"] in ([role, -1, -1], [role, -1, 0]):
                roles.append(role)
        samples.append({"tick": tick, "material_roles": roles,
                        "command": (1 if roles[0] >= 0 else -1) if len(roles) == 1 else None,
                        "simultaneous_conflict": len(roles) > 1})
    if samples[-1]["simultaneous_conflict"]:
        chosen, reason = None, "deadline_conflict"
    else:
        chosen = next((s for s in reversed(samples) if s["command"] is not None), None)
        reason = "no_native_output" if chosen is None else "current" if chosen["tick"] == critical - 15 else "fixed_hold_one_tick"
    return {"rule": "latest_unique_with_max_hold1tick.v1", "samples": samples,
            "command": None if chosen is None else chosen["command"],
            "source_tick": None if chosen is None else chosen["tick"], "reason": reason}


def receipt_counts(requests):
    statuses = Counter(q.get("receipt", {}).get("status", "missing") for q in requests)
    ids = [q.get("id") for q in requests]
    if len(ids) != len(set(ids)):
        raise ValueError("A submitted request ID is repeated inside one episode")
    for q in requests:
        receipt = q.get("receipt", {})
        if receipt.get("id") != q.get("id"):
            raise ValueError("Receipt ID mismatch")
        if "requested_tick" in receipt and receipt["requested_tick"] != q["tick"]:
            raise ValueError("Requested receipt time differs from request")
    return {"requested": len(requests), "applied": statuses["applied"],
            "rejected": sum(v for k, v in statuses.items() if "reject" in k),
            "pending": sum(v for k, v in statuses.items() if "pending" in k or "queue" in k),
            "status_counts": dict(sorted(statuses.items()))}


def registers(witness, key):
    return [q["s_reg"] for q in witness.get(key, [])]


def legacy_social_auxiliary(doc):
    """Keep old CF social probes separate from actual-external EO01 episodes."""
    blocks = []
    for index, block in enumerate(doc["blocks"]):
        private = block.get("private_input", block.get("native_query_calibration"))
        if private is None:
            raise ValueError("Unrecognized archived social probe")
        action = block.get("common_action", block.get("native_query_calibration"))
        decoded = None if action is None else decoder(action["frames"], action["row"]["critical_tick"])
        if decoded is not None and block.get("fixed_reader") != decoded:
            raise ValueError("Legacy social fixed reader differs from archived frames")
        requests = [*private.get("requests", []), *block.get("private_requests", [])]
        if action is not None and action is not private:
            requests += action.get("requests", [])
        busses = []
        waypoint_frames = block.get("passive_waypoints", [])
        for f in waypoint_frames:
            for name, dx, site in (("minus", -1, [12, 19, 9]), ("plus", 1, [0, 19, 9])):
                q = next((q for q in f["message_waypoints"][name] if q["site"] == site), None)
                if q and q["state"] > 0 and q["semantic"] == 1 and q["direction"] == [dx, 0, 0]:
                    busses.append({"tick": f["tick"], "side": name, "s_reg": q["s_reg"], "raw": q["raw"], "direction": q["direction"]})
        blocks.append({"index": index, "before_tick": private["before"]["tick"],
            "after_tick": (private if action is None else action)["after"]["tick"],
            "own_before": registers(private["before"], "own"),
            "own_after": registers((private if action is None else action)["after"], "own"),
            "context_before": registers(private["before"], "context_A"),
            "context_after_private": registers(private["after"], "context_A"),
            "context_after_common": None if action is None else registers(action["after"], "context_A"),
            "private_B_before": registers(private["before"], "private_B"),
            "private_B_after": registers((private if action is None else action)["after"], "private_B"),
            "native_common_command_from_frames": None if decoded is None else decoded["command"],
            "inputs": receipt_counts(requests), "observed_bus_packets": busses,
            "scope": "Legacy CF pulse/query auxiliary; not new external-consequence service, not a scored world-completion trial"})
    return {"case": doc["case"], "life_id": doc["final_record"]["life_id"],
        "parent": doc["fork_record"]["parent"], "arguments": doc["arguments"], "blocks": blocks,
        "native_ticks_executed_by_recalculator": 0,
        "scope": "Separate diagnostic life; its history is not added to MAIN knowledge"}


def environment(episode):
    if "environment_before" in episode:
        before, observed = episode["environment_before"], episode["observed_result"]
        public = before["raw_measurements"]
        ref = before["reference_not_injected"]
        executed = episode["executed_external_command"]
        return public, ref, executed, observed, before["available_gate_not_injected"]
    env = episode["environment"]
    req = {q["port"].rsplit(".", 1)[-1]: q["payload"] for q in episode["requests"] if ".public." in q["port"]}
    public = [req["sin"], req["cos"]]
    observed = {"tick": env["observation_tick"], "movement": env["moved"],
                "contact": env["observed_closed_gate_contact"], "actuator_posture": env["actual_actuator_posture"],
                "job_completed": env["job_completed"]}
    return public, env["reference_not_injected"], env["executed_command"], observed, env["available_gate_not_injected"]


def social_decoder(episode):
    """Fixed B packet reader; never sees raw private datum or desired gate."""
    social = episode.get("social_actuation")
    if social is None:
        return None
    critical = episode["plan"]["critical_tick"]
    tick = critical + 30
    if social["observation_tick"] != tick:
        raise ValueError("B actuator reader time changed")
    buses = social["buses"]
    expected_sites = {"minus": [12, 19, 9], "plus": [0, 19, 9]}
    valid = []
    for name, direction in (("minus", -1), ("plus", 1)):
        q = buses[name]
        if q["site"] != expected_sites[name] or q["tick"] != tick:
            raise ValueError("B fixed motor coordinate/time changed")
        if q["state"] > 0 and q["semantic"] == 1 and q["s_reg"] == 5 and q["direction"] == [direction, 0, 0]:
            valid.append(direction)
    formed = valid[0] if len(valid) == 1 else None
    if social["formed_B_command"] != formed or social["conflict"] != (len(valid) > 1):
        raise ValueError("B fixed reader disagrees with archived raw witnesses")
    frame = next((f for f in episode["frames"] if f["tick"] == tick), None)
    duplicate_bus_equality = None
    if frame is not None and "message_waypoints" in frame:
        found = {name: next(q for q in frame["message_waypoints"][name] if q["site"] == expected_sites[name]) for name in expected_sites}
        duplicate_bus_equality = found == buses
        if not duplicate_bus_equality:
            raise ValueError("Independent frame waypoint and actuation bus witnesses differ")
    row = episode.get("row", {})
    resource = row.get("private_B_raw") is not None
    if social["prepared_opportunity_present"] != resource:
        raise ValueError("P0 opportunity is not fixed from presence of a private environmental request")
    executed = formed if resource and social["B_actuator"] == "closed" else None
    ref = episode["environment_before"]["reference_not_injected"]
    after = ref if executed is None else max(-64, min(64, ref + executed))
    if social["executed_valve_command"] != executed or social["reference_before"] != ref or social["reference_after"] != after:
        raise ValueError("B fixed mechanical actuator law disagrees")
    if social["actual_displacement"] != after - ref:
        raise ValueError("B actual displacement disagrees")
    if episode["environment_after"]["reference_not_injected"] != after:
        raise ValueError("Post-valve environment state disagrees")
    if social["resource_window"] != [tick, tick] or social["pending_resource_after_episode"] != 0 or not social["resource_expired_after_window"]:
        raise ValueError("B P0 opportunity window/state disagrees")
    if social["resource_consumed_by_actuation"] != (executed is not None):
        raise ValueError("B resource consumption differs from actuator use")
    return {"observation_tick": tick, "formed_B_command_from_bus": formed,
            "executed_valve_command": executed, "reference_at_A_action": ref, "reference_for_next_job": after,
            "actual_environment_displacement": after - ref, "fixed_opportunity_present": resource,
            "private_raw_requested": row.get("private_B_raw"), "postformed_cut": row.get("post_formation_message_cut"),
            "B_actuator": social["B_actuator"], "duplicate_frame_bus_equal": duplicate_bus_equality,
            "pending_opportunities_after_episode": 0, "P0_prepared_not_learned_resource_selection": True,
            "scope": "External shared-world valve, not direct new acquisition in occupied A context fields"}


def analyze_episode(ep, case, index):
    plan, frames, requests = ep["plan"], ep["frames"], ep["requests"]
    critical = plan["critical_tick"]
    decoded = decoder(frames, critical)
    reported = ep.get("reader", ep.get("decoder"))
    if reported != decoded:
        raise ValueError("Fixed reader mismatch in " + case)
    public, ref, executed, observed, reported_available = environment(ep)
    available = 1 if public[0] + ref >= public[1] else -1
    if available != reported_available:
        raise ValueError("Environment law mismatch")
    completed = bool(executed is not None and executed == available)
    contact = bool(executed is not None and executed != available)
    if observed["contact"] != contact or observed["job_completed"] != completed or observed["movement"] != (executed is not None):
        raise ValueError("Observed physical environment outcome disagrees")
    supplied = [q for q in requests if ".resource." in q["port"]]
    stages = [int(q["port"].split(".")[-2]) for q in supplied]
    if any(stage == 0 for stage in stages) or len(supplied) != 12:
        raise ValueError("Old stage0 source or incorrect downstream supply count")
    tactile = [q for q in requests if ".tactile." in q["port"]]
    if any(q["tick"] <= observed["tick"] for q in tactile):
        raise ValueError("A consequence does not follow execution")
    if not plan.get("all_j0_sources_omitted"):
        raise ValueError("No evidence that old j0 was omitted")
    before, after = ep["before"], ep["after"]
    own_before, own_after = registers(before, "own"), registers(after, "own")
    context_before, context_after = registers(before, "context_A"), registers(after, "context_A")
    row = {"case": case, "episode_index": index, "revision": ep.get("revision"),
           "start_tick": before["tick"], "decision_tick": observed["tick"], "end_tick": after["tick"],
           "raw_public": public, "environment_reference_auditor_only": ref,
           "native_command_from_frames": decoded["command"], "native_reader_reason": decoded["reason"],
           "material_roles": decoded["samples"], "executed_command": executed,
           "observable_contact": contact, "completed_recalculated": completed,
           "native_valid": decoded["command"] is not None, "silence_or_invalid": decoded["command"] is None,
           "deadline_conflict": decoded["reason"] == "deadline_conflict",
           "wrong_executed": executed is not None and not completed,
           "action_annulled_or_neutral": executed is None,
           "own_before": own_before, "own_after": own_after,
           "own_difference_before": own_before[0] - own_before[1], "own_difference_after": own_after[0] - own_after[1],
           "context_before": context_before, "context_after": context_after,
           "private_B_before": registers(before, "private_B"), "private_B_after": registers(after, "private_B"),
           "tactile_inputs": [{"port": q["port"], "tick": q["tick"], "payload": q["payload"], "status": q["receipt"]["status"]} for q in tactile],
           "inputs": receipt_counts(requests), "generic_supplies": len(supplied), "old_j0_inputs": 0,
           "observed_consequence_precedes_material_input": all(q["tick"] > observed["tick"] for q in tactile),
           "social_actuation_recalculated": social_decoder(ep),
           "sampling_scope": "Declared local witnesses plus full checkpoint hashes, not every microscopic collision or unrecorded input"}
    if "row" in ep:
        row["controls"] = {k: ep["row"][k] for k in ("actuator", "feedback", "cut", "phase_offset") if k in ep["row"]}
        if ep["row"]["job_completed"] != completed:
            raise ValueError("Declared verdict disagrees with recomputed environmental effect")
    return row


def analyze_queue(case, payload, analyzed_rows):
    """Recompute fixed FIFO accounting; retry initiative belongs to environment."""
    wrapped = payload["rows"]
    if len(wrapped) != len(analyzed_rows):
        raise ValueError("FIFO analyzed attempt count differs")
    first, final = wrapped[0]["queue_before"], payload["queue"]
    jobs = first["jobs"]
    if final != wrapped[-1]["queue_after"]:
        raise ValueError("Reported final FIFO differs from last transition")
    attempted = set()
    for index, (entry, native) in enumerate(zip(wrapped, analyzed_rows)):
        before, after = entry["queue_before"], entry["queue_after"]
        if index and before != wrapped[index - 1]["queue_after"]:
            raise ValueError("FIFO continuity breaks between attempts")
        if before["jobs"] != jobs or after["jobs"] != jobs:
            raise ValueError("FIFO raw jobs changed during use")
        cursor = before["cursor"]
        if native["raw_public"] != jobs[cursor]:
            raise ValueError("Attempt did not receive exact current pending raw job")
        attempted.add(cursor)
        success = native["completed_recalculated"]
        expected = {"attempts": before["attempts"] + 1,
                    "completed": before["completed"] + int(success),
                    "cursor": cursor + int(success),
                    "first_attempt_completed": before["first_attempt_completed"] + int(success and before["current_job_attempts"] == 0),
                    "current_job_attempts": 0 if success else before["current_job_attempts"] + 1,
                    "last_tick": native["end_tick"]}
        if any(after[k] != v for k, v in expected.items()):
            raise ValueError("FIFO counter/cursor transition disagrees")
        native["queue_job_index"] = cursor
        native["queue_job_attempt"] = before["current_job_attempts"] + 1
    refs = sorted(set(r["environment_reference_auditor_only"] for r in analyzed_rows))
    references = {}
    if len(refs) == 1:
        # Auditor-only controls of this deterministic external queue. These
        # policies never supply a command to a native participant.
        horizon = len(wrapped)
        for name, policy in (("fixed_left", lambda i: 1), ("fixed_right", lambda i: -1),
                             ("alternating_left_first", lambda i: 1 if i % 2 == 0 else -1),
                             ("alternating_right_first", lambda i: -1 if i % 2 == 0 else 1)):
            cursor, attempts, first_completed, this_job_attempts = first["cursor"], 0, 0, first["current_job_attempts"]
            for i in range(horizon):
                if cursor >= len(jobs):
                    break
                this_job_attempts += 1; attempts += 1
                available = 1 if jobs[cursor][0] + refs[0] >= jobs[cursor][1] else -1
                if policy(i) == available:
                    first_completed += int(this_job_attempts == 1)
                    cursor += 1; this_job_attempts = 0
            references[name] = {"attempt_horizon": horizon, "attempts_used": attempts,
                                "jobs_completed_in_call": cursor - first["cursor"], "first_attempt_completions_in_call": first_completed,
                                "post_hoc_descriptive_reference_not_new_native_control": True,
                                "scope": "Archived external-law calculation only; never acts for DEE"}
    return {"case": case, "requested_queue_jobs": len(jobs), "distinct_jobs_attempted_this_call": len(attempted),
            "attempts_this_call": len(wrapped), "completed_jobs_this_call": final["completed"] - first["completed"],
            "first_attempt_completions_this_call": final["first_attempt_completed"] - first["first_attempt_completed"],
            "pending_queue_jobs": len(jobs) - final["cursor"], "final_cursor": final["cursor"],
            "raw_jobs_unchanged_and_pending_repeated": True,
            "reference_values_at_attempt": refs, "external_references": references,
            "initiative": "Fixed environmental FIFO opportunity and retry; no learned native retry-selection claim"}


def run(evidence, codes=None):
    result = {"schema": "EO01.archived_recalculation.v1", "native_ticks_executed": 0,
              "scope": "Exact archived observations, requests and environmental laws; no engine import, new simulation or snapshot restoration",
              "primaries": [], "episodes": [], "queues": [], "legacy_social_auxiliaries": [], "non_episode_material_uses": [], "mismatches": [], "limitations": [
                  "Repeated ticks/queries and forks sharing a parent are not independent learning replicas.",
                  "Source review and Python audit fence are evidence for the inspected information boundary, not an operating-system security proof.",
                  "A local RAW difference or successful outcome alone is not a learned autonomous strategy.",
                  "This tool recalculates archived metrics; it does not reproduce native physics or continue a life."]}
    docs = {}
    source_cache = {}
    for path in sorted(p for p in evidence.rglob("*.json*") if p.name.endswith((".json", ".json.gz"))):
        if "codigo_ejecutado" in path.parts:
            continue
        key = path.relative_to(evidence).as_posix()
        try:
            doc = load(path); docs[key] = doc
            primary = {"path": key, "bytes": path.stat().st_size, "sha256": sha(path),
                       "case": doc.get("case", path.name), "source_revision": doc.get("code_revision_sha256", doc.get("source_sha256")),
                       "returncode": doc.get("returncode"), "recorded_started_utc": doc.get("started_utc"),
                       "exact_observation_fields_checked": exact_observations(doc.get("result", {})) + exact_observations(doc.get("blocks", []))}
            if doc.get("code_revision_sha256"):
                archive = (codes or evidence / "codigo_ejecutado") / doc["code_revision_sha256"]
                revision = doc["code_revision_sha256"]
                if revision in source_cache:
                    primary["archived_source"] = source_cache[revision]
                elif (archive / "INDICE.json").is_file():
                    signatures = load(archive / "INDICE.json")
                    bad = [name for name, expected in signatures.items()
                           if not (archive / name).is_file() or sha(archive / name) != expected]
                    aggregate = hashlib.sha256(json.dumps(signatures, sort_keys=True).encode()).hexdigest()
                    primary["archived_source"] = {"file_count": len(signatures), "mismatched_members": bad,
                        "aggregate_sha256_matches": aggregate == doc["code_revision_sha256"]}
                    source_cache[revision] = primary["archived_source"]
                    if bad or aggregate != doc["code_revision_sha256"]:
                        raise ValueError("Executed source archive integrity differs")
                else:
                    primary["archived_source"] = {"status": "Not included at this input location; archive hash retained"}
            if doc.get("schema") == "EO01.social.aux.primary.v1":
                archive = path.parent / "codigo_ejecutado" / doc["code_digest"]
                index = doc["source_index"]
                aggregate = hashlib.sha256(json.dumps(index, sort_keys=True).encode()).hexdigest()
                if aggregate != doc["code_digest"]:
                    raise ValueError("Legacy social source index aggregate changed")
                bad = []
                if archive.is_dir():
                    for member in index:
                        local = archive.joinpath(*member["path"].replace("\\", "/").split("/"))
                        if not local.is_file() or sha(local) != member["sha256"]:
                            bad.append(member["path"])
                    if bad:
                        raise ValueError("Legacy social archived sources differ: " + str(bad))
                primary["legacy_social_archived_source"] = {"index_aggregate_sha256_verified": True,
                    "members_verified": len(index) if archive.is_dir() else 0,
                    "scope": "Archive absent here" if not archive.is_dir() else "Exact frozen auxiliary source members"}
                result["legacy_social_auxiliaries"].append(legacy_social_auxiliary(doc))
            if "stdout" in doc and "result" in doc:
                if json.loads(doc["stdout"]) != doc["result"]:
                    raise ValueError("Duplicate full stdout and parsed result disagree")
                primary["stdout_result_identical"] = True
            envelope = doc.get("result", {})
            payload = envelope.get("result", {}) if isinstance(envelope, dict) else {}
            primary["instrument"] = envelope.get("INSTRUMENTO")
            primary["fence"] = envelope.get("INSTRUMENTO_FENCE")
            if path.name == "OBSERVACION_EQUIVALENCIA.json":
                result["passive_observer_saved_snapshot_comparison"] = {"original_primary": key,
                    "sha256": primary["sha256"], "comparison": doc.get("comparison"),
                    "scope": "Existing full-byte comparison retained. Repeating snapshot parsing requires its identified local complete snapshots; not inferred from output text alone."}
            if isinstance(payload, dict) and "rows" in payload:
                episodes = payload["rows"]
            elif isinstance(payload, dict) and all(k in payload for k in ("plan", "frames", "requests")):
                episodes = [payload]
            else:
                episodes = []
                if isinstance(payload, dict) and all(k in payload for k in ("before", "after", "requests")):
                    result["non_episode_material_uses"].append({"case": key,
                        "before_tick": payload["before"]["tick"], "after_tick": payload["after"]["tick"],
                        "own_before": registers(payload["before"], "own"), "own_after": registers(payload["after"], "own"),
                        "context_before": registers(payload["before"], "context_A"), "context_after": registers(payload["after"], "context_A"),
                        "private_B_before": registers(payload["before"], "private_B"), "private_B_after": registers(payload["after"], "private_B"),
                        "inputs": receipt_counts(payload["requests"]), "scope": "Material pulse, not a scored operational decision"})
            analyzed_for_primary = []
            for index, episode in enumerate(episodes):
                if "native" in episode and "queue_before" in episode:
                    episode = episode["native"]
                if not all(k in episode for k in ("plan", "frames", "requests")):
                    continue
                analyzed = analyze_episode(episode, key, index)
                analyzed["life_id"] = envelope.get("INSTRUMENTO", {}).get("life_id")
                result["episodes"].append(analyzed)
                analyzed_for_primary.append(analyzed)
            if "queue" in payload and episodes:
                result["queues"].append(analyze_queue(key, payload, analyzed_for_primary))
            primary["scored_episodes"] = len(episodes)
            result["primaries"].append(primary)
        except Exception as e:
            result["mismatches"].append({"path": key, "type": type(e).__name__, "detail": str(e)})
    bycase = {}
    for row in result["episodes"]:
        bycase.setdefault(row["case"], []).append(row)
    result["metrics_per_case"] = {}
    for case, rows in bycase.items():
        result["metrics_per_case"][case] = {"attempts": len(rows), "native_valid": sum(r["native_valid"] for r in rows),
            "completed": sum(r["completed_recalculated"] for r in rows), "wrong_executed": sum(r["wrong_executed"] for r in rows),
            "silence_or_invalid": sum(r["silence_or_invalid"] for r in rows), "deadline_conflicts": sum(r["deadline_conflict"] for r in rows),
            "neutral_or_annulled": sum(r["action_annulled_or_neutral"] for r in rows),
            "inputs": {key: sum(r["inputs"][key] for r in rows) for key in ("requested", "applied", "rejected", "pending")},
            "fixed_left_reference": sum(1 == (1 if r["raw_public"][0] + r["environment_reference_auditor_only"] >= r["raw_public"][1] else -1) for r in rows),
            "fixed_right_reference": sum(-1 == (1 if r["raw_public"][0] + r["environment_reference_auditor_only"] >= r["raw_public"][1] else -1) for r in rows)}
        result["metrics_per_case"][case]["fixed_reference_scope"] = "Scored against archived per-attempt environmental state; with social valve this is not a simulated alternative closed-loop trajectory"
        result["metrics_per_case"][case]["social"] = {
            "fixed_B_reader_windows": sum(r["social_actuation_recalculated"] is not None for r in rows),
            "B_commands_formed": sum(r["social_actuation_recalculated"] is not None and r["social_actuation_recalculated"]["formed_B_command_from_bus"] is not None for r in rows),
            "B_valve_commands_executed": sum(r["social_actuation_recalculated"] is not None and r["social_actuation_recalculated"]["executed_valve_command"] is not None for r in rows),
            "P0_opportunities_offered": sum(r["social_actuation_recalculated"] is not None and r["social_actuation_recalculated"]["fixed_opportunity_present"] for r in rows)}
    result["metrics_by_life"] = {}
    result["metrics_by_episode_revision"] = {}
    for target, field in ((result["metrics_by_life"], "life_id"), (result["metrics_by_episode_revision"], "revision")):
        groups = {}
        for row in result["episodes"]:
            groups.setdefault(str(row.get(field)), []).append(row)
        for key, rows in groups.items():
            target[key] = {"episodes": len(rows), "first_recorded_start_tick": min(r["start_tick"] for r in rows),
                "last_recorded_end_tick": max(r["end_tick"] for r in rows),
                "native_valid": sum(r["native_valid"] for r in rows),
                "completed": sum(r["completed_recalculated"] for r in rows),
                "wrong_executed": sum(r["wrong_executed"] for r in rows),
                "neutral_or_annulled": sum(r["action_annulled_or_neutral"] for r in rows),
                "silence_or_invalid": sum(r["silence_or_invalid"] for r in rows),
                "inputs": {key: sum(r["inputs"][key] for r in rows) for key in ("requested", "applied", "rejected", "pending")},
                "scope": "Recorded operational episodes only; auxiliary pulses/observations remain separate, not independent individuals or all historical capacities"}
    result["social_reserved_sequences"] = {}
    for index in (1, 2, 3):
        selected = [r for r in result["episodes"] if re.search(r"SOCIAL_RESERVA" + str(index) + r"_[1-6]\.json\.gz$", r["case"])]
        if selected:
            selected.sort(key=lambda r: r["start_tick"])
            result["social_reserved_sequences"][str(index)] = {
                "cases": [r["case"] for r in selected], "attempts": len(selected),
                "completed": sum(r["completed_recalculated"] for r in selected),
                "native_valid": sum(r["native_valid"] for r in selected),
                "inputs": {key: sum(r["inputs"][key] for r in selected) for key in ("requested", "applied", "rejected", "pending")},
                "actual_B_valve_moves": sum(r["social_actuation_recalculated"] is not None and r["social_actuation_recalculated"]["executed_valve_command"] is not None for r in selected),
                "fixed_left_on_archived_world": sum(1 == (1 if r["raw_public"][0] + r["environment_reference_auditor_only"] >= r["raw_public"][1] else -1) for r in selected),
                "scope": "Single continuous MAIN; six opportunities are not independent individuals. Fixed reference uses recorded world path, not a new interactive run."}
    result["matched_common_opportunities"] = {}
    result["observed_prefix_comparisons"] = []
    for prefix in ("EO01_AUX_R01_", "EO01_AUX_R02_R0_", "EO01_AUX_R02_MINUS_"):
        group = []
        normal_key = prefix + "NORMAL.json.gz"
        normal_doc = docs.get(normal_key)
        normal_payload = None if normal_doc is None else normal_doc.get("result", {}).get("result", {})
        for arm in ("NORMAL", "ANNULLED", "OMIT_RETURN", "DECOUPLED", "SHAM", "CUT"):
            key = prefix + arm + ".json.gz"
            initial = bycase.get(key, [])
            common = bycase.get(prefix + arm + "_COMMON.json.gz", [])
            if not initial:
                continue
            i = initial[0]; c = common[0] if common else None
            group.append({"arm": arm, "initial_native_command": i["native_command_from_frames"],
                "initial_executed_command": i["executed_command"], "initial_contact": i["observable_contact"],
                "initial_own_before": i["own_before"], "initial_own_after": i["own_after"],
                "first_common_native_command": None if c is None else c["native_command_from_frames"],
                "first_common_completed": None if c is None else c["completed_recalculated"],
                "first_common_input": None if c is None else c["raw_public"],
                "same_native_history_continued": None if c is None else i["end_tick"] == c["start_tick"],
                "initial_inputs": i["inputs"], "common_inputs": None if c is None else c["inputs"]})
            current_doc = docs.get(key)
            current = None if current_doc is None else current_doc.get("result", {}).get("result", {})
            if current and normal_payload:
                deadline = i["decision_tick"]
                nframes = [f for f in normal_payload["frames"] if f["tick"] <= deadline]
                cframes = [f for f in current["frames"] if f["tick"] <= deadline]
                np = normal_doc.get("parent_record_at_fork", {}).get("physical")
                cp = current_doc.get("parent_record_at_fork", {}).get("physical")
                result["observed_prefix_comparisons"].append({"normal_case": normal_key, "compared_case": key,
                    "full_fork_RAW_clocks_physical_hashes_equal": None if np is None or cp is None else np == cp,
                    "before_witness_equal": normal_payload["before"] == current["before"],
                    "recorded_frames_through_action_equal": nframes == cframes,
                    "fixed_downstream_supplies_equal": normal_payload["plan"]["supplies"] == current["plan"]["supplies"],
                    "scope": "Whole-world RAW/clocks hashes at exact fork; then equality of recorded local witnesses, not whole snapshots at every tick"})
        if group:
            result["matched_common_opportunities"][prefix] = group
    if all(k in docs for k in ("49_SOCIAL_RESERVA3_6.json.gz", "50_COLA_CONTROL_FORK.json.gz", "51_COLA_MAIN.json.gz", "52_COLA_SIN_RETORNO.json.gz")):
        prior = docs["49_SOCIAL_RESERVA3_6.json.gz"]["result"]
        fork = docs["50_COLA_CONTROL_FORK.json.gz"]["result"]
        main = docs["51_COLA_MAIN.json.gz"]["result"]["result"]["rows"][0]["native"]
        control = docs["52_COLA_SIN_RETORNO.json.gz"]["result"]["result"]["rows"][0]["native"]
        deadline = main["plan"]["decision_deadline"]
        result["FIFO_matched_initial_prefix"] = {
            "prior_snapshot_sha256": prior["INSTRUMENTO"]["snapshot_sha256"],
            "fork_names_exact_prior_snapshot": fork["parent"]["snapshot_sha256"] == prior["INSTRUMENTO"]["snapshot_sha256"],
            "complete_fork_physical_hashes_equal": fork["physical"] == prior["physical"],
            "initial_witnesses_equal": main["before"] == control["before"],
            "local_frames_through_first_action_equal": [f for f in main["frames"] if f["tick"] <= deadline] == [f for f in control["frames"] if f["tick"] <= deadline],
            "initial_generic_schedule_equal": main["plan"]["supplies"] == control["plan"]["supplies"],
            "initial_external_environment_equal": main["environment_before"] == control["environment_before"],
            "scope": "Matched full-state fork and first decision. Later pending jobs diverge as actual completions diverge; not identical-input control for all later attempts."}
    if all(k in docs for k in ("51_COLA_MAIN.json.gz", "53_GUARDADO_MAIN.json.gz", "54_CONTINUACION_NUEVO_PROCESO.json.gz")):
        queue = docs["51_COLA_MAIN.json.gz"]["result"]
        saved = docs["53_GUARDADO_MAIN.json.gz"]["result"]
        continued = docs["54_CONTINUACION_NUEVO_PROCESO.json.gz"]["result"]
        first = continued["result"]["rows"][0]
        result["saved_process_continuation"] = {
            "life_id": continued["INSTRUMENTO"]["life_id"],
            "same_life_identity": queue["INSTRUMENTO"]["life_id"] == saved["INSTRUMENTO"]["life_id"] == continued["INSTRUMENTO"]["life_id"],
            "save_did_not_advance_or_change_RAW_clocks": saved["physical"] == queue["physical"],
            "saved_tick": saved["INSTRUMENTO"]["tick"], "continued_from_tick": first["before"]["tick"],
            "continued_to_tick": continued["INSTRUMENTO"]["tick"],
            "prior_final_witness_equals_new_first_witness": queue["result"]["rows"][-1]["native"]["after"] == first["before"],
            "saved_snapshot_sha256": saved["INSTRUMENTO"]["snapshot_sha256"],
            "new_snapshot_sha256": continued["INSTRUMENTO"]["snapshot_sha256"],
            "scope": "Recorded supervisor launches a fresh manager process for each call; same computer, not an independent second machine or native re-simulation by this tool."}
        final = continued["result"]["final"]
        service = final["service"]
        q = service.get("queue")
        env = service.get("environment", {})
        result["final_MAIN_state_and_backlog_scope"] = {
            "tick": final["witness"]["tick"], "own": registers(final["witness"], "own"),
            "context": registers(final["witness"], "context_A"), "private_B": registers(final["witness"], "private_B"),
            "environment_reference": env.get("reference"), "social_valve_enabled": env.get("social_valve_enabled", False),
            "historical_failed_attempt_records_current_environment": len(env.get("backlog", [])),
            "FIFO_pending_jobs": None if q is None else len(q["jobs"]) - q["cursor"],
            "FIFO_cursor": None if q is None else q["cursor"],
            "scope": "Environment backlog is an append-only record of failed attempts, not the live FIFO cursor or proof that a completed job remains pending. Neither list is participant cognitive memory."}
    manifest = [{"path": p["path"], "bytes": p["bytes"], "sha256": p["sha256"]} for p in result["primaries"]]
    result["input_manifest_sha256"] = hashlib.sha256(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf8")).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidencia", "--primarios", dest="evidencia", required=True, type=Path)
    parser.add_argument("--codigos", type=Path, help="Optional executed-source archive root; default is primaries/codigo_ejecutado")
    parser.add_argument("--salida", required=True, type=Path)
    args = parser.parse_args()
    out = run(args.evidencia.resolve(), None if args.codigos is None else args.codigos.resolve())
    args.salida.mkdir(parents=True, exist_ok=True)
    destination = args.salida / "RECALCULO_RESULTADOS.json"
    destination.write_text(json.dumps(out, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"result": str(destination), "primaries": len(out["primaries"]), "episodes": len(out["episodes"]),
                      "mismatches": out["mismatches"], "native_ticks_executed": 0}, ensure_ascii=False))
    return int(bool(out["mismatches"]))


if __name__ == "__main__":
    raise SystemExit(main())
