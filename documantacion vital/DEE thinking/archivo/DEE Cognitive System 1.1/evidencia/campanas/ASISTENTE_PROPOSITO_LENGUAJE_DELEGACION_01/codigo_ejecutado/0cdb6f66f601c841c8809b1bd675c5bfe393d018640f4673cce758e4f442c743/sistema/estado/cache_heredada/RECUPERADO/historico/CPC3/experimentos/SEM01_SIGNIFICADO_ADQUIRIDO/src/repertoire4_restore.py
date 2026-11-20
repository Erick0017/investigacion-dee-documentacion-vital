"""Map-free fresh-process technical continuation of a four-signal snapshot."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import common
import repertoire4


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--snapshot",required=True,type=Path)
    parser.add_argument("--reference-after",required=True,type=Path)
    parser.add_argument("--wheel",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args();identity=common.identity(args.wheel)
    import dee_thinking as dee
    world=dee.OrganizationalWorld.load_snapshot(str(args.snapshot.resolve()))
    neutral=json.loads(world.runtime.snapshot_metadata("sem01.repertoire4.neutral_protocol"))
    assert set(neutral)=={"version","translation","signals","hubs","training_ticks","query_ticks","cue_load","outcome_load","two_toroidal_periods_are_prepared"}
    assert world.runtime.current_tick==150
    initial=common.digest(world)
    # No MEASUREMENTS, EXPERIENCE log, assignment, future event or generator is
    # read. The native query operation receives only current world and signal.
    prediction=repertoire4.participant_signal_only(world,"S1",151,tuple(neutral["translation"]))
    # Reference is opened only AFTER the new live evolution and emission.
    reference=dee.OrganizationalWorld.load_snapshot(str(args.reference_after.resolve()))
    equality=common.digest(world)==common.digest(reference)
    assert equality
    common.put(args.output,{"classification":"TECHNICAL_RESTORE_CONTINUATION_NOT_NEW_FRESH_COHORT",
        "identity":identity,"snapshot_sha256":common.sha(args.snapshot),"initial":initial,
        "loaded_neutral_metadata":neutral,"prediction":prediction,
        "reference_opened_after_native_emission":True,"reference_sha256":common.sha(args.reference_after),
        "RAW_clocks_tick_equal_reference154":equality,"final":common.digest(world),
        "teaching_map_or_external_history_read":False,"future_event_submitted":False})


if __name__=="__main__":main()
