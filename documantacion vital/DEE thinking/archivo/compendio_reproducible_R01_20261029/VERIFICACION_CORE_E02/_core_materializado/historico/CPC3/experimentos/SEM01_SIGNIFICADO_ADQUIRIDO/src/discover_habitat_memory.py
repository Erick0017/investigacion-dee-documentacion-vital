"""Two finite wiring references: acquired M1 emissions directly enter the bank.

Calibration only: teachers are explicit U/V reports here. Confirmation must
obtain those reports through the actual present-world consequence sensor.
No output is copied, transformed, routed or reinserted by the host.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
import habitat
import memory


def execute(case, output, wheel):
    identity=common.identity(wheel)
    import dee_thinking as dee
    world=memory.create_world(dee)
    banks={s:habitat.bank_spec(memory.hub(s),s+".bank",version=case.get("bank_version","v1")) for s in memory.HUBS}
    for spec in banks.values():
        habitat.declare_bank_interfaces(world,spec)
    initial=memory.digest(world)
    world.save_snapshot(str(output/"T0.deetsnap"))
    ids=[];operations=[];predictions={};captures={s:{} for s in banks};trace=[]
    training={0:("S1",case["history"][0]),8:("S2",case["history"][1])}
    query_ticks={67:"S1",75:"S2"};emission_ticks={70:"S1",78:"S2"}
    actual_events={71:("S1",case["history"][0]),79:("S2",case["history"][1])}
    for tick in range(93):
        assert world.runtime.current_tick==tick
        if tick in training:
            signal,outcome=training[tick]
            requests=[memory.present_signal(world,signal,tick)]+memory.broadcast_outcome(world,outcome,tick)
            ids.extend(r.id for r in requests)
            operations.append({"tick":tick,"operation":"SIGNAL_AND_EXPLICIT_OUTCOME_REPORT_CALIBRATION",
                               "signal":signal,"supplied_class":outcome,"receipt_ids":[r.id for r in requests]})
        if tick in query_ticks:
            signal=query_ticks[tick]
            request=memory.present_signal(world,signal,tick);ids.append(request.id)
            operations.append({"tick":tick,"operation":"SAME_PHYSICAL_SIGNAL_ALONE","signal":signal,"receipt_id":request.id})
        if tick in emission_ticks:
            signal=emission_ticks[tick]
            predictions[signal]=memory.read_emission(world,signal)
            common.put(output/(signal+"_PREDICTION_BEFORE_EVENT.json"),
                       {"prediction":predictions[signal],"actual_event_not_submitted_yet":True,
                        "actual_event_first_submission":tick+1,"world":memory.digest(world)})
            world.save_snapshot(str(output/(signal+"_NATIVE_EMISSION.deetsnap")))
            requests=habitat.submit_resources(world,banks[signal],tick)
            ids.extend(r.id for r in requests)
            operations.append({"tick":tick,"operation":"COMMON_RESOURCE_OPPORTUNITIES",
                               "signal":signal,"receipt_ids":[r.id for r in requests],
                               "not_selected_by_prediction":True})
        if tick in actual_events:
            signal,outcome=actual_events[tick]
            request=habitat.submit_event(world,banks[signal],outcome,tick-1);ids.append(request.id)
            operations.append({"tick":tick,"operation":"ACTUAL_ENVIRONMENTAL_EVENT_AFTER_NATIVE_EMISSION",
                               "signal":signal,"generator_class":outcome,"receipt_id":request.id,
                               "generator_uses_history_protocol_not_predicted_output":True})
        for emission_tick,signal in emission_ticks.items():
            if emission_tick<=tick<=emission_tick+14:
                trace.append({"signal":signal,**habitat.read_bank(world,banks[signal],emission_tick,captures[signal])})
        if tick in (12,66,92):
            world.save_snapshot(str(output/("T"+str(tick)+".deetsnap")))
        if tick<92:
            world.advance()
    return {"case":case,"identity":identity,"initial":initial,"banks":banks,
            "predictions":predictions,"operations":operations,"trace":trace,
            "receipts":[memory.receipt(world.runtime,i) for i in ids],
            "functional_effects":{s:habitat.evaluate_captures(captures[s]) for s in banks},
            "final":memory.digest(world),"operational_forks":0,"external_raw_or_clock_edits":[],
            "action_coupling":"Native M1 diagonal emission travels directly inside this same Runtime; host never calls an action input",
            "scope":"WIRING_CALIBRATION_DIRECT_TEACHERS: history supplied as explicit fixed-class reports, not yet the consequence-derived teaching demonstration"}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--wheel",type=Path,required=True);parser.add_argument("--python",type=Path)
    parser.add_argument("--child",type=Path);parser.add_argument("--output",type=Path)
    parser.add_argument("--bank-version",choices=("v1","v2_delayed_supply"),default="v1")
    args=parser.parse_args();root=args.root.resolve()
    if args.child:
        args.output.mkdir(parents=True,exist_ok=True);start=time.monotonic()
        row=execute(json.loads(args.child.read_text()),args.output,args.wheel)
        row.update(elapsed_seconds=time.monotonic()-start,runner_sha256=common.sha(__file__),
                   habitat_sha256=common.sha(Path(habitat.__file__)),memory_sha256=common.sha(Path(memory.__file__)))
        common.put(args.output/"MEASUREMENTS.json",row);return
    assert args.python
    sys.path.insert(0,str(root));from supervise import run
    group="habitat_memory02" if args.bank_version=="v2_delayed_supply" else "habitat_memory01"
    out=root/("resultados/discovery_"+group);out.mkdir(parents=True,exist_ok=True)
    config=out/"CONFIG.json"
    if not config.exists():
        common.put(config,{"cases":[{"id":"paired_A_native_action","history":["U","V"],"bank_version":args.bank_version},
                                    {"id":"paired_B_native_action","history":["V","U"],"bank_version":args.bank_version}],
                           "classification":"Two additional discovery configurations after four isolated-bank references; total6",
                           "dimension":67,"emission_ticks":[70,78],"event_submission_after_emission":[71,79],
                           "read_ticks":{"S1":{"R":77,"F":84},"S2":{"R":85,"F":92}},
                           "no_teacher_claim":"Direct reported class is calibration only; actual consequence teacher is separate confirmation"})
    rows=[]
    for case in json.loads(config.read_text())["cases"]:
        folder=out/case["id"];folder.mkdir(parents=True,exist_ok=True)
        path=folder/"CASE.json";common.put(path,case)
        name=group+"_"+case["id"];attempt=1
        while (root/"jobs"/name).exists():
            attempt+=1;name=group+"_"+case["id"]+"_attempt"+str(attempt)
        assert attempt<=3
        job=run(root,name,[str(args.python),"-I","-B",str(Path(__file__).resolve()),"--root",str(root),
                          "--wheel",str(args.wheel.resolve()),"--child",str(path),"--output",str(folder)],180,cwd=str(out))
        row=json.loads((folder/"MEASUREMENTS.json").read_text()) if job["exit_code"]==0 else {"case":case,"status":"TECHNICAL_ERROR","job":job}
        rows.append(row);common.put(out/"RESULTS.json",{"cases":rows,"config_sha256":common.sha(config)})


if __name__=="__main__":
    main()
