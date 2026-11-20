#!/usr/bin/env python3
"""Generate opaque CORE15 expansion challenges from OS entropy after source freeze."""
from __future__ import annotations
import hashlib, itertools, json, secrets, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from extension_common import ROOT, canonical_hash, read_json, sha, utc, write_json


def main():
    out=ROOT/"NEW_FRESH_CHALLENGES"/"CHALLENGE_MANIFEST.json"
    if out.exists(): print(out.read_text(encoding="utf-8")); return
    freeze_path=ROOT/"SOURCE_FREEZE_EXPANSION.json"; freeze=read_json(freeze_path)
    for rel,expected in freeze["source_hashes"].items():
        if sha(ROOT/rel)!=expected: raise RuntimeError(f"source freeze invalid: {rel}")
    seed_bytes=secrets.token_bytes(32); seed_hex=seed_bytes.hex(); seed_hash=hashlib.sha256(seed_bytes).hexdigest(); rng=np.random.default_rng(int.from_bytes(seed_bytes,"big")); cases=[]
    def add_case(claim,role,cfg):
        opaque="T_"+hashlib.sha256((seed_hex+claim+role+str(len(cases))).encode()).hexdigest()[:12].upper(); cases.append({"trial_id":opaque,"claim_id":claim,"role":role,"configuration":cfg,"configuration_hash":canonical_hash(cfg)})
    base_offsets=[(0,0,0),(0,0,3),(0,3,0),(0,3,3),(0,6,0),(0,6,3),(0,3,6),(0,6,6)]
    dirs=[d for d in itertools.product((-1,0,1),repeat=3) if d!=(0,0,0)]
    for i in range(8):
        n=int(rng.choice([27,33,39,43])); d=dirs[int(rng.integers(0,len(dirs)))]; count=int(rng.integers(4,9)); cfg={"n":n,"direction":d,"origin":[int(x) for x in rng.integers(8,n-9,size=3)],"offsets":base_offsets[:count],"sreg_base":int(rng.integers(1,300)),"sreg_step":int(rng.integers(1,19)),"state_base":int(rng.integers(1000,100000)),"horizon":int(rng.integers(5,10))}; add_case("C15XC01","POSITIVE",cfg); add_case("C15XC01","CANARY",cfg)
    for i in range(8):
        k=int(rng.integers(2,11)); selected=[dirs[j] for j in rng.choice(len(dirs),size=k,replace=False)]; cfg={"n":int(rng.choice([21,25,29])),"center":[11,11,11],"directions":selected,"loads":[int(x) for x in rng.integers(1,6000,size=k)],"state_base":int(rng.integers(1000,100000))}; cfg["center"]=[cfg["n"]//2]*3; add_case("C15XC02","POSITIVE",cfg); add_case("C15XC02","CANARY",cfg)
    for i in range(8):
        cfg={"n":int(rng.choice([19,25,31])),"count":int(rng.integers(6,28)),"seed":int(rng.integers(0,2**63))}; add_case("C15XC03","POSITIVE",cfg); add_case("C15XC03","CANARY",cfg)
    mechanisms=["singleton","source","collision","guard","ensemble","singleton","source","guard"]
    for i,mech in enumerate(mechanisms):
        n=int(rng.choice([27,31,35])); cfg={"n":n,"center":[n//2]*3,"mechanism":mech,"horizon":int(rng.integers(6,13))}; add_case("C15XC04","POSITIVE",cfg); add_case("C15XC04","CANARY",cfg)
    axes=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1),(1,0,0),(0,1,0)]
    for d in axes:
        n=int(rng.choice([33,37,41])); dist=int(rng.integers(5,9)); down=int(rng.integers(3,6)); cfg={"n":n,"center":[n//2]*3,"direction":d,"source_distance":dist,"downstream_distance":down,"horizon":dist+down+12,"sreg":int(rng.integers(1,19665))}; add_case("C15XC05","POSITIVE",cfg); add_case("C15XC05","CANARY",cfg)
    for i in range(8):
        n=int(rng.choice([29,35,41])); d=dirs[int(rng.integers(0,len(dirs)))]; distance=int(rng.integers(4,10)); source=[n//3,n//3,n//3]; cfg={"n":n,"direction":d,"distance":distance,"source":source,"sreg":int(rng.integers(1,19665))}; add_case("C15XC06","POSITIVE",cfg); add_case("C15XC06","CANARY",cfg)
    seed_record={"source":"os.urandom via secrets.token_bytes","seed_hex":seed_hex,"seed_sha256":seed_hash,"generated_utc":utc(),"source_freeze_sha256":freeze["freeze_sha256"]}; write_json(ROOT/"NEW_FRESH_CHALLENGES"/"CHALLENGE_SEED.json",seed_record); manifest={"schema":"dee.v27.core15.expansion.challenge.v1","source_freeze_sha256":freeze["freeze_sha256"],"seed_sha256":seed_hash,"case_count":len(cases),"cases":cases,"opaque_ids":True,"manual_case_picking":False,"generated_utc":utc()}; manifest["content_sha256"]=canonical_hash(manifest); write_json(out,manifest); write_json(ROOT/"CHECKPOINTS"/"D2_CHALLENGES_GENERATED.json",{"checkpoint":"D2_CHALLENGES_GENERATED","pass":True,"case_count":len(cases),"seed_sha256":seed_hash,"manifest_sha256":sha(out),"completed_utc":utc()}); print(json.dumps({"case_count":len(cases),"seed_sha256":seed_hash,"manifest_sha256":sha(out)},indent=2))


if __name__=="__main__": main()
