"""Finite common-event evaluator. Participants never receive query targets.

DEE is installed official4.5, one native Runtime per trajectory. Conventional
participants are models.py; audit/evaluation below is not fed back to either.
"""
from __future__ import annotations
from array import array
from datetime import datetime,timezone
import argparse,gc,hashlib,json,random,sys,time,traceback
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
sys.path.insert(0,str(BASE))
from models import RelationshipDictionary,ReplayMLP

WHEEL_SHA="09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c"
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".pending")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    tmp.replace(path)
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def physics(s):
    r=s.world.runtime
    return {"tick":s.tick,"raw_sha256":hashlib.sha256(array("Q",r.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",r.clock_copy()).tobytes()).hexdigest()}
def compact_size(value):return len(json.dumps(value,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode())
def curriculum(config,seed):
    rng=random.Random(seed)
    observations=[rng.choice((-1,1)) for _ in range(config["count"])]
    blocks=[]
    for b in config["blocks"]:
        order=list(range(b["start"],b["stop"]));rng.shuffle(order)
        blocks.append({**b,"observations":[{"form":i,"observation":observations[i]} for i in order]})
    return {"seed":seed,"blocks":blocks,"revision":{"form":0,"observation":-observations[0],**config["revision"]}}
def metric(rows):
    known=[r for r in rows if r["expected"] is not None]
    return {"queries":len(known),"correct":sum(r["correct"] for r in known),
       "wrong":sum(not r["correct"] and r["response"]["value"] is not None for r in known),
       "missing":sum(r["response"]["value"] is None for r in known),
       "acquisition_queries":sum(r["category"]=="new" for r in known),
       "acquisition_correct":sum(r["correct"] and r["category"]=="new" for r in known),
       "retention_queries":sum(r["category"]=="retained" for r in known),
       "retention_correct":sum(r["correct"] and r["category"]=="retained" for r in known),
       "revision_queries":sum(r["category"]=="revision" for r in known),
       "revision_correct":sum(r["correct"] and r["category"]=="revision" for r in known)}

def main():
    p=argparse.ArgumentParser();p.add_argument("--method",choices=("DEE","B1","B2"),required=True)
    p.add_argument("--seed",type=int,required=True);p.add_argument("--output",type=Path)
    a=p.parse_args();config=json.loads((BASE/"FROZEN_CONFIG.json").read_text(encoding="utf-8"))
    if a.seed not in config["reserved_seeds"]:raise ValueError("Only frozen reserved seeds accepted")
    for name,digest in config["source_hashes"].items():
        if sha(BASE/name)!=digest:raise ValueError("Frozen source changed: "+name)
    out=a.output or ROOT/"resultados"/"comparadores"/(a.method+"_"+str(a.seed))
    if out.exists():raise FileExistsError("Output trajectory already exists; do not duplicate")
    out.mkdir(parents=True)
    start=time.perf_counter();cpu=time.process_time();events=curriculum(config,a.seed)
    write(out/"EVENTS.json",events)
    record={"case_id":out.name,"method":a.method,"seed":a.seed,"started_utc":datetime.now(timezone.utc).isoformat(),
      "scope":config["scope"],"configuration_sha256":sha(BASE/"FROZEN_CONFIG.json"),"source_hashes":config["source_hashes"],
      "observations":[],"panels":[],"checkpoints":[],"status":"RUNNING"}
    rows=[];truth={};training=[]
    try:
        if a.method=="DEE":
            import dee_thinking as d
            from dee_thinking.consolidated import RepertoireSession
            if d.__version__!="4.5.0":raise RuntimeError("Wrong installed version")
            record["engine"]={"version":d.__version__,"import_path":str(Path(d.__file__).resolve()),"wheel_sha256":WHEEL_SHA}
            s=RepertoireSession.create(count=65,dimension=131,backend="LAZY",threads=1,identifier=out.name)
            record["initial_physics"]=physics(s)
            record["resources"]={"native_basic_buffers_bytes":32*131**3,"prepared_form_interfaces":65,
              "prepared_revision_interfaces":True,"backend":"LAZY","threads":1,"modality":"EXPERIENCE_PROTOCOL/PHYSICAL_PROBE_ON_MAIN"}
        else:
            cls=RelationshipDictionary if a.method=="B1" else ReplayMLP
            kw={} if a.method=="B1" else config["mlp"]
            s=cls(count=65,seed=a.seed,**kw)
            record["resources"]={"modality":"CONVENTIONAL_COMPUTATION","replay_bound":65 if a.method=="B2" else 0}
        def checkpoint(tag):
            if a.method=="DEE":
                path=out/(tag+".deetsnap.gz");proof=s.save_snapshot(path)
                r={"file":path.name,"stored_bytes":path.stat().st_size,"sha256":sha(path),"proof":proof,
                   "physics":physics(s),"protocol_requests":len(s.journal),"query_protocols":len(s.queries)}
            else:
                state=s.state();path=out/(tag+".json");write(path,state)
                r={"file":path.name,"stored_bytes":path.stat().st_size,"compact_json_bytes":compact_size(state),"sha256":sha(path)}
            record["checkpoints"].append(r)
            return path
        def panel(tick,n,new_start=None,revision=False,restored=False):
            t=time.perf_counter();c=time.process_time()
            if a.method=="DEE":
                answer=s.query(list(range(n)),tick,payload=config["query_payload"])
                responses=answer["responses"]
            else:responses=[s.query(i) for i in range(n)]
            local=[]
            for i,response in enumerate(responses):
                category="revision" if revision and i==0 else "new" if new_start is not None and i>=new_start else "retained"
                row={"form":i,"form_name":"L%02d"%(i+1),"panel_tick":tick,"read_tick":tick+3 if a.method=="DEE" else None,
                     "category":category,"restored":restored,"response":response,"expected":truth.get(i),
                     "correct":response["value"]==truth.get(i) and truth.get(i) is not None}
                rows.append(row);local.append(row)
            result={"panel_tick":tick,"read_tick":tick+3 if a.method=="DEE" else None,"world_age_ticks":s.tick if a.method=="DEE" else None,
              **metric(local),"wall_seconds":time.perf_counter()-t,"cpu_seconds":time.process_time()-c,
              "response_latency_ticks":3 if a.method=="DEE" else None,"restored":restored}
            record["panels"].append(result)
            write(out/"OBSERVATIONS.json",rows)
            record["totals"]=metric(rows);write(out/"MEASUREMENTS.json",record)
            return result
        checkpoint("T0")
        for b in events["blocks"]:
            t=time.perf_counter();c=time.process_time();batch={e["form"]:e["observation"] for e in b["observations"]}
            if a.method=="DEE":
                receipts=s.acquire_block(batch,b["experience_tick"])
            else:
                for e in b["observations"]:s.experience(e["form"],e["observation"])
                receipts=[]
            training.append({"kind":"acquire","tick":b["experience_tick"],"events":b["observations"],"receipts_at_request":receipts,
              "wall_seconds":time.perf_counter()-t,"cpu_seconds":time.process_time()-c})
            truth.update(batch)
            panel(b["panel_tick"],b["stop"],new_start=b["start"])
            checkpoint("after_panel_"+str(b["panel_tick"]))
            write(out/"TRAINING.json",training)
        e=events["revision"];t=time.perf_counter();c=time.process_time()
        if a.method=="DEE":receipts=s.revise(e["form"],e["observation"],e["tick"],method=e["method"])
        else:s.experience(e["form"],e["observation"]);receipts=[]
        training.append({"kind":"revision","tick":e["tick"],"events":[{"form":e["form"],"observation":e["observation"]}],
          "receipts_at_request":receipts,"wall_seconds":time.perf_counter()-t,"cpu_seconds":time.process_time()-c})
        truth[e["form"]]=e["observation"]
        panel(e["panel_tick"],65,revision=True)
        path=checkpoint("before_restore_T1182")
        if a.method=="DEE":
            before=physics(s);protocol=s.queries;requests=s.receipts()
            del s;gc.collect()
            s=RepertoireSession.load_snapshot(path)
            record["restore"]={"physical_exact":physics(s)==before,"query_protocol_exact":s.queries==protocol,
              "receipts_exact":s.receipts()==requests,"identifier":s.identifier,"tick":s.tick}
            assert all(record["restore"][k] for k in ("physical_exact","query_protocol_exact","receipts_exact"))
        else:
            before=[s.query(i) for i in range(65)]
            cls=type(s);s=cls.restore(json.loads(path.read_text(encoding="utf-8")))
            record["restore"]={"forward_exact":before==[s.query(i) for i in range(65)]}
            assert record["restore"]["forward_exact"]
        panel(config["restored_panel_tick"],65,restored=True)
        checkpoint("final")
        if a.method=="DEE":
            record["receipts"]=s.receipts()
            record["resources"]["physical_request_count"]=len(s.journal)
            record["resources"]["applied_request_count"]=sum(r["receipt"]["status"]=="applied" for r in s.receipts())
            record["resources"]["query_protocol_count"]=len(s.queries)
            record["final_physics"]=physics(s)
        else:
            state=s.state();record["resources"].update({"compact_state_bytes":compact_size(state),"experience_events":s.experiences,
                "replay_presentations":getattr(s,"replay_presentations",0),"replay_items":len(getattr(s,"buffer",{})),
                "float_parameter_count":65*24+24+24+1 if a.method=="B2" else 0})
        record["status"]="MEASURED";record["totals"]=metric(rows)
        write(out/"TRAINING.json",training)
    except BaseException as error:
        record["status"]="TECHNICAL_ERROR";record["error"]=repr(error);record["traceback"]=traceback.format_exc();raise
    finally:
        record["wall_seconds"]=time.perf_counter()-start;record["cpu_seconds"]=time.process_time()-cpu
        record["finished_utc"]=datetime.now(timezone.utc).isoformat();write(out/"MEASUREMENTS.json",record)
        print(json.dumps({k:record.get(k) for k in ("case_id","method","status","totals","wall_seconds","cpu_seconds","error")}),flush=True)
if __name__=="__main__":main()
