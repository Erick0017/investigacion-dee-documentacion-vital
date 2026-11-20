"""Recalculate packaged CF01 evidence using Python stdlib only, without DEE.

Usage: python RECALCULO/recalcular_todo.py --evidence EVIDENCIA_CAUSAL --out SALIDA
Complete native snapshots are intentionally not required or reconstructed.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--code-index", type=Path, default=HERE.parent / "CODIGO_EJECUTADO/INDICE_CONTENIDOS.json")
    args = p.parse_args()
    evidence = args.evidence.resolve(); out = args.out.resolve()
    if not evidence.is_dir() or not args.code_index.is_file():
        raise FileNotFoundError("Supply the exported primary folder and deduplicated code index")
    out.mkdir(parents=True, exist_ok=True)
    source_index_path = HERE.parent / "INDICE_FUENTES_Y_OMISIONES.json"
    source_index = json.loads(source_index_path.read_text(encoding="utf8"))
    for member in source_index["exported_originals"]:
        if member["category"] != "primary":
            continue
        path = evidence / Path(member["export_relative_path"]).name
        assert path.stat().st_size == member["bytes"] and sha(path) == member["sha256"]
    material_spec = importlib.util.spec_from_file_location("cf01_materializer", HERE / "materializar_codigo_cf01.py")
    material = importlib.util.module_from_spec(material_spec); material_spec.loader.exec_module(material)
    commands = []
    with tempfile.TemporaryDirectory(prefix="cf01_archived_recalc_") as temp:
        view = Path(temp) / "evidence"
        view.mkdir()
        for path in sorted(evidence.glob("*.json.gz")):
            shutil.copyfile(path, view / path.name)
        materialization = material.materialize(args.code_index, view / "codigo_ejecutado")
        scripts = ("recalcular_primarios_cf01.py", "recalcular_tarea_cf01.py", "recalcular_contexto_cf01.py",
                   "recalcular_compuesto_cf01.py", "recalcular_servicio_v3_cf01.py", "recalcular_post_cal8_cf01.py")
        for script in scripts:
            destination = out / (Path(script).stem + ".json")
            argv = [sys.executable, "-I", "-B", str(HERE / script), "--evidence", str(view), "--out", str(destination)]
            result = subprocess.run(argv, capture_output=True, text=True, encoding="utf8")
            commands.append({"script": script, "returncode": result.returncode, "stderr": result.stderr,
                             "stdout": result.stdout, "result_file": str(destination),
                             "result_sha256": sha(destination) if destination.exists() else None})
            if result.returncode:
                raise RuntimeError(script + " failed: " + result.stderr)
    load = lambda name: json.loads((out / (name + ".json")).read_text(encoding="utf8"))
    queue = load("recalcular_tarea_cf01")
    context = load("recalcular_contexto_cf01")
    old = load("recalcular_compuesto_cf01")
    service = load("recalcular_servicio_v3_cf01")
    post = load("recalcular_post_cal8_cf01")
    all_primary = load("recalcular_primarios_cf01")
    report = {"schema": "CF01.packaged_stdlib_recalculation.v1", "new_native_ticks": 0,
      "imports_dee_or_uses_snapshots": False, "python": sys.version, "evidence": str(evidence),
      "all_primaries_verified": all_primary["files_checked"],
      "exact_observations_checked_across_all_primaries": all_primary["observation_records_checked"],
      "source_revisions_materialization": materialization,
      "queue_totals_by_arm": queue["totals_by_arm"],
      "new_context_first_ticks": [{"case": q["case"], "left_context": None if q["first_new_left_context"] is None else q["first_new_left_context"]["tick"]} for q in context["cases"]],
      "old_compound_original_scores": [{"case": q["case"], "summary": q["summary"]} for q in old["cases"]],
      "service_protocol3_totals": service["totals_by_arm"], "POST_and_CAL8": post["summary"],
      "commands": commands,
      "limits": ["Archived arithmetic/field/receipt recalculation only; neither native reproduction nor new experiments.",
                 "Complete snapshots, agendas and unexported deep evidence stay local. Full-state identity checks recorded locally cannot be independently repeated from these reduced primaries alone.",
                 "All exported raw positive and negative primaries are retained, including rejected inputs and old-reader failures."]}
    target = out / "VERIFICACION_RECALCULO_ARCHIVADO.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"report": str(target), "sha256": sha(target), "all_primaries": report["all_primaries_verified"],
                      "new_native_ticks": 0, "service": {k: v["summary"]["external_passed"] for k, v in service["totals_by_arm"].items()},
                      "CAL8": post["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
