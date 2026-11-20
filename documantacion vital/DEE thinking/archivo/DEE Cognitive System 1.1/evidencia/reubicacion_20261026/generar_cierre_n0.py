"""Cierre de rutas e integridad: sólo lecturas y JSON, sin importar DEE."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[1]
THINKING = ROOT.parent

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def witness(path):
    path = Path(path)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)}

native = read(EVIDENCE / "prueba_operativa_R01/RESULTADO_REUBICACION.json")
conservation = read(EVIDENCE / "CONSERVACION_TODOS_LOS_ARCHIVOS.json")
hash_comparison = read(EVIDENCE / "COMPARACION_POSTTRASLADO_N0_R01.json")
manual = ROOT / "DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_17_APD03_AUTONOMIA_DESARROLLO_SIN_VALIDACION_VISUAL.docx"
active = read(ROOT / "sistema/estado/ACTIVO.json")
final_card = read(ROOT / "sistema/estado/vidas/REORG_APD03_01/VIDA.json")
final_snapshot = ROOT / "sistema" / final_card["snapshot"]
assert sha(final_snapshot) == final_card["snapshot_sha256"]
assert not native["issues"] and native["source_and_protected_files_unchanged"]
assert not conservation["fallos"]

out = {
    "schema": "DEE.thinking.reorganization.closure.v1",
    "utc": datetime.now(timezone.utc).isoformat(),
    "status": "MAIN_RELOCATED_AND_PHYSICALLY_VERIFIED_WITH_TWO_UNRESOLVED_REQUIREMENTS",
    "canonical_root": str(ROOT),
    "thinking_root_members": sorted(p.name for p in THINKING.iterdir()),
    "exactly_three_root_folders": False,
    "unresolved": {
        "casos_practicos": {"error": "Windows AccessDenied during rename; cause not established",
            "source": str(THINKING / "casos practicos"),
            "source_still_present": (THINKING / "casos practicos").is_dir(),
            "proposed_archive": str(THINKING / "archivo/estructura_anterior_20261026/casos practicos"),
            "proposed_archive_present": (THINKING / "archivo/estructura_anterior_20261026/casos practicos").exists(),
            "forced_or_deleted": False},
        "original_thinking_45_DOCX": read(EVIDENCE / "BUSQUEDA_MANUALES_45.json")},
    "active_protected": active,
    "latest_principal_option": {"life": "APD03_MAIN", "N": 67, "tick": 604825,
        "native_snapshot_sha256": "c7cf2e78837ed5f99c950016314bfe5f8fbfa868f72a67af36a94a78261a24ba",
        "complete_pair": str(ROOT / "sistema/estado/fuentes_emparejadas/APD03_MAIN_T604825_R01"),
        "not_advanced_by_reorganization_test": True},
    "real_test": {"life": "REORG_APD03_01", "N": 67, "final_tick": final_card["physical"]["tick"],
        "snapshot": witness(final_snapshot), "continuity": native["continuity"],
        "new_native_inputs": native["native_inputs"], "words_RAW": native["words_RAW"],
        "MA_RAW": native["MA_RAW"], "goal_actions": native["goal_actions"],
        "goal_completed": native["goal_progress"]["verified_file_goal_completed"],
        "use_after_reopening": native["reopened_luma_use"],
        "all_own_jobs_completed": all(r["exit_code"] == 0 and not r["resources"].get("job_active_processes") for r in native["runs"]),
        "scope": "Selected operational regression on one identified clone, not all historical suites or a new scientific campaign"},
    "preservation": {"original_files": conservation["archivos_originales"],
        "original_bytes": conservation["bytes_originales_verificados"], "metadata_discrepancies": 0,
        "cryptographic_report": hash_comparison,
        "README_prior_content_backup": str(THINKING / "archivo/reubicacion_20261026/documentos_antes/LEER_PRIMERO.md"),
        "no_snapshot_memory_queue_SQLite_rewriting": True, "files_deleted": 0},
    "manual_current": witness(manual),
    "entry": witness(ROOT / "INICIAR.bat"),
    "entry_adapter": witness(ROOT / "iniciar_local.py"),
    "installed_identity": json.loads(native["official_import"]["stdout"]),
    "official_wheel": witness(ROOT / "sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl"),
    "instructions": {"new_explicit_copy": "INICIAR.bat usar --nueva MI_COPIA",
        "continue_test_clone": "INICIAR.bat usar --vida REORG_APD03_01",
        "same_existing_manager": "INICIAR.bat gestor --help"},
    "evidence": [witness(EVIDENCE / name) for name in (
        "INFORME_REORGANIZACION.md", "MAPA_TRASLADOS.json", "CONSERVACION_TODOS_LOS_ARCHIVOS.json",
        "COMPARACION_POSTTRASLADO_N0_R01.json", "LINEA_BASE_CONSERVACION_N0_R01.json",
        "prueba_operativa_R01/RESULTADO_REUBICACION.json")],
    "interpretation": "The main system works at its new location and states are preserved. The requested visual structure and recovery of the two original DOCX remain incomplete; no global PASS."
}
target = EVIDENCE / "VERIFICACION_FINAL_REORGANIZACION.json"
with target.open("x", encoding="utf8") as stream:
    json.dump(out, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"file": str(target), "sha256": sha(target), "root_folders": out["thinking_root_members"],
                  "test_final_tick": out["real_test"]["final_tick"], "own_jobs_completed": out["real_test"]["all_own_jobs_completed"]}, ensure_ascii=False))
