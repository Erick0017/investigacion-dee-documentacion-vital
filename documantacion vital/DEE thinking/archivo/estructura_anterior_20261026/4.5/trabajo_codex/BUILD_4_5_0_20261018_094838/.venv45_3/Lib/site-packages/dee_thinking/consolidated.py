"""Reusable sessions over the consolidated native 4.5 preparations.

Python coordinates explicit experiences, bounded query protocols and storage.
Preparations, physical transitions and directional readout are C++ operations.
No training map, evaluator, expected answer or past response is used to answer
a new query. A scheduled request is never reported as an applied experience.
"""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from pathlib import Path

from . import _native as native
from .persistence import (DEFAULT_MAX_SNAPSHOT_BYTES, decode_metadata,
                          encode_metadata, load_world_snapshot, save_world_snapshot)

SESSION_METADATA_KEY = "dee_thinking.consolidated.session.v1"
LEGACY_KEYS = ("cpc7.update_methods.session.v1", "cpc5.extension.capacity.v1",
               "cpc6.u0.session.v1")
MAX_JOURNAL_REQUESTS = 20000


def _integer(value, name, low=0, high=2**64 - 1):
    if type(value) is not int:
        raise TypeError(name + " must be an exact integer, not bool or float")
    if not low <= value <= high:
        raise ValueError(name + " is outside its representable range")
    return value


def _sign(value):
    if type(value) is not int or value not in (-1, 1):
        raise ValueError("The current observed consequence must be exactly -1 or +1")
    return value


def _coordinate(value):
    if isinstance(value, native.Coordinate):
        return value
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise TypeError("Coordinate needs three exact integer components")
    return native.Coordinate(*[_integer(v, "coordinate", -(2**31), 2**31 - 1) for v in value])


def exact_observation(observation):
    r = observation.record
    return {"tick": int(observation.tick),
            "site": [int(observation.coordinate.x), int(observation.coordinate.y), int(observation.coordinate.z)],
            "raw": str(observation.raw), "clock": str(observation.clock),
            "state": int(r.state), "s_reg": int(r.s_reg), "semantic": int(r.semantic),
            "direction": [int(r.dx), int(r.dy), int(r.dz)],
            "active": bool(r.state > 0 and r.semantic != 5)}


def exact_receipt(receipt, identifier=None):
    if receipt is None:
        return {"id": identifier, "status": "MISSING_RECEIPT"}
    return {"id": int(receipt.id), "status": str(receipt.status),
            "channels": list(receipt.channels), "requested_tick": int(receipt.requested_tick),
            "effective_tick": None if receipt.effective_tick is None else int(receipt.effective_tick),
            "kind": str(receipt.kind), "reason": str(receipt.reason)}


def directional_readout(value):
    """Export the already-decoded native readout without another classifier."""
    return {"physical": exact_observation(value.physical),
            "receipt": exact_receipt(value.receipt), "applied": bool(value.applied),
            "covered": bool(value.covered), "value": value.value,
            "status": str(value.status), "ordinary_cap_reached": bool(value.ordinary_cap_reached),
            "modality": str(value.modality), "scope": str(value.scope)}


def _backend(value, threads):
    _integer(threads, "threads", 1, 1024)
    if isinstance(value, str):
        try:
            value = getattr(native.Backend, value)
        except AttributeError as error:
            raise ValueError("Unknown native backend") from error
    return native.TickOptions(value, threads)


class ConsolidatedSession:
    """One mutable native world owner; explicit forks never replace MAIN.

    ``attach`` is inert: it recovers the native preparation descriptor already
    stored in a world. Only ``create`` calls ``create_world``. All times are
    absolute ticks; observation does not advance and queries are physical.
    """
    session_kind = "abstract"

    def __init__(self, world, preparation, *, identifier="DEE", state=None):
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128:
            raise ValueError("identifier needs 1..128 text characters")
        self.world = world
        self.preparation = preparation
        expected_kind={"repertoire":"repertoire.cpc5.v1","integrated":"integrated_u0.cpc7.v1"}.get(self.session_kind)
        if expected_kind is not None and preparation.kind!=expected_kind:
            raise ValueError("The native preparation belongs to another session profile")
        self.identifier = identifier
        self._geometry = deepcopy(preparation.geometry())
        self._state = deepcopy(state) if state is not None else {
            "schema": 1, "requests": [], "queries": [], "next_query_id": 1,
            "branch_parent": None, "migration": None}
        self.storage_proof = None
        self._validate_state()

    @property
    def tick(self):
        return int(self.world.runtime.current_tick)

    @property
    def dimension(self):
        return int(self.world.runtime.dimension)

    @property
    def geometry(self):
        return deepcopy(self._geometry)

    @property
    def journal(self):
        return deepcopy(self._state["requests"])

    @property
    def queries(self):
        return deepcopy(self._state["queries"])

    @property
    def forms(self):
        return tuple(form.name for form in self.preparation.forms)

    def _validate_state(self):
        encode_metadata(self._state)
        if self._state.get("schema") != 1 or not isinstance(self._state.get("requests"), list):
            raise ValueError("Unsupported consolidated session protocol")
        if len(self._state["requests"]) > MAX_JOURNAL_REQUESTS:
            raise ValueError("Session journal exceeds its bound")
        if not isinstance(self._state.get("queries"), list):
            raise ValueError("Malformed query progression")
        identifiers = []
        for request in self._state["requests"]:
            identifiers.append(_integer(request["id"], "receipt ID", 1))
            if self.world.runtime.receipt(request["id"]) is None:
                raise ValueError("Protocol references a receipt absent from the loaded Runtime")
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Duplicate protocol request ID")
        _integer(self._state.get("next_query_id"), "next_query_id", 1)
        query_ids=[]
        for query in self._state["queries"]:
            _integer(query["id"], "query ID", 1)
            query_ids.append(query["id"])
            _integer(query["input_tick"], "input_tick")
            _integer(query["read_tick"], "read_tick")
            if query["read_tick"] != query["input_tick"] + 3:
                raise ValueError("Unsupported query contact interval")
            if query.get("captured") is None and query["read_tick"] < self.tick:
                raise ValueError("An uncaptured protocol read is already in the past")
            if not isinstance(query.get("items"),list) or not 1<=len(query["items"])<=65:
                raise ValueError("Malformed query item list")
            for item in query["items"]:
                _integer(item["receipt_id"],"query receipt ID",1)
                if self.world.runtime.receipt(item["receipt_id"]) is None:raise ValueError("Query receipt is missing")
                if "index" in item:self._index(item["index"])
                elif "site" in item:
                    if not isinstance(item["site"],list) or len(item["site"])!=3:raise ValueError("Malformed query site")
                    for component in item["site"]:_integer(component,"query site",0,self.dimension-1)
                else:raise ValueError("Query has neither a form nor a declared site")
        if len(query_ids)!=len(set(query_ids)) or (query_ids and max(query_ids)>=self._state["next_query_id"]):
            raise ValueError("Query progression IDs are inconsistent")

    def _index(self, form):
        if type(form) is int:
            return _integer(form, "form index", 0, len(self.preparation.forms) - 1)
        if isinstance(form, str):
            for item in self.preparation.forms:
                if item.name == form:
                    return int(item.index)
        raise ValueError("Form is outside the declared native interface")

    def _at(self, tick):
        _integer(tick, "absolute tick")
        if tick < self.tick:
            raise ValueError("Cannot schedule in the past of MAIN")
        return tick

    def _room(self, count):
        if len(self._state["requests"]) + count > MAX_JOURNAL_REQUESTS:
            raise ValueError("Journal capacity reached; no request was submitted")

    def _remember(self, receipts, *, operation, form=None, payload=None, tick=None):
        for r in receipts:
            channels=list(r.channels)
            exact_payload=payload
            if isinstance(payload,dict):
                if any(".counter." in channel for channel in channels):exact_payload=0
                elif any(channel.endswith(".signal") for channel in channels):exact_payload=payload["cue"]
                else:exact_payload=payload["event"]
            self._state["requests"].append({"id": int(r.id), "operation": operation,
                "form": form, "payload": exact_payload, "requested_tick": int(r.requested_tick),
                "call_tick": self.tick, "channels": channels})
        return [exact_receipt(r) for r in receipts]

    def receipts(self):
        return [{**deepcopy(request), "receipt": exact_receipt(
                    self.world.runtime.receipt(request["id"]), request["id"])}
                for request in self._state["requests"]]

    def submit(self, port, payload, tick, *, probe=False):
        """Explicit low-level experience/probe, not a learned selection."""
        self._at(tick); _integer(payload, "payload", 0, 65535)
        if type(probe) is not bool:
            raise TypeError("probe must be boolean")
        if not isinstance(port, str) or port not in set(self.world.runtime.channel_names):
            raise ValueError("Unknown declared physical interface")
        self._room(1)
        r = (self.world.probe if probe else self.world.submit)(port, payload, tick)
        return self._remember([r], operation="PHYSICAL_PROBE" if probe else "EXPERIENCE_PROTOCOL",
                              payload=payload, tick=tick)[0]

    def acquire(self, form, consequence, tick, *, cue=5, teacher=11, mode="paired"):
        """Queue a current consequence and an opaque cue, never an answer map."""
        i=self._index(form); _sign(consequence); self._at(tick)
        _integer(cue,"cue",0,65535); _integer(teacher,"teacher",0,65535)
        if mode not in ("paired","unpaired","no_event","no_symbol"):
            raise ValueError("Unknown finite experience protocol")
        if mode=="unpaired" and tick==2**64-1:raise ValueError("Unpaired cue tick would overflow uint64")
        name=self.preparation.forms[i].name
        self._room(2)
        if mode == "paired":
            rr=native.experience_form(self.world,self.preparation,i,consequence,tick,cue,teacher)
            return self._remember(rr,operation="PAIRED_CURRENT_EXPERIENCE",form=name,
                                  payload={"cue":cue,"event":teacher},tick=tick)
        rows=[]
        if mode != "no_event":
            rows.append(self.submit(name+".event."+("plus" if consequence==1 else "minus"),teacher,tick))
        if mode != "no_symbol":
            rows.append(self.submit(name+".signal",cue,tick+int(mode=="unpaired")))
        return rows

    experience = acquire

    def acquire_block(self, observations, tick, *, cue=5, teacher=11, mode="paired"):
        if not isinstance(observations, Mapping) or not observations:
            raise TypeError("acquire_block requires a nonempty form->current-consequence mapping")
        resolved=[(self._index(form),_sign(value)) for form,value in observations.items()]
        if len({i for i,_ in resolved}) != len(resolved):
            raise ValueError("Repeated physical form in one experience block")
        self._at(tick); self._room(2*len(resolved))
        _integer(cue,"cue",0,65535); _integer(teacher,"teacher",0,65535)
        if mode not in ("paired","unpaired","no_event","no_symbol"):
            raise ValueError("Unknown experience protocol")
        result=[]
        for i,value in resolved:
            result.extend(self.acquire(i,value,tick,cue=cue,teacher=teacher,mode=mode))
        return result

    def revise(self, form, consequence, tick, *, method="double_teacher", mode="treatment", cue=5, teacher=11):
        """A declared prepared revision protocol, not learned regulation choice."""
        i=self._index(form); _sign(consequence); self._at(tick)
        _integer(cue,"cue",0,65535); _integer(teacher,"teacher",0,65535)
        if method not in ("double_teacher","symmetric_counterflow") or mode not in ("treatment","offpath_sham"):
            raise ValueError("Unknown native revision method/control")
        if method == "symmetric_counterflow" and tick < self.tick+4:
            raise ValueError("Counterflow must be scheduled four ticks before the new pair")
        self._room(4)
        rr=native.revise_form(self.world,self.preparation,i,consequence,tick,method,mode,cue,teacher)
        return self._remember(rr,operation="PREPARED_REVISION_"+method,form=self.preparation.forms[i].name,
                              payload={"cue":cue,"event":teacher,"zero_payload_has_physical_effect":method=="symmetric_counterflow"},tick=tick)

    update = revise

    def _schedule_read(self, items, tick, payload, kind):
        self._at(tick); _integer(payload,"probe payload",0,65535)
        if tick > 2**64-4:
            raise ValueError("Query read tick would overflow uint64")
        query={"id":self._state["next_query_id"],"kind":kind,"input_tick":tick,
               "read_tick":tick+3,"payload":payload,"items":items,"captured":None}
        self._state["next_query_id"]+=1;self._state["queries"].append(query)
        return deepcopy(query)

    def schedule_query(self, forms, tick, *, payload=5):
        if isinstance(forms,(str,int)):forms=[forms]
        if not isinstance(forms,(tuple,list)) or not forms:
            raise ValueError("At least one physical form is required")
        indices=[self._index(f) for f in forms]
        if len(indices)!=len(set(indices)):raise ValueError("Duplicate query form")
        self._at(tick); _integer(payload,"probe payload",0,65535);self._room(len(indices))
        if tick>2**64-4:raise ValueError("Query read tick would overflow uint64")
        items=[]
        for i in indices:
            r=native.query_form(self.world,self.preparation,i,payload,tick)
            name=self.preparation.forms[i].name
            self._remember([r],operation="PHYSICAL_PROBE",form=name,payload=payload,tick=tick)
            items.append({"form":name,"index":i,"receipt_id":int(r.id)})
        return self._schedule_read(items,tick,payload,"forms")

    def _capture_query(self, query):
        result=[]
        for item in query["items"]:
            if "index" in item:
                r=native.read_form_response(self.world,self.preparation,item["index"],
                    item["receipt_id"],query["payload"],query["read_tick"])
            else:
                r=native.read_directional_response(self.world,_coordinate(item["site"]),
                    item["receipt_id"],query["payload"],query["read_tick"])
            result.append({"form":item.get("form"),"bank":item.get("bank"),**directional_readout(r)})
        query["captured"]={"query_id":query["id"],"input_tick":query["input_tick"],
            "read_tick":query["read_tick"],"responses":result,"modality":"PHYSICAL_PROBE_ON_MAIN",
            "scope":"Fresh native responses captured at the declared read boundary; not a table used for later answers."}

    def run_until(self, tick):
        self._at(tick)
        boundaries=sorted({q["read_tick"] for q in self._state["queries"]
                           if q["captured"] is None and self.tick<=q["read_tick"]<=tick})
        for boundary in boundaries:
            self.world.run_until(boundary)
            for q in self._state["queries"]:
                if q["captured"] is None and q["read_tick"]==boundary:self._capture_query(q)
        self.world.run_until(tick)
        return {"tick":self.tick,"operation":"NATIVE_EVOLUTION","modality":"NATIVE_EVOLUTION"}

    advance_to = run_until

    def advance(self, ticks=1):
        _integer(ticks,"tick duration")
        if self.tick+ticks>=2**64:raise ValueError("Tick overflow")
        return self.run_until(self.tick+ticks)

    def query(self, forms, tick=None, *, payload=5):
        if tick is None:
            tick=max(self.dimension,((self.tick+self.dimension-1)//self.dimension)*self.dimension)
        q=self.schedule_query(forms,tick,payload=payload)
        self.run_until(q["read_tick"])
        return deepcopy(next(v["captured"] for v in self._state["queries"] if v["id"]==q["id"]))

    def observe(self, form=None):
        if form is not None:
            f=self.preparation.forms[self._index(form)]
            return {"form":f.name,"physical":exact_observation(self.world.runtime.observe(f.hub)),
                    "modality":"PASSIVE_OBSERVATION"}
        return {"identifier":self.identifier,"kind":self.session_kind,"tick":self.tick,
            "forms":{f.name:exact_observation(self.world.runtime.observe(f.hub)) for f in self.preparation.forms},
            "sites":{name:exact_observation(self.world.runtime.observe(site)) for name,site in self.preparation.sites.items()},
            "modality":"PASSIVE_OBSERVATION","scope":"Current selected sites, not a global scalar cognition score."}

    def _metadata(self):
        return {"schema":1,"session_kind":self.session_kind,"identifier":self.identifier,
                "tick":self.tick,"dimension":self.dimension,"channels":sorted(self.world.runtime.channel_names),
                "protocol":self._state,"scope":"Operational progression and explicit requests only; no target map or response lookup policy."}

    def save_snapshot(self,path,*,compress=None,include_trace=True,overwrite=False):
        if Path(path).exists() and not overwrite:raise FileExistsError(path)
        self._validate_state()
        self.world.runtime.set_snapshot_metadata(SESSION_METADATA_KEY,encode_metadata(self._metadata()))
        return save_world_snapshot(self.world,path,compress=compress,include_trace=include_trace,overwrite=overwrite)

    save = save_snapshot

    @classmethod
    def attach(cls,world,*,identifier="DEE"):
        prep=native.preparation_for_world(world)
        target=cls
        if cls is ConsolidatedSession:
            target={"repertoire.cpc5.v1":RepertoireSession,"integrated_u0.cpc7.v1":IntegratedSession}.get(prep.kind)
            if target is None:raise ValueError("Unknown native preparation profile")
        return target(world,prep,identifier=identifier)

    @classmethod
    def load_snapshot(cls,path,*,max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES,expected_sha256=None,allow_legacy=False):
        result=load_consolidated_session(path,max_bytes=max_bytes,expected_sha256=expected_sha256,allow_legacy=allow_legacy)
        if not isinstance(result,cls):raise ValueError("Snapshot belongs to another consolidated profile")
        return result

    load = load_snapshot

    def fork(self,identifier=None):
        world=self.world.fork()
        state=deepcopy(self._state);state["branch_parent"]={"identifier":self.identifier,"tick":self.tick}
        result=type(self)(world,native.preparation_for_world(world),identifier=identifier or self.identifier+".fork",state=state)
        return result


class RepertoireSession(ConsolidatedSession):
    session_kind="repertoire"

    @classmethod
    def create(cls,*,count=16,dimension=None,plane_gap=2,translation=(0,0,0),
               revision_interfaces=True,revision_form=0,backend="LAZY",threads=1,identifier="REPERTOIRE"):
        _integer(count,"form count",1,65)
        if dimension is None:dimension=67 if count<=32 else 131
        _integer(dimension,"dimension",1,512);_integer(plane_gap,"plane gap",2,512)
        if type(revision_interfaces) is not bool:raise TypeError("revision_interfaces must be boolean")
        o=native.RepertoireOptions();o.dimension=dimension;o.forms=count;o.plane_gap=plane_gap
        o.translation=_coordinate(translation);o.revision_interfaces=revision_interfaces
        o.revision_form=_integer(revision_form,"revision form",0,count-1);o.execution=_backend(backend,threads)
        p=native.prepare_repertoire(o)
        return cls(p.create_world(),p,identifier=identifier)


class IntegratedSession(ConsolidatedSession):
    session_kind="integrated"

    @classmethod
    def create(cls,*,center=(33,25,42),guard_mode="treatment",revision_interfaces=True,
               body_source_load=0,backend="LAZY",threads=1,identifier="U0"):
        if guard_mode not in("none","treatment","sham"):raise ValueError("Unknown prepared guard mode")
        if type(revision_interfaces) is not bool:raise TypeError("revision_interfaces must be boolean")
        o=native.IntegratedOptions();o.center=_coordinate(center);o.guard_mode=guard_mode
        o.revision_interfaces=revision_interfaces;o.body_source_load=_integer(body_source_load,"source load",0,65535)
        o.execution=_backend(backend,threads);p=native.prepare_integrated_u0(o)
        return cls(p.create_world(),p,identifier=identifier)

    def experience_order(self,order,*,payload=3,reader_payload=7):
        if order not in("AB","BA") or self.tick!=0:
            raise ValueError("Published two-event order experience is AB or BA at T0")
        _integer(payload,"event payload",0,65535);_integer(reader_payload,"reader payload",0,65535)
        self._room(3)
        return [self.submit("event."+order[0],payload,0),
                self.submit("event."+order[1],payload,1),
                self.submit("order.read",reader_payload,2,probe=True)]

    def consequence(self,value,*,tick=11,payload=17):
        _sign(value);self._at(tick);_integer(payload,"sensor payload",0,65535)
        if tick!=11:raise ValueError("Published actual-event contact uses inputT11/comparisonT15")
        prefix=self._geometry["need"]["prefix"]
        self._room(2)
        return [self.submit(prefix+".actual."+lane+"."+str(value),payload,tick) for lane in("left","right")]

    def action(self,*,tick=69,payload=7):
        self._at(tick);_integer(payload,"action resource",0,65535)
        if tick!=69:raise ValueError("Published common action resource is supplied atT69")
        names=list(self._geometry["action_inputs"]);self._room(len(names))
        return [self.submit(name,payload,tick,probe=True) for name in names]

    def teach_form(self,*,tick=72,payload=5,mode="paired"):
        self._at(tick);_integer(payload,"opaque cue",0,65535)
        if mode not in("paired","unpaired","omitted") or tick!=72:
            raise ValueError("Published later opaque teaching usesT72 (orT73unpaired)")
        if mode=="omitted":return []
        names=list(self._geometry["names"].values());self._room(len(names))
        return [self.submit(v["teach_port"],payload,tick+int(mode=="unpaired")) for v in names]

    def schedule_form_query(self,tick=139,*,payload=5):
        self._at(tick);_integer(payload,"opaque query payload",0,65535)
        if tick>2**64-4:raise ValueError("Read boundary overflow")
        names=self._geometry["names"];self._room(len(names));items=[]
        for key,value in names.items():
            r=self.submit(value["query_port"],payload,tick,probe=True)
            items.append({"bank":key,"site":value["site"],"receipt_id":r["id"]})
        return self._schedule_read(items,tick,payload,"opaque_form")

    def query_form(self,tick=139,*,payload=5):
        q=self.schedule_form_query(tick,payload=payload);self.run_until(q["read_tick"])
        return deepcopy(next(v["captured"] for v in self._state["queries"] if v["id"]==q["id"]))


def create_integrated_session(**preparation):
    return IntegratedSession.create(**preparation)


def create_repertoire_session(**preparation):
    return RepertoireSession.create(**preparation)


def load_nsm_catalogue():
    """Return a documentary inventory, never a participant's learned answers."""
    from importlib.resources import files
    return decode_metadata(files("dee_thinking").joinpath("data","NSM65_CATALOGO_HISTORICO.json").read_text(encoding="utf-8"))


def load_nsm_scope():
    """Separate catalogue registration, historical evidence and 4.5 port scope."""
    from importlib.resources import files
    return decode_metadata(files("dee_thinking").joinpath("data","NSM65_ALCANCE_4_5.json").read_text(encoding="utf-8"))


def load_consolidated_session(path,*,max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES,expected_sha256=None,allow_legacy=False):
    world,proof=load_world_snapshot(path,max_bytes=max_bytes,expected_sha256=expected_sha256)
    metadata=dict(world.runtime.snapshot_metadata_entries)
    if SESSION_METADATA_KEY not in metadata:
        if allow_legacy:return _load_legacy_world(world,proof)
        raise ValueError("Not a consolidated session; explicit allow_legacy=True is required for a supported CPC7 adapter")
    value=decode_metadata(metadata[SESSION_METADATA_KEY])
    if value.get("schema")!=1 or value.get("tick")!=int(world.runtime.current_tick):
        raise ValueError("Unsupported or stale consolidated session metadata")
    if value.get("dimension")!=int(world.runtime.dimension) or value.get("channels")!=sorted(world.runtime.channel_names):
        raise ValueError("Stored session interfaces/dimension differ from the loaded native world")
    kind=value.get("session_kind");cls={"repertoire":RepertoireSession,"integrated":IntegratedSession}.get(kind)
    if cls is None:raise ValueError("Unknown consolidated session profile")
    prep=native.preparation_for_world(world)
    result=cls(world,prep,identifier=value["identifier"],state=value["protocol"])
    result.storage_proof=proof
    return result


def _load_legacy_world(world,proof):
    """Explicit limited adapter; never create/replace/reinstall the Runtime."""
    metadata=dict(world.runtime.snapshot_metadata_entries)
    found=[key for key in LEGACY_KEYS if key in metadata]
    if not found:raise ValueError("No supported CPC7 session metadata; original snapshot is preserved")
    key=found[0];value=decode_metadata(metadata[key]);g=value.get("geometry",{})
    if key in LEGACY_KEYS[:2]:
        o=native.RepertoireOptions();o.dimension=g["N"];o.forms=g["K"];o.plane_gap=g["plane_gap"]
        o.translation=_coordinate(g.get("translation",[0,0,0]));o.revision_interfaces=key==LEGACY_KEYS[0]
        p=native.prepare_repertoire(o);cls=RepertoireSession
        requests=value.get("protocol",{}).get("calls",[]);identifier="LEGACY_REPERTOIRE"
    elif g.get("schema")=="CPC7.selective_native.geometry.v1":
        o=native.IntegratedOptions();o.center=_coordinate(g["body"]["center"])
        o.guard_mode=g.get("residue_guard",{}).get("mode","none")
        o.revision_interfaces="integrated_revision" in g
        o.body_source_load=g["body"].get("prepared_scalar_source",{}).get("initial_load",0)
        p=native.prepare_integrated_u0(o);cls=IntegratedSession
        requests=value.get("requests",[]);identifier=value.get("identity","LEGACY_U0")
    else:raise ValueError("Legacy profile is not a verified consolidated preparation")
    expected={i.name for i in p.recipe.interfaces};actual=set(world.runtime.channel_names)
    if int(world.runtime.dimension)!=p.recipe.dimension or expected!=actual:
        raise ValueError("Legacy geometry/interfaces do not match this explicit adapter")
    current_forms=[(f.name,[f.hub.x,f.hub.y,f.hub.z]) for f in p.forms]
    if current_forms!=[(f["name"],f["hub"]) for f in g["forms"]]:
        raise ValueError("Legacy form supports differ from the declared native descriptor")
    # Only attach descriptor metadata to the already loaded world. Native code
    # validates the descriptor; it never installs p.recipe. Old metadata stays.
    native.attach_preparation_descriptor(world,p)
    state={"schema":1,"requests":[],"queries":[],"next_query_id":1,"branch_parent":None,
           "migration":{"source_key":key,"mode":"EXPLICIT_LEGACY_DESCRIPTOR_ATTACH_NO_REPREPARATION",
                        "prior_protocol_queries_not_reconstructed":True}}
    for q in requests:
        state["requests"].append({"id":int(q["id"]),"operation":"LEGACY_EXPLICIT_REQUEST",
            "form":None,"payload":q.get("payload"),"requested_tick":q.get("tick",q.get("requested_tick")),
            "call_tick":q.get("call_tick",0),"channels":list(world.runtime.receipt(int(q["id"])).channels)})
    result=cls(world,native.preparation_for_world(world),identifier=identifier,state=state)
    result.storage_proof=proof
    return result
