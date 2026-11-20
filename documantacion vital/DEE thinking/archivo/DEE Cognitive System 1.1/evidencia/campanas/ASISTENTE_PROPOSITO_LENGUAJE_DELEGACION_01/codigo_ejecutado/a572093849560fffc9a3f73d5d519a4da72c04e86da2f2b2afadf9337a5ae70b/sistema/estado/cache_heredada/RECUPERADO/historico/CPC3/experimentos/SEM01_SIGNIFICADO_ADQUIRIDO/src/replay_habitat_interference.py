"""Two short technical replays of the stored wiring references, not new cases."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import common
import habitat
import memory


def execute(root,wheel):
    identity=common.identity(wheel)
    import dee_thinking as dee
    rows=[]
    for case in ("paired_A_native_action","paired_B_native_action"):
        folder=root/"resultados/discovery_habitat_memory01"/case
        measured=json.loads((folder/"MEASUREMENTS.json").read_text())
        world=dee.OrganizationalWorld.load_snapshot(str(folder/"S1_NATIVE_EMISSION.deetsnap"))
        reference=dee.OrganizationalWorld.load_snapshot(str(folder/"S2_NATIVE_EMISSION.deetsnap"))
        spec=habitat.bank_spec(memory.hub("S1"),"S1.bank")
        habitat.submit_resources(world,spec,70)
        target=tuple(spec["cost_meeting"]);before=None;neighbors=[];proposals=[]
        while world.runtime.current_tick<78:
            tick=world.runtime.current_tick
            if tick==71:
                habitat.submit_event(world,spec,measured["case"]["history"][0],70)
            if tick==75:
                memory.present_signal(world,"S2",75)
            if tick==73:
                before=common.obs(world,target)
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        for dz in (-1,0,1):
                            if (dx,dy,dz)==(0,0,0):continue
                            q=tuple((target[j]+off)%67 for j,off in enumerate((dx,dy,dz)))
                            sample=common.obs(world,q);neighbors.append(sample)
                            direction=sample["direction"]
                            if any(direction) and tuple((q[j]+direction[j])%67 for j in range(3))==target:
                                proposals.append(sample)
            world.advance()
            if world.runtime.current_tick==74:
                after=common.obs(world,target)
                original=next(x for x in measured["trace"] if x["signal"]=="S1" and x["tick"]==74)["current"]["cost_meeting"]
                assert after==original
        equal=memory.digest(world)==memory.digest(reference)
        assert equal,"Technical replay differs from original full RAW/clocks/tick at78"
        rows.append({"case":case,"classification":"TECHNICAL_REPLAY_70_TO78_NOT_NEW_PREPARATION",
            "before73":before,"neighbors73":neighbors,"proposals_pointing_to_target73":proposals,
            "observed_after74":after,"original_after74_equal":after==original,
            "whole_state78_equal_to_saved_reference":equal,
            "predicted_historical_source":{
                "second_training_report_broadcast_tick":8,"arrival_at_S1_hub":11,
                "current_at73_predicted_from_declared_direction":memory.plus(memory.hub("S1"),memory.OUTCOME_DIRECTIONS[measured["case"]["history"][1]],62),
                "scope":"Kinematic provenance candidate, additionally compare actual source RAW/direction below; no ablation performed"},
            "scope":"Void destination directional reduction reconstructed from actual sources; necessity of each contribution is not independently ablated"})
    report={"identity":identity,"technical_replays":rows,"fresh_case_count_added":0,
        "interpretation":"In the old0/8 training schedule, an unpaired historical broadcast can return to the bank during actuation. The empty-bank function remains measured, but coupling requires checking this actual residual flow.",
        "source":"source/src/kernel_v27.cpp buscar_fuente_demux multi-source branch; occupied-target precedence not bypassed"}
    common.put(root/"resultados/discovery_habitat_memory01/INTERFERENCE_REPLAY.json",report)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--wheel",type=Path,required=True)
    a=p.parse_args();execute(a.root.resolve(),a.wheel.resolve())
