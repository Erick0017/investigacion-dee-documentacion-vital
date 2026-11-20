"""New fixed native regulation of an observed toroidal residual.

This is not learned regulation. A zero-load, nonzero-direction carrier is real
matter supplied at a fixed declared time, whether or not D was useful. The old
dual preparation and its adverse results remain untouched.
"""
from __future__ import annotations
import json
from pathlib import Path
from . import recipe_v3 as r
from . import dual_session as base

KEY="cpc4.extension02.abcd.fixed_counterflow.v1"
ALLOWED=base.ALLOWED|{"neutralizer"}


def describe(translation=(0,0,0)):
    spec=base.describe(translation);spec["recipe"]="ABCD06.fixed_native_counterflow.v1"
    turn=spec["role"]["turn_site"]
    spec["regulation"]={"counterflow_source":r.moved(turn,(0,0,1),-5),
          "sham_source":r.moved(r.moved(turn,(0,0,1),-5),(1,0,0),10),
          "meeting":r.moved(turn,(0,0,1),-2),"direction":(0,0,1),"input_tick":290,
          "scope":"Fixed external supply of a real zero-load carrier; subsequent encounter and disappearance are native, not learned regulation or a host deletion."}
    return spec


def interfaces(d,spec):
    ports=base.interfaces(d,spec)
    ports.append(r.interface("regulation.counterflow",spec["regulation"]["counterflow_source"],(0,0,1)))
    ports.append(r.interface("regulation.sham",spec["regulation"]["sham_source"],(0,0,1)))
    return ports


def protocol(case):
    entries=base.protocol(case)
    method=case.get("neutralizer","none")
    if method not in ("none","counterflow","sham"):raise ValueError("Unknown fixed counterflow condition")
    if method!="none":entries.append({"channel":"regulation."+method,"load":0,"tick":290,"role":"FIXED_NATIVE_REGULATION_INPUT"})
    return entries


class NetworkSession(base.NetworkSession):
    @classmethod
    def create(cls,case=None,translation=(0,0,0)):
        import dee_thinking as d
        case=dict(case or {})
        if set(case)-ALLOWED:raise ValueError("Unknown finite regulation protocol fields")
        spec=describe(translation)
        recipe=d.OrganizationRecipe.research(r.N,[],0);recipe.interfaces=interfaces(d,spec);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        world=d.OrganizationalWorld.create(recipe);pending=[]
        for item in protocol(case):
            receipt=world.submit(item["channel"],item["load"],item["tick"])
            pending.append({**item,"receipt_id":receipt.id,"call_tick":0,"modality":"EXPERIENCE_PROTOCOL"})
        state={"version":6,"translation":list(translation),"case":case,"protocol":pending,"tick":0,
               "scope":"External finite protocol and fixed native counterflow input, no expected output, response cache or utility."}
        session=cls(world,spec,state);session._commit();return session

    def _commit(self):
        self.state["tick"]=self.world.runtime.current_tick
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(self.state,separators=(",",":")))

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        world=d.OrganizationalWorld.load_snapshot(str(path));text=world.runtime.snapshot_metadata(KEY)
        if not text or len(text)>131072:raise ValueError("No compatible finite regulation session metadata")
        state=json.loads(text)
        if state.get("version")!=6 or state.get("tick")!=world.runtime.current_tick or world.runtime.paused:
            raise ValueError("Version, actual tick or paused state outside session domain")
        if not isinstance(state.get("case"),dict) or set(state["case"])-ALLOWED:raise ValueError("Unknown protocol fields")
        spec=describe(tuple(state["translation"]));expected=interfaces(d,spec);actual=list(world.interfaces)
        if world.runtime.dimension!=r.N or len(expected)!=len(actual) or world.recipe.placements:raise ValueError("Changed recipe")
        lookup={item.name:item.channel for item in actual}
        if set(lookup)!={item.name for item in expected}:raise ValueError("Changed interface names")
        for item in expected:
            a,b=lookup[item.name],item.channel
            if (base._point(a.injection_site),base._direction(a.direction),a.state,a.semantic,a.allow_experience,a.allow_probe)!=(
               base._point(b.injection_site),base._direction(b.direction),b.state,b.semantic,b.allow_experience,b.allow_probe):raise ValueError("Changed physical interface: "+item.name)
        logical=protocol(state["case"])
        if len(logical)!=len(state["protocol"]):raise ValueError("Changed finite pending protocol")
        for item,planned in zip(state["protocol"],logical):
            if any(item[k]!=planned[k] for k in planned):raise ValueError("Changed actual pending protocol entry")
            rec=world.runtime.receipt(item["receipt_id"])
            if rec is None or rec.requested_tick!=planned["tick"] or list(rec.channels)!=[planned["channel"]]:raise ValueError("Missing operative receipt")
        return cls(world,spec,state)

    def observe(self):
        out=super().observe()
        out["regulation_samples"]={key:r.observe(self.world,self.spec["regulation"][key]) for key in ("counterflow_source","sham_source","meeting")}
        return out
