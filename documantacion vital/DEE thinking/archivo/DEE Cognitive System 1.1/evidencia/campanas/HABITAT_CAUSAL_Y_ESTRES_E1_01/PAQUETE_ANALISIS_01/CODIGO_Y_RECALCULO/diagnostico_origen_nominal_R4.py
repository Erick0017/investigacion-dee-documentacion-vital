"""Exact R4 replay/control from T4492, with a bounded passive T5200..5296 trace.

Not executed on import. Never advances MAIN or the protected parent. Control
consumes every original RNG draw but omits native noise submissions explicitly.
"""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import inspect
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
SYSTEM = ROOT / "sistema"
EV = ROOT / "evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01"
SOURCE = LAB / "habitat_R4_exact_metadata.py"
SOURCE_SHA = "41c8c21630d048eef0a56d9602cff172ff1660f4af0edeab371ca1d115104050"
PARENT = "estado/checkpoints/E1_ECO_MAIN.T4492.8eb9f41b7b59.deetsnap.gz"
CONTEXT_KEY = "DEE.Cognitive.System.1.1.habitat01.diagnostic_R4_resume_context.v1"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def json_exact(value):
    return json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))


def run(arm, life_id, name):
    if arm not in ("replay", "omit_noise"):
        raise ValueError("Only the frozen original replay and noise-omission control")
    if life_id in ("E1_SOCIAL_11", "E1_ECO_MAIN"):
        raise ValueError("A new diagnostic identity is mandatory")
    if digest(SOURCE) != SOURCE_SHA:
        raise ValueError("Frozen original R4 source changed; do not substitute another revision")
    sys.path.insert(0, str(SYSTEM))
    sys.path.insert(0, str(ROOT / "laboratorio/campanas/PAISAJE_CAUSAL_01"))
    from app.lives import Store
    from app.native_tools import physical, atomic_json, exact_receipt
    from app.process_control import protect_current, current_resources
    from instrumentos_pc01 import Trace, receipts
    from dee_thinking.persistence import encode_metadata
    spec = importlib.util.spec_from_file_location("_habitat_frozen_R4", SOURCE)
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    h.check_budget()
    protect_current()
    out = EV / name
    out.mkdir(parents=True, exist_ok=False)
    h.EV = out  # original R4 writes its grouped rows only into this new folder
    store = Store()
    source_path = SYSTEM / PARENT
    source_sha = digest(source_path)
    record = store.fork("E1_ECO_MAIN", life_id, kind="DIAGNOSTIC_COPY", checkpoint=PARENT)
    report = {"schema": "DCS1.1.HABITAT.nominal_R4.origin_diagnostic.v1",
              "arm": arm, "life_id": life_id, "parent": PARENT,
              "parent_sha256": source_sha, "source": SOURCE.name,
              "source_sha256": SOURCE_SHA, "wrapper_sha256": digest(__file__),
              "fixed_protocol": {"steps": 12, "seed": 142, "noise_rate": 1,
                                 "noise_amplitude": 5, "supply": "full", "feedback": "closed"},
              "trace_window": [5200, 5296], "omitted_inputs": [],
              "attribution": "Diagnostic descendant; no results or repaired state are imported into MAIN.",
              "status": "PREPARED"}
    atomic_json(out / "PREDECLARACION.json", report)
    original_emit = h.emit

    def controlled_emit(a, port, payload, tick, probe=False, origin="ENVIRONMENT_FIXED_CODEC"):
        if arm == "omit_noise" and origin == "EXOGENOUS_SEEDED_INPUT":
            omitted = {"port": port, "payload": int(payload), "tick": int(tick),
                       "probe": bool(probe), "origin": origin,
                       "id": -1 - len(report["omitted_inputs"]),
                       "status": "CONTROL_OMITTED_NOT_A_NATIVE_RECEIPT"}
            report["omitted_inputs"].append(omitted)
            return omitted
        return original_emit(a, port, payload, tick, probe, origin)

    h.emit = controlled_emit

    def callback(a):
        if int(a.tick) != 4492:
            raise ValueError("Wrong diagnostic starting tick")
        initial = physical(a.world, occupation=True)
        tracer = Trace(a, out / "TRAZA_T5200_T5296.jsonl.gz", start=5200, end=5296).install()
        pre_saved = False
        trace_summary = None

        def supervised_owner_run(target):
            nonlocal pre_saved
            # The caller is the unchanged R4 habitat_block frame; capture its
            # real environmental state, RNG and pending protocol stage. Do not
            # derive them from a target or from the later observed answer.
            caller = inspect.currentframe().f_back
            if not pre_saved and int(a.tick) < 5200 <= target:
                context = {"schema": "DCS1.1.habitat.R4.mid_step_context.v1",
                           "stage": "INPUTS_ALREADY_SCHEDULED_BEFORE_NATIVE_ADVANCE",
                           "arm": arm, "tick": 5200, "next_owner_target": int(target),
                           "R4_source_sha256": SOURCE_SHA,
                           "original_common_seed_argument": 142,
                           "local_index": int(caller.f_locals["local"]),
                           "state_before_current_output": json_exact(caller.f_locals["state"]),
                           "rng_after_current_noise_before_current_exogenous": json_exact(caller.f_locals["rng"].getstate()),
                           "current_object": int(caller.f_locals["q"]),
                           "object_tick": int(caller.f_locals["t"]),
                           "read_tick": int(caller.f_locals["read"]),
                           "noise_requests_current_step": json_exact(caller.f_locals["noise"]),
                           "reader_requests_current_step": json_exact(caller.f_locals["requested"]),
                           "current_step_pre": json_exact(caller.f_locals["pre"]),
                           "completed_rows": json_exact(caller.f_locals["rows"]),
                           "omitted_inputs": deepcopy(report["omitted_inputs"]),
                           "warning": "Native world is complete. Resuming mid-step requires this protocol context; calling unchanged R4 habitat_block from its top would duplicate pending inputs."}
                tracer.run(5200)
                before = physical(a.world)
                a.world.runtime.set_snapshot_metadata(CONTEXT_KEY, encode_metadata(context))
                if physical(a.world) != before:
                    raise AssertionError("Documentary diagnostic context altered physical fields")
                pre_path = out / "PRE_T5200.deetsnap.gz"
                a.save(pre_path)
                report["pre_T5200"] = {"path": str(pre_path.relative_to(ROOT)),
                                        "sha256": digest(pre_path), "physical": before,
                                        "protocol_context": context}
                atomic_json(out / "PRE_T5200_CONTEXTO.json", report["pre_T5200"])
                pre_saved = True
            return tracer.run(target)

        a.run_until = supervised_owner_run
        try:
            result = h.habitat_block(a, name=name, steps=12, seed=142,
                                     noise_rate=1, noise_amplitude=5,
                                     supply="full", feedback="closed")
        finally:
            trace_summary = tracer.close()
            report["trace"] = trace_summary
        if not pre_saved:
            raise AssertionError("The fixed pre-failure boundary was not reached")
        post_path = out / "POST_T5296.deetsnap.gz"
        a.save(post_path)
        report["post_T5296"] = {"path": str(post_path.relative_to(ROOT)),
                                 "sha256": digest(post_path),
                                 "physical": physical(a.world, occupation=True)}
        report["native_receipts"] = receipts(a.world.runtime)
        report["initial"] = initial
        report["result"] = result
        # Future environment is allowed to differ after different native actions.
        # Both arms nevertheless consume identical R4 exogenous RNG draws.
        if arm == "replay":
            original = json.loads((EV / "MAIN_NOISE_NOMINAL_03.json").read_text(encoding="utf8"))
            old = original["result"]
            def row_without_name(row):
                row = deepcopy(row)
                row.pop("block", None)
                return row
            report["reproduction"] = {
                "physical_final_equal_original": result["final"] == old["final"],
                "all_rows_equal_except_explicit_block_name": [row_without_name(x) for x in result["rows"]] == [row_without_name(x) for x in old["rows"]],
                "native_receipts_equal_original": report["native_receipts"] == original["receipts"],
                "original_primary_sha256": digest(EV / "MAIN_NOISE_NOMINAL_03.json"),
                "not_compared_as_same_file": "Diagnostic life identifiers and added instrument context differ by declaration."}
        report["status"] = "MEASURED_FIXED_HORIZON"
        atomic_json(out / "MEDICIONES.json", report)
        return {"diagnostic_report": str((out / "MEDICIONES.json").relative_to(ROOT)),
                "arm": arm, "trace": trace_summary, "native_final": result["final"],
                "reproduction": report.get("reproduction"),
                "omitted_inputs_count": len(report["omitted_inputs"])}

    try:
        operation = store.mutate(life_id, "HABITAT01_R4_ORIGIN_DIAGNOSTIC", callback,
                                 {"arm": arm, "source_revision_sha256": SOURCE_SHA,
                                  "wrapper_sha256": digest(__file__), "parent": PARENT,
                                  "trace_window": [5200, 5296], "no_MAIN_mutation": True})
        report["operative_commit"] = operation
        report["resources"] = current_resources()
        atomic_json(out / "MEDICIONES.json", report)
        print(json.dumps(operation, ensure_ascii=False, indent=2))
    except BaseException as error:
        report["status"] = "DIAGNOSTIC_ERROR_PRESERVED_BY_STORE"
        report["error"] = {"type": type(error).__name__, "detail": str(error)}
        atomic_json(out / "MEDICIONES.json", report)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arm", choices=("replay", "omit_noise"), required=True)
    p.add_argument("--life", required=True)
    p.add_argument("--name", required=True)
    args = p.parse_args()
    run(args.arm, args.life, args.name)
