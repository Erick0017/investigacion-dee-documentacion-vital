#!/usr/bin/env python3
from __future__ import annotations
import itertools,json,secrets,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core16x_common import ROOT,canonical_hash,read_json,update_state,utc,write_json
def main():
    lock=read_json(ROOT/"HOLDOUT_LOCKS"/"FUNCTIONAL_CAPABILITY_LOCK.json");rng=secrets.SystemRandom();perms=list(itertools.permutations((0,1,2)));signs=list(itertools.product((-1,1),repeat=3));transfer=[]
    for i in range(8):transfer.append({"id":f"T{i}","seed":secrets.randbelow(900000)+100000,"n":(29,33,37)[i%3],"distance":(6,8,10)[i%3],"permutation":rng.choice(perms),"signs":rng.choice(signs)})
    regen=[]
    for i in range(6):
        n=(21,25,29)[i%3];regen.append({"id":f"R{i}","seed":secrets.randbelow(900000)+100000,"n":n,"center":[rng.randrange(4,n-4) for _ in range(3)],"cycles":8})
    dirs=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1));guard=[]
    for i,d in enumerate(dirs):
        n=(33,37,41)[i%3];guard.append({"id":f"G{i}","n":n,"center":[n//2]*3,"direction":d,"sreg":rng.randrange(1,19665)})
    payload={"challenge_set":"C16X-CAPABILITY-FINAL-V1","generated_utc":utc(),"entropy_source":"OS entropy","lock_sha256":lock["lock_sha256"],"transfer":transfer,"regeneration":regen,"guard":guard};payload["challenge_sha256"]=canonical_hash({k:v for k,v in payload.items() if k!="challenge_sha256"});write_json(ROOT/"FINAL_HOLDOUTS"/"CAPABILITY_CHALLENGES.json",payload);update_state(status="CAPABILITY_CHALLENGES_GENERATED",current_phase="RUN_CAPABILITY_HOLDOUT",capability_challenge_sha256=payload["challenge_sha256"]);print(json.dumps({"transfer":len(transfer),"regeneration":len(regen),"guard":len(guard),"sha256":payload["challenge_sha256"]},indent=2))
if __name__=="__main__":main()

