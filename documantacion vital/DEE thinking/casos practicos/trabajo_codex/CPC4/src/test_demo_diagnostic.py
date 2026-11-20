"""One explicit public diagnostic witness, without repeating acquisition.

A measured scientific172 snapshot receives ONLY inert neutral UI metadata.
That technical adapter is declared; RAW/clocks/queue/receipts are unchanged.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--child",action="store_true");args=parser.parse_args()
    out=ROOT/"resultados/DEMO_DIAGNOSTIC"
    if not args.child:
        if out.exists():raise FileExistsError(out)
        put(out/"CONFIG.json",{"purpose":"Technical public diagnostic operation at already-measured172; no new acquisition or independent science sample",
                                "sources":{n:sha(ROOT/n) for n in ("demostracion.py","src/app_worker.py","src/language.py","src/phase_language.py","src/demo_validation.py","src/test_demo_diagnostic.py")},
                                "adapter":"Inert UI phase/order/alias metadata only, after full Native snapshot load. No RAW/clocks/tick/queue/canal edit."})
        from supervise import run
        job=run(ROOT,"public_demo_diagnostic_at172",[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child"],180)
        assert job["exit_code"]==0
        return
    config=json.loads((out/"CONFIG.json").read_text())
    assert all(sha(ROOT/n)==v for n,v in config["sources"].items())
    import dee_thinking as d
    from src.app_worker import APP_KEY
    from src import channel
    from src.demo_validation import bounded
    source=ROOT/"resultados/confirmacion/MAIN_MINUS/LENGUAJE/AFTER_W1_EXPERIENCE.deetsnap"
    world=d.OrganizationalWorld.load_snapshot(str(source))
    before=channel.digest(world)
    old_receipts=[channel.receipt(world,r.id) for r in world.runtime.receipts]
    neutral={"version":1,"translation":[0,0,0],"stage":"FIRST_WORD_EXPERIENCE","word_order":["W1"],"aliases":{"hay":"W1","no":"W2"}}
    world.runtime.set_snapshot_metadata(APP_KEY,json.dumps(neutral))
    assert channel.digest(world)==before
    assert [channel.receipt(world,r.id) for r in world.runtime.receipts]==old_receipts
    bridge=out/"UI_VIEW_ONLY172.deetsnap";world.save_snapshot(str(bridge));del world
    events=out/"EVENTOS.txt"
    events.write_text('diagnóstico\nobservar\nguardar "'+(out/"MAIN_UNCHANGED172.deetsnap").as_posix()+'"\nsalir\n',encoding="utf-8")
    job=bounded("PUBLIC_DIAGNOSTIC",[sys.executable,"-I","-B",str(ROOT/"demostracion.py"),"--cargar",str(bridge),"--eventos",str(events),"--salida",str(out/"SESION")],out,out)
    rows=[json.loads(x) for x in (out/"SESION/TRANSCRIPCION.jsonl").read_text(encoding="utf-8").splitlines()]
    response=next(r["response"]["result"] for r in rows if r.get("command")=="diagnóstico")
    panels={r["mode"]:r["panel"] for r in response["counterfactuals"]}
    final=d.OrganizationalWorld.load_snapshot(str(out/"MAIN_UNCHANGED172.deetsnap"))
    checks={"metadata_adapter_preserves_physical_state":before["tick"]==172,
            "public_diagnostic_attributed_to_instrument":response["attribution"]=="INSTRUMENTO",
            "three_explicit_counterfactuals":set(panels)=={"reference","memory_cut","sham"},
            "reference_both_queries_available":all(q["available"] for q in panels["reference"]),
            "cut_W1_removes_first_access_not_second":not panels["memory_cut"][0]["available"] and panels["memory_cut"][1]["available"],
            "sham_both_queries_available":all(q["available"] for q in panels["sham"]),
            "parent_preserved_by_diagnostic":response["parent_unchanged"],
            "saved_main_still_identical_at172":channel.digest(final)==before,
            "saved_main_receipts_identical":old_receipts==[channel.receipt(final,r.id) for r in final.runtime.receipts],
            "source_unchanged":all(sha(ROOT/n)==v for n,v in config["sources"].items())}
    put(out/"RESULTS.json",{"verified":all(checks.values()),"checks":checks,"count":len(checks),"diagnostic":response,
                            "command":job,"adapter_source_sha256":sha(source),"bridge_sha256":sha(bridge),
                            "main_future_ticks_executed":0,"counterfactual_trajectories":3,"new_independent_scientific_samples":0})
    assert all(checks.values())
    print(json.dumps({"verified":True,"checks":len(checks),"main_tick":172}))


if __name__=="__main__":main()
