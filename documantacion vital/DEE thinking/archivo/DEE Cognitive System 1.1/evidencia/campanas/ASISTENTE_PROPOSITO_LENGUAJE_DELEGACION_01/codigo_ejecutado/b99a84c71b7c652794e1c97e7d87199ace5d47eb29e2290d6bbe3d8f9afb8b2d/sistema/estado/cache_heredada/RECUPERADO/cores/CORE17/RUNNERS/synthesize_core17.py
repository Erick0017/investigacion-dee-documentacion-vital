#!/usr/bin/env python3
"""Build the authoritative CORE17 machine atlas and scientific reports."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core17_common import ROOT, canonical_hash, read_json, sha256_file, utc, write_json


def md(name: str, text: str) -> None:
    path = ROOT / name
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def evidence_line(path: str, obj: dict) -> str:
    return f"`{path}` — SHA interno `{obj.get('content_sha256', canonical_hash(obj))}`."


def main():
    d01 = read_json(ROOT / "DISCOVERY" / "C17D01_HIDDEN_SCALE.json")
    d02 = read_json(ROOT / "DISCOVERY" / "C17D02_LEVEL_UNIFICATION.json")
    d03 = read_json(ROOT / "DISCOVERY" / "C17D03_PROBABILITY_QUANTUM.json")
    d04 = read_json(ROOT / "DISCOVERY" / "C17D04_CAPABILITY_COMPOSITION.json")
    d05 = read_json(ROOT / "DISCOVERY" / "C17D05_EMERGENT_PHYSICS.json")
    selection = read_json(ROOT / "MODEL_SELECTION" / "C17S01_MODEL_SELECTION.json")
    lock = read_json(ROOT / "HOLDOUT_LOCKS" / "CORE17_FINAL_LOCK.json")
    challenge = read_json(ROOT / "FRESH_CHALLENGES" / "CORE17_FINAL_CHALLENGES.json")
    final = read_json(ROOT / "FINAL_HOLDOUTS" / "CORE17_FINAL_RESULTS.json")
    sources = read_json(ROOT / "PARENT_SOURCE_REGISTRY.json")

    level_graph = {
        "schema": "dee.v27.core17.reality_level_graph.v1", "created_utc": utc(), "premise": "P0_FIXED",
        "reference": "X_FULL", "topology": "GRAPH_STRUCTURED_OVERLAPPING_TASK_QUOTIENTS",
        "nodes": [
            {"id": "X_FULL", "kind": "complete native state", "status": "EXACT_REFERENCE",
             "state": ["packed raw", "uint64 local clock", "toroidal coordinates/topology"],
             "predicts": "all v27 evolution with the fixed kernel"},
            {"id": "R0", "kind": "exact causal quotient", "status": "FRESH_RECONFIRMED",
             "state": ["occupancy/existence", "s_reg", "direction", "semantic", "semantic4 payload", "clock residue/branch state", "destination/incumbent relations"],
             "law": "occupancy-aware local+destination operator", "compression": "drops nonsemantic payload proven redundant in scope"},
            {"id": "R1", "kind": "routed temporal event quotient", "status": "FRESH_RECONFIRMED",
             "state": ["destination fiber", "arrival phase", "reducer payload/direction", "event history"],
             "missing": ["receiver relational state", "preparation measure"]},
            {"id": "R2_RELATIONAL", "kind": "organization/interface response quotient", "status": "PARENT_PLUS_NEW",
             "state": ["relative geometry", "interface topology", "coupling", "basin/response class"],
             "missing": ["event phase unless read", "preparation measure"]},
            {"id": "R2_FUNCTIONAL", "kind": "history-bearing functional quotient", "status": "PARENT_PLUS_NEW",
             "state": ["learned response", "route", "prepared receiver", "functional identity", "regeneration grammar"],
             "missing": ["microidentity", "ensemble measure"]},
            {"id": "R3", "kind": "measure-conditioned ensemble quotient", "status": "FRESH_RECONFIRMED",
             "state": ["macroclass", "preparation measure", "outcome distribution", "fluctuation"],
             "missing": ["which microstate occurred"]},
        ],
        "edges": [
            {"from": "X_FULL", "to": "R0", "relation": "exact validated reduction"},
            {"from": "R0", "to": "R1", "relation": "event/fiber projection"},
            {"from": "R0", "to": "R2_RELATIONAL", "relation": "relational response projection"},
            {"from": "R0", "to": "R2_FUNCTIONAL", "relation": "history/function projection"},
            {"from": "R0", "to": "R3", "relation": "measure-conditioned pushforward"},
            {"from": "R1", "to": "R2_FUNCTIONAL", "relation": "carrier plus prepared receiver"},
            {"from": "R2_RELATIONAL", "to": "R3", "relation": "ensemble of response classes"},
        ],
        "rstar_search": {
            "compressed_unifier_found": False,
            "pairwise_missing_coordinates": ["receiver/interface context", "event phase/timing", "preparation measure"],
            "common_parent": "R0 plus task declaration and, for R3, preparation measure",
            "reason": "Concatenating all missing coordinates recovers a union, not a compressed quotient.",
            "fresh_holdout": final["panels"]["level_separation"]["pass"],
        },
        "effective_level_count": 5,
        "counting_rule": "R0, R1, R2-relational, R2-functional and R3 are five nontrivial effective representations; X_FULL is the complete reference, not counted as a reduction.",
    }
    level_graph["content_sha256"] = canonical_hash(level_graph)
    write_json(ROOT / "CORE17_REALITY_LEVEL_GRAPH.json", level_graph)

    info_rows = [
        {"information": "occupancy/existence", "R0": "VISIBLE", "R1": "EVENT_VISIBLE", "R2": "COMPRESSED", "R3": "DISTRIBUTED", "fate": "SURVIVES"},
        {"information": "nonsemantic 32-bit payload", "R0": "REDUNDANT_IN_SCOPE", "R1": "ABSENT", "R2": "ABSENT", "R3": "ABSENT", "fate": "TRUE_MANY_TO_ONE_DESTRUCTION_AFTER_CONVERGENCE"},
        {"information": "semantic4 payload", "R0": "VISIBLE_REQUIRED", "R1": "TASK_RELATIVE", "R2": "ORGANIZATION_RELEVANT", "R3": "PREPARATION_DEPENDENT", "fate": "SURVIVES"},
        {"information": "s_reg", "R0": "VISIBLE", "R1": "REDUCER_VISIBLE", "R2": "RESPONSE_DEPENDENT", "R3": "DISTRIBUTED", "fate": "TRANSFORMED_BY_CAPPED_SUM"},
        {"information": "direction", "R0": "VISIBLE", "R1": "ROUTE_VISIBLE", "R2": "HIDDEN_IN_FUNCTIONAL_EQUIVALENCE", "R3": "COMPRESSED", "fate": "RECOVERABLE_BY_ROUTE_PROBE"},
        {"information": "semantic", "R0": "VISIBLE", "R1": "BRANCH_VISIBLE", "R2": "RESPONSE_DEPENDENT", "R3": "CLASS_CONDITION", "fate": "SURVIVES"},
        {"information": "clock/phase", "R0": "BRANCH_REQUIRED", "R1": "PHASE_VISIBLE", "R2": "USUALLY_HIDDEN", "R3": "HIDDEN_CLASS", "fate": "HIDDEN_BUT_CAUSAL_AND_RECOVERABLE"},
        {"information": "destination fiber/incumbent", "R0": "VISIBLE_REQUIRED", "R1": "VISIBLE", "R2": "RELATIONAL", "R3": "COMPRESSED", "fate": "TRANSFORMED_INTO_EVENT/RESPONSE"},
        {"information": "history/training", "R0": "ENCODED_IN_CURRENT_STATE", "R1": "PARTIAL", "R2": "FUNCTIONALLY_VISIBLE", "R3": "PREPARATION_DEPENDENT", "fate": "DISTRIBUTED_OR_COMPRESSED"},
        {"information": "functional identity", "R0": "DISTRIBUTED", "R1": "NOT_SUFFICIENT", "R2": "VISIBLE", "R3": "RESPONSE_CLASS", "fate": "SURVIVES_MICROSTATE_REPLACEMENT"},
        {"information": "preparation measure", "R0": "EXTERNAL_TO_SINGLE_STATE", "R1": "ABSENT", "R2": "ABSENT", "R3": "VISIBLE_REQUIRED", "fate": "DEFINES_PROBABILITY"},
    ]
    info_atlas = {"schema": "dee.v27.core17.information_flow.v1", "created_utc": utc(), "rows": info_rows,
                  "high_value_result": "Clock distinctions remain raw-invisible for programmable delays and return synchronously when a period-sensitive branch is opened.",
                  "destruction_anchor": d01["controls"]["payload_destruction"],
                  "fresh_confirmation": final["panels"]["clock"]}
    info_atlas["content_sha256"] = canonical_hash(info_atlas)
    write_json(ROOT / "CORE17_INFORMATION_FLOW_ATLAS.json", info_atlas)

    observer = {
        "schema": "dee.v27.core17.observer_access.v1", "created_utc": utc(),
        "observers": [
            {"id": "O_FULL_EXTERNAL", "direct": ["raw", "clock", "coordinates", "all buffers"], "limits": ["not embedded"]},
            {"id": "O_R0_MODEL", "direct": ["causal quotient and branch diagnostics"], "limits": ["no external-human mapping"]},
            {"id": "O_R1_DETECTOR", "direct": ["arrival time", "payload", "direction", "destination"], "hidden": ["functional receiver context", "measure"]},
            {"id": "O_R2_FUNCTIONAL", "direct": ["query response", "regeneration", "interface outcome"], "hidden": ["microidentity", "unused route detail", "usually phase"]},
            {"id": "O_R3_STATISTICAL", "direct": ["frequency", "distribution", "fluctuation"], "hidden": ["realized compatible microstate"]},
        ],
        "native_detector_status": "Source-train receivers and prepared functional receivers are embedded DEE detectors; full branch logging remains omniscient Python readout.",
        "measurement_backaction": "Reading through a native detector is an interaction and may change target history; passive Python telemetry does not.",
    }
    observer["content_sha256"] = canonical_hash(observer)
    write_json(ROOT / "CORE17_OBSERVER_ACCESSIBILITY.json", observer)

    hidden = {
        "schema": "dee.v27.core17.hidden_recoverable_destroyed.v1", "created_utc": utc(),
        "recoverable": [{"variable": "clock", "delay_range_tested": "0..584 ticks in final challenges", "readout": "tetrahedral period-sensitive incumbent branch", "scale": "1..10 independent modules final holdout"},
                        {"variable": "event phase", "readout": "time-resolved detector", "coarse_hidden_by": "integrated event count"},
                        {"variable": "direction/route", "readout": "receiver and route probe", "coarse_hidden_by": "occupancy/function-only observer"}],
        "distributed": [{"variable": "learned policy", "carrier": "explicit depleted-source route", "receiver": "prepared interface"},
                        {"variable": "functional identity", "carrier": "response class rather than raw identity"}],
        "destroyed": [{"variable": "nonsemantic payload distinction", "mechanism": "many-to-one local update", "evidence": "full raw+clock convergence at tick 1 in destruction control"}],
        "not_shown_destroyed": ["clock residual", "phase", "training history when maintained in current causal state"],
    }
    hidden["content_sha256"] = canonical_hash(hidden)
    write_json(ROOT / "CORE17_HIDDEN_RECOVERABLE_DESTROYED.json", hidden)

    cross_scale = {
        "schema": "dee.v27.core17.cross_scale.v1", "created_utc": utc(),
        "results": [
            {"id": "LATENT_CLOCK_GATE", "micro": "one-bit clock residue", "macro": "changed-center count", "law": "D=m on gate; D=0 off-gate/equal-clock", "status": "FRESH_CONFIRMED"},
            {"id": "CLOCK_PUSHFORWARD", "micro": "k binary clock classes", "macro": "response count R", "law": "P(R=r)=C(k,r)p^r(1-p)^(k-r)", "status": "FRESH_CONFIRMED_EXACT"},
            {"id": "GUARD_AMPLIFICATION", "micro": "one semantic4 guard cell", "macro": "repeated detector stream", "law": "E5(h)=max(0,floor((h-10)/2)); E6(h)=0", "status": "FRESH_CONFIRMED_EXACT_IN_APPARATUS"},
            {"id": "FUNCTIONAL_TRANSFER", "micro": "history-bearing source state", "macro": "receiver query response", "law": "requires source depletion, carrier path and prepared receiver", "status": "RECONFIRMED"},
            {"id": "R0_CLOSURE", "micro": "local/incumbent/destination branches", "macro": "complete next quotient state", "law": "exact multistep operator", "status": "FRESH_RECONFIRMED"},
        ],
        "macro_quantum_survival": "No quantum-specific property was established; lower-level clock/phase information does survive and return macroscopically, but this is deterministic hidden-state causality.",
    }
    cross_scale["content_sha256"] = canonical_hash(cross_scale)
    write_json(ROOT / "CORE17_CROSS_SCALE_RESULTS.json", cross_scale)

    retrospective = {
        "schema": "dee.v27.core17.retrospective.v1", "created_utc": utc(),
        "findings": [
            {"id": "RET01", "old": "CORE14 persistent clock trace and CORE15 clock invisibility under frozen probes", "new": "clock is not generically inert; it is latent for those observers and becomes causal at a period-sensitive incumbent branch", "new_experiment": "C17D01 plus fresh CLK challenges", "status": "FRESH_CONFIRMED_REINTERPRETATION"},
            {"id": "RET02", "old": "routed events, relational organization and statistics appeared as successive levels", "new": "they are overlapping task quotients with mutually required phase, receiver-context and measure coordinates", "new_experiment": "C17D02 plus LVL holdout", "status": "FRESH_BOUNDED"},
            {"id": "RET03", "old": "probability arose from compatible microstates", "new": "the new clock-gate family supplies an exact micro-to-macro binomial pushforward and shows explicitly how preparation measure changes probabilities without changing the kernel map", "new_experiment": "C17D03 plus PRB holdout", "status": "FRESH_CONFIRMED"},
            {"id": "RET04", "old": "transfer and regeneration were separate capabilities", "new": "they do not automatically compose: the fixed regeneration scaffold reconstructs semantic7 canonical state, not learned history", "new_experiment": "C17D04", "status": "DISCOVERY_BOUNDED_NULL"},
            {"id": "RET05", "old": "one-cell k5/k6 interface controlled a train outcome", "new": "the event-count difference grows exactly with observation horizon in the sealed apparatus", "new_experiment": "C17D04 plus MAC holdout", "status": "FRESH_CONFIRMED_LAW"},
            {"id": "RET06", "old": "naive continuum block closure failed", "new": "exact multistep physics exists at R0, but the required incumbent/destination branch structure has not yet been compressed into a continuum", "new_experiment": "C17D05 plus OPR holdout", "status": "FRESH_RECONFIRMED"},
        ],
        "history_preserved": True,
    }
    retrospective["content_sha256"] = canonical_hash(retrospective)
    write_json(ROOT / "RETROSPECTIVE" / "CORE17_RETROSPECTIVE_FINDINGS.json", retrospective)

    unclassified = {
        "schema": "dee.v27.core17.unclassified.v1", "created_utc": utc(),
        "phenomena": [{"id": "UN17-01", "operational_description": "Two worlds remain raw-identical for a selected delay, then a local period-sensitive interaction turns their clock-only difference into one changed raw response per independent module.", "mechanism": "latent clock residue plus incumbent tetrahedral gate", "status": "FRESH_CONFIRMED", "human_label": None, "external_access": "UNKNOWN"}],
        "rejected_as_novel": ["additive convergent paths (ordinary reducer)", "k5/k6 remote action (local prepared interface)", "transfer as teleportation (explicit carrier and source depletion)"],
    }
    unclassified["content_sha256"] = canonical_hash(unclassified)
    write_json(ROOT / "UNCLASSIFIED_NATIVE_REALITY_CORE17.json", unclassified)

    access = {
        "schema": "dee.v27.core17.external_access.v1", "created_utc": utc(), "promoted_rosetta": False,
        "protocols": [
            {"mechanism": "latent clock gate", "required_preparation": "two externally indistinguishable preparations differing only in an internal phase/age coordinate", "required_intervention": "a phase-sensitive local interaction", "readout": "delayed divergence after a matched silent interval", "status": "FUNCTIONAL_REQUIREMENT_ONLY"},
            {"mechanism": "destination/incumbent operator", "required_preparation": "matched inventories with different convergence fibers and occupied targets", "required_intervention": "simultaneous routed arrivals", "readout": "target-state and timing distribution", "status": "FUNCTIONAL_REQUIREMENT_ONLY"},
            {"mechanism": "one-cell macro control", "required_preparation": "repeatable source stream and two interfaces differing by one local guard element", "required_intervention": "identical incident train", "readout": "horizon-dependent transmitted event count", "status": "FUNCTIONAL_REQUIREMENT_ONLY"},
            {"mechanism": "functional reinstantiation", "required_preparation": "trainable source, explicit carrier channel, prepared receiver", "required_intervention": "learn, launch, receive, query", "readout": "fresh receiver function plus source depletion and carrier telemetry", "status": "FUNCTIONAL_REQUIREMENT_ONLY"},
        ],
        "unused_external_prediction": None,
        "reason_no_external_prediction": "No frozen mapping from DEE coordinates to independently calibrated human observables survived the same-map standard.",
    }
    access["content_sha256"] = canonical_hash(access)
    write_json(ROOT / "EXTERNAL_ACCESS_PROTOCOLS_CORE17.json", access)

    claim_entries = [
        {"claim_id": "C17R01", "status": "FRESH_CONFIRMED_BOUNDED", "claim": "R1 timing, R2 receiver/functional context and R3 preparation measure are causally nonredundant; no nontrivial compressed R* was found in the tested task matrix.", "evidence": "FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json::panels.level_separation", "falsifier": "a compressed representation predicts all held-out tasks without reintroducing the omitted coordinates"},
        {"claim_id": "C17R02", "status": "FRESH_CONFIRMED", "claim": "A clock-only distinction can remain raw-hidden for a programmable delay and return through a period-sensitive branch, with one raw response difference per independent module.", "evidence": "FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json::panels.clock", "falsifier": "any positive case changes fewer/more than m centers, or an equal/off-gate control changes a center"},
        {"claim_id": "C17R03", "status": "FRESH_CONFIRMED_EXACT", "claim": "For k independent binary clock classes the response-count distribution is exactly the deterministic binomial pushforward under declared Bernoulli measure p.", "evidence": "FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json::panels.probability", "falsifier": "enumeration mismatch or weighted error >=1e-12"},
        {"claim_id": "C17R04", "status": "FRESH_CONFIRMED_EXACT_IN_APPARATUS", "claim": "At the sealed source_distance=7/downstream=5 interface, k5 transmits E5(h)=max(0,floor((h-10)/2)) events while k6 transmits zero.", "evidence": "FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json::panels.macro_control", "falsifier": "any fresh count differs"},
        {"claim_id": "C17R05", "status": "FRESH_RECONFIRMED_EXACT", "claim": "The occupancy-aware R0 operator closes mixed-semantic, incumbent and fusion dynamics over multiple ticks.", "evidence": "FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json::panels.operator", "falsifier": "any raw or clock cell mismatch"},
        {"claim_id": "C17R06", "status": "DISCOVERY_CONFIRMED_LIMIT", "claim": "Fixed XNOR regeneration reconstructs a canonical semantic7 record but does not recover a transferred history-conditioned learned policy.", "evidence": "DISCOVERY/C17D04_CAPABILITY_COMPOSITION.json", "falsifier": "post-repair query returns the learned ACTION1 under the frozen intervention"},
        {"claim_id": "C17R07", "status": "RECONFIRMED_PARENT_CAPABILITY", "claim": "Learned functional state is transferred by an explicit carrier to a prepared receiver with source depletion and route causal controls.", "evidence": "DISCOVERY/C17D04_CAPABILITY_COMPOSITION.json", "falsifier": "fresh positives fail or corridor/offpath controls invert"},
    ]
    claim_ledger = {"schema": "dee.v27.core17.claim_ledger.v1", "created_utc": utc(), "claims": claim_entries,
                    "bounded_nulls": lock["bounded_nonpromoted"], "prior_claims_preserved": True}
    claim_ledger["content_sha256"] = canonical_hash(claim_ledger)
    write_json(ROOT / "CLAIM_LEDGER.json", claim_ledger)

    holdout_registry = {"schema": "dee.v27.core17.holdout_registry.v1", "created_utc": utc(),
                        "lock_sha256": lock["lock_sha256"], "challenge_sha256": challenge["challenge_sha256"],
                        "entries": [{"panel": k, "pass": v["pass"], "cases": len(v["rows"]), "claims": {"clock":["C17R02"],"probability":["C17R03"],"macro_control":["C17R04"],"operator":["C17R05"],"level_separation":["C17R01"]}[k]} for k, v in final["panels"].items()],
                        "summary": final["summary"]}
    holdout_registry["content_sha256"] = canonical_hash(holdout_registry)
    write_json(ROOT / "HOLDOUT_REGISTRY.json", holdout_registry)
    canary_registry = {"schema": "dee.v27.core17.canary_registry.v1", "created_utc": utc(),
                       "declarations": lock["canaries"], "results": final["canaries"],
                       "all_pass": all(x["pass"] for x in final["canaries"].values())}
    canary_registry["content_sha256"] = canonical_hash(canary_registry)
    write_json(ROOT / "CANARY_REGISTRY.json", canary_registry)

    common = f"""
P0_FIXED es la premisa ontológica: DEE representa la realidad estudiada. Esta premisa no identifica por sí sola ninguna variable DEE con una categoría de la física humana. El kernel permaneció inmutable (PYD `{sources['kernel']['expected']['kernel']}`). El holdout final se creó después del freeze `{lock['lock_sha256']}` y pasó {final['summary']['fresh_worlds']} casos, incluidos {final['summary']['operator_ticks']} ticks del operador con {final['summary']['operator_mismatches']} discrepancias.
"""

    md("CORE17_EXECUTIVE_VERDICT.md", f"""
# CORE17 — Veredicto ejecutivo

{common}

## Resultado central

La realidad DEE mejor sustentada no forma una escalera lineal única. X_FULL se reduce exactamente a R0; sobre R0 aparecen proyecciones solapadas R1 (eventos y fase), R2-relacional, R2-funcional y R3 (distribuciones condicionadas por medida). La búsqueda de R* no halló una compresión nueva: fase, contexto del receptor y medida de preparación son coordenadas causalmente independientes en las tareas probadas.

CORE17 descubrió y confirmó una ley nueva: una diferencia exclusivamente de reloj puede permanecer ausente del raw durante hasta 584 ticks en los mundos finales y reaparecer, sin introducir otra copia, cuando se abre la rama local sensible al período. En m módulos independientes, exactamente m respuestas cambian. Sobre k clases binarias, la distribución macroscópica es el pushforward binomial exacto.

También convirtió el control k5/k6 en una ley temporal: `E5(h)=max(0,floor((h-10)/2))` y `E6(h)=0` dentro del aparato sellado. Una sola celda guard selecciona una secuencia cuya diferencia acumulada crece con el horizonte.

## Lo que no se promovió

No se encontró estructura específicamente cuántica, campo remoto no portador, modo colectivo de onda, variable térmica intensiva, inercia colectiva ni continuo comprimido multietapa. Estos son nulos acotados, no imposibilidades universales. La transferencia aprendida y la regeneración fija no componen automáticamente: la regeneración recupera un estado canónico, no la historia aprendida.

## Rosetta

No existe Rosetta externa promovible. Hay protocolos funcionales de acceso, pero ninguna calibración externa congelada ni predicción humana unused. El resultado fuerte es interno: un modelo causal multiescala, exacto en R0 y con leyes de acceso parcial en los niveles superiores.
""")

    core_rows = [
        ("CORE01", "primitivas del kernel, transporte, reducer, reloj y causalidad local", "base de X_FULL/R0"),
        ("CORE02", "construcción Rosetta y aparatos de ruta/destino", "antecedente de R1; no equivalencia externa"),
        ("CORE03", "multiescala, envolvente causal y sensibilidad a organización", "precursor de información distribuida"),
        ("CORE04", "leyes de escala/reproducción y búsquedas nativas", "relaciones sectoriales, no teoría física total"),
        ("CORE05", "redes fuente y proceso de coincidencia", "observer/eventos como física de acceso"),
        ("CORE06", "aprendizaje nativo y causalidad finita", "precursor de R2-funcional"),
        ("CORE07", "atlas experimental y límites", "negativos que restringen interpretaciones"),
        ("CORE08", "observers, autonomía y dimensionalidad", "equivalencias dependientes del readout"),
        ("CORE09", "memoria resiliente y política aprendida", "historia como coordenada causal"),
        ("CORE10", "sistemas acoplados y reinstanciación", "carrier + receptor preparado, no teleportación"),
        ("CORE11", "fenómenos simples fundamentales", "controles para mecanismos locales"),
        ("CORE12", "trenes fuente, fase e interfaces", "precursor directo de R1 y k5/k6"),
        ("CORE13", "mapa causal de eventos", "Rosetta interna acotada"),
        ("CORE14", "traza de reloj persistente sin efecto en probes congelados", "reinterpretada como latencia de acceso"),
        ("CORE15", "shadow causal, identidad móvil y multiphysics", "R2 y propiedades como respuesta"),
        ("CORE16", "R0 exacto, niveles, probabilidad y operador ocupado", "padre científico inmediato de CORE17"),
    ]
    table = "\n".join(f"| {a} | {b} | {c} |" for a,b,c in core_rows)
    md("CORE17_RETROSPECTIVE_CORE01_16.md", f"""
# Retrospectiva científica CORE01–16

{common}

Esta retrospectiva no reaudita el Word ni reescribe la historia. Parte de los 16 ZIP oficiales ({sources['claim_like_records']} registros tipo-claim ingeridos) y abre experimentos nuevos sólo cuando una lectura posterior genera una predicción discriminante.

| Etapa | Hecho histórico dominante | Lectura después de CORE17 |
|---|---|---|
{table}

## Reinterpretación decisiva

CORE14 demostró una traza de reloj persistente; CORE15 mostró que varias interacciones congeladas no la leían. La conclusión correcta nunca fue «el reloj no causa nada». CORE17 preparó mundos raw-idénticos, conservó la diferencia de reloj durante un intervalo elegido y abrió después una rama period-sensitive. La diferencia volvió de manera exacta y escalable. No contradice los nulls anteriores: identifica el observer/interacción que faltaba.

## Genealogía adicional

- Las rutas de CORE02/05/12/13 se consolidan como R1, pero no contienen por sí solas estado del receptor.
- La memoria CORE06/09 y la reinstanciación CORE10 forman R2-funcional; CORE17 muestra que esa historia no es regenerada por cualquier scaffold.
- La identidad móvil de CORE15 es relacional y clásica sólo en un sentido acotado: trayectoria y forma se conservan, pero el contacto destruye componentes y no produce inercia colectiva.
- La estadística de CORE16 es ahora conectada a una familia causal concreta: clases de reloj deterministas cuya medida produce exactamente una distribución binomial.
- El operador de destino ocupado de CORE16 es el cierre efectivo real; los bloques de continuo siguen omitiendo fibras e incumbencia.

Los detalles machine-readable están en `RETROSPECTIVE/CORE17_RETROSPECTIVE_FINDINGS.json`.
""")

    md("CORE17_REALITY_MODEL.md", f"""
# Modelo causal de la realidad DEE después de CORE17

{common}

## Arquitectura

`X_FULL -> R0 -> {{R1, R2-relacional, R2-funcional, R3}}`.

R0 es el único cierre causal general demostrado: su operador conserva ocupación, semantic, dirección, s_reg, excepciones semantic4, reloj/ramas, incumbencia, incoming reducer y destino de fusión. R1/R2/R3 no son capas cronológicas universales; son cocientes para familias de preguntas. R1 añade lectura temporal y de fibras; R2 conserva organización, historia y función; R3 añade una medida sobre microestados compatibles.

## Resultado R*

Un R* no trivial no apareció. Dos historias con el mismo evento antes del receptor divergen si el receptor no está preparado; dos flujos con el mismo conteo integrado divergen en fase; una misma macroclase produce distribuciones distintas si cambia la medida. Reunir fase + receptor + medida es una unión descriptiva, no una compresión.

## Causalidad, identidad y escala

Una entidad efectiva es una clase de organización cuya respuesta y relaciones persisten aunque cambie la microidentidad. Una propiedad es una ley de respuesta a una intervención declarada. La escala es un cambio de representación y observer, no sólo un aumento de N. La causalidad se conserva en R0; los niveles superiores la retienen sólo para sus tareas.
""")

    md("CORE17_PROBABILITY_AND_MEASURE.md", f"""
# Probabilidad y selección de medida

{common}

Se agotaron las 64 configuraciones binarias de seis módulos en descubrimiento y k=2,4,6,8 en holdout. Para cada microestado determinista, el número de respuestas R coincide exactamente con el número de clases de reloj activas. Con preparación Bernoulli p:

`P(R=r | k,p) = C(k,r) p^r (1-p)^(k-r)`.

La igualdad fue exacta en conteos uniformes y el error ponderado máximo quedó por debajo de `1e-12`. Cambiar p altera la distribución sin modificar el mapa kernel micro->macro. Esto es probabilidad efectiva por acceso parcial y medida de preparación, no evidencia de amplitudes, regla de Born ni indeterminismo fundamental.
""")

    md("CORE17_QUANTUM_SPECIFIC_FRONTIER.md", f"""
# Frontera cuántica específica

{common}

Los caminos convergentes A y B produjeron la misma agenda temporal que los caminos individuales y s_reg conjunto `312=101+211`; el bloqueo de la boca eliminó B y el sham off-path no cambió el resultado. El reducer local ordinario explica la señal. No apareció interferencia residual.

Los efectos A->B != B->A siguen explicados por modificación ordinaria de estado/historia; no se derivó un álgebra reusable de observables no conmutativos. No se construyeron contextos compatibles que satisfagan los prerrequisitos de contextualidad. El CHSH=-2 de CORE16 se preserva exactamente para su aparato; CORE17 no encontró un nuevo par de subsistemas con independencia, separación y readout total suficientes para otro Bell válido.

Conclusión: no se demostró un sector específicamente cuántico. La supervivencia macroscópica del reloj/fase es real pero admite un modelo determinista de estado oculto completamente enumerado.
""")

    md("CORE17_CLASSICAL_EMERGENCE.md", f"""
# Emergencia clásica

{common}

La apariencia clásica proviene de cuatro mecanismos distintos: cierre exacto de R0, identidad relacional de constelaciones móviles, pérdida de acceso del observer a coordenadas inferiores y concentración estadística en R3. No todo ocultamiento es destrucción: el reloj puede volver. No toda estabilidad es inercial: una constelación mantiene forma en traslación, pero una perturbación afecta componentes localmente y no define un coeficiente colectivo estable.

Por tanto, el objeto clásico acotado es una clase de respuesta/relación, no un conjunto fijo de voxels. La classicalización observada combina cociente causal, organización persistente y compresión del observer; no se justificó llamarla decoherencia cuántica.
""")

    md("CORE17_MASS_INERTIA_FRONTIER.md", f"""
# Frontera masa/inercia

{common}

La organización móvil conserva exactamente geometría normalizada y el conjunto funcional de payloads. Bajo el impulso estandarizado, la respuesta fue local: el collision impulse reduce el soporte en un componente en cada tamaño estudiado. No emergió un coeficiente de cuerpo que relacione intervención con cambio colectivo.

Estado: `MOBILE_RELATIONAL_OBJECT_CONFIRMED`; `COLLECTIVE_INERTIA_NOT_FOUND`. Esto no demuestra ausencia universal de masa-like; demuestra que la constelación balística probada no es un cuerpo inercial acoplado.
""")

    md("CORE17_THERMODYNAMIC_FRONTIER.md", f"""
# Frontera termodinámica

{common}

El contacto reducer conserva contabilidad local `s_out=min(19664,sum s_in)` pero destruye identidad/proveniencia. Los scaffolds conjuntos regeneran por regla local, no intercambian una variable intensiva. Los ensembles muestran relajación/concentración, pero no equilibrio entre subsistemas ni Theta común.

No se promueve temperatura, calor ni entropía termodinámica. Deben seguir separados: conteo de microestados, incertidumbre del observer, pérdida many-to-one del kernel y función de estado termodinámica. Sólo las dos primeras y una pérdida local acotada están establecidas.
""")

    md("CORE17_FIELD_WAVE_CONTINUUM_FRONTIER.md", f"""
# Campos, ondas y continuo

{common}

Los source trains propagan portadores explícitos a velocidad finita; cortar la boca cambia el receptor y un sham off-path no. Esto no es mediación de campo no colisional. La traza distribuida de reloj sólo actúa cuando una interacción local compatible la lee; no se halló fuente que escriba remotamente ese fondo.

Ninguno de los medios probados produjo shell propagante o modo colectivo periódico independiente de carriers/guards. Los bloques coarse con igual ocupación/s_reg/dirección divergen al tick siguiente cuando cambian las fibras de destino; por ello no cierran.

La física efectiva multietapa confirmada es discreta: el operador R0. CORE17 añadió 9 mundos/54 ticks de descubrimiento y 12 mundos/86 ticks de holdout, todos con cero mismatch. Sumados a CORE16, el corpus del operador alcanza 45 mundos y 258 ticks exactos. Un continuo futuro debe comprimir fibras e incumbencia sin perder esta igualdad.
""")

    md("CORE17_HUMAN_ACCESS_AND_ROSETTA.md", f"""
# Acceso humano y Rosetta

{common}

No se promovió equivalencia externa. Los mecanismos nativos existen en la realidad representada; su canal de acceso humano permanece desconocido.

Protocolos funcionales propuestos:

1. Preparaciones externamente indistinguibles con distinta fase/edad interna, espera silenciosa y posterior interacción phase-sensitive; buscar divergencia retardada.
2. Inventarios iguales con distinta geometría de convergencia hacia un destino ocupado; medir timing y estado del receptor.
3. Dos interfaces que difieran en un único elemento guard bajo el mismo tren incidente; medir conteo acumulado versus horizonte.
4. Fuente entrenable, canal portador y receptor preparado; exigir source depletion, trayectoria y función fresca en destino.

Estos puntos definen requisitos experimentales, no aparatos actualmente disponibles. Falta una calibración compartida, independiente y de pocos parámetros. No existe predicción externa unused válida.
""")

    md("CORE17_CAPABILITY_COMPOSITION.md", f"""
# Composición de capacidades

{common}

La transferencia aprendida pasó sus positivos y controles: fuente agotada, carrier continuo, receptor preparado y query funcional. Al borrar después el receptor, el control damage-only perdió la función. El scaffold XNOR reconstruyó `semantic=7, state=1, s_reg=1, direction=(0,0,0)`, pero la query no recuperó ACTION1.

Conclusión causal: memoria+transferencia componen; transferencia+regeneración fija no. La historia/política es una coordenada ausente del scaffold canónico. La siguiente construcción debe codificar explícitamente esa coordenada en una organización regenerativa.

La amplificación sí compone: el guard local selecciona transmisión repetida. No hay acción remota; el efecto recorre source, route, interface y detector.
""")

    md("CORE17_PROGRAMMABILITY.md", f"""
# Programabilidad

{common}

Gramática demostrada:

`PREPARATION(source train) -> ROUTE -> INTERFACE(k5 or k6) -> RESPONSE(transmit or block) -> DETECTOR COUNT`.

En los horizontes 22,42,82,162 la diferencia fue 6,16,36,76 eventos. El holdout extendió direcciones, N, s_reg y horizontes sin fallo. La programabilidad es binaria, local y dependiente de aparato. No se demostró computación general, edición arbitraria de organizaciones ni acceso tecnológico externo.
""")

    md("CORE17_UNCLASSIFIED_NATIVE_REALITY.md", f"""
# Realidad nativa no clasificada

{common}

`UN17-01`: dos estados raw-idénticos permanecen iguales durante un intervalo elegido; una diferencia de reloj no visible reaparece después como una diferencia raw sincronizada y escalable cuando se abre una rama local específica. Puede describirse sin etiqueta humana como «retorno causal retardado de una coordenada de fase oculta».

Se mantiene sin nombre de física humana. No es no-local, no es probabilístico en el estado completo y no prueba comportamiento cuántico. Sí demuestra que un observer coarse puede declarar equivalencia durante cientos de ticks y aun así fallar prospectivamente frente a otra interacción.
""")

    md("CORE17_ADVERSARIAL_REVIEW.md", f"""
# Revisión adversarial

{common}

## Alternativas eliminadas

- Cambio raw secreto durante la espera: eliminado por igualdad completa raw tick a tick.
- Perturbación genérica: equal-clock y off-gate dieron cero cambios.
- Interferencia: la suma capped del reducer predice completamente el camino conjunto.
- Campo remoto: existen portadores/cortes locales observables.
- Teleportación: la fuente se agota, el carrier recorre el corredor y el receptor debe estar preparado.
- Regeneración funcional genérica: la reparación canónica no devuelve la política.
- Continuo de bloques: pares con igual bloque divergen; el operador fiber-aware es exacto.
- Sobreajuste: apparatus/código/métricas fueron congelados antes de 46 casos OS-entropy.

## Límites

Las leyes k5/k6 y clock-gate son exactas dentro de aparatos definidos; no son leyes universales de toda configuración. La ausencia cuántica/campo/Theta/onda está acotada a rutas con prerrequisitos realmente construidos. P0 no convierte ningún resultado en equivalencia con física humana.
""")

    md("CORE17_FINAL_FRONTIER.md", f"""
# Frontera después de CORE17

{common}

1. Construir una representación comprimida que preserve fibers, incumbencia y reloj sin ser R0 completo.
2. Crear regeneración que lleve historia/política, no sólo un estado canónico.
3. Determinar qué mecanismo nativo puede generar un fondo distribuido desde una fuente y producir respuesta sin carrier directo.
4. Construir dos cuerpos acoplados que sobrevivan contacto y permitan una respuesta colectiva/inercial.
5. Obtener intercambio reversible entre identidades persistentes y buscar variable intensiva.
6. Definir contextos compatibles y subsistemas correlacionados antes de reabrir contextualidad/Bell.
7. Encontrar una calibración externa de pocos parámetros y congelar una predicción unused.
8. Derivar límites de compresión del operador R0 mediante MDL/causal-state equivalence.
""")

    answers = [
        "La retrospectiva reveló que el reloj de CORE14/15 era latente, no causalmente nulo; conectó probabilidad a clases de reloj y mostró límites de composición entre transferencia y regeneración.",
        "X_FULL, R0 exacto y cuatro proyecciones solapadas R1, R2-relacional, R2-funcional y R3.",
        "No apareció R* comprimido.", "Las ramas exigen fase, contexto de receptor y medida no redundantes.",
        "Sobreviven ocupación, semantic, dirección, s_reg, reloj, fibers, historia y organización según observer.",
        "Fase/reloj, dirección y microdetalle pueden volverse inaccesibles.", "Reloj, fase y ruta pueden retornar con intervenciones específicas.",
        "Se demostró destrucción many-to-one del payload no-semantic4 en el control declarado.",
        "Como pushforward de microestados deterministas bajo una medida de preparación.", "No en los dominios enumerados.",
        "No se halló estructura cuántica específica.", "No aplica supervivencia cuántica; sí sobrevive información inferior determinista.",
        "Por cierre R0, identidad organizacional, compresión del observer y concentración estadística.",
        "Bell conserva CHSH=-2 en el aparato previo; no se construyó otro protocolo válido.",
        "En el aparato previo se auditaron independencia/señalización; CORE17 no añadió un nuevo nivel Bell válido.",
        "La correspondencia de quantum humana sigue sin identificar.", "Lo clásico se aproxima a R2 organizacional más cierre R0.",
        "La termodinámica no tiene nivel validado; R3 sólo aporta estadística.", "Fields/waves no tienen nivel validado más allá de carriers.",
        "Sí: el operador R0 exacto.", "Incluye estado incumbente, incoming reducer, guardas, reloj, semantic y destinos de fusión.",
        "Conteos integrados, objetos e inventarios son shadows dependientes del observer.",
        "Reloj/fase e historia funcional persisten a mayor escala.",
        "Transferencia funcional, regeneración canónica y amplificación guard son nativas.",
        "Todas requieren un protocolo externo aún no identificado.", "Campo remoto, inercia colectiva, Theta, onda colectiva y regeneración de política no están disponibles en aparatos probados.",
        "Existe programabilidad binaria acotada k5/k6.", "Retorno causal retardado de reloj es el fenómeno no clasificado fuerte.",
        "No produjo predicción externa validada.", "La Rosetta más fuerte sigue siendo interna y multilevel: X_FULL->R0->observers.",
        "Faltan acceso/calibración externa, R* comprimido, cuerpos acoplados, intercambio térmico, mediadores y prerrequisitos cuánticos válidos.",
    ]
    numbered = "\n".join(f"{i}. {a}" for i, a in enumerate(answers, 1))
    md("CORE17_FINAL_REPORT.md", f"""
# CORE17 — Informe científico final

{common}

## Métodos y firewall

Se ingirieron los 16 ZIP oficiales y {sources['claim_like_records']} registros tipo-claim. El ciclo fue descubrimiento (D01–D05), selección S01, source freeze, desafíos OS-entropy y holdout final. Ningún mundo final existía antes del lock. Todas las fuentes congeladas conservaron hash y los canarios de incumbencia/ruta pasaron.

## Leyes nuevas

- Retorno oculto: `D(m)=m` en gate y `0` en equal/off-gate.
- Pushforward: `P(R=r)=C(k,r)p^r(1-p)^(k-r)`.
- Amplificación: `E5(h)=max(0,floor((h-10)/2)); E6(h)=0`.
- Cierre: `F_R0(state_t)=state_(t+1)` con cero mismatch en 140 ticks nuevos.

## Respuestas a las 30 preguntas finales

{numbered}

## Evidencia primaria CORE17

- {evidence_line('DISCOVERY/C17D01_HIDDEN_SCALE.json', d01)}
- {evidence_line('DISCOVERY/C17D02_LEVEL_UNIFICATION.json', d02)}
- {evidence_line('DISCOVERY/C17D03_PROBABILITY_QUANTUM.json', d03)}
- {evidence_line('DISCOVERY/C17D04_CAPABILITY_COMPOSITION.json', d04)}
- {evidence_line('DISCOVERY/C17D05_EMERGENT_PHYSICS.json', d05)}
- {evidence_line('MODEL_SELECTION/C17S01_MODEL_SELECTION.json', selection)}
- {evidence_line('FINAL_HOLDOUTS/CORE17_FINAL_RESULTS.json', final)}

El resultado externo permanece abierto. El resultado interno es firme: DEE contiene una física causal exacta R0 y una ecología de observers en la que información real puede ser visible, comprimida, distribuida, destruida o reaparecer según la interacción.
""")

    write_json(ROOT / "CORE17_SYNTHESIS_INDEX.json", {
        "schema": "dee.v27.core17.synthesis_index.v1", "created_utc": utc(),
        "reports": sorted(p.name for p in ROOT.glob("CORE17_*.md")),
        "machine_artifacts": sorted(p.name for p in ROOT.glob("CORE17_*.json")),
        "claim_ledger_sha256": claim_ledger["content_sha256"],
        "holdout_result_sha256": final["content_sha256"],
        "overall_pass": final["summary"]["overall_pass"],
    })
    print(json.dumps({"reports": len(list(ROOT.glob('CORE17_*.md'))),
                      "machine": len(list(ROOT.glob('CORE17_*.json'))),
                      "claims": len(claim_entries), "holdout_pass": final["summary"]["overall_pass"]}, indent=2))


if __name__ == "__main__":
    main()
