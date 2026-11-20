"""Last authorized instrumented window: occupied-target precedence286->287.

The original inverse320 hypothesis stays in its file as refuted. This window
does not repair the reader or install a carrier; it samples both actual
opposing records, all26 neighbors and the selected material survival branch.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src import channel
from src.common import put,sha

TETRA=(
 ((1,0,0),(0,1,0),(0,0,1),(1,1,1)),
 ((-1,0,0),(0,-1,0),(0,0,-1),(-1,-1,-1)),
 ((1,0,0),(0,-1,0),(0,0,-1),(1,-1,-1)),
 ((-1,0,0),(0,1,0),(0,0,1),(-1,1,1)),
 ((1,0,0),(0,1,0),(0,0,-1),(1,1,-1)),
 ((-1,0,0),(0,-1,0),(0,0,1),(-1,-1,1)),
 ((-1,0,0),(0,1,0),(0,0,-1),(-1,1,-1)),
 ((1,0,0),(0,-1,0),(0,0,1),(1,-1,1)))


def material_guard(world,site):
    center=channel.observe(world,site);context=channel.moore_context(world,site)
    active={tuple(row["offset"]):row["sample"]["active"] for row in context}
    n_active=sum(active.values())
    hadron=any(all(active[offset] for offset in pattern) for pattern in TETRA)
    tension=16.0 if hadron and n_active<7 else 2.5
    rho=n_active*tension/26.0
    rule=math.floor(rho+0.5)
    incoming=[]
    for row in context:
        record=row["sample"]
        if any(record["direction"]) and channel.moved(record["site"],record["direction"])==tuple(site):
            incoming.append(record)
    return {"center":center,"moore26":context,"n_active":n_active,"tetrahedron":hadron,
            "incomplete_n_active_lt7":n_active<7,"T_local":tension,"rho_eff":rho,"rule_value":rule,
            "semantic4_guard":center["semantic"]==4,"directional_proposals_present":incoming,
            "branch":"OCCUPIED_MATERIAL_RULE_VALUE_ZERO_RETURN" if center["state"]>0 and center["semantic"]!=4 and rule==0 else "OTHER_BRANCH_REQUIRES_SEPARATE_ANALYSIS",
            "ordinary_increment_protection_and_gradient_not_reached":center["state"]>0 and center["semantic"]!=4 and rule==0,
            "empty_destination_reducer_not_invoked":center["state"]>0}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=ROOT);parser.add_argument("--config",type=Path,required=True);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();config=json.loads(args.config.read_text(encoding="utf-8"));root=args.root.resolve();args.output.mkdir(parents=True,exist_ok=True)
    import dee_thinking as d
    if d.__version__!="4.0.0" or sha(d._native.__file__)!=channel.NATIVE_SHA256:raise RuntimeError("Qualified DEE4 instrument required")
    source=root/config["source"];world=d.OrganizationalWorld.load_snapshot(str(source));calls=[{"operation":"load_snapshot","source":config["source"],"tick":world.runtime.current_tick}]
    if world.runtime.current_tick!=267:raise ValueError("Recorded inverse parent267 required")
    initial=channel.digest(world);journal_before=list(world.external_operations)
    pending=[channel.receipt(world,r.id) for r in world.runtime.receipts if str(r.status)=="scheduled"]
    world.run_until(286);calls.append({"operation":"run_until","target_tick":286,"actual_tick":world.runtime.current_tick})
    before={name:material_guard(world,site) for name,site in config["sites"].items()}
    max_load=max(((v>>32)&65535 for v in world.runtime.raw_copy()),default=0)
    world.save_snapshot(str(args.output/"PRE286.deetsnap"));calls.append({"operation":"save_snapshot","tick":286})
    world.advance();calls.append({"operation":"advance","count":1,"actual_tick":world.runtime.current_tick})
    after={name:channel.observe(world,site) for name,site in config["sites"].items()}
    world.save_snapshot(str(args.output/"POST287.deetsnap"));calls.append({"operation":"save_snapshot","tick":287})
    checks={name:{"selected_rule_value_zero":row["rule_value"]==0,
                  "observed_post_raw_zero":after[name]["raw"]==0,
                  "clock_increment_one":after[name]["clock"]==row["center"]["clock"]+1,
                  "pre_occupied":row["center"]["state"]>0,
                  "incoming_other_record_exists":bool(row["directional_proposals_present"])} for name,row in before.items()}
    result={"classification":"ONE_INSTRUMENTED_REPEAT_OF_EXISTING_267_321_DIAGNOSTIC_WINDOW",
            "source":config["source"],"source_sha256":sha(source),"initial":initial,"final":channel.digest(world),
            "actual_calls":calls,"pending_inputs_at_source":pending,"external_operation_journal_unchanged":list(world.external_operations)==journal_before,
            "pre286":before,"post287":after,"technical_field_checks":checks,
            "overflow_DEMUX_upper_bound":{"max_s_reg":max_load,"ordinary_increment_maximum":1,"fusion_threshold":19665,"no_overflow_source_possible":max_load+1<19665},
            "mechanism":"Each occupied center has the opposing record as its one active neighbor. The ordinary material branch returns RAW0 for rule_value0 before the directional reducer can act. They do not pass through occupied destinations to a later empty-center collision.",
            "distinction_from_W1":"W1 uses an empty-destination two-source reducer to form32dir0, then loses isolated material next tick. W2 loses two occupied records directly under survival precedence; no32 record is asserted there.",
            "scope":"The identified physical21 candidate is lost before inverse access; not a global proof that all historical information has vanished, and not rejection of the later probes."}
    put(args.output/"MATERIAL_BRANCH.json",result)


if __name__=="__main__":main()
