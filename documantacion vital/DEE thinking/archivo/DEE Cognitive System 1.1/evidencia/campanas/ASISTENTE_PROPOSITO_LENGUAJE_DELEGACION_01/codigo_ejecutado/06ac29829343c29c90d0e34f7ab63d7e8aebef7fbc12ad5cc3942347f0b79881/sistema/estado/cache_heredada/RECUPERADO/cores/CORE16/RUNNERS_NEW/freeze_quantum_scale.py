#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core16x_common import ROOT,audit_kernel,canonical_hash,read_json,sha256_file,update_state,utc,write_json
def main():
    audit_kernel("CORE16X_QUANTUM_SCALE_SOURCE_FREEZE");selection=read_json(ROOT/"MODEL_SELECTION"/"QUANTUM_SCALE_REFINEMENT.json");s=selection["summary"]
    if s["macro_time_readable"]!=s["macro_sizes"] or s["algebra_model_exact"]!=s["algebra_cases"]:raise RuntimeError("selection gates failed")
    names=("run_quantum_multilevel_discovery.py","run_quantum_scale_refinement.py","run_quantum_scale_holdout.py","native_runtime_x.py")
    sources={n:sha256_file(ROOT/"RUNNERS_NEW"/n) for n in names};lock={"lock_id":"C16X-LOCK-QUANTUM-SCALE-V1","frozen_utc":utc(),"selection_sha256":canonical_hash(selection),"source_hashes":sources,"challenge_instances_exist_at_freeze":False,"claims":[
        {"claim_id":"C16X004","claim":"Period-two routed phase remains encoded in organized source banks and can be hidden by time-integrated observation yet recovered by time/lane-resolved detection.","metric":"same integrated total, different time and lane phase readout","threshold":"all fresh sizes pass","prediction":"PASS"},
        {"claim_id":"C16X005","claim":"Sequential direction-response interventions realize the frozen classical transformation T_d(s)=sign(s+d), including noncommuting compositions.","metric":"binary final directions equal algebraic prediction for AB and BA","threshold":"all fresh cases exact and AB!=BA","prediction":"PASS"}],"quantum_interpretation":"NOT_PART_OF_CLAIMS"}
    lock["lock_sha256"]=canonical_hash({k:v for k,v in lock.items() if k!="lock_sha256"});write_json(ROOT/"HOLDOUT_LOCKS"/"QUANTUM_SCALE_LOCK.json",lock);update_state(status="QUANTUM_SCALE_FROZEN",current_phase="GENERATE_QUANTUM_SCALE_CHALLENGES",quantum_scale_lock_sha256=lock["lock_sha256"]);print(json.dumps({"lock":lock["lock_id"],"sha256":lock["lock_sha256"]},indent=2))
if __name__=="__main__":main()

