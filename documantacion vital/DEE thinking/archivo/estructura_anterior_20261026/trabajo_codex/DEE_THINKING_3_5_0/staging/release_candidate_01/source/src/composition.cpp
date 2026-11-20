#include "dee_thinking/composition.hpp"

#include <algorithm>
#include <charconv>
#include <cstddef>
#include <fstream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string_view>
#include <tuple>
#include <utility>

namespace dee::thinking::catalog {
namespace {

constexpr std::string_view kCatalogSchemaKey = "dee_thinking.organization_catalog_schema";
constexpr std::string_view kCatalogSchema = "1";
constexpr std::string_view kRecipeSchemaKey = "dee_thinking.composition_recipe_schema";
constexpr std::string_view kRecipeSchema = "1";
constexpr std::string_view kRecipeKey = "dee_thinking.composition_recipe";
constexpr std::string_view kRecipeHeader = "DEE_THINKING_COMPOSITION_RECIPE_V1";
constexpr std::string_view kManifestKey = "dee_thinking.composition_manifest";
constexpr std::uint64_t kMaxRecipeItems = 65536;
constexpr std::size_t kMaxRecipeBytes = 1U << 20;

struct OrganizationRecipe {
    OrganizationRequest request;
    std::string constructor_version;
};

struct CompositionRecipe {
    int dimension{};
    std::vector<OrganizationRecipe> organizations;
    std::vector<ConnectionRequest> connections;
};

void append_line(std::string& output, std::string_view value) {
    if (value.size() >= kMaxRecipeBytes ||
        output.size() > kMaxRecipeBytes - value.size() - 1) {
        throw std::length_error("composition recipe exceeds snapshot metadata limit");
    }
    output.append(value);
    output.push_back('\n');
}

std::string hex_encode(std::string_view value) {
    static constexpr char digits[] = "0123456789abcdef";
    if (value.size() > (kMaxRecipeBytes - 1) / 2) {
        throw std::length_error("composition recipe field exceeds snapshot metadata limit");
    }
    std::string result;
    result.reserve(value.size() * 2);
    for (const auto character : value) {
        const auto byte = static_cast<unsigned char>(character);
        result.push_back(digits[byte >> 4]);
        result.push_back(digits[byte & 0x0f]);
    }
    return result;
}

unsigned char hex_nibble(char value) {
    if (value >= '0' && value <= '9') return static_cast<unsigned char>(value - '0');
    if (value >= 'a' && value <= 'f') return static_cast<unsigned char>(value - 'a' + 10);
    throw std::runtime_error("composition recipe contains invalid hexadecimal text");
}

std::string hex_decode(std::string_view value) {
    if ((value.size() & 1U) != 0) {
        throw std::runtime_error("composition recipe contains truncated hexadecimal text");
    }
    std::string result;
    result.reserve(value.size() / 2);
    for (std::size_t index = 0; index < value.size(); index += 2) {
        result.push_back(static_cast<char>((hex_nibble(value[index]) << 4) |
                                           hex_nibble(value[index + 1])));
    }
    return result;
}

class RecipeReader {
public:
    explicit RecipeReader(std::string_view input) : input_(input) {}

    [[nodiscard]] std::string_view line(std::string_view field) {
        const auto end = input_.find('\n', position_);
        if (end == std::string_view::npos) {
            throw std::runtime_error("composition recipe is truncated at " + std::string(field));
        }
        const auto value = input_.substr(position_, end - position_);
        position_ = end + 1;
        return value;
    }

    void require_end() const {
        if (position_ != input_.size()) {
            throw std::runtime_error("composition recipe has trailing data");
        }
    }

private:
    std::string_view input_;
    std::size_t position_{};
};

template <class Integer>
Integer parse_integer(std::string_view text, std::string_view field) {
    Integer result{};
    const auto* begin = text.data();
    const auto* end = begin + text.size();
    const auto parsed = std::from_chars(begin, end, result);
    if (text.empty() || parsed.ec != std::errc{} || parsed.ptr != end) {
        throw std::runtime_error("composition recipe has invalid " + std::string(field));
    }
    return result;
}

std::size_t parse_count(RecipeReader& reader, std::string_view field) {
    const auto count = parse_integer<std::uint64_t>(reader.line(field), field);
    if (count > kMaxRecipeItems || count > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("composition recipe " + std::string(field) + " exceeds its limit");
    }
    return static_cast<std::size_t>(count);
}

std::string serialize_recipe(int dimension,
                             const std::vector<OrganizationInstance>& organizations,
                             const std::vector<ConnectionRecord>& connections) {
    std::string output;
    append_line(output, kRecipeHeader);
    append_line(output, std::to_string(dimension));
    append_line(output, std::to_string(organizations.size()));
    for (const auto& organization : organizations) {
        append_line(output, hex_encode(organization.descriptor().id));
        append_line(output, hex_encode(organization.descriptor().constructor_version));
        append_line(output, hex_encode(organization.instance_id()));
        append_line(output, std::to_string(organization.anchor().x));
        append_line(output, std::to_string(organization.anchor().y));
        append_line(output, std::to_string(organization.anchor().z));
        append_line(output, std::to_string(organization.parameters().size()));
        for (const auto& [name, value] : organization.parameters()) {
            append_line(output, hex_encode(name));
            append_line(output, std::to_string(value));
        }
    }
    append_line(output, std::to_string(connections.size()));
    for (const auto& connection : connections) {
        append_line(output, hex_encode(connection.request.source.instance));
        append_line(output, hex_encode(connection.request.source.port));
        append_line(output, hex_encode(connection.request.target.instance));
        append_line(output, hex_encode(connection.request.target.port));
        append_line(output, hex_encode(connection.request.purpose));
    }
    return output;
}

CompositionRecipe parse_recipe(std::string_view serialized) {
    RecipeReader reader(serialized);
    if (reader.line("header") != kRecipeHeader) {
        throw std::runtime_error("unsupported composition recipe version");
    }

    CompositionRecipe recipe;
    recipe.dimension = parse_integer<int>(reader.line("dimension"), "dimension");
    const auto organization_count = parse_count(reader, "organization count");
    recipe.organizations.reserve(organization_count);
    for (std::size_t index = 0; index < organization_count; ++index) {
        OrganizationRecipe organization;
        organization.request.catalog_id = hex_decode(reader.line("catalog id"));
        organization.constructor_version = hex_decode(reader.line("constructor version"));
        organization.request.instance_id = hex_decode(reader.line("instance id"));
        organization.request.anchor.x = parse_integer<int>(reader.line("anchor x"), "anchor x");
        organization.request.anchor.y = parse_integer<int>(reader.line("anchor y"), "anchor y");
        organization.request.anchor.z = parse_integer<int>(reader.line("anchor z"), "anchor z");
        const auto parameter_count = parse_count(reader, "parameter count");
        for (std::size_t parameter = 0; parameter < parameter_count; ++parameter) {
            auto name = hex_decode(reader.line("parameter name"));
            const auto value = parse_integer<std::int64_t>(reader.line("parameter value"),
                                                           "parameter value");
            if (!organization.request.parameters.emplace(std::move(name), value).second) {
                throw std::runtime_error("composition recipe contains a duplicate parameter");
            }
        }
        recipe.organizations.push_back(std::move(organization));
    }

    const auto connection_count = parse_count(reader, "connection count");
    recipe.connections.reserve(connection_count);
    for (std::size_t index = 0; index < connection_count; ++index) {
        ConnectionRequest connection;
        connection.source.instance = hex_decode(reader.line("source instance"));
        connection.source.port = hex_decode(reader.line("source port"));
        connection.target.instance = hex_decode(reader.line("target instance"));
        connection.target.port = hex_decode(reader.line("target port"));
        connection.purpose = hex_decode(reader.line("connection purpose"));
        recipe.connections.push_back(std::move(connection));
    }
    reader.require_end();
    return recipe;
}

std::string required_metadata(const Runtime& runtime, std::string_view key) {
    const auto value = runtime.snapshot_metadata(std::string(key));
    if (!value) {
        throw std::runtime_error("composed snapshot is missing metadata: " + std::string(key));
    }
    return *value;
}

Coordinate normalize(Coordinate value, int n) {
    return {v27::wrap_coordinate(value.x, n),
            v27::wrap_coordinate(value.y, n),
            v27::wrap_coordinate(value.z, n)};
}

Coordinate translate(Coordinate anchor, Coordinate relative, int n) {
    return normalize({anchor.x + relative.x, anchor.y + relative.y, anchor.z + relative.z}, n);
}

Coordinate advance(Coordinate value, Direction direction, std::uint64_t count, int n) {
    const auto step = static_cast<std::int64_t>(count);
    auto component = [n](std::int64_t base, std::int64_t delta) {
        auto result = (base + delta) % n;
        if (result < 0) result += n;
        return static_cast<int>(result);
    };
    return {component(value.x, step * direction.dx),
            component(value.y, step * direction.dy),
            component(value.z, step * direction.dz)};
}

bool same(Direction left, Direction right) {
    return left.dx == right.dx && left.dy == right.dy && left.dz == right.dz;
}

std::string escape_json(const std::string& value) {
    std::string result;
    result.reserve(value.size() + 8);
    for (const char ch : value) {
        switch (ch) {
            case '\\': result += "\\\\"; break;
            case '"': result += "\\\""; break;
            case '\n': result += "\\n"; break;
            case '\r': result += "\\r"; break;
            case '\t': result += "\\t"; break;
            default: result += ch; break;
        }
    }
    return result;
}

bool is_source_role(PortRole role) {
    return role == PortRole::InternalOutput || role == PortRole::ContextInterface;
}

bool is_target_role(PortRole role) {
    return role == PortRole::UpdateInput || role == PortRole::ContextInterface;
}

bool contributions_compatible(ContributionKind source, ContributionKind target) {
    return source == target;
}

bool is_external_input_role(PortRole role) {
    return role == PortRole::ExperienceInput || role == PortRole::QueryInput ||
           role == PortRole::SupplyInput;
}

const InstancePort& checked_input_port(const std::vector<OrganizationInstance>& organizations,
                                       const std::string& instance,
                                       const std::string& port_name,
                                       std::uint64_t at_tick,
                                       std::uint16_t s_reg,
                                       bool require_query) {
    const auto organization = std::find_if(organizations.begin(), organizations.end(),
                                           [&](const auto& value) { return value.instance_id() == instance; });
    if (organization == organizations.end()) throw std::invalid_argument("unknown organization instance: " + instance);
    const auto* port_value = organization->find_port(port_name);
    if (port_value == nullptr) throw std::invalid_argument("unknown organization port: " + instance + "." + port_name);
    if (!is_external_input_role(port_value->contract.role)) {
        throw std::invalid_argument("port is not an external input: " + instance + "." + port_name);
    }
    if (require_query && port_value->contract.role != PortRole::QueryInput) {
        throw std::invalid_argument("probe requires a QUERY_INPUT port: " + instance + "." + port_name);
    }
    if (at_tick < port_value->contract.earliest_tick || at_tick > port_value->contract.latest_tick) {
        throw std::invalid_argument("requested tick is outside port contract: " + instance + "." + port_name);
    }
    if (s_reg < port_value->contract.minimum_load || s_reg > port_value->contract.maximum_load) {
        throw std::invalid_argument("s_reg is outside port contract: " + instance + "." + port_name);
    }
    return *port_value;
}

}  // namespace

ComposedWorld::ComposedWorld(Runtime runtime,
                             std::vector<OrganizationInstance> organizations,
                             std::vector<ConnectionRecord> connections,
                             std::map<std::string, Coordinate> landmarks)
    : runtime_(std::move(runtime)),
      organizations_(std::move(organizations)),
      connections_(std::move(connections)),
      landmarks_(std::move(landmarks)) {}

ComposedWorld ComposedWorld::load_snapshot(const std::string& path) {
    const OrganizationCatalog catalog;
    return load_snapshot(path, catalog);
}

ComposedWorld ComposedWorld::load_snapshot(const std::string& path,
                                           const OrganizationCatalog& catalog) {
    Runtime saved_runtime = Runtime::load_snapshot(path);
    if (saved_runtime.loaded_snapshot_version() != 2) {
        throw std::runtime_error("self-contained composition restore requires snapshot version 2");
    }
    if (required_metadata(saved_runtime, kCatalogSchemaKey) != kCatalogSchema) {
        throw std::runtime_error("snapshot organization catalog schema is unsupported");
    }
    if (required_metadata(saved_runtime, kRecipeSchemaKey) != kRecipeSchema) {
        throw std::runtime_error("snapshot composition recipe schema is unsupported");
    }

    const auto serialized_recipe = required_metadata(saved_runtime, kRecipeKey);
    const auto stored_manifest = required_metadata(saved_runtime, kManifestKey);
    const auto recipe = parse_recipe(serialized_recipe);
    if (recipe.dimension != saved_runtime.dimension()) {
        throw std::runtime_error("snapshot composition recipe dimension does not match Runtime");
    }

    CompositionPlanner planner(recipe.dimension);
    for (const auto& organization : recipe.organizations) {
        const auto* descriptor = catalog.find(organization.request.catalog_id);
        if (descriptor == nullptr) {
            throw std::runtime_error("snapshot names an unknown catalog constructor: " +
                                     organization.request.catalog_id);
        }
        if (descriptor->constructor_version != organization.constructor_version) {
            throw std::runtime_error("snapshot catalog constructor version mismatch: " +
                                     organization.request.catalog_id);
        }
        planner.add(catalog.instantiate(organization.request));
    }
    for (const auto& connection : recipe.connections) planner.connect(connection);

    ComposedWorld reconstructed = planner.build();
    const auto canonical_recipe = required_metadata(reconstructed.runtime(), kRecipeKey);
    if (serialized_recipe != canonical_recipe) {
        throw std::runtime_error("snapshot composition recipe is not canonical for this catalog");
    }
    if (stored_manifest != reconstructed.manifest_json()) {
        throw std::runtime_error("snapshot composition manifest does not match its recipe");
    }
    if (saved_runtime.channel_names() != reconstructed.runtime().channel_names()) {
        throw std::runtime_error("snapshot Runtime channels do not match its composition recipe");
    }

    reconstructed.runtime_ = std::move(saved_runtime);
    return reconstructed;
}

std::string ComposedWorld::qualified_channel(const std::string& instance,
                                             const std::string& local_name) const {
    const auto found = std::find_if(organizations_.begin(), organizations_.end(),
                                    [&](const auto& value) { return value.instance_id() == instance; });
    if (found == organizations_.end()) throw std::invalid_argument("unknown organization instance: " + instance);
    const auto channel = instance + "." + local_name;
    const auto names = runtime_.channel_names();
    if (std::find(names.begin(), names.end(), channel) == names.end()) {
        throw std::invalid_argument("unknown local channel: " + channel);
    }
    return channel;
}

EventReceipt ComposedWorld::experience(const std::string& instance, const std::string& port,
                                       std::uint64_t at_tick, std::uint16_t s_reg) {
    (void)checked_input_port(organizations_, instance, port, at_tick, s_reg, false);
    return runtime_.experience(qualified_channel(instance, port), at_tick, s_reg);
}

EventReceipt ComposedWorld::experience_batch(const std::vector<PortInputRequest>& inputs,
                                             std::uint64_t at_tick) {
    std::vector<InputRequest> requests;
    requests.reserve(inputs.size());
    for (const auto& input : inputs) {
        (void)checked_input_port(organizations_, input.instance, input.port, at_tick, input.s_reg, false);
        requests.push_back({qualified_channel(input.instance, input.port), input.s_reg});
    }
    return runtime_.experience_batch(requests, at_tick);
}

EventReceipt ComposedWorld::probe(const std::string& instance, const std::string& port,
                                  std::uint64_t at_tick, std::uint16_t s_reg) {
    (void)checked_input_port(organizations_, instance, port, at_tick, s_reg, true);
    return runtime_.probe(qualified_channel(instance, port), at_tick, s_reg);
}

std::string ComposedWorld::manifest_json() const {
    std::ostringstream out;
    out << "{\n  \"format\": \"DEE_THINKING_COMPOSITION_V1\",\n"
        << "  \"dimension\": " << runtime_.dimension() << ",\n"
        << "  \"organizations\": [\n";
    for (std::size_t i = 0; i < organizations_.size(); ++i) {
        const auto& value = organizations_[i];
        out << "    {\"instance\": \"" << escape_json(value.instance_id())
            << "\", \"catalog_id\": \"" << escape_json(value.descriptor().id)
            << "\", \"constructor_version\": \"" << escape_json(value.descriptor().constructor_version)
            << "\", \"anchor\": [" << value.anchor().x << ", " << value.anchor().y
            << ", " << value.anchor().z << "], \"parameters\": {";
        std::size_t count = 0;
        for (const auto& [name, parameter] : value.parameters()) {
            if (count++ != 0) out << ", ";
            out << "\"" << escape_json(name) << "\": " << parameter;
        }
        out << "}}" << (i + 1 == organizations_.size() ? "" : ",") << "\n";
    }
    out << "  ],\n  \"connections\": [\n";
    for (std::size_t i = 0; i < connections_.size(); ++i) {
        const auto& value = connections_[i];
        out << "    {\"source\": \"" << escape_json(value.request.source.instance + "." + value.request.source.port)
            << "\", \"target\": \"" << escape_json(value.request.target.instance + "." + value.request.target.port)
            << "\", \"purpose\": \"" << escape_json(value.request.purpose)
            << "\", \"verification\": \"" << to_string(value.verification)
            << "\", \"physical_contract\": \"" << escape_json(value.physical_contract) << "\"}"
            << (i + 1 == connections_.size() ? "" : ",") << "\n";
    }
    out << "  ]\n}\n";
    return out.str();
}

void ComposedWorld::save_manifest(const std::string& path) const {
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    if (!stream) throw std::runtime_error("cannot create composition manifest: " + path);
    const auto content = manifest_json();
    stream.write(content.data(), static_cast<std::streamsize>(content.size()));
    stream.close();
    if (!stream) throw std::runtime_error("cannot finish composition manifest: " + path);
}

void ComposedWorld::save_snapshot(const std::string& path) const {
    runtime_.save_snapshot(path);
}

void ComposedWorld::restore_snapshot(const std::string& path) {
    ComposedWorld candidate = ComposedWorld::load_snapshot(path);
    if (candidate.manifest_json() != manifest_json()) {
        throw std::runtime_error("snapshot composition manifest does not match this composed world");
    }
    runtime_ = std::move(candidate.runtime_);
}

CompositionPlanner::CompositionPlanner(int dimension) : dimension_(dimension) {
    if (dimension < 3) throw std::invalid_argument("composition dimension must be at least 3");
}

void CompositionPlanner::add(OrganizationInstance organization) {
    if (find_instance(organization.instance_id()) != nullptr) {
        throw std::invalid_argument("duplicate organization instance: " + organization.instance_id());
    }
    organizations_.push_back(std::move(organization));
}

void CompositionPlanner::connect(ConnectionRequest connection) {
    connections_.push_back(std::move(connection));
}

const OrganizationInstance* CompositionPlanner::find_instance(const std::string& id) const noexcept {
    const auto found = std::find_if(organizations_.begin(), organizations_.end(),
                                    [&](const auto& value) { return value.instance_id() == id; });
    return found == organizations_.end() ? nullptr : &*found;
}

std::vector<Diagnostic> CompositionPlanner::analyze() const {
    std::vector<Diagnostic> result;
    if (organizations_.empty()) {
        result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                          "EMPTY_COMPOSITION", "At least one organization is required."});
        return result;
    }

    using Site = std::tuple<int, int, int>;
    std::map<Site, std::string> occupied;
    std::map<Site, std::string> channels;
    const auto world_capacity = static_cast<std::uint64_t>(dimension_) *
                                static_cast<std::uint64_t>(dimension_) *
                                static_cast<std::uint64_t>(dimension_);
    for (const auto& organization : organizations_) {
        const auto budget = organization.resource_budget();
        if (budget.initial_voxels + budget.input_channels > world_capacity) {
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "RESOURCE_BUDGET_EXCEEDS_WORLD",
                              organization.instance_id() + " declares more initial sites/channels than the world contains."});
        } else {
            result.push_back({DiagnosticSeverity::Information, VerificationClass::StaticVerified,
                              "RESOURCE_BUDGET_STATICALLY_VALID",
                              organization.instance_id() + " uses " +
                                  std::to_string(budget.initial_voxels) + " initial voxels, " +
                                  std::to_string(budget.persistent_sources) + " persistent sources, " +
                                  std::to_string(budget.input_channels) + " input channels and " +
                                  std::to_string(budget.declared_connection_capacity) +
                                  " declared connection slots."});
        }
        for (const auto& voxel : organization.initial_voxels_) {
            const auto site = translate(organization.anchor_, voxel.relative_site, dimension_);
            const Site key{site.x, site.y, site.z};
            const auto [it, inserted] = occupied.emplace(key, organization.instance_id_ + ":" + voxel.purpose);
            if (!inserted) {
                result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                                  "INITIAL_VOXEL_OVERLAP",
                                  "Initial voxel overlap between " + it->second + " and " +
                                      organization.instance_id_ + ":" + voxel.purpose + "."});
            }
        }
        for (const auto& channel : organization.channels_) {
            const auto site = translate(organization.anchor_, channel.relative_site, dimension_);
            const Site key{site.x, site.y, site.z};
            if (const auto found = occupied.find(key); found != occupied.end()) {
                result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                                  "CHANNEL_INITIALLY_OCCUPIED",
                                  "Channel " + organization.instance_id_ + "." + channel.local_name +
                                      " starts on occupied site " + found->second + "."});
            }
            const auto [it, inserted] = channels.emplace(key, organization.instance_id_ + "." + channel.local_name);
            if (!inserted) {
                result.push_back({DiagnosticSeverity::Warning, VerificationClass::RequiresSimulation,
                                  "CHANNEL_SITE_SHARED",
                                  "Channels " + it->second + " and " + organization.instance_id_ + "." +
                                      channel.local_name + " share an admission site; simultaneous requests conflict."});
            }
        }
    }

    std::map<std::string, std::string> source_targets;
    std::map<std::string, std::vector<std::string>> target_sources;
    for (const auto& request : connections_) {
        const auto source_key = request.source.instance + "." + request.source.port;
        const auto target_key = request.target.instance + "." + request.target.port;
        const bool inserted = source_targets.emplace(source_key, target_key).second;
        target_sources[target_key].push_back(source_key);
        if (!inserted) {
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "PHYSICAL_FANOUT_UNSUPPORTED",
                              "Output " + source_key + " is connected more than once; the planner does not clone physical memory or carriers."});
        }
    }

    for (const auto& request : connections_) {
        const auto* source_instance = find_instance(request.source.instance);
        const auto* target_instance = find_instance(request.target.instance);
        if (source_instance == nullptr || target_instance == nullptr) {
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "UNKNOWN_CONNECTION_INSTANCE", "Connection names an unknown organization instance."});
            continue;
        }
        const auto* source = source_instance->find_port(request.source.port);
        const auto* target = target_instance->find_port(request.target.port);
        if (source == nullptr || target == nullptr) {
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "UNKNOWN_CONNECTION_PORT", "Connection names an unknown organization port."});
            continue;
        }
        bool compatible = true;
        const auto target_key = request.target.instance + "." + request.target.port;
        const auto target_count = target_sources.at(target_key).size();
        if (target_count > target->contract.maximum_connections) {
            compatible = false;
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "TARGET_CONNECTION_CARDINALITY_EXCEEDED",
                              target_key + " receives " + std::to_string(target_count) +
                                  " declared sources but its contract admits at most " +
                                  std::to_string(target->contract.maximum_connections) + "."});
        } else if (target_count > 1) {
            result.push_back({DiagnosticSeverity::Warning, VerificationClass::RequiresSimulation,
                              "MULTISOURCE_TARGET_OUTCOME_REQUIRES_SIMULATION",
                              target_key + " has multiple physical sources; reducer order, phase and interference require simulation."});
        }
        if (!is_source_role(source->contract.role) || !is_target_role(target->contract.role)) {
            compatible = false;
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "PORT_ROLE_MISMATCH", "Connection requires an internal/context output and update/context input."});
        }
        if (!contributions_compatible(source->contract.contribution, target->contract.contribution)) {
            compatible = false;
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "CONTRIBUTION_MISMATCH", "Connection contribution kinds differ."});
        }
        if (source->contract.maximum_load < target->contract.minimum_load ||
            target->contract.maximum_load < source->contract.minimum_load) {
            compatible = false;
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "LOAD_RANGE_MISMATCH", "Source and target load ranges do not overlap."});
        }
        if (source->contract.direction && target->contract.direction &&
            !same(*source->contract.direction, *target->contract.direction)) {
            compatible = false;
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "DIRECTION_MISMATCH", "Source direction does not match the target contract."});
        }
        if (source->contract.latest_tick > target->contract.earliest_tick) {
            compatible = false;
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "TEMPORAL_ORDER_MISMATCH", "Source is not available before the target encounter."});
        }
        if (compatible) {
            const auto source_site = normalize(source->absolute_site, dimension_);
            const auto target_site = normalize(target->absolute_site, dimension_);
            const auto travel = target->contract.earliest_tick - source->contract.earliest_tick;
            const auto predicted = source->contract.direction
                ? advance(source_site, *source->contract.direction, travel, dimension_)
                : source_site;
            if (!(predicted == target_site)) {
                result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                                  "PHYSICAL_ROUTE_MISMATCH",
                                  "Declared source path does not reach the target site at the target tick."});
            } else {
                result.push_back({DiagnosticSeverity::Information, VerificationClass::StaticVerified,
                                  "CONNECTION_ROUTE_STATICALLY_VALID",
                                  request.source.instance + "." + request.source.port + " reaches " +
                                      request.target.instance + "." + request.target.port +
                                      " under the declared geometry and timing."});
                result.push_back({DiagnosticSeverity::Information, VerificationClass::RequiresSimulation,
                                  "CONNECTION_OUTCOME_REQUIRES_SIMULATION",
                                  "Survival, reducer precedence, phase, and interference remain physical outcomes."});
                result.push_back({DiagnosticSeverity::Information, VerificationClass::RequiresSimulation,
                                  "PHASE_REQUIRES_SIMULATION",
                                  "Clock/phase compatibility is not inferred from metadata; execute the declared common-age protocol."});
            }
        }
    }
    if (connections_.empty() && organizations_.size() > 1) {
        result.push_back({DiagnosticSeverity::Warning, VerificationClass::RequiresSimulation,
                          "NO_DECLARED_CONNECTIONS", "Multiple organizations have no declared physical contract."});
    }

    auto has_inbound = [&](const std::string& instance, const std::string& port_name) {
        return std::any_of(connections_.begin(), connections_.end(), [&](const auto& connection) {
            return connection.target.instance == instance && connection.target.port == port_name;
        });
    };
    for (const auto& organization : organizations_) {
        std::optional<std::string> required_port;
        if (organization.descriptor().id == "relation_query.c6h01.v1") required_port = "relation_input";
        if (organization.descriptor().id == "query_recurrence.p01.v1") required_port = "updated_relation_input";
        if (organization.descriptor().id == "relative_history.i02.v1") required_port = "context";
        if (organization.descriptor().id == "contextual_multichannel_recurrence.p02.v1") required_port = "context_input";
        if (required_port && !has_inbound(organization.instance_id(), *required_port)) {
            result.push_back({DiagnosticSeverity::Error, VerificationClass::Unsupported,
                              "MISSING_REQUIRED_CONNECTION",
                              organization.instance_id() + "." + *required_port +
                                  " requires an explicit physical connection before build()."});
        }
    }
    return result;
}

ComposedWorld CompositionPlanner::build() const {
    const auto diagnostics = analyze();
    const auto error = std::find_if(diagnostics.begin(), diagnostics.end(),
                                    [](const auto& value) { return value.severity == DiagnosticSeverity::Error; });
    if (error != diagnostics.end()) throw std::logic_error("composition rejected: " + error->code + ": " + error->message);

    const auto n = static_cast<std::size_t>(dimension_);
    if (n > std::numeric_limits<std::size_t>::max() / n / n) {
        throw std::length_error("composition world size overflow");
    }
    std::vector<std::uint64_t> raw(n * n * n, 0);
    std::vector<std::uint64_t> clock(raw.size(), 0);
    for (const auto& organization : organizations_) {
        for (const auto& voxel : organization.initial_voxels_) {
            const auto site = translate(organization.anchor_, voxel.relative_site, dimension_);
            const auto index = v27::linear_index(site.x, site.y, site.z, dimension_);
            raw[index] = voxel.raw;
            clock[index] = voxel.clock;
        }
    }
    Runtime runtime = Runtime::import_research_state(dimension_, 0, std::move(raw), std::move(clock));
    std::map<std::string, Coordinate> landmarks;
    for (const auto& organization : organizations_) {
        for (const auto& channel : organization.channels_) {
            runtime.register_channel(ChannelSpec{
                organization.instance_id_ + "." + channel.local_name,
                translate(organization.anchor_, channel.relative_site, dimension_),
                channel.state, channel.direction, channel.semantic,
                channel.allow_experience, channel.allow_probe});
        }
        for (const auto& [name, site] : organization.landmarks_) {
            landmarks.emplace(organization.instance_id_ + "." + name, normalize(site, dimension_));
        }
    }
    runtime.set_protocol_phase("composition_ready");
    std::vector<ConnectionRecord> records;
    records.reserve(connections_.size());
    for (const auto& connection : connections_) {
        records.push_back({connection, VerificationClass::RequiresSimulation,
                           "Static route accepted; native v27 evolution determines survival and result."});
    }
    ComposedWorld world(std::move(runtime), organizations_, std::move(records), std::move(landmarks));
    world.runtime().set_snapshot_metadata(std::string(kCatalogSchemaKey), std::string(kCatalogSchema));
    world.runtime().set_snapshot_metadata(std::string(kRecipeSchemaKey), std::string(kRecipeSchema));
    world.runtime().set_snapshot_metadata(
        std::string(kRecipeKey),
        serialize_recipe(dimension_, world.organizations_, world.connections_));
    world.runtime().set_snapshot_metadata(std::string(kManifestKey), world.manifest_json());
    return world;
}

const char* to_string(DiagnosticSeverity value) noexcept {
    switch (value) {
        case DiagnosticSeverity::Information: return "INFORMATION";
        case DiagnosticSeverity::Warning: return "WARNING";
        case DiagnosticSeverity::Error: return "ERROR";
    }
    return "UNKNOWN";
}

const char* to_string(VerificationClass value) noexcept {
    switch (value) {
        case VerificationClass::StaticVerified: return "STATIC_VERIFIED";
        case VerificationClass::RequiresSimulation: return "REQUIRES_SIMULATION";
        case VerificationClass::Unsupported: return "UNSUPPORTED";
    }
    return "UNKNOWN";
}

}  // namespace dee::thinking::catalog
