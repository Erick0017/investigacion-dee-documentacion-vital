"""Prepara índices/configuración desde pruebas cerradas; NO mide ni ejecuta Native."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / "DEE Cognitive 2.0"


def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    if p.exists(): raise FileExistsError(p)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    closure = P / "control/CIERRE_CIENTIFICO_PI08_R01.json"
    assert sha(closure) == "46ce150dd7bcd720d1cc48825bf806ec7d3c9a57515aba4bc8ffbbdbe9bd6145"
    assert read(closure)["closed"] and read(closure)["all_scoped_Native_writers_closed"]
    cfg = read(P / "codigo/CONFIG_CONTABILIDAD_FINAL_PI08_PLANTILLA.json")
    cfg["closure_gates"] = [{"source": str(closure), "sha256": sha(closure), "pointer": ptr, "expected": True}
                            for ptr in ("/closed", "/all_scoped_Native_writers_closed")]
    partial = P / "control/PI08_F1_CUT_R03.json"
    card = P / "estados/F1_CUT_R03/sistema/estado/vidas/ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_F1_CUT_01/VIDA.json"
    assert read(card)["physical"]["tick"] == read(partial)["final_tick"] == 850023
    cfg["uncheckpointed_advancement_proofs"] = [{
        "source": str(partial), "sha256": sha(partial), "life_pointer": "/life_id",
        "last_observed_tick_pointer": "/final_tick", "unknown_later_advancement": False,
        "scope": "Actual card already850023: extra gap0. Its378ticks are counted by849645→850023, never added twice.",
    }]
    delta = read(P / "control/DELTA_OPERATIVO_PRODUCTO_PROPUESTO_PI08_R02.json")
    cfg["expected_selected_code"] = [{"path": str(C / "sistema" / row["file"]), "sha256": row["sha256"]}
                                      for row in delta["proposed_code_files"]
                                      if row["role"] == "CODE_OR_IMMUTABLE_PROTOCOL"]
    assert len(cfg["expected_selected_code"]) == 19
    cfg["exact_additional_storage_roots"] = []
    cfg["instructions_final_extraction"] = (
        "No external extraction exists at generation. Root must append actual W/p8v08 (or real "
        "fresh destination) with origin_evidence AFTER creating it, then measure once writers "
        "and document/ZIP writes are quiet. All P8 tests/staging are already included by P8 root."
    )
    cfg["expected_ledger"] = {"Native_ticks": 87963, "material_world_slots_including_identity_fork": 10,
                              "unique_life_cards": 9, "actual_identity_forks": 1, "raw_cut_forks": 0}
    config_path = P / "codigo/CONFIG_CONTABILIDAD_FINAL_PI08_R01.json"
    save(config_path, cfg)

    index = {"schema": "DEE.PI08.execution_ledger_index.v1", "evidence": {}, "executions": [],
             "prospective_limits": {"Native_ticks": 150000, "worlds": 10},
             "coverage_is_complete_campaign": True,
             "coverage_declaration": (
                 "All nine material life trajectories, plus the actual zero-future identity "
                 "Runtime fork as a tenth material world slot. Thirteen nonoverlapping execution "
                 "windows sum87963Native. Imports/preparations with0Native contribute0; no cut "
                 "Runtime was created. These are paired physical histories, not independent individuals."
             )}
    files = []
    docs = {}

    def evidence(alias, source, target):
        source = Path(source)
        doc = read(source)
        index["evidence"][alias] = {"file": target, "bytes": source.stat().st_size, "sha256": sha(source),
                                    "source_reference_for_packager_only": str(source)}
        docs[alias] = doc
        files.append({"source": str(source), "file": target, "role": "Actual closed execution-ledger source, complete literal JSON"})

    def add(alias, name):
        evidence(alias, P / "control" / name, "04_EVIDENCIAS/CONTROL/" + name)

    def execution(identity, life, world, bindings, modality="ACTUAL_NATIVE_EXECUTION"):
        fields = {field: {"evidence": alias, "pointer": ptr} for field, (alias, ptr) in bindings.items()}
        index["executions"].append({"execution_id": identity, "life_id": life, "world_key": world,
                                    "modality": modality, "fields": fields})

    add("closure", closure.name)
    add("A_eval", "EVALUACION_CONSOLIDACION_A_PI08_R01.json")
    add("A_public", "PI08_USO_PUBLICO_PRINCIPAL_R01.json")
    life_a = docs["A_eval"]["life_id"]
    a_card = C / "sistema/estado/vidas" / life_a / "VIDA.json"
    assert sha(a_card) == "50ec14550436f5e86892c1b0b4edc3493d6c54c92e548c60d7b899807c7f3966"
    evidence("A_card", a_card, "04_EVIDENCIAS/CONTROL/VIDA_PRINCIPAL_A_T861426.json")
    execution("A_POST4_to_consolidation", life_a, life_a, {
        "life_id": ("A_eval", "/life_id"), "before_tick": ("A_card", "/parent/source_tick"),
        "after_tick": ("A_eval", "/T"), "Native_ticks": ("A_eval", "/Native_ticks_this_candidate_fromPOST4"),
        "scope_closed": ("closure", "/closed")})
    execution("A_selected_public_use", life_a, life_a, {
        "life_id": ("A_public", "/life_id"), "before_tick": ("A_public", "/initial_tick"),
        "after_tick": ("A_public", "/final_tick"), "Native_ticks": ("A_public", "/new_Native_ticks"),
        "scope_closed": ("A_public", "/closed")})
    bi = read(P / "control/B_PORTABLE_CUATRO18_R01/INDICE_B_PI08_R01.json")
    for role, arm in bi["arms"].items():
        alias = "B_" + role
        entry = arm["summary"]
        evidence(alias, P / "control/B_PORTABLE_CUATRO18_R01" / entry["file"], "04_EVIDENCIAS/B/" + entry["file"])
        life = docs[alias]["life_id"]
        execution(alias + "_eighteen", life, life, {"life_id": (alias, "/life_id"),
            "before_tick": (alias, "/initial_tick"), "after_tick": (alias, "/final_tick"),
            "Native_ticks": (alias, "/new_Native_ticks"), "scope_closed": (alias, "/closed")})
    for alias, name in (("B_panel", "PI08_B_CONSERVACION_R02.json"),
                        ("NONE_panel", "PI08_B_NONE_AUTOPSIA_PANEL_R02.json"),
                        ("F1", "PI08_F1_CUT_R03.json"),
                        ("C_prepare", "PI08_C_PREPARAR_R04.json"),
                        ("C_six", "PI08_C_EVALUAR_R04.json")):
        add(alias, name)
        life = docs[alias]["life_id"]
        execution(alias, life, life, {"life_id": (alias, "/life_id"), "before_tick": (alias, "/initial_tick"),
            "after_tick": (alias, "/final_tick"), "Native_ticks": (alias, "/new_Native_ticks"),
            "scope_closed": (alias, "/closed")})
    add("ARP", "VERIFICACION_RO_A_PANEL12_PI08_R01.json")
    life_arp = docs["ARP"]["life_id"]
    execution("ARP_panel12_real_frontend", life_arp, life_arp, {"life_id": ("ARP", "/life_id"),
        "before_tick": ("ARP", "/source_prefix/physical/tick"),
        "after_tick": ("ARP", "/final_record/physical/tick"),
        "Native_ticks": ("ARP", "/actual_new_Native_ticks"),
        "scope_closed": ("ARP", "/actual_material_control_completed")})
    evidence("F1_identity", P / "fuentes/F1_IDENTITY_FALLO_DIFERENCIAS_EXACTAS_R03.json",
             "04_EVIDENCIAS/F1_Q8/F1_IDENTITY_FALLO_DIFERENCIAS_EXACTAS_R03.json")
    life_f1 = docs["F1"]["life_id"]
    execution("F1_actual_identity_fork_no_future", life_f1, life_f1 + "::IDENTITY_RUNTIME_FORK", {
        "life_id": ("F1", "/life_id"), "before_tick": ("F1", "/final_tick"),
        "after_tick": ("F1", "/final_tick"), "Native_ticks": ("F1_identity", "/identity_future_advanced_ticks"),
        "scope_closed": ("F1", "/closed"), "actual_Runtime_forks": ("F1_identity", "/identity_fork_created"),
        "raw_cut_executed": ("F1_identity", "/actual_Native_cut_executed")}, "ACTUAL_IDENTITY_FORK_ZERO_NATIVE_FUTURE")
    assert len(index["executions"]) == 13
    out = P / "fuentes/INDICE_LEDGER_PI08.json"
    save(out, index)
    addon = {
        "files_to_append": files + [{"source": str(out), "file": "04_EVIDENCIAS/CONTROL/INDICE_LEDGER_PI08.json", "role": "Thirteen exact actual execution windows; 87963Native/10material world slots"}],
        "portable_verifications_to_append": [{
            "script": "05_RECALCULO/RECALCULAR_LEDGER_PI08.py", "argv": ["--raiz", "{EXTRACTION}", "--salida", "{OUTPUT}/LEDGER.json"],
            "result_file": "LEDGER.json", "result_schema": "DEE.PI08.portable_execution_ledger_recalculation.v1",
            "expect": {"/all_ledger_checks_passed": True, "/actual_included_Native_ticks": 87963,
                       "/declared_world_scopes": 10, "/coverage_is_complete_campaign": True,
                       "/new_Native_ticks": 0, "/DEE_imports": 0}}],
        "scope": "Additive documentary bindings; Native0. Existing shared evidence members deduplicate only by exact membername/SHA."
    }
    addon_path = P / "fuentes/CONFIG_LEDGER_PORTABLE_PARA_PLAN_PI08_R01.json"
    save(addon_path, addon)
    print(json.dumps({"Native": 0, "measured": False, "created": [{"file": str(q.relative_to(P)), "sha256": sha(q)} for q in (config_path, out, addon_path)]}))


if __name__ == "__main__": main()
