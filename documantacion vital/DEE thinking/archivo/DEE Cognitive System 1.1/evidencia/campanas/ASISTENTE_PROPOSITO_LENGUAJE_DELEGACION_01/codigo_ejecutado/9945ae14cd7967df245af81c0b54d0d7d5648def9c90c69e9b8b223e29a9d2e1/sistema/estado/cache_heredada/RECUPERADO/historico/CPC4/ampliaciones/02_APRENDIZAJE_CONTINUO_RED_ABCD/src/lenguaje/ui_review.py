"""Final UI read-only review and passive loads; no native advance or teaching."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from lenguaje.protocol import put,sha,digest


def main():
    p=argparse.ArgumentParser();p.add_argument("--child",action="store_true");a=p.parse_args()
    output=ROOT/"resultados/lenguaje/UI_REVIEW.json"
    if not a.child:
        import supervision
        job=supervision.run(ROOT,"language_final_ui_passive_review",[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child"],120)
        if job["exit_code"]!=0:raise RuntimeError("Preserved passive UI-review error")
        return
    from lenguaje.session_safe import GroundedSession
    from lenguaje.directions import KEY as DIRECTION_KEY
    from red.session_v3 import NetworkSession
    references={"language1501":ROOT/"resultados/demo/CENTRAL_V3_01/RED_LENGUAJE_T1501.deetsnap",
                "directions1634":ROOT/"resultados/demo/DIRECCIONES_V3_03/RED_T1634.deetsnap"}
    proofs={}
    for name,path in references.items():
        view=GroundedSession.load(path) if name=="language1501" else NetworkSession.load(path)
        world=view.world;before=digest(world);current=view.observe();after=digest(world)
        proofs[name]={"checkpoint":path.relative_to(ROOT).as_posix(),"sha256":sha(path),"tick":world.runtime.current_tick,
                      "loader":"safeGroundedSession" if name=="language1501" else "NetworkSessionV3",
                      "passive_RAW_clocks_tick_unchanged":before==after,"physical":after,
                      "direction_metadata_present":bool(world.runtime.snapshot_metadata(DIRECTION_KEY))}
        assert before==after
        assert world.runtime.current_tick==(1501 if name=="language1501" else 1634)
    files={n:sha(ROOT/n) for n in ("src/interactive_worker.py","demostracion.py","src/lenguaje/session_safe.py","src/lenguaje/ui_review.py")}
    result={"review_mode":"READ_ONLY_CODE_AND_PASSIVE_NATIVE_LOADS","new_learning_or_native_advance":False,
        "source_hashes_at_passive_review":files,"proofs":proofs,
        "supported_semantics":["User seed chooses a toroidal translation, not an expected answer.",
            "New preparation is explicit; curriculum passes the same native object to the experience protocol.",
            "Language attaches inertly and teaches current physical F7/R3 classes, never metadata-case answers.",
            "SafeGroundedSession is imported for attach/load; after directions the archived old language view must not resume at stale1529.",
            "Direction snapshot1634 is loaded as NetworkSessionV3 and observed at its actual current state.",
            "Scheduled and Applied are distinguished; manual input has explicit modality and receipt.",
            "Native queries may consume state; supported windows are finite, not unlimited dialogue."],
        "findings_reported_to_root":[
            {"id":"UI_LOAD_TRANSACTION","severity":"P1","basis":"Code review of initial root worker: self.language cleared and self.session assigned before safe-loader completion.",
             "risk":"A rejected candidate snapshot can replace the live MAIN or drop the previous view.",
             "requested_fix":"Load into candidate local variables and commit all self fields only after full validation.","dynamic_adversarial_test":"NOT_RUN_HERE; parent owns final UI fix/test"},
            {"id":"CURRICULUM_WRONG_PHASE_SIDE_EFFECT","severity":"P2","basis":"continue_session freezes its output config before checking actual431; initial UI did not check current tick.",
             "risk":"Repeated wrong-phase curriculum may rewrite the session's configuration before rejecting, although native RAW is unchanged.",
             "requested_fix":"Validate exact actual431 and fresh output before invoking the helper.","dynamic_adversarial_test":"NOT_RUN_HERE"},
            {"id":"PUBLIC_ENGINE_IDENTITY","severity":"P2_SCOPE","basis":"Demo CLI accepts --python while initial worker has no local version/PYD assertion; campaign-level identity was verified separately.",
             "risk":"A manually selected different interpreter should not silently be presented as official4.",
             "requested_fix":"At worker startup validate version4.0.0/kernel27/officialPYD hash or explicitly reject another engine.","dynamic_adversarial_test":"NOT_RUN_HERE"}],
        "followup":"Root may amend UI only; frozen scientific sources and32measured trajectories remain unchanged."}
    put(output,result);print(json.dumps({"passive_loads_verified":True,"findings":len(result["findings_reported_to_root"])}))


if __name__=="__main__":main()
