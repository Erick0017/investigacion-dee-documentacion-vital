"""Orthogonal-input refinement after the V2 unpaired controls exposed a shortcut.

This is the same directional encounter family, with an independently versioned
preparation. Query axes cancel uncued report components instead of reproducing
their useful direction. No old V2 world is relabeled, edited or overwritten.
"""
from __future__ import annotations
from array import array
import hashlib
from pathlib import Path

from .common_helpers import put,sha,observe,receipt,interface,identity

EXT=Path(__file__).resolve().parents[2]
BASE=EXT.parents[1]
N=67
CENTERS={"A":(42,20,12),"B":(30,32,12),"C":(32,36,22),"D":(18,44,16)}
SIGNALS={name:(-1,0,0) for name in CENTERS}
QUERIES={"A":(-1,0,0),"B":(0,0,1),"C":(-1,0,0),"D":(1,0,0)}
TRAIN={"A":0,"B":12,"C":10,"D":24}


def moved(site,direction,count=1,translation=(0,0,0)):
    return tuple((site[i]+count*direction[i]+translation[i])%N for i in range(3))


def digest(world):
    return {"tick":world.runtime.current_tick,
            "RAW_sha256":hashlib.sha256(array("Q",world.runtime.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",world.runtime.clock_copy()).tobytes()).hexdigest()}


def geometry(translation=(0,0,0)):
    if len(translation)!=3 or any(type(x) is not int for x in translation):raise ValueError("Integer translation required")
    centers={k:moved(v,(0,0,0),translation=translation) for k,v in CENTERS.items()}
    emit=centers["D"];action=(-1,1,1);resource=(1,0,-1);supply=(0,1,0)
    h=moved(emit,action,4);intercept=moved(h,supply,4)
    bank={"emitter":emit,"action":action,"resource_direction":resource,"supply_direction":supply,
          "cost_meeting":h,"interception":intercept,"resource_source":moved(h,resource,-4),
          "resource_receiver":moved(h,resource,3),"supply_source":moved(h,supply,-6),
          "function_receiver":moved(h,supply,2),"U_source":moved(intercept,(0,-1,0),-7),
          "V_source":moved(intercept,(0,-1,1),-7),"emission_tick":228,"resource_read":235,"function_read":242}
    return {"recipe":"ABCD03.orthogonal_joint_social.v3","N":N,"translation":list(translation),
            "centers":centers,"joint_site":moved((26,36,16),(0,0,0),translation=translation),"bank":bank,
            "training_ticks":TRAIN,"A_emission_tick":70,"C_emission_tick":80,"B_contact_tick":82,
            "joint_tick":86,"D_social_contact_tick":94,"D_read_ticks":[161,228],
            "scope":"Four finite mobile functional regions, not four fully renewable basal bodies"}


def describe_interfaces(d,spec):
    ports=[]
    for name,center in spec["centers"].items():
        ports.append(interface(name+".signal",moved(center,SIGNALS[name],-3),SIGNALS[name]))
        ports.append(interface(name+".query",moved(center,QUERIES[name],-3),QUERIES[name]))
        if name=="D":ports.append(interface("D.query_return",moved(center,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,"plus"),(-1,"minus")):
            dr=(1,sign,0) if name=="A" else (1,0,sign)
            ports.append(interface(name+".report."+label,moved(center,dr,-3),dr))
    bank=spec["bank"]
    for label,key,dr in (("resource","resource_source",bank["resource_direction"]),
                         ("supply","supply_source",bank["supply_direction"]),
                         ("U","U_source",(0,-1,0)),("V","V_source",(0,-1,1))):
        ports.append(interface("world."+label,bank[key],dr))
    for word,q in (("L1",(30,30,40)),("L2",(30,30,56))):
        hub=moved(q,(0,0,0),translation=spec["translation"])
        ports.append(interface("lex."+word+".signal",moved(hub,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,"plus"),(-1,"minus")):
            dr=(1,sign,0);ports.append(interface("lex."+word+".report."+label,moved(hub,dr,-3),dr))
    ports.append(interface("instrument.sham",moved((50,60,60),(0,0,0),translation=spec["translation"]),(1,0,0)))
    return ports


def panel(world,spec):
    t=world.runtime.current_tick;sites=dict(spec["centers"]);sites["joint"]=spec["joint_site"]
    if t>=70:sites["A_segment_plus"]=moved(spec["centers"]["A"],(-1,1,0),t-70)
    if t>=70:sites["A_segment_minus"]=moved(spec["centers"]["A"],(-1,-1,0),t-70)
    if t>=80:
        sites["C_selected_segment"]=moved(spec["centers"]["C"],(-1,0,-1),t-80)
        sites["C_uncued_report_segment"]=moved(spec["centers"]["C"],(0,0,-1),t-80)
    sites.update({"bank_"+key:spec["bank"][key] for key in ("cost_meeting","interception","resource_receiver","function_receiver")})
    return {"tick":t,"samples":{name:observe(world,q) for name,q in sites.items()}}


def edit_actual(world,site,expected_load,label,raw=None,direction=None):
    import dee_thinking as d
    before=observe(world,site)
    if not before["active"] or before["s_reg"]!=expected_load:raise ValueError("Actual selected component absent")
    if raw is None:raw=d.pack_record(before["state"],before["s_reg"],*direction,before["semantic"])
    pr=world.runtime.raw_copy();pc=world.runtime.clock_copy();prior=digest(world)
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=raw;edit.label=label
    child=world.diagnostic_fork([edit],True)
    assert [i for i,(a,b) in enumerate(zip(pr,child.runtime.raw_copy())) if a!=b]==[(site[0]*N+site[1])*N+site[2]]
    assert child.runtime.clock_copy()==pc and digest(world)==prior
    return child,{"modality":"DIAGNOSTIC_FORK","label":label,"before":before,"after":observe(child,site),
                  "RAW_sites_changed":1,"clock_sites_changed":0,"parent_unchanged":True}
