#include "dee_thinking/runtime.hpp"

#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: generate_legacy_v1_pending OUTPUT\n";
        return 2;
    }
    try {
        using namespace dee::thinking;
        Runtime world(9);
        world.register_channel(ChannelSpec{"early", {1, 1, 1}, 1, {1, 0, 0}, 1, true, false});
        world.register_channel(ChannelSpec{"pending", {7, 7, 7}, 1, {-1, 0, 0}, 1, true, true});
        world.set_protocol_phase("entrega01_legacy_pending_fixture");
        if (world.experience("early", 0, 4).status != EventStatus::Scheduled ||
            world.probe("pending", 5, 6).status != EventStatus::Scheduled) {
            std::cerr << "event scheduling failed\n";
            return 1;
        }
        world.advance(1);
        world.save_snapshot(argv[1]);
        std::cout << "legacy_v1_tick=" << world.current_tick()
                  << " pending_event_id=2 pending_boundary=5\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
