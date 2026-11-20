#pragma once

#include "dee_thinking/runtime.hpp"

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking::basal {

enum class Preset : std::uint8_t { RelationalBody = 1, ContextualRewrite = 2 };
enum class History : std::uint8_t { AB = 1, BA = 2, H0 = 3, Simultaneous = 4, Sham = 5 };
enum class Control : std::uint8_t {
    Full = 1,
    NoAction = 2,
    ReturnCut = 3,
    OffPath = 4,
    PhaseMiss = 5,
    Bare = 6,
    ReadCut = 7,
    ActionCut = 8,
};
enum class DomainMode : std::uint8_t { Validated = 1, Research = 2 };

[[nodiscard]] const char* to_string(Preset value) noexcept;
[[nodiscard]] const char* to_string(History value) noexcept;
[[nodiscard]] const char* to_string(Control value) noexcept;
[[nodiscard]] const char* to_string(DomainMode value) noexcept;

struct Config {
    Preset preset{Preset::RelationalBody};
    History history{History::AB};
    Control control{Control::Full};
    DomainMode domain_mode{DomainMode::Validated};
    int dimension{47};
    Coordinate origin{15, 15, 15};
    int action_distance{5};
    v27::TickOptions execution{v27::Backend::Lazy, 1};
    std::string seed_snapshot;

    [[nodiscard]] static Config relational_reference(std::string seed_snapshot);
    [[nodiscard]] static Config contextual_reference(std::string seed_snapshot);
};

struct Ports {
    Coordinate origin;
    Coordinate a;
    Coordinate b;
    Coordinate comparator;
    Coordinate reader_source;
    std::vector<Coordinate> event_sources;
    std::vector<Coordinate> supports;
    std::vector<Coordinate> environmental_sources;
    std::optional<Coordinate> action_site;
    std::optional<Coordinate> return_site;
    std::optional<Coordinate> bend_site;
    std::optional<Coordinate> bend2_site;
};

enum class Availability : std::uint8_t {
    Available = 1,
    MissingA = 2,
    MissingB = 3,
    MissingComparator = 4,
};

[[nodiscard]] const char* to_string(Availability value) noexcept;

struct Observation {
    std::uint64_t absolute_tick{};
    std::uint64_t relative_tick{};
    Availability availability{Availability::Available};
    std::optional<::dee::thinking::Observation> a;
    std::optional<::dee::thinking::Observation> b;
    std::optional<::dee::thinking::Observation> comparator;
    std::optional<std::int64_t> delta;
    std::optional<int> axis_projection;
    std::vector<::dee::thinking::Observation> supports;
};

class World {
public:
    [[nodiscard]] static World create(const Config& config);
    // Attach reconstructs only the inert view. It never installs matter.
    // The caller retains ownership and must keep Runtime alive for this view.
    [[nodiscard]] static World attach(Runtime& runtime, Config config, Ports ports,
                                      std::uint64_t t0_tick);
    [[nodiscard]] static World load_snapshot(const std::string& path);

    World(World&&) noexcept = default;
    World& operator=(World&&) noexcept = default;
    World(const World&) = delete;
    World& operator=(const World&) = delete;

    [[nodiscard]] const Config& config() const noexcept { return config_; }
    [[nodiscard]] const Ports& ports() const noexcept { return ports_; }
    [[nodiscard]] std::uint64_t t0_tick() const noexcept { return t0_tick_; }
    [[nodiscard]] Runtime& runtime() noexcept { return *runtime_; }
    [[nodiscard]] const Runtime& runtime() const noexcept { return *runtime_; }

    v27::TickInfo advance(std::uint64_t count = 1) { return runtime_->advance(count); }
    [[nodiscard]] Observation observe() const;
    [[nodiscard]] World fork() const;
    [[nodiscard]] World diagnostic_fork(
        const std::vector<ResearchStateEdit>& edits,
        bool authorize_diagnostic_intervention) const;
    void save_snapshot(const std::string& path);

private:
    World(std::unique_ptr<Runtime> runtime, Config config, Ports ports,
          std::uint64_t t0_tick)
        : owned_runtime_(std::move(runtime)), runtime_(owned_runtime_.get()),
          config_(std::move(config)),
          ports_(std::move(ports)), t0_tick_(t0_tick) {}
    World(Runtime& runtime, Config config, Ports ports, std::uint64_t t0_tick)
        : runtime_(&runtime), config_(std::move(config)),
          ports_(std::move(ports)), t0_tick_(t0_tick) {}

    std::unique_ptr<Runtime> owned_runtime_;
    Runtime* runtime_{};
    Config config_;
    Ports ports_;
    std::uint64_t t0_tick_{};
};

}  // namespace dee::thinking::basal
