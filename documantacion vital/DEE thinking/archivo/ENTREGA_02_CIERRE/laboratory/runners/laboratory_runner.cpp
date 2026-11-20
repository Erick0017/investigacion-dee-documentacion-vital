#include "dee_thinking/composition.hpp"
#include "dee_thinking/kernel_v27.hpp"
#include "dee_thinking/organization_catalog.hpp"
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
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::EventReceipt;
using dee::thinking::EventStatus;
using dee::thinking::Observation;
using dee::thinking::Runtime;
using dee::thinking::WorldMetrics;
using dee::thinking::catalog::ComposedWorld;
using dee::thinking::catalog::CompositionPlanner;
using dee::thinking::catalog::OrganizationCatalog;

namespace {

constexpr int kNativeN = 17;
constexpr std::uint16_t kSupply = 20;
constexpr std::uint16_t kMarker = 17;
constexpr std::uint16_t kUpdatedLoad = kSupply + kMarker;
constexpr Coordinate kUpdate{4, 4, 4};
constexpr Coordinate kJunction{6, 6, 4};
dee::v27::TickOptions g_execution_options{dee::v27::Backend::Lazy, 4};

struct NativeCase {
    std::string name;
    bool cancel_y{};
    bool add_z{};
    Direction expected_direction{};
    Coordinate expected_endpoint{};
    std::vector<Observation> update_trace;
    std::vector<Observation> junction_trace;
    std::vector<std::array<Observation, 4>> endpoint_trace;
    std::vector<WorldMetrics> metrics;
    std::vector<dee::v27::TickInfo> tick_info;
    bool update_match{};
    bool junction_match{};
    bool endpoint_match{};
    std::size_t occupied_endpoints{};
};

struct CoupledFrame {
    std::uint64_t tick{};
    Observation response;
    WorldMetrics metrics;
    dee::v27::TickInfo tick_info;
    std::vector<std::uint64_t> raw;
    std::vector<std::uint64_t> clock;
    std::size_t raw_diff_from_absent{};
    std::size_t clock_diff_from_absent{};
};

struct CoupledCase {
    std::string name;
    bool trained{};
    bool submit_second{};
    std::uint16_t second_load{};
    Observation first_response;
    EventReceipt first_query;
    EventReceipt second_query;
    std::vector<CoupledFrame> frames;
};

std::size_t index(Coordinate c, int n) {
    return dee::v27::linear_index(c.x, c.y, c.z, n);
}

void place(std::vector<std::uint64_t>& raw, int n, Coordinate c,
           std::uint16_t s_reg, Direction direction, std::uint8_t semantic = 1) {
    raw.at(index(c, n)) = dee::v27::pack_record(
        1, s_reg, direction.dx, direction.dy, direction.dz, semantic);
}

bool same_record(const Observation& observation, std::uint16_t s_reg, Direction direction) {
    const auto& r = observation.record;
    return r.state == 1 && r.s_reg == s_reg && r.dx == direction.dx &&
           r.dy == direction.dy && r.dz == direction.dz && r.semantic == 1;
}

std::string json_escape(const std::string& value) {
    std::ostringstream out;
    for (const unsigned char c : value) {
        switch (c) {
            case '\\': out << "\\\\"; break;
            case '"': out << "\\\""; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (c < 0x20) {
                    out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                        << static_cast<int>(c) << std::dec;
                } else {
                    out << c;
                }
        }
    }
    return out.str();
}

std::string quote(const std::string& value) {
    return "\"" + json_escape(value) + "\"";
}

std::string coordinate_json(Coordinate c) {
    return "[" + std::to_string(c.x) + "," + std::to_string(c.y) + "," +
           std::to_string(c.z) + "]";
}

std::string direction_json(Direction d) {
    return "[" + std::to_string(d.dx) + "," + std::to_string(d.dy) + "," +
           std::to_string(d.dz) + "]";
}

std::string observation_json(const Observation& o) {
    std::ostringstream out;
    out << "{\"tick\":" << o.tick
        << ",\"coordinate\":" << coordinate_json(o.coordinate)
        << ",\"raw\":" << o.raw
        << ",\"clock\":" << o.clock
        << ",\"state\":" << o.record.state
        << ",\"s_reg\":" << o.record.s_reg
        << ",\"direction\":[" << static_cast<int>(o.record.dx) << ','
        << static_cast<int>(o.record.dy) << ',' << static_cast<int>(o.record.dz) << ']'
        << ",\"semantic\":" << static_cast<unsigned>(o.record.semantic) << '}';
    return out.str();
}

std::string receipt_json(const EventReceipt& receipt) {
    std::ostringstream out;
    out << "{\"id\":" << receipt.id
        << ",\"status\":" << quote(dee::thinking::to_string(receipt.status))
        << ",\"requested_tick\":" << receipt.requested_tick
        << ",\"effective_tick\":";
    if (receipt.effective_tick) out << *receipt.effective_tick; else out << "null";
    out << ",\"reason\":" << quote(receipt.reason) << '}';
    return out.str();
}

std::size_t vector_diff(const std::vector<std::uint64_t>& a,
                        const std::vector<std::uint64_t>& b) {
    if (a.size() != b.size()) throw std::runtime_error("incompatible vectors");
    std::size_t result = 0;
    for (std::size_t i = 0; i < a.size(); ++i) result += (a[i] != b[i]);
    return result;
}

NativeCase run_native_case(std::string name, bool cancel_y, bool add_z) {
    NativeCase result;
    result.name = std::move(name);
    result.cancel_y = cancel_y;
    result.add_z = add_z;
    result.expected_direction = {1, cancel_y ? 0 : 1, add_z ? 1 : 0};
    result.expected_endpoint = {
        kJunction.x + 3 * result.expected_direction.dx,
        kJunction.y + 3 * result.expected_direction.dy,
        kJunction.z + 3 * result.expected_direction.dz,
    };

    const std::size_t volume = static_cast<std::size_t>(kNativeN) * kNativeN * kNativeN;
    std::vector<std::uint64_t> raw(volume, 0);
    std::vector<std::uint64_t> clock(volume, 0);
    place(raw, kNativeN, {3, 4, 4}, kSupply, {1, 0, 0});
    place(raw, kNativeN, {4, 3, 4}, kMarker, {0, 1, 0});
    if (cancel_y) place(raw, kNativeN, {6, 9, 4}, 0, {0, -1, 0});
    if (add_z) place(raw, kNativeN, {6, 6, 1}, 0, {0, 0, 1});

    Runtime runtime = Runtime::import_research_state(kNativeN, 0, std::move(raw), std::move(clock));
    runtime.set_execution_options(g_execution_options);

    const std::array<Coordinate, 4> endpoints{{
        {9, 9, 4}, {9, 6, 4}, {9, 9, 7}, {9, 6, 7},
    }};
    for (std::uint64_t tick = 0; tick <= 6; ++tick) {
        result.update_trace.push_back(runtime.observe(kUpdate));
        result.junction_trace.push_back(runtime.observe(kJunction));
        std::array<Observation, 4> endpoint_observations{};
        for (std::size_t i = 0; i < endpoints.size(); ++i) {
            endpoint_observations[i] = runtime.observe(endpoints[i]);
        }
        result.endpoint_trace.push_back(std::move(endpoint_observations));
        result.metrics.push_back(runtime.metrics());
        result.tick_info.push_back(runtime.last_tick_info());
        if (tick < 6) runtime.advance(1);
    }

    result.update_match = same_record(result.update_trace.at(1), kUpdatedLoad, {1, 1, 0});
    result.junction_match = same_record(result.junction_trace.at(3), kUpdatedLoad,
                                        result.expected_direction);
    const auto& final_endpoints = result.endpoint_trace.at(6);
    result.occupied_endpoints = static_cast<std::size_t>(std::count_if(
        final_endpoints.begin(), final_endpoints.end(),
        [](const Observation& o) { return o.record.occupied(); }));
    result.endpoint_match = false;
    for (const auto& o : final_endpoints) {
        if (o.coordinate == result.expected_endpoint) {
            result.endpoint_match = same_record(o, kUpdatedLoad, result.expected_direction);
        }
    }
    return result;
}

ComposedWorld make_c6_world(bool trained) {
    OrganizationCatalog catalog;
    CompositionPlanner planner(34);
    planner.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    planner.add(catalog.instantiate({"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    planner.connect({{"learner", "learned_relation"}, {"reader", "relation_input"},
                     "laboratory later-query reuse"});
    auto world = planner.build();
    world.runtime().set_execution_options(g_execution_options);
    if (trained) {
        const auto receipt = world.experience_batch(
            {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0);
        if (receipt.status != EventStatus::Scheduled) {
            throw std::runtime_error("training batch rejected: " + receipt.reason);
        }
    } else {
        const auto receipt = world.experience("learner", "cue", 0, 5);
        if (receipt.status != EventStatus::Scheduled) {
            throw std::runtime_error("cue-only control rejected: " + receipt.reason);
        }
    }
    return world;
}

CoupledCase run_coupled_case(std::string name, bool trained,
                             bool submit_second, std::uint16_t second_load) {
    CoupledCase result;
    result.name = std::move(name);
    result.trained = trained;
    result.submit_second = submit_second;
    result.second_load = second_load;
    auto world = make_c6_world(trained);
    world.runtime().run_until(6);
    result.first_query = world.probe("reader", "query", 6, 13);
    if (result.first_query.status != EventStatus::Scheduled) {
        throw std::runtime_error("first query rejected: " + result.first_query.reason);
    }
    world.runtime().run_until(11);
    const Coordinate response_site = world.landmarks().at("reader.response");
    result.first_response = world.runtime().observe(response_site);

    // No reset or reconstruction: continue the exact same world.  Tick 40 is
    // one N=34 transport period after the first query boundary (t=6).  This
    // exploratory arm deliberately uses Runtime's public channel contract,
    // because the catalog port contract only claims the originally validated
    // t=6 window.  It is therefore ACOPLADA and not a catalog extension.
    world.runtime().run_until(40);
    if (submit_second) {
        result.second_query = world.runtime().probe(
            world.qualified_channel("reader", "query"), 40, second_load);
    } else {
        result.second_query.status = EventStatus::RejectedInvalid;
        result.second_query.requested_tick = 40;
        result.second_query.reason = "control: no second input submitted";
    }

    for (std::uint64_t tick = 40; tick <= 46; ++tick) {
        CoupledFrame frame;
        frame.tick = tick;
        frame.response = world.runtime().observe(response_site);
        frame.metrics = world.runtime().metrics();
        frame.tick_info = world.runtime().last_tick_info();
        frame.raw = world.runtime().raw_copy();
        frame.clock = world.runtime().clock_copy();
        result.frames.push_back(std::move(frame));
        if (tick < 46) world.runtime().advance(1);
    }
    if (submit_second) {
        result.second_query = world.runtime().receipt(result.second_query.id).value();
    }
    return result;
}

void compare_coupled(std::vector<CoupledCase>& cases) {
    const auto absent = std::find_if(cases.begin(), cases.end(),
        [](const CoupledCase& c) { return c.name == "TRAINED_ABSENT_SECOND"; });
    if (absent == cases.end()) throw std::runtime_error("absent control missing");
    for (auto& c : cases) {
        for (std::size_t i = 0; i < c.frames.size(); ++i) {
            c.frames[i].raw_diff_from_absent = vector_diff(c.frames[i].raw, absent->frames[i].raw);
            c.frames[i].clock_diff_from_absent = vector_diff(c.frames[i].clock, absent->frames[i].clock);
        }
    }
}

void write_csv(const fs::path& path, const std::vector<NativeCase>& native,
               const std::vector<CoupledCase>& coupled) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot create telemetry CSV");
    out << "family,modality,case,tick,site,x,y,z,state,s_reg,dx,dy,dz,semantic,raw_support,occupied,evaluated,raw_diff_vs_absent,clock_diff_vs_absent\n";
    for (const auto& c : native) {
        for (std::size_t i = 0; i < c.update_trace.size(); ++i) {
            const auto emit = [&](const char* site, const Observation& o) {
                out << "native_update_route,NATIVA," << c.name << ',' << o.tick << ',' << site << ','
                    << o.coordinate.x << ',' << o.coordinate.y << ',' << o.coordinate.z << ','
                    << o.record.state << ',' << o.record.s_reg << ',' << static_cast<int>(o.record.dx) << ','
                    << static_cast<int>(o.record.dy) << ',' << static_cast<int>(o.record.dz) << ','
                    << static_cast<unsigned>(o.record.semantic) << ',' << c.metrics[i].raw_support << ','
                    << c.metrics[i].occupied << ',' << c.tick_info[i].evaluated << ",0,0\n";
            };
            emit("update", c.update_trace[i]);
            emit("junction", c.junction_trace[i]);
            for (std::size_t j = 0; j < 4; ++j) {
                const std::string label = "endpoint_" + std::to_string(j);
                emit(label.c_str(), c.endpoint_trace[i][j]);
            }
        }
    }
    for (const auto& c : coupled) {
        for (const auto& frame : c.frames) {
            const auto& o = frame.response;
            out << "c6_later_query_reuse,ACOPLADA," << c.name << ',' << o.tick << ",reader_response,"
                << o.coordinate.x << ',' << o.coordinate.y << ',' << o.coordinate.z << ','
                << o.record.state << ',' << o.record.s_reg << ',' << static_cast<int>(o.record.dx) << ','
                << static_cast<int>(o.record.dy) << ',' << static_cast<int>(o.record.dz) << ','
                << static_cast<unsigned>(o.record.semantic) << ',' << frame.metrics.raw_support << ','
                << frame.metrics.occupied << ',' << frame.tick_info.evaluated << ','
                << frame.raw_diff_from_absent << ',' << frame.clock_diff_from_absent << '\n';
        }
    }
}

void write_results(const fs::path& path, const std::vector<NativeCase>& native,
                   const std::vector<CoupledCase>& coupled,
                   std::uint64_t elapsed_ms, const std::string& backend_name) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot create results JSON");
    out << "{\n  \"schema\": \"dee-thinking-e2-laboratory-v1\",\n"
        << "  \"kernel\": \"DEE Universe v27 frozen via dee_thinking public API\",\n"
        << "  \"elapsed_ms\": " << elapsed_ms << ",\n"
        << "  \"backend\": " << quote(backend_name) << ",\n"
        << "  \"families\": [\n    {\n"
        << "      \"id\": \"native_update_route\",\n"
        << "      \"modality\": \"NATIVA\",\n"
        << "      \"host_writes_after_t0\": false,\n"
        << "      \"question\": \"Can a native two-carrier update be routed by pre-existing context without copying its carrier?\",\n"
        << "      \"cases\": [\n";
    for (std::size_t i = 0; i < native.size(); ++i) {
        const auto& c = native[i];
        out << "        {\"name\":" << quote(c.name)
            << ",\"selectors\":{\"cancel_y\":" << (c.cancel_y ? "true" : "false")
            << ",\"add_z\":" << (c.add_z ? "true" : "false") << "}"
            << ",\"expected_direction\":" << direction_json(c.expected_direction)
            << ",\"expected_endpoint\":" << coordinate_json(c.expected_endpoint)
            << ",\"update_at_t1\":" << observation_json(c.update_trace.at(1))
            << ",\"junction_at_t3\":" << observation_json(c.junction_trace.at(3))
            << ",\"endpoint_at_t6\":";
        for (const auto& o : c.endpoint_trace.at(6)) {
            if (o.coordinate == c.expected_endpoint) out << observation_json(o);
        }
        out << ",\"update_prediction_matched\":" << (c.update_match ? "true" : "false")
            << ",\"junction_prediction_matched\":" << (c.junction_match ? "true" : "false")
            << ",\"endpoint_prediction_matched\":" << (c.endpoint_match ? "true" : "false")
            << ",\"occupied_declared_endpoints_at_t6\":" << c.occupied_endpoints << '}';
        if (i + 1 != native.size()) out << ',';
        out << '\n';
    }
    out << "      ]\n    },\n    {\n"
        << "      \"id\": \"c6_later_query_reuse\",\n"
        << "      \"modality\": \"ACOPLADA\",\n"
        << "      \"host_writes_after_advance\": true,\n"
        << "      \"catalog_export\": false,\n"
        << "      \"question\": \"Does a later external query admitted on the same physical C6 world produce a distinguishable later response without reset?\",\n"
        << "      \"cases\": [\n";
    for (std::size_t i = 0; i < coupled.size(); ++i) {
        const auto& c = coupled[i];
        out << "        {\"name\":" << quote(c.name)
            << ",\"trained\":" << (c.trained ? "true" : "false")
            << ",\"second_input_submitted\":" << (c.submit_second ? "true" : "false")
            << ",\"second_load\":" << c.second_load
            << ",\"first_query\":" << receipt_json(c.first_query)
            << ",\"first_response\":" << observation_json(c.first_response)
            << ",\"second_query\":" << receipt_json(c.second_query)
            << ",\"frames\":[";
        for (std::size_t j = 0; j < c.frames.size(); ++j) {
            const auto& f = c.frames[j];
            out << "{\"tick\":" << f.tick
                << ",\"response\":" << observation_json(f.response)
                << ",\"raw_diff_from_absent\":" << f.raw_diff_from_absent
                << ",\"clock_diff_from_absent\":" << f.clock_diff_from_absent << '}';
            if (j + 1 != c.frames.size()) out << ',';
        }
        out << "]}";
        if (i + 1 != coupled.size()) out << ',';
        out << '\n';
    }
    out << "      ]\n    }\n  ]\n}\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const fs::path output = argc > 1 ? fs::path(argv[1]) : fs::path("results");
        std::string backend_name = "lazy-4";
        if (argc > 2) {
            const std::string requested = argv[2];
            if (requested == "dense-1") {
                g_execution_options = {dee::v27::Backend::DenseSequential, 1};
                backend_name = requested;
            } else if (requested != "lazy-4") {
                throw std::invalid_argument("backend must be lazy-4 or dense-1");
            }
        }
        fs::create_directories(output);
        const auto started = std::chrono::steady_clock::now();

        std::vector<NativeCase> native;
        native.push_back(run_native_case("NO_SELECTOR", false, false));
        native.push_back(run_native_case("CANCEL_Y", true, false));
        native.push_back(run_native_case("ADD_Z", false, true));
        native.push_back(run_native_case("BOTH_SELECTORS", true, true));

        std::vector<CoupledCase> coupled;
        coupled.push_back(run_coupled_case("TRAINED_ABSENT_SECOND", true, false, 0));
        coupled.push_back(run_coupled_case("TRAINED_LOAD13", true, true, 13));
        coupled.push_back(run_coupled_case("TRAINED_ZERO_LOAD", true, true, 0));
        coupled.push_back(run_coupled_case("CUE_ONLY_LOAD13", false, true, 13));
        compare_coupled(coupled);

        const auto elapsed_ms = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - started).count());
        write_csv(output / "telemetry.csv", native, coupled);
        write_results(output / "results.json", native, coupled, elapsed_ms, backend_name);

        std::cout << "backend=" << backend_name << " native_cases=" << native.size()
                  << " coupled_cases=" << coupled.size()
                  << " elapsed_ms=" << elapsed_ms << '\n';
        for (const auto& c : native) {
            std::cout << c.name << " update=" << c.update_match
                      << " junction=" << c.junction_match
                      << " endpoint=" << c.endpoint_match
                      << " occupied_endpoints=" << c.occupied_endpoints << '\n';
        }
        for (const auto& c : coupled) {
            const auto& last = c.frames.back();
            std::cout << c.name << " first_s=" << c.first_response.record.s_reg
                      << " second_status=" << dee::thinking::to_string(c.second_query.status)
                      << " t46_s=" << last.response.record.s_reg
                      << " raw_diff=" << last.raw_diff_from_absent << '\n';
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "laboratory error: " << error.what() << '\n';
        return 1;
    }
}
