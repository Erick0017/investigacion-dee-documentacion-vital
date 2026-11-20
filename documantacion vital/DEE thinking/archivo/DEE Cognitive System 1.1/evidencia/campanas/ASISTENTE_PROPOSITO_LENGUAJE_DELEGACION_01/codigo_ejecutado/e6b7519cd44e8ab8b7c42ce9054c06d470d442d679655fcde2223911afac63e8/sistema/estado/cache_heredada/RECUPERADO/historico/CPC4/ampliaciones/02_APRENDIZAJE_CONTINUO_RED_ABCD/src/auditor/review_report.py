"""Read-only review of the root's draft against closed primary evidence."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]


def main():
    documents = {}
    for name in ('INFORME.md', 'LEEME.md'):
        raw = (ROOT / name).read_bytes()
        documents[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    reproduction = ROOT / 'resultados/reproduccion_limpia'
    findings = [
        {'severity': 'PENDING_CLOSE', 'location': 'INFORME.md / Procedencia, comprobaciones y cierre',
         'claim': 'Clean extraction/offline/other-process evidence is described as registered under resultados/reproduccion_limpia.',
         'observed_at_review': 'Directory present' if reproduction.exists() else 'Directory not yet present',
         'action': 'Before publication, link actual completed clean-reproduction primary results or explicitly retain this as pending. Do not count planned execution as measured.'},
        {'severity': 'PENDING_OWNER_INDEX', 'location': 'INFORME.md / Contexto, rutas alternativas e interferencia',
         'claim': 'New physical counterflow preparation is reported separately in network closure.',
         'observed_at_review': 'New native interference diagnostic/counterflow records are excluded from consolidated scientific count pending the owner final index.',
         'action': 'Reconcile final network owner index and neutralization provenance; do not adjust inherited failedFlat case.'},
        {'severity': 'OPTIONAL_SCOPE_CLARIFICATION', 'location': 'INFORME.md / Continuidad hacia nombres y usos nuevos',
         'claim': 'Direction source/payload17/23 variants are reserved.',
         'observed_at_review': 'LANGUAGE_SUMMARY explicitly identifies their source worlds as already observed; these are reserved new task parameters, not additional fresh worlds.',
         'action': 'Keep that distinction clear in final counts or one short clause; the current text does not explicitly claim they are new worlds.'}]
    report = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'READ_ONLY_DRAFT_REPORT_REVIEW_NO_NEW_SIMULATION',
        'documents_reviewed': documents,
        'scope_findings': findings,
        'claims_checked_without_detected_contradiction': [
            'I02two-relation retention versus reader availability, finite versus persistent source and rejected400query.',
            'ABCD finite mobile functional regions, native sameRuntime message paths and prepared relay rather than learned routing.',
            'C alternate B-only useful path retained; D unpaired/late-cut and sham contrasts kept distinct.',
            'Upstream matchedApplied exposure changes native expression but not A/Bdelta.',
            'Two task-relative F7/R3 form mappings plus two later dz mappings; neither four simultaneous accessible meanings nor full65NSM semantics claimed.',
            'Finite common naming and wordquery panels are explicitly separate; no unlimited renewal claim.',
            'LEEMElauncher/relative wheel path/localvenv and documented commands match the inspected public entry points by source reading.',
            'Hashes, binary container identity and physical/operative equality are not conflated.'],
        'no_mental_global_verdict_requested_or_generated': True,
        'scientific_count_reference': 'resultados/auditor/FINAL_COVERAGE_INDEX.json',
        'read_only_evidence_references': ['resultados/auditor/NATIVE_PREEMPTION_RECONSTRUCTION.json',
            'resultados/auditor/LANGUAGE_CONTINUITY_REVIEW.json',
            'resultados/auditor/NETWORK_V3_SCOPE_REVIEW.json',
            'resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_RECONSTRUCTION.json',
            'resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_BRANCH_RECONSTRUCTION.json',
            'resultados/continuidad/CONTINUITY_SUMMARY.json',
            'resultados/lenguaje/LANGUAGE_SUMMARY.json', 'resultados/red/NETWORK_MEASUREMENTS_SUMMARY.json'],
        'limits': 'Source review and saved results only. No additional simulation, malformed-state suite, independent replication or automatic scientific success classification.'}
    target = ROOT / 'resultados/auditor/REPORT_DRAFT_REVIEW.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'reviewed': list(documents), 'findings': len(findings)}))


if __name__ == '__main__': main()
