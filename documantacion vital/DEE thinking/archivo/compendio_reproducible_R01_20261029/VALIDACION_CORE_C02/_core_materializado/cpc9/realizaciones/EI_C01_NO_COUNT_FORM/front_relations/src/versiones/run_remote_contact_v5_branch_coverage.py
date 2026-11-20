"""Finite exact-data auxiliary execution; external audit never drives native inputs."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    temporary = path.with_name(path.name + ".pending." + str(os.getpid()))
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-src", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--parent", type=Path)
    parser.add_argument("--fork", choices=("cut", "sham"))
    parser.add_argument("--bank", choices=("all", "left.changed", "left.free", "right.changed", "right.free"), default="all")
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(args.base_src.resolve()))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from remote_contact import RemoteContactSession
    from integracion.relational_pair import physical
    from dee_thinking import _native as d
    import dee_thinking
    if dee_thinking.__version__ != "4.5.0" or not Path(dee_thinking.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError("Official isolated 4.5 required")
    if sha(d.__file__) != "17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d":
        raise RuntimeError("Native identity mismatch")
    config = json.loads(args.config.read_text(encoding="utf8"))
    case = next(row for row in config["cases"] if row["id"] == args.case_id)
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    m = {"schema": "CPC9.remote_contact.measurements.v1", "case": case,
        "configuration_sha256": sha(args.config), "status": "RUNNING",
        "preparations": int(not bool(args.parent)), "diagnostic_forks": int(bool(args.fork)),
        "continuations": int(bool(args.parent) and not args.fork), "frames": [], "snapshots": [],
        "host_RAW_clock_edits_on_MAIN": [], "coverage": "Moore27 only at declared boundaries; no inferred unique lineages outside coverage.",
        "engine": {"version": dee_thinking.__version__, "module": dee_thinking.__file__,
            "native_sha256": sha(d.__file__), "python": sys.executable}}
    s = None
    try:
        if args.parent:
            parent = RemoteContactSession.load(args.parent)
            before = physical(parent.world)
            m["parent"] = {"path": str(args.parent), "sha256": sha(args.parent), "physical": before}
            if args.fork:
                edits, rows = [], []
                for item in parent.geometry["remote_contact"]["surfaces"]:
                    if args.bank != "all" and item["id"] != args.bank:
                        continue
                    pre = parent.observe(item["hub"])
                    edit = d.ResearchStateEdit()
                    edit.coordinate = d.Coordinate(*item["hub"])
                    edit.raw = 0 if args.fork == "cut" else int(pre["raw"])
                    edit.label = "CPC9_AUDITOR_ONLY_REMOTE_MEMORY_" + args.fork
                    edits.append(edit)
                    rows.append({"id": item["id"], "pre": pre, "requested_raw": str(edit.raw), "clock_edit": None})
                child = parent.world.diagnostic_fork(edits, True)
                s = RemoteContactSession(child, parent.geometry, parent.export_operational_state(), args.case_id)
                for row in rows:
                    item = next(item for item in parent.geometry["remote_contact"]["surfaces"] if item["id"] == row["id"])
                    row["post"] = s.observe(item["hub"])
                m["edits"] = rows
                m["parent_unchanged"] = before == physical(parent.world)
            else:
                s = parent
        else:
            s = RemoteContactSession.create(identifier=args.case_id, **case.get("preparation", {}))
            s.curriculum(**case.get("curriculum", {}))
        m["geometry"] = s.geometry
        m["initial_physical"] = physical(s.world)
        def save():
            path = args.out / ("T" + str(s.tick) + ".deetsnap.gz")
            storage = s.save(path)
            m["snapshots"].append({"path": path.name, "tick": s.tick,
                "sha256": sha(path), "bytes": path.stat().st_size,
                "physical": physical(s.world), "storage": storage})
        save()
        g = s.geometry["remote_contact"]
        boundaries = set((340, 344, 411, 417, 478, 484, 549, 616,
            g["association_tick"], g["query_tick"], g["use_tick"], g["renew_tick"], g["reuse_tick"]))
        if g.get("regulation",{}).get("mode") != "omitted":
            boundaries |= {347,348,349,350}
        boundaries |= {value - 1 for value in tuple(boundaries)}
        if args.trace:
            boundaries |= set(range(g["association_tick"], g["query_tick"] + 1))
        for tick in sorted(value for value in boundaries if s.tick < value <= case.get("horizon", 616)):
            s.run_until(tick)
            m["frames"].append(s.view())
            if args.trace and g["association_tick"] <= tick <= g["query_tick"]:
                from integracion.relational_pair import move
                m.setdefault("nominal_route_coverage", []).append({"tick": tick,
                    "qualification": "Predetermined unperturbed route, NOT unique lineage after an encounter.",
                    "banks": [{"id": item["id"], "center": move(item["hub"], (0, 1, item["z"]), tick - g["association_tick"]),
                        "Moore27": [s.observe(move(move(item["hub"], (0, 1, item["z"]), tick - g["association_tick"]), (x,y,z)))
                            for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)]}
                        for item in g["surfaces"]]})
                if tick in (349,350):
                    for item in g["surfaces"]:
                        destination=move(item["hub"],(0,1,item["z"]),350-g["association_tick"])
                        gate=d.inspect_write_gate(s.world.runtime,d.Coordinate(*destination),True)
                        m.setdefault("decisive_destination_coverage",[]).append({"tick":tick,"bank":item["id"],"center":destination,
                            "Moore27":[s.observe(move(destination,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],
                            "gate":{key:getattr(gate,key)for key in("absolute_tick","local_clock","center_available","n_active","rule_value","write_protected","branch","demux_status")}})
            if tick in (347,348,349,350) and g.get("regulation",{}).get("mode") != "omitted":
                from integracion.relational_pair import move
                for item in g.get("regulation",{}).get("items",[]):
                    gate=d.inspect_write_gate(s.world.runtime,d.Coordinate(*item["target"]),True)
                    m.setdefault("counterflow_local",[]).append({"tick":tick,"port":item["port"],"center":item["target"],
                        "Moore27":[s.observe(move(item["target"],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],
                        "gate":{key:getattr(gate,key)for key in("absolute_tick","local_clock","center_available","n_active","rule_value","write_protected","branch","demux_status")}})
            if tick in (g["association_tick"], 549, 616):
                save()
            m.update(last_complete_tick=s.tick, requests=s.receipts(),
                remote_contact_observations=s.state["remote_contact_observations"],
                elapsed_seconds=time.monotonic() - started)
            put(args.out / "MEASUREMENTS.json", m)
        m.update(status="EXECUTED", final_physical=physical(s.world),
            receipt_statuses=dict(Counter(row["receipt"]["status"] for row in s.receipts())))
    except BaseException as error:
        m.update(status="TECHNICAL_ERROR", error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
        raise
    finally:
        if s is not None:
            m.update(last_complete_tick=s.tick, requests=s.receipts(),
                remote_contact_observations=s.state["remote_contact_observations"],
                elapsed_seconds=time.monotonic() - started)
            m["component_observations"] = {
                "quantity": s.quantity.state.get("observations", []),
                "mode": s.mode.state.get("captures", []),
                "mode_social": s.mode.state.get("social_captures", []),
                "initiative": s.initiative.state.get("captures", []),
                "magnitude": s.state.get("magnitude_observations", []),
                "contact_social": s.state.get("contact_social_observations", []),
                "contact_regulation": s.state.get("contact_regulation_observations", []),
                "contact_renewal": s.state.get("renewal_observations", [])}
        sources = {}
        for name, module in list(sys.modules.items()):
            path = getattr(module, "__file__", None)
            if path and Path(path).suffix == ".py" and (
                    Path(path).resolve().is_relative_to(args.base_src.resolve()) or
                    Path(path).resolve().is_relative_to(Path(__file__).resolve().parent)):
                sources[str(Path(path).resolve())] = sha(path)
        m["source_sha256"] = sources
        put(args.out / "MEASUREMENTS.json", m)
    summary = [{"tick": row["tick"], "stage": row["stage"], "active": [
        {"id": item["id"], "direction": item["physical"]["direction"], "load": item["physical"]["s_reg"]}
        for item in row["surfaces"] if item["physical"]["active"]]}
        for row in m["remote_contact_observations"] if not row["stage"].startswith("pre_")]
    print(json.dumps({"id": args.case_id, "status": m["status"], "seconds": m["elapsed_seconds"], "remote": summary}), flush=True)


if __name__ == "__main__":
    main()
