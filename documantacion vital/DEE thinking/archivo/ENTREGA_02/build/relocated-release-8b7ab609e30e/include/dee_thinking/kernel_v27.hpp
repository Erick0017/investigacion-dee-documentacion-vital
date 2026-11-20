#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

namespace dee::v27 {

inline constexpr std::uint64_t kKernelModulus = 19665ULL;
inline constexpr std::uint16_t kReducerCap = 19664U;

enum class Semantic : std::uint8_t {
    Void = 0,
    Normal = 1,
    ElectronSeed = 2,
    ProtonSeed = 3,
    Observer = 4,
    OrphanBit = 5,
    Horizon = 6,
    BornXnor = 7,
};

// Execution backends are scheduling choices only.  They all evaluate the
// frozen v27 local rule and produce the same RAW+clock transition.
enum class Backend : std::uint8_t {
    DenseSequential = 0,
    DenseParallel = 1,
    Lazy = 2,
};

struct TickOptions {
    Backend backend{Backend::DenseSequential};
    std::size_t threads{1};
};

struct Record {
    std::uint64_t raw{};
    std::uint32_t state{};
    std::uint16_t s_reg{};
    std::int8_t dx{};
    std::int8_t dy{};
    std::int8_t dz{};
    std::uint8_t semantic{};

    [[nodiscard]] bool raw_present() const noexcept { return raw != 0; }
    [[nodiscard]] bool occupied() const noexcept { return state != 0; }
};

struct TickInfo {
    std::uint64_t overflows{};
    std::uint64_t genesis{};
    std::uint64_t evaluated{};
    std::uint64_t active_raw{};
    std::uint64_t total{};
    Backend requested_backend{Backend::DenseSequential};
    Backend used_backend{Backend::DenseSequential};
    std::size_t requested_threads{1};
    std::size_t used_threads{1};
    bool fallback{};
    // Host-side technical timings.  They are not DEE physical state and are
    // intentionally excluded from snapshots and equivalence comparisons.
    std::uint64_t preparation_ns{};
    std::uint64_t evaluation_ns{};
    std::uint64_t postprocess_ns{};
    std::uint64_t total_ns{};
};

[[nodiscard]] const char* backend_name(Backend backend) noexcept;

[[nodiscard]] std::uint64_t pack_record(
    std::uint32_t state,
    std::uint16_t s_reg,
    int dx,
    int dy,
    int dz,
    std::uint8_t semantic);

[[nodiscard]] Record decode_record(std::uint64_t raw) noexcept;
[[nodiscard]] std::size_t linear_index(int x, int y, int z, int n);
[[nodiscard]] int wrap_coordinate(int value, int n);

// Exact dense v27 transition. gA/clockA are active buffers and are overwritten
// with the destination, matching the historical kernel copy-back contract.
TickInfo tick(
    std::vector<std::uint64_t>& gA,
    std::vector<std::uint64_t>& gB,
    std::vector<std::uint64_t>& clockA,
    std::vector<std::uint64_t>& clockB,
    int n);

// Explicit execution-backend entry point.  Valid thread requests are in the
// positive int range used by the canonical v27 tick_universo boundary.
// DenseSequential always uses one caller thread.  DenseParallel and Lazy use
// at most the requested number of workers and report the actual count.
TickInfo tick(
    std::vector<std::uint64_t>& gA,
    std::vector<std::uint64_t>& gB,
    std::vector<std::uint64_t>& clockA,
    std::vector<std::uint64_t>& clockB,
    int n,
    const TickOptions& options);

}  // namespace dee::v27
