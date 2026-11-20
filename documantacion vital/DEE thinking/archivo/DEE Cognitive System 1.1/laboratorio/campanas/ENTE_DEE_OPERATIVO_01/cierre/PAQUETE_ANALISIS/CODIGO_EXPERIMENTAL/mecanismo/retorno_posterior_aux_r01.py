"""EO01 auxiliary fixed tactile-result transduction on exact CF01 descendants.

No engine changes, native memory writes, old contact(j0) resources or old return
are submitted. All general downstream supplies precede the action and are the
same in every arm. Only a subsequently observed external contact emits a
tactile sample carrying the actual actuator posture, not a desired correction.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import gzip
import hashlib
import json
import sys
import time

REVISION = "EO01.aux.post_result.r01"
DEADLINE = "2026-10-25T00:59:18+00:00"
KEY = "DEE.Cognitive.System.1.1.EO01.aux.external_result.v1"
MODES = ("normal", "annulled", "omit_return", "decoupled", "sham", "cut")


def configure(system):
    system = Path(system).resolve()
    if str(system) not in sys.path:
        sys.path.insert(0, str(system))
    from capacidades import cierre_funcional_cf01 as cf
    from capacidades import arquitectura_distribuida_mi02_r8 as body
    from capacidades import integracion_distribuida_mi02_r6 as native
    from dee_thinking.persistence import encode_metadata
    return cf, body, native, encode_metadata


def fixed_plan(a, cf, body):
    g = cf.geometry(a); C = g["A"]
    critical = 391 + 782 * max(0, (a.tick + 90 - 391 + 781) // 782)
    turn = critical - 15
    # j0 is excluded for ALL roles. Availability never selects a resource here.
    original = body.cycle_plan(a, {"Q": C}, 1, critical)
    supplies = []
    for row in original["sources"]:
        role, stage, serial = map(int, row["name"].split(".")[2:])
        if stage == 0:
            continue
        supplies.append({**row, "name": "EO01.post.resource." + str(role) + "." + str(stage) + "." + str(serial),
                         "tick": row["tick"] + 2,
                         "role": "Fixed general downstream resource; identical in all arms, no environmental gate value"})
    tactile = {}
    for role in (-1, 0, 1):
        if role:
            site = body.xyz(a, C, (3 * role, -3, -1))
            direction = [role, -1, 0]; tick = turn + 4
            first_head = body.xyz(a, C, (4 * role, -4, -1)); arrival = turn + 5
        else:
            site = body.xyz(a, C, (0, -4, -1))
            direction = [0, -1, 0]; tick = turn + 5
            first_head = body.xyz(a, C, (0, -5, -1)); arrival = turn + 6
        tactile[str(role)] = {"site": site, "direction": direction, "tick": tick, "payload": 0,
                              "first_head": first_head, "expected_arrival": arrival}
    return {"critical_tick": critical, "decision_deadline": turn, "supplies": supplies,
            "tactile_ports": tactile, "all_j0_sources_omitted": True,
            "downstream_delay_relative_to_CF01": 2,
            "criterion": "Action from fixed native samples; environment contact from actually executed posture; native subsequent relative fields/action are outcomes, not imposed targets."}


def sample(a, cf, body, plan):
    f = cf.witness(a); C = cf.geometry(a)["A"]
    f["contacts"] = {str(r): body.obs(a, body.xyz(a, C, (r, -1, -1))) for r in (-1, 0, 1)}
    f["return_heads"] = {str(r): [body.obs(a, row["head"]) for row in body.cycle_plan(a, {"Q": C}, 1, plan["critical_tick"])["routes"] if row["r"] == r] for r in (-1, 0, 1)}
    f["tactile_entries"] = {r: body.obs(a, port["site"]) for r, port in plan["tactile_ports"].items()}
    return f


def episode(a, *, system, mode="normal", public=(18, 27), environment_reference=9, trace=True):
    if mode not in MODES or len(public) != 2 or any(type(v) is not int or not 0 <= v <= 64 for v in public):
        raise ValueError("Frozen auxiliary mode and two raw public integers0..64 required")
    if datetime.now(timezone.utc) >= datetime.fromisoformat(DEADLINE):
        raise TimeoutError("Original campaign deadline reached; never reset")
    cf, body, native, encode_metadata = configure(system)
    before = cf.witness(a); plan = fixed_plan(a, cf, body)
    u = plan["decision_deadline"]; critical = plan["critical_tick"]
    requests = []
    for row in plan["supplies"]:
        requests.append(body.send(a, row["name"], row["site"], row["direction"], row["tick"], row["payload"]))
    for name, value in zip(("sin", "cos"), public):
        spec = next(q for q in body.get(a)["external_sensors"] if q["name"] == name)
        requests.append(body.send(a, "EO01.post.public." + name, spec["origin"], spec["direction"], critical - 22, value))
    # Samples through the deadline occur BEFORE external execution/result.
    frames = []
    for tick in range(critical - 25, u + 1):
        a.run_until(tick); frames.append(sample(a, cf, body, plan))
    decoded = cf.decode_window({"row": {"critical_tick": critical}, "frames": frames})
    emitted = decoded["command"]
    chosen = next((q for q in decoded["samples"] if q["tick"] == decoded["source_tick"]), None)
    posture = chosen["material_roles"][0] if chosen is not None else None
    executed = emitted if mode != "annulled" else None
    actual_posture = posture if executed is not None else None
    # This is the ENVIRONMENT law, never passed to the native codec/reader.
    available = 1 if public[0] + environment_reference >= public[1] else -1
    moved = executed is not None
    contact = bool(moved and executed != available)
    completed = bool(moved and executed == available)
    environment = {"law": "EO01.fixed_gate_with_distinct_actuator_postures.v1", "observation_tick": u,
                   "reference_not_injected": environment_reference, "available_gate_not_injected": available,
                   "emitted_command": emitted, "emitted_posture": posture, "executed_command": executed,
                   "actual_actuator_posture": actual_posture, "moved": moved,
                   "observed_closed_gate_contact": contact, "job_completed": completed,
                   "posture_rule": "Native0/+ both actuate left but distinct mechanical postures; native- actuates right. No movement has no contact."}
    sensor_role = actual_posture if contact else None
    if mode == "omit_return":
        sensor_role = None
    elif mode == "decoupled" and sensor_role is not None:
        # Explicit diagnostic false proprioception, equal one-event dose.
        sensor_role = -sensor_role if sensor_role else 1
    tactile_request = None
    if sensor_role is not None:
        port = plan["tactile_ports"][str(sensor_role)]
        tactile_request = body.send(a, "EO01.post.tactile." + str(sensor_role), port["site"], port["direction"], port["tick"], port["payload"])
        requests.append(tactile_request)
    intervention = None
    if mode in ("sham", "cut") and actual_posture in (-1, 1):
        role = -actual_posture if mode == "sham" else actual_posture
        p = plan["tactile_ports"][str(role)]
        intervention = body.send(a, "EO01.post.diagnostic." + mode + "." + str(role), p["first_head"], (0, 0, 0), u + 4, 0, sem=4)
        requests.append(intervention)
    times = range(u + 1, critical + 81) if trace else sorted(set((u + 1, u + 4, u + 5, critical, critical + 2, critical + 3, critical + 40, critical + 80)))
    for tick in times:
        a.run_until(tick); frames.append(sample(a, cf, body, plan))
    after = cf.witness(a)
    state = {"revision": REVISION, "mode": mode, "last_environment": environment,
             "last_tactile_role": sensor_role, "last_tick": a.tick,
             "host_does_not_write_learned_fields": True}
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(state))
    ns = native.saved(a); ns["index"] += 1; native.put(a, ns)
    view = body.get(a); view["index"] = ns["index"]; body.put(a, view)
    return {"revision": REVISION, "deadline_utc": DEADLINE, "before": before, "plan": plan,
            "requests": body.receipts(a, requests), "decoder": decoded, "environment": environment,
            "tactile_role_returned": sensor_role, "tactile_request_id": None if tactile_request is None else tactile_request["id"],
            "intervention_id": None if intervention is None else intervention["id"], "frames": frames, "after": after,
            "attribution": "General supplies fixed; actual post-actuation contact+posture transduced to a material sample. No old j0 return, no target direction or memory correction computed for the participant.",
            "limitations": ["Prepared transduction/return anatomy; not learned sensor construction or routing.", "Decoupled/sham/cut are identified diagnostic interventions, never native choices."]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", type=Path, required=True)
    p.add_argument("--life", required=True)
    p.add_argument("--parent", default="CF01_MAIN")
    p.add_argument("--mode", choices=MODES, required=True)
    p.add_argument("--public", default="18,27")
    p.add_argument("--reference", type=int, default=9)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if not args.life.startswith("EO01_AUX_"):
        raise ValueError("Auxiliary life namespace required; never mutate MAIN")
    if args.out.exists():
        raise FileExistsError("Prior primary is protected")
    public = tuple(map(int, args.public.split(",")))
    configure(args.system)
    from app.lives import Store
    store = Store(args.system)
    started = datetime.now(timezone.utc).isoformat(); monotonic = time.monotonic()
    if datetime.now(timezone.utc) >= datetime.fromisoformat(DEADLINE):
        raise TimeoutError("Budget deadline precedes any native mutation")
    fork = store.fork(args.parent, args.life, kind="DIAGNOSTIC_COPY")
    result = store.mutate(args.life, REVISION, lambda a: episode(a, system=args.system, mode=args.mode, public=public, environment_reference=args.reference),
                          details={"mode": args.mode, "raw_public": public, "deadline_utc": DEADLINE,
                                   "fixed_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    primary = {"case": args.life, "started_utc": started, "elapsed_seconds": time.monotonic() - monotonic,
               "deadline_utc": DEADLINE, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "parent_record_at_fork": fork, "result": result, "new_preparation": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.out, "wt", encoding="utf8", compresslevel=6) as stream:
        json.dump(primary, stream, ensure_ascii=False, allow_nan=False)
    print(json.dumps({"output": str(args.out), "life": args.life, "tick": result["INSTRUMENTO"]["tick"],
                      "environment": result["result"]["environment"], "decoder": result["result"]["decoder"],
                      "before_own": [q["s_reg"] for q in result["result"]["before"]["own"]],
                      "after_own": [q["s_reg"] for q in result["result"]["after"]["own"]],
                      "receipts": [{"id": q["id"], "status": q["receipt"]["status"]} for q in result["result"]["requests"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
