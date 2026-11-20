"""Physical dual-route channel execution; no host selects the receiver action."""
from __future__ import annotations
from pathlib import Path
import time
from . import channel


def panel(world, spec):
    tick=world.runtime.current_tick
    sites={name:site for name,site in spec["centers"].items()}
    if 70<=tick<=88:
        for sign,label in ((1,"plus"),(-1,"minus")):
            sites["message_"+label]=channel.moved(spec["centers"]["A"],(-1,sign,0),tick-70)
    for name,contact in spec["contacts"].items():
        if contact<=tick<=spec["B_responses"][name]:
            for sign,label in ((1,"plus"),(-1,"minus"),(0,"flat")):
                sites[name+"_candidate_"+label]=channel.moved(spec["centers"][name],(-1,sign,0),tick-contact)
    for name,bank in spec["banks"].items():
        for key in ("cost_meeting","interception","resource_receiver","function_receiver"):
            sites[name+"_"+key]=bank[key]
    return {"tick":tick,"samples":{name:channel.observe(world,site) for name,site in sites.items()}}


def run(case,output,return_world=False):
    import dee_thinking as d
    from .common import put,sha
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    if d.__version__!="4.0.0" or d.kernel_identity()["kernel_version"]!=27 or sha(d._native.__file__)!=channel.NATIVE_SHA256:
        raise RuntimeError("Fixed DEE4/v27 instrument required")
    world,spec=channel.prepare_dual(d,tuple(case.get("translation",(0,0,0))))
    initial=channel.digest(world)
    world.save_snapshot(str(output/"MAIN_T0.deetsnap"))
    calls=[];ids=[];trace=[];edits=[];bank_captures={name:{} for name in spec["banks"]}
    def register(items,role):
        for r in items:
            ids.append(r.id);calls.append({"operation":"submit","id":r.id,"role":role,"requested_tick":r.requested_tick,"channels":list(r.channels)})
    a_sign=case["A_history"];policy=case.get("B_policy",1)
    register(channel.acquire_dual(world,"A",a_sign,0),"A_ACQUISITION")
    world.run_until(3)
    acquisition=[{"role":"A_AFTER_ACQUISITION","sample":channel.observe(world,spec["centers"]["A"])}]
    world.save_snapshot(str(output/"A_AFTER_ACQUISITION.deetsnap"))
    register(channel.acquire_dual(world,"Bplus",policy,12),"B_PLUS_REGION_ACQUISITION")
    world.run_until(15)
    acquisition.append({"role":"B_PLUS_AFTER_ACQUISITION","sample":channel.observe(world,spec["centers"]["Bplus"])})
    register(channel.acquire_dual(world,"Bminus",-policy,18),"B_MINUS_REGION_ACQUISITION")
    register([world.submit("A.signal",5,67)],"A_FIXED_COMMON_QUERY")
    for core,tick in spec["B_queries"].items():
        register([world.submit(core+".query_z",5,tick)],"B_FIXED_LATER_COMMON_QUERY")
    capture_ticks={21,66,67,69,70,71,78,79,80,81,82,83,84,85,86,87,88,89,100,120,145,146,147,148,149,150,151,152,153,154,155,156,157,158,161,162,163,164,168,169}
    checkpoint_names={21:"B_AFTER_HISTORY",70:"A_EMITTED",81:"BEFORE_CONTACT_PLUS",82:"AFTER_CONTACT_PLUS",87:"BEFORE_CONTACT_MINUS",88:"AFTER_CONTACT_MINUS",148:"BEFORE_COMMON_QUERY_PLUS",149:"AFTER_COMMON_QUERY_PLUS",154:"BEFORE_COMMON_QUERY_MINUS",155:"AFTER_COMMON_QUERY_MINUS",169:"MAIN_FINAL"}
    context=case.get("future_context",a_sign)
    while world.runtime.current_tick<=169:
        tick=world.runtime.current_tick
        if tick==70 and case.get("cut"):
            world,edit=channel.cut_dual_message(world,spec);edits.append(edit)
        for name,bank in spec["banks"].items():
            emit=bank["emission_tick"]
            if tick==emit:
                register(channel.dual_resources(world,bank),"FIXED_COMMON_RESOURCE_OPPORTUNITIES")
            if tick==emit+1:
                # Context is an explicit external world law, not inferred from
                # A/B's readout. Both event streams start after their response.
                event="U" if bank["orientation"]==context else "V"
                register([world.submit(bank["prefix"]+"."+event,11,tick)],"EXTERNAL_WORLD_EVENT_AFTER_RESPONSE")
            if tick==bank["resource_read_tick"]:
                bank_captures[name]["resource"]=channel.observe(world,bank["resource_receiver"])
            if tick==bank["function_read_tick"]:
                bank_captures[name]["function"]=channel.observe(world,bank["function_receiver"])
        if tick in capture_ticks:
            trace.append(panel(world,spec))
        if tick in checkpoint_names:
            world.save_snapshot(str(output/(checkpoint_names[tick]+".deetsnap")))
        if tick==169:break
        world.advance()
    by_tick={r["tick"]:r for r in trace}
    evaluations={name:channel.evaluate_oriented_bank(spec["banks"][name],cap["resource"],cap["function"]) for name,cap in bank_captures.items()}
    result={"case":case,"spec":spec,"initial":initial,"final":channel.digest(world),
            "A_emission":by_tick[70]["samples"]["A"],
            "B_contacts":{core:by_tick[t]["samples"][core] for core,t in spec["contacts"].items()},
            "B_common_responses":{core:by_tick[t]["samples"][core] for core,t in spec["B_responses"].items()},
            "evaluations":evaluations,"primary_sum":sum(v["profile"][0] for v in evaluations.values()),
            "optional_sum":sum(v["profile"][1] for v in evaluations.values()),
            "external_utility":sum(v["external_utility"] for v in evaluations.values()),
            "bank_captures":bank_captures,"acquisition":acquisition,"trace":trace,"operation_calls":calls,"diagnostic_edits":edits,
            "receipts":[channel.receipt(world,i) for i in ids],"elapsed_seconds":time.monotonic()-started,
            "native_threads":1,"source_sha256":{"src/channel.py":sha(Path(__file__).with_name("channel.py")),"src/channel_dual.py":sha(__file__)},
            "scope":"A is one acquired sender core; B is one distributed receiver with two acquired regions. No claim of two fully renewable basal bodies. The same native A product modifies the selected B relation and its retained state changes a later common probe and a physical bank consequence."}
    put(output/"MEASUREMENTS.json",result)
    return (result,world) if return_world else result
