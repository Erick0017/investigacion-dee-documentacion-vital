"""Diagnostic fork: omit only the first post-revision L01 physical probe."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gc,json,sys,time,traceback
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE))
from run_comparison import ROOT,write,sha,physics

def neighborhood(s):
    from dee_thinking import Coordinate
    from dee_thinking.consolidated import exact_observation
    hub=s.preparation.forms[0].hub;n=s.dimension
    rows=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for dz in (-1,0,1):
                c=Coordinate((hub.x+dx)%n,(hub.y+dy)%n,(hub.z+dz)%n)
                rows.append({"offset":[dx,dy,dz],**exact_observation(s.world.runtime.observe(c))})
    return {"tick":s.tick,"hub":[hub.x,hub.y,hub.z],"coverage":"27 sites: center and Moore26, not the full composed causal cone or certified mobile genealogy", "sites":rows}

def main():
    p=argparse.ArgumentParser();p.add_argument("--seed",type=int,required=True);a=p.parse_args()
    from dee_thinking.consolidated import RepertoireSession
    cfg=json.loads((BASE/"QUERY_ABLATION_CONFIG.json").read_text(encoding="utf-8"))
    assert sha(BASE/"query_ablation.py")==cfg["source_sha256"]
    if a.seed not in cfg["seeds"]:raise ValueError("Unfrozen control seed")
    prior=ROOT/"resultados"/"comparadores"/("DEE_"+str(a.seed))
    main_result=prior.with_name(prior.name+"_continuation")
    out=prior.with_name(prior.name+"_omit_first_L01")
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);start=time.perf_counter();cpu=time.process_time()
    record={"case_id":out.name,"status":"RUNNING","seed":a.seed,"modality":"AUDIT_CONTINUATION_FORK",
       "independent_worlds":0,"parent_checkpoint":str((prior/"after_panel_917.deetsnap.gz").relative_to(ROOT)),
       "parent_sha256":sha(prior/"after_panel_917.deetsnap.gz"),"config_sha256":sha(BASE/"QUERY_ABLATION_CONFIG.json"),
       "source_sha256":sha(BASE/"query_ablation.py"),"checkpoints":[],"windows":[],"main_saved_windows":[],
       "criterion":"Same physical revision; only L01 query@1179 omitted. All64 other queries retained. Compare fresh L01 probe@1310.",
       "started_utc":datetime.now(timezone.utc).isoformat()}
    try:
        original=RepertoireSession.load_snapshot(prior/"after_panel_917.deetsnap.gz")
        before=physics(original);s=original.fork(identifier=original.identifier+".omit_first_L01")
        assert physics(s)==before
        events=json.loads((prior/"EVENTS.json").read_text(encoding="utf-8"));e=events["revision"]
        for d in ("plus","minus"):s.submit("revision.counter."+d,0,1044)
        s.acquire(0,e["observation"],1048)
        def save(tag):
            path=out/(tag+".deetsnap.gz");proof=s.save_snapshot(path)
            record["checkpoints"].append({"file":path.name,"sha256":sha(path),"proof":proof,"physics":physics(s)})
            return path
        s.run_until(1179);record["windows"].append(neighborhood(s));save("pre_panel_T1179")
        q=s.query(list(range(1,65)),1179,payload=5)
        record["first_panel_without_L01"]=q
        record["windows"].append(neighborhood(s));path=save("post_panel_T1182")
        before_restore=physics(s);del s;gc.collect();s=RepertoireSession.load_snapshot(path)
        record["restore_exact"]=physics(s)==before_restore;assert record["restore_exact"]
        s.run_until(1309);record["windows"].append(neighborhood(s))
        result=s.query(list(range(65)),1310,payload=5)
        record["final_panel"]=result
        record["windows"].append(neighborhood(s));save("final_T1313")
        record["parent_unchanged"]=physics(original)==before;assert record["parent_unchanged"]
        truth={v["form"]:v["observation"] for b in events["blocks"] for v in b["observations"]};truth[0]=e["observation"]
        original_rows=json.loads((main_result/"OBSERVATIONS.json").read_text(encoding="utf-8"))
        main_row=next(r for r in original_rows if r["form"]==0 and r["panel_tick"]==1310)
        record["contrast"]={"expected":truth[0],"main_L01_response":main_row["response"],
            "omit_first_L01_response":result["responses"][0],
            "main_correct":main_row["correct"],"omit_correct":result["responses"][0]["value"]==truth[0],
            "all_final_correct":sum(r["value"]==truth[i] for i,r in enumerate(result["responses"])),"all_final_queries":65,
            "interpretation_rule":"A recovered final response under omission identifies first-probe-dependent access loss; equal absence leaves timing/revision dynamics as alternatives."}
        record["receipts"]=s.receipts();record["applied_requests"]=sum(r["receipt"]["status"]=="applied" for r in s.receipts())
        del original,s;gc.collect()
        # Observe preserved MAIN boundaries; no intervention and no new evolution.
        for name in ("before_restore_T1182.deetsnap.gz","final.deetsnap.gz"):
            saved=RepertoireSession.load_snapshot(main_result/name)
            record["main_saved_windows"].append(neighborhood(saved));del saved;gc.collect()
        record["status"]="MEASURED"
    except BaseException as error:
        record["status"]="TECHNICAL_ERROR";record["error"]=repr(error);record["traceback"]=traceback.format_exc();raise
    finally:
        record["wall_seconds"]=time.perf_counter()-start;record["cpu_seconds"]=time.process_time()-cpu
        record["finished_utc"]=datetime.now(timezone.utc).isoformat();write(out/"MEASUREMENTS.json",record)
        print(json.dumps({"case_id":out.name,"status":record["status"],"contrast":record.get("contrast"),"error":record.get("error")}),flush=True)
if __name__=="__main__":main()
