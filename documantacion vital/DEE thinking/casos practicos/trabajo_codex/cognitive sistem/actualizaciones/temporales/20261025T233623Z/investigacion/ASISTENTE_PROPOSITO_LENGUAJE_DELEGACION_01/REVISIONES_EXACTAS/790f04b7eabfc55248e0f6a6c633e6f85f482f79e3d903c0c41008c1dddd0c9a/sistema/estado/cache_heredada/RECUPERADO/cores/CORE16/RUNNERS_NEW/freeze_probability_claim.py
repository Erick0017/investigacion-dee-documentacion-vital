#!/usr/bin/env python3
from __future__ import annotations
import json,secrets,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core16x_common import ROOT,audit_kernel,canonical_hash,read_json,sha256_file,update_state,utc,write_json

def main():
    audit_kernel("CORE16X_PROBABILITY_SOURCE_FREEZE")
    refinement=read_json(ROOT/"MODEL_SELECTION"/"PROBABILITY_BRANCH_REFINEMENT.json")
    if refinement["summary"]["model_exact_scores"]["M4_branch_union"]!=refinement["summary"]["trials"]:raise RuntimeError("branch law not selected")
    names=("run_probability_measure_discovery.py","run_probability_branch_refinement.py","run_probability_holdout.py","native_runtime_x.py")
    sources={n:sha256_file(ROOT/"RUNNERS_NEW"/n) for n in names}
    lock={"lock_id":"C16X-LOCK-PROBABILITY-BRANCH-V1","frozen_utc":utc(),"source_hashes":sources,"selection_result_sha256":canonical_hash(refinement),"challenge_instances_exist_at_freeze":False,
          "claim":{"claim_id":"C16X003","claim":"For the tested semantic1 ensemble family, effective next-support probability is induced by the declared microstate preparation measure and a deterministic branch-union law (incoming destinations, surviving incumbents, and XNOR births where present), not by support alone.","metric":"exact predicted next support in every fresh binary trial; at least 6/8 uniform-vs-clustered pairs TV>0.05","threshold":"all binary trials exact and measure sensitivity gate passes","prediction":"PASS"},
          "canary":"Aligned uniform sources remain destination-bijection negative anchors; scrambling preparation labels must not preserve paired distributions by construction."}
    lock["lock_sha256"]=canonical_hash({k:v for k,v in lock.items() if k!="lock_sha256"});write_json(ROOT/"HOLDOUT_LOCKS"/"PROBABILITY_MEASURE_LOCK.json",lock)
    update_state(status="PROBABILITY_FROZEN",current_phase="GENERATE_PROBABILITY_CHALLENGES",probability_lock_sha256=lock["lock_sha256"])
    print(json.dumps({"lock":lock["lock_id"],"sha256":lock["lock_sha256"]},indent=2))
if __name__=="__main__":main()

