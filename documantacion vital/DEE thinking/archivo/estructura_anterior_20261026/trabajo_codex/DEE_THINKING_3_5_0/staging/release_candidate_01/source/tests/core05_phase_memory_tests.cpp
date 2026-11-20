#include "dee_thinking/composition.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <map>
#include <optional>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {

using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::Runtime;
using dee::thinking::catalog::ComposedWorld;
using dee::thinking::catalog::CompositionPlanner;
using dee::thinking::catalog::OrganizationCatalog;

constexpr const char* kCatalogId = "temporal_phase_memory.core05.v1";

std::map<std::string, std::int64_t> parameters(int mode, int n) {
    std::map<std::string, std::int64_t> values{
        {"distance", 3}, {"permutation_code", 2}, {"sign_mask", 1},
        {"control_mode", mode}, {"source_index", 3}, {"block_sreg", 1},
        {"source0_sreg", 347}, {"source1_sreg", 382},
        {"source2_sreg", 23}, {"source3_sreg", 304},
    };
    // These are the first NRH06 frozen-result clocks.  Splitting at 32 bits
    // exercises the public catalog's lossless uint64 representation, including
    // values above INT64_MAX.
    constexpr std::array<std::uint64_t, 4> clocks{{
        13534422518340007686ULL, 8838052676805015040ULL,
        8480231960862266535ULL, 5558095591164900842ULL}};
    for (std::size_t i = 0; i < clocks.size(); ++i) {
        const auto prefix = "source" + std::to_string(i) + "_clock_";
        values[prefix + "high"] = static_cast<std::int64_t>(clocks[i] >> 32U);
        values[prefix + "low"] = static_cast<std::int64_t>(clocks[i] & 0xffffffffULL);
    }
    (void)n;
    return values;
}

ComposedWorld make_world(const OrganizationCatalog& catalog, int n, int mode,
                         int distance = 3) {
    auto values = parameters(mode, n);
    values["distance"] = distance;
    CompositionPlanner planner(n);
    planner.add(catalog.instantiate(
        {kCatalogId, "phase", {1, 6, n - 4}, std::move(values)}));
    return planner.build();
}

using HubKey = std::optional<std::tuple<std::uint32_t, std::uint16_t, int, int, int,
                                        std::uint8_t>>;

HubKey hub_key(const ComposedWorld& world) {
    const auto observation = world.runtime().observe(world.landmarks().at("phase.hub"));
    if (observation.raw == 0) return std::nullopt;
    const auto& r = observation.record;
    return std::tuple{r.state, r.s_reg, static_cast<int>(r.dx),
                      static_cast<int>(r.dy), static_cast<int>(r.dz), r.semantic};
}

std::vector<HubKey> trace_hub(ComposedWorld& world, std::uint64_t horizon) {
    std::vector<HubKey> trace;
    trace.reserve(static_cast<std::size_t>(horizon + 1));
    for (std::uint64_t tick = 0; tick <= horizon; ++tick) {
        trace.push_back(hub_key(world));
        if (tick != horizon) world.runtime().advance();
    }
    return trace;
}

bool present(const ComposedWorld& world, const std::string& landmark) {
    return world.runtime().observe(world.landmarks().at(landmark)).raw != 0;
}

std::optional<std::uint64_t> first_difference(const std::vector<HubKey>& left,
                                              const std::vector<HubKey>& right,
                                              std::uint64_t begin) {
    for (std::uint64_t tick = begin; tick < left.size(); ++tick) {
        if (left[static_cast<std::size_t>(tick)] != right[static_cast<std::size_t>(tick)]) {
            return tick;
        }
    }
    return std::nullopt;
}

bool has_four_tick_restoration(const std::vector<HubKey>& baseline,
                               const std::vector<HubKey>& blocked,
                               std::uint64_t begin) {
    for (std::uint64_t tick = begin; tick + 3 < baseline.size(); ++tick) {
        bool equal = true;
        for (std::uint64_t offset = 0; offset < 4; ++offset) {
            equal = equal && baseline[static_cast<std::size_t>(tick + offset)] ==
                                 blocked[static_cast<std::size_t>(tick + offset)];
        }
        if (equal) return true;
    }
    return false;
}

}  // namespace

int main() {
    dee::thinking::test::Suite suite("core05_phase_memory");
    OrganizationCatalog catalog;
    const auto* descriptor = catalog.find(kCatalogId);
    DEE_CHECK(suite, descriptor != nullptr);
    DEE_CHECK_EQ(suite, descriptor->constructor_version, std::string("1.0.0"));
    DEE_CHECK(suite, descriptor->pending_reason.empty());

    // Public contract and full-width clock transport.
    {
        auto world = make_world(catalog, 17, 1);
        const auto& organization = world.organizations().front();
        DEE_CHECK_EQ(suite, organization.initial_footprint().size(), std::size_t{5});
        DEE_CHECK_EQ(suite, organization.resource_budget().persistent_sources, std::size_t{4});
        DEE_CHECK_EQ(suite, organization.channel_contracts().size(), std::size_t{0});
        const auto source0 = world.runtime().observe(world.landmarks().at("phase.source0"));
        DEE_CHECK_EQ(suite, source0.clock, 13534422518340007686ULL);
        DEE_CHECK_EQ(suite, source0.record.semantic, std::uint8_t{4});
    }

    // NRH04 controls: a one-tick obstruction inverts the selected emission
    // parity, survives as phase history, and matches permanent ablation at the
    // hub through distance+12.  The matched spatial rewire produces no hub.
    {
        constexpr int n = 29;
        constexpr int distance = 4;
        constexpr std::uint64_t horizon = distance + 12;
        auto baseline = make_world(catalog, n, 0, distance);
        auto blocked = make_world(catalog, n, 1, distance);
        auto ablation = make_world(catalog, n, 2, distance);
        auto rewired = make_world(catalog, n, 3, distance);
        std::vector<bool> baseline_mouth(horizon + 1), blocked_mouth(horizon + 1);
        std::vector<HubKey> base_hub, block_hub, ablation_hub, rewire_hub;
        for (std::uint64_t tick = 0; tick <= horizon; ++tick) {
            baseline_mouth[tick] = present(baseline, "phase.mouth3");
            blocked_mouth[tick] = present(blocked, "phase.mouth3");
            base_hub.push_back(hub_key(baseline));
            block_hub.push_back(hub_key(blocked));
            ablation_hub.push_back(hub_key(ablation));
            rewire_hub.push_back(hub_key(rewired));
            if (tick != horizon) {
                baseline.runtime().advance(); blocked.runtime().advance();
                ablation.runtime().advance(); rewired.runtime().advance();
            }
        }
        DEE_CHECK(suite, !blocked_mouth[1]);
        for (std::uint64_t tick = 1; tick <= horizon; ++tick) {
            DEE_CHECK_DETAIL(suite, baseline_mouth[tick] != blocked_mouth[tick],
                             "emission parity at tick " + std::to_string(tick));
        }
        DEE_CHECK(suite, block_hub == ablation_hub);
        DEE_CHECK(suite, std::all_of(rewire_hub.begin(), rewire_hub.end(),
                                    [](const auto& value) { return !value.has_value(); }));
        DEE_CHECK(suite, blocked.runtime().raw_copy() != baseline.runtime().raw_copy());
        for (std::uint64_t tick = distance; tick <= horizon; tick += 2) {
            DEE_CHECK(suite, base_hub[tick].has_value());
            if (base_hub[tick]) {
                DEE_CHECK_EQ(suite, std::get<1>(*base_hub[tick]), std::uint16_t{1056});
                DEE_CHECK_EQ(suite, std::get<2>(*base_hub[tick]), -1);
                DEE_CHECK_EQ(suite, std::get<3>(*base_hub[tick]), 1);
                DEE_CHECK_EQ(suite, std::get<4>(*base_hub[tick]), 1);
            }
        }
    }

    // NRH06 toroidal parity oracle: even N diverges from ablation at d+N;
    // odd N remains equivalent through d+3N. Neither arm restores the baseline
    // for four consecutive ticks in the frozen horizon.
    for (const int n : {17, 18}) {
        constexpr int distance = 3;
        const auto horizon = static_cast<std::uint64_t>(distance + 3 * n);
        auto baseline = make_world(catalog, n, 0, distance);
        auto blocked = make_world(catalog, n, 1, distance);
        auto ablation = make_world(catalog, n, 2, distance);
        const auto baseline_trace = trace_hub(baseline, horizon);
        const auto blocked_trace = trace_hub(blocked, horizon);
        const auto ablation_trace = trace_hub(ablation, horizon);
        const auto divergence = first_difference(ablation_trace, blocked_trace, distance);
        if (n % 2 == 0) DEE_CHECK_EQ(suite, divergence, std::optional<std::uint64_t>{distance + n});
        else DEE_CHECK(suite, !divergence.has_value());
        DEE_CHECK(suite, !has_four_tick_restoration(baseline_trace, blocked_trace, distance));
    }

    // Persistence reconstructs the versioned catalog recipe, not just Runtime.
    {
        auto uninterrupted = make_world(catalog, 17, 1);
        uninterrupted.runtime().advance(5);
        auto checkpointed = make_world(catalog, 17, 1);
        checkpointed.runtime().advance(5);
        const auto path = std::filesystem::temp_directory_path() /
                          "dee_core05_phase_memory_v1.deetsnap";
        checkpointed.save_snapshot(path.string());
        auto restored = ComposedWorld::load_snapshot(path.string(), catalog);
        std::filesystem::remove(path);
        DEE_CHECK_EQ(suite, restored.organizations().front().descriptor().id,
                     std::string(kCatalogId));
        DEE_CHECK_EQ(suite, restored.organizations().front().descriptor().constructor_version,
                     std::string("1.0.0"));
        DEE_CHECK_EQ(suite, restored.organizations().front().parameters().at("control_mode"), 1);
        uninterrupted.runtime().advance(13);
        restored.runtime().advance(13);
        DEE_CHECK(suite, restored.runtime().raw_copy() == uninterrupted.runtime().raw_copy());
        DEE_CHECK(suite, restored.runtime().clock_copy() == uninterrupted.runtime().clock_copy());
    }

    // All public execution schedules are exact at every intermediate state.
    {
        auto reference = make_world(catalog, 17, 1);
        reference.runtime().set_execution_options({dee::v27::Backend::DenseSequential, 1});
        std::array<ComposedWorld, 2> candidates{{
            make_world(catalog, 17, 1), make_world(catalog, 17, 1)}};
        candidates[0].runtime().set_execution_options({dee::v27::Backend::DenseParallel, 4});
        candidates[1].runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
        for (int tick = 0; tick < 18; ++tick) {
            DEE_CHECK(suite, candidates[0].runtime().raw_copy() == reference.runtime().raw_copy());
            DEE_CHECK(suite, candidates[1].runtime().raw_copy() == reference.runtime().raw_copy());
            DEE_CHECK(suite, candidates[0].runtime().clock_copy() == reference.runtime().clock_copy());
            DEE_CHECK(suite, candidates[1].runtime().clock_copy() == reference.runtime().clock_copy());
            reference.runtime().advance();
            candidates[0].runtime().advance();
            candidates[1].runtime().advance();
        }
    }

    return suite.finish();
}
