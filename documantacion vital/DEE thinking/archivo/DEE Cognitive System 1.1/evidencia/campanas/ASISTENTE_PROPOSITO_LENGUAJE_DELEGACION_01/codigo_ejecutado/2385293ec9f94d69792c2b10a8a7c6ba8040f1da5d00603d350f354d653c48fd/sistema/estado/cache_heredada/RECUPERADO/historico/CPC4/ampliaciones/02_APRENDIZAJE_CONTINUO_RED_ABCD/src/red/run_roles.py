"""Finite D receiver->source / B relay->receiver attempt, one persistent MAIN."""
import argparse
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red.session import NetworkSession
from red import recipe as r


def main():
    p=argparse.ArgumentParser();p.add_argument("--case",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();case=json.loads(a.case.read_text(encoding="utf-8"));out=a.output;out.mkdir(parents=True,exist_ok=True)
    translation=tuple(case.pop("translation",(0,0,0)))
    control=case.pop("diagnostic_control",None)
    if control not in (None,"D_LATE_REMOVE","D_DZ_ZERO","SHAM_REMOVE"):
        raise ValueError("Unknown frozen diagnostic control")
    r.identity(r.BASE/"runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl")
    session=NetworkSession.create(case,translation);trace=[];edits=[]
    for tick in (0,3,13,15,27,70,80,82,85,86,93,94,160,161,227,228,242,290,291,349,350,416,417,421,424,431):
        trace.append(session.run_until(tick))
        if tick==228 and control:
            if control=="SHAM_REMOVE":
                site=r.moved((50,60,60),(1,0,0),228,translation)
                child,edit=r.edit_actual(session.world,site,13,"ABCD_ROLE_SHAM228",raw=0)
            elif control=="D_DZ_ZERO":
                child,edit=r.edit_actual(session.world,session.spec["centers"]["D"],84,"ABCD_D_CONTENT_DZ_ZERO228",direction=(-1,1,0))
            else:
                child,edit=r.edit_actual(session.world,session.spec["centers"]["D"],84,"ABCD_D_SOURCE_LATE_REMOVE228",raw=0)
            session.world=child;session._commit();edits.append(edit)
            trace[-1]["after_diagnostic"]=session.observe()
        session.save(out/("T"+str(tick)+".deetsnap"))
        r.put(out/"PROGRESS.json",{"tick":tick,"trace":trace})
    samples={row["tick"]:row for row in trace}
    resource=samples[424]["role_samples"]["resource_receiver"];function=samples[431]["role_samples"]["function_receiver"]
    R=int(resource["active"] and resource["s_reg"]==3 and resource["direction"]==[1,-1,-1])
    F=int(function["active"] and function["s_reg"]==7 and function["direction"]==[1,0,0])
    result={"case":case,"diagnostic_control":control,"diagnostic_edits":edits,"recipe":session.spec,"final":r.digest(session.world),"trace":trace,
            "D_first":samples[161]["samples"]["D"],"D_reused":samples[228]["samples"]["D"],
            "native_turn":samples[291]["role_samples"]["turn_site"],"B_social_received":samples[350]["samples"]["B"],
            "B_future_read":samples[417]["samples"]["B"],"task_profile":[F,R],"external_utility":2*F+R,
            "actual_protocol_receipts":[r.receipt(session.world,x["receipt_id"]) for x in session.state["protocol"]],
            "source_sha256":{"session.py":r.sha(Path(__file__).with_name("session.py")),"run_roles.py":r.sha(__file__)},
            "scope":"Roles are a prepared physical relay topology. D acquired its mobile state from A+B+C, later becomes the native source to B. No host message copy or learned routing policy is claimed."}
    r.put(out/"MEASUREMENTS.json",result)
    print(json.dumps({"id":case.get("id"),"profile":[F,R],"native_turn":result["native_turn"],"B_received":result["B_social_received"],"B_read":result["B_future_read"]}))


if __name__=="__main__":main()
