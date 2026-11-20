"""JSON-only cumulative red analysis; no Native imports or repeat evolution."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def read(path):return json.loads(path.read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def traced(data,tick,site):
    for frame in data.get("trace",[]):
        if frame["tick"]==tick:return frame.get("samples",{}).get(site)
    return None


def main():
    folder=ROOT/"resultados/red";rows=[]
    groups=(("V1_DISCOVERY",folder/"discovery01/CENTRAL/MEASUREMENTS.json"),
            ("V2_ROLES_DISCOVERY",folder/"roles_discovery01/MAIN/MEASUREMENTS.json"))
    files=list(groups)
    files += [(group,path) for group,glob in (("V2_CONFIRMATION","confirmacion02/*/MEASUREMENTS.json"),
               ("V3_DISCOVERY","v3_discovery01/*/MEASUREMENTS.json"),("V3_CONFIRMATION","confirmacion03/*/MEASUREMENTS.json"),
               ("SELECTIVE_NEGATIVE_NEW_CONTEXT","selective_negative01/*/MEASUREMENTS.json"),
               ("DUAL_HABITAT_NEW_CONTEXT","dual_habitat01/*/MEASUREMENTS.json"),
               ("FIXED_NATIVE_COUNTERFLOW","fixed_counterflow01/*/MEASUREMENTS.json"))
              for path in sorted(folder.glob(glob))]
    for group,path in files:
        if not path.exists():continue
        data=read(path)
        if "case" not in data:continue
        rs=data.get("actual_protocol_receipts",data.get("receipts",[]))
        D1=data.get("D_first",data.get("D_first_read",traced(data,161,"D")))
        D2=data.get("D_reused",data.get("D_reused_read",traced(data,228,"D")))
        rows.append({"group":group,"id":data["case"]["id"],"case":data["case"],
                     "path":str(path.relative_to(ROOT)).replace("\\","/"),"sha256":sha(path),
                     "initial_tick":0,"final_tick":data.get("final",data.get("world"))["tick"],
                     "profile":data.get("task_profile",data.get("profiles")),
                     "external_utility":data["external_utility"],"D_first":D1,"D_reused":D2,
                     "D_to_B_current_received":data.get("B_social_received",traced(data,350,"B")),
                     "B_later_query":data.get("B_future_read",traced(data,417,"B")),
                     "receipt_status_counts":dict(Counter(r["status"] for r in rs)),
                     "diagnostic_edits":data.get("diagnostic_edits",[]),
                     "scientific_sample_boundary":"Fresh finite preparation or explicitly identified diagnostic child; known deterministic repetitions are not independent statistical samples."})
    continuations=[]
    for group in ("curriculum01","curriculum03"):
        path=folder/group/"MEASUREMENTS.json"
        if not path.exists():continue
        d=read(path)
        continuations.append({"version_group":group,"path":str(path.relative_to(ROOT)).replace("\\","/"),"sha256":sha(path),
            "parent":d["config"]["parent_checkpoint"],"parent_sha256":d["config"]["parent_sha256"],
            "initial":d["initial"],"final":d["final"],"native_advanced_ticks":d["final"]["tick"]-d["initial"]["tick"],
            "episodes":[{"external_conditions":e["episode"]["conditions"],"offset":e["episode"]["offset"],
                         "D_first":e["D_first"],"D_reused":e["D_reused"],"B_later_query":e["B_later_query"],
                         "profile":e["task_profile"],"external_utility":e["external_utility"],
                         "receipt_counts":dict(Counter(x["status"] for x in e["receipts"]))} for e in d["episodes"]],
            "scope":"One restored full-state MAIN continues through two newly presented external experience episodes, without another create or a fork. It is a continuation of its parent, not another independent preparation.",
            "retention_vs_reacquisition":"The prior useful mobile core can be consumed in action. New experience can reacquire a function in the same declared regions; this does not automatically show rewriting of an unconsumed old carrier."})
    fixed_continuation_path=folder/"fixed_counterflow_continuation01/MEASUREMENTS.json"
    if fixed_continuation_path.exists():
        d=read(fixed_continuation_path);restored=read(fixed_continuation_path.parent/"RESTORE_CHECK.json")
        continuations.append({"version_group":"fixed_counterflow_continuation01",
            "path":str(fixed_continuation_path.relative_to(ROOT)).replace("\\","/"),"sha256":sha(fixed_continuation_path),
            "parent":d["config"]["parent_checkpoint"],"parent_sha256":d["config"]["parent_sha256"],
            "initial":d["initial"],"final":d["final"],"native_advanced_ticks":d["final"]["tick"]-d["initial"]["tick"],
            "same_world_object":d["same_world_object"],"scheduling_physical_state_unchanged":d["initial"]==d["after_scheduling"],
            "episodes":[{"external_conditions":d["config"]["external_conditions"],"offset":d["config"]["offset"],
                         "D_first":traced(d,661,"D"),"D_reused":traced(d,728,"D"),"B_later_query":traced(d,917,"B"),
                         "profile":d["profiles"],"external_utility":d["external_utility"],
                         "receipt_counts":dict(Counter(x["status"] for x in d["receipts"]))}],
            "restore_check":restored,
            "scope":"Same current world437->937, with a new external experience C- after the earlier Flat/C+ use. No create/fork/body replacement in continue_session; one explicit complete-state load only at CLI entry.",
            "retention_vs_reacquisition":"Prior products can have been consumed. The record establishes finite continuing acquisition/use, not unlimited renewal or overwrite of an unconsumed individual carrier."})
    by_id={(x["group"],x["id"]):x for x in rows}
    comparisons=[]
    for version,full,other,meaning in (
        ("V2_CONFIRMATION","FULL_U","D_NAIVE_U","In U, the acquired D path changes the measured bank profile"),
        ("V2_CONFIRMATION","FULL_V","D_NAIVE_V","In V, the same action spends an optional resource without adding primary delivery"),
        ("V2_CONFIRMATION","FULL_U","C_UNPAIRED_U","Unpaired C still produces the useful route; V2 does not isolate necessary pair acquisition for C"),
        ("V2_CONFIRMATION","FULL_U","D_UNPAIRED_U","Unpaired D still preserves V2 task utility with lower payload"),
        ("V3_CONFIRMATION","FULL_U","D_UNPAIRED_U","V3 distinguishes the prepared D report-alone alternative under its fixed two-probe panel"),
        ("V3_CONFIRMATION","FULL_U","D_SOURCE_LATE_CUT","A one-site late removal after learned D84 emission changes later B reception and use"),
        ("V3_CONFIRMATION","FULL_U","SHAM_DUMMY_REMOVE","The common supplied dummy removal is measured rather than assumed comparable"),
        ("V3_CONFIRMATION","FULL_U","C_OPPOSITE_ALTERNATIVE_PATH","Equal bank output can coexist with different D access and a retained B path")):
        a,b=by_id.get((version,full)),by_id.get((version,other))
        if a and b:comparisons.append({"version":version,"left":full,"right":other,"meaning":meaning,
            "left_profile":a["profile"],"right_profile":b["profile"],"left_D_read":a["D_reused"],"right_D_read":b["D_reused"],
            "left_B_read":a["B_later_query"],"right_B_read":b["B_later_query"]})
    selective=[]
    for row in rows:
        if row["group"]=="SELECTIVE_NEGATIVE_NEW_CONTEXT":
            selective.append({"id":row["id"],"B_later_query":row["B_later_query"],"profile":row["profile"],
                              "scope":"New negative-z physical probe and independently prepared negative-z bank; never a rescore of the positive-z V3 bank."})
    dual_calibration=None
    calibration_path=folder/"dual_habitat01/CALIBRATION/MEASUREMENTS.json"
    if calibration_path.exists():
        d=read(calibration_path)
        dual_calibration={"path":str(calibration_path.relative_to(ROOT)).replace("\\","/"),
            "sha256":sha(calibration_path),"empty_preparation_count":1,"empty_parent_advanced_ticks":d["parent"]["tick"],
            "diagnostic_fixed_policy_forks":len(d["rows"]),
            "native_ticks_forks":sum(x["world"]["tick"]-d["parent"]["tick"] for x in d["rows"]),
            "parent_unchanged":d["parent_unchanged"],
            "rows":[{"x":x["x"],"c":x["c"],"fixed_external_policy":x["external_fixed_policy"],
                     "profiles":x["profiles"],"external_utility":x["external_utility"],
                     "receipt_status_counts":dict(Counter(q["status"] for q in x["receipts"]))} for x in d["rows"]],
            "scope":"One empty prepared world advanced to416 and16 complete instrumental forks advanced21 ticks each. No learned organization was erased. These are not16 independently acquired network preparations."}
    dual_rows=[{"id":row["id"],"profile":row["profile"],"utility":row["external_utility"],
                "B_later_query":row["B_later_query"],"case":row["case"]} for row in rows if row["group"]=="DUAL_HABITAT_NEW_CONTEXT"]
    regulation=[]
    for path in sorted((folder/"fixed_counterflow01").glob("*/MEASUREMENTS.json")):
        d=read(path);frames={q["tick"]:q for q in d["trace"]}
        regulation.append({"id":d["case"]["id"],"case":d["case"],"meeting292":d["local_contexts"]["meeting292"],
            "actual_meeting293":frames[293]["regulation_samples"]["meeting"],
            "actual_meeting294":frames[294]["regulation_samples"]["meeting"],
            "n_active293":d["local_contexts"]["meeting293"]["n_active"],
            "material_branch_scope":"When the293 center is state>0,semantic1 and n_active0, its material survival rule is0; the observed294 site becomes empty. The empty-destination reconstruction is not applied to this occupied293 center.",
            "B_social350":frames[350]["samples"]["B"],"B_query417":frames[417]["samples"]["B"],
            "profiles":d["profiles"],"external_utility":d["external_utility"],
            "receipt_counts":dict(Counter(q["status"] for q in d["receipts"]))})
    residual=None
    residual_path=folder/"residual425_diagnostic01/MEASUREMENTS.json"
    if residual_path.exists():
        d=read(residual_path);branch=d["local_branch424"]
        residual={"path":str(residual_path.relative_to(ROOT)).replace("\\","/"),"sha256":sha(residual_path),
            "native_advanced_ticks":33,"intact_replay":{"initial_tick":417,"final_tick":437,"advanced_ticks":20},
            "diagnostic_child":{"initial_tick":424,"final_tick":437,"advanced_ticks":13},
            "intact_reproduces_canonical437":d["passive_reproduces_canonical437"],"source_snapshot_unchanged":d["source_snapshot_unchanged"],
            "local_target":branch["center"],"local_active_neighbor_count":branch["n_active"],
            "crystallization_guard":branch["crystallization_guard"],"XNOR_guard":branch["xnor_guard"],
            "actual_sources":branch["directional_sources"],"directional_reducer_prediction":branch["reconstructed_empty_directional_result"],
            "edit":d["edit"],"outcomes":d["outcomes"],
            "scope":"Observed 42+5->47 at an empty destination changes direction; a one-site raw deletion has conditional rescue in this complete saved background. This is an external diagnostic, not an autonomous action or repair."}
    identity=[]
    for group in ("confirmacion02","confirmacion03","selective_negative01","dual_habitat01","fixed_counterflow01"):
        if not (folder/group/"EXPERIMENT_CONFIG.json").exists():continue
        config=read(folder/group/"EXPERIMENT_CONFIG.json")
        identity.append({"group":group,"checks":[{"file":name,"frozen_sha256":expected,
            "current_sha256":sha(ROOT/"src/red"/name),"current_equal":sha(ROOT/"src/red"/name)==expected,
            "frozen_copy_present":(folder/group/"EXECUTED_SOURCE"/name).exists(),
            "frozen_copy_equal":sha(folder/group/"EXECUTED_SOURCE"/name)==expected}
            for name,expected in config["source_sha256"].items()]})
    report={"type":"READ_ONLY_REANALYSIS","native_calls":0,"fresh_preparation_records":len(rows),
            "counts_by_group":dict(Counter(row["group"] for row in rows)),
            "native_ticks_fresh_trajectories":sum(x["final_tick"] for x in rows),
            "continuation_count":len(continuations),"continuation_new_experience_episodes":sum(len(x["episodes"]) for x in continuations),
            "native_ticks_continuations":sum(x["native_advanced_ticks"] for x in continuations),
            "counts_exclude":"Language, small-backend/persistence windows and observer diagnostics are separately owned and not counted here.",
            "rows":rows,"continuations":continuations,"comparisons":comparisons,"selective_negative_extension":selective,
            "dual_habitat_extension":dual_rows,"dual_instrumental_calibration":dual_calibration,
            "residual_counterfactual_replay":residual,"frozen_source_checks":identity,
            "fixed_native_regulation":regulation,
            "mechanism_scope":[
                "Initial RAW/clock worlds are empty prepared Research67 worlds. All finite physical interfaces exist at T0; experiences are actual queued inputs, not prewritten learned carrier states.",
                "A/B/C/D denote finite mobile functional regions, not four fully renewable basal bodies.",
                "Native coalescence transforms acquired relations. D's full v3 path combines its prior acquired z component with the A+B+C product and is later used as the source to B through a prepared native relay.",
                "The routing/turner geometry was designed, not acquired as an arbitrary policy. No host read-A then write-message-to-B copy occurs.",
                "V3 D uses a fixed alternating +X then -X two-probe panel. It is not two identical endlessly renewable probes; queries alter the state.",
                "The C-unpaired/opposite-context v3 worlds expose another useful route: a current B37-compatible retained state is later expressed as B42. Equal F/R does not make the internal acquired relations equal.",
                "The additional two experience episodes are received in one continuing world per curriculum. Cases, ticks, queries and deterministic replays are not statistically independent replicates.",
                "R/F availability and score2*F+R are finite external task measures. The score is never supplied as a reward or used to choose an action.",
                "External future U/V packets and experience reports are declared synthetic protocols. The Native kernel does not read case names, pending-input metadata, semantic labels or evaluator state.",
                "The negative-z reader is an externally selected physical query context. Its selective D-dependent bank is a new protocol, not a reinterpretation of the positive-z V3 output and not learned attention.",
                "The two-bank external habitat was independently calibrated with fixed physical policies and no organism. In the integrated network, N use and both benign contexts preserve their intended finite profiles, while Flat use has an observed residual-interference boundary also present in its reserved translation.",
                "The confirmed unused relay5 is a real residual carrier. A later fixed zero-load carrier is a distinct native-regulation experiment, not learned attention, learned utility, or a retrospective repair of earlier records.",
            ],
            "limits":[
                "C alone has not been shown necessary for every successful bank response; the preserved B alternative is an observed limit on that attribution.",
                "The current sparse frames and compatible transport endpoints are not a complete unique global genealogy. Local branch and selective-cut evidence is separate.",
                "Function reuse and new experience through1431 are finite observations, not autonomous indefinitely sustained learning or optimal utility adaptation.",
                "Resource packets are supplied each episode. New resource supply is an explicit environmental opportunity, not hidden replenishment to erase saturation.",
                "Operational metadata/save writes are host operations distinct from RAW/clock physics. Input receipts are real; absence of an undocumented API call is limited by the reviewed source/instrument coverage.",
                "A correct empty-world actuator calibration does not establish that the same actuator trajectory remains isolated from all residual carriers in an acquired network.",
            ],
            "technical_hotfixes":["Private common-helper import resolves src namespace collision; original executed V2 source copies remain intact.",
                 "The unexecuted first V3 curriculum evaluator used V2 direction constants. It was corrected to declared role-bank directions before the first V3 curriculum Native run; the previous source remains preserved. This did not alter Native inputs or evolution."]}
    put(folder/"NETWORK_MEASUREMENTS_SUMMARY.json",report)
    auxiliary_ticks=(dual_calibration["empty_parent_advanced_ticks"]+dual_calibration["native_ticks_forks"] if dual_calibration else 0)+(residual["native_advanced_ticks"] if residual else 0)
    report["native_ticks_including_own_instrumental_windows"]=report["native_ticks_fresh_trajectories"]+report["native_ticks_continuations"]+auxiliary_ticks
    put(folder/"NETWORK_MEASUREMENTS_SUMMARY.json",report)
    index={"type":"ARTIFACT_INDEX_READ_ONLY","native_calls":0,
        "fresh_preparation_records":len(rows),"counted_groups":report["counts_by_group"],"continuation_worlds":len(continuations),
        "continuation_new_episodes":report["continuation_new_experience_episodes"],
        "instrumental_empty_parent":1 if dual_calibration else 0,"instrumental_fixed_policy_forks":dual_calibration["diagnostic_fixed_policy_forks"] if dual_calibration else 0,
        "diagnostic_local_replays":1 if residual else 0,"diagnostic_one_site_children":1 if residual else 0,
        "native_advanced_ticks_own_records_only":report["native_ticks_including_own_instrumental_windows"],
        "not_independent_samples":"No tick, query, source code copy, repeated deterministic state, cumulative analysis or diagnostic clone is promoted to an independent learned individual.",
        "measurement_files":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p)} for p in sorted(folder.rglob("MEASUREMENTS.json")) if "EXECUTED_SOURCE" not in p.parts],
        "source_files":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p)} for p in sorted((ROOT/"src/red").glob("*.py"))],
        "configuration_files":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p)} for p in sorted(folder.rglob("*EXPERIMENT_CONFIG.json"))],
        "checkpoints":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"bytes":p.stat().st_size} for p in sorted(folder.rglob("*.deetsnap"))],
        "last_resumable_checkpoints":["resultados/red/curriculum03/T1431.deetsnap","resultados/red/fixed_counterflow_continuation01/T937.deetsnap"],
        "other_owners_excluded":"Language and observer/backend/fork technical checks have separate identities and counts."}
    put(folder/"NETWORK_INDEX.json",index)
    freeze={"scope":"Current red tools at closure; historical executed-source capsules retain their independently frozen bytes.",
            "no_additional_native_evolution_after_closure":True,"files":index["source_files"]+
            [{"path":"src/red/LEEME_RED.md","sha256":sha(ROOT/"src/red/LEEME_RED.md")}],
            "frozen_configurations":index["configuration_files"]}
    put(folder/"RED_SOURCE_FREEZE.json",freeze)
    final_path=folder/"fixed_counterflow_continuation01/T937.deetsnap"
    closure={"status":"FINITE_CUT_CLOSED","native_jobs_owned_by_red_running":0,
        "fresh_preparation_records":len(rows),"counts":report["counts_by_group"],
        "continuations":len(continuations),"new_experience_episodes":report["continuation_new_experience_episodes"],
        "instrumental_calibration":{"empty_preparation":1,"fixed_policy_forks":16},
        "causal_window":{"intact_local_replay":1,"one_site_external_diagnostic_child":1,"native_ticks":33},
        "native_ticks_own_records_including_instrumental":report["native_ticks_including_own_instrumental_windows"],
        "final_resumable_checkpoint":{"path":str(final_path.relative_to(ROOT)).replace("\\","/"),"sha256":sha(final_path),
              "tick":937,"profile":"red.regulated_session.NetworkSession","metadata_key":"cpc4.extension02.abcd.fixed_counterflow.v1","metadata_version":6},
        "other_resumable_checkpoint":"resultados/red/curriculum03/T1431.deetsnap",
        "reproduction":["python -I -B src/red/regulated_habitat.py --case resultados/red/fixed_counterflow01/casos/FILTER_FLAT.json --output NUEVO",
                        "python -I -B src/red/regulated_curriculum.py --parent NUEVO/T437.deetsnap --output NUEVO_CONT"],
        "scope_statements_es":[
            "Las regiones A/B/C/D son aparatos móviles funcionales finitos en un Runtime, no cuatro cuerpos basales plenamente renovables.",
            "D combina la historia previa adquirida con el producto social nativo y puede convertirse después en fuente física para B; la topología y el relay son preparados.",
            "Los controles desacoplados de V2 preservan una alternativa real; V3 y el lector negativo son preguntas físicas versionadas, no borran ese dato.",
            "El hábitat de dos bancos fue calibrado sin organismo y no admite una misma política fija óptima en los cuatro contextos ensayados. La red original falla en Flat por una colisión residual medida y preservada.",
            "El contraflujo fijo de carga cero produce un encuentro nativo que elimina la dirección del residuo; no es regulación aprendida, atención autónoma, feedback de puntuación ni limpieza de MAIN desde Python.",
            "La misma World continúa437→937 con nuevas experiencias C-; usa D→B y cambia la vía funcional sin resets, recreación ni retorno de forks.",
            "La query es intervención física consumible. Se probaron horizontes finitos, con recursos externos explícitos; no se afirma aprendizaje ilimitado ni transferencia universal.",
            "Los puntajes son análisis externos de perfiles RAW actuales, jamás entradas del decisor. U/V es una ley ambiental sintética que no lee la acción para escoger la amenaza."]}
    put(folder/"RED_CLOSURE.json",closure)
    print(json.dumps({"records":len(rows),"counts":report["counts_by_group"],"continuations":len(continuations),
                      "native_ticks_excluding_other_tools":report["native_ticks_fresh_trajectories"]+report["native_ticks_continuations"]}))


if __name__=="__main__":main()
