"""Passive synthesis of already-frozen C02 evidence. Never imports DEE."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(relative: str):
    path = ROOT / relative
    raw = path.read_bytes()
    return json.loads(raw), {
        "path_relative_R05": relative,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def main():
    dev, dev_source = source("analisis/DEV_FINAL_RECALCULO_R02/HECHOS_Y_ATRIBUCION_DEV_R02.json")
    adverse, adverse_source = source("analisis/MAIN_PRIMERA_LECCION_ADMISION_R01.json")
    base = ROOT / "fuentes/MATRIZ_REPERTORIO_BASE.csv"
    raw = base.read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(rows) != 12 or dev["final_cut"] != 953651 or adverse["actual_after_tick"] != 947852:
        raise RuntimeError("Frozen evidence identity mismatch; no synthesis written")
    statuses = {
        "01": (
            "DEV physical lesson/use observed; R01 signed revision partly rejected",
            "DEV luma- and nara+ lesson:6/6 admitted; later respective emissions -1,+1. R01 luma+/nara-:4/6 admitted,2 rejected_occupied.",
            "No new same-phase DEV prelesson baseline; paired/desync causal control not terminal at this cut.",
        ),
        "02": (
            "Specific DEV sign used after save/reopen; inherited contextual panel not repeated",
            "nara+ emitted at T950935 after reopening T950523; actual A4 was also retained as transport state. alfa context was not newly queried.",
            "A transport integer retained is not by itself Native lexical memory; do not attribute the other historical signs to a new panel.",
        ),
        "03": (
            "Historical comparison retained as base claim; no new three-sign comparison panel",
            "DEV numerical FI128 output4 and5 formed; this is not a fresh positive/negative/zero comparison test.",
            "Preserve q+4 material zero versus q+6 NULL distinction. No substitution of an arithmetic output for the inherited comparison contract.",
        ),
        "04": (
            "Two real Native calculations observed on one DEV trajectory",
            "luma- selected diferencia:6-2 produced4; nara+ selected suma:actual4+1 produced5. Both183/183 inputs admitted.",
            "2/2 are dependent opportunities in one life. FI128 arithmetic architecture and decoder are prepared, not an acquired arithmetic algorithm.",
        ),
        "05": (
            "Actual product transport and finite environmental effect observed in DEV",
            "Native A4 crossed save/reopen into B left4; actual B5 opened the code5 lock; one resource contact and inventory increment occurred.",
            "Station order, contact pipeline and sign-to-opcode codec are P0 assistance. No Native multi-step plan was demonstrated.",
        ),
        "06": (
            "Four Native query/route cycles completed in DEV",
            "8 distinct action IDs,4 feedback IDs,424 distinct admitted Native receipt IDs; observations passed fixed scalar and Q2 transducers.",
            "Scalar invertibility is not evidence Native separates its packed features. No same-information advantage over rivals has yet been established.",
        ),
        "07": (
            "Real generic consequences returned; new exclusive contingency effect unconfirmed",
            "DEV4 completed; R01 failed-preserved at its first lesson before full opportunity feedback. Matched acquisition control remains separate.",
            "Do not infer learned policy or exclusive reinforcement causation from DEV success; historical PI10 yoke limitation remains.",
        ),
        "08": (
            "No new Native plan/initiation claim",
            "Native physical events selected local actions and lexical opcodes; the host offered each opportunity and station function.",
            "Prepared recurrence, fixed movement geometry and automatic contact are not discovered exploration or self-generated task sequencing.",
        ),
        "09": (
            "No new regulation/protection result",
            "Finite resource and query/toll stock are environmental variables. R01 rejection is a measured admission failure.",
            "No subjective pain, metabolism, autonomous recovery or beneficial host RAM regulation follows from these records.",
        ),
        "10": (
            "Historical social mechanisms available; C02 has no new two-participant social proof",
            "Archive signs are visible environmental teaching; there is no independently evolving interlocutor in this DEV sequence.",
            "No general language, negotiation or transfer of other lives' social memories into DEV/MAIN.",
        ),
        "11": (
            "R01 access/admission problem localized; no recovery tested here",
            "Two revision sources [44,7,44] and [47,4,50] rejected_occupied at947782/947849. Cue and teacher pulses did apply.",
            "No memory deletion or global loss demonstrated. New R02 no-result handling is instrumentation, not Native self-repair.",
        ),
        "12": (
            "DEV full paired continuation/reopen observed; protected principal unchanged",
            "DEV947395->953651,+6256 ticks, same logical session across950523 boundary,4 completed opportunities. Principal remains REAL2 T947395 in this evidence cut.",
            "No new full inherited12/12 panel at DEV final; do not promote, merge R01/R02 futures or treat the analysis ZIP as executable state.",
        ),
    }
    extra = ["estado_C02_verificado", "evidencia_C02", "limite_C02"]
    output = ROOT / "fuentes/MATRIZ_REPERTORIO_C02_DEV4_R01.csv"
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) + extra)
        writer.writeheader()
        for row in rows:
            row.update(zip(extra, statuses[row["id"]]))
            writer.writerow(row)
    report = {
        "schema": "DEE.RBX01.C02.scientific_evidence_cut.DEV4_R01.v1",
        "inspection_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "passive synthesis of frozen primary-derived reports; no Native execution",
        "protected_principal_reference": {"life": "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01", "N": 67, "T": 947395},
        "DEV": {
            "life": dev["life_id"], "N": dev["N"], "parent_T": dev["parent_cut"], "final_T": dev["final_cut"],
            "ticks": dev["new_ticks"], "functions": dev["actual_functions"],
            "observations": dev["closed_observations"],
            "Native_contribution": dev["Native_contribution"],
            "prepared_host_contribution": dev["prepared_host_contribution"],
            "not_demonstrated": dev["not_demonstrated"],
            "decision": "Development branch only. No main adoption and no memory merger.",
        },
        "R01_adverse": {
            "life": adverse["life_id"], "operation_id": adverse["operation_id"],
            "status": adverse["Native_queue_record"]["status"],
            "before_T": adverse["actual_before_tick"], "after_T": adverse["actual_after_tick"],
            "requests": adverse["requests"], "rejected_exact_requests": adverse["rejected_exact_requests"],
            "diagnosis_demonstrated": adverse["diagnosis_demonstrated"],
            "not_demonstrated": adverse["not_demonstrated"],
            "snapshot": adverse["snapshot"], "snapshot_sha256": adverse["snapshot_sha256"],
            "historical_diagnostic_caution": "The diagnosis captured an unresolved ledger intent. Subsequent authorized close/reconciliation, if performed by Root, must be evidenced separately; this passive synthesis does not assert current transport status.",
        },
        "controls_at_cut": {
            "MEMPAIR_RESULTADO_present": (ROOT / "evidencia/CONTROL_MEMPAIR_R01/RESULTADO.json").exists(),
            "interpretation": "An absent terminal result is pending, not a negative cognitive result. No active Native DB inspected by this synthesis.",
        },
        "new_R02_candidate": {
            "life": "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02",
            "source_parent_T": 947395,
            "WorldId": "RBX01_R05_C02_R02",
            "planned_opportunities": 36, "planned_boundary": 12, "planned_reserve": [25, 36],
            "state_at_synthesis": "Prepared successor candidate; Root owns import/execution and must supply actual outcome. No result imported from R01 or DEV.",
            "partial_admission_policy": "Preserve exact receipts and primary; return formedFalse/numeric_resultNone/NO_RESULT to unchanged environmental consequence path. This is declared transport handling, not a physical memory repair.",
        },
        "sources": [dev_source, adverse_source, {"path_relative_R05": "fuentes/MATRIZ_REPERTORIO_BASE.csv", "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}],
        "coverage": "Twelve families use prior targeted source readings recorded in LOCALIZADORES_REPERTORIO_BASE.json. This cut adds complete frozen DEV function/World-derived reports and exact R01 admission diagnosis; no full Manual reread or new visual audit.",
        "subagent_native_ticks": 0,
        "operational_files_modified": False,
    }
    target = ROOT / "analisis/CORTE_CIENTIFICO_DEV4_Y_R01_PRE_R02.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path in (output, target):
        data = path.read_bytes()
        print(json.dumps({"file": str(path.relative_to(ROOT)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
