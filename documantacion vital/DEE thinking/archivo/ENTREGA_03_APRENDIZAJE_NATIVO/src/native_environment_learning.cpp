#include "dee_thinking/integrated_protocols.hpp"
#include "dee_thinking/kernel_v27.hpp"
#include "dee_thinking/runtime.hpp"
#include "dee_thinking/version.hpp"

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
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
using dee::thinking::ChannelSpec;
using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::EventReceipt;
using dee::thinking::EventStatus;
using dee::thinking::Runtime;

namespace {

constexpr int kN = 127;
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
// Matches the proven F2 upstream response direction; the paired proposal is
// the environmental bias.  Their native merge is the cap-reaching context.
constexpr Direction kEnvironmentA{1, 1, 0};
constexpr Direction kEnvironmentB{0, -1, 0};
constexpr Direction kUpdateDirection{0, 0, 1};
constexpr Direction kUpdateRedirect{-1, 0, -1};

constexpr std::uint64_t kTrainTick = 5;
constexpr std::uint64_t kConsequenceTick = 8;
constexpr std::uint64_t kProgramTick = 12;
constexpr std::uint64_t kRedirectTick = 18;
constexpr std::uint64_t kQuery1Tick = 34;
constexpr std::uint64_t kRevision1Tick = 38;
constexpr std::uint64_t kQuery2Tick = 46;
constexpr std::uint64_t kRevision2Tick = 50;
constexpr std::uint64_t kQuery3Tick = 58;
constexpr std::uint64_t kFinalTick = 60;
constexpr std::array<std::uint64_t, 4> kUpdateTicks{14, 18, 22, 26};

constexpr std::uint16_t kBaseCueLoad = 4083;
constexpr std::uint16_t kBaseTeacherLoad = 19;
constexpr std::uint16_t kSupplyLoad = 23;
constexpr std::uint16_t kMarkerLoad = 17;
constexpr std::uint16_t kEnvironmentLoadA = 4149;
constexpr std::uint16_t kEnvironmentLoadB = 15515;
constexpr std::uint16_t kUpdateCarrierLoad = 23;

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
    Coordinate update_redirect{};
    std::array<Coordinate, 4> demux{};
    std::array<Coordinate, 4> environment{};
};

struct CaseSpec {
    std::string id;
    std::uint8_t regular_mask{};
    bool phase_cut{};
    bool unpaired_control{};
    std::uint16_t query2_load{5};
    std::uint16_t query3_load{3};
    bool schedule_evaluation_at_t0{true};
};

struct TraceRow {
    std::uint64_t tick{};
    std::string label;
    Coordinate site{};
    std::uint64_t raw{};
    std::uint64_t clock{};
    dee::v27::Record record{};
    std::uint64_t overflows_so_far{};
};

struct CaseResult {
    CaseSpec spec;
    std::string backend;
    std::size_t requested_inputs{};
    std::size_t admitted_inputs{};
    std::size_t rejected_inputs{};
    std::uint64_t overflows{};
    std::array<std::uint16_t, 4> carrier_after_episode{};
    std::array<std::uint16_t, 4> environment_at_merge{};
    std::uint16_t carrier_after_redirect{};
    std::uint16_t response_before_learning{};
    std::uint16_t response_after_learning{};
    std::uint16_t response_second_use{};
    std::uint16_t revision_site_load{};
    bool backend_fallback{};
    std::size_t final_raw_support{};
    std::size_t final_occupied{};
    std::uint64_t final_s_reg_sum{};
    std::vector<TraceRow> trace;
    std::vector<EventReceipt> receipts;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

struct PreparedWorld {
    Runtime runtime;
    Geometry geometry;
    std::vector<std::uint64_t> receipt_ids;
};

int wrap(int value) {
    const int remainder = value % kN;
    return remainder < 0 ? remainder + kN : remainder;
}

Coordinate plus(Coordinate q, Direction direction, int scale = 1) {
    return {wrap(q.x + direction.dx * scale),
            wrap(q.y + direction.dy * scale),
            wrap(q.z + direction.dz * scale)};
}

Coordinate plus(Coordinate a, Coordinate b) {
    return {wrap(a.x + b.x), wrap(a.y + b.y), wrap(a.z + b.z)};
}

Coordinate source_for(Coordinate target, std::uint64_t travel,
                      Direction direction) {
    return plus(target, direction, -static_cast<int>(travel % kN));
}

std::size_t index(Coordinate q) {
    return dee::v27::linear_index(q.x, q.y, q.z, kN);
}

Geometry geometry() {
    Geometry g;
    g.junction = kJunction;
    g.program = plus(kJunction, kMemory,
                     static_cast<int>(kProgramTick - kTrainTick));
    g.consequence = plus(g.program, kProgrammer,
                         -static_cast<int>(kProgramTick - kConsequenceTick));
    g.redirect = plus(g.program, kProgrammed,
                      static_cast<int>(kRedirectTick - kProgramTick));
    g.response1 = plus(g.redirect, kMemory,
                       static_cast<int>(kQuery1Tick - kRedirectTick));
    g.revision1 = plus(g.response1, kResponse,
                       static_cast<int>(kRevision1Tick - kQuery1Tick));
    g.response2 = plus(g.revision1, kMemory,
                       static_cast<int>(kQuery2Tick - kRevision1Tick));
    g.revision2 = plus(g.response2, kResponse,
                       static_cast<int>(kRevision2Tick - kQuery2Tick));
    g.response3 = plus(g.revision2, kMemory,
                       static_cast<int>(kQuery3Tick - kRevision2Tick));
    g.update_redirect = plus(g.revision1, Direction{1, 0, 0}, 8);
    for (std::size_t i = 0; i < g.demux.size(); ++i) {
        const auto remaining = static_cast<int>(30 - kUpdateTicks[i]);
        g.demux[i] = plus(g.update_redirect, kUpdateDirection, -remaining);
        g.environment[i] = plus(g.demux[i], Coordinate{1, 1, 1});
    }
    return g;
}

std::string backend_label(dee::v27::Backend backend) {
    return dee::v27::backend_name(backend);
}

std::string csv_escape(std::string_view value) {
    if (value.find_first_of(",\"\n\r") == std::string_view::npos) {
        return std::string(value);
    }
    std::string output{"\""};
    for (const char ch : value) {
        if (ch == '"') output += '"';
        output += ch;
    }
    output += '"';
    return output;
}

void ensure_parent(const fs::path& path) {
    if (!path.parent_path().empty()) fs::create_directories(path.parent_path());
}

void install_support(std::vector<std::uint64_t>& raw,
                     std::vector<std::uint64_t>& clock,
                     Coordinate environment, std::uint64_t phase) {
    clock[index(environment)] = phase;
    constexpr std::array<Coordinate, 6> offsets{{
        {1, -1, -1}, {1, -1, 0}, {1, -1, 1},
        {1, 0, -1},  {1, 0, 0},  {1, 0, 1},
    }};
    for (std::size_t i = 0; i < offsets.size(); ++i) {
        const auto site = plus(environment, offsets[i]);
        raw[index(site)] = dee::v27::pack_record(
            9300U + static_cast<std::uint32_t>(i), 0, 0, 0, 0,
            static_cast<std::uint8_t>(dee::v27::Semantic::Observer));
    }
}

void schedule_carrier(Runtime& runtime, std::vector<std::uint64_t>& ids,
                      const std::string& label, Coordinate target,
                      std::uint64_t arrival_tick, Direction direction,
                      std::uint32_t state, std::uint16_t load,
                      std::uint64_t injection_tick = 0) {
    if (arrival_tick < injection_tick) {
        throw std::invalid_argument("arrival precedes injection");
    }
    const auto source = source_for(target, arrival_tick - injection_tick,
                                   direction);
    runtime.register_channel(
        ChannelSpec{label, source, state, direction, 1, true, false});
    const auto receipt = runtime.experience(label, injection_tick, load);
    ids.push_back(receipt.id);
}

void schedule_base(Runtime& runtime, const Geometry& g,
                   std::vector<std::uint64_t>& ids) {
    schedule_carrier(runtime, ids, "base.training.cue", g.junction,
                     kTrainTick, kCue, 91001, kBaseCueLoad);
    schedule_carrier(runtime, ids, "base.training.teacher", g.junction,
                     kTrainTick, kTeacher, 91002, kBaseTeacherLoad);
    schedule_carrier(runtime, ids, "base.bridge.supply", g.consequence,
                     kConsequenceTick, kProgrammer, 91003, kSupplyLoad);
    schedule_carrier(runtime, ids, "base.bridge.marker", g.consequence,
                     kConsequenceTick, kMarkerDirection, 91004, kMarkerLoad);
    schedule_carrier(runtime, ids, "base.lineage.redirect0", g.redirect,
                     kRedirectTick, kRedirect, 91005, 0);
    schedule_carrier(runtime, ids, "evaluation.query1", g.response1,
                     kQuery1Tick, kCue, 91101, 7);
}

void schedule_evaluation(Runtime& runtime, const Geometry& g,
                         std::vector<std::uint64_t>& ids,
                         std::uint16_t query2_load,
                         std::uint16_t query3_load,
                         std::uint64_t injection_tick) {
    schedule_carrier(runtime, ids, "evaluation.query2", g.response2,
                     kQuery2Tick, kCue, 91102, query2_load, injection_tick);
    schedule_carrier(runtime, ids, "evaluation.redirect2", g.revision2,
                     kRevision2Tick, kQueryRedirect, 91202, 0,
                     injection_tick);
    schedule_carrier(runtime, ids, "evaluation.query3", g.response3,
                     kQuery3Tick, kCue, 91103, query3_load, injection_tick);
}

PreparedWorld prepare(const CaseSpec& spec, dee::v27::TickOptions options) {
    const auto g = geometry();
    const auto total = static_cast<std::size_t>(kN) * kN * kN;
    std::vector<std::uint64_t> raw(total, 0);
    std::vector<std::uint64_t> clock(total, 0);

    for (std::size_t i = 0; i < kUpdateTicks.size(); ++i) {
        const auto merge_tick = kUpdateTicks[i] - 1;
        auto phase = 391U - static_cast<unsigned>(merge_tick);
        const bool receptive =
            !spec.phase_cut && (spec.regular_mask & (1U << i)) != 0;
        if (!receptive) --phase;
        install_support(raw, clock, g.environment[i], phase);
    }

    auto runtime = Runtime::import_research_state(kN, 0, std::move(raw),
                                                  std::move(clock));
    runtime.set_execution_options(options);
    runtime.set_protocol_phase("ENTREGA03_ENVIRONMENTAL_EXPOSURE");
    runtime.set_snapshot_metadata("campaign.id", "entrega03.native_learning.v1");
    runtime.set_snapshot_metadata("case.id", spec.id);
    runtime.set_snapshot_metadata("case.regular_mask",
                                  std::to_string(spec.regular_mask));
    runtime.set_snapshot_metadata("case.phase_cut", spec.phase_cut ? "1" : "0");
    runtime.set_snapshot_metadata("case.query2_load",
                                  std::to_string(spec.query2_load));
    runtime.set_snapshot_metadata("case.query3_load",
                                  std::to_string(spec.query3_load));

    std::vector<std::uint64_t> ids;
    schedule_base(runtime, g, ids);

    for (std::size_t i = 0; i < kUpdateTicks.size(); ++i) {
        const auto merge_tick = kUpdateTicks[i] - 1;
        const auto arrival_a =
            spec.unpaired_control ? merge_tick - 1 : merge_tick;
        schedule_carrier(runtime, ids,
                         "environment.e" + std::to_string(i + 1) + ".a",
                         g.environment[i], arrival_a, kEnvironmentA,
                         92000U + static_cast<std::uint32_t>(i * 2),
                         kEnvironmentLoadA);
        schedule_carrier(runtime, ids,
                         "environment.e" + std::to_string(i + 1) + ".b",
                         g.environment[i], merge_tick, kEnvironmentB,
                         92001U + static_cast<std::uint32_t>(i * 2),
                         kEnvironmentLoadB);
    }

    schedule_carrier(runtime, ids, "learning.update_carrier", g.demux[0],
                     kUpdateTicks[0], kUpdateDirection, 92501,
                     kUpdateCarrierLoad);
    schedule_carrier(runtime, ids, "learning.update_redirect",
                     g.update_redirect, 30, kUpdateRedirect, 92502, 0);

    if (spec.schedule_evaluation_at_t0) {
        schedule_evaluation(runtime, g, ids, spec.query2_load,
                            spec.query3_load, 0);
    }
    return PreparedWorld{std::move(runtime), g, std::move(ids)};
}

void record(std::vector<TraceRow>& rows, const Runtime& runtime,
            std::uint64_t tick, std::string label, Coordinate site,
            std::uint64_t overflows) {
    const auto observation = runtime.observe(site);
    rows.push_back({tick, std::move(label), site, observation.raw,
                    observation.clock, observation.record, overflows});
}

void finalize_receipts(CaseResult& result, const Runtime& runtime,
                       const std::vector<std::uint64_t>& ids) {
    result.requested_inputs = ids.size();
    for (const auto id : ids) {
        const auto receipt = runtime.receipt(id);
        if (!receipt) throw std::runtime_error("missing event receipt");
        result.receipts.push_back(*receipt);
        if (receipt->status == EventStatus::Applied) {
            ++result.admitted_inputs;
        } else {
            ++result.rejected_inputs;
        }
    }
}

CaseResult evolve(PreparedWorld world, const CaseSpec& spec,
                  std::uint64_t target_tick = kFinalTick) {
    CaseResult result;
    result.spec = spec;
    result.backend = backend_label(world.runtime.execution_options().backend);
    const std::set<std::uint64_t> checkpoints{
        13, 14, 17, 18, 21, 22, 25, 26, 30, 34, 38, 40, 46, 50, 58, 60};

    while (world.runtime.current_tick() <= target_tick) {
        const auto tick = world.runtime.current_tick();
        if (checkpoints.contains(tick)) {
            for (std::size_t i = 0; i < kUpdateTicks.size(); ++i) {
                if (tick == kUpdateTicks[i] - 1) {
                    result.environment_at_merge[i] =
                        world.runtime.observe(world.geometry.environment[i])
                            .record.s_reg;
                    record(result.trace, world.runtime, tick,
                           "environment." + std::to_string(i + 1),
                           world.geometry.environment[i], result.overflows);
                }
                if (tick == kUpdateTicks[i]) {
                    result.carrier_after_episode[i] =
                        world.runtime.observe(world.geometry.demux[i])
                            .record.s_reg;
                    record(result.trace, world.runtime, tick,
                           "carrier.after." + std::to_string(i + 1),
                           world.geometry.demux[i], result.overflows);
                }
            }
            if (tick == 30) {
                result.carrier_after_redirect =
                    world.runtime.observe(world.geometry.update_redirect)
                        .record.s_reg;
                record(result.trace, world.runtime, tick,
                       "carrier.redirected", world.geometry.update_redirect,
                       result.overflows);
            } else if (tick == 34) {
                result.response_before_learning =
                    world.runtime.observe(world.geometry.response1).record.s_reg;
                record(result.trace, world.runtime, tick,
                       "response.before_learning", world.geometry.response1,
                       result.overflows);
            } else if (tick == 38) {
                result.revision_site_load =
                    world.runtime.observe(world.geometry.revision1).record.s_reg;
                record(result.trace, world.runtime, tick,
                       "learned_revision", world.geometry.revision1,
                       result.overflows);
            } else if (tick == 46) {
                result.response_after_learning =
                    world.runtime.observe(world.geometry.response2).record.s_reg;
                record(result.trace, world.runtime, tick,
                       "response.use1", world.geometry.response2,
                       result.overflows);
            } else if (tick == 50) {
                record(result.trace, world.runtime, tick,
                       "neutral_redirect", world.geometry.revision2,
                       result.overflows);
            } else if (tick == 58) {
                result.response_second_use =
                    world.runtime.observe(world.geometry.response3).record.s_reg;
                record(result.trace, world.runtime, tick,
                       "response.use2", world.geometry.response3,
                       result.overflows);
            }
        }
        if (tick == target_tick) break;
        const auto info = world.runtime.advance();
        result.overflows += info.overflows;
        result.backend_fallback = result.backend_fallback || info.fallback;
    }
    finalize_receipts(result, world.runtime, world.receipt_ids);
    const auto metrics = world.runtime.metrics();
    result.final_raw_support = metrics.raw_support;
    result.final_occupied = metrics.occupied;
    result.final_s_reg_sum = metrics.s_reg_sum;
    result.final_raw = world.runtime.raw_copy();
    result.final_clock = world.runtime.clock_copy();
    return result;
}

CaseResult run_case(const CaseSpec& spec, dee::v27::TickOptions options) {
    return evolve(prepare(spec, options), spec);
}

void write_trace(const fs::path& path, const CaseResult& result) {
    ensure_parent(path);
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write trace: " + path.string());
    out << "case_id,backend,tick,label,x,y,z,raw,clock,state,s_reg,dx,dy,dz,semantic,overflows_so_far\n";
    for (const auto& row : result.trace) {
        out << csv_escape(result.spec.id) << ',' << result.backend << ','
            << row.tick << ',' << csv_escape(row.label) << ',' << row.site.x
            << ',' << row.site.y << ',' << row.site.z << ',' << row.raw << ','
            << row.clock << ',' << row.record.state << ',' << row.record.s_reg
            << ',' << static_cast<int>(row.record.dx) << ','
            << static_cast<int>(row.record.dy) << ','
            << static_cast<int>(row.record.dz) << ','
            << static_cast<int>(row.record.semantic) << ','
            << row.overflows_so_far << '\n';
    }
}

void write_receipts(const fs::path& path, const CaseResult& result) {
    ensure_parent(path);
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write receipts: " + path.string());
    out << "case_id,event_id,status,requested_tick,effective_tick,channels,reason\n";
    for (const auto& receipt : result.receipts) {
        std::ostringstream channels;
        for (std::size_t i = 0; i < receipt.channels.size(); ++i) {
            if (i != 0) channels << ';';
            channels << receipt.channels[i];
        }
        out << csv_escape(result.spec.id) << ',' << receipt.id << ','
            << dee::thinking::to_string(receipt.status) << ','
            << receipt.requested_tick << ',';
        if (receipt.effective_tick) out << *receipt.effective_tick;
        out << ',' << csv_escape(channels.str()) << ','
            << csv_escape(receipt.reason) << '\n';
    }
}

std::size_t popcount4(std::uint8_t value) {
    std::size_t count = 0;
    for (int bit = 0; bit < 4; ++bit) count += (value >> bit) & 1U;
    return count;
}

void append_summary(std::ofstream& out, const CaseResult& r) {
    out << csv_escape(r.spec.id) << ',' << r.backend << ','
        << static_cast<unsigned>(r.spec.regular_mask) << ','
        << popcount4(r.spec.regular_mask) << ',' << (r.spec.phase_cut ? 1 : 0)
        << ',' << (r.spec.unpaired_control ? 1 : 0)
        << ',' << r.spec.query2_load << ',' << r.spec.query3_load << ','
        << r.requested_inputs << ',' << r.admitted_inputs << ','
        << r.rejected_inputs << ',' << r.overflows;
    for (const auto value : r.environment_at_merge) out << ',' << value;
    for (const auto value : r.carrier_after_episode) out << ',' << value;
    out << ',' << r.carrier_after_redirect << ','
        << r.response_before_learning << ',' << r.revision_site_load << ','
        << r.response_after_learning << ',' << r.response_second_use << ','
        << (r.backend_fallback ? 1 : 0) << ',' << r.final_raw_support << ','
        << r.final_occupied << ',' << r.final_s_reg_sum << '\n';
}

void write_summary_header(std::ofstream& out) {
    out << "case_id,backend,receptive_mask,effective_experiences,phase_cut,unpaired_control,q2_load,q3_load,"
           "requested_inputs,admitted_inputs,rejected_inputs,overflows,"
           "env1,env2,env3,env4,carrier1,carrier2,carrier3,carrier4,"
           "carrier_redirect,q1_before,revision1,q2_use1,q3_use2,backend_fallback,"
           "final_raw_support,final_occupied,final_s_reg_sum\n";
}

void write_backend_comparison(const fs::path& path, const CaseResult& lazy,
                              const CaseResult& dense,
                              const CaseResult& parallel) {
    ensure_parent(path);
    std::ofstream out(path);
    if (!out) throw std::runtime_error("cannot write backend comparison");
    const bool dense_raw = lazy.final_raw == dense.final_raw;
    const bool dense_clock = lazy.final_clock == dense.final_clock;
    const bool parallel_raw = lazy.final_raw == parallel.final_raw;
    const bool parallel_clock = lazy.final_clock == parallel.final_clock;
    out << "case_id,lazy_vs_dense_raw,lazy_vs_dense_clock,lazy_vs_parallel_raw,"
           "lazy_vs_parallel_clock,lazy_q3,dense_q3,parallel_q3\n";
    out << lazy.spec.id << ',' << dense_raw << ',' << dense_clock << ','
        << parallel_raw << ',' << parallel_clock << ','
        << lazy.response_second_use << ',' << dense.response_second_use << ','
        << parallel.response_second_use << '\n';
    if (!(dense_raw && dense_clock && parallel_raw && parallel_clock)) {
        throw std::runtime_error("backend RAW/clock divergence");
    }
}

void validate_case(const CaseResult& r) {
    if (r.rejected_inputs != 0 || r.backend_fallback) {
        throw std::runtime_error(r.spec.id + ": admission or backend failure");
    }
    if (r.response_before_learning != 4149) {
        throw std::runtime_error(r.spec.id + ": unexpected pre-learning response");
    }
    if (r.spec.unpaired_control) return;
    const auto dose = r.spec.phase_cut ? 0U : popcount4(r.spec.regular_mask);
    const auto expected_carrier = static_cast<std::uint16_t>(23U + dose);
    const auto expected_revision = static_cast<std::uint16_t>(4149U + expected_carrier);
    const auto expected_use1 = static_cast<std::uint16_t>(expected_revision + r.spec.query2_load);
    const auto expected_use2 = static_cast<std::uint16_t>(expected_use1 + r.spec.query3_load);
    if (r.carrier_after_redirect != expected_carrier ||
        r.revision_site_load != expected_revision ||
        r.response_after_learning != expected_use1 ||
        r.response_second_use != expected_use2) {
        std::ostringstream message;
        message << r.spec.id << ": frozen prediction mismatch carrier="
                << r.carrier_after_redirect << '/' << expected_carrier
                << " revision=" << r.revision_site_load << '/'
                << expected_revision << " use1=" << r.response_after_learning
                << '/' << expected_use1 << " use2=" << r.response_second_use
                << '/' << expected_use2;
        throw std::runtime_error(message.str());
    }
}

void run_baseline(const fs::path& output) {
    ensure_parent(output);
    const auto descriptors =
        dee::thinking::protocols::integrated_protocol_descriptors();
    dee::thinking::protocols::EnvironmentalReturnConfig config;
    const dee::v27::TickOptions lazy{dee::v27::Backend::Lazy, 4};
    const auto result =
        dee::thinking::protocols::run_environmental_return(config, lazy);
    const auto checkpoint = output.parent_path() / "baseline_f2_t40.deetsnap";
    dee::thinking::protocols::save_environmental_return_checkpoint(
        config, 40, checkpoint.string(), lazy);
    const auto resumed =
        dee::thinking::protocols::resume_environmental_return_checkpoint(
            checkpoint.string(), lazy);
    std::ofstream out(output);
    if (!out) throw std::runtime_error("cannot write baseline result");
    out << "product=" << dee::thinking::kProductName << '\n';
    out << "version=" << dee::thinking::kProductVersion << '\n';
    out << "kernel=" << dee::thinking::kKernelVersion << '\n';
    out << "integrated_protocols=" << descriptors.size() << '\n';
    out << "f2_downstream=";
    for (std::size_t i = 0; i < result.downstream_loads.size(); ++i) {
        if (i != 0) out << ',';
        out << result.downstream_loads[i];
    }
    out << '\n';
    out << "f2_resume_raw_exact=" << (resumed.final_raw == result.final_raw) << '\n';
    out << "f2_resume_clock_exact=" << (resumed.final_clock == result.final_clock) << '\n';
    if (descriptors.size() != 6 || result.downstream_loads !=
            std::array<std::uint16_t, 5>{24, 55, 62, 62, 67} ||
        resumed.final_raw != result.final_raw ||
        resumed.final_clock != result.final_clock) {
        throw std::runtime_error("DEE thinking 2.2.0 baseline check failed");
    }
}

void run_panel(const fs::path& output_root, bool confirm_backends) {
    fs::create_directories(output_root / "traces");
    fs::create_directories(output_root / "receipts");
    const dee::v27::TickOptions lazy{dee::v27::Backend::Lazy, 4};
    const std::vector<CaseSpec> specs{
        {"DOSE_0", 0b0000, false, false, 5, 3, true},
        {"DOSE_1", 0b0001, false, false, 5, 3, true},
        {"DOSE_2_EARLY", 0b0011, false, false, 5, 3, true},
        {"DOSE_2_LATE", 0b1100, false, false, 5, 3, true},
        {"DOSE_4", 0b1111, false, false, 5, 3, true},
        {"PHASE_CUT", 0b1111, true, false, 5, 3, true},
        {"UNPAIRED_SAME_INVENTORY", 0b1111, false, true, 5, 3, true},
        {"HOLDOUT_DOSE_0", 0b0000, false, false, 9, 4, true},
        {"HOLDOUT_DOSE_4", 0b1111, false, false, 9, 4, true},
    };

    std::ofstream summary(output_root / "case_summary.csv");
    if (!summary) throw std::runtime_error("cannot write panel summary");
    write_summary_header(summary);
    std::ofstream mismatches(output_root / "prediction_mismatches.txt");
    if (!mismatches) throw std::runtime_error("cannot write mismatch log");
    std::map<std::string, CaseResult> cases;
    for (const auto& spec : specs) {
        auto result = run_case(spec, lazy);
        write_trace(output_root / "traces" / (spec.id + ".csv"), result);
        write_receipts(output_root / "receipts" / (spec.id + ".csv"), result);
        append_summary(summary, result);
        try {
            validate_case(result);
        } catch (const std::exception& error) {
            mismatches << error.what() << '\n';
        }
        std::cout << "case=" << spec.id
                  << " dose=" << popcount4(spec.regular_mask)
                  << " overflows=" << result.overflows
                  << " carrier=" << result.carrier_after_redirect
                  << " q1=" << result.response_before_learning
                  << " q2=" << result.response_after_learning
                  << " q3=" << result.response_second_use << '\n';
        cases.emplace(spec.id, std::move(result));
    }
    summary.close();

    if (!confirm_backends) return;
    const CaseSpec confirm{"DOSE_4", 0b1111, false, false, 5, 3, true};
    const auto dense = run_case(
        confirm, {dee::v27::Backend::DenseSequential, 1});
    const auto parallel = run_case(
        confirm, {dee::v27::Backend::DenseParallel, 4});
    try {
        validate_case(dense);
        validate_case(parallel);
    } catch (const std::exception& error) {
        mismatches << "backend confirmation: " << error.what() << '\n';
    }
    write_backend_comparison(output_root / "backend_equivalence.csv",
                             cases.at("DOSE_4"), dense, parallel);
}

void inject_holdout(Runtime& runtime, const Geometry& g,
                    std::vector<std::uint64_t>& ids) {
    if (runtime.current_tick() != 40) {
        throw std::invalid_argument("holdout injection requires tick 40");
    }
    schedule_evaluation(runtime, g, ids, 9, 4, 40);
}

std::tuple<std::uint16_t, std::uint16_t> continue_holdout(
    Runtime& runtime, const Geometry& g, std::uint64_t& overflows) {
    std::uint16_t use1 = 0;
    std::uint16_t use2 = 0;
    while (runtime.current_tick() <= kFinalTick) {
        const auto tick = runtime.current_tick();
        if (tick == kQuery2Tick) use1 = runtime.observe(g.response2).record.s_reg;
        if (tick == kQuery3Tick) use2 = runtime.observe(g.response3).record.s_reg;
        if (tick == kFinalTick) break;
        const auto info = runtime.advance();
        overflows += info.overflows;
    }
    return {use1, use2};
}

void make_checkpoint(const fs::path& checkpoint,
                     const fs::path& final_reference,
                     const fs::path& result_csv) {
    CaseSpec spec{"CHECKPOINT_DOSE_4", 0b1111, false, false, 9, 4, false};
    const dee::v27::TickOptions lazy{dee::v27::Backend::Lazy, 4};
    auto world = prepare(spec, lazy);
    std::uint64_t overflows = 0;
    while (world.runtime.current_tick() < 40) {
        const auto info = world.runtime.advance();
        overflows += info.overflows;
    }
    world.runtime.set_protocol_phase("LEARNED_STATE_BEFORE_HOLDOUT");
    world.runtime.set_snapshot_metadata("evaluation.pending", "0");
    world.runtime.save_snapshot(checkpoint.string());

    std::vector<std::uint64_t> holdout_ids;
    inject_holdout(world.runtime, world.geometry, holdout_ids);
    const auto [use1, use2] = continue_holdout(world.runtime, world.geometry,
                                               overflows);
    world.runtime.set_protocol_phase("HOLDOUT_COMPLETED");
    world.runtime.save_snapshot(final_reference.string());

    ensure_parent(result_csv);
    std::ofstream out(result_csv);
    if (!out) throw std::runtime_error("cannot write checkpoint result");
    out << "mode,tick,holdout_use1,holdout_use2,overflows,events_scheduled\n";
    out << "same_process_reference," << world.runtime.current_tick() << ','
        << use1 << ',' << use2 << ',' << overflows << ','
        << holdout_ids.size() << '\n';
    if (use1 != 4185 || use2 != 4189) {
        throw std::runtime_error("checkpoint holdout prediction mismatch");
    }
}

void resume_checkpoint(const fs::path& checkpoint,
                       const fs::path& final_reference,
                       const fs::path& result_csv,
                       const fs::path& resumed_snapshot) {
    auto runtime = Runtime::load_snapshot(checkpoint.string());
    if (runtime.snapshot_metadata("campaign.id") !=
            std::optional<std::string>{"entrega03.native_learning.v1"} ||
        runtime.current_tick() != 40) {
        throw std::invalid_argument("not an Entrega 03 learned-state checkpoint");
    }
    runtime.set_execution_options({dee::v27::Backend::Lazy, 4});
    const auto g = geometry();
    std::vector<std::uint64_t> ids;
    inject_holdout(runtime, g, ids);
    std::uint64_t overflows = 0;
    const auto [use1, use2] = continue_holdout(runtime, g, overflows);
    runtime.set_protocol_phase("HOLDOUT_COMPLETED_RESUMED_PROCESS");
    runtime.save_snapshot(resumed_snapshot.string());

    const auto reference = Runtime::load_snapshot(final_reference.string());
    const bool raw_exact = runtime.raw_copy() == reference.raw_copy();
    const bool clock_exact = runtime.clock_copy() == reference.clock_copy();

    ensure_parent(result_csv);
    std::ofstream out(result_csv);
    if (!out) throw std::runtime_error("cannot write resume result");
    out << "mode,tick,holdout_use1,holdout_use2,new_overflows,events_scheduled,raw_exact,clock_exact\n";
    out << "new_process_resume," << runtime.current_tick() << ',' << use1
        << ',' << use2 << ',' << overflows << ',' << ids.size() << ','
        << raw_exact << ',' << clock_exact << '\n';
    if (use1 != 4185 || use2 != 4189 || !raw_exact || !clock_exact) {
        throw std::runtime_error("new-process checkpoint continuation mismatch");
    }
}

void usage() {
    std::cerr
        << "Usage:\n"
        << "  dee_entrega03_native_learning --baseline OUT.txt\n"
        << "  dee_entrega03_native_learning --panel OUT_DIR\n"
        << "  dee_entrega03_native_learning --panel-lazy OUT_DIR\n"
        << "  dee_entrega03_native_learning --make-checkpoint CHECKPOINT FINAL_REF OUT.csv\n"
        << "  dee_entrega03_native_learning --resume CHECKPOINT FINAL_REF OUT.csv RESUMED\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 3 && std::string_view(argv[1]) == "--baseline") {
            run_baseline(argv[2]);
            std::cout << "baseline=PASS output=" << argv[2] << '\n';
            return 0;
        }
        if (argc == 3 && std::string_view(argv[1]) == "--panel") {
            run_panel(argv[2], true);
            std::cout << "panel=PASS output=" << argv[2] << '\n';
            return 0;
        }
        if (argc == 3 && std::string_view(argv[1]) == "--panel-lazy") {
            run_panel(argv[2], false);
            std::cout << "panel_lazy=PASS output=" << argv[2] << '\n';
            return 0;
        }
        if (argc == 5 && std::string_view(argv[1]) == "--make-checkpoint") {
            make_checkpoint(argv[2], argv[3], argv[4]);
            std::cout << "checkpoint=PASS path=" << argv[2] << '\n';
            return 0;
        }
        if (argc == 6 && std::string_view(argv[1]) == "--resume") {
            resume_checkpoint(argv[2], argv[3], argv[4], argv[5]);
            std::cout << "resume=PASS checkpoint=" << argv[2] << '\n';
            return 0;
        }
        usage();
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
