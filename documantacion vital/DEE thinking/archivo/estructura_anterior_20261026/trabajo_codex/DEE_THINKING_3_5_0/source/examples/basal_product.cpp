#include "dee_thinking/basal.hpp"
#include "dee_thinking/diagnostics.hpp"
#include "dee_thinking/genealogy.hpp"
#include "dee_thinking/observation.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>

int main(int argc, char** argv) {
    using namespace dee::thinking;
    if (argc != 3) {
        std::cerr << "usage: dee_basal_product <seed.deetsnap> <output.deetsnap>\n";
        return 2;
    }

    auto config = basal::Config::relational_reference(argv[1]);
    config.history = basal::History::AB;
    auto world = basal::World::create(config);

    genealogy::PassiveTracker tracker({
        {"memory.a", world.ports().a},
        {"memory.b", world.ports().b},
        {"comparator", world.ports().comparator},
    });
    tracker.capture(world.runtime());
    world.advance(1);
    tracker.capture(world.runtime());

    const auto learned = world.observe();
    if (!learned.delta || *learned.delta != 1) {
        throw std::runtime_error("relational AB reference did not produce delta +1");
    }

    const auto gate = observation::inspect_write_gate(
        world.runtime(), world.ports().b, true);
    if (gate.neighbors.size() != 26) {
        throw std::runtime_error("passive gate observer did not return the Moore neighborhood");
    }

    ResearchStateEdit phase_edit{};
    phase_edit.coordinate = world.ports().b;
    phase_edit.clock = gate.local_clock + 1;
    phase_edit.label = "example.phase_plus_one";
    const auto comparison = diagnostics::compare_fork(
        world, {phase_edit}, 1, true);
    if (!comparison.parent_unchanged) {
        throw std::runtime_error("diagnostic fork modified its parent");
    }

    world.save_snapshot(argv[2]);
    auto restored = basal::World::load_snapshot(argv[2]);
    if (restored.runtime().raw_copy() != world.runtime().raw_copy() ||
        restored.runtime().clock_copy() != world.runtime().clock_copy()) {
        throw std::runtime_error("basal snapshot round trip mismatch");
    }

    std::cout << "tick=" << learned.absolute_tick
              << " delta=" << *learned.delta
              << " trace_frames=" << tracker.frames().size()
              << " diagnostic_raw_diffs=" << comparison.raw_different_sites
              << " snapshot=" << std::filesystem::absolute(argv[2]).string()
              << '\n';
    return 0;
}
