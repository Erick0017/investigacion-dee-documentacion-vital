"""Recalculate exact observable signatures; auditor only, no engine import."""
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(r):
    return {key:r[key]for key in("tick","site","raw","clock","state","s_reg","semantic","direction")if key in r}
def main():
    p=argparse.ArgumentParser();p.add_argument("--front",type=Path,required=True);a=p.parse_args()
    rows=[];raw={}
    for path in sorted((a.front/"resultados").glob("*/MEASUREMENTS.json")):
        m=json.loads(path.read_text(encoding="utf8"));schema=m.get("schema","")
        if not any(v in schema for v in("counterprop","tiled_order","order_social","late_export")):continue
        identity=path.parent.name;raw[identity]=m;c=m.get("case",{});curr=c.get("curriculum",{});alpha=curr.get("a_load",3);beta=curr.get("b_load",3)
        data={"id":identity,"primary":str(path.relative_to(a.front)),"sha256":sha(path),"schema":schema,"status":m["status"],
          "preparations":m.get("preparations",0),"continuations":m.get("continuations",0),"diagnostic_forks":m.get("diagnostic_forks",0),
          "curriculum":curr,"last_complete_tick":m.get("last_complete_tick"),"final_physical":m.get("final_physical"),
          "sources_unchanged":m.get("sources_unchanged_during_execution"),"requests":{},"stages":{},"old_joint616":None}
        receiptrows=m.get("requests",[]);receiptrows=receiptrows if isinstance(receiptrows,list)else []
        data["requests"]={"requested":len(receiptrows),"status_counts":{s:sum(row.get("receipt",{}).get("status")==s for row in receiptrows)for s in sorted({row.get("receipt",{}).get("status","")for row in receiptrows})},"payload_total":sum(row.get("payload",0)for row in receiptrows)}
        for field in("counterprop_observations","tiled_order_observations","order_social_observations","late_export_observations"):
            for index,row in enumerate(m.get(field,[])):
                if row.get("stage","").startswith("pre_"):continue
                surfaces=row.get("surfaces",row.get("banks",[]))
                data["stages"][field+":"+str(row.get("stage"))]={"tick":row.get("tick"),"locator":field+"/"+str(index),
                  "states":{item["id"]:compact(item["physical"])for item in surfaces}}
        for frame in m.get("frames",[]):
            if frame.get("tick")==616:
                data["old_joint616"]={key:compact(item["delivery_site"])for key,item in frame.get("joint",{}).items()}
        if "parallel"in schema or "order_social"in schema:
            delta=curr.get("interval",5)*(1 if curr.get("tile_order","AB")=="AB"else -1);bank="d"+str(delta)
            data["auditor_expected_bank"]={"bank":bank,"derivation":"Known presented occurrence order and interval, used by auditor after trajectory, never injected as a participant response"}
            criteria={"record":((0,1,0),5+alpha+beta),"read":((0,1,1),12+alpha+beta),"use":((0,0,1),23+alpha+beta)}
            data["exact_source_signature_matches"]={}
            for name,(vector,load)in criteria.items():
                stage=data["stages"].get("tiled_order_observations:"+name,{});obs=stage.get("states",{}).get(bank)
                data["exact_source_signature_matches"][name]=None if obs is None else obs["direction"]==list(vector)and obs["s_reg"]==load
            if "order_social"in schema:
                criteria={"record":((0,1,0),28+alpha+beta),"read":((0,1,-1),35+alpha+beta),"use":((0,0,-1),46+alpha+beta)}
                data["exact_receiver_signature_matches"]={}
                for name,(vector,load)in criteria.items():
                    obs=data["stages"].get("order_social_observations:"+name,{}).get("states",{}).get(bank)
                    data["exact_receiver_signature_matches"][name]=None if obs is None else obs["direction"]==list(vector)and obs["s_reg"]==load
        rows.append(data)
    restore=[]
    for base,others in(("CP_D01_AB",("CP_MEMORY_sham","CP_RESTORE481","CP_MEMORY_cut")),
      ("TP_D01_AB_I5",("TP_MEMORY_sham","TP_MEMORY_restore","TP_MEMORY_cut")),
      ("OS_D01_AB_I5",("OS_MESSAGE_sham","OS_RESTORE555","OS_MESSAGE_cut"))):
        if base not in raw:continue
        for name in others:
            if name not in raw:continue
            left=raw[base];right=raw[name]
            restore.append({"reference":base,"comparison":name,"RAW_equal":left.get("final_physical",{}).get("RAW_sha256")==right.get("final_physical",{}).get("RAW_sha256"),
              "clocks_equal":left.get("final_physical",{}).get("clocks_sha256")==right.get("final_physical",{}).get("clocks_sha256"),"parent_unchanged":right.get("parent_unchanged"),"edit":right.get("edit")})
    report={"schema":"CPC9.relations.observable_recalculation.v1","engine_imported":False,"participant_uses_this_file":False,
      "formulas":{"load_counterprop":"record=5+a+b;query=12+a+b;use=23+a+b","load_social":"receiver_record=28+a+b;query=35+a+b;use=46+a+b",
       "coverage":"A signature match requires exact direction AND load, not merely nonzero","retained_oldword":"At tick616 inspect all four oldjoint delivery sites and report exact signatures; expected historical default plus.changed=(0,1,1),load115"},
      "interpretive_limits":["No automatic semantic or cognitive verdicts.","Fresh individuals with their own cue pairing do not demonstrate old learned-word interval transfer.","Auxiliary world panels are not the main E1 life.","Fullstate equality uses complete RAW/clocks digests at equal finaltick, not equality of a selected summary."],
      "counts":{"containers":len(rows),"preparations":sum(r["preparations"]for r in rows),"continuations":sum(r["continuations"]for r in rows),"diagnostic_forks":sum(r["diagnostic_forks"]for r in rows)},"cases":rows,"state_comparisons":restore}
    target=a.front/"revision/RELACIONES_RECALCULO.json";target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({"counts":report["counts"],"comparisons":restore},ensure_ascii=False))
if __name__=="__main__":main()
