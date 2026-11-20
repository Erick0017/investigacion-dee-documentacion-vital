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
// Canonical name: CORE06 C6H01 initial relational learning.
[[nodiscard]] ReferenceWorld make_relational_learning_world();
// Compatibility alias retained from Entrega 01; it does not implement C7H03.
[[nodiscard]] ReferenceWorld make_reprogramming_world();
[[nodiscard]] ReferenceWorld make_history_world(HistoryMode mode);
[[nodiscard]] ReferenceWorld make_recurrence_multichannel_world(HistoryMode mode = HistoryMode::HA);

}  // namespace dee::thinking
