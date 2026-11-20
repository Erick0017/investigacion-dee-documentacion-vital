"""Compare two frozen function primaries only; no DB, DEE, MCP or HTTP."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_"
OLD = ROOT / "native/MAIN/sistema/estado/servicios_locales" / (PREFIX + "MAIN") / "RBX02_NATIVE_C02/functions/6fbe0205c45a49d183107acf83c21170.json"
NEW = ROOT / "native/MAIN_R02/sistema/estado/servicios_locales" / (PREFIX + "MAIN_R02") / "RBX02_NATIVE_C02_R02/functions/ee770dce962246cc9fd754679c296cba.json"
ABSENT = {"__audit_absent_key__": True}


def differences(a, b, path=""):
    if type(a) is not type(b):
        return [{"path": path or "/", "R01": a, "R02": b}]
    if isinstance(a, dict):
        rows = []
        for key in sorted(set(a) | set(b)):
            at = path + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in a or key not in b:
                rows.append({"path": at, "R01": a.get(key, ABSENT), "R02": b.get(key, ABSENT)})
            else:
                rows.extend(differences(a[key], b[key], at))
        return rows
    if isinstance(a, list):
        rows = []
        for index in range(max(len(a), len(b))):
            at = path + "/" + str(index)
            if index >= len(a) or index >= len(b):
                rows.append({"path": at, "R01": a[index] if index < len(a) else ABSENT,
                             "R02": b[index] if index < len(b) else ABSENT})
            else:
                rows.extend(differences(a[index], b[index], at))
        return rows
    return [] if a == b else [{"path": path or "/", "R01": a, "R02": b}]


def remove_life_identity(value):
    if isinstance(value, dict):
        return {key: remove_life_identity(item) for key, item in value.items() if key != "life_id"}
    if isinstance(value, list):
        return [remove_life_identity(item) for item in value]
    return value


def material_view(primary):
    return {key: remove_life_identity(primary[key]) for key in
            ("visible_tool", "teacher_mode", "before_tick", "after_tick", "fixed_deadline_tick",
             "native_function", "requests_normalized", "Native_inputs", "prepared_order",
             "no_host_arithmetic_or_expected_value")}


def source(path):
    raw = path.read_bytes()
    return json.loads(raw), raw, {"path_relative_R05": str(path.relative_to(ROOT)),
                                 "bytes": len(raw), "sha256_before": hashlib.sha256(raw).hexdigest()}


def main():
    output = ROOT / "analisis/PRIMERA_LECCION_R01_R02_CONTRASTE_R01"
    if output.exists():
        raise ValueError("Preserve earlier comparison; new absent output required")
    old, old_raw, old_source = source(OLD)
    new, new_raw, new_source = source(NEW)
    for primary in (old, new):
        if primary["before_tick"] != 947773 or primary["after_tick"] != 947852:
            raise ValueError("Exact first material lesson interval required")
        if primary["visible_tool"] != {"kind": "LESSON", "items": [{"form": "luma", "observedSign": 1}, {"form": "nara", "observedSign": -1}]}:
            raise ValueError("Unexpected physical lesson, do not reinterpret")
    full = differences(old, new)
    material = differences(material_view(old), material_view(new))
    signatures = []
    for index, (left, right) in enumerate(zip(old["native_function"], new["native_function"])):
        signatures.append({"form": left["form"], "observed_sign": left["observed_sign"],
                           "R01_before": left["native_lesson"]["before"], "R02_before": right["native_lesson"]["before"],
                           "before_signature_equal": left["native_lesson"]["before"] == right["native_lesson"]["before"],
                           "R01_after": left["native_lesson"]["after"], "R02_after": right["native_lesson"]["after"],
                           "after_signature_equal": left["native_lesson"]["after"] == right["native_lesson"]["after"]})
    for path, original, metadata in ((OLD, old_raw, old_source), (NEW, new_raw, new_source)):
        final = path.read_bytes()
        metadata["sha256_after"] = hashlib.sha256(final).hexdigest()
        metadata["bytes_identical_before_after"] = final == original
        if final != original:
            raise RuntimeError("Frozen primary changed during comparison")
    report = {"schema": "DEE.RBX01.C02.first_lesson_physical_R01_R02.passive_contrast.R01",
              "inspection_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "Only immutable JSON primary bytes read; no active journal, SQLite, Native, HTTP or MCP",
              "sources": [old_source, new_source], "before_T": 947773, "after_T": 947852,
              "Native_lesson_ticks": 79, "material_views_equal": not material,
              "Native_receipt_rows_exact_equal_including_Native_IDs": old["requests_normalized"] == new["requests_normalized"],
              "Native_input_summary_exact_equal": old["Native_inputs"] == new["Native_inputs"],
              "Native_input_summary_R01": old["Native_inputs"], "Native_input_summary_R02": new["Native_inputs"],
              "physical_signatures": signatures, "material_differences": material,
              "all_primary_differences": full,
              "comparison_exclusions": ["Life identity life_id strings only within material view; original differing values remain in all_primary_differences.",
                                        "Top-level schema, life/context transport identity and additional R02 admission/public-output wrapper fields are recorded separately, not presented as physical changes.",
                                        "No Native input/receipt ID, channel, payload, requested/effective tick, rejection reason, RAW/clocks hash, geometry, sign or reading was dropped from the material comparison."],
              "R02_public_admission": {"input_admission_complete": new.get("input_admission_complete"),
                                       "public_tool_result": new.get("public_tool_result")},
              "interpretation_if_equal": "The recorded first lesson has identical physical execution and admission outcomes through T947852. R02 changes how the known terminal admission result is transported; later feedback may then change the physical future. This does not assert equality after feedback or repair/recovery of word content.",
              "subagent_native_ticks": 0}
    output.mkdir()
    (output / "CONTRASTE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "TODAS_DIFERENCIAS.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("path", "R01", "R02")); writer.writeheader()
        for row in full:
            writer.writerow({"path": row["path"], "R01": json.dumps(row["R01"], ensure_ascii=False, sort_keys=True),
                             "R02": json.dumps(row["R02"], ensure_ascii=False, sort_keys=True)})
    print(json.dumps({"output": str(output.relative_to(ROOT)), "material_equal": not material,
                      "Native_receipts_including_IDs_equal": report["Native_receipt_rows_exact_equal_including_Native_IDs"],
                      "physical_signatures_equal": all(row["before_signature_equal"] and row["after_signature_equal"] for row in signatures),
                      "full_difference_count": len(full), "material_difference_count": len(material),
                      "R02_public": report["R02_public_admission"], "source_hashes": [row["sha256_before"] for row in report["sources"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
