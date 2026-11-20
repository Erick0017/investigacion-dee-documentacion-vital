"""Run frozen CORE15 shadow holdouts and causal canaries on fresh worlds."""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from core15_common import ROOT,audit_kernel,canonical_hash,read_json,sha,update_state,utc,write_json
from core15_holdout_engine import execute
from native_core import verify_and_load_kernel


def verify_freeze():
    freeze=read_json(ROOT/"SOURCE_FREEZE.json");bad=[]
    for row in freeze["files"]:
        p=ROOT/row["path"]
        if not p.exists() or sha(p)!=row["sha256"]:bad.append(row["path"])
    if bad:raise RuntimeError(f"source freeze invalid: {bad}")
    return freeze


def verify_locks():
    locks=[]
    for p in sorted((ROOT/"HOLDOUT_LOCKS").glob("C15H*.json")):
        lock=read_json(p)
        expected=lock["self_sha256_precommit"];probe=dict(lock);probe["self_sha256_precommit"]=""
        if canonical_hash(probe)!=expected:raise RuntimeError(f"lock hash mismatch {p.name}")
        locks.append(lock)
    if len(locks)!=4:raise RuntimeError(f"expected four locks, got {len(locks)}")
    return locks


def main():
    out=ROOT/"RESULTS"/"C15H00_FRESH_HOLDOUT_SUMMARY.json"
    if out.exists():print(out.read_text(encoding="utf-8"));return
    started=time.perf_counter();freeze=verify_freeze();locks=verify_locks();manifest=read_json(ROOT/"FRESH_CHALLENGES"/"CHALLENGE_WAVE_A.json")
    if manifest["source_freeze_sha256"]!=sha(ROOT/"SOURCE_FREEZE.json"):raise RuntimeError("challenge/freeze mismatch")
    audit_kernel("CORE15_BEFORE_HOLDOUT");kernel,env=verify_and_load_kernel(1);positives=[];canaries=[]
    for trial in manifest["trials"]:
        pos=execute(kernel,trial,False);pos.update({"trial_id":trial["trial_id"],"role":"FRESH_POSITIVE","observed_from":"kernel telemetry"});positives.append(pos)
        can=execute(kernel,trial,True);can.update({"trial_id":trial["trial_id"]+"_C","role":"CAUSAL_CANARY","observed_from":"kernel telemetry"});canaries.append(can)
    for row in positives:write_json(ROOT/"RAW_OR_SPARSE_TELEMETRY"/(row["trial_id"]+".json"),row)
    for row in canaries:write_json(ROOT/"CANARIES"/(row["trial_id"]+".json"),row)
    by_family={}
    for family in sorted(set(x["family"] for x in positives)):
        p=[x for x in positives if x["family"]==family];c=[x for x in canaries if x["family"]==family];by_family[family]={"positive_pass":sum(x["pass"] for x in p),"positive_total":len(p),"canary_pass":sum(x["pass"] for x in c),"canary_total":len(c),"pass":all(x["pass"] for x in p+c)}
    gates={
      "C15H01_SHADOW_COMPONENT_NECESSITY":all(by_family[x]["pass"] for x in ("direction","payload","semantic","guard_geometry","phase_history","ordered_history")),
      "C15H02_DIRECTIONAL_ENSEMBLE_RESPONSE":by_family["ensemble_direction"]["pass"],
      "C15H03_CLOCK_RESIDUAL_BOUNDED_INVISIBILITY":by_family["clock"]["pass"],
      "C15H04_COUPLED_SHADOW_PANEL":all(x["pass"] for x in by_family.values()),
    }
    summary={"module":"C15H00_FRESH_HOLDOUT_SUMMARY","role":"FROZEN_CONFIRMATION","source_freeze":sha(ROOT/"SOURCE_FREEZE.json"),"challenge_manifest":sha(ROOT/"FRESH_CHALLENGES"/"CHALLENGE_WAVE_A.json"),"fresh_trials":len(positives),"fresh_pass":sum(x["pass"] for x in positives),"canaries":len(canaries),"canaries_correct":sum(x["pass"] for x in canaries),"by_family":by_family,"gates":gates,"all_gates_pass":all(gates.values()),"post_hoc_repairs":0,"elapsed_seconds":time.perf_counter()-started,"completed_utc":utc()}
    write_json(ROOT/"RESULTS"/"C15H01_SHADOW_COMPONENT_NECESSITY.json",{"gate":gates["C15H01_SHADOW_COMPONENT_NECESSITY"],"families":{k:by_family[k] for k in ("direction","payload","semantic","guard_geometry","phase_history","ordered_history")},"lock_sha256":sha(ROOT/"HOLDOUT_LOCKS"/"C15H01_SHADOW_COMPONENT_NECESSITY.json")})
    write_json(ROOT/"RESULTS"/"C15H02_DIRECTIONAL_ENSEMBLE_RESPONSE.json",{"gate":gates["C15H02_DIRECTIONAL_ENSEMBLE_RESPONSE"],"family":by_family["ensemble_direction"],"lock_sha256":sha(ROOT/"HOLDOUT_LOCKS"/"C15H02_DIRECTIONAL_ENSEMBLE_RESPONSE.json")})
    write_json(ROOT/"RESULTS"/"C15H03_CLOCK_RESIDUAL_BOUNDED_INVISIBILITY.json",{"gate":gates["C15H03_CLOCK_RESIDUAL_BOUNDED_INVISIBILITY"],"family":by_family["clock"],"lock_sha256":sha(ROOT/"HOLDOUT_LOCKS"/"C15H03_CLOCK_RESIDUAL_BOUNDED_INVISIBILITY.json")})
    write_json(ROOT/"RESULTS"/"C15H04_COUPLED_SHADOW_PANEL.json",{"gate":gates["C15H04_COUPLED_SHADOW_PANEL"],"families":by_family,"lock_sha256":sha(ROOT/"HOLDOUT_LOCKS"/"C15H04_COUPLED_SHADOW_PANEL.json")})
    write_json(out,summary);audit_kernel("CORE15_AFTER_HOLDOUT");update_state(status="HOLDOUTS_COMPLETE",completed_modules=["C15A01","C15D00","C15H00"],last_completed="C15H00_FRESH_HOLDOUT_SUMMARY",fresh_holdouts=len(positives),canaries=len(canaries))
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
