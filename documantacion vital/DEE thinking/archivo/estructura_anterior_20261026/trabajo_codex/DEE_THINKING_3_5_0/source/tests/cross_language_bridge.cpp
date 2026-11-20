#include "dee_thinking/runtime.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using dee::thinking::ChannelSpec;
using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::EventReceipt;
using dee::thinking::EventStatus;
using dee::thinking::Runtime;

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

bool same_receipt(const EventReceipt& left, const EventReceipt& right) {
    return left.id == right.id && left.kind == right.kind &&
           left.status == right.status &&
           left.requested_tick == right.requested_tick &&
           left.effective_tick == right.effective_tick &&
           left.channels == right.channels && left.reason == right.reason;
}

void compare_receipts(const std::vector<EventReceipt>& actual,
                      const std::vector<EventReceipt>& expected) {
    require(actual.size() == expected.size(), "receipt count differs");
    for (std::size_t i = 0; i < actual.size(); ++i) {
        require(same_receipt(actual[i], expected[i]),
                "receipt differs at index " + std::to_string(i));
    }
}

Runtime prepared_world() {
    Runtime world(11);
    ChannelSpec channel;
    channel.name = "bridge_input";
    channel.injection_site = {3, 4, 5};
    channel.state = 101;
    channel.direction = {1, 0, 0};
    channel.semantic = 1;
    channel.allow_experience = true;
    channel.allow_probe = true;
    world.register_channel(channel);
    const auto first = world.experience("bridge_input", 0, 17);
    require(first.status == EventStatus::Scheduled, "initial bridge input rejected");
    world.advance(1);
    const auto pending = world.experience("bridge_input", 1, 19);
    require(pending.status == EventStatus::Scheduled, "pending bridge input rejected");
    world.set_snapshot_metadata("bridge.origin", "cpp");
    world.set_protocol_phase("bridge.pending_second_input");
    return world;
}

int produce(const std::filesystem::path& checkpoint,
            const std::filesystem::path& future) {
    auto world = prepared_world();
    world.save_snapshot(checkpoint.string());
    world.run_until(6);
    world.save_snapshot(future.string());
    std::cout << "cpp_produce tick=1 future_tick=6 pending=true\n";
    return 0;
}

int consume(const std::filesystem::path& checkpoint,
            const std::filesystem::path& future) {
    auto resumed = Runtime::load_snapshot(checkpoint.string());
    const auto expected = Runtime::load_snapshot(future.string());
    require(resumed.current_tick() < expected.current_tick(),
            "checkpoint is not earlier than reference future");
    resumed.run_until(expected.current_tick());
    require(resumed.raw_copy() == expected.raw_copy(), "RAW future differs");
    require(resumed.clock_copy() == expected.clock_copy(), "clock future differs");
    compare_receipts(resumed.receipts(), expected.receipts());
    require(resumed.protocol_phase() == expected.protocol_phase(),
            "protocol phase differs");
    std::cout << "cpp_consume raw_clock_receipts_exact=true tick="
              << resumed.current_tick() << '\n';
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 4) {
            std::cerr << "usage: dee_cross_language_bridge produce|consume "
                         "CHECKPOINT FUTURE\n";
            return 2;
        }
        const std::string mode = argv[1];
        if (mode == "produce") return produce(argv[2], argv[3]);
        if (mode == "consume") return consume(argv[2], argv[3]);
        std::cerr << "unknown mode: " << mode << '\n';
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "cross-language bridge error: " << error.what() << '\n';
        return 1;
    }
}
