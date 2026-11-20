"""Generate previously nonexistent CORE15 holdout worlds after source freeze."""
from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core15_common import ROOT, canonical_hash, read_json, sha, utc, write_json


def verify_freeze():
    freeze=read_json(ROOT/"SOURCE_FREEZE.json");bad=[]
    for row in freeze["files"]:
        path=ROOT/row["path"]
        if not path.is_file() or sha(path)!=row["sha256"]:bad.append(row["path"])
    if bad:raise RuntimeError(f"source freeze invalid: {bad}")
    return freeze


def interior(rng,n,margin):
    return [int(x) for x in rng.integers(margin,n-margin,size=3)]


def different_direction(rng,d1):
    dirs=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    return list(dirs[(dirs.index(tuple(d1))+int(rng.integers(1,len(dirs))))%len(dirs)])


def build(seed_bytes):
    seed=int.from_bytes(seed_bytes,"big");rng=np.random.default_rng(seed);trials=[];ordinal=0
    def add_trial(family,config):
        nonlocal ordinal;ordinal+=1;tid=f"T_{hashlib.sha256(seed_bytes+ordinal.to_bytes(4,'big')).hexdigest()[:10].upper()}";config["trial_id"]=tid;trials.append({"trial_id":tid,"family":family,"config":config,"run_positive":True,"run_canary":True})
    for _ in range(3):
        n=int(rng.choice([29,31,35,37,41]));d1=list([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)][int(rng.integers(6))]);add_trial("direction",{"n":n,"q":interior(rng,n,7),"d1":d1,"d2":different_direction(rng,d1),"state":int(rng.integers(1,2**31)),"sreg":int(rng.integers(31,700))})
    for _ in range(3):
        n=int(rng.choice([31,35,39,43]));d=int(rng.integers(5,9));s1=int(rng.integers(17,400));b1=int(rng.integers(17,400));b2=int(rng.integers(401,900));add_trial("payload",{"n":n,"center":interior(rng,n,10),"distance":d,"sreg_a":s1,"sreg_b1":b1,"sreg_b2":b2})
    for _ in range(3):
        n=int(rng.choice([37,41,43,47]));direction=list([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)][int(rng.integers(6))]);add_trial("semantic",{"n":n,"source":interior(rng,n,11),"direction":direction,"distance":int(rng.integers(7,11)),"sreg":int(rng.integers(61,500))})
    for _ in range(3):
        n=int(rng.choice([29,31,35,39]));direction=list([(1,0,0),(0,1,0),(0,0,1)][int(rng.integers(3))]);add_trial("clock",{"n":n,"q":interior(rng,n,8),"direction":direction,"canary_direction":different_direction(rng,direction),"state":int(rng.integers(1,2**31)),"sreg":int(rng.integers(41,700)),"clock":int(rng.integers(2**40,2**63,dtype=np.uint64)),"horizon":int(rng.integers(7,13))})
    for _ in range(3):
        n=int(rng.choice([43,47,49,53]));direction=list([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)][int(rng.integers(6))]);add_trial("guard_geometry",{"n":n,"center":interior(rng,n,13),"direction":direction,"source_distance":int(rng.integers(8,12)),"downstream_distance":7,"horizon":32,"sreg":int(rng.integers(71,600))})
    for _ in range(3):
        n=int(rng.choice([20,23,26]));add_trial("ensemble_direction",{"n":n,"fill":float(rng.choice([.22,.35,.48,.62])),"seed":int(rng.integers(1,2**31)),"direction":[1,0,0]})
    for _ in range(3):
        n=int(rng.choice([43,47,49,53]));L=int(rng.integers(7,11));axes=[int(x) for x in rng.permutation(3)];add_trial("phase_history",{"n":n,"path_length":L,"center":interior(rng,n,13),"sregs":[int(rng.integers(61,300)),int(rng.integers(301,700))],"frame":axes})
    for i in range(3):
        n=int(rng.choice([41,45,49,53]));axes=[int(x) for x in rng.permutation(3)];signs=[int(x) for x in rng.choice([-1,1],size=3)];add_trial("ordered_history",{"index":10+i,"n":n,"seed":int(rng.integers(1,2**31)),"junction":interior(rng,n,10),"frame_axes":axes,"frame_signs":signs,"train_tick":int(rng.integers(4,7)),"delay":int(rng.integers(12,19)),"states":[int(x) for x in rng.integers(1,2**32,size=4,dtype=np.uint64)],"clocks":[int(x) for x in rng.integers(0,2**63,size=4,dtype=np.uint64)]})
    return trials


def main():
    out=ROOT/"FRESH_CHALLENGES"/"CHALLENGE_WAVE_A.json"
    if out.exists():print(out.read_text(encoding="utf-8"));return
    freeze=verify_freeze();seed_bytes=secrets.token_bytes(32);trials=build(seed_bytes)
    write_json(ROOT/"FRESH_CHALLENGES"/"CHALLENGE_SEED.json",{"generation_utc":utc(),"seed_hex":seed_bytes.hex(),"seed_sha256":hashlib.sha256(seed_bytes).hexdigest(),"generator_sha256":sha(Path(__file__)),"source_freeze_sha256":sha(ROOT/"SOURCE_FREEZE.json")})
    manifest={"wave":"A","generated_after_source_freeze":True,"generation_utc":utc(),"source_freeze_sha256":sha(ROOT/"SOURCE_FREEZE.json"),"trial_count":len(trials),"families":sorted(set(x["family"] for x in trials)),"trials":trials,"manifest_hash":canonical_hash(trials)}
    write_json(out,manifest);print(json.dumps({"wave":"A","trial_count":len(trials),"manifest_hash":manifest["manifest_hash"]},indent=2))


if __name__=="__main__":main()
