#pragma once

#include "dee_thinking/runtime.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking::observation {

struct LocalSite {
    Coordinate offset;
    Coordinate site;
    std::uint64_t raw{};
    std::uint64_t clock{};
    v27::Record record{};
    bool raw_present{};
    bool active_for_rule{};
};

struct WriteGate {
    Coordinate site;
    std::uint64_t absolute_tick{};
    std::uint64_t local_clock{};
    v27::Record center{};
    bool center_available{};
    int n_active{};
    Direction direction_sum{};
    std::optional<int> tetra_pattern;
    bool hadron{};
    int rule_value{};
    bool survives_material_rule{};
    bool semantic_protected{};
    bool write_protected{};
    int k{};
    std::optional<int> period;
    std::optional<std::uint64_t> phase_remainder;
    bool ordinary_increment_condition{};
    std::string branch;
    std::string demux_status{"UNRESOLVED_FROM_PASSIVE_PRESTATE"};
    std::vector<LocalSite> neighbors;
};

struct SiteTransition {
    Coordinate site;
    std::uint64_t tick_before{};
    std::uint64_t tick_after{};
    std::uint64_t raw_before{};
    std::uint64_t raw_after{};
    std::uint64_t clock_before{};
    std::uint64_t clock_after{};
    std::vector<std::string> changed_fields;
    std::string classification;
};

[[nodiscard]] WriteGate inspect_write_gate(const Runtime& runtime, Coordinate site,
                                           bool include_neighbors = true);
[[nodiscard]] SiteTransition compare_site(const Runtime& before, const Runtime& after,
                                          Coordinate site);

}  // namespace dee::thinking::observation
