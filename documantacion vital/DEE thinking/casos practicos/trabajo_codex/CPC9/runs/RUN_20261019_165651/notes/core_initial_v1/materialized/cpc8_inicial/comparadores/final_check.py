"""Metadata/source/primary audit only; no native Runtime or model training."""
from pathlib import Path
from datetime import datetime,timezone
import ast,json,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parent
sys.path.insert(0,str(BASE))
from run_comparison import sha,write

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
    checked=[]
    for path in BASE.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"),filename=str(path));checked.append({"path":str(path.relative_to(ROOT)),"sha256":sha(path)})
    cfg=load(BASE/"FROZEN_CONFIG.json")
    for name,digest in cfg["source_hashes"].items():assert sha(BASE/name)==digest
    for name,module,key in (("LATE_REVISION_PROTOCOL.json","continue_native.py","continuation_source_sha256"),
        ("QUERY_ABLATION_CONFIG.json","query_ablation.py","source_sha256"),("PRIVATE_RNG_PROTOCOL.json","run_mlp_private.py","source_sha256")):
        assert sha(BASE/module)==load(BASE/name)[key]
    summary=load(BASE/"SUMMARY.json");assert len(summary["cases"])==6
    assert summary["counts"]["total_comparable_queries"]==1506
    assert len(summary["query_ablation_diagnostic_forks"])==2
    assert len(summary["preserved_methodological_attempts"])==2
    assert summary["counts"]["semantic_meanings_validated"]==0
    jobs=[]
    for p in sorted((ROOT/"jobs").glob("cmp_*/COMMAND.json")):
        j=load(p)
        assert j.get("owned_job_closed") and j.get("owned_worker_waited"),str(p)
        jobs.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p),"exit_code":j.get("exit_code"),"status":j.get("status"),"owned_job_closed":True})
    unexpected=[j for j in jobs if j["exit_code"]!=0 and not any(s in j["path"].replace("\\","/") for s in
       ("cmp_discovery_k8_01/","cmp_DEE_402817_01/","cmp_DEE_591307_01/"))]
    assert not unexpected,unexpected
    primary=[]
    for c in summary["cases"]:
        p=ROOT/c["primary"];assert sha(p)==c["primary_sha256"]
        primary.append({"path":c["primary"],"sha256":sha(p)})
    for c in summary["query_ablation_diagnostic_forks"]:
        p=ROOT/c["primary"];assert sha(p)==c["sha256"]
        assert c["contrast"]["omit_correct"] and c["contrast"]["all_final_correct"]==65
    expanded=sum(p.stat().st_size for folder in (BASE,ROOT/"resultados"/"comparadores") for p in folder.rglob("*") if p.is_file())
    record={"closed_utc":datetime.now(timezone.utc).isoformat(),"status":"FINITE_COMPARISON_MEASURED_AND_AUDITED",
       "summary_sha256":sha(BASE/"SUMMARY.json"),"source_files":checked,"primary_cases":primary,"jobs":jobs,
       "counts":summary["counts"],"nonzero_exit_attempts":sum(j["exit_code"]!=0 for j in jobs),
       "nonzero_exits_preserved":"One path-launch error, two finite-helper contract rejections; not failed native acquisition, not erased",
       "all_owned_jobs_closed":True,"native_worlds":2,"extra_diagnostic_forks":2,
       "independent_environment_worlds_added_by_B2_retry":0,"expanded_bytes_before_this_record":expanded,
       "next_task":"None in this comparator front; parent may integrate evidence without asserting integration into E1"}
    write(BASE/"CLOSED.json",record)
    print(json.dumps({"status":record["status"],"jobs":len(jobs),"nonzero_exit_attempts":record["nonzero_exit_attempts"],"summary_sha256":record["summary_sha256"],"expanded_bytes":expanded}))
if __name__=="__main__":main()
