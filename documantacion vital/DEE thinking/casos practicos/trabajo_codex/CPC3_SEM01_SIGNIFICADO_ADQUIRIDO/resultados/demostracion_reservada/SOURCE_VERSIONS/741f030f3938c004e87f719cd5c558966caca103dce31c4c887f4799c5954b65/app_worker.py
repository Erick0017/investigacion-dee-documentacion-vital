"""Finite SEM01 application worker: one restored MAIN, no response lookup.

Query mode accepts a snapshot and S1/S2 only. Teaching belongs to a different
operation/process. The operational metadata stores phase, interface aliases and
neutral physical recipe parameters, never a signal->outcome correspondence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROTOCOL_KEY = "sem01.neutral_protocol"
APP_KEY = "sem01.application.neutral.v1"
NATIVE_SHA = "20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066"
ALLOWED_PHASES = {"CREATED", "READY", "EMITTED", "COMPLETE"}


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def access_audit(snapshot, output_snapshot=None):
    """Reject Python-level reads of generator/results data in query process.

    C++ opens the single explicitly supplied snapshot internally; Python's
    audit hook does not intercept native fopen. This is not an OS sandbox.
    The query call graph never receives a generator directory, map or target.
    """
    allowed_snapshot = Path(snapshot).resolve()
    allowed_output = Path(output_snapshot).resolve() if output_snapshot else None
    reads = []
    rejected = []
    source = ROOT / "src"

    def hook(event, args):
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else 0
        writing = isinstance(mode, str) and any(x in mode for x in ("w", "a", "+", "x"))
        writing = writing or isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR))
        if writing:
            return
        path = Path(os.fsdecode(args[0])).resolve()
        denied = False
        if path.is_relative_to(ROOT):
            permitted_source = path.is_relative_to(source) and path.name in {
                "app_worker.py", "participant.py", "memory.py", "habitat.py", "__init__.py"
            }
            permitted_source = permitted_source or path.parent == source / "__pycache__" and path.name.split(".")[0] in {"participant", "memory", "habitat", "__init__"}
            denied = not (path == allowed_snapshot or path == allowed_output or permitted_source or path.is_relative_to(ROOT / "runtime"))
        if denied:
            rejected.append(str(path))
            raise PermissionError("Query process cannot read generator/history/result files")
        reads.append(str(path))

    sys.addaudithook(hook)
    return reads, rejected


def native():
    import dee_thinking as d
    if d.__version__ != "4.0.0" or d.kernel_identity()["kernel_version"] != 27:
        raise RuntimeError("The immutable DEE thinking4.0.0/v27 instrument is required")
    if sha(d._native.__file__) != NATIVE_SHA:
        raise RuntimeError("The installed native artifact is not the qualified instrument")
    return d


def neutral(world):
    value = world.runtime.snapshot_metadata(PROTOCOL_KEY)
    if not isinstance(value, str):
        raise ValueError("Snapshot lacks SEM01 neutral protocol")
    value = json.loads(value)
    required = {"version", "translation", "signal_order", "signal_payload", "training_slots", "query_slots"}
    if set(value) != required or value["version"] != 1:
        raise ValueError("Unsupported/extra neutral protocol fields")
    if len(value["translation"]) != 3 or any(type(x) is not int for x in value["translation"]):
        raise ValueError("Invalid translation")
    if sorted(value["signal_order"]) != ["S1", "S2"] or len(value["signal_order"]) != 2:
        raise ValueError("Invalid physical signal order")
    if value["signal_payload"] not in (5, 7) or value["training_slots"] != [17, 45] or value["query_slots"] != [84, 112]:
        raise ValueError("Snapshot protocol is outside the finite published application")
    return value


def application(world):
    value = world.runtime.snapshot_metadata(APP_KEY)
    if not isinstance(value, str):
        raise ValueError("Snapshot lacks application continuation metadata")
    value = json.loads(value)
    if set(value) != {"version", "phase", "next_index", "aliases", "last_signal", "emission_tick"}:
        raise ValueError("Unexpected application metadata: no associations/answers are permitted")
    if value["version"] != 1 or value["phase"] not in ALLOWED_PHASES:
        raise ValueError("Unsupported application version/phase")
    index = value["next_index"]
    if type(index) is not int or index not in (0, 1, 2):
        raise ValueError("Invalid operational cursor")
    aliases = value["aliases"]
    if not isinstance(aliases, dict) or set(aliases.values()) != {"S1", "S2"} or len(aliases) != 2:
        raise ValueError("Two interface aliases are required")
    if any(not isinstance(k, str) or not k or len(k) > 40 or any(c.isspace() for c in k) for k in aliases):
        raise ValueError("Invalid alias")
    p = neutral(world)
    expected_tick = {("CREATED", 0): 0, ("READY", 0): 83, ("READY", 1): 101,
                     ("EMITTED", 0): 87, ("EMITTED", 1): 115, ("COMPLETE", 2): 129}.get((value["phase"], index))
    if world.runtime.current_tick != expected_tick:
        raise ValueError("The snapshot physical tick and application phase disagree")
    if value["phase"] == "EMITTED":
        if value["last_signal"] != p["signal_order"][index] or value["emission_tick"] != expected_tick:
            raise ValueError("Invalid pending native emission window")
    elif value["last_signal"] is not None or value["emission_tick"] is not None:
        raise ValueError("Unexpected remembered prediction; readouts are never cached in application state")
    if world.runtime.dimension != 67 or world.recipe.id != "research.v1":
        raise ValueError("The snapshot is not the finite N67 research preparation")
    validate_physical_interfaces(world, p)
    return value


def validate_physical_interfaces(world, protocol):
    """Metadata cannot redirect the fixed physical signal or observation route."""
    from src import memory, habitat
    d = __import__("dee_thinking")
    translation = protocol["translation"]
    expected = {}
    for item in memory.memory_interfaces(d, translation):
        channel = item.channel
        expected[item.name] = ([channel.injection_site.x, channel.injection_site.y, channel.injection_site.z],
                               [channel.direction.dx, channel.direction.dy, channel.direction.dz])
    banks = [("train.S1", memory.plus((10, 10, 58), (0, 0, 0), translation=translation)),
             ("train.S2", memory.plus((50, 10, 58), (0, 0, 0), translation=translation)),
             ("use.S1", memory.hub("S1", translation)), ("use.S2", memory.hub("S2", translation))]
    for prefix, emitter in banks:
        bank = habitat.bank_spec(emitter, prefix, "v2_delayed_supply")
        for suffix, key, direction in (("resource", "resource_source", [1, 0, 0]),
                                       ("supply", "supply_source", [0, 1, 0]),
                                       ("U", "event_U_source", list(habitat.U)),
                                       ("V", "event_V_source", list(habitat.V)),
                                       ("reference_action", "emitter", list(habitat.ACTION))):
            expected[prefix + "." + suffix] = (list(bank[key]), direction)
    actual = {item.name: item.channel for item in world.interfaces}
    if len(actual) != len(world.interfaces) or set(actual) != set(expected):
        raise ValueError("Snapshot physical interfaces do not match the declared preparation")
    for name, (site, direction) in expected.items():
        channel = actual[name]
        if (channel.name != name or [channel.injection_site.x, channel.injection_site.y, channel.injection_site.z] != site
                or [channel.direction.dx, channel.direction.dy, channel.direction.dz] != direction
                or channel.state != 1 or channel.semantic != 1 or not channel.allow_experience or not channel.allow_probe):
            raise ValueError("Physical channel and neutral continuation metadata disagree")
    recipe = world.recipe
    if recipe.dimension != 67 or recipe.t0_tick != 0 or recipe.placements:
        raise ValueError("Snapshot initial recipe is not the declared empty physical organization")


def set_application(world, value):
    world.runtime.set_snapshot_metadata(APP_KEY, json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def current_panel(world, protocol, app):
    from src import memory
    # Always re-read the current physical state; this never reconstructs an old
    # answer from a filename, history log or prior response object.
    return {"tick": world.runtime.current_tick, "phase": app["phase"],
            "next_signal": protocol["signal_order"][app["next_index"]] if app["next_index"] < 2 else None,
            "aliases": app["aliases"], "physical_digest": memory.digest(world),
            "current_hubs": {s: memory.read_emission(world, s, protocol["translation"]) for s in ("S1", "S2")},
            "scope": "INSTRUMENTO: passive current hubs; tested prediction only at the finite emission boundary"}


def save(world, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("Refusing to overwrite an earlier MAIN snapshot")
    world.save_snapshot(str(path))
    return {"path": str(path.resolve()), "sha256": sha(path)}


def execute(args):
    audited = denied = []
    if args.operation == "query":
        if args.snapshot is None or args.signal not in ("S1", "S2"):
            raise ValueError("Query accepts exactly an identified snapshot and S1/S2")
        if args.pairing or args.event or args.translation is not None or args.order is not None or args.payload is not None:
            raise ValueError("Query cannot receive a lesson, event, target or preparation override")
        audited, denied = access_audit(args.snapshot, args.output_snapshot)
    d = native()
    if args.operation == "create":
        if args.snapshot is not None:
            raise ValueError("Create is an explicit NEW individual, not restoration")
        from src.experiment import prepare
        world, unused_banks = prepare(d, tuple(args.translation or (0, 0, 0)), tuple(args.order or ("S1", "S2")), args.payload or 5)
        app = {"version": 1, "phase": "CREATED", "next_index": 0,
               "aliases": {"zuvi": "S1", "pako": "S2"}, "last_signal": None, "emission_tick": None}
        set_application(world, app)
        result = {"attribution": "INTERFAZ: explicit new empty organization; no lesson selected at creation"}
    else:
        if args.snapshot is None:
            raise ValueError("A continuation snapshot is required")
        world = d.OrganizationalWorld.load_snapshot(str(args.snapshot))
        app = application(world)
        result = {"loaded_snapshot_sha256": sha(args.snapshot), "restoration": "same complete operative state, no create or history replay"}
    protocol = neutral(world)
    before = current_panel(world, protocol, app)
    if args.operation == "train":
        if app["phase"] != "CREATED" or world.runtime.current_tick != 0:
            raise ValueError("This finite demonstrator teaches once from its own T0")
        pairing = json.loads(args.pairing or "null")
        if not isinstance(pairing, dict) or set(pairing) != {"S1", "S2"} or any(x not in ("U", "V") for x in pairing.values()):
            raise ValueError("The EXTERNAL generator must declare both physical U/V experiences")
        from src.experiment import descriptors, generate_training
        training = generate_training(world, descriptors(protocol["translation"]), pairing, "paired", args.evidence,
                                     protocol["translation"], protocol["signal_order"], protocol["signal_payload"])
        # The local variable belongs to this teaching process only. Nothing is
        # serialized into the participant except the physical evolved world.
        pairing.clear()
        app.update(phase="READY", next_index=0)
        set_application(world, app)
        result.update(attribution="EXPERIENCE_PROTOCOL: fixed current-physical-outcome sensor broadcasts a teacher; no A/B edit", training=training)
    elif args.operation == "query":
        if app["phase"] != "READY":
            raise ValueError("Query requires the next finite READY phase; reveal pending event first")
        index = app["next_index"]
        if args.signal != protocol["signal_order"][index]:
            raise ValueError("This finite preparation exposes a declared order; no sensor relocation or phase reset")
        from src.participant import signal_only
        query = signal_only(world, args.signal, protocol["query_slots"][index], protocol["translation"], protocol["signal_payload"])
        applied = query["receipt"].get("status", "").split(".")[-1].lower() == "applied"
        app.update(phase="EMITTED", last_signal=args.signal, emission_tick=query["emission_tick"])
        set_application(world, app)
        result.update(attribution="ENTE: actual native emission before future event; fixed passive direction decoder" if applied else "INSTRUMENTO: requested signal was not applied; current RAW is not a newly admitted prediction",
                      query=query, query_admitted=applied)
    elif args.operation == "reveal":
        if app["phase"] != "EMITTED" or args.event not in ("U", "V"):
            raise ValueError("Reveal requires a current emission and an explicit subsequent U/V world event")
        from src import habitat, memory
        emit = app["emission_tick"]
        signal = app["last_signal"]
        bank = habitat.bank_spec(memory.hub(signal, protocol["translation"]), "use." + signal, "v2_delayed_supply")
        receipts = habitat.submit_resources(world, bank, emit)
        captures = {}
        trace = []
        for tick in range(emit, emit + 15):
            if tick == emit + 1:
                receipts.append(habitat.submit_event(world, bank, args.event, emit))
            trace.append(habitat.read_bank(world, bank, emit, captures))
            if tick < emit + 14:
                world.advance()
        evaluation = habitat.evaluate_captures(captures)
        app.update(next_index=app["next_index"] + 1, last_signal=None, emission_tick=None)
        app["phase"] = "COMPLETE" if app["next_index"] == 2 else "READY"
        set_application(world, app)
        result.update(attribution="MUNDO: declared physical event after emission; utility is EXTERNAL evaluation only",
                      actual_event=args.event, trace=trace, evaluation=evaluation,
                      receipts=[habitat.receipt_dict(world.runtime.receipt(r.id)) for r in receipts])
    elif args.operation == "alias":
        if args.signal not in ("S1", "S2") or not args.alias or len(args.alias) > 40 or any(c.isspace() for c in args.alias):
            raise ValueError("Alias must be a single short token for S1 or S2")
        other = {key: value for key, value in app["aliases"].items() if value != args.signal}
        if args.alias.lower() in other:
            raise ValueError("Alias already refers to the other physical signal")
        other[args.alias.lower()] = args.signal
        app["aliases"] = other
        set_application(world, app)
        result["attribution"] = "INTERFAZ: text->fixed signal name only; not an acquired functional correspondence"
    elif args.operation not in ("create", "train", "observe", "validate", "query", "reveal"):
        raise ValueError("Unsupported application operation")
    # Validate the continuation BEFORE publishing a new snapshot.
    application(world)
    result.update(operation=args.operation, before=before, after=current_panel(world, protocol, app),
                  instrument={"version": d.__version__, "kernel": 27, "module": d.__file__, "native_sha256": NATIVE_SHA},
                  protocol=protocol, teaching_map_in_application_metadata=False)
    if args.output_snapshot:
        result["snapshot"] = save(world, args.output_snapshot)
    if args.operation == "query":
        result["query_isolation"] = {"contract": "snapshot + fixed physical S1/S2; no lesson map or future event argument",
                                     "python_read_paths": sorted(set(audited)), "denied_reads": denied,
                                     "audit_scope": "Python open events; native snapshot load is the single explicit file, not OS sandboxing",
                                     "imported_local_modules": sorted(name for name in sys.modules if name.startswith("src."))}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("create", "train", "query", "reveal", "observe", "validate", "alias"))
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--output-snapshot", type=Path)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--pairing")
    parser.add_argument("--signal", choices=("S1", "S2"))
    parser.add_argument("--event", choices=("U", "V"))
    parser.add_argument("--alias")
    parser.add_argument("--translation", type=int, nargs=3)
    parser.add_argument("--order", choices=("S1", "S2"), nargs=2)
    parser.add_argument("--payload", type=int, choices=(5, 7))
    args = parser.parse_args()
    if args.operation == "train" and args.evidence is None:
        parser.error("Teaching requires an EXTERNAL evidence directory")
    try:
        result = execute(args)
        result["completed"] = True
        put(args.result, result)
        print(json.dumps({"completed": True, "operation": args.operation, "tick": result["after"]["tick"]}))
    except Exception as exc:
        put(args.result, {"completed": False, "operation": args.operation, "error_type": type(exc).__name__, "error": str(exc)})
        raise


if __name__ == "__main__":
    main()
