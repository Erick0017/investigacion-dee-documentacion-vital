"""New finite experiments, gated on the separately qualified installed 4.0 WHL.

No historical runner is imported. Contact preparations are explicit research
interfaces; production sessions, acquisition, composition and evolution use the
public compiled library. This script does not publish a release or a verdict.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def qualify(path):
    import dee_thinking as dee
    qualified = json.loads(Path(path).read_text(encoding="utf-8"))
    assert qualified.get("qualified") is True, "BLOQUE I must be qualified before new experiments"
    assert dee.__version__ == "4.0.0" and dee.kernel_identity()["kernel_version"] == 27
    assert Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), "Installed non-editable product required"
    assert "site-packages" in str(Path(dee.__file__).resolve())
    assert Path(qualified["python_executable"]).resolve() == Path(sys.executable).resolve()
    assert qualified["version"] == "4.0.0" and qualified["kernel"] == 27
    assert sha(dee._native.__file__) == qualified["native_sha256"], "Loaded native extension differs from the qualified build"
    wheel = Path(path).resolve().parent.parent / "wheel" / "dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"
    assert sha(wheel) == qualified["wheel_sha256"], "Wheel differs from the qualified artifact"
    installed_package = Path(dee.__file__).resolve().parent
    python_members = {}
    with zipfile.ZipFile(wheel) as archive:
        for member in archive.namelist():
            if member.startswith("dee_thinking/") and member.endswith((".py", ".pyi")):
                relative = Path(member).relative_to("dee_thinking")
                installed = installed_package / relative
                expected = hashlib.sha256(archive.read(member)).hexdigest()
                assert installed.is_file() and sha(installed) == expected, "Installed Python implementation differs from qualified wheel: " + member
                python_members[member] = expected
    assert "dee_thinking/cognition.py" in python_members and "dee_thinking/dialogue.py" in python_members
    return {"qualification_sha256": sha(path), "wheel_sha256": qualified["wheel_sha256"],
            "wheel": str(wheel), "installed_python_member_hashes": python_members,
            "python": sys.executable, "module": dee.__file__, "native": dee._native.__file__,
            "native_sha256": sha(dee._native.__file__), "version": dee.__version__, "kernel": 27}


def observation(value):
    r = value.record
    return {"tick": value.tick, "site": [value.coordinate.x,value.coordinate.y,value.coordinate.z],
            "raw": value.raw, "clock": value.clock, "state": r.state, "semantic": r.semantic,
            "s_reg": r.s_reg, "direction": [r.dx,r.dy,r.dz], "active": r.state > 0 and r.semantic != 5}


def digest(world):
    rt = world.runtime
    return {"tick": rt.current_tick,
            "raw_sha256": hashlib.sha256(array("Q",rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256": hashlib.sha256(array("Q",rt.clock_copy()).tobytes()).hexdigest()}


def movement_case(dee,spec,output):
    n=34;origin=spec.get("translation",[0,0,0]);phase=spec.get("local_clock",0)
    descriptions=[([8,8,8],[1,0,0],5,13),([22,5,24],[0,1,0],9,17)]
    placements=[];targets=[];prepared=[]
    for start,direction,distance,value in descriptions:
        start=[(x+y)%n for x,y in zip(start,origin)]
        target=[(x+distance*d)%n for x,d in zip(start,direction)]
        p=dee.InitialPlacement();p.site=dee.Coordinate(*start);p.clock=phase
        p.raw=dee.pack_record(1,value,*direction,1);p.role="Declared native movement signal"
        placements.append(p);targets.append(target)
        prepared.append({"source":start,"direction":direction,"target":target,"distance":distance,
                         "s_reg":value,"initial_local_clock":phase})
    recipe=dee.OrganizationRecipe.research(n,placements,0);recipe.execution=dee.TickOptions(dee.Backend.LAZY,1)
    world=dee.OrganizationalWorld.create(recipe);world.save_snapshot(str(output/"T0.deetsnap"))
    forecast={"recorded_before_evolution":True,"attribution":"INSTRUMENTO",
              "method":"Declared free-transport geometry, not a DEE-acquired forecast", "arrival_ticks":[5,9]}
    write(output/"BEFORE_EVOLUTION_INSTRUMENT_FORECAST.json",forecast)
    first=[None,None];trace=[]
    for tick in range(13):
        readings=[observation(world.runtime.observe(dee.Coordinate(*target))) for target in targets]
        for j,o in enumerate(readings):
            if o["active"] and first[j] is None:first[j]=tick
        trace.append({"tick":tick,"targets":readings})
        if tick<12:world.advance()
    world.save_snapshot(str(output/"MAIN_FINAL.deetsnap"))
    return {"identity":spec["id"],"modality":"NATIVE_EVOLUTION_AFTER_DECLARED_RESEARCH_PREPARATION",
        "preparation":prepared,"trace":trace,"first_arrival_ticks":first,"before_evolution_instrument_forecast":forecast,
        "scope":"Transport, arrival time, route and initial local clock measured separately; this alone is not acquisition or learned anticipation",
        "phase_contrast":"Only initial local clocks change in the phase arm; no clock resets after T0", "final":digest(world)}


def contact_case(dee, spec, output):
    """One native finite encounter; no T, energy or FDT is inferred from load."""
    n=34; shift=spec.get("translation",[0,0,0]); target=[(14+s)%n for s in shift]
    directions=[[1,0,0],spec.get("second_direction",[0,1,0])]
    placements=[]; starts=[]
    for j,(value,direction) in enumerate(zip(spec.get("loads",[12,24]),directions)):
        q=[(x-5*d)%n for x,d in zip(target,direction)]
        if j==1 and spec.get("offpath"):
            q[2]=(q[2]+7)%n
        p=dee.InitialPlacement();p.site=dee.Coordinate(*q);p.clock=0
        p.raw=dee.pack_record(1,value,*direction,1);p.role="Declared current "+str(j)
        placements.append(p);starts.append({"site":q,"raw":p.raw,"direction":direction,"load":value})
    recipe=dee.OrganizationRecipe.research(n,placements,0)
    recipe.execution=dee.TickOptions(dee.Backend.LAZY,1)
    world=dee.OrganizationalWorld.create(recipe);world.save_snapshot(str(output/"T0.deetsnap"))
    trace=[];first_active=None
    for tick in range(13):
        rt=world.runtime;raw=rt.raw_copy();active=[]
        for linear,value in enumerate(raw):
            if not value:continue
            r=dee.decode_record(value)
            if r.state>0 and r.semantic!=5:
                # Native idx3d is ((x*N)+y)*N+z: z is the fast axis.
                q=[linear//(n*n),(linear//n)%n,linear%n]
                assert dee.linear_index(*q,n)==linear
                active.append({"site":q,"raw":value,"state":r.state,"semantic":r.semantic,
                               "s_reg":r.s_reg,"direction":[r.dx,r.dy,r.dz]})
        center=observation(rt.observe(dee.Coordinate(*target)))
        if 4<=tick<=6 and center["active"] and first_active is None:first_active=center
        trace.append({"tick":tick,"target":center,"active":active,
            "observer_vector":{"active_count":len(active),"sum_s_reg_not_energy":sum(x["s_reg"] for x in active),
                "direction_counts":{str(d):sum(x["direction"]==d for x in active) for d in directions},
                "left_count":sum(x["site"][0]<target[0] for x in active),
                "right_count":sum(x["site"][0]>=target[0] for x in active)}})
        if tick in (5,6):world.save_snapshot(str(output/("T"+str(tick)+".deetsnap")))
        if tick<12:world.advance()
    world.save_snapshot(str(output/"FINAL.deetsnap"))
    # A registered, injective direction pattern code for current active records.
    # It reads no case ID, expected result or history label. Missing is null.
    code=(1+(first_active["direction"][0]+1)+3*(first_active["direction"][1]+1)+9*(first_active["direction"][2]+1)) if first_active else None
    return {"identity":spec["id"],"modality":"NATIVE_EVOLUTION_AFTER_DECLARED_RESEARCH_PREPARATION",
            "preparation":{"N":n,"initial_records":starts,"target":target,"initial_inventory":sum(spec.get("loads",[12,24]))},
            "trace":trace,"first_current_contact_record":first_active,"fixed_direction_codec":code,
            "codec_contract":"Current active direction only:1+(dx+1)+3*(dy+1)+9*(dz+1); null if no current target record in frozen4..6 window",
            "final":digest(world),"scope":"Native contact and organizational contrast; no calibrated temperature, thermodynamic energy or FDT measurement",
            "temperature_attempt":{"executed":True,"measured":"finite regional/native field exchange and direction-dependent contact",
                                   "not_established":["thermodynamic temperature","energy equivalence of s_reg","equilibrium","FDT"]}}


def acquired_case(dee,spec,output):
    from dee_thinking.cognition import create_session
    output.mkdir(parents=True,exist_ok=True)
    parameters=dee.NativeAssociationParameters();parameters.translation=dee.Coordinate(*spec.get("translation",[0,0,0]))
    session=dee.NativeAssociationSession.create(parameters)
    forms=spec.get("forms",{"zuvi":0,"pako":1})
    session.set_interface_metadata("blockII.external_forms",json.dumps(forms,separators=(",",":")))
    session.save_snapshot(str(output/"T0.deetsnap"))
    teaching=session.train(spec["teachers"],5,spec.get("mode","paired"))
    session.save_snapshot(str(output/"ACQUIRED_T6.deetsnap"))
    before=digest(session.world);passive=[session.observe(),session.observe()]
    assert digest(session.world)==before
    queries=spec.get("queries",[13,17,21]);session.start_sequence(queries,"new_native_phenomenon_queries",6)
    session.run_until(11);session.save_snapshot(str(output/"SEQUENCE_T11.deetsnap"))
    before_restore=digest(session.world)
    session=dee.NativeAssociationSession.load_snapshot(str(output/"SEQUENCE_T11.deetsnap"))
    assert digest(session.world)==before_restore
    session.run_until(6+5*len(queries))
    protocol=session.world.protocols[-1]
    captures=[]
    for step in protocol.steps:
        receipts=[]
        for identity in step.receipt_ids:
            receipt=session.world.runtime.receipt(identity)
            receipts.append({"id":identity,"status":str(receipt.status),"requested_tick":receipt.requested_tick,
                "effective_tick":receipt.effective_tick,"reason":receipt.reason} if receipt is not None else
                {"id":identity,"status":"MISSING_RECEIPT"})
        captures.append({"query":step.input,"input_tick":step.input_tick,"read_tick":step.read_tick,
                         "physical":[observation(o) for o in step.captured],"receipts":receipts})
    final=digest(session.world);session.save_snapshot(str(output/"MAIN_FINAL.deetsnap"))
    # Evaluate only; the oracle is never passed to a world/interface/decoder.
    expected=[[q+5+t for t in spec["teachers"]] for q in queries]
    actual=[[o["s_reg"] if o["active"] else None for o in row["physical"]] for row in captures]
    return {"identity":spec["id"],"modality":"EXPERIENCE_PROTOCOL_THEN_NATIVE_EVOLUTION",
            "teaching":teaching,"teacher_provenance":spec.get("teacher_provenance"),
            "same_native_main":True,"operational_forks":0,"queries":queries,"captures":captures,
            "explicit_save_load_mid_protocol":{"tick":11,"raw_and_clock_preserved":True,"remaining_queries_executed_after_restore":len(queries)-1},
            "forms_interface_only":forms,"fixed_decoder_by_form":[{form:row[port] for form,port in forms.items()} for row in actual],
            "fixed_site_final_observer":session.observe(),"passive_observation_unchanged":True,
            "evaluation_only":{"first_query_expected_if_paired":expected[0],"actual":actual,
                "sequential_expected_is_not_reused":"Later physical queries alter the mobile relations; no invariant first-query oracle is imposed"},
            "actual_external_operations":list(session.world.external_operations),"final":final,
            "scope":"Two fixed physical routes, acquired additive transformations. Opaque names are not an arbitrary learned dictionary."}


def online_signal_case(dee,spec,output):
    """One finite moving organization experiences a native contact in its world.

    All resources and both probe requests are declared before the first advance.
    Unlike the measured-contact replay arm, no host codec transports a teacher
    between worlds. The observer uses the frozen geometry, not a response oracle.
    """
    n=47;shift=spec.get("translation",[0,0,0])
    def point(q):return [(a+b)%n for a,b in zip(q,shift)]
    recipe_inputs=[([17,22,25],12,[1,0,0],"environment_current_A"),
                   ([22,17,25],24,[0,1,0],"environment_current_B"),
                   ([33,25,25],5,[-1,0,0],"finite_organization_cue")]
    if spec.get("contact_cut"):recipe_inputs[1][0][2]+=7
    if spec.get("cue_offpath"):recipe_inputs[2][0][2]+=4
    placements=[]
    for site,load,direction,role in recipe_inputs:
        placement=dee.InitialPlacement();placement.site=dee.Coordinate(*point(site));placement.clock=0
        placement.raw=dee.pack_record(1,load,*direction,1);placement.role=role;placements.append(placement)
    recipe=dee.OrganizationRecipe.research(n,placements,0);recipe.execution=dee.TickOptions(dee.Backend.LAZY,1)
    probes=[("common_probe_1",[30,33,25],11,spec.get("queries",[13,19])[0]),
            ("common_probe_2",[25,38,25],16,spec.get("queries",[13,19])[1])]
    interfaces=[]
    for name,site,at_tick,payload in probes:
        interface=dee.InterfaceSpec();interface.name=name
        channel=dee.ChannelSpec();channel.name=name;channel.injection_site=dee.Coordinate(*point(site))
        channel.direction=dee.Direction(-1,0,0);channel.allow_experience=False;channel.allow_probe=True
        interface.channel=channel;interfaces.append(interface)
    recipe.interfaces=interfaces
    world=dee.OrganizationalWorld.create(recipe)
    requests=[world.probe(name,payload,at_tick) for name,site,at_tick,payload in probes]
    def pending_state(current):
        return {"channels":list(current.runtime.channel_names),"receipts":[{
            "id":r.id,"status":str(r.status),"requested_tick":r.requested_tick,
            "effective_tick":r.effective_tick,"channels":list(r.channels),"reason":r.reason}
            for r in current.runtime.receipts]}
    world.save_snapshot(str(output/"T0_PENDING_PROBES.deetsnap"))
    declared={"environment_contact":point([22,22,25]),"acquisition_encounter":point([25,25,25]),
              "common_response_1":point([25,33,25]),"common_response_2":point([20,38,25])}
    trace=[];restoration=None
    for tick in range(23):
        row={"tick":tick,"readings":{name:observation(world.runtime.observe(dee.Coordinate(*site))) for name,site in declared.items()}}
        trace.append(row)
        if tick in (5,8,16,21):world.save_snapshot(str(output/("STATE_T"+str(tick)+".deetsnap")))
        if tick==9:
            world.save_snapshot(str(output/"ACQUIRED_PENDING_T9.deetsnap"));prior=digest(world);pending=pending_state(world)
            world=dee.OrganizationalWorld.load_snapshot(str(output/"ACQUIRED_PENDING_T9.deetsnap"))
            restoration={"tick":9,"before":prior,"after":digest(world),"pending_before":pending,"pending_after":pending_state(world)}
            assert restoration["before"]==restoration["after"]
            assert restoration["pending_before"]==restoration["pending_after"]
        if tick<22:world.advance()
    receipts=[]
    for request in requests:
        actual=world.runtime.receipt(request.id)
        receipts.append({"id":actual.id,"status":str(actual.status),"requested_tick":actual.requested_tick,
                         "effective_tick":actual.effective_tick,"reason":actual.reason})
    world.save_snapshot(str(output/"MAIN_FINAL.deetsnap"))
    return {"identity":spec["id"],"modality":"NATIVE_WORLD_EXPERIENCE_THEN_FIXED_PHYSICAL_PROBES",
            "preparation":{"dimension":n,"resources":[{"site":point(site),"load":load,"direction":direction,"role":role} for site,load,direction,role in recipe_inputs],
                           "all_requests_before_first_advance":True,"probes":[{"port":name,"site":point(site),"requested_tick":at_tick,"payload":payload} for name,site,at_tick,payload in probes]},
            "trace":trace,"declared_observers":declared,"receipts":receipts,"restoration":restoration,
            "same_native_main":True,"operational_forks":0,"final":digest(world),
            "actual_external_operations":list(world.external_operations),
            "scope":"Finite moving relation, not a renewable basal body; native contact can enter the same world/organization before two consumable common probes. No host teacher codec, adaptive event installation or hidden recreation."}


def dialogue_case(dee,spec,output):
    from dee_thinking.dialogue import ConversationSession
    ui=ConversationSession("composicion",directory=output,preparation={"translation":spec.get("translation",[0,0,0])})
    a,b=spec["teachers"]
    events=["Instancia nueva",f"Enseña dos relaciones 3,{a} y 3,{b}",
            "A esto lo llamaremos encuentro de dos trazas", "Guarda la sesión en antes_pregunta_nueva.deetsnap",
            "Carga antes_pregunta_nueva.deetsnap", f"Consulta nueva {spec['query']}","Por qué", "Guarda la sesión en MAIN_FINAL.deetsnap"]
    rows=[];saved=None
    for event in events:
        response=ui.execute(event);rows.append({"input":event,"response":response,"tick":ui.session.tick})
        if event.startswith("Guarda la sesión en antes_"):saved=digest(ui.session.world)
        if event.startswith("Carga antes_"):assert digest(ui.session.world)==saved
        with (output/"DIALOGOS.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(rows[-1],ensure_ascii=False)+"\n")
    return {"identity":spec["id"],"modality":"EXPERIENCE_PROTOCOL_AND_FIXED_SPANISH_INTERFACE",
        "events":events,"rows":rows,"new_question_after_load":{"payload":spec["query"],"previously_queried":False,
            "question_external_description":"¿Qué respuesta produce combinar las dos relaciones adquiridas del fenómeno para esta consulta nueva?"},
        "human_name_assigned_after_native_regularities":True,"name_scope":"External translation; not a learned arbitrary dictionary",
        "restored_physical_continuity":True,"final":digest(ui.session.world)}


def composition_case(dee,spec,output):
    world=dee.create_learnable_cascade(2,dee.Coordinate(*spec.get("translation",[0,0,0])),dee.TickOptions(dee.Backend.LAZY,1))
    world.save_snapshot(str(output/"T0.deetsnap"))
    receipts=dee.experience_composition(world,spec["pairs"],spec.get("omit"))
    world.save_snapshot(str(output/"ACQUIRED_T6.deetsnap"))
    before=digest(world);answer=dee.query_composition(world,spec["query"])
    world.save_snapshot(str(output/"MAIN_FINAL.deetsnap"))
    return {"identity":spec["id"],"modality":"EXPERIENCE_PROTOCOL_THEN_NATIVE_COMPOSITION",
            "pairs":spec["pairs"],"receipts":receipts,"before_new_query":before,
            "query":spec["query"],"answer":answer,"final":digest(world),
            "actual_external_operations":list(world.external_operations),
            "coordinator_calls":["create_learnable_cascade","experience_composition","query_composition","save_snapshot"],
            "scope":"One native Runtime, two acquired relations, one previously unused common query"}


def observer_cut(dee,spec,output):
    session=dee.NativeAssociationSession.create();session.train(spec["teachers"],5,"paired")
    world=session.world;before=digest(world)
    # Catalog declares a mobile +y relation born at the junction at3; at6 the
    # declared segment is junction+(0,3,0). Validate actual fields before edit.
    hub=world.view("l0").spec.ports["learned_relation"]
    site=dee.Coordinate(hub.x,(hub.y+3)%34,hub.z);current=world.runtime.observe(site)
    if not(current.record.state>0 and current.record.semantic==1
           and [current.record.dx,current.record.dy,current.record.dz]==[0,1,0]):
        return {"status":"INSTRUMENTATION_BLOCKED","current":observation(current),"reason":"Declared mobile segment not present; no alternative site selected after seeing result"}
    edit=dee.ResearchStateEdit();edit.coordinate=site;edit.raw=0;edit.label="Explicit diagnostic removal of one actual learned carrier; clock preserved"
    cut=world.diagnostic_fork([edit],True)
    cut.start_mobile_sequence("cut_query",[spec["query"]],6);cut.run_until(11)
    intact=world.fork();intact.start_mobile_sequence("intact_query",[spec["query"]],6);intact.run_until(11)
    assert digest(world)==before
    cut.save_snapshot(str(output/"DIAGNOSTIC_CUT_FINAL.deetsnap"));intact.save_snapshot(str(output/"DIAGNOSTIC_INTACT_FINAL.deetsnap"))
    return {"identity":spec["id"],"modality":"DIAGNOSTIC_FORK_NOT_MAIN_EXPERIENCE",
            "intervention":{"site":[site.x,site.y,site.z],"raw_before":current.raw,"raw_after":0,"clock_preserved":current.clock},
            "intact":[observation(o) for o in intact.protocols[-1].steps[-1].captured],
            "cut":[observation(o) for o in cut.protocols[-1].steps[-1].captured],
            "main_unchanged":True,"scope":"Investigator contrast, not introspection or autonomous self-removal"}


def child(root,qualification,case_path,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    identity=qualify(qualification)
    import dee_thinking as dee
    spec=json.loads(Path(case_path).read_text(encoding="utf-8"));start=time.monotonic()
    handlers={"movement":movement_case,"contact":contact_case,"acquired":acquired_case,"composition":composition_case,"observer_cut":observer_cut,"dialogue":dialogue_case,"online_signal":online_signal_case}
    result=handlers[spec["family"]](dee,spec,output)
    result.update(product=identity,case=spec,runner_sha256=sha(__file__),elapsed_seconds=time.monotonic()-start,
                  closed_utc=datetime.now(timezone.utc).isoformat())
    write(output/"MEASUREMENTS.json",result)


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True)
    p.add_argument("--qualification",type=Path,required=True);p.add_argument("--python",type=Path)
    p.add_argument("--child",type=Path);p.add_argument("--output",type=Path)
    p.add_argument("--online-signal",action="store_true",help="Include one finite second apparatus family: native contact to acquired relation in the same Runtime")
    args=p.parse_args()
    if args.child:
        child(args.root,args.qualification,args.child,args.output);return
    assert args.python,"Use the isolated installed, qualified4.0 interpreter"
    root=args.root.resolve();sys.path.insert(0,str(root));from supervise40 import run
    seal=json.loads(args.qualification.read_text(encoding="utf-8"));assert seal.get("qualified") is True
    out=root/"experiments/BLOCK_II";out.mkdir(parents=True,exist_ok=True)
    movement=[{"id":"native_arrival_routes","family":"movement"},
              {"id":"native_arrival_phase","family":"movement","local_clock":11},
              {"id":"reserved_native_arrival","family":"movement","translation":[3,1,2],"local_clock":7}]
    contacts=[{"id":"contact_y","family":"contact"},{"id":"contact_z","family":"contact","second_direction":[0,0,1]},
              {"id":"no_contact","family":"contact","offpath":True},
              {"id":"reserved_contact_y","family":"contact","translation":[2,3,1]},
              {"id":"reserved_contact_z","family":"contact","translation":[2,3,1],"second_direction":[0,0,1]}]
    write(out/"EXPERIMENT_CONFIG.json",{"schema":1,"movement_frozen":movement,"contacts_frozen":contacts,"reserved_queries":[19,23],
        "main_query_sequence":[13,17,21],
        "numeric_panels_frozen":{"transport":"first actual active target observation, compared with declared5/9 free transport baseline",
            "contact":"direction pattern codes for equal initial load inventory; no temperature estimate",
            "history":"same fixed query/readout: paired vs inverted, unpaired, omitted and explicit actual-carrier removal",
            "sequential":"physical current captures in one genealogy, no invariant first-response requirement",
            "composition":"two acquired relations vs one omitted; fresh23 query after save/load at6"},
        "opaque_forms_fixed_before_exposure":{"zuvi":0,"pako":1},"swapped_forms_control":{"zuvi":1,"pako":0},
        "codec":"Current active contact direction -> registered1..27 pattern, no hidden case identity",
        "native_family":"acquired mobile relations and composition", "maximum_methods_per_obstacle":3,
        "temperature_scope":"finite contact/regional field observations only; no T=s_reg or FDT claim",
        "reserved_communication_frozen":{"id":"spanish_reserved_combined_question","family":"dialogue","query":29,"translation":[1,2,0],
            "teachers":"fixed direction codes measured from contact_y and contact_z; data inputs, not fitted response parameters",
            "scope":"One supplemental reserved interface realization; counted once, not a new capability"},
        "online_signal_family_enabled":args.online_signal,
        "online_signal_frozen":[{"id":"online_contact_main","family":"online_signal"},{"id":"online_contact_route_cut","family":"online_signal","contact_cut":True},
                               {"id":"online_cue_offpath","family":"online_signal","cue_offpath":True},
                               {"id":"reserved_online_contact","family":"online_signal","translation":[2,3,1],"queries":[17,23]}] if args.online_signal else []})
    rows=[]
    def execute(spec):
        folder=out/spec["id"];folder.mkdir(parents=True,exist_ok=True);config=folder/"CASE.json";write(config,spec)
        if (folder/"MEASUREMENTS.json").exists():
            actual=json.loads((folder/"MEASUREMENTS.json").read_text(encoding="utf-8"));assert actual["case"]==spec
            assert actual["product"]["wheel_sha256"]==seal["wheel_sha256"], "A completed case belongs to another qualified artifact; preserve it rather than silently mixing cuts"
            rows.append(actual);return actual
        name="blockII_"+spec["id"];attempt=1
        while (root/"jobs"/name).exists():
            attempt+=1;name="blockII_"+spec["id"]+"_attempt"+str(attempt)
        job=run(root,name,[str(args.python),"-I","-B",str(Path(__file__).resolve()),"--root",str(root),
            "--qualification",str(args.qualification.resolve()),"--child",str(config.resolve()),"--output",str(folder.resolve())],180,cwd=str(out))
        if job["exit_code"]==0:actual=json.loads((folder/"MEASUREMENTS.json").read_text(encoding="utf-8"))
        else:actual={"case":spec,"status":"TECHNICAL_ERROR","job":job}
        rows.append(actual)
        with (out/"CASE_LEDGER.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps({"id":spec["id"],"job":job,"measurement":str(folder/"MEASUREMENTS.json")})+"\n")
        write(out/"RESULTS.json",{"cases":rows,"not_independent_when_shared_measurement":True})
        return actual
    for spec in movement:execute(spec)
    if args.online_signal:
        for spec in [{"id":"online_contact_main","family":"online_signal"},{"id":"online_contact_route_cut","family":"online_signal","contact_cut":True},
                     {"id":"online_cue_offpath","family":"online_signal","cue_offpath":True},
                     {"id":"reserved_online_contact","family":"online_signal","translation":[2,3,1],"queries":[17,23]}]:execute(spec)
    measured={spec["id"]:execute(spec) for spec in contacts}
    a=measured["contact_y"].get("fixed_direction_codec");b=measured["contact_z"].get("fixed_direction_codec")
    if a is None or b is None:
        write(out/"CHAIN_BOUNDARY.json",{"status":"NATIVE_CONTACT_CODEC_UNAVAILABLE","observed":[a,b],
            "reason":"Frozen contact window lacked a usable native record; no teacher or expected response invented"});return
    provenance={"mode":"EXTERNAL_REPLAY_OF_PREVIOUSLY_MEASURED_NATIVE_CONTACT_WITH_FIXED_CODEC",
        "measurements":["contact_y/MEASUREMENTS.json","contact_z/MEASUREMENTS.json"],"values":[a,b],
        "not_online_single_runtime_contact_to_memory":True}
    for spec in [
        {"id":"native_main","family":"acquired","teachers":[a,b]},
        {"id":"inverted_history","family":"acquired","teachers":[b,a]},
        {"id":"swapped_external_forms","family":"acquired","teachers":[a,b],"forms":{"zuvi":1,"pako":0}},
        {"id":"unpaired_history","family":"acquired","teachers":[a,b],"mode":"unpaired"},
        {"id":"omitted_history","family":"acquired","teachers":[a,b],"mode":"omitted"},
        {"id":"reserved_main","family":"acquired","teachers":[a,b],"translation":[3,2,1],"queries":[19,23,7]},
        {"id":"observer_memory_cut","family":"observer_cut","teachers":[a,b],"query":19},
        {"id":"new_combined_query","family":"composition","pairs":[[3,a],[3,b]],"query":17},
        {"id":"reserved_combined_query","family":"composition","pairs":[[3,a],[3,b]],"query":23,"translation":[2,3,1]},
        {"id":"omitted_combined_relation","family":"composition","pairs":[[3,a],[3,b]],"query":17,"omit":1},
        {"id":"spanish_new_combined_question","family":"dialogue","teachers":[a,b],"query":23},
        {"id":"spanish_reserved_combined_question","family":"dialogue","teachers":[a,b],"query":29,"translation":[1,2,0],"reserved_interface":True}]:
        spec["teacher_provenance"]=provenance;execute(spec)
    write(out/"RESULTS.json",{"cases":rows,"coverage":["movement_and_signal","finite_contact_temperature_attempt_not_temperature_estimate","organization_response","observer_and_probe_backaction"],
        "same_measurement_reused_not_independent":True,"host_coupling":"Native contact world -> fixed external codec -> separate acquired native MAIN declared, not native inter-Runtime transfer"})


if __name__=="__main__":main()
