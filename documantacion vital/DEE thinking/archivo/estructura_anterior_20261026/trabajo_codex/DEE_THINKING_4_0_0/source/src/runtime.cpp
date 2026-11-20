#include "dee_thinking/runtime.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <set>
#include <stdexcept>
#include <utility>

#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#else
#include <unistd.h>
#endif

namespace dee::thinking {
namespace {

constexpr std::array<std::uint8_t, 8> kMagic{'D', 'E', 'E', 'T', 'S', 'N', 'P', '1'};
constexpr std::uint32_t kSnapshotVersion = 2;
constexpr std::uint32_t kOldestReadableSnapshotVersion = 1;
constexpr std::uint64_t kMaxSnapshotBytes = 2ULL * 1024ULL * 1024ULL * 1024ULL;
constexpr std::size_t kMaxSnapshotStringBytes = 1U << 20;
constexpr std::size_t kMaxSnapshotChannels = 65536;
constexpr std::size_t kMaxSnapshotEventFields = 65536;
constexpr std::size_t kMaxSnapshotReceipts = 1000000;

struct Writer {
    std::vector<std::uint8_t> data;
    void need(std::size_t count) const {
        if (data.size() > kMaxSnapshotBytes || count > kMaxSnapshotBytes - data.size()) {
            throw std::length_error("snapshot size limit exceeded");
        }
    }
    void u8(std::uint8_t v) { need(1); data.push_back(v); }
    void u32(std::uint32_t v) {
        need(4);
        for (int i = 0; i < 4; ++i) data.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
    }
    void u64(std::uint64_t v) {
        need(8);
        for (int i = 0; i < 8; ++i) data.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
    }
    void i32(int v) { u32(static_cast<std::uint32_t>(v)); }
    void string(const std::string& value) {
        if (value.size() > kMaxSnapshotStringBytes) {
            throw std::length_error("snapshot string limit exceeded");
        }
        u32(static_cast<std::uint32_t>(value.size()));
        need(value.size());
        data.insert(data.end(), value.begin(), value.end());
    }
};

struct Reader {
    const std::vector<std::uint8_t>& data;
    std::size_t pos{};
    void need(std::size_t count) const {
        if (pos > data.size() || count > data.size() - pos) {
            throw std::runtime_error("truncated snapshot");
        }
    }
    std::uint8_t u8() { need(1); return data[pos++]; }
    std::uint32_t u32() {
        need(4);
        std::uint32_t value = 0;
        for (int i = 0; i < 4; ++i) value |= static_cast<std::uint32_t>(data[pos++]) << (8 * i);
        return value;
    }
    std::uint64_t u64() {
        need(8);
        std::uint64_t value = 0;
        for (int i = 0; i < 8; ++i) value |= static_cast<std::uint64_t>(data[pos++]) << (8 * i);
        return value;
    }
    int i32() { return static_cast<int>(u32()); }
    std::string string() {
        const auto count = u32();
        if (count > kMaxSnapshotStringBytes) throw std::runtime_error("snapshot string limit exceeded");
        need(count);
        std::string value(reinterpret_cast<const char*>(data.data() + pos), count);
        pos += count;
        return value;
    }
};

std::uint64_t fnv1a64(const std::uint8_t* data, std::size_t count) {
    std::uint64_t hash = 1469598103934665603ULL;
    for (std::size_t i = 0; i < count; ++i) {
        hash ^= data[i];
        hash *= 1099511628211ULL;
    }
    return hash;
}

std::uint64_t process_id() noexcept {
#ifdef _WIN32
    return static_cast<std::uint64_t>(::GetCurrentProcessId());
#else
    return static_cast<std::uint64_t>(::getpid());
#endif
}

void write_snapshot_atomically(const std::filesystem::path& requested_path,
                               const std::vector<std::uint8_t>& bytes) {
    if (requested_path.empty()) throw std::invalid_argument("snapshot path is empty");
    const auto target = std::filesystem::absolute(requested_path);
    const auto parent = target.parent_path();
    if (parent.empty() || !std::filesystem::is_directory(parent)) {
        throw std::runtime_error("snapshot parent directory does not exist");
    }

    static std::atomic<std::uint64_t> serial{0};
    const auto nonce = serial.fetch_add(1, std::memory_order_relaxed);
    auto temporary = target;
    temporary += ".tmp." + std::to_string(process_id()) + "." + std::to_string(nonce);

    std::error_code cleanup_error;
    try {
        {
            std::ofstream stream(temporary, std::ios::binary | std::ios::trunc);
            if (!stream) throw std::runtime_error("cannot open snapshot temporary for writing");
            stream.write(reinterpret_cast<const char*>(bytes.data()),
                         static_cast<std::streamsize>(bytes.size()));
            stream.flush();
            if (!stream) throw std::runtime_error("failed writing snapshot temporary");
            stream.close();
            if (!stream) throw std::runtime_error("failed closing snapshot temporary");
        }

#ifdef _WIN32
        // The stream is closed before durability/replacement operations.  Flush
        // the same-volume temporary, then use the platform replacement primitive.
        HANDLE handle = ::CreateFileW(temporary.c_str(), GENERIC_WRITE, FILE_SHARE_READ,
                                      nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
        if (handle == INVALID_HANDLE_VALUE) {
            throw std::runtime_error("cannot reopen snapshot temporary for flush");
        }
        const BOOL flushed = ::FlushFileBuffers(handle);
        const DWORD flush_error = flushed ? ERROR_SUCCESS : ::GetLastError();
        ::CloseHandle(handle);
        if (!flushed) {
            throw std::runtime_error("failed flushing snapshot temporary: " +
                                     std::to_string(flush_error));
        }

        std::error_code exists_error;
        const bool target_exists = std::filesystem::exists(target, exists_error);
        if (exists_error) throw std::runtime_error("cannot inspect snapshot destination");
        BOOL replaced = FALSE;
        if (target_exists) {
            replaced = ::ReplaceFileW(target.c_str(), temporary.c_str(), nullptr,
                                      REPLACEFILE_WRITE_THROUGH, nullptr, nullptr);
        } else {
            replaced = ::MoveFileExW(temporary.c_str(), target.c_str(), MOVEFILE_WRITE_THROUGH);
        }
        if (!replaced) {
            throw std::runtime_error("atomic snapshot replacement failed: " +
                                     std::to_string(::GetLastError()));
        }
#else
        // POSIX rename on one filesystem replaces the directory entry atomically.
        // The temporary deliberately lives beside the target to keep this true.
        std::error_code rename_error;
        std::filesystem::rename(temporary, target, rename_error);
        if (rename_error) {
            throw std::runtime_error("atomic snapshot replacement failed: " +
                                     rename_error.message());
        }
#endif
    } catch (...) {
        std::filesystem::remove(temporary, cleanup_error);
        throw;
    }
}

std::size_t checked_total(int n) {
    if (n <= 0 || n > 512) throw std::invalid_argument("DEE dimension must be in [1,512]");
    const auto value = static_cast<std::size_t>(n);
    if (value > std::numeric_limits<std::size_t>::max() / value ||
        value * value > std::numeric_limits<std::size_t>::max() / value) {
        throw std::overflow_error("DEE world size overflow");
    }
    return value * value * value;
}

void write_coordinate(Writer& out, Coordinate q) {
    out.i32(q.x); out.i32(q.y); out.i32(q.z);
}

Coordinate read_coordinate(Reader& in) {
    return Coordinate{in.i32(), in.i32(), in.i32()};
}

}  // namespace

const char* to_string(EventStatus status) noexcept {
    switch (status) {
        case EventStatus::Scheduled: return "scheduled";
        case EventStatus::Applied: return "applied";
        case EventStatus::RejectedLate: return "rejected_late";
        case EventStatus::RejectedInvalid: return "rejected_invalid";
        case EventStatus::RejectedOccupied: return "rejected_occupied";
        case EventStatus::RejectedConflict: return "rejected_conflict";
        case EventStatus::RejectedQueueFull: return "rejected_queue_full";
    }
    return "unknown";
}

const char* to_string(EventKind kind) noexcept {
    return kind == EventKind::Probe ? "probe" : "experience";
}

Runtime::Runtime(int dimension) : n_(dimension) {
    const auto total = checked_total(n_);
    raw_a_.assign(total, 0);
    raw_b_.assign(total, 0);
    clock_a_.assign(total, 0);
    clock_b_.assign(total, 0);
}

Runtime Runtime::import_research_state(int dimension, std::uint64_t tick,
                                       std::vector<std::uint64_t> raw,
                                       std::vector<std::uint64_t> clock) {
    Runtime world(dimension);
    const auto total = checked_total(dimension);
    if (raw.size() != total || clock.size() != total) {
        throw std::invalid_argument("research state buffer size mismatch");
    }
    world.tick_ = tick;
    world.raw_a_ = std::move(raw);
    world.clock_a_ = std::move(clock);
    world.raw_b_ = world.raw_a_;
    world.clock_b_ = world.clock_a_;
    world.protocol_phase_ = "research_import";
    return world;
}

void Runtime::set_execution_options(v27::TickOptions options) {
    if (options.threads == 0 ||
        options.threads > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        throw std::invalid_argument("execution thread count must be in [1, INT_MAX]");
    }
    switch (options.backend) {
        case v27::Backend::DenseSequential:
        case v27::Backend::DenseParallel:
        case v27::Backend::Lazy:
            break;
        default:
            throw std::invalid_argument("execution backend value is invalid");
    }
    execution_options_ = options;
}

std::size_t Runtime::index(Coordinate q) const {
    return v27::linear_index(q.x, q.y, q.z, n_);
}

void Runtime::register_channel(ChannelSpec channel) {
    if (channel.name.empty()) throw std::invalid_argument("channel name is empty");
    (void)index(channel.injection_site);
    if (channel.direction.dx < -8 || channel.direction.dx > 7 ||
        channel.direction.dy < -8 || channel.direction.dy > 7 ||
        channel.direction.dz < -8 || channel.direction.dz > 7 || channel.semantic > 15) {
        throw std::invalid_argument("channel fields exceed packed representation");
    }
    if (!channels_.emplace(channel.name, std::move(channel)).second) {
        throw std::invalid_argument("duplicate channel name");
    }
}

std::vector<std::string> Runtime::channel_names() const {
    std::vector<std::string> names;
    names.reserve(channels_.size());
    for (const auto& [name, ignored] : channels_) {
        (void)ignored;
        names.push_back(name);
    }
    return names;
}

EventReceipt Runtime::experience(const std::string& channel, std::uint64_t at_tick,
                                 std::uint16_t s_reg) {
    return experience_batch({InputRequest{channel, s_reg}}, at_tick);
}

EventReceipt Runtime::experience_batch(const std::vector<InputRequest>& inputs,
                                       std::uint64_t at_tick) {
    return schedule(EventKind::Experience, inputs, at_tick);
}

EventReceipt Runtime::probe(const std::string& channel, std::uint64_t at_tick,
                            std::uint16_t s_reg) {
    return schedule(EventKind::Probe, {InputRequest{channel, s_reg}}, at_tick);
}

EventReceipt Runtime::schedule(EventKind kind, const std::vector<InputRequest>& inputs,
                               std::uint64_t at_tick) {
    if (next_event_id_ == std::numeric_limits<std::uint64_t>::max() ||
        next_sequence_ == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error("runtime event counter exhausted");
    }
    EventReceipt receipt;
    receipt.id = next_event_id_++;
    receipt.kind = kind;
    receipt.requested_tick = at_tick;
    for (const auto& input : inputs) receipt.channels.push_back(input.channel);
    auto reject = [&](EventStatus status, const std::string& why) {
        receipt.status = status;
        receipt.reason = why;
        receipts_[receipt.id] = receipt;
        return receipt;
    };
    if (at_tick < tick_) return reject(EventStatus::RejectedLate, "requested boundary precedes current tick");
    if (inputs.empty()) return reject(EventStatus::RejectedInvalid, "empty input batch");
    if (pending_.size() >= kMaxPendingEvents) return reject(EventStatus::RejectedQueueFull, "pending event limit reached");

    PendingEvent event;
    event.id = receipt.id;
    event.kind = kind;
    event.requested_tick = at_tick;
    event.sequence = next_sequence_++;
    event.channels = receipt.channels;
    std::set<std::size_t> local_targets;
    for (const auto& input : inputs) {
        const auto found = channels_.find(input.channel);
        if (found == channels_.end()) return reject(EventStatus::RejectedInvalid, "unknown channel: " + input.channel);
        const auto& channel = found->second;
        if ((kind == EventKind::Experience && !channel.allow_experience) ||
            (kind == EventKind::Probe && !channel.allow_probe)) {
            return reject(EventStatus::RejectedInvalid, "channel disallows requested event kind: " + input.channel);
        }
        const auto idx = index(channel.injection_site);
        if (!local_targets.insert(idx).second) {
            return reject(EventStatus::RejectedConflict, "batch writes the same register more than once");
        }
        event.writes.push_back(Write{
            channel.injection_site,
            v27::pack_record(channel.state, input.s_reg, channel.direction.dx,
                             channel.direction.dy, channel.direction.dz, channel.semantic)});
    }
    receipt.status = EventStatus::Scheduled;
    receipts_[receipt.id] = receipt;
    pending_.emplace(at_tick, std::move(event));
    return receipt;
}

std::optional<EventReceipt> Runtime::receipt(std::uint64_t id) const {
    const auto found = receipts_.find(id);
    if (found == receipts_.end()) return std::nullopt;
    return found->second;
}

std::vector<EventReceipt> Runtime::receipts() const {
    std::vector<EventReceipt> out;
    out.reserve(receipts_.size());
    for (const auto& [id, value] : receipts_) {
        (void)id;
        out.push_back(value);
    }
    return out;
}

void Runtime::apply_events_at_boundary() {
    const auto range = pending_.equal_range(tick_);
    if (range.first == range.second) return;
    std::vector<PendingEvent> events;
    for (auto it = range.first; it != range.second; ++it) events.push_back(it->second);
    std::sort(events.begin(), events.end(), [](const PendingEvent& a, const PendingEvent& b) {
        return a.sequence < b.sequence;
    });
    std::map<std::size_t, std::size_t> target_counts;
    for (const auto& event : events) {
        for (const auto& write : event.writes) ++target_counts[index(write.coordinate)];
    }
    for (const auto& event : events) {
        EventStatus status = EventStatus::Applied;
        std::string reason;
        for (const auto& write : event.writes) {
            const auto idx = index(write.coordinate);
            if (target_counts[idx] > 1) {
                status = EventStatus::RejectedConflict;
                reason = "simultaneous events target the same register";
                break;
            }
            if (raw_a_[idx] != 0) {
                status = EventStatus::RejectedOccupied;
                reason = "target register is not RAW-empty at application boundary";
                break;
            }
        }
        auto& receipt = receipts_.at(event.id);
        receipt.status = status;
        receipt.reason = reason;
        if (status == EventStatus::Applied) {
            for (const auto& write : event.writes) {
                raw_a_[index(write.coordinate)] = write.raw;
                // Intentionally preserve the existing full clock word.
            }
            receipt.effective_tick = tick_;
        }
    }
    pending_.erase(range.first, range.second);
}

v27::TickInfo Runtime::advance(std::uint64_t count) {
    if (paused_ && count != 0) throw std::logic_error("runtime is paused");
    if (count > std::numeric_limits<std::uint64_t>::max() - tick_) {
        throw std::overflow_error("runtime tick overflow");
    }
    v27::TickInfo total{};
    for (std::uint64_t step = 0; step < count; ++step) {
        apply_events_at_boundary();
        const auto info = v27::tick(raw_a_, raw_b_, clock_a_, clock_b_, n_, execution_options_);
        last_tick_info_ = info;
        total.overflows += info.overflows;
        total.genesis += info.genesis;
        total.evaluated += info.evaluated;
        total.active_raw = info.active_raw;
        total.total = info.total;
        total.requested_backend = info.requested_backend;
        total.used_backend = info.used_backend;
        total.requested_threads = info.requested_threads;
        total.used_threads = info.used_threads;
        total.fallback = total.fallback || info.fallback;
        total.preparation_ns += info.preparation_ns;
        total.evaluation_ns += info.evaluation_ns;
        total.postprocess_ns += info.postprocess_ns;
        total.total_ns += info.total_ns;
        ++tick_;
    }
    return total;
}

v27::TickInfo Runtime::run_until(std::uint64_t target_tick) {
    if (target_tick < tick_) throw std::invalid_argument("run_until target precedes current tick");
    return advance(target_tick - tick_);
}

Observation Runtime::observe(Coordinate coordinate) const {
    const auto idx = index(coordinate);
    const auto raw = raw_a_[idx];
    return Observation{tick_, coordinate, raw, clock_a_[idx], v27::decode_record(raw)};
}

std::vector<Observation> Runtime::observe_many(const std::vector<Coordinate>& coordinates) const {
    std::vector<Observation> out;
    out.reserve(coordinates.size());
    for (const auto q : coordinates) out.push_back(observe(q));
    return out;
}

WorldMetrics Runtime::metrics() const {
    WorldMetrics out;
    out.tick = tick_;
    for (const auto raw : raw_a_) {
        if (raw != 0) ++out.raw_support;
        const auto record = v27::decode_record(raw);
        if (record.occupied()) ++out.occupied;
        out.s_reg_sum += record.s_reg;
    }
    return out;
}

void Runtime::validate_invariants() const {
    const auto total = checked_total(n_);
    if (raw_a_.size() != total || raw_b_.size() != total ||
        clock_a_.size() != total || clock_b_.size() != total) {
        throw std::runtime_error("runtime buffer invariant violated");
    }
    if (channels_.size() > kMaxSnapshotChannels) {
        throw std::runtime_error("runtime channel limit exceeded");
    }
    for (const auto& [name, channel] : channels_) {
        if (name != channel.name) throw std::runtime_error("channel map invariant violated");
        (void)index(channel.injection_site);
    }
    if (pending_.size() > kMaxPendingEvents) {
        throw std::runtime_error("runtime pending-event limit exceeded");
    }
    if (receipts_.size() > kMaxSnapshotReceipts) {
        throw std::runtime_error("runtime receipt limit exceeded");
    }
    if (next_event_id_ == 0) throw std::runtime_error("runtime event counter invariant violated");

    std::set<std::uint64_t> pending_ids;
    std::set<std::uint64_t> pending_sequences;
    for (const auto& [boundary, event] : pending_) {
        if (boundary < tick_ || event.requested_tick != boundary || event.id == 0 ||
            event.sequence >= next_sequence_ || !pending_ids.insert(event.id).second ||
            !pending_sequences.insert(event.sequence).second) {
            throw std::runtime_error("pending-event identity invariant violated");
        }
        if (event.channels.empty() || event.channels.size() != event.writes.size() ||
            event.channels.size() > kMaxSnapshotEventFields) {
            throw std::runtime_error("pending-event payload invariant violated");
        }
        const auto receipt = receipts_.find(event.id);
        if (receipt == receipts_.end() || receipt->second.status != EventStatus::Scheduled) {
            throw std::runtime_error("pending event has no scheduled receipt");
        }
        std::set<std::size_t> targets;
        for (std::size_t i = 0; i < event.channels.size(); ++i) {
            const auto channel = channels_.find(event.channels[i]);
            if (channel == channels_.end()) {
                throw std::runtime_error("pending event names an unknown channel");
            }
            const auto& write = event.writes[i];
            const auto target = index(write.coordinate);
            if (!targets.insert(target).second || !(write.coordinate == channel->second.injection_site)) {
                throw std::runtime_error("pending-event write invariant violated");
            }
            const auto record = v27::decode_record(write.raw);
            if (v27::pack_record(channel->second.state, record.s_reg,
                                 channel->second.direction.dx, channel->second.direction.dy,
                                 channel->second.direction.dz, channel->second.semantic) != write.raw) {
                throw std::runtime_error("pending-event record invariant violated");
            }
            if ((event.kind == EventKind::Experience && !channel->second.allow_experience) ||
                (event.kind == EventKind::Probe && !channel->second.allow_probe)) {
                throw std::runtime_error("pending-event channel-kind invariant violated");
            }
        }
    }

    for (const auto& [id, receipt] : receipts_) {
        if (id == 0 || id != receipt.id || id >= next_event_id_ ||
            receipt.channels.size() > kMaxSnapshotEventFields) {
            throw std::runtime_error("event-receipt identity invariant violated");
        }
        const bool is_pending = pending_ids.contains(id);
        if ((receipt.status == EventStatus::Scheduled) != is_pending) {
            throw std::runtime_error("event-receipt lifecycle invariant violated");
        }
        if (is_pending) {
            const auto event = std::find_if(pending_.begin(), pending_.end(),
                                            [id](const auto& value) { return value.second.id == id; });
            if (event == pending_.end() || event->second.kind != receipt.kind ||
                event->second.requested_tick != receipt.requested_tick ||
                event->second.channels != receipt.channels || receipt.effective_tick.has_value()) {
                throw std::runtime_error("pending-event receipt invariant violated");
            }
        }
    }
    if (snapshot_metadata_.size() > kMaxSnapshotMetadataEntries) {
        throw std::runtime_error("snapshot metadata entry limit exceeded");
    }
}

void Runtime::set_snapshot_metadata(std::string key, std::string value) {
    if (key.empty() || key.size() > 1024) {
        throw std::invalid_argument("snapshot metadata key length invalid");
    }
    if (value.size() > kMaxSnapshotStringBytes) {
        throw std::invalid_argument("snapshot metadata value length invalid");
    }
    if (snapshot_metadata_.find(key) == snapshot_metadata_.end() &&
        snapshot_metadata_.size() >= kMaxSnapshotMetadataEntries) {
        throw std::length_error("snapshot metadata entry limit reached");
    }
    snapshot_metadata_[std::move(key)] = std::move(value);
}

bool Runtime::erase_snapshot_metadata(const std::string& key) {
    return snapshot_metadata_.erase(key) != 0;
}

std::optional<std::string> Runtime::snapshot_metadata(const std::string& key) const {
    const auto found = snapshot_metadata_.find(key);
    if (found == snapshot_metadata_.end()) return std::nullopt;
    return found->second;
}

Runtime Runtime::diagnostic_fork(
    const std::vector<ResearchStateEdit>& edits,
    bool authorize_diagnostic_intervention) const {
    if (!authorize_diagnostic_intervention) {
        throw std::invalid_argument(
            "diagnostic fork requires explicit intervention authorization");
    }
    Runtime branch = *this;
    std::set<std::size_t> touched;
    for (const auto& edit : edits) {
        if (!edit.raw.has_value() && !edit.clock.has_value()) {
            throw std::invalid_argument("diagnostic edit changes no field");
        }
        const auto i = branch.index(edit.coordinate);
        if (!touched.insert(i).second) {
            throw std::invalid_argument("duplicate diagnostic edit coordinate");
        }
        if (edit.raw.has_value()) {
            branch.raw_a_[i] = *edit.raw;
            branch.raw_b_[i] = *edit.raw;
        }
        if (edit.clock.has_value()) {
            branch.clock_a_[i] = *edit.clock;
            branch.clock_b_[i] = *edit.clock;
        }
    }
    branch.set_snapshot_metadata("dee_thinking.diagnostic_fork", "true");
    branch.set_snapshot_metadata(
        "dee_thinking.diagnostic_edit_count", std::to_string(edits.size()));
    branch.validate_invariants();
    return branch;
}

void Runtime::save_snapshot(const std::string& path) const {
    validate_invariants();
    Writer out;
    out.data.insert(out.data.end(), kMagic.begin(), kMagic.end());
    out.u32(kSnapshotVersion);
    out.u32(static_cast<std::uint32_t>(n_));
    out.u64(tick_);
    out.u8(paused_ ? 1 : 0);
    out.u64(next_event_id_);
    out.u64(next_sequence_);
    out.string(protocol_phase_);
    out.u64(static_cast<std::uint64_t>(raw_a_.size()));
    for (const auto value : raw_a_) out.u64(value);
    for (const auto value : clock_a_) out.u64(value);
    out.u32(static_cast<std::uint32_t>(channels_.size()));
    for (const auto& [name, channel] : channels_) {
        out.string(name);
        write_coordinate(out, channel.injection_site);
        out.u32(channel.state);
        out.i32(channel.direction.dx); out.i32(channel.direction.dy); out.i32(channel.direction.dz);
        out.u8(channel.semantic);
        out.u8(channel.allow_experience ? 1 : 0);
        out.u8(channel.allow_probe ? 1 : 0);
    }
    out.u32(static_cast<std::uint32_t>(pending_.size()));
    for (const auto& [boundary, event] : pending_) {
        out.u64(boundary); out.u64(event.id); out.u8(static_cast<std::uint8_t>(event.kind));
        out.u64(event.requested_tick); out.u64(event.sequence);
        out.u32(static_cast<std::uint32_t>(event.channels.size()));
        for (const auto& name : event.channels) out.string(name);
        out.u32(static_cast<std::uint32_t>(event.writes.size()));
        for (const auto& write : event.writes) { write_coordinate(out, write.coordinate); out.u64(write.raw); }
    }
    out.u32(static_cast<std::uint32_t>(receipts_.size()));
    for (const auto& [id, receipt] : receipts_) {
        out.u64(id); out.u8(static_cast<std::uint8_t>(receipt.kind));
        out.u8(static_cast<std::uint8_t>(receipt.status)); out.u64(receipt.requested_tick);
        out.u8(receipt.effective_tick.has_value() ? 1 : 0);
        if (receipt.effective_tick) out.u64(*receipt.effective_tick);
        out.u32(static_cast<std::uint32_t>(receipt.channels.size()));
        for (const auto& name : receipt.channels) out.string(name);
        out.string(receipt.reason);
    }
    out.u8(static_cast<std::uint8_t>(execution_options_.backend));
    out.u64(static_cast<std::uint64_t>(execution_options_.threads));
    out.u32(static_cast<std::uint32_t>(snapshot_metadata_.size()));
    for (const auto& [key, value] : snapshot_metadata_) {
        out.string(key);
        out.string(value);
    }
    const auto checksum = fnv1a64(out.data.data(), out.data.size());
    out.u64(checksum);
    write_snapshot_atomically(path, out.data);
}

Runtime Runtime::load_snapshot(const std::string& path) {
    std::ifstream stream(path, std::ios::binary | std::ios::ate);
    if (!stream) throw std::runtime_error("cannot open snapshot");
    const auto end = stream.tellg();
    if (end < 0 || static_cast<std::uint64_t>(end) > kMaxSnapshotBytes) {
        throw std::runtime_error("snapshot size invalid");
    }
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(end));
    stream.seekg(0);
    stream.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    if (!stream || bytes.size() < kMagic.size() + 12) throw std::runtime_error("truncated snapshot");
    std::uint64_t stored_checksum = 0;
    for (int i = 0; i < 8; ++i) stored_checksum |= static_cast<std::uint64_t>(bytes[bytes.size() - 8 + i]) << (8 * i);
    if (fnv1a64(bytes.data(), bytes.size() - 8) != stored_checksum) {
        throw std::runtime_error("snapshot checksum mismatch");
    }
    bytes.resize(bytes.size() - 8);
    Reader in{bytes};
    for (const auto expected : kMagic) if (in.u8() != expected) throw std::runtime_error("snapshot magic mismatch");
    const auto snapshot_version = in.u32();
    if (snapshot_version < kOldestReadableSnapshotVersion || snapshot_version > kSnapshotVersion) {
        throw std::runtime_error("unsupported snapshot version");
    }
    const auto n_raw = in.u32();
    if (n_raw > static_cast<std::uint32_t>(std::numeric_limits<int>::max())) throw std::runtime_error("snapshot dimension overflow");
    const auto total = checked_total(static_cast<int>(n_raw));
    const std::uint64_t minimum_non_array_bytes = snapshot_version >= 2 ? 62ULL : 49ULL;
    const auto remaining = static_cast<std::uint64_t>(bytes.size() - in.pos);
    if (remaining < minimum_non_array_bytes ||
        total > (remaining - minimum_non_array_bytes) / (2ULL * sizeof(std::uint64_t))) {
        throw std::runtime_error("snapshot payload is too small for its dimension");
    }
    Runtime world(static_cast<int>(n_raw));
    world.loaded_snapshot_version_ = snapshot_version;
    world.tick_ = in.u64();
    const auto paused_value = in.u8();
    if (paused_value > 1) throw std::runtime_error("snapshot paused flag invalid");
    world.paused_ = paused_value != 0;
    world.next_event_id_ = in.u64();
    world.next_sequence_ = in.u64();
    world.protocol_phase_ = in.string();
    const auto count = in.u64();
    if (count != world.raw_a_.size()) throw std::runtime_error("snapshot array dimension mismatch");
    for (auto& value : world.raw_a_) value = in.u64();
    for (auto& value : world.clock_a_) value = in.u64();
    world.raw_b_ = world.raw_a_;
    world.clock_b_ = world.clock_a_;
    const auto channel_count = in.u32();
    if (channel_count > kMaxSnapshotChannels) throw std::runtime_error("snapshot channel count invalid");
    for (std::uint32_t i = 0; i < channel_count; ++i) {
        ChannelSpec channel;
        channel.name = in.string(); channel.injection_site = read_coordinate(in);
        channel.state = in.u32();
        channel.direction = Direction{in.i32(), in.i32(), in.i32()};
        channel.semantic = in.u8();
        const auto allow_experience = in.u8();
        const auto allow_probe = in.u8();
        if (allow_experience > 1 || allow_probe > 1) {
            throw std::runtime_error("snapshot channel flag invalid");
        }
        channel.allow_experience = allow_experience != 0;
        channel.allow_probe = allow_probe != 0;
        world.register_channel(std::move(channel));
    }
    const auto pending_count = in.u32();
    if (pending_count > kMaxPendingEvents) throw std::runtime_error("snapshot pending-event count invalid");
    for (std::uint32_t i = 0; i < pending_count; ++i) {
        const auto boundary = in.u64();
        if (boundary < world.tick_) throw std::runtime_error("snapshot contains late pending event");
        PendingEvent event;
        event.id = in.u64();
        const auto kind_value = in.u8();
        if (kind_value < static_cast<std::uint8_t>(EventKind::Experience) ||
            kind_value > static_cast<std::uint8_t>(EventKind::Probe)) {
            throw std::runtime_error("snapshot event kind invalid");
        }
        event.kind = static_cast<EventKind>(kind_value);
        event.requested_tick = in.u64(); event.sequence = in.u64();
        if (event.requested_tick != boundary) throw std::runtime_error("snapshot event boundary mismatch");
        const auto names = in.u32();
        if (names > kMaxSnapshotEventFields) throw std::runtime_error("snapshot event channel count invalid");
        for (std::uint32_t j = 0; j < names; ++j) event.channels.push_back(in.string());
        const auto writes = in.u32();
        if (writes > kMaxSnapshotEventFields) throw std::runtime_error("snapshot event write count invalid");
        for (std::uint32_t j = 0; j < writes; ++j) {
            const auto coordinate = read_coordinate(in);
            (void)world.index(coordinate);
            event.writes.push_back(Write{coordinate, in.u64()});
        }
        if (event.writes.empty() || event.writes.size() != event.channels.size()) {
            throw std::runtime_error("snapshot event payload invalid");
        }
        world.pending_.emplace(boundary, std::move(event));
    }
    const auto receipt_count = in.u32();
    if (receipt_count > kMaxSnapshotReceipts) throw std::runtime_error("snapshot receipt count invalid");
    for (std::uint32_t i = 0; i < receipt_count; ++i) {
        EventReceipt receipt;
        receipt.id = in.u64();
        const auto kind_value = in.u8();
        const auto status_value = in.u8();
        if (kind_value < static_cast<std::uint8_t>(EventKind::Experience) ||
            kind_value > static_cast<std::uint8_t>(EventKind::Probe) ||
            status_value < static_cast<std::uint8_t>(EventStatus::Scheduled) ||
            status_value > static_cast<std::uint8_t>(EventStatus::RejectedQueueFull)) {
            throw std::runtime_error("snapshot receipt enum invalid");
        }
        receipt.kind = static_cast<EventKind>(kind_value);
        receipt.status = static_cast<EventStatus>(status_value);
        receipt.requested_tick = in.u64();
        const auto has_effective_tick = in.u8();
        if (has_effective_tick > 1) throw std::runtime_error("snapshot receipt flag invalid");
        if (has_effective_tick != 0) receipt.effective_tick = in.u64();
        const auto names = in.u32();
        if (names > kMaxSnapshotEventFields) throw std::runtime_error("snapshot receipt channel count invalid");
        for (std::uint32_t j = 0; j < names; ++j) receipt.channels.push_back(in.string());
        receipt.reason = in.string();
        if (!world.receipts_.emplace(receipt.id, std::move(receipt)).second) {
            throw std::runtime_error("snapshot duplicate receipt id");
        }
    }
    if (snapshot_version >= 2) {
        const auto backend_value = in.u8();
        const auto thread_count = in.u64();
        if (backend_value > static_cast<std::uint8_t>(v27::Backend::Lazy) ||
            thread_count == 0 ||
            thread_count > static_cast<std::uint64_t>(std::numeric_limits<int>::max()) ||
            thread_count > std::numeric_limits<std::size_t>::max()) {
            throw std::runtime_error("snapshot execution configuration invalid");
        }
        world.set_execution_options(v27::TickOptions{
            static_cast<v27::Backend>(backend_value), static_cast<std::size_t>(thread_count)});
        const auto metadata_count = in.u32();
        if (metadata_count > kMaxSnapshotMetadataEntries) {
            throw std::runtime_error("snapshot metadata count invalid");
        }
        for (std::uint32_t i = 0; i < metadata_count; ++i) {
            auto key = in.string();
            auto value = in.string();
            if (key.empty() || key.size() > 1024 || !world.snapshot_metadata_.emplace(
                    std::move(key), std::move(value)).second) {
                throw std::runtime_error("snapshot metadata key invalid or duplicated");
            }
        }
    }
    if (in.pos != bytes.size()) throw std::runtime_error("snapshot trailing payload");
    world.validate_invariants();
    return world;
}

void Runtime::restore_snapshot(const std::string& path) {
    Runtime replacement = load_snapshot(path);
    *this = std::move(replacement);
}

}  // namespace dee::thinking
