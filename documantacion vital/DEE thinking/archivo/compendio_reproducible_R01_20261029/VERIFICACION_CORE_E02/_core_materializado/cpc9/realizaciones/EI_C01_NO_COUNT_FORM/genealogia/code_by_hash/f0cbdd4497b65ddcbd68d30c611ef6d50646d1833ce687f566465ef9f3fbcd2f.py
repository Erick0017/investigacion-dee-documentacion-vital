"""Data-only source/uint64/finite-v27 branch checks. Never imported by participant."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

KERNEL_SHA="fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"
MOORE=[v for v in itertools.product((-1,0,1),repeat=3)if v!=(0,0,0)]
TETRA=[((sx,0,0),(0,sy,0),(0,0,sz),(sx,sy,sz))for sx in(-1,1)for sy in(-1,1)for sz in(-1,1)]
MASK=(1<<64)-1
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pack(state,load,v,semantic):return str(state|(load<<32)|((v[0]&15)<<48)|((v[1]&15)<<52)|((v[2]&15)<<56)|((semantic&15)<<60))
def sign(x):return int(x>0)-int(x<0)
def one_step(rows):
    center=rows[13];site=center["site"];n=67
    by={tuple((r["site"][i]-site[i]+n//2)%n-n//2 for i in range(3)):r for r in rows}
    if len(by)!=27:raise ValueError("Full Moore27 required")
    neighbours=[by[offset]for offset in MOORE]
    if any(r["s_reg"]>=19664 for r in rows):raise ValueError("Possible fusion/second-order delta outside bounded local checker")
    alive=lambda r:r["state"]>0 and r["semantic"]!=5
    active=[r for r in neighbours if alive(r)]
    gradient=[-sum(offset[i]*by[offset]["s_reg"]for offset in MOORE if by[offset]["state"]>0)for i in range(3)]
    if center["semantic"]==4:return{"branch":"OBSERVER_PRESERVED","raw":center["raw"],"clock":str((int(center["clock"])+1)&MASK)}
    if center["state"]==0:
        if active and sum(abs(x)for x in gradient)//19665>=int(9.887*9.887*9.887)and not any(r["semantic"]==5 for r in neighbours):
            raise ValueError("Crystallization branch outside this finite low-gradient checker")
        symmetric=all(alive(by[offset])==alive(by[tuple(-v for v in offset)])for offset in MOORE)
        if symmetric and len(active)>=8:return{"branch":"EMPTY_XNOR","raw":pack(1,1,(0,0,0),7),"clock":str((int(center["clock"])+1)&MASK)}
        sources=[r for r in neighbours if any(r["direction"])and[(r["site"][i]+r["direction"][i])%n for i in range(3)]==site]
        if sources:
            load=min(sum(r["s_reg"]for r in sources),19664)
            direction=[sign(sum(r["direction"][i]for r in sources))for i in range(3)]
            return{"branch":"EMPTY_DEMUX_"+str(len(sources)),"sources":[{"site":r["site"],"raw":r["raw"],"load":r["s_reg"],"direction":r["direction"]}for r in sources],
                "raw":pack(1,load,direction,1),"clock":str((int(center["clock"])+1)&MASK)}
        return{"branch":"EMPTY_NO_SOURCE","raw":"0","clock":str((int(center["clock"])+1)&MASK)}
    hadron=any(all(alive(by[offset])for offset in pattern)for pattern in TETRA)
    tension=16.0 if hadron and len(active)<7 else 2.5
    rule=math.floor(len(active)*tension/26.0+0.5)
    if rule==0:return{"branch":"OCCUPIED_MATERIAL_DECAY_NO_DEMUX","raw":"0","clock":str((int(center["clock"])+1)&MASK)}
    protected=len(active)>=7 and all(sum(r["direction"][i]for r in active)==0 for i in range(3))
    load=center["s_reg"];increment=False;k=8-len(active)
    if not protected and 0<k<=8:
        period=max(782//k,1);increment=int(center["clock"])%period==0
        load+=int(increment)
    if load>=19665:raise ValueError("Fusion branch not certified")
    direction=[sign(x)for x in gradient]if any(center["direction"])or center["semantic"]==5 else[0,0,0]
    return{"branch":"OCCUPIED_MATERIAL","n_active":len(active),"hadron":hadron,"write_protected":protected,"increment":increment,
        "gradient":gradient,"raw":pack(rule,load,direction,center["semantic"] or 1),"clock":str((int(center["clock"])+1)&MASK)}

def main():
    p=argparse.ArgumentParser();p.add_argument("--front",type=Path,required=True);p.add_argument("--base-src",type=Path,required=True)
    p.add_argument("--kernel",type=Path,required=True);a=p.parse_args()
    if sha(a.kernel)!=KERNEL_SHA:raise RuntimeError("Kernel source mismatch")
    files={}
    for directory in(a.front/"src",a.base_src):
        for path in directory.rglob("*.py"):files.setdefault(sha(path),[]).append(str(path))
    sources={};unresolved=[];cases=[];branches=[];invalid=[];exact_count=0
    def check(value,path=""):
        nonlocal exact_count
        if isinstance(value,dict):
            for key,item in value.items():
                if key.lower()in("raw","clock"):
                    if isinstance(item,str)and item.isdigit() and 0<=int(item)<=MASK:exact_count+=1
                    elif isinstance(item,int) and 0<=item<=MASK:exact_count+=1
                    else:invalid.append({"field":path+"/"+key,"value":item})
                else:check(item,path+"/"+key)
        elif isinstance(value,list):
            for index,item in enumerate(value):check(item,path+"/"+str(index))
    for path in sorted((a.front/"resultados").glob("*/MEASUREMENTS.json")):
        m=json.loads(path.read_text(encoding="utf8"));check(m,path.parent.name)
        for key in("source_sha256","source_sha256_before_execution"):
            for name,digest in m.get(key,{}).items():
                sources.setdefault(digest,{"declared_paths":set(),"available":files.get(digest,[])})["declared_paths"].add(name)
                if digest not in files:unresolved.append({"primary":path.parent.name,"source":name,"sha256":digest})
        cases.append({"id":path.parent.name,"schema":m["schema"],"status":m["status"],"sha256":sha(path),
            "preparations":m.get("preparations",0),"continuations":m.get("continuations",0),"diagnostic_forks":m.get("diagnostic_forks",0),"last_complete_tick":m.get("last_complete_tick"),"final_physical":m.get("final_physical")})
        for field,key in(("decisive_destination_coverage","bank"),("counterflow_local","port"),("local","id")):
            if field=="local" and m["schema"]=="CPC9.late_export.measurements.v1":
                continue
            pairs={}
            for index,row in enumerate(m.get(field,[])):
                identity=(row.get(key),tuple(row["center"]));pairs.setdefault(identity,{})[row["tick"]]=(index,row)
            for identity,ticks in pairs.items():
                for tick,(index,pre)in ticks.items():
                    if tick+1 not in ticks:continue
                    postindex,post=ticks[tick+1]
                    try:
                        result=one_step(pre["Moore27"]);actual=post["Moore27"][13]
                        branches.append({"primary":str(path.relative_to(a.front)),"field":field,"identity":identity[0],"pre_tick":tick,
                            "pre_locator":field+"/"+str(index),"post_locator":field+"/"+str(postindex),"reconstruction":result,
                            "observed_raw":actual["raw"],"observed_clock":actual["clock"],"exact_match":result["raw"]==actual["raw"]and result["clock"]==actual["clock"]})
                    except ValueError as error:branches.append({"primary":str(path.relative_to(a.front)),"field":field,"pre_tick":tick,"not_certified":str(error)})
        # Fixed-site pre/post observations include the complete current
        # neighbours; teaching/probe inputs were applied three ticks earlier.
        # This never joins moving carriers by proximity or equal load.
        for field in("counterprop_observations","tiled_order_observations","order_social_observations"):
            pairs={}
            for index,row in enumerate(m.get(field,[])):
                for bankindex,item in enumerate(row.get("surfaces",row.get("banks",[]))):
                    if "Moore27"not in item:continue
                    identity=(item["id"],tuple(item["physical"]["site"]))
                    pairs.setdefault(identity,{})[row["tick"]]=(index,bankindex,item)
            for identity,ticks in pairs.items():
                for tick,(index,bankindex,pre)in ticks.items():
                    if tick+1 not in ticks:continue
                    postindex,postbankindex,post=ticks[tick+1]
                    try:
                        result=one_step(pre["Moore27"]);actual=post["physical"]
                        branches.append({"primary":str(path.relative_to(a.front)),"field":field,"identity":identity[0],"pre_tick":tick,
                            "pre_locator":field+"/"+str(index)+"/bank/"+str(bankindex),"post_locator":field+"/"+str(postindex)+"/bank/"+str(postbankindex),
                            "reconstruction":result,"observed_raw":actual["raw"],"observed_clock":actual["clock"],
                            "exact_match":result["raw"]==actual["raw"]and result["clock"]==actual["clock"]})
                    except ValueError as error:branches.append({"primary":str(path.relative_to(a.front)),"field":field,"pre_tick":tick,"not_certified":str(error)})
    for value in sources.values():value["declared_paths"]=sorted(value["declared_paths"])
    out={"schema":"CPC9.front_relations.data_audit.v1","engine_imported":False,"kernel_source_sha256":sha(a.kernel),
        "checker_scope":"Finite low-load local transitions only. Local sources cannot reach fusion; no staged current inputs may be omitted. TemporalF1 body boundaries with current-event injection are not fed to this checker. No unique message genealogies inferred.",
        "cases":cases,"source_hashes":sources,"unresolved_sources":unresolved,"exact_integer_fields":exact_count,"invalid_integer_fields":invalid,
        "certified_local_branches":branches,"counts":{"terminal_containers":len(cases),"preparations":sum(x["preparations"]for x in cases),"continuations":sum(x["continuations"]for x in cases),"diagnostic_forks":sum(x["diagnostic_forks"]for x in cases),
            "branch_matches":sum(x.get("exact_match",False)for x in branches),"branch_mismatches":sum(x.get("exact_match")is False for x in branches)}}
    path=a.front/"revision/PRIMARY_AUDIT.json";path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({"counts":out["counts"],"invalid_uint64":len(invalid),"unresolved_sources":len(unresolved)}))
if __name__=="__main__":main()
