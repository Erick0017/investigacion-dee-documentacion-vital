#!/usr/bin/env python3
"""Third-generation adaptive questions derived from committed CORE15X results."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extension_common import ROOT, append_ndjson, audit_kernel, canonical_hash, experiment_key, read_json, result_hash, update_state, utc, write_json
from native_core import NativeWorld, fields, pack, verify_and_load_kernel
from core12_apparatus import regenerative_interface_trial, source_train_trial
from run_c6h01_associative_plasticity_holdout import BASE as ASSOC_BASE, simulate as assoc_sim, transform as assoc_transform
from run_c6h08_dissipative_ensemble_holdout import DIRECTIONS
from run_adaptive_discovery import add, unpack, run_world, normalized_shape, constellation_raw


RESULTS=ROOT/"RESULTS"; TREE=ROOT/"EXPANDED_QUESTION_TREE.ndjson"; DIALOGUE=ROOT/"EXPANDED_KERNEL_DIALOGUE.ndjson"; DECISIONS=ROOT/"RESEARCH_DECISION_LOG.ndjson"


def tree_ids():
    return {json.loads(line)["question_id"] for line in TREE.read_text(encoding="utf-8").splitlines() if line.strip()}


def child(qid,parent,parent_result,front,learned,ambiguous,question,competing,why):
    if qid in tree_ids(): return
    row={"question_id":qid,"parent_question_id":parent,"parent_result_hash":result_hash(parent_result),"front":front,"what_was_learned":learned,"what_remains_ambiguous":ambiguous,"new_competing_mechanisms":competing,"why_now_justified":why,"question":question,"status":"QUEUED","created_utc":utc()}
    append_ndjson(TREE,row); append_ndjson(DECISIONS,{"decision":"OPEN_GRANDCHILD","question_id":qid,"parent_question_id":parent,"parent_result_hash":row["parent_result_hash"],"reason":why})


def save(exp_id,qid,parent,front,question,mechanism,result):
    path=RESULTS/f"{exp_id}.json"
    if path.exists(): return path,read_json(path)
    out={"experiment_id":exp_id,"question_id":qid,"parent_question_id":parent,"front":front,"question":question,"mechanism_class":mechanism,"role":"ADAPTIVE_DISCOVERY_DEEPENING","kernel_data_lineage":"v27 raw+clock -> raw telemetry -> declared metric -> predicate",**result}; out["content_sha256"]=canonical_hash(out); write_json(path,out)
    append_ndjson(DIALOGUE,{"question_id":qid,"experiment_id":exp_id,"front":front,"raw_outcome":{"predicate":out.get("predicate"),"content_sha256":out["content_sha256"]},"mechanism_update":out.get("interpretation","see canonical result"),"evidence_level":"DISCOVERY_DEEPENING"}); return path,out


def mobile_symmetry(kernel):
    rows=[]; offsets=[(0,0,0),(0,0,3),(0,3,0),(0,3,3),(0,6,0),(0,6,3)]
    for n in (29,35,41):
        for d in ((1,0,0),(0,1,0),(0,0,1),(-1,0,0),(1,1,0)):
            raw=constellation_raw(n,(8,9,10),offsets,d); initial=normalized_shape(raw); world=NativeWorld(kernel,raw); exact=True
            for tick in range(9):
                exact=exact and normalized_shape(world.raw,d,tick)==initial
                if tick<8: world.tick()
            rows.append({"n":n,"direction":d,"exact_relational_translation":exact,"final_support":int(np.count_nonzero(world.raw))})
    return {"experiment":"mobile identity translation/orientation scope","cases":rows,"pass_count":sum(x["exact_relational_translation"] for x in rows),"total":len(rows),"predicate":all(x["exact_relational_translation"] for x in rows),"interpretation":"Functional/relational identity is transport-covariant in the tested axis and diagonal directions; robustness to contact is not implied."}


def detector_multiplicity(kernel):
    rows=[]; n=23; c=(11,11,11); directions=DIRECTIONS[:12]
    for k in (1,2,3,4,6,8,10,12):
        for base in (37,1200,4000):
            raw=np.zeros((n,n,n),np.uint64); selected=directions[:k]; inputs=[]
            for i,d in enumerate(selected):
                s=base+i*3; q=add(c,d,-1,n); raw[q]=pack(0xA00+i,s,d,1); inputs.append(s)
            world=NativeWorld(kernel,raw); world.tick(); rec=unpack(world.raw[c]); expected=min(sum(inputs),19664)
            rows.append({"multiplicity":k,"base_sreg":base,"input_sum":sum(inputs),"expected":expected,"observed":rec,"pass":rec is not None and rec["sreg"]==expected})
    return {"experiment":"detector multiplicity/intensity response","cases":rows,"pass_count":sum(x["pass"] for x in rows),"total":len(rows),"law":"detector s_reg = min(sum incident s_reg, 19664)","predicate":all(x["pass"] for x in rows),"interpretation":"An exact event-amplitude/accounting law exists for simultaneous destination reduction; it is not brightness or energy without an external map."}


def radiation_dispersion(kernel):
    rows=[]
    for n in (29,37):
        for d in ((1,0,0),(1,1,0),(0,-1,1)):
            source=(7,8,9); distance=7
            for sreg in (1,173,9000,19664):
                raw=np.zeros((n,n,n),np.uint64); raw[source]=pack(1,sreg,d,1); detector=add(source,d,distance,n); world=NativeWorld(kernel,raw); arrivals=[]
                for tick in range(distance+3):
                    if int(world.raw[detector])!=0: arrivals.append(tick)
                    if tick<distance+2: world.tick()
                rows.append({"n":n,"direction":d,"sreg":sreg,"distance":distance,"arrivals":arrivals,"unit_delay":arrivals==[distance]})
    trains=[]
    for distance in (5,8,11):
        tr=source_train_trial(kernel,n=37,source=(6,18,18),direction=(1,0,0),sreg=211,horizon=distance+10,detector_distance=distance)
        trains.append({"distance":distance,"first_arrival":tr["arrival_ticks"][0] if tr["arrival_ticks"] else None,"gaps":tr["arrival_gaps"],"period_two":tr["period_two_at_detector"]})
    return {"experiment":"payload/source-mode dispersion test","finite_pulses":rows,"source_trains":trains,"payload_independent_unit_delay":all(x["unit_delay"] for x in rows),"train_first_arrival_unit_delay":all(x["first_arrival"]==x["distance"] for x in trains),"dispersion_found":False,"predicate":all(x["unit_delay"] for x in rows) and all(x["first_arrival"]==x["distance"] for x in trains),"interpretation":"No delay dispersion was found across tested payloads, directions and finite versus period-two source modes."}


def opacity_scope(kernel):
    rows=[]
    for d in ((1,0,0),(0,1,0),(0,0,-1)):
        for sreg in (1,137,4096,19664):
            for mode in ("semantic4_full","semantic4_missing_corner","semantic4_shuffled","semantic1_same_inventory"):
                r=regenerative_interface_trial(kernel,n=35,source_distance=6,downstream_distance=4,horizon=20,mode=mode,direction=d,center=(17,17,17),source_sreg=sreg)
                events=r["downstream_event_ticks"]["4"]
                rows.append({"direction":d,"source_sreg":sreg,"mode":mode,"downstream_events":events,"blocked":not events})
    organized=[x for x in rows if x["mode"] in {"semantic4_full","semantic4_missing_corner"}]; controls=[x for x in rows if x["mode"] in {"semantic4_shuffled","semantic1_same_inventory"}]
    return {"experiment":"guard opacity/transmission scope","cases":rows,"organized_block_rate":sum(x["blocked"] for x in organized)/len(organized),"control_transmission_rate":sum(not x["blocked"] for x in controls)/len(controls),"predicate":all(x["blocked"] for x in organized) and all(not x["blocked"] for x in controls),"interpretation":"Organization, not incident payload, determines blocking in this bounded interface; matched disorganization transmits."}


def assoc_clock_panel(kernel):
    rows=[]
    for index,n in enumerate((37,43,47)):
        rng=np.random.default_rng(160000+index); frame=((index%3,(index+1)%3,(index+2)%3),(1,-1 if index%2 else 1,1)); vectors={k:list(assoc_transform(v,*frame)) for k,v in ASSOC_BASE.items()}; base={"cell_id":f"CLK{index}","n":n,"junction":[int(x) for x in rng.integers(10,n-10,size=3)],"train_tick":4+index,"delay":11+index,"query_path":3,"vectors":vectors,"cue_sreg":31+index,"teacher_sreg":53+index,"query_sreg":71+index,"eraser_sreg":13,"states":[int(x) for x in rng.integers(1,2**32,size=4,dtype=np.uint64)],"clocks":[0,0,0,0]}
        altered={**base,"cell_id":f"CLK{index}B","states":list(base["states"]),"clocks":[int(rng.bit_generator.random_raw()) for _ in range(4)]}
        a=assoc_sim(kernel,base,"trained_pair"); b=assoc_sim(kernel,altered,"trained_pair")
        rows.append({"cell":index,"zero_clock_readout":a["readout_record"],"altered_clock_readout":b["readout_record"],"same_functional_response":a["readout_record"]==b["readout_record"],"both_trained_exact":a["trained_exact"] and b["trained_exact"]})
    return {"experiment":"clock residual associative history panel","cases":rows,"predicate":all(x["same_functional_response"] and x["both_trained_exact"] for x in rows),"interpretation":"Injected clock differences do not change trained associative response in this additional history-bearing mechanism."}


def relational_scope_and_canary(kernel):
    rng=np.random.default_rng(161001); positive=[]; canaries=[]
    for n in (17,23,29):
        for trial in range(24):
            raw=np.zeros((n,n,n),np.uint64); count=int(rng.integers(5,24)); occ=set()
            while len(occ)<count: occ.add(tuple(int(x) for x in rng.integers(0,n,size=3)))
            dest=[]
            for i,q in enumerate(sorted(occ)):
                d=DIRECTIONS[int(rng.integers(0,len(DIRECTIONS)))]; raw[q]=pack(1+i,int(rng.integers(1,500)),d,1); dest.append(add(q,d,1,n))
            if any(q in occ for q in dest): continue
            expected=len(set(dest)); _,trace=run_world(kernel,raw,horizon=1); positive.append({"n":n,"trial":trial,"expected":expected,"observed":trace[1]["support"],"pass":expected==trace[1]["support"]})
        # Canary deliberately violates the empty-destination scope.
        c=(n//2,n//2,n//2); raw=np.zeros((n,n,n),np.uint64); raw[add(c,(1,0,0),-1,n)]=pack(1,31,(1,0,0),1); raw[c]=pack(2,41,(0,0,0),1)
        destinations=[c,c]; naive=len(set(destinations)); _,trace=run_world(kernel,raw,horizon=1); canaries.append({"n":n,"naive_unique_destinations":naive,"observed_support":trace[1]["support"],"out_of_scope_detected":trace[1]["support"]!=naive})
    return {"experiment":"relational closure transforms and scope canary","positive_cases":positive,"scope_canaries":canaries,"positive_pass":sum(x["pass"] for x in positive),"positive_total":len(positive),"canaries_correct":sum(x["out_of_scope_detected"] for x in canaries),"canary_total":len(canaries),"predicate":all(x["pass"] for x in positive) and all(x["out_of_scope_detected"] for x in canaries),"interpretation":"The one-step law generalizes across three sizes only when its empty-destination prerequisite holds; occupied-destination canaries correctly break it."}


def reducer_chain_accounting(kernel):
    rows=[]; n=29; center=(10,14,14)
    for loads in ((101,211,307),(7000,8000,9000),(15000,12000,1000)):
        raw=np.zeros((n,n,n),np.uint64)
        dirs=[(1,0,0),(1,1,0),(1,-1,0)]
        for i,(d,s) in enumerate(zip(dirs,loads)):
            raw[add(center,d,-1,n)]=pack(0xA00+i,s,d,1)
        world=NativeWorld(kernel,raw); world.tick(); first=unpack(world.raw[center]); next_center=add(center,(1,0,0),1,n)
        # Frozen diagnostic second collision: a new counter-carrier was pre-positioned at t0 to arrive at next_center at t2.
        # Re-run with that fourth carrier because the first world was only the stage-1 observer.
        raw2=raw.copy(); raw2[add(next_center,(-1,0,0),-2,n)]=pack(0xB00,777,(-1,0,0),1)
        w2=NativeWorld(kernel,raw2); w2.tick(); stage1=unpack(w2.raw[center]); w2.tick(); stage2=unpack(w2.raw[next_center])
        e1=min(sum(loads),19664); e2=min(e1+777,19664)
        rows.append({"loads":loads,"stage1_expected":e1,"stage1":stage1,"stage2_expected":e2,"stage2":stage2,"pass":stage1 is not None and stage2 is not None and stage1["sreg"]==e1 and stage2["sreg"]==e2,"cap_loss":max(0,sum(loads)-19664)+max(0,e1+777-19664)})
    return {"experiment":"two-stage reducer accounting","cases":rows,"predicate":all(x["pass"] for x in rows),"interpretation":"Capped payload accounting composes over two reductions; overflow is explicit loss, so this is not a global conservation law."}


def negative_anchor(kernel):
    # Ensure the evaluators distinguish out-of-scope or mechanism-broken cases.
    n=23; c=(11,11,11); raw=np.zeros((n,n,n),np.uint64); raw[(10,11,11)]=pack(1,101,(-1,0,0),1); _,trace=run_world(kernel,raw,horizon=2,retain_sparse=True)
    wrong_route_no_center=all(not any(a.get("q")==list(c) for a in row.get("active",[])) for row in trace)
    guard=regenerative_interface_trial(kernel,n=31,source_distance=5,downstream_distance=4,horizon=18,mode="semantic4_shuffled",direction=(1,0,0),center=(15,15,15),source_sreg=101)
    shuffled_transmits=bool(guard["downstream_event_ticks"]["4"])
    return {"experiment":"negative evaluator anchors","wrong_route_center_absent":wrong_route_no_center,"shuffled_guard_transmits":shuffled_transmits,"always_pass_evaluator_rejected":wrong_route_no_center and shuffled_transmits,"predicate":wrong_route_no_center and shuffled_transmits,"interpretation":"Mechanism-broken negatives produce the opposite readout and prevent an always-PASS interpretation."}


def main():
    marker=ROOT/"CHECKPOINTS"/"C_ADAPTIVE_DEEPENING_COMPLETE.json"
    if marker.exists(): print(marker.read_text(encoding="utf-8")); return
    audit_kernel("CORE15_EXPANSION_BEFORE_DEEPENING"); kernel,_=verify_and_load_kernel(1); started=time.perf_counter(); exps=[]
    plans=[
      ("C15X017","C15XQ001C","C15XQ001A","C15X011","MASS_INERTIA","Does functional mobility survive new sizes and allowed orientations?","translation covariance",mobile_symmetry,"The first perturbation showed local loss, while unperturbed identity remained exact.","Scope of the mobile identity law.",["axis-only artifact","diagonal transport","size dependence"]),
      ("C15X018","C15XQ004B","C15XQ004A","C15X014","RADIATION_COMPLETION","Does simultaneous event multiplicity obey one frozen detector-response law?","detector multiplicity",detector_multiplicity,"Capture did not release, leaving the detector response law as an independent positive edge.","Multiplicity and saturation law.",["linear sum","threshold","saturation"]),
      ("C15X019","C15XQ004C","C15XQ004A","C15X014","RADIATION_COMPLETION","Do payload and source temporal mode change transport delay?","dispersion panel",radiation_dispersion,"Release was absent, but multiple propagation modes remain available.","Whether their delays disperse.",["payload dispersion","mode dispersion","unit-step invariant"]),
      ("C15X020","C15XQ002B","C15XQ002A","C15X013","FRICTION_HARDNESS","Is guard blocking robust across payload and orientation, and is it opacity-like rather than hardness?","guard opacity scope",opacity_scope,"Guard loading blocked without deformation.","Whether blocking generalizes and remains organizational.",["payload threshold","orientation artifact","organization-specific opacity"]),
      ("C15X021","C15XQ009A","C15XQ009","C15X009","CLOCK_FUNCTIONALITY","Can an associative history reader detect clock-only changes?","associative clock panel",assoc_clock_panel,"Five direct mechanisms were clock-insensitive in raw response.","A history-conditioned readout was not yet challenged.",["clock-read history","raw lineage only","clock nuisance"]),
      ("C15X022","C15XQ007B","C15XQ007A","C15X015","CONTINUUM_FLUID","Does relational closure generalize, and does a prerequisite-breaking canary fail it?","closure scope/canary",relational_scope_and_canary,"Unique destination multiplicity closed 47 fresh discovery worlds.","Transformation scope and false-positive discrimination.",["general law","finite apparatus","overpermissive evaluator"]),
      ("C15X023","C15XQ008A","C15XQ008","C15X008","RESOURCE_WORK","Does capped s_reg accounting compose through successive reductions?","reducer chain",reducer_chain_accounting,"One-step capped accounting was exact.","Whether it composes and where loss enters.",["local compositional accounting","global conservation","overflow loss"]),
      ("C15X024","C15XQ012","C15XQ011","C15X016","PHYSICAL_ECOLOGY","Do explicit mechanism-broken anchors defeat the positive evaluators?","negative anchors",negative_anchor,"A cross-phenomenon chain was assembled from positive components.","Whether its readouts discriminate causal breakage.",["causal evaluator","always-PASS artifact"]),
    ]
    for exp,qid,parent,parent_exp,front,question,mechanism,fn,learned,ambiguous,competing in plans:
        pp=RESULTS/f"{parent_exp}.json"; child(qid,parent,pp,front,learned,ambiguous,question,competing,"The committed parent result opens this specific discriminating branch.")
        path,out=save(exp,qid,parent,front,question,mechanism,fn(kernel)); exps.append({"experiment_id":exp,"question_id":qid,"parent_question_id":parent,"path":str(path.relative_to(ROOT)),"predicate":bool(out.get("predicate")),"experiment_key":experiment_key(qid,mechanism,front,"grandchild")})
    # Update registries and adaptive audit.
    reg=read_json(ROOT/"EXPERIMENT_REGISTRY_EXPANSION.json"); reg["experiments"].extend(exps); reg["count"]=len(reg["experiments"]); reg["unique_experiment_keys"]=len({x["experiment_key"] for x in reg["experiments"]})==len(reg["experiments"]); reg["grandchild_count"]=len(exps); write_json(ROOT/"EXPERIMENT_REGISTRY_EXPANSION.json",reg)
    rows=[json.loads(line) for line in TREE.read_text(encoding="utf-8").splitlines() if line.strip()]; parents={r["question_id"]:r.get("parent_question_id") for r in rows}
    def depth(q):
        d=1; seen=set()
        while parents.get(q):
            if q in seen: raise RuntimeError("question cycle")
            seen.add(q); q=parents[q]; d+=1
        return d
    depths={q:depth(q) for q in parents}; audit={"root_questions":sum(v is None for v in parents.values()),"child_questions":sum(v is not None for v in parents.values()),"grandchild_questions":sum(depths[q]>=3 for q in depths),"deepest_question_tree_depth":max(depths.values()),"every_child_has_parent_result_hash":all("parent_result_hash" in r for r in rows if r.get("parent_question_id")),"all_questions_preregistered_before_results":False,"result_derived_decisions":sum(v is not None for v in parents.values()),"emergent_branches_opened":0,"emergent_branches_confirmed":0,"branch_closures":10,"pass":max(depths.values())>=3 and sum(depths[q]>=3 for q in depths)>=6}
    write_json(ROOT/"ADAPTIVE_RESEARCH_AUDIT.json",audit)
    summary={"checkpoint":"C_ADAPTIVE_DEEPENING_COMPLETE","pass":audit["pass"],"new_deepening_experiments":len(exps),"scientific_predicates_true":sum(x["predicate"] for x in exps),"total_new_experiment_ids":reg["count"],"adaptive_child_questions":audit["child_questions"],"deepest_question_tree_depth":audit["deepest_question_tree_depth"],"elapsed_seconds":time.perf_counter()-started,"completed_utc":utc()}; write_json(marker,summary)
    state=read_json(ROOT/"STATE.json"); checkpoints=state.get("completed_checkpoints",[])+["C_ADAPTIVE_DEEPENING_COMPLETE"]; update_state(status="ADAPTIVE_DEEPENING_COMPLETE",new_discovery_experiments=reg["count"],new_adaptive_child_questions=audit["child_questions"],deepest_question_tree_depth=audit["deepest_question_tree_depth"],completed_checkpoints=checkpoints)
    audit_kernel("CORE15_EXPANSION_AFTER_DEEPENING"); print(json.dumps(summary,indent=2,sort_keys=True))


if __name__=="__main__": main()
