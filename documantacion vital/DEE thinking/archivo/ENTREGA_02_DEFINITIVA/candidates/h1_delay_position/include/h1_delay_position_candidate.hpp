#pragma once

#include "dee_thinking/kernel_v27.hpp"
#include "dee_thinking/runtime.hpp"

#include <array>
#include <cstdint>
#include <optional>
#include <vector>

namespace dee::thinking::candidates::h1 {

inline constexpr const char* kCandidateId = "delay_position_bank.core05.nrh05.candidate.v1";
inline constexpr const char* kConstructorVersion = "0.1.1-candidate";

enum class Arm : std::uint8_t { Native = 0, ReversedCalibration = 1, TargetAbsent = 2 };

struct Config {
    int dimension{59};
    Coordinate base{13, 17, 19};
    Direction separation{0, 1, 0};
    int channel_spacing{5};
    int base_path_length{12};
    std::vector<int> labels{-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5};
    Direction target_direction{1, 0, 0};
    Direction probe_direction{0, 0, 1};
    int input_delta{};
    Arm arm{Arm::Native};
    std::array<std::uint16_t, 2> sregs{321, 654};
    std::array<std::uint32_t, 2> states{1001, 2003};
    std::array<std::uint64_t, 2> clocks{0x123456789abcdef0ULL, 0xfedcba9876543210ULL};
};

struct DetectionEvent {
    std::uint64_t tick{};
    int label{};
    v27::Record record{};
};

struct RunResult {
    bool initial_hubs_empty{};
    std::optional<int> measurement;
    std::vector<int> active_labels;
    std::vector<DetectionEvent> merged_events;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] RunResult run(const Config& config,
                            v27::TickOptions options = {v27::Backend::DenseSequential, 1});

}  // namespace dee::thinking::candidates::h1
