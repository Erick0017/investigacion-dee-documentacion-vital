#pragma once
#include "dee_thinking/organizational.hpp"
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking {

// The barrier and the meanings of its input codes are an EXTERNAL interface.
// Only current observations enter Runtime; a forecast/error never selects input.
struct CognitiveParameters {
    std::string seed_path;
    std::string profile{"continuity"}; // continuity or comparison (one episode)
    Coordinate origin{15,15,15};
    bool initial_open{};
    std::optional<std::uint64_t> change_tick{80};
    std::uint32_t event_state{1};
    v27::TickOptions execution{v27::Backend::Lazy,1};
    std::size_t journal_limit{32768};
    std::size_t prediction_limit{4096};
};
struct CognitiveCall {
    std::uint64_t tick{}, target_tick{}, receipt_id{};
    std::string operation, scope, channel, source;
    std::optional<std::uint16_t> value;
};
struct BarrierSample {
    std::uint64_t tick{};
    bool arrived{}, reference_branch{};
    std::string observable{"packet_arrival_at_barrier_output"};
    std::string modality{"OBSERVED_EXTERNAL_ENVIRONMENT"};
};
struct CognitivePrediction {
    std::uint64_t id{}, emission_tick{}, target_tick{};
    Observation physical_output;
    std::vector<bool> prediction_set;
    std::optional<EventReceipt> receipt;
    bool evaluated{};
    std::string modality;
};
struct CognitiveEvaluation {
    std::uint64_t prediction_id{}, emission_tick{}, target_tick{};
    bool actual{}, singleton{};
    std::optional<bool> error;
    std::string modality{"ANALISIS_EXTERNO_NOT_INPUT"};
};
struct CognitiveComparison {
    Observation physical_output;
    bool signed_comparison_marker_present{}, represented_expectation_before_report{};
    bool report_applied{}, within_window{};
    std::string presentation, validity;
    std::string scope{"one singleton expectation/current consequence; no general error memory"};
};
struct CognitiveReadout {
    std::uint64_t tick{};
    FunctionalReadout memory;
    Observation physical_output, a, b;
    observation::WriteGate gate_a, gate_b;
    std::vector<bool> prediction_set;
    std::string profile, comparison_stage, forecast_domain, domain_status;
    std::optional<CognitiveComparison> comparison;
};
struct CognitiveResult {
    std::string kind, status, modality, detail;
    std::uint64_t tick{};
    CognitiveReadout readout;
    std::vector<EventReceipt> receipts;
    std::vector<BarrierSample> samples;
    std::vector<CognitiveEvaluation> evaluations;
    std::optional<CognitivePrediction> prediction;
    std::optional<CognitiveComparison> comparison;
};

class CognitiveSession {
public:
    CognitiveSession(CognitiveSession&&) noexcept = default;
    CognitiveSession& operator=(CognitiveSession&&) noexcept = default;
    [[nodiscard]] static CognitiveSession create(CognitiveParameters parameters);
    [[nodiscard]] static CognitiveSession load_snapshot(const std::string& path);
    // Explicit legacy PHYSICAL import: no restoration of unparsed CPC3 Python
    // protocol state and no preparation of missing channels/history.
    [[nodiscard]] static Runtime load_legacy_physical_snapshot(const std::string& path);
    [[nodiscard]] OrganizationalWorld& world() noexcept { return world_; }
    [[nodiscard]] const OrganizationalWorld& world() const noexcept { return world_; }
    [[nodiscard]] std::uint64_t tick() const noexcept;
    [[nodiscard]] std::uint64_t preferred_horizon() const noexcept;
    [[nodiscard]] const CognitiveParameters& parameters() const noexcept { return parameters_; }
    [[nodiscard]] const std::vector<CognitiveCall>& journal() const noexcept { return journal_; }
    [[nodiscard]] const std::vector<CognitivePrediction>& predictions() const noexcept { return predictions_; }
    [[nodiscard]] const std::vector<BarrierSample>& samples() const noexcept { return samples_; }
    [[nodiscard]] CognitiveReadout observe() const;
    CognitiveResult experience(const std::string& symbol);
    CognitiveResult sense();
    CognitiveResult predict(std::uint64_t horizon=0);
    CognitiveResult compare();
    CognitiveResult advance(std::uint64_t ticks=1);
    CognitiveResult run_until(std::uint64_t absolute_tick);
    // Explicit diagnostic copy only. No session protocol calls this method.
    [[nodiscard]] CognitiveSession fork() const;
    void save_snapshot(const std::string& path, bool include_trace=true);
    void set_interface_metadata(const std::string& key, const std::string& value);
    [[nodiscard]] std::optional<std::string> get_interface_metadata(const std::string& key) const;
    [[nodiscard]] const std::map<std::string,std::string>& interface_metadata() const noexcept { return interface_metadata_; }
private:
    // A plain C++ copy must not silently alias one Runtime with two protocols.
    CognitiveSession(const CognitiveSession&) = default;
    CognitiveSession& operator=(const CognitiveSession&) = default;
    CognitiveSession(OrganizationalWorld world, CognitiveParameters parameters);
    OrganizationalWorld world_;
    CognitiveParameters parameters_;
    std::vector<CognitiveCall> journal_;
    std::vector<CognitivePrediction> predictions_;
    std::vector<BarrierSample> samples_;
    std::map<std::string,std::string> interface_metadata_;
    bool reader_primed_{}, past_pair_presented_{};
    std::size_t slot_index_{};
    std::string comparison_stage_{"ready"}, expectation_invalidated_;
    std::optional<std::size_t> pending_prediction_;
    std::optional<std::uint64_t> last_report_tick_;
    bool last_comparison_valid_{};
    void log(CognitiveCall call);
    void advance_to(std::uint64_t absolute_tick);
    [[nodiscard]] bool barrier_at(std::uint64_t tick) const;
    BarrierSample sample(bool reference=false);
    [[nodiscard]] std::optional<std::uint64_t> next_slot();
    CognitiveResult input(const std::string& key, std::uint64_t when, const std::string& source);
    CognitiveResult result(std::string kind, std::string status, std::string modality, std::string detail={}) const;
    [[nodiscard]] CognitiveComparison comparison_readout(bool valid, bool applied) const;
    [[nodiscard]] std::vector<CognitiveEvaluation> evaluate_due();
    [[nodiscard]] std::string serialize() const;
    void deserialize(const std::string& bytes);
};

struct NativeAssociationParameters {
    Coordinate translation{};
    v27::TickOptions execution{v27::Backend::Lazy,1};
};
struct AssociationResponse {
    std::string operation, modality, scope;
    std::uint64_t input_tick{}, tick{};
    std::vector<EventReceipt> receipts;
    std::map<std::string,Observation> outputs;
    std::map<std::string,std::optional<std::uint16_t>> decoded;
};
class NativeAssociationSession {
public:
    NativeAssociationSession(NativeAssociationSession&&) noexcept = default;
    NativeAssociationSession& operator=(NativeAssociationSession&&) noexcept = default;
    [[nodiscard]] static NativeAssociationSession create(NativeAssociationParameters parameters={});
    [[nodiscard]] static NativeAssociationSession load_snapshot(const std::string& path);
    [[nodiscard]] OrganizationalWorld& world() noexcept { return world_; }
    [[nodiscard]] const OrganizationalWorld& world() const noexcept { return world_; }
    [[nodiscard]] std::uint64_t tick() const noexcept { return world_.runtime().current_tick(); }
    AssociationResponse train(const std::vector<std::uint16_t>& teachers, std::uint16_t cue=5,
                              const std::string& mode="paired");
    AssociationResponse query(int port, std::uint16_t payload=13);
    AssociationResponse query_panel(std::uint16_t payload=13);
    void start_sequence(const std::vector<std::int64_t>& payloads,
                        const std::string& protocol_id="association_sequence", std::uint64_t first_tick=6);
    void advance(std::uint64_t count=1);
    void run_until(std::uint64_t absolute_tick);
    [[nodiscard]] AssociationResponse observe() const;
    [[nodiscard]] NativeAssociationSession fork() const;
    void save_snapshot(const std::string& path, bool include_trace=true);
    void set_interface_metadata(const std::string& key, const std::string& value);
    [[nodiscard]] std::optional<std::string> get_interface_metadata(const std::string& key) const;
    [[nodiscard]] const std::map<std::string,std::string>& interface_metadata() const noexcept { return metadata_; }
private:
    NativeAssociationSession(const NativeAssociationSession&) = default;
    NativeAssociationSession& operator=(const NativeAssociationSession&) = default;
    explicit NativeAssociationSession(OrganizationalWorld world) : world_(std::move(world)) {}
    OrganizationalWorld world_;
    std::map<std::string,std::string> metadata_;
};
// Empty native cascade with the actual online cue/teacher interfaces installed
// before T0. Pairs are acquired by v27, not assigned as learned state.
[[nodiscard]] OrganizationalWorld create_learnable_cascade(int depth=2, Coordinate translation={},
    v27::TickOptions execution={v27::Backend::Lazy,1});
[[nodiscard]] std::vector<EventReceipt> experience_composition(OrganizationalWorld& world,
    const std::vector<std::pair<std::uint16_t,std::uint16_t>>& pairs,
    std::optional<std::size_t> omit=std::nullopt);
[[nodiscard]] AssociationResponse query_composition(OrganizationalWorld& world, std::uint16_t payload);

} // namespace dee::thinking
