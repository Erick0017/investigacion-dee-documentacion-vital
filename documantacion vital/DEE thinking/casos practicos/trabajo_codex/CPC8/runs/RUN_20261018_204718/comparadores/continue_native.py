"""Resume saved T920; late revision via declared physical public interfaces.

No RAW/clock/descriptor edit, no reconstruction, no replay of completed blocks.
The finite published revise() helper rejects this late1048 tick; that attempt
and its121 measurements remain unchanged. This explicitly labelled research
continuation schedules the same four prepared ports through ordinary submit.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gc,json,sys,time,traceback
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from run_comparison import ROOT,write,sha,physics,metric

def main():
    p=argparse.ArgumentParser();p.add_argument("--seed",type=int,required=True);p.add_argument("--output",type=Path);a=p.parse_args()
    import dee_thinking as d
    from dee_thinking.consolidated import RepertoireSession
    config=json.loads((BASE/"FROZEN_CONFIG.json").read_text(encoding="utf-8"))
    amendment=json.loads((BASE/"LATE_REVISION_PROTOCOL.json").read_text(encoding="utf-8"))
    if a.seed not in config["reserved_seeds"]:raise ValueError("Not a frozen reserved world")
    if sha(BASE/"continue_native.py")!=amendment["continuation_source_sha256"]:raise ValueError("Continuation source changed")
    prior=ROOT/"resultados"/"comparadores"/("DEE_"+str(a.seed))
    out=a.output or prior.with_name(prior.name+"_continuation")
    if out.exists():raise FileExistsError("Continuation output already exists")
    out.mkdir(parents=True)
    original=json.loads((prior/"MEASUREMENTS.json").read_text(encoding="utf-8"))
    events=json.loads((prior/"EVENTS.json").read_text(encoding="utf-8"))
    rows=json.loads((prior/"OBSERVATIONS.json").read_text(encoding="utf-8"))
    truth={e["form"]:e["observation"] for b in events["blocks"] for e in b["observations"]}
    start=time.perf_counter();cpu=time.process_time()
    record={"case_id":out.name,"method":"DEE","seed":a.seed,"status":"RUNNING","parent":str(prior.relative_to(ROOT)),
      "parent_measurements_sha256":sha(prior/"MEASUREMENTS.json"),"parent_checkpoint_sha256":sha(prior/"after_panel_917.deetsnap.gz"),
      "source_sha256":sha(BASE/"continue_native.py"),"amendment_sha256":sha(BASE/"LATE_REVISION_PROTOCOL.json"),
      "scope":"Explicit late physical revision research continuation; not published finite revise helper domain",
      "started_utc":datetime.now(timezone.utc).isoformat(),"panels":[],"checkpoints":[]}
    try:
        s=RepertoireSession.load_snapshot(prior/"after_panel_917.deetsnap.gz")
        assert s.tick==920
        record["initial_physics"]=physics(s)
        assert record["initial_physics"]==original["checkpoints"][-1]["physics"]
        assert s.identifier==original["case_id"]
        e=events["revision"];label="plus" if e["observation"]==1 else "minus"
        required={"revision.counter.plus","revision.counter.minus","L01.signal","L01.event."+label}
        assert required<=set(s.world.runtime.channel_names)
        t=time.perf_counter();c=time.process_time()
        initial_requests=len(s.journal)
        rr=[s.submit("revision.counter."+direction,0,e["tick"]-4) for direction in ("plus","minus")]
        rr+=s.acquire(e["form"],e["observation"],e["tick"])
        record["revision"]={"tick":e["tick"],"observation":e["observation"],"public_method":"submit counter± plus acquire cue/current consequence",
          "receipts_at_request":rr,"requests_before":initial_requests,"requests_after":len(s.journal),
          "wall_seconds":time.perf_counter()-t,"cpu_seconds":time.process_time()-c}
        truth[0]=e["observation"]
        def panel(tick,restored=False):
            t=time.perf_counter();c=time.process_time();answer=s.query(list(range(65)),tick,payload=config["query_payload"])
            local=[]
            for i,response in enumerate(answer["responses"]):
                row={"form":i,"form_name":"L%02d"%(i+1),"panel_tick":tick,"read_tick":tick+3,
                    "category":"revision" if i==0 and not restored else "retained","restored":restored,
                    "response":response,"expected":truth[i],"correct":response["value"]==truth[i]}
                rows.append(row);local.append(row)
            record["panels"].append({"panel_tick":tick,"read_tick":tick+3,"world_age_ticks":s.tick,
                **metric(local),"response_latency_ticks":3,"wall_seconds":time.perf_counter()-t,"cpu_seconds":time.process_time()-c,"restored":restored})
            record["combined_totals"]=metric(rows)
            write(out/"OBSERVATIONS.json",rows);write(out/"MEASUREMENTS.json",record)
        def save(tag):
            path=out/(tag+".deetsnap.gz");proof=s.save_snapshot(path)
            record["checkpoints"].append({"file":path.name,"stored_bytes":path.stat().st_size,"sha256":sha(path),"proof":proof,"physics":physics(s)})
            return path
        panel(e["panel_tick"])
        path=save("before_restore_T1182")
        before=physics(s);queries=s.queries;receipts=s.receipts();identifier=s.identifier
        del s;gc.collect();s=RepertoireSession.load_snapshot(path)
        record["restore"]={"physical_exact":physics(s)==before,"query_protocol_exact":s.queries==queries,
             "receipts_exact":s.receipts()==receipts,"identifier_exact":s.identifier==identifier,"tick":s.tick}
        assert all(record["restore"][key] for key in ("physical_exact","query_protocol_exact","receipts_exact","identifier_exact"))
        panel(config["restored_panel_tick"],restored=True)
        save("final")
        record["resources"]={**original["resources"],"physical_request_count":len(s.journal),
            "applied_request_count":sum(r["receipt"]["status"]=="applied" for r in s.receipts()),
            "query_protocol_count":len(s.queries),"trajectory_experience_events":66,"host_state_edits":0,
            "fixed_prepared_revision_port_invocations":4}
        record["receipts"]=s.receipts();record["final_physics"]=physics(s)
        record["combined_wall_seconds"]=original["wall_seconds"]+time.perf_counter()-start
        record["combined_cpu_seconds"]=original["cpu_seconds"]+time.process_time()-cpu
        record["combined_panels"]=original["panels"]+record["panels"]
        record["combined_totals"]=metric(rows);record["status"]="MEASURED"
    except BaseException as error:
        record["status"]="TECHNICAL_ERROR";record["error"]=repr(error);record["traceback"]=traceback.format_exc();raise
    finally:
        record["wall_seconds"]=time.perf_counter()-start;record["cpu_seconds"]=time.process_time()-cpu
        record["finished_utc"]=datetime.now(timezone.utc).isoformat();write(out/"MEASUREMENTS.json",record)
        print(json.dumps({k:record.get(k) for k in ("case_id","status","combined_totals","wall_seconds","error")}),flush=True)
if __name__=="__main__":main()
