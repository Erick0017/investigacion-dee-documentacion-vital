#pragma once
#include "dee_thinking/basal.hpp"
#include "dee_thinking/composition.hpp"
#include "dee_thinking/observation.hpp"
#include <array>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace dee::thinking {

enum class OperationModality : std::uint8_t {
    NativeEvolution=1, ExperienceProtocol=2, PassiveObservation=3,
    PhysicalProbe=4, DiagnosticFork=5, AssistedReconstruction=6
};
enum class CodecType : std::uint8_t { BoundedInteger=1, Boolean=2, Enumeration=3, RegisteredPattern=4 };

struct InputCodec {
    std::string version{"1.0.0"};
    CodecType type{CodecType::BoundedInteger};
    std::int64_t minimum{};
    std::int64_t maximum{65535};
    std::map<std::string,std::uint16_t> symbols;
    // A registered pattern is an external name for a fixed physical load on
    // the declared ChannelSpec, not a meaning learnt by the Runtime.
    [[nodiscard]] std::uint16_t encode_integer(std::int64_t value) const;
    [[nodiscard]] std::uint16_t encode_symbol(const std::string& value) const;
    [[nodiscard]] bool injective() const;
    void validate() const;
};
struct InterfaceSpec {
    std::string name;
    ChannelSpec channel;
    InputCodec codec;
    std::string admission{"Runtime scheduled boundary; occupied/conflict rejection"};
    std::string meaning_location{"external application contract only"};
};
struct DecodedOutput {
    Observation physical;
    std::optional<std::int64_t> integer;
    std::vector<std::string> symbols;
    bool available{};
    bool ambiguous{};
    bool ordinary_cap_reached{};
    std::string status;
};
struct OutputDecoder {
    std::string version{"1.0.0"};
    CodecType type{CodecType::BoundedInteger};
    std::map<std::string,std::uint16_t> symbols;
    [[nodiscard]] DecodedOutput decode(const Observation& observation) const;
};

struct InitialPlacement {
    Coordinate site;
    std::uint64_t raw{};
    std::uint64_t clock{};
    std::string role;
};
struct OrganizationSpec {
    std::string id;
    std::string recipe_id;
    std::map<std::string,Coordinate> ports;
    std::vector<Coordinate> supports;
    std::optional<Coordinate> a, b, comparator;
    std::uint64_t t0_tick{};
};
struct ActionCoupling {
    std::string id;
    std::vector<Coordinate> sites;
    std::vector<std::string> roles;
    std::vector<std::uint64_t> observation_ticks;
    std::string scope{"declared native routes; no callback writes"};
};
struct OrganizationRecipe {
    std::string id;
    std::string version{"1.0.0"};
    int dimension{34};
    Coordinate origin{};
    std::map<std::string,std::int64_t> parameters;
    std::map<std::string,std::string> options;
    std::vector<InitialPlacement> placements;
    std::vector<InterfaceSpec> interfaces;
    std::vector<OrganizationSpec> organizations;
    std::vector<ActionCoupling> actions;
    v27::TickOptions execution{v27::Backend::Lazy,1};
    std::uint64_t t0_tick{};
    std::string domain;
    // Published factories produce recipes, never evolved answers.
    [[nodiscard]] static OrganizationRecipe mobile_pair(Coordinate translation={});
    [[nodiscard]] static OrganizationRecipe cascade(int depth=4, Coordinate translation={});
    [[nodiscard]] static OrganizationRecipe phase(int mode=0, Coordinate origin={15,15,15});
    [[nodiscard]] static OrganizationRecipe distributed(int history_mode=1, Coordinate origin={30,30,30});
    [[nodiscard]] static OrganizationRecipe relational(std::string seed, basal::History history=basal::History::AB,
                                                      bool keep_reader=false, Coordinate origin={15,15,15});
    [[nodiscard]] static OrganizationRecipe contextual(std::string seed, Coordinate origin={15,15,15});
    [[nodiscard]] static OrganizationRecipe mobile_basal(std::string seed, basal::History history=basal::History::AB,
                                                       Coordinate origin={15,15,15});
    [[nodiscard]] static OrganizationRecipe native_transfer(Coordinate translation={});
    [[nodiscard]] static OrganizationRecipe contingent(std::string seed, Coordinate origin={15,15,15});
    [[nodiscard]] static OrganizationRecipe information(std::string seed, basal::History history=basal::History::AB,
                                                      std::uint16_t hidden=23, Coordinate origin={15,15,15});
    [[nodiscard]] static OrganizationRecipe competition(Coordinate translation={});
    [[nodiscard]] static OrganizationRecipe predictive(Coordinate translation={});
    [[nodiscard]] static OrganizationRecipe research(int dimension, std::vector<InitialPlacement> placements,
                                                  std::uint64_t tick=0);
};

struct FunctionalReadout {
    std::string organization_id;
    std::uint64_t tick{}, relative_tick{};
    std::map<std::string,Observation> observations;
    std::optional<std::int64_t> delta;
    bool centers_available{}, reader_available{}, supports_intact{};
    std::optional<int> axis_projection;
    std::string scope{"declared finite panel; no ontological adjudication"};
};
struct ResilienceObservation {
    FunctionalReadout functional;
    std::vector<Coordinate> missing_supports;
    std::vector<std::string> ordinary_cap_sites, representable_cap_sites;
    std::string recovery_claim{"not inferred by this passive observer"};
};
struct TraceSample {
    std::string id;
    std::uint64_t tick{};
    Observation observation;
    Coordinate relative_to_origin;
    std::array<std::int64_t,3> unwrapped{};
    std::string coverage;
};
struct MobileSegment {
    std::string id;
    Coordinate birth_site;
    Direction direction;
    std::uint64_t birth_tick{}, last_tick{};
    std::optional<std::uint16_t> expected_load;
    std::optional<std::uint8_t> expected_semantic;
    bool correspondence_stopped{};
};
struct TraceSession {
    std::size_t sample_budget{4096};
    bool capture_stopped{};
    std::map<std::string,Coordinate> sites;
    std::vector<MobileSegment> segments;
    std::vector<TraceSample> samples;
    void capture(const Runtime& runtime, Coordinate origin={});
    void export_trace(const std::string& path) const;
    [[nodiscard]] static TraceSession load_trace(const std::string& path);
};
struct EncounterObservation {
    std::uint64_t tick_before{}, tick_after{};
    Coordinate destination;
    Observation before, after;
    std::vector<Observation> direct_ballistic_contributors;
    observation::WriteGate destination_gate;
    std::string attribution_scope{"direct ballistic proposals only; material/DEMUX dependencies not fully attributed"};
    std::string branch;
};
[[nodiscard]] EncounterObservation observe_encounter(const Runtime& before, const Runtime& after, Coordinate destination);

struct DiagnosticEditReceipt {
    Coordinate site;
    std::string label;
    std::uint64_t tick{}, raw_before{}, raw_after{}, clock_before{}, clock_after{};
    OperationModality modality{OperationModality::DiagnosticFork};
};
struct ReconstructionSpec {
    std::vector<Coordinate> source_sites, destination_sites;
    bool copy_raw{true}, copy_clocks{false};
    bool authorize_assisted_reconstruction{};
};
struct QueryStep {
    std::uint64_t input_tick{}, read_tick{};
    std::int64_t input{};
    std::vector<std::uint64_t> receipt_ids;
    std::vector<Coordinate> targets;
    std::vector<Observation> captured;
};
struct QueryProtocol {
    std::string id;
    std::string kind;
    OperationModality modality{OperationModality::PhysicalProbe};
    std::vector<QueryStep> steps;
    std::size_t next_capture{};
};

struct OrganizationalState;
class OrganizationView {
public:
    [[nodiscard]] const OrganizationSpec& spec() const;
    [[nodiscard]] Runtime& runtime() const;
    [[nodiscard]] FunctionalReadout observe() const;
    [[nodiscard]] ResilienceObservation resilience() const;
private:
    OrganizationView(std::shared_ptr<OrganizationalState> state, std::string id);
    std::shared_ptr<OrganizationalState> state_;
    std::string id_;
    friend class OrganizationalWorld;
};

class OrganizationalWorld {
public:
    [[nodiscard]] static OrganizationalWorld create(const OrganizationRecipe& recipe);
    // Inert attach retains a shared owner and only validates/describes existing
    // Runtime state. It neither installs records nor registers channels.
    [[nodiscard]] static OrganizationalWorld attach(std::shared_ptr<Runtime> runtime,
                                                    OrganizationRecipe recipe,
                                                    std::vector<OrganizationSpec> specs);
    [[nodiscard]] static OrganizationalWorld load_snapshot(const std::string& path);
    [[nodiscard]] Runtime& runtime() const;
    [[nodiscard]] const OrganizationRecipe& recipe() const;
    [[nodiscard]] std::vector<std::string> organization_ids() const;
    [[nodiscard]] OrganizationView view(const std::string& id) const;
    [[nodiscard]] std::vector<InterfaceSpec> interfaces() const;
    void declare_interface(InterfaceSpec spec); // explicit protocol operation
    EventReceipt submit(const std::string& name, std::int64_t value, std::uint64_t at_tick);
    EventReceipt submit_symbol(const std::string& name, const std::string& value, std::uint64_t at_tick);
    EventReceipt probe(const std::string& name, std::int64_t value, std::uint64_t at_tick);
    EventReceipt probe_symbol(const std::string& name, const std::string& value, std::uint64_t at_tick);
    [[nodiscard]] Observation observe(const std::string& organization, const std::string& port) const;
    [[nodiscard]] DecodedOutput decode(const std::string& organization, const std::string& port,
                                       const OutputDecoder& decoder) const;
    void declare_decoder(std::string name, OutputDecoder decoder);
    [[nodiscard]] OutputDecoder decoder(const std::string& name) const;
    v27::TickInfo advance(std::uint64_t count=1);
    v27::TickInfo run_until(std::uint64_t absolute_tick);
    void start_mobile_sequence(const std::string& id, const std::vector<std::int64_t>& inputs,
                               std::uint64_t first_tick=6, std::uint64_t interval=5);
    [[nodiscard]] const std::vector<QueryProtocol>& protocols() const;
    [[nodiscard]] OrganizationalWorld fork() const;
    [[nodiscard]] OrganizationalWorld diagnostic_fork(const std::vector<ResearchStateEdit>& edits, bool authorize) const;
    [[nodiscard]] OrganizationalWorld assisted_reconstruction(const OrganizationalWorld& source,
                                                              const ReconstructionSpec& spec) const;
    [[nodiscard]] const std::vector<DiagnosticEditReceipt>& diagnostic_edits() const;
    [[nodiscard]] const std::vector<std::string>& external_operations() const;
    void set_trace(TraceSession trace);
    [[nodiscard]] TraceSession trace() const;
    void capture_trace();
    void save_snapshot(const std::string& path, bool include_trace=true) const;
private:
    explicit OrganizationalWorld(std::shared_ptr<OrganizationalState> state) : state_(std::move(state)) {}
    std::shared_ptr<OrganizationalState> state_;
};
[[nodiscard]] const char* to_string(OperationModality value) noexcept;
} // namespace dee::thinking
