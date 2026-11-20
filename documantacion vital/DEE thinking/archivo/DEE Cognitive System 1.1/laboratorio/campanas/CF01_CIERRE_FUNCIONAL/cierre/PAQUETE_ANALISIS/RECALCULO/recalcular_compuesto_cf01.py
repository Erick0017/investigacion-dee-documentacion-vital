"""Recalculate original frozen one-tick compound panel; never repair its score.

Earlier material samples explain an instrumental miss; they are not rescored
with a later reader. This uses archived primaries and Python stdlib only.
"""
from pathlib import Path
import argparse
import gzip
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SPEC=importlib.util.spec_from_file_location("cf01_archived_task_reader",HERE/"recalcular_tarea_cf01.py")
TASK=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TASK)
CASES=("CF01_MAIN","CF01_B_CUT","CF01_B_SHAM","CF01_B_DESACOPLADO")


def decode_contact(frame):
    branches=[];observations=[]
    for r in (-1,0,1):
        o=frame["contacts"][str(r)]
        TASK.observation(o)
        if o["state"]>0 and o["semantic"]==1 and o["direction"] in ([r,-1,-1],[r,-1,0]):
            branches.append(r);observations.append(o)
    return {"tick":frame["tick"],"branches":branches,"exact_material":observations,
            "unique_command":(1 if branches[0]>=0 else -1) if len(branches)==1 else None}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence",type=Path,default=ROOT/"evidencia/campanas/CF01_CIERRE_FUNCIONAL")
    p.add_argument("--out",type=Path,default=HERE/"RECALCULO_COMPUESTO_ORIGINAL_CF01.json")
    a=p.parse_args();cases=[]
    for life in CASES:
        path=a.evidence/("COMPUESTO_"+life+".json.gz")
        trial=TASK.parse_trial(path,a.evidence)
        x=TASK.read(path);native_rows=x["result"]["result"]["rows"]
        for q,primary in zip(trial["rows"],native_rows):
            native=primary["native"]
            critical=native["row"]["critical_tick"]
            early=decode_contact(next(f for f in native["frames"] if f["tick"]==critical-16))
            frozen=decode_contact(next(f for f in native["frames"] if f["tick"]==critical-15))
            assert frozen["unique_command"]==q["formed_command"]
            q["earlier_sample_not_used_by_frozen_reader"]=early
            q["actual_frozen_sample"]=frozen
            q["old_silence_despite_earlier_unique_material"]=q["silence"] and early["unique_command"] is not None
            q["context_before"]=TASK.loads(native["before"],"context_A")
            q["context_after"]=TASK.loads(native["after"],"context_A")
            q["private_before"]=TASK.loads(native["before"],"private_B")
            q["private_after"]=TASK.loads(native["after"],"private_B")
            q["prepared_gradient_prediction_not_direct_gradient_measurement"]={
                "own_relative_before":q["delta_start"],"prepared_bias":2,
                "context_relative_before":q["context_before"][0]-q["context_before"][1],
                "current_public_relative":q["public_input"][0]-q["public_input"][1],
                "Gx_prediction_from_these_components":q["delta_start"]+2+q["context_before"][0]-q["context_before"][1]+q["public_input"][0]-q["public_input"][1],
                "coverage":"Current sensor-target RAW/complete Q Moore26 were not recorded in these sparse witness fields. This algebra is a mechanism prediction, not an invented direct measurement."}
        trial["summary"]["silences_with_earlier_material_sample"]=sum(q["old_silence_despite_earlier_unique_material"] for q in trial["rows"])
        trial["summary"]["all_old_context_0_5_retained"]=trial["summary"].pop("all_A_context_retained")
        initial_context=trial["rows"][0]["context_before"]
        trial["summary"]["initial_current_context_loads"]=initial_context
        trial["summary"]["all_current_context_loads_retained"]=all(q["context_before"]==initial_context and q["context_after"]==initial_context for q in trial["rows"])
        cases.append(trial)
    result={"schema":"CF01.original_compound_panel.exact_recalculation.v1","new_ticks":0,
      "declared_reader":"Original fixed single contact sample at critical-15; all original scores retained.","cases":cases,
      "limits":["This is the original protocol2 panel, not the later two-sample reader reserve.",
        "An earlier native packet can explain why a single frozen phase returned no output. It does not justify silently changing the original score.",
        "Same public inputs and target gates do not imply identical later histories after different earlier actions.",
        "All four original target gates were+1; a fixed-left external reference could solve them. This panel tests causal contextual contribution in these organizations, not superiority to every external policy.",
        "The first compound opportunity starts with the same own relation in all four arms; subsequent own relations may diverge through failed-contact consequences.",
        "A later fixed two-sample hold is an instrument change, not a learned recovery strategy, and requires new reserved inputs.",
        "Private52 versus36 are alternative observations; they are not equal-amplitude unpaired histories."]}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"output":str(a.out),"new_ticks":0,"original_reader_not_rescored":True,
      "cases":[{"case":q["case"],"summary":q["summary"],"own_delta_before_after":[[r["delta_start"],r["delta_end"]]for r in q["rows"]]}for q in cases]},ensure_ascii=False))


if __name__=="__main__":main()
