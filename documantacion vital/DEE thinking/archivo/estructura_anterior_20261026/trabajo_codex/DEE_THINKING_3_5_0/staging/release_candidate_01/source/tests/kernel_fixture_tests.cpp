#include "dee_thinking/kernel_v27.hpp"

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
    Fixture f;
    f.n = read_exact<std::uint32_t>(input);
    f.ticks = read_exact<std::uint32_t>(input);
    const auto total64 = read_exact<std::uint64_t>(input);
    const auto expected_total = static_cast<std::uint64_t>(f.n) * f.n * f.n;
    if (f.n == 0 || total64 != expected_total || total64 > 100000000ULL) {
        throw std::runtime_error("invalid fixture dimensions: " + path.string());
    }
    const auto total = static_cast<std::size_t>(total64);
    auto read_vector = [&](std::vector<std::uint64_t>& values) {
        values.resize(total);
        input.read(reinterpret_cast<char*>(values.data()),
                   static_cast<std::streamsize>(total * sizeof(std::uint64_t)));
        if (!input) throw std::runtime_error("truncated fixture arrays: " + path.string());
    };
    read_vector(f.initial_raw);
    read_vector(f.initial_clock);
    read_vector(f.expected_raw);
    read_vector(f.expected_clock);
    if (input.peek() != std::char_traits<char>::eof()) {
        throw std::runtime_error("trailing fixture bytes: " + path.string());
    }
    return f;
}

std::size_t first_difference(const std::vector<std::uint64_t>& a,
                             const std::vector<std::uint64_t>& b) {
    for (std::size_t i = 0; i < a.size(); ++i) if (a[i] != b[i]) return i;
    return a.size();
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("usage: dee_kernel_fixture_tests FIXTURE_DIR");
        const std::filesystem::path root(argv[1]);
        std::size_t cases = 0;
        for (const auto& entry : std::filesystem::directory_iterator(root)) {
            if (!entry.is_regular_file() || entry.path().extension() != ".dtr") continue;
            const auto fixture = load_fixture(entry.path());
            auto raw_a = fixture.initial_raw;
            auto raw_b = fixture.initial_raw;
            auto clock_a = fixture.initial_clock;
            auto clock_b = fixture.initial_clock;
            for (std::uint32_t tick = 0; tick < fixture.ticks; ++tick) {
                (void)dee::v27::tick(raw_a, raw_b, clock_a, clock_b,
                                    static_cast<int>(fixture.n));
                if (raw_a != raw_b || clock_a != clock_b) {
                    throw std::runtime_error(entry.path().filename().string() +
                                             ": four-buffer copy-back mismatch");
                }
            }
            if (raw_a != fixture.expected_raw) {
                const auto at = first_difference(raw_a, fixture.expected_raw);
                throw std::runtime_error(entry.path().filename().string() +
                                         ": RAW differs first at linear index " + std::to_string(at));
            }
            if (clock_a != fixture.expected_clock) {
                const auto at = first_difference(clock_a, fixture.expected_clock);
                throw std::runtime_error(entry.path().filename().string() +
                                         ": clock differs first at linear index " + std::to_string(at));
            }
            ++cases;
            std::cout << "MATCH " << entry.path().filename().string() << '\n';
        }
        if (cases < 15) throw std::runtime_error("expected at least fifteen independent fixtures");
        std::cout << "WHL_DIFFERENTIAL_CASES=" << cases << " ALL_EXACT=true\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "fixture validation failed: " << error.what() << '\n';
        return 1;
    }
}
