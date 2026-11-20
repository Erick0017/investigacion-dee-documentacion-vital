"""Finite app persistence/adversarial checks, not new scientific samples."""
import argparse
import importlib.util
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);args=p.parse_args()
    root=args.root.resolve();out=root/"experiments/BLOCK_II/online_application_technical";out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location("online_app_under_test",root/"app/mundo_nativo.py")
    app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
    import dee_thinking as d
    assert d.__version__=="4.0.0" and d.kernel_identity()["kernel_version"]==27
    checks={};source=root/"experiments/BLOCK_II/online_demonstrator_main/pendiente11.deetsnap"
    history=[json.loads(x) for x in (source.parent/"DIALOGOS.jsonl").read_text(encoding="utf-8").splitlines()]
    observed=[x["response"]["physical_output"] for x in history if x["input"]=="Observa respuesta"]
    s=app.NativeWorldSession(out);loaded=s.load(source);checks["load_pending11"]=s.meta["stage"]=="PENDING1"
    checks["native_receipt_still_scheduled"]=s.receipt(s.meta["requests"][0]["id"])["status"]=="scheduled"
    checks["external_alias_restored"]=s.meta["aliases"]=={"encuentro diagonal":"current_native_encounter"}
    before=app.physical_digest(s.world);s.observe();s.observe();checks["passive_repeated_observation"]=before==app.physical_digest(s.world)
    first=s.response();checks["future_after_load_first_response"]=first["physical_output"]==observed[0]
    s.submit_question(19);s.save(out/"new_pending16.deetsnap");pending=app.physical_digest(s.world)
    s.load(out/"new_pending16.deetsnap");checks["second_pending_restore"]=pending==app.physical_digest(s.world)
    second=s.response();checks["new_question_after_load_evolves"]=second["physical_output"]==observed[1]
    s.save(out/"MAIN_FINAL.deetsnap");stable=app.physical_digest(s.world)

    def reject_metadata(name,source_path,mutation):
        world=d.OrganizationalWorld.load_snapshot(str(source_path));meta=json.loads(world.runtime.snapshot_metadata(app.KEY));mutation(meta)
        world.runtime.set_snapshot_metadata(app.KEY,json.dumps(meta));path=out/(name+".deetsnap");world.save_snapshot(str(path))
        try:s.load(path)
        except (ValueError,RuntimeError):checks[name]=app.physical_digest(s.world)==stable
        else:checks[name]=False
    reject_metadata("mismatched_translation_rejected",source,lambda x:x.update(translation=[2,3,1]))
    reject_metadata("translated_metadata_without_geometry_rejected",source,lambda x:x.update(translation=[2,3,1],preparation="reservada"))
    reject_metadata("missing_receipt_id_rejected",source,lambda x:x["requests"][0].update(id=999))
    reject_metadata("wrong_request_time_rejected",source,lambda x:x["requests"][0].update(requested_tick=16))
    reject_metadata("duplicate_receipt_id_rejected",out/"MAIN_FINAL.deetsnap",lambda x:x["requests"][1].update(id=x["requests"][0]["id"]))
    reject_metadata("invalid_stage_rejected",source,lambda x:x.update(stage="FINISHED"))

    recipe=d.OrganizationRecipe.research(47,list(s.world.recipe.placements),0)
    recipe.execution=d.TickOptions(d.Backend.LAZY,1);interfaces=[]
    for j,site in enumerate(([31,33,25],[25,38,25]),1):
        interface=d.InterfaceSpec();interface.name="world.query"+str(j);channel=d.ChannelSpec();channel.name=interface.name
        channel.injection_site=d.Coordinate(*site);channel.direction=d.Direction(-1,0,0);channel.allow_experience=False;channel.allow_probe=True
        interface.channel=channel;interfaces.append(interface)
    recipe.interfaces=interfaces;wrong=d.OrganizationalWorld.create(recipe)
    meta=dict(s.meta);meta.update(stage="T0",requests=[]);wrong.runtime.set_snapshot_metadata(app.KEY,json.dumps(meta))
    wrong.save_snapshot(str(out/"wrong_interface_geometry.deetsnap"))
    try:s.load(out/"wrong_interface_geometry.deetsnap")
    except (ValueError,RuntimeError):checks["wrong_interface_geometry_rejected"]=app.physical_digest(s.world)==stable
    else:checks["wrong_interface_geometry_rejected"]=False
    (out/"truncated.deetsnap").write_bytes(source.read_bytes()[:100])
    try:s.load(out/"truncated.deetsnap")
    except (ValueError,RuntimeError):checks["truncated_snapshot_rejected"]=app.physical_digest(s.world)==stable
    else:checks["truncated_snapshot_rejected"]=False
    result={"technical_checks":checks,"all_checks":all(checks.values()),"first_physical_output":first["physical_output"],
            "second_physical_output":second["physical_output"],"main_digest":stable,
            "scope":"Technical replay/continuation and malformed-state checks only; not additional independent science cases"}
    (out/"TECHNICAL_CHECKS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    assert result["all_checks"],checks
    print(json.dumps({"all_checks":True,"count":len(checks),"path":str(out/"TECHNICAL_CHECKS.json")}))


if __name__=="__main__":main()
