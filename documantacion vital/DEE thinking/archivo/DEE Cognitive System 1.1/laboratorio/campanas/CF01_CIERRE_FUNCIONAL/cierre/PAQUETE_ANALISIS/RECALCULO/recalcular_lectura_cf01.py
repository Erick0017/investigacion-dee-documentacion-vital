"""Compact existing-primary readout. No engine import, Runtime or new ticks.

The full input primaries remain authoritative. Output records native scalar,
direction and RAW transitions, not a table of inferred correct responses.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIELDS = ("A", "B", "own", "private_B", "context_A", "B_datum", "query_gate")
_SPEC = importlib.util.spec_from_file_location("cf01_snapshot_observer", HERE/"observador_snapshot_existente.py")
OBSERVER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(OBSERVER)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig") as stream:
        return json.load(stream)


def exact_obs(value):
    if isinstance(value, list):
        return [exact_obs(q) for q in value]
    if not isinstance(value, dict) or "raw" not in value:
        return value
    raw = value["raw"]
    if not isinstance(raw, str) or not raw.isdecimal():
        raise ValueError("RAW must remain an exact decimal string")
    decoded = OBSERVER.fields(int(raw))
    for key in ("raw", "state", "s_reg", "direction", "semantic"):
        if key in value and value[key] != decoded[key]:
            raise ValueError("Observation disagrees with packed RAW: " + key)
    if "clock" in value and not str(value["clock"]).isdecimal():
        raise ValueError("Clock is not an exact nonnegative integer")
    return {k: value[k] for k in ("tick", "site", "raw", "clock", "state", "s_reg", "semantic", "direction") if k in value}


def signature(value):
    if isinstance(value, list):
        return tuple(signature(q) for q in value)
    if isinstance(value, dict) and "raw" in value:
        return value["raw"]
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def frame_transitions(frames):
    result = {}
    for key in FIELDS:
        present = [q for q in frames if key in q]
        if not present:
            continue
        changes = []
        previous = None
        for frame in present:
            value = exact_obs(frame[key])
            mark = signature(value)
            if not changes or mark != previous:
                changes.append({"tick": frame["tick"], "value": value})
                previous = mark
        result[key] = {"samples": len(present), "RAW_transitions": changes,
                       "final_sample": {"tick": present[-1]["tick"], "value": exact_obs(present[-1][key])}}
    return result


def request_rows(value):
    out = []
    seen = set()
    for q in value or []:
        if not isinstance(q, dict):
            continue
        r = q.get("receipt", {})
        key = (q.get("id", r.get("id")), q.get("port"), q.get("tick"))
        if key in seen:
            continue
        seen.add(key)
        out.append({k: q[k] for k in ("id", "port", "site", "direction", "tick", "payload", "semantic") if k in q} |
                   {"status": r.get("status", "receipt_missing"),
                    "effective_tick": r.get("effective_tick"), "reason": r.get("reason", "")})
    return out


def waypoint_readout(frames):
    """Per-location transitions, without printing or inventing whole frames."""
    grouped = {}
    for frame in frames:
        for branch, observations in frame.get("message_waypoints", {}).items():
            for value in observations:
                observation = exact_obs(value)
                key = branch + ":" + ",".join(map(str, observation["site"]))
                item = grouped.setdefault(key, {"branch": branch, "site": observation["site"], "samples": 0, "RAW_transitions": []})
                item["samples"] += 1
                if not item["RAW_transitions"] or item["RAW_transitions"][-1]["raw"] != observation["raw"]:
                    item["RAW_transitions"].append(observation)
                item["final_sample"] = observation
    blocked = []
    for first, later in zip(frames, frames[1:]):
        if later["tick"] != first["tick"] + 1:
            continue
        for branch, observations in first.get("message_waypoints", {}).items():
            if len(observations) < 3:
                continue
            incoming, head = observations[1:3]
            after_list = later.get("message_waypoints", {}).get(branch, [])
            if len(after_list) < 3:
                continue
            after = after_list[2]
            points_at_head = all((incoming["site"][i]+incoming["direction"][i]) % 26 == head["site"][i] for i in range(3))
            if (incoming["state"] > 0 and incoming["semantic"] == 1 and points_at_head
                    and head["state"] > 0 and head["semantic"] == 1 and after["raw"] == "0"):
                blocked.append({"tick_before": first["tick"], "tick_after": later["tick"], "branch": branch,
                    "incoming": exact_obs(incoming), "occupied_turn_before": exact_obs(head), "turn_after": exact_obs(after),
                    "native_rule": "Nonempty normal head uses matter rule, not the empty-destination directional reducer. Observed next RAW0 implies rule_value0; incoming does not fuse with the old turn carrier.",
                    "support_bound_not_full_neighbour_measurement": "At least one live incoming neighbour; rule_value0 requires no tetrahedral strong condition and at most5 ordinary alive neighbours. Full Moore26 was not recorded in this trace.",
                    "scope": "This identifies local transport exclusion, not global information destruction or incapacity of B."})
    return {"locations": list(grouped.values()), "occupied_turn_deaths_with_incoming": blocked}


def compact_primary(path):
    x = load(path)
    envelope = x.get("result", {})
    instrument = envelope.get("INSTRUMENTO", {}) if isinstance(envelope, dict) else {}
    data = envelope.get("result", envelope) if isinstance(envelope, dict) else {}
    out = {"case": x.get("case", path.stem), "source": str(path), "source_bytes": path.stat().st_size,
           "source_sha256": digest(path), "returncode": x.get("returncode"),
           "code_revision_sha256": x.get("code_revision_sha256"),
           "instrument": instrument, "scope": "Archived recalculation only; zero new ticks"}
    if not isinstance(data, dict):
        out["result_kind"] = type(data).__name__
        return out
    if "frames" in data:
        frames = ([data["before"]] if isinstance(data.get("before"), dict) and "tick" in data["before"] else []) + data["frames"]
        out["interval"] = [frames[0]["tick"], frames[-1]["tick"]] if frames else None
        out["field_transitions"] = frame_transitions(frames)
        if any("message_waypoints" in q for q in frames):
            out["message_waypoints"] = waypoint_readout(frames)
    requests = list(data.get("requests", []))
    if isinstance(data.get("request"), dict):
        requests.append(data["request"])
    out["requests"] = request_rows(requests)
    out["receipt_statuses"] = dict(Counter(q["status"] for q in out["requests"]))
    if isinstance(data.get("rows"), list):
        rows = []
        for row in data["rows"]:
            if not isinstance(row, dict):
                continue
            compact = {k: row[k] for k in ("index", "critical_tick", "availability", "useful_material_actions",
                       "failed_material_actions", "emitted_motor_actions", "wrong_unreturned_actions",
                       "query_material", "conflict", "no_motor_output") if k in row}
            frames = row.get("frames", [])
            if frames:
                compact["sample_ticks"] = [q["tick"] for q in frames]
                compact["own_reference_first_last"] = [exact_obs(frames[j].get("M", frames[j].get("own"))) for j in (0,-1)]
                compact["B_first_last"] = [exact_obs(frames[j].get("B")) for j in (0,-1)]
                compact["A_first_last"] = [exact_obs(frames[j].get("A")) for j in (0,-1)]
                compact["context_recorded_in_frames"] = any("context_A" in q for q in frames)
            rows.append(compact)
        out["opportunities"] = rows
        out["opportunity_totals"] = {"requested": len(rows),
           "with_useful_contact": sum(bool(q.get("useful_material_actions")) for q in rows),
           "with_failed_product": sum(bool(q.get("failed_material_actions")) for q in rows),
           "with_motor_emission": sum(bool(q.get("emitted_motor_actions")) for q in rows),
           "with_query_at_contact_sample": sum(bool(q.get("query_material")) for q in rows),
           "no_motor_output": sum(bool(q.get("no_motor_output")) for q in rows),
           "conflict": sum(bool(q.get("conflict")) for q in rows)}
    final = data.get("final", {})
    if isinstance(final, dict) and "regions" in final:
        regions = final["regions"]
        out["final_references"] = {"own": exact_obs(regions.get("memories", {}).get("A", [])),
                                  "private_B": exact_obs(regions.get("memories", {}).get("B", []))}
    out["physical_after"] = envelope.get("physical", {}) if isinstance(envelope, dict) else {}
    out["limitations"] = ["A sampled native query is not an independent learner or exclusive act/ask decision.",
                           "A missing field was not reconstructed from its expected answer.",
                           "An admitted input is not by itself a usable response or learning."]
    return out


def snapshot_readout(path):
    s = OBSERVER.Snapshot(path)
    if s.N != 26:
        raise ValueError("This R9 coordinate reader requires N26")
    points = {"A": [[6,14,14]], "own": [[5,15,15],[7,15,15]],
              "context_A": [[5,15,13],[7,15,13]], "B": [[19,14,14]],
              "private_B": [[18,15,15],[20,15,15]], "B_datum": [[20,13,15]],
              "B_source": [[20,13,16]], "message_cuts": [[0,19,9],[12,19,9]],
              "query_cut": [[6,12,12]]}
    return {"snapshot": str(path), "sha256": s.encoded_sha256, "tick": s.tick,
            "checksum_valid": s.checksum_valid, "pending": s.pending,
            "fields": {k: [s.observation(p) for p in positions] for k,positions in points.items()},
            "new_ticks": 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, default=ROOT/"evidencia/campanas/CF01_CIERRE_FUNCIONAL")
    p.add_argument("--case", action="append", default=[])
    p.add_argument("--snapshot", type=Path, action="append", default=[])
    p.add_argument("--compare-snapshots", type=Path, nargs=2, action="append", default=[])
    p.add_argument("--out", type=Path, default=HERE/"LECTURA_PRIMARIOS_CF01.json")
    a = p.parse_args()
    paths = sorted(a.evidence.glob("*.json.gz"))
    if a.case:
        paths = [q for q in paths if q.name.removesuffix(".json.gz") in a.case]
    data = [compact_primary(q) for q in paths]
    result = {"schema": "CF01.compact.readout.v1", "new_ticks": 0,
              "raw_observer_source_sha256": digest(HERE/"observador_snapshot_existente.py"),
              "primaries": data, "snapshots": [snapshot_readout(q) for q in a.snapshot],
              "snapshot_comparisons": [{"a": str(q), "b": str(z), "a_sha256": digest(q), "b_sha256": digest(z),
                                        "comparison": OBSERVER.compare(OBSERVER.Snapshot(q), OBSERVER.Snapshot(z), sample_limit=8)}
                                       for q,z in a.compare_snapshots],
              "limits": "Primary frame coverage varies; exact complete snapshot fields are boundary samples, not invented intermediate histories."}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"output": str(a.out), "primary_count": len(data), "snapshots": len(a.snapshot), "new_ticks": 0,
                      "cases": [{"case": q["case"], "returncode": q["returncode"],
                                 "receipt_statuses": q.get("receipt_statuses",{}),
                                 "totals": q.get("opportunity_totals",{})} for q in data]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
