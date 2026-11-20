#include "dee_thinking/runtime.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <fstream>
#include <limits>
#include <set>
#include <stdexcept>
#include <utility>

namespace dee::thinking {
namespace {

constexpr std::array<std::uint8_t, 8> kMagic{'D', 'E', 'E', 'T', 'S', 'N', 'P', '1'};
constexpr std::uint32_t kSnapshotVersion = 1;
constexpr std::uint64_t kMaxSnapshotBytes = 2ULL * 1024ULL * 1024ULL * 1024ULL;

struct Writer {
    std::vector<std::uint8_t> data;
    void u8(std::uint8_t v) { data.push_back(v); }
    void u32(std::uint32_t v) {
        for (int i = 0; i < 4; ++i) data.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
    }
    void u64(std::uint64_t v) {
        for (int i = 0; i < 8; ++i) data.push_back(static_cast<std::uint8_t>(v >> (8 * i)));
    }
    void i32(int v) { u32(static_cast<std::uint32_t>(v)); }
    void string(const std::string& value) {
        if (value.size() > std::numeric_limits<std::uint32_t>::max()) {
            throw std::length_error("snapshot string too long");
        }
        u32(static_cast<std::uint32_t>(value.size()));
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
        if (count > (1U << 20)) throw std::runtime_error("snapshot string limit exceeded");
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
    v27::TickInfo total{};
    for (std::uint64_t step = 0; step < count; ++step) {
        apply_events_at_boundary();
        const auto info = v27::tick(raw_a_, raw_b_, clock_a_, clock_b_, n_);
        total.overflows += info.overflows;
        total.genesis += info.genesis;
        total.evaluated += info.evaluated;
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
    for (const auto& [name, channel] : channels_) {
        if (name != channel.name) throw std::runtime_error("channel map invariant violated");
        (void)index(channel.injection_site);
    }
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
    const auto checksum = fnv1a64(out.data.data(), out.data.size());
    out.u64(checksum);
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    if (!stream) throw std::runtime_error("cannot open snapshot for writing");
    stream.write(reinterpret_cast<const char*>(out.data.data()), static_cast<std::streamsize>(out.data.size()));
    if (!stream) throw std::runtime_error("failed writing snapshot");
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
    if (in.u32() != kSnapshotVersion) throw std::runtime_error("unsupported snapshot version");
    const auto n_raw = in.u32();
    if (n_raw > static_cast<std::uint32_t>(std::numeric_limits<int>::max())) throw std::runtime_error("snapshot dimension overflow");
    Runtime world(static_cast<int>(n_raw));
    world.tick_ = in.u64();
    world.paused_ = in.u8() != 0;
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
    if (channel_count > 65536) throw std::runtime_error("snapshot channel count invalid");
    for (std::uint32_t i = 0; i < channel_count; ++i) {
        ChannelSpec channel;
        channel.name = in.string(); channel.injection_site = read_coordinate(in);
        channel.state = in.u32();
        channel.direction = Direction{in.i32(), in.i32(), in.i32()};
        channel.semantic = in.u8();
        channel.allow_experience = in.u8() != 0;
        channel.allow_probe = in.u8() != 0;
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
        if (names > 65536) throw std::runtime_error("snapshot event channel count invalid");
        for (std::uint32_t j = 0; j < names; ++j) event.channels.push_back(in.string());
        const auto writes = in.u32();
        if (writes > 65536) throw std::runtime_error("snapshot event write count invalid");
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
    if (receipt_count > 1000000) throw std::runtime_error("snapshot receipt count invalid");
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
        if (in.u8() != 0) receipt.effective_tick = in.u64();
        const auto names = in.u32();
        if (names > 65536) throw std::runtime_error("snapshot receipt channel count invalid");
        for (std::uint32_t j = 0; j < names; ++j) receipt.channels.push_back(in.string());
        receipt.reason = in.string();
        world.receipts_.emplace(receipt.id, std::move(receipt));
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
