#include "dee_thinking/integrated_protocols.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <numeric>
#include <sstream>
#include <set>
#include <stdexcept>
#include <tuple>
#include <utility>

namespace dee::thinking::protocols {
namespace {

Coordinate add(Coordinate q, Direction d, int k, int n) {
    return {v27::wrap_coordinate(q.x + k * d.dx, n),
            v27::wrap_coordinate(q.y + k * d.dy, n),
            v27::wrap_coordinate(q.z + k * d.dz, n)};
}

Coordinate add(Coordinate a, Coordinate b, int n) {
    return {v27::wrap_coordinate(a.x + b.x, n),
            v27::wrap_coordinate(a.y + b.y, n),
            v27::wrap_coordinate(a.z + b.z, n)};
}

std::size_t index(Coordinate q, int n) {
    return v27::linear_index(q.x, q.y, q.z, n);
}

Direction sign_sum(Direction a, Direction b) {
    const auto sign = [](int value) { return (value > 0) - (value < 0); };
    return {sign(a.dx + b.dx), sign(a.dy + b.dy), sign(a.dz + b.dz)};
}

bool is_cardinal(Direction d) {
    return std::abs(d.dx) + std::abs(d.dy) + std::abs(d.dz) == 1;
}

int dot(Direction a, Direction b) {
    return a.dx * b.dx + a.dy * b.dy + a.dz * b.dz;
}

void place(std::vector<std::uint64_t>& raw,
           std::vector<std::uint64_t>& clock,
           Coordinate q,
           std::uint32_t state,
           std::uint16_t load,
           Direction direction,
           std::uint64_t phase,
           int n,
           std::uint8_t semantic = 1) {
    const auto at = index(q, n);
    if (raw.at(at) != 0) throw std::invalid_argument("initial footprint overlap");
    raw[at] = v27::pack_record(state, load, direction.dx, direction.dy,
                               direction.dz, semantic);
    clock[at] = phase;
}

std::size_t raw_support(const std::vector<std::uint64_t>& raw) {
    return static_cast<std::size_t>(
        std::count_if(raw.begin(), raw.end(), [](std::uint64_t value) {
            return value != 0;
        }));
}

std::uint64_t load_sum(const std::vector<std::uint64_t>& raw) {
    return std::accumulate(raw.begin(), raw.end(), std::uint64_t{},
                           [](std::uint64_t sum, std::uint64_t value) {
        return sum + v27::decode_record(value).s_reg;
    });
}

template <class Range>
std::string join_integers(const Range& values) {
    std::ostringstream output;
    bool first = true;
    for (const auto value : values) {
        if (!first) output << ',';
        first = false;
        output << static_cast<long long>(value);
    }
    return output.str();
}

std::vector<int> parse_integers(const std::string& value) {
    std::vector<int> output;
    std::istringstream input(value);
    std::string token;
    while (std::getline(input, token, ',')) {
        if (token.empty()) throw std::runtime_error("empty integer metadata token");
        std::size_t used = 0;
        const auto parsed = std::stoll(token, &used);
        if (used != token.size()) throw std::runtime_error("invalid integer metadata");
        output.push_back(static_cast<int>(parsed));
    }
    return output;
}

constexpr Direction kH2Cue{1, 0, 0};
constexpr Direction kH2TeacherY{-1, 1, 0};
constexpr Direction kH2TeacherZ{-1, 0, 1};
constexpr Direction kH2MoveY{0, 1, 0};
constexpr Direction kH2MoveZ{0, 0, 1};
constexpr Direction kH2Query{1, 0, 0};

void place_for_arrival(std::vector<std::uint64_t>& raw,
                       std::vector<std::uint64_t>& clock,
                       Coordinate target,
                       int tick,
                       Direction direction,
                       std::uint16_t load,
                       std::uint32_t state,
                       std::uint64_t phase,
                       int n) {
    place(raw, clock, add(target, direction, -tick, n), state, load,
          direction, phase, n);
}

void inject(std::vector<std::uint64_t>& raw,
            std::vector<std::uint64_t>& scratch,
            std::vector<std::uint64_t>& clock,
            std::vector<std::uint64_t>& clock_scratch,
            Coordinate q,
            Direction direction,
            std::uint16_t load,
            std::uint32_t state,
            std::uint64_t phase,
            int n) {
    const auto at = index(q, n);
    if (raw.at(at) != 0) throw std::runtime_error("occupied protocol input");
    const auto value = v27::pack_record(state, load, direction.dx, direction.dy,
                                        direction.dz, 1);
    raw[at] = scratch[at] = value;
    clock[at] = clock_scratch[at] = phase;
}

}  // namespace

const std::vector<IntegratedProtocolDescriptor>&
integrated_protocol_descriptors() {
    static const std::vector<IntegratedProtocolDescriptor> descriptors{
        {kH1Id, "1.0.0", ProtocolModality::NativePostHostStop,
         "CORE05 NRD05/NRH05", "Retardo codificado a posicion de coincidencia.",
         "N=59; labels -5..5; sector positivo no saturado; calibracion documentada.",
         "No generaliza automaticamente T_div ni geometria fuera del banco declarado.",
         {22, 0, 2, 11, true},
         {{"target", "experience", "t0 carrier / calibrated arrival", 0, v27::kReducerCap, true},
          {"probe", "experience", "t0 carrier / calibrated arrival", 0, v27::kReducerCap, true},
          {"hub_bank", "passive_readout", "bounded coincidence window", 0, v27::kReducerCap, false}},
         {"-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4", "5"}},
        {kH2Id, "1.0.0", ProtocolModality::Coupled,
         "CORE07 C7H02", "Repertorios por fibras separadas y solapamiento controlado.",
         "K=3 y K=7 reejecutados; constructor acotado a K<=40; overlap de dos fibras.",
         "K>7 permanece historico/no verificado en este build; consulta transformativa.",
         {14, 0, 7, 7, true},
         {{"training", "experience", "training_tick", 0, v27::kReducerCap, true},
          {"query", "query", "query_tick-query_path", 0, v27::kReducerCap, true},
          {"channel_readout", "passive_readout", "query_tick", 0, v27::kReducerCap, false}},
         {"channel[0..K-1]", "overlap.merge", "off_fiber.control"}},
        {kH3Id, "1.0.0", ProtocolModality::Diagnostic,
         "CORE17", "Reparacion funcional desde redundancia entrenada separadamente.",
         "N=31; dos geometrías reservadas; siete brazos causales.",
         "No replica una memoria; daño requiere opt-in y las copias se entrenan separadamente.",
         {2, 0, 7, 2, true},
         {{"primary", "trained_copy", "prepared/trained before damage", 0, v27::kReducerCap, true},
          {"backup", "trained_copy", "prepared/trained before damage", 0, v27::kReducerCap, true},
          {"damage", "diagnostic_intervention", "after primary use", 0, 0, true},
          {"fresh_query", "query", "after reconstruction", 0, v27::kReducerCap, true}},
         {"treatment", "backup_untrained", "backup_direction_reset", "no_backup", "path_cut", "offpath_cut", "wrong_receiver"}},
        {kH4Id, "1.0.0", ProtocolModality::Diagnostic,
         "Ingenierias 03-04.5/POST", "Contraste finito challenge-minus-baseline por historia.",
         "Lecturas pareadas, edades alineadas, aparato/challenge/observer congelados.",
         "No es make_reachable, no muta Runtime y no demuestra reachability universal.",
         {0, 0, 0, 0, false},
         {{"baseline", "observer_input", "same-history no-challenge", 0, 0, false},
          {"challenged", "observer_input", "diagnostic clone", 0, 0, false}},
         {"constructed", "reached", "acquired", "not_demonstrated"}},
        {kF1Id, "1.0.0", ProtocolModality::NativePostHostStop,
         "PENSAMIENTO/Entrega 02 laboratorio final", "Dos revisiones suministradas y reutilizadas por un linaje movil C7H03.",
         "N=127; consultas t34/46/58; revisiones t38/50; loads 7/5/3.",
         "Teachers presentes en t0; no streaming arbitrario ni autoensenanza general.",
         {12, 0, 12, 5, true},
         {{"training", "experience", "t0 -> t5", 0, v27::kReducerCap, true},
          {"revision1", "update", "t0 -> t38", 0, v27::kReducerCap, true},
          {"revision2", "update", "t0 -> t50", 0, v27::kReducerCap, true},
          {"queries", "query", "t0 -> t34/46/58", 0, v27::kReducerCap, true}},
         {"response1", "revision1", "response2", "revision2", "response3"}},
        {kF2Id, "1.0.0", ProtocolModality::NativePostHostStop,
         "PENSAMIENTO/Entrega 02 laboratorio final", "Mediacion ambiental finita por overflow y postpaso DEMUX.",
         "N=127; fase 353; seis soportes semantic=4; bias 15515; usos t39/43/47/51/55.",
         "Delta fijo +1 de DEMUX; preparacion de fase/soportes; no teacher arbitrario ni sostenibilidad infinita.",
         {12, 6, 12, 7, true},
         {{"upstream", "trained_response", "t0 -> t34", 0, v27::kReducerCap, true},
          {"bias", "environment", "t0 -> t38", 0, v27::kReducerCap, true},
          {"independent_carrier", "query", "t0 -> t39", 0, v27::kReducerCap, true},
          {"later_uses", "query", "t0 -> t43/47/51/55", 0, v27::kReducerCap, true}},
         {"environment", "demux", "return_site", "use1", "redirect", "use2"}},
    };
    return descriptors;
}

const IntegratedProtocolDescriptor* find_integrated_protocol(
    const std::string& id) noexcept {
    const auto& descriptors = integrated_protocol_descriptors();
    const auto found = std::find_if(
        descriptors.begin(), descriptors.end(),
        [&](const auto& descriptor) { return descriptor.id == id; });
    return found == descriptors.end() ? nullptr : &*found;
}

DelayPositionResult run_delay_position(const DelayPositionConfig& c,
                                       v27::TickOptions options) {
    if (c.dimension < 3 || c.labels.empty() || c.channel_spacing < 1 ||
        c.base_path_length < 1 ||
        std::find(c.labels.begin(), c.labels.end(), c.input_delay) ==
            c.labels.end()) {
        throw std::invalid_argument("invalid bounded NRH05 configuration");
    }
    if (std::set<int>(c.labels.begin(), c.labels.end()).size() !=
        c.labels.size()) {
        throw std::invalid_argument("NRH05 labels must be unique");
    }
    if (!is_cardinal(c.target_direction) ||
        !is_cardinal(c.probe_direction) || !is_cardinal(c.bank_axis) ||
        dot(c.target_direction, c.probe_direction) != 0 ||
        dot(c.bank_axis, c.target_direction) != 0 ||
        dot(c.bank_axis, c.probe_direction) != 0) {
        throw std::invalid_argument(
            "NRH05 requires cardinal bank and orthogonal proposal directions");
    }
    if (c.states[0] == 0 || c.states[1] == 0 ||
        static_cast<unsigned>(c.loads[0]) + c.loads[1] > v27::kReducerCap) {
        throw std::invalid_argument("NRH05 leaves its verified unsaturated sector");
    }
    int maximum_absolute_label = 0;
    for (int label : c.labels) {
        if (c.base_path_length + label < 1) {
            throw std::invalid_argument("NRH05 path length must remain positive");
        }
        maximum_absolute_label = std::max(maximum_absolute_label, std::abs(label));
    }
    const auto bank_span =
        static_cast<long long>(c.labels.size() - 1) * c.channel_spacing;
    const int horizon = c.base_path_length + maximum_absolute_label + 3;
    if (bank_span >= c.dimension || 2LL * horizon >= c.dimension) {
        throw std::invalid_argument("NRH05 geometry wraps inside its read horizon");
    }

    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension *
                       c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total),
        clock_scratch(total);
    std::vector<Coordinate> hubs;
    auto calibration = c.labels;
    if (c.arm == DelayPositionArm::ReversedCalibration) {
        std::reverse(calibration.begin(), calibration.end());
    }
    for (std::size_t i = 0; i < c.labels.size(); ++i) {
        const auto hub = add(c.base, c.bank_axis,
                             static_cast<int>(i) * c.channel_spacing,
                             c.dimension);
        hubs.push_back(hub);
        place(raw, clock,
              add(hub, c.probe_direction,
                  -(c.base_path_length + calibration[i]), c.dimension),
              c.states[1], c.loads[1], c.probe_direction, c.phases[1],
              c.dimension);
        if (c.arm != DelayPositionArm::TargetAbsent) {
            place(raw, clock,
                  add(hub, c.target_direction,
                      -(c.base_path_length + c.input_delay), c.dimension),
                  c.states[0], c.loads[0], c.target_direction, c.phases[0],
                  c.dimension);
        }
    }
    scratch = raw;
    clock_scratch = clock;

    DelayPositionResult result;
    result.initial_hubs_empty =
        std::all_of(hubs.begin(), hubs.end(), [&](Coordinate hub) {
            return raw[index(hub, c.dimension)] == 0;
        });
    const auto output_direction =
        sign_sum(c.target_direction, c.probe_direction);
    const auto output_load = static_cast<std::uint16_t>(
        std::min<unsigned>(static_cast<unsigned>(c.loads[0]) + c.loads[1],
                           v27::kReducerCap));
    std::set<int> active;
    for (int tick = 0; tick <= horizon; ++tick) {
        for (std::size_t i = 0; i < hubs.size(); ++i) {
            const auto record =
                v27::decode_record(raw[index(hubs[i], c.dimension)]);
            if (record.raw != 0 && record.state == 1 && record.semantic == 1 &&
                record.dx == output_direction.dx &&
                record.dy == output_direction.dy &&
                record.dz == output_direction.dz &&
                record.s_reg == output_load) {
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
    if (result.active_labels.size() == 1) {
        result.measurement = result.active_labels.front();
    }
    result.final_raw = std::move(raw);
    result.final_clock = std::move(clock);
    return result;
}

void save_delay_position_checkpoint(const DelayPositionConfig& c,
                                    std::uint64_t stop_at_tick,
                                    const std::string& path,
                                    v27::TickOptions options) {
    if (c.labels.empty()) throw std::invalid_argument("H1 labels are empty");
    int maximum_absolute_label = 0;
    for (const int label : c.labels) {
        if (c.base_path_length + label < 1) {
            throw std::invalid_argument("H1 path length must remain positive");
        }
        maximum_absolute_label = std::max(maximum_absolute_label, std::abs(label));
    }
    const auto bank_span = static_cast<long long>(c.labels.size() - 1) * c.channel_spacing;
    const int horizon = c.base_path_length + maximum_absolute_label + 3;
    if (bank_span >= c.dimension || 2LL * horizon >= c.dimension) {
        throw std::invalid_argument("H1 checkpoint geometry wraps in its read horizon");
    }
    int minimum_arrival = c.base_path_length + *std::min_element(c.labels.begin(), c.labels.end());
    if (stop_at_tick == 0 || stop_at_tick >= static_cast<std::uint64_t>(minimum_arrival)) {
        throw std::invalid_argument(
            "H1 checkpoint is supported before the first coincidence event");
    }
    // The public runner performs complete domain validation.  Calling it here
    // would evolve a second world, so repeat only construction after a cheap
    // validation pass over the same guards.
    if (c.dimension < 3 || c.channel_spacing < 1 || c.base_path_length < 1 ||
        std::find(c.labels.begin(), c.labels.end(), c.input_delay) == c.labels.end() ||
        std::set<int>(c.labels.begin(), c.labels.end()).size() != c.labels.size() ||
        !is_cardinal(c.target_direction) || !is_cardinal(c.probe_direction) ||
        !is_cardinal(c.bank_axis) || dot(c.target_direction, c.probe_direction) != 0 ||
        dot(c.bank_axis, c.target_direction) != 0 ||
        dot(c.bank_axis, c.probe_direction) != 0 ||
        c.states[0] == 0 || c.states[1] == 0 ||
        static_cast<unsigned>(c.loads[0]) + c.loads[1] > v27::kReducerCap) {
        throw std::invalid_argument("invalid H1 checkpoint configuration");
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension * c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total), clock_scratch(total);
    auto calibration = c.labels;
    if (c.arm == DelayPositionArm::ReversedCalibration) std::reverse(calibration.begin(), calibration.end());
    for (std::size_t i = 0; i < c.labels.size(); ++i) {
        const auto hub = add(c.base, c.bank_axis, static_cast<int>(i) * c.channel_spacing, c.dimension);
        place(raw, clock, add(hub, c.probe_direction, -(c.base_path_length + calibration[i]), c.dimension),
              c.states[1], c.loads[1], c.probe_direction, c.phases[1], c.dimension);
        if (c.arm != DelayPositionArm::TargetAbsent) {
            place(raw, clock, add(hub, c.target_direction, -(c.base_path_length + c.input_delay), c.dimension),
                  c.states[0], c.loads[0], c.target_direction, c.phases[0], c.dimension);
        }
    }
    scratch = raw;
    clock_scratch = clock;
    for (std::uint64_t tick = 0; tick < stop_at_tick; ++tick) {
        v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    auto snapshot = Runtime::import_research_state(c.dimension, stop_at_tick, std::move(raw), std::move(clock));
    snapshot.set_protocol_phase("H1_DELAY_POSITION_TICK_" + std::to_string(stop_at_tick));
    snapshot.set_snapshot_metadata("protocol.id", kH1Id);
    snapshot.set_snapshot_metadata("protocol.version", "1.0.0");
    snapshot.set_snapshot_metadata("h1.base", join_integers(std::array{c.base.x, c.base.y, c.base.z}));
    snapshot.set_snapshot_metadata("h1.axis", join_integers(std::array{c.bank_axis.dx, c.bank_axis.dy, c.bank_axis.dz}));
    snapshot.set_snapshot_metadata("h1.target", join_integers(std::array{c.target_direction.dx, c.target_direction.dy, c.target_direction.dz}));
    snapshot.set_snapshot_metadata("h1.probe", join_integers(std::array{c.probe_direction.dx, c.probe_direction.dy, c.probe_direction.dz}));
    snapshot.set_snapshot_metadata("h1.spacing", std::to_string(c.channel_spacing));
    snapshot.set_snapshot_metadata("h1.base_path", std::to_string(c.base_path_length));
    snapshot.set_snapshot_metadata("h1.labels", join_integers(c.labels));
    snapshot.set_snapshot_metadata("h1.input_delay", std::to_string(c.input_delay));
    snapshot.set_snapshot_metadata("h1.arm", std::to_string(static_cast<unsigned>(c.arm)));
    snapshot.set_snapshot_metadata("h1.loads", join_integers(c.loads));
    snapshot.set_snapshot_metadata("h1.states", join_integers(c.states));
    snapshot.set_snapshot_metadata("h1.phase0", std::to_string(c.phases[0]));
    snapshot.set_snapshot_metadata("h1.phase1", std::to_string(c.phases[1]));
    snapshot.save_snapshot(path);
}

DelayPositionResult resume_delay_position_checkpoint(const std::string& path,
                                                     v27::TickOptions options) {
    const auto snapshot = Runtime::load_snapshot(path);
    const auto require = [&](const std::string& key) {
        const auto value = snapshot.snapshot_metadata(key);
        if (!value) throw std::runtime_error("missing H1 metadata: " + key);
        return *value;
    };
    if (require("protocol.id") != kH1Id ||
        require("protocol.version") != "1.0.0") {
        throw std::invalid_argument("snapshot is not an H1 v1.0.0 checkpoint");
    }
    const auto scalar = [&](const std::string& key) { return std::stoll(require(key)); };
    DelayPositionConfig c;
    c.dimension = snapshot.dimension();
    auto values = parse_integers(require("h1.base"));
    if (values.size() != 3) throw std::runtime_error("invalid H1 base");
    c.base = {values[0], values[1], values[2]};
    values = parse_integers(require("h1.axis")); c.bank_axis = {values.at(0), values.at(1), values.at(2)};
    values = parse_integers(require("h1.target")); c.target_direction = {values.at(0), values.at(1), values.at(2)};
    values = parse_integers(require("h1.probe")); c.probe_direction = {values.at(0), values.at(1), values.at(2)};
    c.channel_spacing = static_cast<int>(scalar("h1.spacing"));
    c.base_path_length = static_cast<int>(scalar("h1.base_path"));
    c.labels = parse_integers(require("h1.labels"));
    c.input_delay = static_cast<int>(scalar("h1.input_delay"));
    c.arm = static_cast<DelayPositionArm>(scalar("h1.arm"));
    values = parse_integers(require("h1.loads")); c.loads = {static_cast<std::uint16_t>(values.at(0)), static_cast<std::uint16_t>(values.at(1))};
    values = parse_integers(require("h1.states")); c.states = {static_cast<std::uint32_t>(values.at(0)), static_cast<std::uint32_t>(values.at(1))};
    c.phases = {static_cast<std::uint64_t>(std::stoull(require("h1.phase0"))), static_cast<std::uint64_t>(std::stoull(require("h1.phase1")))};
    int max_abs = 0;
    for (int label : c.labels) max_abs = std::max(max_abs, std::abs(label));
    const int horizon = c.base_path_length + max_abs + 3;
    auto raw = snapshot.raw_copy();
    auto clock = snapshot.clock_copy();
    auto scratch = raw;
    auto clock_scratch = clock;
    std::vector<Coordinate> hubs;
    for (std::size_t i = 0; i < c.labels.size(); ++i) hubs.push_back(add(c.base, c.bank_axis, static_cast<int>(i) * c.channel_spacing, c.dimension));
    DelayPositionResult result;
    result.initial_hubs_empty = std::all_of(hubs.begin(), hubs.end(), [&](Coordinate q) { return raw[index(q, c.dimension)] == 0; });
    const auto output_direction = sign_sum(c.target_direction, c.probe_direction);
    const auto output_load = static_cast<std::uint16_t>(c.loads[0] + c.loads[1]);
    std::set<int> active;
    for (std::uint64_t tick = snapshot.current_tick(); tick <= static_cast<std::uint64_t>(horizon); ++tick) {
        for (std::size_t i = 0; i < hubs.size(); ++i) {
            const auto record = v27::decode_record(raw[index(hubs[i], c.dimension)]);
            if (record.raw != 0 && record.state == 1 && record.semantic == 1 &&
                record.dx == output_direction.dx && record.dy == output_direction.dy &&
                record.dz == output_direction.dz && record.s_reg == output_load) {
                result.merged_events.push_back({tick, c.labels[i], record});
                active.insert(c.labels[i]);
            }
        }
        if (tick < static_cast<std::uint64_t>(horizon)) v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    result.active_labels.assign(active.begin(), active.end());
    if (result.active_labels.size() == 1) result.measurement = result.active_labels.front();
    result.final_raw = std::move(raw);
    result.final_clock = std::move(clock);
    return result;
}

SeparatedRepertoireResult run_separated_repertoire(
    const SeparatedRepertoireConfig& c, v27::TickOptions options) {
    if (c.dimension < 79 || c.channels < 1 || c.channels > 40 ||
        c.delta_cycle.empty() || c.training_tick < 1 || c.query_path < 1 ||
        c.query_tick <= c.training_tick ||
        c.query_tick - c.query_path < c.training_tick ||
        2LL * c.query_tick >= c.dimension) {
        throw std::invalid_argument("invalid bounded separated C7H02 configuration");
    }
    const int maximum_x = 25 + std::min<int>(10, static_cast<int>(c.channels) - 1);
    if (c.base_offset <= maximum_x ||
        static_cast<unsigned>(c.query_base) + c.channels - 1 >
            v27::kReducerCap) {
        throw std::invalid_argument("C7H02 separated loads leave tested sector");
    }
    for (std::size_t i = 0; i < c.channels; ++i) {
        const int x = 25 + static_cast<int>(i % 11);
        const int delta = c.delta_cycle[i % c.delta_cycle.size()];
        const int query = static_cast<int>(c.query_base) + static_cast<int>(i);
        if (x + delta < 0 || x + delta > static_cast<int>(v27::kReducerCap) ||
            static_cast<int>(c.base_offset) + delta + query < 0 ||
            static_cast<int>(c.base_offset) + delta + query >
                static_cast<int>(v27::kReducerCap)) {
            throw std::invalid_argument("C7H02 separated response saturates");
        }
    }

    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension *
                       c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total),
        clock_scratch(total);
    struct Channel {
        Coordinate target;
        Coordinate port;
        int delta;
        std::uint16_t query;
    };
    std::vector<Channel> channels;
    channels.reserve(c.channels);
    for (std::size_t i = 0; i < c.channels; ++i) {
        const Coordinate base{5 + 10 * static_cast<int>(i % 8), 11,
                              7 + 14 * static_cast<int>(i / 8)};
        const auto junction = add(base, c.translation, c.dimension);
        const int x = 25 + static_cast<int>(i % 11);
        const int delta = c.delta_cycle[i % c.delta_cycle.size()];
        const auto query = static_cast<std::uint16_t>(c.query_base + i);
        place_for_arrival(raw, clock, junction, c.training_tick, kH2Cue,
                          static_cast<std::uint16_t>(c.base_offset - x),
                          1000U + static_cast<std::uint32_t>(i), 100U + i,
                          c.dimension);
        place_for_arrival(raw, clock, junction, c.training_tick, kH2TeacherY,
                          static_cast<std::uint16_t>(x + delta),
                          2000U + static_cast<std::uint32_t>(i), 200U + i,
                          c.dimension);
        const auto target = add(junction, kH2MoveY,
                                c.query_tick - c.training_tick, c.dimension);
        channels.push_back({target,
                            add(target, kH2Query, -c.query_path, c.dimension),
                            delta, query});
    }
    scratch = raw;
    clock_scratch = clock;
    const auto initial_support = raw_support(raw);
    const auto initial_load = load_sum(raw);
    std::size_t trained_support = 0;
    std::size_t injected_support = 0;
    std::size_t final_support = 0;
    std::uint64_t final_load = 0;
    SeparatedRepertoireResult result;
    for (int tick = 0; tick <= c.query_tick; ++tick) {
        if (tick == c.training_tick) trained_support = raw_support(raw);
        if (tick == c.query_tick - c.query_path) {
            result.ports_empty =
                std::all_of(channels.begin(), channels.end(), [&](const auto& item) {
                    return raw[index(item.port, c.dimension)] == 0;
                });
            for (std::size_t i = 0; i < channels.size(); ++i) {
                inject(raw, scratch, clock, clock_scratch, channels[i].port,
                       kH2Query, channels[i].query,
                       3000U + static_cast<std::uint32_t>(i), 300U + i,
                       c.dimension);
            }
            injected_support = raw_support(raw);
        }
        if (tick == c.query_tick) {
            for (const auto& channel : channels) {
                const auto record =
                    v27::decode_record(raw[index(channel.target, c.dimension)]);
                result.observed_responses.push_back(record.s_reg);
                const auto expected = static_cast<std::uint16_t>(
                    c.base_offset + channel.delta + channel.query);
                if (record.raw != 0 && record.dx == 1 && record.dy == 1 &&
                    record.dz == 0 && record.s_reg == expected) {
                    ++result.exact_channels;
                }
            }
            final_support = raw_support(raw);
            final_load = load_sum(raw);
        }
        if (tick < c.query_tick) {
            v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
        }
    }
    result.all_exact = result.exact_channels == c.channels;
    result.training_budget_exact = initial_support - trained_support == c.channels;
    result.read_budget_exact = injected_support - final_support == c.channels;
    std::uint64_t queries = 0;
    for (const auto& channel : channels) queries += channel.query;
    result.load_accounting_exact = final_load == initial_load + queries;
    result.final_raw = std::move(raw);
    result.final_clock = std::move(clock);
    return result;
}

OverlapRepertoireResult run_overlap_repertoire(
    const OverlapRepertoireConfig& c, v27::TickOptions options) {
    if (c.dimension < 45 || c.geometry_index < 0 || c.training_tick < 1 ||
        c.merge_tick <= c.training_tick || c.query_tick <= c.merge_tick ||
        c.query_tick - 4 < c.merge_tick ||
        2LL * c.query_tick >= c.dimension || c.base_offset <= 21) {
        throw std::invalid_argument("invalid bounded overlap C7H02 configuration");
    }
    const int component_y = 12 + c.deltas[0];
    const int component_z = 21 + c.deltas[1];
    const int merged_load =
        2 * static_cast<int>(c.base_offset) + c.deltas[0] + c.deltas[1];
    const int response_load = merged_load + c.query_load;
    if (component_y < 0 || component_z < 0 || merged_load < 0 ||
        response_load > static_cast<int>(v27::kReducerCap)) {
        throw std::invalid_argument("C7H02 overlap leaves tested sector");
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension *
                       c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total),
        clock_scratch(total);
    const Coordinate merge{(17 + 6 * c.geometry_index) % c.dimension,
                           (19 + 9 * c.geometry_index) % c.dimension,
                           (23 + 11 * c.geometry_index) % c.dimension};
    auto jy = add(merge, kH2MoveY, -(c.merge_tick - c.training_tick),
                  c.dimension);
    auto jz = add(merge, kH2MoveZ, -(c.merge_tick - c.training_tick),
                  c.dimension);
    if (c.off_fiber) jz = add(jz, Direction{1, 0, 0}, 3, c.dimension);
    const std::array<Coordinate, 2> junctions{jy, jz};
    const std::array<Direction, 2> teachers{kH2TeacherY, kH2TeacherZ};
    const std::array<int, 2> xs{12, 21};
    for (std::size_t i = 0; i < 2; ++i) {
        place_for_arrival(raw, clock, junctions[i], c.training_tick, kH2Cue,
                          static_cast<std::uint16_t>(c.base_offset - xs[i]),
                          4000U + static_cast<std::uint32_t>(i), 400U + i,
                          c.dimension);
        place_for_arrival(raw, clock, junctions[i], c.training_tick, teachers[i],
                          static_cast<std::uint16_t>(xs[i] + c.deltas[i]),
                          5000U + static_cast<std::uint32_t>(i), 500U + i,
                          c.dimension);
    }
    scratch = raw;
    clock_scratch = clock;
    const Direction merged_direction{0, 1, 1};
    const auto receiver = add(merge, merged_direction,
                              c.query_tick - c.merge_tick, c.dimension);
    const auto port = add(receiver, kH2Query, -4, c.dimension);
    OverlapRepertoireResult result;
    const auto expected_merge = static_cast<std::uint16_t>(merged_load);
    const auto expected_response = static_cast<std::uint16_t>(response_load);
    for (int tick = 0; tick <= c.query_tick; ++tick) {
        if (tick == c.merge_tick) {
            const auto record = v27::decode_record(raw[index(merge, c.dimension)]);
            result.observed_merge_load = record.s_reg;
            result.merge_exact = !c.off_fiber && record.raw != 0 &&
                                 record.dx == 0 && record.dy == 1 &&
                                 record.dz == 1 && record.s_reg == expected_merge;
            result.false_merge = c.off_fiber && record.raw != 0 &&
                                 record.dx == 0 && record.dy == 1 &&
                                 record.dz == 1 && record.s_reg == expected_merge;
        }
        if (tick == c.query_tick - 4 && !c.off_fiber) {
            result.port_empty = raw[index(port, c.dimension)] == 0;
            inject(raw, scratch, clock, clock_scratch, port, kH2Query,
                   c.query_load, 6000, 600, c.dimension);
        }
        if (tick == c.query_tick && !c.off_fiber) {
            const auto record =
                v27::decode_record(raw[index(receiver, c.dimension)]);
            result.observed_response_load = record.s_reg;
            result.composed_response_exact =
                record.raw != 0 && record.dx == 1 && record.dy == 1 &&
                record.dz == 1 && record.s_reg == expected_response;
            result.individual_identity_preserved =
                record.raw != 0 &&
                (static_cast<int>(record.s_reg) - c.base_offset ==
                     static_cast<int>(c.query_load) + c.deltas[0] ||
                 static_cast<int>(record.s_reg) - c.base_offset ==
                     static_cast<int>(c.query_load) + c.deltas[1]);
        }
        if (tick < c.query_tick) {
            v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
        }
    }
    result.final_raw = std::move(raw);
    result.final_clock = std::move(clock);
    return result;
}

void save_separated_repertoire_checkpoint(
    const SeparatedRepertoireConfig& c, std::uint64_t stop_at_tick,
    const std::string& path, v27::TickOptions options) {
    const int injection_tick = c.query_tick - c.query_path;
    if (c.dimension < 79 || c.channels < 1 || c.channels > 40 ||
        c.delta_cycle.empty() || c.training_tick < 1 || c.query_path < 1 ||
        injection_tick <= c.training_tick || 2LL * c.query_tick >= c.dimension ||
        stop_at_tick <= static_cast<std::uint64_t>(c.training_tick) ||
        stop_at_tick >= static_cast<std::uint64_t>(injection_tick)) {
        throw std::invalid_argument(
            "H2 separated checkpoint must lie after training and before query injection");
    }
    const int maximum_x = 25 + std::min<int>(10, static_cast<int>(c.channels) - 1);
    if (c.base_offset <= maximum_x ||
        static_cast<unsigned>(c.query_base) + c.channels - 1 > v27::kReducerCap) {
        throw std::invalid_argument("H2 separated checkpoint loads leave tested sector");
    }
    for (std::size_t i = 0; i < c.channels; ++i) {
        const int x = 25 + static_cast<int>(i % 11);
        const int delta = c.delta_cycle[i % c.delta_cycle.size()];
        const int query = static_cast<int>(c.query_base) + static_cast<int>(i);
        if (x + delta < 0 || x + delta > static_cast<int>(v27::kReducerCap) ||
            static_cast<int>(c.base_offset) + delta + query < 0 ||
            static_cast<int>(c.base_offset) + delta + query > static_cast<int>(v27::kReducerCap)) {
            throw std::invalid_argument("H2 separated checkpoint response saturates");
        }
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension * c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total), clock_scratch(total);
    for (std::size_t i = 0; i < c.channels; ++i) {
        const Coordinate base{5 + 10 * static_cast<int>(i % 8), 11,
                              7 + 14 * static_cast<int>(i / 8)};
        const auto junction = add(base, c.translation, c.dimension);
        const int x = 25 + static_cast<int>(i % 11);
        const int delta = c.delta_cycle[i % c.delta_cycle.size()];
        place_for_arrival(raw, clock, junction, c.training_tick, kH2Cue,
                          static_cast<std::uint16_t>(c.base_offset - x),
                          1000U + static_cast<std::uint32_t>(i), 100U + i,
                          c.dimension);
        place_for_arrival(raw, clock, junction, c.training_tick, kH2TeacherY,
                          static_cast<std::uint16_t>(x + delta),
                          2000U + static_cast<std::uint32_t>(i), 200U + i,
                          c.dimension);
    }
    scratch = raw; clock_scratch = clock;
    const auto initial_support = raw_support(raw);
    const auto initial_load = load_sum(raw);
    std::size_t trained_support = 0;
    for (std::uint64_t tick = 0; tick < stop_at_tick; ++tick) {
        v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
        if (tick + 1 == static_cast<std::uint64_t>(c.training_tick)) trained_support = raw_support(raw);
    }
    auto snapshot = Runtime::import_research_state(c.dimension, stop_at_tick, std::move(raw), std::move(clock));
    snapshot.set_protocol_phase("H2_SEPARATED_TICK_" + std::to_string(stop_at_tick));
    snapshot.set_snapshot_metadata("protocol.id", kH2Id);
    snapshot.set_snapshot_metadata("protocol.version", "1.0.0");
    snapshot.set_snapshot_metadata("protocol.h2.mode", "separated");
    snapshot.set_snapshot_metadata("h2.channels", std::to_string(c.channels));
    snapshot.set_snapshot_metadata("h2.translation", join_integers(std::array{c.translation.x, c.translation.y, c.translation.z}));
    snapshot.set_snapshot_metadata("h2.base_offset", std::to_string(c.base_offset));
    snapshot.set_snapshot_metadata("h2.deltas", join_integers(c.delta_cycle));
    snapshot.set_snapshot_metadata("h2.query_base", std::to_string(c.query_base));
    snapshot.set_snapshot_metadata("h2.training_tick", std::to_string(c.training_tick));
    snapshot.set_snapshot_metadata("h2.query_tick", std::to_string(c.query_tick));
    snapshot.set_snapshot_metadata("h2.query_path", std::to_string(c.query_path));
    snapshot.set_snapshot_metadata("h2.initial_support", std::to_string(initial_support));
    snapshot.set_snapshot_metadata("h2.trained_support", std::to_string(trained_support));
    snapshot.set_snapshot_metadata("h2.initial_load", std::to_string(initial_load));
    snapshot.save_snapshot(path);
}

SeparatedRepertoireResult resume_separated_repertoire_checkpoint(
    const std::string& path, v27::TickOptions options) {
    const auto snapshot = Runtime::load_snapshot(path);
    const auto require = [&](const std::string& key) {
        const auto value = snapshot.snapshot_metadata(key);
        if (!value) throw std::runtime_error("missing H2 metadata: " + key);
        return *value;
    };
    if (require("protocol.id") != kH2Id ||
        require("protocol.version") != "1.0.0" ||
        require("protocol.h2.mode") != "separated") {
        throw std::invalid_argument("snapshot is not an H2 separated v1.0.0 checkpoint");
    }
    const auto scalar = [&](const std::string& key) { return std::stoull(require(key)); };
    SeparatedRepertoireConfig c;
    c.dimension = snapshot.dimension();
    c.channels = static_cast<std::size_t>(scalar("h2.channels"));
    auto v = parse_integers(require("h2.translation"));
    c.translation = {v.at(0), v.at(1), v.at(2)};
    c.base_offset = static_cast<std::uint16_t>(scalar("h2.base_offset"));
    c.delta_cycle = parse_integers(require("h2.deltas"));
    c.query_base = static_cast<std::uint16_t>(scalar("h2.query_base"));
    c.training_tick = static_cast<int>(scalar("h2.training_tick"));
    c.query_tick = static_cast<int>(scalar("h2.query_tick"));
    c.query_path = static_cast<int>(scalar("h2.query_path"));
    struct Channel { Coordinate target; Coordinate port; int delta; std::uint16_t query; };
    std::vector<Channel> channels;
    for (std::size_t i = 0; i < c.channels; ++i) {
        const Coordinate base{5 + 10 * static_cast<int>(i % 8), 11, 7 + 14 * static_cast<int>(i / 8)};
        const auto junction = add(base, c.translation, c.dimension);
        const auto target = add(junction, kH2MoveY, c.query_tick - c.training_tick, c.dimension);
        channels.push_back({target, add(target, kH2Query, -c.query_path, c.dimension),
                            c.delta_cycle[i % c.delta_cycle.size()], static_cast<std::uint16_t>(c.query_base + i)});
    }
    auto raw = snapshot.raw_copy(); auto clock = snapshot.clock_copy();
    auto scratch = raw; auto clock_scratch = clock;
    SeparatedRepertoireResult result;
    const auto initial_support = static_cast<std::size_t>(scalar("h2.initial_support"));
    const auto trained_support = static_cast<std::size_t>(scalar("h2.trained_support"));
    const auto initial_load = scalar("h2.initial_load");
    std::size_t injected_support = 0, final_support = 0; std::uint64_t final_load = 0;
    for (std::uint64_t tick = snapshot.current_tick(); tick <= static_cast<std::uint64_t>(c.query_tick); ++tick) {
        if (tick == static_cast<std::uint64_t>(c.query_tick - c.query_path)) {
            result.ports_empty = std::all_of(channels.begin(), channels.end(), [&](const auto& item) { return raw[index(item.port, c.dimension)] == 0; });
            for (std::size_t i = 0; i < channels.size(); ++i) inject(raw, scratch, clock, clock_scratch, channels[i].port, kH2Query, channels[i].query, 3000U + static_cast<std::uint32_t>(i), 300U + i, c.dimension);
            injected_support = raw_support(raw);
        }
        if (tick == static_cast<std::uint64_t>(c.query_tick)) {
            for (const auto& channel : channels) {
                const auto record = v27::decode_record(raw[index(channel.target, c.dimension)]);
                result.observed_responses.push_back(record.s_reg);
                const auto expected = static_cast<std::uint16_t>(c.base_offset + channel.delta + channel.query);
                if (record.raw != 0 && record.dx == 1 && record.dy == 1 && record.dz == 0 && record.s_reg == expected) ++result.exact_channels;
            }
            final_support = raw_support(raw); final_load = load_sum(raw);
        }
        if (tick < static_cast<std::uint64_t>(c.query_tick)) v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    result.all_exact = result.exact_channels == c.channels;
    result.training_budget_exact = initial_support - trained_support == c.channels;
    result.read_budget_exact = injected_support - final_support == c.channels;
    std::uint64_t queries = 0; for (const auto& item : channels) queries += item.query;
    result.load_accounting_exact = final_load == initial_load + queries;
    result.final_raw = std::move(raw); result.final_clock = std::move(clock);
    return result;
}

void save_overlap_repertoire_checkpoint(
    const OverlapRepertoireConfig& c, std::uint64_t stop_at_tick,
    const std::string& path, v27::TickOptions options) {
    const int injection_tick = c.query_tick - 4;
    if (c.off_fiber || c.dimension < 45 || c.geometry_index < 0 ||
        c.training_tick < 1 || c.base_offset <= 21 ||
        c.merge_tick <= c.training_tick || injection_tick <= c.merge_tick ||
        2LL * c.query_tick >= c.dimension ||
        stop_at_tick < static_cast<std::uint64_t>(c.merge_tick) ||
        stop_at_tick >= static_cast<std::uint64_t>(injection_tick)) {
        throw std::invalid_argument(
            "H2 overlap checkpoint supports the on-fiber post-merge/pre-query interval");
    }
    const int component_y = 12 + c.deltas[0];
    const int component_z = 21 + c.deltas[1];
    const int merged_load = 2 * static_cast<int>(c.base_offset) + c.deltas[0] + c.deltas[1];
    if (component_y < 0 || component_z < 0 || merged_load < 0 ||
        merged_load + c.query_load > static_cast<int>(v27::kReducerCap)) {
        throw std::invalid_argument("H2 overlap checkpoint loads leave tested sector");
    }
    const auto total = static_cast<std::size_t>(c.dimension) * c.dimension * c.dimension;
    std::vector<std::uint64_t> raw(total), scratch(total), clock(total), clock_scratch(total);
    const Coordinate merge{(17 + 6 * c.geometry_index) % c.dimension,
                           (19 + 9 * c.geometry_index) % c.dimension,
                           (23 + 11 * c.geometry_index) % c.dimension};
    const std::array<Coordinate, 2> junctions{
        add(merge, kH2MoveY, -(c.merge_tick - c.training_tick), c.dimension),
        add(merge, kH2MoveZ, -(c.merge_tick - c.training_tick), c.dimension)};
    const std::array<Direction, 2> teachers{kH2TeacherY, kH2TeacherZ};
    const std::array<int, 2> xs{12, 21};
    for (std::size_t i = 0; i < 2; ++i) {
        place_for_arrival(raw, clock, junctions[i], c.training_tick, kH2Cue,
                          static_cast<std::uint16_t>(c.base_offset - xs[i]),
                          4000U + static_cast<std::uint32_t>(i), 400U + i, c.dimension);
        place_for_arrival(raw, clock, junctions[i], c.training_tick, teachers[i],
                          static_cast<std::uint16_t>(xs[i] + c.deltas[i]),
                          5000U + static_cast<std::uint32_t>(i), 500U + i, c.dimension);
    }
    const auto expected_merge = static_cast<std::uint16_t>(2 * c.base_offset + c.deltas[0] + c.deltas[1]);
    bool merge_exact = false;
    std::uint16_t observed_merge_load = 0;
    const auto capture_merge = [&] {
        const auto record = v27::decode_record(raw[index(merge, c.dimension)]);
        observed_merge_load = record.s_reg;
        merge_exact = record.raw != 0 && record.dx == 0 && record.dy == 1 &&
                      record.dz == 1 && record.s_reg == expected_merge;
    };
    scratch = raw; clock_scratch = clock;
    for (std::uint64_t tick = 0; tick < stop_at_tick; ++tick) {
        if (tick == static_cast<std::uint64_t>(c.merge_tick)) capture_merge();
        v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    if (stop_at_tick == static_cast<std::uint64_t>(c.merge_tick)) {
        capture_merge();
    }
    auto snapshot = Runtime::import_research_state(c.dimension, stop_at_tick, std::move(raw), std::move(clock));
    snapshot.set_protocol_phase("H2_OVERLAP_TICK_" + std::to_string(stop_at_tick));
    snapshot.set_snapshot_metadata("protocol.id", kH2Id);
    snapshot.set_snapshot_metadata("protocol.version", "1.0.0");
    snapshot.set_snapshot_metadata("protocol.h2.mode", "overlap");
    snapshot.set_snapshot_metadata("h2.geometry_index", std::to_string(c.geometry_index));
    snapshot.set_snapshot_metadata("h2.deltas", join_integers(c.deltas));
    snapshot.set_snapshot_metadata("h2.query_load", std::to_string(c.query_load));
    snapshot.set_snapshot_metadata("h2.base_offset", std::to_string(c.base_offset));
    snapshot.set_snapshot_metadata("h2.training_tick", std::to_string(c.training_tick));
    snapshot.set_snapshot_metadata("h2.merge_tick", std::to_string(c.merge_tick));
    snapshot.set_snapshot_metadata("h2.query_tick", std::to_string(c.query_tick));
    snapshot.set_snapshot_metadata("h2.merge_exact", merge_exact ? "1" : "0");
    snapshot.set_snapshot_metadata("h2.merge_load", std::to_string(observed_merge_load));
    snapshot.save_snapshot(path);
}

OverlapRepertoireResult resume_overlap_repertoire_checkpoint(
    const std::string& path, v27::TickOptions options) {
    const auto snapshot = Runtime::load_snapshot(path);
    const auto require = [&](const std::string& key) {
        const auto value = snapshot.snapshot_metadata(key);
        if (!value) throw std::runtime_error("missing H2 overlap metadata: " + key);
        return *value;
    };
    if (require("protocol.id") != kH2Id ||
        require("protocol.version") != "1.0.0" ||
        require("protocol.h2.mode") != "overlap") {
        throw std::invalid_argument("snapshot is not an H2 overlap v1.0.0 checkpoint");
    }
    const auto scalar = [&](const std::string& key) { return std::stoll(require(key)); };
    OverlapRepertoireConfig c;
    c.dimension = snapshot.dimension(); c.geometry_index = static_cast<int>(scalar("h2.geometry_index"));
    auto deltas = parse_integers(require("h2.deltas")); c.deltas = {deltas.at(0), deltas.at(1)};
    c.query_load = static_cast<std::uint16_t>(scalar("h2.query_load"));
    c.base_offset = static_cast<std::uint16_t>(scalar("h2.base_offset"));
    c.training_tick = static_cast<int>(scalar("h2.training_tick"));
    c.merge_tick = static_cast<int>(scalar("h2.merge_tick"));
    c.query_tick = static_cast<int>(scalar("h2.query_tick"));
    const Coordinate merge{(17 + 6 * c.geometry_index) % c.dimension,
                           (19 + 9 * c.geometry_index) % c.dimension,
                           (23 + 11 * c.geometry_index) % c.dimension};
    const Direction merged_direction{0, 1, 1};
    const auto receiver = add(merge, merged_direction, c.query_tick - c.merge_tick, c.dimension);
    const auto port = add(receiver, kH2Query, -4, c.dimension);
    auto raw = snapshot.raw_copy(); auto clock = snapshot.clock_copy(); auto scratch = raw; auto clock_scratch = clock;
    OverlapRepertoireResult result;
    result.merge_exact = scalar("h2.merge_exact") == 1;
    result.observed_merge_load = static_cast<std::uint16_t>(scalar("h2.merge_load"));
    const auto expected_response = static_cast<std::uint16_t>(2 * c.base_offset + c.deltas[0] + c.deltas[1] + c.query_load);
    for (std::uint64_t tick = snapshot.current_tick(); tick <= static_cast<std::uint64_t>(c.query_tick); ++tick) {
        if (tick == static_cast<std::uint64_t>(c.query_tick - 4)) {
            result.port_empty = raw[index(port, c.dimension)] == 0;
            inject(raw, scratch, clock, clock_scratch, port, kH2Query, c.query_load, 6000, 600, c.dimension);
        }
        if (tick == static_cast<std::uint64_t>(c.query_tick)) {
            const auto record = v27::decode_record(raw[index(receiver, c.dimension)]);
            result.observed_response_load = record.s_reg;
            result.composed_response_exact = record.raw != 0 && record.dx == 1 && record.dy == 1 && record.dz == 1 && record.s_reg == expected_response;
            result.individual_identity_preserved = record.raw != 0 &&
                (static_cast<int>(record.s_reg) - c.base_offset == static_cast<int>(c.query_load) + c.deltas[0] ||
                 static_cast<int>(record.s_reg) - c.base_offset == static_cast<int>(c.query_load) + c.deltas[1]);
        }
        if (tick < static_cast<std::uint64_t>(c.query_tick)) v27::tick(raw, scratch, clock, clock_scratch, c.dimension, options);
    }
    result.final_raw = std::move(raw); result.final_clock = std::move(clock);
    return result;
}

namespace {

using Vector3 = std::array<int, 3>;

Vector3 as_vector(Coordinate q) { return {q.x, q.y, q.z}; }
Direction as_direction(Vector3 value) {
    return {value[0], value[1], value[2]};
}

Vector3 vector_add(Vector3 q, Vector3 direction, int k, int n) {
    for (int i = 0; i < 3; ++i) {
        q[i] = v27::wrap_coordinate(q[i] + k * direction[i], n);
    }
    return q;
}

Vector3 vector_plus(Vector3 a, Vector3 b) {
    for (int i = 0; i < 3; ++i) a[i] += b[i];
    return a;
}

Vector3 vector_negate(Vector3 value) {
    for (auto& item : value) item = -item;
    return value;
}

Vector3 vector_transform(Vector3 value,
                         const std::array<int, 3>& permutation,
                         const std::array<int, 3>& signs) {
    return {signs[0] * value[permutation[0]],
            signs[1] * value[permutation[1]],
            signs[2] * value[permutation[2]]};
}

std::uint64_t pack_vector(std::uint32_t state, std::uint16_t load,
                          Vector3 direction, std::uint8_t semantic = 1) {
    return v27::pack_record(state, load, direction[0], direction[1],
                            direction[2], semantic);
}

bool direction_is(const v27::Record& record, Vector3 expected) {
    return record.raw_present() &&
           Vector3{record.dx, record.dy, record.dz} == expected;
}

class RepairWorld {
public:
    explicit RepairWorld(int dimension, v27::TickOptions options)
        : n_(dimension),
          raw_a_(static_cast<std::size_t>(n_) * n_ * n_),
          raw_b_(raw_a_.size()),
          clock_a_(raw_a_.size()),
          clock_b_(raw_a_.size()),
          options_(options) {
        if (dimension < 3) throw std::invalid_argument("invalid repair dimension");
    }
    RepairWorld(int dimension, v27::TickOptions options,
                std::vector<std::uint64_t> raw,
                std::vector<std::uint64_t> clock)
        : n_(dimension), raw_a_(std::move(raw)), raw_b_(raw_a_),
          clock_a_(std::move(clock)), clock_b_(clock_a_), options_(options) {
        const auto expected = static_cast<std::size_t>(n_) * n_ * n_;
        if (n_ < 3 || raw_a_.size() != expected || clock_a_.size() != expected) {
            throw std::invalid_argument("invalid restored repair state");
        }
    }

    [[nodiscard]] int dimension() const noexcept { return n_; }
    [[nodiscard]] std::size_t at(Vector3 q) const {
        return v27::linear_index(q[0], q[1], q[2], n_);
    }
    [[nodiscard]] std::uint64_t raw(Vector3 q) const {
        return raw_a_.at(at(q));
    }
    [[nodiscard]] std::uint64_t clock(Vector3 q) const {
        return clock_a_.at(at(q));
    }
    [[nodiscard]] v27::Record read(Vector3 q) const {
        return v27::decode_record(raw(q));
    }
    void put(Vector3 q, std::uint64_t raw_value, std::uint64_t clock_value) {
        const auto i = at(q);
        if (raw_a_[i] != 0) throw std::runtime_error("occupied repair input");
        raw_a_[i] = raw_b_[i] = raw_value;
        clock_a_[i] = clock_b_[i] = clock_value;
    }
    void overwrite(Vector3 q, std::uint64_t raw_value,
                   std::uint64_t clock_value) {
        const auto i = at(q);
        raw_a_[i] = raw_b_[i] = raw_value;
        clock_a_[i] = clock_b_[i] = clock_value;
    }
    void clear(Vector3 q) { overwrite(q, 0, 0); }
    void tick() {
        v27::tick(raw_a_, raw_b_, clock_a_, clock_b_, n_, options_);
    }
    [[nodiscard]] std::vector<std::uint64_t> take_raw() {
        return std::move(raw_a_);
    }
    [[nodiscard]] std::vector<std::uint64_t> take_clock() {
        return std::move(clock_a_);
    }
    [[nodiscard]] const std::vector<std::uint64_t>& raw_state() const noexcept {
        return raw_a_;
    }
    [[nodiscard]] const std::vector<std::uint64_t>& clock_state() const noexcept {
        return clock_a_;
    }

private:
    int n_{};
    std::vector<std::uint64_t> raw_a_;
    std::vector<std::uint64_t> raw_b_;
    std::vector<std::uint64_t> clock_a_;
    std::vector<std::uint64_t> clock_b_;
    v27::TickOptions options_{};
};

void repair_inject_arrival(RepairWorld& world, Vector3 target,
                           Vector3 direction, std::uint16_t load,
                           std::uint32_t state, std::uint64_t phase) {
    world.put(vector_add(target, direction, -1, world.dimension()),
              pack_vector(state, load, direction), phase);
}

void validate_repair_config(const RepairConfig& c) {
    if (!c.authorize_diagnostic_damage) {
        throw std::invalid_argument(
            "CORE17 repair requires explicit diagnostic-damage authorization");
    }
    const auto& g = c.geometry;
    const auto is_geometry_00 =
        g.id == "fresh_like_00" && g.dimension == 31 &&
        g.primary_distance == 7 && g.backup_distance == 7 &&
        g.permutation == std::array<int, 3>{2, 1, 0} &&
        g.signs == std::array<int, 3>{-1, 1, -1} &&
        g.receiver == Coordinate{15, 15, 15};
    const auto is_geometry_01 =
        g.id == "fresh_like_01" && g.dimension == 31 &&
        g.primary_distance == 6 && g.backup_distance == 6 &&
        g.permutation == std::array<int, 3>{0, 1, 2} &&
        g.signs == std::array<int, 3>{1, 1, -1} &&
        g.receiver == Coordinate{15, 15, 15};
    if (!is_geometry_00 && !is_geometry_01) {
        throw std::invalid_argument("CORE17 geometry is outside the two verified preparations");
    }
    if (static_cast<unsigned>(c.arm) > static_cast<unsigned>(RepairArm::WrongReceiver)) {
        throw std::invalid_argument("invalid CORE17 repair arm");
    }
    std::array<bool, 3> seen{};
    for (int value : g.permutation) {
        if (value < 0 || value > 2 || seen[value]) {
            throw std::invalid_argument("repair permutation must contain 0,1,2");
        }
        seen[value] = true;
    }
    for (int value : g.signs) {
        if (value != -1 && value != 1) {
            throw std::invalid_argument("repair signs must be -1 or +1");
        }
    }
}

class RepairMachine {
public:
    RepairMachine(RepairConfig config, v27::TickOptions options)
        : config_(std::move(config)), world_(config_.geometry.dimension, options) {
        validate_repair_config(config_);
        derive();
        world_.put(source1_, pack_vector(610000u + config_.preparation_tag, 7, a_),
                   710000u + config_.preparation_tag);
        world_.put(source2_, pack_vector(610001u + config_.preparation_tag, 8, a_),
                   710001u + config_.preparation_tag);
    }

    RepairMachine(RepairConfig config, v27::TickOptions options,
                  std::uint64_t completed_tick,
                  std::vector<std::uint64_t> raw,
                  std::vector<std::uint64_t> clock,
                  RepairResult partial)
        : config_(std::move(config)),
          world_(config_.geometry.dimension, options, std::move(raw),
                 std::move(clock)),
          completed_tick_(completed_tick), result_(std::move(partial)) {
        validate_repair_config(config_);
        derive();
        if (completed_tick_ >= static_cast<std::uint64_t>(query_tick_)) {
            throw std::invalid_argument("repair checkpoint is already terminal");
        }
    }

    [[nodiscard]] std::uint64_t completed_tick() const noexcept {
        return completed_tick_;
    }
    [[nodiscard]] std::uint64_t terminal_tick() const noexcept {
        return static_cast<std::uint64_t>(query_tick_);
    }
    [[nodiscard]] const RepairConfig& config() const noexcept { return config_; }
    [[nodiscard]] const RepairResult& partial_result() const noexcept {
        return result_;
    }
    [[nodiscard]] const std::vector<std::uint64_t>& raw_state() const noexcept {
        return world_.raw_state();
    }
    [[nodiscard]] const std::vector<std::uint64_t>& clock_state() const noexcept {
        return world_.clock_state();
    }

    void step() {
        if (completed_tick_ >= terminal_tick()) {
            throw std::logic_error("repair protocol is terminal");
        }
        const int next = static_cast<int>(completed_tick_ + 1);
        const auto tag = config_.preparation_tag;
        if (next == config_.geometry.dimension) {
            repair_inject_arrival(world_, source1_, sensor_, 47, 720000u + tag,
                                  730000u + tag);
            repair_inject_arrival(world_, source2_, sensor_, 48, 720001u + tag,
                                  730001u + tag);
        }
        if (next == learned_tick_) {
            repair_inject_arrival(world_, source1_, normalizer_, 53,
                                  740000u + tag, 750000u + tag);
            repair_inject_arrival(world_, source2_, normalizer_, 54,
                                  740001u + tag, 750001u + tag);
            repair_inject_arrival(world_, source1_, penalty0_, 59,
                                  760000u + tag, 770000u + tag);
            if (config_.arm != RepairArm::BackupUntrained) {
                repair_inject_arrival(world_, source2_, penalty0_, 60,
                                      760001u + tag, 770001u + tag);
            }
        }
        if (next == launch1_) {
            repair_inject_arrival(world_, source1_, relay1_, 61,
                                  780000u + tag, 790000u + tag);
        }
        if (next == arrival1_) {
            repair_inject_arrival(world_, receiver_, vector_negate(relay1_), 71,
                                  800000u + tag, 810000u + tag);
        }
        if (next == launch2_ && config_.arm != RepairArm::NoBackup) {
            repair_inject_arrival(world_, source2_, relay2_, 67,
                                  820000u + tag, 830000u + tag);
        }
        if (next == launch2_ + cut_offset_ &&
            (config_.arm == RepairArm::PathCut ||
             config_.arm == RepairArm::OffpathCut)) {
            auto target = vector_add(source2_, route2_, cut_offset_,
                                     config_.geometry.dimension);
            if (config_.arm == RepairArm::OffpathCut) {
                target = vector_add(
                    target,
                    vector_transform({0, 0, 5}, config_.geometry.permutation,
                                     config_.geometry.signs),
                    1, config_.geometry.dimension);
            }
            repair_inject_arrival(world_, target, vector_negate(route2_), 73,
                                  840000u + tag, 850000u + tag);
        }
        if (next == arrival2_ && config_.arm != RepairArm::NoBackup) {
            const auto converter = config_.arm == RepairArm::WrongReceiver
                                       ? vector_negate(b_)
                                       : vector_negate(relay2_);
            repair_inject_arrival(world_, receiver_, converter, 79,
                                  860000u + tag, 870000u + tag);
        }
        if (next == query_tick_) {
            repair_inject_arrival(world_, receiver_, sensor_, 101,
                                  880000u + tag, 890000u + tag);
        }
        world_.tick();
        completed_tick_ = static_cast<std::uint64_t>(next);

        if (next == learned_tick_) {
            const auto backup = world_.read(source2_);
            result_.backup_learned = direction_is(backup, b_);
            if (config_.arm == RepairArm::BackupDirectionReset &&
                backup.raw_present()) {
                world_.overwrite(source2_,
                                 pack_vector(backup.state, backup.s_reg, a_,
                                             backup.semantic),
                                 world_.clock(source2_));
            } else if (config_.arm == RepairArm::NoBackup) {
                world_.clear(source2_);
            }
        }
        if (next == arrival1_) {
            result_.primary_function_before_damage =
                direction_is(world_.read(receiver_), b_);
        }
        if (next == damage_tick_) {
            const bool existed = world_.raw(damaged_site_) != 0;
            world_.clear(damaged_site_);
            result_.damage_applied = existed && world_.raw(damaged_site_) == 0;
            result_.function_lost_after_damage =
                world_.raw(damaged_site_) == 0;
        }
        if (next == arrival2_) {
            result_.reconstructed_at_arrival =
                direction_is(world_.read(receiver_), b_);
        }
    }

    void run_to(std::uint64_t tick) {
        if (tick > terminal_tick()) {
            throw std::invalid_argument("repair stop tick exceeds protocol horizon");
        }
        while (completed_tick_ < tick) step();
    }

    RepairResult finish() {
        run_to(terminal_tick());
        const auto query = world_.read(receiver_);
        result_.fresh_function = direction_is(query, action1_);
        result_.primary_source_depleted = world_.raw(source1_) == 0;
        result_.backup_source_depleted = world_.raw(source2_) == 0;
        result_.query_load = query.s_reg;
        result_.query_direction = as_direction({query.dx, query.dy, query.dz});
        result_.final_raw = world_.raw_state();
        result_.final_clock = world_.clock_state();
        return result_;
    }

private:
    void derive() {
        constexpr Vector3 A{1, 0, 0};
        constexpr Vector3 B{0, 1, 0};
        constexpr Vector3 SENSOR{-1, 0, 1};
        constexpr Vector3 NORMALIZER{1, 0, -1};
        constexpr Vector3 PENALTY0{-1, 1, 0};
        constexpr Vector3 ACTION1{-1, 1, 1};
        const auto& g = config_.geometry;
        a_ = vector_transform(A, g.permutation, g.signs);
        b_ = vector_transform(B, g.permutation, g.signs);
        sensor_ = vector_transform(SENSOR, g.permutation, g.signs);
        normalizer_ = vector_transform(NORMALIZER, g.permutation, g.signs);
        penalty0_ = vector_transform(PENALTY0, g.permutation, g.signs);
        action1_ = vector_transform(ACTION1, g.permutation, g.signs);
        relay1_ = vector_transform({1, -1, 1}, g.permutation, g.signs);
        relay2_ = vector_transform({-1, -1, 1}, g.permutation, g.signs);
        route1_ = vector_plus(relay1_, b_);
        route2_ = vector_plus(relay2_, b_);
        receiver_ = as_vector(g.receiver);
        source1_ = vector_add(receiver_, route1_, -g.primary_distance, g.dimension);
        source2_ = vector_add(receiver_, route2_, -g.backup_distance, g.dimension);
        if (source1_ == source2_) {
            throw std::invalid_argument("degenerate CORE17 redundant sources");
        }
        learned_tick_ = 2 * g.dimension;
        launch1_ = 3 * g.dimension;
        arrival1_ = launch1_ + g.primary_distance;
        damage_tick_ = arrival1_ + 1;
        launch2_ = 5 * g.dimension;
        arrival2_ = launch2_ + g.backup_distance;
        query_tick_ = arrival2_ + g.dimension;
        cut_offset_ = std::max(2, g.backup_distance / 2);
        damaged_site_ = vector_add(receiver_, b_, 1, g.dimension);
    }

    RepairConfig config_;
    RepairWorld world_;
    std::uint64_t completed_tick_{};
    RepairResult result_;
    Vector3 a_{}, b_{}, sensor_{}, normalizer_{}, penalty0_{}, action1_{};
    Vector3 relay1_{}, relay2_{}, route1_{}, route2_{};
    Vector3 receiver_{}, source1_{}, source2_{}, damaged_site_{};
    int learned_tick_{}, launch1_{}, arrival1_{}, damage_tick_{};
    int launch2_{}, arrival2_{}, query_tick_{}, cut_offset_{};
};

}  // namespace

RepairResult run_trained_redundancy_repair(const RepairConfig& c,
                                           v27::TickOptions options) {
    validate_repair_config(c);
    if (!c.authorize_diagnostic_damage) {
        throw std::invalid_argument(
            "CORE17 repair requires explicit diagnostic-damage authorization");
    }
    const auto& g = c.geometry;
    if (g.dimension < 17 || g.primary_distance < 2 ||
        g.backup_distance < 2) {
        throw std::invalid_argument("invalid bounded CORE17 geometry");
    }
    std::array<bool, 3> seen{};
    for (int value : g.permutation) {
        if (value < 0 || value > 2 || seen[value]) {
            throw std::invalid_argument("repair permutation must contain 0,1,2");
        }
        seen[value] = true;
    }
    for (int value : g.signs) {
        if (value != -1 && value != 1) {
            throw std::invalid_argument("repair signs must be -1 or +1");
        }
    }

    constexpr Vector3 A{1, 0, 0};
    constexpr Vector3 B{0, 1, 0};
    constexpr Vector3 SENSOR{-1, 0, 1};
    constexpr Vector3 NORMALIZER{1, 0, -1};
    constexpr Vector3 PENALTY0{-1, 1, 0};
    constexpr Vector3 ACTION1{-1, 1, 1};
    const auto a = vector_transform(A, g.permutation, g.signs);
    const auto b = vector_transform(B, g.permutation, g.signs);
    const auto sensor = vector_transform(SENSOR, g.permutation, g.signs);
    const auto normalizer =
        vector_transform(NORMALIZER, g.permutation, g.signs);
    const auto penalty0 = vector_transform(PENALTY0, g.permutation, g.signs);
    const auto action1 = vector_transform(ACTION1, g.permutation, g.signs);
    const auto relay1 =
        vector_transform({1, -1, 1}, g.permutation, g.signs);
    const auto relay2 =
        vector_transform({-1, -1, 1}, g.permutation, g.signs);
    const auto route1 = vector_plus(relay1, b);
    const auto route2 = vector_plus(relay2, b);
    const auto receiver = as_vector(g.receiver);
    const auto source1 =
        vector_add(receiver, route1, -g.primary_distance, g.dimension);
    const auto source2 =
        vector_add(receiver, route2, -g.backup_distance, g.dimension);
    if (source1 == source2) {
        throw std::invalid_argument("degenerate CORE17 redundant sources");
    }

    RepairWorld world(g.dimension, options);
    world.put(source1, pack_vector(610000u + c.preparation_tag, 7, a),
              710000u + c.preparation_tag);
    world.put(source2, pack_vector(610001u + c.preparation_tag, 8, a),
              710001u + c.preparation_tag);

    const int learned_tick = 2 * g.dimension;
    const int launch1 = 3 * g.dimension;
    const int arrival1 = launch1 + g.primary_distance;
    const int damage_tick = arrival1 + 1;
    const int launch2 = 5 * g.dimension;
    const int arrival2 = launch2 + g.backup_distance;
    const int query2 = arrival2 + g.dimension;
    const int cut_offset = std::max(2, g.backup_distance / 2);
    const auto damaged_site = vector_add(receiver, b, 1, g.dimension);

    RepairResult result;
    for (int current = 0; current < query2; ++current) {
        const int next = current + 1;
        if (next == g.dimension) {
            repair_inject_arrival(world, source1, sensor, 47,
                                  720000u + c.preparation_tag,
                                  730000u + c.preparation_tag);
            repair_inject_arrival(world, source2, sensor, 48,
                                  720001u + c.preparation_tag,
                                  730001u + c.preparation_tag);
        }
        if (next == learned_tick) {
            repair_inject_arrival(world, source1, normalizer, 53,
                                  740000u + c.preparation_tag,
                                  750000u + c.preparation_tag);
            repair_inject_arrival(world, source2, normalizer, 54,
                                  740001u + c.preparation_tag,
                                  750001u + c.preparation_tag);
            repair_inject_arrival(world, source1, penalty0, 59,
                                  760000u + c.preparation_tag,
                                  770000u + c.preparation_tag);
            if (c.arm != RepairArm::BackupUntrained) {
                repair_inject_arrival(world, source2, penalty0, 60,
                                      760001u + c.preparation_tag,
                                      770001u + c.preparation_tag);
            }
        }
        if (next == launch1) {
            repair_inject_arrival(world, source1, relay1, 61,
                                  780000u + c.preparation_tag,
                                  790000u + c.preparation_tag);
        }
        if (next == arrival1) {
            repair_inject_arrival(world, receiver, vector_negate(relay1), 71,
                                  800000u + c.preparation_tag,
                                  810000u + c.preparation_tag);
        }
        if (next == launch2 && c.arm != RepairArm::NoBackup) {
            repair_inject_arrival(world, source2, relay2, 67,
                                  820000u + c.preparation_tag,
                                  830000u + c.preparation_tag);
        }
        if (next == launch2 + cut_offset &&
            (c.arm == RepairArm::PathCut ||
             c.arm == RepairArm::OffpathCut)) {
            auto target =
                vector_add(source2, route2, cut_offset, g.dimension);
            if (c.arm == RepairArm::OffpathCut) {
                target = vector_add(
                    target,
                    vector_transform({0, 0, 5}, g.permutation, g.signs), 1,
                    g.dimension);
            }
            repair_inject_arrival(world, target, vector_negate(route2), 73,
                                  840000u + c.preparation_tag,
                                  850000u + c.preparation_tag);
        }
        if (next == arrival2 && c.arm != RepairArm::NoBackup) {
            const auto converter = c.arm == RepairArm::WrongReceiver
                                       ? vector_negate(b)
                                       : vector_negate(relay2);
            repair_inject_arrival(world, receiver, converter, 79,
                                  860000u + c.preparation_tag,
                                  870000u + c.preparation_tag);
        }
        if (next == query2) {
            repair_inject_arrival(world, receiver, sensor, 101,
                                  880000u + c.preparation_tag,
                                  890000u + c.preparation_tag);
        }

        world.tick();

        if (next == learned_tick) {
            const auto backup = world.read(source2);
            result.backup_learned = direction_is(backup, b);
            if (c.arm == RepairArm::BackupDirectionReset &&
                backup.raw_present()) {
                world.overwrite(source2,
                                pack_vector(backup.state, backup.s_reg, a,
                                            backup.semantic),
                                world.clock(source2));
            } else if (c.arm == RepairArm::NoBackup) {
                world.clear(source2);
            }
        }
        if (next == arrival1) {
            result.primary_function_before_damage =
                direction_is(world.read(receiver), b);
        }
        if (next == damage_tick) {
            const bool existed = world.raw(damaged_site) != 0;
            world.clear(damaged_site);
            result.damage_applied = existed && world.raw(damaged_site) == 0;
            result.function_lost_after_damage = world.raw(damaged_site) == 0;
        }
        if (next == arrival2) {
            result.reconstructed_at_arrival =
                direction_is(world.read(receiver), b);
        }
    }

    const auto query = world.read(receiver);
    result.fresh_function = direction_is(query, action1);
    result.primary_source_depleted = world.raw(source1) == 0;
    result.backup_source_depleted = world.raw(source2) == 0;
    result.query_load = query.s_reg;
    result.query_direction = as_direction({query.dx, query.dy, query.dz});
    result.final_clock = world.take_clock();
    result.final_raw = world.take_raw();
    return result;
}

void save_trained_redundancy_repair_checkpoint(
    const RepairConfig& config, std::uint64_t stop_after_tick,
    const std::string& path, v27::TickOptions options) {
    RepairMachine machine(config, options);
    if (stop_after_tick == 0 || stop_after_tick >= machine.terminal_tick()) {
        throw std::invalid_argument(
            "H3 checkpoint must be strictly inside the protocol horizon");
    }
    machine.run_to(stop_after_tick);
    auto snapshot = Runtime::import_research_state(
        config.geometry.dimension, stop_after_tick,
        machine.raw_state(), machine.clock_state());
    const auto& partial = machine.partial_result();
    snapshot.set_protocol_phase("H3_REPAIR_TICK_" +
                                std::to_string(stop_after_tick));
    snapshot.set_snapshot_metadata("protocol.id", kH3Id);
    snapshot.set_snapshot_metadata("protocol.version", "1.0.0");
    snapshot.set_snapshot_metadata("protocol.h3.geometry_id", config.geometry.id);
    snapshot.set_snapshot_metadata("protocol.h3.dimension", std::to_string(config.geometry.dimension));
    snapshot.set_snapshot_metadata("protocol.h3.primary_distance", std::to_string(config.geometry.primary_distance));
    snapshot.set_snapshot_metadata("protocol.h3.backup_distance", std::to_string(config.geometry.backup_distance));
    for (std::size_t i = 0; i < 3; ++i) {
        snapshot.set_snapshot_metadata("protocol.h3.permutation" + std::to_string(i),
                                       std::to_string(config.geometry.permutation[i]));
        snapshot.set_snapshot_metadata("protocol.h3.sign" + std::to_string(i),
                                       std::to_string(config.geometry.signs[i]));
    }
    snapshot.set_snapshot_metadata("protocol.h3.receiver_x", std::to_string(config.geometry.receiver.x));
    snapshot.set_snapshot_metadata("protocol.h3.receiver_y", std::to_string(config.geometry.receiver.y));
    snapshot.set_snapshot_metadata("protocol.h3.receiver_z", std::to_string(config.geometry.receiver.z));
    snapshot.set_snapshot_metadata("protocol.h3.arm", std::to_string(static_cast<unsigned>(config.arm)));
    snapshot.set_snapshot_metadata("protocol.h3.damage_authorized", config.authorize_diagnostic_damage ? "1" : "0");
    snapshot.set_snapshot_metadata("protocol.h3.preparation_tag", std::to_string(config.preparation_tag));
    snapshot.set_snapshot_metadata("protocol.h3.backup_learned", partial.backup_learned ? "1" : "0");
    snapshot.set_snapshot_metadata("protocol.h3.primary_before_damage", partial.primary_function_before_damage ? "1" : "0");
    snapshot.set_snapshot_metadata("protocol.h3.damage_applied", partial.damage_applied ? "1" : "0");
    snapshot.set_snapshot_metadata("protocol.h3.function_lost", partial.function_lost_after_damage ? "1" : "0");
    snapshot.set_snapshot_metadata("protocol.h3.reconstructed", partial.reconstructed_at_arrival ? "1" : "0");
    snapshot.save_snapshot(path);
}

RepairResult resume_trained_redundancy_repair_checkpoint(
    const std::string& path, v27::TickOptions options) {
    const auto snapshot = Runtime::load_snapshot(path);
    const auto protocol = snapshot.snapshot_metadata("protocol.id");
    const auto version = snapshot.snapshot_metadata("protocol.version");
    if (!protocol || *protocol != kH3Id || !version || *version != "1.0.0") {
        throw std::invalid_argument("snapshot is not an H3 v1.0.0 checkpoint");
    }
    const auto required = [&](const std::string& key) -> std::string {
        const auto value = snapshot.snapshot_metadata(key);
        if (!value) throw std::runtime_error("missing H3 checkpoint metadata: " + key);
        return *value;
    };
    const auto integer = [&](const std::string& key) -> std::int64_t {
        const auto value = required(key);
        std::size_t used = 0;
        const auto parsed = std::stoll(value, &used);
        if (used != value.size()) throw std::runtime_error("invalid H3 metadata: " + key);
        return parsed;
    };
    RepairConfig config;
    config.geometry.id = required("protocol.h3.geometry_id");
    config.geometry.dimension = static_cast<int>(integer("protocol.h3.dimension"));
    config.geometry.primary_distance = static_cast<int>(integer("protocol.h3.primary_distance"));
    config.geometry.backup_distance = static_cast<int>(integer("protocol.h3.backup_distance"));
    for (std::size_t i = 0; i < 3; ++i) {
        config.geometry.permutation[i] = static_cast<int>(
            integer("protocol.h3.permutation" + std::to_string(i)));
        config.geometry.signs[i] = static_cast<int>(
            integer("protocol.h3.sign" + std::to_string(i)));
    }
    config.geometry.receiver = {
        static_cast<int>(integer("protocol.h3.receiver_x")),
        static_cast<int>(integer("protocol.h3.receiver_y")),
        static_cast<int>(integer("protocol.h3.receiver_z")),
    };
    const auto arm_value = integer("protocol.h3.arm");
    if (arm_value < 0 || arm_value > static_cast<std::int64_t>(RepairArm::WrongReceiver)) {
        throw std::runtime_error("invalid H3 arm in checkpoint");
    }
    config.arm = static_cast<RepairArm>(arm_value);
    config.authorize_diagnostic_damage = integer("protocol.h3.damage_authorized") == 1;
    config.preparation_tag = static_cast<std::uint32_t>(integer("protocol.h3.preparation_tag"));
    RepairResult partial;
    partial.backup_learned = integer("protocol.h3.backup_learned") == 1;
    partial.primary_function_before_damage = integer("protocol.h3.primary_before_damage") == 1;
    partial.damage_applied = integer("protocol.h3.damage_applied") == 1;
    partial.function_lost_after_damage = integer("protocol.h3.function_lost") == 1;
    partial.reconstructed_at_arrival = integer("protocol.h3.reconstructed") == 1;
    RepairMachine machine(config, options, snapshot.current_tick(),
                          snapshot.raw_copy(), snapshot.clock_copy(), partial);
    return machine.finish();
}

AccessibilityResult analyze_accessibility(const AccessibilityRequest& request) {
    AccessibilityResult result;
    if (request.observer_id.empty()) {
        result.diagnostics.push_back("observer_id is required");
    }
    if (request.challenge_id.empty()) {
        result.diagnostics.push_back("challenge_id is required");
    }
    if (!request.apparatus_frozen) {
        result.diagnostics.push_back("apparatus differs across histories");
    }
    if (!request.challenge_frozen) {
        result.diagnostics.push_back("challenge differs across histories");
    }
    if (!request.ages_aligned) {
        result.diagnostics.push_back("history ages are not aligned");
    }
    if (request.cases.empty()) {
        result.diagnostics.push_back("at least one history case is required");
    }

    for (const auto& item : request.cases) {
        if (item.history_id.empty()) {
            result.diagnostics.push_back("history_id is required");
            continue;
        }
        if (item.baseline_tick != item.challenged_tick) {
            result.diagnostics.push_back(item.history_id +
                                         ": baseline/challenge ages differ");
        }
        if (!item.challenge_applied_to_diagnostic_clone) {
            result.diagnostics.push_back(
                item.history_id +
                ": challenge is not declared as a diagnostic-clone intervention");
        }
        if (item.baseline.size() != item.challenged.size() ||
            item.baseline.empty()) {
            result.diagnostics.push_back(item.history_id +
                                         ": observer readings are not paired");
            continue;
        }
        AccessibilityEffect effect;
        effect.history_id = item.history_id;
        effect.status = item.history_status;
        if (item.history_reached_natively &&
            effect.status == AccessibilityStatus::Constructed) {
            result.diagnostics.push_back(
                item.history_id +
                ": constructed status conflicts with native-history flag");
        }
        bool sites_match = true;
        for (std::size_t i = 0; i < item.baseline.size(); ++i) {
            const auto& baseline = item.baseline[i];
            const auto& challenged = item.challenged[i];
            if (!(baseline.site == challenged.site)) {
                sites_match = false;
                break;
            }
            effect.raw_changed_sites += baseline.raw != challenged.raw;
            effect.clock_changed_sites += baseline.clock != challenged.clock;
            effect.s_reg_deltas.push_back(
                static_cast<std::int32_t>(v27::decode_record(challenged.raw).s_reg) -
                static_cast<std::int32_t>(v27::decode_record(baseline.raw).s_reg));
        }
        if (!sites_match) {
            result.diagnostics.push_back(item.history_id +
                                         ": observer coordinates differ");
            continue;
        }
        result.effects.push_back(std::move(effect));
    }

    result.comparable = result.diagnostics.empty() &&
                        result.effects.size() == request.cases.size();
    if (result.comparable && result.effects.size() > 1) {
        const auto& first = result.effects.front();
        result.history_conditioned_response =
            std::any_of(result.effects.begin() + 1, result.effects.end(),
                        [&](const AccessibilityEffect& effect) {
            return effect.raw_changed_sites != first.raw_changed_sites ||
                   effect.clock_changed_sites != first.clock_changed_sites ||
                   effect.s_reg_deltas != first.s_reg_deltas;
        });
    }
    if (!result.history_conditioned_response && result.comparable) {
        result.diagnostics.push_back(
            "the declared observer found no history-conditioned effect");
    }
    return result;
}

namespace {

constexpr int kProtocolN = 127;
constexpr Coordinate kJunction{63, 63, 63};
constexpr Direction kCue{1, 0, 0};
constexpr Direction kTeacher{-1, 1, 0};
constexpr Direction kMemory{0, 1, 0};
constexpr Direction kProgrammer{1, -1, 0};
constexpr Direction kProgrammed{1, 0, 0};
constexpr Direction kRedirect{-1, 1, 0};
constexpr Direction kResponse{1, 1, 0};
constexpr Direction kQueryRedirect{-1, 0, 0};
constexpr Direction kMarkerDirection{0, -1, 0};
constexpr std::uint64_t kTrainTick = 5;
constexpr std::uint64_t kConsequenceTick = 8;
constexpr std::uint64_t kProgramTick = 12;
constexpr std::uint64_t kRedirectTick = 18;
constexpr std::array<std::uint64_t, 3> kQueryTicks{34, 46, 58};
constexpr std::array<std::uint64_t, 2> kRevisionTicks{38, 50};
constexpr std::array<std::uint16_t, 3> kQueryLoads{7, 5, 3};
constexpr std::uint16_t kBaseCueLoad = 4083;
constexpr std::uint16_t kBaseTeacherLoad = 19;
constexpr std::uint16_t kSupplyLoad = 23;
constexpr std::uint16_t kMarkerLoad = 17;

struct ProtocolGeometry {
    Coordinate junction{};
    Coordinate consequence{};
    Coordinate program{};
    Coordinate redirect{};
    Coordinate response1{};
    Coordinate revision1{};
    Coordinate response2{};
    Coordinate revision2{};
    Coordinate response3{};
};

int protocol_wrap(int value) {
    int remainder = value % kProtocolN;
    return remainder < 0 ? remainder + kProtocolN : remainder;
}

Coordinate protocol_plus(Coordinate q, Direction d, int scale = 1) {
    return {protocol_wrap(q.x + d.dx * scale),
            protocol_wrap(q.y + d.dy * scale),
            protocol_wrap(q.z + d.dz * scale)};
}

Coordinate protocol_plus(Coordinate a, Coordinate b) {
    return {protocol_wrap(a.x + b.x), protocol_wrap(a.y + b.y),
            protocol_wrap(a.z + b.z)};
}

Coordinate protocol_source(Coordinate target, std::uint64_t tick,
                           Direction direction) {
    const int distance = static_cast<int>(tick % kProtocolN);
    return protocol_plus(target, direction, -distance);
}

std::size_t protocol_index(Coordinate q) {
    return v27::linear_index(q.x, q.y, q.z, kProtocolN);
}

ProtocolGeometry protocol_geometry() {
    ProtocolGeometry geometry;
    geometry.junction = kJunction;
    geometry.program = protocol_plus(
        kJunction, kMemory, static_cast<int>(kProgramTick - kTrainTick));
    geometry.consequence = protocol_plus(
        geometry.program, kProgrammer,
        -static_cast<int>(kProgramTick - kConsequenceTick));
    geometry.redirect = protocol_plus(
        geometry.program, kProgrammed,
        static_cast<int>(kRedirectTick - kProgramTick));
    geometry.response1 = protocol_plus(
        geometry.redirect, kMemory,
        static_cast<int>(kQueryTicks[0] - kRedirectTick));
    geometry.revision1 = protocol_plus(
        geometry.response1, kResponse,
        static_cast<int>(kRevisionTicks[0] - kQueryTicks[0]));
    geometry.response2 = protocol_plus(
        geometry.revision1, kMemory,
        static_cast<int>(kQueryTicks[1] - kRevisionTicks[0]));
    geometry.revision2 = protocol_plus(
        geometry.response2, kResponse,
        static_cast<int>(kRevisionTicks[1] - kQueryTicks[1]));
    geometry.response3 = protocol_plus(
        geometry.revision2, kMemory,
        static_cast<int>(kQueryTicks[2] - kRevisionTicks[1]));
    return geometry;
}

void track(std::vector<ProtocolReceipt>& receipts, std::string label,
           EventReceipt receipt) {
    receipts.push_back({std::move(label), std::move(receipt)});
}

void finalize_receipts(Runtime& runtime,
                       std::vector<ProtocolReceipt>& receipts) {
    for (auto& item : receipts) {
        const auto final = runtime.receipt(item.receipt.id);
        if (!final) throw std::runtime_error("protocol lost an event receipt");
        item.receipt = *final;
    }
}

bool all_applied_at_zero(const std::vector<ProtocolReceipt>& receipts) {
    return std::all_of(receipts.begin(), receipts.end(), [](const auto& item) {
        return item.receipt.status == EventStatus::Applied &&
               item.receipt.effective_tick == std::optional<std::uint64_t>{0};
    });
}

void schedule_carrier(Runtime& runtime,
                      std::vector<ProtocolReceipt>& receipts,
                      const std::string& label, Coordinate target,
                      std::uint64_t arrival_tick, Direction direction,
                      std::uint32_t state, std::uint16_t load,
                      int z_shift = 0, std::uint8_t semantic = 1) {
    if (z_shift != 0) {
        target = {target.x, target.y, protocol_wrap(target.z + z_shift)};
    }
    const auto source = protocol_source(target, arrival_tick, direction);
    runtime.register_channel(
        ChannelSpec{label, source, state, direction, semantic, true, false});
    track(receipts, label, runtime.experience(label, 0, load));
}

void schedule_c7_base(Runtime& runtime,
                      std::vector<ProtocolReceipt>& receipts, bool teacher,
                      bool include_first_query,
                      std::uint16_t marker_load = kMarkerLoad) {
    const auto geometry = protocol_geometry();
    schedule_carrier(runtime, receipts, "training.cue", geometry.junction,
                     kTrainTick, kCue, 81001, kBaseCueLoad);
    schedule_carrier(
        runtime, receipts, "training.teacher",
        teacher ? geometry.junction
                : Coordinate{geometry.junction.x, geometry.junction.y,
                             protocol_wrap(geometry.junction.z + 4)},
        kTrainTick, kTeacher, 81002, kBaseTeacherLoad);
    schedule_carrier(runtime, receipts, "bridge.supply",
                     geometry.consequence, kConsequenceTick, kProgrammer,
                     81003, kSupplyLoad);
    schedule_carrier(runtime, receipts, "bridge.marker",
                     geometry.consequence, kConsequenceTick,
                     kMarkerDirection, 81004, marker_load);
    schedule_carrier(runtime, receipts, "lineage.redirect0",
                     geometry.redirect, kRedirectTick, kRedirect, 81005, 0);
    if (include_first_query) {
        schedule_carrier(runtime, receipts, "query.q1", geometry.response1,
                         kQueryTicks[0], kCue, 81101, kQueryLoads[0]);
    }
}

Runtime protocol_runtime(v27::TickOptions options) {
    Runtime runtime(kProtocolN);
    runtime.set_execution_options(options);
    return runtime;
}

void record_observation(std::vector<ProtocolObservation>& output,
                        const std::string& label, const Runtime& runtime,
                        Coordinate site) {
    output.push_back({label, runtime.observe(site)});
}

std::uint64_t metadata_u64(const Runtime& runtime, const std::string& key,
                           std::uint64_t fallback = 0) {
    const auto value = runtime.snapshot_metadata(key);
    if (!value) return fallback;
    std::size_t used = 0;
    const auto parsed = std::stoull(*value, &used);
    if (used != value->size()) {
        throw std::runtime_error("invalid protocol checkpoint metadata: " + key);
    }
    return parsed;
}

bool metadata_bool(const Runtime& runtime, const std::string& key,
                   bool fallback = false) {
    const auto value = runtime.snapshot_metadata(key);
    if (!value) return fallback;
    if (*value == "1") return true;
    if (*value == "0") return false;
    throw std::runtime_error("invalid protocol checkpoint boolean: " + key);
}

void collect_runtime_receipts(Runtime& runtime,
                              std::vector<ProtocolReceipt>& output) {
    output.clear();
    for (const auto& receipt : runtime.receipts()) {
        const std::string label = receipt.channels.empty()
                                      ? ("event." + std::to_string(receipt.id))
                                      : receipt.channels.front();
        output.push_back({label, receipt});
    }
}

std::uint16_t observed_load(const Runtime& runtime, Coordinate site) {
    return runtime.observe(site).record.s_reg;
}

void install_environment_support(std::vector<std::uint64_t>& raw,
                                 std::vector<std::uint64_t>& clock,
                                 Coordinate environment,
                                 std::uint64_t phase) {
    clock[protocol_index(environment)] = phase;
    constexpr std::array<Coordinate, 6> offsets{{
        {1, -1, -1}, {1, -1, 0}, {1, -1, 1},
        {1, 0, -1},  {1, 0, 0},  {1, 0, 1},
    }};
    for (std::size_t i = 0; i < offsets.size(); ++i) {
        const auto site = protocol_plus(environment, offsets[i]);
        raw[protocol_index(site)] = v27::pack_record(
            9000U + static_cast<std::uint32_t>(i), 0, 0, 0, 0, 4);
    }
}

void validate_f1(const ReusableRevisionConfig& c) {
    using Key = std::tuple<std::uint16_t, std::uint16_t, std::uint16_t,
                           std::uint16_t, bool>;
    const Key key{c.revision1, c.revision2, c.sham1, c.sham2,
                  c.trained_relation};
    const std::array<std::pair<const char*, Key>, 6> allowed{{
        {"REV_11_13", {std::uint16_t{11}, std::uint16_t{13}, std::uint16_t{0}, std::uint16_t{0}, true}},
        {"REV_13_11", {std::uint16_t{13}, std::uint16_t{11}, std::uint16_t{0}, std::uint16_t{0}, true}},
        {"FIRST_ONLY_11", {std::uint16_t{11}, std::uint16_t{0}, std::uint16_t{0}, std::uint16_t{13}, true}},
        {"SECOND_ONLY_13", {std::uint16_t{0}, std::uint16_t{13}, std::uint16_t{11}, std::uint16_t{0}, true}},
        {"SHAM_11_13", {std::uint16_t{0}, std::uint16_t{0}, std::uint16_t{11}, std::uint16_t{13}, true}},
        {"NO_TRAINED_RELATION", {std::uint16_t{11}, std::uint16_t{13}, std::uint16_t{0}, std::uint16_t{0}, false}},
    }};
    const auto match = std::find_if(allowed.begin(), allowed.end(), [&](const auto& item) {
        return c.id == item.first && key == item.second;
    });
    if (match == allowed.end()) {
        throw std::invalid_argument(
            "F1 configuration is outside the six verified revision arms");
    }
}

void validate_f2(const EnvironmentalReturnConfig& c) {
    if (c.id.empty() || c.environment_clock_phase != 353) {
        throw std::invalid_argument(
            "F2 requires the verified phase-353 environmental preparation");
    }
    using Key = std::tuple<bool, std::uint16_t, std::uint16_t,
                           EnvironmentalQueryMode>;
    const Key key{c.trained_response, c.bias_load, c.marker_load,
                  c.query_mode};
    const std::array<std::pair<const char*, Key>, 6> allowed{{
        {"ENV_INTACT", {true, std::uint16_t{15515}, std::uint16_t{17}, EnvironmentalQueryMode::Intact}},
        {"ENV_RESPONSE_CUT", {false, std::uint16_t{15515}, std::uint16_t{17}, EnvironmentalQueryMode::Intact}},
        {"ENV_NO_QUERY", {true, std::uint16_t{15515}, std::uint16_t{17}, EnvironmentalQueryMode::Absent}},
        {"ENV_QUERY_SHAM", {true, std::uint16_t{15515}, std::uint16_t{17}, EnvironmentalQueryMode::Sham}},
        {"ENV_SUBTHRESHOLD", {true, std::uint16_t{15514}, std::uint16_t{17}, EnvironmentalQueryMode::Intact}},
        {"ENV_CONTENT_19", {true, std::uint16_t{15515}, std::uint16_t{19}, EnvironmentalQueryMode::Intact}},
    }};
    const auto match = std::find_if(allowed.begin(), allowed.end(), [&](const auto& item) {
        return c.id == item.first && key == item.second;
    });
    if (match == allowed.end()) {
        throw std::invalid_argument(
            "F2 configuration is outside the six verified environmental arms");
    }
}

}  // namespace

ReusableRevisionResult run_reusable_revision(
    const ReusableRevisionConfig& c, v27::TickOptions options) {
    validate_f1(c);
    auto runtime = protocol_runtime(options);
    const auto geometry = protocol_geometry();
    ReusableRevisionResult result;
    schedule_c7_base(runtime, result.receipts, c.trained_relation, true);
    schedule_carrier(runtime, result.receipts, "revision.r1.onpath",
                     geometry.revision1, kRevisionTicks[0], kQueryRedirect,
                     81201, c.revision1);
    schedule_carrier(runtime, result.receipts, "revision.r1.sham",
                     geometry.revision1, kRevisionTicks[0], kQueryRedirect,
                     81301, c.sham1, 3);
    schedule_carrier(runtime, result.receipts, "query.q2",
                     geometry.response2, kQueryTicks[1], kCue, 81102,
                     kQueryLoads[1]);
    schedule_carrier(runtime, result.receipts, "revision.r2.onpath",
                     geometry.revision2, kRevisionTicks[1], kQueryRedirect,
                     81202, c.revision2);
    schedule_carrier(runtime, result.receipts, "revision.r2.sham",
                     geometry.revision2, kRevisionTicks[1], kQueryRedirect,
                     81302, c.sham2, 3);
    schedule_carrier(runtime, result.receipts, "query.q3",
                     geometry.response3, kQueryTicks[2], kCue, 81103,
                     kQueryLoads[2]);

    const std::set<std::uint64_t> checkpoints{34, 38, 46, 50, 58, 60};
    while (runtime.current_tick() <= 60) {
        const auto tick = runtime.current_tick();
        if (checkpoints.contains(tick)) {
            if (tick == 34) {
                result.response_loads[0] =
                    observed_load(runtime, geometry.response1);
                record_observation(result.checkpoints, "response1", runtime,
                                   geometry.response1);
            } else if (tick == 38) {
                result.post_revision_loads[0] =
                    observed_load(runtime, geometry.revision1);
                record_observation(result.checkpoints, "revision1", runtime,
                                   geometry.revision1);
            } else if (tick == 46) {
                result.response_loads[1] =
                    observed_load(runtime, geometry.response2);
                record_observation(result.checkpoints, "response2", runtime,
                                   geometry.response2);
            } else if (tick == 50) {
                result.post_revision_loads[1] =
                    observed_load(runtime, geometry.revision2);
                record_observation(result.checkpoints, "revision2", runtime,
                                   geometry.revision2);
            } else if (tick == 58) {
                result.response_loads[2] =
                    observed_load(runtime, geometry.response3);
                record_observation(result.checkpoints, "response3", runtime,
                                   geometry.response3);
            }
        }
        if (tick == 60) break;
        const auto info = runtime.advance();
        result.backend_fallback = result.backend_fallback || info.fallback;
    }
    finalize_receipts(runtime, result.receipts);
    result.all_inputs_applied_at_t0 = all_applied_at_zero(result.receipts);
    result.final_raw = runtime.raw_copy();
    result.final_clock = runtime.clock_copy();
    return result;
}

void save_reusable_revision_checkpoint(const ReusableRevisionConfig& c,
                                       std::uint64_t stop_at_tick,
                                       const std::string& path,
                                       v27::TickOptions options) {
    validate_f1(c);
    if (stop_at_tick == 0 || stop_at_tick >= 60) {
        throw std::invalid_argument("F1 checkpoint tick must be in [1,59]");
    }
    auto runtime = protocol_runtime(options);
    const auto geometry = protocol_geometry();
    std::vector<ProtocolReceipt> receipts;
    schedule_c7_base(runtime, receipts, c.trained_relation, true);
    schedule_carrier(runtime, receipts, "revision.r1.onpath",
                     geometry.revision1, kRevisionTicks[0], kQueryRedirect,
                     81201, c.revision1);
    schedule_carrier(runtime, receipts, "revision.r1.sham",
                     geometry.revision1, kRevisionTicks[0], kQueryRedirect,
                     81301, c.sham1, 3);
    schedule_carrier(runtime, receipts, "query.q2", geometry.response2,
                     kQueryTicks[1], kCue, 81102, kQueryLoads[1]);
    schedule_carrier(runtime, receipts, "revision.r2.onpath",
                     geometry.revision2, kRevisionTicks[1], kQueryRedirect,
                     81202, c.revision2);
    schedule_carrier(runtime, receipts, "revision.r2.sham",
                     geometry.revision2, kRevisionTicks[1], kQueryRedirect,
                     81302, c.sham2, 3);
    schedule_carrier(runtime, receipts, "query.q3", geometry.response3,
                     kQueryTicks[2], kCue, 81103, kQueryLoads[2]);

    std::array<std::uint16_t, 3> response{};
    std::array<std::uint16_t, 2> revisions{};
    bool fallback = false;
    while (runtime.current_tick() <= stop_at_tick) {
        const auto tick = runtime.current_tick();
        if (tick == 34) response[0] = observed_load(runtime, geometry.response1);
        if (tick == 38) revisions[0] = observed_load(runtime, geometry.revision1);
        if (tick == 46) response[1] = observed_load(runtime, geometry.response2);
        if (tick == 50) revisions[1] = observed_load(runtime, geometry.revision2);
        if (tick == 58) response[2] = observed_load(runtime, geometry.response3);
        if (tick == stop_at_tick) break;
        const auto info = runtime.advance();
        fallback = fallback || info.fallback;
    }
    runtime.set_protocol_phase("F1_REUSABLE_REVISION_TICK_" +
                               std::to_string(stop_at_tick));
    runtime.set_snapshot_metadata("protocol.id", kF1Id);
    runtime.set_snapshot_metadata("protocol.version", "1.0.0");
    runtime.set_snapshot_metadata("protocol.f1.id", c.id);
    runtime.set_snapshot_metadata("protocol.f1.response0", std::to_string(response[0]));
    runtime.set_snapshot_metadata("protocol.f1.response1", std::to_string(response[1]));
    runtime.set_snapshot_metadata("protocol.f1.response2", std::to_string(response[2]));
    runtime.set_snapshot_metadata("protocol.f1.revision0", std::to_string(revisions[0]));
    runtime.set_snapshot_metadata("protocol.f1.revision1", std::to_string(revisions[1]));
    runtime.set_snapshot_metadata("protocol.fallback", fallback ? "1" : "0");
    runtime.save_snapshot(path);
}

ReusableRevisionResult resume_reusable_revision_checkpoint(
    const std::string& path, v27::TickOptions options) {
    auto runtime = Runtime::load_snapshot(path);
    const auto protocol = runtime.snapshot_metadata("protocol.id");
    const auto version = runtime.snapshot_metadata("protocol.version");
    if (!protocol || *protocol != kF1Id || !version || *version != "1.0.0") {
        throw std::invalid_argument("snapshot is not an F1 v1.0.0 checkpoint");
    }
    if (runtime.current_tick() >= 60) {
        throw std::invalid_argument("F1 checkpoint is already terminal");
    }
    runtime.set_execution_options(options);
    const auto geometry = protocol_geometry();
    ReusableRevisionResult result;
    result.response_loads = {
        static_cast<std::uint16_t>(metadata_u64(runtime, "protocol.f1.response0")),
        static_cast<std::uint16_t>(metadata_u64(runtime, "protocol.f1.response1")),
        static_cast<std::uint16_t>(metadata_u64(runtime, "protocol.f1.response2")),
    };
    result.post_revision_loads = {
        static_cast<std::uint16_t>(metadata_u64(runtime, "protocol.f1.revision0")),
        static_cast<std::uint16_t>(metadata_u64(runtime, "protocol.f1.revision1")),
    };
    result.backend_fallback = metadata_bool(runtime, "protocol.fallback");
    while (runtime.current_tick() <= 60) {
        const auto tick = runtime.current_tick();
        if (tick == 34) result.response_loads[0] = observed_load(runtime, geometry.response1);
        if (tick == 38) result.post_revision_loads[0] = observed_load(runtime, geometry.revision1);
        if (tick == 46) result.response_loads[1] = observed_load(runtime, geometry.response2);
        if (tick == 50) result.post_revision_loads[1] = observed_load(runtime, geometry.revision2);
        if (tick == 58) result.response_loads[2] = observed_load(runtime, geometry.response3);
        if (tick == 60) break;
        const auto info = runtime.advance();
        result.backend_fallback = result.backend_fallback || info.fallback;
    }
    collect_runtime_receipts(runtime, result.receipts);
    result.all_inputs_applied_at_t0 = all_applied_at_zero(result.receipts);
    result.final_raw = runtime.raw_copy();
    result.final_clock = runtime.clock_copy();
    return result;
}

EnvironmentalReturnResult run_environmental_return(
    const EnvironmentalReturnConfig& c, v27::TickOptions options) {
    validate_f2(c);
    const auto geometry = protocol_geometry();
    const auto environment = geometry.revision1;
    const auto demux = protocol_plus(environment, Coordinate{-1, -1, -1});
    const auto query_sham = protocol_plus(demux, Coordinate{0, 4, 0});
    const auto return_site = protocol_plus(demux, Coordinate{0, 0, 4});
    const auto use1_site = protocol_plus(return_site, Coordinate{4, 0, 4});
    const auto return_redirect = protocol_plus(use1_site, Coordinate{4, 4, 4});
    const auto use2_site = protocol_plus(return_redirect, Coordinate{0, 4, 4});

    std::vector<std::uint64_t> raw(
        static_cast<std::size_t>(kProtocolN) * kProtocolN * kProtocolN, 0);
    std::vector<std::uint64_t> clock(raw.size(), 0);
    install_environment_support(raw, clock, environment,
                                c.environment_clock_phase);
    auto runtime = Runtime::import_research_state(
        kProtocolN, 0, std::move(raw), std::move(clock));
    runtime.set_execution_options(options);

    EnvironmentalReturnResult result;
    schedule_c7_base(runtime, result.receipts, c.trained_response, true,
                     c.marker_load);
    schedule_carrier(runtime, result.receipts, "environment.bias", environment,
                     kRevisionTicks[0], Direction{0, -1, 0}, 82001,
                     c.bias_load);
    if (c.query_mode != EnvironmentalQueryMode::Absent) {
        const auto target = c.query_mode == EnvironmentalQueryMode::Intact
                                ? demux
                                : query_sham;
        schedule_carrier(runtime, result.receipts, "environment.query", target,
                         39, Direction{0, 0, 1}, 82002, 23);
    }
    schedule_carrier(runtime, result.receipts, "return.partner", return_site,
                     43, Direction{1, 0, 0}, 82003, 31);
    schedule_carrier(runtime, result.receipts, "return.use1", use1_site, 47,
                     Direction{0, 1, 0}, 82004, 7);
    schedule_carrier(runtime, result.receipts, "return.redirect",
                     return_redirect, 51, Direction{-1, 0, 0}, 82005, 0);
    schedule_carrier(runtime, result.receipts, "return.use2", use2_site, 55,
                     Direction{1, 0, 0}, 82006, 5);

    const std::set<std::uint64_t> checkpoints{34, 38, 39, 43, 47, 51, 55, 56};
    while (runtime.current_tick() <= 56) {
        const auto tick = runtime.current_tick();
        if (checkpoints.contains(tick)) {
            if (tick == 34) {
                result.upstream_response_load =
                    observed_load(runtime, geometry.response1);
                record_observation(result.checkpoints, "upstream_response",
                                   runtime, geometry.response1);
            } else if (tick == 38) {
                result.environment_load = observed_load(runtime, environment);
                record_observation(result.checkpoints, "environment", runtime,
                                   environment);
            } else if (tick == 39) {
                result.downstream_loads[0] = observed_load(runtime, demux);
                record_observation(result.checkpoints, "demux", runtime, demux);
            } else if (tick == 43) {
                result.downstream_loads[1] = observed_load(runtime, return_site);
                record_observation(result.checkpoints, "return_site", runtime,
                                   return_site);
            } else if (tick == 47) {
                result.downstream_loads[2] = observed_load(runtime, use1_site);
                record_observation(result.checkpoints, "use1_site", runtime,
                                   use1_site);
            } else if (tick == 51) {
                result.downstream_loads[3] =
                    observed_load(runtime, return_redirect);
                record_observation(result.checkpoints, "return_redirect",
                                   runtime, return_redirect);
            } else if (tick == 55) {
                result.downstream_loads[4] = observed_load(runtime, use2_site);
                record_observation(result.checkpoints, "use2_site", runtime,
                                   use2_site);
            }
        }
        if (tick == 56) break;
        const auto info = runtime.advance();
        result.overflow_total += info.overflows;
        result.backend_fallback = result.backend_fallback || info.fallback;
    }
    finalize_receipts(runtime, result.receipts);
    result.all_inputs_applied_at_t0 = all_applied_at_zero(result.receipts);
    const auto query = std::find_if(
        result.receipts.begin(), result.receipts.end(), [](const auto& item) {
            return item.label == "environment.query";
        });
    result.query_admitted =
        query != result.receipts.end() &&
        query->receipt.status == EventStatus::Applied &&
        query->receipt.effective_tick == std::optional<std::uint64_t>{0};
    result.final_raw = runtime.raw_copy();
    result.final_clock = runtime.clock_copy();
    return result;
}

void save_environmental_return_checkpoint(
    const EnvironmentalReturnConfig& c, std::uint64_t stop_at_tick,
    const std::string& path, v27::TickOptions options) {
    validate_f2(c);
    if (stop_at_tick == 0 || stop_at_tick >= 56) {
        throw std::invalid_argument("F2 checkpoint tick must be in [1,55]");
    }
    const auto geometry = protocol_geometry();
    const auto environment = geometry.revision1;
    const auto demux = protocol_plus(environment, Coordinate{-1, -1, -1});
    const auto query_sham = protocol_plus(demux, Coordinate{0, 4, 0});
    const auto return_site = protocol_plus(demux, Coordinate{0, 0, 4});
    const auto use1_site = protocol_plus(return_site, Coordinate{4, 0, 4});
    const auto return_redirect = protocol_plus(use1_site, Coordinate{4, 4, 4});
    const auto use2_site = protocol_plus(return_redirect, Coordinate{0, 4, 4});

    std::vector<std::uint64_t> raw(
        static_cast<std::size_t>(kProtocolN) * kProtocolN * kProtocolN, 0);
    std::vector<std::uint64_t> clock(raw.size(), 0);
    install_environment_support(raw, clock, environment,
                                c.environment_clock_phase);
    auto runtime = Runtime::import_research_state(
        kProtocolN, 0, std::move(raw), std::move(clock));
    runtime.set_execution_options(options);
    std::vector<ProtocolReceipt> receipts;
    schedule_c7_base(runtime, receipts, c.trained_response, true, c.marker_load);
    schedule_carrier(runtime, receipts, "environment.bias", environment,
                     kRevisionTicks[0], Direction{0, -1, 0}, 82001,
                     c.bias_load);
    if (c.query_mode != EnvironmentalQueryMode::Absent) {
        const auto target = c.query_mode == EnvironmentalQueryMode::Intact
                                ? demux
                                : query_sham;
        schedule_carrier(runtime, receipts, "environment.query", target, 39,
                         Direction{0, 0, 1}, 82002, 23);
    }
    schedule_carrier(runtime, receipts, "return.partner", return_site, 43,
                     Direction{1, 0, 0}, 82003, 31);
    schedule_carrier(runtime, receipts, "return.use1", use1_site, 47,
                     Direction{0, 1, 0}, 82004, 7);
    schedule_carrier(runtime, receipts, "return.redirect", return_redirect,
                     51, Direction{-1, 0, 0}, 82005, 0);
    schedule_carrier(runtime, receipts, "return.use2", use2_site, 55,
                     Direction{1, 0, 0}, 82006, 5);

    std::uint16_t upstream = 0;
    std::uint16_t environmental = 0;
    std::array<std::uint16_t, 5> downstream{};
    std::uint64_t overflow = 0;
    bool fallback = false;
    while (runtime.current_tick() <= stop_at_tick) {
        const auto tick = runtime.current_tick();
        if (tick == 34) upstream = observed_load(runtime, geometry.response1);
        if (tick == 38) environmental = observed_load(runtime, environment);
        if (tick == 39) downstream[0] = observed_load(runtime, demux);
        if (tick == 43) downstream[1] = observed_load(runtime, return_site);
        if (tick == 47) downstream[2] = observed_load(runtime, use1_site);
        if (tick == 51) downstream[3] = observed_load(runtime, return_redirect);
        if (tick == 55) downstream[4] = observed_load(runtime, use2_site);
        if (tick == stop_at_tick) break;
        const auto info = runtime.advance();
        overflow += info.overflows;
        fallback = fallback || info.fallback;
    }
    runtime.set_protocol_phase("F2_ENVIRONMENTAL_RETURN_TICK_" +
                               std::to_string(stop_at_tick));
    runtime.set_snapshot_metadata("protocol.id", kF2Id);
    runtime.set_snapshot_metadata("protocol.version", "1.0.0");
    runtime.set_snapshot_metadata("protocol.f2.id", c.id);
    runtime.set_snapshot_metadata("protocol.f2.upstream", std::to_string(upstream));
    runtime.set_snapshot_metadata("protocol.f2.environment", std::to_string(environmental));
    for (std::size_t i = 0; i < downstream.size(); ++i) {
        runtime.set_snapshot_metadata("protocol.f2.downstream" + std::to_string(i),
                                      std::to_string(downstream[i]));
    }
    runtime.set_snapshot_metadata("protocol.f2.overflow", std::to_string(overflow));
    runtime.set_snapshot_metadata("protocol.fallback", fallback ? "1" : "0");
    runtime.save_snapshot(path);
}

EnvironmentalReturnResult resume_environmental_return_checkpoint(
    const std::string& path, v27::TickOptions options) {
    auto runtime = Runtime::load_snapshot(path);
    const auto protocol = runtime.snapshot_metadata("protocol.id");
    const auto version = runtime.snapshot_metadata("protocol.version");
    if (!protocol || *protocol != kF2Id || !version || *version != "1.0.0") {
        throw std::invalid_argument("snapshot is not an F2 v1.0.0 checkpoint");
    }
    if (runtime.current_tick() >= 56) {
        throw std::invalid_argument("F2 checkpoint is already terminal");
    }
    runtime.set_execution_options(options);
    const auto geometry = protocol_geometry();
    const auto environment = geometry.revision1;
    const auto demux = protocol_plus(environment, Coordinate{-1, -1, -1});
    const auto return_site = protocol_plus(demux, Coordinate{0, 0, 4});
    const auto use1_site = protocol_plus(return_site, Coordinate{4, 0, 4});
    const auto return_redirect = protocol_plus(use1_site, Coordinate{4, 4, 4});
    const auto use2_site = protocol_plus(return_redirect, Coordinate{0, 4, 4});
    EnvironmentalReturnResult result;
    result.upstream_response_load = static_cast<std::uint16_t>(
        metadata_u64(runtime, "protocol.f2.upstream"));
    result.environment_load = static_cast<std::uint16_t>(
        metadata_u64(runtime, "protocol.f2.environment"));
    for (std::size_t i = 0; i < result.downstream_loads.size(); ++i) {
        result.downstream_loads[i] = static_cast<std::uint16_t>(
            metadata_u64(runtime, "protocol.f2.downstream" + std::to_string(i)));
    }
    result.overflow_total = metadata_u64(runtime, "protocol.f2.overflow");
    result.backend_fallback = metadata_bool(runtime, "protocol.fallback");
    while (runtime.current_tick() <= 56) {
        const auto tick = runtime.current_tick();
        if (tick == 34) result.upstream_response_load = observed_load(runtime, geometry.response1);
        if (tick == 38) result.environment_load = observed_load(runtime, environment);
        if (tick == 39) result.downstream_loads[0] = observed_load(runtime, demux);
        if (tick == 43) result.downstream_loads[1] = observed_load(runtime, return_site);
        if (tick == 47) result.downstream_loads[2] = observed_load(runtime, use1_site);
        if (tick == 51) result.downstream_loads[3] = observed_load(runtime, return_redirect);
        if (tick == 55) result.downstream_loads[4] = observed_load(runtime, use2_site);
        if (tick == 56) break;
        const auto info = runtime.advance();
        result.overflow_total += info.overflows;
        result.backend_fallback = result.backend_fallback || info.fallback;
    }
    collect_runtime_receipts(runtime, result.receipts);
    result.all_inputs_applied_at_t0 = all_applied_at_zero(result.receipts);
    const auto query = std::find_if(result.receipts.begin(), result.receipts.end(),
                                    [](const auto& item) {
        return item.label == "environment.query";
    });
    result.query_admitted = query != result.receipts.end() &&
                            query->receipt.status == EventStatus::Applied &&
                            query->receipt.effective_tick ==
                                std::optional<std::uint64_t>{0};
    result.final_raw = runtime.raw_copy();
    result.final_clock = runtime.clock_copy();
    return result;
}

const char* to_string(ProtocolModality value) noexcept {
    switch (value) {
        case ProtocolModality::NativePostHostStop: return "NATIVE_POST_HOST_STOP";
        case ProtocolModality::Coupled: return "COUPLED";
        case ProtocolModality::Diagnostic: return "DIAGNOSTIC";
    }
    return "UNKNOWN";
}

const char* to_string(DelayPositionArm value) noexcept {
    switch (value) {
        case DelayPositionArm::Native: return "NATIVE";
        case DelayPositionArm::ReversedCalibration: return "REVERSED_CALIBRATION";
        case DelayPositionArm::TargetAbsent: return "TARGET_ABSENT";
    }
    return "UNKNOWN";
}

const char* to_string(RepairArm value) noexcept {
    switch (value) {
        case RepairArm::Treatment: return "TREATMENT";
        case RepairArm::BackupUntrained: return "BACKUP_UNTRAINED";
        case RepairArm::BackupDirectionReset: return "BACKUP_DIRECTION_RESET";
        case RepairArm::NoBackup: return "NO_BACKUP";
        case RepairArm::PathCut: return "PATH_CUT";
        case RepairArm::OffpathCut: return "OFFPATH_CUT";
        case RepairArm::WrongReceiver: return "WRONG_RECEIVER";
    }
    return "UNKNOWN";
}

const char* to_string(AccessibilityStatus value) noexcept {
    switch (value) {
        case AccessibilityStatus::Constructed: return "CONSTRUCTED";
        case AccessibilityStatus::Reached: return "REACHED";
        case AccessibilityStatus::Acquired: return "ACQUIRED";
        case AccessibilityStatus::NotDemonstrated: return "NOT_DEMONSTRATED";
    }
    return "UNKNOWN";
}

const char* to_string(EnvironmentalQueryMode value) noexcept {
    switch (value) {
        case EnvironmentalQueryMode::Intact: return "INTACT";
        case EnvironmentalQueryMode::Absent: return "ABSENT";
        case EnvironmentalQueryMode::Sham: return "SHAM";
    }
    return "UNKNOWN";
}

}  // namespace dee::thinking::protocols
