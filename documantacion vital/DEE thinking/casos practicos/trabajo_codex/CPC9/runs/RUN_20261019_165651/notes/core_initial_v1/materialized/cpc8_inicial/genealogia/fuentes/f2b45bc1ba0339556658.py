"""One new fixed-counterflow episode in the same already acquired world.

No previous state is erased or restored into MAIN. The CLI explicitly loads the
full parent once; continue_session itself uses the caller's same world object.
"""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
from red.regulated_session import NetworkSession,protocol
from red.dual_habitat import evaluate
from red.residual_diagnostic import empty_branch


def continue_session(session,output,config):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    if session.world.runtime.current_tick!=437:raise ValueError("This frozen continuation starts only at actual437")
    initial=r.digest(session.world);object_identity=id(session.world);offset=config["offset"]
    entries=[{**entry,"tick":entry["tick"]+offset} for entry in protocol(config["external_conditions"]) if entry["channel"]!="instrument.sham"]
    calls=[]
    for entry in entries:
        rec=session.world.submit(entry["channel"],entry["load"],entry["tick"])
        calls.append({**entry,"receipt_id":rec.id,"call_tick":437,"modality":"EXPERIENCE_PROTOCOL"})
    after_scheduling=r.digest(session.world)
    if initial!=after_scheduling:raise RuntimeError("Scheduling changed physical RAW/clock state")
    episode={"version":1,"external_conditions":config["external_conditions"],"offset":offset,"protocol":calls,
             "scope":"Second external episode in the same current organization. Conditions choose only actual experience and habitat packets, never a response or reward."}
    session.state.setdefault("continued_external_episodes",[]).append(episode);session._commit()
    captures={name:{} for name in session.spec["banks"]};trace=[];contexts={}
    for tick in (437,499,500,503,513,515,527,570,580,582,585,586,593,594,660,661,727,728,790,791,792,793,794,849,850,916,917,921,924,925,927,930,931,937):
        trace.append(session.run_until(tick))
        if tick in (792,793):contexts[str(tick)]=empty_branch(session.world,session.spec["regulation"]["meeting"])
        for name,bank in session.spec["banks"].items():
            if tick==bank["resource_read"]+offset:captures[name]["R"]=r.observe(session.world,bank["resource_receiver"])
            if tick==bank["function_read"]+offset:captures[name]["F"]=r.observe(session.world,bank["function_receiver"])
        if tick in (437,594,661,728,791,793,794,850,917,937):session.save(out/("T"+str(tick)+".deetsnap"))
        r.put(out/"PROGRESS.json",{"tick":tick,"trace":trace})
    result={"config":config,"initial":initial,"after_scheduling":after_scheduling,"final":r.digest(session.world),
            "same_world_object":id(session.world)==object_identity,"trace":trace,"local_contexts":contexts,"captures":captures,
            **evaluate(session.world,session.spec,captures),"actual_input_calls":calls,"receipts":[r.receipt(session.world,x["receipt_id"]) for x in calls],
            "modality":"EXPERIENCE_PROTOCOL then NATIVE_EVOLUTION",
            "scope":"No create, fork, direct RAW edit, clock reset or body replacement is invoked by continue_session. New supplies are explicit experience/environment inputs, not invisible restoration of old states."}
    r.put(out/"MEASUREMENTS.json",result);return session,result


def main():
    p=argparse.ArgumentParser();p.add_argument("--parent",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    config_path=a.output.parent/(a.output.name+"_EXPERIMENT_CONFIG.json")
    if config_path.exists():raise FileExistsError("Do not replace a frozen continuation configuration")
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"parent_checkpoint":str(a.parent.resolve()),"parent_sha256":r.sha(a.parent),
       "worker_sha256":r.sha(__file__),"offset":500,"external_conditions":{"id":"SECOND_CONTEXT_C_MINUS","roles":True,
         "A_history":1,"B_history":1,"C_history":-1,"D_history":1,"neutralizer":"counterflow"},
       "initial_tick":437,"horizon":937,"fixed_zero_input_tick":790,"new_common_dummy_input":False,
       "no_expected_response_in_session":True,"reason":"One bounded continuation after the four-context regulated network contrast, not another geometry or timing search."}
    r.put(config_path,config)
    session=NetworkSession.load(a.parent)
    _,result=continue_session(session,a.output,config)
    # Passive restoration verifies no new body was prepared by load.
    restored=NetworkSession.load(a.output/"T937.deetsnap")
    r.put(a.output/"RESTORE_CHECK.json",{"same_physical":r.digest(restored.world)==result["final"],
       "saved_episode_metadata_equal":restored.state["continued_external_episodes"]==session.state["continued_external_episodes"],
       "all_new_receipts_equal":[r.receipt(restored.world,x["receipt_id"]) for x in result["actual_input_calls"]]==result["receipts"],
       "native_advanced_ticks":0,"scope":"Passive load and observation, not another evolution or independent sample."})
    print(json.dumps({"same_world":result["same_world_object"],"profiles":result["profiles"],"utility":result["external_utility"]}))


if __name__=="__main__":main()
