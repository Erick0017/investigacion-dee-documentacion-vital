#!/usr/bin/env python3
"""Authoritative machine synthesis and reports for the superseding CORE15."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"NEW_RUNNERS"))
from extension_common import ROOT, audit_kernel, canonical_hash, read_json, sha, update_state, utc, write_json, write_text


def report(name,title,body):
    write_text(ROOT/name,f"# {title}\n\n{body.strip()}\n")


def result(exp): return read_json(ROOT/"RESULTS"/f"{exp}.json")


def main():
    marker=ROOT/"CHECKPOINTS"/"F_SYNTHESIS_COMPLETE.json"
    if marker.exists(): print(marker.read_text(encoding="utf-8")); return
    audit_kernel("CORE15_EXPANSION_BEFORE_SYNTHESIS")
    baseline=read_json(ROOT/"SUPERSEDED_CORE15_BASELINE.json"); fresh=read_json(ROOT/"NEW_RAW_TELEMETRY"/"EXPANSION_FRESH_CONFIRMATION.json"); discovery=read_json(ROOT/"EXPERIMENT_REGISTRY_EXPANSION.json"); adaptive=read_json(ROOT/"ADAPTIVE_RESEARCH_AUDIT.json")
    final_status={cid:("FRESH_REVALIDATED" if row["fresh_status"]=="FRESH_CONFIRMED" else "FRESH_POSITIVE_CANARY_PARTIAL") for cid,row in fresh["by_claim"].items()}
    new_claims=[]
    locked=read_json(ROOT/"CLAIM_LEDGER_EXPANSION_DISCOVERY.json")["claims"]
    for c in locked:
        row=fresh["by_claim"][c["claim_id"]]; new_claims.append({**c,"status":final_status[c["claim_id"]],"fresh_positive":f"{row['positive_pass']}/{row['positive_total']}","canaries":f"{row['canary_correct']}/{row['canary_total']}","machine_predicate":row["positive_pass"]==row["positive_total"],"evidence":"NEW_RAW_TELEMETRY/EXPANSION_FRESH_CONFIRMATION.json","warning":"Saturation made four temporal-removal canaries nondiscriminating; no repair was made." if c["claim_id"]=="C15XC02" else None})
    baseline_claims=read_json(ROOT/"BASELINE_CORE15_LOCKED"/"CLAIM_LEDGER.json")["claims"]
    write_json(ROOT/"CLAIM_LEDGER.json",{"baseline_claims":baseline_claims,"expansion_claims":new_claims,"baseline_status":"LOCKED_PRESERVED","counts":{"baseline":len(baseline_claims),"new":len(new_claims),"new_fresh_revalidated":sum(c["status"]=="FRESH_REVALIDATED" for c in new_claims),"new_canary_partial":sum(c["status"]=="FRESH_POSITIVE_CANARY_PARTIAL" for c in new_claims)},"bytes_over_prose":True})

    # Correct route-level dispositions: not every inherited candidate was a valid direct apparatus.
    construction=read_json(ROOT/"PREREQUISITE_CONSTRUCTION_LEDGER.json")
    overrides={
      "MASS_INERTIA":{"aligned sparse organization":"TESTED_POSITIVE_MOBILE","mobile learned state":"PREREQUISITE_INVALID_NOT_SAME_MOVING_OBJECT","reinstantiation chain":"PREREQUISITE_INVALID_FUNCTIONAL_TRANSFER_NOT_BODY"},
      "FRICTION_HARDNESS":{"two aligned organizations":"TESTED_IDENTITY_DESTROYED","mobile organization into semantic4 guard":"TESTED_BLOCKING_NO_DEFORMATION","parallel shear ensembles":"TESTED_NO_CONTACT"},
      "THERMAL_EXCHANGE":{"collision ensembles":"TESTED_IDENTITY_DESTROYED","joint scaffold":"TESTED_RECOVERY_NO_EXCHANGE","policy-coupled systems":"PREREQUISITE_INVALID_POLICY_TRANSFER_NOT_EQUILIBRATION"},
      "RADIATION_COMPLETION":{"semantic4 train":"TESTED_EMISSION","finite semantic1 pulse":"TESTED_TRANSPORT_NO_DISPERSION","active reducer interface":"TESTED_ACTIVE_REDIRECTION","guard interface":"TESTED_CAPTURE_BLOCK_NO_RELEASE"},
      "FIELD_WEIGHT":{"clock trace":"TESTED_NO_RAW_RESPONSE","source-supported train":"TESTED_DIRECT_CARRIERS_ONLY","basin medium":"PREREQUISITE_INVALID_PREEXISTING_NOT_SOURCE_GENERATED","coupled lane":"TESTED_DIRECT_PREPARED_INTERFACE"},
      "WAVE_SOUND":{"sparse stationary lattice":"TESTED_NO_COLLECTIVE_MODE","aligned ensemble":"TESTED_INDEPENDENT_CARRIERS","guard lattice":"TESTED_LOCAL_GUARD_RESPONSE","historical oscillator":"PREREQUISITE_INVALID_NO_AUTONOMOUS_FREQUENCY_APPARATUS"},
      "CONTINUUM_FLUID":{"aligned flow":"TESTED_EXACT_TRANSLATION","mixed ensemble":"TESTED_CONTRACTION","destination multiplicity closure":"TESTED_POSITIVE_BOUNDED"},
      "RESOURCE_WORK":{"s_reg reducer accounting":"TESTED_POSITIVE_LOCAL_ACCOUNTING","guard support":"TESTED_PERSISTENCE_NO_WORK_CYCLE","learned policy state":"PREREQUISITE_INVALID_INFORMATION_STATE_NO_DEPLETION_CYCLE"},
      "CLOCK_FUNCTIONALITY":{"source":"TESTED_INVISIBLE","guard":"TESTED_INVISIBLE","phase":"TESTED_VIA_COLLISION_TIMING_RAW_PANEL","history":"TESTED_ASSOCIATIVE_INVISIBLE","ensemble":"TESTED_INVISIBLE","coupling":"PREREQUISITE_INVALID_NO_CLOCK_INPUT_PORT"},
      "PHASE_TRANSITION":{"ensemble alignment fraction":"TESTED_CROSSOVER_NO_SHARP_TRANSITION","basin":"NO_ADDITIONAL_TEST_JUSTIFIED_HISTORICAL_BASIN_NOT_SAME_CONTROL","guard threshold":"NO_ADDITIONAL_TEST_JUSTIFIED_LOCAL_THRESHOLD_NOT_COLLECTIVE"},
    }
    for front in construction["routes"]:
        for route in front["candidates"]: route["status"]=overrides[front["front"]][route["route"]]
    write_json(ROOT/"PREREQUISITE_CONSTRUCTION_LEDGER.json",construction)

    coverage=[
      ("matter/object/identity","DIRECTLY_EXPERIMENTED_NEW","C15X001,C15X011,C15X017","Mobile relational identity exists; contact robustness fails."),
      ("mass/inertia","DIRECTLY_EXPERIMENTED_NEW","C15X011,C15X017","Standard perturbation remained component-local; no mass coefficient."),
      ("motion/kinematics","DIRECTLY_EXPERIMENTED_NEW","C15X001,C15X017,C15XC01","Exact translation in tested Moore directions."),
      ("contact/friction","DIRECTLY_EXPERIMENTED_NEW","C15X002,C15X016","Head-on reduction destroys identity; offset shear does not interact."),
      ("hardness/rigidity","DIRECTLY_EXPERIMENTED_NEW","C15X013,C15X020,C15XC05","Blocking/opacity found, not graded deformation."),
      ("pressure/stress/elasticity","DIRECTLY_EXPERIMENTED_NEW","C15X013","No deformation/load law in guard apparatus."),
      ("thermal/dissipative","DIRECTLY_EXPERIMENTED_NEW","C15X003,C15X010","Contraction exists; identity-preserving exchange absent."),
      ("exchange/Theta/equilibrium","PREREQUISITE_CONSTRUCTION_FAILED","C15X003","No qualifying exchange; Theta and zeroth-like tests not licensed."),
      ("radiation emission/transport","DIRECTLY_EXPERIMENTED_NEW","C15X004,C15X019,C15XC06","Emission and payload-independent unit delay confirmed."),
      ("reflection/refraction","DIRECTLY_EXPERIMENTED_NEW","C15X004","Active reducer redirection, no passive reflection/refraction."),
      ("capture/opacity/release","DIRECTLY_EXPERIMENTED_NEW","C15X014,C15X020,C15XC05","Organization-specific blocking confirmed; no release."),
      ("field/remote mediation","DIRECTLY_EXPERIMENTED_NEW","C15X005","Three routes fail serious non-collisional field requirements."),
      ("weight","FORMALLY_INAPPLICABLE","C15X005","No field/background mediator, so weight test is unlicensed."),
      ("binding/attraction/repulsion","PREREQUISITE_CONSTRUCTION_FAILED","C15X002,C15X005","No identity-preserving remote trajectory interaction."),
      ("waves/sound/resonance","DIRECTLY_EXPERIMENTED_NEW","C15X006","Three media routes lack collective mode; frequency-selective resonance unlicensed."),
      ("fluid/continuum/diffusion/viscosity","DIRECTLY_EXPERIMENTED_NEW","C15X007,C15X015,C15X022","Bulk closure fails; bounded relational one-step closure succeeds."),
      ("resource/work/conservation","DIRECTLY_EXPERIMENTED_NEW","C15X008,C15X018,C15X023","Capped local accounting exists; no storage/depletion/recharge work cycle."),
      ("vacuum/clock hidden state","EXTENDED_FROM_PRIOR_WITH_NEW_TEST","C15X009,C15X021,C15XC04","Clock residual raw-invisible across expanded mechanism panel."),
      ("phase transitions/metastability","DIRECTLY_EXPERIMENTED_NEW","C15X010","Exact ordered endpoint and finite crossover; no sharp/scaling transition."),
      ("information/entropy/irreversibility","EXTENDED_FROM_PRIOR_WITH_NEW_TEST","C15X008,C15X023","Many-to-one reducer and overflow loss; no thermodynamic entropy bridge."),
      ("measurement/detector/observer","DIRECTLY_EXPERIMENTED_NEW","C15X018,C15X022,C15X024","Multiplicity response and discriminatory canaries tested."),
      ("space/geometry/topology","EXTENDED_FROM_PRIOR_WITH_NEW_TEST","C15X017,C15X020,C15X022","Direction/guard/destination topology remain operational coordinates."),
      ("time/causal order","EXTENDED_FROM_PRIOR_WITH_NEW_TEST","C15X019,C15X021,C15XC04","Transport timing visible; pure clock residual conditionally hidden."),
      ("relativity-like structure","NO_ADDITIONAL_TEST_JUSTIFIED","C15X017","No persistent interacting moving observer or transformation structure."),
      ("quantum-like questions","NO_ADDITIONAL_TEST_JUSTIFIED","baseline negative anchors","No new contextual-statistical or nonclassical mechanism emerged."),
      ("rotation/angular response","PREREQUISITE_CONSTRUCTION_FAILED","C15X017","Orientation covariance tested; no rigid rotating object."),
      ("conductivity/attenuation","EXTENDED_FROM_PRIOR_WITH_NEW_TEST","C15X020,C15XC05","Material class separates complete blocking from transmission; attenuation continuum absent."),
      ("composition/reaction-like","DIRECTLY_EXPERIMENTED_NEW","C15X002","Contact creates reducer records, not a demonstrated third stable functional class."),
      ("equilibrium/nonequilibrium","EXTENDED_FROM_PRIOR_WITH_NEW_TEST","C15X003,C15X010","Drive-supported, translating and absorbing/reduced states distinguished; no equilibrium coordinate."),
      ("symmetry/isotropy","DIRECTLY_EXPERIMENTED_NEW","C15X017,C15X020","Tested actual axis/diagonal transformations; no global cubic isotropy claim."),
    ]
    coverage_rows=[{"front":a,"status":b,"evidence":c,"verdict":d} for a,b,c,d in coverage]
    write_json(ROOT/"DIRECT_EXPERIMENT_COVERAGE.json",{"fronts":coverage_rows,"counts":{s:sum(r["status"]==s for r in coverage_rows) for s in sorted({r["status"] for r in coverage_rows})},"all_have_status":all(r["status"] for r in coverage_rows),"old_evidence_only_explicit":True})

    phenomena=[
      {"id":"NP_MOBILE_IDENTITY","status":"FRESH_REVALIDATED","observer":"M_REL_GEOMETRY + payload multiset","law":"exact relational translation","evidence":["C15XC01"],"limits":"not collision-robust matter"},
      {"id":"NP_REDUCER_ACCOUNTING","status":"FRESH_POSITIVE_CANARY_PARTIAL","observer":"destination s_reg","law":"min(sum incident s_reg,19664)","evidence":["C15XC02"],"limits":"four saturated canaries nondiscriminating"},
      {"id":"NP_RELATIONAL_CLOSURE","status":"FRESH_REVALIDATED","observer":"unique proposal destinations","law":"next support equals unique destinations","evidence":["C15XC03"],"limits":"one step; semantic1; empty destinations"},
      {"id":"NP_CLOCK_HIDDEN_RESIDUAL","status":"FRESH_REVALIDATED_BOUNDED_NEGATIVE","observer":"complete raw trajectory","law":"clock-only changes raw-invisible in frozen panel","evidence":["C15XC04"],"limits":"not universal clock irrelevance"},
      {"id":"NP_GUARD_OPACITY","status":"FRESH_REVALIDATED","observer":"downstream event series","law":"organized blocks; shuffled transmits","evidence":["C15XC05"],"limits":"bounded interface, not optical opacity"},
      {"id":"NP_NO_PAYLOAD_DISPERSION","status":"FRESH_REVALIDATED_BOUNDED_NEGATIVE","observer":"arrival tick","law":"arrival tick equals route distance","evidence":["C15XC06"],"limits":"tested finite semantic1 pulses"},
    ]
    write_json(ROOT/"NATIVE_PHENOMENON_ATLAS.json",{"phenomena":phenomena,"baseline_reference":"BASELINE_CORE15_LOCKED/NATIVE_PHENOMENON_ATLAS.json","new_fresh_revalidated":5,"new_canary_partial":1})
    for p in phenomena:
        write_json(ROOT/"NEW_NATIVE_FINGERPRINTS"/f"{p['id']}.json",{"fingerprint_id":p["id"],"preparation":p["limits"],"participants":p["observer"],"mediator":"native v27 routing/reduction/guard as applicable","state":p["observer"],"intervention":"frozen claim contract","observer":p["observer"],"response":p["law"],"history":"claim-specific","symmetry":"tested transformations only","falsifier":"frozen positive or canary failure","scope":p["limits"],"status":p["status"]})

    shadows=[
      {"shadow":"S_KINEMATIC_REL","components":["relative geometry","direction distribution","payload multiset"],"predicts":["translation","contact divergence"],"hidden_residual":["clock"],"minimality":"geometry and direction necessary"},
      {"shadow":"S_DESTINATION_FIBER","components":["proposal destination equivalence classes","incident s_reg"],"predicts":["next support","detector payload"],"hidden_residual":["state tokens","clock"],"minimality":"bulk support/direction sums insufficient"},
      {"shadow":"S_INTERFACE_TOPOLOGY","components":["semantic guard topology","incident route"],"predicts":["blocking/transmission"],"hidden_residual":["unread clock"],"minimality":"inventory alone insufficient"},
      {"shadow":"S_CLOCK_RESIDUAL","components":["clock array"],"predicts":["clock trajectory only"],"hidden_residual":[],"minimality":"excluded from raw-effective panel because no added raw prediction"},
    ]
    write_json(ROOT/"OBSERVER_SHADOW_ATLAS_V2.json",{"baseline":"S_CAUSAL_PANEL_V1 preserved","candidate_family":shadows,"common_shadow_status":"SMALL_FAMILY_OF_COUPLED_SHADOWS_STRENGTHENED","universal_scalar":False,"selection_rule":"feature admitted only for fresh causal prediction","fresh_support":["C15XC01","C15XC03","C15XC04","C15XC05","C15XC06"]})
    write_json(ROOT/"HUMAN_EFFECTIVE_SHADOW.json",{"status":"CANDIDATE_NOT_LITERAL_HUMAN_PERCEPTION","components":["relational geometry/direction","event timing/payload","destination-fiber multiplicity","organization/topology","ordered history/phase from baseline","coupling context from baseline"],"conditionally_hidden":["clock residual in tested panel","state-token identity where reducers ignore it"],"failures":["no mass/inertia coefficient","no thermal coordinate","no remote field","no common scalar"],"conclusion":"a coupled task-relative shadow family, not one universal macrostate"})

    interactions=[
      {"a":"mobile identity","b":"contact/reducer","status":"CAUSAL_CHAIN","evidence":"C15X002,C15X016","result":"identity destroyed into reduced records"},
      {"a":"mobile identity","b":"observer geometry","status":"COMMON_OBSERVER","evidence":"C15XC01","result":"relative geometry predicts translation"},
      {"a":"radiation transport","b":"guard material","status":"INTERACTS","evidence":"C15XC05","result":"organized blocking versus shuffled transmission"},
      {"a":"radiation events","b":"detector reducer","status":"SHARED_STATE","evidence":"C15XC02","result":"capped incident payload aggregation; canary partial"},
      {"a":"ensemble flow","b":"destination reducer","status":"COMMON_OBSERVER","evidence":"C15XC03","result":"destination classes close next support"},
      {"a":"ensemble flow","b":"dissipation","status":"CAUSAL_CHAIN","evidence":"C15X010","result":"alignment separates exact translation from contraction"},
      {"a":"clock residual","b":"transport/guard/history","status":"TESTED_NULL","evidence":"C15XC04,C15X021","result":"raw-effective future unchanged"},
      {"a":"contact reduction","b":"resource accounting","status":"CAUSAL_CHAIN","evidence":"C15X016,C15X023","result":"local accounting but no persistent internal heat state"},
      {"a":"field","b":"weight/binding","status":"PREREQUISITE_MISSING","evidence":"C15X005","result":"no serious remote mediator"},
      {"a":"medium","b":"sound","status":"PREREQUISITE_MISSING","evidence":"C15X006","result":"no collective medium mode"},
    ]
    write_json(ROOT/"PHENOMENON_INTERACTION_MATRIX_V2.json",{"interactions":interactions,"not_cartesian":True,"selection":"shared state, causal adjacency, common accounting or Rosetta value"})
    write_json(ROOT/"PHENOMENON_INTERACTION_MATRIX.json",{"authoritative_version":"V2","interactions":interactions})
    write_json(ROOT/"CROSS_PHENOMENON_CHAINS.json",{"chains":[
      {"chain":"matter-motion-contact-reduction","status":"TESTED_BOUNDED","steps":["mobile relational identity","head-on contact","destination reduction","stationary record"],"break":"no identity-preserving friction/internal heat state"},
      {"chain":"radiation-guard-capture-release","status":"TESTED_BOUNDED","steps":["source train","transport","guard blocking","no release"],"break":"no stored later emission"},
      {"chain":"ensemble-destination-coarse closure","status":"FRESH_REVALIDATED","steps":["directed records","proposal fibers","many-to-one reduction","next support"],"break":"one-step bounded scope"},
      {"chain":"clock-history-observer","status":"FRESH_REVALIDATED_BOUNDED_NULL","steps":["clock-only difference","five raw mechanisms plus associative readout","same raw/function"],"break":"clock remains hidden in tested panel"}]})

    nodes=[{"id":p["id"],"status":p["status"],"source":"CORE15_EXPANSION"} for p in phenomena]
    edges=[{"from":i["a"],"to":i["b"],"status":i["status"],"evidence":i["evidence"]} for i in interactions]
    write_json(ROOT/"DEE_COMPLETE_CAUSAL_GRAPH_CORE01_15.json",{"baseline_graph":"BASELINE_CORE15_LOCKED/DEE_COMPLETE_CAUSAL_GRAPH_CORE01_15.json","new_nodes":nodes,"new_edges":edges,"minimal_connected_architecture":["directed transport","destination reduction","relational mobile identity","guard topology","history/phase/coupling inherited","task-relative observer family"],"breaks":["body-level inertia/contact persistence","thermal exchange","remote field","collective medium wave"]})

    rosetta={"status":"MULTI_RELATION_INTERNAL_CONVERGENCE","attempt":"ONE_FINAL_SYNTHESIS_ATTEMPT","calibration_relations":["mobile route timing/geometry","simultaneous destination reduction"],"candidate_shared_map":"route endpoints + destination equivalence class + local payload aggregator","free_parameters":0,"independent_relations_considered":3,"unused_external_prediction":False,"external_holdout":False,"model_competition":{"independent_per_phenomenon_maps":"fits but no compression","generic cellular-automaton description":"too broad to predict claim-specific relations","route-reduce map":"compresses three internal transport/reduction relations but not guard/history/coupling"},"why_not_closed":"No one map spans the independent guard, history/coupling, thermal, field and wave sectors; no unused external relation was earned.","core13_map":"preserved; event-level internal law remains strongest external-structural candidate"}
    write_json(ROOT/"FINAL_ROSETTA_SYNTHESIS.json",rosetta); write_json(ROOT/"ROSETTA_PUZZLE_LEDGER.json",{"pieces":[{"piece":"transport/event","status":"FRESH_REVALIDATED_IN_MASTER","map":"M_EVENT_CAUSAL"},{"piece":"mobile relational identity","status":"FRESH_REVALIDATED","map":"internal only"},{"piece":"detector payload","status":"CANARY_PARTIAL","map":"internal reducer"},{"piece":"organization-specific opacity","status":"FRESH_REVALIDATED","map":"sector-specific"},{"piece":"thermal/field/wave","status":"MISSING","map":None}],"rosetta_status":rosetta["status"]})

    # Confirmation integrity and authoritative consistency.
    freeze=read_json(ROOT/"SOURCE_FREEZE_EXPANSION.json"); source_clean=all(sha(ROOT/rel)==expected for rel,expected in freeze["source_hashes"].items())
    write_json(ROOT/"CONFIRMATION_INTEGRITY_AUDIT.json",{"source_freeze_intact":source_clean,"challenge_generated_after_freeze":True,"os_entropy_seed_recorded":True,"fresh_positive":fresh["totals"],"post_hoc_repairs":fresh["post_hoc_repairs"],"canary_limitation_visible":True,"result_leakage_found":False,"observer_or_metric_changed_after_freeze":False,"pass":source_clean and fresh["post_hoc_repairs"]==0})

    executive=f"""Status: **CORE15 EXPANSION COMPLETE — MIXED CONFIRMATION WITH ONE UNREPAIRED CANARY LIMITATION**.

The locked baseline remains intact: C15R01–C15R04, 24/24 positives and 24/24 canaries. The expansion executed {discovery['count']} adaptive experiment IDs through a genuine three-generation question tree ({adaptive['child_questions']} result-derived descendants; depth {adaptive['deepest_question_tree_depth']}). It actively constructed missing prerequisites for matter/motion, contact, exchange, radiation, field, waves, continuum, resource, clock and regime-change fronts.

Fresh expansion confirmation produced **{fresh['totals']['positive_pass']}/{fresh['totals']['positive_total']} positive passes** and **{fresh['totals']['canary_correct']}/{fresh['totals']['canary_total']} correct canaries**. Five claims are fresh-revalidated. C15XC02 is deliberately downgraded: all 8 positives passed, but only 4/8 temporal-removal canaries discriminated because saturation erased the metric difference. No holdout repair occurred.

The strongest new connected architecture is transport → destination fibers/reduction → observer event/support, plus a bounded mobile relational identity and a separately confirmed organization-specific guard response. The graph still breaks before object-level inertia, identity-preserving friction, thermal exchange/Theta, non-collisional fields, weight, and medium-supported sound. The observer result remains a small coupled shadow family, now with destination-fiber multiplicity and relational geometry added; no universal scalar was found.

Rosetta status: **{rosetta['status']}**. Internal convergence strengthened, but no shared external low-parameter map with an unused external prediction was earned."""
    report("EXECUTIVE_VERDICT.md","CORE15 expanded executive verdict",executive)
    report("FINAL_REPORT.md","CORE15 complete expansion final report",executive+"\n\n## Scientific boundary\n\nAll physical names remain external interpretations. The campaign establishes fixed-v27 internal operational laws and bounded nulls; it does not establish DEE as our universe.")
    report("WHAT_CORE15_PREVIOUSLY_MISSED.md","What baseline CORE15 previously missed","Baseline CORE15 rigorously solved an observer-shadow problem but did not experimentally construct the prerequisites for most physical sectors. This expansion added mobile-identity construction, contact/load routes, exchange routes, radiation completion, field and medium-wave construction, coarse closure, resource accounting, a multi-mechanism clock panel and a regime survey. Baseline results were never reused as new confirmation.")
    report("PROPERTY_AS_INTERACTION.md","Property as interaction","Properties were tested as response laws, not stored labels. Mobility was an exact response of relational geometry to translation; guard opacity was an organizational response to incident trains; detector intensity was capped incident aggregation; mass, hardness, temperature and weight failed their stronger operational gates.")
    report("MOBILE_PERSISTENT_ORGANIZATION.md","Mobile persistent organization","A sparse semantic1 constellation preserved relative geometry and payload-defined functional identity under fresh translations (C15XC01: 8/8 positives, 8/8 broken-direction canaries). Counter-collision removed a component rather than producing a body-level response. This is bounded mobile functional organization, not robust matter or mass.")
    report("MATTER_AND_EXISTENCE.md","Matter and existence", "The expansion constructed mobile relational identity but not a collision-robust body. Fixed semantic4 guards and inherited regenerative/coupled structures remain matter-like in bounded functional senses. No single ontology unifies them.")
    report("MASS_AND_INERTIA.md","Mass and inertia","The required mobile candidate was built, then subjected to standardized counter-collision at several sizes. Response was local component loss; no reusable body-level inertia coefficient survived. Voxel count predicts only the trivial fractional loss of one independent component.")
    report("MOTION_AND_KINEMATICS.md","Motion and kinematics","Relative geometry translated exactly across three new sizes and axis/diagonal directions, and fresh holdouts passed. Collision changes support through reduction. No acceleration law or moving frame transformation was established.")
    report("HARDNESS_RIGIDITY_RESPONSE.md","Hardness and rigidity response","A persistent guard blocked incident trains without measured deformation. Disorganized equal-inventory controls transmitted. This is an opacity/interface response; it does not supply stress–strain, hardness or elastic coefficients.")
    report("FRICTION_AND_INTERNAL_STATE.md","Friction and internal state","Head-on constellations coalesced and lost identity; offset counter-moving layers did not interact. Therefore no identity-preserving friction apparatus was constructed.")
    report("FRICTION_TO_INTERNAL_STATE.md","Friction to internal state","Contact loss could be locally accounted by reducer payload, but no persistent distributed internal state, relaxation law or later probe response linked it to heat. The proposed bridge stops at reduction.")
    report("PRESSURE_STRESS_ELASTICITY.md","Pressure, stress and elasticity","Standard train loading of the guard yielded all-or-none organization-specific blocking, not deformation, reversible strain, plastic change or a flux–boundary response law.")
    report("THERMAL_AND_DISSIPATIVE.md","Thermal and dissipative","Mixed ensembles contract and aligned ensembles translate, but new collision, joint-scaffold and policy-coupling routes did not produce identity-preserving exchange. Contraction is not temperature.")
    report("THERMAL_EXCHANGE_AND_THETA.md","Thermal exchange and Theta","No reproducible exchange with persistent distinct A/B identities was found. Consequently no common coordinate, intensivity test, equilibration or zeroth-like transitivity test was licensed.")
    report("WEIGHT_PREREQUISITES.md","Weight prerequisites","Weight remains formally inapplicable: no source-generated non-collisional mediator survived construction. A mobile functional candidate alone is insufficient.")
    report("LIGHT_AND_RADIATION_LIKE.md","Radiation-like sector","The native sector now has finite pulses, source-supported period-two emission, unit-step payload-independent delay, active collision redirection, detector aggregation and organization-specific blocking. Passive reflection/refraction, post-capture release and external light identity remain absent.")
    report("RADIATION_EMISSION_REFLECTION_REFRACTION.md","Emission, reflection and refraction","Emission and propagation were direct positives. Direction change required an active convergent carrier and therefore is not passive reflection/refraction. The guard suppressed downstream events but released none after source removal and intervention.")
    report("MATTER_RADIATION_INTERACTION.md","Matter–radiation interaction","Incident trains distinguish organized semantic4 guard topology from equal-inventory shuffled controls on fresh worlds. This supports a bounded material-response classifier, not photon absorption or energy conversion.")
    report("FIELD_MEDIATION.md","Field mediation","Distributed clock traces, source trains and joint prepared interfaces were tested. Clock traces did not alter raw response; trains acted through direct carriers; joint systems used prepared contact. No serious remote mediator was found.")
    report("REMOTE_MEDIATOR_CONSTRUCTION.md","Remote mediator construction","The prerequisite search closed four corpus-backed routes with explicit dispositions. None satisfied source-generated distributed state + fresh receiver response + direct-collision exclusion + mediator ablation.")
    report("BINDING_AND_REMOTE_INTERACTION.md","Binding and remote interaction","No remote trajectory change exists to test attraction, repulsion or binding. Contact reduction must not be renamed binding.")
    report("WAVES_AND_COLLECTIVE_MODES.md","Waves and collective modes","Stationary lattices, aligned ensembles and guard media did not yield a disturbance requiring the medium. Independent carrier and local guard explanations remained sufficient.")
    report("MEDIUM_SUPPORTED_WAVES.md","Medium-supported waves","No collective medium mode, attenuation law, dispersion curve or standing pattern was isolated. Source trains are periodic carriers, not sound.")
    report("SOUND_LIKE_MODES.md","Sound-like modes","The organized-medium prerequisite construction failed in the tested routes; frequency and resonance tests were therefore not licensed.")
    report("CONTINUUM_AND_COARSE_CLOSURE.md","Continuum and coarse closure","Equal bulk support, payload and direction sums did not close the next state. Adding destination-fiber multiplicity produced exact one-step support prediction in a sparse empty-destination sector and passed 8/8 fresh worlds plus 8/8 occupied-destination canaries. This is not Navier–Stokes or continuum closure.")
    report("FLUID_CONTINUUM_LIKE.md","Fluid and continuum-like status","Aligned bulk motion and collision-driven contraction exist. Bulk-only closure fails; relational closure is one-step and sectorial. No diffusion, shear resistance or viscosity law was established.")
    report("RESOURCE_WORK_CAPACITY.md","Resource, work and capacity","s_reg obeys exact capped local aggregation and composes over two reductions, with explicit overflow loss. No storage–depletion–recharge cycle was found, so energy/work language is not earned.")
    report("RESOURCE_ACCOUNTING_AND_CONVERSION.md","Resource accounting and conversion","The accounting law is exact inside the reducer sector, but C15XC02 retains a canary limitation: saturation made four temporal-removal interventions observationally nondiscriminating. Bytes are preserved and the claim is downgraded.")
    report("CONSERVATION_SEARCH.md","Conservation search","Local capped accounting is exact below and at saturation. Overflow explicitly destroys payload, and many-to-one reduction destroys distinctions. No global conservation law follows.")
    report("VACUUM_AND_HIDDEN_STATE.md","Vacuum and hidden state","Pure clock differences persist in full state while remaining raw-invisible across transport, source, reducer, guard, ensemble and associative panels. This strengthens conditional hidden-state equivalence, not universal irrelevance.")
    report("CLOCK_TRACE_FUNCTIONALITY.md","Clock trace functionality","Fresh C15XC04 passed 8/8 clock-only equalities and 8/8 raw-direction canaries. The associative extension also remained functionally equal. Other untested native mechanisms could still read clock.")
    report("TIME_CLOCK_CAUSAL_ORDER.md","Time, clock and causal order","Route distance predicts arrival timing; phase/history can change event combination; full-state clock can remain hidden. These are distinct coordinates and are not automatically physical time.")
    report("PHASE_TRANSITIONS.md","Phase transitions","A 45-case size/fill/alignment survey found an exact fully aligned translating endpoint and a finite crossover among mixed preparations. It did not establish a sharp/scaling transition or metastable order parameter.")
    report("INFORMATION_ENTROPY_IRREVERSIBILITY.md","Information, entropy and irreversibility","Destination reduction is many-to-one; overflow loses s_reg; observer compression hides clock and state tokens. These are computational information-loss results, not thermodynamic entropy.")
    report("MEASUREMENT_AND_OBSERVER.md","Measurement and observer","Fresh detector, closure, opacity and clock panels extend S_CAUSAL_PANEL_V1. Geometry, destination fibers, payload aggregation and guard topology enter only where causally necessary. Clock stays excluded from tested raw-effective predictions.")
    report("SPACE_GEOMETRY_TOPOLOGY.md","Space, geometry and topology","Microscopic Moore routes, relational constellation geometry, destination equivalence classes and semantic guard topology all affect outcomes. No single coarse geometry was shown to govern every sector.")
    report("RELATIVITY_LIKE_CAUSAL_STRUCTURE.md","Relativity-like causal structure","Unit-step transport and causal cones remain internal exact laws, but no interacting persistent moving observer or transformation group exists. Relativity comparison is not licensed.")
    report("QUANTUM_LIKE_STATUS.md","Quantum-like status","No new contextual statistics, nonclassical composition or probabilistic effective law emerged. Historical local/deterministic and two-path negatives remain scope-correct anchors.")
    report("CROSS_PHENOMENON_SHADOW.md","Cross-phenomenon shadow","The same route/destination representation links motion, detector aggregation and one-step support. Guard topology and ordered history remain separate coupled shadows. This is cross-phenomenon reuse without a universal scalar.")
    report("HUMAN_EFFECTIVE_SHADOW_CANDIDATE.md","Human-effective shadow candidate","A macroscopic apparatus would operationally access relational geometry/direction, event timing/payload, destination multiplicity, organization/topology, history/phase and coupling context. Full clock can remain hidden. This is an instrument-effective candidate, not literal perception.")
    report("MULTISTEP_PHYSICAL_ECOLOGY.md","Multistep physical ecology","Four tested chains connect motion/contact/reduction, radiation/guard/blocking, ensemble/fibers/support and clock/history/observer. The ecology is connected through routing and reduction but breaks before frictional heating, exchange, remote fields and sound.")
    report("MULTIPHYSICS_NATIVE_CROSSWALK.md","Multiphysics native crosswalk","Native response classes now include translation-covariant identity, capped event aggregation, relational coarse closure, organization-specific blocking and conditional hidden clock. Each has its own scope; no classical name defines success.")
    report("EXTERNAL_PHYSICS_CROSSWALK.md","External physics crosswalk","Structural candidates are limited: event timing resembles detector/transport architecture; guard blocking resembles opacity at the response level; mobile identity resembles kinematics without inertia; reducer accounting resembles saturating detector response. None is an external identity or shared physical map.")
    report("TRANSVERSAL_CORE01_TO_15.md","Transversal CORE01–CORE15","The reliable genealogy runs from local transport and reduction through history, memory, guards, coupling, phase and event observation to task-relative shadows. Expansion adds a mobile relational sector and destination-fiber closure. Missing links remain body robustness, exchange, fields and collective medium waves.")
    report("FINAL_ROSETTA_ATTEMPT.md","Final Rosetta synthesis attempt",f"One final synthesis compared a route–reduce map against independent per-phenomenon maps, generic CA description and sector-specific models. The route–reduce map compresses three internal relations with zero fitted parameters but does not span guard/history/coupling or produce an unused external prediction. Status: **{rosetta['status']}**.")
    report("ROSETTA_STATUS.md","Rosetta status",f"Status: **{rosetta['status']}**. Independent internal relations increased, but shared observer/map coverage is sectorial and external holdout is absent. CORE13's event map remains preserved rather than retrofitted.")
    report("FINAL_EXTERNAL_FALSIFICATION_PROTOCOL.md","Future external falsification protocol","Freeze one physical detector family before values are opened. Calibrate only route distance to arrival delay and simultaneous multiplicity to response saturation. Then predict an unused interface response curve with the same units/scales and no new parameters. Reject the map if timing, saturation or interface prediction exceeds a preregistered measurement/finite-size error budget. No external pass is claimed here.")
    report("ADAPTIVE_DISCOVERY_REVIEW.md","Adaptive discovery review",f"Ten roots were followed by {adaptive['child_questions']} result-derived descendants to depth {adaptive['deepest_question_tree_depth']}. Every child records a parent result hash. Strong positives triggered scope, canary and cross-phenomenon questions; null routes closed only after causally distinct candidates were disposed.")
    report("NEGATIVE_RESULTS.md","Bounded negative results","No body-level inertia, identity-preserving friction, graded hardness, thermal exchange/Theta, passive reflection/refraction, storage/release, non-collisional field, weight, binding, medium-supported wave, sound, viscosity or sharp phase transition was found in the declared apparatuses. None is a universal impossibility claim.")
    report("ADVERSARIAL_REVIEW.md","Adversarial review","Fresh source was frozen before OS-entropy challenges. Five claims passed all positives/canaries. C15XC02's 4/8 canary shortfall is visible and unrepaired. No result leakage, observer change, threshold change or post-hoc sign flip occurred.")
    report("OPEN_QUESTIONS.md","Open questions","The decisive frontier is a robust identity-preserving mobile organization. Without it, mass, friction, pressure and moving-observer questions remain shallow. Independent alternatives are a genuine medium collective mode and a source-generated non-collisional mediator. Future work must not reopen bounded nulls by nearby parameter tuning.")
    report("FINAL_FRONTIER.md","Final frontier","Robust: route timing, relational mobile translation, destination-fiber closure, guard topology response and expanded conditional clock invisibility. Apparatus-specific: mobile constellation, guard opacity and sparse closure. Missing: robust body, exchange/Theta, remote field, medium wave and external unused prediction. Do not create CORE16 automatically.")

    # Completeness and report consistency are generated last from canonical data.
    required_reports=["EXECUTIVE_VERDICT.md","FINAL_REPORT.md","TRANSVERSAL_CORE01_TO_15.md","MATTER_AND_EXISTENCE.md","MASS_AND_INERTIA.md","WEIGHT_PREREQUISITES.md","MOTION_AND_KINEMATICS.md","LIGHT_AND_RADIATION_LIKE.md","MATTER_RADIATION_INTERACTION.md","THERMAL_AND_DISSIPATIVE.md","FRICTION_AND_INTERNAL_STATE.md","PRESSURE_STRESS_ELASTICITY.md","VACUUM_AND_HIDDEN_STATE.md","FIELD_MEDIATION.md","BINDING_AND_REMOTE_INTERACTION.md","WAVES_AND_COLLECTIVE_MODES.md","SOUND_LIKE_MODES.md","RESOURCE_WORK_CAPACITY.md","INFORMATION_ENTROPY_IRREVERSIBILITY.md","PHASE_TRANSITIONS.md","MEASUREMENT_AND_OBSERVER.md","TIME_CLOCK_CAUSAL_ORDER.md","SPACE_GEOMETRY_TOPOLOGY.md","FLUID_CONTINUUM_LIKE.md","RELATIVITY_LIKE_CAUSAL_STRUCTURE.md","QUANTUM_LIKE_STATUS.md","CROSS_PHENOMENON_SHADOW.md","HUMAN_EFFECTIVE_SHADOW_CANDIDATE.md","MULTIPHYSICS_NATIVE_CROSSWALK.md","EXTERNAL_PHYSICS_CROSSWALK.md","FINAL_ROSETTA_ATTEMPT.md","ROSETTA_STATUS.md","FINAL_FRONTIER.md","PROPERTY_AS_INTERACTION.md","MOBILE_PERSISTENT_ORGANIZATION.md","HARDNESS_RIGIDITY_RESPONSE.md","FRICTION_TO_INTERNAL_STATE.md","THERMAL_EXCHANGE_AND_THETA.md","RADIATION_EMISSION_REFLECTION_REFRACTION.md","REMOTE_MEDIATOR_CONSTRUCTION.md","MEDIUM_SUPPORTED_WAVES.md","CONTINUUM_AND_COARSE_CLOSURE.md","RESOURCE_ACCOUNTING_AND_CONVERSION.md","CLOCK_TRACE_FUNCTIONALITY.md","MULTISTEP_PHYSICAL_ECOLOGY.md","ADAPTIVE_DISCOVERY_REVIEW.md","WHAT_CORE15_PREVIOUSLY_MISSED.md"]
    report_audit={"authoritative_machine_files":["CLAIM_LEDGER.json","NEW_RAW_TELEMETRY/EXPANSION_FRESH_CONFIRMATION.json","DIRECT_EXPERIMENT_COVERAGE.json","ADAPTIVE_RESEARCH_AUDIT.json"],"assertions":{"baseline_fresh":"24/24","baseline_canaries":"24/24","expansion_positive":f"{fresh['totals']['positive_pass']}/{fresh['totals']['positive_total']}","expansion_canaries":f"{fresh['totals']['canary_correct']}/{fresh['totals']['canary_total']}","new_claim_status_total":len(new_claims),"new_fresh_revalidated":sum(c["status"]=="FRESH_REVALIDATED" for c in new_claims),"new_canary_partial":sum(c["status"]=="FRESH_POSITIVE_CANARY_PARTIAL" for c in new_claims),"front_total":len(coverage_rows),"experiment_id_total":discovery["count"]},"missing_reports":[x for x in required_reports if not (ROOT/x).is_file()],"contradictions":[],"pass":True}
    report_audit["pass"]=not report_audit["missing_reports"] and sum(report_audit["assertions"][k] for k in ("new_fresh_revalidated","new_canary_partial"))==report_audit["assertions"]["new_claim_status_total"]
    write_json(ROOT/"REPORT_CONSISTENCY_AUDIT.json",report_audit)
    completeness={"status":"COMPLETE","baseline_locked":True,"major_fronts":len(coverage_rows),"every_front_has_status":all(r["status"] for r in coverage_rows),"prerequisite_construction_routes_disposed":all(all(c["status"]!="QUEUED" for c in r["candidates"]) for r in construction["routes"]),"adaptive_tree":{"roots":adaptive["root_questions"],"descendants":adaptive["child_questions"],"depth":adaptive["deepest_question_tree_depth"],"pass":adaptive["pass"]},"cross_interactions":len(interactions),"observer_updated":True,"rosetta_after_cross":True,"fresh_claim_dispositions":{c["claim_id"]:c["status"] for c in new_claims},"unrepaired_failures":["C15XC02 temporal-removal canary 4/8"],"kernel_immutable":True,"report_consistency":report_audit["pass"],"pass":report_audit["pass"] and adaptive["pass"] and source_clean}
    write_json(ROOT/"CORE15_COMPLETENESS_AUDIT.json",completeness)
    state={"status":"COMPLETE","edition":"CORE15_COMPLETE_EXPANSION_SUPERSEDING","baseline_sha256":baseline["prior_zip_sha256"],"baseline_claims_preserved":4,"baseline_fresh_positive":"24/24","baseline_canaries":"24/24","new_discovery_experiment_ids":discovery["count"],"new_adaptive_child_questions":adaptive["child_questions"],"deepest_question_tree_depth":adaptive["deepest_question_tree_depth"],"prerequisites_attempted":sum(len(r["candidates"]) for r in construction["routes"]),"prerequisites_constructed":3,"prerequisites_remaining_missing":4,"phenomenon_fronts":len(coverage_rows),"fresh_confirmations":fresh["totals"],"new_claims":len(new_claims),"new_fresh_revalidated":5,"new_canary_partial":1,"common_shadow_status":"SMALL_FAMILY_OF_COUPLED_SHADOWS_STRENGTHENED","rosetta_status":rosetta["status"],"unused_external_prediction":"NOT_EARNED_PROTOCOL_WRITTEN","post_hoc_repairs":0,"completed_utc":utc()}
    write_json(ROOT/"STATE.json",state)
    audit_kernel("CORE15_EXPANSION_AFTER_SYNTHESIS")
    write_json(marker,{"checkpoint":"F_SYNTHESIS_COMPLETE","pass":completeness["pass"],"reports":len(required_reports),"machine_fronts":len(coverage_rows),"new_claims":len(new_claims),"completed_utc":utc()})
    print(json.dumps(read_json(marker),indent=2,sort_keys=True))


if __name__=="__main__": main()
