"""One fresh MCTS life plus actual counterpropagating events; exact audit only."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    t=p.with_name(p.name+".pending."+str(os.getpid()));t.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf8");os.replace(t,p)
def main():
    p=argparse.ArgumentParser();p.add_argument("--base-src",type=Path,required=True);p.add_argument("--config",type=Path,required=True)
    p.add_argument("--case-id",required=True);p.add_argument("--out",type=Path,required=True);p.add_argument("--parent",type=Path)
    p.add_argument("--fork",choices=("cut","sham"));p.add_argument("--bank",choices=("d-5","d-3","d-1","d1","d3","d5"),default="d5")
    a=p.parse_args();sys.path.insert(0,str(a.base_src.resolve()));sys.path.insert(0,str(Path(__file__).resolve().parent))
    from tiled_order import TiledOrderSession
    from integracion.relational_pair import physical,move
    from dee_thinking import _native as d
    import dee_thinking
    if dee_thinking.__version__!="4.5.0"or sha(d.__file__)!="17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d"or not Path(dee_thinking.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError("Official isolated instrument required")
    config=json.loads(a.config.read_text(encoding="utf8"));case=next(row for row in config["cases"]if row["id"]==a.case_id)
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=None
    m={"schema":"CPC9.tiled_order.measurements.v1","case":case,"configuration_sha256":sha(a.config),"status":"RUNNING",
        "preparations":int(not a.parent),"diagnostic_forks":int(bool(a.fork)),"continuations":int(bool(a.parent)and not a.fork),
        "frames":[],"local":[],"snapshots":[],"host_RAW_clock_edits_on_MAIN":[],
        "engine":{"version":dee_thinking.__version__,"module":dee_thinking.__file__,"native_sha256":sha(d.__file__),"python":sys.executable}}
    sources={}
    for name,module in list(sys.modules.items()):
        path=getattr(module,"__file__",None)
        if path and Path(path).suffix==".py"and(Path(path).resolve().is_relative_to(a.base_src.resolve())or Path(path).resolve().is_relative_to(Path(__file__).resolve().parent)):sources[str(Path(path).resolve())]=sha(path)
    m["source_sha256"]=sources
    try:
        if a.parent:
            parent=TiledOrderSession.load(a.parent);before=physical(parent.world);m["parent"]={"path":str(a.parent),"sha256":sha(a.parent),"physical":before}
            if a.fork:
                item=next(item for item in parent.geometry["tiled_order"]["surfaces"]if item["id"]==a.bank)
                pre=parent.observe(item["hub"]);edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*item["hub"])
                edit.raw=0 if a.fork=="cut"else int(pre["raw"]);edit.label="CPC9_AUDITOR_COUNTERPROP_MEMORY_"+a.fork
                parent.state["mode"]=deepcopy(parent.mode.state);parent.state["quantity"]=deepcopy(parent.quantity.state)
                parent.state["initiative"]=deepcopy(parent.initiative.state);parent.state["transferred_quantity"]=deepcopy(parent.transferred_quantity.state)
                child=parent.world.diagnostic_fork([edit],True);s=TiledOrderSession(child,parent.geometry,parent.state,a.out.name)
                m["edit"]={"pre":pre,"requested_raw":str(edit.raw),"post":s.observe(item["hub"]),"clock_edit":None}
                m["parent_unchanged"]=before==physical(parent.world)
            else:s=parent
        else:
            s=TiledOrderSession.create(identifier=case["id"],**case.get("preparation",{}));s.curriculum(**case.get("curriculum",{}))
        m["geometry"]=s.geometry;m["initial_physical"]=physical(s.world);g=s.geometry["tiled_order"]
        def save():
            path=a.out/("T"+str(s.tick)+".deetsnap.gz");storage=s.save(path)
            m["snapshots"].append({"path":path.name,"sha256":sha(path),"tick":s.tick,"bytes":path.stat().st_size,"physical":physical(s.world),"storage":storage})
        save();boundaries={469,470,472,474,475,476,477,478,481,482,483,548,549,550,554,555,556,616}
        for tick in sorted(t for t in boundaries if s.tick<t<=case.get("horizon",616)):
            s.run_until(tick);m["frames"].append(s.view())
            if tick in(474,475,476,477,478):
                for item in g["surfaces"]:
                    site=item["meeting"];m["local"].append({"tick":tick,"id":item["id"],"center":site,
                        "Moore27":[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if tick in(477,g["record_tick"],616):save()
            m.update(last_complete_tick=s.tick,requests=s.receipts(),tiled_order_observations=s.state["tiled_order_observations"],elapsed_seconds=time.monotonic()-started);put(a.out/"MEASUREMENTS.json",m)
        m.update(status="EXECUTED",final_physical=physical(s.world))
    except BaseException as error:m.update(status="TECHNICAL_ERROR",error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:m.update(last_complete_tick=s.tick,requests=s.receipts(),tiled_order_observations=s.state["tiled_order_observations"],elapsed_seconds=time.monotonic()-started)
        m["sources_unchanged_during_execution"]=all(sha(path)==digest for path,digest in sources.items());put(a.out/"MEASUREMENTS.json",m)
    print(json.dumps({"id":case["id"],"status":m["status"],"seconds":m["elapsed_seconds"],"pair":[{"tick":row["tick"],"stage":row["stage"],"states":[{"id":item["id"],"direction":item["physical"]["direction"],"load":item["physical"]["s_reg"]}for item in row["surfaces"]]}for row in m["tiled_order_observations"]if not row["stage"].startswith("pre_")]}),flush=True)
if __name__=="__main__":main()
