#include "dee_thinking/kernel_v27.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <array>
#include <climits>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct Fixture {
    std::uint32_t n{};
    std::uint32_t ticks{};
    std::vector<std::uint64_t> initial_raw;
    std::vector<std::uint64_t> initial_clock;
    std::vector<std::uint64_t> expected_raw;
    std::vector<std::uint64_t> expected_clock;
};

struct State {
    std::vector<std::uint64_t> raw;
    std::vector<std::uint64_t> clock;
    std::uint64_t overflows{};
    std::uint64_t genesis{};
};

template <typename T>
T read_exact(std::ifstream& input) {
    T value{};
    input.read(reinterpret_cast<char*>(&value), sizeof(value));
    if (!input) throw std::runtime_error("truncated fixture header");
    return value;
}

Fixture load_fixture(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open fixture: " + path.string());
    char magic[8]{};
    input.read(magic, sizeof(magic));
    if (!input || std::string(magic, sizeof(magic)) != "DTRV2701") {
        throw std::runtime_error("invalid fixture magic: " + path.string());
    }
    Fixture fixture;
    fixture.n = read_exact<std::uint32_t>(input);
    fixture.ticks = read_exact<std::uint32_t>(input);
    const auto total64 = read_exact<std::uint64_t>(input);
    const auto expected_total =
        static_cast<std::uint64_t>(fixture.n) * fixture.n * fixture.n;
    if (fixture.n == 0 || total64 != expected_total || total64 > 100000000ULL) {
        throw std::runtime_error("invalid fixture dimensions: " + path.string());
    }
    const auto total = static_cast<std::size_t>(total64);
    auto read_vector = [&](std::vector<std::uint64_t>& values) {
        values.resize(total);
        input.read(reinterpret_cast<char*>(values.data()),
                   static_cast<std::streamsize>(total * sizeof(std::uint64_t)));
        if (!input) throw std::runtime_error("truncated fixture arrays: " + path.string());
    };
    read_vector(fixture.initial_raw);
    read_vector(fixture.initial_clock);
    read_vector(fixture.expected_raw);
    read_vector(fixture.expected_clock);
    if (input.peek() != std::char_traits<char>::eof()) {
        throw std::runtime_error("trailing fixture bytes: " + path.string());
    }
    return fixture;
}

std::size_t wrap(int value, int n) {
    const int remainder = value % n;
    return static_cast<std::size_t>(remainder < 0 ? remainder + n : remainder);
}

std::size_t index_of(int x, int y, int z, int n) {
    return (wrap(x, n) * static_cast<std::size_t>(n) + wrap(y, n)) *
               static_cast<std::size_t>(n) +
           wrap(z, n);
}

std::size_t lazy_candidate_count(const std::vector<std::uint64_t>& raw, int n) {
    std::vector<std::uint8_t> candidates(raw.size(), 0);
    const std::size_t plane = static_cast<std::size_t>(n) * n;
    for (std::size_t index = 0; index < raw.size(); ++index) {
        if (raw[index] == 0ULL) continue;
        const int x = static_cast<int>(index / plane);
        const auto remainder = index % plane;
        const int y = static_cast<int>(remainder / static_cast<std::size_t>(n));
        const int z = static_cast<int>(remainder % static_cast<std::size_t>(n));
        for (int dx = -1; dx <= 1; ++dx) {
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dz = -1; dz <= 1; ++dz) {
                    candidates[index_of(x + dx, y + dy, z + dz, n)] = 1;
                }
            }
        }
    }
    return static_cast<std::size_t>(
        std::count(candidates.begin(), candidates.end(), std::uint8_t{1}));
}

std::uint64_t active_raw_count(const std::vector<std::uint64_t>& raw) {
    return static_cast<std::uint64_t>(
        std::count_if(raw.begin(), raw.end(), [](auto value) { return value != 0ULL; }));
}

std::size_t first_difference(const std::vector<std::uint64_t>& left,
                             const std::vector<std::uint64_t>& right) {
    const auto common = std::min(left.size(), right.size());
    for (std::size_t index = 0; index < common; ++index) {
        if (left[index] != right[index]) return index;
    }
    return common;
}

std::string divergence_detail(const std::string& context,
                              const std::vector<std::uint64_t>& left,
                              const std::vector<std::uint64_t>& right) {
    const auto index = first_difference(left, right);
    if (index == left.size() && index == right.size()) return context;
    return context + " first divergence at linear index " +
           std::to_string(index) + " left_size=" + std::to_string(left.size()) +
           " right_size=" + std::to_string(right.size());
}

void check_backend_telemetry(dee::thinking::test::Suite& suite,
                             const dee::v27::TickInfo& info,
                             const dee::v27::TickOptions& options,
                             std::size_t expected_work,
                             std::uint64_t expected_active,
                             std::size_t total,
                             int n) {
    DEE_CHECK(suite, info.requested_backend == options.backend);
    DEE_CHECK(suite, info.used_backend == options.backend);
    DEE_CHECK_EQ(suite, info.requested_threads, options.threads);
    DEE_CHECK_EQ(suite, info.evaluated, static_cast<std::uint64_t>(expected_work));
    DEE_CHECK_EQ(suite, info.active_raw, expected_active);
    DEE_CHECK_EQ(suite, info.total, static_cast<std::uint64_t>(total));
    DEE_CHECK(suite, !info.fallback);
    DEE_CHECK(suite, info.total_ns >= info.preparation_ns);
    DEE_CHECK(suite, info.total_ns >= info.evaluation_ns);
    DEE_CHECK(suite, info.total_ns >= info.postprocess_ns);
    DEE_CHECK(suite, info.total_ns >=
                         info.preparation_ns + info.evaluation_ns +
                             info.postprocess_ns);
    if (options.backend == dee::v27::Backend::DenseSequential) {
        DEE_CHECK_EQ(suite, info.used_threads, std::size_t{1});
    } else if (options.backend == dee::v27::Backend::DenseParallel) {
        const auto possible_workers =
            std::min(options.threads, static_cast<std::size_t>(n));
        const auto slabs =
            (static_cast<std::size_t>(n) + possible_workers - 1U) /
            possible_workers;
        const auto nonempty_workers =
            (static_cast<std::size_t>(n) + slabs - 1U) / slabs;
        DEE_CHECK_EQ(
            suite, info.used_threads, nonempty_workers);
    } else {
        DEE_CHECK_EQ(suite, info.used_threads,
                     std::min(options.threads, expected_work));
    }
}

}  // namespace

int main(int argc, char** argv) {
    dee::thinking::test::Suite suite("backend_equivalence");
    try {
        if (argc != 2) throw std::runtime_error("usage: dee_backend_tests FIXTURE_DIR");
        const std::filesystem::path root(argv[1]);
        const std::array<dee::v27::TickOptions, 7> configurations{{
            {dee::v27::Backend::DenseSequential, 1},
            {dee::v27::Backend::DenseParallel, 1},
            {dee::v27::Backend::DenseParallel, 2},
            {dee::v27::Backend::DenseParallel, 4},
            {dee::v27::Backend::Lazy, 1},
            {dee::v27::Backend::Lazy, 2},
            {dee::v27::Backend::Lazy, 4},
        }};

        std::size_t fixture_count = 0;
        bool lazy_zero_worker_case_seen = false;
        bool lazy_four_worker_case_seen = false;
        bool dense_uneven_worker_case_seen = false;
        bool physical_demux_event_seen = false;
        bool orphan_evolution_case_seen = false;
        bool occupied_saturation_case_seen = false;
        bool strong_and_protected_case_seen = false;
        for (const auto& entry : std::filesystem::directory_iterator(root)) {
            if (!entry.is_regular_file() || entry.path().extension() != ".dtr") continue;
            const Fixture fixture = load_fixture(entry.path());
            const int n = static_cast<int>(fixture.n);
            const std::size_t total = fixture.initial_raw.size();

            // DenseSequential is retained as the reference execution schedule,
            // and each intermediate state is kept so transient divergence cannot
            // hide behind later convergence.
            std::vector<State> reference_states;
            auto reference_raw = fixture.initial_raw;
            auto reference_raw_scratch = fixture.initial_raw;
            auto reference_clock = fixture.initial_clock;
            auto reference_clock_scratch = fixture.initial_clock;
            for (std::uint32_t step = 0; step < fixture.ticks; ++step) {
                const auto before = reference_raw;
                const auto info = dee::v27::tick(
                    reference_raw, reference_raw_scratch, reference_clock,
                    reference_clock_scratch, n,
                    {dee::v27::Backend::DenseSequential, 1});
                check_backend_telemetry(suite, info,
                                        {dee::v27::Backend::DenseSequential, 1},
                                        total, active_raw_count(before), total, n);
                DEE_CHECK(suite, reference_raw == reference_raw_scratch);
                DEE_CHECK(suite, reference_clock == reference_clock_scratch);
                reference_states.push_back(
                    {reference_raw, reference_clock, info.overflows, info.genesis});
            }
            DEE_CHECK(suite, reference_raw == fixture.expected_raw);
            DEE_CHECK(suite, reference_clock == fixture.expected_clock);

            // Three repeats exercise the same 1/2/4-thread schedules.  Exact
            // vector equality is required; there is no integer tolerance.
            for (const auto& options : configurations) {
                for (int repeat = 0; repeat < 3; ++repeat) {
                    auto raw = fixture.initial_raw;
                    auto raw_scratch = fixture.initial_raw;
                    auto clock = fixture.initial_clock;
                    auto clock_scratch = fixture.initial_clock;
                    for (std::uint32_t step = 0; step < fixture.ticks; ++step) {
                        const auto before = raw;
                        const std::size_t work =
                            options.backend == dee::v27::Backend::Lazy
                                ? lazy_candidate_count(before, n)
                                : total;
                        const auto info = dee::v27::tick(
                            raw, raw_scratch, clock, clock_scratch, n, options);
                        check_backend_telemetry(suite, info, options, work,
                                                active_raw_count(before), total, n);
                        if (options.backend == dee::v27::Backend::Lazy &&
                            info.used_threads == 0U) {
                            lazy_zero_worker_case_seen = true;
                        }
                        if (options.backend == dee::v27::Backend::Lazy &&
                            options.threads == 4U && info.used_threads == 4U) {
                            lazy_four_worker_case_seen = true;
                        }
                        if (options.backend == dee::v27::Backend::DenseParallel &&
                            options.threads == 4U && info.used_threads < 4U) {
                            dense_uneven_worker_case_seen = true;
                        }
                        if (info.overflows != 0U) physical_demux_event_seen = true;
                        const auto context =
                            entry.path().filename().string() + " step=" +
                            std::to_string(step) + " repeat=" +
                            std::to_string(repeat) + " backend=" +
                            dee::v27::backend_name(options.backend) + " threads=" +
                            std::to_string(options.threads);
                        DEE_CHECK_DETAIL(
                            suite, raw == reference_states[step].raw,
                            divergence_detail(context + " RAW", raw,
                                              reference_states[step].raw));
                        DEE_CHECK_DETAIL(
                            suite, clock == reference_states[step].clock,
                            divergence_detail(context + " clock", clock,
                                              reference_states[step].clock));
                        DEE_CHECK_EQ(suite, info.overflows,
                                     reference_states[step].overflows);
                        DEE_CHECK_EQ(suite, info.genesis,
                                     reference_states[step].genesis);
                        DEE_CHECK_DETAIL(
                            suite, raw == raw_scratch,
                            divergence_detail(context + " RAW/scratch", raw,
                                              raw_scratch));
                        DEE_CHECK_DETAIL(
                            suite, clock == clock_scratch,
                            divergence_detail(context + " clock/scratch", clock,
                                              clock_scratch));
                    }
                    DEE_CHECK(suite, raw == fixture.expected_raw);
                    DEE_CHECK(suite, clock == fixture.expected_clock);
                }
            }

            // The legacy five-argument entry point remains dense sequential.
            if (fixture.ticks != 0) {
                auto raw = fixture.initial_raw;
                auto raw_scratch = fixture.initial_raw;
                auto clock = fixture.initial_clock;
                auto clock_scratch = fixture.initial_clock;
                const auto info =
                    dee::v27::tick(raw, raw_scratch, clock, clock_scratch, n);
                DEE_CHECK(suite,
                          info.used_backend == dee::v27::Backend::DenseSequential);
                DEE_CHECK_EQ(suite, info.used_threads, std::size_t{1});
                DEE_CHECK(suite, raw == reference_states.front().raw);
                DEE_CHECK(suite, clock == reference_states.front().clock);
            }

            if (entry.path().filename() == "demux_overflow_six_neighbors.dtr") {
                DEE_CHECK_EQ(suite, reference_states.front().overflows, 1ULL);
                DEE_CHECK_EQ(suite, reference_states.front().genesis, 0ULL);
            }
            if (entry.path().filename() == "demux_atomic_shared_target.dtr") {
                DEE_CHECK_EQ(suite, reference_states.front().overflows, 2ULL);
                DEE_CHECK_EQ(suite, reference_states.front().genesis, 0ULL);
                const auto target = dee::v27::decode_record(
                    reference_states.front().raw[index_of(3, 2, 2, n)]);
                DEE_CHECK_EQ(suite, target.state, 1U);
                DEE_CHECK_EQ(suite, target.s_reg, static_cast<std::uint16_t>(12));
            }
            if (entry.path().filename() == "orphan_reachable_evolution.dtr") {
                orphan_evolution_case_seen = true;
                DEE_CHECK_EQ(suite, reference_states.size(), std::size_t{1});
                const auto center = dee::v27::decode_record(
                    reference_states.front().raw[index_of(3, 3, 3, n)]);
                DEE_CHECK_EQ(suite, center.state, 1U);
                DEE_CHECK_EQ(suite, center.s_reg, static_cast<std::uint16_t>(8));
                DEE_CHECK_EQ(suite, static_cast<int>(center.dx), -1);
                DEE_CHECK_EQ(suite, static_cast<int>(center.dy), 0);
                DEE_CHECK_EQ(suite, static_cast<int>(center.dz), 0);
                DEE_CHECK_EQ(suite, center.semantic, static_cast<std::uint8_t>(5));
            }
            if (entry.path().filename() == "demux_occupied_saturation.dtr") {
                occupied_saturation_case_seen = true;
                DEE_CHECK_EQ(suite, reference_states.size(), std::size_t{1});
                DEE_CHECK_EQ(suite, reference_states.front().overflows, 2ULL);
                const auto target = dee::v27::decode_record(
                    reference_states.front().raw[index_of(3, 2, 2, n)]);
                DEE_CHECK_EQ(suite, target.state, 1U);
                DEE_CHECK_EQ(suite, target.s_reg,
                             static_cast<std::uint16_t>(19664));
                DEE_CHECK_EQ(suite, static_cast<int>(target.dz), -1);
                DEE_CHECK_EQ(suite, target.semantic, static_cast<std::uint8_t>(1));
            }
            if (entry.path().filename() == "strong_tension_write_protection.dtr") {
                strong_and_protected_case_seen = true;
                DEE_CHECK_EQ(suite, reference_states.size(), std::size_t{1});
                const auto strong = dee::v27::decode_record(
                    reference_states.front().raw[index_of(3, 3, 3, n)]);
                DEE_CHECK_EQ(suite, strong.state, 2U);
                DEE_CHECK_EQ(suite, strong.s_reg, static_cast<std::uint16_t>(5));
                const auto protected_record = dee::v27::decode_record(
                    reference_states.front().raw[index_of(9, 9, 9, n)]);
                DEE_CHECK_EQ(suite, protected_record.state, 1U);
                DEE_CHECK_EQ(suite, protected_record.s_reg,
                             static_cast<std::uint16_t>(42));
            }

            ++fixture_count;
            std::cout << "BACKENDS_EXACT " << entry.path().filename().string()
                      << " configurations=7 repeats=3\n";
        }
        DEE_CHECK(suite, fixture_count >= 15);
        DEE_CHECK(suite, lazy_zero_worker_case_seen);
        DEE_CHECK(suite, lazy_four_worker_case_seen);
        DEE_CHECK(suite, dense_uneven_worker_case_seen);
        DEE_CHECK(suite, physical_demux_event_seen);
        DEE_CHECK(suite, orphan_evolution_case_seen);
        DEE_CHECK(suite, occupied_saturation_case_seen);
        DEE_CHECK(suite, strong_and_protected_case_seen);

        // Invalid execution settings fail before mutating any physical buffer.
        constexpr int n = 3;
        std::vector<std::uint64_t> raw(27, 0), raw_scratch(27, 0);
        std::vector<std::uint64_t> clock(27, 9), clock_scratch(27, 4);
        const auto raw_before = raw;
        const auto raw_scratch_before = raw_scratch;
        const auto clock_before = clock;
        const auto clock_scratch_before = clock_scratch;
        DEE_CHECK_THROWS(
            suite, dee::v27::tick(raw, raw_scratch, clock, clock_scratch, n,
                                  {dee::v27::Backend::Lazy, 0}));
        DEE_CHECK(suite, raw == raw_before);
        DEE_CHECK(suite, raw_scratch == raw_scratch_before);
        DEE_CHECK(suite, clock == clock_before);
        DEE_CHECK(suite, clock_scratch == clock_scratch_before);
        DEE_CHECK_THROWS(
            suite, dee::v27::tick(raw, raw_scratch, clock, clock_scratch, n,
                                  {static_cast<dee::v27::Backend>(255), 1}));
        DEE_CHECK_THROWS(
            suite,
            dee::v27::tick(
                raw, raw_scratch, clock, clock_scratch, n,
                {dee::v27::Backend::DenseParallel,
                 static_cast<std::size_t>(INT_MAX) + std::size_t{1}}));

        std::cout << "SOURCE_V27_SHA256="
                     "44a80f7863d78f596099ddf7d41c9947fa8513503f65067097f1f3b05a8207ab\n";
        return suite.finish();
    } catch (const std::exception& error) {
        std::cerr << "backend validation failed: " << error.what() << '\n';
        return 1;
    }
}
