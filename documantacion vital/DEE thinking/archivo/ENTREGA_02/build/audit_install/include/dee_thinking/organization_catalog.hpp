#pragma once

#include "dee_thinking/runtime.hpp"

#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking::catalog {

enum class OrganizationFamily : std::uint8_t {
    TransportRedirection = 1,
    RelationalLearning = 2,
    FunctionalUpdateTransfer = 3,
    RelativeMemoryHistorySelection = 4,
    MultichannelIntegrationSeparation = 5,
    RecurrenceLaterUse = 6,
    DistributedContextMemory = 7,
};

enum class Availability : std::uint8_t {
    Available = 1,
    Pending = 2,
};

enum class ParameterKind : std::uint8_t {
    Integer = 1,
    Boolean = 2,
    Enumeration = 3,
};

enum class PortRole : std::uint8_t {
    ExperienceInput = 1,
    QueryInput = 2,
    UpdateInput = 3,
    SupplyInput = 4,
    PassiveReadout = 5,
    InternalOutput = 6,
    ContextInterface = 7,
};

enum class ContributionKind : std::uint8_t {
    Carrier = 1,
    CollisionProposal = 2,
    MobileRelation = 3,
    ContextCondition = 4,
    PassiveObservation = 5,
};

struct ParameterSpec {
    std::string name;
    ParameterKind kind{ParameterKind::Integer};
    std::int64_t default_value{};
    std::int64_t minimum{};
    std::int64_t maximum{};
    std::map<std::int64_t, std::string> enumeration;
    std::string meaning;
};

struct PortSpec {
    std::string name;
    PortRole role{PortRole::ExperienceInput};
    ContributionKind contribution{ContributionKind::Carrier};
    Coordinate relative_site{};
    std::optional<Direction> direction;
    std::uint64_t earliest_tick{};
    std::uint64_t latest_tick{};
    std::uint16_t minimum_load{};
    std::uint16_t maximum_load{v27::kReducerCap};
    bool transforms_world{};
    std::string timing_and_phase;
};

struct OrganizationDescriptor {
    std::string id;
    std::string constructor_version;
    std::vector<OrganizationFamily> families;
    Availability availability{Availability::Pending};
    std::string source_mechanism;
    std::string source_reference;
    std::string summary;
    std::vector<ParameterSpec> parameters;
    std::vector<PortSpec> ports;
    std::string preparation;
    std::string resources;
    std::string query_effects;
    std::string possible_interference;
    std::string retention_and_saturation;
    std::string tested_domain;
    std::string pending_reason;
};

struct OrganizationRequest {
    std::string catalog_id;
    std::string instance_id;
    Coordinate anchor{};
    std::map<std::string, std::int64_t> parameters;
};

struct InstancePort {
    PortSpec contract;
    Coordinate absolute_site{};
};

// Instances expose contracts and landmarks, but not mutable voxel templates.
// Installation is performed only by CompositionPlanner before execution.
class OrganizationInstance {
public:
    [[nodiscard]] const OrganizationDescriptor& descriptor() const noexcept { return descriptor_; }
    [[nodiscard]] const std::string& instance_id() const noexcept { return instance_id_; }
    [[nodiscard]] Coordinate anchor() const noexcept { return anchor_; }
    [[nodiscard]] const std::map<std::string, std::int64_t>& parameters() const noexcept { return parameters_; }
    [[nodiscard]] const std::vector<InstancePort>& ports() const noexcept { return ports_; }
    [[nodiscard]] const std::map<std::string, Coordinate>& landmarks() const noexcept { return landmarks_; }
    [[nodiscard]] const InstancePort* find_port(const std::string& name) const noexcept;

private:
    struct InitialVoxel {
        Coordinate relative_site{};
        std::uint64_t raw{};
        std::uint64_t clock{};
        std::string purpose;
    };
    struct ChannelTemplate {
        std::string local_name;
        Coordinate relative_site{};
        std::uint32_t state{1};
        Direction direction{};
        std::uint8_t semantic{1};
        bool allow_experience{true};
        bool allow_probe{};
    };

    OrganizationDescriptor descriptor_;
    std::string instance_id_;
    Coordinate anchor_{};
    std::map<std::string, std::int64_t> parameters_;
    std::vector<InstancePort> ports_;
    std::map<std::string, Coordinate> landmarks_;
    std::vector<InitialVoxel> initial_voxels_;
    std::vector<ChannelTemplate> channels_;

    friend class OrganizationCatalog;
    friend class CompositionPlanner;
    friend struct CatalogAssembler;
};

class OrganizationCatalog {
public:
    OrganizationCatalog();

    [[nodiscard]] const std::vector<OrganizationDescriptor>& descriptors() const noexcept { return descriptors_; }
    [[nodiscard]] const OrganizationDescriptor* find(const std::string& id) const noexcept;
    [[nodiscard]] OrganizationInstance instantiate(const OrganizationRequest& request) const;

private:
    std::vector<OrganizationDescriptor> descriptors_;
};

[[nodiscard]] const char* to_string(OrganizationFamily value) noexcept;
[[nodiscard]] const char* to_string(Availability value) noexcept;
[[nodiscard]] const char* to_string(PortRole value) noexcept;
[[nodiscard]] const char* to_string(ContributionKind value) noexcept;

}  // namespace dee::thinking::catalog
