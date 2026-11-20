#pragma once

#include "dee_thinking/kernel_v27.hpp"
#include "dee_thinking/runtime.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace dee::thinking::candidates::h2 {

inline constexpr const char* kCandidateId = "destination_repertoires.core07.c7h02.candidate.v1";
inline constexpr const char* kConstructorVersion = "0.1.1-candidate";

struct SeparatedConfig {
    int dimension{79};
    std::size_t channels{3};
    Coordinate translation{2, 5, 7};
    std::uint16_t base_offset{4096};
    std::vector<int> delta_cycle{-6, -3, 1, 4, 8};
    std::uint16_t query_base{151};
    int training_tick{5};
    int query_tick{19};
    int query_path{5};
};

struct SeparatedResult {
    bool ports_empty{};
    std::size_t exact_channels{};
    bool all_exact{};
    bool training_budget_exact{};
    bool read_budget_exact{};
    bool sreg_accounting_exact{};
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

struct OverlapConfig {
    int dimension{71};
    int index{};
    std::array<int, 2> deltas{-5, 2};
    std::uint16_t query{17};
    bool off_fiber{};
    std::uint16_t base_offset{4096};
    int training_tick{5};
    int merge_tick{14};
    int query_tick{22};
};

struct OverlapResult {
    bool port_empty{};
    bool merge_exact{};
    bool composed_response_exact{};
    bool individual_identity{};
    bool false_merge{};
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] SeparatedResult run_separated(
    const SeparatedConfig& config,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
[[nodiscard]] OverlapResult run_overlap(
    const OverlapConfig& config,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});

}  // namespace dee::thinking::candidates::h2
