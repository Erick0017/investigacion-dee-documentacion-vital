#pragma once
#include "dee_thinking/organizational.hpp"
#include <cstddef>
#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking::consolidated {

struct FormDescriptor {
    std::size_t index{};
    std::string name;
    Coordinate hub;
};

// These are initial-preparation options, not a teaching/answer map.
struct RepertoireOptions {
    int dimension{67};
    std::size_t forms{16};
    int plane_gap{2};
    Coordinate translation{};
    bool revision_interfaces{true};
    std::size_t revision_form{0};
    v27::TickOptions execution{v27::Backend::Lazy,1};
};

struct IntegratedOptions {
    Coordinate center{33,25,42};
    std::string guard_mode{"treatment"}; // none, treatment, sham
    bool revision_interfaces{true};
    std::uint16_t body_source_load{0};
    v27::TickOptions execution{v27::Backend::Lazy,1};
};

// No Runtime is created by a factory. create_world() creates one fresh owner;
// loading/attaching an existing world never calls a preparation factory.
// The flat maps are also the C++ counterpart of the Python geometry manifest.
struct NativePreparation {
    OrganizationRecipe recipe;
    std::string kind, domain;
    std::vector<FormDescriptor> forms;
    std::map<std::string,Coordinate> sites;
    std::map<std::string,Direction> directions;
    std::map<std::string,std::uint64_t> ticks;
    std::map<std::string,std::string> ports;
    std::map<std::string,std::int64_t> parameters;
    bool initial_state_available{};
    [[nodiscard]] OrganizationalWorld create_world() const;
};

[[nodiscard]] NativePreparation prepare_repertoire(const RepertoireOptions& options={});
[[nodiscard]] NativePreparation prepare_integrated_u0(const IntegratedOptions& options={});
// Descriptor-only restoration from inert, versioned recipe metadata. Does not
// call a preparation factory, allocate a Runtime, install matter or advance.
[[nodiscard]] NativePreparation preparation_for_world(const OrganizationalWorld& world);

// Explicit finite experience/probe protocols. They queue inputs only; none
// reads an old answer, selects a response, advances, clears or resets a world.
[[nodiscard]] std::vector<EventReceipt> experience_form(OrganizationalWorld& world,
    const NativePreparation& preparation, std::size_t form_index, int current_sign,
    std::uint64_t at_tick, std::uint16_t cue_load=5, std::uint16_t event_load=11);
[[nodiscard]] EventReceipt query_form(OrganizationalWorld& world,
    const NativePreparation& preparation, std::size_t form_index,
    std::uint16_t payload, std::uint64_t at_tick);
[[nodiscard]] std::vector<EventReceipt> revise_form(OrganizationalWorld& world,
    const NativePreparation& preparation, std::size_t form_index, int current_sign,
    std::uint64_t at_tick, const std::string& method="double_teacher",
    const std::string& mode="treatment", std::uint16_t cue_load=5,
    std::uint16_t event_load=11);

struct DirectionalReadout {
    Observation physical;
    std::optional<EventReceipt> receipt;
    bool applied{}, covered{}, ordinary_cap_reached{};
    std::optional<int> value;
    std::string status;
    std::string modality{"PASSIVE_OBSERVATION"};
    std::string scope{"Current exact physical fields plus declared receipt; not unique causal ancestry or a cached answer"};
};
[[nodiscard]] DirectionalReadout read_directional_response(const OrganizationalWorld& world,
    Coordinate site, std::uint64_t receipt_id, std::uint16_t probe_load,
    std::optional<std::uint64_t> expected_read_tick=std::nullopt);
[[nodiscard]] DirectionalReadout read_form_response(const OrganizationalWorld& world,
    const NativePreparation& preparation, std::size_t form_index,
    std::uint64_t receipt_id, std::uint16_t probe_load,
    std::optional<std::uint64_t> expected_read_tick=std::nullopt);

} // namespace dee::thinking::consolidated
