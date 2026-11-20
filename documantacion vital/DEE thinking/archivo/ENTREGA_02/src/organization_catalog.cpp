#include "dee_thinking/organization_catalog.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <stdexcept>
#include <utility>

namespace dee::thinking::catalog {

struct CatalogAssembler {
    static void add_port(OrganizationInstance& instance, PortSpec value) {
        instance.ports_.push_back({value,
            {instance.anchor_.x + value.relative_site.x,
             instance.anchor_.y + value.relative_site.y,
             instance.anchor_.z + value.relative_site.z}});
    }
    static void add_channel(OrganizationInstance& instance, std::string name, Coordinate site,
                            std::uint32_t state, Direction direction, bool experience = true,
                            bool probe = false, std::uint8_t semantic = 1) {
        instance.channels_.push_back({std::move(name), site, state, direction, semantic, experience, probe});
    }
    static void add_voxel(OrganizationInstance& instance, Coordinate site,
                          std::uint32_t state, std::uint16_t sreg, Direction direction,
                          std::uint8_t semantic, std::uint64_t clock, std::string purpose) {
        instance.initial_voxels_.push_back(
            {site, v27::pack_record(state, sreg, direction.dx, direction.dy, direction.dz, semantic),
             clock, std::move(purpose)});
    }
    static void add_landmark(OrganizationInstance& instance, std::string name, Coordinate relative) {
        instance.landmarks_.emplace(std::move(name),
            Coordinate{instance.anchor_.x + relative.x,
                       instance.anchor_.y + relative.y,
                       instance.anchor_.z + relative.z});
    }
};

namespace {

using Family = OrganizationFamily;

Coordinate plus(Coordinate left, Coordinate right) {
    return {left.x + right.x, left.y + right.y, left.z + right.z};
}

Coordinate scaled(Direction direction, int count) {
    return {direction.dx * count, direction.dy * count, direction.dz * count};
}

Coordinate source_for(Coordinate target, std::uint64_t tick, Direction direction) {
    if (tick > static_cast<std::uint64_t>(std::numeric_limits<int>::max())) {
        throw std::invalid_argument("tick is outside catalog coordinate range");
    }
    return plus(target, scaled(direction, -static_cast<int>(tick)));
}

ParameterSpec integer_parameter(std::string name, std::int64_t value,
                                std::int64_t minimum, std::int64_t maximum,
                                std::string meaning) {
    return {std::move(name), ParameterKind::Integer, value, minimum, maximum, {}, std::move(meaning)};
}

ParameterSpec boolean_parameter(std::string name, bool value, std::string meaning) {
    return {std::move(name), ParameterKind::Boolean, value ? 1 : 0, 0, 1, {}, std::move(meaning)};
}

ParameterSpec enumeration_parameter(std::string name, std::int64_t value,
                                    std::map<std::int64_t, std::string> values,
                                    std::string meaning) {
    const auto bounds = std::minmax_element(
        values.begin(), values.end(), [](const auto& left, const auto& right) { return left.first < right.first; });
    return {std::move(name), ParameterKind::Enumeration, value,
            bounds.first->first, bounds.second->first, std::move(values), std::move(meaning)};
}

PortSpec port(std::string name, PortRole role, ContributionKind contribution,
              Coordinate site, std::optional<Direction> direction,
              std::uint64_t tick, std::uint16_t minimum_load,
              std::uint16_t maximum_load, bool transforms, std::string timing) {
    return {std::move(name), role, contribution, site, direction, tick, tick,
            minimum_load, maximum_load, transforms, std::move(timing)};
}

OrganizationDescriptor descriptor(
    std::string id, std::string version, std::vector<Family> families,
    Availability availability, std::string mechanism, std::string reference,
    std::string summary, std::vector<ParameterSpec> parameters,
    std::vector<PortSpec> ports, std::string preparation, std::string resources,
    std::string query_effects, std::string interference,
    std::string retention, std::string domain, std::string pending = {}) {
    OrganizationDescriptor result{
        std::move(id), std::move(version), std::move(families), availability,
        std::move(mechanism), std::move(reference), std::move(summary),
        std::move(parameters), std::move(ports), std::move(preparation),
        std::move(resources), std::move(query_effects), std::move(interference),
        std::move(retention), std::move(domain), std::move(pending)};
    result.initial_footprint = result.preparation;
    result.functional_relation = result.query_effects;
    std::string reads;
    for (const auto& value : result.ports) {
        if (value.role != PortRole::PassiveReadout) continue;
        if (!reads.empty()) reads += "; ";
        reads += value.name + "@(" + std::to_string(value.relative_site.x) + "," +
                 std::to_string(value.relative_site.y) + "," +
                 std::to_string(value.relative_site.z) + ")";
    }
    result.read_region = reads.empty() ? "No passive readout is declared by this component." : reads;
    result.required_context = result.resources + " " + result.possible_interference;
    result.context_horizon = result.tested_domain + " " + result.retention_and_saturation;
    return result;
}

Direction axis_direction(std::int64_t code) {
    switch (code) {
        case 0: return {1, 0, 0};
        case 1: return {-1, 0, 0};
        case 2: return {0, 1, 0};
        case 3: return {0, -1, 0};
        case 4: return {0, 0, 1};
        case 5: return {0, 0, -1};
        default: throw std::invalid_argument("invalid direction_code");
    }
}

std::map<std::string, std::int64_t> validated_parameters(
    const OrganizationDescriptor& value,
    const std::map<std::string, std::int64_t>& supplied) {
    std::map<std::string, std::int64_t> result;
    for (const auto& spec : value.parameters) result.emplace(spec.name, spec.default_value);
    for (const auto& [name, parameter_value] : supplied) {
        const auto found = std::find_if(value.parameters.begin(), value.parameters.end(),
                                        [&](const auto& spec) { return spec.name == name; });
        if (found == value.parameters.end()) {
            throw std::invalid_argument("unknown parameter '" + name + "' for " + value.id);
        }
        if (parameter_value < found->minimum || parameter_value > found->maximum) {
            throw std::invalid_argument("parameter '" + name + "' outside admitted range");
        }
        if (found->kind == ParameterKind::Enumeration && !found->enumeration.contains(parameter_value)) {
            throw std::invalid_argument("parameter '" + name + "' is not an admitted enumeration value");
        }
        result[name] = parameter_value;
    }
    return result;
}

}  // namespace

namespace {
void add_port(OrganizationInstance& value, PortSpec port_value) {
    CatalogAssembler::add_port(value, std::move(port_value));
}
void add_channel(OrganizationInstance& value, std::string name, Coordinate site,
                 std::uint32_t state, Direction direction, bool experience = true,
                 bool probe = false, std::uint8_t semantic = 1) {
    CatalogAssembler::add_channel(value, std::move(name), site, state, direction, experience, probe, semantic);
}
void add_voxel(OrganizationInstance& value, Coordinate site,
               std::uint32_t state, std::uint16_t sreg, Direction direction,
               std::uint8_t semantic, std::uint64_t clock, std::string purpose) {
    CatalogAssembler::add_voxel(value, site, state, sreg, direction, semantic, clock, std::move(purpose));
}
void add_landmark(OrganizationInstance& value, std::string name, Coordinate relative) {
    CatalogAssembler::add_landmark(value, std::move(name), relative);
}
}  // namespace

const InstancePort* OrganizationInstance::find_port(const std::string& name) const noexcept {
    const auto found = std::find_if(ports_.begin(), ports_.end(),
                                    [&](const auto& value) { return value.contract.name == name; });
    return found == ports_.end() ? nullptr : &*found;
}

ResourceBudget OrganizationInstance::resource_budget() const noexcept {
    ResourceBudget result;
    result.initial_voxels = initial_voxels_.size();
    result.input_channels = channels_.size();
    result.declared_ports = ports_.size();
    for (const auto& voxel : initial_voxels_) {
        if (v27::decode_record(voxel.raw).semantic == 4U) ++result.persistent_sources;
    }
    for (const auto& value : ports_) {
        if (value.contract.role == PortRole::InternalOutput ||
            value.contract.role == PortRole::UpdateInput ||
            value.contract.role == PortRole::ContextInterface) {
            result.declared_connection_capacity += value.contract.maximum_connections;
        }
    }
    return result;
}

OrganizationCatalog::OrganizationCatalog() {
    descriptors_.push_back(descriptor(
        "transport.axis.v1", "1.0.0", {Family::TransportRedirection}, Availability::Available,
        "DEE v27 directional carrier transport and toroidal arrival",
        "DEE thinking Entrega 01 E1; CORE05 transport lineage",
        "One admitted carrier propagates on one representable axis; zero load remains a present carrier.",
        {integer_parameter("distance", 5, 1, 20, "Transitions from admission site to readout"),
         enumeration_parameter("direction_code", 0,
                               {{0, "+x"}, {1, "-x"}, {2, "+y"}, {3, "-y"}, {4, "+z"}, {5, "-z"}},
                               "Representable axis direction")},
        {port("carrier", PortRole::ExperienceInput, ContributionKind::Carrier, {}, Direction{1, 0, 0},
              0, 0, v27::kReducerCap, true, "Admission occurs at the requested boundary"),
         port("arrival", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {5, 0, 0},
              Direction{1, 0, 0}, 5, 0, v27::kReducerCap, false, "Read at the configured distance")},
        "Empty transport corridor; the planner does not create a barrier around it.",
        "One admitted carrier; load zero and absence are distinct.",
        "Observation is passive; an occupied destination can change or suppress the expected arrival.",
        "Other proposals, toroidal returns, and occupied destinations can interfere.",
        "The witness is finite-horizon transport, not indefinite storage.",
        "Axis directions; distance 1..20; validated on toroidal worlds large enough to avoid unintended wrap."));

    descriptors_.push_back(descriptor(
        "relation_learning.c6h01.v1", "1.0.0", {Family::RelationalLearning}, Availability::Available,
        "CORE06 C6H01 paired cue/teacher collision and mobile learned relation",
        "CORE06 C6H01 F0_T0; Entrega 01 make_reprogramming_world nomenclature correction",
        "A cue and an explicit teacher meet at a fixed junction; their DEE reducer product is later queryable.",
        {},
        {port("cue", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {3, 0, 0},
              Direction{-1, 0, 0}, 0, 0, v27::kReducerCap, true, "Schedule at boundary 0"),
         port("teacher", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {-3, -3, 0},
              Direction{1, 1, 0}, 0, 0, v27::kReducerCap, true, "Schedule at boundary 0; teacher role is explicit"),
         port("learned_relation", PortRole::InternalOutput, ContributionKind::MobileRelation, {},
              Direction{0, 1, 0}, 3, 0, v27::kReducerCap, true, "Product exists at the junction after three transitions")},
        "Fixed junction geometry, with cue and teacher admitted through separate public channels.",
        "One cue and one teacher carrier.",
        "The later query is transformating; no non-destructive RAM behavior is claimed.",
        "Additional proposals on the junction or learned path alter the relation.",
        "Retention is mobile and limited to the tested path/horizon.",
        "N>=17 witness; cue/teacher boundary 0, relation at t=3."));

    descriptors_.push_back(descriptor(
        "relation_query.c6h01.v1", "1.0.0", {Family::RelationalLearning}, Availability::Available,
        "CORE06 C6H01 later query of a mobile learned relation",
        "CORE06 C6H01 F0_T0; Entrega 01 reference test E2",
        "A separately admitted query meets the learned relation at a declared response site.",
        {},
        {port("relation_input", PortRole::UpdateInput, ContributionKind::MobileRelation, {},
              Direction{0, 1, 0}, 11, 0, v27::kReducerCap, true, "Expected mobile relation arrival at t=11"),
         port("query", PortRole::QueryInput, ContributionKind::CollisionProposal, {5, 0, 0},
              Direction{-1, 0, 0}, 6, 0, v27::kReducerCap, true, "Admit after advancing to boundary 6"),
         port("response", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {},
              std::nullopt, 11, 0, v27::kReducerCap, false, "Observe the common response site at t=11")},
        "Place the reader anchor eight +y cells from the learner junction.",
        "One later query carrier; the learned carrier is supplied by a physical connection.",
        "The query participates in the reducer and therefore changes the world.",
        "Wrong age, path, phase, or another proposal at the response site changes the outcome.",
        "Only the fixed C6H01 timing and compatible loads are supported.",
        "Query admitted at boundary 6; response at boundary 11."));

    descriptors_.push_back(descriptor(
        "mobile_lineage.c7h03.v1", "1.0.0",
        {Family::RelationalLearning, Family::FunctionalUpdateTransfer}, Availability::Available,
        "C7H03 mobile reprogrammable lineage training segment",
        "PENSAMIENTO 01 run_native_consequence_reprogramming.py; C7H03 lineage",
        "Paired training proposals create a mobile relation and expose a physical update encounter at t=12.",
        {},
        {port("cue", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {-5, 0, 0},
              Direction{1, 0, 0}, 0, 0, v27::kReducerCap, true, "Admit at boundary 0"),
         port("teacher", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {5, -5, 0},
              Direction{-1, 1, 0}, 0, 0, v27::kReducerCap, true, "Admit at boundary 0"),
         port("mobile_relation", PortRole::InternalOutput, ContributionKind::MobileRelation, {0, 7, 0},
              Direction{0, 1, 0}, 12, 0, v27::kReducerCap, true, "Relation reaches the update site at t=12"),
         port("update_input", PortRole::UpdateInput, ContributionKind::CollisionProposal, {0, 7, 0},
              Direction{1, -1, 0}, 12, 0, v27::kReducerCap, true, "Native update proposal must meet the relation at t=12"),
         port("updated_relation", PortRole::InternalOutput, ContributionKind::MobileRelation, {0, 7, 0},
              Direction{1, 0, 0}, 12, 0, v27::kReducerCap, true, "Conditional reducer product after a valid update encounter")},
        "The training junction is the instance anchor; all proposal sources are public channels.",
        "Training cue and teacher plus a separately connected update proposal.",
        "Subsequent reads remain transformating.",
        "The updated output is conditional on survival and exact simultaneous arrival.",
        "s_reg is capped by v27; the witness does not establish unlimited reprogramming.",
        "N=127 reference geometry; t=5 training, t=12 update."));

    descriptors_.push_back(descriptor(
        "native_update_bridge.p01.v1", "1.0.0", {Family::FunctionalUpdateTransfer}, Availability::Available,
        "Native supply/marker consequence transported into a C7H03 update encounter",
        "PENSAMIENTO 01 run_native_consequence_reprogramming.py",
        "Common supply and optional marker collide natively; the product reaches the lineage update port.",
        {},
        {port("supply", PortRole::SupplyInput, ContributionKind::CollisionProposal, {-12, 19, 0},
              Direction{1, -1, 0}, 0, 0, v27::kReducerCap, true, "Admit at boundary 0"),
         port("marker", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {-4, 19, 0},
              Direction{0, -1, 0}, 0, 0, v27::kReducerCap, true, "Presence and load zero are separate cases"),
         port("cut_update_link", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {0, 7, -12},
              Direction{0, 0, 1}, 0, 0, v27::kReducerCap, true,
              "Optional declared control proposal reroutes the t=12 update product away from the query path"),
         port("native_update", PortRole::InternalOutput, ContributionKind::CollisionProposal, {0, 7, 0},
              Direction{1, -1, 0}, 12, 0, v27::kReducerCap, true, "Consequence product arrives at lineage update site at t=12")},
        "The anchor is the C7H03 training junction; supply and marker use fixed physical routes.",
        "Supply and marker are explicit resources; the history determines whether marker is admitted.",
        "No readout is performed by this component; it creates a physical update proposal.",
        "Off-path marker, absent supply, or extra proposals change the consequence.",
        "Loads can saturate at the v27 cap; no normalization or recycling is performed.",
        "N=127 geometry, consequence t=8, update t=12."));

    descriptors_.push_back(descriptor(
        "query_recurrence.p01.v1", "1.0.0", {Family::RecurrenceLaterUse}, Availability::Available,
        "Fixed query/redirect train acting on an updated mobile lineage",
        "PENSAMIENTO 01 run_native_consequence_reprogramming.py",
        "The updated lineage is redirected through three transformating query encounters.",
        {},
        {port("updated_relation_input", PortRole::UpdateInput, ContributionKind::MobileRelation, {0, 7, 0},
              Direction{1, 0, 0}, 12, 0, v27::kReducerCap, true, "Updated lineage starts from this physical site"),
         port("program_redirect", PortRole::SupplyInput, ContributionKind::CollisionProposal, {24, -11, 0},
              Direction{-1, 1, 0}, 0, 0, v27::kReducerCap, true, "Prepared redirect admitted at boundary 0"),
         port("query1", PortRole::QueryInput, ContributionKind::CollisionProposal, {-28, 23, 0},
              Direction{1, 0, 0}, 0, 0, v27::kReducerCap, true, "Finite query train input admitted at boundary 0"),
         port("query_redirect1", PortRole::SupplyInput, ContributionKind::CollisionProposal, {48, 27, 0},
              Direction{-1, 0, 0}, 0, 0, v27::kReducerCap, true, "First query redirect admitted at boundary 0"),
         port("query2", PortRole::QueryInput, ContributionKind::CollisionProposal, {-36, 35, 0},
              Direction{1, 0, 0}, 0, 0, v27::kReducerCap, true, "Finite query train input admitted at boundary 0"),
         port("query_redirect2", PortRole::SupplyInput, ContributionKind::CollisionProposal, {64, 39, 0},
              Direction{-1, 0, 0}, 0, 0, v27::kReducerCap, true, "Second query redirect admitted at boundary 0"),
         port("query3", PortRole::QueryInput, ContributionKind::CollisionProposal, {-44, 47, 0},
              Direction{1, 0, 0}, 0, 0, v27::kReducerCap, true, "Finite query train input admitted at boundary 0"),
         port("response1", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {6, 23, 0},
              std::nullopt, 34, 0, v27::kReducerCap, false, "First query encounter"),
         port("response2", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {10, 35, 0},
              std::nullopt, 46, 0, v27::kReducerCap, false, "Second query encounter"),
         port("response3", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {14, 47, 0},
              std::nullopt, 58, 0, v27::kReducerCap, false, "Third query encounter")},
        "Redirects and query carriers are admitted through declared channels at boundary 0.",
        "Finite query/redirect train; it is not a source of indefinite autonomous queries.",
        "Every query adds its load to the mobile lineage and changes it.",
        "Missing redirects, occupied paths, or saturation can terminate the chain.",
        "Three uses are the tested finite horizon; no unlimited sustainability claim.",
        "N=127, responses t=34,46,58."));

    descriptors_.push_back(descriptor(
        "relative_history.i02.v1", "1.0.0", {Family::RelativeMemoryHistorySelection}, Availability::Available,
        "Relative early/late history carriers around two persistent context centers",
        "Ingenieria 02; PENSAMIENTO/Procesos contextual helper inherited by Entrega 01",
        "HA and HB use equal inventory but exchange which temporal contribution is already at its target.",
        {enumeration_parameter("history_mode", 1, {{0, "H0"}, {1, "HA"}, {2, "HB"}},
                               "Prepared history witness")},
        {port("context", PortRole::ContextInterface, ContributionKind::ContextCondition, {},
              std::nullopt, 0, 0, v27::kReducerCap, true, "Shares the declared context anchor"),
         port("history_state", PortRole::InternalOutput, ContributionKind::ContextCondition, {},
              std::nullopt, 0, 0, v27::kReducerCap, true, "Causal effect requires common-age simulation")},
        "Requires the distributed_context.i05.v1 scaffold at the same anchor.",
        "Two state=0 but RAW-nonzero temporal carriers in HA/HB; H0 omits them.",
        "The reader and downstream recurrence are transformating physical interactions.",
        "Changing age or deleting the distributed scaffold changes the question.",
        "Finite prepared history witness; not a general temporal-memory compiler.",
        "N>=31 scaffold; HA/HB common inventory, exchanged early/late order."));

    descriptors_.push_back(descriptor(
        "contextual_multichannel_recurrence.p02.v1", "1.0.0",
        {Family::MultichannelIntegrationSeparation, Family::RecurrenceLaterUse}, Availability::Available,
        "A/B/C collision consequence coupled to a history-conditioned recurrence port",
        "Procesos 02; Entrega 01 make_recurrence_multichannel_world",
        "A/B/C channels remain separate until a native encounter; AB and ABC are distinct from channel absence and load zero.",
        {},
        {port("context_input", PortRole::ContextInterface, ContributionKind::ContextCondition, {},
              std::nullopt, 0, 0, v27::kReducerCap, true, "Requires the preserved contextual scaffold/history"),
         port("A", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {3, 9, -6},
              Direction{0, -1, 1}, 0, 0, v27::kReducerCap, true, "Admit at boundary 0"),
         port("B", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {3, 9, 6},
              Direction{0, -1, -1}, 0, 0, v27::kReducerCap, true, "Admit at boundary 0"),
         port("C", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {3, 9, 0},
              Direction{0, -1, 0}, 0, 0, v27::kReducerCap, true, "Admit at boundary 0"),
         port("cut_link", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {5, 1, -8},
              Direction{0, 0, 1}, 0, 0, v27::kReducerCap, true, "Declared causal cut admitted at boundary 0"),
         port("sham_link", PortRole::ExperienceInput, ContributionKind::CollisionProposal, {5, 2, -8},
              Direction{0, 0, 1}, 0, 0, v27::kReducerCap, true,
              "Matched zero-load trajectory parallel to the cut; it misses the redirect site over the measured window"),
         port("q_response", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {9, 1, 0},
              std::nullopt, 12, 0, v27::kReducerCap, false, "Read the recurrent q site at common age t=12")},
        "Anchor matches the distributed context center; recurrence support is preinstalled in the same world.",
        "A/B/C carriers, one redirect proposal, q carrier, and four semantic=4 persistent sources.",
        "The response is a physical recurrent interaction, not an arithmetic merge in the runtime.",
        "History, channel timing, and cut-link interventions alter the same landscape.",
        "Finite horizon and v27 cap; periodic return alone is not claimed as learned recurrence.",
        "N=127 witness; A/B/C consequence t=6, redirect t=8, q readout t=12."));

    descriptors_.push_back(descriptor(
        "distributed_context.i05.v1", "1.0.0", {Family::DistributedContextMemory}, Availability::Available,
        "Two-center distributed scaffold and reader retained as physical context",
        "Ingenieria 05/06 NRD contextual apparatus; Procesos 02 inherited helper",
        "Persistent semantic=4 support and two material centers form a non-scalar context used by later interactions.",
        {},
        {port("context_output", PortRole::ContextInterface, ContributionKind::ContextCondition, {},
              std::nullopt, 0, 0, v27::kReducerCap, true, "Context is spatially distributed around the anchor"),
         port("reader_initial", PortRole::PassiveReadout, ContributionKind::PassiveObservation, {0, -2, 0},
              Direction{0, 1, 0}, 0, 0, v27::kReducerCap, false, "Initial physical reader position")},
        "Two centers, eight support records, and one reader; no enclosing box is implied.",
        "Prepared support remains part of the world and can interfere with other organizations.",
        "The reader is not a non-invasive abstract observer; Runtime::observe is the passive observer.",
        "Copying only one center would discard causal context and is not supported.",
        "Finite apparatus with no claim that all modified support is necessary or capacity-consuming.",
        "N>=31; intended shared-anchor use with relative_history and contextual recurrence."));

    descriptors_.push_back(descriptor(
        "temporal_phase_memory.core05.pending", "0.0.0", {Family::RelativeMemoryHistorySelection},
        Availability::Pending,
        "CORE05 encounter-phase temporal memory",
        "CORE05 primary implementation/fixture not yet ported into Entrega 02",
        "Catalog entry retained so phase memory is not silently replaced by s_reg accumulation.",
        {}, {}, "Not available as a builder.", "NOT_RECORDED in this port.",
        "Not available.", "Requires exact source/fixture reconstruction before public exposure.",
        "No executable domain declared.", "PENDING: exact CORE05 constructor and reserved-case oracle are not in the Entrega 01 native source set."));
}

const OrganizationDescriptor* OrganizationCatalog::find(const std::string& id) const noexcept {
    const auto found = std::find_if(descriptors_.begin(), descriptors_.end(),
                                    [&](const auto& value) { return value.id == id; });
    return found == descriptors_.end() ? nullptr : &*found;
}

OrganizationInstance OrganizationCatalog::instantiate(const OrganizationRequest& request) const {
    const auto* selected = find(request.catalog_id);
    if (selected == nullptr) throw std::invalid_argument("unknown organization: " + request.catalog_id);
    if (selected->availability != Availability::Available) {
        throw std::logic_error("organization is pending and has no builder: " + request.catalog_id);
    }
    if (request.instance_id.empty()) throw std::invalid_argument("instance_id cannot be empty");

    OrganizationInstance result;
    result.descriptor_ = *selected;
    result.instance_id_ = request.instance_id;
    result.anchor_ = request.anchor;
    result.parameters_ = validated_parameters(*selected, request.parameters);

    if (selected->id == "transport.axis.v1") {
        const auto direction = axis_direction(result.parameters_.at("direction_code"));
        const auto distance = static_cast<int>(result.parameters_.at("distance"));
        add_channel(result, "carrier", {}, 1, direction, true, true);
        auto input = selected->ports.at(0);
        input.direction = direction;
        auto output = selected->ports.at(1);
        output.relative_site = scaled(direction, distance);
        output.direction = direction;
        output.earliest_tick = output.latest_tick = static_cast<std::uint64_t>(distance);
        add_port(result, std::move(input));
        add_port(result, std::move(output));
        add_landmark(result, "input", {});
        add_landmark(result, "arrival", scaled(direction, distance));
    } else if (selected->id == "relation_learning.c6h01.v1") {
        add_channel(result, "cue", {3, 0, 0}, 1, {-1, 0, 0});
        add_channel(result, "teacher", {-3, -3, 0}, 1, {1, 1, 0});
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "training_junction", {});
    } else if (selected->id == "relation_query.c6h01.v1") {
        add_channel(result, "query", {5, 0, 0}, 1, {-1, 0, 0}, true, true);
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "response", {});
    } else if (selected->id == "mobile_lineage.c7h03.v1") {
        add_channel(result, "cue", {-5, 0, 0}, 81001, {1, 0, 0});
        add_channel(result, "teacher", {5, -5, 0}, 81002, {-1, 1, 0});
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "junction", {});
        add_landmark(result, "program_site", {0, 7, 0});
    } else if (selected->id == "native_update_bridge.p01.v1") {
        add_channel(result, "supply", {-12, 19, 0}, 81003, {1, -1, 0});
        add_channel(result, "marker", {-4, 19, 0}, 81004, {0, -1, 0});
        add_channel(result, "cut_update_link", {0, 7, -12}, 81006, {0, 0, 1});
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "consequence_site", {-4, 11, 0});
        add_landmark(result, "program_site", {0, 7, 0});
    } else if (selected->id == "query_recurrence.p01.v1") {
        constexpr Direction cue{1, 0, 0};
        constexpr Direction redirect{-1, 1, 0};
        constexpr Direction query_redirect{-1, 0, 0};
        const std::array<Coordinate, 3> receivers{{{6, 23, 0}, {10, 35, 0}, {14, 47, 0}}};
        const std::array<std::uint64_t, 3> query_ticks{{34, 46, 58}};
        const std::array<Coordinate, 2> redirect_sites{{{10, 27, 0}, {14, 39, 0}}};
        const std::array<std::uint64_t, 2> redirect_ticks{{38, 50}};
        add_channel(result, "program_redirect", source_for({6, 7, 0}, 18, redirect), 81005, redirect);
        for (std::size_t i = 0; i < receivers.size(); ++i) {
            add_channel(result, "query" + std::to_string(i + 1), source_for(receivers[i], query_ticks[i], cue),
                        81101 + static_cast<std::uint32_t>(i), cue);
        }
        for (std::size_t i = 0; i < redirect_sites.size(); ++i) {
            add_channel(result, "query_redirect" + std::to_string(i + 1),
                        source_for(redirect_sites[i], redirect_ticks[i], query_redirect),
                        81201 + static_cast<std::uint32_t>(i), query_redirect);
        }
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "program_site", {0, 7, 0});
        add_landmark(result, "response1", receivers[0]);
        add_landmark(result, "response2", receivers[1]);
        add_landmark(result, "response3", receivers[2]);
    } else if (selected->id == "distributed_context.i05.v1") {
        const Coordinate a{-1, 0, 0};
        const Coordinate b{1, 0, 0};
        add_voxel(result, a, 1000, 100, {}, 1, 260, "context center A");
        add_voxel(result, b, 2000, 100, {}, 1, 260, "context center B");
        constexpr std::array<Direction, 4> pattern_a{{{-1, 0, 0}, {-1, 1, 1}, {0, 0, 1}, {0, 1, 0}}};
        constexpr std::array<Direction, 4> pattern_b{{{0, -1, 0}, {0, 0, -1}, {1, -1, -1}, {1, 0, 0}}};
        for (std::size_t i = 0; i < pattern_a.size(); ++i) {
            add_voxel(result, plus(a, scaled(pattern_a[i], 1)), 3000 + static_cast<std::uint32_t>(i),
                      0, {}, 4, 31 + i, "persistent support A");
            add_voxel(result, plus(b, scaled(pattern_b[i], 1)), 4000 + static_cast<std::uint32_t>(i),
                      0, {}, 4, 41 + i, "persistent support B");
        }
        add_voxel(result, {0, -2, 0}, 6000, 7, {0, 1, 0}, 4, 23, "context reader");
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "center", {});
        add_landmark(result, "reader_initial", {0, -2, 0});
        add_landmark(result, "reader_after_one", {0, -1, 0});
    } else if (selected->id == "relative_history.i02.v1") {
        const auto mode = result.parameters_.at("history_mode");
        auto install = [&](Coordinate memory, Coordinate offset, Direction direction,
                           bool early, std::uint32_t state) {
            const auto target = plus(memory, offset);
            if (early) add_voxel(result, target, state, 0, direction, 1, 17, "early history carrier");
            else add_voxel(result, plus(target, scaled(direction, -1)), 0, 0, direction, 1, 19,
                           "late state-zero RAW-nonzero history carrier");
        };
        if (mode == 1) {
            install({-1, 0, 0}, {0, -1, 0}, {0, 0, -1}, true, 5000);
            install({1, 0, 0}, {0, 1, 0}, {0, 0, 1}, false, 5001);
        } else if (mode == 2) {
            install({-1, 0, 0}, {0, -1, 0}, {0, 0, -1}, false, 5000);
            install({1, 0, 0}, {0, 1, 0}, {0, 0, 1}, true, 5001);
        }
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "history_center", {});
    } else if (selected->id == "contextual_multichannel_recurrence.p02.v1") {
        constexpr Direction p{1, 0, 0};
        constexpr Direction s1{-1, 1, 0}, s2{-1, -1, 0};
        constexpr Direction n1{1, 0, 1}, n2{1, 0, -1};
        const Coordinate consequence{3, 3, 0};
        const Coordinate redirect{5, 1, 0};
        const Coordinate q{9, 1, 0};
        const Coordinate qp{10, 1, 0};
        add_voxel(result, source_for(redirect, 8, {0, 1, 0}), 90010, 0, {0, 1, 0}, 1, 0,
                  "fixed redirect proposal");
        add_voxel(result, q, 1, 7, p, 1, 11, "recurrent q carrier");
        add_voxel(result, plus(qp, scaled(s1, -1)), 91000, 11, s1, 4, 100000, "persistent source s1");
        add_voxel(result, plus(qp, scaled(s2, -1)), 91001, 13, s2, 4, 100001, "persistent source s2");
        add_voxel(result, plus(q, scaled(n1, -2)), 91002, 17, n1, 4, 100002, "persistent source n1");
        add_voxel(result, plus(q, scaled(n2, -2)), 91003, 19, n2, 4, 100003, "persistent source n2");
        add_channel(result, "A", source_for(consequence, 6, {0, -1, 1}), 90001, {0, -1, 1});
        add_channel(result, "B", source_for(consequence, 6, {0, -1, -1}), 90002, {0, -1, -1});
        add_channel(result, "C", source_for(consequence, 6, {0, -1, 0}), 90003, {0, -1, 0});
        add_channel(result, "cut_link", source_for(redirect, 8, {0, 0, 1}), 90020, {0, 0, 1});
        add_channel(result, "sham_link", source_for({5, 2, 0}, 8, {0, 0, 1}), 90020, {0, 0, 1});
        for (const auto& value : selected->ports) add_port(result, value);
        add_landmark(result, "consequence", consequence);
        add_landmark(result, "redirect", redirect);
        add_landmark(result, "q", q);
        add_landmark(result, "qp", qp);
    } else {
        throw std::logic_error("available catalog entry has no builder: " + selected->id);
    }
    return result;
}

const char* to_string(OrganizationFamily value) noexcept {
    switch (value) {
        case Family::TransportRedirection: return "TRANSPORT_REDIRECTION";
        case Family::RelationalLearning: return "RELATIONAL_LEARNING";
        case Family::FunctionalUpdateTransfer: return "FUNCTIONAL_UPDATE_TRANSFER";
        case Family::RelativeMemoryHistorySelection: return "RELATIVE_MEMORY_HISTORY_SELECTION";
        case Family::MultichannelIntegrationSeparation: return "MULTICHANNEL_INTEGRATION_SEPARATION";
        case Family::RecurrenceLaterUse: return "RECURRENCE_LATER_USE";
        case Family::DistributedContextMemory: return "DISTRIBUTED_CONTEXT_MEMORY";
    }
    return "UNKNOWN";
}

const char* to_string(Availability value) noexcept {
    return value == Availability::Available ? "AVAILABLE" : "PENDING";
}

const char* to_string(PortRole value) noexcept {
    switch (value) {
        case PortRole::ExperienceInput: return "EXPERIENCE_INPUT";
        case PortRole::QueryInput: return "QUERY_INPUT";
        case PortRole::UpdateInput: return "UPDATE_INPUT";
        case PortRole::SupplyInput: return "SUPPLY_INPUT";
        case PortRole::PassiveReadout: return "PASSIVE_READOUT";
        case PortRole::InternalOutput: return "INTERNAL_OUTPUT";
        case PortRole::ContextInterface: return "CONTEXT_INTERFACE";
    }
    return "UNKNOWN";
}

const char* to_string(ContributionKind value) noexcept {
    switch (value) {
        case ContributionKind::Carrier: return "CARRIER";
        case ContributionKind::CollisionProposal: return "COLLISION_PROPOSAL";
        case ContributionKind::MobileRelation: return "MOBILE_RELATION";
        case ContributionKind::ContextCondition: return "CONTEXT_CONDITION";
        case ContributionKind::PassiveObservation: return "PASSIVE_OBSERVATION";
    }
    return "UNKNOWN";
}

}  // namespace dee::thinking::catalog
