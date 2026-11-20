#include "dee_thinking/organizations.hpp"

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void require_scheduled(const dee::thinking::EventReceipt& receipt) {
    if (receipt.status != dee::thinking::EventStatus::Scheduled) {
        throw std::runtime_error("event rejected: " + receipt.reason);
    }
}

void e1() {
    auto world = dee::thinking::make_transport_world(false);
    require_scheduled(world.runtime.experience("carrier", 0, 7));
    world.runtime.run_until(5);
    const auto r = world.runtime.observe(world.landmarks.at("destination")).record;
    std::cout << "E1 transport: state=" << r.state << " s_reg=" << r.s_reg
              << " dir=" << static_cast<int>(r.dx) << ',' << static_cast<int>(r.dy)
              << ',' << static_cast<int>(r.dz) << '\n';
}

void e2() {
    auto world = dee::thinking::make_reprogramming_world();
    require_scheduled(world.runtime.experience_batch({{"cue_train", 5}, {"teacher", 7}}, 0));
    world.runtime.run_until(6);
    require_scheduled(world.runtime.probe("query", 6, 11));
    world.runtime.run_until(11);
    const auto r = world.runtime.observe(world.landmarks.at("response")).record;
    std::cout << "E2 reprogramming: state=" << r.state << " s_reg=" << r.s_reg
              << " dir=" << static_cast<int>(r.dx) << ',' << static_cast<int>(r.dy)
              << ',' << static_cast<int>(r.dz) << '\n';
}

void e3() {
    auto world = dee::thinking::make_history_world(dee::thinking::HistoryMode::HA);
    world.runtime.run_until(3);
    const auto r = world.runtime.observe(world.landmarks.at("comparator")).record;
    std::cout << "E3 history HA: state=" << r.state << " s_reg=" << r.s_reg
              << " dir=" << static_cast<int>(r.dx) << ',' << static_cast<int>(r.dy)
              << ',' << static_cast<int>(r.dz) << '\n';
}

void e4() {
    auto world = dee::thinking::make_recurrence_multichannel_world(
        dee::thinking::HistoryMode::HA);
    require_scheduled(world.runtime.experience_batch({{"A", 8}, {"B", 9}}, 0));
    world.runtime.run_until(12);
    const auto q = world.runtime.observe(world.landmarks.at("q")).record;
    std::cout << "E4 HA+AB recurrence at t12: state=" << q.state
              << " s_reg=" << q.s_reg << " dir=" << static_cast<int>(q.dx) << ','
              << static_cast<int>(q.dy) << ',' << static_cast<int>(q.dz) << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const std::string selection = argc > 1 ? argv[1] : "all";
        if (selection == "e1" || selection == "all") e1();
        if (selection == "e2" || selection == "all") e2();
        if (selection == "e3" || selection == "all") e3();
        if (selection == "e4" || selection == "all") e4();
        if (selection != "all" && selection != "e1" && selection != "e2" &&
            selection != "e3" && selection != "e4") {
            throw std::invalid_argument("usage: dee_thinking_demo [all|e1|e2|e3|e4]");
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "demo error: " << error.what() << '\n';
        return 1;
    }
}
