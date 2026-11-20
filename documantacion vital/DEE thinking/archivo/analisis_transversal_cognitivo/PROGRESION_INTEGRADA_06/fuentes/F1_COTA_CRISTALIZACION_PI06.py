"""Static, stdlib-only source bound; never imports or executes DEE.

Run with --source <official kernel_v27.cpp> --out <new result.json>.
The result is a proof about the identified source, not a measured binary result.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import re


def calculate(source: Path) -> dict:
    data = source.read_bytes()
    text = data.decode("utf-8-sig")
    lines = text.splitlines()
    k_literal = re.search(r"constexpr double K_LIMIT\s*=\s*([\d.]+)\s*;", text).group(1)
    p = int(re.search(r"constexpr uint64_t P_KERNEL\s*=\s*(\d+)ULL\s*;", text).group(1))
    body = re.search(r"MOORE_DXYZ\[26\]\[3\]\s*=\s*\{(.*?)\};", text, re.S).group(1)
    offsets = [tuple(map(int, v)) for v in re.findall(r"\{\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\}", body)]
    expected = set(itertools.product((-1, 0, 1), repeat=3)) - {(0, 0, 0)}
    assert len(offsets) == 26 and set(offsets) == expected
    needed = [
        "static inline uint16_t get_s_reg(uint64_t v) { return (uint16_t)((v >> SHIFT_SREG) & 0xFFFFULL); }",
        "int grad_x = 0, grad_y = 0, grad_z = 0;",
        "int s_v = (int)get_s_reg(nv);",
        "grad_x -= MOORE_DXYZ[k_v][0] * s_v;",
        "grad_y -= MOORE_DXYZ[k_v][1] * s_v;",
        "grad_z -= MOORE_DXYZ[k_v][2] * s_v;",
        "int grad_mag = std::abs(grad_x) + std::abs(grad_y) + std::abs(grad_z);",
        "if (tiene_vecino_vivo && (grad_mag / P_KERNEL) >= UMBRAL_CRISTALIZACION && !hay_vecino_orphan) {",
        "static constexpr int UMBRAL_CRISTALIZACION = (int)(K_LIMIT * K_LIMIT * K_LIMIT);",
    ]
    for value in needed:
        assert value in text, "Source differs at proof dependency: " + value
    max_sreg = (1 << 16) - 1
    conservative_axis = len(offsets) * max_sreg
    conservative_l1 = 3 * conservative_axis
    exact_decimal_cube = Decimal(k_literal) ** 3
    threshold = int(exact_decimal_cube)
    # ||g||_1 = max_u u.g. Nonnegative independent charges can occupy all
    # offsets with positive projection for that sign vector. exists() can
    # only remove terms, so this also bounds the actual filtered sum.
    sign_weights = {
        str(u): sum(max(sum(u[a] * d[a] for a in range(3)), 0) for d in offsets)
        for u in itertools.product((-1, 1), repeat=3)
    }
    sharp_l1 = max(sign_weights.values()) * max_sreg
    excerpts = []
    for first, last in [(26, 36), (64, 70), (99, 100), (248, 301), (311, 320)]:
        excerpts.append({"first_line": first, "last_line": last,
                         "text": "\n".join(lines[first - 1:last])})
    return {
        "schema": "DEE.PI06.static_crystallization_bound.v1",
        "mode": "STATIC_SOURCE_RECALCULATION_ONLY",
        "source": {"path": str(source.resolve()), "bytes": len(data),
                   "sha256": hashlib.sha256(data).hexdigest(), "excerpts": excerpts},
        "domain": {"raw_word": "uint64_t", "sreg_getter": "uint16_t, mask 0xFFFF",
                   "sreg_min": 0, "sreg_max": max_sreg,
                   "gradient_accumulators": "int", "assumed_int_bits": 32,
                   "abi_scope": "Windows x64 C++ int32; mathematical source proof under this ABI",
                   "neighbourhood": "26 Moore offsets, each coordinate -1/0/+1",
                   "exists_filter": "May omit contributions; cannot increase the stated bound",
                   "N_scope": "Any positive valid N; wrap/alias does not exceed26 loop contributions"},
        "constants": {"K_LIMIT_literal": k_literal, "decimal_cube": str(exact_decimal_cube),
                      "threshold_cast": threshold, "P_KERNEL_uint64": p,
                      "floating_point_note": "966.481627103 is far from an integer boundary; ordinary IEEE double rounding does not change cast966."},
        "proof": {"per_term_abs_max": max_sreg,
                  "conservative_axis_abs_max": conservative_axis,
                  "conservative_l1_max": conservative_l1,
                  "conservative_integer_quotient_max": conservative_l1 // p,
                  "threshold_times_divisor": threshold * p,
                  "int32_signed_overflow_possible_in_bound": conservative_l1 > (1 << 31) - 1,
                  "sharper_moore_sign_weights": sign_weights,
                  "sharper_l1_max": sharp_l1,
                  "sharper_integer_quotient_max": sharp_l1 // p,
                  "necessary_test_can_be_true": conservative_l1 // p >= threshold,
                  "deduction": "The source branch at line301 cannot be reached by any valid16-bit sreg neighbourhood under the stated ABI."},
        "limitations": [
            "Not a binary execution, disassembly, compiler-equivalence or empirical test.",
            "Does not apply without checking the same constants/types to other historical kernels.",
            "Does not rule out XNOR genesis, directed-source demux, material evolution, clock effects or other kinds of organization.",
            "No claim of general impossibility of memory, learning, recovery or self-organization."
        ],
        "native_ticks_executed": 0,
        "binary_measurement": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.out.exists():
        raise SystemExit("Refusing to overwrite an existing proof")
    result = calculate(a.source)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(a.out), "source_sha256": result["source"]["sha256"],
                      "bound": result["proof"]["conservative_l1_max"],
                      "quotient": result["proof"]["conservative_integer_quotient_max"],
                      "threshold": result["constants"]["threshold_cast"],
                      "test_can_be_true": result["proof"]["necessary_test_can_be_true"]}))


if __name__ == "__main__":
    main()
