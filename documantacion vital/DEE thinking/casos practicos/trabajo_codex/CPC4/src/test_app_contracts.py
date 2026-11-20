"""Bounded loader/admission-negative checks; no new scientific trajectory."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put, sha


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--child",action="store_true"); args=parser.parse_args()
    output=ROOT/"resultados/DEMO_CONTRACTS"
    if not args.child:
        if output.exists(): raise FileExistsError(output)
        put(output/"CONFIG.json",{"purpose":"Technical application loading/grammar rejection checks; no Native future evolution",
                                  "sources":{name:sha(ROOT/name) for name in ("demostracion.py","src/app_worker.py","src/test_app_contracts.py")}})
        from supervise import run
        job=run(ROOT,"demonstration_contracts",[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--child"],90)
        assert job["exit_code"]==0
        return
    import dee_thinking as d
    from src.app_worker import Application, APP_KEY
    from src import channel
    app=Application(output/"OBSERVER")
    source=ROOT/"resultados/demo02/ANTES_DE_CONSULTAR200.deetsnap"
    result=app.load(source)
    checks={"normal_load_at200":result["physical"]["tick"]==200}
    main=app.world; before=channel.digest(main)
    def rejected(name, callback):
        try:
            callback(); checks[name]=False
        except (ValueError,FileExistsError):
            checks[name]=app.world is main and channel.digest(app.world)==before
    rejected("query_wrong_order_does_not_advance",lambda:app.query("NO"))
    rejected("create_does_not_reset_existing_main",lambda:app.create())
    for kind in ("pending_teacher","translation","alias_case","unknown_answer_map","phase","float_coordinate","missing_contract"):
        candidate=d.OrganizationalWorld.load_snapshot(str(source))
        metadata=json.loads(candidate.runtime.snapshot_metadata(APP_KEY))
        if kind=="pending_teacher":
            candidate.submit("lex.W1.outcome.plus",11,236)
            assert any(str(r.status)=="scheduled" for r in candidate.runtime.receipts)
        elif kind=="translation":metadata["translation"][0]=(metadata["translation"][0]+1)%67
        elif kind=="alias_case":metadata["aliases"]["ZUVI"]=metadata["aliases"].pop("zuvi", "W1")
        elif kind=="unknown_answer_map":metadata["answer_map"]={"W1":"present"}
        elif kind=="phase":metadata["stage"]="FIRST_WORD_QUERY"
        elif kind=="float_coordinate":metadata["translation"][0]=float(metadata["translation"][0])
        if kind=="missing_contract":candidate.runtime.erase_snapshot_metadata(APP_KEY)
        else:candidate.runtime.set_snapshot_metadata(APP_KEY,json.dumps(metadata))
        path=output/("ADVERSARIAL_"+kind+".deetsnap")
        candidate.save_snapshot(str(path))
        rejected("load_rejects_"+kind+"_without_main_replacement",lambda p=path:app.load(p))
    for _ in range(5):app.observe()
    checks["five_passive_observations_preserve_RAW_clocks_tick"]=channel.digest(app.world)==before
    assert all(checks.values())
    app.load(ROOT/"resultados/demo02/MAIN_FINAL267.deetsnap")
    main=app.world; before=channel.digest(main)
    rejected("third_query_rejected_without_hidden_recreation",lambda:app.query("HAY"))
    checks["normal_load_at267"]=before["tick"]==267
    put(output/"RESULTS.json",{"verified":all(checks.values()),"checks":checks,"count":len(checks),
                                "new_scientific_samples":0,"native_future_ticks_executed":0,
                                "source_snapshot_sha256":sha(source),"scope":"Real Native snapshot/schema/queue validation; not an attack-resistant OS sandbox"})
    print(json.dumps({"verified":all(checks.values()),"checks":len(checks)}))


if __name__=="__main__":main()
