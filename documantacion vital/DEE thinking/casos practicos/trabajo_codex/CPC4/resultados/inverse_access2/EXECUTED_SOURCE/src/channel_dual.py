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
    for core,birth in (("Bplus",15),("Bminus",21)):
        if birth<=tick<=spec["contacts"][core]:
            for sign,label in ((1,"plus"),(-1,"minus")):
                direction=(0,0,sign) if spec["receiver_basis"]=="z" else (0,sign,0)
                sites[core+"_precontact_basis_"+label]=channel.moved(spec["centers"][core],direction,tick-birth)
    for name,contact in spec["contacts"].items():
        if contact<=tick<=spec["B_responses"][name]:
            if spec["receiver_basis"]=="z":
                route=1 if name=="Bplus" else -1
                for y in (route,0):
                    for z in (-1,1):
                        sites[name+"_candidate_y"+str(y)+"z"+str(z)]=channel.moved(spec["centers"][name],(-1,y,z),tick-contact)
            else:
                for sign,label in ((1,"plus"),(-1,"minus"),(0,"flat")):
                    sites[name+"_candidate_"+label]=channel.moved(spec["centers"][name],(-1,sign,0),tick-contact)
    for name,bank in spec["banks"].items():
        for key in ("cost_meeting","interception","resource_receiver","function_receiver"):
            sites[name+"_"+key]=bank[key]
        sites[name+"_action_out"]=channel.moved(bank["emitter"],bank["action"])
    return {"tick":tick,"samples":{name:channel.observe(world,site) for name,site in sites.items()}}


def run_native(world,spec,case,output,snapshot_policy="central"):
    import dee_thinking as d
    from .common import put,sha
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    if d.__version__!="4.0.0" or d.kernel_identity()["kernel_version"]!=27 or sha(d._native.__file__)!=channel.NATIVE_SHA256:
        raise RuntimeError("Fixed DEE4/v27 instrument required")
    if world.runtime.current_tick!=0 or world.runtime.dimension!=channel.N:
        raise ValueError("run_native starts the supplied prepared T0 world; it never reconstructs or resets an individual")
    if snapshot_policy not in ("central","none"):
        raise ValueError("snapshot_policy must be central or none")
    calls=[];ids=[];trace=[];edits=[];local_contexts=[];bank_captures={name:{} for name in spec["banks"]}
    def snapshot(name):
        if snapshot_policy=="central":
            path=output/(name+".deetsnap")
            world.save_snapshot(str(path))
            calls.append({"operation":"save_snapshot","call_tick":world.runtime.current_tick,"path":path.name,"physical_RAW_clock_write":False})
    initial=channel.digest(world)
    snapshot("MAIN_T0")
    def register(items,role):
        for r in items:
            ids.append(r.id);calls.append({"operation":"submit","id":r.id,"role":role,"call_tick":world.runtime.current_tick,"requested_tick":r.requested_tick,"channels":list(r.channels)})
    def log_edit(edit):
        edits.append(edit)
        calls.append({"operation":"diagnostic_fork","call_tick":world.runtime.current_tick,
                      "label":edit.get("label",edit["operation"]),"actual_edit":edit})
    a_sign=case["A_history"];policy=case.get("B_policy",1)
    instrument_action=case.get("instrument_action","none")
    if instrument_action not in ("none","both","plus","minus"):
        raise ValueError("Explicit instrument policy must be none,both,plus,minus")
    if instrument_action!="none" and case.get("direct_actuator"):
        raise ValueError("Do not duplicate diagnostic reference-action treatments")
    register([world.submit("instrument.sham",13,0)],"COMMON_UNINFORMATIVE_DUMMY")
    if not case.get("A_untrained"):
        register(channel.acquire_dual(world,"A",a_sign,0,signal_delay=int(bool(case.get("A_unpaired")))),"A_ACQUISITION")
    world.run_until(3)
    acquisition=[{"role":"A_AFTER_ACQUISITION","sample":channel.observe(world,spec["centers"]["A"])}]
    snapshot("A_AFTER_ACQUISITION")
    if not case.get("receiver_untrained"):
        if case.get("receiver_teacher_only"):
            world.run_until(12)
            register([world.submit("Bplus.outcome."+("plus" if policy==1 else "minus"),11,12)],"B_PLUS_OUTCOME_ONLY")
        else:register(channel.acquire_dual(world,"Bplus",policy,12,signal_delay=int(bool(case.get("receiver_unpaired")))),"B_PLUS_REGION_ACQUISITION")
    world.run_until(15)
    acquisition.append({"role":"B_PLUS_AFTER_ACQUISITION","sample":channel.observe(world,spec["centers"]["Bplus"])})
    if not case.get("receiver_untrained"):
        minus_policy=policy if spec["receiver_basis"]=="z" else -policy
        if case.get("receiver_teacher_only"):
            world.run_until(18)
            register([world.submit("Bminus.outcome."+("plus" if minus_policy==1 else "minus"),11,18)],"B_MINUS_OUTCOME_ONLY")
        else:register(channel.acquire_dual(world,"Bminus",minus_policy,18,signal_delay=int(bool(case.get("receiver_unpaired")))),"B_MINUS_REGION_ACQUISITION")
    if not case.get("no_A_query"):
        register([world.submit("A.signal",5,67)],"A_FIXED_COMMON_QUERY")
    for core,tick in spec["B_queries"].items():
        register([world.submit(spec["B_query_channels"][core],5,tick)],"B_FIXED_LATER_COMMON_QUERY")
    capture_ticks={21,66,67,69,70,71,78,79,80,81,82,83,84,85,86,87,88,89,100,120,145,146,147,148,149,150,151,152,153,154,155,156,157,158,161,162,163,164,168,169}
    checkpoint_names={21:"B_AFTER_HISTORY",70:"A_EMITTED",81:"BEFORE_CONTACT_PLUS",82:"AFTER_CONTACT_PLUS",87:"BEFORE_CONTACT_MINUS",88:"AFTER_CONTACT_MINUS",148:"BEFORE_COMMON_QUERY_PLUS",149:"AFTER_COMMON_QUERY_PLUS",154:"BEFORE_COMMON_QUERY_MINUS",155:"AFTER_COMMON_QUERY_MINUS",169:"MAIN_FINAL"}
    world_context=case.get("future_context",a_sign)
    a_emission_before_intervention=None
    while world.runtime.current_tick<=169:
        tick=world.runtime.current_tick
        if tick==70:
            a_emission_before_intervention=channel.observe(world,spec["centers"]["A"])
            if case.get("cut"):
                world,edit=channel.cut_dual_message(world,spec);log_edit(edit)
            if case.get("message_control"):
                control=case["message_control"]
                if control not in ("force_plus","z_miss"):raise ValueError("Unknown fixed diagnostic message field control")
                direction=(-1,1,0) if control=="force_plus" else (-1,a_sign,1)
                world,edit=channel.diagnostic_record_edit(world,spec["centers"]["A"],"MESSAGE_"+control,direction=direction,expected_load=21);log_edit(edit)
            if case.get("sham_remove"):
                site=channel.moved(spec["sham_source"],(1,0,0),70)
                sham_context=channel.moore_context(world,site)
                world,edit=channel.diagnostic_record_edit(world,site,"SHAM_REMOVE_COMMON_DUMMY",raw=0,expected_load=13)
                edit["active_neighbors_before"]=sum(item["sample"]["active"] for item in sham_context)
                edit["context_before"]=sham_context;log_edit(edit)
        if case.get("receiver_flatten") and tick==spec["contacts"]["Bplus" if a_sign==1 else "Bminus"]:
            core="Bplus" if a_sign==1 else "Bminus"
            actual=channel.observe(world,spec["centers"][core])
            direction=(actual["direction"][0],0,actual["direction"][2])
            world,edit=channel.diagnostic_record_edit(world,spec["centers"][core],"POSTCONTACT_RECEIVER_DY_ZERO",direction=direction,expected_load=37);log_edit(edit)
        if case.get("receiver_z_remove") and tick==spec["contacts"]["Bplus" if a_sign==1 else "Bminus"]:
            if case.get("receiver_flatten"):raise ValueError("Use separate selective receiver-field controls")
            core="Bplus" if a_sign==1 else "Bminus"
            actual=channel.observe(world,spec["centers"][core])
            direction=(actual["direction"][0],actual["direction"][1],0)
            world,edit=channel.diagnostic_record_edit(world,spec["centers"][core],"POSTCONTACT_RECEIVER_DZ_ZERO",direction=direction,expected_load=37);log_edit(edit)
        for name,bank in spec["banks"].items():
            emit=bank["emission_tick"]
            if tick==emit:
                register(channel.dual_resources(world,bank),"FIXED_COMMON_RESOURCE_OPPORTUNITIES")
            if tick==emit+1:
                # Context is an explicit external world law, not inferred from
                # A/B's readout. Both event streams start after their response.
                event="U" if bank["orientation"]==world_context else "V"
                register([world.submit(bank["prefix"]+"."+event,11,tick)],"EXTERNAL_WORLD_EVENT_AFTER_RESPONSE")
                if case.get("direct_actuator") and bank["orientation"]==world_context:
                    register([world.submit(bank["prefix"]+".reference_action_out",42,tick)],"DIAGNOSTIC_REFERENCE_ACTION_AT_PREDECLARED_OUTBOUND_SITE")
                if instrument_action=="both" or instrument_action==name:
                    register([world.submit(bank["prefix"]+".reference_action_out",42,tick)],"EXTERNAL_FIXED_POLICY_REFERENCE_ACTION_"+instrument_action)
            if tick==bank["resource_read_tick"]:
                bank_captures[name]["resource"]=channel.observe(world,bank["resource_receiver"])
            if tick==bank["function_read_tick"]:
                bank_captures[name]["function"]=channel.observe(world,bank["function_receiver"])
        if tick in capture_ticks:
            trace.append(panel(world,spec))
        if tick in (70,78,79,80,81,82,84,85,86,87,88):
            for core,birth,orientation in (("Bplus",15,1),("Bminus",21,-1)):
                if tick<=spec["contacts"][core]:
                    basis=(0,0,policy) if spec["receiver_basis"]=="z" else (0,orientation*policy,0)
                    site=channel.moved(spec["centers"][core],basis,tick-birth)
                    local_contexts.append({"tick":tick,"role":core,"sampled_center_hypothesis":"precontact acquired basis segment; missing/changed records remain explicit",
                                           "center":channel.observe(world,site),"moore26":channel.moore_context(world,site)})
        if tick==21:
            acquisition.append({"role":"B_MINUS_AFTER_ACQUISITION","sample":channel.observe(world,spec["centers"]["Bminus"])})
        if tick in checkpoint_names:
            snapshot(checkpoint_names[tick])
        if tick==169:break
        world.advance()
    by_tick={r["tick"]:r for r in trace}
    evaluations={name:channel.evaluate_oriented_bank(spec["banks"][name],cap["resource"],cap["function"]) for name,cap in bank_captures.items()}
    result={"case":case,"spec":spec,"initial":initial,"final":channel.digest(world),
            "A_emission":a_emission_before_intervention,
            "A_current_after_intervention":by_tick[70]["samples"]["A"],
            "B_contacts":{core:by_tick[t]["samples"][core] for core,t in spec["contacts"].items()},
            "B_common_responses":{core:by_tick[t]["samples"][core] for core,t in spec["B_responses"].items()},
            "evaluations":evaluations,"primary_sum":sum(v["profile"][0] for v in evaluations.values()),
            "optional_sum":sum(v["profile"][1] for v in evaluations.values()),
            "external_utility":sum(v["external_utility"] for v in evaluations.values()),
            "bank_captures":bank_captures,"acquisition":acquisition,"trace":trace,"local_contexts":local_contexts,
            "operation_calls":calls,"diagnostic_edits":edits,
            "receipts":[channel.receipt(world,i) for i in ids],"elapsed_seconds":time.monotonic()-started,
            "native_threads":1,"prepared_interface_names":[item.name for item in world.interfaces],
            "source_sha256":{"src/channel.py":sha(Path(__file__).with_name("channel.py")),"src/channel_dual.py":sha(__file__)},
            "scope":"A is one acquired sender core; B is one distributed receiver with two acquired regions. No claim of two fully renewable basal bodies. The same native A product modifies the selected B relation and its retained state changes a later common probe and a physical bank consequence."}
    put(output/"MEASUREMENTS.json",result)
    return world,result


def run(case,output,return_world=False):
    """Explicit fresh preparation wrapper for discovery/reproduction only."""
    import dee_thinking as d
    world,spec=channel.prepare_dual(d,tuple(case.get("translation",(0,0,0))),receiver_basis=case.get("receiver_basis","z"))
    world,result=run_native(world,spec,case,output)
    return (world,spec,result) if return_world else result
