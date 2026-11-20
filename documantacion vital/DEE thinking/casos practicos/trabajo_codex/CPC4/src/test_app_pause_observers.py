"""Final application-only pause guards and passive atlas integration checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--child",action="store_true");args=parser.parse_args()
    out=ROOT/"resultados/DEMO_PAUSE_AND_OBSERVERS"
    if not args.child:
        if out.exists():raise FileExistsError(out)
        put(out/"CONFIG.json",{"purpose":"Application-only real pause-state rejection and O1/O2/O4 passivity. No Native future evolution.",
                                "sources":{n:sha(ROOT/n) for n in ("demostracion.py","src/app_worker.py","src/language.py","src/observers.py","src/test_app_pause_observers.py")}})
        from supervise import run
        job=run(ROOT,"application_pause_and_observers",[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child"],90)
        assert job["exit_code"]==0
        return
    import dee_thinking as d
    from src.app_worker import Application,APP_KEY
    from src import channel
    app=Application(out/"OBSERVER")
    source=ROOT/"resultados/demo02/ANTES_DE_CONSULTAR200.deetsnap"
    app.load(source);main=app.world;before=channel.digest(main)
    first,second=app.observe(),app.observe()
    checks={"two_observations_no_native_advance":channel.digest(main)==before,
            "both_passivity_guards_true":first["passivity_RAW_clocks_tick_verified"] and second["passivity_RAW_clocks_tick_verified"],
            "same_current_multiscale_panel":first["atlas_O4"]==second["atlas_O4"],
            "actual_integer_clock_panel":all(type(x) is int for x in first["clock_panel"]["first16_integer_values"]),
            "coverage_budget_explicit":first["atlas_O4"]["truncated"] is False and first["O2_counts"]["sampled"]<=256,
            "four_graph_scales_current":set(first["atlas_O4"]["scales"])=={"1","2","4","8"}}
    candidate=d.OrganizationalWorld.load_snapshot(str(source));candidate.runtime.pause()
    assert candidate.runtime.paused and channel.digest(candidate)==before
    path=out/"ADVERSARIAL_PAUSED200.deetsnap";candidate.save_snapshot(str(path))
    try:app.load(path);checks["paused_snapshot_rejected_without_replacing_main"]=False
    except ValueError as error:checks["paused_snapshot_rejected_without_replacing_main"]=("pausado" in str(error) and app.world is main and not app.world.runtime.paused and channel.digest(main)==before)
    main.runtime.pause();old_receipts=[channel.receipt(main,r.id) for r in main.runtime.receipts];old_metadata=main.runtime.snapshot_metadata(APP_KEY)
    try:app.query("HAY");checks["paused_query_rejected_before_input_or_nominal_emission"]=False
    except ValueError as error:checks["paused_query_rejected_before_input_or_nominal_emission"]=("pausado" in str(error) and channel.digest(main)==before and [channel.receipt(main,r.id) for r in main.runtime.receipts]==old_receipts and main.runtime.snapshot_metadata(APP_KEY)==old_metadata)
    main.runtime.resume();checks["explicit_test_resume_preserves_physical_state"]=(not main.runtime.paused and channel.digest(main)==before)
    config=json.loads((out/"CONFIG.json").read_text());checks["source_unchanged"]=all(sha(ROOT/n)==v for n,v in config["sources"].items())
    result={"verified":all(checks.values()),"checks":checks,"count":len(checks),"atlas":first,
            "native_future_ticks_executed":0,"new_scientific_samples":0,"scope":"Technical paused state and actual passive fields; graph metrics are not PH or causal proof."}
    put(out/"RESULTS.json",result);assert result["verified"]
    print(json.dumps({"verified":True,"checks":len(checks)}))


if __name__=="__main__":main()
