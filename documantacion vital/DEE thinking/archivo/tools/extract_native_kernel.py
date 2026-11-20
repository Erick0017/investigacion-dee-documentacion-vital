#!/usr/bin/env python3
"""Mechanically extract the pure v27 rule from the frozen pybind source.

Development-only tool. The generated C++ product does not load Python or the
extension module. The source SHA-256 is checked before extraction.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPECTED = "44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: extract_native_kernel.py SOURCE OUTPUT")
    source, output = map(Path, sys.argv[1:])
    payload = source.read_bytes()
    observed = hashlib.sha256(payload).hexdigest()
    if observed != EXPECTED:
        raise SystemExit(f"source hash mismatch: {observed}")
    text = payload.decode("utf-8")
    marker = "// =========================================================================\n// SECCION 8: tick_universo"
    if marker not in text:
        raise SystemExit("expected section marker not found")
    pure = text.split(marker, 1)[0]
    pure = pure.replace("#include <pybind11/pybind11.h>\n", "")
    pure = pure.replace("#include <pybind11/numpy.h>\n", "")
    pure = pure.replace("#include <pybind11/stl.h>\n", "")
    pure = pure.replace("namespace py = pybind11;\n", "")
    include_anchor = "#include <string>\n"
    pure = pure.replace(include_anchor, include_anchor + '#include "dee_thinking/kernel_v27.hpp"\n#include <stdexcept>\n\nnamespace dee::v27 {\n')
    appendix = r'''

std::uint64_t pack_record(std::uint32_t state, std::uint16_t s_reg,
                          int dx, int dy, int dz, std::uint8_t semantic) {
    return pack_voxel(state, s_reg, dx, dy, dz, semantic);
}

Record decode_record(std::uint64_t raw) noexcept {
    return Record{raw, get_estado(raw), get_s_reg(raw),
                  static_cast<std::int8_t>(get_dir_x(raw)),
                  static_cast<std::int8_t>(get_dir_y(raw)),
                  static_cast<std::int8_t>(get_dir_z(raw)), get_sem(raw)};
}

std::size_t linear_index(int x, int y, int z, int n) {
    if (n <= 0 || x < 0 || y < 0 || z < 0 || x >= n || y >= n || z >= n) {
        throw std::out_of_range("DEE coordinate outside world");
    }
    return idx3d(x, y, z, n);
}

int wrap_coordinate(int value, int n) {
    if (n <= 0) throw std::invalid_argument("DEE dimension must be positive");
    return wrap(value, n);
}

TickInfo tick(std::vector<std::uint64_t>& gA,
              std::vector<std::uint64_t>& gB,
              std::vector<std::uint64_t>& clockA,
              std::vector<std::uint64_t>& clockB,
              int n) {
    if (n <= 0) throw std::invalid_argument("DEE dimension must be positive");
    const std::size_t nn = static_cast<std::size_t>(n);
    if (nn > SIZE_MAX / nn || nn * nn > SIZE_MAX / nn) {
        throw std::overflow_error("DEE dimension overflow");
    }
    const std::size_t total = nn * nn * nn;
    if (gA.size() != total || gB.size() != total ||
        clockA.size() != total || clockB.size() != total) {
        throw std::invalid_argument("DEE buffer size mismatch");
    }
    std::vector<std::atomic<std::uint32_t>> delta_demux(total);
    for (auto& item : delta_demux) item.store(0, std::memory_order_relaxed);
    std::atomic<std::uint64_t> overflow_count(0);
    std::atomic<std::uint64_t> genesis_count(0);
    for (int x = 0; x < n; ++x) {
        for (int y = 0; y < n; ++y) {
            for (int z = 0; z < n; ++z) {
                actualizar_voxel(gA.data(), clockA.data(), gB.data(), clockB.data(),
                                  delta_demux.data(), &overflow_count, &genesis_count,
                                  x, y, z, n);
            }
        }
    }
    aplicar_demux(gB.data(), delta_demux.data(), total);
    std::memcpy(gA.data(), gB.data(), total * sizeof(std::uint64_t));
    std::memcpy(clockA.data(), clockB.data(), total * sizeof(std::uint64_t));
    return TickInfo{overflow_count.load(), genesis_count.load(),
                    static_cast<std::uint64_t>(total)};
}

}  // namespace dee::v27
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(pure + appendix, encoding="utf-8", newline="\n")
    print(f"generated {output} from {source} sha256={observed}")


if __name__ == "__main__":
    main()
