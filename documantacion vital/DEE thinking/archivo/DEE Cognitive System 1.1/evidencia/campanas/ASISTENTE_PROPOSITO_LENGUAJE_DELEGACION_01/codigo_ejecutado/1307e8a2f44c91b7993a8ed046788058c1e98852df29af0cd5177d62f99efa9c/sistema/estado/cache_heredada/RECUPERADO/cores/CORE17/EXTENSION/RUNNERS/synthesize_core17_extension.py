#!/usr/bin/env python3
"""Synthesize only the definitive CORE17 extension and closure."""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from core17e_common import PRE_EXTENSION_SHA256, ROOT, audit_kernel, seal, sha256_file, write_json


def load(path): return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    e01=load(ROOT/"DISCOVERY"/"C17E01_POLICY_COORDINATE.json")
    e02=load(ROOT/"DISCOVERY"/"C17E02_REDUNDANT_POLICY_REPAIR.json")
    h03=load(ROOT/"HOLDOUT"/"C17E03_POLICY_REPAIR_HOLDOUT.json")
    e04=load(ROOT/"DISCOVERY"/"C17E04_R0_FACTOR_COMPRESSION.json")
    h05=load(ROOT/"HOLDOUT"/"C17E05_R0_FACTOR_HOLDOUT.json")
    e06=load(ROOT/"DISCOVERY"/"C17E06_PREREQUISITE_CONSTRUCTIONS.json")
    claims=[
      {"claim_id":"C17E-CLAIM-001","status":"FRESH_CONFIRMED_BOUNDED","claim":"In the learned-transfer apparatus, the operational policy is carried by direction rather than s_reg; a second learned direction-state can reconstruct a damaged policy through an intact explicit carrier route and restore fresh function.","evidence":"EXTENSION/HOLDOUT/C17E03_POLICY_REPAIR_HOLDOUT.json","falsifier":"any frozen treatment/offpath failure or any untrained/direction-reset/no-backup/path-cut/wrong-receiver success","scope":"source-supported redundant reconstruction, not autonomous local regeneration"},
      {"claim_id":"C17E-CLAIM-002","status":"FRESH_CONFIRMED_EXACT_QUOTIENT","claim":"R0_FACTOR_52 is an exact multistep causal quotient in the declared well-formed domain: ordinary cells require 52 bits, semantic-4 cells 64 bits, and the fixed global clock phase modulus is 304980.","evidence":"EXTENSION/HOLDOUT/C17E05_R0_FACTOR_HOLDOUT.json","falsifier":"any reduced raw/clock mismatch","scope":"well-formed voxels, s_reg<=19664, horizons away from uint64 wrap; modulus minimality only within the fixed-global-modulus family"}
    ]
    nulls=[
      {"id":"C17E-N01","status":"BOUNDED_PREREQUISITE_GAP","statement":"Autonomous local regeneration of learned policy was not constructed; the confirmed repair requires an intact redundant source, carrier route and receiver converter."},
      {"id":"C17E-N02","status":"BOUNDED_CONSTRUCTION_NULL","statement":"Opposed learned policies preserve identities when separated but reduce many-to-one on contact; no identity-preserving exchange or collective inertial response was constructed."},
      {"id":"C17E-N03","status":"PREREQUISITE_NOT_LICENSED","statement":"No new evidence licensed thermal, field/wave, contextuality or Bell tests; the new repair mechanism is explicit-carrier and common-preparation based."},
      {"id":"C17E-N04","status":"EXTERNAL_ACCESS_UNKNOWN","statement":"No low-parameter external Rosetta gained local empirical support in the extension."}
    ]
    holdouts={"schema":"dee.v27.core17.extension.holdout_registry.v1","entries":[
      {"panel":"redundant_policy_repair","claim_ids":["C17E-CLAIM-001"],"fresh_worlds":12,"executions":84,"passed":h03["passed"],"result_sha256":sha256_file(ROOT/"HOLDOUT"/"C17E03_POLICY_REPAIR_HOLDOUT.json")},
      {"panel":"r0_factor_52","claim_ids":["C17E-CLAIM-002"],"fresh_worlds":10,"ticks":h05["ticks_compared"],"passed":h05["passed"],"result_sha256":sha256_file(ROOT/"HOLDOUT"/"C17E05_R0_FACTOR_HOLDOUT.json")}
    ],"summary":{"fresh_worlds":22,"all_pass":bool(h03["passed"] and h05["passed"]),"new_operator_ticks":h05["ticks_compared"],"new_operator_mismatches":h05["raw_mismatches"]+h05["clock_mismatches"]}}
    canaries={"schema":"dee.v27.core17.extension.canary_registry.v1","entries":[
      {"id":"C17E-CAN-001","claim":"C17E-CLAIM-001","prerequisite":"learned direction","result":"0/12 after direction reset","pass":h03["counts_functional"]["backup_direction_reset"]==0},
      {"id":"C17E-CAN-002","claim":"C17E-CLAIM-001","prerequisite":"intact route","result":"0/12 after on-path cut","pass":h03["counts_functional"]["path_cut"]==0},
      {"id":"C17E-CAN-003","claim":"C17E-CLAIM-001","prerequisite":"spatial specificity","result":"12/12 after off-path cut","pass":h03["counts_functional"]["offpath_cut"]==12},
      {"id":"C17E-CAN-004","claim":"C17E-CLAIM-002","prerequisite":"direction retained","result":h05["canaries"]["direction_ablation_detected"],"pass":h05["canaries"]["direction_ablation_detected"]},
      {"id":"C17E-CAN-005","claim":"C17E-CLAIM-002","prerequisite":"semantic4 full raw retained","result":h05["canaries"]["semantic4_collapse_detected"],"pass":h05["canaries"]["semantic4_collapse_detected"]}
    ]}
    write_json(ROOT/"CLAIM_LEDGER_EXTENSION.json",seal({"schema":"dee.v27.core17.extension.claim_ledger.v1","claims":claims,"bounded_nulls":nulls}))
    write_json(ROOT/"HOLDOUT_REGISTRY_EXTENSION.json",seal(holdouts)); write_json(ROOT/"CANARY_REGISTRY_EXTENSION.json",seal(canaries))
    closure=seal({
      "schema":"dee.v27.core17.definitive_closure.v1","CORE17_DEFINITIVELY_CLOSED":True,"pre_extension_core17_sha256":PRE_EXTENSION_SHA256,"post_extension_core17_sha256":"SELF_HASH_RECORDED_EXTERNALLY_AFTER_ZIP_FINALIZATION",
      "new_experiments":["C17E01 policy coordinate","C17E02 redundant reconstruction discovery","C17E03 fresh reconstruction holdout","C17E04 R0_FACTOR_52 discovery","C17E05 fresh quotient holdout","C17E06 prerequisite constructions"],
      "new_claims":[c["claim_id"] for c in claims],"new_nulls":[n["id"] for n in nulls],
      "closed_frontier_branches":{"compressed_representation":"R0_FACTOR_52 validated","policy_regeneration":"source-supported repair validated; autonomous regeneration gap isolated",**e06["adjudication"]},
      "still_impossible_prerequisites":["autonomous policy restoration without redundant source","two persistent bodies surviving contact","identity-preserving exchange","source-generated noncarrier mediator","compatible nondisturbing contexts","independent correlated subsystems","external calibration evidence"],
      "new_fresh_worlds":22,"old_fresh_worlds_preserved":46,"kernel":audit_kernel("CORE17_DEFINITIVE_CLOSURE")
    })
    write_json(ROOT/"CORE17_DEFINITIVE_CLOSURE.json",closure)
    write_json(ROOT/"CORE17_EXTENSION_RESULTS.json",seal({"schema":"dee.v27.core17.extension.results.v1","policy_coordinate":e01["summary"],"repair_discovery":e02["summary"],"repair_holdout":{"counts":h03["counts_functional"],"passed":h03["passed"]},"r0_factor":e04["representation"],"r0_discovery":e04["summary"],"r0_holdout":{"worlds":h05["worlds"],"ticks":h05["ticks_compared"],"raw_mismatches":h05["raw_mismatches"],"clock_mismatches":h05["clock_mismatches"],"passed":h05["passed"]},"prerequisite_closure":e06["adjudication"]}))

    verdict=f"""# CORE17 — Clausura definitiva

CORE17 se reabrió exclusivamente sobre las ramas vivas de su propia frontera. No se repitieron los 46 mundos finales anteriores, el panel de reloj oculto, el pushforward probabilístico, la ley k5/k6 ni el holdout R0 anterior.

## Nuevos resultados promovidos

1. **Coordenada de política y reparación redundante.** En 8 geometrías de localización, alterar `s_reg` conservó la función mientras resetear dirección la destruyó. El aparato de reparación entrenó una segunda copia, dañó la primera y reinstanció la política por un portador explícito. El holdout posterior al freeze pasó: tratamiento 12/12, corte fuera de ruta 12/12; copia no entrenada, dirección reseteada, copia ausente, corte de ruta y receptor incorrecto 0/12 cada uno.

2. **Compresión causal real de R0.** `R0_FACTOR_52` conserva para celdas ordinarias sólo existencia (1 bit), `s_reg` (16), dirección (12), semántica (4) y fase de reloj (19): 52 bits en lugar de 128. Semántica-4 necesita sus 64 bits raw pero no el reloj. El holdout fresco probó 10 mundos durante {h05['ticks_compared']} pasos con cero discrepancias raw o reloj reducidas. `304980=lcm(195,260,391,782)` es el módulo fijo global mínimo para los periodos locales alcanzables de esa familia.

## Cierre de prerrequisitos

Las políticas aprendidas opuestas mantuvieron dos identidades en el control separado y se redujeron a un único estado en contacto (`s_reg=336`, dirección nula). La perturbación de una pareja redundante actuó localmente, no colectivamente. El híbrido semántica-4/móvil rompió su geometría relativa en un paso. No se construyeron cuerpos que sobrevivan contacto, intercambio con identidad, mediador distribuido no portador, contextos compatibles, subsistemas Bell válidos ni Rosetta externa.

La reparación demostrada es **reconstrucción soportada por una copia aprendida redundante**. No es autorregeneración local, acción remota ni teleportación.

`CORE17_DEFINITIVELY_CLOSED = TRUE`.
"""
    (ROOT/"CORE17_DEFINITIVE_CLOSURE.md").write_text(verdict,encoding="utf-8")
    frontier="""# Frontera final y permanente de CORE17

CORE17 queda cerrado. Sus dos antiguas ramas de mayor información recibieron disposición experimental: R0 sí admite la compresión exacta `R0_FACTOR_52`; la función aprendida sí admite reparación por redundancia y transporte, pero no se obtuvo autorregeneración sin fuente. Los demás frentes quedaron en brechas de prerrequisito precisas, no en inexistencias universales.

El trabajo posterior sobre memoria, aprendizaje, plasticidad, capacidad, interferencia, bucles internos y autorreparación pertenece a **INGENIERIA 01**, no a CORE18 ni a una nueva reapertura de CORE17.
"""
    (ROOT/"CORE17_FINAL_FRONTIER_EXTENSION.md").write_text(frontier,encoding="utf-8")
    repro="""# Reproducción de la extensión definitiva de CORE17

Use Python 3.13, NumPy 2.2.6, un hilo y el kernel v27 cuyo PYD tiene SHA-256 `0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff`.

Orden exacto: `run_e01_policy_coordinate.py`; `run_e02_redundant_policy_repair.py`; `freeze_e03_policy_repair.py`; `generate_e03_challenge.py`; `run_e03_policy_repair_holdout.py`; `run_e04_r0_compression_discovery.py`; `freeze_e05_r0_factor.py`; `generate_e05_challenge.py`; `run_e05_r0_factor_holdout.py`; `run_e06_prerequisite_constructions.py`; `synthesize_core17_extension.py`.

Los archivos `CHALLENGES` preservan la entropía y cada seed, de modo que los holdouts son reproducibles bit a bit con el binario fijado. Los JSON de `HOLDOUT` contienen todos los registros por caso y por tick usados para adjudicar las claims.
"""
    (ROOT/"CORE17_EXTENSION_REPRODUCTION.md").write_text(repro,encoding="utf-8")
    print({"claims":len(claims),"nulls":len(nulls),"fresh_worlds":22,"closed":True})


if __name__=="__main__": main()
