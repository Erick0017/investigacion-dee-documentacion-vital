"""Exact archived social-context contrast; stdlib only, no native execution."""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CASES=("CONTEXTO_MAIN_52","CONTEXTO_CUT_52","CONTEXTO_SHAM_52","CONTEXTO_DESACOPLADO_36")
EXPECTED_DIRECTIONS=([-1,-1,-1],[-1,-1,-1],[-1,0,0],[0,1,-1],[0,1,0],[-1,0,0],[-1,0,0],[-1,-1,1],[-1,-1,1],[-1,-1,1],[-1,-1,1],[-1,-1,1])


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def exact(q):
    raw=q["raw"]
    assert isinstance(raw,str) and raw.isdecimal()
    v=int(raw)
    def sign(k):
        n=(v>>k)&15
        return n-16 if n&8 else n
    decoded={"state":v&0xffffffff,"s_reg":(v>>32)&65535,"semantic":(v>>60)&15,
             "direction":[sign(k) for k in (48,52,56)]}
    assert all(q[k]==value for k,value in decoded.items())
    assert isinstance(q["clock"],str) and q["clock"].isdecimal()
    return {k:q[k] for k in ("tick","site","raw","clock","state","s_reg","semantic","direction")}


def pair(w,key):return [exact(o) for o in w[key]]


def load(p):
    with gzip.open(p,"rt",encoding="utf8") as stream:x=json.load(stream)
    assert x["returncode"]==0
    return x,x["result"]["result"]


def analyse(p):
    x,r=load(p)
    frames=[r["before"],*r["frames"]]
    validated=0
    for f in frames:
        for k in ("A","B","B_datum","query_gate"):
            exact(f[k]);validated+=1
        for k in ("own","private_B","context_A"):
            for q in f[k]:exact(q);validated+=1
        for seq in f.get("message_waypoints",{}).values():
            for q in seq:exact(q);validated+=1
    before,after=r["before"],r["after"]
    requests={}
    for q in r["requests"]:
        requests[q["id"]]=q
    private_negative=[exact(f["B"]) for f in frames if f["B"]["state"]>0 and f["B"]["semantic"]==1 and f["B"]["direction"]==[-1,-1,-1]]
    route=[]
    for index,wanted in enumerate(EXPECTED_DIRECTIONS):
        matches=[f["message_waypoints"]["minus"][index] for f in frames if "message_waypoints" in f
                 and f["message_waypoints"]["minus"][index]["state"]>0
                 and f["message_waypoints"]["minus"][index]["semantic"]==1
                 and f["message_waypoints"]["minus"][index]["s_reg"]>0
                 and f["message_waypoints"]["minus"][index]["direction"]==wanted]
        route.append({"index":index,"site":r["frames"][0]["message_waypoints"]["minus"][index]["site"],
                      "first_qualified_observation":exact(matches[0]) if matches else None,
                      "all_qualified_sample_ticks":[z["tick"] for z in matches]})
    first_left=next((exact(f["context_A"][0]) for f in frames if f["context_A"][0]["state"]>0 and f["context_A"][0]["s_reg"]>0),None)
    first_action_change=next((exact(f["A"]) for f in frames if f["A"]["direction"]!=before["A"]["direction"]),None)
    return {"case":x["case"],"source":str(p),"source_bytes":p.stat().st_size,"source_sha256":sha(p),
      "code_revision_sha256":x["code_revision_sha256"],"instrument":x["result"]["INSTRUMENTO"],
      "interval":[before["tick"],after["tick"]],"validated_exact_observations":validated,
      "requests":list(requests.values()),"receipt_statuses":dict(Counter(q["receipt"]["status"] for q in requests.values())),
      "before":{"A":exact(before["A"]),"B":exact(before["B"]),"own":pair(before,"own"),"private_B":pair(before,"private_B"),"context_A":pair(before,"context_A")},
      "after":{"A":exact(after["A"]),"B":exact(after["B"]),"own":pair(after,"own"),"private_B":pair(after,"private_B"),"context_A":pair(after,"context_A")},
      "own_RAW_unchanged_entire_interval":all([q["raw"] for q in f["own"]]==[q["raw"] for q in before["own"]] for f in frames),
      "B_private_RAW_unchanged_entire_interval":all([q["raw"] for q in f["private_B"]]==[q["raw"] for q in before["private_B"]] for f in frames),
      "old_right_context_RAW_unchanged_entire_interval":all(f["context_A"][1]["raw"]==before["context_A"][1]["raw"] for f in frames),
      "negative_B_observations":private_negative,"minus_route":route,
      "first_new_left_context":first_left,"first_A_direction_change":first_action_change,
      "sampled_B_empty_ticks":[f["tick"] for f in frames if f["B"]["raw"]=="0"]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence",type=Path,default=ROOT/"evidencia/campanas/CF01_CIERRE_FUNCIONAL")
    p.add_argument("--out",type=Path,default=HERE/"RECALCULO_CONTEXTO_CF01.json")
    a=p.parse_args()
    rows=[analyse(a.evidence/(case+".json.gz")) for case in CASES]
    baseline=rows[0]["before"]
    assert all(q["before"]==baseline for q in rows)
    bycase={q["case"]:q for q in rows}
    positive=bycase["CONTEXTO_MAIN_52"]
    sham=bycase["CONTEXTO_SHAM_52"]
    cut=bycase["CONTEXTO_CUT_52"]
    alternate=bycase["CONTEXTO_DESACOPLADO_36"]
    parent_path=a.evidence/"CF01_MAIN_R3.json.gz"
    with gzip.open(parent_path,"rt",encoding="utf8") as stream:parent_primary=json.load(stream)
    parent_physical=parent_primary["result"]["physical"]
    parent_sha=parent_primary["result"]["INSTRUMENTO"]["snapshot_sha256"]
    genealogies=[]
    for name in ("B_CUT_FORK","B_SHAM_FORK","B_DESACOPLADO_FORK"):
        path=a.evidence/(name+".json.gz")
        with gzip.open(path,"rt",encoding="utf8") as stream:fork_primary=json.load(stream)
        record=fork_primary["result"]
        assert fork_primary["returncode"]==0
        assert record["parent"]["life_id"]=="CF01_MAIN" and record["parent"]["tick"]==44263
        assert record["parent"]["snapshot_sha256"]==parent_sha
        assert all(record["physical"][k]==parent_physical[k] for k in ("N","tick","RAW_sha256","clocks_sha256"))
        genealogies.append({"source":str(path),"source_sha256":sha(path),"life_id":record["life_id"],
                           "parent":record["parent"],"own_snapshot_sha256":record["snapshot_sha256"],
                           "recorded_physical_equal_to_parent":True})
    assert positive["negative_B_observations"]==sham["negative_B_observations"]==cut["negative_B_observations"]
    assert not alternate["negative_B_observations"]
    assert positive["first_new_left_context"]["tick"]==sham["first_new_left_context"]["tick"]==44288
    assert not cut["first_new_left_context"] and not alternate["first_new_left_context"]
    assert positive["first_A_direction_change"]["tick"]==sham["first_A_direction_change"]["tick"]==44289
    assert not cut["first_A_direction_change"] and not alternate["first_A_direction_change"]
    result={"schema":"CF01.social_context.exact_recalculation.v1","new_ticks":0,"cases":rows,
      "genealogy":{"parent_source":str(parent_path),"parent_source_sha256":sha(parent_path),
                   "parent_snapshot_sha256":parent_sha,"parent_physical":parent_physical,"forks":genealogies,
                   "scope":"Recorded exact-parent identities and RAW/clock hashes checked. Full boundary snapshots remain separately identified; complete owner equality is not inferred from sampled fields alone."},
      "same_sampled_full_witness_before_input":True,
      "causal_scope":["Same physical prefix, same private52 input; negative-bus blocker and opposite-bus sham are admitted after B's negative output has formed.",
        "New left context7 and later A direction change occur intact/sham but not after the negative-message bus cut.",
        "Private36 is a different raw environmental value, not an equal-dose unpaired control.",
        "B's stored61/19 and A's own116/113 remain unchanged over this80-tick window. The new context coexists with old right5; it does not overwrite it.",
        "The input route and cadence are externally prepared transduction. Native comparison, transport, context change and output are distinct from learning to choose that route.",
        "Observed waypoint sequences and the selective cut establish route contribution; no unique particle identity is inferred merely from equal payloads.",
        "A x0 and x+1 both decode to left in this motor codec. A direction change alone is not yet improved external utility; compound held-out trials assess that separately.",
        "The opposite-bus sham can affect old positive trains and is not universally innocuous; its preserved own/private fields and new-context effect are measured in this domain."]}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"output":str(a.out),"new_ticks":0,"same_before_witness":True,
      "cases":[{"case":q["case"],"receipts":q["receipt_statuses"],
                "first_B_negative_tick":q["negative_B_observations"][0]["tick"] if q["negative_B_observations"] else None,
                "first_left_context_tick":q["first_new_left_context"]["tick"] if q["first_new_left_context"] else None,
                "first_A_change_tick":q["first_A_direction_change"]["tick"] if q["first_A_direction_change"] else None}
               for q in rows]},ensure_ascii=False))


if __name__=="__main__":main()
