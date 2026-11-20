#include "dee_thinking/genealogy.hpp"

#include <stdexcept>
#include <utility>

namespace dee::thinking::genealogy {
namespace {

observation::SiteTransition compare_observations(
    const ::dee::thinking::Observation& a,
    const ::dee::thinking::Observation& b) {
    observation::SiteTransition out{};
    out.site = a.coordinate;
    out.tick_before = a.tick;
    out.tick_after = b.tick;
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

}  // namespace

PassiveTracker::PassiveTracker(std::vector<TrackedSite> sites,
                               std::size_t frame_budget)
    : sites_(std::move(sites)), frame_budget_(frame_budget) {
    if (sites_.empty()) throw std::invalid_argument("tracker requires at least one site");
    if (frame_budget_ == 0) throw std::invalid_argument("tracker frame budget must be positive");
    for (std::size_t i = 0; i < sites_.size(); ++i) {
        if (sites_[i].id.empty()) throw std::invalid_argument("tracked site id is empty");
        for (std::size_t j = 0; j < i; ++j) {
            if (sites_[i].id == sites_[j].id) throw std::invalid_argument("duplicate tracked site id");
        }
    }
}

TraceFrame PassiveTracker::capture(const Runtime& runtime) {
    TraceFrame frame{};
    frame.tick = runtime.current_tick();
    std::vector<Coordinate> coordinates;
    coordinates.reserve(sites_.size());
    for (const auto& site : sites_) coordinates.push_back(site.site);
    frame.observations = runtime.observe_many(coordinates);
    if (capture_stopped_) return frame;
    if (frames_.size() >= frame_budget_) {
        capture_stopped_ = true;
        return frame;
    }
    if (!frames_.empty()) {
        const auto& previous = frames_.back();
        TraceTransition transition{};
        transition.tick_before = previous.tick;
        transition.tick_after = frame.tick;
        for (std::size_t i = 0; i < sites_.size(); ++i) {
            auto change = compare_observations(previous.observations[i], frame.observations[i]);
            if (change.classification != "UNCHANGED") {
                transition.ids.push_back(sites_[i].id);
                transition.changes.push_back(std::move(change));
            }
        }
        transitions_.push_back(std::move(transition));
    }
    frames_.push_back(frame);
    return frame;
}

void PassiveTracker::clear_trace() {
    frames_.clear();
    transitions_.clear();
    capture_stopped_ = false;
}

}  // namespace dee::thinking::genealogy
