#pragma once

#include "dee_thinking/observation.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace dee::thinking::genealogy {

struct TrackedSite {
    std::string id;
    Coordinate site;
};

struct TraceFrame {
    std::uint64_t tick{};
    std::vector<::dee::thinking::Observation> observations;
};

struct TraceTransition {
    std::uint64_t tick_before{};
    std::uint64_t tick_after{};
    std::vector<std::string> ids;
    std::vector<observation::SiteTransition> changes;
    std::string scope{"DECLARED_SITES_ONLY"};
};

class PassiveTracker {
public:
    explicit PassiveTracker(std::vector<TrackedSite> sites,
                            std::size_t frame_budget = 4096);

    [[nodiscard]] TraceFrame capture(const Runtime& runtime);
    [[nodiscard]] const std::vector<TraceTransition>& transitions() const noexcept {
        return transitions_;
    }
    [[nodiscard]] const std::vector<TraceFrame>& frames() const noexcept { return frames_; }
    [[nodiscard]] std::size_t frame_budget() const noexcept { return frame_budget_; }
    [[nodiscard]] bool capture_stopped() const noexcept { return capture_stopped_; }
    void clear_trace();

private:
    std::vector<TrackedSite> sites_;
    std::size_t frame_budget_{};
    bool capture_stopped_{};
    std::vector<TraceFrame> frames_;
    std::vector<TraceTransition> transitions_;
};

}  // namespace dee::thinking::genealogy
