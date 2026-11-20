"""Final finite habitat extension: two physically distinct useful action routes.

The baseline policies are externally injected instrumental controls, not native
learned policies. The network rows use the actual native B emission. No score or
expected action enters the organization. All interfaces exist in the T0 recipe.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red.dual_session import NetworkSession,describe,interfaces,environment_protocol
from red import recipe_v3 as r


def actual_profile(resource,function,bank):
    R=int(resource["active"] and resource["s_reg"]==3 and resource["direction"]==list(bank["resource_direction"]))
    F=int(function["active"] and function["s_reg"]==7 and function["direction"]==list(bank["supply_direction"]))
    return [F,R]


def evaluate(world,spec,captures):
    profiles={name:actual_profile(cap["R"],cap["F"],spec["banks"][name]) for name,cap in captures.items()}
    return {"profiles":profiles,"F_sum":sum(v[0] for v in profiles.values()),"R_sum":sum(v[1] for v in profiles.values()),
            "external_utility":sum(2*v[0]+v[1] for v in profiles.values()),"world":r.digest(world),
            "scope":"Finite external task score only. It is not a reward or native answer and never feeds back into the Runtime."}


def calibration(output):
    import dee_thinking as d
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    r.identity(r.BASE/"runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl")
    spec=describe();rec=d.OrganizationRecipe.research(r.N,[],0);rec.interfaces=interfaces(d,spec);rec.execution=d.TickOptions(d.Backend.LAZY,1)
    parent=d.OrganizationalWorld.create(rec);parent.run_until(416)
    parent.save_snapshot(str(output/"EMPTY_PREPARED_T416.deetsnap"))
    initial=r.digest(parent);rows=[]
    for x in (-1,1):
        for c in (-1,1):
            for policy in ("None","N","Flat","Both"):
                world=parent.fork();ids=[];calls=[];captures={name:{} for name in spec["banks"]}
                for item in environment_protocol(x,c):
                    receipt=world.submit(item["channel"],item["load"],item["tick"]);ids.append(receipt.id);calls.append({**item,"receipt_id":receipt.id,"call_tick":416})
                for name in ("N","Flat"):
                    if policy in (name,"Both"):
                        receipt=world.submit("instrument.action_"+name+"_out",94,418);ids.append(receipt.id)
                        calls.append({"channel":"instrument.action_"+name+"_out","load":94,"tick":418,"call_tick":416,
                                      "receipt_id":receipt.id,"modality":"EXTERNAL_FIXED_REFERENCE_POLICY"})
                for tick in (424,430,431,437):
                    world.run_until(tick)
                    for name,bank in spec["banks"].items():
                        if tick==bank["resource_read"]:captures[name]["R"]=r.observe(world,bank["resource_receiver"])
                        if tick==bank["function_read"]:captures[name]["F"]=r.observe(world,bank["function_receiver"])
                record={"x":x,"c":c,"external_fixed_policy":policy,"captures":captures,**evaluate(world,spec,captures),
                        "actual_input_calls":calls,"receipts":[r.receipt(world,i) for i in ids],
                        "scope":"Independent complete fork of an empty prepared T416 world, not a learned organization and not a late erase of an existing organism."}
                rows.append(record);r.put(output/"MEASUREMENTS.json",{"parent":initial,"rows":rows,"parent_unchanged":r.digest(parent)==initial})
    # External predictions evaluate the proposed bank, never generate output.
    expected={(-1,-1):{"None":6,"N":5,"Flat":5,"Both":4},(-1,1):{"None":6,"N":5,"Flat":5,"Both":4},
              (1,-1):{"None":4,"N":5,"Flat":3,"Both":4},(1,1):{"None":4,"N":3,"Flat":5,"Both":4}}
    comparisons=[{"x":v["x"],"c":v["c"],"policy":v["external_fixed_policy"],"expected_evaluation_only":expected[(v["x"],v["c"])][v["external_fixed_policy"]],
                  "observed":v["external_utility"],"equal":v["external_utility"]==expected[(v["x"],v["c"])][v["external_fixed_policy"]]} for v in rows]
    gate=all(v["equal"] for v in comparisons) and all(all(q["status"]=="applied" for q in row["receipts"]) for row in rows)
    r.put(output/"FOLLOWUP_SELECTION.json",{"continue_network":gate,"comparisons":comparisons,
          "scope":"External finite budget selection after physical habitat calibration, not a scientific global verdict or native policy."})
    return gate


def run_network(case,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    case=dict(case);translation=tuple(case.pop("translation",(0,0,0)));control=case.pop("diagnostic_control",None)
    session=NetworkSession.create(case,translation);captures={name:{} for name in session.spec["banks"]};trace=[];edits=[]
    for tick in (0,3,13,15,27,70,80,82,85,86,93,94,160,161,227,228,242,290,291,349,350,416,417,421,424,427,430,431,437):
        trace.append(session.run_until(tick))
        if tick==228 and control:
            if control!="D_LATE_REMOVE":raise ValueError("Only the predeclared D source late cut is in this final extension")
            child,edit=r.edit_actual(session.world,session.spec["centers"]["D"],84,"DUAL_HABITAT_D_SOURCE_LATE_CUT",raw=0)
            session.world=child;session._commit();edits.append(edit)
        for name,bank in session.spec["banks"].items():
            if tick==bank["resource_read"]:captures[name]["R"]=r.observe(session.world,bank["resource_receiver"])
            if tick==bank["function_read"]:captures[name]["F"]=r.observe(session.world,bank["function_receiver"])
        if tick in (0,94,161,228,350,416,417,431,437):session.save(output/("T"+str(tick)+".deetsnap"))
        r.put(output/"PROGRESS.json",{"tick":tick,"trace":trace})
    result={"case":case,"diagnostic_control":control,"recipe":session.spec,"trace":trace,"captures":captures,
            **evaluate(session.world,session.spec,captures),"diagnostic_edits":edits,
            "receipts":[r.receipt(session.world,x["receipt_id"]) for x in session.state["protocol"]],
            "scope":"Two environmental routes with equal supplied inventory. x and c choose only external physical threat streams, never the native response. D relevance is assessed by matched context and late-cut contrasts."}
    r.put(output/"MEASUREMENTS.json",result);return session,result


def main():
    p=argparse.ArgumentParser();p.add_argument("--calibration",action="store_true");p.add_argument("--case",type=Path);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    if a.calibration:print(json.dumps({"calibration_followup":calibration(a.output)}))
    else:
        _,data=run_network(json.loads(a.case.read_text(encoding="utf-8")),a.output)
        print(json.dumps({"id":data["case"]["id"],"profiles":data["profiles"],"utility":data["external_utility"]}))


if __name__=="__main__":main()
