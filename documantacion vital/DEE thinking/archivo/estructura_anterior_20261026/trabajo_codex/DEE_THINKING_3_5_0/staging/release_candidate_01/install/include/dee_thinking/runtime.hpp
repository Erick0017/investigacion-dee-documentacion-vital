#pragma once

#include "dee_thinking/kernel_v27.hpp"

#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking {

struct Coordinate {
    int x{};
    int y{};
    int z{};
    friend bool operator==(const Coordinate&, const Coordinate&) = default;
};

struct Direction {
    int dx{};
    int dy{};
    int dz{};
};

enum class EventKind : std::uint8_t { Experience = 1, Probe = 2 };
enum class EventStatus : std::uint8_t {
    Scheduled = 1,
    Applied = 2,
    RejectedLate = 3,
    RejectedInvalid = 4,
    RejectedOccupied = 5,
    RejectedConflict = 6,
    RejectedQueueFull = 7,
};

struct ChannelSpec {
    std::string name;
    Coordinate injection_site;
    std::uint32_t state{1};
    Direction direction{};
    std::uint8_t semantic{1};
    bool allow_experience{true};
    bool allow_probe{false};
};

struct InputRequest {
    std::string channel;
    std::uint16_t s_reg{};
};

struct EventReceipt {
    std::uint64_t id{};
    EventKind kind{EventKind::Experience};
    EventStatus status{EventStatus::Scheduled};
    std::uint64_t requested_tick{};
    std::optional<std::uint64_t> effective_tick;
    std::vector<std::string> channels;
    std::string reason;
};

struct Observation {
    std::uint64_t tick{};
    Coordinate coordinate;
    std::uint64_t raw{};
    std::uint64_t clock{};
    v27::Record record{};
};

struct WorldMetrics {
    std::uint64_t tick{};
    std::size_t raw_support{};
    std::size_t occupied{};
    std::uint64_t s_reg_sum{};
};

// Explicit, diagnostic-only mutation applied to a deep Runtime fork.  Missing
// optionals preserve the corresponding field.  The parent Runtime, pending
// events, channels, receipts, metadata and protocol phase are copied before
// these edits are applied to the fork.
struct ResearchStateEdit {
    Coordinate coordinate;
    std::optional<std::uint64_t> raw;
    std::optional<std::uint64_t> clock;
    std::string label;
};

class Runtime {
public:
    explicit Runtime(int dimension);

    [[nodiscard]] static Runtime import_research_state(
        int dimension,
        std::uint64_t tick,
        std::vector<std::uint64_t> raw,
        std::vector<std::uint64_t> clock);

    [[nodiscard]] int dimension() const noexcept { return n_; }
    [[nodiscard]] std::uint64_t current_tick() const noexcept { return tick_; }
    [[nodiscard]] bool paused() const noexcept { return paused_; }

    // Execution options alter only the evaluation schedule.  A setter call
    // takes effect at the next tick boundary and never mutates Q0 directly.
    void set_execution_options(v27::TickOptions options);
    [[nodiscard]] v27::TickOptions execution_options() const noexcept { return execution_options_; }
    [[nodiscard]] const v27::TickInfo& last_tick_info() const noexcept { return last_tick_info_; }

    void register_channel(ChannelSpec channel);
    [[nodiscard]] std::vector<std::string> channel_names() const;

    EventReceipt experience(const std::string& channel, std::uint64_t at_tick, std::uint16_t s_reg);
    EventReceipt experience_batch(const std::vector<InputRequest>& inputs, std::uint64_t at_tick);
    EventReceipt probe(const std::string& channel, std::uint64_t at_tick, std::uint16_t s_reg);
    [[nodiscard]] std::optional<EventReceipt> receipt(std::uint64_t id) const;
    [[nodiscard]] std::vector<EventReceipt> receipts() const;

    v27::TickInfo advance(std::uint64_t count = 1);
    v27::TickInfo run_until(std::uint64_t target_tick);
    void pause() noexcept { paused_ = true; }
    void resume() noexcept { paused_ = false; }

    [[nodiscard]] Observation observe(Coordinate coordinate) const;
    [[nodiscard]] std::vector<Observation> observe_many(const std::vector<Coordinate>& coordinates) const;
    [[nodiscard]] WorldMetrics metrics() const;

    [[nodiscard]] Runtime fork() const { return *this; }
    [[nodiscard]] Runtime diagnostic_fork(
        const std::vector<ResearchStateEdit>& edits,
        bool authorize_diagnostic_intervention) const;
    void save_snapshot(const std::string& path) const;
    [[nodiscard]] static Runtime load_snapshot(const std::string& path);
    void restore_snapshot(const std::string& path);

    // Snapshot v2 carries opaque, inert product metadata so higher-level
    // organization/composition descriptors can survive a restart without
    // becoming executable code.  Keys and values never affect F_DEE.
    void set_snapshot_metadata(std::string key, std::string value);
    bool erase_snapshot_metadata(const std::string& key);
    [[nodiscard]] std::optional<std::string> snapshot_metadata(const std::string& key) const;
    [[nodiscard]] const std::map<std::string, std::string>& snapshot_metadata_entries() const noexcept {
        return snapshot_metadata_;
    }
    [[nodiscard]] std::uint32_t loaded_snapshot_version() const noexcept {
        return loaded_snapshot_version_;
    }
    [[nodiscard]] bool imported_legacy_snapshot() const noexcept {
        return loaded_snapshot_version_ == 1;
    }

    void set_protocol_phase(std::string phase) { protocol_phase_ = std::move(phase); }
    [[nodiscard]] const std::string& protocol_phase() const noexcept { return protocol_phase_; }

    // Explicit research exports. They return copies and cannot mutate the world.
    [[nodiscard]] std::vector<std::uint64_t> raw_copy() const { return raw_a_; }
    [[nodiscard]] std::vector<std::uint64_t> clock_copy() const { return clock_a_; }

private:
    struct Write {
        Coordinate coordinate;
        std::uint64_t raw{};
    };
    struct PendingEvent {
        std::uint64_t id{};
        EventKind kind{EventKind::Experience};
        std::uint64_t requested_tick{};
        std::uint64_t sequence{};
        std::vector<std::string> channels;
        std::vector<Write> writes;
    };

    Runtime() = default;
    EventReceipt schedule(EventKind kind, const std::vector<InputRequest>& inputs, std::uint64_t at_tick);
    void apply_events_at_boundary();
    [[nodiscard]] std::size_t index(Coordinate coordinate) const;
    void validate_invariants() const;

    int n_{};
    std::uint64_t tick_{};
    bool paused_{};
    std::uint64_t next_event_id_{1};
    std::uint64_t next_sequence_{};
    std::string protocol_phase_{"initialized"};
    std::vector<std::uint64_t> raw_a_;
    std::vector<std::uint64_t> raw_b_;
    std::vector<std::uint64_t> clock_a_;
    std::vector<std::uint64_t> clock_b_;
    std::map<std::string, ChannelSpec> channels_;
    std::multimap<std::uint64_t, PendingEvent> pending_;
    std::map<std::uint64_t, EventReceipt> receipts_;
    std::map<std::string, std::string> snapshot_metadata_;
    std::uint32_t loaded_snapshot_version_{2};
    v27::TickOptions execution_options_{};
    v27::TickInfo last_tick_info_{};
    static constexpr std::size_t kMaxPendingEvents = 4096;
    static constexpr std::size_t kMaxSnapshotMetadataEntries = 4096;
};

[[nodiscard]] const char* to_string(EventStatus status) noexcept;
[[nodiscard]] const char* to_string(EventKind kind) noexcept;

}  // namespace dee::thinking
