#include "dee_thinking/runtime.hpp"
#include "test_support.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

using dee::thinking::ChannelSpec;
using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::EventKind;
using dee::thinking::EventStatus;
using dee::thinking::InputRequest;
using dee::thinking::Runtime;

namespace {

std::size_t index(Coordinate q, int n) {
    return dee::v27::linear_index(q.x, q.y, q.z, n);
}

ChannelSpec channel(std::string name, Coordinate site, Direction direction = {1, 0, 0},
                    std::uint8_t semantic = 1, bool experience = true, bool probe = false) {
    return ChannelSpec{std::move(name), site, 1, direction, semantic, experience, probe};
}

void check_same_world(dee::thinking::test::Suite& suite, const Runtime& a, const Runtime& b) {
    DEE_CHECK_EQ(suite, a.dimension(), b.dimension());
    DEE_CHECK_EQ(suite, a.current_tick(), b.current_tick());
    DEE_CHECK_EQ(suite, a.paused(), b.paused());
    DEE_CHECK_EQ(suite, a.protocol_phase(), b.protocol_phase());
    DEE_CHECK_EQ(suite, a.channel_names(), b.channel_names());
    DEE_CHECK_EQ(suite, a.raw_copy(), b.raw_copy());
    DEE_CHECK_EQ(suite, a.clock_copy(), b.clock_copy());
    DEE_CHECK_EQ(suite, a.receipts().size(), b.receipts().size());
}

}  // namespace

int main() {
    dee::thinking::test::Suite suite("runtime_tests");

    // Packed state is exact, including signed direction nibbles and state-zero RAW.
    const auto packed = dee::v27::pack_record(0x89abcdefU, 0x4321U, -8, 7, -1, 0xAU);
    const auto decoded = dee::v27::decode_record(packed);
    DEE_CHECK_EQ(suite, decoded.state, 0x89abcdefU);
    DEE_CHECK_EQ(suite, decoded.s_reg, 0x4321U);
    DEE_CHECK_EQ(suite, decoded.dx, -8);
    DEE_CHECK_EQ(suite, decoded.dy, 7);
    DEE_CHECK_EQ(suite, decoded.dz, -1);
    DEE_CHECK_EQ(suite, decoded.semantic, 0xAU);
    DEE_CHECK(suite, decoded.raw_present());
    DEE_CHECK(suite, decoded.occupied());

    const auto state_zero_raw = dee::v27::pack_record(0, 0, 1, 0, 0, 1);
    const auto state_zero = dee::v27::decode_record(state_zero_raw);
    DEE_CHECK(suite, state_zero.raw_present());
    DEE_CHECK(suite, !state_zero.occupied());

    // advance(0) is a strict no-op and does not apply boundary events.
    Runtime zero(7);
    zero.register_channel(channel("in", {1, 1, 1}));
    const auto zero_event = zero.experience("in", 0, 9);
    const auto raw_before_zero = zero.raw_copy();
    const auto clock_before_zero = zero.clock_copy();
    const auto zero_info = zero.advance(0);
    DEE_CHECK_EQ(suite, zero.current_tick(), 0ULL);
    DEE_CHECK_EQ(suite, zero.raw_copy(), raw_before_zero);
    DEE_CHECK_EQ(suite, zero.clock_copy(), clock_before_zero);
    DEE_CHECK_EQ(suite, zero_info.evaluated, 0ULL);
    DEE_CHECK_EQ(suite, zero.receipt(zero_event.id)->status, EventStatus::Scheduled);
    zero.advance(1);
    DEE_CHECK_EQ(suite, zero.current_tick(), 1ULL);
    DEE_CHECK_EQ(suite, zero.receipt(zero_event.id)->status, EventStatus::Applied);
    DEE_CHECK_EQ(suite, *zero.receipt(zero_event.id)->effective_tick, 0ULL);

    // run_until stops at the requested boundary; an event at that boundary remains pending.
    Runtime boundary(7);
    boundary.register_channel(channel("at3", {1, 2, 2}));
    const auto boundary_event = boundary.experience("at3", 3, 4);
    boundary.run_until(3);
    DEE_CHECK_EQ(suite, boundary.current_tick(), 3ULL);
    DEE_CHECK_EQ(suite, boundary.receipt(boundary_event.id)->status, EventStatus::Scheduled);
    boundary.advance(1);
    DEE_CHECK_EQ(suite, boundary.receipt(boundary_event.id)->status, EventStatus::Applied);
    DEE_CHECK_EQ(suite, *boundary.receipt(boundary_event.id)->effective_tick, 3ULL);
    DEE_CHECK_THROWS(suite, boundary.run_until(2));

    // One call and repeated one-tick calls are exactly equivalent.
    Runtime block_a(9);
    block_a.register_channel(channel("a", {1, 4, 4}));
    block_a.register_channel(channel("b", {7, 3, 4}, {-1, 0, 0}));
    block_a.experience("a", 0, 7);
    block_a.experience("b", 2, 11);
    Runtime block_b = block_a.fork();
    block_a.advance(6);
    for (int i = 0; i < 6; ++i) block_b.advance(1);
    check_same_world(suite, block_a, block_b);

    // Pause is explicit and does not mutate state; resume continues the same trajectory.
    Runtime paused = block_a.fork();
    const auto paused_raw = paused.raw_copy();
    const auto paused_clock = paused.clock_copy();
    paused.pause();
    DEE_CHECK_THROWS(suite, paused.advance(1));
    DEE_CHECK_EQ(suite, paused.raw_copy(), paused_raw);
    DEE_CHECK_EQ(suite, paused.clock_copy(), paused_clock);
    paused.resume();
    paused.advance(1);
    DEE_CHECK_EQ(suite, paused.current_tick(), block_a.current_tick() + 1);

    // Observation and metrics are passive.
    Runtime observed = block_a.fork();
    const auto observed_raw = observed.raw_copy();
    const auto observed_clock = observed.clock_copy();
    const auto observed_tick = observed.current_tick();
    (void)observed.observe({0, 0, 0});
    (void)observed.observe_many({{0, 0, 0}, {1, 1, 1}});
    (void)observed.metrics();
    DEE_CHECK_EQ(suite, observed.current_tick(), observed_tick);
    DEE_CHECK_EQ(suite, observed.raw_copy(), observed_raw);
    DEE_CHECK_EQ(suite, observed.clock_copy(), observed_clock);

    // Admission is checked at the application boundary. Conflicting simultaneous events
    // are rejected symmetrically, while a multi-write batch is atomic.
    Runtime admission(7);
    admission.register_channel(channel("shared_a", {2, 2, 2}));
    admission.register_channel(channel("shared_b", {2, 2, 2}, {0, 1, 0}));
    admission.register_channel(channel("other", {4, 4, 4}));
    const auto conflict_a = admission.experience("shared_a", 0, 1);
    const auto conflict_b = admission.experience("shared_b", 0, 2);
    admission.advance(1);
    DEE_CHECK_EQ(suite, admission.receipt(conflict_a.id)->status, EventStatus::RejectedConflict);
    DEE_CHECK_EQ(suite, admission.receipt(conflict_b.id)->status, EventStatus::RejectedConflict);

    Runtime atomic(7);
    atomic.register_channel(channel("x", {1, 1, 1}));
    atomic.register_channel(channel("y", {1, 1, 1}, {0, 1, 0}));
    const auto duplicate_batch = atomic.experience_batch({{"x", 1}, {"y", 2}}, 0);
    DEE_CHECK_EQ(suite, duplicate_batch.status, EventStatus::RejectedConflict);
    DEE_CHECK_EQ(suite, atomic.receipts().size(), 1ULL);
    DEE_CHECK_EQ(suite, atomic.raw_copy(), std::vector<std::uint64_t>(343, 0));

    Runtime occupied(7);
    std::vector<std::uint64_t> occupied_raw(343, 0), occupied_clock(343, 0);
    occupied_raw[index({3, 3, 3}, 7)] = dee::v27::pack_record(12, 1, 0, 0, 0, 4);
    occupied = Runtime::import_research_state(7, 0, std::move(occupied_raw), std::move(occupied_clock));
    occupied.register_channel(channel("occupied", {3, 3, 3}));
    const auto occupied_event = occupied.experience("occupied", 0, 5);
    occupied.advance(1);
    DEE_CHECK_EQ(suite, occupied.receipt(occupied_event.id)->status, EventStatus::RejectedOccupied);
    const auto late = occupied.experience("occupied", 0, 5);
    DEE_CHECK_EQ(suite, late.status, EventStatus::RejectedLate);
    const auto invalid = occupied.experience("missing", 1, 5);
    DEE_CHECK_EQ(suite, invalid.status, EventStatus::RejectedInvalid);

    // Boundary writes preserve the pre-existing clock word. An observer insertion makes
    // the preservation directly visible after one tick: 123 -> 124, not 0 -> 1.
    std::vector<std::uint64_t> phase_raw(343, 0), phase_clock(343, 0);
    phase_clock[index({3, 3, 3}, 7)] = 123;
    Runtime phase = Runtime::import_research_state(7, 0, std::move(phase_raw), std::move(phase_clock));
    phase.register_channel(channel("phase", {3, 3, 3}, {0, 0, 0}, 4));
    phase.experience("phase", 0, 6);
    phase.advance(1);
    DEE_CHECK_EQ(suite, phase.observe({3, 3, 3}).clock, 124ULL);
    DEE_CHECK_EQ(suite, phase.observe({3, 3, 3}).record.s_reg, 6);

    // Probe events remain identifiable in receipts and require explicit channel permission.
    Runtime probes(7);
    probes.register_channel(channel("probe", {2, 3, 3}, {1, 0, 0}, 1, false, true));
    const auto probe = probes.probe("probe", 0, 8);
    DEE_CHECK_EQ(suite, probe.kind, EventKind::Probe);
    probes.advance(1);
    DEE_CHECK_EQ(suite, probes.receipt(probe.id)->status, EventStatus::Applied);
    DEE_CHECK_EQ(suite, probes.receipt(probe.id)->kind, EventKind::Probe);
    const auto disallowed = probes.experience("probe", 1, 8);
    DEE_CHECK_EQ(suite, disallowed.status, EventStatus::RejectedInvalid);

    // RAW-present/state-zero is a first-class distinction.  This directional
    // record is not occupied at t0, yet it is a causal transport proposal and
    // therefore produces an occupied destination at t1.
    std::vector<std::uint64_t> raw_zero(343, 0), clock_zero(343, 0);
    raw_zero[index({1, 1, 1}, 7)] = state_zero_raw;
    Runtime raw_zero_world = Runtime::import_research_state(
        7, 0, std::move(raw_zero), std::move(clock_zero));
    DEE_CHECK_EQ(suite, raw_zero_world.metrics().raw_support, 1ULL);
    DEE_CHECK_EQ(suite, raw_zero_world.metrics().occupied, 0ULL);
    raw_zero_world.advance(1);
    DEE_CHECK_EQ(suite, raw_zero_world.metrics().raw_support, 1ULL);
    DEE_CHECK_EQ(suite, raw_zero_world.metrics().occupied, 1ULL);
    const auto transported_state_zero = raw_zero_world.observe({2, 1, 1}).record;
    DEE_CHECK_EQ(suite, transported_state_zero.state, 1U);
    DEE_CHECK_EQ(suite, transported_state_zero.dx, 1);

    // Forks and wholly separate worlds do not alias buffers or queues.
    Runtime parent(7);
    parent.register_channel(channel("fork_input", {1, 1, 1}));
    Runtime child = parent.fork();
    child.experience("fork_input", 0, 3);
    child.advance(2);
    DEE_CHECK_EQ(suite, parent.current_tick(), 0ULL);
    DEE_CHECK_EQ(suite, parent.metrics().raw_support, 0ULL);
    DEE_CHECK(suite, child.metrics().raw_support != 0);
    Runtime independent_a(5), independent_b(5);
    independent_a.register_channel(channel("only_a", {1, 1, 1}));
    independent_a.experience("only_a", 0, 3);
    independent_a.advance(1);
    DEE_CHECK_EQ(suite, independent_b.current_tick(), 0ULL);
    DEE_CHECK_EQ(suite, independent_b.metrics().raw_support, 0ULL);

    // Snapshot round-trip includes queue, receipts, channels, phase, clock and RAW. The
    // resumed trajectory must remain bit-exact after pending events become effective.
    const auto temp = std::filesystem::temp_directory_path() / "dee_thinking_runtime_test.snapshot";
    const auto corrupt = std::filesystem::temp_directory_path() / "dee_thinking_runtime_test_corrupt.snapshot";
    std::error_code remove_error;
    std::filesystem::remove(temp, remove_error);
    std::filesystem::remove(corrupt, remove_error);
    Runtime checkpoint(9);
    checkpoint.register_channel(channel("now", {1, 1, 1}));
    checkpoint.register_channel(channel("later", {7, 7, 7}, {-1, 0, 0}));
    checkpoint.set_protocol_phase("mid_protocol");
    checkpoint.experience("now", 0, 4);
    checkpoint.experience("later", 3, 6);
    checkpoint.advance(1);
    checkpoint.save_snapshot(temp.string());
    Runtime resumed = Runtime::load_snapshot(temp.string());
    check_same_world(suite, checkpoint, resumed);
    checkpoint.advance(6);
    resumed.advance(6);
    check_same_world(suite, checkpoint, resumed);

    // A corrupt restore is rejected before replacing the live runtime.
    {
        std::ifstream input(temp, std::ios::binary);
        std::vector<char> bytes((std::istreambuf_iterator<char>(input)), {});
        DEE_CHECK(suite, !bytes.empty());
        bytes[bytes.size() / 2] ^= 0x5A;
        std::ofstream output(corrupt, std::ios::binary | std::ios::trunc);
        output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    }
    const auto resumed_raw = resumed.raw_copy();
    const auto resumed_clock = resumed.clock_copy();
    const auto resumed_tick = resumed.current_tick();
    DEE_CHECK_THROWS(suite, resumed.restore_snapshot(corrupt.string()));
    DEE_CHECK_EQ(suite, resumed.current_tick(), resumed_tick);
    DEE_CHECK_EQ(suite, resumed.raw_copy(), resumed_raw);
    DEE_CHECK_EQ(suite, resumed.clock_copy(), resumed_clock);
    std::filesystem::remove(temp, remove_error);
    std::filesystem::remove(corrupt, remove_error);

    return suite.finish();
}
