"""Small public facilitators for the native 4.0 sessions.

No physical transition, forecast, learned response or environmental policy is
implemented here. Every operation below delegates to the compiled library.
The interface metadata contains external names only, never response tables.
"""
from __future__ import annotations

from pathlib import Path
import os
import shutil
import tempfile

from . import _native as native


PROFILES = ("continuidad", "comparacion", "politica", "informacion", "relaciones", "composicion")
_COGNITIVE_PROFILES = {"continuidad": "continuity", "comparacion": "comparison"}


def record(value):
    """Export a native measurement. This function does not decode an answer."""
    if isinstance(value, dict):
        return value
    if isinstance(value, native.FunctionalReadout):
        # Serialization of an inherited passive public observer, not a second
        # implementation of its relational measurement or a learned decoder.
        observations = {}
        for name, observation in value.observations.items():
            r = observation.record
            observations[name] = {"tick": observation.tick, "raw": observation.raw,
                "clock": observation.clock, "site": [observation.coordinate.x, observation.coordinate.y, observation.coordinate.z],
                "state": r.state, "semantic": r.semantic, "s_reg": r.s_reg,
                "direction": [r.dx, r.dy, r.dz]}
        return {"organization_id": value.organization_id, "tick": value.tick,
            "relative_tick": value.relative_tick, "observations": observations,
            "delta": value.delta, "centers_available": value.centers_available,
            "reader_available": value.reader_available, "supports_intact": value.supports_intact,
            "axis_projection": value.axis_projection, "scope": value.scope}
    method = getattr(value, "as_dict", None)
    if callable(method):
        result = method()
        if not isinstance(result, dict):
            raise TypeError("Native as_dict() did not return a mapping")
        return result
    raise TypeError("This native result does not expose its declared as_dict() contract")


def _seed_path():
    from importlib.resources import files
    return str(files("dee_thinking").joinpath("data", "OBP_FRESH_VALIDATED_T32.deetsnap"))


def _assign(parameters, values):
    for key, value in values.items():
        if not hasattr(parameters, key):
            raise ValueError("Unknown preparation parameter: " + key)
        if key in ("origin", "translation") and isinstance(value, (tuple, list)):
            if len(value) != 3:
                raise ValueError("origin needs three integer components")
            value = native.Coordinate(*value)
        setattr(parameters, key, value)
    return parameters


def _load_native(cls, path):
    path = Path(path).resolve()
    if str(path).isascii():
        return cls.load_snapshot(str(path))
    # A byte-preserving explicit filesystem adapter, not a physical intervention.
    with tempfile.TemporaryDirectory(prefix="dee40-load-") as folder:
        bridge = Path(folder) / "snapshot.deetsnap"
        if not str(bridge).isascii():
            raise ValueError("Use an ASCII snapshot path with this Windows native build")
        shutil.copyfile(path, bridge)
        return cls.load_snapshot(str(bridge))


class Session:
    """One native session owner, with an explicit preparation/profile contract.

    The underlying C++ object remains available as ``native``. A fork is always
    an explicit independent object. It never replaces or merges into MAIN.
    """

    def __init__(self, implementation, profile):
        if profile not in PROFILES:
            raise ValueError("Unknown session profile")
        self.native = implementation
        self.profile = profile

    @property
    def tick(self):
        return self.native.tick

    @property
    def preferred_horizon(self):
        return getattr(self.native, "preferred_horizon", None)

    @property
    def world(self):
        return self.native.world

    @property
    def journal(self):
        return self.native.journal if hasattr(self.native, "journal") else self.world.external_operations

    @property
    def interface_metadata(self):
        return dict(self.native.interface_metadata)

    def set_interface_metadata(self, metadata):
        if not isinstance(metadata, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()
        ):
            raise TypeError("External interface metadata must map strings to strings")
        if self.profile in ("continuidad", "comparacion", "relaciones"):
            for key, value in metadata.items():
                self.native.set_interface_metadata(key, value)
        else:
            self.native.set_interface_metadata(metadata)

    def _operation(self, method, *args):
        function = getattr(self.native, method, None)
        if not callable(function):
            return {
                "tick": self.tick,
                "status": "OPERATION_NOT_IMPLEMENTED_IN_PROFILE",
                "operation": method,
                "modality": "INTERFACE_NOT_NATIVE_ANSWER",
                "available": False,
            }
        result = function(*args)
        return record(self.native.observe() if result is None else result)

    def observe(self):
        return self._operation("observe")

    def sense(self):
        return self._operation("sense")

    def predict(self, horizon=None):
        if horizon is None:
            horizon = self.preferred_horizon
        return self._operation("predict") if horizon is None else self._operation("predict", horizon)

    def compare(self):
        return self._operation("compare")

    def source(self):
        return self._operation("source")

    def experience(self, symbol):
        if not isinstance(symbol, str):
            raise TypeError("Experience names are explicit strings")
        return self._operation("experience", symbol)

    def advance(self, ticks=1):
        if isinstance(ticks, bool) or not isinstance(ticks, int) or ticks < 0:
            raise ValueError("advance needs a nonnegative integer duration")
        return self._operation("advance", ticks)

    def run_until(self, absolute_tick):
        if isinstance(absolute_tick, bool) or not isinstance(absolute_tick, int) or absolute_tick < self.tick:
            raise ValueError("run_until needs a nondecreasing absolute tick")
        return self._operation("run_until", absolute_tick)

    def train(self, teachers, cue=5, mode="paired"):
        """Explicit physical teaching protocol; no learned output is supplied."""
        return self._operation("train", teachers, cue, mode)

    def train_all(self, pairs):
        return self._operation("train_all", pairs)

    def query(self, value):
        """Physical native query. The implementation owns timing and admission."""
        return self._operation("query_panel" if self.profile == "relaciones" else "query", value)

    def query_port(self, port, value):
        if self.profile != "relaciones":
            return {"tick": self.tick, "status": "OPERATION_NOT_IMPLEMENTED_IN_PROFILE",
                    "modality": "INTERFACE_NOT_NATIVE_ANSWER"}
        return self._operation("query", port, value)

    def query_sequence(self, values):
        """Execute the native, consumable five-tick mobile query protocol."""
        if self.profile != "relaciones":
            return {"tick": self.tick, "status": "OPERATION_NOT_IMPLEMENTED_IN_PROFILE",
                    "modality": "INTERFACE_NOT_NATIVE_ANSWER"}
        if self.world.protocols:
            raise ValueError("This facilitator starts one native moving sequence; continue its saved native protocol rather than silently starting a replacement")
        start = self.tick
        self.native.start_sequence(values, "public_dialogue_sequence", start)
        self.native.run_until(start + 5 * len(values))
        protocol = self.world.protocols[-1]
        steps = []
        for step in protocol.steps:
            captured = []
            for value in step.captured:
                r = value.record
                captured.append({"tick": value.tick, "raw": value.raw, "clock": value.clock,
                    "state": r.state, "semantic": r.semantic, "s_reg": r.s_reg,
                    "direction": [r.dx,r.dy,r.dz], "active": r.state > 0 and r.semantic != 5,
                    "site": [value.coordinate.x,value.coordinate.y,value.coordinate.z]})
            receipts = []
            for identity in step.receipt_ids:
                receipt = self.world.runtime.receipt(identity)
                receipts.append({"id": identity, "status": str(receipt.status),
                    "requested_tick": receipt.requested_tick, "effective_tick": receipt.effective_tick,
                    "reason": receipt.reason, "channels": list(receipt.channels)} if receipt is not None else
                    {"id": identity, "status": "MISSING_RECEIPT", "available": False})
            steps.append({"query": step.input, "input_tick": step.input_tick,
                          "read_tick": step.read_tick, "captured": captured, "receipts": receipts})
        return {"tick": self.tick, "operation": "native_query_sequence", "modality": "PHYSICAL_PROBE_ON_MAIN",
                "steps": steps, "scope": "Queries executed by the native protocol in one continuing world; captures are investigator records, not cached learned answers"}

    def fork(self):
        if not hasattr(self.native, "fork"):
            raise NotImplementedError("This profile has no published session-level fork; use explicit Runtime diagnostics")
        return Session(self.native.fork(), self.profile)

    def save_snapshot(self, path, *, include_trace=True):
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Metadata is already part of the native snapshot. No UI sidecar,
        # functions, decoder cache or pickle is needed to continue.
        with tempfile.TemporaryDirectory(prefix="dee40-save-") as folder:
            bridge = Path(folder) / "snapshot.deetsnap"
            if not str(bridge).isascii():
                raise ValueError("Use an ASCII temporary location with this Windows native build")
            self.native.save_snapshot(str(bridge), include_trace)
            staging = path.with_name(path.name + ".writing")
            shutil.copyfile(bridge, staging)
            os.replace(staging, path)
        return {"path": str(path), "tick": self.tick, "scope": "EXPLICIT_NATIVE_OPERATIONAL_SNAPSHOT"}


def create_session(profile="continuidad", **preparation):
    """Prepare one native individual. Calling again creates a different one."""
    if profile in _COGNITIVE_PROFILES:
        parameters = native.CognitiveParameters()
        parameters.seed_path = _seed_path()
        parameters.profile = _COGNITIVE_PROFILES[profile]
        implementation = native.CognitiveSession.create(_assign(parameters, preparation))
    elif profile == "politica":
        parameters = _assign(native.FinitePolicyParameters(), preparation)
        implementation = native.FinitePolicySession.create(parameters)
    elif profile == "informacion":
        parameters = native.NativeInformationParameters()
        parameters.seed_path = _seed_path()
        implementation = native.NativeInformationSession.create(_assign(parameters, preparation))
    elif profile == "relaciones":
        parameters = _assign(native.NativeAssociationParameters(), preparation)
        implementation = native.NativeAssociationSession.create(parameters)
    elif profile == "composicion":
        depth = preparation.pop("depth", 2)
        translation = preparation.pop("translation", (0, 0, 0))
        execution = preparation.pop("execution", native.TickOptions(native.Backend.LAZY, 1))
        if preparation:
            raise ValueError("Unknown composition preparation parameter")
        return CompositionSession(native.create_learnable_cascade(depth, native.Coordinate(*translation), execution))
    else:
        raise ValueError("Choose an explicit profile: " + ", ".join(PROFILES))
    return Session(implementation, profile)


def load_session(path, *, profile="continuidad"):
    """Restore, never prepare/install. The declared native loader checks format."""
    if profile == "composicion":
        return CompositionSession(_load_native(native.OrganizationalWorld, path))
    classes = {
        "continuidad": "CognitiveSession", "comparacion": "CognitiveSession",
        "politica": "FinitePolicySession", "informacion": "NativeInformationSession",
        "relaciones": "NativeAssociationSession",
    }
    if profile not in classes:
        raise ValueError("Unknown snapshot profile")
    implementation = _load_native(getattr(native, classes[profile]), path)
    if profile in _COGNITIVE_PROFILES and implementation.parameters.profile != _COGNITIVE_PROFILES[profile]:
        raise ValueError("Snapshot profile differs from the selected decoder; MAIN was not replaced")
    return Session(implementation, profile)


class CompositionSession(Session):
    """Coordinate native cascade methods; physical geometry and queries are C++."""
    KEY = "dee.cognition.composition.interface.v1"

    def __init__(self, world):
        if (world.recipe.id != "cascade.v1" or not 1 <= len(world.organization_ids) <= 8
                or world.recipe.parameters.get("source_absent") != 1):
            raise ValueError("This profile requires its declared native cascade snapshot")
        super().__init__(world, "composicion")

    @property
    def tick(self):
        return self.native.runtime.current_tick

    @property
    def world(self):
        return self.native

    @property
    def interface_metadata(self):
        import json
        packed = self.native.runtime.snapshot_metadata(self.KEY)
        return json.loads(packed) if packed else {}

    def set_interface_metadata(self, metadata):
        import json
        if not isinstance(metadata, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()):
            raise TypeError("External interface metadata must map strings to strings")
        self.native.runtime.set_snapshot_metadata(self.KEY, json.dumps(metadata, ensure_ascii=False, separators=(",", ":")))

    def observe(self):
        return {"tick": self.tick, "profile": self.profile, "modality": "PASSIVE_OBSERVATION",
                "stages": {name: record(self.native.view(name).observe()) for name in self.native.organization_ids}}

    def train_all(self, pairs):
        receipts = native.experience_composition(self.native, pairs)
        return {"tick": self.tick, "profile": self.profile, "modality": "EXPERIENCE_PROTOCOL",
                "receipts": receipts,
                "scope": "All declared pairs meet through v27 in one Runtime; no response value is assigned"}

    def query(self, value):
        return record(native.query_composition(self.native, value))

    def advance(self, ticks=1):
        if isinstance(ticks, bool) or not isinstance(ticks, int) or ticks < 0:
            raise ValueError("Nonnegative duration required")
        self.native.advance(ticks)
        return self.observe()

    def run_until(self, absolute_tick):
        self.native.run_until(absolute_tick)
        return self.observe()

    def fork(self):
        return CompositionSession(self.native.fork())


__all__ = ["PROFILES", "Session", "CompositionSession", "create_session", "load_session", "record"]
