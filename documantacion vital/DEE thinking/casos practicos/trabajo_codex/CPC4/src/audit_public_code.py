"""Read-only static audit of the CPC4 public implementation; no DEE import."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("src/channel.py", "src/channel_dual.py", "src/channel_discovery.py",
         "src/phase_language.py", "src/app_worker.py", "src/observers.py",
         "demostracion.py", "ejecutar.py")


def main():
    sources = {}
    for name in FILES:
        data = (ROOT / name).read_bytes()
        sources[name] = {"sha256": hashlib.sha256(data).hexdigest(),
                         "line_count": len(data.decode("utf-8").splitlines())}
    value = {
        "audit_type": "STATIC_READ_ONLY_SOURCE_REVIEW",
        "native_jobs_executed_for_this_audit": 0,
        "source_code_modified_by_audit": False,
        "files_reviewed": sources,
        "findings": [
            {"topic": "Hidden answer lookup", "observation": "Not found in the reviewed response path. Query uses current Native RAW via observe and the same load21/direction decoder for both forms and histories.",
             "locations": ["src/phase_language.py:74", "src/phase_language.py:141", "src/app_worker.py:167"],
             "scope": "Source inspection, not a universal proof about the binary or every possible application caller."},
            {"topic": "A to B communication", "observation": "The host schedules A acquisition/query and B history/common queries. No read-A then submit-A-value-to-B bridge is present. A physical emission traverses the prepared geometry; B contact and subsequent common query are native encounters.",
             "locations": ["src/channel_dual.py:68", "src/channel_dual.py:88", "src/channel.py:240", "src/channel.py:321"],
             "scope": "Selective edits and environmental control protocols remain separately declared; source inspection does not replace saved causal contrasts."},
            {"topic": "RAW edits and clocks", "observation": "Explicit RAW removals/direction changes use complete diagnostic_fork. The original parent RAW/clocks and child clocks/receipts are checked. No direct clock reset was found. FULL operational paths do not call these edits.",
             "locations": ["src/channel.py:344", "src/channel.py:367", "src/channel_dual.py:99", "src/phase_language.py:90", "src/app_worker.py:210"],
             "scope": "Diagnostic campaign variables named world are rebound to the child; this is a counterfactual continuation, not an intervention silently merged back into the untouched parent MAIN."},
            {"topic": "Prepared vs learned environmental action", "observation": "Resources and U/V events are external fixed experience protocols. future_context selects the environmental event independently of the measured A/B output. Reference actions are explicit diagnostic/external fixed-policy submissions, not native learned outputs.",
             "locations": ["src/channel_dual.py:93", "src/channel_dual.py:124", "src/channel_dual.py:128", "src/channel_dual.py:133"],
             "scope": "The finite score is an external evaluator, never a teacher or feedback scalar sent to DEE."},
            {"topic": "External lexical sensor", "observation": "Actual current RAW at a projected prepared-resource path determines a fixed external presence/absence report; the same report is broadcast to both lexical regions. The query does not consult that past report, a class table or a case/history label.",
             "locations": ["src/phase_language.py:47", "src/phase_language.py:74", "src/phase_language.py:117", "src/channel.py:112"],
             "scope": "This is EXTERNAL_TRANSDUCTION of a finite expected-packet observation window, not native detection of arbitrary absence, certified universal resource lineage or unrestricted NSM semantics."},
            {"topic": "Persistence and preparation", "observation": "Only create explicitly prepares the empty Research recipe. Load restores a candidate snapshot, validates physical time, interfaces, dimension, neutral metadata and no pending inputs before replacing MAIN. Descriptor/validation helpers do not instantiate another Runtime.",
             "locations": ["src/app_worker.py:51", "src/app_worker.py:118", "src/app_worker.py:245", "src/app_worker.py:258", "src/channel.py:279", "src/channel.py:301"],
             "scope": "The finite UI intentionally rejects states outside its declared stage/queue domain; arbitrary runtime snapshots are not promised as application sessions."},
            {"topic": "Observation coverage", "observation": "Observers retain integer RAW/clocks, activity and inactive/orphan context; O2 marks truncation, O3 marks current compatibility rather than parentage, and O4 is toroidal graph connectivity/rays rather than persistent homology. UI verifies passive RAW/clock/tick invariance.",
             "locations": ["src/observers.py:28", "src/observers.py:55", "src/observers.py:93", "src/observers.py:136", "src/observers.py:155", "src/app_worker.py:190"],
             "scope": "Sparse/limited captures and ballistic hypotheses do not certify whole-world genealogy, causal necessity or native perception."},
            {"topic": "Controller and restart", "observation": "One owned worker persists through commands; controller parses/renders and explicitly supervises its owned process. Creates are rejected when MAIN exists. Diagnostic children do not return to MAIN.",
             "locations": ["demostracion.py:38", "demostracion.py:78", "src/app_worker.py:118", "src/app_worker.py:210"],
             "scope": "Explicit cargar may replace MAIN with another validated full snapshot; this is visible restoration, not hidden individual continuity across unrelated snapshots."},
        ],
        "adversarial_guard_gap_not_executed": {
            "severity": "INSTRUMENTATION_RISK_SOURCE_ONLY",
            "locations": ["src/app_worker.py:51", "src/phase_language.py:123", "src/phase_language.py:146"],
            "description": "The validator checks physical tick/stage and pending receipts but does not explicitly reject a paused Runtime. After run_until, teaching/query methods do not assert the actual requested boundary was reached. If a valid paused snapshot is accepted by the underlying Runtime, a result may carry requested emission_tick while physical_output.tick exposes an earlier actual tick; the scheduled receipt remains non-applied and read_word validity is false.",
            "status": "NO_ADVERSARIAL_NATIVE_RUN_PERFORMED; runtime pause semantics not revalidated in this audit",
            "scope": "No observed canonical result is invalidated by this static concern. Do not claim the UI supports arbitrary paused session snapshots without a guard or a dedicated test.",
        },
        "not_audited_here": ["New M2 inverse diagnostic implementation and its later results", "Binary implementation beyond the separately preserved product tests", "Every possible custom Research preparation"],
        "scientific_boundary": "No global success/failure or cognition verdict. This artifact records software modalities, visible interventions and finite instrumentation coverage only.",
    }
    output = ROOT / "resultados/AUDIT_SUMMARY.json"
    output.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "reviewed_files": len(sources), "native_jobs": 0}))


if __name__ == "__main__":
    main()
