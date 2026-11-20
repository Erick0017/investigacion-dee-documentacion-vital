"""Technical save/load and finite-domain checks, not new scientific samples."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from lenguaje.protocol import digest,put,sha


def check_error(operation):
    try: operation()
    except ValueError: return True
    return False


def child(mode,output):
    from lenguaje.session import GroundedSession,KEY
    from red.session_v3 import NetworkSession
    proof={};reference=ROOT/"resultados/lenguaje/continuous02/MAIN_NEW_FORMS"
    if mode=="first_process":
        language=GroundedSession.load(reference/"AFTER_NEW_EXPERIENCE1.deetsnap")
        proof["restored_actual1434"]=language.tick==1434
        before=digest(language.world);observations=[language.observe() for _ in range(3)]
        proof["passive_observation_preserves_RAW_clocks_tick"]=digest(language.world)==before
        lesson=language.teach_next();read=language.query_next_word("L1")
        language.save(output/"RESTORED_AFTER_FIRST_READ1501.deetsnap")
        proof["new_experience_after_restore_presented"]=lesson["sensor"]["profile"]==[0,1]
        proof["new_query_evolved_to1501"]=language.tick==1501 and read["readout"]["valid"]
        put(output/"FIRST_PROCESS.json",{"checks":proof,"lesson":lesson,"readout":read,"physical":digest(language.world)})
    elif mode=="second_process":
        language=GroundedSession.load(output/"RESTORED_AFTER_FIRST_READ1501.deetsnap")
        proof["other_process_restored1501"]=language.tick==1501
        read=language.query_next_word("L2");canonical=NetworkSession.load(reference/"MAIN_FINAL1529.deetsnap")
        proof["new_question_after_restore_used_native_future"]=language.tick==1529 and read["readout"]["valid"] and read["readout"]["class_sign"]==-1
        proof["full_RAW_clocks_tick_equal_direct_future"]=digest(language.world)==digest(canonical.world)
        language.save(output/"RESTORED_NEW_QUESTION_MAIN_FINAL1529.deetsnap")
        before=digest(language.world);proof["third_query_rejected_without_mutation"]=check_error(lambda:language.query_next_word("L1")) and digest(language.world)==before
        put(output/"SECOND_PROCESS.json",{"checks":proof,"readout":read,"physical":digest(language.world)})
    elif mode=="guards":
        language=GroundedSession.load(reference/"AFTER_NEW_EXPERIENCE2.deetsnap")
        before=digest(language.world);language.world.runtime.pause()
        proof["paused_query_rejected_before_mutation"]=check_error(lambda:language.query_next_word("L1")) and digest(language.world)==before
        language.network.save(output/"DIAGNOSTIC_PAUSED.deetsnap")
        proof["paused_snapshot_rejected_without_resume"]=check_error(lambda:GroundedSession.load(output/"DIAGNOSTIC_PAUSED.deetsnap"))
        for name,field,value in (("word_order","word_order",["L1","L1"]),("tick","tick",1463)):
            candidate=NetworkSession.load(reference/"AFTER_NEW_EXPERIENCE2.deetsnap")
            neutral=json.loads(candidate.world.runtime.snapshot_metadata(KEY));neutral[field]=value
            candidate.world.runtime.set_snapshot_metadata(KEY,json.dumps(neutral));path=output/("DIAGNOSTIC_BAD_"+name+".deetsnap")
            candidate.save(path);proof["invalid_"+name+"_rejected"]=check_error(lambda p=path:GroundedSession.load(p))
        put(output/"GUARDS.json",{"checks":proof,"modality":"TECHNICAL_DIAGNOSTIC_BRANCHES_ONLY"})
    else:raise ValueError("Unknown technical mode")
    assert all(proof.values()),proof
    print(json.dumps({"mode":mode,"checks":proof}));return proof


def main():
    p=argparse.ArgumentParser();p.add_argument("--child");p.add_argument("--output",type=Path);a=p.parse_args()
    output=a.output or ROOT/"resultados/lenguaje/TECHNICAL_CHECKS";output.mkdir(parents=True,exist_ok=True)
    if a.child:child(a.child,output);return
    import supervision
    modes=("first_process","second_process","guards");rows=[]
    for mode in modes:
        filename=output/{"first_process":"FIRST_PROCESS.json","second_process":"SECOND_PROCESS.json","guards":"GUARDS.json"}[mode]
        if not filename.exists():
            job=supervision.run(ROOT,"language_technical_"+mode,[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child",mode,"--output",str(output)],180)
            if job["exit_code"]!=0:raise RuntimeError("Preserved technical failure")
        data=json.loads(filename.read_text(encoding="utf-8"));rows.append({"mode":mode,"checks":data["checks"]})
    put(output/"TECHNICAL_SUMMARY.json",{"checks":rows,"all_technical_checks":all(all(x["checks"].values()) for x in rows),
        "scientific_samples_added":0,"source_sha256":{n:sha(ROOT/n) for n in ("src/lenguaje/protocol.py","src/lenguaje/session.py","src/lenguaje/validate.py")}})


if __name__=="__main__":main()
