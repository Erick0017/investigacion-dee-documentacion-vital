"""Reconcile only the three product matrices from completed, immutable reports.

This is metadata consolidation, not a test runner or a scientific experiment.
It never imports the participant, edits source, or modifies a binary.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WHEEL_SHA = "09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c"
PYD_SHA = "17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d"
KERNEL_SHA = "fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
EVOLUTION_ONLY = "--evolution-only" in sys.argv


def resolve_evidence_path(relative):
    """Resolve the delivery alias locally, without copying the native reports.

    The archive publishes these files under validation/native-build, while the
    development tree keeps the original build output under candidate_final.
    Manifest references must always retain the delivered, not development, path.
    """
    path = ROOT / relative
    prefix = "validation/native-build/"
    if not path.is_file() and relative.startswith(prefix):
        path = ROOT / "candidate_final/validation" / relative[len(prefix):]
    return path


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def evidence(relative, selection=None, scope=None):
    path = resolve_evidence_path(relative)
    assert path.is_file(), relative
    result = {"path": relative, "sha256": digest(path)}
    if selection is not None:
        result["selection"] = selection
    if scope:
        result["scope"] = scope
    return result


def write(relative, value):
    # The only output targets are explicitly enumerated at the end of this file.
    (ROOT / relative).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def report(relative):
    value = read(relative)
    if "status" in value:
        assert value["status"] == "PASS", (relative, value["status"])
    else:
        assert type(value.get("total")) is int and value["total"] > 0
        assert value["pass_count"] == value["total"]
        assert all(case["status"] == "PASS" for case in value["cases"])
    return value


final_run = report("validation/FINAL_RUN_final6.json")
summary = report("validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json")
ports = report("validation/CPC_PORT_DIFF_final6.json")
revision = report("validation/FINITE_REVISION_DIFF_final6.json")
regulation = report("validation/EXPERIMENTAL_REGULATION_DIFF_final6.json")
remote = report("validation/remote_port45_final6_01/RESULT.json")
absence = report("validation/absence_port45_final6_01/RESULT.json")
legacy = report("validation/legacy_actual_cpc7_final6_01/RESULT.json")
api = read("validation/API_DIFF_final6.json")
inherited = read("validation/INHERITED_PYTHON_FINAL.json")
new = read("validation/installed_new_suites_final6_01/RESULT.json")
diff = read("validation/SOURCE_DIFF.json")
nsm = read("source/python/dee_thinking/data/NSM65_ALCANCE_4_5.json")
reg_provenance = read("source/python/dee_thinking/data/CPC5_REGULATION_PROVENANCE.json")

assert final_run["native_world_paths"] == 68
assert final_run["cross_version_cross_process_continuations"] == 4
assert inherited["tests_run"] == 61 and inherited["failures"] == inherited["errors"] == inherited["skipped"] == 0
assert new["tests_run"] == new["passed"] == 21 and new["failures"] == new["errors"] == new["skipped"] == 0
assert api["name_surface_preserved"] and not api["removed_public_symbols"] and not api["removed_public_class_attributes"]
assert diff["kernel_byte_identical"] and diff["kernel_sha256"] == KERNEL_SHA
assert not diff["modified_inherited_transition_sources"]
assert sum(item["changes"] for item in diff["modified_file_io_sources"]) == 4
assert all(item["non_io_sections_equal"] for item in diff["modified_file_io_sources"])
assert nsm["count"] == len(nsm["entries"]) == 65
assert all(item["DEE_thinking_4_5_0"]["new_NSM_semantic_experiment"] == "NOT_PERFORMED_IN_THIS_PRODUCT_PORT" for item in nsm["entries"])

wheels = list((ROOT / "candidate_final/wheel").glob("dee_thinking-4.5.0-*.whl"))
assert len(wheels) == 1
assert digest(wheels[0]) == WHEEL_SHA
with zipfile.ZipFile(wheels[0]) as archive:
    pyd = [name for name in archive.namelist() if name.endswith(".pyd")]
    assert len(pyd) == 1
    assert hashlib.sha256(archive.read(pyd[0])).hexdigest() == PYD_SHA

cpp_reports = [
    "validation/native-build/ctest.xml",
    "validation/native-build/ctest_directed.xml",
    "validation/native-build/ctest_final_affected.xml",
]
cpp_latest, cpp_initial_failures = {}, []
for index, relative in enumerate(cpp_reports):
    tree = ET.parse(resolve_evidence_path(relative))
    for case in tree.iter("testcase"):
        passed = case.find("failure") is None and case.find("error") is None and case.find("skipped") is None
        cpp_latest[case.attrib["name"]] = {"status": "PASS" if passed else "FAIL", "report": relative}
        if not passed:
            cpp_initial_failures.append({"test": case.attrib["name"], "report": relative})
assert len(cpp_latest) == 23 and all(row["status"] == "PASS" for row in cpp_latest.values())
assert len(list(ET.parse(resolve_evidence_path(cpp_reports[-1])).iter("testcase"))) == 9
remote_boundaries = sum(len(case["frame_comparisons"]) for case in remote["cases"])
assert len(remote["cases"]) == 3 and remote_boundaries == 38
absence_boundaries = sum(len(case["frames"]) for case in absence["cases"])
assert len(absence["cases"]) == 5 and absence_boundaries == 35
examples = []
for kind in ("integrado", "remoto", "repertorio"):
    relative = f"validation/examples_final6/{kind}/RESULT.json"
    assert read(relative)["exit_code"] == 0
    examples.append(evidence(relative))

identity = {
    "version": "4.5.0", "candidate": "final6", "kernel": "v27",
    "wheel_sha256": WHEEL_SHA, "native_pyd_sha256": PYD_SHA,
    "kernel_source_sha256": KERNEL_SHA,
}
counts = {
    "inherited_python_tests_passed": 61,
    "new_python_tests_passed": 21,
    "cpp_unique_tests_resolved_pass_across_build_stages": 23,
    "cpp_affected_tests_rerun_pass_final_candidate": 9,
    "differential_native_world_paths": 68,
    "differential_breakdown": {"neutral": 48, "CPC_ports": 10, "M1_M2": 6, "experimental_acquired_regulation": 4},
    "cross_version_cross_process_continuations": 4,
    "remote_trajectories": 3, "remote_boundary_comparisons": 38,
    "absence_trajectories": 5, "absence_boundary_comparisons": 35,
    "examples_executed": 3,
    "legacy_CPC7_continuation": {"from_tick": 204, "to_tick": 472, "status": "PASS"},
    "counting_rule": "Tests, trajectories, boundaries, examples and continuation proofs overlap in scope and are not independent cognitive replicas or new capabilities.",
}
common = [evidence("validation/INHERITED_PYTHON_FINAL.json"), evidence("validation/NEUTRAL_DIFF_final6.json"), evidence("validation/API_DIFF_final6.json")]
port_ref = "validation/CPC_PORT_DIFF_final6.json"
new_ref = "validation/installed_new_suites_final6_01/RESULT.json"

cap = read("MATRIZ_CAPACIDADES_CPC.json")
cap["phase"] = "EXECUTED_VALIDATION_CUT_FINAL6"
cap["artifact_identity"] = identity
cap["coverage_counts"] = counts
cap["publication_scope"] = "Technical functionality on the recorded finite domains; this matrix does not attest ZIP publication or a global cognitive verdict."
cap["evidence_interpretation"] = {
    "historical_references": "positive_reference/control/reserve identify historical mechanisms, not fresh experiments automatically credited to every 4.5 API.",
    "current_evidence": "evidence entries point to executed final6 reports and implementation/tests; technical_status separates test success from scientific breadth.",
    "stable_core": "Optional native repertoire/U0 preparation and protocol helpers plus their typed session/persistence facilitators. Direct Runtime remains empty until explicitly prepared.",
    "experimental": ["C15", "C19", "C23"],
    "documentary_only": ["C22"],
}
for entry in cap["entries"]:
    entry["technical_status"] = "PASS_RECORDED_TESTS"
    if entry["id"].startswith("F"):
        entry["final_status"] = "INHERITED_API_PRESERVED_REGRESSION_PASS"
        entry["publication_tier"] = "INHERITED_PUBLISHED_DOMAIN"
        entry["evidence"] = common
        entry["coverage_limit"] = "Inherited suite and neutral differential were executed, not the full historical scientific corpus. The original finite domain remains authoritative."
    else:
        entry["origin"] = "CPC3-CPC7 selected genealogy"
        entry["final_status"] = "IMPLEMENTED_AND_VERIFIED_BOUNDED"
        entry["publication_tier"] = "OPTIONAL_STABLE_BOUNDED"
        entry["evidence"] = [evidence(new_ref)]
        entry["coverage_limit"] = "Only the implemented recipe/protocol and the explicit recorded horizons are validated; no arbitrary-language, universal attention or indefinitely renewable individual is inferred."

entries = {entry["id"]: entry for entry in cap["entries"]}
by_case = {
    "C10": ["K65_PAIRED_Q9", "K65_NO_EVENT", "K65_UNPAIRED", "K65_RESERVED_Q13"],
    "C11": ["K65_LONGITUDINAL_32_33"],
    "C13": ["IR_P01_GUARDED_M1", "IR_C01_OFFPATH_GUARDS", "IR_C02_AUX_OFFPATH", "IR_R607_GUARDED_M1", "IR_MATCH_CURRENT"],
    "C14": ["IR_P01_GUARDED_M1", "IR_MATCH_CURRENT"],
    "C16": ["IR_P01_GUARDED_M1", "IR_C01_OFFPATH_GUARDS", "IR_C02_AUX_OFFPATH"],
    "C18": ["IR_P01_GUARDED_M1", "IR_R607_GUARDED_M1"],
    "C20": ["IR_P01_GUARDED_M1", "IR_R607_GUARDED_M1"],
}
available_cases = {case["case_id"] for case in ports["cases"]}
for key, ids in by_case.items():
    assert set(ids) <= available_cases
    entries[key]["evidence"].append(evidence(port_ref, {"case_ids": ids}, "Original 4.0 laboratory trajectory versus installed 4.5 implementation, full RAW/clocks and operative comparisons at declared boundaries."))

entries["C10"]["api_4_5"] = ["prepare_repertoire", "RepertoireOptions", "RepertoireSession.create", "RepertoireSession.acquire", "RepertoireSession.query"]
entries["C10"]["coverage_limit"] = "K=65 addressable opaque forms carry independently experienced choices within the tested directional family; this is not acquisition of the 65 NSM meanings. N31/K8, N67/K16 and N131/K65 are distinct physical preparations."
entries["C11"]["api_4_5"] = ["RepertoireSession.acquire_block", "RepertoireSession.query", "RepertoireSession.save_snapshot", "RepertoireSession.load_snapshot"]
entries["C11"]["coverage_limit"] = "The 32+33 block witness retains early relations under the documented finite query panels; repeated ticks/queries are not independent new learners."
entries["C12"]["api_4_5"] = ["revise_form", "RepertoireSession.revise(method='double_teacher')", "RepertoireSession.revise(method='symmetric_counterflow')"]
entries["C12"]["evidence"].append(evidence("validation/FINITE_REVISION_DIFF_final6.json", {"case_ids": [case["case_id"] for case in revision["cases"]]}))
entries["C12"]["coverage_limit"] = "Finite M1/M2 protocols add declared teacher dose or two zero-load counterflow experiences. They do not select their timing or relevance through reward feedback."
for key in ("C15", "C19"):
    entries[key]["final_status"] = "EXPERIMENTAL_BOUNDED"
    entries[key]["publication_tier"] = "EXPERIMENTAL_BOUNDED"
entries["C15"]["api_4_5"] = ["dee_thinking.experimental_absence.AbsenceSession"]
entries["C15"]["domain"] = "Separate N67 finite-aperture absence recipe; source load 7; 17 placements, 31 declared interfaces; horizon 35; reported reads at 19/24/29. Not silently fused with U0."
entries["C15"]["evidence"].append(evidence("source/tests/python/test_experimental_absence.py", "AbsenceTests: all five cases in final6 installed suite"))
entries["C15"]["evidence"].append(evidence("validation/absence_port45_final6_01/RESULT.json", {"case_ids": [case["case"]["id"] for case in absence["cases"]], "boundary_comparisons": absence_boundaries}))
entries["C15"]["coverage_limit"] = "Prepared physical aperture and learned source distinction in this finite recipe; a host timeout is not treated as a native absence response. No general detection of all missing events is claimed."
entries["C16"]["coverage_limit"] = "Six prepared semantic=4 interceptors are fixed physical regulation. Guarded and offpath preparations differ in geometry/resources; this is not evidence of adaptive attention."
entries["C17"]["name"] = "Calibración preparada de una fuente corporal"
entries["C17"]["final_status"] = "IMPLEMENTED_PREPARED_CALIBRATION"
entries["C17"]["api_4_5"] = ["IntegratedOptions.body_source_load"]
entries["C17"]["mechanism"] = "Prepared source parameter (including 0 versus 7); v27, not a host corrective callback, determines the later emission and occupancy."
entries["C17"]["modality"] = ["PREPARATION", "NATIVE_EVOLUTION", "PASSIVE_OBSERVATION"]
entries["C17"]["evidence"].append(evidence("source/include/dee_thinking/consolidated.hpp", "IntegratedOptions.body_source_load"))
entries["C17"]["coverage_limit"] = "The source parameter is exposed and exercised as a preparation/calibration. No new report establishes a feedback-acquired 0-to-7 policy, reinforced adaptation or general homeostasis. Historical source0/source7 observations retain their original scope."
entries["C18"]["coverage_limit"] = "U0 combines measured directional/order relations and native action/comparison in the declared circuit. A scalar cascade remains a separate family. This is not arbitrary symbolic syntax."
entries["C19"]["api_4_5"] = ["RemoteReaderSession.create", "RemoteReaderSession.acquire_sources", "RemoteReaderSession.query_first_form", "RemoteReaderSession.learn_second_form", "RemoteReaderSession.read_current_reader", "RemoteReaderSession.diagnostic_remote_cut", "RemoteReaderSession.save_snapshot", "RemoteReaderSession.load_snapshot"]
entries["C19"]["domain"] = "N67 remote-reader recipe, horizon 170; measured source/request and remote-use boundaries include T53/T90/T162. The finite prepared transport delay is not general instantaneous or indefinitely renewable access."
entries["C19"]["evidence"].append(evidence("validation/remote_port45_final6_01/RESULT.json", {"case_ids": [case["case_id"] for case in remote["cases"]], "boundary_comparisons": remote_boundaries}))
entries["C19"]["evidence"].append(evidence("source/tests/python/test_remote_reader_api.py", "RemoteReaderTests, five final6 installed tests"))
entries["C19"]["coverage_limit"] = "38 exact physical boundary comparisons across three trajectories plus five API tests; captured operation IDs/inert envelopes are explicitly distinguished from physical state. Historical T117 witnesses are not generalized to this T162 public route. Inner remote-protocol metadata validation is narrower than the consolidated facade's strict schema; arbitrary malformed session metadata is not advertised as supported."
entries["C20"]["coverage_limit"] = "Opaque cue/function association follows the native-use experience in the same U0 continuity. A fixed text-to-ID renderer is external; it neither stores the acquired correspondence nor resolves arbitrary vocabulary."
entries["C21"]["api_4_5"] = ["save_world_snapshot", "load_world_snapshot", "inspect_snapshot", "RepertoireSession.save_snapshot", "IntegratedSession.load_snapshot", "attach_preparation_descriptor"]
entries["C21"]["evidence"] += [evidence("validation/legacy_actual_cpc7_final6_01/RESULT.json"), evidence("validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json", "four cross-version/cross-process continuations"), evidence("validation/SOURCE_DIFF.json", "modified_file_io_sources: exactly four UTF-8 path conversions, non-I/O sections equal")]
entries["C21"]["coverage_limit"] = "Runtime v1/v2 physical support is retained; optional namespaced session descriptors and gzip storage preserve operational continuation. Explicit legacy attachment does not prepare a body. Other format/toolchain ABI compatibility is not implied."
entries["C22"]["final_status"] = "DOCUMENTARY_CATALOG_VERIFIED"
entries["C22"]["publication_tier"] = "DOCUMENTARY_RESOURCE"
entries["C22"]["modality"] = ["DOCUMENTARY_RESOURCE", "PASSIVE_OBSERVATION"]
entries["C22"]["evidence"] = [evidence("source/python/dee_thinking/data/NSM65_ALCANCE_4_5.json", {"registered_entries": 65, "new_NSM_semantic_experiments": 0}), evidence("source/python/dee_thinking/data/NSM65_CATALOGO_HISTORICO.json"), evidence(new_ref, "RemoteReaderTests.test_documentary_catalogue_is_not_training")]
entries["C22"]["coverage_limit"] = "65 documented interface entries, historical evidence kept separately. This product port performed zero new NSM semantic-acquisition experiments; opaque repertoire tests do not prove those 65 meanings."

new_reg = {
    "id": "C23", "name": "Regulación experimental mediante pulso direccional adquirido",
    "origin": "CPC5 learned-pulse genealogy",
    "origin_archive_sha256": reg_provenance["source_zip_sha256"],
    "source_member": "CPC5/src/network.py: regulate/learned_pulse; selected physical helpers listed in the installed provenance resource",
    "source_sha256": reg_provenance["sources"][0]["sha256"], "source_available": True,
    "state_4_0": "CPC5 laboratory realization, not a consolidated stable 4.0 public constructor",
    "posterior_contribution": "Self-contained optional experimental session; Python declares preparation/experiences, native C++ Runtime/v27 determines every transition.",
    "mechanism": reg_provenance["mechanism"], "domain": reg_provenance["domain"],
    "protocol_horizon": "T0 paired neutral experiences; acquired pulse at T3; occupied-residual contact around T292; later resource/function panels through T437",
    "resources": "N67 basic four-buffer storage is 9,624,416 bytes, before scratch/clones; finite fixed curriculum and physical communication routes declared at T0",
    "modality": reg_provenance["modalities"],
    "api_4_5": ["dee_thinking.experimental_regulation.CPC5RegulationSession", "create_cpc5_regulation", "run_until", "observe", "save_snapshot", "load_snapshot", "fork"],
    "positive_reference": ["REG_PAIRED"], "control": ["REG_UNPAIRED", "REG_OPPOSITE"],
    "reserve": ["REG_RESERVED_TRANSLATION"], "planned_status": "experimental public finite port",
    "final_status": "EXPERIMENTAL_BOUNDED", "publication_tier": "EXPERIMENTAL_BOUNDED",
    "technical_status": "PASS_RECORDED_TESTS",
    "evidence": [evidence("validation/EXPERIMENTAL_REGULATION_DIFF_final6.json", {"case_ids": [case["case_id"] for case in regulation["cases"]]}), evidence(new_ref, "ExperimentalRegulationTests: two executed tests"), evidence("source/python/dee_thinking/data/CPC5_REGULATION_PROVENANCE.json"), evidence("source/python/dee_thinking/experimental_regulation.py")],
    "design_and_learning_separation": reg_provenance["design_and_learning_separation"],
    "coverage_limit": "Paired history changes the pulse direction and the later physical contact/use within this finite N67 apparatus. It does not implement feedback-selected attention, universal homeostasis, an indefinitely reusable regulator or a full native C++ factory for the CPC5 geometry. No archived answer or output-selected callback participates in the response.",
}
cap["entries"] = [entry for entry in cap["entries"] if entry["id"] != "C23"] + [new_reg]
cap["entry_counts"] = {"inherited_families": 9, "new_or_experimental_or_documentary_entries": 14, "total_registry_entries": 23, "experimental_entries": 3, "documentary_entries": 1, "NSM_semantics_not_inferred": True}
cap["rule"] = "Capabilities are scoped software operations backed by the cited executed evidence; registry rows, historical cases, interfaces and meanings are distinct counts. No global cognitive verdict is generated."
assert len(cap["entries"]) == len({entry["id"] for entry in cap["entries"]}) == 23

sup = read("MATRIZ_SUPERSESIONES.json")
sup["decisions"] = [decision for decision in sup["decisions"] if decision["id"] in {f"S{number:02d}" for number in range(1, 8)}]
sup["phase"] = "EXECUTED_VALIDATION_CUT_FINAL6"
sup["artifact_identity"] = identity
sup_evidence = {
    "S01": [evidence("validation/API_DIFF_final6.json"), evidence("validation/INHERITED_PYTHON_FINAL.json")],
    "S02": [evidence(new_ref, "ConsolidatedApiTests.test_invalid_inputs_do_not_schedule_partial_blocks"), evidence("source/tests/python/test_consolidated_api.py")],
    "S03": [evidence(port_ref, {"case_ids": ["IR_P01_GUARDED_M1", "IR_C01_OFFPATH_GUARDS"]})],
    "S04": [evidence("validation/FINITE_REVISION_DIFF_final6.json"), evidence(new_ref, "ConsolidatedApiTests.test_finite_revision_both_methods_retains_other_relation")],
    "S05": [evidence(port_ref), evidence("validation/remote_port45_final6_01/RESULT.json"), evidence("validation/examples_final6/integrado/RESULT.json")],
    "S06": [evidence(new_ref, "ConsolidatedApiTests and AbsenceTests are separate profiles"), evidence("source/tests/python/test_experimental_absence.py")],
    "S07": [evidence("validation/legacy_actual_cpc7_final6_01/RESULT.json"), evidence("validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json", "four cross-process/version continuation proofs"), evidence(new_ref, "metadata, CRC, bounds, pending query and fork tests")],
}
for decision in sup["decisions"]:
    decision["status"] = "IMPLEMENTED_WITH_EXECUTED_EVIDENCE"
    decision["evidence"] = sup_evidence[decision["id"]]
    decision["historical_artifacts_modified"] = False
sup["decisions"] += [
    {"id": "S08", "old": "Native snapshot/trace paths interpreted through narrow Windows path strings", "decision": "Four explicit UTF-8 path conversions in file-I/O only", "status": "IMPLEMENTED_SOURCE_AND_DIFFERENTIAL_VERIFIED", "evidence": [evidence("validation/SOURCE_DIFF.json", "modified_file_io_sources"), evidence("validation/NEUTRAL_DIFF_final6.json")], "limit": "No changed microscopic transition sources; Unicode support is an interface correction, not changed physics."},
    {"id": "S09", "old": "Prepared source-load and fixed guards discussed alongside acquired regulation", "decision": "Retain separate claims: C17 source calibration; C16 six fixed guards; C23 experimental history-dependent pulse", "status": "SCOPE_SEPARATED", "evidence": [evidence("source/python/dee_thinking/data/CPC5_REGULATION_PROVENANCE.json"), evidence("validation/EXPERIMENTAL_REGULATION_DIFF_final6.json")], "limit": "No acquired reward-selected policy or generic homeostasis inferred from any of these three mechanisms."},
    {"id": "S10", "old": "Finite absence, remote-access and regulation apparatuses", "decision": "Publish complementary optional experimental bounded modules, not silently universalize them into the stable U0", "status": "EXPERIMENTAL_BOUNDED", "evidence": [evidence(new_ref), evidence("validation/absence_port45_final6_01/RESULT.json"), evidence("validation/remote_port45_final6_01/RESULT.json"), evidence("validation/EXPERIMENTAL_REGULATION_DIFF_final6.json")]},
    {"id": "S11", "old": "65 opaque physical signal forms and a 65-entry NSM inventory", "decision": "Preserve both but keep addressable repertoire separate from semantic mastery", "status": "DOCUMENTARY_AND_PHYSICAL_SCOPES_SEPARATED", "evidence": [evidence("source/python/dee_thinking/data/NSM65_ALCANCE_4_5.json"), evidence(port_ref)], "limit": "65 catalogued human forms do not entail 65 acquired meanings; no new NSM-semantic experiment was performed by this product port."},
]
sup["policy"] = "These supersessions apply only to new 4.5 implementation/interpretation. Historical source, results and packages remain original; no old public API was removed."

evolution = read("MATRIZ_4_0_A_4_5.json")
evolution["status"] = "EXECUTED_VALIDATION_CUT_FINAL6"
evolution["artifact_identity"] = identity
evolution["inherited"] = {
    "preserved": "Runtime, catalogue, composition, H1-H4/F1-F2, BasalWorld, observer/diagnostic APIs and Runtime v1/v2 support; all recorded public 4.0 names and class attributes retained.",
    "ownership": "Shared Runtime ownership and inert views are retained. New optional session attachment adds descriptors, not physical preparation; a direct Runtime does not autoload a body.",
    "snapshots": "The physical Runtime v1/v2 envelope is retained. Optional namespaced 4.5 session metadata and bounded gzip storage encode operational continuation, not a new microscopic state law. Legacy descriptor attachment is explicit on copies.",
    "interface_hardening": "New preparation/experience helpers preflight declared batches, keys, sizes, codecs and interface references before scheduling. No RAW/clock clearing to obtain admission; effective Scheduled/Applied/Rejected receipts remain native.",
    "compatibility_scope": "Name surface, executed use and behavior are checked. Binary C++ ABI across compilers/toolchains and untested parameter combinations are not promised.",
}
evolution["invariants"] = ["kernel_v27.cpp byte-identical: " + KERNEL_SHA, "No changes to packing/constants/clocks/reducer/branch ordering or inherited transition sources", "Direct Runtime has no cognitive autoload or compulsory preparation", "No recorded 4.0 public symbol/class attribute removed", "Participant state transitions remain C++ Runtime/v27, not cached reference outputs"]
evolution["new_layers"] = [
    {"layer": "Optional native core", "contents": "C++ repertoire/U0 constructors, typed descriptors, structural preflight, declared experience/query/revision helpers; Python bindings use the same library.", "tier": "STABLE_BOUNDED"},
    {"layer": "Session facilitation", "contents": "Installed repertoire/integrated sessions, finite protocols, actual receipts, physical/passive readout separation and deep fork.", "tier": "STABLE_BOUNDED"},
    {"layer": "Experimental public recipes", "contents": "Finite absence, remote reader and acquired-directional regulation modules; Python recipe preparation, native v27 evolution.", "tier": "EXPERIMENTAL_BOUNDED", "capability_ids": ["C15", "C19", "C23"]},
    {"layer": "Persistence and I/O", "contents": "Lossless bounded gzip/session storage, explicit legacy descriptors and four UTF-8 file-path conversions; no physical state rewriting on load."},
    {"layer": "Language resources", "contents": "Sourced documentary 65-entry catalogue with independent semantic-evidence scope; no automatic training from catalogue load.", "tier": "DOCUMENTARY_RESOURCE"},
]
evolution["coverage_counts"] = counts
evolution["comparisons"] = [
    {"id": "A", "description": "Installed 4.0 versus final6 4.5 under identical neutral preparations/inputs; exact physical and operative state, including adversarial/occupied cases.", "status": "PASS", "evidence": [evidence("validation/NEUTRAL_DIFF_final6.json"), evidence("validation/FINAL6_BACKEND_EQUIVALENCE.json"), evidence("validation/BASELINE_BACKEND_EQUIVALENCE.json")]},
    {"id": "B", "description": "Historical 4.0 physical CPC recipes versus installed public 4.5 implementation at declared boundaries, including adverse outputs; no archived answers used by participant.", "status": "PASS", "evidence": [evidence(port_ref), evidence("validation/FINITE_REVISION_DIFF_final6.json"), evidence("validation/EXPERIMENTAL_REGULATION_DIFF_final6.json"), evidence("validation/remote_port45_final6_01/RESULT.json"), evidence("validation/absence_port45_final6_01/RESULT.json")]},
    {"id": "C", "description": "Different fixed guards, offpath control, experience modes, names and regulation histories remain distinct physical preparations/continuations. Equal RAW across different resource configurations is not imposed.", "status": "MEASURED_SCOPED_COMPARISONS", "evidence": [evidence(port_ref, "IR guarded/offpath controls"), evidence("validation/EXPERIMENTAL_REGULATION_DIFF_final6.json")]},
    {"id": "D", "description": "Original CPC7 saved physical/operative state continued T204 to T472 without preparing a new body; four additional cross-version/cross-process continuation directions.", "status": "PASS", "evidence": [evidence("validation/legacy_actual_cpc7_final6_01/RESULT.json"), evidence("validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json")]},
]
evolution["technical_evidence"] = [evidence("validation/FINAL_RUN_final6.json"), evidence("validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json"), evidence("validation/INHERITED_PYTHON_FINAL.json"), evidence(new_ref), evidence("validation/API_DIFF_final6.json"), evidence("validation/SOURCE_DIFF.json")] + [evidence(path) for path in cpp_reports] + examples
evolution["cpp_stage_accounting"] = {"latest_status_by_test": cpp_latest, "earlier_failed_attempts_preserved": cpp_initial_failures, "scope": "23 unique test targets resolved PASS across build stages; nine affected targets rerun PASS in the final affected report. This does not rewrite earlier failed attempts as passes."}
evolution["retained_adverse_scope"] = ["K65_NO_EVENT has occupied/rejected requests, not numeric-zero answers", "K65_UNPAIRED can emit late valid responses; it is not uniformly a negative control", "Offpath revision may be outside the first fixed decoder window while a later reading remains usable", "Prepared source0/source7 calibration is not adaptive policy learning", "Remote operation-ID chronology/inert session metadata are distinguished explicitly from exact physical comparison"]
evolution["limitations"] = ["All functions have finite published geometries, channels, phases, resources and horizons; a common API does not fuse N34/N47/N67/N127/N131 individuals into one MAIN.", "Fixed guards, finite M1/M2 auxiliary experience protocols and the experimental acquired pulse are distinct mechanisms; none establishes general feedback-selected attention.", "The product port adds no proof of the 65 NSM meanings; documentary inventory and opaque repertoire counts remain separate.", "No new C++ binary ABI guarantee; normal users need the declared Windows x64 CPython 3.13/toolchain domain.", "Final archive CRC/manifests and clean-extraction publication are separately reported by the delivery validator, not inferred from these matrices."]

written = ["MATRIZ_4_0_A_4_5.json"]
if not EVOLUTION_ONLY:
    write("MATRIZ_CAPACIDADES_CPC.json", cap)
    write("MATRIZ_SUPERSESIONES.json", sup)
    written = ["MATRIZ_CAPACIDADES_CPC.json", "MATRIZ_SUPERSESIONES.json"] + written
write("MATRIZ_4_0_A_4_5.json", evolution)
print(json.dumps({"status": "MATRICES_RECONCILED", "written": written, "entries": len(cap["entries"]), "experimental": [entry["id"] for entry in cap["entries"] if entry["final_status"] == "EXPERIMENTAL_BOUNDED"], "counts": counts}, ensure_ascii=False))
