#include "h2_destination_repertoires_candidate.hpp"

#include <algorithm>
#include <numeric>
#include <stdexcept>

namespace dee::thinking::candidates::h2 {
namespace {

constexpr Direction kCue{1, 0, 0}, kTeacherY{-1, 1, 0}, kTeacherZ{-1, 0, 1};
constexpr Direction kMoveY{0, 1, 0}, kMoveZ{0, 0, 1}, kQuery{1, 0, 0};

Coordinate add(Coordinate q, Direction d, int k, int n) {
    return {v27::wrap_coordinate(q.x + k * d.dx, n),
            v27::wrap_coordinate(q.y + k * d.dy, n),
            v27::wrap_coordinate(q.z + k * d.dz, n)};
}

Coordinate add_coordinate(Coordinate q, Coordinate d, int n) {
    return {v27::wrap_coordinate(q.x + d.x, n),
            v27::wrap_coordinate(q.y + d.y, n),
            v27::wrap_coordinate(q.z + d.z, n)};
}

std::size_t at(Coordinate q, int n) { return v27::linear_index(q.x, q.y, q.z, n); }

void place(std::vector<std::uint64_t>& raw, std::vector<std::uint64_t>& clock,
           Coordinate target, int tick, Direction d, std::uint16_t sreg,
           std::uint32_t state, std::uint64_t phase, int n) {
    const auto q = add(target, d, -tick, n);
    const auto i = at(q, n);
    if (raw[i] != 0) throw std::invalid_argument("C7H02 candidate initial overlap");
    raw[i] = v27::pack_record(state, sreg, d.dx, d.dy, d.dz, 1);
    clock[i] = phase;
}

void inject(std::vector<std::uint64_t>& raw, std::vector<std::uint64_t>& scratch,
            std::vector<std::uint64_t>& clock, std::vector<std::uint64_t>& clock_scratch,
            Coordinate q, Direction d, std::uint16_t sreg, std::uint32_t state,
            std::uint64_t phase, int n) {
    const auto i = at(q, n);
    if (raw[i] != 0) throw std::runtime_error("C7H02 candidate occupied injection port");
    const auto value = v27::pack_record(state, sreg, d.dx, d.dy, d.dz, 1);
    raw[i] = scratch[i] = value;
    clock[i] = clock_scratch[i] = phase;
}

std::size_t support(const std::vector<std::uint64_t>& raw) {
    return static_cast<std::size_t>(std::count_if(raw.begin(), raw.end(), [](auto x) { return x != 0; }));
}

std::uint64_t sreg_sum(const std::vector<std::uint64_t>& raw) {
    return std::accumulate(raw.begin(), raw.end(), std::uint64_t{}, [](auto sum, auto x) {
        return sum + v27::decode_record(x).s_reg;
    });
}

}  // namespace

SeparatedResult run_separated(const SeparatedConfig& c, v27::TickOptions options) {
    if (c.dimension < 79 || c.channels < 1 || c.channels > 40 || c.delta_cycle.empty() ||
        c.training_tick < 1 || c.query_path < 1 || c.query_tick <= c.training_tick ||
        c.query_tick - c.query_path < c.training_tick || 2LL * c.query_tick >= c.dimension) {
        throw std::invalid_argument("invalid separated C7H02 configuration");
    }
    const int maximum_x = 25 + std::min<int>(10, static_cast<int>(c.channels) - 1);
    if (c.base_offset <= maximum_x ||
        static_cast<unsigned>(c.query_base) + c.channels - 1 > v27::kReducerCap) {
        throw std::invalid_argument("separated C7H02 loads leave the documented unsaturated sector");
    }
    for (std::size_t i = 0; i < c.channels; ++i) {
        const int x = 25 + static_cast<int>(i % 11);
        const int delta = c.delta_cycle[i % c.delta_cycle.size()];
        const int query = static_cast<int>(c.query_base) + static_cast<int>(i);
        if (x + delta < 0 || x + delta > static_cast<int>(v27::kReducerCap) ||
            static_cast<int>(c.base_offset) + delta + query < 0 ||
            static_cast<int>(c.base_offset) + delta + query > static_cast<int>(v27::kReducerCap)) {
            throw std::invalid_argument("separated C7H02 component or response would underflow/saturate");
        }
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension * c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total), clock_scratch(total);
    struct Channel { Coordinate target; Coordinate port; int delta; std::uint16_t query; };
    std::vector<Channel> channels;
    for (std::size_t i = 0; i < c.channels; ++i) {
        Coordinate base{5 + 10 * static_cast<int>(i % 8), 11,
                        7 + 14 * static_cast<int>(i / 8)};
        const auto junction = add_coordinate(base, c.translation, c.dimension);
        const int x = 25 + static_cast<int>(i % 11);
        const int delta = c.delta_cycle[i % c.delta_cycle.size()];
        const auto query = static_cast<std::uint16_t>(c.query_base + i);
        place(raw, clock, junction, c.training_tick, kCue,
              static_cast<std::uint16_t>(c.base_offset - x), 1000U + static_cast<std::uint32_t>(i),
              100U + i, c.dimension);
        place(raw, clock, junction, c.training_tick, kTeacherY,
              static_cast<std::uint16_t>(x + delta), 2000U + static_cast<std::uint32_t>(i),
              200U + i, c.dimension);
        const auto target = add(junction, kMoveY, c.query_tick - c.training_tick, c.dimension);
        channels.push_back({target, add(target, kQuery, -c.query_path, c.dimension), delta, query});
    }
    scratch = raw; clock_scratch = clock;
    const auto initial_support = support(raw);
    const auto initial_sreg = sreg_sum(raw);
    std::size_t trained_support{}, injected_support{}, final_support{};
    std::uint64_t final_sreg{};
    SeparatedResult result;
    for (int tick = 0; tick <= c.query_tick; ++tick) {
        if (tick == c.training_tick) trained_support = support(raw);
        if (tick == c.query_tick - c.query_path) {
            result.ports_empty = std::all_of(channels.begin(), channels.end(), [&](const auto& x) {
                return raw[at(x.port, c.dimension)] == 0;
            });
            for (std::size_t i = 0; i < channels.size(); ++i) {
                inject(raw, scratch, clock, clock_scratch, channels[i].port, kQuery,
                       channels[i].query, 3000U + static_cast<std::uint32_t>(i), 300U + i, c.dimension);
            }
            injected_support = support(raw);
        }
        if (tick == c.query_tick) {
            for (const auto& channel : channels) {
                const auto r = v27::decode_record(raw[at(channel.target, c.dimension)]);
                const auto expected = static_cast<std::uint16_t>(c.base_offset + channel.delta + channel.query);
                if (r.raw != 0 && r.dx == 1 && r.dy == 1 && r.dz == 0 && r.s_reg == expected) {
                    ++result.exact_channels;
                }
            }
            final_support = support(raw);
            final_sreg = sreg_sum(raw);
        }
        if (tick < c.query_tick) v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    result.all_exact = result.exact_channels == c.channels;
    result.training_budget_exact = initial_support - trained_support == c.channels;
    result.read_budget_exact = injected_support - final_support == c.channels;
    std::uint64_t queries{};
    for (const auto& x : channels) queries += x.query;
    result.sreg_accounting_exact = final_sreg == initial_sreg + queries;
    result.final_raw = std::move(raw); result.final_clock = std::move(clock);
    return result;
}

OverlapResult run_overlap(const OverlapConfig& c, v27::TickOptions options) {
    if (c.dimension < 45 || c.index < 0 || c.training_tick < 1 ||
        c.merge_tick <= c.training_tick || c.query_tick <= c.merge_tick ||
        c.query_tick - 4 < c.merge_tick || 2LL * c.query_tick >= c.dimension ||
        c.base_offset <= 21) {
        throw std::invalid_argument("invalid overlap C7H02 configuration");
    }
    const int component_y = 12 + c.deltas[0];
    const int component_z = 21 + c.deltas[1];
    const int merged_load = 2 * static_cast<int>(c.base_offset) + c.deltas[0] + c.deltas[1];
    const int response_load = merged_load + c.query;
    if (component_y < 0 || component_z < 0 || merged_load < 0 ||
        response_load > static_cast<int>(v27::kReducerCap)) {
        throw std::invalid_argument("overlap C7H02 loads leave the documented unsaturated sector");
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension * c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total), clock_scratch(total);
    const Coordinate merge{(17 + 6 * c.index) % c.dimension,
                           (19 + 9 * c.index) % c.dimension,
                           (23 + 11 * c.index) % c.dimension};
    auto jy = add(merge, kMoveY, -(c.merge_tick - c.training_tick), c.dimension);
    auto jz = add(merge, kMoveZ, -(c.merge_tick - c.training_tick), c.dimension);
    if (c.off_fiber) jz = add(jz, Direction{1, 0, 0}, 3, c.dimension);
    const std::array<Coordinate, 2> junctions{jy, jz};
    const std::array<Direction, 2> teachers{kTeacherY, kTeacherZ};
    const std::array<int, 2> xs{12, 21};
    for (std::size_t i = 0; i < 2; ++i) {
        place(raw, clock, junctions[i], c.training_tick, kCue,
              static_cast<std::uint16_t>(c.base_offset - xs[i]), 4000U + i, 400U + i, c.dimension);
        place(raw, clock, junctions[i], c.training_tick, teachers[i],
              static_cast<std::uint16_t>(xs[i] + c.deltas[i]), 5000U + i, 500U + i, c.dimension);
    }
    scratch = raw; clock_scratch = clock;
    const Direction merged_direction{0, 1, 1};
    const auto receiver = add(merge, merged_direction, c.query_tick - c.merge_tick, c.dimension);
    const auto port = add(receiver, kQuery, -4, c.dimension);
    OverlapResult result;
    const auto expected_merge = static_cast<std::uint16_t>(2 * c.base_offset + c.deltas[0] + c.deltas[1]);
    const auto expected_response = static_cast<std::uint16_t>(expected_merge + c.query);
    for (int tick = 0; tick <= c.query_tick; ++tick) {
        if (tick == c.merge_tick) {
            const auto r = v27::decode_record(raw[at(merge, c.dimension)]);
            result.merge_exact = !c.off_fiber && r.raw != 0 && r.dx == 0 && r.dy == 1 &&
                                 r.dz == 1 && r.s_reg == expected_merge;
            result.false_merge = c.off_fiber && r.raw != 0 && r.dx == 0 && r.dy == 1 &&
                                 r.dz == 1 && r.s_reg == expected_merge;
        }
        if (tick == c.query_tick - 4 && !c.off_fiber) {
            result.port_empty = raw[at(port, c.dimension)] == 0;
            inject(raw, scratch, clock, clock_scratch, port, kQuery, c.query, 6000, 600, c.dimension);
        }
        if (tick == c.query_tick && !c.off_fiber) {
            const auto r = v27::decode_record(raw[at(receiver, c.dimension)]);
            result.composed_response_exact = r.raw != 0 && r.dx == 1 && r.dy == 1 &&
                                             r.dz == 1 && r.s_reg == expected_response;
            result.individual_identity = r.raw != 0 &&
                (static_cast<int>(r.s_reg) - c.base_offset == c.query + c.deltas[0] ||
                 static_cast<int>(r.s_reg) - c.base_offset == c.query + c.deltas[1]);
        }
        if (tick < c.query_tick) v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    result.final_raw = std::move(raw); result.final_clock = std::move(clock);
    return result;
}

}  // namespace dee::thinking::candidates::h2
