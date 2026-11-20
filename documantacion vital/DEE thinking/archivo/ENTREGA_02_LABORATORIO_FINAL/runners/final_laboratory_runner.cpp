#include "dee_thinking/kernel_v27.hpp"
#include "dee_thinking/runtime.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
using dee::thinking::ChannelSpec;
using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::EventReceipt;
using dee::thinking::EventStatus;
using dee::thinking::InputRequest;
using dee::thinking::Observation;
using dee::thinking::Runtime;

namespace {

constexpr int N = 127;
constexpr Coordinate J{63, 63, 63};
constexpr Direction CUE{1, 0, 0};
constexpr Direction TEACHER{-1, 1, 0};
constexpr Direction MEMORY{0, 1, 0};
constexpr Direction PROGRAMMER{1, -1, 0};
constexpr Direction PROGRAMMED{1, 0, 0};
constexpr Direction REDIRECT{-1, 1, 0};
constexpr Direction RESPONSE{1, 1, 0};
constexpr Direction QUERY_REDIRECT{-1, 0, 0};
constexpr Direction MARKER_DIRECTION{0, -1, 0};

constexpr std::uint64_t TRAIN_TICK = 5;
constexpr std::uint64_t CONSEQUENCE_TICK = 8;
constexpr std::uint64_t PROGRAM_TICK = 12;
constexpr std::uint64_t REDIRECT_TICK = 18;
constexpr std::array<std::uint64_t, 3> QUERY_TICKS{{34, 46, 58}};
constexpr std::array<std::uint64_t, 2> REVISION_TICKS{{38, 50}};
constexpr std::array<std::uint16_t, 3> QUERY_LOADS{{7, 5, 3}};
constexpr std::uint16_t BASE_CUE_LOAD = 4083;
constexpr std::uint16_t BASE_TEACHER_LOAD = 19;
constexpr std::uint16_t SUPPLY_LOAD = 23;
constexpr std::uint16_t MARKER_LOAD = 17;

struct Geometry {
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

struct TrackedReceipt {
    std::string label;
    EventReceipt initial;
    EventReceipt final;
};

struct TraceRow {
    std::string family;
    std::string backend;
    std::string arm;
    std::uint64_t tick{};
    std::string site;
    Observation observation;
    dee::v27::TickInfo info{};
};

struct F1Spec {
    std::string id;
    std::uint16_t revision1{};
    std::uint16_t revision2{};
    std::uint16_t sham1{};
    std::uint16_t sham2{};
    bool teacher{true};
};

struct F1Result {
    F1Spec spec;
    std::string backend;
    std::vector<TrackedReceipt> receipts;
    std::map<std::uint64_t, std::map<std::string, Observation>> checkpoints;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
    bool fallback{};
};

enum class QueryMode { Intact, Absent, Sham };

struct F2Spec {
    std::string id;
    bool response{true};
    std::uint16_t bias_load{15515};
    std::uint16_t marker_load{17};
    QueryMode query_mode{QueryMode::Intact};
    std::uint64_t environment_clock_phase{353};
};

struct F2Result {
    F2Spec spec;
    std::string backend;
    std::vector<TrackedReceipt> receipts;
    std::map<std::uint64_t, std::map<std::string, Observation>> checkpoints;
    std::vector<std::tuple<std::uint64_t, Coordinate, Observation>> local_nonzero;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
    std::uint64_t overflow_total{};
    bool fallback{};
};

int wrap(int value) {
    int r = value % N;
    return r < 0 ? r + N : r;
}

Coordinate plus(Coordinate q, Direction d, int scale = 1) {
    return {wrap(q.x + d.dx * scale), wrap(q.y + d.dy * scale), wrap(q.z + d.dz * scale)};
}

Coordinate plus(Coordinate a, Coordinate b) {
    return {wrap(a.x + b.x), wrap(a.y + b.y), wrap(a.z + b.z)};
}

Coordinate source_for(Coordinate target, std::uint64_t tick, Direction direction) {
    const int t = static_cast<int>(tick % static_cast<std::uint64_t>(N));
    return plus(target, direction, -t);
}

std::size_t index(Coordinate q) {
    return dee::v27::linear_index(q.x, q.y, q.z, N);
}

Geometry geometry() {
    Geometry g;
    g.junction = J;
    g.program = plus(J, MEMORY, static_cast<int>(PROGRAM_TICK - TRAIN_TICK));
    g.consequence = plus(g.program, PROGRAMMER, -static_cast<int>(PROGRAM_TICK - CONSEQUENCE_TICK));
    g.redirect = plus(g.program, PROGRAMMED, static_cast<int>(REDIRECT_TICK - PROGRAM_TICK));
    g.response1 = plus(g.redirect, MEMORY, static_cast<int>(QUERY_TICKS[0] - REDIRECT_TICK));
    g.revision1 = plus(g.response1, RESPONSE, static_cast<int>(REVISION_TICKS[0] - QUERY_TICKS[0]));
    g.response2 = plus(g.revision1, MEMORY, static_cast<int>(QUERY_TICKS[1] - REVISION_TICKS[0]));
    g.revision2 = plus(g.response2, RESPONSE, static_cast<int>(REVISION_TICKS[1] - QUERY_TICKS[1]));
    g.response3 = plus(g.revision2, MEMORY, static_cast<int>(QUERY_TICKS[2] - REVISION_TICKS[1]));
    return g;
}

std::string json_escape(const std::string& value) {
    std::ostringstream out;
    for (unsigned char c : value) {
        switch (c) {
            case '\\': out << "\\\\"; break;
            case '"': out << "\\\""; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (c < 0x20) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(c) << std::dec;
                else out << c;
        }
    }
    return out.str();
}

std::string quote(const std::string& value) { return "\"" + json_escape(value) + "\""; }

std::string coord_json(Coordinate q) {
    return "[" + std::to_string(q.x) + "," + std::to_string(q.y) + "," + std::to_string(q.z) + "]";
}

std::string obs_json(const Observation& o) {
    std::ostringstream out;
    out << "{\"tick\":" << o.tick << ",\"coordinate\":" << coord_json(o.coordinate)
        << ",\"raw\":" << o.raw << ",\"clock\":" << o.clock
        << ",\"state\":" << o.record.state << ",\"s_reg\":" << o.record.s_reg
        << ",\"direction\":[" << static_cast<int>(o.record.dx) << ','
        << static_cast<int>(o.record.dy) << ',' << static_cast<int>(o.record.dz) << ']'
        << ",\"semantic\":" << static_cast<unsigned>(o.record.semantic) << '}';
    return out.str();
}

std::string backend_label(dee::v27::Backend backend) {
    return dee::v27::backend_name(backend);
}

void track(std::vector<TrackedReceipt>& receipts, std::string label, EventReceipt receipt) {
    receipts.push_back({std::move(label), receipt, receipt});
}

void finalize_receipts(Runtime& runtime, std::vector<TrackedReceipt>& receipts) {
    for (auto& item : receipts) {
        const auto value = runtime.receipt(item.initial.id);
        if (!value) throw std::runtime_error("lost event receipt");
        item.final = *value;
    }
}

void schedule_carrier(Runtime& runtime, std::vector<TrackedReceipt>& receipts,
                      const std::string& label, Coordinate target, std::uint64_t arrival_tick,
                      Direction direction, std::uint32_t state, std::uint16_t load,
                      int z_shift = 0, std::uint8_t semantic = 1) {
    if (z_shift != 0) target = {target.x, target.y, wrap(target.z + z_shift)};
    const Coordinate source = source_for(target, arrival_tick, direction);
    runtime.register_channel(ChannelSpec{label, source, state, direction, semantic, true, false});
    track(receipts, label, runtime.experience(label, 0, load));
}

void schedule_c7_base(Runtime& runtime, std::vector<TrackedReceipt>& receipts,
                      bool teacher, bool through_query1,
                      std::uint16_t marker_load = MARKER_LOAD) {
    const auto g = geometry();
    schedule_carrier(runtime, receipts, "training.cue", g.junction, TRAIN_TICK,
                     CUE, 81001, BASE_CUE_LOAD);
    schedule_carrier(runtime, receipts, "training.teacher", teacher ? g.junction : Coordinate{g.junction.x, g.junction.y, wrap(g.junction.z + 4)},
                     TRAIN_TICK, TEACHER, 81002, BASE_TEACHER_LOAD);
    schedule_carrier(runtime, receipts, "bridge.supply", g.consequence, CONSEQUENCE_TICK,
                     PROGRAMMER, 81003, SUPPLY_LOAD);
    schedule_carrier(runtime, receipts, "bridge.marker", g.consequence, CONSEQUENCE_TICK,
                     MARKER_DIRECTION, 81004, marker_load);
    schedule_carrier(runtime, receipts, "lineage.redirect0", g.redirect, REDIRECT_TICK,
                     REDIRECT, 81005, 0);
    if (through_query1) {
        schedule_carrier(runtime, receipts, "query.q1", g.response1, QUERY_TICKS[0],
                         CUE, 81101, QUERY_LOADS[0]);
    }
}

Runtime empty_runtime(dee::v27::Backend backend) {
    Runtime runtime(N);
    runtime.set_execution_options({backend, backend == dee::v27::Backend::DenseSequential ? 1U : 4U});
    return runtime;
}

F1Result run_f1(const F1Spec& spec, dee::v27::Backend backend,
                std::vector<TraceRow>& trace, const fs::path& checkpoint_dir) {
    F1Result result;
    result.spec = spec;
    result.backend = backend_label(backend);
    auto runtime = empty_runtime(backend);
    const auto g = geometry();
    schedule_c7_base(runtime, result.receipts, spec.teacher, true);
    schedule_carrier(runtime, result.receipts, "revision.r1.onpath", g.revision1, REVISION_TICKS[0],
                     QUERY_REDIRECT, 81201, spec.revision1);
    schedule_carrier(runtime, result.receipts, "revision.r1.sham", g.revision1, REVISION_TICKS[0],
                     QUERY_REDIRECT, 81301, spec.sham1, 3);
    schedule_carrier(runtime, result.receipts, "query.q2", g.response2, QUERY_TICKS[1],
                     CUE, 81102, QUERY_LOADS[1]);
    schedule_carrier(runtime, result.receipts, "revision.r2.onpath", g.revision2, REVISION_TICKS[1],
                     QUERY_REDIRECT, 81202, spec.revision2);
    schedule_carrier(runtime, result.receipts, "revision.r2.sham", g.revision2, REVISION_TICKS[1],
                     QUERY_REDIRECT, 81302, spec.sham2, 3);
    schedule_carrier(runtime, result.receipts, "query.q3", g.response3, QUERY_TICKS[2],
                     CUE, 81103, QUERY_LOADS[2]);

    const std::set<std::uint64_t> key_ticks{5, 8, 12, 18, 34, 38, 46, 50, 58, 60};
    const std::map<std::string, Coordinate> sites{
        {"junction", g.junction}, {"consequence", g.consequence}, {"program", g.program},
        {"redirect", g.redirect}, {"response1", g.response1}, {"revision1", g.revision1},
        {"response2", g.response2}, {"revision2", g.revision2}, {"response3", g.response3}};
    while (runtime.current_tick() <= 60) {
        const auto tick = runtime.current_tick();
        if (key_ticks.contains(tick)) {
            for (const auto& [name, site] : sites) {
                const auto observation = runtime.observe(site);
                result.checkpoints[tick][name] = observation;
                trace.push_back({"F1", result.backend, spec.id, tick, name, observation, runtime.last_tick_info()});
            }
            if (spec.id == "REV_11_13" && backend == dee::v27::Backend::Lazy &&
                (tick == 38 || tick == 58)) {
                fs::create_directories(checkpoint_dir);
                runtime.save_snapshot((checkpoint_dir / ("F1_REV_11_13_t" + std::to_string(tick) + ".deetsnap")).string());
            }
        }
        if (tick == 60) break;
        const auto info = runtime.advance();
        result.fallback = result.fallback || info.fallback;
    }
    finalize_receipts(runtime, result.receipts);
    result.final_raw = runtime.raw_copy();
    result.final_clock = runtime.clock_copy();
    return result;
}

void install_environment_support(std::vector<std::uint64_t>& raw,
                                 std::vector<std::uint64_t>& clock,
                                 Coordinate environment, std::uint64_t phase) {
    clock[index(environment)] = phase;
    constexpr std::array<Coordinate, 6> offsets{{
        {1, -1, -1}, {1, -1, 0}, {1, -1, 1},
        {1, 0, -1}, {1, 0, 0}, {1, 0, 1}}};
    for (std::size_t i = 0; i < offsets.size(); ++i) {
        const Coordinate q = plus(environment, offsets[i]);
        raw[index(q)] = dee::v27::pack_record(9000U + static_cast<std::uint32_t>(i), 0, 0, 0, 0, 4);
    }
}

F2Result run_f2(const F2Spec& spec, dee::v27::Backend backend,
                std::vector<TraceRow>& trace, const fs::path& checkpoint_dir) {
    F2Result result;
    result.spec = spec;
    result.backend = backend_label(backend);
    const auto g = geometry();
    const Coordinate environment = g.revision1;
    const Coordinate demux = plus(environment, Coordinate{-1, -1, -1});
    const Coordinate query_sham = plus(demux, Coordinate{0, 4, 0});
    const Coordinate return_site = plus(demux, Coordinate{0, 0, 4});
    const Coordinate use1_site = plus(return_site, Coordinate{4, 0, 4});
    const Coordinate return_redirect = plus(use1_site, Coordinate{4, 4, 4});
    const Coordinate use2_site = plus(return_redirect, Coordinate{0, 4, 4});
    std::vector<std::uint64_t> raw(static_cast<std::size_t>(N) * N * N, 0);
    std::vector<std::uint64_t> clock(raw.size(), 0);
    install_environment_support(raw, clock, environment, spec.environment_clock_phase);
    auto runtime = Runtime::import_research_state(N, 0, std::move(raw), std::move(clock));
    runtime.set_execution_options({backend, backend == dee::v27::Backend::DenseSequential ? 1U : 4U});
    schedule_c7_base(runtime, result.receipts, spec.response, true, spec.marker_load);
    // Approach from +y.  The earlier -x approach crossed the declared
    // support voxel at environment+(1,0,0) and therefore never reached the
    // receptor.  This route is disjoint from all six support positions.
    schedule_carrier(runtime, result.receipts, "environment.bias", environment, REVISION_TICKS[0],
                     Direction{0, -1, 0}, 82001, spec.bias_load);
    if (spec.query_mode != QueryMode::Absent) {
        const Coordinate target = spec.query_mode == QueryMode::Intact ? demux : query_sham;
        // Arrive in the same transition in which DEMUX is post-applied.  The
        // intact environmental delta therefore updates this independent
        // carrier from 23 to 24 instead of merely occupying its destination.
        schedule_carrier(runtime, result.receipts, "environment.query", target, 39,
                         Direction{0, 0, 1}, 82002, 23);
    }
    schedule_carrier(runtime, result.receipts, "return.partner", return_site, 43,
                     Direction{1, 0, 0}, 82003, 31);
    schedule_carrier(runtime, result.receipts, "return.use1", use1_site, 47,
                     Direction{0, 1, 0}, 82004, 7);
    schedule_carrier(runtime, result.receipts, "return.redirect", return_redirect, 51,
                     Direction{-1, 0, 0}, 82005, 0);
    schedule_carrier(runtime, result.receipts, "return.use2", use2_site, 55,
                     Direction{1, 0, 0}, 82006, 5);

    const std::set<std::uint64_t> key_ticks{34, 37, 38, 39, 40, 41, 43, 47, 51, 55, 56};
    const std::map<std::string, Coordinate> sites{
        {"response1", g.response1}, {"environment", environment}, {"demux", demux},
        {"query_sham", query_sham}, {"return_site", return_site},
        {"use1_site", use1_site}, {"return_redirect", return_redirect},
        {"use2_site", use2_site},
        {"demux_xm", plus(demux, Coordinate{-1, 0, 0})},
        {"demux_xp", plus(demux, Coordinate{1, 0, 0})},
        {"demux_ym", plus(demux, Coordinate{0, -1, 0})},
        {"demux_yp", plus(demux, Coordinate{0, 1, 0})},
        {"demux_zm", plus(demux, Coordinate{0, 0, -1})},
        {"demux_zp", plus(demux, Coordinate{0, 0, 1})}};
    while (runtime.current_tick() <= 56) {
        const auto tick = runtime.current_tick();
        if (key_ticks.contains(tick)) {
            for (const auto& [name, site] : sites) {
                const auto observation = runtime.observe(site);
                result.checkpoints[tick][name] = observation;
                trace.push_back({"F2", result.backend, spec.id, tick, name, observation, runtime.last_tick_info()});
            }
            if (tick >= 38 && tick <= 41) {
                for (int dx = -3; dx <= 3; ++dx) for (int dy = -3; dy <= 3; ++dy) for (int dz = -3; dz <= 3; ++dz) {
                    const Coordinate q = plus(demux, Coordinate{dx, dy, dz});
                    const auto o = runtime.observe(q);
                    if (o.raw != 0) result.local_nonzero.emplace_back(tick, q, o);
                }
            }
            if (spec.id == "ENV_INTACT" && backend == dee::v27::Backend::Lazy &&
                (tick == 39 || tick == 55)) {
                fs::create_directories(checkpoint_dir);
                runtime.save_snapshot((checkpoint_dir / ("F2_ENV_INTACT_t" + std::to_string(tick) + ".deetsnap")).string());
            }
        }
        if (tick == 56) break;
        const auto info = runtime.advance();
        result.overflow_total += info.overflows;
        result.fallback = result.fallback || info.fallback;
    }
    finalize_receipts(runtime, result.receipts);
    result.final_raw = runtime.raw_copy();
    result.final_clock = runtime.clock_copy();
    return result;
}

std::size_t vector_diff(const std::vector<std::uint64_t>& a,
                        const std::vector<std::uint64_t>& b) {
    if (a.size() != b.size()) throw std::runtime_error("state size mismatch");
    std::size_t result = 0;
    for (std::size_t i = 0; i < a.size(); ++i) result += a[i] != b[i];
    return result;
}

bool all_applied_at_zero(const std::vector<TrackedReceipt>& receipts) {
    return std::all_of(receipts.begin(), receipts.end(), [](const auto& r) {
        return r.final.status == EventStatus::Applied && r.final.effective_tick == std::optional<std::uint64_t>{0};
    });
}

void write_trace_csv(const fs::path& path, const std::vector<TraceRow>& rows) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot write trace CSV");
    out << "family,backend,arm,tick,site,x,y,z,raw,clock,state,s_reg,dx,dy,dz,semantic,overflows,genesis,evaluated,fallback\n";
    for (const auto& row : rows) {
        const auto& o = row.observation;
        out << row.family << ',' << row.backend << ',' << row.arm << ',' << row.tick << ',' << row.site
            << ',' << o.coordinate.x << ',' << o.coordinate.y << ',' << o.coordinate.z
            << ',' << o.raw << ',' << o.clock << ',' << o.record.state << ',' << o.record.s_reg
            << ',' << static_cast<int>(o.record.dx) << ',' << static_cast<int>(o.record.dy)
            << ',' << static_cast<int>(o.record.dz) << ',' << static_cast<unsigned>(o.record.semantic)
            << ',' << row.info.overflows << ',' << row.info.genesis << ',' << row.info.evaluated
            << ',' << (row.info.fallback ? "true" : "false") << '\n';
    }
}

void write_local_csv(const fs::path& path, const std::vector<F2Result>& results) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot write local CSV");
    out << "backend,arm,tick,x,y,z,raw,clock,state,s_reg,dx,dy,dz,semantic\n";
    for (const auto& result : results) for (const auto& [tick, q, o] : result.local_nonzero) {
        out << result.backend << ',' << result.spec.id << ',' << tick << ',' << q.x << ',' << q.y << ',' << q.z
            << ',' << o.raw << ',' << o.clock << ',' << o.record.state << ',' << o.record.s_reg
            << ',' << static_cast<int>(o.record.dx) << ',' << static_cast<int>(o.record.dy)
            << ',' << static_cast<int>(o.record.dz) << ',' << static_cast<unsigned>(o.record.semantic) << '\n';
    }
}

const Observation& at(const F1Result& r, std::uint64_t tick, const std::string& site) {
    return r.checkpoints.at(tick).at(site);
}

const Observation& at(const F2Result& r, std::uint64_t tick, const std::string& site) {
    return r.checkpoints.at(tick).at(site);
}

bool write_results(const fs::path& path, const std::vector<F1Result>& f1,
                   const std::vector<F2Result>& f2, std::uint64_t elapsed_ms) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot write results JSON");
    out << "{\n  \"schema\": \"dee-thinking-final-laboratory-pilot-v1\",\n"
        << "  \"scope\": \"LABORATORY_ONLY_NOT_STABLE_CATALOG\",\n"
        << "  \"kernel\": \"DEE_v27_frozen\",\n"
        << "  \"elapsed_ms\": " << elapsed_ms << ",\n"
        << "  \"f1\": [\n";
    for (std::size_t i = 0; i < f1.size(); ++i) {
        const auto& r = f1[i];
        if (i) out << ",\n";
        out << "    {\"arm\":" << quote(r.spec.id) << ",\"backend\":" << quote(r.backend)
            << ",\"revision_loads\":[" << r.spec.revision1 << ',' << r.spec.revision2 << ']'
            << ",\"sham_loads\":[" << r.spec.sham1 << ',' << r.spec.sham2 << ']'
            << ",\"all_inputs_applied_at_t0\":" << (all_applied_at_zero(r.receipts) ? "true" : "false")
            << ",\"fallback\":" << (r.fallback ? "true" : "false")
            << ",\"responses\":[" << obs_json(at(r, 34, "response1")) << ','
            << obs_json(at(r, 46, "response2")) << ',' << obs_json(at(r, 58, "response3")) << ']'
            << ",\"revisions\":[" << obs_json(at(r, 38, "revision1")) << ','
            << obs_json(at(r, 50, "revision2")) << "]}";
    }
    out << "\n  ],\n  \"f2\": [\n";
    for (std::size_t i = 0; i < f2.size(); ++i) {
        const auto& r = f2[i];
        if (i) out << ",\n";
        out << "    {\"arm\":" << quote(r.spec.id) << ",\"backend\":" << quote(r.backend)
            << ",\"response_enabled\":" << (r.spec.response ? "true" : "false")
            << ",\"bias_load\":" << r.spec.bias_load
            << ",\"marker_load\":" << r.spec.marker_load
            << ",\"query_mode\":" << quote(r.spec.query_mode == QueryMode::Intact ? "intact" : (r.spec.query_mode == QueryMode::Absent ? "absent" : "sham"))
            << ",\"all_inputs_applied_at_t0\":" << (all_applied_at_zero(r.receipts) ? "true" : "false")
            << ",\"overflow_total\":" << r.overflow_total
            << ",\"fallback\":" << (r.fallback ? "true" : "false")
            << ",\"environment_t38\":" << obs_json(at(r, 38, "environment"))
            << ",\"environment_t39\":" << obs_json(at(r, 39, "environment"))
            << ",\"demux_t39\":" << obs_json(at(r, 39, "demux"))
            << ",\"demux_t40\":" << obs_json(at(r, 40, "demux"))
            << ",\"demux_t41\":" << obs_json(at(r, 41, "demux"))
            << ",\"return_t43\":" << obs_json(at(r, 43, "return_site"))
            << ",\"use1_t47\":" << obs_json(at(r, 47, "use1_site"))
            << ",\"redirect_t51\":" << obs_json(at(r, 51, "return_redirect"))
            << ",\"use2_t55\":" << obs_json(at(r, 55, "use2_site")) << '}';
    }
    out << "\n  ],\n  \"comparisons\": {\n";
    const auto find_f1 = [&](const std::string& id, const std::string& backend) -> const F1Result& {
        return *std::find_if(f1.begin(), f1.end(), [&](const auto& r) { return r.spec.id == id && r.backend == backend; });
    };
    const auto find_f2 = [&](const std::string& id, const std::string& backend) -> const F2Result& {
        return *std::find_if(f2.begin(), f2.end(), [&](const auto& r) { return r.spec.id == id && r.backend == backend; });
    };
    const auto& order_a = find_f1("REV_11_13", "lazy");
    const auto& order_b = find_f1("REV_13_11", "lazy");
    const auto& sham = find_f1("SHAM_11_13", "lazy");
    const auto& env = find_f2("ENV_INTACT", "lazy");
    const auto& env_cut = find_f2("ENV_RESPONSE_CUT", "lazy");
    const auto& env_no_query = find_f2("ENV_NO_QUERY", "lazy");
    const auto& env_sham = find_f2("ENV_QUERY_SHAM", "lazy");
    const auto& env_subthreshold = find_f2("ENV_SUBTHRESHOLD", "lazy");
    const auto& env_content19 = find_f2("ENV_CONTENT_19", "lazy");
    const bool f1_expected =
        at(order_a, 34, "response1").record.s_reg == 4149 &&
        at(order_a, 46, "response2").record.s_reg == 4165 &&
        at(order_a, 58, "response3").record.s_reg == 4181 &&
        at(order_b, 46, "response2").record.s_reg == 4167 &&
        at(order_b, 58, "response3").record.s_reg == 4181 &&
        at(sham, 34, "response1").record.s_reg == 4149 &&
        at(sham, 46, "response2").record.s_reg == 4154 &&
        at(sham, 58, "response3").record.s_reg == 4157;
    const auto f2_chain = [](const F2Result& r, std::array<std::uint16_t, 5> expected) {
        return at(r, 39, "demux").record.s_reg == expected[0] &&
               at(r, 43, "return_site").record.s_reg == expected[1] &&
               at(r, 47, "use1_site").record.s_reg == expected[2] &&
               at(r, 51, "return_redirect").record.s_reg == expected[3] &&
               at(r, 55, "use2_site").record.s_reg == expected[4];
    };
    const bool f2_expected =
        env.overflow_total == 1 && f2_chain(env, {24, 55, 62, 62, 67}) &&
        env_cut.overflow_total == 0 && f2_chain(env_cut, {23, 54, 61, 61, 66}) &&
        env_subthreshold.overflow_total == 0 && f2_chain(env_subthreshold, {23, 54, 61, 61, 66}) &&
        f2_chain(env_no_query, {0, 31, 7, 0, 5}) &&
        f2_chain(env_sham, {0, 31, 7, 0, 5}) &&
        env_content19.overflow_total == 1 && f2_chain(env_content19, {24, 55, 62, 62, 67});
    const bool admissions = std::all_of(f1.begin(), f1.end(), [](const auto& r) { return all_applied_at_zero(r.receipts); }) &&
                            std::all_of(f2.begin(), f2.end(), [](const auto& r) { return all_applied_at_zero(r.receipts); });
    const bool no_fallback = std::none_of(f1.begin(), f1.end(), [](const auto& r) { return r.fallback; }) &&
                             std::none_of(f2.begin(), f2.end(), [](const auto& r) { return r.fallback; });
    bool backend_exact = true;
    const auto compare_backend_f1 = [&](const std::string& id) {
        const auto& lazy = find_f1(id, "lazy");
        const auto found = std::find_if(f1.begin(), f1.end(), [&](const auto& r) {
            return r.spec.id == id && r.backend == "dense_parallel";
        });
        if (found == f1.end()) return true;
        return lazy.final_raw == found->final_raw && lazy.final_clock == found->final_clock;
    };
    const auto compare_backend_f2 = [&](const std::string& id) {
        const auto& lazy = find_f2(id, "lazy");
        const auto found = std::find_if(f2.begin(), f2.end(), [&](const auto& r) {
            return r.spec.id == id && r.backend == "dense_parallel";
        });
        if (found == f2.end()) return true;
        return lazy.final_raw == found->final_raw && lazy.final_clock == found->final_clock;
    };
    backend_exact = compare_backend_f1("REV_11_13") && compare_backend_f1("SHAM_11_13") &&
                    compare_backend_f2("ENV_INTACT") && compare_backend_f2("ENV_RESPONSE_CUT");
    const bool technical_ok = f1_expected && f2_expected && admissions && no_fallback && backend_exact;
    out << "    \"f1_order_intermediate_sreg\":[" << at(order_a, 46, "response2").record.s_reg << ','
        << at(order_b, 46, "response2").record.s_reg << "],\n"
        << "    \"f1_order_final_sreg\":[" << at(order_a, 58, "response3").record.s_reg << ','
        << at(order_b, 58, "response3").record.s_reg << "],\n"
        << "    \"f1_primary_vs_sham_final_raw_diff\":" << vector_diff(order_a.final_raw, sham.final_raw) << ",\n"
        << "    \"f2_intact_vs_response_cut_final_raw_diff\":" << vector_diff(env.final_raw, env_cut.final_raw) << ",\n"
        << "    \"f3_distinct_upstream_responses\":[" << at(env, 34, "response1").record.s_reg << ','
        << at(env_content19, 34, "response1").record.s_reg << "],\n"
        << "    \"f3_downstream_use2_outputs\":[" << at(env, 55, "use2_site").record.s_reg << ','
        << at(env_content19, 55, "use2_site").record.s_reg << "]\n"
        << "  },\n  \"technical_checks\": {\n"
        << "    \"f1_expected_relations\":" << (f1_expected ? "true" : "false") << ",\n"
        << "    \"f2_expected_mediation\":" << (f2_expected ? "true" : "false") << ",\n"
        << "    \"all_inputs_applied_at_t0\":" << (admissions ? "true" : "false") << ",\n"
        << "    \"no_backend_fallback\":" << (no_fallback ? "true" : "false") << ",\n"
        << "    \"selected_lazy_dense_raw_clock_exact\":" << (backend_exact ? "true" : "false") << ",\n"
        << "    \"technical_ok\":" << (technical_ok ? "true" : "false") << "\n"
        << "  }\n}\n";
    return technical_ok;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const auto started = std::chrono::steady_clock::now();
        const fs::path output = argc > 1 ? fs::path(argv[1]) : fs::path("results");
        const bool confirm_dense = !(argc > 2 && std::string(argv[2]) == "--lazy-only");
        fs::create_directories(output);
        fs::create_directories(output / "checkpoints");
        std::vector<TraceRow> trace;

        const std::vector<F1Spec> f1_specs{
            {"REV_11_13", 11, 13, 0, 0, true},
            {"REV_13_11", 13, 11, 0, 0, true},
            {"FIRST_ONLY_11", 11, 0, 0, 13, true},
            {"SECOND_ONLY_13", 0, 13, 11, 0, true},
            {"SHAM_11_13", 0, 0, 11, 13, true},
            {"NO_TRAINED_RELATION", 11, 13, 0, 0, false},
        };
        std::vector<F1Result> f1;
        for (const auto& spec : f1_specs) f1.push_back(run_f1(spec, dee::v27::Backend::Lazy, trace, output / "checkpoints"));
        if (confirm_dense) {
            for (const auto& id : {std::string("REV_11_13"), std::string("SHAM_11_13")}) {
                const auto spec = *std::find_if(f1_specs.begin(), f1_specs.end(), [&](const auto& s) { return s.id == id; });
                f1.push_back(run_f1(spec, dee::v27::Backend::DenseParallel, trace, output / "checkpoints"));
            }
        }

        const std::vector<F2Spec> f2_specs{
            {"ENV_INTACT", true, 15515, 17, QueryMode::Intact, 353},
            {"ENV_RESPONSE_CUT", false, 15515, 17, QueryMode::Intact, 353},
            {"ENV_NO_QUERY", true, 15515, 17, QueryMode::Absent, 353},
            {"ENV_QUERY_SHAM", true, 15515, 17, QueryMode::Sham, 353},
            {"ENV_SUBTHRESHOLD", true, 15514, 17, QueryMode::Intact, 353},
            {"ENV_CONTENT_19", true, 15515, 19, QueryMode::Intact, 353},
        };
        std::vector<F2Result> f2;
        for (const auto& spec : f2_specs) f2.push_back(run_f2(spec, dee::v27::Backend::Lazy, trace, output / "checkpoints"));
        if (confirm_dense) {
            for (const auto& id : {std::string("ENV_INTACT"), std::string("ENV_RESPONSE_CUT")}) {
                const auto spec = *std::find_if(f2_specs.begin(), f2_specs.end(), [&](const auto& s) { return s.id == id; });
                f2.push_back(run_f2(spec, dee::v27::Backend::DenseParallel, trace, output / "checkpoints"));
            }
        }

        const auto elapsed = static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - started).count());
        write_trace_csv(output / "telemetry.csv", trace);
        write_local_csv(output / "f2_local_nonzero.csv", f2);
        const bool technical_ok = write_results(output / "results.json", f1, f2, elapsed);
        std::cout << "completed_f1=" << f1.size() << " completed_f2=" << f2.size()
                  << " elapsed_ms=" << elapsed << " technical_ok=" << (technical_ok ? "true" : "false") << '\n';
        return technical_ok ? 0 : 2;
    } catch (const std::exception& e) {
        std::cerr << "final laboratory runner failed: " << e.what() << '\n';
        return 1;
    }
}
