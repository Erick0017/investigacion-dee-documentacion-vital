#include "dee_thinking/observation.hpp"

#include <array>
#include <cmath>
#include <stdexcept>

namespace dee::thinking::observation {
namespace {

constexpr std::array<Coordinate, 26> kMoore{{
    {-1,-1,-1},{-1,-1,0},{-1,-1,1},{-1,0,-1},{-1,0,0},{-1,0,1},{-1,1,-1},{-1,1,0},{-1,1,1},
    {0,-1,-1},{0,-1,0},{0,-1,1},{0,0,-1},{0,0,1},{0,1,-1},{0,1,0},{0,1,1},
    {1,-1,-1},{1,-1,0},{1,-1,1},{1,0,-1},{1,0,0},{1,0,1},{1,1,-1},{1,1,0},{1,1,1}
}};

constexpr std::array<std::array<Coordinate, 4>, 8> kTetra{{
    std::array<Coordinate,4>{{{1,0,0},{0,1,0},{0,0,1},{1,1,1}}},
    std::array<Coordinate,4>{{{-1,0,0},{0,1,0},{0,0,1},{-1,1,1}}},
    std::array<Coordinate,4>{{{1,0,0},{0,-1,0},{0,0,1},{1,-1,1}}},
    std::array<Coordinate,4>{{{1,0,0},{0,1,0},{0,0,-1},{1,1,-1}}},
    std::array<Coordinate,4>{{{-1,0,0},{0,-1,0},{0,0,1},{-1,-1,1}}},
    std::array<Coordinate,4>{{{-1,0,0},{0,1,0},{0,0,-1},{-1,1,-1}}},
    std::array<Coordinate,4>{{{1,0,0},{0,-1,0},{0,0,-1},{1,-1,-1}}},
    std::array<Coordinate,4>{{{-1,0,0},{0,-1,0},{0,0,-1},{-1,-1,-1}}},
}};

Coordinate add(Coordinate q, Coordinate d, int n) {
    return {v27::wrap_coordinate(q.x + d.x, n),
            v27::wrap_coordinate(q.y + d.y, n),
            v27::wrap_coordinate(q.z + d.z, n)};
}

bool active(const v27::Record& record) {
    return record.state > 0 && record.semantic != static_cast<std::uint8_t>(v27::Semantic::OrphanBit);
}

}  // namespace

WriteGate inspect_write_gate(const Runtime& runtime, Coordinate site,
                             bool include_neighbors) {
    WriteGate out{};
    out.site = site;
    out.absolute_tick = runtime.current_tick();
    const auto center = runtime.observe(site);
    out.local_clock = center.clock;
    out.center = center.record;
    out.center_available = center.raw != 0;
    std::array<bool, 26> alive{};
    for (std::size_t i = 0; i < kMoore.size(); ++i) {
        const auto q = add(site, kMoore[i], runtime.dimension());
        const auto observed = runtime.observe(q);
        alive[i] = active(observed.record);
        if (alive[i]) {
            ++out.n_active;
            out.direction_sum.dx += observed.record.dx;
            out.direction_sum.dy += observed.record.dy;
            out.direction_sum.dz += observed.record.dz;
        }
        if (include_neighbors) {
            out.neighbors.push_back(LocalSite{
                kMoore[i], q, observed.raw, observed.clock, observed.record,
                observed.raw != 0, alive[i]});
        }
    }
    auto is_alive_offset = [&](Coordinate offset) {
        for (std::size_t i = 0; i < kMoore.size(); ++i) {
            if (kMoore[i] == offset) return alive[i];
        }
        return false;
    };
    for (std::size_t p = 0; p < kTetra.size(); ++p) {
        bool match = true;
        for (const auto offset : kTetra[p]) match = match && is_alive_offset(offset);
        if (match) {
            out.tetra_pattern = static_cast<int>(p);
            break;
        }
    }
    out.hadron = out.tetra_pattern.has_value();
    // Keep this diagnostic calculation byte-for-byte aligned with the frozen
    // kernel's COMPLETE_CUBE_VECINOS constant.  The Moore neighbourhood has
    // 26 positions, but v27 deliberately defines the material completeness
    // threshold as seven active neighbours.
    const bool incomplete = out.n_active < 7;
    const double tension = out.hadron && incomplete ? 16.0 : 2.5;
    out.rule_value = static_cast<int>(std::floor(out.n_active * tension / 26.0 + 0.5));
    out.survives_material_rule = out.rule_value != 0;
    out.semantic_protected = out.center_available &&
        out.center.semantic == static_cast<std::uint8_t>(v27::Semantic::Observer);
    const bool symmetric = out.direction_sum.dx == 0 && out.direction_sum.dy == 0 &&
                           out.direction_sum.dz == 0;
    out.write_protected = out.n_active >= 7 && symmetric;
    out.k = 8 - out.n_active;
    if (out.k > 0 && out.k <= 8) {
        out.period = 782 / out.k;
        if (*out.period < 1) out.period = 1;
        out.phase_remainder = out.local_clock % static_cast<std::uint64_t>(*out.period);
    }
    out.ordinary_increment_condition = out.center.state > 0 &&
        !out.semantic_protected && out.rule_value != 0 && !out.write_protected &&
        out.period.has_value() && *out.phase_remainder == 0;
    if (out.semantic_protected) out.branch = "SEMANTIC4_PRESERVE";
    else if (out.center.state == 0) out.branch = "VOID_PRECEDENCE_UNRESOLVED";
    else if (out.rule_value == 0) out.branch = "MATERIAL_RULE_VALUE_ZERO";
    else if (out.write_protected) out.branch = "MATERIAL_WRITE_PROTECTED";
    else if (out.ordinary_increment_condition) out.branch = "MATERIAL_ORDINARY_INCREMENT_CONDITION";
    else out.branch = "MATERIAL_NO_ORDINARY_INCREMENT";
    return out;
}

SiteTransition compare_site(const Runtime& before, const Runtime& after,
                            Coordinate site) {
    if (before.dimension() != after.dimension()) {
        throw std::invalid_argument("transition worlds have different dimensions");
    }
    const auto a = before.observe(site);
    const auto b = after.observe(site);
    SiteTransition out{};
    out.site = site;
    out.tick_before = before.current_tick();
    out.tick_after = after.current_tick();
    out.raw_before = a.raw;
    out.raw_after = b.raw;
    out.clock_before = a.clock;
    out.clock_after = b.clock;
    if ((a.raw == 0) != (b.raw == 0)) out.changed_fields.push_back("presence");
    if (a.record.state != b.record.state) out.changed_fields.push_back("state");
    if (a.record.s_reg != b.record.s_reg) out.changed_fields.push_back("s_reg");
    if (a.record.dx != b.record.dx || a.record.dy != b.record.dy || a.record.dz != b.record.dz)
        out.changed_fields.push_back("direction");
    if (a.record.semantic != b.record.semantic) out.changed_fields.push_back("semantic");
    if (a.clock != b.clock) out.changed_fields.push_back("clock");
    out.classification = out.changed_fields.empty() ? "UNCHANGED" : "OBSERVED_CHANGE";
    return out;
}

}  // namespace dee::thinking::observation
