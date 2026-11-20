#include "dee_thinking/kernel_v27.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

using V = std::array<int, 3>;
using dee::v27::Record;

constexpr V A{1, 0, 0};
constexpr V B{0, 1, 0};
constexpr V SENSOR{-1, 0, 1};
constexpr V NORMALIZER{1, 0, -1};
constexpr V PENALTY0{-1, 1, 0};
constexpr V ACTION1{-1, 1, 1};

struct World {
    int n{};
    std::vector<std::uint64_t> raw_a, raw_b, clock_a, clock_b;

    explicit World(int dimension)
        : n(dimension),
          raw_a(static_cast<std::size_t>(n) * n * n), raw_b(raw_a.size()),
          clock_a(raw_a.size()), clock_b(raw_a.size()) {}

    std::size_t index(V q) const {
        return dee::v27::linear_index(q[0], q[1], q[2], n);
    }
    std::uint64_t raw(V q) const { return raw_a.at(index(q)); }
    Record read(V q) const { return dee::v27::decode_record(raw(q)); }
    void put(V q, std::uint64_t raw_value, std::uint64_t clock_value) {
        const auto i = index(q);
        if (raw_a[i] != 0) throw std::runtime_error("occupied injection port");
        raw_a[i] = raw_b[i] = raw_value;
        clock_a[i] = clock_b[i] = clock_value;
    }
    void overwrite(V q, std::uint64_t raw_value, std::uint64_t clock_value) {
        const auto i = index(q);
        raw_a[i] = raw_b[i] = raw_value;
        clock_a[i] = clock_b[i] = clock_value;
    }
    void clear(V q) { overwrite(q, 0, 0); }
    void tick() {
        dee::v27::tick(raw_a, raw_b, clock_a, clock_b, n,
                       {dee::v27::Backend::Lazy, 4});
    }
};

V add(V q, V d, int k, int n) {
    for (int i = 0; i < 3; ++i) q[i] = dee::v27::wrap_coordinate(q[i] + k * d[i], n);
    return q;
}

V plus(V a, V b) {
    for (int i = 0; i < 3; ++i) a[i] += b[i];
    return a;
}

V neg(V value) {
    for (auto& x : value) x = -x;
    return value;
}

V transform(V value, V permutation, V signs) {
    return {signs[0] * value[permutation[0]],
            signs[1] * value[permutation[1]],
            signs[2] * value[permutation[2]]};
}

std::uint64_t pack(std::uint32_t state, std::uint16_t sreg, V direction,
                   std::uint8_t semantic = 1) {
    return dee::v27::pack_record(state, sreg, direction[0], direction[1],
                                 direction[2], semantic);
}

void inject_arrival(World& world, V target, V direction, std::uint16_t sreg,
                    std::uint32_t state, std::uint64_t clock) {
    world.put(add(target, direction, -1, world.n),
              pack(state, sreg, direction), clock);
}

bool direction_is(const Record& record, V expected) {
    return record.raw_present() && V{record.dx, record.dy, record.dz} == expected;
}

struct Geometry {
    std::string id;
    int n;
    int d1;
    int d2;
    V permutation;
    V signs;
    V receiver;
};

struct Row {
    std::string geometry;
    std::string mode;
    bool backup_learned{};
    bool reconstructed_at_arrival{};
    bool fresh_function{};
    bool source1_depleted{};
    bool source2_depleted{};
    std::uint16_t query_sreg{};
    V query_direction{};
};

Row run_case(const Geometry& g, const std::string& mode, std::uint32_t seed) {
    World world(g.n);
    const V a = transform(A, g.permutation, g.signs);
    const V b = transform(B, g.permutation, g.signs);
    const V sensor = transform(SENSOR, g.permutation, g.signs);
    const V normalizer = transform(NORMALIZER, g.permutation, g.signs);
    const V penalty0 = transform(PENALTY0, g.permutation, g.signs);
    const V action1 = transform(ACTION1, g.permutation, g.signs);
    const V relay1 = transform({1, -1, 1}, g.permutation, g.signs);
    const V relay2 = transform({-1, -1, 1}, g.permutation, g.signs);
    const V route1 = plus(relay1, b);
    const V route2 = plus(relay2, b);
    const V source1 = add(g.receiver, route1, -g.d1, g.n);
    const V source2 = add(g.receiver, route2, -g.d2, g.n);
    if (source1 == source2) throw std::runtime_error("degenerate redundant sources");

    world.put(source1, pack(610000u + seed, 7, a), 710000u + seed);
    world.put(source2, pack(610001u + seed, 8, a), 710001u + seed);

    const int learned_tick = 2 * g.n;
    const int launch1 = 3 * g.n;
    const int arrival1 = launch1 + g.d1;
    const int damage_tick = arrival1 + 1;
    const int launch2 = 5 * g.n;
    const int arrival2 = launch2 + g.d2;
    const int query2 = arrival2 + g.n;
    const int cut_offset = std::max(2, g.d2 / 2);
    bool backup_learned = false;
    bool reconstructed = false;

    for (int current = 0; current < query2; ++current) {
        const int next = current + 1;
        if (next == g.n) {
            inject_arrival(world, source1, sensor, 47, 720000u + seed, 730000u + seed);
            inject_arrival(world, source2, sensor, 48, 720001u + seed, 730001u + seed);
        }
        if (next == learned_tick) {
            inject_arrival(world, source1, normalizer, 53, 740000u + seed, 750000u + seed);
            inject_arrival(world, source2, normalizer, 54, 740001u + seed, 750001u + seed);
            inject_arrival(world, source1, penalty0, 59, 760000u + seed, 770000u + seed);
            if (mode != "backup_untrained") {
                inject_arrival(world, source2, penalty0, 60, 760001u + seed, 770001u + seed);
            }
        }
        if (next == launch1) {
            inject_arrival(world, source1, relay1, 61, 780000u + seed, 790000u + seed);
        }
        if (next == arrival1) {
            inject_arrival(world, g.receiver, neg(relay1), 71, 800000u + seed, 810000u + seed);
        }
        if (next == launch2 && mode != "no_backup") {
            inject_arrival(world, source2, relay2, 67, 820000u + seed, 830000u + seed);
        }
        if (next == launch2 + cut_offset && (mode == "path_cut" || mode == "offpath_cut")) {
            V target = add(source2, route2, cut_offset, g.n);
            if (mode == "offpath_cut") {
                target = add(target, transform({0, 0, 5}, g.permutation, g.signs), 1, g.n);
            }
            inject_arrival(world, target, neg(route2), 73, 840000u + seed, 850000u + seed);
        }
        if (next == arrival2 && mode != "receiver_none") {
            const V converter = mode == "wrong_receiver" ? neg(b) : neg(relay2);
            inject_arrival(world, g.receiver, converter, 79, 860000u + seed, 870000u + seed);
        }
        if (next == query2) {
            inject_arrival(world, g.receiver, sensor, 101, 880000u + seed, 890000u + seed);
        }

        world.tick();

        if (next == learned_tick) {
            const auto backup = world.read(source2);
            backup_learned = direction_is(backup, b);
            if (mode == "backup_direction_reset" && backup.raw_present()) {
                world.overwrite(source2, pack(backup.state, backup.s_reg, a, backup.semantic),
                                world.clock_a.at(world.index(source2)));
            } else if (mode == "no_backup") {
                world.clear(source2);
            }
        }
        if (next == damage_tick) {
            world.clear(add(g.receiver, b, 1, g.n));
        }
        if (next == arrival2) reconstructed = direction_is(world.read(g.receiver), b);
    }

    const Record query = world.read(g.receiver);
    return {
        g.id, mode, backup_learned, reconstructed, direction_is(query, action1),
        world.raw(source1) == 0, world.raw(source2) == 0, query.s_reg,
        {query.dx, query.dy, query.dz}
    };
}

std::string boolean(bool value) { return value ? "true" : "false"; }

void write_results(const fs::path& path, const std::vector<Row>& rows) {
    std::map<std::string, int> functional;
    for (const auto& row : rows) functional[row.mode] += row.fresh_function ? 1 : 0;
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot create results file");
    out << "{\n  \"schema\": \"dee-thinking-candidate-core17-repair-v1\",\n"
        << "  \"modality\": \"ACOPLADA_DIAGNOSTIC\",\n"
        << "  \"copy_semantics\": \"two separately trained copies; no acquired replication from copy1 to copy2\",\n"
        << "  \"rows\": [\n";
    for (std::size_t i = 0; i < rows.size(); ++i) {
        const auto& r = rows[i];
        out << "    {\"geometry\":\"" << r.geometry << "\",\"mode\":\"" << r.mode
            << "\",\"backup_learned\":" << boolean(r.backup_learned)
            << ",\"reconstructed_at_arrival\":" << boolean(r.reconstructed_at_arrival)
            << ",\"fresh_function\":" << boolean(r.fresh_function)
            << ",\"source1_depleted\":" << boolean(r.source1_depleted)
            << ",\"source2_depleted\":" << boolean(r.source2_depleted)
            << ",\"query_s_reg\":" << r.query_sreg
            << ",\"query_direction\":[" << r.query_direction[0] << ','
            << r.query_direction[1] << ',' << r.query_direction[2] << "]}";
        if (i + 1 != rows.size()) out << ',';
        out << '\n';
    }
    out << "  ],\n  \"counts_functional\": {";
    std::size_t emitted = 0;
    for (const auto& [mode, count] : functional) {
        out << (emitted++ ? "," : "") << "\"" << mode << "\":" << count;
    }
    out << "},\n  \"technical_expectation_matched\": "
        << boolean(functional["treatment"] == 2 && functional["offpath_cut"] == 2 &&
                   functional["backup_untrained"] == 0 &&
                   functional["backup_direction_reset"] == 0 &&
                   functional["no_backup"] == 0 && functional["path_cut"] == 0 &&
                   functional["wrong_receiver"] == 0)
        << "\n}\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const fs::path output = argc > 1 ? argv[1] : "results.json";
        const std::array<Geometry, 2> geometries{{
            {"fresh_like_00", 31, 7, 7, {2, 1, 0}, {-1, 1, -1}, {15, 15, 15}},
            {"fresh_like_01", 31, 6, 6, {0, 1, 2}, {1, 1, -1}, {15, 15, 15}},
        }};
        const std::array<std::string, 7> modes{{
            "treatment", "backup_untrained", "backup_direction_reset", "no_backup",
            "path_cut", "offpath_cut", "wrong_receiver",
        }};
        std::vector<Row> rows;
        constexpr std::uint32_t preparation_tag = 1721000;
        for (const auto& geometry : geometries) {
            // Treatment and controls must begin with identical non-geometric
            // payload/clock values.  The fixed tag is part of the declared
            // preparation; it does not encode the mode or episode index.
            for (const auto& mode : modes) {
                rows.push_back(run_case(geometry, mode, preparation_tag));
            }
        }
        write_results(output, rows);
        int functional = 0;
        for (const auto& row : rows) {
            functional += row.fresh_function ? 1 : 0;
            std::cout << row.geometry << ' ' << row.mode
                      << " learned=" << row.backup_learned
                      << " reconstructed=" << row.reconstructed_at_arrival
                      << " functional=" << row.fresh_function << '\n';
        }
        std::cout << "cases=" << rows.size() << " functional=" << functional << '\n';
        const auto count_functional = [&](const std::string& mode) {
            return static_cast<int>(std::count_if(rows.begin(), rows.end(), [&](const Row& row) {
                return row.mode == mode && row.fresh_function;
            }));
        };
        const bool matched = rows.size() == 14 && count_functional("treatment") == 2 &&
            count_functional("offpath_cut") == 2 && count_functional("backup_untrained") == 0 &&
            count_functional("backup_direction_reset") == 0 && count_functional("no_backup") == 0 &&
            count_functional("path_cut") == 0 && count_functional("wrong_receiver") == 0;
        return matched ? 0 : 2;
    } catch (const std::exception& error) {
        std::cerr << "repair candidate error: " << error.what() << '\n';
        return 1;
    }
}
