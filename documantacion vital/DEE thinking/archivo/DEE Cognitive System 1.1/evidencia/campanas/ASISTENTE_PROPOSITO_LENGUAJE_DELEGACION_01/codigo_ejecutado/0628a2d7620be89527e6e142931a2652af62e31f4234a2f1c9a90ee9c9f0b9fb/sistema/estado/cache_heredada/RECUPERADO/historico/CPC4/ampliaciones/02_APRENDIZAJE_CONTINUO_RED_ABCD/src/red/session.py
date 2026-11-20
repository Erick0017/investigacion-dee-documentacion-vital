"""Persistent ABCD session with a native pending-input queue, no response cache.

The user's case chooses declared external experience conditions.  All pending
inputs belong to a finite explicit protocol, not a host controller observing and
copying native messages.  Novel lexical experiences remain unscheduled.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import recipe as r

KEY="cpc4.extension02.abcd.neutral.v2"
ALLOWED={"id","roles","A_history","B_history","C_history","D_history","event",
         "A_naive","B_naive","C_naive","D_naive","A_unpaired","B_unpaired","C_unpaired","D_unpaired",
         "omit_A_query","omit_C_query","omit_D_query","omit_role_relay","omit_B_role_query"}


def role_geometry(spec):
    b=spec["centers"]["B"];joint=r.moved((30,40,20),(0,0,0),translation=spec["translation"])
    action=(0,1,1);resource=(1,-1,-1);supply=(1,0,0)
    h=r.moved(b,action,4);intercept=r.moved(h,supply,4)
    return {"turn_site":joint,"turn_input":r.moved(joint,(1,0,0),-3),"turn_tick":291,
            "B_social_tick":350,"B_role_read_tick":417,"action":action,"resource_direction":resource,
            "supply_direction":supply,"cost_meeting":h,"interception":intercept,
            "resource_source":r.moved(h,resource,-4),"resource_receiver":r.moved(h,resource,3),
            "supply_source":r.moved(h,supply,-6),"function_receiver":r.moved(h,supply,2),
            "U_source":r.moved(intercept,(-1,0,0),-7),"V_source":r.moved(intercept,(-1,0,1),-7),
            "emission_tick":417,"resource_read":424,"function_read":431,
            "scope":"Prepared native relay changes direction; D's acquired state, not a host copy, travels to B."}


def describe(translation=(0,0,0)):
    spec=r.geometry(translation);spec["recipe"]="ABCD02.vector_joint_social_roles.v2"
    spec["role"]=role_geometry(spec)
    spec["lexical_hubs"]={name:r.moved(q,(0,0,0),translation=translation) for name,q in (
        ("L1",(30,30,40)),("L2",(30,30,56)),("L3",(50,50,10)),("L4",(50,50,26)))}
    return spec


def interfaces(d,spec):
    ports=r.describe_interfaces(d,spec)
    g=spec["role"]
    ports.append(r.interface("role.turn",g["turn_input"],(1,0,0)))
    for label,key,dr in (("resource","resource_source",g["resource_direction"]),
                         ("supply","supply_source",g["supply_direction"]),
                         ("U","U_source",(-1,0,0)),("V","V_source",(-1,0,1))):
        ports.append(r.interface("role.world."+label,g[key],dr))
    for name in ("L3","L4"):
        hub=spec["lexical_hubs"][name]
        ports.append(r.interface("lex."+name+".signal",r.moved(hub,(-1,0,0),-3),(-1,0,0)))
        for sign,label in ((1,"plus"),(-1,"minus")):
            dr=(1,sign,0);ports.append(r.interface("lex."+name+".report."+label,r.moved(hub,dr,-3),dr))
    return ports


def protocol(case):
    entries=[]
    def add(name,load,tick,role):entries.append({"channel":name,"load":load,"tick":tick,"role":role})
    add("instrument.sham",13,0,"common_uninformative_inventory")
    for name in ("A","C","B","D"):
        if case.get(name+"_naive"):continue
        sign=case.get(name+"_history",-1 if name=="D" else 1)
        if type(sign) is not int or sign not in (-1,1):raise ValueError("Physical external sign must be +/-1")
        tick=r.TRAIN[name]
        add(name+".signal",5,tick+int(bool(case.get(name+"_unpaired"))),name+"_experience_signal")
        add(name+".report."+("plus" if sign==1 else "minus"),11,tick,name+"_external_report")
    for name,tick in (("A",67),("C",77),("D",158),("D",225)):
        if not case.get("omit_"+name+"_query"):add(name+".query",5,tick,name+"_physical_common_query")
    if case.get("event","U") not in ("U","V"):raise ValueError("Fixed external U/V event required")
    if case.get("roles"):
        if not case.get("omit_role_relay"):add("role.turn",5,288,"prepared_native_directional_relay")
        if not case.get("omit_B_role_query"):add("B.query",5,414,"new_B_common_social_query")
        add("role.world.resource",3,417,"fixed_resource")
        add("role.world.supply",7,423,"fixed_supply")
        add("role.world."+case.get("event","U"),11,418,"external_future_event")
    else:
        add("world.resource",3,228,"fixed_resource")
        add("world.supply",7,234,"fixed_supply")
        add("world."+case.get("event","U"),11,229,"external_future_event")
    return entries


def _point(q):return(q.x,q.y,q.z)
def _direction(q):return(q.dx,q.dy,q.dz)


class NetworkSession:
    def __init__(self,world,spec,state):self.world,self.spec,self.state=world,spec,state

    @classmethod
    def create(cls,case=None,translation=(0,0,0)):
        import dee_thinking as d
        case=dict(case or {})
        unknown=set(case)-ALLOWED
        if unknown:raise ValueError("Unknown protocol fields: "+repr(sorted(unknown)))
        spec=describe(translation)
        rec=d.OrganizationRecipe.research(r.N,[],0);rec.interfaces=interfaces(d,spec);rec.execution=d.TickOptions(d.Backend.LAZY,1)
        world=d.OrganizationalWorld.create(rec)
        pending=[]
        for item in protocol(case):
            receipt=world.submit(item["channel"],item["load"],item["tick"])
            pending.append({**item,"receipt_id":receipt.id,"call_tick":0,"modality":"EXPERIENCE_PROTOCOL"})
        state={"version":2,"translation":list(translation),"case":case,"protocol":pending,"tick":0,
               "scope":"External declared finite conditions; no expected answer, utility, decoded label or observer output is stored."}
        result=cls(world,spec,state);result._commit();return result

    def _commit(self):
        self.state["tick"]=self.world.runtime.current_tick
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(self.state,separators=(",",":")))

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        world=d.OrganizationalWorld.load_snapshot(str(path))
        text=world.runtime.snapshot_metadata(KEY)
        if not text or len(text)>131072:raise ValueError("No compatible ABCD neutral session metadata")
        state=json.loads(text)
        if state.get("version")!=2 or state.get("tick")!=world.runtime.current_tick or world.runtime.paused:
            raise ValueError("Session version, tick or paused state outside declared domain")
        spec=describe(tuple(state["translation"]))
        expected=interfaces(d,spec);actual=list(world.interfaces)
        if world.runtime.dimension!=r.N or len(expected)!=len(actual) or world.recipe.placements:
            raise ValueError("ABCD recipe/dimension mismatch")
        by_name={x.name:x.channel for x in actual}
        if set(by_name)!={x.name for x in expected}:raise ValueError("Changed session interfaces")
        for item in expected:
            a,b=by_name[item.name],item.channel
            if (_point(a.injection_site),_direction(a.direction),a.state,a.semantic,a.allow_experience,a.allow_probe)!=(
                    _point(b.injection_site),_direction(b.direction),b.state,b.semantic,b.allow_experience,b.allow_probe):
                raise ValueError("Changed physical session interface: "+item.name)
        logical=protocol(state["case"])
        if len(logical)!=len(state["protocol"]):raise ValueError("Changed finite protocol")
        for actual_item,planned in zip(state["protocol"],logical):
            if any(actual_item[k]!=planned[k] for k in planned):raise ValueError("Changed protocol entry")
            if world.runtime.receipt(actual_item["receipt_id"]) is None:raise ValueError("Lost operative receipt")
        return cls(world,spec,state)

    def run_until(self,tick):
        if type(tick) is not int or not self.world.runtime.current_tick<=tick<=4096 or self.world.runtime.paused:
            raise ValueError("Absolute monotone tick within finite supervised domain required")
        self.world.run_until(tick)
        if self.world.runtime.current_tick!=tick:raise RuntimeError("Native did not reach actual requested boundary")
        self._commit();return self.observe()

    advance_to=run_until

    def observe(self):
        before=r.digest(self.world);out=r.panel(self.world,self.spec)
        out["role_samples"]={name:r.observe(self.world,self.spec["role"][name]) for name in (
            "turn_site","cost_meeting","interception","resource_receiver","function_receiver")}
        out["lexical_samples"]={name:r.observe(self.world,hub) for name,hub in self.spec["lexical_hubs"].items()}
        out["scope"]="Current passive fields, not a cached answer or unique ancestry certificate"
        assert r.digest(self.world)==before
        return out

    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError("Do not overwrite a session snapshot")
        path.parent.mkdir(parents=True,exist_ok=True);self._commit();self.world.save_snapshot(str(path))
        return {"path":str(path.resolve()),"sha256":r.sha(path),"physical":r.digest(self.world)}

    save_snapshot=save
