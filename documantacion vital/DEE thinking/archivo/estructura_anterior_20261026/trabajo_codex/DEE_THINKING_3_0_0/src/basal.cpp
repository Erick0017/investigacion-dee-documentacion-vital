#include "dee_thinking/basal.hpp"

#include <algorithm>
#include <array>
#include <set>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace dee::thinking::basal {
namespace {

constexpr std::array<Coordinate, 4> kPatternA{{
    {-1,0,0},{-1,1,1},{0,0,1},{0,1,0}}};
constexpr std::array<Coordinate, 4> kPatternB{{
    {0,-1,0},{0,0,-1},{1,-1,-1},{1,0,0}}};
constexpr std::array<Coordinate, 26> kMoore{{
    {-1,-1,-1},{-1,-1,0},{-1,-1,1},{-1,0,-1},{-1,0,0},{-1,0,1},{-1,1,-1},{-1,1,0},{-1,1,1},
    {0,-1,-1},{0,-1,0},{0,-1,1},{0,0,-1},{0,0,1},{0,1,-1},{0,1,0},{0,1,1},
    {1,-1,-1},{1,-1,0},{1,-1,1},{1,0,-1},{1,0,0},{1,0,1},{1,1,-1},{1,1,0},{1,1,1}
}};

Coordinate add(Coordinate q, Direction d, int k, int n) {
    return {v27::wrap_coordinate(q.x + d.dx * k, n),
            v27::wrap_coordinate(q.y + d.dy * k, n),
            v27::wrap_coordinate(q.z + d.dz * k, n)};
}

Coordinate add(Coordinate q, Coordinate d, int n) {
    return {v27::wrap_coordinate(q.x + d.x, n),
            v27::wrap_coordinate(q.y + d.y, n),
            v27::wrap_coordinate(q.z + d.z, n)};
}

std::string coordinate_string(Coordinate q) {
    return std::to_string(q.x) + "," + std::to_string(q.y) + "," + std::to_string(q.z);
}

Coordinate parse_coordinate(const std::string& value) {
    std::istringstream stream(value);
    Coordinate q{};
    char comma1{}, comma2{};
    if (!(stream >> q.x >> comma1 >> q.y >> comma2 >> q.z) || comma1 != ',' || comma2 != ',') {
        throw std::runtime_error("invalid basal coordinate metadata");
    }
    return q;
}

std::size_t index(Coordinate q, int n) {
    return v27::linear_index(q.x, q.y, q.z, n);
}

void put(std::vector<std::uint64_t>& raw, std::vector<std::uint64_t>& clocks,
         int n, Coordinate site, std::uint32_t state, std::uint16_t load,
         Direction direction, std::uint8_t semantic, std::uint64_t clock,
         const char* label) {
    const auto i = index(site, n);
    if (raw[i] != 0) {
        throw std::runtime_error(std::string("basal preparation overlap at ") + label);
    }
    raw[i] = v27::pack_record(state, load, direction.dx, direction.dy, direction.dz, semantic);
    clocks[i] = clock;
}

bool validated_origin(Coordinate q) {
    return q == Coordinate{15,15,15} || q == Coordinate{22,20,24} ||
           q == Coordinate{28,26,18};
}

void validate_config(const Config& config, bool require_seed = true) {
    if (require_seed && config.seed_snapshot.empty())
        throw std::invalid_argument("basal seed snapshot is required");
    if (config.dimension != 47) throw std::invalid_argument("published basal presets require N=47");
    if (config.action_distance != 5) throw std::invalid_argument("published basal presets require action_distance=5");
    if (config.execution.threads == 0) throw std::invalid_argument("backend threads must be positive");
    if (config.domain_mode == DomainMode::Validated && !validated_origin(config.origin)) {
        throw std::invalid_argument("origin outside validated basal translation set");
    }
    if (config.preset == Preset::ContextualRewrite) {
        if (config.history != History::AB)
            throw std::invalid_argument("contextual rewrite preset is validated only for AB history");
        if (config.control != Control::Full && config.control != Control::NoAction &&
            config.control != Control::ReturnCut && config.control != Control::OffPath &&
            config.control != Control::PhaseMiss)
            throw std::invalid_argument("control unsupported by contextual rewrite preset");
    }
}

Coordinate install_event(std::vector<std::uint64_t>& raw,
                         std::vector<std::uint64_t>& clocks, int n,
                         Coordinate memory, Coordinate target_offset,
                         Direction direction, bool early, std::uint32_t state,
                         const char* label) {
    const auto target = add(memory, target_offset, n);
    if (early) {
        put(raw, clocks, n, target, state, 0, direction, 1, 17, label);
        return target;
    }
    const auto source = add(target, direction, -1, n);
    put(raw, clocks, n, source, 0, 0, direction, 1, 19, label);
    return source;
}

struct TurnLoop {
    Coordinate action;
    Coordinate bend;
    Coordinate returned;
    Coordinate action_source;
    Coordinate bend_source_a;
    Coordinate bend_source_b;
    std::optional<Coordinate> blocker;
    std::vector<Coordinate> sources;
};

TurnLoop describe_turn_loop(int n, Coordinate origin, int sign, int distance,
                            Control control) {
    const Direction route{sign, 1, 0};
    const auto action = add(origin, route, distance, n);
    const int arrival = 3 + distance;
    const Direction action_turn{-sign, -1, 1};
    const auto action_source = add(action, action_turn, -arrival, n);
    const auto bend = add(action, Direction{0,0,1}, distance, n);
    const int bend_arrival = arrival + distance;
    const Direction return_direction{-sign,-1,-1};
    const auto bend_source_a = add(bend, return_direction, -bend_arrival, n);
    const auto bend_source_b = add(bend, Direction{0,0,-1}, -bend_arrival, n);
    const auto returned = add(bend, return_direction, 1, n);
    const bool include_action = control != Control::ActionCut && control != Control::Bare;
    const bool include_return = control != Control::ReturnCut && control != Control::Bare;
    std::vector<Coordinate> sources;
    std::optional<Coordinate> blocker;
    if (include_action) sources = {action_source, bend_source_a, bend_source_b};
    if (include_action && !include_return) {
        const int blocker_steps = std::max(2, distance / 2);
        blocker = add(bend, return_direction, blocker_steps, n);
        sources.push_back(*blocker);
    }
    return {action, bend, returned, action_source, bend_source_a,
            bend_source_b, blocker, std::move(sources)};
}

TurnLoop install_turn_loop(std::vector<std::uint64_t>& raw,
                           std::vector<std::uint64_t>& clocks, int n,
                           Coordinate origin, int sign, int distance,
                           Control control, const char* prefix) {
    const Direction action_turn{-sign, -1, 1};
    const Direction return_direction{-sign,-1,-1};
    auto loop = describe_turn_loop(n, origin, sign, distance, control);
    const bool include_action = control != Control::ActionCut && control != Control::Bare;
    const bool include_return = control != Control::ReturnCut && control != Control::Bare;
    if (include_action) {
        put(raw, clocks, n, loop.action_source, static_cast<std::uint32_t>(7100 + sign), 11,
            action_turn, 4, 31, prefix);
        put(raw, clocks, n, loop.bend_source_a, static_cast<std::uint32_t>(7200 + sign), 13,
            return_direction, 4, 41, prefix);
        put(raw, clocks, n, loop.bend_source_b, static_cast<std::uint32_t>(7300 + sign), 17,
            {0,0,-1}, 4, 47, prefix);
    }
    if (include_action && !include_return) {
        put(raw, clocks, n, *loop.blocker, static_cast<std::uint32_t>(7400 + sign), 0,
            {0,0,0}, 4, 43, prefix);
    }
    return loop;
}

Ports install_relational(std::vector<std::uint64_t>& raw,
                         std::vector<std::uint64_t>& clocks,
                         const Config& config) {
    const int n = config.dimension;
    const auto c = config.origin;
    const auto a = add(c, Coordinate{-1,0,0}, n);
    const auto b = add(c, Coordinate{1,0,0}, n);
    put(raw, clocks, n, a, 1000, 100, {0,0,0}, 1, 260, "memory.a");
    put(raw, clocks, n, b, 2000, 100, {0,0,0}, 1, 260, "memory.b");
    Ports ports{};
    ports.origin = c; ports.a = a; ports.b = b; ports.comparator = c;
    for (std::size_t i = 0; i < kPatternA.size(); ++i) {
        const auto q = add(a, kPatternA[i], n);
        put(raw, clocks, n, q, static_cast<std::uint32_t>(3000 + i), 0,
            {0,0,0}, 4, 31 + i, "support.a");
        ports.supports.push_back(q);
    }
    for (std::size_t i = 0; i < kPatternB.size(); ++i) {
        const auto q = add(b, kPatternB[i], n);
        put(raw, clocks, n, q, static_cast<std::uint32_t>(4000 + i), 0,
            {0,0,0}, 4, 41 + i, "support.b");
        ports.supports.push_back(q);
    }
    auto add_history = [&](Coordinate memory, Coordinate offset, Direction direction,
                           bool early, std::uint32_t state, const char* label) {
        ports.event_sources.push_back(install_event(
            raw, clocks, n, memory, offset, direction, early, state, label));
    };
    switch (config.history) {
        case History::AB:
            add_history(a, {0,-1,0}, {0,0,-1}, true, 5000, "event.a");
            add_history(b, {0,1,0}, {0,0,1}, false, 5001, "event.b");
            break;
        case History::BA:
            add_history(a, {0,-1,0}, {0,0,-1}, false, 5000, "event.a");
            add_history(b, {0,1,0}, {0,0,1}, true, 5001, "event.b");
            break;
        case History::Simultaneous:
            add_history(a, {0,-1,0}, {0,0,-1}, true, 5000, "event.a");
            add_history(b, {0,1,0}, {0,0,1}, true, 5001, "event.b");
            break;
        case History::Sham: {
            const auto sham = add(c, Direction{0,0,1}, 6, n);
            put(raw, clocks, n, sham, 5099, 0,
                {0,0,1}, 1, 17, "event.sham");
            ports.event_sources.push_back(sham);
            break;
        }
        case History::H0: break;
    }
    ports.reader_source = add(c, Coordinate{0,-2,0}, n);
    if (config.control != Control::ReadCut) {
        put(raw, clocks, n, ports.reader_source, 6000, 7, {0,1,0}, 4, 23,
            "reader.source");
    }
    const auto plus = install_turn_loop(raw, clocks, n, c, 1,
                                        config.action_distance, config.control,
                                        "environment.plus");
    const auto minus = install_turn_loop(raw, clocks, n, c, -1,
                                         config.action_distance, config.control,
                                         "environment.minus");
    ports.action_site = plus.action;
    ports.bend_site = plus.bend;
    ports.return_site = plus.returned;
    ports.environmental_sources.insert(ports.environmental_sources.end(),
                                       plus.sources.begin(), plus.sources.end());
    ports.environmental_sources.insert(ports.environmental_sources.end(),
                                       minus.sources.begin(), minus.sources.end());
    return ports;
}

void erase_site(std::vector<std::uint64_t>& raw,
                std::vector<std::uint64_t>& clocks, int n, Coordinate site) {
    const auto i = index(site, n);
    raw[i] = 0;
    clocks[i] = 0;
}

Ports install_contextual(std::vector<std::uint64_t>& raw,
                         std::vector<std::uint64_t>& clocks,
                         const Config& config) {
    Config base = config;
    base.control = Control::Bare;
    Ports ports = install_relational(raw, clocks, base);
    const int n = config.dimension;
    const auto c = config.origin;
    erase_site(raw, clocks, n, ports.reader_source);
    const auto query = add(c, Coordinate{0,-1,0}, n);
    ports.reader_source = query;
    if (config.control != Control::NoAction) {
        put(raw, clocks, n, query, 6000, 7, {0,1,0}, 5, 23, "single_orphan_query");
    }
    put(raw, clocks, n, add(c, Coordinate{0,1,0}, n), 6099, 0, {0,0,0}, 5, 29,
        "pre_relational_output_absorber");
    const std::array<Coordinate,2> sinks{{
        add(c, Direction{-1,-1,-10}, 1, n), add(c, Direction{1,1,10}, 1, n)}};
    for (std::size_t i = 0; i < sinks.size(); ++i) {
        put(raw, clocks, n, sinks[i], static_cast<std::uint32_t>(8100 + i), 0,
            {0,0,0}, 4, 61 + i, "history_sink");
    }
    const int phase_shift = config.control == Control::PhaseMiss ? 1 : 0;
    const int d = 16;
    const int first_reader_arrival = 2 + d + phase_shift;
    const auto action_site = add(c, Direction{1,1,0}, d, n);
    const Direction action_turn{-1,-1,1};
    const auto action_source = add(action_site, action_turn, -first_reader_arrival, n);
    const int first_leg = 36;
    const auto bend_site = add(action_site, Direction{0,0,1}, first_leg, n);
    const int bend_arrival = first_reader_arrival + first_leg;
    const Direction bend_aux{1,1,-1};
    const auto bend_source_a = add(bend_site, bend_aux, -bend_arrival, n);
    const Direction middle{1,1,0};
    const int middle_leg = 40;
    const auto bend2_site = add(bend_site, middle, middle_leg, n);
    const int bend2_arrival = bend_arrival + middle_leg;
    const Direction bend2_aux = config.control == Control::OffPath
        ? Direction{-1,0,-1} : Direction{0,0,-1};
    const Direction return_direction = config.control == Control::OffPath
        ? Direction{0,1,-1} : Direction{1,1,-1};
    const auto bend_source_b = add(bend2_site, bend2_aux, -bend2_arrival, n);
    const int return_steps = 37;
    const auto return_target = add(bend2_site, return_direction, return_steps, n);

    std::set<std::size_t> keep;
    for (const auto q : ports.supports) keep.insert(index(q, n));
    for (const auto q : std::array<Coordinate,8>{ports.a, ports.b, ports.comparator,
             query, return_target, add(c, Coordinate{-1,-1,0}, n),
             add(c, Coordinate{1,1,-1}, n), add(c, Coordinate{1,1,0}, n)})
        keep.insert(index(q, n));
    std::uint32_t envelope_state = 8200;
    for (const auto center : std::array<Coordinate,2>{ports.a, ports.b}) {
        for (const auto offset : kMoore) {
            const auto q = add(center, offset, n);
            const auto i = index(q, n);
            if (keep.count(i) || raw[i] != 0) continue;
            put(raw, clocks, n, q, envelope_state++, 0, {0,0,0}, 5, 67,
                "causal_envelope");
        }
    }
    put(raw, clocks, n, action_source, 7101, 11, action_turn, 4, 31,
        "feedback.action_turn_source");
    put(raw, clocks, n, bend_source_a, 7201, 13, bend_aux, 1, 41,
        "feedback.bend_source_a");
    if (config.control != Control::ReturnCut) {
        put(raw, clocks, n, bend_source_b, 7301, 17, bend2_aux, 1, 47,
            "feedback.bend_source_b");
    }
    ports.environmental_sources = {action_source, bend_source_a};
    if (config.control != Control::ReturnCut) ports.environmental_sources.push_back(bend_source_b);
    ports.action_site = action_site;
    ports.return_site = return_target;
    ports.bend_site = bend_site;
    ports.bend2_site = bend2_site;
    return ports;
}

Ports derive_ports(const Config& config) {
    Ports ports{};
    const int n = config.dimension;
    const auto c = config.origin;
    ports.origin = c;
    ports.a = add(c, Coordinate{-1,0,0}, n);
    ports.b = add(c, Coordinate{1,0,0}, n);
    ports.comparator = c;
    ports.reader_source = add(c, Coordinate{0,-2,0}, n);
    for (const auto offset : kPatternA) ports.supports.push_back(add(ports.a, offset, n));
    for (const auto offset : kPatternB) ports.supports.push_back(add(ports.b, offset, n));

    auto remember_event_source = [&](Coordinate memory, Coordinate offset,
                                     Direction direction, bool early) {
        const auto target = add(memory, offset, n);
        ports.event_sources.push_back(early ? target : add(target, direction, -1, n));
    };
    switch (config.history) {
        case History::AB:
            remember_event_source(ports.a, {0,-1,0}, {0,0,-1}, true);
            remember_event_source(ports.b, {0,1,0}, {0,0,1}, false);
            break;
        case History::BA:
            remember_event_source(ports.a, {0,-1,0}, {0,0,-1}, false);
            remember_event_source(ports.b, {0,1,0}, {0,0,1}, true);
            break;
        case History::Simultaneous:
            remember_event_source(ports.a, {0,-1,0}, {0,0,-1}, true);
            remember_event_source(ports.b, {0,1,0}, {0,0,1}, true);
            break;
        case History::Sham:
            ports.event_sources.push_back(add(c, Direction{0,0,1}, 6, n));
            break;
        case History::H0: break;
    }

    if (config.preset == Preset::ContextualRewrite) {
        const int shift = config.control == Control::PhaseMiss ? 1 : 0;
        const int arrival = 18 + shift;
        const auto action = add(c, Direction{1,1,0}, 16, n);
        const Direction action_turn{-1,-1,1};
        const auto action_source = add(action, action_turn, -arrival, n);
        const auto bend = add(action, Direction{0,0,1}, 36, n);
        const int bend_arrival = arrival + 36;
        const Direction bend_aux{1,1,-1};
        const auto bend_source_a = add(bend, bend_aux, -bend_arrival, n);
        const auto bend2 = add(bend, Direction{1,1,0}, 40, n);
        const int bend2_arrival = bend_arrival + 40;
        const Direction bend2_aux = config.control == Control::OffPath
            ? Direction{-1,0,-1} : Direction{0,0,-1};
        const auto bend_source_b = add(bend2, bend2_aux, -bend2_arrival, n);
        const Direction ret = config.control == Control::OffPath ? Direction{0,1,-1} : Direction{1,1,-1};
        ports.reader_source = add(c, Coordinate{0,-1,0}, n);
        ports.action_site = action;
        ports.bend_site = bend;
        ports.bend2_site = bend2;
        ports.return_site = add(bend2, ret, 37, n);
        ports.environmental_sources = {action_source, bend_source_a};
        if (config.control != Control::ReturnCut) {
            ports.environmental_sources.push_back(bend_source_b);
        }
    } else {
        const auto plus = describe_turn_loop(n, c, 1, config.action_distance,
                                             config.control);
        const auto minus = describe_turn_loop(n, c, -1, config.action_distance,
                                              config.control);
        ports.action_site = plus.action;
        ports.bend_site = plus.bend;
        ports.return_site = plus.returned;
        ports.environmental_sources = plus.sources;
        ports.environmental_sources.insert(ports.environmental_sources.end(),
                                           minus.sources.begin(), minus.sources.end());
    }
    return ports;
}

template <typename Enum>
Enum parse_enum(const std::string& text);

template <> Preset parse_enum<Preset>(const std::string& text) {
    if (text == "relational_body") return Preset::RelationalBody;
    if (text == "contextual_rewrite") return Preset::ContextualRewrite;
    throw std::runtime_error("unknown basal preset metadata");
}
template <> History parse_enum<History>(const std::string& text) {
    if (text == "AB") return History::AB; if (text == "BA") return History::BA;
    if (text == "H0") return History::H0; if (text == "simultaneous") return History::Simultaneous;
    if (text == "sham") return History::Sham;
    throw std::runtime_error("unknown basal history metadata");
}
template <> Control parse_enum<Control>(const std::string& text) {
    if (text == "full") return Control::Full; if (text == "no_action") return Control::NoAction;
    if (text == "return_cut") return Control::ReturnCut; if (text == "off_path") return Control::OffPath;
    if (text == "phase_miss") return Control::PhaseMiss; if (text == "bare") return Control::Bare;
    if (text == "read_cut") return Control::ReadCut; if (text == "action_cut") return Control::ActionCut;
    throw std::runtime_error("unknown basal control metadata");
}
template <> DomainMode parse_enum<DomainMode>(const std::string& text) {
    if (text == "validated") return DomainMode::Validated;
    if (text == "research") return DomainMode::Research;
    throw std::runtime_error("unknown basal domain metadata");
}

std::string required_metadata(const Runtime& runtime, const std::string& key) {
    const auto value = runtime.snapshot_metadata(key);
    if (!value) throw std::runtime_error("snapshot lacks basal metadata: " + key);
    return *value;
}

void apply_metadata(Runtime& runtime, const Config& config, std::uint64_t t0) {
    runtime.set_snapshot_metadata("dee_thinking.basal.schema", "1");
    runtime.set_snapshot_metadata("dee_thinking.basal.recipe", "mbp4.reference.v1");
    runtime.set_snapshot_metadata("dee_thinking.basal.preset", to_string(config.preset));
    runtime.set_snapshot_metadata("dee_thinking.basal.history", to_string(config.history));
    runtime.set_snapshot_metadata("dee_thinking.basal.control", to_string(config.control));
    runtime.set_snapshot_metadata("dee_thinking.basal.domain", to_string(config.domain_mode));
    runtime.set_snapshot_metadata("dee_thinking.basal.origin", coordinate_string(config.origin));
    runtime.set_snapshot_metadata("dee_thinking.basal.action_distance", std::to_string(config.action_distance));
    runtime.set_snapshot_metadata("dee_thinking.basal.t0", std::to_string(t0));
    runtime.set_snapshot_metadata("dee_thinking.basal.seed_id", "OBP_FRESH_VALIDATED_T32");
}

}  // namespace

const char* to_string(Preset value) noexcept {
    switch (value) { case Preset::RelationalBody: return "relational_body";
                     case Preset::ContextualRewrite: return "contextual_rewrite"; }
    return "unknown";
}
const char* to_string(History value) noexcept {
    switch (value) { case History::AB: return "AB"; case History::BA: return "BA";
        case History::H0: return "H0"; case History::Simultaneous: return "simultaneous";
        case History::Sham: return "sham"; }
    return "unknown";
}
const char* to_string(Control value) noexcept {
    switch (value) { case Control::Full: return "full"; case Control::NoAction: return "no_action";
        case Control::ReturnCut: return "return_cut"; case Control::OffPath: return "off_path";
        case Control::PhaseMiss: return "phase_miss"; case Control::Bare: return "bare";
        case Control::ReadCut: return "read_cut"; case Control::ActionCut: return "action_cut"; }
    return "unknown";
}
const char* to_string(DomainMode value) noexcept {
    switch (value) { case DomainMode::Validated: return "validated";
                     case DomainMode::Research: return "research"; }
    return "unknown";
}
const char* to_string(Availability value) noexcept {
    switch (value) { case Availability::Available: return "available";
        case Availability::MissingA: return "missing_a"; case Availability::MissingB: return "missing_b";
        case Availability::MissingComparator: return "missing_comparator"; }
    return "unknown";
}

Config Config::relational_reference(std::string seed) {
    Config config{};
    config.seed_snapshot = std::move(seed);
    return config;
}

Config Config::contextual_reference(std::string seed) {
    Config config{};
    config.preset = Preset::ContextualRewrite;
    config.control = Control::Full;
    config.seed_snapshot = std::move(seed);
    return config;
}

World World::create(const Config& config) {
    validate_config(config);
    Runtime seed = Runtime::load_snapshot(config.seed_snapshot);
    if (seed.dimension() != config.dimension || seed.current_tick() != 32) {
        throw std::invalid_argument("unexpected basal seed dimension or tick");
    }
    if (!seed.channel_names().empty() || !seed.receipts().empty()) {
        throw std::invalid_argument("basal seed must not contain channels or receipts");
    }
    auto raw = seed.raw_copy();
    auto clocks = seed.clock_copy();
    Ports ports = config.preset == Preset::RelationalBody
        ? install_relational(raw, clocks, config)
        : install_contextual(raw, clocks, config);
    Runtime runtime = Runtime::import_research_state(
        config.dimension, seed.current_tick(), std::move(raw), std::move(clocks));
    runtime.set_execution_options(config.execution);
    runtime.set_protocol_phase("basal.prepared");
    apply_metadata(runtime, config, runtime.current_tick());
    return World(std::make_unique<Runtime>(std::move(runtime)), config,
                 std::move(ports), seed.current_tick());
}

World World::attach(Runtime& runtime, Config config, Ports ports,
                    std::uint64_t t0_tick) {
    validate_config(config, false);
    if (runtime.dimension() != config.dimension) {
        throw std::invalid_argument("attached Runtime dimension does not match basal config");
    }
    if (t0_tick > runtime.current_tick()) {
        throw std::invalid_argument("attached basal t0 is later than the Runtime tick");
    }
    // Attaching is an inert view operation: reflect the owner's current
    // scheduler setting rather than silently changing it.
    config.execution = runtime.execution_options();
    return World(runtime, std::move(config), std::move(ports), t0_tick);
}

World World::load_snapshot(const std::string& path) {
    Runtime runtime = Runtime::load_snapshot(path);
    if (required_metadata(runtime, "dee_thinking.basal.schema") != "1") {
        throw std::runtime_error("unsupported basal snapshot schema");
    }
    if (required_metadata(runtime, "dee_thinking.basal.recipe") !=
        "mbp4.reference.v1") {
        throw std::runtime_error("unsupported basal snapshot recipe");
    }
    if (required_metadata(runtime, "dee_thinking.basal.seed_id") !=
        "OBP_FRESH_VALIDATED_T32") {
        throw std::runtime_error("unsupported basal snapshot seed identity");
    }
    Config config{};
    config.preset = parse_enum<Preset>(required_metadata(runtime, "dee_thinking.basal.preset"));
    config.history = parse_enum<History>(required_metadata(runtime, "dee_thinking.basal.history"));
    config.control = parse_enum<Control>(required_metadata(runtime, "dee_thinking.basal.control"));
    config.domain_mode = parse_enum<DomainMode>(required_metadata(runtime, "dee_thinking.basal.domain"));
    config.dimension = runtime.dimension();
    config.origin = parse_coordinate(required_metadata(runtime, "dee_thinking.basal.origin"));
    config.action_distance = std::stoi(required_metadata(runtime, "dee_thinking.basal.action_distance"));
    config.execution = runtime.execution_options();
    const auto t0 = std::stoull(required_metadata(runtime, "dee_thinking.basal.t0"));
    validate_config(config, false);
    if (t0 != 32 || t0 > runtime.current_tick()) {
        throw std::runtime_error("incoherent basal snapshot t0");
    }
    return World(std::make_unique<Runtime>(std::move(runtime)), config,
                 derive_ports(config), t0);
}

Observation World::observe() const {
    Observation out{};
    out.absolute_tick = runtime().current_tick();
    out.relative_tick = out.absolute_tick >= t0_tick_ ? out.absolute_tick - t0_tick_ : 0;
    const auto a = runtime().observe(ports_.a);
    const auto b = runtime().observe(ports_.b);
    const auto comparator = runtime().observe(ports_.comparator);
    if (a.raw != 0) out.a = a;
    if (b.raw != 0) out.b = b;
    if (comparator.raw != 0) out.comparator = comparator;
    if (!out.a) out.availability = Availability::MissingA;
    else if (!out.b) out.availability = Availability::MissingB;
    else if (!out.comparator) out.availability = Availability::MissingComparator;
    else out.availability = Availability::Available;
    if (out.a && out.b) {
        out.delta = static_cast<std::int64_t>(out.a->record.s_reg) -
                    static_cast<std::int64_t>(out.b->record.s_reg);
    }
    if (out.comparator) out.axis_projection = static_cast<int>(out.comparator->record.dx);
    out.supports = runtime().observe_many(ports_.supports);
    return out;
}

World World::fork() const {
    return World(std::make_unique<Runtime>(runtime().fork()), config_, ports_, t0_tick_);
}

World World::diagnostic_fork(const std::vector<ResearchStateEdit>& edits,
                             bool authorize_diagnostic_intervention) const {
    return World(std::make_unique<Runtime>(runtime().diagnostic_fork(
                     edits, authorize_diagnostic_intervention)),
                 config_, ports_, t0_tick_);
}

void World::save_snapshot(const std::string& path) {
    apply_metadata(runtime(), config_, t0_tick_);
    runtime().save_snapshot(path);
}

}  // namespace dee::thinking::basal
