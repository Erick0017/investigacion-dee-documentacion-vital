from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "provenance" / "core10_minimal" / "RUNNERS"
sys.path.insert(0, str(SOURCE))

from core10_common import sha256_file, verify_and_load_kernel
from core10_apparatus import run_learned_policy_transfer


def main() -> int:
    kernel, environment = verify_and_load_kernel(1)
    modes = ("trained", "untrained", "corridor_cut", "receiver_none")
    cases = []
    for offset, mode in enumerate(modes):
        cases.append(run_learned_policy_transfer(
            kernel, 312000 + offset, 29, 6, mode, (0, 1, 2), (1, 1, 1)))
    by_mode = {case["mode"]: case for case in cases}
    gates = {
        "trained_positive": bool(by_mode["trained"]["functional_policy_reinstantiated"]),
        "trained_source_depleted": bool(by_mode["trained"]["source_depleted_after_launch"]),
        "trained_corridor_observed": bool(
            by_mode["trained"]["corridor_all_intermediate_ticks_observed"]),
        "untrained_negative": not bool(by_mode["untrained"]["functional_policy_reinstantiated"]),
        "corridor_cut_negative": not bool(
            by_mode["corridor_cut"]["functional_policy_reinstantiated"]),
        "receiver_none_negative": not bool(
            by_mode["receiver_none"]["functional_policy_reinstantiated"]),
    }
    historical = ROOT / "provenance" / "core10_minimal" / "C10H02_HISTORICAL_RESULT.json"
    lock = ROOT / "provenance" / "core10_minimal" / "C10H02_LOCK.json"
    result = {
        "schema": "mbp3.c10h02-minimal-revalidation.v1",
        "classification": "PROBADO_EN_v27_REVALIDACION_MINIMA_LOCAL",
        "verdict": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "domain": {"N": 29, "distance": 6, "frame": {"permutation": [0, 1, 2],
                                                               "signs": [1, 1, 1]}},
        "modes": list(modes),
        "kernel_environment": environment,
        "historical_result_sha256": sha256_file(historical),
        "holdout_lock_sha256": sha256_file(lock),
        "cases": cases,
        "integration_decision": "not installed in MAIN; retained as independently revalidated native phenomenon",
        "identity_limits": {
            "source_material_continuity": False,
            "microscopic_identity": False,
            "discontinuous_remote_effect": False,
            "class": "destructive functional reinstantiation through a causal corridor",
        },
    }
    output = ROOT / "validation" / "C10H02_MINIMAL_REVALIDATION.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps({"output": str(output), "verdict": result["verdict"],
                      "gates": gates}, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
