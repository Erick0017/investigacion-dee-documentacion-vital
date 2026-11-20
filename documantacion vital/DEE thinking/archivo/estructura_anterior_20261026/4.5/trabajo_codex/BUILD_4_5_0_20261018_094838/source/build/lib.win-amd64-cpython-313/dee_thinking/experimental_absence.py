"""EXPERIMENTAL_BUNDLED: CPC7's finite missing-actual opportunity, V2.

This separate research profile assembles an untrained N67 body and fixed
mediators before T0. All state evolution, admission and encounters occur in
the native Runtime. A missing report means specifically no report arriving at
the declared T15 aperture; it is not unbounded absence or learned uncertainty.
No laboratory import, expected-answer map or future rollout is used.
"""
from copy import deepcopy
from . import _native as native
from .consolidated import _integer, _sign, exact_observation, exact_receipt
from .persistence import (encode_metadata, decode_metadata, load_world_snapshot,
                         save_world_snapshot, DEFAULT_MAX_SNAPSHOT_BYTES)

KEY = "dee_thinking.experimental_absence.session.v1"
GEOMETRY_KEY = "dee_thinking.experimental_absence.geometry.v1"
PROFILE_STATUS = "EXPERIMENTAL_BUNDLED"


def _move(q, direction, count=1):
    return [(q[i] + direction[i] * count) % 67 for i in range(3)]


def prepare_absence_recipe(*, center=(33, 25, 33), backend="LAZY", threads=1):
    """Prepare geometry only, without history, source content or a Runtime.

    Default physical preparation adapts order_memory + comparison_need V1/V2
    from CPC7. Additional centers/backends are research preparations until
    measured. It is deliberately not the integrated source0 CPC7 U0 recipe.
    """
    if not isinstance(center, (tuple, list)) or len(center) != 3:
        raise ValueError("center requires three N67 coordinates")
    center = [_integer(v, "center coordinate", 0, 66) for v in center]
    _integer(threads, "threads", 1, 1024)
    if backend not in ("LAZY", "DENSE_SEQUENTIAL", "DENSE_PARALLEL"):
        raise ValueError("Unknown backend")
    placements = []; interfaces = []; occupied = set()

    def place(q, state, load, direction, semantic, clock, role):
        key = tuple(q)
        if key in occupied:
            raise ValueError("Initial research placements overlap")
        occupied.add(key)
        p = native.InitialPlacement(); p.site = native.Coordinate(*q)
        p.raw = native.pack_record(state, load, *direction, semantic)
        p.clock = clock; p.role = role; placements.append(p)

    def port(name, q, direction, state=1):
        c = native.ChannelSpec(); c.name = name; c.injection_site = native.Coordinate(*q)
        c.direction = native.Direction(*direction); c.state = state; c.semantic = 1
        c.allow_experience = True; c.allow_probe = True
        p = native.InterfaceSpec(); p.name = name; p.channel = c; interfaces.append(p)

    a = _move(center, (-1, 0, 0)); b = _move(center, (1, 0, 0))
    origin = _move(center, (0, -1, 0))
    role = "Fresh relative-order support, not an acquired association"
    place(a, 1000, 100, (0, 0, 0), 1, 260, role)
    place(b, 2000, 100, (0, 0, 0), 1, 260, role)
    pa = ((-1, 0, 0), (-1, 1, 1), (0, 0, 1), (0, 1, 0))
    pb = ((0, -1, 0), (0, 0, -1), (1, -1, -1), (1, 0, 0))
    for q, pattern, state, clock in ((a, pa, 3000, 31), (b, pb, 4000, 41)):
        for i, v in enumerate(pattern):
            place(_move(q, v), state+i, 0, (0, 0, 0), 4, clock+i, role)
    place(_move(center, (0, 0, 1)), 6100, 7, (0, 0, 0), 4, 19, role)
    port("event.A", _move(a, (0, -1, 0)), (0, -1, 0), 5000)
    port("event.B", _move(b, (0, 1, 0)), (0, 1, 0), 5001)
    port("order.read", origin, (0, 1, 0))
    hubs = {}; branches = {}; sources = {}; uses = {}

    def data_route(lane, sign, request_site, suffix=""):
        contact = _move(request_site, (sign, 0, 0), 5)
        key = lane + ("."+suffix if suffix else ".different")
        for value in (-1, 1):
            dr = (0, value, 0); h = _move(contact, dr, -21)
            name = "need.source."+lane+("."+suffix if suffix else "")+"."+str(value)
            for label, direction in zip(("cue", "event"), ((1, 0, 0), (-1, value, 0))):
                port(name+"."+label, _move(h, direction, -3), direction)
            sources[name] = {"lane": lane, "value": value, "hub": h,
                "direction": list(dr), "loads": [5, 18], "source_contact": contact}
            target = _move(contact, (sign, value, 0), 5)
            name = "need.use."+lane+("."+suffix if suffix else "")+"."+str(value)
            port(name, _move(target, (0, 0, 1), -3), (0, 0, 1))
            uses[name] = {"site": target, "request_tick": 26, "read_tick": 29,
                          "lane": lane, "value": value}
        branches[key]["source_contact"] = contact

    # Original V1 preparation: comparison, common opportunity and data routes.
    for sign, lane in ((-1, "left"), (1, "right")):
        hub = _move(origin, (sign, -1, 0), 10); hubs[lane] = hub
        for actual in (-1, 1):
            direction = (-actual, 0, 1)
            port("need.actual."+lane+"."+str(actual), _move(hub, direction, -4), direction)
        for dx in (0, sign):
            key = lane+(".equal" if dx == 0 else ".different")
            direction = (dx, -1, 1); q = _move(hub, direction, 4)
            place(_move(q, (0, 1, -1), -19), 1, 13, (0, 1, -1), 1, 0,
                  "Prepared common request opportunity "+key)
            branches[key] = {"lane": lane, "dx": dx, "request_site": q,
                             "comparison_direction": list(direction)}
            if dx:
                data_route(lane, sign, q)
    # V2 adds a finite opportunity on the expectation's original-z route.
    for sign, lane in ((-1, "left"), (1, "right")):
        direction = (sign, -1, 0); q = _move(hubs[lane], direction, 4)
        place(_move(q, (0, 1, 0), -19), 1, 13, (0, 1, 0), 1, 0,
              "Finite internal missing-actual opportunity "+lane)
        key = lane+".missing_actual"
        branches[key] = {"lane": lane, "dx": sign, "request_site": q,
            "comparison_direction": list(direction),
            "trigger": "Expected carrier remains in original z plane without on-time actual-induced transduction"}
        data_route(lane, sign, q, "missing_actual")
    geometry = {"schema": "dee_thinking.experimental_absence.geometry.v1", "N": 67,
        "profile_status": PROFILE_STATUS, "body": {"center": center, "A": a, "B": b,
            "emission_site": origin, "phase": 260, "source_load": 7},
        "comparison_hubs": hubs, "branches": branches, "source_codecs": sources,
        "later_queries": uses, "ticks": {"emission": 5, "actual_input": 11,
            "comparison": 15, "question": 19, "information": 24, "use": 29},
        "initial_material_sites": len(placements), "interfaces": len(interfaces),
        "scope": "Finite prepared missing-on-time-report route; not learned uncertainty, general NO, or an integrated U0 capability.",
        "provenance": {"antecedent": "CPC7 order_memory.py + comparison_need.py + comparison_need_v2.py",
                       "adaptation": "Self-contained experimental Python preparation; native v27 evolution only"}}
    recipe = native.OrganizationRecipe.research(67, placements, 0)
    recipe.interfaces = interfaces; recipe.execution = native.TickOptions(getattr(native.Backend, backend), threads)
    recipe.domain = geometry["scope"]; recipe.options = {GEOMETRY_KEY: encode_metadata(geometry)}
    return recipe, geometry


class AbsenceSession:
    """One native owner and explicit finite requests; observe never advances."""
    session_kind = "absence_v2_experimental"

    def __init__(self, world, geometry, state=None, identifier="ABSENCE_V2"):
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128:
            raise ValueError("identifier requires 1..128 characters")
        self.world = world; self.geometry = deepcopy(geometry); self.identifier = identifier
        self.state = deepcopy(state) if state is not None else {"schema": 1, "requests": [], "reads": []}
        encode_metadata(self.state); self.storage_proof = None
        if self.geometry.get("schema") != "dee_thinking.experimental_absence.geometry.v1" or int(world.runtime.dimension) != 67:
            raise ValueError("Incompatible absence profile")
        for q in self.state["requests"]:
            if world.runtime.receipt(q["id"]) is None:
                raise ValueError("Operational request absent from Runtime")

    @classmethod
    def create(cls, *, center=(33, 25, 33), backend="LAZY", threads=1, identifier="ABSENCE_V2"):
        recipe, geometry = prepare_absence_recipe(center=center, backend=backend, threads=threads)
        return cls(native.OrganizationalWorld.create(recipe), geometry, identifier=identifier)

    @property
    def tick(self):
        return int(self.world.runtime.current_tick)

    @property
    def readings(self):
        return deepcopy(self.state["reads"])

    def stimulate(self, requests):
        """Validate the complete public request batch before scheduling it."""
        channels = set(self.world.runtime.channel_names)
        if not isinstance(requests, list) or len(self.state["requests"])+len(requests) > 20000:
            raise ValueError("Explicit bounded request list required")
        checked = []
        for q in requests:
            p = q["port"]; payload = _integer(q["payload"], "payload", 0, 65535)
            tick = _integer(q["tick"], "absolute tick", self.tick); kind = q.get("kind", "submit")
            if p not in channels or kind not in ("submit", "probe"):
                raise ValueError("Undeclared physical interface or operation")
            checked.append({"port": p, "payload": payload, "tick": tick, "kind": kind})
        results = []
        for q in checked:
            r = getattr(self.world, q["kind"])(q["port"], q["payload"], q["tick"])
            self.state["requests"].append({**q, "id": int(r.id), "call_tick": self.tick})
            results.append(exact_receipt(r))
        return results

    def experience_order(self, order, *, payload=3, reader=True):
        if self.tick != 0 or order not in ("AB", "BA") or type(reader) is not bool:
            raise ValueError("Finite T0 AB/BA protocol and explicit reader boolean required")
        _integer(payload, "event payload", 1, 19664)
        entries = [{"port": "event."+v, "payload": payload, "tick": i} for i, v in enumerate(order)]
        if reader:
            entries.append({"port": "order.read", "payload": 7, "tick": 2, "kind": "probe"})
        return self.stimulate(entries)

    def acquire_source(self, value=1, *, mode="paired"):
        _sign(value)
        if self.tick != 0 or mode not in ("paired", "unpaired", "omitted"):
            raise ValueError("Finite source acquisition starts atT0")
        entries = []
        if mode != "omitted":
            for name, p in self.geometry["source_codecs"].items():
                if p["value"] == value:
                    entries.extend(({"port": name+".cue", "payload": 5, "tick": int(mode == "unpaired")},
                                    {"port": name+".event", "payload": 18, "tick": 0}))
        return self.stimulate(entries)

    def actual(self, value, *, payload=17):
        _sign(value); _integer(payload, "actual payload", 0, 65535)
        return self.stimulate([{"port": "need.actual."+lane+"."+str(value), "payload": payload, "tick": 11}
                               for lane in ("left", "right")])

    def prepare_use(self, *, payload=7):
        _integer(payload, "probe payload", 0, 65535)
        return self.stimulate([{"port": name, "payload": payload, "tick": p["request_tick"], "kind": "probe"}
                               for name, p in self.geometry["later_queries"].items()])

    def observe(self):
        def at(q):
            return exact_observation(self.world.runtime.observe(native.Coordinate(*q)))
        g = self.geometry
        return {"tick": self.tick, "provenance": "INSTRUMENTO", "profile_status": PROFILE_STATUS,
            "comparison": {k: at(q) for k, q in g["comparison_hubs"].items()},
            "questions": {k: at(p["request_site"]) for k, p in g["branches"].items()},
            "information": {k: at(p["source_contact"]) for k, p in g["branches"].items() if "source_contact" in p},
            "use": {k: at(p["site"]) for k, p in g["later_queries"].items()}}

    def _capture(self):
        row = self.observe(); groups = {"questions": [], "information": [], "use": []}
        stage = {19: "questions", 24: "information", 29: "use"}.get(self.tick)
        if stage:
            for key, p in row[stage].items():
                dx, dy, dz = p["direction"]
                shape = ((dx in (-1, 1) and dy == dz == 0) if stage == "questions" else
                         (dx in (-1, 1) and dy in (-1, 1) and dz == (1 if stage == "use" else 0)))
                receipt = None
                if stage == "use":
                    candidates = [q for q in self.state["requests"] if q["port"] == key and q["tick"] == 26 and q["kind"] == "probe"]
                    if candidates:
                        receipt = exact_receipt(self.world.runtime.receipt(candidates[-1]["id"]))
                    shape = shape and receipt is not None and receipt["status"] == "applied"
                if p["active"] and p["semantic"] == 1 and shape:
                    groups[stage].append({"route": key, "physical": p, "receipt": receipt, "provenance": "ENTE"})
        return {**row, "decoded": groups, "scope": self.geometry["scope"]}

    def run_until(self, tick):
        _integer(tick, "absolute tick", self.tick)
        for boundary in (5, 15, 19, 24, 29):
            if self.tick < boundary <= tick:
                self.world.run_until(boundary); self.state["reads"].append(self._capture())
        self.world.run_until(tick)
        return self.observe()

    def receipts(self):
        return [{**deepcopy(q), "receipt": exact_receipt(self.world.runtime.receipt(q["id"]))}
                for q in self.state["requests"]]

    def save_snapshot(self, path, *, compress=None, overwrite=False):
        self.world.runtime.set_snapshot_metadata(KEY, encode_metadata({"schema": 1, "tick": self.tick,
            "identifier": self.identifier, "state": self.state, "channels": sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world, path, compress=compress, overwrite=overwrite)

    @classmethod
    def load_snapshot(cls, path, *, max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES, expected_sha256=None):
        world, proof = load_world_snapshot(path, max_bytes=max_bytes, expected_sha256=expected_sha256)
        metadata = dict(world.runtime.snapshot_metadata_entries)
        if KEY not in metadata or GEOMETRY_KEY not in world.recipe.options:
            raise ValueError("Not an absence V2 operational snapshot")
        state = decode_metadata(metadata[KEY]); geometry = decode_metadata(world.recipe.options[GEOMETRY_KEY])
        if state["schema"] != 1 or state["tick"] != int(world.runtime.current_tick) or state["channels"] != sorted(world.runtime.channel_names):
            raise ValueError("Incompatible or stale absence V2 snapshot")
        result = cls(world, geometry, state["state"], state["identifier"]); result.storage_proof = proof
        return result

    def diagnostic_question_cut(self, *, sham=False):
        """T20 external cut/sham on a separate native fork; never replaces MAIN."""
        if self.tick != 20 or type(sham) is not bool:
            raise ValueError("Declared question-route diagnostic requiresT20")
        edits = []
        for p in self.geometry["branches"].values():
            if p["dx"]:
                q = _move(p["request_site"], (p["dx"], 0, 0))
                o = self.world.runtime.observe(native.Coordinate(*q))
                e = native.ResearchStateEdit(); e.coordinate = native.Coordinate(*q)
                e.raw = o.raw if sham else 0; e.label = "Explicit absence V2 question-route "+("sham" if sham else "cut")
                edits.append(e)
        child = self.world.diagnostic_fork(edits, True)
        return type(self)(child, self.geometry, self.state, self.identifier+(".sham" if sham else ".cut"))
