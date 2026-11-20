"""Freeze CORE15 observer, claims, evaluators and source before fresh worlds exist."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from core15_common import ROOT,canonical_hash,read_json,sha,update_state,utc,write_json,write_text


def make_lock(claim_id,text,predicate,scope,falsifier):
    path=ROOT/"HOLDOUT_LOCKS"/(claim_id+".json")
    body={"claim_id":claim_id,"created_utc":utc(),"role":"FROZEN_BEFORE_CHALLENGE_GENERATION","claim":text,"observer":"S_CAUSAL_PANEL_V1 components declared in FROZEN_OBSERVER_SPEC.json","apparatus":"family-specific rules in core15_holdout_engine.py","metric":"exact family predicate; no fitted tolerance","threshold":"all three fresh trials and their paired canaries pass","prediction":predicate,"scope":scope,"canary_semantics":"positive changes one named hidden coordinate; canary keeps it fixed (clock canary changes raw direction to verify discrimination)","falsifier":falsifier,"fresh_world_rule":"OS-entropy seed; admissible N/geometry/range fixed by challenge generator","post_hoc_change_allowed":False}
    write_json(path,{**body,"self_sha256_precommit":"PENDING"});temp=read_json(path);temp["self_sha256_precommit"]="";digest=canonical_hash(temp)
    # Stable self-check is the hash of the lock with an empty self field; runner recomputes this convention.
    body["self_sha256_precommit"]=digest;write_json(path,body);write_text(path.with_suffix(".sha256"),sha(path)+"  "+path.name+"\n")
    return path


def main():
    freeze_path=ROOT/"SOURCE_FREEZE.json"
    if freeze_path.exists():print(freeze_path.read_text(encoding="utf-8"));return
    discovery=read_json(ROOT/"RESULTS"/"C15D00_SHADOW_DISCOVERY_SUMMARY.json")
    candidates=[
      {"observer_id":"M_OCCUPANCY","components":["occupied coordinates"],"discovery_score":1,"causal_score":0,"complexity":1,"status":"REJECTED_AS_GENERAL_SHADOW","reason":"fails direction, payload, semantic, guard, phase and history ambiguities"},
      {"observer_id":"M_EVENT_CAUSAL","components":["route","tick","s_reg","direction","phase","target occupancy","guard count"],"discovery_score":6,"causal_score":6,"complexity":7,"status":"RETAINED_EVENT_SECTOR","reason":"strong transport/interface observer but misses associative/coupling context"},
      {"observer_id":"M_HISTORY","components":["ordered lineage","training relation","target history"],"discovery_score":2,"causal_score":2,"complexity":3,"status":"RETAINED_HISTORY_SECTOR","reason":"necessary for later query response"},
      {"observer_id":"M_MATTER_REL","components":["support geometry","semantic topology","direction distribution","functional response"],"discovery_score":3,"causal_score":3,"complexity":4,"status":"RETAINED_MATTER_SECTOR","reason":"distinguishes capture/regeneration/dissipation"},
      {"observer_id":"S_CAUSAL_PANEL_V1","components":["route/geometry","direction field","s_reg payload","semantic/source class","relative phase","target history","guard topology","ordered lineage","coupling context"],"discovery_score":8,"causal_score":8,"complexity":9,"status":"FROZEN_CROSS_PHENOMENON_CANDIDATE","reason":"small union of causally necessary coordinates across eight distinct ambiguities; task-relative components may be omitted when their intervention is absent"},
      {"observer_id":"M_Q0","components":["full raw","full clock"],"discovery_score":8,"causal_score":8,"complexity":100,"status":"TRIVIAL_BASELINE","reason":"sufficient but not reduced"},
    ]
    write_json(ROOT/"OBSERVER_SHADOW_CANDIDATES.json",{"candidates":candidates,"selected":"S_CAUSAL_PANEL_V1","selection":"highest causal coverage under explicit component cost; no learned threshold"})
    write_json(ROOT/"OBSERVER_SEARCH_LEDGER.json",{"discovery_data":"C15D01-D08 only","holdout_data_used":False,"candidates":candidates,"combinations_examined":6,"powerset_search":False,"freeze_utc":utc()})
    write_json(ROOT/"FROZEN_OBSERVER_SPEC.json",{"observer_id":"S_CAUSAL_PANEL_V1","form":"small family of coupled task-relative shadows, not one scalar","components":candidates[4]["components"],"selection_rule":"include a component only when ablation creates a demonstrated equivalence failure in that causal domain","prediction":"family-specific projections preserve eight frozen response predicates","full_state_required":False,"clock_component":"retained as residual metadata but predicted behaviorally unnecessary for singleton raw trajectory in frozen horizon","no_external_label":True})
    locks=[
      make_lock("C15H01_SHADOW_COMPONENT_NECESSITY","Occupancy/bulk shadows are incomplete across six independent interaction families; the named hidden coordinate changes the fresh response.","direction, payload, semantic, guard geometry, phase/history and ordered lineage each yield predicted divergence; identical-coordinate canary does not","fresh admissible worlds in six frozen mechanism classes","any positive lacks predicted divergence or any identical-coordinate canary diverges"),
      make_lock("C15H02_DIRECTIONAL_ENSEMBLE_RESPONSE","Direction distribution is necessary to predict the material-like ensemble response at fixed support, s_reg, semantic and clock.","mixed worlds contract; aligned worlds translate exactly; identical aligned canary does not diverge","semantic1 sparse ensemble N20/23/26 and declared fills","mixed world does not contract, aligned translation fails, or identical canary diverges"),
      make_lock("C15H03_CLOCK_RESIDUAL_BOUNDED_INVISIBILITY","A source-clock difference persists but does not alter the raw singleton trajectory in the frozen panel.","raw trajectories equal and clock trajectories differ; raw-direction canary is detected as divergent","single semantic1 carrier, N29-39, horizon7-12","clock-only pair changes raw trajectory or raw-difference canary is missed"),
      make_lock("C15H04_COUPLED_SHADOW_PANEL","The frozen coupled shadow family discriminates all eight causal families without the full Q0 state.","every fresh positive and paired causal canary passes its exact predicate","union of eight declared task domains; no global closure claim","any constituent family gate fails"),
    ]
    # Freeze all executable source before challenge worlds are generated.
    files=[]
    for p in sorted((ROOT/"RUNNERS").glob("*.py")):
        if p.name==Path(__file__).name:continue
        files.append({"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"size":p.stat().st_size})
    source={"created_utc":utc(),"challenge_worlds_existed_at_freeze":False,"observer":"S_CAUSAL_PANEL_V1","locks":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p)} for p in locks],"files":files,"post_freeze_changes_forbidden":True,"source_hash":canonical_hash(files)}
    write_json(freeze_path,source);update_state(status="SOURCE_FROZEN",last_completed="C15_SOURCE_FREEZE",source_freeze_sha256=sha(freeze_path));print(json.dumps(source,indent=2))


if __name__=="__main__":main()
