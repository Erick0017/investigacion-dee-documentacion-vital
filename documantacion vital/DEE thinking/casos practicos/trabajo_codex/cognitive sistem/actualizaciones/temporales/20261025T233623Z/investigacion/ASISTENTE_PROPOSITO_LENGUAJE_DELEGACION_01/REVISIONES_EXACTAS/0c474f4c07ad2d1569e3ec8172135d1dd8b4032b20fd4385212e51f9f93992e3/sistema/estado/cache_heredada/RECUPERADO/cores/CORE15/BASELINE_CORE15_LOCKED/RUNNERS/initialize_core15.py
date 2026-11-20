"""CORE15 Phase A: parent audit, Q forensics, observer inventory and causal atlas."""
from __future__ import annotations

import json
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core15_common import (
    ARCHIVE,
    CORE14_NAME,
    EXPECTED_CORE14,
    EXPECTED_MASTER,
    MASTER_NAME,
    MASTER_WORK,
    ROOT,
    audit_kernel,
    read_json,
    scan_q_mentions,
    sha,
    update_state,
    utc,
    verify_zip,
    write_json,
)


def core_archives() -> list[Path]:
    rows = []
    for path in sorted(ARCHIVE.glob("[0-1][0-9]_*.zip")):
        try:
            core = int(path.name[:2])
        except ValueError:
            continue
        if 1 <= core <= 14:
            rows.append(path)
    if len(rows) != 14 or [int(p.name[:2]) for p in rows] != list(range(1, 15)):
        raise RuntimeError("CORE01-14 archive chain is incomplete")
    return rows


def parent_audit(paths: list[Path]) -> None:
    chain = []
    for path in paths:
        integrity = verify_zip(path)
        if not integrity["pass"]:
            raise RuntimeError(f"parent integrity failure: {path.name}")
        chain.append({"core": int(path.name[:2]), "name": path.name, **integrity})
    core14 = chain[-1]
    if core14["sha256"] != EXPECTED_CORE14:
        raise RuntimeError(f"CORE14 parent mismatch: {core14['sha256']}")
    master_path = ARCHIVE / MASTER_NAME
    master = verify_zip(master_path)
    if not master["pass"] or master["sha256"] != EXPECTED_MASTER:
        raise RuntimeError(f"MASTER mismatch: {master}")
    write_json(
        ROOT / "PARENT_CHAIN.json",
        {
            "immediate_parent": CORE14_NAME,
            "core_chain": chain,
            "master_reliability_audit": master,
            "parent_core14_expected": EXPECTED_CORE14,
            "master_expected": EXPECTED_MASTER,
            "parents_embedded": False,
        },
    )


def q_forensics(paths: list[Path]) -> None:
    merged = {f"Q{i}": [] for i in range(5)}
    per_core = {}
    for path in paths:
        found = scan_q_mentions(path)
        core = int(path.name[:2])
        per_core[str(core)] = {label: len(rows) for label, rows in found.items()}
        for label, rows in found.items():
            merged[label].extend({"source_core": core, **row} for row in rows)
    interpretations = {
        "Q0": {
            "historical_definition": "Full raw plus clock state when used as the unreduced Markov baseline; some older sources use Q0 for the finest represented state.",
            "type": "microstate/full-state baseline",
            "supported": True,
            "caution": "Historical notation is not perfectly uniform; source context remains authoritative.",
        },
        "Q1": {
            "historical_definition": "First coarse/local state summaries, commonly occupancy/support or local proposal-level representation.",
            "type": "coarse causal representation",
            "supported": bool(merged["Q1"]),
            "caution": "Not a literal spatial dimension.",
        },
        "Q2": {
            "historical_definition": "Relational/fiber or collective representation in the historical observer hierarchy.",
            "type": "collective/relational representation",
            "supported": bool(merged["Q2"]),
            "caution": "Definitions vary by apparatus and must not be merged without the source predicate.",
        },
        "Q3": {
            "historical_definition": "History-aware/effective observer level used in several earlier multiscale discussions.",
            "type": "history-aware representation",
            "supported": bool(merged["Q3"]),
            "caution": "Historical mention does not prove autonomous closure.",
        },
        "Q4": {
            "historical_definition": "Proposed higher observer/quotient level in historical narrative where mentioned.",
            "type": "unsupported as a universal operational level",
            "supported": False,
            "caution": "No canonical fresh-revalidated machine predicate in CORE01-14 establishes a universal Q4.",
        },
    }
    entries = []
    for label in ("Q0", "Q1", "Q2", "Q3", "Q4"):
        entries.append(
            {
                "q_level": label,
                **interpretations[label],
                "occurrence_count_retained": len(merged[label]),
                "source_cores": sorted(set(row["source_core"] for row in merged[label])),
                "machine_evidence": merged[label][:120],
                "scope": "source-specific; no literal dimension claim",
            }
        )
    write_json(ROOT / "Q_LEVEL_FORENSIC_ATLAS.json", {"entries": entries, "counts_by_core": per_core})


def observer_inventory() -> None:
    source = ROOT.parent / "DEE_V27_CORE13_OBSERVER_LEVEL_ROSETTA_CONVERGENCE_WORK" / "OBSERVER_CANDIDATES.json"
    historical = read_json(source)["candidates"]
    extra = [
        {
            "observer_id": "M_OCCUPANCY",
            "variables": ["occupied coordinates"],
            "what_it_sees": "support geometry only",
            "what_it_ignores": ["state", "s_reg", "direction", "semantic", "clock", "lineage"],
            "known_successes": ["support/presence"],
            "known_failures": ["phase-path", "guard", "payload", "history"],
            "scope": "negative baseline",
            "information_cost": "O(support)",
        },
        {
            "observer_id": "M_HISTORY",
            "variables": ["current lineage", "training relation", "prior target occupancy", "ordered intervention record"],
            "what_it_sees": "causally stored/ordered history",
            "what_it_ignores": ["unrelated global microstate"],
            "known_successes": ["CORE06 associative response", "CORE14 path dependence"],
            "known_failures": ["global closure"],
            "scope": "history-bearing apparatuses",
            "information_cost": "task-relative sparse lineage",
        },
        {
            "observer_id": "M_MATTER",
            "variables": ["functional identity", "guard topology", "persistence", "damage response", "recovery"],
            "what_it_sees": "persistent organization and response class",
            "what_it_ignores": ["irrelevant voxel identity"],
            "known_successes": ["CORE08/14 regeneration"],
            "known_failures": ["mobile inertia not established"],
            "scope": "guarded/regenerative organizations",
            "information_cost": "local topology plus response trace",
        },
        {
            "observer_id": "M_COUPLING",
            "variables": ["endpoint functional states", "lane/interface state", "directional causal cuts", "joint recovery"],
            "what_it_sees": "bounded coupled-system causal response",
            "what_it_ignores": ["unrelated bulk"],
            "known_successes": ["CORE10/14 exchange, transfer, joint recovery"],
            "known_failures": ["global ecology closure"],
            "scope": "prepared coupled systems",
            "information_cost": "sparse endpoints plus mediator",
        },
        {
            "observer_id": "M_CLOCK_RESIDUAL",
            "variables": ["raw state", "local/global clock residual relative to matched age"],
            "what_it_sees": "hidden clock trace",
            "what_it_ignores": ["semantic interpretation"],
            "known_successes": ["CORE14 exact persistent clock trace"],
            "known_failures": ["no functional effect under two frozen probes"],
            "scope": "clock-trace apparatus",
            "information_cost": "clock patch or hash",
        },
    ]
    normalized = []
    for row in historical:
        normalized.append(
            {
                **row,
                "what_it_sees": row.get("variables", []),
                "what_it_ignores": row.get("phenomena_failed", []),
                "known_successes": row.get("phenomena_explained", []),
                "known_failures": row.get("phenomena_failed", []),
                "scope": row.get("rationale", "historical candidate"),
                "cost": row.get("information_cost"),
                "source": "CORE13",
            }
        )
    write_json(
        ROOT / "OBSERVER_LIBRARY.json",
        {
            "observers": normalized + extra,
            "count": len(normalized) + len(extra),
            "baseline": "M_Q0",
            "historical_selected": "M_EVENT_CAUSAL",
            "core15_policy": "discovery may combine observers; confirmation freezes only causally necessary components",
        },
    )


def causal_atlas() -> None:
    registry = read_json(MASTER_WORK / "MASTER_CLAIM_REGISTRY.json")["claims"]
    scorecard = read_json(MASTER_WORK / "ANTI_OVERFIT_SCORECARD.json")
    score_rows = scorecard if isinstance(scorecard, list) else scorecard.get("claims", scorecard.get("scorecard", []))
    status_by_id = {row.get("canonical_claim_id", row.get("claim_id")): row.get("final_status", row.get("status")) for row in score_rows}
    family_counts = Counter()
    nodes = set()
    edges = []
    interactions = []
    family_nodes = {
        "CLOCK_PHASE": ("clock", "phase/history"),
        "TRANSPORT": ("event", "propagation"),
        "REDUCER": ("destination_fiber", "reduced_event"),
        "HISTORY": ("history", "response"),
        "MEMORY": ("memory", "response"),
        "LEARNING": ("training_event", "learned_state"),
        "MATTER": ("persistent_organization", "matter_response"),
        "REGENERATION": ("damage", "recovery"),
        "COUPLING": ("system_A", "system_B"),
        "HOMEOSTASIS": ("perturbation", "recovery"),
        "OBSERVER": ("interaction", "detector_record"),
        "INTERFACE": ("incident_event", "interface_response"),
        "PHASE": ("relative_phase", "event_record"),
        "RESOURCE": ("resource_state", "future_capacity"),
    }
    for row in registry:
        if row.get("tier") != "GOLD":
            continue
        family = str(row.get("family", "unknown"))
        family_counts[family] += 1
        canonical = row.get("canonical_claim_id") or row.get("claim_id")
        key = next((name for name in family_nodes if name in family.upper()), None)
        source, target = family_nodes.get(key, ("native_state", "native_response"))
        nodes.update((source, target))
        final = status_by_id.get(canonical)
        reliability = "FRESH_REVALIDATED" if final == "REVALIDATED_FRESH" else "EXACT" if final == "EXACT_DERIVED" else "REPLAY_ONLY" if final == "REPLAY_ONLY" else "HOLDOUT_CONFIRMED"
        edge = {
            "claim_id": canonical,
            "source_core": row.get("source_core"),
            "source": source,
            "target": target,
            "family": family,
            "status": reliability,
            "scope": row.get("scope"),
            "text": row.get("original_text"),
        }
        edges.append(edge)
        interactions.append(
            {
                "interaction_id": canonical,
                "pre_state": source,
                "participants": [source, target],
                "mediator": row.get("mechanism") or "source apparatus native mediator",
                "event": row.get("original_text"),
                "post_state": target,
                "history_effect": "source-specific",
                "observable_consequences": family,
                "hidden_state_consequences": "not fully determined by historical claim",
                "persistence": "claim-specific",
                "relaxation": "claim-specific",
                "canaries": row.get("controls"),
                "scope": row.get("scope"),
                "reliability": reliability,
            }
        )
    graph = {
        "nodes": [{"id": node} for node in sorted(nodes)],
        "edges": edges,
        "gold_claims": len(edges),
        "family_counts": dict(sorted(family_counts.items())),
        "reliability_source": "latest MASTER anti-overfit scorecard",
    }
    write_json(ROOT / "CORE01_14_CAUSAL_PHYSICS_GRAPH.json", graph)
    write_json(ROOT / "DEE_CAUSAL_PHYSICS_GRAPH_CORE01_14.json", graph)
    write_json(ROOT / "INTERACTION_ATLAS.json", {"interactions": interactions})


def initialize_statuses() -> None:
    families = [
        "existence_object_matter", "mass_inertia", "weight", "motion_kinematics",
        "radiation_like", "matter_radiation", "thermal_dissipative", "friction",
        "pressure_stress_elasticity", "vacuum_empty_substrate", "field_mediation",
        "binding_remote", "waves_collective", "sound_like", "resource_work_capacity",
        "information_entropy_irreversibility", "phase_transitions", "measurement_detection",
        "time_clock_causal_order", "space_geometry_topology", "fluid_continuum",
        "relativity_like", "quantum_like",
    ]
    write_json(
        ROOT / "NATIVE_PHENOMENON_ATLAS.json",
        {"families": [{"family": name, "status": "PENDING_ADJUDICATION", "experiments": [], "reason": None} for name in families]},
    )


def main() -> None:
    marker = ROOT / "RESULTS" / "C15A01_TRANSVERSAL_AUDIT.json"
    if marker.exists():
        print(marker.read_text(encoding="utf-8"))
        return
    started = time.perf_counter()
    audit_kernel("CORE15_START")
    paths = core_archives()
    parent_audit(paths)
    q_forensics(paths)
    observer_inventory()
    causal_atlas()
    initialize_statuses()
    write_json(
        marker,
        {
            "module": "C15A01_TRANSVERSAL_AUDIT",
            "status": "COMPLETE",
            "core_archives": 14,
            "q_levels_audited": 5,
            "observer_library_created": True,
            "causal_graph_created": True,
            "elapsed_seconds": time.perf_counter() - started,
            "completed_utc": utc(),
        },
    )
    update_state(status="TRANSVERSAL_COMPLETE", completed_modules=["C15A01"], last_completed="C15A01_TRANSVERSAL_AUDIT")
    print(json.dumps(read_json(marker), indent=2))


if __name__ == "__main__":
    main()
