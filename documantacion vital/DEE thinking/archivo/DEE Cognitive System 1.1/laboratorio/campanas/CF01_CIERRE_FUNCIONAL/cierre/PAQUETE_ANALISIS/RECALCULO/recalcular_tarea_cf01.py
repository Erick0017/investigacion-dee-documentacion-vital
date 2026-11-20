"""Recalculate nine archived CF01 queue trials; no DEE/Gym imports or ticks.

Fixed/random references operate separate external queue copies. Their actions
never enter a native participant. Both the declared attempt cap and each
MAIN observed horizon are reported, preventing favourable horizon selection.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARMS = ("MAIN", "SIN_RETORNO", "ACCION_ANULADA")
SEEDS = (101,202,303,404,505,606,707,808)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with gzip.open(path, "rt", encoding="utf8") as stream:
        return json.load(stream)


def observation(q):
    raw = q["raw"]
    if not isinstance(raw, str) or not raw.isdecimal():
        raise ValueError("Packed RAW must remain an exact decimal string")
    v = int(raw)
    signed = lambda shift: ((v >> shift) & 15) - (16 if (v >> shift) & 8 else 0)
    decoded = {"state": v & 0xffffffff, "s_reg": (v >> 32) & 65535,
               "semantic": (v >> 60) & 15, "direction": [signed(i) for i in (48,52,56)]}
    for key,value in decoded.items():
        if q[key] != value:
            raise ValueError("Field disagrees with packed RAW: " + key)
    if not isinstance(q["clock"], str) or not q["clock"].isdecimal():
        raise ValueError("Clock must remain an exact decimal string")
    return decoded


def validate_witness(w):
    count = 0
    for key in ("A", "B", "B_datum", "query_gate"):
        if key in w:
            observation(w[key]);count += 1
    for key in ("own", "private_B", "context_A"):
        for q in w.get(key, []):
            observation(q);count += 1
    for q in w.get("contacts", {}).values():
        observation(q);count += 1
    return count


def loads(w,key):
    return [q["s_reg"] for q in w[key]]


def delta(w):
    values = loads(w,"own")
    return values[0]-values[1]


def parse_trial(path, evidence):
    x = read(path)
    if x["returncode"] != 0:
        raise ValueError("Trial process failed: " + path.name)
    envelope = x["result"]
    data = envelope["result"]
    argv = x["argv"]
    cap = int(argv[argv.index("--pasos")+1])
    rows=[];receipts={};checked=0;previous_env=None
    for index,outer in enumerate(data["rows"]):
        native = outer["native"]
        nr = native["row"]
        before_env, after_env = outer["environment_before"], outer["environment_after"]
        if before_env["law"] != "CF01.two_gate_work_queue.v1":
            raise ValueError("Unknown external law")
        if previous_env is not None and before_env != previous_env:
            raise ValueError("Environment discontinuity within one trial")
        if nr["availability"] != before_env["jobs"][before_env["cursor"]]:
            raise ValueError("Native world condition differs from actual current job")
        frames=native["frames"]
        checked += validate_witness(native["before"])+validate_witness(native["after"])
        checked += sum(validate_witness(w) for w in frames)
        critical=nr["critical_tick"]
        contact=next(w for w in frames if w["tick"]==critical-15)
        emitted=[];right=[];wrong=[];reflected=[]
        for r in (-1,0,1):
            o=contact["contacts"][str(r)]
            if o["state"]>0 and o["semantic"]==1 and o["direction"] in ([r,-1,-1],[r,-1,0]):
                emitted.append(r)
                (right if (1 if r>=0 else -1)==nr["availability"] else wrong).append(r)
                if o["direction"]==[r,-1,0]:reflected.append(r)
        formed=(1 if emitted[0]>=0 else -1) if len(emitted)==1 else None
        executed=formed if outer["actuator_mode"]=="closed" else None
        completed=executed==nr["availability"]
        assert emitted==nr["emitted"] and right==nr["useful"] and wrong==nr["wrong"]
        assert formed==outer["formed_native_command"] and executed==outer["executed_external_command"]
        assert completed==outer["job_completed"]
        assert after_env["attempts"]==before_env["attempts"]+1
        assert after_env["cursor"]==before_env["cursor"]+int(completed)
        assert after_env["completed"]==before_env["completed"]+int(completed)
        q=contact["contacts"]["0"]
        query=bool(q["state"]>0 and q["semantic"]==1 and q["direction"]==[0,-1,-1])
        assert query==nr["query_at_contact"]
        pre=next(w for w in frames if w["tick"]==critical-16)
        at=next(w for w in frames if w["tick"]==critical)
        post=next(w for w in frames if w["tick"]==critical+3)
        endpoints=[native["before"],*frames,native["after"]]
        retained_private=all(loads(w,"private_B")==[61,19] for w in endpoints)
        retained_context=all(loads(w,"context_A")==[0,5] for w in endpoints)
        for request in native["requests"]:
            receipt=request["receipt"]
            ident=receipt["id"]
            if ident in receipts and receipts[ident] != receipt:
                raise ValueError("Conflicting receipt identity")
            receipts[ident]=receipt
        rows.append({"attempt_index":index,"native_start_tick":nr["start_tick"],"critical_tick":critical,
          "end_tick":nr["end_tick"],"cursor_before":before_env["cursor"],"availability":nr["availability"],
          "formed_command":formed,"executed_command":executed,"external_job_completed":completed,
          "emitted_native_branches":emitted,"native_useful_branches":right,"native_wrong_branches":wrong,
          "reflected_failure_branches":reflected,"query_at_contact":query,"silence":not emitted,
          "conflict":bool(right and wrong),"own_start":loads(native["before"],"own"),
          "own_pre_contact":loads(pre,"own"),"own_at_critical":loads(at,"own"),
          "own_post3":loads(post,"own"),"own_end":loads(native["after"],"own"),
          "delta_start":delta(native["before"]),"delta_pre_contact":delta(pre),
          "delta_post3":delta(post),"delta_end":delta(native["after"]),
          "private_B_61_19_retained_in_all_samples":retained_private,
          "A_context_0_5_retained_in_all_samples":retained_context,
          "sampled_B_active_frames":sum(w["B"]["state"]>0 for w in frames),
          "sampled_gate_forwarding_frames":sum(w["query_gate"]["state"]>0 and w["query_gate"]["semantic"]==1 and w["query_gate"]["direction"]==[0,1,0] for w in frames),
          "public_input":nr["public_raw"],"new_private_B_input":nr["private_B_raw"]})
        previous_env=after_env
    initial=data["rows"][0]["environment_before"]
    final=data["rows"][-1]["environment_after"]
    assert initial["cursor"]==0
    assert len(rows)<=cap
    assert len(rows)==cap or final["cursor"]==len(final["jobs"])
    version=x["code_revision_sha256"]
    archived=evidence/"codigo_ejecutado"/version/"sistema/capacidades/cierre_funcional_cf01.py"
    source={"path":str(archived),"exists":archived.exists(),"sha256":sha(archived) if archived.exists() else None}
    return {"case":x["case"],"source":str(path),"source_bytes":path.stat().st_size,"source_sha256":sha(path),
      "code_revision_sha256":version,"archived_service_code":source,"instrument":envelope["INSTRUMENTO"],
      "declared_attempt_cap":cap,"jobs":initial["jobs"],"environment_reset_index":initial["external_resets"],
      "rows":rows,"summary":{"attempts":len(rows),"jobs_completed":final["completed"],"jobs_total":len(final["jobs"]),
        "valid_unique_native_commands":sum(q["formed_command"] is not None for q in rows),
        "executed_external_commands":sum(q["executed_command"] is not None for q in rows),
        "native_useful_opportunities":sum(bool(q["native_useful_branches"]) for q in rows),
        "native_wrong_opportunities":sum(bool(q["native_wrong_branches"]) for q in rows),
        "query_contact_samples":sum(q["query_at_contact"] for q in rows),
        "silence":sum(q["silence"] for q in rows),"conflict":sum(q["conflict"] for q in rows),
        "receipts":dict(Counter(q["status"] for q in receipts.values())),
        "packed_observations_checked":checked,
        "all_private_references_retained":all(q["private_B_61_19_retained_in_all_samples"] for q in rows),
        "all_A_context_retained":all(q["A_context_0_5_retained_in_all_samples"] for q in rows)}}


def external_reference(jobs,cap,policy,rng=None):
    cursor=0;rows=[]
    for i in range(cap):
        if cursor==len(jobs):break
        command=1 if policy=="fixed_left" else -1 if policy=="fixed_right" else rng.choice((-1,1))
        # Only the ENVIRONMENT compares command with its currently pending job.
        # Policy selection above has no input containing the pending job value.
        current=jobs[cursor]
        completed=command==current
        rows.append({"attempt":i,"cursor_before":cursor,"job":current,"command":command,"completed":completed})
        cursor+=int(completed)
    return {"attempt_cap":cap,"attempts_executed":len(rows),"completed":cursor,"jobs_total":len(jobs),"rows":rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence",type=Path,default=ROOT/"evidencia/campanas/CF01_CIERRE_FUNCIONAL")
    p.add_argument("--out",type=Path,default=HERE/"RECALCULO_TAREA_CF01.json")
    a=p.parse_args()
    trials=[parse_trial(a.evidence/("CF01_"+arm+"_R"+str(i)+".json.gz"),a.evidence) for arm in ARMS for i in (1,2,3)]
    bycase={q["case"]:q for q in trials}
    main_trials=[bycase["CF01_MAIN_R"+str(i)] for i in (1,2,3)]
    # Preserve a single RNG continuation across the three external queue resets.
    references=[]
    for horizon in ("declared_cap","MAIN_observed_attempts"):
        for policy in ("fixed_left","fixed_right","random"):
            for seed in SEEDS if policy=="random" else (None,):
                rng=random.Random(seed) if seed is not None else None
                runs=[]
                for trial in main_trials:
                    cap=trial["declared_attempt_cap"] if horizon=="declared_cap" else len(trial["rows"])
                    runs.append({"reserve":trial["case"],**external_reference(trial["jobs"],cap,policy,rng)})
                references.append({"policy":policy,"seed":seed,"horizon":horizon,"native_ticks":0,
                  "runs":runs,"total_completed":sum(q["completed"] for q in runs),
                  "scope":"Independent external policy reference, never a controller of E1; RNG continues across queue resets."})
    paired=[]
    aa=bycase["CF01_MAIN_R1"]["rows"]
    bb=bycase["CF01_SIN_RETORNO_R1"]["rows"]
    for left,right in zip(aa[:4],bb[:4]):
        assert left["critical_tick"]==right["critical_tick"] and left["availability"]==right["availability"]
        paired.append({"same_age_critical_tick":left["critical_tick"],"common_world_availability":left["availability"],
          "intact":left,"return_omitted":right})
    summary_by_arm={arm:{k:sum(q["summary"][k] for q in trials if q["case"].startswith("CF01_"+arm+"_"))
                    for k in ("attempts","jobs_completed","jobs_total","valid_unique_native_commands",
                              "executed_external_commands","native_useful_opportunities","native_wrong_opportunities",
                              "query_contact_samples","silence","conflict")} for arm in ARMS}
    result={"schema":"CF01.external_queue.recalculation.v1","new_native_ticks":0,
      "trials":trials,"totals_by_arm":summary_by_arm,"same_age_first_four_R1":paired,
      "separate_external_references":references,"random_seeds_all_reported":list(SEEDS),
      "limits":["Three consecutive reserves per arm are one physical lineage, not three independent learners.",
        "After actions diverge, queue cursors and available jobs legitimately diverge; no identical future is imposed.",
        "Action annulment only removes external action, not the native contact or native return.",
        "The return-omitted arm omits prepared return resources; it is distinct from a selective post-formation cut.",
        "These queue trials supply no new private scalar or public scalar observation. Retained social context is not a newly learned message.",
        "Query and gate counts are sampled material occurrences, not independent information requests or exclusive learned act-versus-ask choices.",
        "Own absolute fields grow with age even without return; the contrast concerns their relative difference and subsequent action.",
        "Fixed/random policy runs are external arithmetic controls, not DEE reproductions or new experiments on E1."]}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"output":str(a.out),"native_ticks":0,"totals_by_arm":summary_by_arm,
      "references":[{k:q[k] for k in ("policy","seed","horizon","total_completed")} for q in references]},ensure_ascii=False))


if __name__=="__main__":main()
