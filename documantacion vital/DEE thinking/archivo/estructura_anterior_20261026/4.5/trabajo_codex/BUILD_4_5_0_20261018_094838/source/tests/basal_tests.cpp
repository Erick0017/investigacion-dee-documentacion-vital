#include "dee_thinking/basal.hpp"
#include "dee_thinking/diagnostics.hpp"
#include "dee_thinking/genealogy.hpp"
#include "dee_thinking/observation.hpp"
#include "test_support.hpp"

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>

namespace basal = dee::thinking::basal;
namespace diag = dee::thinking::diagnostics;
namespace genealogy = dee::thinking::genealogy;
namespace observation = dee::thinking::observation;

using dee::thinking::Coordinate;
using dee::thinking::ResearchStateEdit;

namespace {

basal::World relational(const std::string& seed, basal::History history,
                        Coordinate origin = {15, 15, 15}) {
    auto config = basal::Config::relational_reference(seed);
    config.history = history;
    config.origin = origin;
    config.execution = {dee::v27::Backend::Lazy, 1};
    return basal::World::create(config);
}

basal::World contextual(const std::string& seed,
                        Coordinate origin = {15, 15, 15}) {
    auto config = basal::Config::contextual_reference(seed);
    config.origin = origin;
    config.execution = {dee::v27::Backend::Lazy, 1};
    return basal::World::create(config);
}

basal::World contextual_with_backend(const std::string& seed,
                                     dee::v27::Backend backend,
                                     unsigned int threads) {
    auto config = basal::Config::contextual_reference(seed);
    config.execution = {backend, threads};
    return basal::World::create(config);
}

void check_history(dee::thinking::test::Suite& suite, const std::string& seed,
                   basal::History history, std::int64_t expected_delta) {
    auto world = relational(seed, history);
    const auto before = world.observe();
    DEE_CHECK_EQ(suite, before.absolute_tick, 32ULL);
    DEE_CHECK_EQ(suite, before.relative_tick, 0ULL);
    // The comparator is intentionally not preinstalled at t0; relational
    // state A/B remains observable while the later physical reader is absent.
    DEE_CHECK_EQ(suite, before.availability,
                 basal::Availability::MissingComparator);
    DEE_CHECK(suite, before.delta.has_value());
    DEE_CHECK_EQ(suite, *before.delta, 0);
    DEE_CHECK_EQ(suite, before.a->record.s_reg, 100);
    DEE_CHECK_EQ(suite, before.b->record.s_reg, 100);

    world.advance(1);
    const auto after = world.observe();
    DEE_CHECK_EQ(suite, after.absolute_tick, 33ULL);
    DEE_CHECK_EQ(suite, after.relative_tick, 1ULL);
    DEE_CHECK(suite, after.delta.has_value());
    DEE_CHECK_EQ(suite, *after.delta, expected_delta);
    if (history == basal::History::AB) {
        DEE_CHECK_EQ(suite, after.a->record.s_reg, 101);
        DEE_CHECK_EQ(suite, after.b->record.s_reg, 100);
    } else if (history == basal::History::BA) {
        DEE_CHECK_EQ(suite, after.a->record.s_reg, 100);
        DEE_CHECK_EQ(suite, after.b->record.s_reg, 101);
    }
}

void check_world_equal(dee::thinking::test::Suite& suite,
                       const basal::World& left, const basal::World& right) {
    DEE_CHECK_EQ(suite, left.runtime().dimension(), right.runtime().dimension());
    DEE_CHECK_EQ(suite, left.runtime().current_tick(), right.runtime().current_tick());
    DEE_CHECK_EQ(suite, left.runtime().raw_copy(), right.runtime().raw_copy());
    DEE_CHECK_EQ(suite, left.runtime().clock_copy(), right.runtime().clock_copy());
    DEE_CHECK_EQ(suite, left.t0_tick(), right.t0_tick());
    DEE_CHECK_EQ(suite, left.observe().delta, right.observe().delta);
    DEE_CHECK_EQ(suite, left.observe().axis_projection, right.observe().axis_projection);
}

void check_ports_equal(dee::thinking::test::Suite& suite,
                       const basal::Ports& left, const basal::Ports& right) {
    DEE_CHECK_EQ(suite, left.origin, right.origin);
    DEE_CHECK_EQ(suite, left.a, right.a);
    DEE_CHECK_EQ(suite, left.b, right.b);
    DEE_CHECK_EQ(suite, left.comparator, right.comparator);
    DEE_CHECK_EQ(suite, left.reader_source, right.reader_source);
    DEE_CHECK_EQ(suite, left.event_sources, right.event_sources);
    DEE_CHECK_EQ(suite, left.supports, right.supports);
    DEE_CHECK_EQ(suite, left.environmental_sources, right.environmental_sources);
    DEE_CHECK_EQ(suite, left.action_site, right.action_site);
    DEE_CHECK_EQ(suite, left.return_site, right.return_site);
    DEE_CHECK_EQ(suite, left.bend_site, right.bend_site);
    DEE_CHECK_EQ(suite, left.bend2_site, right.bend2_site);
}

}  // namespace

int main(int argc, char** argv) {
    dee::thinking::test::Suite suite("basal_tests");
    if (argc != 2) {
        std::cerr << "usage: basal_tests PATH_TO_OBP_FRESH_VALIDATED_T32.deetsnap\n";
        return 2;
    }
    const std::string seed = argv[1];
    DEE_CHECK(suite, std::filesystem::is_regular_file(seed));

    // The published relational histories share the same body and seed.  Only
    // the physical history preparation differs before t0.
    check_history(suite, seed, basal::History::AB, 1);
    check_history(suite, seed, basal::History::BA, -1);
    check_history(suite, seed, basal::History::H0, 0);

    // The validated translations reproduce the same one-step relational
    // response without changing the toroidal frame or the recipe.
    for (const Coordinate origin :
         std::vector<Coordinate>{{22, 20, 24}, {28, 26, 18}}) {
        auto translated = relational(seed, basal::History::AB, origin);
        translated.advance(1);
        const auto result = translated.observe();
        DEE_CHECK_EQ(suite, *result.delta, 1);
        DEE_CHECK_EQ(suite, result.a->record.s_reg, 101);
        DEE_CHECK_EQ(suite, result.b->record.s_reg, 100);
    }

    // The contextual fixture reaches the documented B write gate at relative
    // tick 131.  Gate inspection is passive and exposes rule facts without
    // claiming that the prestate alone resolves DEMUX provenance.
    auto feedback = contextual(seed);
    feedback.advance(131);
    const auto at_131 = feedback.observe();
    DEE_CHECK_EQ(suite, at_131.absolute_tick, 163ULL);
    DEE_CHECK_EQ(suite, at_131.relative_tick, 131ULL);
    DEE_CHECK_EQ(suite, at_131.a->record.s_reg, 101);
    DEE_CHECK_EQ(suite, at_131.b->record.s_reg, 100);
    DEE_CHECK_EQ(suite, *at_131.delta, 1);

    const auto raw_before_gate = feedback.runtime().raw_copy();
    const auto clock_before_gate = feedback.runtime().clock_copy();
    const auto gate = observation::inspect_write_gate(
        feedback.runtime(), feedback.ports().b, true);
    DEE_CHECK_EQ(suite, gate.absolute_tick, 163ULL);
    DEE_CHECK_EQ(suite, gate.local_clock, 391ULL);
    DEE_CHECK_EQ(suite, gate.center.s_reg, 100);
    DEE_CHECK_EQ(suite, gate.n_active, 6);
    DEE_CHECK(suite, gate.period.has_value());
    DEE_CHECK_EQ(suite, *gate.period, 391);
    DEE_CHECK(suite, gate.phase_remainder.has_value());
    DEE_CHECK_EQ(suite, *gate.phase_remainder, 0ULL);
    DEE_CHECK(suite, gate.ordinary_increment_condition);
    DEE_CHECK_EQ(suite, gate.neighbors.size(), 26ULL);
    DEE_CHECK_EQ(suite, gate.demux_status,
                 std::string("UNRESOLVED_FROM_PASSIVE_PRESTATE"));
    DEE_CHECK_EQ(suite, feedback.runtime().raw_copy(), raw_before_gate);
    DEE_CHECK_EQ(suite, feedback.runtime().clock_copy(), clock_before_gate);

    auto before_write = feedback.fork();
    feedback.advance(1);
    const auto at_132 = feedback.observe();
    DEE_CHECK_EQ(suite, at_132.relative_tick, 132ULL);
    DEE_CHECK_EQ(suite, at_132.b->record.s_reg, 101);
    DEE_CHECK_EQ(suite, *at_132.delta, 0);
    const auto transition = observation::compare_site(
        before_write.runtime(), feedback.runtime(), feedback.ports().b);
    DEE_CHECK(suite, transition.classification == "OBSERVED_CHANGE");
    DEE_CHECK(suite, !transition.changed_fields.empty());

    feedback.advance(38);
    const auto retained = feedback.observe();
    DEE_CHECK_EQ(suite, retained.relative_tick, 170ULL);
    DEE_CHECK_EQ(suite, retained.b->record.s_reg, 101);
    DEE_CHECK_EQ(suite, *retained.delta, 0);

    // The new preset is an orchestration layer over the unchanged v27 rule.
    // Verify a decisive contextual boundary with every published backend.
    auto dense_feedback = contextual_with_backend(
        seed, dee::v27::Backend::DenseSequential, 1);
    auto parallel_feedback = contextual_with_backend(
        seed, dee::v27::Backend::DenseParallel, 2);
    auto lazy_feedback = contextual_with_backend(
        seed, dee::v27::Backend::Lazy, 1);
    dense_feedback.advance(132);
    parallel_feedback.advance(132);
    lazy_feedback.advance(132);
    check_world_equal(suite, dense_feedback, lazy_feedback);
    check_world_equal(suite, parallel_feedback, lazy_feedback);

    // A declared-site tracker reads passively.  Capturing the tracked world at
    // every boundary produces exactly the same physical trajectory as an
    // unobserved reference world.
    auto tracked = relational(seed, basal::History::AB);
    auto untracked = tracked.fork();
    genealogy::PassiveTracker tracker({{"A", tracked.ports().a},
                                        {"B", tracked.ports().b}}, 8);
    (void)tracker.capture(tracked.runtime());
    for (int i = 0; i < 3; ++i) {
        tracked.advance(1);
        (void)tracker.capture(tracked.runtime());
        untracked.advance(1);
    }
    check_world_equal(suite, tracked, untracked);
    DEE_CHECK_EQ(suite, tracker.frames().size(), 4ULL);
    DEE_CHECK_EQ(suite, tracker.transitions().size(), 3ULL);

    // Plain and diagnostic forks own independent state.  A phase-only edit at
    // B suppresses the documented ordinary write in the diagnostic branch,
    // while the parent and reference trajectory remain unchanged.
    auto phase_parent = contextual(seed);
    phase_parent.advance(131);
    const auto parent_raw = phase_parent.runtime().raw_copy();
    const auto parent_clock = phase_parent.runtime().clock_copy();
    auto child = phase_parent.fork();
    child.advance(1);
    DEE_CHECK_EQ(suite, phase_parent.runtime().current_tick(), 163ULL);
    DEE_CHECK_EQ(suite, phase_parent.runtime().raw_copy(), parent_raw);
    DEE_CHECK_EQ(suite, phase_parent.runtime().clock_copy(), parent_clock);

    // attach() is a non-owning view over the exact Runtime supplied by the
    // caller.  Advancing through the view must advance that owner rather than
    // a duplicated universe, and attaching must not replace its scheduler.
    auto attach_source = relational(seed, basal::History::AB);
    auto owner = attach_source.runtime().fork();
    owner.set_execution_options({dee::v27::Backend::DenseSequential, 1});
    auto attach_config = attach_source.config();
    attach_config.execution = {dee::v27::Backend::Lazy, 1};
    auto attached = basal::World::attach(
        owner, attach_config, attach_source.ports(), attach_source.t0_tick());
    DEE_CHECK(suite, &attached.runtime() == &owner);
    DEE_CHECK_EQ(suite, owner.execution_options().backend,
                 dee::v27::Backend::DenseSequential);
    attached.advance(1);
    DEE_CHECK_EQ(suite, owner.current_tick(), 33ULL);
    DEE_CHECK_EQ(suite, attached.observe().delta, std::optional<std::int64_t>{1});
    DEE_CHECK_EQ(suite, *child.observe().delta, 0);

    const ResearchStateEdit phase_edit{
        phase_parent.ports().b, std::nullopt, 392ULL,
        "diagnostic.phase_miss_at_b"};
    DEE_CHECK_THROWS(suite, phase_parent.diagnostic_fork({phase_edit}, false));
    const auto comparison = diag::compare_fork(
        phase_parent, {phase_edit}, 1, true);
    DEE_CHECK(suite, comparison.parent_unchanged);
    DEE_CHECK_EQ(suite, comparison.reference_observation.delta,
                 std::optional<std::int64_t>{0});
    DEE_CHECK_EQ(suite, comparison.diagnostic_observation.delta,
                 std::optional<std::int64_t>{1});
    DEE_CHECK(suite, comparison.raw_different_sites > 0);
    DEE_CHECK_EQ(suite, phase_parent.runtime().raw_copy(), parent_raw);
    DEE_CHECK_EQ(suite, phase_parent.runtime().clock_copy(), parent_clock);

    // Basal snapshot metadata is sufficient to restore the inert product
    // descriptor and resume the same future without invoking the constructor.
    const auto nonce = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto snapshot = std::filesystem::temp_directory_path() /
        ("dee_thinking_basal_" + std::to_string(nonce) + ".deetsnap");
    std::error_code remove_error;
    std::filesystem::remove(snapshot, remove_error);
    auto save_source = relational(seed, basal::History::AB);
    save_source.advance(1);
    save_source.save_snapshot(snapshot.string());
    auto restored = basal::World::load_snapshot(snapshot.string());
    check_world_equal(suite, save_source, restored);
    check_ports_equal(suite, save_source.ports(), restored.ports());

    auto invalid_recipe = dee::thinking::Runtime::load_snapshot(snapshot.string());
    invalid_recipe.set_snapshot_metadata(
        "dee_thinking.basal.recipe", "unsupported.recipe");
    invalid_recipe.save_snapshot(snapshot.string());
    DEE_CHECK_THROWS(suite, basal::World::load_snapshot(snapshot.string()));

    save_source.save_snapshot(snapshot.string());
    auto invalid_seed = dee::thinking::Runtime::load_snapshot(snapshot.string());
    invalid_seed.set_snapshot_metadata(
        "dee_thinking.basal.seed_id", "unknown-seed");
    invalid_seed.save_snapshot(snapshot.string());
    DEE_CHECK_THROWS(suite, basal::World::load_snapshot(snapshot.string()));

    save_source.save_snapshot(snapshot.string());
    auto invalid_t0 = dee::thinking::Runtime::load_snapshot(snapshot.string());
    invalid_t0.set_snapshot_metadata("dee_thinking.basal.t0", "999999");
    invalid_t0.save_snapshot(snapshot.string());
    DEE_CHECK_THROWS(suite, basal::World::load_snapshot(snapshot.string()));

    save_source.save_snapshot(snapshot.string());
    restored = basal::World::load_snapshot(snapshot.string());
    save_source.advance(8);
    restored.advance(8);
    check_world_equal(suite, save_source, restored);

    feedback.save_snapshot(snapshot.string());
    auto restored_feedback = basal::World::load_snapshot(snapshot.string());
    check_world_equal(suite, feedback, restored_feedback);
    check_ports_equal(suite, feedback.ports(), restored_feedback.ports());
    std::filesystem::remove(snapshot, remove_error);

    return suite.finish();
}
