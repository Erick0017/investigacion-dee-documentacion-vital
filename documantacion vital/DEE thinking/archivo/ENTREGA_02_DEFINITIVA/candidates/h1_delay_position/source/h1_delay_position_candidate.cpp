#include "h1_delay_position_candidate.hpp"

#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>

namespace dee::thinking::candidates::h1 {
namespace {

Coordinate add(Coordinate q, Direction d, int k, int n) {
    return {v27::wrap_coordinate(q.x + k * d.dx, n),
            v27::wrap_coordinate(q.y + k * d.dy, n),
            v27::wrap_coordinate(q.z + k * d.dz, n)};
}

std::size_t index(Coordinate q, int n) {
    return v27::linear_index(q.x, q.y, q.z, n);
}

Direction sign_sum(Direction a, Direction b) {
    const auto sign = [](int v) { return (v > 0) - (v < 0); };
    return {sign(a.dx + b.dx), sign(a.dy + b.dy), sign(a.dz + b.dz)};
}

bool is_cardinal(Direction d) {
    const int magnitude = std::abs(d.dx) + std::abs(d.dy) + std::abs(d.dz);
    return magnitude == 1 && std::abs(d.dx) <= 1 && std::abs(d.dy) <= 1 &&
           std::abs(d.dz) <= 1;
}

int dot(Direction a, Direction b) {
    return a.dx * b.dx + a.dy * b.dy + a.dz * b.dz;
}

void place(std::vector<std::uint64_t>& raw, std::vector<std::uint64_t>& clock,
           Coordinate q, std::uint32_t state, std::uint16_t sreg, Direction d,
           std::uint64_t phase, int n) {
    const auto at = index(q, n);
    if (raw[at] != 0) throw std::invalid_argument("candidate source overlap");
    raw[at] = v27::pack_record(state, sreg, d.dx, d.dy, d.dz, 1);
    clock[at] = phase;
}

}  // namespace

RunResult run(const Config& c, v27::TickOptions options) {
    if (c.dimension < 3 || c.labels.empty() || c.channel_spacing < 1 ||
        c.base_path_length < 1 ||
        std::find(c.labels.begin(), c.labels.end(), c.input_delta) == c.labels.end()) {
        throw std::invalid_argument("invalid NRH05 candidate configuration");
    }
    if (std::set<int>(c.labels.begin(), c.labels.end()).size() != c.labels.size()) {
        throw std::invalid_argument("NRH05 labels must be unique");
    }
    if (!is_cardinal(c.target_direction) || !is_cardinal(c.probe_direction) ||
        !is_cardinal(c.separation) || dot(c.target_direction, c.probe_direction) != 0) {
        throw std::invalid_argument("NRH05 requires orthogonal cardinal proposal directions and a cardinal bank axis");
    }
    if (c.states[0] == 0 || c.states[1] == 0 ||
        static_cast<unsigned>(c.sregs[0]) + c.sregs[1] > v27::kReducerCap) {
        throw std::invalid_argument("NRH05 candidate states/s_reg leave the documented positive unsaturated sector");
    }
    int max_abs_label = 0;
    for (const int label : c.labels) {
        if (c.base_path_length + label < 1) {
            throw std::invalid_argument("NRH05 path length must stay positive for every label");
        }
        max_abs_label = std::max(max_abs_label, std::abs(label));
    }
    const auto bank_span = static_cast<long long>(c.labels.size() - 1) * c.channel_spacing;
    const int horizon = c.base_path_length + max_abs_label + 3;
    if (bank_span >= c.dimension || 2LL * horizon >= c.dimension) {
        throw std::invalid_argument("NRH05 candidate geometry would wrap within the declared measurement horizon");
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension * c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total), clock_scratch(total);
    std::vector<Coordinate> hubs;
    hubs.reserve(c.labels.size());
    auto calibration = c.labels;
    if (c.arm == Arm::ReversedCalibration) std::reverse(calibration.begin(), calibration.end());
    for (std::size_t i = 0; i < c.labels.size(); ++i) {
        const auto hub = add(c.base, c.separation,
                             static_cast<int>(i) * c.channel_spacing, c.dimension);
        hubs.push_back(hub);
        place(raw, clock,
              add(hub, c.probe_direction, -(c.base_path_length + calibration[i]), c.dimension),
              c.states[1], c.sregs[1], c.probe_direction, c.clocks[1], c.dimension);
        if (c.arm != Arm::TargetAbsent) {
            place(raw, clock,
                  add(hub, c.target_direction, -(c.base_path_length + c.input_delta), c.dimension),
                  c.states[0], c.sregs[0], c.target_direction, c.clocks[0], c.dimension);
        }
    }
    scratch = raw;
    clock_scratch = clock;
    RunResult result;
    result.initial_hubs_empty = std::all_of(hubs.begin(), hubs.end(), [&](Coordinate q) {
        return raw[index(q, c.dimension)] == 0;
    });
    const auto out_direction = sign_sum(c.target_direction, c.probe_direction);
    const auto out_sreg = static_cast<std::uint16_t>(
        std::min<unsigned>(static_cast<unsigned>(c.sregs[0]) + c.sregs[1], v27::kReducerCap));
    std::set<int> active;
    for (int tick = 0; tick <= horizon; ++tick) {
        for (std::size_t i = 0; i < hubs.size(); ++i) {
            const auto record = v27::decode_record(raw[index(hubs[i], c.dimension)]);
            if (record.raw != 0 && record.state == 1 && record.semantic == 1 &&
                record.dx == out_direction.dx && record.dy == out_direction.dy &&
                record.dz == out_direction.dz && record.s_reg == out_sreg) {
                result.merged_events.push_back(
                    {static_cast<std::uint64_t>(tick), c.labels[i], record});
                active.insert(c.labels[i]);
            }
        }
        if (tick < horizon) {
            v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
        }
    }
    result.active_labels.assign(active.begin(), active.end());
    if (result.active_labels.size() == 1) result.measurement = result.active_labels.front();
    result.final_raw = std::move(raw);
    result.final_clock = std::move(clock);
    return result;
}

}  // namespace dee::thinking::candidates::h1
