#include "dee_thinking/diagnostics.hpp"

#include <algorithm>

namespace dee::thinking::diagnostics {

Comparison compare_fork(const basal::World& parent,
                        const std::vector<ResearchStateEdit>& edits,
                        std::uint64_t horizon,
                        bool authorize_diagnostic_intervention) {
    const auto parent_raw = parent.runtime().raw_copy();
    const auto parent_clock = parent.runtime().clock_copy();
    basal::World reference = parent.fork();
    basal::World diagnostic = parent.diagnostic_fork(
        edits, authorize_diagnostic_intervention);
    Comparison out{};
    out.parent_tick = parent.runtime().current_tick();
    out.horizon = horizon;
    for (const auto& edit : edits) {
        const auto before = reference.runtime().observe(edit.coordinate);
        const auto after = diagnostic.runtime().observe(edit.coordinate);
        const bool support = std::find(parent.ports().supports.begin(),
                                       parent.ports().supports.end(),
                                       edit.coordinate) != parent.ports().supports.end();
        out.edits.push_back(AppliedEdit{
            edit.coordinate, edit.label, before.raw, after.raw,
            before.clock, after.clock, before.raw != after.raw,
            before.clock != after.clock, support});
    }
    reference.advance(horizon);
    diagnostic.advance(horizon);
    const auto ref_raw = reference.runtime().raw_copy();
    const auto test_raw = diagnostic.runtime().raw_copy();
    const auto ref_clock = reference.runtime().clock_copy();
    const auto test_clock = diagnostic.runtime().clock_copy();
    for (std::size_t i = 0; i < ref_raw.size(); ++i) {
        if (ref_raw[i] != test_raw[i]) ++out.raw_different_sites;
        if (ref_clock[i] != test_clock[i]) ++out.clock_different_sites;
    }
    out.reference_observation = reference.observe();
    out.diagnostic_observation = diagnostic.observe();
    out.parent_unchanged = parent_raw == parent.runtime().raw_copy() &&
                           parent_clock == parent.runtime().clock_copy();
    return out;
}

}  // namespace dee::thinking::diagnostics
