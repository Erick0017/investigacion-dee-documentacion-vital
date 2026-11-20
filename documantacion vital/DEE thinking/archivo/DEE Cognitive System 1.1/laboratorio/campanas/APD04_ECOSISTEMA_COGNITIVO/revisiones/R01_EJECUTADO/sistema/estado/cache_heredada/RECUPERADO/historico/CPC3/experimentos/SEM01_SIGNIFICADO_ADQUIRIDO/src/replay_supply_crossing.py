"""Retrospective short replay of the stored S2/V supply crossing, no new case."""
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
    folder=root/"resultados/actual_sensor_discovery02"
    measurements=json.loads((folder/"MEASUREMENTS.json").read_text())
    use=measurements["uses"][1]
    spec=use["bank"]
    world=dee.OrganizationalWorld.load_snapshot(str(folder/"EMISSION_S2.deetsnap"))
    reference119=dee.OrganizationalWorld.load_snapshot(str(folder/"S2_USE_T119.deetsnap"))
    reference123=dee.OrganizationalWorld.load_snapshot(str(folder/"S2_USE_T123.deetsnap"))
    emitter=tuple(spec["emitter"])
    crossing=habitat.moved(emitter,(-1,-1,0),4)
    habitat.submit_resources(world,spec,115)
    before=None;after=None;neighbors=[];sources=[]
    while world.runtime.current_tick<123:
        tick=world.runtime.current_tick
        if tick==116:
            habitat.submit_event(world,spec,use["generator_later_event"],115)
        if tick==118:
            before=common.obs(world,crossing)
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1):
                        if (dx,dy,dz)==(0,0,0):continue
                        q=tuple((crossing[j]+v)%67 for j,v in enumerate((dx,dy,dz)))
                        sample=common.obs(world,q);neighbors.append(sample)
                        direction=sample["direction"]
                        if any(direction) and tuple((q[j]+direction[j])%67 for j in range(3))==crossing:
                            sources.append(sample)
        world.advance()
        if world.runtime.current_tick==119:
            after=common.obs(world,crossing)
            eq119=memory.digest(world)==memory.digest(reference119)
            assert eq119
    eq123=memory.digest(world)==memory.digest(reference123)
    assert eq123
    common.put(folder/"V_SUPPLY_CROSSING_REPLAY.json",{
        "classification":"TECHNICAL_RETROSPECTIVE_REPLAY_115_TO123_NOT_NEW_FRESH_PREPARATION",
        "identity":identity,"crossing":crossing,"before118":before,"neighbors118":neighbors,
        "proposals_pointing_to_crossing118":sources,"after119":after,
        "whole_RAW_clocks_tick_equal_saved119":eq119,"whole_RAW_clocks_tick_equal_saved123":eq123,
        "observed_function129":use["evaluation"],
        "reconstruction":"The learned V emission and primary supply converge, producing an outgoing -x load28 carrier instead of the required +y load7 delivery. This crossing is distinct from the old0/8 residual-teacher interference.",
        "intervention":"None; inputs replay exact fixed resources and the original subsequent actual event",
        "conditional_alternative_not_executed_here":"Delay supply6 and sourceH-6y: same arrivalH+12 andF+14, V has passed crossingx=E.x-4 at+4 before supply exists"})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--wheel",type=Path,required=True)
    a=p.parse_args();execute(a.root.resolve(),a.wheel.resolve())
