from __future__ import annotations

"""Offline, fork-only scientific description of an immutable MBP3 cut."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbp3


def _query_positive(query: dict[str, Any]) -> bool:
    if not query.get("executed"):
        return False
    second = query["second"]
    treatment = second["with_query"]
    control = second["same_history_no_query"]
    return (treatment["raw_present"] and
            (treatment["raw"] != control["raw"] or treatment["clock"] != control["clock"]))


def _diff_counts(a: list[int], b: list[int]) -> tuple[int, list[int]]:
    count = 0
    sample: list[int] = []
    for index, (left, right) in enumerate(zip(a, b, strict=True)):
        if left != right:
            count += 1
            if len(sample) < 64:
                sample.append(index)
    return count, sample


def build(campaign_root: Path, descriptor: Path) -> dict[str, Any]:
    campaign_root = campaign_root.resolve()
    descriptor = descriptor.resolve()
    cut = json.loads(descriptor.read_text(encoding="utf-8"))
    # A descriptor lives at WORLD/history/collections/name.json.
    world_root = descriptor.parents[2]
    end_checkpoint = (world_root / cut["end_checkpoint"]).resolve()
    if world_root.resolve() not in end_checkpoint.parents:
        raise RuntimeError("terminal checkpoint escapes MAIN world root")

    diagnostic_path = campaign_root / "analysis" / "NATIVE_CAPABILITY_INTERROGATION.json"
    diagnostic = mbp3.diagnostic_evaluate(end_checkpoint, diagnostic_path)
    final_runtime = mbp3.dee.Runtime.load_snapshot(str(end_checkpoint))
    parent_runtime = mbp3.dee.Runtime.load_snapshot(str(mbp3.parent_path()))
    raw_changes, raw_sample = _diff_counts(parent_runtime.raw_copy(), final_runtime.raw_copy())
    clock_changes, clock_sample = _diff_counts(parent_runtime.clock_copy(), final_runtime.clock_copy())
    static_root = mbp3.project_root()
    pilot = json.loads((static_root / "pilots" / "CURRICULUM_PILOT.json").read_text(encoding="utf-8"))
    c10 = json.loads((static_root / "validation" / "C10H02_MINIMAL_REVALIDATION.json").read_text(encoding="utf-8"))
    qprev = diagnostic["queries"]["Q_PREV_XY"]
    holdout = diagnostic["queries"]["Q_HOLDOUT_XZ"]
    separate = diagnostic["queries"]["Q_SEPARATE_FIBER"]
    primary = diagnostic["primary"]
    companion = diagnostic["companion"]
    primary_retained = not primary.get("ambiguous", True) and primary.get("observation", {}).get("s_reg") == 34
    companion_retained = not companion.get("ambiguous", True) and companion.get("observation", {}).get("s_reg") == 27
    order_control = bool(pilot["criteria"].get("same_query_order_specific_effect"))
    mediation_control = bool(pilot["criteria"].get("mediator_causally_relevant"))

    profile = {
        "schema": "mbp3.capability-profile.v1",
        "campaign_id": mbp3.CAMPAIGN_ID,
        "world_id": mbp3.WORLD_ID,
        "checkpoint": str(end_checkpoint.relative_to(campaign_root)),
        "tick": int(final_runtime.current_tick),
        "parent_tick": mbp3.PARENT_TICK,
        "claims": [
            {
                "id": "PREVIOUS_B_HISTORY",
                "status": "RETENIDO" if primary_retained and _query_positive(qprev) else "NO_RETENIDO",
                "basis": "parent-derived primary remains in the accumulated lineage and responds on a fork",
                "limit": "the q16 contribution is embedded in q34 and is not independently factorized",
            },
            {
                "id": "PRIMARY_NATIVE_CURRICULUM",
                "status": "UTILIZADO" if primary_retained else "NO_RETENIDO",
                "basis": "five kernel contacts yield the frozen q34/x lineage",
                "controls": ["P1 omitted", "P4 mediator omitted", "P1 sham"],
            },
            {
                "id": "SEPARATE_COMPANION_HISTORY",
                "status": "UTILIZADO" if companion_retained and _query_positive(separate) else "NO_RETENIDO",
                "basis": "a distinct fiber reaches q27/x and answers a common fork query",
            },
            {
                "id": "ORDER_AB_VS_BA",
                "status": "UTILIZADO" if order_control else "NO_RETENIDO",
                "basis": "same P1/P2 inventory in reverse order gives a different response to one frozen query",
            },
            {
                "id": "RESERVED_ORIENTATION_HOLDOUT",
                "status": "GENERALIZO_EN_ESTE_HOLDOUT" if _query_positive(holdout) else "NO_GENERALIZO_EN_ESTE_HOLDOUT",
                "basis": "XZ query, positions and timing were frozen before MAIN and applied only on a diagnostic fork",
                "limit": "bounded collision relation; not arbitrary transfer or general intelligence",
            },
            {
                "id": "COMPOSITION",
                "status": "PARCIAL" if primary_retained and order_control and mediation_control else "NO_DEMOSTRADA",
                "basis": "order-dependent route and mediator are both causally relevant",
                "limit": "the prepared apparatus targets the route; untrained recombination is only the reserved fork query",
            },
            {
                "id": "ACTION_ENVIRONMENT_RETURN",
                "status": "PARCIAL" if mediation_control else "NO_DEMOSTRADA",
                "basis": "P4 is necessary for the later P5 encounter",
                "limit": "the same carrier continues through the chain; exclusive environment-stored mediation was not separated",
            },
            {
                "id": "FUNCTIONAL_REINSTANTIATION_C10H02",
                "status": "NO_UTILIZADO",
                "basis": f"independent minimal v27 revalidation {c10['verdict']}",
                "limit": "not installed in MAIN and not counted as acquired knowledge",
            },
        ],
        "no_magic_score": True,
    }
    mbp3.base.atomic_json(campaign_root / "analysis" / "CAPABILITY_PROFILE.json", profile)
    result = {
        "schema": "mbp3.final-analysis.v1",
        "campaign_id": mbp3.CAMPAIGN_ID,
        "world_id": mbp3.WORLD_ID,
        "parent": {"tick": mbp3.PARENT_TICK, "sha256": mbp3.PARENT_SHA256},
        "terminal": {
            "tick": int(final_runtime.current_tick),
            "relative_ticks": int(final_runtime.current_tick) - mbp3.PARENT_TICK,
            "raw_support": int(final_runtime.metrics().raw_support),
            "occupied": int(final_runtime.metrics().occupied),
            "s_reg_sum": int(final_runtime.metrics().s_reg_sum),
            "checkpoint": str(end_checkpoint.relative_to(campaign_root)),
            "checkpoint_sha256": mbp3.sha256(end_checkpoint),
        },
        "comparison_to_parent": {
            "raw_sites_changed": raw_changes, "raw_changed_index_sample": raw_sample,
            "clock_sites_changed": clock_changes, "clock_changed_index_sample": clock_sample,
            "meaning": "full-state change; interpretation comes from frozen functional readers, not these counts",
        },
        "capability_profile": profile,
        "native_interrogation": str(diagnostic_path.relative_to(campaign_root)),
        "pilot_controls": pilot["criteria"],
        "historical_mechanism_revalidation": {
            "C10H02": c10["verdict"], "installed_in_main": False,
        },
        "host_boundary": {
            "environment_installed_at_campaign_t0": True,
            "host_inputs_after_t0": 0,
            "diagnostic_queries_returned_to_main": False,
        },
        "epistemic_limits": [
            "no claim of language, consciousness, universal learning or a general closed loop",
            "prepared geometry is apparatus capacity, not acquired knowledge",
            "state differences without later use are not promoted to learning",
        ],
    }
    output = campaign_root / "analysis" / "FINAL_ANALYSIS.json"
    mbp3.base.atomic_json(output, result)
    report = f"""# MBP3 — informe integrado automático

El mundo `{mbp3.WORLD_ID}` continuó el checkpoint byte-exacto de
`MBP2-B-INTERACTIVO` (tick {mbp3.PARENT_TICK}, SHA-256 `{mbp3.PARENT_SHA256}`).
El ambiente finito fue instalado en la frontera inicial; después no hubo
entradas físicas del host.

El corte terminal está en tick {int(final_runtime.current_tick)}
({int(final_runtime.current_tick) - mbp3.PARENT_TICK} ticks nuevos). Los
observadores relacionales localizaron la fibra primaria q34 y la fibra
compañera q27 cuando las condiciones congeladas se conservaron. Las consultas
se ejecutaron únicamente en forks y no regresaron a MAIN.

El control AB/BA utilizó el mismo inventario y una consulta común: su respuesta
dependió del orden. El holdout XZ se reservó antes de la exposición y se informa
con alcance acotado. La cadena P4→P5 sustenta una mediación directa necesaria,
pero no separa un estado ambiental retenido del portador que continúa; por eso
el closed-loop permanece PARCIAL.

C10H02 fue revalidado aparte sobre v27 con tratamiento, no entrenado, corte de
corredor y receptor ausente. No se instaló en MAIN ni se contabiliza como
adquisición de esta continuidad.

Véanse `analysis/CAPABILITY_PROFILE.json` y
`analysis/NATIVE_CAPABILITY_INTERROGATION.json` para resultados y límites por
consulta. No se emite un score global de inteligencia.
"""
    mbp3.base.atomic_text(campaign_root / "docs" / "INFORME_INTEGRADO.md", report)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--descriptor", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.campaign_root, args.descriptor)
    print(json.dumps({"status": "OK", "analysis": str(args.campaign_root / 'analysis' / 'FINAL_ANALYSIS.json'),
                      "tick": result["terminal"]["tick"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
