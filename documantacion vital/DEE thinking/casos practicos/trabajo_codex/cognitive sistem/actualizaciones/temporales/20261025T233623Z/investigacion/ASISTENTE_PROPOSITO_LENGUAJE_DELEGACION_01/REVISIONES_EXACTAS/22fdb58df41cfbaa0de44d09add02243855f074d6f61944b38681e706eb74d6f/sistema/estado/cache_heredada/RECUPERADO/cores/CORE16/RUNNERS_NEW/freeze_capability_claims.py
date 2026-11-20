#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core16x_common import ROOT,audit_kernel,canonical_hash,read_json,sha256_file,update_state,utc,write_json
def main():
    audit_kernel("CORE16X_CAPABILITY_SOURCE_FREEZE");d=read_json(ROOT/"DISCOVERY"/"CAPABILITY_FUNCTIONAL_LEVEL.json")
    if d["functional_level_test"]["disposition"]!="L2_FUNCTIONAL_SUBBRANCH_SUPPORTED_PENDING_FRESH_FREEZE":raise RuntimeError("functional gate failed")
    names=("run_capability_functional_level.py","run_capability_holdout.py","native_runtime_x.py");sources={n:sha256_file(ROOT/"RUNNERS_NEW"/n) for n in names}
    lock={"lock_id":"C16X-LOCK-FUNCTIONAL-CAPABILITY-V1","frozen_utc":utc(),"discovery_sha256":canonical_hash(d),"source_hashes":sources,"challenge_instances_exist_at_freeze":False,"claims":[
        {"claim_id":"C16X006","claim":"A compressed learned response class is destructively reinstantiated at a route/distance-selected prepared receiver through an observed local carrier corridor.","threshold":"all trained positives and causal controls correct","prediction":"PASS"},
        {"claim_id":"C16X007","claim":"Center regeneration is repeatable with intact eight-corner semantic4 topology and fails after a required corner is removed.","threshold":"all primary worlds all cycles; all missing-corner controls null","prediction":"PASS"},
        {"claim_id":"C16X008","claim":"One semantic4 cell at the ordered k5/k6 interface boundary selects a train-level transmission/blocking outcome.","threshold":"all fresh k5 transmit and k6 block","prediction":"PASS"}],"external_access":"UNKNOWN_NOT_PART_OF_INTERNAL_CLAIMS"}
    lock["lock_sha256"]=canonical_hash({k:v for k,v in lock.items() if k!="lock_sha256"});write_json(ROOT/"HOLDOUT_LOCKS"/"FUNCTIONAL_CAPABILITY_LOCK.json",lock);update_state(status="CAPABILITY_FROZEN",current_phase="GENERATE_CAPABILITY_CHALLENGES",capability_lock_sha256=lock["lock_sha256"]);print(json.dumps({"lock":lock["lock_id"],"sha256":lock["lock_sha256"]},indent=2))
if __name__=="__main__":main()

