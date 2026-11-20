"""Pure file-based follow-up of the CPC4 paused-UI audit; no Native import."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    audit_path = ROOT / "resultados/AUDIT_SUMMARY.json"
    initial_path = ROOT / "resultados/AUDIT_SUMMARY_INITIAL.json"
    if not initial_path.exists():
        initial_path.write_bytes(audit_path.read_bytes())
    audit = json.loads(initial_path.read_text(encoding="utf-8"))
    result_path = ROOT / "resultados/DEMO_PAUSE_AND_OBSERVERS/RESULTS.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    expected = {
        "src/app_worker.py": "399d3e5f924f7614087a6bb7711988a64fb7fb520d0c28b8144cfcff50932a0a",
        "demostracion.py": "98014c56638d170f0c30654a85530b72bbb9d91aa7c3b214b8e64452585aa0d1",
    }
    actual = {name: sha(ROOT / name) for name in expected}
    assert actual == expected, "Final UI source does not match the tested follow-up identity"
    assert result["count"] == 10 and result["verified"] and all(result["checks"].values())
    assert result["native_future_ticks_executed"] == 0 and result["new_scientific_samples"] == 0
    assert sha(ROOT / "src/phase_language.py") == audit["files_reviewed"]["src/phase_language.py"]["sha256"]
    followup = {
        "status": "RESOLVED_IN_PUBLIC_UI",
        "verification_type": "READ_ONLY_SOURCE_AND_EXISTING_TEST_EVIDENCE_REVIEW",
        "audit_initial_preserved": "resultados/AUDIT_SUMMARY_INITIAL.json",
        "initial_audit_sha256": sha(initial_path),
        "existing_technical_test": "resultados/DEMO_PAUSE_AND_OBSERVERS/RESULTS.json",
        "existing_test_sha256": sha(result_path),
        "checks": result["checks"],
        "final_UI_source_sha256": actual,
        "source_guards_reviewed": [
            {"source": "src/app_worker.py:59", "guard": "Reject paused candidate before replacing MAIN"},
            {"source": "src/app_worker.py:176", "guard": "Reject paused query before metadata or input submission"},
            {"source": "src/app_worker.py:189", "guard": "Verify actual input boundary reached before query"},
            {"source": "src/app_worker.py:195", "guard": "Verify actual emission boundary and physical_output tick before presentation"},
        ],
        "scope_remaining": "The frozen phase_language experiment helpers were not changed. Their published continuation domain remains an unpaused Runtime with the fixed declared boundaries. The UI guards do not broaden that helper domain or certify arbitrary paused snapshots as application sessions.",
        "audit_native_jobs": 0,
        "no_new_scientific_trajectories": True,
    }
    audit["adversarial_guard_gap_not_executed"]["initial_status_preserved"] = audit["adversarial_guard_gap_not_executed"]["status"]
    audit["adversarial_guard_gap_not_executed"]["status"] = "RESOLVED_IN_PUBLIC_UI_BY_EXPLICIT_PAUSE_AND_ACTUAL_TICK_GUARDS"
    audit["followup"] = followup
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "resultados/AUDIT_FOLLOWUP.json").write_text(json.dumps(followup, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": followup["status"], "existing_checks": 10, "audit_native_jobs": 0}))


if __name__ == "__main__":
    main()
