"""Official4/v27, exact inherited snapshots, passive records and declared ports."""
from array import array
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT.parents[1]
NATIVE_SHA="20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066"
WHEEL_SHA="17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623"


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")


def inherited_channel():
    """Load only the passive/port apparatus module, never an old campaign main."""
    name="cpc4_frozen_channel_continuation"
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,PARENT/"src/channel.py")
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return sys.modules[name]


def identity():
    import dee_thinking as d
    if d.__version__!="4.0.0" or d.kernel_identity()["kernel_version"]!=27 or sha(d._native.__file__)!=NATIVE_SHA:
        raise RuntimeError("Exact official4/v27 required")
    return {"version":d.__version__,"kernel":27,"native_sha256":sha(d._native.__file__),"module":d.__file__,"python":sys.executable}


def load(path):
    import dee_thinking as d
    identity()
    world=d.OrganizationalWorld.load_snapshot(str(path))
    if world.runtime.paused:raise ValueError("Paused Runtime not advanced or falsely labelled")
    raw=world.runtime.snapshot_metadata("cpc4.lexical.neutral.v1")
    if not raw:raise ValueError("Real lexical genealogy metadata absent")
    neutral=json.loads(raw)
    if world.runtime.dimension!=67 or sorted(neutral["word_order"])!=["W1","W2"]:
        raise ValueError("Inherited finite apparatus contract mismatch")
    channel=inherited_channel()
    spec=channel.describe_dual(tuple(neutral["translation"]),receiver_basis="z")
    if set(world.runtime.channel_names)!={x.name for x in world.interfaces}:
        raise ValueError("Channels/interfaces lost during continuation")
    return world,spec,neutral


def digest(world):
    rt=world.runtime
    return {"tick":rt.current_tick,"raw_sha256":hashlib.sha256(array("Q",rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",rt.clock_copy()).tobytes()).hexdigest()}


def resource_sensor(world,spec,bank_name):
    channel=inherited_channel();bank=spec["banks"][bank_name];tick=world.runtime.current_tick
    site=channel.moved(bank["cost_meeting"],bank["resource_direction"],tick-bank["emission_tick"]-4)
    actual=channel.observe(world,site)
    present=(actual["active"] and actual["semantic"]==1 and actual["s_reg"]==3 and actual["direction"]==list(bank["resource_direction"]))
    return {"modality":"EXTERNAL_FIXED_CURRENT_RESOURCE_WINDOW", "bank":bank_name,"tick":tick,
            "observation":actual,"present":bool(present),"class_sign":1 if present else -1,
            "scope":"Actual current native packet/window; absence is external transduction, not Native absence perception"}


def until(world,tick):
    if world.runtime.paused:raise ValueError("Paused Runtime")
    world.run_until(tick)
    if world.runtime.current_tick!=tick:raise RuntimeError("Actual tick did not reach declared boundary")


FORMS={"W1":"HAY","W2":"NO"} # External form identity ONLY; no form-to-class map.
