from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXPECTED = {
    "DOSE_0": (23, 4172, 4177, 4180, 0),
    "DOSE_1": (24, 4173, 4178, 4181, 1),
    "DOSE_2_EARLY": (25, 4174, 4179, 4182, 2),
    "DOSE_2_LATE": (25, 4174, 4179, 4182, 2),
    "DOSE_4": (27, 4176, 4181, 4184, 4),
    "PHASE_CUT": (23, 4172, 4177, 4180, 0),
    "HOLDOUT_DOSE_0": (23, 4172, 4181, 4185, 0),
    "HOLDOUT_DOSE_4": (27, 4176, 4185, 4189, 4),
}


def read_one(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    panel = args.root / "results" / "panel_final"
    rows = {row["case_id"]: row for row in read_one(panel / "case_summary.csv")}
    checks: dict[str, bool] = {}
    checks["all_expected_cases_present"] = set(EXPECTED).issubset(rows)
    checks["all_inputs_admitted"] = all(
        row["requested_inputs"] == row["admitted_inputs"]
        and row["rejected_inputs"] == "0"
        for row in rows.values()
    )
    checks["pre_learning_common"] = all(
        rows[name]["q1_before"] == "4149" for name in EXPECTED
    )
    checks["frozen_predictions"] = all(
        (
            int(rows[name]["carrier_redirect"]),
            int(rows[name]["revision1"]),
            int(rows[name]["q2_use1"]),
            int(rows[name]["q3_use2"]),
            int(rows[name]["overflows"]),
        )
        == values
        for name, values in EXPECTED.items()
    )
    checks["phase_cut_matches_dose_zero"] = all(
        rows["PHASE_CUT"][field] == rows["DOSE_0"][field]
        for field in ("carrier_redirect", "revision1", "q2_use1", "q3_use2")
    )
    checks["early_late_dose_two_converge"] = all(
        rows["DOSE_2_EARLY"][field] == rows["DOSE_2_LATE"][field]
        for field in ("carrier_redirect", "revision1", "q2_use1", "q3_use2")
    )
    checks["holdout_preserves_four_unit_contrast"] = (
        int(rows["HOLDOUT_DOSE_4"]["q2_use1"])
        - int(rows["HOLDOUT_DOSE_0"]["q2_use1"])
        == 4
        and int(rows["HOLDOUT_DOSE_4"]["q3_use2"])
        - int(rows["HOLDOUT_DOSE_0"]["q3_use2"])
        == 4
    )
    checks["unpaired_control_records_path_loss"] = (
        rows["UNPAIRED_SAME_INVENTORY"]["carrier_redirect"] == "0"
        and rows["UNPAIRED_SAME_INVENTORY"]["q2_use1"] == "5"
        and rows["UNPAIRED_SAME_INVENTORY"]["q3_use2"] == "3"
    )

    backend = read_one(panel / "backend_equivalence.csv")[0]
    checks["lazy_dense_parallel_raw_clock_exact"] = all(
        backend[field] == "1"
        for field in (
            "lazy_vs_dense_raw",
            "lazy_vs_dense_clock",
            "lazy_vs_parallel_raw",
            "lazy_vs_parallel_clock",
        )
    )
    checks["prediction_mismatch_log_empty"] = (
        panel.joinpath("prediction_mismatches.txt").stat().st_size == 0
    )

    resume = read_one(args.root / "results" / "checkpoint_new_process_resume.csv")[0]
    checks["new_process_resume_exact"] = (
        resume["holdout_use1"] == "4185"
        and resume["holdout_use2"] == "4189"
        and resume["raw_exact"] == "1"
        and resume["clock_exact"] == "1"
    )
    checks["learned_checkpoint_present"] = (
        args.root / "checkpoints" / "learned_dose4_t40.deetsnap"
    ).is_file()

    result = {
        "campaign": "entrega03.native_learning.v1",
        "status": "VERIFIED" if all(checks.values()) else "FAILED",
        "checks": checks,
        "case_count": len(rows),
        "kernel_modified": False,
        "baseline_product": "DEE thinking 2.2.0",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

