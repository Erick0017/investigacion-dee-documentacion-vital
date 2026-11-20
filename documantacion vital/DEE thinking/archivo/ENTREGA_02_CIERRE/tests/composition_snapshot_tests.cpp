#include "dee_thinking/composition.hpp"
#include "test_support.hpp"

#include <cstdint>
#include <filesystem>
#include <random>
#include <stdexcept>
#include <string>
#include <system_error>
#include <utility>

using namespace dee::thinking;
using namespace dee::thinking::catalog;

namespace {

CompositionPlanner plan(const OrganizationCatalog& catalog) {
    CompositionPlanner value(34);
    value.add(catalog.instantiate(
        {"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    value.add(catalog.instantiate(
        {"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    value.connect({{"learner", "learned_relation"},
                   {"reader", "relation_input"},
                   "snapshot reconstructs this purpose too"});
    return value;
}

class TemporaryDirectory {
public:
    TemporaryDirectory() {
        std::random_device random;
        const auto base = std::filesystem::temp_directory_path();
        for (int attempt = 0; attempt < 32; ++attempt) {
            const auto token = (static_cast<std::uint64_t>(random()) << 32) ^
                               static_cast<std::uint64_t>(random());
            auto candidate = base / ("dee-thinking-composition-snapshot-" +
                                     std::to_string(token));
            std::error_code error;
            if (std::filesystem::create_directory(candidate, error)) {
                path_ = std::move(candidate);
                return;
            }
            if (error && error != std::make_error_code(std::errc::file_exists)) {
                throw std::filesystem::filesystem_error(
                    "cannot create composition test directory", candidate, error);
            }
        }
        throw std::runtime_error("cannot allocate composition test directory");
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] std::filesystem::path file(const std::string& name) const {
        return path_ / name;
    }

private:
    std::filesystem::path path_;
};

}  // namespace

int main(int argc, char** argv) {
    dee::thinking::test::Suite suite("composition_snapshot_tests");
    TemporaryDirectory temporary;
    OrganizationCatalog catalog;

    auto original = plan(catalog).build();
    original.runtime().set_execution_options({dee::v27::Backend::Lazy, 2});
    DEE_CHECK_EQ(suite, original.experience_batch(
        {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0).status,
                 EventStatus::Scheduled);
    original.runtime().run_until(6);
    DEE_CHECK_EQ(suite, original.probe("reader", "query", 6, 13).status,
                 EventStatus::Scheduled);

    const auto snapshot = temporary.file("composition.deetsnap");
    original.save_snapshot(snapshot.string());

    // No caller-side planner is needed: catalog ids, exact constructor
    // versions, anchors, validated parameters, connections and their purpose
    // are all reconstructed from inert v2 metadata.
    auto restored = ComposedWorld::load_snapshot(snapshot.string(), catalog);
    DEE_CHECK_EQ(suite, restored.runtime().loaded_snapshot_version(), 2U);
    DEE_CHECK_EQ(suite, restored.organizations().size(), std::size_t{2});
    DEE_CHECK_EQ(suite, restored.connections().size(), std::size_t{1});
    DEE_CHECK_EQ(suite, restored.connections().front().request.purpose,
                 std::string("snapshot reconstructs this purpose too"));
    DEE_CHECK_EQ(suite, restored.manifest_json(), original.manifest_json());
    DEE_CHECK_EQ(suite, restored.landmarks(), original.landmarks());
    DEE_CHECK_EQ(suite, restored.runtime().raw_copy(), original.runtime().raw_copy());
    DEE_CHECK_EQ(suite, restored.runtime().clock_copy(), original.runtime().clock_copy());
    DEE_CHECK_EQ(suite, restored.runtime().execution_options().backend,
                 dee::v27::Backend::Lazy);
    DEE_CHECK_EQ(suite, restored.runtime().execution_options().threads, std::size_t{2});

    // The convenience overload constructs the public built-in catalog.
    auto implicit_catalog = ComposedWorld::load_snapshot(snapshot.string());
    DEE_CHECK_EQ(suite, implicit_catalog.connections().front().request.purpose,
                 restored.connections().front().request.purpose);

    original.runtime().run_until(11);
    restored.runtime().run_until(11);
    DEE_CHECK_EQ(suite, restored.runtime().raw_copy(), original.runtime().raw_copy());
    DEE_CHECK_EQ(suite, restored.runtime().clock_copy(), original.runtime().clock_copy());
    DEE_CHECK_EQ(suite,
                 restored.runtime().observe(restored.landmarks().at("reader.response")).record.s_reg,
                 std::uint16_t{25});

    // A valid Runtime payload is insufficient when its composition metadata is
    // absent, uses an unknown schema, or disagrees with the rebuilt manifest.
    {
        auto invalid = Runtime::load_snapshot(snapshot.string());
        invalid.set_snapshot_metadata("dee_thinking.composition_manifest", "{}");
        const auto path = temporary.file("bad-manifest.deetsnap");
        invalid.save_snapshot(path.string());
        DEE_CHECK_THROWS(suite, ComposedWorld::load_snapshot(path.string(), catalog));
    }
    {
        auto invalid = Runtime::load_snapshot(snapshot.string());
        invalid.set_snapshot_metadata("dee_thinking.composition_recipe_schema", "999");
        const auto path = temporary.file("bad-schema.deetsnap");
        invalid.save_snapshot(path.string());
        DEE_CHECK_THROWS(suite, ComposedWorld::load_snapshot(path.string(), catalog));
    }
    {
        auto invalid = Runtime::load_snapshot(snapshot.string());
        invalid.erase_snapshot_metadata("dee_thinking.composition_recipe");
        const auto path = temporary.file("missing-recipe.deetsnap");
        invalid.save_snapshot(path.string());
        DEE_CHECK_THROWS(suite, ComposedWorld::load_snapshot(path.string(), catalog));
    }
    {
        auto invalid = Runtime::load_snapshot(snapshot.string());
        auto recipe = invalid.snapshot_metadata("dee_thinking.composition_recipe").value();
        const auto version = recipe.find("312e302e30\n"); // hex("1.0.0")
        DEE_CHECK(suite, version != std::string::npos);
        if (version != std::string::npos) recipe.replace(version, 10, "322e302e30");
        invalid.set_snapshot_metadata("dee_thinking.composition_recipe", std::move(recipe));
        const auto path = temporary.file("bad-constructor-version.deetsnap");
        invalid.save_snapshot(path.string());
        DEE_CHECK_THROWS(suite, ComposedWorld::load_snapshot(path.string(), catalog));
    }

    if (argc == 2) {
        DEE_CHECK_THROWS(suite, ComposedWorld::load_snapshot(argv[1], catalog));
    } else {
        DEE_CHECK(suite, false);
    }

    return suite.finish();
}
