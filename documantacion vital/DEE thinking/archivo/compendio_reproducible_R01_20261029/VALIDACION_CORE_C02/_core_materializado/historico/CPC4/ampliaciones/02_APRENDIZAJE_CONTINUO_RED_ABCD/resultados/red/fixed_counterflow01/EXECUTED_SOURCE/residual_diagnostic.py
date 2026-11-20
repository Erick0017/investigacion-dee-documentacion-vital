"""One frozen local replay and one explicit one-site counterfactual.

The passively reconstructed reducer only checks the saved transition. Native
outputs are always obtained by advancing the immutable official Runtime.
"""
from __future__ import annotations
from datetime import datetime,timezone
from itertools import product
from pathlib import Path
import argparse,json,sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/"src"))
from red import recipe_v3 as r
from red.dual_session import NetworkSession
from red.dual_habitat import evaluate


def neighborhood(world,site):
    return [{"offset":list(off),**r.observe(world,r.moved(site,off))}
            for off in product((-1,0,1),repeat=3) if off!=(0,0,0)]


def empty_branch(world,site):
    center=r.observe(world,site);neighbors=neighborhood(world,site)
    alive={tuple(q["offset"]):q["active"] for q in neighbors}
    active=sum(alive.values());grad=[-sum(q["offset"][i]*q["s_reg"] for q in neighbors if q["state"]>0) for i in range(3)]
    symmetric=sum(alive[off]==alive[tuple(-v for v in off)] for off in alive)//2
    crystal=active>0 and sum(abs(v) for v in grad)//19665>=int(9.887**3) and not any(q["semantic"]==5 for q in neighbors)
    xnor=symmetric==13 and active>=8
    proposals=[q for q in neighbors if q["direction"]!=[0,0,0] and r.moved(q["site"],q["direction"])==tuple(site)]
    vector=[sum(q["direction"][i] for q in proposals) for i in range(3)]
    direction=[(v>0)-(v<0) for v in vector]
    predicted={"s_reg":min(19664,sum(q["s_reg"] for q in proposals)),"direction":direction,"state":1,"semantic":1} if proposals else None
    return {"center":center,"neighbors26":neighbors,"n_active":active,"gradient":grad,"xnor_symmetric_pairs":symmetric,
            "crystallization_guard":crystal,"xnor_guard":xnor,"directional_sources":proposals,"direction_sum":vector,
            "reconstructed_empty_directional_result":predicted,"branch_scope":"Empty-destination directional reducer only, before material branch and poststep DEMUX. No hidden ablations; fields are passive reconstruction of the current saved state."}


def main():
    p=argparse.ArgumentParser();p.add_argument("--parent",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    canonical=a.parent.parent/"T437.deetsnap"
    config={"frozen_utc":datetime.now(timezone.utc).isoformat(),"parent":str(a.parent.resolve()),"parent_sha256":r.sha(a.parent),
       "worker_sha256":r.sha(__file__),"hypothesis":"Unused role.turn5 emitted291 returns after2*67 ticks and meets B42 at R425, producing47 and diverting the Flat action.",
       "passive_window":[417,424,425,426,437],"diagnostic_fork":{"tick":424,"site":[22,40,13],"raw":0,"preserve_all_clocks":True},
       "no_new_inputs":True,"no_new_preparation":True,"interpretation":"One-site conditional necessity/rescue in this saved background, not autonomous repair or a new successful MAIN."}
    r.put(out/"EXPERIMENT_CONFIG.json",config)
    session=NetworkSession.load(a.parent);spec=session.spec
    sites={"collision":spec["role"]["turn_site"],"old_relay_pre":r.moved(spec["role"]["turn_site"],(0,0,1)),
           "B_action_pre":r.moved(spec["role"]["turn_site"],(1,-1,0))}
    session.run_until(424);before=r.digest(session.world)
    branch=empty_branch(session.world,sites["collision"])
    actual_relay=r.observe(session.world,sites["old_relay_pre"])
    if actual_relay["s_reg"]!=5 or actual_relay["direction"]!=[0,0,-1]:raise RuntimeError("Frozen residual source hypothesis not present; no edit is permitted")
    session.save(out/"PASSIVE_T424.deetsnap")
    child,edit=r.edit_actual(session.world,sites["old_relay_pre"],5,"REMOVE_CONFIRMED_RESIDUAL_RELAY_AT424",raw=0)
    shared_pre_R={name:r.observe(session.world,bank["resource_receiver"]) for name,bank in spec["banks"].items() if bank["resource_read"]==424}
    rescue_session=NetworkSession(child,spec,json.loads(json.dumps(session.state)));rescue_session._commit()
    captures={"passive":{name:{} for name in spec["banks"]},"rescue":{name:{} for name in spec["banks"]}}
    traces={"passive":[],"rescue":[]}
    for label,model in (("passive",session),("rescue",rescue_session)):
        world=model.world
        for tick in (424,425,426,427,430,431,437):
            model.run_until(tick)
            samples={name:r.observe(world,site) for name,site in sites.items()}
            samples["diverted_segment"]=r.observe(world,r.moved(sites["collision"],(-1,1,-1),tick-425)) if tick>=425 else None
            samples["flat_segment"]=r.observe(world,r.moved(spec["centers"]["B"],(-1,1,0),tick-417))
            traces[label].append({"tick":tick,"samples":samples})
            for name,bank in spec["banks"].items():
                if tick==bank["resource_read"]:
                    if tick==424 and label=="rescue":captures[label][name]["R"]=shared_pre_R[name]
                    else:captures[label][name]["R"]=r.observe(world,bank["resource_receiver"])
                if tick==bank["function_read"]:captures[label][name]["F"]=r.observe(world,bank["function_receiver"])
        model.save(out/(label.upper()+"_T437.deetsnap"))
    canonical_world=NetworkSession.load(canonical)
    result={"config":config,"before424":before,"sites":sites,"local_branch424":branch,"edit":edit,
       "trace":traces,"captures":captures,"outcomes":{label:evaluate(world,spec,captures[label]) for label,world in (("passive",session.world),("rescue",child))},
       "canonical437":r.digest(canonical_world.world),"passive_reproduces_canonical437":r.digest(session.world)==r.digest(canonical_world.world),
       "source_snapshot_unchanged_sha256":r.sha(a.parent),"source_snapshot_unchanged":r.sha(a.parent)==config["parent_sha256"],
       "scope":"The replay is intact. The child differs by one RAW deletion at424 and zero clocks; later changed trajectories are Native. Neither fork is returned to MAIN. ResourceN at424 is shared pre-intervention context."}
    r.put(out/"MEASUREMENTS.json",result)
    print(json.dumps({"profiles":{k:v["profiles"] for k,v in result["outcomes"].items()},"replay_equal":result["passive_reproduces_canonical437"]}))


if __name__=="__main__":main()
