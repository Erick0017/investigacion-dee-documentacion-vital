"""Adversarial loader-only proof; no new scientific trajectories or evolution."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))


def main():
    p=argparse.ArgumentParser();p.add_argument("--child",action="store_true");a=p.parse_args()
    from lenguaje.protocol import put,sha,digest
    output=ROOT/"resultados/lenguaje/LOADER_HARDENING";output.mkdir(parents=True,exist_ok=True)
    if not a.child:
        import supervision
        job=supervision.run(ROOT,"language_loader_hardening",[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child"],120)
        if job["exit_code"]!=0:raise RuntimeError("Preserved loader-only technical error")
        return
    import dee_thinking as d
    from lenguaje.session import GroundedSession as Prior,KEY
    from lenguaje.session_safe import GroundedSession as Safe
    from red.session_v3 import NetworkSession
    native=sha(d._native.__file__)
    assert native=="20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066" and d.__version__=="4.0.0"
    checks={};ref=ROOT/"resultados/lenguaje/continuous02/MAIN_NEW_FORMS"
    for name in ("AFTER_NEW_EXPERIENCE1.deetsnap","AFTER_NEW_EXPERIENCE2.deetsnap","ACTUAL_READ1501.deetsnap","MAIN_FINAL1529.deetsnap"):
        good=Safe.load(ref/name);checks["normal_"+name]=good.tick in (1434,1462,1501,1529)
    candidate=Prior.load(ref/"AFTER_NEW_EXPERIENCE2.deetsnap");before=digest(candidate.world)
    candidate.world.submit("lex.L1.report.plus",11,1498)
    candidate.network.save(output/"DIAGNOSTIC_EXTRA_FUTURE_TEACHER.deetsnap")
    checks["future_input_scheduling_did_not_change_current_RAW_clocks"]=before==digest(candidate.world)
    prior=Prior.load(output/"DIAGNOSTIC_EXTRA_FUTURE_TEACHER.deetsnap")
    checks["prior_loader_gap_reproduced_without_evolving"]=any(str(x.status)=="scheduled" for x in prior.world.runtime.receipts)
    try:Safe.load(output/"DIAGNOSTIC_EXTRA_FUTURE_TEACHER.deetsnap");checks["new_loader_rejects_future_teacher"]=False
    except ValueError:checks["new_loader_rejects_future_teacher"]=True
    candidate=NetworkSession.load(ref/"AFTER_NEW_EXPERIENCE2.deetsnap")
    neutral=json.loads(candidate.world.runtime.snapshot_metadata(KEY));neutral["teaching_mode"]="unsupported"
    candidate.world.runtime.set_snapshot_metadata(KEY,json.dumps(neutral));candidate.save(output/"DIAGNOSTIC_BAD_MODE.deetsnap")
    try:Safe.load(output/"DIAGNOSTIC_BAD_MODE.deetsnap");checks["new_loader_rejects_bad_mode"]=False
    except ValueError:checks["new_loader_rejects_bad_mode"]=True
    assert all(checks.values()),checks
    put(output/"RESULTS.json",{"checks":checks,"all_technical_checks":True,"scientific_samples_added":0,
        "identity":{"version":d.__version__,"kernel":d.kernel_identity(),"module":d.__file__,"native_sha256":native,"python":sys.executable},
        "source_sha256":{n:sha(ROOT/n) for n in ("src/lenguaje/session.py","src/lenguaje/session_safe.py","src/lenguaje/validate_loader.py")},
        "scope":"No native advance in this test. Frozen32scientific trajectories were not repeated or modified."})
    print(json.dumps(checks))


if __name__=="__main__":main()
