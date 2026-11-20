"""M1 new readout, before destructive later interference, with all inputs Native.

Both regions receive the SAME signal and actual class. The observer accepts
only26vertical (16acquired +5common signal +5current report). No memory is cleared,
no clock edited, no region chosen from a hidden class or expected word.
"""
from pathlib import Path
from .common import FORMS,digest,inherited_channel,put,resource_sensor,until


def run(world,spec,case,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);channel=inherited_channel()
    if world.runtime.current_tick!=235:raise ValueError("Temporal access must continue real235 snapshot")
    initial=digest(world);world.save_snapshot(str(output/"SAME_GENEALOGY235.deetsnap"))
    windows=[]
    phase=case.get("phase_shift",0)
    if phase not in (0,1):raise ValueError("Frozen two phase conditions")
    for tick in (236+phase,264+phase):
        until(world,tick)
        sensor=resource_sensor(world,spec,case["bank"])
        suffix="plus" if sensor["present"] else "minus"
        ids={}
        for form in ("W1","W2"):
            ids[form]=[world.probe("lex."+form+".signal",5,tick).id]
            if case.get("report",True):ids[form].append(world.probe("lex."+form+".outcome."+suffix,5,tick).id)
        until(world,tick+3)
        observations={}
        for form,identities in ids.items():
            current=channel.observe(world,spec["lexical_hubs"][form]);receipts=[channel.receipt(world,x) for x in identities]
            valid=(case.get("report",True) and all(r["status"]=="applied" for r in receipts)
                   and current["active"] and current["semantic"]==1 and current["s_reg"]==26
                   and current["direction"] in ([0,1,0],[0,-1,0]))
            observations[form]={"physical_output":current,"receipts":receipts,"available":bool(valid),
                                "emitted_form":FORMS[form] if valid else None,
                                "decoder":"NEW TEMPORAL PANEL: admitted26vertical, same at both forms; no5/16/21 accepted"}
        windows.append({"sensor":sensor,"input_tick":tick,"read_tick":world.runtime.current_tick,"observations":observations})
        world.save_snapshot(str(output/("CURRENT_READ"+str(world.runtime.current_tick)+".deetsnap")))
    emitted=[o["emitted_form"] for window in windows for o in window["observations"].values() if o["available"]]
    result={"initial":initial,"final":digest(world),"windows":windows,"emitted_forms":emitted,
            "unique_form":emitted[0] if len(emitted)==1 else None,"same_main_between_windows":True,
            "raw_edits":[],"clock_edits":[],"transplants":[],"new_interface_installations":[],
            "modality":"PHYSICAL_PROBE_WITH_EXTERNAL_ACTUAL_CLASS_TRANSDUCER",
            "mechanism_claim":"New finite temporal access protocol; not recovery from a destroyed complete state, not relearning or learned self-regulation",
            "full_NSM_semantics":False}
    put(output/"MEASUREMENTS.json",result)
    return world,result
