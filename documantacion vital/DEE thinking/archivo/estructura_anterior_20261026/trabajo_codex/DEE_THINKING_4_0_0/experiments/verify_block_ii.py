"""Read saved evidence; technical assertions do not adjudicate cognition."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);args=p.parse_args()
    root=args.root.resolve();base=root/"experiments/BLOCK_II";qualified=read(root/"validation/BLOCK_I_QUALIFICATION.json")
    results=read(base/"RESULTS.json");rows=results["cases"]
    assert len(rows)==24 and len({x["identity"] for x in rows})==24
    assert all(x["product"]["wheel_sha256"]==qualified["wheel_sha256"] and x["product"]["native_sha256"]==qualified["native_sha256"] for x in rows)
    assert all(x.get("status")!="TECHNICAL_ERROR" for x in rows)
    by_id={x["identity"]:x for x in rows};snapshots=[]
    for row in rows:
        folder=base/row["identity"];assert (folder/"MEASUREMENTS.json").is_file()
        for snapshot in sorted(folder.glob("*.deetsnap")):
            assert snapshot.stat().st_size>0
            snapshots.append({"path":str(snapshot.relative_to(root)),"sha256":sha(snapshot),"size":snapshot.stat().st_size})
    acquisitions=[]
    for x in rows:
        if x["case"]["family"]!="acquired":continue
        assert x["explicit_save_load_mid_protocol"]["raw_and_clock_preserved"]
        assert all(r["status"]=="applied" for q in x["captures"] for r in q["receipts"])
        acquisitions.append({"id":x["identity"],"queries":x["queries"],"responses":x["evaluation_only"]["actual"],
                             "forms":x["forms_interface_only"],"receipts":[r for q in x["captures"] for r in q["receipts"]]})
    assert by_id["native_main"]["final"]==by_id["swapped_external_forms"]["final"]
    online=[]
    for x in rows:
        if x["case"]["family"]!="online_signal":continue
        restore=x["restoration"]
        assert restore["before"]==restore["after"] and restore["pending_before"]==restore["pending_after"]
        assert all(r["status"]=="applied" for r in x["receipts"])
        windows={t["tick"]:t["readings"] for t in x["trace"] if t["tick"] in (5,8,16,21)}
        online.append({"id":x["identity"],"windows":windows,"receipts":x["receipts"],"final":x["final"]})
    dialogues=[]
    for name in ("main","reserved"):
        folder=base/("online_demonstrator_"+name)
        transcript=[json.loads(line) for line in (folder/"DIALOGOS.jsonl").read_text(encoding="utf-8").splitlines()]
        assert transcript and all("error" not in x["response"] for x in transcript)
        pids={x["pid"] for x in transcript};assert len(pids)==1
        saves={};pairs=[];responses=[]
        for x in transcript:
            result=x["response"]
            if x["input"].startswith("Guarda "):
                filename=x["input"][len("Guarda "):]
                saves[filename]=result["physical_digest"]
                assert sha(folder/filename)==result["snapshot_sha256"]
            elif x["input"].startswith("Carga "):
                filename=x["input"][len("Carga "):]
                assert result["physical_digest"]==saves[filename]
                pairs.append({"snapshot":filename,"tick":result["physical_digest"]["tick"],"physical_equal":True,
                              "receipts_after_load":result["measurement"]["receipts"]})
            elif x["input"]=="Observa respuesta":
                assert result["receipt"]["status"]=="applied" and result["available"] and result["physical_output"]["active"]
                responses.append(result["physical_output"])
        assert len(responses)==2 and len(pairs)>=2
        dialogues.append({"id":name,"engine_pid":next(iter(pids)),"single_persistent_engine":True,
                          "errors":[],"save_load_pairs":pairs,"current_native_responses":responses,
                          "transcript_sha256":sha(folder/"DIALOGOS.jsonl"),"final_snapshot_sha256":sha(folder/"MAIN_FINAL.deetsnap")})
    final_rows=[json.loads(x) for x in (base/"online_demonstrator_load_final/DIALOGOS.jsonl").read_text(encoding="utf-8").splitlines()]
    assert final_rows and all("error" not in x["response"] for x in final_rows)
    assert len({x["pid"] for x in final_rows})==1 and final_rows[0]["input"].startswith("Carga ")
    final_outputs=[x["response"]["physical_output"] for x in final_rows if x["input"]=="Observa respuesta"]
    assert final_outputs==dialogues[0]["current_native_responses"]
    application_checks=read(base/"online_application_technical/TECHNICAL_CHECKS.json")
    assert application_checks["all_checks"] and all(application_checks["technical_checks"].values())
    summary={"technical_evidence_checks":True,"case_count":24,"cases_unique":True,"cases_use_qualified_artifact":True,
             "wheel_sha256":qualified["wheel_sha256"],"native_sha256":qualified["native_sha256"],
             "new_observations_not_global_verdict":True,"cases":[{"id":x["identity"],"family":x["case"]["family"],"elapsed_seconds":x["elapsed_seconds"],"runner_sha256":x["runner_sha256"]} for x in rows],
             "acquisition_measurements":acquisitions,"online_measurements":online,"dialogues":dialogues,
             "swapped_external_forms_physical_final_equal":True,"checkpoints":snapshots,
             "application_loader_checks":application_checks["technical_checks"],
             "final_cli_load_continuation":{"single_persistent_engine":True,"pid":final_rows[0]["pid"],"errors":[],"physical_outputs":final_outputs,
                 "transcript_sha256":sha(base/"online_demonstrator_load_final/DIALOGOS.jsonl")},
             "sources":{"runner_sha256":sha(root/"experiments/run_block_ii.py"),
                 "initial_demos_application_source":"validation/source_revisions/mundo_nativo_before_load_flag.py",
                 "initial_demos_application_sha256":sha(root/"validation/source_revisions/mundo_nativo_before_load_flag.py"),
                 "final_application_sha256":sha(root/"app/mundo_nativo.py"),
                 "final_application_evidence":["online_application_technical/TECHNICAL_CHECKS.json","online_demonstrator_load_final/DIALOGOS.jsonl"],
                 "verifier_sha256":sha(__file__)},
             "counting":"24 finite scientific cases. Two additional UI continuations reproduce the already frozen online family; they are demonstrations/technical continuations, not two new independent capabilities.",
             "limits":["No thermodynamic temperature estimate or FDT test","No arbitrary dictionary acquisition","Finite consumable mobile relations, not a renewable basal body","External contact codec replay and native same-Runtime online path are separate modalities"]}
    target=base/"TECHNICAL_EVIDENCE_CHECKS.json";target.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"technical_evidence_checks":True,"case_count":24,"ui_continuations":2,"checkpoints":len(snapshots),"path":str(target)}))


if __name__=="__main__":main()
