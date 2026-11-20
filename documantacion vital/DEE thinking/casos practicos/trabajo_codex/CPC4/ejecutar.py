"""Single CPC4 entry point: finite campaign, one case, verification, reproduction."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.common import append, put, sha


def load_config(path=None):
    return json.loads(Path(path or ROOT/"EXPERIMENT_CONFIG.json").read_text(encoding="utf-8"))


def case_worker(identifier, output, config_path=None):
    import dee_thinking as d
    from src import channel, channel_dual
    from src.common import digest, identity
    config = load_config(config_path)
    case = next(x for x in config["cases"] if x["id"] == identifier)
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    if (output/"COMPLETED.json").exists():
        raise FileExistsError("The case is already complete; resume verifies and skips it")
    started = time.monotonic()
    journal = []
    put(output/"CASE_CONFIG.json", case)
    put(output/"RUNNING.json", {"id": identifier, "utc": datetime.now(timezone.utc).isoformat(), "config_sha256": sha(config_path or ROOT/"EXPERIMENT_CONFIG.json")})
    identity(ROOT/"runtime"/"dee_thinking-4.0.0-cp313-cp313-win_amd64.whl")
    if case["kind"] == "native":
        world, spec = channel.prepare_dual(d, tuple(case.get("translation", (0,0,0))), receiver_basis=case.get("receiver_basis", "z"))
        journal.append({"operation":"create", "tick":0, "count":1, "recipe":"CPC4_DUAL_ORTHOGONAL_V2"})
        world, physical = channel_dual.run_native(world, spec, case, output/"NATIVO", snapshot_policy=case.get("snapshot_policy", "none"))
        result = {"case":case, "physical":physical}
        if case.get("language"):
            from src.phase_language import forward
            same_world = world
            before = digest(world)
            world, lexical = forward(world, spec, case["language"], output/"LENGUAJE")
            assert world is same_world
            assert lexical["initial"] == before == physical["final"]
            journal.append({"operation":"native_to_language", "native_end_tick":169,
                            "language_end_tick":world.runtime.current_tick,
                            "same_OrganizationalWorld_object":True,
                            "initial_RAW_clock_tick_preserved":True,
                            "creates_after_T0":0})
            result["language"] = lexical
    elif case["kind"] == "language_control":
        from src.phase_language import forward
        parent = ROOT/case["parent"]
        world = d.OrganizationalWorld.load_snapshot(str(parent))
        spec = channel.describe_dual(tuple(case.get("translation",(0,0,0))))
        journal.append({"operation":"restore_full_diagnostic_cohort", "tick":world.runtime.current_tick,
                        "parent":case["parent"], "parent_sha256":sha(parent), "merged_into_MAIN":False})
        world, lexical = forward(world, spec, case["language"], output/"LENGUAJE")
        result = {"case":case, "language":lexical}
    else:
        raise ValueError("Unknown case type")
    result.update(operation_journal=journal, elapsed_seconds=time.monotonic()-started,
                  source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [Path(__file__),ROOT/"src"/"common.py",ROOT/"src"/"channel.py",ROOT/"src"/"channel_dual.py",ROOT/"src"/"phase_language.py"]})
    put(output/"MEASUREMENTS.json",result)
    put(output/"COMPLETED.json",{"id":identifier,"measurement_sha256":sha(output/"MEASUREMENTS.json"),"elapsed_seconds":result["elapsed_seconds"],"final_tick":world.runtime.current_tick})
    print(json.dumps({"id":identifier,"status":"MEASURED","tick":world.runtime.current_tick,"elapsed":result["elapsed_seconds"]}))
    return result


def completed(path):
    marker=Path(path)/"COMPLETED.json"
    if not marker.exists(): return False
    x=json.loads(marker.read_text(encoding="utf-8"))
    assert sha(Path(path)/"MEASUREMENTS.json")==x["measurement_sha256"]
    return True


def campaign(config_path=None):
    import supervise
    config=load_config(config_path)
    rows=[]
    # Language cohorts depend on the one saved MAIN boundary, never merge back.
    for stage in ("native","language_control"):
        cases=[x for x in config["cases"] if x["kind"]==stage]
        def launch(case):
            target=ROOT/"resultados"/"confirmacion"/case["id"]
            if completed(target): return {"id":case["id"],"status":"VERIFIED_PREVIOUSLY_COMPLETED"}
            argv=[sys.executable,"-I","-B",str(Path(__file__)),"--worker",case["id"],"--output",str(target)]
            if config_path: argv += ["--config",str(Path(config_path).resolve())]
            run=supervise.run(ROOT,"confirm_"+case["id"]+"_"+datetime.now().strftime("%H%M%S"),argv,config["timeout_per_case_seconds"],str(ROOT))
            row={"id":case["id"],"status":"MEASURED" if run["exit_code"]==0 else "TECHNICAL_ERROR","job":run}
            append(ROOT/"resultados"/"CASE_LEDGER.jsonl",row)
            return row
        with ThreadPoolExecutor(max_workers=2) as pool:
            for future in as_completed([pool.submit(launch,c) for c in cases]):
                row=future.result();rows.append(row);print(json.dumps(row),flush=True)
    put(ROOT/"resultados"/"EXECUTION_INDEX.json",{"cases":rows,"config_sha256":sha(config_path or ROOT/"EXPERIMENT_CONFIG.json")})
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",nargs="?",choices=("run","resume","identity","verify","package","reproduce","demonstrate","reproduce-access2"),default="run")
    parser.add_argument("--worker")
    parser.add_argument("--case")
    parser.add_argument("--output",type=Path)
    parser.add_argument("--config",type=Path)
    parser.add_argument("--events",type=Path)
    args=parser.parse_args()
    if args.worker:
        case_worker(args.worker,args.output,args.config)
    elif args.command in ("run","resume"):
        campaign(args.config)
    elif args.command=="identity":
        from src.common import identity
        print(json.dumps(identity(ROOT/"runtime"/"dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"),indent=2))
    elif args.command=="reproduce":
        if not args.case or not args.output: parser.error("reproduce requires --case and --output")
        # A later reproduction is labelled separately; it never changes BUDGET.
        subprocess.run([sys.executable,"-I","-B",str(Path(__file__)),"--worker",args.case,"--output",str(args.output.resolve())],check=True,timeout=240,cwd=ROOT)
    elif args.command=="demonstrate":
        if not args.output:parser.error("demonstrate requires --output")
        argv=[sys.executable,"-I","-B",str(ROOT/"demostracion.py"),"--salida",str(args.output.resolve())]
        if args.events:argv += ["--eventos",str(args.events.resolve())]
        subprocess.run(argv,check=True,timeout=600,cwd=ROOT)
    elif args.command=="reproduce-access2":
        if not args.case or not args.output:parser.error("reproduce-access2 requires --case and --output")
        config_file=ROOT/"resultados"/"inverse_access2"/"INVERSE_ACCESS2_CONFIG.json"
        config=json.loads(config_file.read_text(encoding="utf-8"))
        if args.case not in [x["id"] for x in config["cases"]]:parser.error("Unknown frozen access2 case")
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/config_file.name).write_bytes(config_file.read_bytes())
        subprocess.run([sys.executable,"-I","-B",str(ROOT/"src"/"inverse_access2.py"),"--output",str(args.output.resolve()),"--child",args.case],check=True,timeout=240,cwd=ROOT)
    else:
        from src.finalize import main as finalize
        finalize(args.command)


if __name__=="__main__": main()
