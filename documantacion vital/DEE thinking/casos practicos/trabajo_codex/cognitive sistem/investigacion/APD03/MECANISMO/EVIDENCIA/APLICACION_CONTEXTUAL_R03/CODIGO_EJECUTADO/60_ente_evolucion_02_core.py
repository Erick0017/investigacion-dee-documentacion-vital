"""EO02 multi-environment core1: one prospective schedule revision, no anatomy changes.

R01 preserved: role0 transported but missed its support-update window. This
revision advances only role0 downstream resources/tactile2ticks. Role+/- stays.
EO01 fixed post-action tactile core, compatible with the lived CF01/R9 body.

The old first/contact resource(j0) is NEVER supplied. Every downstream generic
resource is fixed before reading action. A real actuator contact, obtained only
after execution, can emit a fixed tactile pulse at that actuator's physical
posture. The codec never computes the next action or a memory correction.
"""
from capacidades import cierre_funcional_cf01 as cf
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import integracion_distribuida_mi02_r6 as native

REVISION = "EO02.post_action_tactile.multi_environment.core.1"


def _plan(a):
    C = cf.geometry(a)["A"]
    critical = 391 + 782 * max(0, (a.tick + 90 - 391 + 781) // 782)
    u = critical - 15
    original = body.cycle_plan(a, {"Q": C}, 1, critical)
    supplies = []
    for row in original["sources"]:
        role, stage, serial = map(int, row["name"].split(".")[2:])
        if stage == 0:
            continue
        supplies.append({**row, "name": "EO01.post.resource." + str(role) + "." + str(stage) + "." + str(serial),
                         "tick": row["tick"] + (0 if role == 0 else 2),
                         "role": "Generic downstream resource independent of environment result, target and native action"})
    ports = {}
    for r in (-1, 0, 1):
        ports[str(r)] = {"site": body.xyz(a, C, (3 * r, -3, -1) if r else (0, -4, -1)),
                         "direction": [r, -1, 0], "tick": u + (4 if r else 3), "payload": 0,
                         "first_head": body.xyz(a, C, (4 * r, -4, -1) if r else (0, -5, -1)),
                         "expected_arrival": u + (5 if r else 4)}
    return {"critical_tick": critical, "decision_deadline": u, "supplies": supplies,
            "tactile_ports": ports, "all_j0_sources_omitted": True,
            "generic_downstream_delay": {"-1": 2, "0": 0, "1": 2},
            "source_grammar": "All roles0,+,- retain separate mechanical return paths. Availability is not an argument of this schedule."}


def _sample(a, plan, detailed):
    f = cf.witness(a); C = cf.geometry(a)["A"]
    f["contacts"] = {str(r): body.obs(a, body.xyz(a, C, (r, -1, -1))) for r in (-1, 0, 1)}
    f['sensory_fanin_targets']=[body.obs(a,p)for p in((5,13,15),(7,13,15))]
    if detailed:
        f['message_waypoints']=cf.message_witness(a)
        original = body.cycle_plan(a, {"Q": C}, 1, plan["critical_tick"])
        f["return_heads"] = {str(r): [body.obs(a, q["head"]) for q in original["routes"] if q["r"] == r] for r in (-1, 0, 1)}
        f["tactile_entries"] = {r: body.obs(a, port["site"]) for r, port in plan["tactile_ports"].items()}
    return f


def external_episode(a, *, public, reference, actuator="closed", feedback="real", trace=False, offset=0, cut="none", private_B=None, message_cut="none", social_valve=False, B_actuator="closed", environment=None):
    if len(public) != 2 or any(type(v) is not int or not 0 <= v <= 64 for v in public):
        raise ValueError("Two raw public integers0..64 required")
    if type(reference) is not int or not -64 <= reference <= 64:
        raise ValueError("Reference belongs to bounded external law only")
    if actuator not in ("closed", "nulled") or feedback not in ("real", "omit", "decoupled") or cut not in ("none", "path", "sham"):
        raise ValueError("Explicit frozen actuator/feedback/control modes required")
    if type(offset) is not int or not 0 <= offset <= 52:
        raise ValueError("Fixed sensor offset0..52 required")
    if private_B is not None and(type(private_B)is not int or not 0<=private_B<=255):
        raise ValueError("Private B raw scalar0..255 required; not a solved social message")
    if message_cut not in('none','minus_bus','plus_bus'):
        raise ValueError("Fixed post-formation message intervention required")
    if type(social_valve)is not bool or B_actuator not in('closed','nulled'):
        raise ValueError('Explicit prepared shared-environment instrument and B actuator required')
    before = cf.witness(a); plan = _plan(a)
    critical = plan["critical_tick"]; u = plan["decision_deadline"]
    requests = []
    for q in plan["supplies"]:
        requests.append(body.send(a, q["name"], q["site"], q["direction"], q["tick"], q["payload"]))
    for name, value in zip(("sin", "cos"), public):
        sensor = next(q for q in body.get(a)["external_sensors"] if q["name"] == name)
        requests.append(body.send(a, "EO01.post.public." + name, sensor["origin"], sensor["direction"], critical - 22 - offset, value))
    if private_B is not None:
        requests.append(body.send(a,'EO01.post.private.B_incoming',body.xyz(a,cf.geometry(a)['B'],(0,-2,0)),(1,1,1),critical+13,private_B))
    if message_cut!='none':
        site=(12,19,9)if message_cut=='minus_bus'else(0,19,9)
        requests.append(body.send(a,'EO01.post.message_cut.'+message_cut,site,(0,0,0),critical+19,0,sem=4))
    frames = []
    times = range(critical - 25 - offset, u + 1) if trace else sorted(set((critical - 25 - offset, critical - 17, u - 1, u)))
    for tick in times:
        a.run_until(tick); frames.append(_sample(a, plan, trace))
    reader = cf.decode_window({"row": {"critical_tick": critical}, "frames": frames})
    formed = reader["command"]
    selected = next((q for q in reader["samples"] if q["tick"] == reader["source_tick"]), None)
    posture = None if selected is None else selected["material_roles"][0]
    executed = formed if actuator == "closed" else None
    actual_posture = posture if executed is not None else None
    # ENVIRONMENT ONLY. Neither this gate nor reference enters the participant.
    available = 1 if public[0] + reference >= public[1] else -1
    moved = executed is not None
    contact = bool(moved and executed != available)
    completed = bool(moved and executed == available)
    environment_before = {"law": "EO01.fixed_gate_with_distinct_actuator_postures.v1", "raw_measurements": list(public),
                          "reference_not_injected": reference, "available_gate_not_injected": available,
                          "actuator_pose": "rest", "rest_rule": "Mechanical fixture offers one new approach per environmental job; no native reset"}
    observed = {"tick": u, "movement": moved, "contact": contact, "actuator_posture": actual_posture,
                "effect": "closed_gate_contact" if contact else "gate_passed" if completed else "no_movement",
                "job_completed": completed}
    environment_after = {**environment_before, "actuator_pose": actual_posture, "observed_result": observed}
    if environment is not None:
        external = environment.act(formed=formed, executed=executed, posture=actual_posture, public=list(public), native_tick=u)
        environment_before = external['before']
        environment_after = external['after']
        observed = external['observed']
        moved = bool(observed['movement'])
        contact = bool(observed['contact'])
        completed = bool(observed['job_completed'])
    sensor_role = actual_posture if contact else None
    if feedback == "omit":
        sensor_role = None
    elif feedback == "decoupled" and sensor_role is not None:
        sensor_role = -sensor_role if sensor_role else 1
    tactile = None
    if sensor_role is not None:
        port = plan["tactile_ports"][str(sensor_role)]
        tactile = body.send(a, "EO01.post.tactile." + str(sensor_role), port["site"], port["direction"], port["tick"], port["payload"])
        requests.append(tactile)
    intervention = None
    if cut != "none" and actual_posture is not None:
        role = actual_posture if cut == "path" else (-actual_posture if actual_posture else 1)
        port = plan["tactile_ports"][str(role)]
        # A diagnostic barrier is not a native repair. It may be rejected.
        intervention = body.send(a, "EO01.post.diagnostic." + cut + "." + str(role), port["first_head"], (0, 0, 0), u + (4 if actual_posture else 3), 0, sem=4)
        requests.append(intervention)
    times = range(u + 1, critical + 81) if trace else sorted(set((u + 1, u + 4, u + 5, u + 6, u + 8, u + 14, critical, critical + 2, critical + 3, critical + 13, critical + 14, critical + 15, critical + 19, critical + 30, critical + 37, critical + 38, critical + 40, critical + 80)))
    social_actuation=None
    for tick in times:
        a.run_until(tick); frames.append(_sample(a, plan, trace))
        if social_valve and tick==critical+30:
            buses={'minus':body.obs(a,(12,19,9)),'plus':body.obs(a,(0,19,9))}
            valid=[dx for name,dx in(('minus',-1),('plus',1))if buses[name]['state']>0 and buses[name]['semantic']==1 and buses[name]['s_reg']==5 and buses[name]['direction']==[dx,0,0]]
            bus_command=valid[0]if len(valid)==1 else None
            # This is a prepared external material opportunity, not a learned
            # host selection: one new private observation provides one valve
            # resource, independent of its value, result or desired action.
            resource=private_B is not None
            valve_command=bus_command if resource and B_actuator=='closed'else None
            next_reference=reference if valve_command is None else max(-64,min(64,reference+valve_command))
            social_actuation={'observation_tick':tick,'buses':buses,'fixed_reader':'unique_SEM1_statepositive_load5_horizontal_at_critical_plus30.v1','formed_B_command':bus_command,'conflict':len(valid)>1,'prepared_opportunity_present':resource,'resource_fixed_from_private_request_not_admission':True,'resource_window':[critical+30,critical+30],'resource_consumed_by_actuation':valve_command is not None,'resource_expired_after_window':True,'pending_resource_after_episode':0,'B_actuator':B_actuator,'executed_valve_command':valve_command,'reference_before':reference,'reference_after':next_reference,'actual_displacement':next_reference-reference,'mechanical_endstop':valve_command is not None and next_reference==reference,'assistance':'External fixed unit valve and nonaccumulating resource, not autonomous routing or closed-v27 social update'}
            environment_after.update({'reference_not_injected':next_reference,'valve_effective_tick':tick,'social_valve':social_actuation,'available_gate_scope':'Gate at A action time, before later valve motion; next job recomputes its own physical gate'})
    after = cf.witness(a)
    ns = native.saved(a); ns["index"] += 1; native.put(a, ns)
    view = body.get(a); view["index"] = ns["index"]; body.put(a, view)
    consequence = {"information_origin": "Actual post-execution contact and actuator posture, not gate calibration or desired action",
                   "sensor_role": sensor_role, "observed_at_tick": u,
                   "material_input_tick": None if tactile is None else tactile["tick"],
                   "tactile_request_id": None if tactile is None else tactile["id"],
                   "intervention_id": None if intervention is None else intervention["id"],
                   "old_contact_resource_submitted": False,
                   "dose_rule": "One tactile event for a real closed-gate contact, none for an unmoved or passing actuator; general supplies fixed in all cases"}
    row = {"start_tick": before["tick"], "critical_tick": critical, "end_tick": after["tick"],
           "public_raw": list(public), "actuator": actuator, "feedback": feedback, "cut": cut, "phase_offset": offset,
           "private_B_raw":private_B,"private_input_fixed_tick":None if private_B is None else critical+13,"post_formation_message_cut":message_cut,
           "native_posture": posture, "formed_native_command": formed, "executed_external_command": executed,
           "observed_contact": contact, "returned_posture": sensor_role, "job_completed": completed,
           "native_query_sample": any(0 in q["material_roles"] for q in reader["samples"]),
           "native_query_scope": "Material0 has both query and default-left role, not an exclusive learned act/ask decision"}
    row['social_valve_enabled']=social_valve
    return {"revision": REVISION, "before": before, "after": after, "row": row, "frames": frames,
            "plan": plan, "requests": body.receipts(a, requests), "reader": reader,
            "environment_before": environment_before, "environment_after": environment_after,
            "formed_native_command": formed, "executed_external_command": executed,
            "social_actuation":social_actuation,
            "observed_result": observed, "consequence": consequence, "job_completed": completed,
            "attribution": "Prepared body/codec/supplies and external fixture; native decisions and field transformations. No pre-action consequence, learned-field write, desired next direction or target-dependent reader."}
