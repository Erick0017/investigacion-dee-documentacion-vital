#pragma once

#include "dee_thinking/organizational.hpp"
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking {

// These source roles describe an explicit prepared environment. They are not
// passed to a native policy chooser or used by the output decoder.
enum class SourceRole : std::uint8_t { PInformative=1, QInformative=2 };

struct FinitePolicyParameters {
    Coordinate origin{30,30,30};
    SourceRole roles{SourceRole::QInformative};
    int actual_class{1};
    bool actual_enabled{true};
    v27::TickOptions execution{v27::Backend::Lazy,1};
};

struct NativeInformationParameters {
    std::string seed_path;
    Coordinate origin{15,15,15};
    basal::History history{basal::History::AB};
    int context{};
    int actual_class{1};
    std::uint16_t information_load{23};
    bool query_enabled{true}, actual_enabled{true}, source_enabled{true};
    bool post_query{true};
    std::string source_cut; // empty, "P" or "Q"; initial preparation control
    int distance{10};
    v27::TickOptions execution{v27::Backend::Lazy,1};
};

struct InformativeOperation {
    std::uint64_t tick{};
    std::string operation, interface_name;
    std::int64_t value{};
    std::optional<std::uint64_t> receipt_id;
    OperationModality modality{OperationModality::ExperienceProtocol};
};

struct PhysicalCandidate {
    std::string port, source, presentation;
    Observation physical;
    std::optional<std::int64_t> value;
};

struct InformationReadout {
    std::uint64_t tick{};
    std::string profile, status, scope;
    OperationModality modality{OperationModality::PassiveObservation};
    std::vector<PhysicalCandidate> comparisons, policies, actions, information, later_responses;
    std::map<std::string,Observation> physical_outputs;
    std::vector<EventReceipt> receipts;
    std::optional<int> current_prediction;
    std::optional<std::int64_t> delta;
    bool centers_available{}, supports_intact{};
    bool journal_truncated{};
};

// One continuing N67 Runtime and one finite, consumed-resource policy revision.
// The retain-P / switch-Q update rule and binary complementary sources are
// prepared, not themselves learnt. Only the explicit current actual report is
// submitted later; no externally calculated error or action is injected.
class FinitePolicySession {
public:
    [[nodiscard]] static FinitePolicySession create(FinitePolicyParameters parameters={});
    [[nodiscard]] static FinitePolicySession load_snapshot(const std::string& path);
    FinitePolicySession(FinitePolicySession&&) noexcept = default;
    FinitePolicySession& operator=(FinitePolicySession&&) noexcept = default;
    FinitePolicySession(const FinitePolicySession&) = delete;
    FinitePolicySession& operator=(const FinitePolicySession&) = delete;
    [[nodiscard]] std::uint64_t tick() const;
    [[nodiscard]] OrganizationalWorld& world() { return world_; }
    [[nodiscard]] const FinitePolicyParameters& parameters() const { return parameters_; }
    [[nodiscard]] const std::vector<InformativeOperation>& journal() const { return journal_; }
    [[nodiscard]] InformationReadout observe() const;
    InformationReadout advance(std::uint64_t count=1);
    InformationReadout run_until(std::uint64_t absolute_tick);
    InformationReadout compare();
    InformationReadout source();
    InformationReadout sense();
    // Explicit sensor operation, allowed only at the declared current boundary.
    // It accepts a present binary report, not an absence inferred by timeout.
    std::vector<EventReceipt> submit_actual(int actual_class);
    void process_boundary();
    [[nodiscard]] FinitePolicySession fork() const;
    [[nodiscard]] FinitePolicySession diagnostic_fork(const std::vector<ResearchStateEdit>& edits, bool authorize) const;
    void save_snapshot(const std::string& path, bool include_trace=true) const;
    void set_interface_metadata(std::map<std::string,std::string> metadata);
    void set_interface_metadata(std::string key, std::string value);
    [[nodiscard]] std::optional<std::string> get_interface_metadata(const std::string& key) const;
    [[nodiscard]] const std::map<std::string,std::string>& interface_metadata() const { return interface_metadata_; }
private:
    FinitePolicySession(OrganizationalWorld world, FinitePolicyParameters parameters);
    void append(InformativeOperation operation);
    OrganizationalWorld world_;
    FinitePolicyParameters parameters_;
    bool actual_submitted_{};
    bool journal_truncated_{};
    std::vector<InformativeOperation> journal_;
    std::map<std::string,std::string> interface_metadata_;
};

// A distinct N47 individual: online A/B history -> native emission -> physical
// comparison -> P/Q route -> acquired information -> common later query.
// It is not fused with CognitiveSession and does not claim utility learning or
// indefinite reuse. All physical mediators are prepared before T0 (tick32).
class NativeInformationSession {
public:
    [[nodiscard]] static NativeInformationSession create(NativeInformationParameters parameters);
    [[nodiscard]] static NativeInformationSession load_snapshot(const std::string& path);
    NativeInformationSession(NativeInformationSession&&) noexcept = default;
    NativeInformationSession& operator=(NativeInformationSession&&) noexcept = default;
    NativeInformationSession(const NativeInformationSession&) = delete;
    NativeInformationSession& operator=(const NativeInformationSession&) = delete;
    [[nodiscard]] std::uint64_t tick() const;
    [[nodiscard]] OrganizationalWorld& world() { return world_; }
    [[nodiscard]] const NativeInformationParameters& parameters() const { return parameters_; }
    [[nodiscard]] const std::vector<InformativeOperation>& journal() const { return journal_; }
    [[nodiscard]] InformationReadout observe() const;
    InformationReadout advance(std::uint64_t count=1);
    InformationReadout run_until(std::uint64_t absolute_tick);
    InformationReadout compare();
    InformationReadout source();
    InformationReadout sense();
    std::vector<EventReceipt> submit_actual(int actual_class);
    void process_boundary();
    [[nodiscard]] NativeInformationSession fork() const;
    [[nodiscard]] NativeInformationSession diagnostic_fork(const std::vector<ResearchStateEdit>& edits, bool authorize) const;
    void save_snapshot(const std::string& path, bool include_trace=true) const;
    void set_interface_metadata(std::map<std::string,std::string> metadata);
    void set_interface_metadata(std::string key, std::string value);
    [[nodiscard]] std::optional<std::string> get_interface_metadata(const std::string& key) const;
    [[nodiscard]] const std::map<std::string,std::string>& interface_metadata() const { return interface_metadata_; }
private:
    NativeInformationSession(OrganizationalWorld world, NativeInformationParameters parameters);
    void append(InformativeOperation operation);
    OrganizationalWorld world_;
    NativeInformationParameters parameters_;
    std::vector<std::string> executed_;
    bool journal_truncated_{};
    std::vector<InformativeOperation> journal_;
    std::map<std::string,std::string> interface_metadata_;
};

} // namespace dee::thinking
