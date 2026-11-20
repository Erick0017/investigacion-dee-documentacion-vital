"""Four-identity extension over one native N67 Runtime; frozen finite cohorts.

This expands physical resources rather than asserting an efficiency gain.
The experience generator knows its schedule. Participant query and decoder do
not receive a teaching assignment, future target, past transcript or utility.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
import common
import habitat
import memory as inherited_memory


SIGNALS=("S1","S2","S3","S4")
HUBS={s:(30,30,z) for s,z in zip(SIGNALS,(8,24,40,56))}
TRAINING_EMITTERS={s:(x,10,64) for s,x in zip(SIGNALS,(8,23,39,54))}
TRAINING_TICKS={s:17+28*i for i,s in enumerate(SIGNALS)}
QUERY_TICKS={s:151+28*i for i,s in enumerate(SIGNALS)}
CLASSES={"U":(1,1,0),"V":(1,-1,0)}
DECODE={(-1,1,0):"U",(-1,-1,0):"V"}
SUBTASK_START="2026-10-14T20:55:58+00:00"
SUBTASK_DEADLINE="2026-10-14T21:25:58+00:00"


def translated(site,translation=(0,0,0)):
    return tuple((q+d)%67 for q,d in zip(site,translation))


def prepare(dee,translation=(0,0,0)):
    """No assignment argument. All four sensory/action possibilities exist."""
    recipe=dee.OrganizationRecipe.research(67,[],0)
    recipe.execution=dee.TickOptions(dee.Backend.LAZY,1)
    interfaces=[]
    for signal,site in HUBS.items():
        h=translated(site,translation)
        interfaces.append(inherited_memory.interface(dee,"signal."+signal,habitat.moved(h,(-1,0,0),-3),(-1,0,0)))
        for outcome,direction in CLASSES.items():
            interfaces.append(inherited_memory.interface(dee,"outcome."+signal+"."+outcome,habitat.moved(h,direction,-3),direction))
    recipe.interfaces=interfaces
    world=dee.OrganizationalWorld.create(recipe)
    banks={}
    for signal in SIGNALS:
        banks["train."+signal]=habitat.bank_spec(translated(TRAINING_EMITTERS[signal],translation),"r4.train."+signal,version="v2_delayed_supply")
        banks["use."+signal]=habitat.bank_spec(translated(HUBS[signal],translation),"r4.use."+signal,version="v2_delayed_supply")
    for spec in banks.values():habitat.declare_bank_interfaces(world,spec)
    # Inert geometry and protocol only; this snapshot metadata has no teaching
    # assignment, future class, case ID, transcript or expected native answer.
    world.runtime.set_snapshot_metadata("sem01.repertoire4.neutral_protocol",json.dumps({
        "version":1,"translation":list(translation),"signals":list(SIGNALS),
        "hubs":HUBS,"training_ticks":TRAINING_TICKS,"query_ticks":QUERY_TICKS,
        "cue_load":5,"outcome_load":11,"two_toroidal_periods_are_prepared":True},separators=(",",":")))
    return world,banks


def current_sensor(world,bank):
    current=common.obs(world,bank["function_receiver"])
    available=current["active"] and current["s_reg"]==7 and current["direction"]==[0,1,0]
    return {"physical":current,"observed_class":"V" if available else "U",
            "modality":"EXTERNAL_FIXED_PRESENT_FUNCTION_SENSOR",
            "absence_is_external_window_observation_not_native_absence_detector":True}


def present_signal(world,signal,tick):
    if signal not in SIGNALS:raise ValueError("S1..S4 only")
    return world.submit("signal."+signal,5,tick)


def broadcast_actual_class(world,outcome,tick):
    if outcome not in CLASSES:raise ValueError("Actual transducer class U/V required")
    return [world.submit("outcome."+signal+"."+outcome,11,tick) for signal in SIGNALS]


def participant_signal_only(world,signal,tick,translation=(0,0,0)):
    """Map-free participant operation; the same fixed signal as in teaching."""
    world.run_until(tick)
    before=common.digest(world)
    admitted=present_signal(world,signal,tick)
    world.run_until(tick+3)
    current=common.obs(world,translated(HUBS[signal],translation))
    decoded=DECODE.get(tuple(current["direction"])) if current["active"] else None
    return {"signal":signal,"input_tick":tick,"emission_tick":world.runtime.current_tick,
            "physical":current,"anticipated_class":decoded,"coverage":decoded is not None,
            "receipt":common.receipt(world,admitted),"before":before,
            "action":"This same physical emission proceeds into the bank; no output callback or insertion",
            "scope":"Four signal identities, two directional consequence classes; prepared two-turn consultation timing"}


def run_case(case,out,wheel):
    import dee_thinking as dee
    identity=common.identity(wheel)
    translation=tuple(case.get("translation",(0,0,0)))
    world,banks=prepare(dee,translation)
    initial=common.digest(world)
    world.save_snapshot(str(out/"MAIN_T0.deetsnap"))
    # Assignment becomes a generator variable only AFTER preparation and the
    # identical-body snapshot. It is not placed in native session metadata.
    mapping=dict(zip(SIGNALS,case["generator_assignment"]))
    mode=case.get("mode","paired")
    teaching=[];teacher_ids=[]
    for signal in SIGNALS:
        effect=TRAINING_TICKS[signal];emit=effect-14;bank=banks["train."+signal]
        world.run_until(emit)
        requests=habitat.submit_resources(world,bank,emit);teacher_ids.extend(r.id for r in requests)
        world.run_until(emit+1)
        event=habitat.submit_event(world,bank,mapping[signal],emit);teacher_ids.append(event.id)
        world.run_until(effect)
        sensed=current_sensor(world,bank)
        # ONLY the actual present native delivery selects this fixed transducer
        # output; the generator's requested event is not supplied to it.
        teachers=broadcast_actual_class(world,sensed["observed_class"],effect)
        teacher_ids.extend(r.id for r in teachers)
        signal_tick=effect+(1 if mode=="unpaired" else 0)
        signal_receipt=present_signal(world,signal,signal_tick);teacher_ids.append(signal_receipt.id)
        row={"signal":signal,"effect_tick":effect,"generator_event":mapping[signal],
             "sensor":sensed,"signal_tick":signal_tick,"mode":mode,
             "teacher_receipts":[r.id for r in teachers],"signal_receipt":signal_receipt.id,
             "broadcast":"Same class and payload11 to ALL four regions, regardless of signal identity"}
        teaching.append(row);common.append(out/"EXPERIENCIAS.jsonl",row)
        world.run_until(effect+5)
        world.save_snapshot(str(out/("AFTER_"+signal+"_EXPERIENCE.deetsnap")))
    world.run_until(150)
    world.save_snapshot(str(out/"BEFORE_FIRST_QUERY.deetsnap"))
    uses=[]
    for signal in SIGNALS:
        tick=QUERY_TICKS[signal];world.run_until(tick-1)
        before_operations=list(world.external_operations)
        prediction=participant_signal_only(world,signal,tick,translation)
        emit=prediction["emission_tick"];bank=banks["use."+signal]
        pending={"recorded_utc":datetime.now(timezone.utc).isoformat(),"prediction":prediction,
                 "no_event_of_this_episode_scheduled_yet":True,"future_event_first_request_tick":emit+1}
        common.append(out/"PREDICCIONES.jsonl",pending)
        world.save_snapshot(str(out/("EMISSION_"+signal+".deetsnap")))
        resource_requests=habitat.submit_resources(world,bank,emit)
        ids=[r.id for r in resource_requests];trace=[];captures={}
        for now in range(emit,emit+15):
            if now==emit+1:
                request=habitat.submit_event(world,bank,mapping[signal],emit);ids.append(request.id)
            trace.append(habitat.read_bank(world,bank,emit,captures))
            if now in (emit+8,emit+14):world.save_snapshot(str(out/(signal+"_USE_T"+str(now)+".deetsnap")))
            if now<emit+14:world.advance()
        evaluation=habitat.evaluate_captures(captures)
        row={"signal":signal,"prediction":prediction,"actual_later_generator_event":mapping[signal],
             "native_use_trace":trace,"evaluation":evaluation,"bank":bank,
             "receipt_after_advance":[common.receipt(world,i) for i in ids],
             "prediction_correct":None if prediction["anticipated_class"] is None else prediction["anticipated_class"]==mapping[signal],
             "external_operations_before_query":before_operations}
        uses.append(row);common.append(out/"USES.jsonl",row)
    world.save_snapshot(str(out/"MAIN_FINAL.deetsnap"))
    receipts=[common.receipt(world,i) for i in teacher_ids]
    return {"case":case,"identity":identity,"initial":initial,"teaching":teaching,"uses":uses,
            "actual_teaching_receipts":receipts,"final":common.digest(world),
            "external_operations_actual":list(world.external_operations),
            "external_diagnostic_edits":[str(e) for e in world.diagnostic_edits],"operational_forks":0,
            "scope":"Expanded resources: four acquired signal identities/two consequence classes; no claim of four independent functions or bits",
            "modalities":{"teaching":"EXPERIENCE_PROTOCOL_WITH_PRESENT_OUTCOME_SENSOR",
                          "anticipation":"NATIVE_STATE_EVOLUTION_PLUS_FIXED_PASSIVE_DECODER",
                          "use":"SAME_RUNTIME_NATIVE_ACTION_WITH_FIXED_ENVIRONMENTAL_INPUTS_AFTER_EMISSION",
                          "evaluation":"EXTERNAL_ONLY"},
            "capture_summary":{"predictions":len(uses),"covered":sum(x["prediction"]["coverage"] for x in uses),
                               "correct_singletons":sum(x["prediction_correct"] is True for x in uses),
                               "primary_deliveries":sum(x["evaluation"]["function_delivery"] for x in uses),
                               "optional_deliveries":sum(x["evaluation"]["resource_delivery"] for x in uses)}}


def frozen_config():
    return {"version":"sem01.repertoire4.v1","frozen_utc":datetime.now(timezone.utc).isoformat(),
            "subtask_start":SUBTASK_START,"subtask_deadline":SUBTASK_DEADLINE,
            "N":67,"hubs":HUBS,"training_emitters":TRAINING_EMITTERS,
            "training_ticks":TRAINING_TICKS,"query_ticks":QUERY_TICKS,"emission_ticks":{s:t+3 for s,t in QUERY_TICKS.items()},
            "signal":"Same single port/payload5/direction(-1,0,0) during teaching and evaluation",
            "teachers":"Payload11 direction(1,+/-1,0), selected only by current physical function sensor and broadcastALL4",
            "decoder":{"-1,1,0":"U","-1,-1,0":"V"},"bank_version":"v2_delayed_supply",
            "cases":[{"id":"paired_A_four","mode":"paired","generator_assignment":["U","U","V","V"]},
                     {"id":"paired_B_nonglobal_inversion","mode":"paired","generator_assignment":["U","V","U","V"]},
                     {"id":"unpaired_A_four","mode":"unpaired","generator_assignment":["U","U","V","V"]},
                     {"id":"reserved_A_translation","mode":"paired","generator_assignment":["U","U","V","V"],"translation":[3,5,7],"reserved":True}],
            "criterion":{"signal_read_window":"Exactly prepared query+3, with RAW/clock and admission retained",
                         "primary_function":"Native delivered load7 direction+y at emission+14",
                         "optional_function":"Native delivered load3 direction+x at emission+7",
                         "errors_and_missing":"Included, no missing or rejected input becomes a correct zero response"},
            "resource_domain":"Same N67 but four memories and eight banks: enlarged resource arm, not equal-resource efficiency comparison",
            "maximum_fresh_cohorts":4,"maximum_high_level_geometry_designs":2,"selected_geometry_design":1,
            "process_timeout_seconds":180,"native_threads":1}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--wheel",required=True,type=Path);parser.add_argument("--python",type=Path)
    parser.add_argument("--child",type=Path);parser.add_argument("--output",type=Path)
    args=parser.parse_args();root=args.root.resolve()
    if args.child:
        args.output.mkdir(parents=True,exist_ok=True);start=time.monotonic()
        row=run_case(json.loads(args.child.read_text()),args.output,args.wheel)
        row.update(elapsed_seconds=time.monotonic()-start,runner_sha256=common.sha(__file__),
                   habitat_sha256=common.sha(habitat.__file__),completed_utc=datetime.now(timezone.utc).isoformat())
        common.put(args.output/"MEASUREMENTS.json",row);return
    assert args.python
    sys.path.insert(0,str(root));from supervise import run
    output=root/"resultados/repertorio4";output.mkdir(parents=True,exist_ok=True)
    config_path=root/"configuraciones/REPERTOIRE4_CONFIG.json"
    if not config_path.exists():common.put(config_path,frozen_config())
    config=json.loads(config_path.read_text());rows=[]
    for case in config["cases"]:
        if datetime.now(timezone.utc)>=datetime.fromisoformat(config["subtask_deadline"]):
            rows.append({"case":case,"status":"NO_EJECUTADO_POR_PRESUPUESTO_DE_SUBTAREA"});continue
        folder=output/case["id"];folder.mkdir(parents=True,exist_ok=True)
        case_path=folder/"CASE.json";common.put(case_path,case)
        if (folder/"MEASUREMENTS.json").exists():
            rows.append(json.loads((folder/"MEASUREMENTS.json").read_text()));continue
        name="repertoire4_"+case["id"];attempt=1
        while (root/"jobs"/name).exists():
            attempt+=1;name="repertoire4_"+case["id"]+"_attempt"+str(attempt)
        assert attempt<=3,"At most two technical repairs"
        job=run(root,name,[str(args.python),"-I","-B",str(Path(__file__).resolve()),"--root",str(root),
                          "--wheel",str(args.wheel.resolve()),"--child",str(case_path),"--output",str(folder)],180,cwd=str(output))
        row=json.loads((folder/"MEASUREMENTS.json").read_text()) if job["exit_code"]==0 else {"case":case,"status":"TECHNICAL_ERROR","job":job}
        rows.append(row);common.put(output/"RESULTS.json",{"cases":rows,"config_sha256":common.sha(config_path)})


if __name__=="__main__":main()
