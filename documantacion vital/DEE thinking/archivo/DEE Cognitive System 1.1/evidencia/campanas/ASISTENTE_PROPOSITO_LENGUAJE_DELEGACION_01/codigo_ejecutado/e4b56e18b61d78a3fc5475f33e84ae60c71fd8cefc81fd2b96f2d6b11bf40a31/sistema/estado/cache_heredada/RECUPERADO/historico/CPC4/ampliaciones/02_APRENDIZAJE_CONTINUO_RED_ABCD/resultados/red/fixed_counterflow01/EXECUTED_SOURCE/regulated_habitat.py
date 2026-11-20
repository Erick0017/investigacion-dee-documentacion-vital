"""One finite predeclared counterflow preparation; no edits or resets on MAIN."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
from red.regulated_session import NetworkSession
from red.dual_habitat import evaluate
from red.residual_diagnostic import empty_branch


def run(case,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False);case=dict(case);tr=tuple(case.pop("translation",(0,0,0)))
    session=NetworkSession.create(case,tr);captures={key:{} for key in session.spec["banks"]};trace=[];branches={}
    for tick in (0,3,13,15,27,70,80,82,85,86,93,94,160,161,227,228,290,291,292,293,294,349,350,416,417,421,424,425,427,430,431,437):
        trace.append(session.run_until(tick))
        if tick==292:branches["meeting292"]=empty_branch(session.world,session.spec["regulation"]["meeting"])
        if tick==293:
            branches["meeting293"]=empty_branch(session.world,session.spec["regulation"]["meeting"])
        if tick==424:branches["late_turn424"]=empty_branch(session.world,session.spec["role"]["turn_site"])
        for name,bank in session.spec["banks"].items():
            if tick==bank["resource_read"]:captures[name]["R"]=r.observe(session.world,bank["resource_receiver"])
            if tick==bank["function_read"]:captures[name]["F"]=r.observe(session.world,bank["function_receiver"])
        if tick in (0,94,161,228,291,292,293,294,350,417,437):session.save(out/("T"+str(tick)+".deetsnap"))
        r.put(out/"PROGRESS.json",{"tick":tick,"trace":trace})
    result={"case":case,"translation":tr,"recipe":session.spec,"trace":trace,"local_contexts":branches,"captures":captures,
            **evaluate(session.world,session.spec,captures),"receipts":[r.receipt(session.world,p["receipt_id"]) for p in session.state["protocol"]],
            "actual_input_calls":session.state["protocol"],"diagnostic_edits":[],
            "scope":"One evolving MAIN, all ports preT0, no direct RAW/clock edits or operational forks. Counterflow is fixed external prepared supply, not acquired regulation. External score never enters Runtime."}
    r.put(out/"MEASUREMENTS.json",result);return result


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--case",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    data=run(json.loads(a.case.read_text(encoding="utf-8")),a.output)
    print(json.dumps({"id":data["case"]["id"],"profiles":data["profiles"],"utility":data["external_utility"]}))
