#include "dee_thinking/composition.hpp"

#include <algorithm>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using dee::thinking::EventReceipt;
using dee::thinking::EventStatus;
using dee::thinking::catalog::ComposedWorld;
using dee::thinking::catalog::CompositionPlanner;
using dee::thinking::catalog::ConnectionRecord;
using dee::thinking::catalog::OrganizationCatalog;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    if (!condition) fail(message);
}

CompositionPlanner persistence_plan(const OrganizationCatalog& catalog) {
    CompositionPlanner planner(34);
    planner.add(catalog.instantiate(
        {"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    planner.add(catalog.instantiate(
        {"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    planner.connect({{"learner", "learned_relation"},
                     {"reader", "relation_input"},
                     "cross-process learned relation"});
    return planner;
}

bool same_receipt(const EventReceipt& left, const EventReceipt& right) {
    return left.id == right.id &&
           left.kind == right.kind &&
           left.status == right.status &&
           left.requested_tick == right.requested_tick &&
           left.effective_tick == right.effective_tick &&
           left.channels == right.channels &&
           left.reason == right.reason;
}

bool same_connection(const ConnectionRecord& left, const ConnectionRecord& right) {
    return left.request.source.instance == right.request.source.instance &&
           left.request.source.port == right.request.source.port &&
           left.request.target.instance == right.request.target.instance &&
           left.request.target.port == right.request.target.port &&
           left.request.purpose == right.request.purpose &&
           left.verification == right.verification &&
           left.physical_contract == right.physical_contract;
}

void compare_receipts(const std::vector<EventReceipt>& actual,
                      const std::vector<EventReceipt>& expected) {
    require(actual.size() == expected.size(), "receipt count differs after process restart");
    for (std::size_t i = 0; i < actual.size(); ++i) {
        require(same_receipt(actual[i], expected[i]),
                "receipt differs after process restart at index " + std::to_string(i));
    }
}

void compare_connections(const ComposedWorld& actual, const ComposedWorld& expected) {
    require(actual.connections().size() == expected.connections().size(),
            "connection count differs after process restart");
    for (std::size_t i = 0; i < actual.connections().size(); ++i) {
        require(same_connection(actual.connections()[i], expected.connections()[i]),
                "connection differs after process restart at index " + std::to_string(i));
    }
    require(actual.manifest_json() == expected.manifest_json(),
            "canonical composition manifest differs after process restart");
}

int produce(const std::filesystem::path& checkpoint,
            const std::filesystem::path& future_reference) {
    OrganizationCatalog catalog;
    auto world = persistence_plan(catalog).build();
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 2});

    const auto training = world.experience_batch(
        {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0);
    require(training.status == EventStatus::Scheduled, "training batch was not scheduled");
    world.runtime().run_until(6);
    require(world.runtime().receipt(training.id).has_value() &&
                world.runtime().receipt(training.id)->status == EventStatus::Applied,
            "training batch was not applied before checkpoint");

    // This event is deliberately pending in the checkpoint. It is submitted
    // after the training trajectory has evolved, so persistence must retain
    // both its identity and its effective boundary without a caller-side plan.
    const auto pending = world.probe("reader", "query", world.runtime().current_tick(), 13);
    require(pending.status == EventStatus::Scheduled, "future query was not scheduled");
    world.save_snapshot(checkpoint.string());

    const auto persisted = world.runtime().receipt(pending.id);
    require(persisted.has_value() && persisted->status == EventStatus::Scheduled &&
                !persisted->effective_tick.has_value(),
            "checkpoint does not contain the pending event contract");

    world.runtime().run_until(11);
    const auto applied = world.runtime().receipt(pending.id);
    require(applied.has_value() && applied->status == EventStatus::Applied &&
                applied->effective_tick == std::optional<std::uint64_t>{6},
            "reference continuation did not apply the pending event at tick 6");
    world.save_snapshot(future_reference.string());

    std::cout << "producer checkpoint_tick=6 future_tick=11 pending_event_id="
              << pending.id << " connections=" << world.connections().size() << '\n';
    return 0;
}

int consume(const std::filesystem::path& checkpoint,
            const std::filesystem::path& future_reference) {
    // This process receives no planner or catalog manifest from process A.
    // Both worlds reconstruct themselves solely from the two self-contained
    // snapshots and the installed built-in catalog.
    auto resumed = ComposedWorld::load_snapshot(checkpoint.string());
    const auto expected = ComposedWorld::load_snapshot(future_reference.string());

    require(resumed.runtime().current_tick() == 6, "checkpoint tick is not 6");
    require(expected.runtime().current_tick() == 11, "reference future tick is not 11");
    require(resumed.organizations().size() == 2, "checkpoint organization count differs");
    compare_connections(resumed, expected);

    const auto checkpoint_receipts = resumed.runtime().receipts();
    const auto pending = std::find_if(
        checkpoint_receipts.begin(), checkpoint_receipts.end(),
        [](const EventReceipt& receipt) { return receipt.status == EventStatus::Scheduled; });
    require(pending != checkpoint_receipts.end(), "checkpoint has no pending event");
    require(!pending->effective_tick.has_value(), "pending event already has an effective tick");

    resumed.runtime().run_until(expected.runtime().current_tick());
    require(resumed.runtime().raw_copy() == expected.runtime().raw_copy(),
            "RAW differs from process A future reference");
    require(resumed.runtime().clock_copy() == expected.runtime().clock_copy(),
            "clock differs from process A future reference");
    compare_receipts(resumed.runtime().receipts(), expected.runtime().receipts());
    compare_connections(resumed, expected);

    const auto response_site = resumed.landmarks().at("reader.response");
    const auto response = resumed.runtime().observe(response_site);
    require(response.record.occupied() && response.record.s_reg == 25,
            "restored future lost the learned response");

    std::cout << "consumer restored_tick=11 raw_clock_exact=true event_exact=true "
                 "connection_exact=true response_s_reg="
              << response.record.s_reg << '\n';
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 4) {
            std::cerr << "usage: dee_cross_process_persistence "
                         "produce|consume CHECKPOINT FUTURE_REFERENCE\n";
            return 2;
        }
        const std::string mode = argv[1];
        if (mode == "produce") return produce(argv[2], argv[3]);
        if (mode == "consume") return consume(argv[2], argv[3]);
        std::cerr << "unknown mode: " << mode << '\n';
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "cross-process persistence error: " << error.what() << '\n';
        return 1;
    }
}
