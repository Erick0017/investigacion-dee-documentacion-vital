#!/usr/bin/env python3
"""Verify and lock baseline CORE15, then seed the expanded scientific registries."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extension_common import (
    BASELINE_SHA, BASELINE_WORK, OFFICIAL, ROOT, audit_kernel, read_json, sha,
    update_state, utc, write_json, write_text,
)


COPY_RUNNERS = [
    "native_core.py", "core12_apparatus.py", "core12_common.py", "core10_apparatus.py",
    "core10_common.py", "core08_common.py", "run_c6h01_associative_plasticity_holdout.py",
    "run_c6h08_dissipative_ensemble_holdout.py", "run_c8h02_repeated_scaffold_regeneration.py",
]


def verify_zip_and_extract() -> dict:
    observed = sha(OFFICIAL)
    if observed != BASELINE_SHA:
        raise RuntimeError(f"baseline CORE15 mismatch: {observed}")
    target = ROOT / "BASELINE_CORE15_LOCKED"
    with zipfile.ZipFile(OFFICIAL) as zf:
        first_bad = zf.testzip()
        names = set(zf.namelist())
        hashes_name = next((n for n in sorted(names) if n.endswith("HASHES.sha256")), None)
        mismatches = []
        checked = 0
        if hashes_name:
            prefix = hashes_name[:-len("HASHES.sha256")]
            for line in zf.read(hashes_name).decode("utf-8-sig").splitlines():
                if not line.strip():
                    continue
                expected, rel = line.split(None, 1)
                member = prefix + rel.strip().lstrip("*")
                checked += 1
                if member not in names or hashlib.sha256(zf.read(member)).hexdigest() != expected.lower():
                    mismatches.append(rel.strip())
        if first_bad or mismatches:
            raise RuntimeError(f"baseline archive failed validation: crc={first_bad} mismatches={mismatches[:5]}")
        for info in zf.infolist():
            if info.is_dir():
                continue
            rel = Path(info.filename)
            if rel.is_absolute() or ".." in rel.parts:
                raise RuntimeError(f"unsafe member {info.filename}")
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(zf.read(info))
    return {"sha256": observed, "size": OFFICIAL.stat().st_size, "zip_crc_pass": True, "internal_hashes_checked": checked, "internal_hash_mismatches": mismatches}


def baseline_json(name: str):
    direct = ROOT / "BASELINE_CORE15_LOCKED" / name
    if direct.is_file():
        return read_json(direct)
    matches = list((ROOT / "BASELINE_CORE15_LOCKED").rglob(name))
    if len(matches) != 1:
        raise RuntimeError(f"baseline member not unique: {name}: {matches}")
    return read_json(matches[0])


def copy_helpers() -> None:
    source = BASELINE_WORK / "RUNNERS"
    for name in COPY_RUNNERS:
        shutil.copy2(source / name, ROOT / "NEW_RUNNERS" / name)


def main() -> None:
    marker = ROOT / "CHECKPOINTS" / "A_BASELINE_AND_REGISTRIES_COMPLETE.json"
    if marker.exists():
        print(marker.read_text(encoding="utf-8")); return
    audit_kernel("CORE15_EXPANSION_PREFLIGHT")
    verification = verify_zip_and_extract()
    copy_helpers()
    state = baseline_json("STATE.json")
    ledger = baseline_json("CLAIM_LEDGER.json")
    manifest = baseline_json("MANIFEST.json")
    kernel = baseline_json("KERNEL_IMMUTABILITY_AUDIT.json")
    baseline = {
        "schema": "dee.v27.core15.expansion.baseline.v1",
        "status": "BASELINE_CORE15_LOCKED",
        "prior_zip_path": str(OFFICIAL),
        "prior_zip_sha256": verification["sha256"],
        "prior_zip_size": verification["size"],
        "prior_manifest_status": manifest.get("status", state.get("status")),
        "prior_kernel_hashes": kernel.get("expected"),
        "prior_promoted_claims": ledger.get("claims", []),
        "prior_holdout_totals": {"fresh_positive_pass": state.get("fresh_pass"), "fresh_positive_total": state.get("fresh_trials"), "canaries_correct": state.get("canaries_correct"), "canaries_total": state.get("canaries")},
        "prior_observer_result": {"status": state.get("common_shadow_status"), "observer": "S_CAUSAL_PANEL_V1", "rosetta": state.get("rosetta_level")},
        "archive_validation": verification,
        "reason_for_expansion": "The locked baseline established observer-shadow laws but did not experimentally construct and interrogate the missing prerequisites across the requested physical ecology.",
        "preservation_statement": "C15R01-C15R04 and the 24/24 positive plus 24/24 canary baseline remain locked evidence; expansion claims use C15X identifiers.",
        "created_utc": utc(),
    }
    write_json(ROOT / "SUPERSEDED_CORE15_BASELINE.json", baseline)

    capabilities = [
        {"capability_id":"CAP_TRANSPORT","source_core":"CORE01/13","mechanism":"unit-step directed semantic1 transport and event timing","persistent":False,"mobile":True,"roles":["CARRIER","PROBE","DETECTOR_INPUT"],"known_controls":["route cut","direction change"],"known_negatives":["not a persistent object"]},
        {"capability_id":"CAP_REDUCER","source_core":"CORE01/05/13","mechanism":"many-to-one destination reduction with capped s_reg payload","persistent":False,"mobile":False,"roles":["INTERFACE","DETECTOR","ACCOUNTING_NODE"],"known_controls":["resolved arrival","single arrival"],"known_negatives":["information-losing"]},
        {"capability_id":"CAP_BASIN","source_core":"CORE03","mechanism":"collective basin/regime organization","persistent":True,"mobile":False,"roles":["MEDIUM","MATERIAL"],"known_controls":[],"known_negatives":["historical apparatus not yet reconstructed for mobile use"]},
        {"capability_id":"CAP_HISTORY","source_core":"CORE04/06/09","mechanism":"ordered history and learned/contextual causal state","persistent":True,"mobile":"conditional","roles":["MEMORY","RECEIVER","MATERIAL"],"known_controls":["history shuffle","memory ablation"],"known_negatives":["not established as rigid moving body"]},
        {"capability_id":"CAP_GUARD","source_core":"CORE08/12","mechanism":"semantic4 topological guard, regeneration and organization-specific capture","persistent":True,"mobile":False,"roles":["MATERIAL","INTERFACE","RECEIVER"],"known_controls":["shuffle","remove guard","wrong semantic"],"known_negatives":["bounded capture did not establish storage/release"]},
        {"capability_id":"CAP_COUPLING","source_core":"CORE10","mechanism":"bidirectional coupling, policy reinstantiation and joint scaffold recovery","persistent":True,"mobile":"functional transfer only","roles":["COUPLED_SYSTEM","RECEIVER","MEMORY"],"known_controls":["route cut","receiver absent","interface deletion"],"known_negatives":["prepared structure required"]},
        {"capability_id":"CAP_PHASE","source_core":"CORE12","mechanism":"relative parity/phase changes convergent event record","persistent":"route dependent","mobile":True,"roles":["OSCILLATOR","CARRIER","DETECTOR_INPUT"],"known_controls":["one-tick shift","path removal"],"known_negatives":["not quantum interference"]},
        {"capability_id":"CAP_ENSEMBLE","source_core":"CORE06/11/15","mechanism":"aligned sparse ensemble translates; mixed directions collide and contract","persistent":"aligned only","mobile":True,"roles":["ENSEMBLE","FLOW","MATERIAL_CANDIDATE"],"known_controls":["direction shuffle","aligned direction"],"known_negatives":["not equilibrium temperature"]},
        {"capability_id":"CAP_CLOCK_TRACE","source_core":"CORE14/15","mechanism":"full-state clock residual can persist while raw singleton future is unchanged","persistent":True,"mobile":"with carrier","roles":["HIDDEN_STATE","HISTORY"],"known_controls":["raw-direction canary"],"known_negatives":["baseline scope only singleton transport"]},
    ]
    write_json(ROOT / "CORE01_15_CAPABILITY_REGISTRY.json", {"capabilities": capabilities, "baseline_sha256": verification["sha256"], "generated_from":"locked CORE15 plus CORE01-14/Master machine corpus"})
    write_json(ROOT / "CORE01_15_MECHANISM_GRAPH.json", {"nodes":[c["capability_id"] for c in capabilities],"edges":[
        {"from":"CAP_TRANSPORT","to":"CAP_REDUCER","relation":"arrival/reduction","status":"FRESH_REVALIDATED"},
        {"from":"CAP_PHASE","to":"CAP_REDUCER","relation":"relative timing changes event record","status":"FRESH_REVALIDATED"},
        {"from":"CAP_TRANSPORT","to":"CAP_GUARD","relation":"organization-specific capture/transmission","status":"FRESH_REVALIDATED"},
        {"from":"CAP_HISTORY","to":"CAP_COUPLING","relation":"policy transfer/reinstantiation","status":"FRESH_REVALIDATED"},
        {"from":"CAP_ENSEMBLE","to":"CAP_REDUCER","relation":"collisions contract support","status":"FRESH_REVALIDATED"},
        {"from":"CAP_CLOCK_TRACE","to":"CAP_TRANSPORT","relation":"raw-invisible in singleton baseline","status":"BOUNDED_NEGATIVE"}],"epistemic_note":"edges are inherited baseline/corpus evidence until directly extended"})

    failures = [
        {"failure_id":"FAIL_EMPTY_VACUUM_MEMORY","attempt":"post-source empty-sector trace","falsifies":"tested empty apparatus only","does_not_falsify":"structured medium memory"},
        {"failure_id":"FAIL_K6_RELEASE","attempt":"semantic4 k6 capture/storage/release","falsifies":"release in this guard apparatus","does_not_falsify":"other memory receivers"},
        {"failure_id":"FAIL_THERMO_CONTACT","attempt":"historical carrier-contact thermal apparatus","falsifies":"that apparatus/equalization metric","does_not_falsify":"all exchange mechanisms"},
        {"failure_id":"FAIL_FIELD_TESTED","attempt":"previous source/medium field routes","falsifies":"tested routes","does_not_falsify":"evidence-based constructed mediator routes"},
        {"failure_id":"FAIL_SINGLETON_CLOCK_READOUT","attempt":"clock-only residual under singleton transport","falsifies":"universal clock readability by that panel","does_not_falsify":"clock readability by guards/history/phase/coupling"},
        {"failure_id":"FAIL_TWO_PATH_QUANTUM","attempt":"two-path additivity/interference apparatus","falsifies":"nonclassical signal there","does_not_falsify":"native phase sensitivity"},
    ]
    write_json(ROOT / "CORE01_15_FAILURE_REGISTRY.json", {"failures": failures, "policy":"consult before every construction; no apparatus null is globalized"})

    prerequisites = [
        {"front":"MASS_INERTIA","requires":["persistent functional identity","mobility","standardized perturbation","response metric"],"candidate_routes":["aligned sparse organization","mobile learned state","reinstantiation chain"]},
        {"front":"FRICTION_HARDNESS","requires":["two identity-preserving bodies/regimes","relative motion or standardized load","contact accounting"],"candidate_routes":["two aligned organizations","mobile organization into semantic4 guard","parallel shear ensembles"]},
        {"front":"THERMAL_EXCHANGE","requires":["persistent distinguishable states","controlled contact","post-separation readout"],"candidate_routes":["collision ensembles","joint scaffold","policy-coupled systems"]},
        {"front":"RADIATION_COMPLETION","requires":["emission","propagation","interface response","detector"],"candidate_routes":["semantic4 train","finite semantic1 pulse","active reducer interface","guard interface"]},
        {"front":"FIELD_WEIGHT","requires":["source-generated distributed mediator","fresh receiver response","direct-carrier exclusion","mediator ablation"],"candidate_routes":["clock trace","source-supported train","basin medium","coupled lane"]},
        {"front":"WAVE_SOUND","requires":["organized medium","collective disturbance","medium-dependent propagation","attenuation/frequency"],"candidate_routes":["sparse stationary lattice","aligned ensemble","guard lattice","historical oscillator"]},
        {"front":"CONTINUUM_FLUID","requires":["coarse ensemble state","flow or spreading","fresh next-state closure"],"candidate_routes":["aligned flow","mixed ensemble","destination multiplicity closure"]},
        {"front":"RESOURCE_WORK","requires":["stored capacity","causal use","depletion or accounting","transfer/recharge where meaningful"],"candidate_routes":["s_reg reducer accounting","guard support","learned policy state"]},
        {"front":"CLOCK_FUNCTIONALITY","requires":["raw-identical clock-different states","independent interaction panels"],"candidate_routes":["source","guard","phase","history","ensemble","coupling"]},
        {"front":"PHASE_TRANSITION","requires":["distinct regimes","control variable","predictive order parameter","size/holdout test"],"candidate_routes":["ensemble alignment fraction","basin","guard threshold"]},
    ]
    write_json(ROOT / "PHYSICAL_PREREQUISITE_GRAPH.json", {"fronts": prerequisites, "policy":"PREREQUISITE_MISSING is intermediate until construction routes are adjudicated"})
    write_json(ROOT / "PREREQUISITE_CONSTRUCTION_LEDGER.json", {"routes":[{"front":p["front"],"required":p["requires"],"candidates":[{"route":r,"level":1 if i==0 else 2,"status":"QUEUED"} for i,r in enumerate(p["candidate_routes"])]} for p in prerequisites]})
    roots = [
        ("C15XQ001","Can confirmed transport and persistent organization compose a mobile identity?","MASS_INERTIA"),
        ("C15XQ002","Can constructed bodies preserve identity through controlled contact or load?","FRICTION_HARDNESS"),
        ("C15XQ003","Can distinct persistent states exchange a reusable internal coordinate?","THERMAL_EXCHANGE"),
        ("C15XQ004","Can the known propagation sector support emission, redirection, release and mode response?","RADIATION_COMPLETION"),
        ("C15XQ005","Can any corpus-supported route create remote mediation without direct carrier collision?","FIELD_WEIGHT"),
        ("C15XQ006","Can an organized medium carry a collective disturbance rather than independent carriers?","WAVE_SOUND"),
        ("C15XQ007","Which coarse variables close fresh ensemble futures?","CONTINUUM_FLUID"),
        ("C15XQ008","Does any state satisfy operational resource accounting beyond a label?","RESOURCE_WORK"),
        ("C15XQ009","Can mechanisms other than singleton transport read a pure clock residual?","CLOCK_FUNCTIONALITY"),
        ("C15XQ010","Does an ensemble control parameter generate a reproducible regime transition?","PHASE_TRANSITION"),
    ]
    lines = [json.dumps({"question_id":qid,"parent_question_id":None,"front":front,"question":question,"status":"QUEUED","decision_rule":"children may be written only after parent result hash exists","created_utc":utc()},separators=(",",":")) for qid,question,front in roots]
    write_text(ROOT / "EXPANDED_QUESTION_TREE.ndjson", "\n".join(lines)+"\n")
    write_text(ROOT / "EXPANDED_KERNEL_DIALOGUE.ndjson", "")
    write_text(ROOT / "RESEARCH_DECISION_LOG.ndjson", "")
    write_json(marker, {"checkpoint":"A_BASELINE_AND_REGISTRIES_COMPLETE","pass":True,"baseline_sha256":verification["sha256"],"capabilities":len(capabilities),"failures":len(failures),"prerequisite_fronts":len(prerequisites),"root_questions":len(roots),"completed_utc":utc()})
    update_state(status="BASELINE_LOCKED_REGISTRIES_COMPLETE", baseline_sha256=verification["sha256"], baseline_claims_preserved=4, baseline_fresh_positive_pass=24, baseline_canaries_correct=24, completed_checkpoints=["A_BASELINE_AND_REGISTRIES_COMPLETE"])
    audit_kernel("CORE15_EXPANSION_AFTER_BASELINE_LOCK")
    print(json.dumps(read_json(marker), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
