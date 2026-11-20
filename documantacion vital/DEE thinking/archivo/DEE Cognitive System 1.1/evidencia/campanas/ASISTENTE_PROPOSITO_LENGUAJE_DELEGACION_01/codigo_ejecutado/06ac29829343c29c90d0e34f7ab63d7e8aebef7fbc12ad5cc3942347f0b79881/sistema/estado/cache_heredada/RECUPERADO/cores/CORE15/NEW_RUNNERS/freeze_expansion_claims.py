#!/usr/bin/env python3
"""Freeze promoted expansion claims and all confirmation source before challenges exist."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from extension_common import ROOT, audit_kernel, canonical_hash, sha, update_state, utc, write_json


def main():
    marker=ROOT/"CHECKPOINTS"/"D_SOURCE_FREEZE_COMPLETE.json"
    if marker.exists(): print(marker.read_text(encoding="utf-8")); return
    challenge_dir=ROOT/"NEW_FRESH_CHALLENGES"
    if any(challenge_dir.iterdir()): raise RuntimeError("fresh challenge artifacts already exist before source freeze")
    audit_kernel("CORE15_EXPANSION_BEFORE_SOURCE_FREEZE")
    claims=[
      {"claim_id":"C15XC01","text":"A sparse multi-record semantic1 constellation preserves relational geometry and payload-defined functional identity under unit-step translation in the frozen scope.","scope":"fresh N/directions/shapes declared by generator; collision robustness excluded","observer":"normalized occupied-coordinate set plus payload multiset","metric":"exact equality every tick","prediction":"positive exact; one reversed constituent canary not exact","source_discovery":["C15X001","C15X017"],"epistemic_level":"L2"},
      {"claim_id":"C15XC02","text":"Simultaneous semantic1 arrivals obey exact capped local payload accounting at the destination.","scope":"declared multiplicities/directions/s_reg; simultaneous arrival","observer":"destination record s_reg","metric":"observed == min(sum inputs,19664)","prediction":"simultaneous positive; temporally resolved canary not simultaneous sum","source_discovery":["C15X008","C15X018","C15X023"],"epistemic_level":"L1"},
      {"claim_id":"C15XC03","text":"Unique destination count closes one-step support for sparse semantic1 worlds whose proposed destinations are empty at t0.","scope":"declared fresh N/count worlds; empty-destination prerequisite","observer":"proposal-destination equivalence classes","metric":"next support == unique destinations","prediction":"positive inside scope; occupied-destination canary breaks relation","source_discovery":["C15X007","C15X015","C15X022"],"epistemic_level":"L2"},
      {"claim_id":"C15XC04","text":"Pure clock differences remain raw-trajectory invisible across the frozen five-mechanism panel.","scope":"singleton/source/reducer/guard/ensemble preparations and horizons","observer":"complete raw hash trajectory","metric":"tickwise equality","prediction":"clock-only positive equality; raw-direction canary divergence","source_discovery":["C15R03","C15X009","C15X021"],"epistemic_level":"L1","refines":"C15R03"},
      {"claim_id":"C15XC05","text":"The organized semantic4 guard blocks the declared incident trains across payload/orientation while equal-inventory shuffled structure transmits.","scope":"guard apparatus, declared orientations/payloads","observer":"downstream event list","metric":"empty for organized, nonempty for shuffled canary","prediction":"organized blocked; shuffled canary transmits","source_discovery":["C15X013","C15X020"],"epistemic_level":"L2"},
      {"claim_id":"C15XC06","text":"Finite semantic1 pulse delay is payload-independent unit-step transport in the frozen directions and sizes.","scope":"declared finite pulses; no universal dispersion claim","observer":"first detector occupancy tick","metric":"arrival tick == route distance","prediction":"positive unit delay; mouth-block canary violates arrival relation","source_discovery":["C15X019"],"epistemic_level":"L1"},
    ]
    for c in claims:
        c.update({"apparatus_frozen":True,"probe_frozen":True,"observer_frozen":True,"metric_frozen":True,"threshold_frozen":True,"time_window_frozen":True,"prediction_frozen":True,"canary_semantics":{"causal_prerequisite":c["scope"],"intervention":c["prediction"].split(";")[-1].strip(),"expected_consequence":c["prediction"]}})
        write_json(ROOT/"NEW_HOLDOUT_LOCKS"/f"{c['claim_id']}.json",c)
    write_json(ROOT/"CLAIM_LEDGER_EXPANSION_DISCOVERY.json",{"claims":claims,"status":"FROZEN_PENDING_FRESH","baseline_claims_untouched":["C15R01","C15R02","C15R03","C15R04"]})
    files=[]
    for p in sorted((ROOT/"NEW_RUNNERS").glob("*.py")): files.append(p)
    for p in sorted((ROOT/"NEW_HOLDOUT_LOCKS").glob("*.json")): files.append(p)
    hashes={str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in files}
    freeze={"schema":"dee.v27.core15.expansion.freeze.v1","frozen_utc":utc(),"claims":[c["claim_id"] for c in claims],"source_hashes":hashes,"fresh_challenges_existed_at_freeze":False,"runner":"NEW_RUNNERS/run_expansion_holdouts.py","generator":"NEW_RUNNERS/generate_expansion_challenges.py","post_freeze_change_policy":"invalidate challenges and refreeze"}; freeze["freeze_sha256"]=canonical_hash(freeze); write_json(ROOT/"SOURCE_FREEZE_EXPANSION.json",freeze); write_json(marker,{"checkpoint":"D_SOURCE_FREEZE_COMPLETE","pass":True,"claims_frozen":len(claims),"files_frozen":len(hashes),"freeze_sha256":freeze["freeze_sha256"],"completed_utc":utc()}); update_state(status="SOURCE_FROZEN_PENDING_CHALLENGES",promoted_new_claims=len(claims),source_freeze_sha256=freeze["freeze_sha256"]); print(json.dumps(freeze,indent=2,sort_keys=True))


if __name__=="__main__": main()

