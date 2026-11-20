"""Directed archival audit for CPC8. No participant import or native execution.

Original archives are read-only. Only metadata and selected byte-exact members
are written under this run's genealogia/, plus two interpretation documents.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

RUN = Path(__file__).resolve().parents[1]
BASE = next(parent for parent in RUN.parents if parent.name == "documantacion vital")
PRACTICAL = BASE / "DEE thinking/casos practicos"
ARCHIVES = {}
SELECTED = {}
OPEN = {}
INCIDENTS = []
MAX_REFERENCE_COPY = 2 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def save(relative, data):
    path = RUN / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, (dict, list)):
        data = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    elif isinstance(data, str):
        data = data.encode("utf-8")
    if path.exists():
        if path.read_bytes() == data:
            return
        if "/fuentes/" in "/" + relative:
            raise ValueError("Different bytes under an existing source identity: " + relative)
    path.write_bytes(data)


def locate(folder, pattern):
    found = list((BASE / folder).glob(pattern))
    if len(found) != 1:
        raise ValueError((folder, pattern, [str(p) for p in found]))
    return found[0]


def register(source_id, folder, pattern, expected=None):
    path = locate(folder, pattern)
    identity = file_sha(path)
    if expected is not None and identity != expected:
        raise ValueError((source_id, "Unexpected original cut", identity, expected))
    archive = zipfile.ZipFile(path)
    OPEN[source_id] = archive
    ARCHIVES[source_id] = {
        "id": source_id, "file": path.name,
        "source_path_relative_to_documentation": path.relative_to(BASE).as_posix(),
        "sha256": identity, "compressed_file_bytes": path.stat().st_size,
        "member_count": len(archive.infolist()),
        "expanded_bytes": sum(info.file_size for info in archive.infolist()),
        "identity": "MATCH_REFERENCE" if expected else "IDENTIFIED_REAL_ARCHIVE",
        "source_modified": False, "read_scope": "CENTRAL_DIRECTORY_AND_EXPLICIT_SELECTED_MEMBERS",
    }
    return archive


def member(source_id, name, expected=None, role="historical_primary_or_source"):
    key = source_id + ":" + name
    if key in SELECTED:
        result = SELECTED[key]
        if expected:
            assert result["member_sha256"] == expected, key
        return deepcopy(result)
    archive = OPEN[source_id]
    info = archive.getinfo(name)
    data = archive.read(info)
    identity = sha(data)
    if expected and identity != expected:
        raise ValueError((key, "Member hash mismatch", identity, expected))
    ext = Path(name).suffix.lower()
    copied = len(data) <= MAX_REFERENCE_COPY and ext in (".json", ".jsonl", ".md", ".txt", ".py", ".cpp", ".hpp", ".h", ".eventos")
    destination = "genealogia/fuentes/" + identity[:20] + ext if copied else None
    if copied:
        save(destination, data)
    result = {
        "source_id": source_id, "source_archive": ARCHIVES[source_id]["file"],
        "archive_sha256": ARCHIVES[source_id]["sha256"], "member": name,
        "member_sha256": identity, "bytes": len(data), "crc32": f"{info.CRC:08x}",
        "role": role, "copied_as": destination,
        "copy_state": "BYTE_EXACT_REFERENCE_INCLUDED" if copied else "HASHED_ARCHIVE_REFERENCE_NOT_INCLUDED",
        "execution_by_this_audit": False,
    }
    SELECTED[key] = result
    return deepcopy(result)


def json_member(source_id, name):
    return json.loads(OPEN[source_id].read(name).decode("utf-8-sig"))


def historical_states(documentary=False):
    return {
        "historical": "DOCUMENTARY_SYNTHESIS" if documentary else "REPORTED_MEASURED_IN_ORIGINAL_CUT",
        "source_preserved": True, "reproduced_in_CPC8": False,
        "adapted_in_CPC8": False, "integrated_in_CPC8_MAIN": False,
        "CPC8_state": "REFERENCE_PRESERVED_NOT_REEXECUTED_BY_AUDIT",
        "rule": "A source hash or inherited API is not a new physical reproduction or integration. CPC8 state requires explicit new result links.",
    }


def add_row(rows, identity, mechanism, domain, sources, limits, new_question, controls, **extra):
    rows.append({"id": identity, "mechanism": mechanism, "domain": domain,
                 "origins": sources, "controls": controls, "published_limits": limits,
                 "CPC8_question": new_question, "state": historical_states(), **extra})


def main():
    # Exact canonical practical cuts, independently rehashed in this audit.
    practical = "DEE thinking/casos practicos"
    for sid, pattern, expected in [
        ("CPC3", "CPC3_*RESULTADOS.zip", "1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6"),
        ("CPC4", "CPC4_*RESULTADOS.zip", "4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723"),
        ("CPC5", "CPC5_*RESULTADOS.zip", "d31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05"),
        ("CPC6", "CPC6_*RESULTADOS.zip", "9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b"),
        ("CPC7", "CPC7_*RESULTADOS.zip", "64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128"),
    ]:
        register(sid, practical, pattern, expected)
    register("PRODUCT45", "DEE thinking/4.5", "DEE_THINKING_4_5_0_*RESULTADOS.zip")
    old_map = json_member("CPC7", "CPC7/revision/MAPA_CPC1_A_6.json")
    member("CPC7", "CPC7/revision/MAPA_CPC1_A_6.json", role="prior_directed_genealogy_index")
    # The previous map fixes the precise original names and hashes, not dates.
    for record in old_map["archives"]:
        sid = record["id"]
        if sid in ARCHIVES:
            assert ARCHIVES[sid]["sha256"] == record["sha256"]
            continue
        folders = {"PRODUCT4": "DEE thinking/4.0", "ING01": "ingenieria", "ING02": "ingenieria", "ING05": "ingenieria", "ING06": "ingenieria", "CORE06": "cores", "CORE07": "cores", "PROC01": "procesos", "PROC02": "procesos", "PROC03": "procesos"}
        folder = folders[sid]
        if not (BASE / folder / record["file"]).is_file() and sid == "PRODUCT4":
            folder = "DEE thinking/archivo"
        register(sid, folder, record["file"], record["sha256"])
    for sid, folder, pattern in [("CORE15", "cores", "15_*.zip"), ("CORE16", "cores", "16_*.zip"), ("CORE17", "cores", "17_*.zip"), ("MBP4", "mente basal", "MENTE_BASAL_4_*.zip"), ("ING03", "ingenieria", "INGENIERIA_03_*.zip"), ("ING04", "ingenieria", "INGENIERIA_04_*.zip")]:
        register(sid, folder, pattern)

    register("FISICA_UNI1", "FISICA DEE UNI 1", "FISICA_DEE_UNI_1_RESULTADOS.zip")
    register("DOCUMENTARY_PACK", "documentos necesarios para cada chat", "DOCUMENTOS_NECESARIOS_PARA_CADA_CHAT.zip")
    ARCHIVES["DOCUMENTARY_PACK"]["read_scope"] = "CENTRAL_DIRECTORY_ONLY; 11 Word documents not newly opened, extracted or claimed read"
    ARCHIVES["DOCUMENTARY_PACK"]["members_located_not_read"] = OPEN["DOCUMENTARY_PACK"].namelist()
    rows = []
    for original in old_map["rows"]:
        evidence = []
        for ref in original["evidence"]:
            if ref.get("source_id") in ARCHIVES and ref.get("member"):
                evidence.append(member(ref["source_id"], ref["member"], ref.get("member_sha256"), ref.get("role", "historical_selected_member")))
            elif ref.get("file"):
                # Existing textual extracts are read as JSON; no new Word
                # extraction, rendering, or full-document reading is implied.
                name = "CPC7/" + ref["file"]
                evidence.append(member("CPC7", name, ref.get("hash"), "prior_documentary_text_extract_not_new_DOCX_read"))
        current = {
            "id": original["id"], "source": original["source"], "mechanism": original["mechanism"],
            "domain": original["domain"], "controls": original["controls"],
            "published_limits": original["published_limits"], "origins": evidence,
            "state": historical_states(original["id"] in ("PROCESAMIENTO_NATIVO", "FISICA_META_ROSETTA")),
            "prior_CPC7_state": original.get("CPC7_state"), "prior_CPC7_state_details": original.get("state"),
            "historical_commands": original.get("historical_execution_command"),
            "CPC7_commands": original.get("CPC7_commands", []),
            "CPC8_question": original.get("CPC7_question", "Preserve the mechanism and test any new coupling separately."),
        }
        # Attach current-CPC7 result identities without turning their old state
        # into a CPC8 execution. Hash all, deduplicate physical copies by SHA.
        current["CPC7_primary_links"] = []
        for ref in original.get("CPC7_evidence", []):
            current["CPC7_primary_links"].append(member("CPC7", "CPC7/" + ref["file"], ref.get("sha256"), "CPC7_result_not_CPC8_reproduction"))
        rows.append(current)

    p7 = "CPC7/"
    cpc7_sources = {
        "integrated": [p7 + "src/integrated_public.py", p7 + "resultados/integrated_revision/IR_P01_GUARDED_M1/MEASUREMENTS.json", p7 + "resultados/integrated_revision/IR_R607_GUARDED_M1/MEASUREMENTS.json"],
        "revision": [p7 + "src/update_methods.py", p7 + "revision/RETENCION_Y_PLASTICIDAD.json"],
        "need": [p7 + "src/endogenous/comparison_need.py", p7 + "revision/INICIATIVA_INTERPRETACION.md"],
        "absence": [p7 + "src/endogenous/comparison_need_v2.py"],
        "composition": [p7 + "src/selective_native.py", p7 + "revision/COMPOSICION_Y_DIALOGO.json"],
        "catalogue": [p7 + "revision/NSM65_EVIDENCIAS.json"],
    }
    refs = {key: [member("CPC7", name) for name in names] for key, names in cpc7_sources.items()}
    add_row(rows, "CPC7_U0_CONTINUITY", "One new U0 acquires its own order and banks, requests/uses information, associates an opaque form, acquires more and selectively revises one relation.", "N67 MAIN T0-472; 16 acquired forms; fourteen lower-bank queries at204/338; L03 update402/read472.", refs["integrated"], "Prepared opportunities, guard geometry and finite pedagogic revision; old/new L03 are not simultaneously retained; the opaque sign was not retested after402.", "Retain earlier functional knowledge during diverse new acquired functions in one actual MAIN.", "auxiliary offpath matched dose; offpath guards; new history/geometry reserve")
    add_row(rows, "CPC7_SELECTIVE_REVISION_M1_M2", "Actual experience plus a second teacher or two zero-load counterflows changes one direction while another remains usable.", "Finite declared phases, query at5N after revision4N; U0 lesson402/read472.", refs["revision"], "Extra physical resources and externally declared timing; not free, reward-selected or unbounded regulation.", "Join finite acquired-state revision to learned relevance and renewable access.", "ordinary revision; dose/routing shams; opposite/history reserves")
    add_row(rows, "CPC7_PREPARED_DISCREPANCY_REQUEST", "An acquired expectation physically meets an independently encoded actual outcome; the resulting state conditions a native request and later use.", "Finite N67 prepared comparison/opportunity; emission5, comparison15, request19; own access70/use72 in U0.", refs["need"], "Question structure and candidate routes are prepared, not a learned general when/what/whom policy.", "Learn which information is needed without a host error-driven corrective callback.", "matching actual; question cut after emission; absent/unpaired source; sham")
    add_row(rows, "CPC7_ABSENCE_APERTURE", "A separate prepared physical aperture makes a missing current report produce a request and use.", "N67 V2 separate from U0; request19/information24/use29; finite horizon35.", refs["absence"], "Native finite window, not host-timeout detection; report/reader/source absences require separate controls.", "Use several uncertainty/absence contexts without giving the agent the auditor's cause label.", "match/discrepancy; request cut; sham; opposite/history reserve")
    add_row(rows, "CPC7_DIRECTIONAL_COMPOSITION_AND_POST_NAME", "Acquired order selects a bank; readout preserves branch X and content Y; common use adds Z; later cue-alone reexpresses acquired content.", "U0 bank70/use72/name75/query139/read142; lower repertoire panels204/338/472.", refs["composition"], "Prepared role geometry, finite association; word direction loses X while spatial bank retains role; not arbitrary syntax or all NSM meanings.", "Preserve referents/roles under new combinations and communicate those combinations physically.", "opposite order; opposite content; omitted/unpaired name; formed-message cut; sham")
    add_row(rows, "CPC7_NSM65_SCOPE", "A sourced catalogue records65 proposed primitives with independent evidence states and mechanism links.", "Documentary registry plus local opaque signs; no complete NSM primitive acquired in CPC7.", refs["catalogue"], "Loading JSON is not learning. Operational local relations require separate generalization/retention/use tests.", "Attempt distinct semantic relations through prelinguistic function, paired arbitrary signal and reserved use.", "fixed codec/decoder, swapped names, unpaired/omitted experience, appropriate intervention")
    rows[-1]["state"] = historical_states(True)

    product_prefix = "DEE_thinking_4_5_0/"
    product_refs = [member("PRODUCT45", product_prefix + name) for name in ["MATRIZ_CAPACIDADES_CPC.json", "MATRIZ_4_0_A_4_5.json", "MATRIZ_SUPERSESIONES.json", "VALIDATION_REPORT.json", "PRODUCT_CONTRACT.json", "validation/SOURCE_DIFF.json", "validation/FINAL_RUN_final6.json"]]
    capabilities45 = json_member("PRODUCT45", product_prefix + "MATRIZ_CAPACIDADES_CPC.json")
    add_row(rows, "PRODUCT45_PORT_VALIDATION", "Compiled optional native repertoire/U0 factories, installed session/persistence interfaces and separate finite experimental recipes preserve measured CPC trajectories.", "Windows x64 CPython3.13; frozen v27; 9 inherited families,14 registry additions including3 experimental and1 documentary entry.", product_refs, "Software port validation is not a new life acquiring65 meanings; a common API does not merge incompatible geometries.", "Use the installed4.5 artifact for all new CPC8 trajectories; compare physical/operative state independently of metadata.", "61 inherited+21 new Python tests;68 differential paths; remote38/absence35 boundaries;4 crossed continuations; exact clean extraction")
    rows[-1]["software_validation_not_new_science"] = True

    extra_specs = [
        ("CORE15_OBSERVER_SHADOW", "CORE15", ["FINAL_REPORT.md", "FINAL_FRONTIER.md", "MECHANISM_ADJUDICATION_EXPANSION.json"], "Transport, destination-fiber reduction and event/support observers form a bounded coupled shadow family.", "48/48 positive expansion confirmations,44/48 canaries; saturation made four temporal-removal canaries non-discriminating.", "Saturation can erase the chosen metric without erasing all function; no universal scalar or external low-parameter Rosetta earned.", "Calibrate multiple descriptors against native function and controls, not cluster appearance."),
        ("CORE16_OBSERVER_INFORMATION", "CORE16", ["FINAL_REPORT.md", "CROSS_SCALE_INFORMATION_FLOW.json", "CROSS_SCALE_MEMORY.json"], "Full RAW,clock,topology and reducer context support distinct R0/R1/R2/R3 projections; hidden information can return through an allowed interaction.", "Source-specific finite domains; no general quantum/thermal identification inferred from shared names.", "Many-to-one convergence differs from projection loss; inaccessible information is not automatically destroyed.", "Locate latent functional knowledge with new common probes and compare complete state before claiming forgetting."),
        ("CORE17_COMPRESSED_OPERATOR_AND_REPAIR", "CORE17", ["CORE17_FINAL_REPORT.md", "CORE17_FINAL_FRONTIER.md", "EXTENSION/CORE17_FINAL_FRONTIER_EXTENSION.md"], "The later definitive closure reports exact R0_FACTOR_52 and functional policy reconstruction from an acquired redundant copy via an explicit carrier.", "Compressed operator:10 fresh worlds/406 steps; redundancy repair treatment12/12 with discriminating source/route/direction controls.", "Initial frontier is superseded by its appended closure on these two branches; repair is supported reconstruction, not local self-regeneration or universal compression.", "Use redundancy as a controllable functional resource; do not reread the initial pending frontier as a still-missing achieved mechanism."),
        ("ING05_HISTORY_FACTORIAL", "ING05", ["INGENIERIA_05/MASTER_INDEX/MASTER_INDEX.md", "INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/SCIENTIFIC_REPORT.md", "INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/RESULTS/NRD05_HISTORY_CONDITIONED_TRANSFORMATION.json"], "The same second experience has a different transformation after a prior history, in a four-world factorial with retained future-relevant differences.", "W00/W10/W01/W11, retention64; disjoint-route and two fresh geometry controls.", "Host initiates real experiences at frozen boundaries; no demonstrated universal environmental autonomy.", "Use matched history-by-new-experience contrasts, not only differing terminal hashes."),
        ("ING06_POST_HOST_OPPORTUNITIES", "ING06", ["INGENIERIA_06/MASTER_INDEX/MASTER_INDEX.md", "INGENIERIA_06/14_THREE_METHOD_CONVERGENCE/SCIENTIFIC_REPORT.md"], "History changes post-host RAW dynamics and persistent organization of existing future-relevant causal opportunities.", "MAIN+two spatial validations; sensitive-opportunity V2 and RAW-only methods; Method C gate not met.", "Missing edge is new unpreloaded contingency to new retained history; no general negative from a failed discovery gate.", "Check whether new consequences actually write new retained distinctions rather than merely reveal old reachability."),
        ("PROC02_PREEXISTING_INTERFACE", "PROC02", ["SCIENTIFIC_REPORT.md", "results.json", "runner_procesos02.py"], "A history-conditioned expanding front transforms an already prepared stable interface; EARLY and LATE produce different stable states and diagnostic future capacity.", "HOST_STOP4; EARLY1→2 and LATE1→2→3; same14-site support; clone challenge2/0/2; MAIN plus two fixed transforms.", "Diagnostic reinstantiation is a fork test, not autonomous repair; central state and surrounding context are not isolated as separate sufficient causes.", "Use function/context readouts when geometry/counts are equal; preserve backaction and query modality."),
        ("PROC03_EXCHANGE_DISCOVERY", "PROC03", ["SUMMARY.json", "CONTRACT.json", "R4_NEW_PREREGISTRATION.json"], "Executed calibrated fluctuation/response and exchange-profile discovery using actual v27 trajectories.", "Official historical WHL, discovery33696 native steps; selected observer/operator absent; holdout untouched in this source cut.", "Discovery UNINFORMATIVE here is not a universal impossibility; a conversation describes later gate tests not assumed present in this archive.", "Recover any later primary gate artifact before promoting a universal native-temperature relation."),
    ]
    for identity, sid, names, mechanism, domain, limits, question in extra_specs:
        add_row(rows, identity, mechanism, domain, [member(sid, name) for name in names], limits, question, "Source-specific controls retained in the named primary cut; no native rerun by this audit.")
        if sid == "CORE17":
            rows[-1]["origins"] += [member(sid, name, role="exact_historical_repair_recipe_or_frozen_primary") for name in ["EXTENSION/RUNNERS/run_e02_redundant_policy_repair.py", "EXTENSION/RUNNERS/run_e03_policy_repair_holdout.py", "EXTENSION/FREEZE/C17E03_POLICY_REPAIR_LOCK.json", "EXTENSION/HOLDOUT/C17E03_POLICY_REPAIR_HOLDOUT.json"]]
            rows[-1]["legacy_runtime_boundary"] = "Historical helper expects the frozen legacy v27 binary and explicit diagnostic damage/source controls. It is not imported as an installed4.5 implementation; any CPC8 port needs its own measured trajectory."
    mbp_prefix = "MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS/24_CONTEXTUAL_CAUSAL_MECHANISM/"
    add_row(rows, "MBP4_CONTEXTUAL_REWRITE", "B100→101 and delta+1→0 arise under a local active-neighbor/comparator/clock configuration; tested action/environment cuts did not establish necessary exterior causation.", "Main relative131→132, absolute163→164 fromT32; zero post-T0 host writes; contextual causal cut24 diagnostic trajectories.", [member("MBP4", mbp_prefix + name) for name in ["RUN_SUMMARY.json", "TELEMETRY/INTACT_REPLAY_AND_GATE.json", "TELEMETRY/ACTION_ENVIRONMENT_INTERVENTIONS.json", "TELEMETRY/LOCAL_INTERVENTIONS_AND_RESCUE.json"]], "Local clock edits/rescues are diagnostic interventions; no claim of acquired native clock control. Failed shell rescue preserves ambiguity about wider/prior context.", "Do not require an expected exterior return when a local/contextual mechanism can enable writing; test exact field and presence dependence.", "late formed-action interventions, environmental cuts, comparator/active-neighbor/clock interventions, sham, rescue, frozen translations")

    physics_refs = [member("FISICA_UNI1", name, role="later_documentary_reduction_not_new_experiment") for name in ["CURRENT_DEE_INTERNAL_PHYSICS.md", "EXACT_MISSING_EDGES.md", "MISSING_EDGE_REASSESSMENT.md", "SCIENTIFIC_GENEALOGY.md", "SCIENTIFIC_SUPERSESSION_GRAPH.json", "F_DEE_CANONICAL.md"]]
    add_row(rows, "FISICA_UNI1_LATER_REDUCTION", "A later directed reduction connects causal geometry, observer equivalence, history-conditioned futures, domain-specific compression and mathematical reversible sectors.", "Documentary cross-sector synthesis with named primary mechanisms; no new CPC8 trajectory or external-universe measurement.", physics_refs, "A summary of Moore-26 access is not by itself a proof of final per-tick RAW radius1: composed update/reducer/DEMUX dependencies and wrapping must be checked in the actual kernel/domain.", "Choose state variables and counterfactual panels from the measured native mechanism rather than force an external anatomical or scalar category.", "Return to primary code/telemetry when a synthesis conflicts with a contract or later measured continuation.")
    rows[-1]["state"] = historical_states(True)
    corpus_index = json_member("FISICA_UNI1", "CORPUS_MASTER_INDEX.json")
    index_ref = member("FISICA_UNI1", "CORPUS_MASTER_INDEX.json", role="file_metadata_index_not_full_50073_contents_read")
    ARCHIVES["FISICA_UNI1"]["index_recovery"] = {"origin": index_ref, "indexed_file_records": len(corpus_index["files"]), "inspection": "metadata keys and targeted filenames only", "later_gate_or_conversation_filename_matches": sum(any(term in row["filename"].lower() for term in ("final_gate", "meta_rosetta", "conversa", "chatgpt", "closure_test")) for row in corpus_index["files"])}

    # Extra compact index/primary references for mechanisms not collapsed into a
    # new row; archive presence is not claimed as full linear content reading.
    for sid, names in {
        "ING01": ["DEE_NATIVE_RESET_REPLENISHMENT.json", "DEE_REUSABLE_FEEDBACK_LOOP.json", "FINAL_FRONTIER.md"],
        "ING02": ["ING02_DISTRIBUTED_MEMORY.json", "ING02_FAILURE_OBSTRUCTION_MAP.json", "ING02_FINAL_FRONTIER.md"],
        "PROC01": ["PROCESOS_01/MASTER_INDEX/README.md"],
    }.items():
        for name in names:
            member(sid, name, role="directed_index_or_mechanism_scope")
    for sid in ("ING03", "ING04"):
        archive = OPEN[sid]
        names = archive.namelist()
        indices = [name for name in names if name.lower().endswith((".md", ".json")) and any(term in name.lower() for term in ("master_index", "scientific_report", "claim_ledger", "final_frontier"))]
        ARCHIVES[sid]["targeted_indices_located"] = indices[:12]
        ARCHIVES[sid]["read_scope"] = "CENTRAL_DIRECTORY; NO_NEW_PHYSICAL_REPRODUCTION"
        for name in indices[:2]:
            member(sid, name, role="inventory_index_not_full_campaign_read")

    cpc8_links_path = RUN / "genealogia/CPC8_RESULT_LINKS.json"
    links = json.loads(cpc8_links_path.read_text(encoding="utf-8-sig")) if cpc8_links_path.exists() else {}
    for row in rows:
        link = links.get(row["id"])
        if link:
            required = ("result", "sha256", "state", "scope")
            assert all(key in link for key in required)
            path = RUN / link["result"]
            assert path.is_file() and file_sha(path) == link["sha256"]
            row["CPC8_result_link"] = link
            row["state"]["CPC8_state"] = link["state"]
            row["state"]["reproduced_in_CPC8"] = link.get("reproduced", False)
            row["state"]["adapted_in_CPC8"] = link.get("adapted", False)
            row["state"]["integrated_in_CPC8_MAIN"] = link.get("integrated_MAIN", False)

    conversations = json.loads((RUN / "genealogia/conversaciones/LECTURAS_ACCESIBLES.json").read_text(encoding="utf-8"))
    conversation_scope = {
        "file": "genealogia/conversaciones/LECTURAS_ACCESIBLES.json",
        "sha256": file_sha(RUN / "genealogia/conversaciones/LECTURAS_ACCESIBLES.json"),
        "thread_count": len(conversations["threads"]),
        "returned_turns": sum(len(thread["turns"]) for thread in conversations["threads"]),
        "all_have_older_unread_pages": all(thread["page"]["hasMore"] for thread in conversations["threads"]),
        "truncated_items": sum(bool(item.get("truncated")) + sum(bool(part.get("truncated")) for part in item.get("content", [])) for thread in conversations["threads"] for turn in thread["turns"] for item in turn.get("items", [])),
        "full_conversation_read_claim": False,
        "role": "Objectives, hypotheses and interpretation history; not substitutes for source trajectories.",
    }
    map_out = {
        "schema": "CPC8.accumulated_genealogy.v1", "kind": "DIRECTED_ARCHIVAL_AUDIT_NOT_NATIVE_EXECUTION",
        "source_authority": "Code and states -> controls/telemetry -> contracts -> synthesis/conversations",
        "original_budget_reset_by_this_audit": False, "native_experiments_executed_by_this_audit": 0,
        "archives": list(ARCHIVES.values()), "rows": rows,
        "historical_CPC7_map": member("CPC7", "CPC7/revision/MAPA_CPC1_A_6.json"),
        "source_availability": "CP01/CP02 are selected genealogy inside canonical CPC3, not missing independent ZIPs.",
        "status_update_contract": "Optional genealogia/CPC8_RESULT_LINKS.json maps row ID to result/sha256/state/scope plus reproduced/adapted/integrated_MAIN flags. Only existing hashed new evidence can update CPC8 status.",
        "conversation_access": conversation_scope,
        "counting": "Rows are linked mechanisms and software/documentary entries, not independent cases, individuals, acquired meanings or cognitive successes.",
    }
    save("genealogia/MAPA_CPC1_A_7.json", map_out)
    capability_matrix = {
        "schema": "CPC8.accumulated_capability_matrix.v1", "source_map": "genealogia/MAPA_CPC1_A_7.json",
        "capabilities": rows, "instrument45_registry": capabilities45,
        "instrument_registry_evidence_namespace": "Original PRODUCT45 archive, prefix DEE_thinking_4_5_0/. Embedded relative references retain that namespace, not the CPC8 run root.",
        "instrument_registry_scope": "The embedded23 registry entries are instrument coverage, not23 independent new CPC8 capabilities. The original catalogue/state labels are retained with source provenance.",
        "source_PRODUCT45_matrix": product_refs[0],
        "status_counts": dict(Counter(row["state"]["CPC8_state"] for row in rows)),
    }
    save("genealogia/MATRIZ_CAPACIDADES_ACUMULADAS.json", capability_matrix)

    pendings = [
        ("P01", "Accumulated semantic diversity", "CPC5/CPC7 preserve opaque directional correspondences; NSM acquisition is not implied by those slots.", ["CPC5_CAPACITY65", "CPC5_LONGITUDINAL65", "CPC7_NSM65_SCOPE"], "Function before name -> physical pairing -> reserved varied referents/context -> retention/use; fixed codec/decoder across opposite histories."),
        ("P02", "Experience-selected relevance", "Fixed guards, declared M1/M2 protocols and learned directional pulse are distinct; no general consequence-selected attention was established.", ["CPC4_REGULATION_ABCD", "CPC7_SELECTIVE_REVISION_M1_M2", "PRODUCT45_PORT_VALIDATION"], "Histories change useful current while evaluation signals/readout remain matched; show physical consequence path and new use without host policy correction."),
        ("P03", "Renewable access during new acquisition", "ING01 L2 replenishment and L3 finite adaptation were separate; ING02 stores relative memory but traffic can corrupt reader access.", ["ING01_R04_R14", "ING02_RELATIVE", "CPC6_RETENTION_CAUSAL"], "Track support, readout, receipts, phases, residuals and function separately; old relation must be used after new acquisition without re-teaching."),
        ("P04", "Learned questions and interlocutors", "CPC7 has a state-conditioned question on prepared routes; T117 remote request was scheduled, not native initiative.", ["CPC7_PREPARED_DISCREPANCY_REQUEST", "CPC6_TWO_FORMS"], "Keep fixed opportunities but vary experience and usefulness; freeze worlds where different sources are needed; no auditor routing by knowledge table."),
        ("P05", "Role-preserving semantic composition", "CPC7 product preserves X/Y/Z locally, while the sign readout loses branchX; arbitrary syntax and new referents remain untested.", ["CPC7_DIRECTIONAL_COMPOSITION_AND_POST_NAME", "CPC5_ORDER_AND_DIALOGUE"], "Teach components separately, reserve a functional combination/role swap, inspect native result rather than concatenate renderer labels."),
        ("P06", "Communication among full compounds", "CPC7 1/2/4 specialists multiply resources and do not establish cooperation of complete integrated compounds.", ["CPC6_ARCHITECTURES", "CPC7_U0_CONTINUITY", "CPC4_AB"], "Same-Runtime source->carrier->receiver->consequence with receptor-history and same-resource route/message controls."),
        ("P07", "Finite learned redundancy versus repair autonomy", "CORE17 later closure already demonstrates carrier-supported repair from a trained redundant copy; local self-regeneration without source remains open.", ["CORE17_COMPRESSED_OPERATOR_AND_REPAIR"], "Preserve source/cost/mode; test copied history, wrong direction, source absent and route cut separately from fresh autonomous learning."),
        ("P08", "Hidden knowledge versus physical convergence", "A scalar or unavailable reader can hide a distinction; complete-state convergence can really destroy its recoverability.", ["CORE16_OBSERVER_INFORMATION", "CPC6_RETENTION_CAUSAL", "PROC02_PREEXISTING_INTERFACE"], "Same common probe in forks; equalize/ablate candidate support; retain complete-state identity and context coverage."),
        ("P09", "New retained history from a new native contingency", "ING06 converged on history->post-host dynamics->reorganized existing opportunities; missing edge is new unpreloaded contingency->new retained history.", ["ING06_POST_HOST_OPPORTUNITIES", "ING05_HISTORY_FACTORIAL"], "Require a new physical consequence and later function, not only evolving RAW or new diagnostic reachability."),
        ("P10", "Later thermal/Rosetta source recovery", "PROC03 source is an uninformative discovery cut with holdout untouched; a visible conversation claims later gate tests.", ["PROC03_EXCHANGE_DISCOVERY"], "Recover later primary artifact/lock/data before promotion; conversation alone cannot override archived primary results."),
        ("P11", "Post-revision retention of named use", "CPC7 sign measured142 was not re-queried after L03 revision402;14-bank retention and named-response retention are different questions.", ["CPC7_U0_CONTINUITY", "CPC7_DIRECTIONAL_COMPOSITION_AND_POST_NAME"], "Query the acquired sign later on the same live MAIN and record admittance, output and query backaction; diagnose separately if port occupied."),
        ("P12", "Causal gate source versus expected return", "MBP4 tested exterior products were not shown necessary for the131->132 write; local presence/clock/comparator mattered.", ["MBP4_CONTEXTUAL_REWRITE"], "Use late formed-product cuts and exact local-context controls; do not identify a missing T0 input with a late consequence cut."),
    ]
    save("genealogia/PENDIENTES_RECUPERADOS.json", {"schema": "CPC8.recovered_questions.v1", "scope": "Recovered method-local questions, not claimed new executions or universal impossibilities", "entries": [{"id": pid, "question": title, "source_boundary": boundary, "source_rows": ids, "decisive_test": test, "CPC8_state": "NOT_EXECUTED_BY_THIS_AUDIT; consult parent experiment evidence"} for pid, title, boundary, ids, test in pendings]})
    inventory = {
        "schema": "CPC8.directed_source_inventory.v1", "archives": list(ARCHIVES.values()),
        "selected_members": list(SELECTED.values()), "conversation_access": conversation_scope,
        "selected_members_total": len(SELECTED),
        "unique_included_files": len({row["copied_as"] for row in SELECTED.values() if row["copied_as"]}),
        "selected_member_bytes": sum(row["bytes"] for row in SELECTED.values()),
        "full_linear_corpus_read": False, "new_native_runs": 0,
        "documentary_scope": "Existing CPC7 JSON text extracts were inspected as selected text. Original Word documents were not newly rendered or claimed read in full.",
        "unread_or_not_reexecuted": ["Unselected archive members", "Older pages of the four selected conversations", "Unresolved content-reference tokens and attachment contents", "Historical runners not executed by this audit", "Original Word chapters not re-extracted in this audit"],
        "incidents": INCIDENTS,
    }
    save("genealogia/INVENTARIO_FUENTES.json", inventory)
    for archive in OPEN.values():
        archive.close()
    outputs = ["genealogia/MAPA_CPC1_A_7.json", "genealogia/MATRIZ_CAPACIDADES_ACUMULADAS.json", "genealogia/INVENTARIO_FUENTES.json", "genealogia/PENDIENTES_RECUPERADOS.json", "revision/ANALISIS_TRANSVERSAL.md", "revision/INTERPRETACIONES_ACTUALIZADAS.md"]
    for ref in SELECTED.values():
        if ref["copied_as"]:
            assert file_sha(RUN / ref["copied_as"]) == ref["member_sha256"]
    for ref in ARCHIVES.values():
        assert file_sha(BASE / ref["source_path_relative_to_documentation"]) == ref["sha256"]
    assert len(rows) == len({row["id"] for row in rows})
    assert not any(row["state"]["integrated_in_CPC8_MAIN"] and "CPC8_result_link" not in row for row in rows)
    save("genealogia/VALIDACION_AUDITORIA.json", {
        "schema": "CPC8.directed_audit.verification.v1", "status": "VERIFIED",
        "scope": "Metadata, selected byte identities and original archive preservation; zero native simulations by this audit",
        "archives_rehashed_unchanged": len(ARCHIVES), "selected_members_CRC_checked_when_read": len(SELECTED),
        "selected_copies_SHA_checked": inventory["unique_included_files"], "registry_rows": len(rows),
        "new_native_runs_by_this_audit": 0, "CPC8_integration_attributed_without_new_evidence": False,
        "conversations": conversation_scope,
        "outputs": [{"path": name, "bytes": (RUN / name).stat().st_size, "sha256": file_sha(RUN / name)} for name in outputs if (RUN / name).is_file()],
    })
    print(json.dumps({"status": "DIRECTED_SOURCE_AUDIT_SAVED", "archives": len(ARCHIVES), "mechanism_rows": len(rows), "selected_members": len(SELECTED), "unique_source_copies": inventory["unique_included_files"], "new_native_experiments": 0, "conversation_turns_returned": conversation_scope["returned_turns"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
