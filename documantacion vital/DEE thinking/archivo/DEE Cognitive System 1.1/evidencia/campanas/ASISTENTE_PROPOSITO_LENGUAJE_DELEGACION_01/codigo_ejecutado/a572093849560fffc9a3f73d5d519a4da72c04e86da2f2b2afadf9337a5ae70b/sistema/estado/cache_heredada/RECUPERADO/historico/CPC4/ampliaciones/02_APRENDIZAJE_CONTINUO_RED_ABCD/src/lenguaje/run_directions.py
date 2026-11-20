"""New content extension with controls and reserved source/payload interfaces."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from lenguaje.protocol import put, sha


def freeze(output):
    main = ROOT / "resultados/lenguaje/continuous02/MAIN_NEW_FORMS/MAIN_FINAL1529.deetsnap"
    cases = []
    for name, change, parent in (
        ("DIRECTION_MAIN", {}, main),
        ("DIRECTION_FORMS_INVERTED", {"word_order": ["L4", "L3"]}, main),
        ("DIRECTION_SIGNALS_OMITTED", {"teaching": "signal_omitted"}, main),
        ("DIRECTION_REPORTS_OMITTED", {"teaching": "report_omitted"}, main),
        ("DIRECTION_UNPAIRED_PLUS1", {"teaching": "unpaired"}, main),
        ("RESERVED_SOURCE_C_PAYLOAD17", {"source": "C", "source_payload": 17}, ROOT / "resultados/lenguaje/continuous02/RESERVED_TRANSLATION_A/MAIN_FINAL1529.deetsnap"),
        ("RESERVED_SOURCE_ORDER_PAYLOAD23", {"source": "C", "source_payload": 23, "word_order": ["L4", "L3"]}, ROOT / "resultados/lenguaje/continuous02/RESERVED_ORDER_TRANSLATION_B/MAIN_FINAL1529.deetsnap")):
        cases.append({"id": name, "parent": parent.relative_to(ROOT).as_posix(), "parent_sha256": sha(parent), **change})
    names = ("src/lenguaje/directions.py", "src/lenguaje/direction_worker.py", "src/lenguaje/run_directions.py",
             "src/lenguaje/protocol.py", "src/red/recipe_v3.py", "src/red/session_v3.py", "src/red/common_helpers.py")
    config = {"frozen_utc": datetime.now(timezone.utc).isoformat(), "cases": cases, "sources": {n: sha(ROOT/n) for n in names},
              "native_workers": 1, "timeout_seconds": 180, "architecture_family": "Same predeclared mobile directional association",
              "phase": "New-content extension, sourceC/payload/order variants reserved before this content was measured",
              "source_events": [1533, 1561], "current_source_observed_and_lessons": [1536, 1564],
              "word_queries": [1603, 1631], "readouts": [1606, 1634], "old_retention_queries": [1565, 1593],
              "criterion": "Current Applied source with actual dz+/-1; physically learned21diagonal under fixed later decoder",
              "full_NSM_semantics": False, "not_gravity": True,
              "reserved_worlds_note": "These parents were seen in the earlier content task, but the new source/payload/order task parameters were not used for tuning. Not newly independent preparation replicas."}
    put(output / "EXPERIMENT_CONFIG.json", config)
    for n in names:
        target=output/"EXECUTED_SOURCE"/n; target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/n,target)
    for case in cases: put(output/"cases"/(case["id"]+".json"),case)
    return config


def main():
    p=argparse.ArgumentParser(); p.add_argument("--freeze-only",action="store_true"); a=p.parse_args()
    output=ROOT/"resultados/lenguaje/direction03"; path=output/"EXPERIMENT_CONFIG.json"
    config=json.loads(path.read_text(encoding="utf-8")) if path.exists() else freeze(output)
    if a.freeze_only: print(json.dumps({"frozen":True,"sha256":sha(path),"cases":len(config["cases"])}));return
    assert all(sha(ROOT/n)==v for n,v in config["sources"].items())
    import supervision
    rows=[]
    for case in config["cases"]:
        parent=ROOT/case["parent"]; assert sha(parent)==case["parent_sha256"]
        target=output/case["id"]; file=target/"MEASUREMENTS.json"
        if not file.exists():
            job=supervision.run(ROOT,"language_directions_"+case["id"].lower(),[sys.executable,"-I","-B",
                str(Path(__file__).with_name("direction_worker.py")),"--case",str(output/"cases"/(case["id"]+".json")),
                "--parent",str(parent),"--output",str(target)],180)
            if job["exit_code"]!=0:raise RuntimeError("Preserved direction-content error; no identical retry")
        data=json.loads(file.read_text(encoding="utf-8")); rows.append({"id":case["id"],"experiences":data["experiences"],
            "readouts":data["readouts"],"old_retention_panel":data["old_retention_panel"],"evidence":file.relative_to(ROOT).as_posix()})
        put(output/"RUN_SUMMARY.json",{"config_sha256":sha(path),"cases":rows})


if __name__=="__main__":main()
