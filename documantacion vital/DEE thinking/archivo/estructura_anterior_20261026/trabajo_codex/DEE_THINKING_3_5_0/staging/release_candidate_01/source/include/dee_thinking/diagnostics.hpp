#pragma once

#include "dee_thinking/basal.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace dee::thinking::diagnostics {

struct AppliedEdit {
    Coordinate site;
    std::string label;
    std::uint64_t raw_before{};
    std::uint64_t raw_after{};
    std::uint64_t clock_before{};
    std::uint64_t clock_after{};
    bool raw_changed{};
    bool clock_changed{};
    bool touches_declared_support{};
};

struct Comparison {
    std::uint64_t parent_tick{};
    std::uint64_t horizon{};
    std::vector<AppliedEdit> edits;
    std::size_t raw_different_sites{};
    std::size_t clock_different_sites{};
    basal::Observation reference_observation;
    basal::Observation diagnostic_observation;
    bool parent_unchanged{};
    std::string modality{"DIAGNOSTIC_FORK"};
};

[[nodiscard]] Comparison compare_fork(
    const basal::World& parent,
    const std::vector<ResearchStateEdit>& edits,
    std::uint64_t horizon,
    bool authorize_diagnostic_intervention);

}  // namespace dee::thinking::diagnostics
