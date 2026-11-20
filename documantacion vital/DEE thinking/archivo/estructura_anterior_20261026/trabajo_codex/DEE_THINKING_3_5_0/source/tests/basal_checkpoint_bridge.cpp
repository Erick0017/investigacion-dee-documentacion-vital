#include "dee_thinking/basal.hpp"

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace basal = dee::thinking::basal;

namespace {

basal::World prepared(const std::string& seed) {
    auto config = basal::Config::relational_reference(seed);
    config.history = basal::History::AB;
    config.execution = {dee::v27::Backend::Lazy, 1};
    auto world = basal::World::create(config);
    world.advance(1);
    if (world.observe().delta != std::optional<std::int64_t>{1}) {
        throw std::runtime_error("unexpected relational response before bridge save");
    }
    return world;
}

void require_same(const basal::World& actual, const basal::World& expected) {
    if (actual.runtime().dimension() != expected.runtime().dimension() ||
        actual.runtime().current_tick() != expected.runtime().current_tick() ||
        actual.runtime().raw_copy() != expected.runtime().raw_copy() ||
        actual.runtime().clock_copy() != expected.runtime().clock_copy() ||
        actual.t0_tick() != expected.t0_tick() ||
        actual.observe().delta != expected.observe().delta ||
        actual.observe().axis_projection != expected.observe().axis_projection) {
        throw std::runtime_error("basal bridge worlds are not bit-exact");
    }
}

void write(const std::string& seed, const std::string& checkpoint,
           const std::string& future) {
    if (!std::filesystem::is_regular_file(seed)) {
        throw std::runtime_error("seed snapshot does not exist");
    }
    auto world = prepared(seed);
    world.save_snapshot(checkpoint);
    world.advance(8);
    world.save_snapshot(future);
    std::cout << "cpp_write checkpoint_tick=33 future_tick=41 delta="
              << *world.observe().delta << '\n';
}

void check(const std::string& checkpoint, const std::string& future) {
    auto resumed = basal::World::load_snapshot(checkpoint);
    const auto expected = basal::World::load_snapshot(future);
    if (resumed.runtime().current_tick() >= expected.runtime().current_tick()) {
        throw std::runtime_error("bridge checkpoint does not precede future");
    }
    resumed.advance(expected.runtime().current_tick() -
                    resumed.runtime().current_tick());
    require_same(resumed, expected);
    std::cout << "cpp_check raw_clock_observation_exact=true tick="
              << resumed.runtime().current_tick() << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 5 && std::string(argv[1]) == "write") {
            write(argv[2], argv[3], argv[4]);
            return 0;
        }
        if (argc == 4 && std::string(argv[1]) == "check") {
            check(argv[2], argv[3]);
            return 0;
        }
        std::cerr << "usage:\n"
                  << "  basal_checkpoint_bridge write SEED CHECKPOINT FUTURE\n"
                  << "  basal_checkpoint_bridge check CHECKPOINT FUTURE\n";
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "basal_checkpoint_bridge: " << error.what() << '\n';
        return 1;
    }
}
