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
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

struct State {
    int n{};
    std::vector<std::uint64_t> raw;
    std::vector<std::uint64_t> clock;
};

struct Configuration {
    dee::v27::Backend backend{};
    std::size_t threads{};
};

std::uint64_t ns(Clock::time_point begin, Clock::time_point end) {
    return static_cast<std::uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin).count());
}

State make_sparse() {
    State state;
    state.n = 31;
    const auto total = static_cast<std::size_t>(state.n) * state.n * state.n;
    state.raw.assign(total, 0);
    state.clock.resize(total);
    for (std::size_t i = 0; i < total; ++i) state.clock[i] = (17U * i + 3U) % 991U;
    const std::array<std::array<int, 3>, 8> sites{{
        {{2, 2, 2}}, {{6, 7, 8}}, {{10, 10, 10}}, {{15, 15, 15}},
        {{20, 21, 22}}, {{25, 4, 17}}, {{30, 30, 30}}, {{0, 12, 19}},
    }};
    for (std::size_t i = 0; i < sites.size(); ++i) {
        const auto& p = sites[i];
        const auto index = dee::v27::linear_index(p[0], p[1], p[2], state.n);
        // The final entry deliberately preserves raw!=0 with decoded state=0.
        state.raw[index] = dee::v27::pack_record(
            i + 1U == sites.size() ? 0U : 1U,
            static_cast<std::uint16_t>(7U + 11U * i),
            static_cast<int>(i % 3U) - 1,
            static_cast<int>((i + 1U) % 3U) - 1,
            static_cast<int>((i + 2U) % 3U) - 1,
            i == 2U ? 4U : 1U);
    }
    return state;
}

State make_dense() {
    State state;
    state.n = 17;
    const auto total = static_cast<std::size_t>(state.n) * state.n * state.n;
    state.raw.assign(total, 0);
    state.clock.resize(total);
    for (std::size_t i = 0; i < total; ++i) {
        state.clock[i] = (194422ULL + 37ULL * i) % 1000003ULL;
        if ((i * 13U + 5U) % 10U < 4U) {
            const int dx = static_cast<int>(i % 3U) - 1;
            const int dy = static_cast<int>((i / 3U) % 3U) - 1;
            int dz = static_cast<int>((i / 9U) % 3U) - 1;
            if (dx == 0 && dy == 0 && dz == 0) dz = 1;
            state.raw[i] = dee::v27::pack_record(
                1U + static_cast<std::uint32_t>(i % 3U),
                static_cast<std::uint16_t>((i * 97U) % 19000U),
                dx, dy, dz,
                static_cast<std::uint8_t>(1U + (i % 4U)));
        }
    }
    return state;
}

State make_history() {
    State state = make_sparse();
    const auto total = state.raw.size();
    std::vector<std::uint64_t> raw_b(total), clock_b(total);
    for (int tick = 0; tick < 12; ++tick) {
        dee::v27::tick(state.raw, raw_b, state.clock, clock_b, state.n);
    }
    return state;
}

void write_string(std::ostream& out, const std::string& value) {
    out << '"';
    for (const char c : value) {
        if (c == '"' || c == '\\') out << '\\';
        out << c;
    }
    out << '"';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const std::filesystem::path output = argc > 1 ? argv[1] : "backend_benchmark.json";
        std::filesystem::create_directories(output.parent_path().empty()
                                                ? std::filesystem::current_path()
                                                : output.parent_path());

        const std::array<std::pair<const char*, State>, 3> cases{{
            {"sparse", make_sparse()},
            {"dense", make_dense()},
            {"history_evolved", make_history()},
        }};
        const std::array<Configuration, 7> configurations{{
            {dee::v27::Backend::DenseSequential, 1},
            {dee::v27::Backend::DenseParallel, 1},
            {dee::v27::Backend::DenseParallel, 2},
            {dee::v27::Backend::DenseParallel, 4},
            {dee::v27::Backend::Lazy, 1},
            {dee::v27::Backend::Lazy, 2},
            {dee::v27::Backend::Lazy, 4},
        }};
        constexpr int repeats = 3;
        constexpr int horizon = 4;

        std::ofstream out(output, std::ios::binary | std::ios::trunc);
        if (!out) throw std::runtime_error("cannot open benchmark output");
        out << "{\n  \"schema\": \"dee-thinking-backend-benchmark-v1\",\n"
               "  \"configuration\": {\"repeats\": " << repeats
            << ", \"horizon_ticks\": " << horizon
            << ", \"instrumentation_included_equally\": true},\n  \"runs\": [\n";

        bool first = true;
        bool all_exact = true;
        for (const auto& [case_name, initial] : cases) {
            std::vector<std::uint64_t> oracle_raw;
            std::vector<std::uint64_t> oracle_clock;
            for (const auto& config : configurations) {
                for (int repeat = 0; repeat < repeats; ++repeat) {
                    const auto initialization_begin = Clock::now();
                    auto raw = initial.raw;
                    auto clock = initial.clock;
                    std::vector<std::uint64_t> raw_b(raw.size()), clock_b(clock.size());
                    const auto initialization_end = Clock::now();

                    std::uint64_t preparation_ns = 0;
                    std::uint64_t evaluation_ns = 0;
                    std::uint64_t postprocess_ns = 0;
                    std::uint64_t kernel_total_ns = 0;
                    std::uint64_t evaluated = 0;
                    std::size_t used_threads = 0;
                    dee::v27::Backend used_backend = config.backend;
                    bool fallback = false;
                    const auto measured_begin = Clock::now();
                    for (int tick_index = 0; tick_index < horizon; ++tick_index) {
                        const auto info = dee::v27::tick(
                            raw, raw_b, clock, clock_b, initial.n,
                            {config.backend, config.threads});
                        preparation_ns += info.preparation_ns;
                        evaluation_ns += info.evaluation_ns;
                        postprocess_ns += info.postprocess_ns;
                        kernel_total_ns += info.total_ns;
                        evaluated += info.evaluated;
                        used_threads = std::max(used_threads, info.used_threads);
                        used_backend = info.used_backend;
                        fallback = fallback || info.fallback;
                    }
                    const auto measured_end = Clock::now();
                    if (config.backend == dee::v27::Backend::DenseSequential && repeat == 0) {
                        oracle_raw = raw;
                        oracle_clock = clock;
                    }
                    const bool exact = raw == oracle_raw && clock == oracle_clock;
                    all_exact = all_exact && exact;

                    if (!first) out << ",\n";
                    first = false;
                    out << "    {\"case\": ";
                    write_string(out, case_name);
                    out << ", \"n\": " << initial.n
                        << ", \"backend_requested\": ";
                    write_string(out, dee::v27::backend_name(config.backend));
                    out << ", \"backend_used\": ";
                    write_string(out, dee::v27::backend_name(used_backend));
                    out << ", \"threads_requested\": " << config.threads
                        << ", \"threads_used_max\": " << used_threads
                        << ", \"repeat\": " << repeat
                        << ", \"initialization_ns\": " << ns(initialization_begin, initialization_end)
                        << ", \"work_preparation_ns\": " << preparation_ns
                        << ", \"local_evaluation_ns\": " << evaluation_ns
                        << ", \"postprocess_clock_copy_ns\": " << postprocess_ns
                        << ", \"kernel_reported_total_ns\": " << kernel_total_ns
                        << ", \"measured_tick_loop_ns\": " << ns(measured_begin, measured_end)
                        << ", \"evaluated_voxels\": " << evaluated
                        << ", \"fallback\": " << (fallback ? "true" : "false")
                        << ", \"raw_clock_exact_vs_dense_reference\": "
                        << (exact ? "true" : "false") << '}';
                }
            }
        }

        // Runtime overhead is kept separate from the kernel rows.  The input
        // is requested after construction, observe is passive, and snapshot
        // persistence is timed without being folded into any backend.
        const auto pipeline_begin = Clock::now();
        const auto runtime_initialization_begin = pipeline_begin;
        dee::thinking::Runtime runtime(17);
        runtime.set_execution_options({dee::v27::Backend::DenseSequential, 1});
        runtime.register_channel({"benchmark_input", {1, 1, 1}, 1, {1, 0, 0}, 1, true, false});
        const auto runtime_initialization_end = Clock::now();
        const auto event_begin = Clock::now();
        const auto receipt = runtime.experience("benchmark_input", 0, 7);
        const auto event_end = Clock::now();
        // advance(1) applies the pending event at the tick boundary and then
        // runs F_DEE once.  Subtracting the kernel's own timer leaves a clearly
        // labelled estimate of event/wrapper management rather than pretending
        // that boundary application is free.
        const auto boundary_begin = Clock::now();
        runtime.advance(1);
        const auto boundary_end = Clock::now();
        const auto boundary_wall_ns = ns(boundary_begin, boundary_end);
        const auto boundary_kernel_ns = runtime.last_tick_info().total_ns;
        const auto boundary_management_estimate_ns =
            boundary_wall_ns > boundary_kernel_ns ? boundary_wall_ns - boundary_kernel_ns : 0;
        const auto observation_begin = Clock::now();
        for (int i = 0; i < 100; ++i) (void)runtime.observe({i % 17, (i / 17) % 17, 0});
        const auto observation_end = Clock::now();
        const auto snapshot_path = output.parent_path() / "benchmark_persistence.deetsnap";
        const auto persistence_begin = Clock::now();
        runtime.save_snapshot(snapshot_path.string());
        const auto persistence_end = Clock::now();
        const auto restore_begin = Clock::now();
        auto restored = dee::thinking::Runtime::load_snapshot(snapshot_path.string());
        const auto restore_end = Clock::now();
        if (restored.current_tick() != runtime.current_tick()) {
            throw std::runtime_error("runtime benchmark restore mismatch");
        }
        const auto pipeline_end = Clock::now();

        out << "\n  ],\n  \"runtime_overhead\": {"
            << "\"runtime_initialization_and_channel_ns\": "
            << ns(runtime_initialization_begin, runtime_initialization_end)
            << ", \"event_schedule_ns\": " << ns(event_begin, event_end)
            << ", \"event_status\": ";
        write_string(out, dee::thinking::to_string(receipt.status));
        out << ", \"event_boundary_advance_wall_ns\": " << boundary_wall_ns
            << ", \"event_boundary_kernel_reported_ns\": " << boundary_kernel_ns
            << ", \"event_application_and_runtime_overhead_estimate_ns\": "
            << boundary_management_estimate_ns
            << ", \"one_hundred_observations_ns\": " << ns(observation_begin, observation_end)
            << ", \"snapshot_persistence_ns\": " << ns(persistence_begin, persistence_end)
            << ", \"snapshot_restore_ns\": " << ns(restore_begin, restore_end)
            << ", \"snapshot_bytes\": " << std::filesystem::file_size(snapshot_path)
            << ", \"end_to_end_total_ns\": " << ns(pipeline_begin, pipeline_end) << "},\n"
            << "  \"all_raw_clock_exact\": " << (all_exact ? "true" : "false") << "\n}\n";
        out.close();
        std::cout << "BENCHMARK_OUTPUT=" << output.string() << '\n'
                  << "ALL_RAW_CLOCK_EXACT=" << (all_exact ? "true" : "false") << '\n';
        return all_exact ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "benchmark error: " << error.what() << '\n';
        return 1;
    }
}
