"""Static regulated-profile UI review and saved-log inspection, no Native jobs."""
import ast
from datetime import datetime,timezone
import json
from pathlib import Path
from .protocol import put,sha

ROOT=Path(__file__).resolve().parents[2]


def run():
    worker=ROOT/"src/interactive_worker.py";source=worker.read_text(encoding="utf-8");tree=ast.parse(source)
    safe=[n for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module=="lenguaje.session_safe"
          and any(item.name=="GroundedSession" for item in n.names)]
    assert len(safe)==2
    sessions=[]
    for name in ("REGULATED_FINAL01","REGULATED_RESTORE02"):
        path=ROOT/"resultados/demo"/name/"DIALOGOS.jsonl"
        data=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        sessions.append({"session":name,"path":path.relative_to(ROOT).as_posix(),"sha256":sha(path),
                         "commands":len(data),"errors":[{"command":x["command"],"error":x["result"]["error"]} for x in data if "error" in x["result"]],
                         "actual_panel_boundaries":[x["result"]["panel"]["tick"] for x in data if "panel" in x["result"]],
                         "same_world_result":[x["result"]["same_world_object"] for x in data if "same_world_object" in x["result"]],
                         "restorations":sum(bool(x["result"].get("restored_not_reprepared")) for x in data)})
    files=("src/interactive_worker.py","demostracion.py","src/red/regulated_session.py","src/red/regulated_curriculum.py","LEEME.md")
    review_path=ROOT/"resultados/lenguaje/UI_REVIEW.json";review=json.loads(review_path.read_text(encoding="utf-8"))
    review["regulated_v6_read_only_followup"]={"utc":datetime.now(timezone.utc).isoformat(),
        "source_hashes":{n:sha(ROOT/n) for n in files},"safe_GS_imports_preserved":len(safe),
        "continuity_and_scope":[
            "nueva-regulada explicitly creates a separate N67 world, marks profilev6, and schedules a finite physical protocol atT0.",
            "The seed determines toroidal translation; C+/C- and normal/none/sham are declared external conditions, not a chosen response.",
            "Fixed zero-load counterflow is physically supplied in every declared normal episode; its subsequent encounter is native, not a host deletion or learned regulator.",
            "renovar-contexto passes the same existing session to continue_session. Its new resources and reports are explicitly scheduled external experiences.",
            "Utility/profile evaluation occurs after native evolution and is never used to choose an action or submit a solved output.",
            "v6 is excluded from both the v3 curriculum and the GroundedSession attach route. No language learned on v3 is transplanted or attributed to v6.",
            "The loader reconstructs the v6 physical recipe and validates at most one continued episode, offset500 and operative receipt channels/ticks before transactional commit.",
            "Rendering adds current actual bank records; a missing current fixed-port record is not asserted to be global function loss."],
        "domain_guard_review":{
            "initial_issue":"Original renew-contexto guard also admitted none/sham, while the second episode always supplied counterflow, confounding the change with a regulator change.",
            "current_source_restricts_initial_counterflow":"s.state['case'].get('neutralizer')!='counterflow'" in source,
            "documentation_note":"The valid renewal domain is initialCplus/normal at437 and one fixed nextCminus/counterflow episode. HELP/LEEME should name normal explicitly."},
        "saved_parent_demo_logs":sessions,
        "remaining_UI_test_to_consider":"Explicitly reject lenguaje and a second renovar-contexto on a v6 session while preserving its fingerprint; only source guards were reviewed here.",
        "reviewer_native_execution":0,"new_scientific_samples_claimed":0,
        "conclusion_scope":"No hidden semantic-answer selector found in the reviewed regulated UI path. This is not a proof of learned self-regulation or language/regulator integration."}
    put(review_path,review);return review


if __name__=="__main__":run()
