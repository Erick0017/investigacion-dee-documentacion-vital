"""Exact primary data for late transient export; no target-driven native decisions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import traceback

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+".pending."+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf8");os.replace(temp,path)

def main():
    p=argparse.ArgumentParser();p.add_argument("--base-src",type=Path,required=True)
    p.add_argument("--config",type=Path,required=True);p.add_argument("--case-id",required=True)
    p.add_argument("--out",type=Path,required=True);p.add_argument("--parent",type=Path)
    a=p.parse_args();sys.path.insert(0,str(a.base_src.resolve()));sys.path.insert(0,str(Path(__file__).resolve().parent))
    from late_order_export import LateExportSession
    from integracion.relational_pair import physical,move
    from dee_thinking import _native as d
    import dee_thinking
    if dee_thinking.__version__!="4.5.0"or sha(d.__file__)!="17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d"or not Path(dee_thinking.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError("Official isolated instrument required")
    config=json.loads(a.config.read_text(encoding="utf8"));case=next(x for x in config["cases"]if x["id"]==a.case_id)
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=None
    m={"schema":"CPC9.late_export.measurements.v1","case":case,"configuration_sha256":sha(a.config),
        "status":"RUNNING","preparations":int(not a.parent),"continuations":int(bool(a.parent)),"diagnostic_forks":0,
        "frames":[],"local":[],"gates":[],"snapshots":[],"host_RAW_clock_edits_on_MAIN":[],
        "coverage":"Moore27 at body/anticipated transport boundaries; uncovered routes have no assigned unique genealogy.",
        "engine":{"version":dee_thinking.__version__,"module":dee_thinking.__file__,"native_sha256":sha(d.__file__),"python":sys.executable}}
    sources={}
    for name,module in list(sys.modules.items()):
        path=getattr(module,"__file__",None)
        if path and Path(path).suffix==".py"and(Path(path).resolve().is_relative_to(a.base_src.resolve())or Path(path).resolve().is_relative_to(Path(__file__).resolve().parent)):
            sources[str(Path(path).resolve())]=sha(path)
    m["source_sha256_before_execution"]=sources
    try:
        if a.parent:
            s=LateExportSession.load(a.parent);m["parent"]={"path":str(a.parent),"sha256":sha(a.parent),"physical":physical(s.world)}
        else:
            s=LateExportSession.create(identifier=a.case_id,**case.get("preparation",{}));s.curriculum(**case.get("curriculum",{}))
        m["geometry"]=s.geometry;m["initial_physical"]=physical(s.world)
        def save():
            path=a.out/("T"+str(s.tick)+".deetsnap.gz");storage=s.save(path)
            m["snapshots"].append({"path":path.name,"tick":s.tick,"sha256":sha(path),"bytes":path.stat().st_size,"physical":physical(s.world),"storage":storage})
        save();g=s.geometry["late_order_export"]
        boundaries=set(range(468,478))|{g["association_tick"]-1,g["association_tick"],g["query_tick"]-1,g["query_tick"],g["use_tick"]-1,g["use_tick"],549,616}
        for tick in sorted(t for t in boundaries if s.tick<t<=case.get("horizon",616)):
            s.run_until(tick);m["frames"].append(s.view())
            centers=[("body."+key,site)for key,site in s.geometry["body"].items()]if tick<=477 else[]
            if 470<=tick<=477:
                centers +=[("nominal."+item["id"],move(s.geometry["body"]["center"],item["vector_before_record"],tick-470))for item in g["surfaces"]]
            for role,site in centers:
                m["local"].append({"tick":tick,"role":role,"center":site,"Moore27":[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
                gate=d.inspect_write_gate(s.world.runtime,d.Coordinate(*site),True)
                m["gates"].append({"tick":tick,"role":role,"site":site,"gate":{key:getattr(gate,key)for key in("absolute_tick","local_clock","center_available","n_active","hadron","rule_value","survives_material_rule","semantic_protected","write_protected","k","period","phase_remainder","ordinary_increment_condition","branch","demux_status")}})
            if tick in(470,g["association_tick"],616):save()
            m.update(last_complete_tick=s.tick,requests=s.receipts(),late_export_observations=s.state["late_export_observations"],elapsed_seconds=time.monotonic()-started);put(a.out/"MEASUREMENTS.json",m)
        m.update(status="EXECUTED",final_physical=physical(s.world))
    except BaseException as error:
        m.update(status="TECHNICAL_ERROR",error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:m.update(last_complete_tick=s.tick,requests=s.receipts(),late_export_observations=s.state["late_export_observations"],elapsed_seconds=time.monotonic()-started)
        m["sources_unchanged_during_execution"]=all(sha(path)==digest for path,digest in sources.items())
        put(a.out/"MEASUREMENTS.json",m)
    print(json.dumps({"id":case["id"],"status":m["status"],"seconds":m["elapsed_seconds"],
        "body470":next((frame["body"]for frame in m["frames"]if frame["tick"]==470),None),
        "late":[{"tick":row["tick"],"stage":row["stage"],"states":[{"id":item["id"],"direction":item["physical"]["direction"],"load":item["physical"]["s_reg"]}for item in row["surfaces"]]}for row in m["late_export_observations"]if not row["stage"].startswith("pre_")]}),flush=True)

if __name__=="__main__":main()
