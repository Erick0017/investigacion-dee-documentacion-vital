"""ABCD01: acquired vector relations, native joint encounter and social use.

All channels exist at T0.  Host supplies only declared experiences/resources.
No host copies an A/C emission into B or D, computes an action, or edits a clock.
The mobile states and their encounters are evolved only by the official v27.
"""
from __future__ import annotations

from array import array
import hashlib
from pathlib import Path

EXT = Path(__file__).resolve().parents[2]
BASE = EXT.parents[1]
from .common_helpers import put, sha, observe, receipt, interface, create, identity

N = 67
CENTERS = {"A": (42,20,12), "B": (30,32,12), "C": (20,36,10), "D": (26,44,24)}
SIGNALS = {"A":(-1,0,0), "B":(-1,0,0), "C":(-1,0,0), "D":(0,-1,0)}
QUERIES = {"A":(-1,0,0), "B":(0,0,1), "C":(1,0,0), "D":(0,0,1)}
TRAIN = {"A":0, "B":12, "C":10, "D":24}


def moved(site, direction, count=1, translation=(0,0,0)):
    return tuple((site[i]+count*direction[i]+translation[i]) % N for i in range(3))


def digest(world):
    rt=world.runtime
    return {"tick":rt.current_tick,
            "RAW_sha256":hashlib.sha256(array("Q",rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",rt.clock_copy()).tobytes()).hexdigest()}


def geometry(translation=(0,0,0)):
    if len(translation)!=3 or any(type(x) is not int for x in translation):
        raise ValueError("Integer toroidal translation required")
    centers={name:moved(site,(0,0,0),translation=translation) for name,site in CENTERS.items()}
    joint=moved((26,36,16),(0,0,0),translation=translation)
    emit=centers["D"];action=(-1,1,1);resource=(1,0,-1);supply=(0,1,0)
    h=moved(emit,action,4);intercept=moved(h,supply,4)
    bank={"emitter":emit,"action":action,"resource_direction":resource,"supply_direction":supply,
          "cost_meeting":h,"interception":intercept,"resource_source":moved(h,resource,-4),
          "resource_receiver":moved(h,resource,3),"supply_source":moved(h,supply,-6),
          "function_receiver":moved(h,supply,2),"U_source":moved(intercept,(0,-1,0),-7),
          "V_source":moved(intercept,(0,-1,1),-7),"emission_tick":228,"resource_read":235,"function_read":242}
    return {"recipe":"ABCD01.vector_joint_social.v1","N":N,"translation":list(translation),
            "centers":centers,"joint_site":joint,"bank":bank,"training_ticks":TRAIN,
            "A_emission_tick":70,"C_emission_tick":80,"B_contact_tick":82,
            "joint_tick":86,"D_social_contact_tick":94,"D_read_ticks":[161,228],
            "scope":"Four named finite mobile functional regions; not four complete renewable basal bodies"}


def describe_interfaces(d, spec):
    ports=[]
    for name,center in spec["centers"].items():
        ports.append(interface(name+".signal",moved(center,SIGNALS[name],-3),SIGNALS[name]))
        ports.append(interface(name+".query",moved(center,QUERIES[name],-3),QUERIES[name]))
        for sign,label in ((1,"plus"),(-1,"minus")):
            teacher=(1,sign,0) if name=="A" else ((1,0,sign) if name in ("B","C") else (sign,1,0))
            ports.append(interface(name+".report."+label,moved(center,teacher,-3),teacher))
    bank=spec["bank"]
    for label,key,dr in (("resource","resource_source",bank["resource_direction"]),
                          ("supply","supply_source",bank["supply_direction"]),
                          ("U","U_source",(0,-1,0)),("V","V_source",(0,-1,1))):
        ports.append(interface("world."+label,bank[key],dr))
    # Fixed neutral lexical channels are only interfaces, not installed history.
    for word,unshifted in (("L1",(30,30,40)),("L2",(30,30,56))):
        hub=moved(unshifted,(0,0,0),translation=spec["translation"])
        ports.append(interface("lex."+word+".signal",moved(hub,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,"plus"),(-1,"minus")):
            dr=(1,sign,0)
            ports.append(interface("lex."+word+".report."+label,moved(hub,dr,-3),dr))
    ports.append(interface("instrument.sham",moved((50,60,60),(0,0,0),translation=spec["translation"]),(1,0,0)))
    return ports


def prepare(d,translation=(0,0,0),backend=None):
    spec=geometry(translation)
    recipe=d.OrganizationRecipe.research(N,[],0)
    recipe.interfaces=describe_interfaces(d,spec)
    recipe.execution=d.TickOptions(backend or d.Backend.LAZY,1)
    return d.OrganizationalWorld.create(recipe),spec


def panel(world,spec):
    t=world.runtime.current_tick
    sites=dict(spec["centers"]);sites["joint"]=spec["joint_site"]
    if t>=70:sites["A_segment"]=moved(spec["centers"]["A"],(-1,1,0),t-70)
    if t>=80:
        sites["C_segment_plus"]=moved(spec["centers"]["C"],(1,0,1),t-80)
        sites["C_segment_minus"]=moved(spec["centers"]["C"],(1,0,-1),t-80)
    for key in ("cost_meeting","interception","resource_receiver","function_receiver"):
        sites["bank_"+key]=spec["bank"][key]
    return {"tick":t,"samples":{name:observe(world,site) for name,site in sites.items()}}


def edit_actual(world,site,expected_load,label,raw=None,direction=None):
    import dee_thinking as d
    before=observe(world,site)
    if not before["active"] or before["s_reg"]!=expected_load:
        raise ValueError("Actual selected diagnostic source absent: "+label)
    if raw is None:
        raw=d.pack_record(before["state"],before["s_reg"],*direction,before["semantic"])
    parent=digest(world);pr=world.runtime.raw_copy();pc=world.runtime.clock_copy()
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=raw;edit.label=label
    child=world.diagnostic_fork([edit],True)
    changed=[i for i,(a,b) in enumerate(zip(pr,child.runtime.raw_copy())) if a!=b]
    assert changed==[(site[0]*N+site[1])*N+site[2]]
    assert child.runtime.clock_copy()==pc and digest(world)==parent
    return child,{"modality":"DIAGNOSTIC_FORK","label":label,"before":before,
                  "after":observe(child,site),"RAW_sites_changed":1,"clock_sites_changed":0,"parent_unchanged":True}


def run(case,output,backend=None):
    import dee_thinking as d
    import time
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    identity_record=identity(BASE/"runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl")
    world,spec=prepare(d,tuple(case.get("translation",(0,0,0))),backend)
    calls=[];ids=[];edits=[];trace=[]
    def submit(name,load,tick,role):
        r=world.submit(name,load,tick);ids.append(r.id)
        calls.append({"operation":"submit","call_tick":world.runtime.current_tick,"requested_tick":tick,
                      "channel":name,"load":load,"receipt_id":r.id,"modality":"EXPERIENCE_PROTOCOL","role":role})
    def snap(name):
        world.save_snapshot(str(output/(name+".deetsnap")))
        calls.append({"operation":"save_snapshot","call_tick":world.runtime.current_tick,"physical_write":False,"name":name})
    initial=digest(world);snap("MAIN_T0")
    submit("instrument.sham",13,0,"same_uninformative_inventory")
    signs={"A":int(case.get("A_history",1)),"B":int(case.get("B_history",1)),
           "C":int(case.get("C_history",1)),"D":int(case.get("D_history",-1))}
    for name in ("A","C","B","D"):
        if case.get(name+"_naive"):continue
        tick=TRAIN[name]
        submit(name+".signal",5,tick+(1 if case.get(name+"_unpaired") else 0),name+"_acquisition_signal")
        submit(name+".report."+("plus" if signs[name]==1 else "minus"),11,tick,name+"_external_actual_report")
    for name,tick in (("A",67),("C",77),("D",158),("D",225)):
        if not case.get("omit_"+name+"_query"):
            submit(name+".query",5,tick,name+"_fixed_physical_query")
    checkpoints={3:"A_ACQUIRED",13:"C_ACQUIRED",15:"B_ACQUIRED",27:"D_PRIOR_ACQUIRED",
                 70:"A_EMITTED",80:"C_EMITTED",81:"BEFORE_B_CONTACT",82:"AFTER_B_CONTACT",
                 85:"BEFORE_JOINT",86:"AFTER_JOINT",93:"BEFORE_D_SOCIAL",94:"AFTER_D_SOCIAL",
                 160:"BEFORE_D_READ",161:"D_FIRST_READ",227:"BEFORE_D_REUSE",228:"D_REUSED_READ",242:"MAIN_FINAL"}
    captured={3,13,15,27,69,70,79,80,81,82,85,86,87,93,94,95,120,160,161,162,200,227,228,229,231,232,235,236,242}
    bank=spec["bank"];bank_reads={}
    while world.runtime.current_tick<=242:
        tick=world.runtime.current_tick
        if tick==70 and case.get("cut_A"):
            world,e=edit_actual(world,spec["centers"]["A"],21,"LATE_A_MESSAGE_REMOVE",raw=0);edits.append(e)
        if tick==80 and case.get("cut_C"):
            world,e=edit_actual(world,spec["centers"]["C"],21,"LATE_C_MESSAGE_REMOVE",raw=0);edits.append(e)
        if tick==94 and case.get("D_social_x_remove"):
            world,e=edit_actual(world,spec["centers"]["D"],74,"D_POSTSOCIAL_X_ZERO",direction=(0,1,1));edits.append(e)
        if tick==70 and case.get("sham_remove"):
            site=moved((50,60,60),(1,0,0),70,tuple(case.get("translation",(0,0,0))))
            world,e=edit_actual(world,site,13,"SHAM_DUMMY_REMOVE",raw=0);edits.append(e)
        if tick==228:
            submit("world.resource",3,228,"fixed_resource")
            submit("world.supply",7,234,"fixed_supply")
        if tick==229:
            submit("world."+case.get("event","U"),11,229,"external_future_event_independent_of_output")
        if tick==235:bank_reads["resource"]=observe(world,bank["resource_receiver"])
        if tick==242:bank_reads["function"]=observe(world,bank["function_receiver"])
        if tick in captured:trace.append(panel(world,spec))
        if tick in checkpoints:snap(checkpoints[tick])
        if tick==242:break
        world.advance()
    resource=bank_reads["resource"];function=bank_reads["function"]
    R=int(resource["active"] and resource["s_reg"]==3 and resource["direction"]==[1,0,-1])
    F=int(function["active"] and function["s_reg"]==7 and function["direction"]==[0,1,0])
    by_tick={row["tick"]:row["samples"] for row in trace}
    result={"case":case,"recipe":spec,"identity":identity_record,"initial":initial,"final":digest(world),
            "operation_calls":calls,"diagnostic_edits":edits,"trace":trace,
            "receipts":[receipt(world,i) for i in ids],"A_emission":by_tick[70]["A"],"C_emission":by_tick[80]["C"],
            "B_contact":by_tick[82]["B"],"joint":by_tick[86]["joint"],"D_social_contact":by_tick[94]["D"],
            "D_first_read":by_tick[161]["D"],"D_reused_read":by_tick[228]["D"],
            "physical_bank":bank_reads,"task_profile":[F,R],"external_utility":2*F+R,
            "elapsed_seconds":time.monotonic()-started,"native_threads":1,
            "source_sha256":sha(__file__),"runtime_external_operations":list(world.external_operations),
            "scope":"Prepared connection plus acquired native vector relations and two sequential D probes; utility is external and never supplied as an answer or reward.",
            "consumption_boundary":"The later bank may consume the emitted functional carrier; no unlimited reader or autonomous long-term maintenance is assumed."}
    put(output/"MEASUREMENTS.json",result)
    return world,spec,result
