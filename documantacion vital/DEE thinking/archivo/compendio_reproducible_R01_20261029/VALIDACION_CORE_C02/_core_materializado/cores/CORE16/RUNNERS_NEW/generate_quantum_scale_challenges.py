#!/usr/bin/env python3
from __future__ import annotations
import itertools,json,secrets,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core16x_common import ROOT,canonical_hash,read_json,update_state,utc,write_json
def main():
    lock=read_json(ROOT/"HOLDOUT_LOCKS"/"QUANTUM_SCALE_LOCK.json")
    macro=[]
    for i,size in enumerate((2,6,12,20,30)):
        shifted=max(1,size//2);macro.append({"id":f"M{i}","size":size,"n":(43,47,53)[i%3],"horizon":24,"shifted_fraction":shifted/size,"entropy_tag":secrets.token_hex(8)})
    configs=[];base_d0=(1,0,0);base_a=(-1,1,0);base_b=(1,-1,0)
    all_cfg=[]
    for p in itertools.permutations((0,1,2)):
        for signs in itertools.product((-1,1),repeat=3):
            tr=lambda v:tuple(signs[i]*v[p[i]] for i in range(3));all_cfg.append((tr(base_d0),tr(base_a),tr(base_b)))
    rng=secrets.SystemRandom();rng.shuffle(all_cfg)
    for i,(d0,a,b) in enumerate(all_cfg[:24]):configs.append({"id":f"A{i}","d0":d0,"a":a,"b":b,"n":(33,39,45)[i%3]})
    payload={"challenge_set":"C16X-QUANTUM-SCALE-FINAL-V1","generated_utc":utc(),"entropy_source":"OS entropy","lock_sha256":lock["lock_sha256"],"macro":macro,"algebra":configs};payload["challenge_sha256"]=canonical_hash({k:v for k,v in payload.items() if k!="challenge_sha256"});write_json(ROOT/"FINAL_HOLDOUTS"/"QUANTUM_SCALE_CHALLENGES.json",payload);update_state(status="QUANTUM_SCALE_CHALLENGES_GENERATED",current_phase="RUN_QUANTUM_SCALE_HOLDOUT",quantum_scale_challenge_sha256=payload["challenge_sha256"]);print(json.dumps({"macro":len(macro),"algebra":len(configs),"sha256":payload["challenge_sha256"]},indent=2))
if __name__=="__main__":main()

