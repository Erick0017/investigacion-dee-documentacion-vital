"""Fresh N131 research preparation combining native K65 and adapted U0.

No trained state is imported. Python assembles declared initial resources and
transports experiences; v27 exclusively produces all responses/encounters.
The N67 torus is not embedded as a copy: paths are rebuilt modulo the fixed
new N, with D=N-16 preserving the shared-action geometry.
"""
from __future__ import annotations
from copy import deepcopy
from array import array
import hashlib
from pathlib import Path
import dee_thinking as dee
from dee_thinking import _native as native
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, decode_metadata, save_world_snapshot, load_world_snapshot

GEOMETRY_KEY = "CPC8.integration.shared_geometry.v1"
SESSION_KEY = "CPC8.integration.shared_session.v1"


def exact_int(v, name, lo=0, hi=2**64-1):
    if type(v) is not int:
        raise TypeError(name+" must be an exact integer")
    if not lo <= v <= hi:
        raise ValueError(name+" outside declared range")
    return v


def sign(v):
    if type(v) is not int or v not in (-1, 1):
        raise ValueError("Current directional consequence must be +/-1")
    return v


def move(q, d, count=1, n=131):
    return [(q[i]+d[i]*count) % n for i in range(3)]


def physical(world):
    r=world.runtime
    return {"tick":int(r.current_tick),
        "RAW_sha256":hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
        "clocks_sha256":hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def build_geometry(*, dimension=131, count=65, center=(35,70,70), translation=(60,60,0), guard_mode="treatment"):
    """Pure preT0 preparation; contains no history or teaching-value map."""
    if dimension not in (131,151) or count not in (63,65):
        raise ValueError("Frozen research families N131/N151 and K63/K65 only")
    if guard_mode not in ("none","treatment","sham"):
        raise ValueError("Explicit prepared guard modality required")
    n=dimension
    for q in (center,translation):
        if len(q)!=3:raise ValueError("Three preparation coordinates required")
        for v in q:exact_int(v,"coordinate",0,n-1)
    options=native.RepertoireOptions();options.dimension=n;options.forms=count
    options.plane_gap=2;options.translation=native.Coordinate(*translation);options.revision_interfaces=False
    options.execution=native.TickOptions(native.Backend.LAZY,1)
    prep=native.prepare_repertoire(options);recipe=prep.recipe
    placements=list(recipe.placements);interfaces=list(recipe.interfaces);occupied=set()

    def at(q,d,c=1):return move(q,d,c,n)
    def put(q,state,load,semantic,clock,role,direction=(0,0,0)):
        if tuple(q) in occupied:raise ValueError("New initial material overlaps")
        occupied.add(tuple(q));p=native.InitialPlacement();p.site=native.Coordinate(*q)
        p.raw=native.pack_record(state,load,*direction,semantic);p.clock=clock;p.role=role;placements.append(p)
    def port(name,q,direction,state=1):
        c=native.ChannelSpec();c.name=name;c.injection_site=native.Coordinate(*q)
        c.direction=native.Direction(*direction);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        i=native.InterfaceSpec();i.name=name;i.channel=c;interfaces.append(i)

    center=list(center);a=at(center,(-1,0,0));b=at(center,(1,0,0));origin=at(center,(0,-1,0))
    bodyrole="CPC8 fresh adapted order support; no acquired relation atT0"
    put(a,1000,100,1,260,bodyrole);put(b,2000,100,1,260,bodyrole)
    pa=((-1,0,0),(-1,1,1),(0,0,1),(0,1,0));pb=((0,-1,0),(0,0,-1),(1,-1,-1),(1,0,0))
    for q,pattern,state,clock in ((a,pa,3000,31),(b,pb,4000,41)):
        for i,d in enumerate(pattern):put(at(q,d),state+i,0,4,clock+i,bodyrole)
    put(at(center,(0,0,1)),6100,0,4,19,"CPC8 fresh explicit source0 preparation")
    port("event.A",at(a,(0,-1,0)),(0,-1,0),5000);port("event.B",at(b,(0,1,0)),(0,1,0),5001)
    port("order.read",origin,(0,1,0))
    distance=n-16;info=19+distance;action=info+2;association=action+3
    comparisons={};questions={};banks={};actions={};names={};guards=[]
    for sx,lane in ((-1,"left"),(1,"right")):
        comparison=at(origin,(sx,-1,0),10);comparisons[lane]=comparison
        for actual in (-1,1):
            direction=(-actual,0,1);port("need.actual."+lane+"."+str(actual),at(comparison,direction,-4),direction)
        for dx in (0,sx):
            key=lane+(".equal" if dx==0 else ".different");q=at(comparison,(dx,-1,1),4)
            questions[key]={"site":q,"dx":dx,"lane":lane}
            put(at(q,(0,1,-1),-19),1,13,1,0,"CPC8 fixed comparison-request opportunity "+key,(0,1,-1))
        h=at(questions[lane+".different"]["site"],(sx,0,0),distance)
        name="U."+lane;banks[lane]={"name":name,"hub":h,"request_direction":sx,"question_distance":distance}
        port(name+".signal",at(h,(-1,0,0),-3),(-1,0,0))
        for v,label in ((-1,"minus"),(1,"plus")):
            port(name+".event."+label,at(h,(1,v,0),-3),(1,v,0))
            target=at(h,(sx,v,0),2);actionport="own.use."+label
            if actionport not in actions:
                port(actionport,at(target,(0,0,1),-3),(0,0,1));actions[actionport]={"site":target,"direction":[0,0,1]}
            elif actions[actionport]["site"]!=target:raise ValueError("New torus does not preserve shared action encounter")
            anchor=at(target,(sx,v,1),3);cue=(-sx,0,-1);key=lane+"."+label
            teach="own.name.teach."+key;query="own.name.query."+key
            port(teach,at(anchor,cue,-3),cue);port(query,at(anchor,(-1,0,0),-3),(-1,0,0))
            names[key]={"site":anchor,"cue_direction":list(cue),"teach_port":teach,"query_port":query,"lane":lane,"content_direction":v}
    if guard_mode!="none":
        candidates=[(p["site"],p["cue_direction"],"unused_cue."+k) for k,p in names.items()]
        candidates += [(p["site"],[0,0,1],"unused_action."+k) for k,p in actions.items()]
        for q,d,role in candidates:
            site=at(q,d,8)
            if guard_mode=="sham":site=at(site,(0,1,0),12)
            put(site,1,0,4,0,"CPC8 prepared fixed interception "+role);guards.append({"site":site,"direction":list(d),"role":role})
    if len({i.name for i in interfaces})!=len(interfaces):raise ValueError("Duplicate interface name")
    geometry={"schema":"CPC8.integration.shared_geometry.v1","N":n,"K":count,
        "lower_forms":prep.geometry()["forms"],"lower_translation":list(translation),"own_banks":banks,
        "body":{"center":center,"A":a,"B":b,"emission":origin,"phase":260,"source_load":0},
        "comparison_hubs":comparisons,"questions":questions,"actions":actions,"names":names,
        "guards":{"mode":guard_mode,"objects":guards,"learned_scheduling":False},
        "ticks":{"emission":5,"actual_input":11,"comparison":15,"question":19,"information":info,
            "action_input":action-3,"action":action,"teach_input":association-3,"association":association,
            "name_query_input":association+n-3,"name_read":association+n},
        "resources":{"independent_lower_relations":count,"extra_own_relations":2,"total_prepared_relation_interfaces":count+2,
            "initial_material_sites":len(placements),"interfaces":len(interfaces),"base_buffer_estimate":32*n**3},
        "scope":"Fresh research adaptation of finite CPC7 U0 plus official native lower repertoire; no inherited functional guarantee at newN or65NSM claim."}
    recipe.placements=placements;recipe.interfaces=interfaces
    org=native.OrganizationSpec();org.id="U0_CPC8";org.recipe_id="CPC8.adapted_u0.v1"
    org.a=native.Coordinate(*a);org.b=native.Coordinate(*b);org.comparator=native.Coordinate(*center)
    org.ports={"center":native.Coordinate(*center),"A":native.Coordinate(*a),"B":native.Coordinate(*b),"emission":native.Coordinate(*origin)}
    recipe.organizations=list(recipe.organizations)+[org]
    recipe.options={**dict(recipe.options),GEOMETRY_KEY:encode_metadata(geometry)}
    recipe.domain=geometry["scope"]
    return recipe,prep,geometry


class SharedSession:
    def __init__(self,world,preparation,geometry,state=None,identifier="CPC8_E1"):
        self.world=world;self.preparation=preparation;self.geometry=deepcopy(geometry);self.identifier=identifier
        self.state=deepcopy(state) if state is not None else {"schema":1,"requests":[],"queries":[],"reads":[],"frames":[],"parent":None}
        if int(world.runtime.dimension)!=geometry["N"]:raise ValueError("Stored geometry dimension differs")
        encode_metadata(self.state)
    @classmethod
    def create(cls,**options):
        identifier=options.pop("identifier","CPC8_E1");recipe,p,g=build_geometry(**options)
        return cls(native.OrganizationalWorld.create(recipe),p,g,identifier=identifier)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def _remember(self,r,port,payload,tick,kind,origin):
        self.state["requests"].append({"id":int(r.id),"port":port,"payload":payload,"tick":tick,"kind":kind,"origin":origin,"call_tick":self.tick})
        return exact_receipt(r)
    def stimulate(self,entries):
        known=set(self.world.runtime.channel_names);checked=[]
        for q in entries:
            if q["port"] not in known or q.get("kind","submit") not in ("submit","probe"):raise ValueError("Undeclared stimulus")
            exact_int(q["payload"],"payload",0,65535);exact_int(q["tick"],"tick",self.tick)
            checked.append(q)
        return [self._remember(getattr(self.world,q.get("kind","submit"))(q["port"],q["payload"],q["tick"]),
            q["port"],q["payload"],q["tick"],q.get("kind","submit"),q.get("origin","EXPLICIT_EXTERNAL_INPUT")) for q in checked]
    def experience_order(self,order,payload=3):
        if order not in ("AB","BA") or self.tick!=0:raise ValueError("Published order exposure beginsT0")
        return self.stimulate([{"port":"event."+v,"payload":payload,"tick":i,"origin":"CURRENT_LOCAL_EVENT"} for i,v in enumerate(order)]+
            [{"port":"order.read","payload":7,"tick":2,"kind":"probe","origin":"COMMON_ORDER_READER"}])
    def experience_own(self,values,*,mode="paired"):
        if self.tick!=0 or set(values)!={"left","right"} or mode not in ("paired","unpaired","omitted"):raise ValueError("Explicit fresh own-memory experience required")
        entries=[]
        for lane,v in values.items():
            sign(v)
            if mode!="omitted":
                name=self.geometry["own_banks"][lane]["name"]
                entries.extend([{"port":name+".signal","payload":5,"tick":int(mode=="unpaired"),"origin":"OPAQUE_CUE"},
                    {"port":name+".event."+("plus" if v>0 else "minus"),"payload":11,"tick":0,"origin":"CURRENT_LOCAL_DIRECTIONAL_CONSEQUENCE"}])
        return self.stimulate(entries)
    def experience_lower(self,values,indices,at_tick):
        exact_int(at_tick,"acquisition tick",self.tick);indices=list(indices)
        for k in indices:exact_int(k,"form index",0,self.geometry["K"]-1);sign(values[k])
        result=[]
        for k in indices:
            rs=native.experience_form(self.world,self.preparation,k,values[k],at_tick)
            name=self.preparation.forms[k].name
            result.append(self._remember(rs[0],name+".signal",5,at_tick,"submit","CURRENT_OPAQUE_CUE"))
            result.append(self._remember(rs[1],name+".event."+("plus" if values[k]>0 else "minus"),11,at_tick,"submit","CURRENT_DIRECTIONAL_EVENT"))
        return result
    def actual(self,value):
        sign(value)
        return self.stimulate([{"port":"need.actual."+lane+"."+str(value),"payload":17,"tick":11,"origin":"CURRENT_SENSOR_REPORT"} for lane in ("left","right")])
    def action_resources(self,payload=7):
        return self.stimulate([{"port":port,"payload":payload,"tick":self.geometry["ticks"]["action_input"],"kind":"probe","origin":"ALL_CONTENT_INDEPENDENT_ACTION_OPPORTUNITIES"} for port in self.geometry["actions"]])
    def teach_name(self,mode="paired",payload=5):
        if mode not in ("paired","unpaired","omitted"):raise ValueError("Explicit name exposure mode required")
        if mode=="omitted":return []
        return self.stimulate([{"port":p["teach_port"],"payload":payload,"tick":self.geometry["ticks"]["teach_input"]+int(mode=="unpaired"),"origin":"ALL_CANDIDATE_OPAQUE_CUES"} for p in self.geometry["names"].values()])
    def query_lower(self,indices,at_tick,payload=9):
        exact_int(at_tick,"query tick",self.tick);indices=list(indices);items=[]
        for k in indices:exact_int(k,"form index",0,self.geometry["K"]-1)
        for k in indices:
            r=native.query_form(self.world,self.preparation,k,payload,at_tick);name=self.preparation.forms[k].name
            self._remember(r,name+".signal",payload,at_tick,"probe","DECLARED_LOWER_PANEL");items.append({"index":k,"receipt_id":int(r.id)})
        self.state["queries"].append({"kind":"lower","input_tick":at_tick,"read_tick":at_tick+3,"payload":payload,"items":items,"captured":None})
    def query_name(self,at_tick=None,payload=9):
        if at_tick is None:at_tick=self.geometry["ticks"]["name_query_input"]
        items=[]
        for key,p in self.geometry["names"].items():
            r=self.world.probe(p["query_port"],payload,at_tick);self._remember(r,p["query_port"],payload,at_tick,"probe","FIXED_ALL_BANK_OPAQUE_QUERY")
            items.append({"key":key,"site":p["site"],"receipt_id":int(r.id)})
        self.state["queries"].append({"kind":"name","input_tick":at_tick,"read_tick":at_tick+3,"payload":payload,"items":items,"captured":None})
    def observe(self):
        def at(q):return exact_observation(self.world.runtime.observe(native.Coordinate(*q)))
        g=self.geometry
        return {"tick":self.tick,"body":{k:at(g["body"][k]) for k in ("A","B","center","emission")},
            "questions":{k:at(p["site"]) for k,p in g["questions"].items()},
            "own_information":{k:at(p["hub"]) for k,p in g["own_banks"].items()},
            "actions":{k:at(p["site"]) for k,p in g["actions"].items()},
            "names":{k:at(p["site"]) for k,p in g["names"].items()},"provenance":"PASSIVE_INSTRUMENT"}
    def run_until(self,tick):
        exact_int(tick,"absolute target",self.tick)
        t=self.geometry["ticks"]
        critical={5,15,19,20,t["information"]-1,t["information"],t["action"],t["association"]-1,t["association"],t["name_read"]-1,t["name_read"]}
        critical.update(q["read_tick"] for q in self.state["queries"] if q["captured"] is None)
        for boundary in sorted(q for q in critical if self.tick<q<=tick):
            self.world.run_until(boundary);self.state["frames"].append(self.observe())
            for q in self.state["queries"]:
                if q["captured"] is None and q["read_tick"]==boundary:
                    rows=[]
                    for item in q["items"]:
                        if q["kind"]=="lower":
                            r=native.read_form_response(self.world,self.preparation,item["index"],item["receipt_id"],q["payload"],boundary)
                            name=self.preparation.forms[item["index"]].name
                        else:
                            r=native.read_directional_response(self.world,native.Coordinate(*item["site"]),item["receipt_id"],q["payload"],boundary);name=item["key"]
                        rows.append({"name":name,"physical":exact_observation(r.physical),"receipt":exact_receipt(r.receipt),
                            "coverage":bool(r.covered),"value":r.value,"status":r.status,"provenance":"ENTE"})
                    q["captured"]={"tick":boundary,"kind":q["kind"],"responses":rows};self.state["reads"].append(deepcopy(q["captured"]))
        self.world.run_until(tick);return self.observe()
    def receipts(self):
        return [{**deepcopy(q),"receipt":exact_receipt(self.world.runtime.receipt(q["id"]))} for q in self.state["requests"]]
    def save(self,path):
        value={"schema":1,"tick":self.tick,"identifier":self.identifier,"state":self.state,"channels":sorted(self.world.runtime.channel_names)}
        self.world.runtime.set_snapshot_metadata(SESSION_KEY,encode_metadata(value,max_bytes=8*1024**2))
        return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        world,proof=load_world_snapshot(path,max_bytes=1024**3)
        meta=dict(world.runtime.snapshot_metadata_entries);value=decode_metadata(meta[SESSION_KEY],max_bytes=8*1024**2)
        geometry=decode_metadata(world.recipe.options[GEOMETRY_KEY]);p=native.preparation_for_world(world)
        if value["tick"]!=int(world.runtime.current_tick) or value["channels"]!=sorted(world.runtime.channel_names):raise ValueError("Incompatible/stale operational state")
        return cls(world,p,geometry,value["state"],value["identifier"])
    def diagnostic_question(self,sham=False):
        if self.tick!=20 or type(sham) is not bool:raise ValueError("Fixed external diagnostic atT20 only")
        edits=[]
        for p in self.geometry["questions"].values():
            if p["dx"]:
                q=move(p["site"],(p["dx"],0,0),1,self.geometry["N"]);o=self.world.runtime.observe(native.Coordinate(*q))
                e=native.ResearchStateEdit();e.coordinate=native.Coordinate(*q);e.raw=o.raw if sham else 0;e.label="CPC8 explicit question "+("sham" if sham else "cut");edits.append(e)
        before=physical(self.world);child=self.world.diagnostic_fork(edits,True)
        if physical(self.world)!=before:raise AssertionError("Diagnostic changed MAIN")
        state=deepcopy(self.state);state["parent"]={"identifier":self.identifier,"physical":before,"modality":"DIAGNOSTIC_FORK"}
        return type(self)(child,native.preparation_for_world(child),self.geometry,state,self.identifier+(".sham" if sham else ".cut"))
