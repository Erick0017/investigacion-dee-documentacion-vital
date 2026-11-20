#include "dee_thinking/composition.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <array>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace dee::thinking;
using namespace dee::thinking::catalog;

namespace {

CompositionPlanner c7_plan(const OrganizationCatalog& catalog) {
    CompositionPlanner planner(127);
    const Coordinate anchor{63, 63, 63};
    planner.add(catalog.instantiate({"mobile_lineage.c7h03.v1", "lineage", anchor, {}}));
    planner.add(catalog.instantiate({"native_update_bridge.p01.v1", "bridge", anchor, {}}));
    planner.add(catalog.instantiate({"query_recurrence.p01.v1", "queries", anchor, {}}));
    planner.connect({{"bridge", "native_update"}, {"lineage", "update_input"}, "native consequence updates lineage"});
    planner.connect({{"lineage", "updated_relation"}, {"queries", "updated_relation_input"}, "updated lineage enters query train"});
    return planner;
}

void admit_c7(ComposedWorld& world, bool marker, std::uint16_t marker_load = 17,
              bool cut_update_link = false, bool supply = true,
              bool teacher = true) {
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
    std::vector<PortInputRequest> requests{
        {"lineage", "cue", 4083},
        {"queries", "program_redirect", 0},
        {"queries", "query1", 7},
        {"queries", "query2", 5},
        {"queries", "query3", 3},
        {"queries", "query_redirect1", 0},
        {"queries", "query_redirect2", 0},
    };
    if (teacher) requests.push_back({"lineage", "teacher", 19});
    if (supply) requests.push_back({"bridge", "supply", 23});
    if (marker) requests.push_back({"bridge", "marker", marker_load});
    if (cut_update_link) {
        requests.push_back({"bridge", "cut_update_link", 0});
    }
    const auto receipt = world.experience_batch(requests, 0);
    if (receipt.status != EventStatus::Scheduled) throw std::runtime_error("C7 inputs were not scheduled");
}

CompositionPlanner context_plan(const OrganizationCatalog& catalog, std::int64_t history_mode) {
    CompositionPlanner planner(127);
    const Coordinate anchor{30, 30, 30};
    planner.add(catalog.instantiate({"distributed_context.i05.v1", "context", anchor, {}}));
    planner.add(catalog.instantiate({"relative_history.i02.v1", "history", anchor,
                                     {{"history_mode", history_mode}}}));
    planner.add(catalog.instantiate({"contextual_multichannel_recurrence.p02.v1", "integration", anchor, {}}));
    planner.connect({{"context", "context_output"}, {"history", "context"}, "relative history uses full scaffold"});
    planner.connect({{"history", "history_state"}, {"integration", "context_input"}, "history conditions recurrence"});
    return planner;
}

dee::v27::Record run_context(const OrganizationCatalog& catalog, std::int64_t history,
                        bool channel_b, std::uint16_t b_load, bool cut,
                        bool sham = false) {
    auto world = context_plan(catalog, history).build();
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
    std::vector<PortInputRequest> inputs{{"integration", "A", 8}};
    if (channel_b) inputs.push_back({"integration", "B", b_load});
    const auto main = world.experience_batch(inputs, 0);
    if (main.status != EventStatus::Scheduled) throw std::runtime_error("context input rejected");
    if (cut) {
        const auto receipt = world.experience("integration", "cut_link", 0, 0);
        if (receipt.status != EventStatus::Scheduled) throw std::runtime_error("cut rejected");
    }
    if (sham) {
        const auto receipt = world.experience("integration", "sham_link", 0, 0);
        if (receipt.status != EventStatus::Scheduled) throw std::runtime_error("sham rejected");
    }
    world.runtime().run_until(12);
    return world.runtime().observe(world.landmarks().at("integration.q")).record;
}

}  // namespace

int main() {
    dee::thinking::test::Suite suite("composition_catalog_tests");
    OrganizationCatalog catalog;

    // All seven required families are represented. CORE05 phase memory is now
    // an exact, versioned public constructor recovered from NRH04/NRH06.
    std::set<OrganizationFamily> covered;
    for (const auto& descriptor : catalog.descriptors()) {
        covered.insert(descriptor.families.begin(), descriptor.families.end());
        DEE_CHECK(suite, !descriptor.initial_footprint.empty());
        DEE_CHECK(suite, !descriptor.functional_relation.empty());
        DEE_CHECK(suite, !descriptor.read_region.empty());
        DEE_CHECK(suite, !descriptor.required_context.empty());
        DEE_CHECK(suite, !descriptor.context_horizon.empty());
    }
    DEE_CHECK_EQ(suite, covered.size(), std::size_t{7});
    const auto* temporal = catalog.find("temporal_phase_memory.core05.v1");
    DEE_CHECK(suite, temporal != nullptr);
    if (temporal != nullptr) {
        DEE_CHECK_EQ(suite, temporal->availability, Availability::Available);
        const auto phase = catalog.instantiate(
            {"temporal_phase_memory.core05.v1", "phase_smoke", {10, 10, 10}, {}});
        DEE_CHECK_EQ(suite, phase.descriptor().id,
                     std::string("temporal_phase_memory.core05.v1"));
        DEE_CHECK(suite, !phase.initial_footprint().empty());
    }
    DEE_CHECK_THROWS(suite, catalog.instantiate(
        {"transport.axis.v1", "bad", {0, 0, 0}, {{"distance", 21}}}));

    // The catalog transport builder itself is executable; it does not merely
    // point at the older monolithic E1 helper.
    {
        CompositionPlanner planner(17);
        planner.add(catalog.instantiate(
             {"transport.axis.v1", "transport", {2, 8, 8}, {{"distance", 5}, {"direction_code", 0}}}));
        auto world = planner.build();
        DEE_CHECK(suite, !world.organizations().front().channel_contracts().empty());
        const auto budget = world.organizations().front().resource_budget();
        DEE_CHECK_EQ(suite, budget.input_channels, std::size_t{1});
        DEE_CHECK(suite, budget.declared_ports >= std::size_t{2});
        const auto composition_identity = world.manifest_json();
        world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
        DEE_CHECK_EQ(suite, world.experience("transport", "carrier", 0, 7).status,
                     EventStatus::Scheduled);
        world.runtime().run_until(5);
        DEE_CHECK_EQ(suite, world.runtime().observe(world.landmarks().at("transport.arrival")).record.s_reg,
                     std::uint16_t{7});
        DEE_CHECK(suite, world.runtime().snapshot_metadata("dee_thinking.composition_manifest").has_value());
        DEE_CHECK_EQ(suite, world.manifest_json(), composition_identity);
        DEE_CHECK_EQ(suite,
                     world.runtime().snapshot_metadata("dee_thinking.composition_manifest").value(),
                     composition_identity);
    }

    // Composition A: three independently selected organizations share one
    // Runtime. The intact, no-marker, and reserved marker-load cases retain the
    // same geometry and public contracts.
    {
        const auto diagnostics = c7_plan(catalog).analyze();
        DEE_CHECK(suite, std::none_of(diagnostics.begin(), diagnostics.end(),
                                     [](const auto& d) { return d.severity == DiagnosticSeverity::Error; }));

        auto intact = c7_plan(catalog).build();
        DEE_CHECK_THROWS(suite, intact.experience("lineage", "update_input", 0, 1));
        admit_c7(intact, true);
        intact.runtime().run_until(12);
        DEE_CHECK_EQ(suite, intact.runtime().observe(intact.landmarks().at("lineage.program_site")).record.s_reg,
                     std::uint16_t{4142});
        intact.runtime().run_until(34);
        DEE_CHECK_EQ(suite, intact.runtime().observe(intact.landmarks().at("queries.response1")).record.s_reg,
                     std::uint16_t{4149});
        intact.runtime().run_until(46);
        DEE_CHECK_EQ(suite, intact.runtime().observe(intact.landmarks().at("queries.response2")).record.s_reg,
                     std::uint16_t{4154});
        intact.runtime().run_until(58);
        DEE_CHECK_EQ(suite, intact.runtime().observe(intact.landmarks().at("queries.response3")).record.s_reg,
                     std::uint16_t{4157});

        auto no_marker = c7_plan(catalog).build();
        admit_c7(no_marker, false);
        no_marker.runtime().run_until(12);
        DEE_CHECK_EQ(suite, no_marker.runtime().observe(no_marker.landmarks().at("lineage.program_site")).record.s_reg,
                     std::uint16_t{4125});

        // A true no-update control keeps the trained C7 relation but omits
        // both bridge reactants.  It is distinct from merely omitting marker,
        // where the common supply still performs a 23-load update.
        auto no_update = c7_plan(catalog).build();
        admit_c7(no_update, false, 0, false, false, true);
        no_update.runtime().run_until(12);
        DEE_CHECK_EQ(suite,
                     no_update.runtime().observe(no_update.landmarks().at("lineage.program_site")).record.s_reg,
                     std::uint16_t{4102});

        // Omit the explicit teacher while preserving the common update
        // resources.  The bridge consequence can still exist, but there is no
        // learned mobile relation for it to update.
        auto no_learning = c7_plan(catalog).build();
        admit_c7(no_learning, true, 17, false, true, false);
        no_learning.runtime().run_until(12);
        DEE_CHECK(suite,
                  no_learning.runtime().observe(no_learning.landmarks().at("lineage.program_site")).record.raw !=
                      intact.runtime().observe(intact.landmarks().at("lineage.program_site")).record.raw);

        auto reserved = c7_plan(catalog).build();
        admit_c7(reserved, true, 19);
        reserved.runtime().run_until(12);
        DEE_CHECK_EQ(suite, reserved.runtime().observe(reserved.landmarks().at("lineage.program_site")).record.s_reg,
                     std::uint16_t{4144});

        auto cut = c7_plan(catalog).build();
        admit_c7(cut, true, 17, true);
        cut.runtime().run_until(34);
        const auto cut_response = cut.runtime().observe(cut.landmarks().at("queries.response1")).record;
        DEE_CHECK(suite, cut_response.raw != std::uint64_t{0});
        DEE_CHECK(suite, cut_response.raw != intact.runtime().observe(intact.landmarks().at("queries.response1")).record.raw);
    }

    // A distinct public composition admits its query only after six ticks.
    // This prevents a t0-only agenda from masquerading as continued use.
    {
        CompositionPlanner planner(34);
        planner.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
        planner.add(catalog.instantiate({"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
        planner.connect({{"learner", "learned_relation"}, {"reader", "relation_input"}, "mobile relation reaches reader"});
        auto trained = planner.build();
        trained.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
        DEE_CHECK_THROWS(suite, trained.probe("reader", "query", 5, 13));
        DEE_CHECK_EQ(suite, trained.experience_batch(
            {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0).status,
                     EventStatus::Scheduled);
        trained.runtime().run_until(6);
        DEE_CHECK_EQ(suite, trained.probe("reader", "query", 6, 13).status,
                     EventStatus::Scheduled);
        trained.runtime().run_until(11);
        DEE_CHECK_EQ(suite, trained.runtime().observe(trained.landmarks().at("reader.response")).record.s_reg,
                     std::uint16_t{25});
    }

    // Composition B: distributed context + relative history + multichannel
    // recurrence. Absence and a present zero-load B carrier are kept distinct.
    {
        const auto ha_ab = run_context(catalog, 1, true, 9, false);
        const auto hb_ab = run_context(catalog, 2, true, 9, false);
        const auto absent_b = run_context(catalog, 1, false, 0, false);
        const auto zero_b = run_context(catalog, 1, true, 0, false);
        const auto cut = run_context(catalog, 1, true, 9, true);
        const auto sham = run_context(catalog, 1, true, 9, false, true);
        DEE_CHECK_EQ(suite, ha_ab.s_reg, std::uint16_t{391});
        DEE_CHECK(suite, ha_ab.raw != hb_ab.raw);
        DEE_CHECK(suite, absent_b.raw != zero_b.raw);
        DEE_CHECK_EQ(suite, cut.s_reg, std::uint16_t{367});
        DEE_CHECK(suite, cut.raw != ha_ab.raw);
        // Same load/state/direction and same admission time as the cut, but a
        // parallel path that never visits the redirect site in this horizon.
        DEE_CHECK_EQ(suite, sham.raw, ha_ab.raw);
    }

    // Unsupported geometry produces a clear static error rather than a path
    // invented by the planner.
    {
        CompositionPlanner invalid(34);
        invalid.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
        invalid.add(catalog.instantiate({"relation_query.c6h01.v1", "reader", {10, 25, 14}, {}}));
        invalid.connect({{"learner", "learned_relation"}, {"reader", "relation_input"}, "misaligned"});
        const auto diagnostics = invalid.analyze();
        DEE_CHECK(suite, std::any_of(diagnostics.begin(), diagnostics.end(),
                                     [](const auto& d) { return d.code == "PHYSICAL_ROUTE_MISMATCH"; }));
        DEE_CHECK_THROWS(suite, invalid.build());
    }


    // One mobile physical output cannot be wired to two consumers by metadata.
    {
        CompositionPlanner fanout(34);
        fanout.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
        fanout.add(catalog.instantiate({"relation_query.c6h01.v1", "reader1", {10, 26, 14}, {}}));
        fanout.add(catalog.instantiate({"relation_query.c6h01.v1", "reader2", {10, 26, 14}, {}}));
        fanout.connect({{"learner", "learned_relation"}, {"reader1", "relation_input"}, "first consumer"});
        fanout.connect({{"learner", "learned_relation"}, {"reader2", "relation_input"}, "unsupported fanout"});
        const auto diagnostics = fanout.analyze();
        DEE_CHECK(suite, std::any_of(diagnostics.begin(), diagnostics.end(),
                                     [](const auto& d) { return d.code == "PHYSICAL_FANOUT_UNSUPPORTED"; }));
        DEE_CHECK_THROWS(suite, fanout.build());
    }

    // Multiple metadata sources cannot silently converge on a single-target
    // contract.  A future catalog entry may explicitly raise its cardinality,
    // in which case the physical outcome remains simulation-required.
    {
        CompositionPlanner fanin(34);
        fanin.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner1", {10, 18, 14}, {}}));
        fanin.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner2", {10, 18, 14}, {}}));
        fanin.add(catalog.instantiate({"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
        fanin.connect({{"learner1", "learned_relation"}, {"reader", "relation_input"}, "first source"});
        fanin.connect({{"learner2", "learned_relation"}, {"reader", "relation_input"}, "second source"});
        const auto diagnostics = fanin.analyze();
        DEE_CHECK(suite, std::any_of(diagnostics.begin(), diagnostics.end(),
                                     [](const auto& d) { return d.code == "TARGET_CONNECTION_CARDINALITY_EXCEEDED"; }));
        DEE_CHECK_THROWS(suite, fanin.build());
    }
    return suite.finish();
}
