#include "dee_thinking/runtime.hpp"
#include "test_support.hpp"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#endif

using dee::thinking::ChannelSpec;
using dee::thinking::Coordinate;
using dee::thinking::Direction;
using dee::thinking::EventStatus;
using dee::thinking::Runtime;

namespace {

ChannelSpec channel(std::string name, Coordinate site) {
    return ChannelSpec{std::move(name), site, 1, Direction{1, 0, 0}, 1, true, true};
}

void same_physics(dee::thinking::test::Suite& suite, const Runtime& a, const Runtime& b) {
    DEE_CHECK_EQ(suite, a.dimension(), b.dimension());
    DEE_CHECK_EQ(suite, a.current_tick(), b.current_tick());
    DEE_CHECK_EQ(suite, a.raw_copy(), b.raw_copy());
    DEE_CHECK_EQ(suite, a.clock_copy(), b.clock_copy());
    DEE_CHECK_EQ(suite, a.receipts().size(), b.receipts().size());
}

std::vector<std::uint8_t> read_bytes(const std::filesystem::path& path) {
    std::ifstream stream(path, std::ios::binary | std::ios::ate);
    if (!stream) throw std::runtime_error("cannot read test snapshot");
    const auto size = stream.tellg();
    if (size < 0) throw std::runtime_error("cannot size test snapshot");
    std::vector<std::uint8_t> bytes(static_cast<std::size_t>(size));
    stream.seekg(0);
    stream.read(reinterpret_cast<char*>(bytes.data()), static_cast<std::streamsize>(bytes.size()));
    if (!stream) throw std::runtime_error("cannot finish reading test snapshot");
    return bytes;
}

void write_u64(std::vector<std::uint8_t>& bytes, std::size_t offset, std::uint64_t value) {
    if (offset > bytes.size() || 8 > bytes.size() - offset) {
        throw std::runtime_error("test snapshot offset is invalid");
    }
    for (int i = 0; i < 8; ++i) {
        bytes[offset + static_cast<std::size_t>(i)] =
            static_cast<std::uint8_t>(value >> (8 * i));
    }
}

void write_snapshot_with_checksum(const std::filesystem::path& path,
                                  std::vector<std::uint8_t> bytes) {
    if (bytes.size() < 8) throw std::runtime_error("test snapshot is truncated");
    std::uint64_t checksum = 1469598103934665603ULL;
    for (std::size_t i = 0; i < bytes.size() - 8; ++i) {
        checksum ^= bytes[i];
        checksum *= 1099511628211ULL;
    }
    write_u64(bytes, bytes.size() - 8, checksum);
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    stream.write(reinterpret_cast<const char*>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    if (!stream) throw std::runtime_error("cannot write test snapshot");
}

}  // namespace

int main(int argc, char** argv) {
    dee::thinking::test::Suite suite("integration_persistence_tests");
    const auto temporary = std::filesystem::temp_directory_path() / "dee_thinking_entrega02_persistence";
    std::error_code ec;
    std::filesystem::create_directories(temporary, ec);
    const auto snapshot = temporary / "metadata_v2.deetsnap";
    const auto replacement = temporary / "replacement.deetsnap";
    const auto malformed_source = temporary / "malformed_source.deetsnap";
    const auto invalid_counter = temporary / "invalid_counter.deetsnap";
    const auto invalid_pending_link = temporary / "invalid_pending_link.deetsnap";

    Runtime original(9);
    original.register_channel(channel("future", {2, 2, 2}));
    const auto pending = original.experience("future", 4, 23);
    DEE_CHECK_EQ(suite, pending.status, EventStatus::Scheduled);
    original.set_protocol_phase("composition_checkpoint");
    original.set_snapshot_metadata("dee.organization.ids", "history.relative@1;recurrence@1");
    original.set_snapshot_metadata("dee.composition.contract", "composition-B-v1");
    original.set_snapshot_metadata("dee.execution.backend", "lazy:4");
    original.set_execution_options({dee::v27::Backend::Lazy, 4});
    original.advance(1);
    original.save_snapshot(snapshot.string());

    auto restored = Runtime::load_snapshot(snapshot.string());
    DEE_CHECK_EQ(suite, restored.loaded_snapshot_version(), 2U);
    DEE_CHECK(suite, !restored.imported_legacy_snapshot());
    DEE_CHECK_EQ(suite, restored.execution_options().backend, dee::v27::Backend::Lazy);
    DEE_CHECK_EQ(suite, restored.execution_options().threads, 4ULL);
    DEE_CHECK_EQ(suite, restored.snapshot_metadata("dee.composition.contract").value(),
                 std::string("composition-B-v1"));
    same_physics(suite, original, restored);
    auto switched_backend = restored.fork();
    switched_backend.set_execution_options({dee::v27::Backend::DenseParallel, 2});
    original.advance(7);
    restored.advance(7);
    switched_backend.advance(7);
    same_physics(suite, original, restored);
    same_physics(suite, original, switched_backend);
    DEE_CHECK_EQ(suite, switched_backend.last_tick_info().requested_backend,
                 dee::v27::Backend::DenseParallel);

    // Replacing an existing valid destination must publish the complete newer
    // snapshot, not append to or partly overwrite the old one.
    Runtime first(7);
    first.set_protocol_phase("first");
    first.save_snapshot(replacement.string());
    Runtime second(7);
    second.set_protocol_phase("second");
    second.advance(2);
    second.save_snapshot(replacement.string());
    const auto replaced = Runtime::load_snapshot(replacement.string());
    DEE_CHECK_EQ(suite, replaced.protocol_phase(), std::string("second"));
    DEE_CHECK_EQ(suite, replaced.current_tick(), 2ULL);

    // Every snapshot emitted by the writer must satisfy the reader's bounds.
    // A rejected save is assembled before publication and preserves the valid
    // destination that was already present.
    Runtime oversized_string(1);
    oversized_string.set_protocol_phase(std::string((1U << 20) + 1U, 'x'));
    DEE_CHECK_THROWS(suite, oversized_string.save_snapshot(replacement.string()));
    DEE_CHECK_EQ(suite, Runtime::load_snapshot(replacement.string()).protocol_phase(),
                 std::string("second"));

    // A checksummed file is still rejected when its event counters or the
    // pending-event/receipt relationship cannot be produced by Runtime.
    Runtime malformed(1);
    malformed.register_channel(channel("x", {0, 0, 0}));
    DEE_CHECK_EQ(suite, malformed.experience("x", 2, 7).status, EventStatus::Scheduled);
    malformed.save_snapshot(malformed_source.string());
    const auto valid_malformed_bytes = read_bytes(malformed_source);
    {
        auto bytes = valid_malformed_bytes;
        // Header offset 25 is next_event_id in both v1 and v2.
        write_u64(bytes, 25, 1);
        write_snapshot_with_checksum(invalid_counter, std::move(bytes));
        DEE_CHECK_THROWS(suite, Runtime::load_snapshot(invalid_counter.string()));
    }
    {
        auto bytes = valid_malformed_bytes;
        // This deliberately minimal snapshot has one cell, protocol phase
        // "initialized", and one one-byte channel. Its pending event id starts
        // at offset 132. Keep the counter ahead while orphaning receipt id 1.
        write_u64(bytes, 25, 3);
        write_u64(bytes, 132, 2);
        write_snapshot_with_checksum(invalid_pending_link, std::move(bytes));
        DEE_CHECK_THROWS(suite, Runtime::load_snapshot(invalid_pending_link.string()));
    }

#ifdef _WIN32
    // Hold the destination without FILE_SHARE_DELETE. ReplaceFileW must fail,
    // and the previously valid bytes must remain readable after releasing it.
    const auto before_raw = replaced.raw_copy();
    const auto before_clock = replaced.clock_copy();
    HANDLE lock = ::CreateFileW(replacement.c_str(), GENERIC_READ, FILE_SHARE_READ,
                                nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    DEE_CHECK(suite, lock != INVALID_HANDLE_VALUE);
    Runtime attempted(7);
    attempted.set_protocol_phase("must_not_publish");
    DEE_CHECK_THROWS(suite, attempted.save_snapshot(replacement.string()));
    if (lock != INVALID_HANDLE_VALUE) ::CloseHandle(lock);
    const auto preserved = Runtime::load_snapshot(replacement.string());
    DEE_CHECK_EQ(suite, preserved.protocol_phase(), std::string("second"));
    DEE_CHECK_EQ(suite, preserved.raw_copy(), before_raw);
    DEE_CHECK_EQ(suite, preserved.clock_copy(), before_clock);
#endif

    // This file is generated by the released Entrega 01 library and contains
    // a pending event. Entrega 02 must import it without inventing metadata and
    // preserve both the immediate state and its future.
    DEE_CHECK(suite, argc == 2);
    if (argc == 2) {
        const std::filesystem::path legacy_path(argv[1]);
        DEE_CHECK(suite, std::filesystem::is_regular_file(legacy_path));
        auto legacy = Runtime::load_snapshot(legacy_path.string());
        DEE_CHECK_EQ(suite, legacy.loaded_snapshot_version(), 1U);
        DEE_CHECK(suite, legacy.imported_legacy_snapshot());
        DEE_CHECK(suite, legacy.snapshot_metadata_entries().empty());
        DEE_CHECK_EQ(suite, legacy.execution_options().backend,
                     dee::v27::Backend::DenseSequential);
        DEE_CHECK_EQ(suite, legacy.execution_options().threads, 1ULL);
        DEE_CHECK_EQ(suite, legacy.current_tick(), 1ULL);
        const auto legacy_receipts = legacy.receipts();
        DEE_CHECK_EQ(suite, legacy_receipts.size(), 2ULL);
        const auto pending_receipt = std::find_if(
            legacy_receipts.begin(), legacy_receipts.end(),
            [](const auto& value) { return value.status == EventStatus::Scheduled; });
        DEE_CHECK(suite, pending_receipt != legacy_receipts.end());
        DEE_CHECK_EQ(suite, pending_receipt->requested_tick, 5ULL);
        auto branch = legacy.fork();
        legacy.advance(6);
        branch.advance(2);
        branch.advance(4);
        same_physics(suite, legacy, branch);
        const auto completed_receipts = legacy.receipts();
        const auto completed = std::find_if(
            completed_receipts.begin(), completed_receipts.end(),
            [id = pending_receipt->id](const auto& value) { return value.id == id; });
        DEE_CHECK(suite, completed != completed_receipts.end());
        DEE_CHECK_EQ(suite, completed->status, EventStatus::Applied);
        DEE_CHECK_EQ(suite, completed->effective_tick.value(), 5ULL);
    }

    std::filesystem::remove(snapshot, ec);
    std::filesystem::remove(replacement, ec);
    std::filesystem::remove(malformed_source, ec);
    std::filesystem::remove(invalid_counter, ec);
    std::filesystem::remove(invalid_pending_link, ec);
    std::filesystem::remove(temporary, ec);
    return suite.finish();
}
