#include "dee_thinking/basal.hpp"
#include "dee_thinking/genealogy.hpp"
#include "dee_thinking/observation.hpp"
#include "dee_thinking/version.hpp"

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace basal = dee::thinking::basal;
namespace genealogy = dee::thinking::genealogy;
namespace observation = dee::thinking::observation;

int main(int argc, char** argv) {
    try {
        if (argc < 2 || argc > 3) {
            std::cerr << "usage: dee_thinking_basal_consumer SEED [OUTPUT_SNAPSHOT]\n";
            return 2;
        }
        const std::string seed = argv[1];
        if (!std::filesystem::is_regular_file(seed)) {
            throw std::runtime_error("seed snapshot does not exist");
        }

        auto config = basal::Config::relational_reference(seed);
        config.history = basal::History::AB;
        config.execution = {dee::v27::Backend::Lazy, 1};
        auto world = basal::World::create(config);
        const auto initial = world.observe();
        if (initial.absolute_tick != 32 || initial.delta != std::optional<std::int64_t>{0}) {
            throw std::runtime_error("unexpected external-consumer t0");
        }

        genealogy::PassiveTracker tracker({{"A", world.ports().a},
                                            {"B", world.ports().b}}, 4);
        (void)tracker.capture(world.runtime());
        const auto gate_before = observation::inspect_write_gate(
            world.runtime(), world.ports().a, false);
        world.advance(1);
        (void)tracker.capture(world.runtime());
        const auto learned = world.observe();
        if (learned.delta != std::optional<std::int64_t>{1}) {
            throw std::runtime_error("external consumer did not reproduce AB relation");
        }

        if (argc == 3) {
            world.save_snapshot(argv[2]);
            auto restored = basal::World::load_snapshot(argv[2]);
            if (restored.runtime().raw_copy() != world.runtime().raw_copy() ||
                restored.runtime().clock_copy() != world.runtime().clock_copy()) {
                throw std::runtime_error("external-consumer snapshot mismatch");
            }
        }

        std::cout << "dee_thinking_version=" << dee::thinking::kProductVersion
                  << " kernel=27 tick=" << learned.absolute_tick
                  << " delta=" << *learned.delta
                  << " gate_branch=" << gate_before.branch
                  << " passive_frames=" << tracker.frames().size() << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "dee_thinking_basal_consumer: " << error.what() << '\n';
        return 1;
    }
}
