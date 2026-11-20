#pragma once

#include "dee_thinking/runtime.hpp"

#include <map>
#include <string>

namespace dee::thinking {

enum class HistoryMode { H0, HA, HB };

struct ReferenceWorld {
    Runtime runtime;
    std::map<std::string, Coordinate> landmarks;
    std::string contract;
};

[[nodiscard]] ReferenceWorld make_transport_world(bool occupied_destination = false);
[[nodiscard]] ReferenceWorld make_reprogramming_world();
[[nodiscard]] ReferenceWorld make_history_world(HistoryMode mode);
[[nodiscard]] ReferenceWorld make_recurrence_multichannel_world(HistoryMode mode = HistoryMode::HA);

}  // namespace dee::thinking
