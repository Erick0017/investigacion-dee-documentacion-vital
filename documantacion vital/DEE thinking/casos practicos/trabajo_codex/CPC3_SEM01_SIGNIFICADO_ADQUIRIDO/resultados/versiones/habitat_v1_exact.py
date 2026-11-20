"""Finite native U/V consequence bank, using the immutable public DEE4 API.

The geometry never reads an association, prediction or trial target. A native
(-1,+1,0) action can protect a supply route, at the physical cost of diverting an
optional resource. A (-1,-1,0) or untrained (-1,0,0) emission misses this bank.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time


N = 67
ACTION = (-1, 1, 0)
U = (0, -1, 0)
V = (0, -1, 1)
REFERENCE_WHEEL = "17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623"
REFERENCE_NATIVE = "20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066"


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moved(site, delta, distance=1):
    return tuple((x + distance*d) % N for x, d in zip(site, delta))


def bank_spec(emitter=(34, 16, 20), prefix="bank"):
    """Inert descriptor: positions only, never an association or desired action."""
    emitter = tuple(emitter)
    if len(emitter) != 3 or any(not isinstance(x, int) or not 0 <= x < N for x in emitter):
        raise ValueError("Emitter must be an integer N67 coordinate")
    h = moved(emitter, ACTION, 4)
    intercept = moved(h, (0, 1, 0), 4)
    return {"version": "sem01.native_supply_bank.v1", "N": N, "prefix": prefix,
            "emitter": emitter, "cost_meeting": h, "interception": intercept,
            "supply_meeting": h, "cost_receiver": moved(h, (1, 0, 0), 3),
            "function_receiver": moved(h, (0, 1, 0), 2),
            "resource_source": moved(h, (1, 0, 0), -4),
            "supply_source": moved(h, (0, 1, 0), -12),
            "event_U_source": moved(intercept, U, -7),
            "event_V_source": moved(intercept, V, -7),
            "offsets": {"cost_meeting":4,"cost_read":7,"interception":8,
                        "supply_meeting":12,"function_read":14},
            "scope": "Finite supplied route and optional-resource delivery; not a universal protective apparatus"}


def _interface(dee, name, site, direction):
    channel = dee.ChannelSpec()
    channel.name = name; channel.injection_site = dee.Coordinate(*site)
    channel.state = 1; channel.semantic = 1
    channel.direction = dee.Direction(*direction)
    channel.allow_experience = True; channel.allow_probe = True
    interface = dee.InterfaceSpec(); interface.name = name; interface.channel = channel
    return interface


def declare_bank_interfaces(world, spec, include_reference_action=False):
    """Call before first experience. Declaring channels installs no matter."""
    import dee_thinking as dee
    prefix = spec["prefix"]
    descriptions = [("resource", "resource_source", (1,0,0)),
                    ("supply", "supply_source", (0,1,0)),
                    ("U", "event_U_source", U), ("V", "event_V_source", V)]
    if include_reference_action:
        descriptions.append(("reference_action", "emitter", ACTION))
    for name, key, direction in descriptions:
        world.declare_interface(_interface(dee, prefix+"."+name, spec[key], direction))


def receipt_dict(value):
    return {"id":value.id,"kind":str(value.kind),"status":str(value.status),
            "requested_tick":value.requested_tick,"effective_tick":value.effective_tick,
            "channels":list(value.channels),"reason":value.reason}


def submit_resources(world, spec, action_emission_tick):
    """Fixed resource opportunities, same for all histories; not selected by action."""
    prefix=spec["prefix"]
    return [world.submit(prefix+".resource",3,action_emission_tick),
            world.submit(prefix+".supply",7,action_emission_tick)]


def submit_event(world, spec, event, action_emission_tick):
    """External experience generator supplies the real event AFTER anticipation.

    U and V have identical load and state. Only their fixed physical trajectory
    differs. This function never reads the organization or decides its action.
    """
    if event not in ("U","V"):
        raise ValueError("Only the fixed physical event classes U and V are declared")
    return world.submit(spec["prefix"]+"."+event,11,action_emission_tick+1)


def observation(value):
    record=value.record
    return {"tick":value.tick,"site":[value.coordinate.x,value.coordinate.y,value.coordinate.z],
            "raw":value.raw,"clock":value.clock,"state":record.state,"semantic":record.semantic,
            "s_reg":record.s_reg,"direction":[record.dx,record.dy,record.dz],
            "active":record.state>0 and record.semantic!=5}


def digest(world):
    return {"tick":world.runtime.current_tick,
            "raw_sha256":hashlib.sha256(array("Q",world.runtime.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",world.runtime.clock_copy()).tobytes()).hexdigest()}


def read_bank(world, spec, emission_tick, captures):
    """Read current sites. History in captures is an EXTERNAL observer record."""
    import dee_thinking as dee
    tick=world.runtime.current_tick
    current={key:observation(world.runtime.observe(dee.Coordinate(*spec[key]))) for key in
             ("emitter","cost_meeting","interception","cost_receiver","function_receiver")}
    if tick==emission_tick+7:
        captures["cost_receiver"]=current["cost_receiver"]
    if tick==emission_tick+14:
        captures["function_receiver"]=current["function_receiver"]
    return {"tick":tick,"relative_to_action":tick-emission_tick,"current":current}


def evaluate_captures(captures):
    """External finite task evaluator. Its values never enter the Runtime."""
    resource=captures.get("cost_receiver"); function=captures.get("function_receiver")
    # Presence alone is insufficient: the declared task requires deliveries
    # along their original supply directions. A stray action is not a success.
    resource_delivered=bool(resource and resource["active"] and resource["direction"]==[1,0,0] and resource["s_reg"]==3)
    function_delivered=bool(function and function["active"] and function["direction"]==[0,1,0] and function["s_reg"]==7)
    return {"resource_delivery":resource_delivered,"function_delivery":function_delivered,
            "profile":[int(function_delivered),int(resource_delivered)],
            "external_utility_for_this_task":2*int(function_delivered)+int(resource_delivered),
            "utility_rule":"Auditor only:2*primary_supply+optional_resource; never a teacher/error or host control input",
            "measurements":captures}


def reference_case(case, output):
    import dee_thinking as dee
    if dee.__version__!="4.0.0" or dee.kernel_identity()["kernel_version"]!=27:
        raise RuntimeError("Immutable DEE4/v27 instrument required")
    if sha(dee._native.__file__)!=REFERENCE_NATIVE:
        raise RuntimeError("Native extension identity differs")
    placements=[]
    recipe=dee.OrganizationRecipe.research(N,placements,0)
    recipe.execution=dee.TickOptions(dee.Backend.LAZY,1)
    world=dee.OrganizationalWorld.create(recipe)
    spec=bank_spec(tuple(case.get("emitter",[34,16,20])))
    declare_bank_interfaces(world,spec,True)
    world.save_snapshot(str(output/"BANK_T0.deetsnap"))
    initial=digest(world)
    receipts=submit_resources(world,spec,0)
    if case["action"]:
        receipts.append(world.submit(spec["prefix"]+".reference_action",21,0))
    captures={};trace=[]
    for tick in range(15):
        if tick==1:
            # At this point an optional action was already emitted at0. The
            # generator supplies an actual event; it does not inspect that action.
            receipts.append(submit_event(world,spec,case["event"],0))
        trace.append(read_bank(world,spec,0,captures))
        if tick in (4,7,8,12,14):
            world.save_snapshot(str(output/("BANK_T"+str(tick)+".deetsnap")))
        if tick<14:
            world.advance()
    final_receipts=[receipt_dict(world.runtime.receipt(r.id)) for r in receipts]
    return {"case":case,"bank":spec,"initial":initial,"trace":trace,
            "evaluation":evaluate_captures(captures),"receipts":final_receipts,"final":digest(world),
            "instrument":{"version":dee.__version__,"kernel":27,"module":dee.__file__,
                          "native_sha256":sha(dee._native.__file__)},
            "external_operations":[{"operation":"submit","id":r.id,"tick":r.requested_tick,"channels":list(r.channels)} for r in receipts],
            "modality":"REFERENCE_ACTION_CONTROL_NOT_YET_ACQUIRED_ACTION",
            "scope":"Bank validation before teaching arbitrary signals; useful action and unnecessary action cost have physical receivers"}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--python",type=Path)
    parser.add_argument("--child",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args();root=args.root.resolve()
    if args.child:
        start=time.monotonic();args.output.mkdir(parents=True,exist_ok=True)
        result=reference_case(json.loads(args.child.read_text()),args.output)
        result.update(elapsed_seconds=time.monotonic()-start,runner_sha256=sha(__file__),completed_utc=datetime.now(timezone.utc).isoformat())
        put(args.output/"MEASUREMENTS.json",result);return
    if not args.python:
        parser.error("--python must identify the isolated official DEE4 environment")
    sys.path.insert(0,str(root));from supervise import run
    output=root/"resultados/discovery_habitat01";output.mkdir(parents=True,exist_ok=True)
    config_path=output/"DISCOVERY_CONFIG.json"
    if not config_path.exists():
        put(config_path,{"frozen_utc":datetime.now(timezone.utc).isoformat(),"N":67,
            "cases":[{"id":event+("_action" if action else "_no_action"),"event":event,"action":action}
                     for event in ("U","V") for action in (False,True)],
            "criterion":"Primary supply direction+y load7 at14; optional resource direction+x load3 at7; both native actual observations",
            "action":"Native direction(-1,+1,0) atemitter0; explicit reference input for this bank calibration only",
            "prepared_interfaces_before_T0":True,"events_after_action_emission":True,
            "resource_cost":"Native optional resource diverted by action, not a score-only penalty",
            "maximum_discovery_cases":6})
    config=json.loads(config_path.read_text());rows=[]
    for case in config["cases"]:
        folder=output/case["id"];folder.mkdir(parents=True,exist_ok=True)
        put(folder/"CASE.json",case)
        name="habitat01_"+case["id"]
        attempt=1
        while (root/"jobs"/name).exists():
            attempt+=1;name="habitat01_"+case["id"]+"_attempt"+str(attempt)
        assert attempt<=3,"Maximum two repairs for a technical error"
        if (folder/"MEASUREMENTS.json").exists():
            rows.append(json.loads((folder/"MEASUREMENTS.json").read_text()));continue
        job=run(root,name,[str(args.python),"-I","-B",str(Path(__file__).resolve()),"--root",str(root),
                          "--child",str(folder/"CASE.json"),"--output",str(folder)],180,cwd=str(output))
        row=json.loads((folder/"MEASUREMENTS.json").read_text()) if job["exit_code"]==0 else {"case":case,"status":"TECHNICAL_ERROR","job":job}
        rows.append(row);put(output/"RESULTS.json",{"cases":rows,"config_sha256":sha(config_path)})


if __name__=="__main__":
    main()
