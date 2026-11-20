#include "dee_thinking/composition.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

using dee::thinking::EventStatus;
using dee::thinking::catalog::ComposedWorld;
using dee::thinking::catalog::CompositionPlanner;
using dee::thinking::catalog::OrganizationCatalog;

void require(bool value, const std::string& message) {
    if (!value) throw std::runtime_error(message);
}

CompositionPlanner learning_query_plan(const OrganizationCatalog& catalog) {
    CompositionPlanner planner(34);
    planner.add(catalog.instantiate(
        {"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    planner.add(catalog.instantiate(
        {"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    planner.connect({{"learner", "learned_relation"},
                     {"reader", "relation_input"},
                     "mobile learned relation reaches the fixed reader"});
    return planner;
}

void train(ComposedWorld& world, bool teacher) {
    if (teacher) {
        require(world.experience_batch(
                    {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0).status ==
                    EventStatus::Scheduled,
                "training batch was not scheduled");
    } else {
        require(world.experience("learner", "cue", 0, 5).status == EventStatus::Scheduled,
                "control cue was not scheduled");
    }
    world.runtime().run_until(6);
}

void later_query(ComposedWorld& world) {
    // This input is submitted at t=6, after the world has already evolved. It
    // is not part of a complete t0 agenda and does not rebuild the world.
    require(world.probe("reader", "query", world.runtime().current_tick(), 13).status ==
                EventStatus::Scheduled,
            "later query was not scheduled");
    world.runtime().run_until(11);
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const auto snapshot = argc > 1
            ? std::filesystem::path(argv[1])
            : std::filesystem::current_path() / "consumer_composition.deetsnap";

        OrganizationCatalog catalog;
        auto world = learning_query_plan(catalog).build();
        world.runtime().set_execution_options({dee::v27::Backend::Lazy, 2});
        train(world, true);
        later_query(world);

        const auto response_site = world.landmarks().at("reader.response");
        const auto response = world.runtime().observe(response_site);
        require(response.record.occupied() && response.record.s_reg == 25,
                "unexpected learned response");

        // The v2 snapshot carries a canonical composition recipe as well as its
        // identity and execution state. No caller-side planner is needed here.
        world.save_snapshot(snapshot.string());
        auto restored = ComposedWorld::load_snapshot(snapshot.string());
        require(restored.organizations().size() == 2 && restored.connections().size() == 1,
                "snapshot did not reconstruct the composition structure");
        require(restored.runtime().raw_copy() == world.runtime().raw_copy(),
                "restored RAW differs at checkpoint");
        require(restored.runtime().clock_copy() == world.runtime().clock_copy(),
                "restored clock differs at checkpoint");

        // A backend switch at a tick boundary changes only the evaluation
        // schedule. The two continuations remain exact in full causal state.
        world.runtime().set_execution_options({dee::v27::Backend::DenseSequential, 1});
        restored.runtime().set_execution_options({dee::v27::Backend::DenseParallel, 2});
        world.runtime().advance(3);
        restored.runtime().advance(3);
        require(restored.runtime().raw_copy() == world.runtime().raw_copy(),
                "restored/backend-switched RAW future differs");
        require(restored.runtime().clock_copy() == world.runtime().clock_copy(),
                "restored/backend-switched clock future differs");

        // Same fixed composition and query protocol, teacher link omitted.
        auto control = learning_query_plan(catalog).build();
        control.runtime().set_execution_options({dee::v27::Backend::Lazy, 2});
        train(control, false);
        later_query(control);
        const auto control_response = control.runtime().observe(
            control.landmarks().at("reader.response"));
        require(control_response.raw != response.raw,
                "teacher control did not separate the response");

        std::cout << "DEE thinking Entrega 02 installed consumer\n"
                  << "organizations=2 connections=1 single_runtime=true\n"
                  << "later_input_tick=6 response_s_reg=" << response.record.s_reg << '\n'
                  << "snapshot_version=" << restored.runtime().loaded_snapshot_version() << '\n'
                  << "restored_future_exact=true control_distinct=true\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "independent consumer error: " << error.what() << '\n';
        return 1;
    }
}
