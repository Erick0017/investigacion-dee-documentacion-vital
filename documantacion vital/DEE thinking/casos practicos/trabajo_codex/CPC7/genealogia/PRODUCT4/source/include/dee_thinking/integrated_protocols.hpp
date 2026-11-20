#pragma once

#include "dee_thinking/runtime.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking::protocols {

inline constexpr const char* kH1Id = "delay_position_bank.core05.nrh05.v1";
inline constexpr const char* kH2Id = "destination_repertoires.core07.c7h02.v1";
inline constexpr const char* kH3Id = "trained_redundancy_repair.core17.v1";
inline constexpr const char* kH4Id = "accessibility.history_conditioned_finite_response.v1";
inline constexpr const char* kF1Id = "reusable_lineage_revision.c7h03.v1";
inline constexpr const char* kF2Id = "environmental_demux_return.v1";

enum class ProtocolModality : std::uint8_t {
    NativePostHostStop = 1,
    Coupled = 2,
    Diagnostic = 3,
};

struct ProtocolResourceBudget {
    std::size_t initial_carriers{};
    std::size_t persistent_supports{};
    std::size_t declared_inputs{};
    std::size_t read_sites{};
    bool resources_consumable{};
};

struct ProtocolPortDescriptor {
    std::string name;
    std::string role;
    std::string timing;
    std::uint16_t minimum_load{};
    std::uint16_t maximum_load{v27::kReducerCap};
    bool transforms_world{};
};

// Protocol registry is deliberately separate from OrganizationCatalog: H4 is
// an external diagnostic contract, while H3 includes an opt-in damage action.
struct IntegratedProtocolDescriptor {
    std::string id;
    std::string version{"1.0.0"};
    ProtocolModality modality{ProtocolModality::NativePostHostStop};
    std::string scientific_source;
    std::string summary;
    std::string tested_domain;
    std::string limits;
    ProtocolResourceBudget resources;
    std::vector<ProtocolPortDescriptor> ports;
    std::vector<std::string> labels;
};

[[nodiscard]] const std::vector<IntegratedProtocolDescriptor>&
integrated_protocol_descriptors();
[[nodiscard]] const IntegratedProtocolDescriptor* find_integrated_protocol(
    const std::string& id) noexcept;

struct ProtocolReceipt {
    std::string label;
    EventReceipt receipt;
};

struct ProtocolObservation {
    std::string label;
    Observation observation;
};

// H1 — CORE05 NRD05/NRH05 bounded delay-to-position transduction.
enum class DelayPositionArm : std::uint8_t {
    Native = 0,
    ReversedCalibration = 1,
    TargetAbsent = 2,
};

struct DelayPositionConfig {
    int dimension{59};
    Coordinate base{13, 17, 19};
    Direction bank_axis{0, 1, 0};
    int channel_spacing{5};
    int base_path_length{12};
    std::vector<int> labels{-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5};
    Direction target_direction{1, 0, 0};
    Direction probe_direction{0, 0, 1};
    int input_delay{};
    DelayPositionArm arm{DelayPositionArm::Native};
    std::array<std::uint16_t, 2> loads{321, 654};
    std::array<std::uint32_t, 2> states{1001, 2003};
    std::array<std::uint64_t, 2> phases{0x123456789abcdef0ULL,
                                        0xfedcba9876543210ULL};
};

struct DelayPositionDetection {
    std::uint64_t tick{};
    int label{};
    v27::Record record{};
};

struct DelayPositionResult {
    bool initial_hubs_empty{};
    std::optional<int> measurement;
    std::vector<int> active_labels;
    std::vector<DelayPositionDetection> merged_events;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] DelayPositionResult run_delay_position(
    const DelayPositionConfig& config,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
void save_delay_position_checkpoint(
    const DelayPositionConfig& config, std::uint64_t stop_at_tick,
    const std::string& path,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
[[nodiscard]] DelayPositionResult resume_delay_position_checkpoint(
    const std::string& path,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});

// H2 — CORE07 C7H02 separated and deliberately overlapping repertoires.
struct SeparatedRepertoireConfig {
    int dimension{79};
    std::size_t channels{3};
    Coordinate translation{2, 5, 7};
    std::uint16_t base_offset{4096};
    std::vector<int> delta_cycle{-6, -3, 1, 4, 8};
    std::uint16_t query_base{151};
    int training_tick{5};
    int query_tick{19};
    int query_path{5};
};

struct SeparatedRepertoireResult {
    bool ports_empty{};
    std::size_t exact_channels{};
    bool all_exact{};
    bool training_budget_exact{};
    bool read_budget_exact{};
    bool load_accounting_exact{};
    std::vector<std::uint16_t> observed_responses;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

struct OverlapRepertoireConfig {
    int dimension{71};
    int geometry_index{};
    std::array<int, 2> deltas{-5, 2};
    std::uint16_t query_load{17};
    bool off_fiber{};
    std::uint16_t base_offset{4096};
    int training_tick{5};
    int merge_tick{14};
    int query_tick{22};
};

struct OverlapRepertoireResult {
    bool port_empty{};
    bool merge_exact{};
    bool composed_response_exact{};
    bool individual_identity_preserved{};
    bool false_merge{};
    std::uint16_t observed_merge_load{};
    std::uint16_t observed_response_load{};
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] SeparatedRepertoireResult run_separated_repertoire(
    const SeparatedRepertoireConfig& config,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
[[nodiscard]] OverlapRepertoireResult run_overlap_repertoire(
    const OverlapRepertoireConfig& config,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
void save_separated_repertoire_checkpoint(
    const SeparatedRepertoireConfig& config, std::uint64_t stop_at_tick,
    const std::string& path,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
[[nodiscard]] SeparatedRepertoireResult resume_separated_repertoire_checkpoint(
    const std::string& path,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
void save_overlap_repertoire_checkpoint(
    const OverlapRepertoireConfig& config, std::uint64_t stop_at_tick,
    const std::string& path,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});
[[nodiscard]] OverlapRepertoireResult resume_overlap_repertoire_checkpoint(
    const std::string& path,
    v27::TickOptions options = {v27::Backend::DenseSequential, 1});

// H3 — CORE17 repair from a second, independently trained relation.
// Diagnostic damage is never implicit: callers must opt in explicitly.
enum class RepairArm : std::uint8_t {
    Treatment = 0,
    BackupUntrained = 1,
    BackupDirectionReset = 2,
    NoBackup = 3,
    PathCut = 4,
    OffpathCut = 5,
    WrongReceiver = 6,
};

struct RepairGeometry {
    std::string id{"fresh_like_00"};
    int dimension{31};
    int primary_distance{7};
    int backup_distance{7};
    std::array<int, 3> permutation{2, 1, 0};
    std::array<int, 3> signs{-1, 1, -1};
    Coordinate receiver{15, 15, 15};
};

struct RepairConfig {
    RepairGeometry geometry{};
    RepairArm arm{RepairArm::Treatment};
    bool authorize_diagnostic_damage{};
    std::uint32_t preparation_tag{1721000};
};

struct RepairResult {
    bool backup_learned{};
    bool primary_function_before_damage{};
    bool damage_applied{};
    bool function_lost_after_damage{};
    bool reconstructed_at_arrival{};
    bool fresh_function{};
    bool primary_source_depleted{};
    bool backup_source_depleted{};
    std::uint16_t query_load{};
    Direction query_direction{};
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] RepairResult run_trained_redundancy_repair(
    const RepairConfig& config,
    v27::TickOptions options = {v27::Backend::Lazy, 4});
void save_trained_redundancy_repair_checkpoint(
    const RepairConfig& config, std::uint64_t stop_after_tick,
    const std::string& path,
    v27::TickOptions options = {v27::Backend::Lazy, 4});
[[nodiscard]] RepairResult resume_trained_redundancy_repair_checkpoint(
    const std::string& path,
    v27::TickOptions options = {v27::Backend::Lazy, 4});

// H4 — finite diagnostic over precomputed observer readings. It never mutates
// a Runtime and never claims universal reachability.
enum class AccessibilityStatus : std::uint8_t {
    Constructed = 1,
    Reached = 2,
    Acquired = 3,
    NotDemonstrated = 4,
};

struct AccessibilityReading {
    Coordinate site{};
    std::uint64_t raw{};
    std::uint64_t clock{};
};

struct AccessibilityCase {
    std::string history_id;
    std::uint64_t baseline_tick{};
    std::uint64_t challenged_tick{};
    std::vector<AccessibilityReading> baseline;
    std::vector<AccessibilityReading> challenged;
    AccessibilityStatus history_status{AccessibilityStatus::NotDemonstrated};
    bool history_reached_natively{};
    bool challenge_applied_to_diagnostic_clone{true};
};

struct AccessibilityRequest {
    std::string observer_id;
    std::string challenge_id;
    bool apparatus_frozen{true};
    bool challenge_frozen{true};
    bool ages_aligned{true};
    std::vector<AccessibilityCase> cases;
};

struct AccessibilityEffect {
    std::string history_id;
    std::size_t raw_changed_sites{};
    std::size_t clock_changed_sites{};
    std::vector<std::int32_t> s_reg_deltas;
    AccessibilityStatus status{AccessibilityStatus::NotDemonstrated};
};

struct AccessibilityResult {
    bool comparable{};
    bool history_conditioned_response{};
    std::vector<AccessibilityEffect> effects;
    std::vector<std::string> diagnostics;
};

[[nodiscard]] AccessibilityResult analyze_accessibility(
    const AccessibilityRequest& request);

// F1 — two externally supplied revisions retained and used by one C7H03
// mobile lineage. All carriers in the validated contract are prepared at t0.
struct ReusableRevisionConfig {
    std::string id{"REV_11_13"};
    std::uint16_t revision1{11};
    std::uint16_t revision2{13};
    std::uint16_t sham1{};
    std::uint16_t sham2{};
    bool trained_relation{true};
};

struct ReusableRevisionResult {
    std::array<std::uint16_t, 3> response_loads{};
    std::array<std::uint16_t, 2> post_revision_loads{};
    bool all_inputs_applied_at_t0{};
    bool backend_fallback{};
    std::vector<ProtocolReceipt> receipts;
    std::vector<ProtocolObservation> checkpoints;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] ReusableRevisionResult run_reusable_revision(
    const ReusableRevisionConfig& config,
    v27::TickOptions options = {v27::Backend::Lazy, 4});
void save_reusable_revision_checkpoint(
    const ReusableRevisionConfig& config, std::uint64_t stop_at_tick,
    const std::string& path,
    v27::TickOptions options = {v27::Backend::Lazy, 4});
[[nodiscard]] ReusableRevisionResult resume_reusable_revision_checkpoint(
    const std::string& path,
    v27::TickOptions options = {v27::Backend::Lazy, 4});

// F2 — prepared, finite environmental mediation through the native DEMUX
// postpass. The +1 content is fixed by v27 DEMUX; it is not an arbitrary
// teacher supplied by the wrapper.
enum class EnvironmentalQueryMode : std::uint8_t {
    Intact = 0,
    Absent = 1,
    Sham = 2,
};

struct EnvironmentalReturnConfig {
    std::string id{"ENV_INTACT"};
    bool trained_response{true};
    std::uint16_t bias_load{15515};
    std::uint16_t marker_load{17};
    EnvironmentalQueryMode query_mode{EnvironmentalQueryMode::Intact};
    std::uint64_t environment_clock_phase{353};
};

struct EnvironmentalReturnResult {
    std::uint16_t upstream_response_load{};
    std::uint16_t environment_load{};
    std::array<std::uint16_t, 5> downstream_loads{};
    std::uint64_t overflow_total{};
    bool query_admitted{};
    bool all_inputs_applied_at_t0{};
    bool backend_fallback{};
    std::vector<ProtocolReceipt> receipts;
    std::vector<ProtocolObservation> checkpoints;
    std::vector<std::uint64_t> final_raw;
    std::vector<std::uint64_t> final_clock;
};

[[nodiscard]] EnvironmentalReturnResult run_environmental_return(
    const EnvironmentalReturnConfig& config,
    v27::TickOptions options = {v27::Backend::Lazy, 4});
void save_environmental_return_checkpoint(
    const EnvironmentalReturnConfig& config, std::uint64_t stop_at_tick,
    const std::string& path,
    v27::TickOptions options = {v27::Backend::Lazy, 4});
[[nodiscard]] EnvironmentalReturnResult resume_environmental_return_checkpoint(
    const std::string& path,
    v27::TickOptions options = {v27::Backend::Lazy, 4});

[[nodiscard]] const char* to_string(ProtocolModality value) noexcept;
[[nodiscard]] const char* to_string(DelayPositionArm value) noexcept;
[[nodiscard]] const char* to_string(RepairArm value) noexcept;
[[nodiscard]] const char* to_string(AccessibilityStatus value) noexcept;
[[nodiscard]] const char* to_string(EnvironmentalQueryMode value) noexcept;

}  // namespace dee::thinking::protocols
