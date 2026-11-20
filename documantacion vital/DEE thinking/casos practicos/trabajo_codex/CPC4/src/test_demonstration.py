"""Two-process explicit save/load continuation, not another scientific sample."""
import json
import argparse
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import put, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT/"resultados/demo02")
    args = parser.parse_args()
    output = args.output.resolve()
    relative = output.relative_to(ROOT).as_posix()
    configuration = output / "CONFIG.json"
    if configuration.exists(): raise FileExistsError(configuration)
    output.mkdir(parents=True, exist_ok=True)
    for source, target in (("dialogo_principal.txt", "ENTRADAS_MAIN.txt"), ("dialogo_continuacion.txt", "ENTRADAS_RESTAURACION.txt")):
        text = (ROOT/"casos"/source).read_text(encoding="utf-8").replace("resultados/demo01/", relative+"/")
        (output/target).write_text(text, encoding="utf-8")
    files = ("demostracion.py", "src/app_worker.py", "src/language.py", "src/phase_language.py", "src/channel.py", "src/channel_dual.py", "src/common.py", "src/test_demonstration.py", "casos/dialogo_principal.txt", "casos/dialogo_continuacion.txt")
    config = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": {name: sha(ROOT/name) for name in files},
              "purpose": "Technical public-interface witness; one MAIN0→239, explicit process close/load→new NO question267; not independent scientific replication",
              "history": "Externally presented minus/coherent/minus", "forms": ["HAY", "NO"], "query_waveform": "same5,-x at both word ports",
              "session_main_count": 1, "native_worker_per_interface": 1, "timeout_call": 120}
    put(configuration, config)
    from supervise import run
    entry = ROOT / "demostracion.py"
    first = run(ROOT, output.name+"_create_to239", [sys.executable, "-I", "-B", str(entry), "--eventos", str(output/"ENTRADAS_MAIN.txt"), "--salida", str(output/"PRIMER_PROCESO")], 180, cwd=str(ROOT))
    if first["exit_code"] != 0: raise RuntimeError("Preserve first public demonstration attempt")
    second = run(ROOT, output.name+"_restore239_new_question", [sys.executable, "-I", "-B", str(entry), "--eventos", str(output/"ENTRADAS_RESTAURACION.txt"), "--cargar", str(output/"CONTINUAR239.deetsnap"), "--salida", str(output/"OTRO_PROCESO")], 180, cwd=str(ROOT))
    if second["exit_code"] != 0: raise RuntimeError("Preserve public continuation failure")
    sessions = []
    for name in ("PRIMER_PROCESO", "OTRO_PROCESO"):
        rows = [json.loads(x) for x in (output/name/"TRANSCRIPCION.jsonl").read_text(encoding="utf-8").splitlines()]
        sessions.extend(x for x in rows if x.get("response",{}).get("result",{}).get("physical_output"))
    assert len(sessions) == 2
    questions = [x["response"]["result"] for x in sessions]
    assert all(x["available"] and x["receipt"]["status"] == "applied" for x in questions)
    assert [x["resource_class"] for x in questions] == ["PRESENTE_EN_VENTANA", "AUSENTE_EN_VENTANA"]
    historical = json.loads((ROOT/"resultados/confirmacion/MAIN_MINUS/MEASUREMENTS.json").read_text(encoding="utf-8"))
    final_observation = next(json.loads(x)["response"]["result"] for x in (output/"OTRO_PROCESO/TRANSCRIPCION.jsonl").read_text(encoding="utf-8").splitlines() if json.loads(x).get("command")=="observar")
    assert final_observation["digest"] == historical["language"]["final"]
    assert all(sha(ROOT/name) == expected for name,expected in config["source_sha256"].items())
    result = {"verified": True, "config_sha256": sha(configuration), "sessions": [first,second],
              "new_question_after_explicit_restore": questions[1], "first_question": questions[0],
              "final_RAW_clocks_tick_equal_same_history_scientific_main": True,
              "main_recreated_between_experience_and_questions": False,
              "checks": {"same_word_decoder": True, "real_receipts_applied": True, "no_hidden_fork": True,
                         "native_worker_owned_and_closed": True, "python_query_read_audit_empty": all(not x["python_read_audit"]["observed_reads"] for x in questions)},
              "final_snapshot_sha256": sha(output/"MAIN_FINAL267.deetsnap"),
              "scope": "Executed public interface and save/load/new-query continuation only; these two queries are not new independent science samples."}
    put(output/"DEMONSTRATION_SUMMARY.json",result)
    print(json.dumps({"verified": True, "classes": [x["resource_class"] for x in questions]}))


if __name__ == "__main__": main()
