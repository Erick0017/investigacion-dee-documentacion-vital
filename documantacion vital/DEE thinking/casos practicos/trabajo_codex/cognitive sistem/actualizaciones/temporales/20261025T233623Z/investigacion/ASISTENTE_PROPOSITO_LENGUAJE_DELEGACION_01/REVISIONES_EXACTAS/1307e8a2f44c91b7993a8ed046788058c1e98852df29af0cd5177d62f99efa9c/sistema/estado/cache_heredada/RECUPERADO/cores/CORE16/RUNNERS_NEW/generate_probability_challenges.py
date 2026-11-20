#!/usr/bin/env python3
from __future__ import annotations
import json,secrets,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core16x_common import ROOT,canonical_hash,read_json,update_state,utc,write_json
def main():
    lock=read_json(ROOT/"HOLDOUT_LOCKS"/"PROBABILITY_MEASURE_LOCK.json");classes=[]
    for n in (11,17):
        for k in (12,26):
            for mode in ("balanced","mixed"):
                for prep in ("uniform","clustered"):
                    classes.append({"class_id":f"P-{n}-{k}-{mode}-{prep}","seed":secrets.randbits(64),"n":n,"support":k,"mode":mode,"preparation":prep,"samples":32})
    for n in (11,17):
        for prep in ("uniform","clustered"):
            classes.append({"class_id":f"ANCHOR-{n}-18-aligned-{prep}","seed":secrets.randbits(64),"n":n,"support":18,"mode":"aligned","preparation":prep,"samples":16})
    payload={"challenge_set":"C16X-PROBABILITY-FINAL-UNTOUCHED-V1","generated_utc":utc(),"entropy_source":"OS entropy via secrets","lock_sha256":lock["lock_sha256"],"classes":classes};payload["challenge_sha256"]=canonical_hash({k:v for k,v in payload.items() if k!="challenge_sha256"})
    write_json(ROOT/"FINAL_HOLDOUTS"/"PROBABILITY_CHALLENGES.json",payload);update_state(status="PROBABILITY_CHALLENGES_GENERATED",current_phase="RUN_PROBABILITY_FINAL_HOLDOUT",probability_challenge_sha256=payload["challenge_sha256"])
    print(json.dumps({"classes":len(classes),"binary_trials":sum(x["samples"] for x in classes),"challenge_sha256":payload["challenge_sha256"]},indent=2))
if __name__=="__main__":main()

