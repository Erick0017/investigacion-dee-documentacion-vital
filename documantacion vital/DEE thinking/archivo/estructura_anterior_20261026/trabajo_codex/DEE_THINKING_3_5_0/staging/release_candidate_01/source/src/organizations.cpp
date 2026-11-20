#include "dee_thinking/organizations.hpp"

#include <array>
#include <stdexcept>
#include <utility>

namespace dee::thinking {
namespace {

std::size_t idx(Coordinate q, int n) {
    return v27::linear_index(q.x, q.y, q.z, n);
}

Coordinate add(Coordinate q, Direction d, int count, int n) {
    return Coordinate{
        v27::wrap_coordinate(q.x + count * d.dx, n),
        v27::wrap_coordinate(q.y + count * d.dy, n),
        v27::wrap_coordinate(q.z + count * d.dz, n)};
}

void put(std::vector<std::uint64_t>& raw, std::vector<std::uint64_t>& clock,
         int n, Coordinate q, std::uint32_t state, std::uint16_t sreg,
         Direction direction = {}, std::uint8_t semantic = 1,
         std::uint64_t phase = 0) {
    const auto i = idx(q, n);
    if (raw[i] != 0) throw std::runtime_error("reference organization overlap");
    raw[i] = v27::pack_record(state, sreg, direction.dx, direction.dy, direction.dz, semantic);
    clock[i] = phase;
}

Coordinate source_for(Coordinate target, std::uint64_t tick, Direction direction, int n) {
    return add(target, direction, -static_cast<int>(tick), n);
}

struct HistoryBuild {
    Runtime runtime;
    Coordinate center;
};

HistoryBuild build_history(int n, Coordinate center, HistoryMode mode) {
    const auto total = static_cast<std::size_t>(n) * n * n;
    std::vector<std::uint64_t> raw(total, 0), clock(total, 0);
    const Direction axis{1, 0, 0};
    const auto a = add(center, Direction{-1, 0, 0}, 1, n);
    const auto b = add(center, axis, 1, n);
    put(raw, clock, n, a, 1000, 100, {}, 1, 260);
    put(raw, clock, n, b, 2000, 100, {}, 1, 260);
    constexpr std::array<Direction, 4> pattern_a{{
        {-1, 0, 0}, {-1, 1, 1}, {0, 0, 1}, {0, 1, 0}}};
    constexpr std::array<Direction, 4> pattern_b{{
        {0, -1, 0}, {0, 0, -1}, {1, -1, -1}, {1, 0, 0}}};
    for (std::size_t i = 0; i < pattern_a.size(); ++i) {
        put(raw, clock, n, add(a, pattern_a[i], 1, n), 3000 + static_cast<std::uint32_t>(i), 0, {}, 4, 31 + i);
        put(raw, clock, n, add(b, pattern_b[i], 1, n), 4000 + static_cast<std::uint32_t>(i), 0, {}, 4, 41 + i);
    }
    auto install = [&](Coordinate memory, Direction offset, Direction direction,
                       bool early, std::uint32_t state) {
        const auto target = add(memory, offset, 1, n);
        if (early) put(raw, clock, n, target, state, 0, direction, 1, 17);
        else put(raw, clock, n, add(target, direction, -1, n), 0, 0, direction, 1, 19);
    };
    if (mode == HistoryMode::HA) {
        install(a, Direction{0, -1, 0}, Direction{0, 0, -1}, true, 5000);
        install(b, Direction{0, 1, 0}, Direction{0, 0, 1}, false, 5001);
    } else if (mode == HistoryMode::HB) {
        install(a, Direction{0, -1, 0}, Direction{0, 0, -1}, false, 5000);
        install(b, Direction{0, 1, 0}, Direction{0, 0, 1}, true, 5001);
    }
    const auto reader = add(center, Direction{0, -2, 0}, 1, n);
    put(raw, clock, n, reader, 6000, 7, Direction{0, 1, 0}, 4, 23);
    Runtime runtime = Runtime::import_research_state(n, 0, std::move(raw), std::move(clock));
    runtime.set_protocol_phase("history_initialized");
    return HistoryBuild{std::move(runtime), center};
}

}  // namespace

ReferenceWorld make_transport_world(bool occupied_destination) {
    constexpr int n = 17;
    std::vector<std::uint64_t> raw(static_cast<std::size_t>(n) * n * n, 0);
    std::vector<std::uint64_t> clock(raw.size(), 0);
    const Coordinate input{2, 8, 8};
    const Coordinate destination{7, 8, 8};
    if (occupied_destination) put(raw, clock, n, destination, 7000, 3, {}, 4, 29);
    Runtime runtime = Runtime::import_research_state(n, 0, std::move(raw), std::move(clock));
    runtime.register_channel(ChannelSpec{"carrier", input, 1, Direction{1, 0, 0}, 1, true, false});
    runtime.register_channel(ChannelSpec{"probe", Coordinate{2, 9, 8}, 1, Direction{1, 0, 0}, 1, false, true});
    runtime.set_protocol_phase("transport_ready");
    return ReferenceWorld{std::move(runtime), {{"input", input}, {"destination", destination}},
                          "A carrier submitted at boundary 0 reaches destination after five transitions."};
}

ReferenceWorld make_relational_learning_world() {
    // CORE06 C6H01 F0_T0: the paired cue/teacher encounter at t=3 writes
    // a mobile relation.  A later cue at boundary 6 meets that relation at
    // t=11.  All carriers are admitted through the public event contract.
    constexpr int n = 34;
    std::vector<std::uint64_t> raw(static_cast<std::size_t>(n) * n * n, 0);
    std::vector<std::uint64_t> clock(raw.size(), 0);
    const Coordinate junction{10, 18, 14};
    const Coordinate response{10, 26, 14};
    Runtime runtime = Runtime::import_research_state(n, 0, std::move(raw), std::move(clock));
    runtime.register_channel(ChannelSpec{"cue_train", Coordinate{13, 18, 14}, 1, Direction{-1, 0, 0}, 1, true, false});
    runtime.register_channel(ChannelSpec{"teacher", Coordinate{7, 15, 14}, 1, Direction{1, 1, 0}, 1, true, false});
    runtime.register_channel(ChannelSpec{"query", Coordinate{15, 26, 14}, 1, Direction{-1, 0, 0}, 1, true, true});
    runtime.set_protocol_phase("reprogramming_ready");
    return ReferenceWorld{std::move(runtime),
                          {{"training_junction", junction}, {"response", response}},
                          "cue_train(load=5)+teacher(load=7) at boundary 0; query(load=11) at boundary 6; observe response at boundary 11. Omit teacher for the causal control."};
}

ReferenceWorld make_reprogramming_world() {
    return make_relational_learning_world();
}

ReferenceWorld make_history_world(HistoryMode mode) {
    constexpr int n = 31;
    const Coordinate center{15, 15, 15};
    auto build = build_history(n, center, mode);
    return ReferenceWorld{std::move(build.runtime),
                          {{"comparator", center}, {"reader", Coordinate{15, 14, 15}}},
                          "HA and HB use the same inventory with early/late order exchanged; observe at common age."};
}

ReferenceWorld make_recurrence_multichannel_world(HistoryMode mode) {
    constexpr int n = 127;
    const Coordinate origin{30, 30, 30};
    auto build = build_history(n, origin, mode);
    Runtime runtime = std::move(build.runtime);
    auto raw = runtime.raw_copy();
    auto clock = runtime.clock_copy();
    const Direction p{1, 0, 0};
    const Direction s1{-1, 1, 0}, s2{-1, -1, 0};
    const Direction n1{1, 0, 1}, n2{1, 0, -1};
    const Coordinate consequence = add(origin, Direction{1, 1, 0}, 3, n);
    const Coordinate redirect = add(consequence, Direction{1, -1, 0}, 2, n);
    const Coordinate q = add(redirect, p, 4, n);
    const Coordinate qp = add(q, p, 1, n);
    put(raw, clock, n, source_for(redirect, 8, Direction{0, 1, 0}, n), 90010, 0, Direction{0, 1, 0});
    put(raw, clock, n, q, 1, 7, p, 1, 11);
    put(raw, clock, n, add(qp, s1, -1, n), 91000, 11, s1, 4, 100000);
    put(raw, clock, n, add(qp, s2, -1, n), 91001, 13, s2, 4, 100001);
    put(raw, clock, n, add(q, n1, -2, n), 91002, 17, n1, 4, 100002);
    put(raw, clock, n, add(q, n2, -2, n), 91003, 19, n2, 4, 100003);
    runtime = Runtime::import_research_state(n, 0, std::move(raw), std::move(clock));
    runtime.register_channel(ChannelSpec{"A", source_for(consequence, 6, Direction{0, -1, 1}, n), 90001, Direction{0, -1, 1}, 1, true, false});
    runtime.register_channel(ChannelSpec{"B", source_for(consequence, 6, Direction{0, -1, -1}, n), 90002, Direction{0, -1, -1}, 1, true, false});
    runtime.register_channel(ChannelSpec{"C", source_for(consequence, 6, Direction{0, -1, 0}, n), 90003, Direction{0, -1, 0}, 1, true, false});
    runtime.register_channel(ChannelSpec{"cut_link", source_for(redirect, 8, Direction{0, 0, 1}, n), 90020, Direction{0, 0, 1}, 1, true, false});
    runtime.set_protocol_phase("recurrence_multichannel_ready");
    return ReferenceWorld{std::move(runtime),
                          {{"consequence", consequence}, {"redirect", redirect}, {"q", q}, {"qp", qp}},
                          "Submit A/B/C at boundary 0; AB reaches the fixed recurrence port in HA. cut_link is a declared causal intervention."};
}

}  // namespace dee::thinking
