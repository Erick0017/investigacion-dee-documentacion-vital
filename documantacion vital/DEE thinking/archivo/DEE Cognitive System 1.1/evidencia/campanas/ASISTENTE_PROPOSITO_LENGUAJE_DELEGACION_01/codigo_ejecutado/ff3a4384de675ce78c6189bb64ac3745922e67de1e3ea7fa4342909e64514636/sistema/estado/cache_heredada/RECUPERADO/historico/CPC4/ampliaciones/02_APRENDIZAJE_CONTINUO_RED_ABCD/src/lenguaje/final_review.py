"""Read-only public-source/document follow-up; no Native imports or execution."""
import ast
from datetime import datetime,timezone
import json
from pathlib import Path
from .protocol import sha,put

ROOT=Path(__file__).resolve().parents[2]


def run():
    path=ROOT/"resultados/lenguaje/UI_REVIEW.json"
    archived=path.with_name("UI_REVIEW_INITIAL.json")
    if not archived.exists():archived.write_bytes(path.read_bytes())
    review=json.loads(path.read_text(encoding="utf-8"))
    worker=ROOT/"src/interactive_worker.py";tree=ast.parse(worker.read_text(encoding="utf-8"))
    safe=[n for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module=="lenguaje.session_safe"
          and any(x.name=="GroundedSession" for x in n.names)]
    unsafe=[n for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module=="lenguaje.session"
            and any(x.name=="GroundedSession" for x in n.names)]
    assert len(safe)==2 and not unsafe
    proof=ROOT/"resultados/technical/PUBLIC_UI_FINAL05/PUBLIC_UI_CHECKS.json"
    data=json.loads(proof.read_text(encoding="utf-8"));checks=data["checks"]
    assert "transactional_load" in checks and "completed_protocol_later_continuation" in checks
    config=ROOT/"resultados/regulacion/DUAL_CONFIRMATION/AB_AB/CONFIG.json"
    assert json.loads(config.read_text(encoding="utf-8"))["id"]=="AB_AB"
    files=("demostracion.py","src/interactive_worker.py","ejecutar.py","iniciar_cpc4.ps1","LEEME.md","INFORME.md",
           "src/test_public_ui.py","src/lenguaje/session_safe.py")
    review["final_read_only_followup"]={"utc":datetime.now(timezone.utc).isoformat(),
        "sources_and_documents_reviewed":{n:sha(ROOT/n) for n in files},
        "safe_GroundedSession_imports":{"attach_and_load":len(safe),"experimental_GS_imports_in_public_worker":len(unsafe)},
        "initial_findings_disposition":{
            "UI_LOAD_TRANSACTION":"Fixed in current source and tested by parent PUBLIC_UI_FINAL05; old MAIN/fingerprint preserved after invalid candidate.",
            "CURRICULUM_WRONG_PHASE_SIDE_EFFECT":"Fixed with actual431 guard before calling helper; parent's test verifies rejection without creating CURRICULO.",
            "PUBLIC_ENGINE_IDENTITY":"Fixed: worker startup runs campaign.identity and records official4/kernel27/PYD identity before commands.",
            "POST_DIRECTION_RESTORE":"Completed direction view is historical; Native current time may advance. Parent tested input1640, save/load and equal direct/restored future1643 without reviving stale GS."},
        "parent_technical_proof":{"path":proof.relative_to(ROOT).as_posix(),"sha256":sha(proof),"checks_recorded":len(checks),
                                  "source_test_inspected":"src/test_public_ui.py","new_scientific_samples_claimed":0},
        "document_review":{"functional_scope":"Consistent with measured local meanings and finite queries; no universal NSM, simultaneous four-meaning retention or N47 memory property attributed to N67.",
                           "regulation_command":"README now uses existing individual AB_AB/CONFIG.json, matching dual_sustained --case/--output. No root script changed by this reviewer.",
                           "report_clean_reproduction":"Described as a final-delivery check; parent must supply actual clean-extraction proof before publication.",
                           "public_startup":"Official included wheel/offline install, CPython3.13/x64, explicit new preparation and user-driven restore documented."},
        "still_to_check_before_publication":["Clean extraction and offline launcher/installation/use in a different location; parent owns this final check."],
        "native_jobs_or_learning_executed_in_this_followup":0,
        "review_scope":"Source and saved-proof inspection only; no modifications to root modules or scientific sources."}
    put(path,review)
    return review


if __name__=="__main__":run()
