"""Compare native 3.5 preparations/evolution against primary builders.

The builder is a test fixture, not imported by the public library. Full physical
state is compared at T0, intermediate save/load and a later evolved endpoint.
"""
import argparse
from array import array
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback
import zipfile
import dee_thinking as d

SECTION="02_REPERTORIO_NATIVO_Y_CIERRES"

def state(rt):
    return {"tick":rt.current_tick,"raw":hashlib.sha256(array("Q",rt.raw_copy()).tobytes()).hexdigest(),
            "clock":hashlib.sha256(array("Q",rt.clock_copy()).tobytes()).hexdigest()}

def main(a):
    report=[]
    with tempfile.TemporaryDirectory(prefix="dt35-recipe-comparison-") as temp:
        root=Path(temp)
        with zipfile.ZipFile(a.science) as z:
            for name in ("apparatus.py","observations.py"):
                (root/name).write_bytes(z.read(SECTION+"/RUNNER/"+name))
        sys.path.insert(0,str(root));old=importlib.import_module("apparatus")
        cases=[]
        for trans in ((0,0,0),(2,1,3)):
            anchors=tuple(tuple((q[i]+trans[i])%34 for i in range(3)) for q in ((10,10,8),(10,10,24)))
            cases.append(("mobile_pair/"+str(trans),lambda t=trans:d.create_organization("mobile_pair",origin=t),lambda x=anchors:old.c6_pair(x).runtime,11,"mobile"))
        for depth in (2,4,8):
            cases.append(("cascade/"+str(depth),lambda v=depth:d.create_organization("cascade",depth=v),lambda v=depth:old.cascade_world(v)[0],11+5*(depth-1),"query"))
        cases.append(("cascade/omit2",lambda:d.create_organization("cascade",depth=4,omit=2),lambda:old.cascade_world(4,omit=2)[0],26,"query"))
        cases.append(("native_transfer/zero_relay",lambda:d.create_organization("native_transfer"),lambda:old.cascade_world(2,[(5,7),(0,0)],omit=1)[0],21,"transfer"))
        for mode in (0,1,2):
            cases.append(("phase/"+str(mode),lambda m=mode:d.create_organization("phase",mode=m),lambda m=mode:old.phase_world(m).runtime,43,"none"))
        for h in (0,1,2):
            cases.append(("distributed/"+str(h),lambda m=h:d.create_organization("distributed",history_mode=m),lambda m=h:old.distributed_world(m).runtime,20,"distributed"))
        for h in ("AB","BA","H0"):
            cases.append(("relational/"+h,lambda x=h:d.create_organization("relational",history=getattr(d.BasalHistory,x)),lambda x=h:old.quiescent(x)[0],62,"none"))
        for o in ((15,15,15),(22,20,24)):
            cases.append(("contextual/"+str(o),lambda x=o:d.create_organization("contextual",origin=x),lambda x=o:old.basal(origin=x,contextual=True).runtime,202,"none"))
        for kw in ({},{"paired":False},{"offpath":True},{"mobile_only":True},{"body_only":True}):
            cases.append(("mobile_basal/"+str(kw),lambda x=kw:d.create_organization("mobile_basal",**x),lambda x=kw:old.mobile_basal_world(**x)[0],44,"none"))
        for h,p in (("AB",23),("AB",25),("BA",23)):
            cases.append(("information/"+h+"/"+str(p),lambda h=h,p=p:d.create_organization("information",history=getattr(d.BasalHistory,h),hidden=p),lambda h=h,p=p:old.native_probe_world(h,p)[0],48,"none"))
        for arm,dest in (("both","empty"),("A_only","empty"),("B_only","empty"),("both","material"),("both","protected")):
            cases.append(("competition/"+arm+"/"+dest,lambda x=arm,y=dest:d.create_organization("competition",arm=x,destination=y),lambda x=arm,y=dest:old.competition_world(arm=x,occupied=y)[0],10,"joint"))
        for sign,paired in ((1,True),(-1,True),(1,False)):
            cases.append(("predictive/"+str((sign,paired)),lambda x=sign,y=paired:d.create_organization("predictive",sign=x,paired=y),lambda x=sign,y=paired:old.predictive_world(sign=x,paired=y)[0],30,"predictive"))
        for name,make,reference,end,inputs in cases:
            start=time.perf_counter();item={"recipe":name,"comparable":"full RAW, full uint64 clock, tick; added named interfaces reported separately"}
            try:
                w=make();r=reference();points=[]
                def compare(label):
                    left,right=state(w.runtime),state(r);points.append({"point":label,"native":left,"reference":right,"equal":left==right});assert left==right,(name,label)
                compare("T0")
                if inputs=="mobile":
                    for j,p in enumerate((7,11)):
                        for port,value in (("cue",5),("teacher",p)):
                            w.submit(f"l{j}.{port}",value,0);r.experience(f"l{j}.{port}",0,value)
                    for j in range(2):w.probe(f"q{j}.query",13,6);r.probe(f"q{j}.query",6,13)
                elif inputs in ("query","transfer"):
                    w.probe("query",0 if inputs=="transfer" else 13,6);r.probe("query",6,0 if inputs=="transfer" else 13)
                    if inputs=="transfer":
                        i=next(i for i in w.interfaces if i.name=="receiver_query");r.register_channel(i.channel)
                        w.probe("receiver_query",13,16);r.probe("receiver_query",16,13)
                elif inputs=="distributed":
                    for port,value in (("A",8),("B",9)):w.submit("integration."+port,value,0);r.experience("integration."+port,0,value)
                elif inputs=="joint":w.probe("joint_query",13,6);r.probe("joint_query",6,13)
                elif inputs=="predictive":
                    for j in (0,1):w.probe("signal"+str(j),13,6);r.probe("signal"+str(j),6,13)
                middle=w.runtime.current_tick+3
                w.run_until(middle);r.run_until(middle);compare("intermediate")
                file=root/"middle.deetsnap";w.save_snapshot(str(file));saved=d.OrganizationalWorld.load_snapshot(str(file))
                saved.run_until(end);w.run_until(end);r.run_until(end);compare("evolved_endpoint")
                assert state(saved.runtime)==state(w.runtime),"save/load continuation"
                item.update(status="PASS",points=points,save_load_future_equal=True,native_interfaces=[i.name for i in w.interfaces],reference_channels=r.channel_names)
            except Exception as e:item.update(status="FAIL",error=str(e),traceback=traceback.format_exc())
            item["seconds"]=time.perf_counter()-start;report.append(item);print(item["status"],name,item.get("error",""),flush=True)
        p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({"version":d.__version__,"cases":report,"failed":[x["recipe"] for x in report if x["status"]!="PASS"]},indent=2),encoding="utf-8")
        return int(any(x["status"]!="PASS" for x in report))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--science",required=True);p.add_argument("--output",required=True);raise SystemExit(main(p.parse_args()))
