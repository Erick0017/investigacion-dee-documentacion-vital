"""Portable bounded validation of the PUBLIC demo, independent of old paths.

Run from an extracted CPC4 with its own WHL4 installation. The only optional
fixture is used AFTER evolution by the auditor to compare physical digests.
No campaign-deadline reset: this is a separate finite reproduction command,
not an extension of the scientific campaign or its case count.
"""
import argparse
import ast
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha


def bounded(name, argv, output, cwd):
    from supervise import owned_job
    started = time.monotonic()
    with (output/(name+".stdout.log")).open("x", encoding="utf-8") as out, (output/(name+".stderr.log")).open("x", encoding="utf-8") as err:
        process = subprocess.Popen(argv, cwd=str(cwd), stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
        job, scope = owned_job(process)
        if not job:
            process.kill(); process.wait(timeout=10)
            raise RuntimeError("Owned process job unavailable")
        try:
            try:
                code = process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                job[0].TerminateJobObject(job[1], 124); code = process.wait(timeout=10)
        finally:
            job[0].CloseHandle(job[1])
    row = {"argv": argv, "cwd": str(cwd), "exit_code": code, "elapsed_seconds": time.monotonic()-started,
           "owned_windows_job": scope, "process_closed": process.poll() is not None}
    put(output/(name+".COMMAND.json"), row)
    if code != 0: raise RuntimeError("Preserve failed public reproduction: " + name)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True, help="New external output directory")
    parser.add_argument("--expected", type=Path, help="Optional packaged MAIN_MINUS MEASUREMENTS.json, used ONLY post-hoc")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists(): raise FileExistsError(output)
    output.mkdir(parents=True)
    work = output/"cwd_distinto"; work.mkdir()
    sources = ("demostracion.py", "src/app_worker.py", "src/language.py", "src/phase_language.py", "src/channel.py", "src/channel_dual.py", "src/common.py", "src/demo_validation.py",
               "configuraciones/demo_principal.txt", "configuraciones/demo_continuacion.txt")
    config = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "extracted_root": str(ROOT),
              "python": sys.executable, "source_sha256": {name: sha(ROOT/name) for name in sources},
              "scope": "Public technical reproduction, one MAIN0→239, explicit save/load to another process, then a NEW question239→267. Not new independent scientific samples.",
              "output_template_substitution": "File paths only; no history, teacher class, answer or decoder changes",
              "no_scientific_budget_reset": True, "timeout_each_process_seconds": 180}
    if args.expected:
        config["auditor_fixture"] = {"path": str(args.expected.resolve()), "sha256": sha(args.expected)}
    put(output/"CONFIG.json", config)
    for name in ("principal", "continuacion"):
        source = (ROOT/"configuraciones"/("demo_"+name+".txt")).read_text(encoding="utf-8")
        (output/(name+".txt")).write_text(source.replace("@SALIDA@", output.as_posix()), encoding="utf-8")
    entry = ROOT/"demostracion.py"
    first = bounded("CREATE_TO239", [sys.executable, "-I", "-B", str(entry), "--eventos", str(output/"principal.txt"), "--salida", str(output/"PRIMER_PROCESO")], output, work)
    second = bounded("LOAD239_NEW_QUESTION", [sys.executable, "-I", "-B", str(entry), "--eventos", str(output/"continuacion.txt"), "--cargar", str(output/"CONTINUAR239.deetsnap"), "--salida", str(output/"OTRO_PROCESO")], output, work)
    rows = []
    for folder in ("PRIMER_PROCESO", "OTRO_PROCESO"):
        rows.extend(json.loads(line) for line in (output/folder/"TRANSCRIPCION.jsonl").read_text(encoding="utf-8").splitlines())
    query_rows = [r for r in rows if r.get("response", {}).get("result", {}).get("physical_output")]
    questions = [r["response"]["result"] for r in query_rows]
    checks = {"two_actual_queries": len(questions) == 2,
              "queries_applied": all(q["receipt"]["status"] == "applied" for q in questions),
              "current_outputs_available": all(q["available"] for q in questions),
              "same_decoder": len({q["decoder"] for q in questions}) == 1,
              "actual_query_read_audit_no_open": all(not q["python_read_audit"]["observed_reads"] for q in questions),
              "explicit_load_before_second_question": any(r.get("command", "").startswith("cargar ") and r.get("response",{}).get("result",{}).get("status") == "MISMO_ESTADO_OPERATIVO_RESTAURADO" for r in rows),
              "all_processes_closed": first["process_closed"] and second["process_closed"],
              "source_unchanged": all(sha(ROOT/name) == expected for name,expected in config["source_sha256"].items())}
    # Static operational-code check complements the ACTUAL run and Native
    # diagnostic receipts; it is not mislabelled a physical causal test.
    tree = ast.parse((ROOT/"src/app_worker.py").read_text(encoding="utf-8"))
    checks["worker_has_no_fork_call_in_source"] = not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ("fork", "diagnostic_fork", "assisted_reconstruction") for n in ast.walk(tree))
    import dee_thinking as d
    from src.common import digest
    final = d.OrganizationalWorld.load_snapshot(str(output/"MAIN_FINAL267.deetsnap"))
    checks["snapshot_tick267"] = final.runtime.current_tick == 267
    checks["no_native_diagnostic_edits_on_main"] = len(final.diagnostic_edits) == 0
    expected_match = None
    if args.expected:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))["language"]["final"]
        expected_match = digest(final) == expected
        checks["final_RAW_clocks_equal_packaged_scientific_fixture"] = expected_match
    value = {"verified": all(checks.values()), "checks": checks, "commands": [first,second],
             "questions": query_rows, "final_physical": digest(final), "final_snapshot_sha256": sha(output/"MAIN_FINAL267.deetsnap"),
             "auditor_fixture_match": expected_match, "config_sha256": sha(output/"CONFIG.json"),
             "source_root_is_this_extraction": str(ROOT), "new_scientific_samples": 0}
    put(output/"DEMONSTRATION_SUMMARY.json", value)
    print(json.dumps({"verified": value["verified"], "checks": len(checks), "output": str(output)}))
    assert value["verified"]


if __name__ == "__main__": main()
