#include <dee_thinking/composition.hpp>

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <random>
#include <stdexcept>
#include <system_error>
#include <utility>

namespace {

dee::thinking::catalog::CompositionPlanner plan(
    const dee::thinking::catalog::OrganizationCatalog& catalog) {
    using namespace dee::thinking::catalog;
    CompositionPlanner value(34);
    value.add(catalog.instantiate(
        {"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    value.add(catalog.instantiate(
        {"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    value.connect({{"learner", "learned_relation"},
                   {"reader", "relation_input"}, "installed consumer route"});
    return value;
}

dee::thinking::catalog::CompositionPlanner core05_plan(
    const dee::thinking::catalog::OrganizationCatalog& catalog) {
    using namespace dee::thinking::catalog;
    CompositionPlanner value(17);
    value.add(catalog.instantiate({
        "temporal_phase_memory.core05.v1", "phase", {1, 6, 13},
        {{"distance", 3}, {"permutation_code", 2}, {"sign_mask", 1},
         {"control_mode", 1}, {"source_index", 3}}}));
    return value;
}

class TemporarySnapshot {
public:
    TemporarySnapshot() {
        std::random_device random;
        const auto base = std::filesystem::temp_directory_path();
        for (int attempt = 0; attempt < 32; ++attempt) {
            const auto token = (static_cast<std::uint64_t>(random()) << 32) ^
                               static_cast<std::uint64_t>(random());
            auto candidate = base / ("dee-thinking-installed-consumer-" +
                                     std::to_string(token));
            std::error_code error;
            if (std::filesystem::create_directory(candidate, error)) {
                directory_ = std::move(candidate);
                path_ = directory_ / "checkpoint.deetsnap";
                return;
            }
            if (error && error != std::make_error_code(std::errc::file_exists)) {
                throw std::filesystem::filesystem_error(
                    "cannot create installed-consumer temporary directory", candidate, error);
            }
        }
        throw std::runtime_error("cannot allocate a unique installed-consumer temporary directory");
    }

    TemporarySnapshot(const TemporarySnapshot&) = delete;
    TemporarySnapshot& operator=(const TemporarySnapshot&) = delete;

    ~TemporarySnapshot() {
        std::error_code ignored;
        std::filesystem::remove(path_, ignored);
        std::filesystem::remove(directory_, ignored);
    }

    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }

private:
    std::filesystem::path directory_;
    std::filesystem::path path_;
};

}  // namespace

int main() {
    using namespace dee::thinking;
    using namespace dee::thinking::catalog;
    try {
        OrganizationCatalog catalog;
        auto world = plan(catalog).build();
        world.runtime().set_execution_options({dee::v27::Backend::Lazy, 2});
        if (world.experience_batch(
                {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0).status !=
            EventStatus::Scheduled) return 2;
        world.runtime().run_until(6);
        // Later public input into the same persistent composed world.
        if (world.probe("reader", "query", 6, 13).status != EventStatus::Scheduled) return 3;
        world.runtime().run_until(11);
        const auto response = world.runtime().observe(world.landmarks().at("reader.response"));
        if (!response.record.occupied() || response.record.s_reg != 25) return 4;

        TemporarySnapshot snapshot;
        world.save_snapshot(snapshot.path().string());
        // Restore only from the installed public API and the snapshot recipe;
        // no caller-side reconstruction of the original planner is required.
        auto restored = ComposedWorld::load_snapshot(snapshot.path().string());
        if (restored.organizations().size() != 2 ||
            restored.connections().size() != 1 ||
            restored.connections().front().request.purpose != "installed consumer route" ||
            !restored.landmarks().contains("reader.response")) return 5;
        if (world.runtime().raw_copy() != restored.runtime().raw_copy() ||
            world.runtime().clock_copy() != restored.runtime().clock_copy()) return 6;
        world.runtime().set_execution_options({dee::v27::Backend::DenseSequential, 1});
        restored.runtime().set_execution_options({dee::v27::Backend::DenseParallel, 2});
        world.runtime().advance(2);
        restored.runtime().advance(2);
        if (world.runtime().raw_copy() != restored.runtime().raw_copy() ||
            world.runtime().clock_copy() != restored.runtime().clock_copy()) return 7;

        // The installed package also exposes the versioned CORE05 constructor.
        // Exercise its transient blocker, public footprint and self-contained
        // composition restore without relying on any in-tree header or fixture.
        auto phase = core05_plan(catalog).build();
        if (phase.organizations().front().descriptor().constructor_version != "1.0.0" ||
            phase.organizations().front().initial_footprint().size() != 5) return 8;
        phase.runtime().advance();
        if (phase.runtime().observe(phase.landmarks().at("phase.mouth3")).raw != 0 ||
            phase.runtime().observe(phase.landmarks().at("phase.source3")).record.semantic != 4) return 9;
        TemporarySnapshot phase_snapshot;
        phase.save_snapshot(phase_snapshot.path().string());
        auto phase_restored = ComposedWorld::load_snapshot(phase_snapshot.path().string());
        if (phase_restored.organizations().front().descriptor().id !=
                "temporal_phase_memory.core05.v1" ||
            phase_restored.runtime().raw_copy() != phase.runtime().raw_copy() ||
            phase_restored.runtime().clock_copy() != phase.runtime().clock_copy()) return 10;
        phase.runtime().advance(9);
        phase_restored.runtime().advance(9);
        if (phase_restored.runtime().raw_copy() != phase.runtime().raw_copy() ||
            phase_restored.runtime().clock_copy() != phase.runtime().clock_copy()) return 11;
        std::cout << "installed_find_package_consumer=true organizations=2 "
                     "later_input=true self_contained_restore=true "
                     "restore_backend_future_exact=true "
                     "core05_phase_memory_v1=true core05_restore_exact=true\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
