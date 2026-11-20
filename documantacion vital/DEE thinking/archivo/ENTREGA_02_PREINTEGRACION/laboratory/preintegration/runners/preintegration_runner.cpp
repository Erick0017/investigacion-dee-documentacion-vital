#include "dee_thinking/composition.hpp"
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
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
using dee::thinking::ChannelSpec;
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
using dee::thinking::catalog::PortInputRequest;

namespace {

constexpr int kDimension = 34;
constexpr std::uint16_t kCueLoad = 5;
constexpr std::uint16_t kTeacherLoad = 7;
constexpr std::uint16_t kQueryLoad = 13;
constexpr std::array<std::uint64_t, 3> kQueryTicks{{6, 40, 74}};
constexpr std::array<std::uint64_t, 3> kResponseTicks{{11, 45, 79}};
constexpr std::uint64_t kInterventionTick = 27;
constexpr std::uint64_t kInterventionEncounterTick = 28;
constexpr std::uint64_t kSupportTick = 44;
constexpr std::uint64_t kFinalTick = 79;
constexpr Coordinate kQuerySource{15, 26, 14};
constexpr Coordinate kResponseSite{10, 26, 14};
constexpr Coordinate kCutSource{27, 9, 13};
constexpr Coordinate kCutEncounter{27, 9, 14};
constexpr Coordinate kShamSource{27, 10, 13};
constexpr Coordinate kShamEncounter{27, 10, 14};
constexpr Coordinate kSupportSource{10, 25, 14};

dee::v27::TickOptions g_options{dee::v27::Backend::Lazy, 4};

enum class Intervention { Intact, Cut, Sham };

struct TrackedReceipt {
    std::string label;
    EventReceipt initial;
    EventReceipt final;
};

struct Frame {
    std::uint64_t tick{};
    Observation response;
    Observation query_source;
    Observation cut_encounter;
    Observation sham_encounter;
    Observation support_source;
    WorldMetrics metrics;
    dee::v27::TickInfo tick_info;
};

struct Checkpoint {
    std::uint64_t tick{};
    Observation response;
    std::vector<std::uint64_t> raw;
    std::vector<std::uint64_t> clock;
};

struct ArmResult {
    std::string name;
    Intervention intervention{Intervention::Intact};
    std::vector<TrackedReceipt> receipts;
    std::vector<Frame> frames;
    std::vector<Checkpoint> checkpoints;
};

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

std::string intervention_name(Intervention value) {
    switch (value) {
        case Intervention::Intact: return "intact";
        case Intervention::Cut: return "cut";
        case Intervention::Sham: return "sham";
    }
    throw std::logic_error("unknown intervention");
}

std::string coordinate_json(Coordinate value) {
    return "[" + std::to_string(value.x) + "," + std::to_string(value.y) + "," +
           std::to_string(value.z) + "]";
}

std::string observation_json(const Observation& value) {
    std::ostringstream out;
    out << "{\"tick\":" << value.tick
        << ",\"coordinate\":" << coordinate_json(value.coordinate)
        << ",\"raw\":" << value.raw
        << ",\"clock\":" << value.clock
        << ",\"state\":" << value.record.state
        << ",\"s_reg\":" << value.record.s_reg
        << ",\"direction\":[" << static_cast<int>(value.record.dx) << ','
        << static_cast<int>(value.record.dy) << ','
        << static_cast<int>(value.record.dz) << ']'
        << ",\"semantic\":" << static_cast<unsigned>(value.record.semantic) << '}';
    return out.str();
}

std::string receipt_json(const EventReceipt& value) {
    std::ostringstream out;
    out << "{\"id\":" << value.id
        << ",\"kind\":" << quote(dee::thinking::to_string(value.kind))
        << ",\"status\":" << quote(dee::thinking::to_string(value.status))
        << ",\"requested_tick\":" << value.requested_tick
        << ",\"effective_tick\":";
    if (value.effective_tick) out << *value.effective_tick; else out << "null";
    out << ",\"channels\":[";
    for (std::size_t i = 0; i < value.channels.size(); ++i) {
        if (i != 0) out << ',';
        out << quote(value.channels[i]);
    }
    out << "],\"reason\":" << quote(value.reason) << '}';
    return out.str();
}

std::size_t vector_diff(const std::vector<std::uint64_t>& left,
                        const std::vector<std::uint64_t>& right) {
    if (left.size() != right.size()) throw std::runtime_error("incompatible state vectors");
    std::size_t result = 0;
    for (std::size_t i = 0; i < left.size(); ++i) result += left[i] != right[i];
    return result;
}

const Checkpoint& checkpoint_at(const ArmResult& arm, std::uint64_t tick) {
    const auto found = std::find_if(arm.checkpoints.begin(), arm.checkpoints.end(),
        [tick](const Checkpoint& value) { return value.tick == tick; });
    if (found == arm.checkpoints.end()) throw std::runtime_error("missing checkpoint");
    return *found;
}

bool is_response_tick(std::uint64_t tick) {
    return std::find(kResponseTicks.begin(), kResponseTicks.end(), tick) != kResponseTicks.end();
}

void track(ArmResult& arm, std::string label, EventReceipt receipt) {
    arm.receipts.push_back({std::move(label), receipt, receipt});
}

ComposedWorld make_world() {
    OrganizationCatalog catalog;
    CompositionPlanner planner(kDimension);
    planner.add(catalog.instantiate(
        {"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    planner.add(catalog.instantiate(
        {"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    planner.connect({{"learner", "learned_relation"}, {"reader", "relation_input"},
                     "preintegration repeated physical use"});
    auto world = planner.build();
    world.runtime().set_execution_options(g_options);
    if (world.landmarks().at("reader.response") != kResponseSite) {
        throw std::runtime_error("catalog geometry no longer matches frozen laboratory coordinates");
    }
    return world;
}

ArmResult run_arm(std::string name, Intervention intervention) {
    ArmResult result;
    result.name = std::move(name);
    result.intervention = intervention;
    auto world = make_world();
    auto& runtime = world.runtime();

    track(result, "training_pair", world.experience_batch(
        {{"learner", "cue", kCueLoad}, {"learner", "teacher", kTeacherLoad}}, 0));

    const Coordinate intervention_source =
        intervention == Intervention::Sham ? kShamSource : kCutSource;
    runtime.register_channel(ChannelSpec{
        "preintegration.intervention", intervention_source, 1, {0, 0, 1}, 1, true, false});
    runtime.register_channel(ChannelSpec{
        "preintegration.phase_support", kSupportSource, 1, {0, 1, 0}, 1, true, false});

    const std::string query_channel = world.qualified_channel("reader", "query");
    for (std::size_t i = 0; i < kQueryTicks.size(); ++i) {
        track(result, "reader_query_" + std::to_string(i + 1),
              runtime.probe(query_channel, kQueryTicks[i], kQueryLoad));
    }
    if (intervention != Intervention::Intact) {
        track(result, "matched_intervention",
              runtime.experience("preintegration.intervention", kInterventionTick, 0));
    }
    track(result, "common_phase_support",
          runtime.experience("preintegration.phase_support", kSupportTick, 0));

    while (runtime.current_tick() <= kFinalTick) {
        Frame frame;
        frame.tick = runtime.current_tick();
        frame.response = runtime.observe(kResponseSite);
        frame.query_source = runtime.observe(kQuerySource);
        frame.cut_encounter = runtime.observe(kCutEncounter);
        frame.sham_encounter = runtime.observe(kShamEncounter);
        frame.support_source = runtime.observe(kSupportSource);
        frame.metrics = runtime.metrics();
        frame.tick_info = runtime.last_tick_info();
        result.frames.push_back(frame);
        if (is_response_tick(frame.tick) || frame.tick == kInterventionEncounterTick) {
            result.checkpoints.push_back(
                {frame.tick, frame.response, runtime.raw_copy(), runtime.clock_copy()});
        }
        if (runtime.current_tick() == kFinalTick) break;
        runtime.advance(1);
    }

    for (auto& receipt : result.receipts) {
        const auto final = runtime.receipt(receipt.initial.id);
        if (!final) throw std::runtime_error("lost runtime receipt");
        receipt.final = *final;
    }
    return result;
}

bool receipt_applied_at_request(const TrackedReceipt& value) {
    return value.final.status == EventStatus::Applied && value.final.effective_tick &&
           *value.final.effective_tick == value.final.requested_tick;
}

const TrackedReceipt& labeled_receipt(const ArmResult& arm, const std::string& label) {
    const auto found = std::find_if(arm.receipts.begin(), arm.receipts.end(),
        [&](const TrackedReceipt& value) { return value.label == label; });
    if (found == arm.receipts.end()) throw std::runtime_error("missing receipt label: " + label);
    return *found;
}

bool query_admission_comparable(const std::vector<ArmResult>& arms) {
    for (std::size_t i = 0; i < kQueryTicks.size(); ++i) {
        const std::string label = "reader_query_" + std::to_string(i + 1);
        for (const auto& arm : arms) {
            const auto& receipt = labeled_receipt(arm, label);
            if (!receipt_applied_at_request(receipt) || receipt.final.requested_tick != kQueryTicks[i]) {
                return false;
            }
        }
    }
    return true;
}

bool common_admission_comparable(const std::vector<ArmResult>& arms) {
    for (const auto& arm : arms) {
        if (!receipt_applied_at_request(labeled_receipt(arm, "training_pair")) ||
            !receipt_applied_at_request(labeled_receipt(arm, "common_phase_support"))) {
            return false;
        }
    }
    return true;
}

bool intact_sham_readout_equal(const std::vector<ArmResult>& arms) {
    const auto& intact = arms.at(0);
    const auto& sham = arms.at(2);
    return std::all_of(kResponseTicks.begin(), kResponseTicks.end(), [&](std::uint64_t tick) {
        const auto& left = checkpoint_at(intact, tick).response;
        const auto& right = checkpoint_at(sham, tick).response;
        return left.raw == right.raw && left.clock == right.clock;
    });
}

bool cut_diverges_after_intervention(const std::vector<ArmResult>& arms) {
    const auto& intact = arms.at(0);
    const auto& cut = arms.at(1);
    return std::all_of(kResponseTicks.begin() + 1, kResponseTicks.end(), [&](std::uint64_t tick) {
        return checkpoint_at(intact, tick).response.raw != checkpoint_at(cut, tick).response.raw;
    });
}

bool expected_functional_sequences(const std::vector<ArmResult>& arms) {
    constexpr std::array<std::uint16_t, 3> intact_expected{{25, 38, 51}};
    constexpr std::array<std::uint16_t, 3> cut_expected{{25, 13, 13}};
    for (std::size_t i = 0; i < kResponseTicks.size(); ++i) {
        if (checkpoint_at(arms.at(0), kResponseTicks[i]).response.record.s_reg != intact_expected[i] ||
            checkpoint_at(arms.at(2), kResponseTicks[i]).response.record.s_reg != intact_expected[i] ||
            checkpoint_at(arms.at(1), kResponseTicks[i]).response.record.s_reg != cut_expected[i]) {
            return false;
        }
    }
    return true;
}

bool no_backend_fallback(const std::vector<ArmResult>& arms) {
    for (const auto& arm : arms) {
        for (const auto& frame : arm.frames) {
            if (frame.tick != 0 && frame.tick_info.fallback) return false;
        }
    }
    return true;
}

void write_csv(const fs::path& path, const std::vector<ArmResult>& arms,
               const std::string& backend_name) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot create telemetry CSV");
    out << "backend,arm,intervention,tick,site,x,y,z,state,s_reg,dx,dy,dz,semantic,raw,clock,raw_support,occupied,evaluated,used_backend,used_threads,fallback\n";
    for (const auto& arm : arms) {
        for (const auto& frame : arm.frames) {
            const auto emit = [&](const char* site, const Observation& observation) {
                out << backend_name << ',' << arm.name << ',' << intervention_name(arm.intervention)
                    << ',' << frame.tick << ',' << site
                    << ',' << observation.coordinate.x << ',' << observation.coordinate.y
                    << ',' << observation.coordinate.z << ',' << observation.record.state
                    << ',' << observation.record.s_reg << ',' << static_cast<int>(observation.record.dx)
                    << ',' << static_cast<int>(observation.record.dy)
                    << ',' << static_cast<int>(observation.record.dz)
                    << ',' << static_cast<unsigned>(observation.record.semantic)
                    << ',' << observation.raw << ',' << observation.clock
                    << ',' << frame.metrics.raw_support << ',' << frame.metrics.occupied
                    << ',' << frame.tick_info.evaluated
                    << ',' << dee::v27::backend_name(frame.tick_info.used_backend)
                    << ',' << frame.tick_info.used_threads
                    << ',' << (frame.tick_info.fallback ? "true" : "false") << '\n';
            };
            emit("response", frame.response);
            emit("query_source", frame.query_source);
            emit("cut_encounter", frame.cut_encounter);
            emit("sham_encounter", frame.sham_encounter);
            emit("support_source", frame.support_source);
        }
    }
}

bool write_results(const fs::path& path, const std::vector<ArmResult>& arms,
                   const std::string& backend_name, std::uint64_t elapsed_ms) {
    const bool query_admission = query_admission_comparable(arms);
    const bool common_admission = common_admission_comparable(arms);
    const bool sham_valid = intact_sham_readout_equal(arms);
    const bool cut_effect = cut_diverges_after_intervention(arms);
    const bool sequence_match = expected_functional_sequences(arms);
    const bool backend_clean = no_backend_fallback(arms);
    const bool supported = query_admission && common_admission && sham_valid && cut_effect &&
                           sequence_match && backend_clean;

    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot create results JSON");
    out << "{\n"
        << "  \"schema\": \"dee-thinking-preintegration-laboratory-v1\",\n"
        << "  \"scope\": \"LABORATORY_ONLY_DO_NOT_EXPORT_TO_STABLE_CATALOG\",\n"
        << "  \"backend\": " << quote(backend_name) << ",\n"
        << "  \"elapsed_ms\": " << elapsed_ms << ",\n"
        << "  \"candidate\": \"relation_learning.c6h01.v1 + relation_query.c6h01.v1\",\n"
        << "  \"question\": \"Can one reader accept three comparable experiences and can the products observed at t11 and t45 participate in later physical uses without reset?\",\n"
        << "  \"design\": {\n"
        << "    \"dimension\": " << kDimension << ",\n"
        << "    \"same_runtime_without_reset\": true,\n"
        << "    \"same_reader_channel\": \"reader.query\",\n"
        << "    \"query_ticks\": [6,40,74],\n"
        << "    \"response_ticks\": [11,45,79],\n"
        << "    \"query_load\": " << kQueryLoad << ",\n"
        << "    \"cut_and_sham_submission_tick\": " << kInterventionTick << ",\n"
        << "    \"cut_encounter_tick\": " << kInterventionEncounterTick << ",\n"
        << "    \"common_zero_load_phase_support_tick\": " << kSupportTick << ",\n"
        << "    \"catalog_extension_claimed\": false,\n"
        << "    \"fanout_used\": false\n"
        << "  },\n"
        << "  \"criteria\": {\n"
        << "    \"all_query_admissions_comparable_and_applied\": " << (query_admission ? "true" : "false") << ",\n"
        << "    \"training_and_common_support_admissions_comparable_and_applied\": " << (common_admission ? "true" : "false") << ",\n"
        << "    \"intact_equals_sham_at_all_response_ticks\": " << (sham_valid ? "true" : "false") << ",\n"
        << "    \"cut_diverges_at_all_post_cut_response_ticks\": " << (cut_effect ? "true" : "false") << ",\n"
        << "    \"predicted_finite_load_sequences_match\": " << (sequence_match ? "true" : "false") << ",\n"
        << "    \"backend_used_without_fallback\": " << (backend_clean ? "true" : "false") << ",\n"
        << "    \"preintegration_candidate_supported\": " << (supported ? "true" : "false") << "\n"
        << "  },\n"
        << "  \"interpretation_guard\": \"s_reg accumulation and toroidal return are measured physical operations; neither is renamed as learning\",\n"
        << "  \"arms\": [\n";

    const auto& intact = arms.at(0);
    const auto& sham = arms.at(2);
    for (std::size_t i = 0; i < arms.size(); ++i) {
        const auto& arm = arms[i];
        out << "    {\n"
            << "      \"name\": " << quote(arm.name) << ",\n"
            << "      \"intervention\": " << quote(intervention_name(arm.intervention)) << ",\n"
            << "      \"receipts\": [\n";
        for (std::size_t j = 0; j < arm.receipts.size(); ++j) {
            const auto& receipt = arm.receipts[j];
            out << "        {\"label\":" << quote(receipt.label)
                << ",\"initial\":" << receipt_json(receipt.initial)
                << ",\"final\":" << receipt_json(receipt.final) << '}';
            if (j + 1 != arm.receipts.size()) out << ',';
            out << '\n';
        }
        out << "      ],\n"
            << "      \"response_checkpoints\": [\n";
        for (std::size_t j = 0; j < kResponseTicks.size(); ++j) {
            const auto tick = kResponseTicks[j];
            const auto& checkpoint = checkpoint_at(arm, tick);
            const auto& intact_checkpoint = checkpoint_at(intact, tick);
            const auto& sham_checkpoint = checkpoint_at(sham, tick);
            out << "        {\"tick\":" << tick
                << ",\"response\":" << observation_json(checkpoint.response)
                << ",\"raw_diff_from_intact\":" << vector_diff(checkpoint.raw, intact_checkpoint.raw)
                << ",\"clock_diff_from_intact\":" << vector_diff(checkpoint.clock, intact_checkpoint.clock)
                << ",\"raw_diff_from_sham\":" << vector_diff(checkpoint.raw, sham_checkpoint.raw)
                << ",\"clock_diff_from_sham\":" << vector_diff(checkpoint.clock, sham_checkpoint.clock)
                << '}';
            if (j + 1 != kResponseTicks.size()) out << ',';
            out << '\n';
        }
        out << "      ]\n    }";
        if (i + 1 != arms.size()) out << ',';
        out << '\n';
    }
    out << "  ]\n}\n";
    return supported;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const fs::path output = argc > 1 ? fs::path(argv[1]) : fs::path("results_lazy");
        std::string backend_name = "lazy-4";
        if (argc > 2) {
            const std::string requested = argv[2];
            if (requested == "dense-1") {
                g_options = {dee::v27::Backend::DenseSequential, 1};
                backend_name = requested;
            } else if (requested != "lazy-4") {
                throw std::invalid_argument("backend must be lazy-4 or dense-1");
            }
        }
        fs::create_directories(output);
        const auto started = std::chrono::steady_clock::now();

        std::vector<ArmResult> arms;
        arms.push_back(run_arm("INTACT", Intervention::Intact));
        arms.push_back(run_arm("CUT_RETURN", Intervention::Cut));
        arms.push_back(run_arm("SHAM_PARALLEL", Intervention::Sham));

        const auto elapsed_ms = static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - started).count());
        write_csv(output / "telemetry.csv", arms, backend_name);
        const bool supported = write_results(output / "results.json", arms, backend_name, elapsed_ms);

        std::cout << "backend=" << backend_name << " arms=" << arms.size()
                  << " final_tick=" << kFinalTick << " elapsed_ms=" << elapsed_ms << '\n';
        return supported ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "preintegration laboratory failed: " << error.what() << '\n';
        return 1;
    }
}
