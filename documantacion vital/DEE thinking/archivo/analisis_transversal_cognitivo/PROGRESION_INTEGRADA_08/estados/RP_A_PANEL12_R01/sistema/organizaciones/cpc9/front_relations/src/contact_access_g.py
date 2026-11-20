"""CPC9 neutral pre-T0 access surfaces for actual late contact carriers.

No answer map, trained state, semantic name or data-dependent callback is used.
The inherited MCTS experiences and readers remain unchanged. The added surfaces
sample the actual current carrier at a different spacetime point and later use
that acquired state. Creation does not add physical material.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession, prepare_magnitude_cts
from integracion.relational_pair import move


def prepare_remote_contact(*, remote_phase=3, remote_regulation="omitted", **options):
    if remote_phase not in (2, 3):
        raise ValueError("Only two predeclared phase families")
    if remote_regulation not in ("onpath", "offpath", "omitted"):
        raise ValueError("Frozen fixed-regulation modalities")
    recipe, geometry = prepare_magnitude_cts(**options)
    ports = list(recipe.interfaces)
    surfaces = []
    for axis, label in ((-1, "left"), (1, "right")):
        for z, kind in ((0, "changed"), (-1, "free")):
            key = label + "." + kind
            hub = move(geometry["contact_base"], (axis, 1, z), remote_phase)
            query_direction = (-axis, 0, 0)
            effect = move(hub, (-axis, 1, z), 6)
            renewed = move(hub, (-axis, 0, 0), 6)
            renewed_effect = move(renewed, (-axis, 1, z), 6)
            names = {}
            for role, site, vector, lead in (
                ("record", hub, query_direction, 3),
                ("read", hub, query_direction, 3),
                ("use", effect, (axis, 0, 0), 3),
                ("renew", renewed, query_direction, 1),
                ("reuse", renewed_effect, (axis, 0, 0), 3),
            ):
                name = "remote_contact." + role + "." + key
                channel = d.ChannelSpec()
                channel.name = name
                channel.injection_site = d.Coordinate(*move(site, vector, -lead))
                channel.direction = d.Direction(*vector)
                channel.state = 1
                channel.semantic = 1
                channel.allow_experience = True
                channel.allow_probe = True
                spec = d.InterfaceSpec()
                spec.name, spec.channel = name, channel
                ports.append(spec)
                names[role] = name
            surfaces.append({"id": key, "axis": axis, "z": z, "hub": hub,
                "effect": effect, "renewed": renewed, "renewed_effect": renewed_effect,
                "ports": names})
    if len({port.name for port in ports}) != len(ports):
        raise ValueError("Added interface collision")
    regulators = []
    for item in geometry["contact"].values():
        axis = item["axis"]
        target = move(item["effect_site"], (axis,0,0), 348 - 82)
        if remote_regulation == "offpath":
            target = move(target, (0,1,0), 8)
        vector = (-axis,0,0)
        name = "remote_contact.counterflow." + str(axis) + "." + str(item["consequence_z"])
        channel = d.ChannelSpec(); channel.name = name
        channel.injection_site = d.Coordinate(*move(target,vector,-3))
        channel.direction = d.Direction(*vector); channel.state = 1; channel.semantic = 1
        channel.allow_experience = True; channel.allow_probe = True
        spec = d.InterfaceSpec(); spec.name = name; spec.channel = channel
        ports.append(spec)
        regulators.append({"port":name,"target":target,"tick":348,"input_tick":345,"payload":0,"direction":list(vector)})
    geometry["remote_contact"] = {"schema": "CPC9.remote_contact.v1", "phase": remote_phase,
        "association_tick": 340 + remote_phase, "query_tick": 407 + remote_phase,
        "use_tick": 413 + remote_phase, "renew_tick": 474 + remote_phase,
        "reuse_tick": 480 + remote_phase, "surfaces": surfaces,
        "regulation": {"mode":remote_regulation,"items":regulators,
            "claim":"R0 fixed counterflow to prior unused use-resource path, not experience-selected regulation."},
        "prepared": "Twenty inert interfaces, no initial material. Actual current-contact carrier and acquired memory supply content.",
        "modality": "Explicit candidate-port probes, not native learned selection of the appropriate port."}
    recipe.interfaces = ports
    geometry["resources"]["interfaces"] = len(ports)
    recipe.options = {"CPC8R.relational_pair.geometry": encode_metadata(geometry)}
    return recipe, geometry


class RemoteContactSession(MagnitudeCTSSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.setdefault("remote_contact_observations", [])
        # Compatibility for the first compact-metadata pilot, whose missing
        # passive histories are restored as empty observer buffers only.
        self.mode.state.setdefault("captures", [])
        self.initiative.state.setdefault("captures", [])
        self.quantity.state.setdefault("observations", [])
        self.transferred_quantity.state.setdefault("observations", [])

    @classmethod
    def create(cls, identifier="CPC9_REMOTE_CONTACT", **options):
        recipe, geometry = prepare_remote_contact(**options)
        return cls(d.OrganizationalWorld.create(recipe), geometry, identifier=identifier)

    def curriculum(self, *, remote_name="paired", remote_cue=5, remote_probe=5,
                   remote_use=7, **options):
        if remote_name not in ("paired", "unpaired", "omitted"):
            raise ValueError("Frozen recording modalities")
        super().curriculum(**options)
        g = self.geometry["remote_contact"]
        if g["regulation"]["mode"] != "omitted":
            for item in g["regulation"]["items"]:
                self.input(item["port"], item["payload"], item["input_tick"],
                    origin="FIXED_COUNTERFLOW_OLD_UNUSED_RESOURCE_ALL_BANKS_NO_TARGET_DECISION")
        for surface in g["surfaces"]:
            if remote_name != "omitted":
                self.input(surface["ports"]["record"], remote_cue,
                    g["association_tick"] - 3 + int(remote_name == "unpaired"),
                    origin="POST_ACTUAL_CONTACT_ARBITRARY_FIXED_CUE_ALL_BANKS")
            self.input(surface["ports"]["read"], remote_probe, g["query_tick"] - 3,
                "probe", "SAME_OPAQUE_PROBE_ALL_CANDIDATE_BANKS")
            self.input(surface["ports"]["use"], remote_use, g["use_tick"] - 3,
                origin="FIXED_EQUAL_CURRENT_USE_RESOURCE_ALL_BANKS")
            self.input(surface["ports"]["renew"], remote_probe, g["renew_tick"] - 1,
                "probe", "FIXED_RENEWED_PROBE_NO_CONTACT_RETEACHING")
            self.input(surface["ports"]["reuse"], remote_use, g["reuse_tick"] - 3,
                origin="FIXED_EQUAL_SECOND_USE_RESOURCE_ALL_BANKS")

    def capture_remote(self, stage):
        g = self.geometry["remote_contact"]
        field = "hub" if stage in ("pre_record", "record", "pre_read", "read") else (
            "effect" if stage in ("pre_use", "use") else (
            "renewed" if stage in ("pre_renew", "renew") else "renewed_effect"))
        rows = []
        for surface in g["surfaces"]:
            center = surface[field]
            rows.append({"id": surface["id"], "field": field,
                "physical": self.observe(center),
                "Moore27": [self.observe(move(center, (x, y, z)))
                    for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]})
        self.state["remote_contact_observations"].append({"tick": self.tick,
            "stage": stage, "surfaces": rows})

    def run_until(self, tick):
        if type(tick) is not int or tick < self.tick:
            raise ValueError("Monotone tick required")
        g = self.geometry["remote_contact"]
        stages = {}
        for key, role in (("association_tick", "record"), ("query_tick", "read"),
                ("use_tick", "use"), ("renew_tick", "renew"), ("reuse_tick", "reuse")):
            stages[g[key] - 1] = "pre_" + role
            stages[g[key]] = role
        for boundary in sorted(value for value in stages if self.tick < value <= tick):
            super().run_until(boundary)
            self.capture_remote(stages[boundary])
        return super().run_until(tick)

    def export_operational_state(self):
        state = deepcopy(self.state)
        state["mode"] = deepcopy(self.mode.state)
        state["quantity"] = deepcopy(self.quantity.state)
        state["initiative"] = deepcopy(self.initiative.state)
        state["transferred_quantity"] = deepcopy(self.transferred_quantity.state)
        return state

    def save(self, path):
        # These histories are passive auditor records, not protocol state. Keep
        # them in MEASUREMENTS, outside the bounded native metadata field.
        originals = [self.state, self.mode.state, self.quantity.state,
            self.initiative.state, self.transferred_quantity.state]
        removed = []
        for mapping in originals:
            for key in list(mapping):
                if any(word in key.lower() for word in ("observation", "capture", "window")):
                    removed.append((mapping, key, mapping[key]))
                    mapping[key] = []
        try:
            return super().save(path)
        finally:
            for mapping, key, value in removed:
                mapping[key] = value


def schedule_remote(session, *, remote_name="paired", remote_cue=5,
                    remote_probe=5, remote_use=7):
    """Add only the frozen G component agenda to an already-created owner.

    The caller has already scheduled the base experiences. All banks receive
    the same current-cue/probe/use resources. This function does not inspect an
    observation or choose a bank from an answer/target.
    """
    if remote_name not in ("paired", "unpaired", "omitted"):
        raise ValueError("Frozen recording modalities")
    g = session.geometry["remote_contact"]
    ids = []
    def emit(*args, **kwargs):
        receipt = session.input(*args, **kwargs)
        ids.append(receipt)
    if g["regulation"]["mode"] != "omitted":
        for item in g["regulation"]["items"]:
            emit(item["port"], item["payload"], item["input_tick"],
                origin="FIXED_COUNTERFLOW_OLD_UNUSED_RESOURCE_ALL_BANKS_NO_TARGET_DECISION")
    for surface in g["surfaces"]:
        if remote_name != "omitted":
            emit(surface["ports"]["record"], remote_cue,
                g["association_tick"]-3+int(remote_name=="unpaired"),
                origin="POST_ACTUAL_CONTACT_ARBITRARY_FIXED_CUE_ALL_BANKS")
        emit(surface["ports"]["read"],remote_probe,g["query_tick"]-3,
            "probe","SAME_OPAQUE_PROBE_ALL_CANDIDATE_BANKS")
        emit(surface["ports"]["use"],remote_use,g["use_tick"]-3,
            origin="FIXED_EQUAL_CURRENT_USE_RESOURCE_ALL_BANKS")
        emit(surface["ports"]["renew"],remote_probe,g["renew_tick"]-1,
            "probe","FIXED_RENEWED_PROBE_NO_CONTACT_RETEACHING")
        emit(surface["ports"]["reuse"],remote_use,g["reuse_tick"]-3,
            origin="FIXED_EQUAL_SECOND_USE_RESOURCE_ALL_BANKS")
    return ids
