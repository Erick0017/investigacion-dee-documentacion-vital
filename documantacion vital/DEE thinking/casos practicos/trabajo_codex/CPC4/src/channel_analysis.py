"""CPC4 retrospective field/context analysis and explicitly bounded local replay.

The reducer below is an external evaluation of OBSERVED native inputs, not a
replacement Runtime. It never supplies responses to A/B or advances MAIN.
--windows restores independent copies of identified checkpoints, replays only
their recorded input calls, and writes diagnostic pre/post evidence.
"""
from __future__ import annotations
from array import array
import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha

P=19665
CRYSTALLIZATION=int(9.887**3)
OFFSETS=[q for q in itertools.product((-1,0,1),repeat=3) if q!=(0,0,0)]


def load(path):return json.loads(Path(path).read_text(encoding="utf-8"))
def rel(path,root):return str(Path(path).resolve().relative_to(root)).replace("\\","/")
def sign(value):return (value>0)-(value<0)
def index(q,n):return (q[0]*n+q[1])*n+q[2]
def plus(q,d,n):return tuple((q[i]+d[i])%n for i in range(3))
def digest_arrays(raw,clocks,tick):
    return {"tick":tick,"raw_sha256":hashlib.sha256(array("Q",raw).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",clocks).tobytes()).hexdigest()}


def context_difference(left,right):
    """Compare actual integer fields at the same declared space/time, not labels."""
    out={}
    for role in ("Bplus","Bminus"):
        a={r["tick"]:r for r in left.get("local_contexts",[]) if r["role"]==role}
        b={r["tick"]:r for r in right.get("local_contexts",[]) if r["role"]==role}
        rows=[]
        for tick in sorted(set(a)&set(b)):
            ca,cb=a[tick],b[tick]
            same_site=ca["center"]["site"]==cb["center"]["site"]
            neighbor_changes=[]
            for na,nb in zip(ca["moore26"],cb["moore26"]):
                if na["offset"]!=nb["offset"]:raise ValueError("Moore offset order changed")
                fields=[f for f in ("raw","clock","state","semantic","s_reg","direction") if na["sample"][f]!=nb["sample"][f]]
                if fields:neighbor_changes.append({"offset":na["offset"],"fields":fields,
                                                   "left":na["sample"],"right":nb["sample"]})
            rows.append({"tick":tick,"same_sampled_site":same_site,
                         "center_fields_changed":[f for f in ("raw","clock","state","semantic","s_reg","direction") if ca["center"][f]!=cb["center"][f]],
                         "neighbors_changed":neighbor_changes})
        diffs=[r for r in rows if r["center_fields_changed"] or r["neighbors_changed"]]
        out[role]={"covered_ticks":[r["tick"] for r in rows],"first_observed_difference":diffs[0] if diffs else None,
                   "all_equal_at_covered_earlier_ticks":True,"rows":rows,
                   "coverage":"Stored precontact segment contexts, not all universe sites or all ticks"}
    return out


def analyze_records(root,output):
    cases={}
    for path in sorted((root/"resultados/confirmacion").glob("*/NATIVO/MEASUREMENTS.json")):
        r=load(path);ident=r["case"]["id"]
        if ident in cases:raise ValueError("Duplicate native case identity")
        cases[ident]=r
    rows=[]
    for ident,r in cases.items():
        rows.append({"id":ident,"case":r["case"],"source":f"resultados/confirmacion/{ident}/NATIVO/MEASUREMENTS.json",
                     "initial":r["initial"],"A_native_emission_before_intervention":r["A_emission"],
                     "A_current_after_intervention":r.get("A_current_after_intervention"),
                     "B_contacts":r["B_contacts"],"B_later_common_responses":r["B_common_responses"],
                     "physical_bank_profiles":{name:v["profile"] for name,v in r["evaluations"].items()},
                     "primary_sum":r["primary_sum"],"optional_sum":r["optional_sum"],"external_utility":r["external_utility"],
                     "admission":dict(Counter(q["status"] for q in r["receipts"])),
                     "diagnostic_edits":r["diagnostic_edits"]})
    contrasts={}
    for name,a,b in (("SOURCE_PLUS_VS_MINUS","FULL_PLUS","MAIN_MINUS"),
                     ("LATE_CUT_PLUS","FULL_PLUS","CUT_PLUS"),
                     ("LATE_CUT_MINUS","MAIN_MINUS","CUT_MINUS")):
        if a in cases and b in cases:
            contrasts[name]={"left":a,"right":b,"contexts":context_difference(cases[a],cases[b])}
    policies={}
    for context in ("PLUS","MINUS"):
        policies[context]={p:cases["WORLD_"+context+"_FIXED_"+p]["external_utility"] for p in ("NONE","PLUS","MINUS","BOTH") if "WORLD_"+context+"_FIXED_"+p in cases}
    report={"scope":"Read-only reanalysis of native case records; no new case or population sample",
            "native_case_records":len(cases),"rows":rows,"precontact_contrasts":contrasts,
            "physical_fixed_policy_cost_panel":policies,
            "selective_compensation":{"case":"B_ROUTE_COMPONENT_REMOVED",
                "observed_utility":cases.get("B_ROUTE_COMPONENT_REMOVED",{}).get("external_utility"),
                "mechanism":"The common regional query supplies y. A removed postcontact DY can therefore be restored at the next encounter; this does not erase B's acquired z. The distinct DZ-removal control cannot get z from that query.",
                "boundary":"A field read by a microscopic rule need not be necessary after prepared contextual compensation; no claim of universal repair."},
            "source_of_scores":"Actual finite F/R delivery records; external utility is not fed into the Runtime",
            "not_independent_samples":"Cases share apparatus and some are diagnostic complete-state forks; ticks and episodes are not treated as replicas"}
    put(output/"RECORD_ANALYSIS.json",report)
    return cases


def record_at(d,raw,clock,n,q,tick):
    q=tuple(q);i=index(q,n);r=d.decode_record(raw[i])
    return {"tick":tick,"site":list(q),"raw":raw[i],"clock":clock[i],"state":r.state,
            "semantic":r.semantic,"s_reg":r.s_reg,"direction":[r.dx,r.dy,r.dz],
            "active":r.state>0 and r.semantic!=5}


def reconstruct_empty_destination(d,world,target,post):
    """Evaluate the selected branch from native RAW/clock observations only."""
    rt=world.runtime;n=rt.dimension;t=rt.current_tick
    raw=rt.raw_copy();clocks=rt.clock_copy();center=record_at(d,raw,clocks,n,target,t)
    neighbors=[];sources=[];gradient=[0,0,0]
    for offset in OFFSETS:
        q=plus(target,offset,n);r=record_at(d,raw,clocks,n,q,t)
        neighbors.append({"offset":list(offset),"record":r})
        if r["state"]>0:
            for k in range(3):gradient[k]-=offset[k]*r["s_reg"]
        # The actual source helper has NO activity filter; all actual fields
        # are retained, including any inactive/orphan directional proposal.
        if any(r["direction"]) and plus(q,r["direction"],n)==tuple(target):sources.append(r)
    activity={tuple(nr["offset"]):nr["record"]["active"] for nr in neighbors}
    n_active=sum(activity.values())
    xnor=(n_active>=8 and all(activity[o]==activity[tuple(-v for v in o)] for o in OFFSETS))
    grad_mag=sum(abs(v) for v in gradient)
    crystal=(n_active>0 and grad_mag//P>=CRYSTALLIZATION and not any(nr["record"]["semantic"]==5 for nr in neighbors))
    max_load=max(((v>>32)&65535 for v in raw),default=0)
    post_demux_possible=max_load+1>=P
    guard={"target_state":center["state"],"target_semantic":center["semantic"],"target_clock":center["clock"],
           "n_active":n_active,"gradient":gradient,"gradient_L1":grad_mag,"crystallization_precedes_reducer":crystal,
           "xnor_precedes_reducer":xnor,"semantic4_preempts_branch":center["semantic"]==4,
           "max_s_reg_any_record":max_load,"overflow_postpass_possible_under_one_increment_upper_bound":post_demux_possible}
    if center["state"]!=0 or center["semantic"]==4 or crystal or xnor:
        return {"coverage":"NOT_EMPTY_REDUCER_BRANCH","guard":guard,"center":center,"neighbors":neighbors,"sources":sources,"post":post}
    sums=[sum(s["direction"][k] for s in sources) for k in range(3)]
    load_sum=sum(s["s_reg"] for s in sources)
    expected={"state":1 if sources else 0,"semantic":1 if sources else 0,
              "s_reg":min(load_sum,P-1),"direction":[sign(v) for v in sums],"clock":center["clock"]+1}
    expected["raw"]=d.pack_record(expected["state"],expected["s_reg"],*expected["direction"],expected["semantic"])
    comparison={key:post[key]==expected[key] for key in ("raw","clock","state","semantic","s_reg","direction")}
    return {"coverage":"OBSERVED_EMPTY_DESTINATION_DIRECTIONAL_REDUCER","guard":guard,
            "center":center,"neighbors":neighbors,"sources":sources,
            "source_predicate":"Nonzero direction and wrapped(source+direction)==target; not RAW-nonzero as activity and not nearest-by-proximity",
            "sum_load_before_cap":load_sum,"sum_direction":sums,"expected_fields_evaluation_only":expected,
            "observed_post":post,"field_equalities":comparison,"all_fields_equal":all(comparison.values()),
            "branch_name_boundary":"Kernel helper buscar_fuente_demux is the empty-destination directional reducer; the overflow postpass aplicar_demux is a different mechanism.",
            "causal_boundary":"Participating inputs in this transition; field reading/addition is not by itself counterfactual necessity. Necessity is assessed separately using saved intervention cases."}


def native_journal(world):
    pattern=re.compile(r"^EXPERIENCE_PROTOCOL interface=(.*?) at=(\d+) load=(\d+) receipt=(\d+)$")
    records={}
    for text in world.external_operations:
        match=pattern.match(text)
        if match:
            channel,tick,payload,ident=match.groups();records[int(ident)]={"channel":channel,"requested_tick":int(tick),"payload":int(payload)}
    return records


def replay_window(root,cases,ident,start_name,pre_tick,post_tick,target,label,output,post_name=None,stored_sample=None):
    import dee_thinking as d
    from src import channel
    source=root/"resultados/confirmacion"/ident/"NATIVO"
    world=d.OrganizationalWorld.load_snapshot(str(source/(start_name+".deetsnap")))
    parent=d.OrganizationalWorld.load_snapshot(str(source/"MAIN_FINAL.deetsnap"))
    journal=native_journal(parent)
    calls=cases[ident]["operation_calls"]
    existing={r.id for r in world.runtime.receipts}
    events=[c for c in calls if c["operation"]=="submit" and c["id"] not in existing and world.runtime.current_tick<=c["call_tick"]<=post_tick]
    folder=output/label;folder.mkdir(parents=True,exist_ok=True)
    pre=None;replayed=[];start_tick=world.runtime.current_tick
    while world.runtime.current_tick<=post_tick:
        t=world.runtime.current_tick
        for call in events:
            if call["call_tick"]==t:
                actual=journal[call["id"]]
                r=world.submit(actual["channel"],actual["payload"],actual["requested_tick"])
                assert r.id==call["id"],"Actual receipt sequence changed during local replay"
                replayed.append({"call_tick":t,"actual_receipt_id":r.id,**actual})
        if t==pre_tick:
            pre=world.fork();pre.save_snapshot(str(folder/"WINDOW_PRE.deetsnap"))
        if t==post_tick:break
        world.advance()
    assert pre is not None
    post=channel.observe(world,target)
    world.save_snapshot(str(folder/"WINDOW_POST.deetsnap"))
    reconstruction=reconstruct_empty_destination(d,pre,target,post)
    validation={"stored_target_equal":None,"complete_RAW_clock_equal":None}
    if post_name:
        expected=d.OrganizationalWorld.load_snapshot(str(source/(post_name+".deetsnap")))
        validation["complete_RAW_clock_equal"]=(world.runtime.raw_copy()==expected.runtime.raw_copy() and world.runtime.clock_copy()==expected.runtime.clock_copy() and world.runtime.current_tick==expected.runtime.current_tick)
    if stored_sample is not None:
        validation["stored_target_equal"]=all(post[k]==stored_sample[k] for k in ("raw","clock","state","semantic","s_reg","direction","site","tick"))
    result={"classification":"BOUNDED_DIAGNOSTIC_REPLAY_NOT_MAIN","source_case":ident,"source_checkpoint":rel(source/(start_name+".deetsnap"),root),
            "source_sha256":sha(source/(start_name+".deetsnap")),"start_tick":start_tick,"pre_tick":pre_tick,"post_tick":post_tick,
            "native_advanced_ticks":post_tick-start_tick,"replayed_external_calls":replayed,"validation":validation,"reconstruction":reconstruction,
            "pre_snapshot":rel(folder/"WINDOW_PRE.deetsnap",root),"post_snapshot":rel(folder/"WINDOW_POST.deetsnap",root)}
    put(folder/"WINDOW.json",result)
    return result


def compare_cuts(root,output):
    import dee_thinking as d
    from src import channel
    rows=[]
    for name in ("A_EMITTED","BEFORE_COMMON_QUERY_PLUS"):
        paths=[root/"resultados/confirmacion"/ident/"NATIVO"/(name+".deetsnap") for ident in ("CUT_PLUS","CUT_MINUS")]
        worlds=[d.OrganizationalWorld.load_snapshot(str(p)) for p in paths]
        a,b=worlds
        pending=lambda w:[channel.receipt(w,r.id) for r in w.runtime.receipts if str(r.status)=="scheduled"]
        rows.append({"checkpoints":[rel(p,root) for p in paths],"sha256":[sha(p) for p in paths],"tick":a.runtime.current_tick,
                     "full_RAW_equal":a.runtime.raw_copy()==b.runtime.raw_copy(),"full_clock_equal":a.runtime.clock_copy()==b.runtime.clock_copy(),
                     "pending_inputs_equal":pending(a)==pending(b),"left_digest":channel.digest(a),"right_digest":channel.digest(b),
                     "history_receipts_may_differ":True,"scope":"Physical and pending-future equivalence; past receipt/history labels are not asserted identical and do not enter F_v27"})
    result={"comparisons":rows,"interpretation":"After removing the emitted message, opposite A acquisition histories have the same full RAW/clocks at70 and148 with the same pending inputs. This excludes a retained alternative physical A-history route in these two blocked worlds over this finite horizon; it is not universal absence of every possible route."}
    put(output/"CUT_WORLD_EQUIVALENCE.json",result)
    return result


def graph_from_windows(windows,output):
    nodes=[];edges=[]
    for label,window in windows.items():
        recon=window["reconstruction"]
        if recon.get("coverage")!="OBSERVED_EMPTY_DESTINATION_DIRECTIONAL_REDUCER":continue
        post=recon["observed_post"];target=label+":post"
        nodes.append({"id":target,"record":post,"kind":"OBSERVED_NATIVE_EVENT"})
        for number,source in enumerate(recon["sources"]):
            sid=label+":source"+str(number);nodes.append({"id":sid,"record":source,"kind":"OBSERVED_DIRECTIONAL_PROPOSAL"})
            for field,value in (("s_reg",source["s_reg"]),("dx",source["direction"][0]),("dy",source["direction"][1]),("dz",source["direction"][2])):
                edges.append({"source":sid,"target":target,"field":field,"observed_value_read":value,
                              "relation":"ADDITIVE_THEN_CAP" if field=="s_reg" else "SUM_THEN_SIGN",
                              "counterfactual_necessity":"NOT_INFERRED_FROM_READING_ALONE"})
    put(output/"EVENT_GRAPH.json",{"nodes":nodes,"edges":edges,"scope":"Local observed proposal/context graph, not labels propagated to all neighbors or a unique global ancestry claim"})
    with (output/"FIELD_EDGES.csv").open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=("source","target","field","observed_value_read","relation","counterfactual_necessity"));writer.writeheader();writer.writerows(edges)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=ROOT);parser.add_argument("--output",type=Path);parser.add_argument("--windows",action="store_true")
    args=parser.parse_args();root=args.root.resolve();output=args.output or root/"resultados/CHANNEL_ANALYSIS";output.mkdir(parents=True,exist_ok=True)
    cases=analyze_records(root,output)
    if args.windows:
        compare_cuts(root,output)
        main=cases["MAIN_MINUS"];full=cases["FULL_PLUS"]
        banksample=next(r for r in full["trace"] if r["tick"]==153)["samples"]["plus_cost_meeting"]
        windows={}
        for label,ident,start,pre,post,target,reference,sample in (
            ("A_ACQUISITION","MAIN_MINUS","MAIN_T0",2,3,main["spec"]["centers"]["A"],"A_AFTER_ACQUISITION",None),
            ("B_CONTACT","MAIN_MINUS","BEFORE_CONTACT_MINUS",87,88,main["spec"]["centers"]["Bminus"],"AFTER_CONTACT_MINUS",None),
            ("B_COMMON_QUERY","MAIN_MINUS","BEFORE_COMMON_QUERY_MINUS",154,155,main["spec"]["centers"]["Bminus"],"AFTER_COMMON_QUERY_MINUS",None),
            ("BANK_COST","FULL_PLUS","AFTER_COMMON_QUERY_PLUS",152,153,full["spec"]["banks"]["plus"]["cost_meeting"],None,banksample)):
            windows[label]=replay_window(root,cases,ident,start,pre,post,target,label,output,reference,sample)
        put(output/"WINDOW_SUMMARY.json",{key:{"validation":value["validation"],"coverage":value["reconstruction"]["coverage"],"fields_equal":value["reconstruction"].get("all_fields_equal"),"sources":value["reconstruction"].get("sources")} for key,value in windows.items()})
        graph_from_windows(windows,output)
    print(json.dumps({"native_records_analyzed":len(cases),"output":str(output),"windows":args.windows}))


if __name__=="__main__":main()
