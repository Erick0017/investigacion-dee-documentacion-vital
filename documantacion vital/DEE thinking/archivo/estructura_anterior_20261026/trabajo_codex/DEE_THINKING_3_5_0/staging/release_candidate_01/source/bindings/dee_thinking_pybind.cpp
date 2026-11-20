#include "dee_thinking/basal.hpp"
#include "dee_thinking/composition.hpp"
#include "dee_thinking/diagnostics.hpp"
#include "dee_thinking/genealogy.hpp"
#include "dee_thinking/integrated_protocols.hpp"
#include "dee_thinking/kernel_v27.hpp"
#include "dee_thinking/organization_catalog.hpp"
#include "dee_thinking/observation.hpp"
#include "dee_thinking/runtime.hpp"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdint>
#include <string>
#include <utility>

namespace py = pybind11;
namespace dt = dee::thinking;
namespace cat = dee::thinking::catalog;
namespace proto = dee::thinking::protocols;
namespace basal = dee::thinking::basal;
namespace obs = dee::thinking::observation;
namespace gen = dee::thinking::genealogy;
namespace diag = dee::thinking::diagnostics;
namespace v27 = dee::v27;

#ifndef DEE_THINKING_PYTHON_VERSION
#define DEE_THINKING_PYTHON_VERSION "3.5.0"
#endif

static_assert(PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION == 13,
              "DEE thinking 3.5.0 wheel contract requires CPython 3.13");

void bind_organizational(py::module_& m);

namespace {

template <typename Enum>
void add_string_repr(py::enum_<Enum>& binding, const char* (*formatter)(Enum) noexcept) {
    binding.def("__str__", [formatter](Enum value) { return std::string(formatter(value)); });
}

void bind_kernel(py::module_& m) {
    auto backend = py::enum_<v27::Backend>(m, "Backend")
        .value("DENSE_SEQUENTIAL", v27::Backend::DenseSequential)
        .value("DENSE_PARALLEL", v27::Backend::DenseParallel)
        .value("LAZY", v27::Backend::Lazy);
    add_string_repr(backend, v27::backend_name);

    py::enum_<v27::Semantic>(m, "Semantic")
        .value("VOID", v27::Semantic::Void)
        .value("NORMAL", v27::Semantic::Normal)
        .value("ELECTRON_SEED", v27::Semantic::ElectronSeed)
        .value("PROTON_SEED", v27::Semantic::ProtonSeed)
        .value("OBSERVER", v27::Semantic::Observer)
        .value("ORPHAN_BIT", v27::Semantic::OrphanBit)
        .value("HORIZON", v27::Semantic::Horizon)
        .value("BORN_XNOR", v27::Semantic::BornXnor);

    py::class_<v27::TickOptions>(m, "TickOptions")
        .def(py::init<>())
        .def(py::init<v27::Backend, std::size_t>(), py::arg("backend"), py::arg("threads") = 1)
        .def_readwrite("backend", &v27::TickOptions::backend)
        .def_readwrite("threads", &v27::TickOptions::threads);

    py::class_<v27::Record>(m, "Record")
        .def(py::init<>())
        .def_readonly("raw", &v27::Record::raw)
        .def_readonly("state", &v27::Record::state)
        .def_readonly("s_reg", &v27::Record::s_reg)
        .def_property_readonly("dx", [](const v27::Record& value) { return static_cast<int>(value.dx); })
        .def_property_readonly("dy", [](const v27::Record& value) { return static_cast<int>(value.dy); })
        .def_property_readonly("dz", [](const v27::Record& value) { return static_cast<int>(value.dz); })
        .def_property_readonly("semantic", [](const v27::Record& value) { return value.semantic; })
        .def_property_readonly("raw_present", &v27::Record::raw_present)
        .def_property_readonly("occupied", &v27::Record::occupied);

    py::class_<v27::TickInfo>(m, "TickInfo")
        .def(py::init<>())
        .def_readonly("overflows", &v27::TickInfo::overflows)
        .def_readonly("genesis", &v27::TickInfo::genesis)
        .def_readonly("evaluated", &v27::TickInfo::evaluated)
        .def_readonly("active_raw", &v27::TickInfo::active_raw)
        .def_readonly("total", &v27::TickInfo::total)
        .def_readonly("requested_backend", &v27::TickInfo::requested_backend)
        .def_readonly("used_backend", &v27::TickInfo::used_backend)
        .def_readonly("requested_threads", &v27::TickInfo::requested_threads)
        .def_readonly("used_threads", &v27::TickInfo::used_threads)
        .def_readonly("fallback", &v27::TickInfo::fallback)
        .def_readonly("preparation_ns", &v27::TickInfo::preparation_ns)
        .def_readonly("evaluation_ns", &v27::TickInfo::evaluation_ns)
        .def_readonly("postprocess_ns", &v27::TickInfo::postprocess_ns)
        .def_readonly("total_ns", &v27::TickInfo::total_ns);

    m.def("pack_record", &v27::pack_record,
          py::arg("state"), py::arg("s_reg"), py::arg("dx"), py::arg("dy"),
          py::arg("dz"), py::arg("semantic"));
    m.def("decode_record", &v27::decode_record, py::arg("raw"));
    m.def("linear_index", &v27::linear_index,
          py::arg("x"), py::arg("y"), py::arg("z"), py::arg("dimension"));
    m.def("wrap_coordinate", &v27::wrap_coordinate, py::arg("value"), py::arg("dimension"));
}

void bind_runtime(py::module_& m) {
    py::class_<dt::Coordinate>(m, "Coordinate")
        .def(py::init<>())
        .def(py::init<int, int, int>(), py::arg("x"), py::arg("y"), py::arg("z"))
        .def_readwrite("x", &dt::Coordinate::x)
        .def_readwrite("y", &dt::Coordinate::y)
        .def_readwrite("z", &dt::Coordinate::z)
        .def("__repr__", [](const dt::Coordinate& c) {
            return "Coordinate(x=" + std::to_string(c.x) + ", y=" +
                   std::to_string(c.y) + ", z=" + std::to_string(c.z) + ")";
        })
        .def("__eq__", [](const dt::Coordinate& a, const dt::Coordinate& b) { return a == b; });

    py::class_<dt::Direction>(m, "Direction")
        .def(py::init<>())
        .def(py::init<int, int, int>(), py::arg("dx"), py::arg("dy"), py::arg("dz"))
        .def_readwrite("dx", &dt::Direction::dx)
        .def_readwrite("dy", &dt::Direction::dy)
        .def_readwrite("dz", &dt::Direction::dz);

    auto event_kind = py::enum_<dt::EventKind>(m, "EventKind")
        .value("EXPERIENCE", dt::EventKind::Experience)
        .value("PROBE", dt::EventKind::Probe);
    add_string_repr(event_kind, dt::to_string);
    auto event_status = py::enum_<dt::EventStatus>(m, "EventStatus")
        .value("SCHEDULED", dt::EventStatus::Scheduled)
        .value("APPLIED", dt::EventStatus::Applied)
        .value("REJECTED_LATE", dt::EventStatus::RejectedLate)
        .value("REJECTED_INVALID", dt::EventStatus::RejectedInvalid)
        .value("REJECTED_OCCUPIED", dt::EventStatus::RejectedOccupied)
        .value("REJECTED_CONFLICT", dt::EventStatus::RejectedConflict)
        .value("REJECTED_QUEUE_FULL", dt::EventStatus::RejectedQueueFull);
    add_string_repr(event_status, dt::to_string);

    py::class_<dt::ChannelSpec>(m, "ChannelSpec")
        .def(py::init<>())
        .def_readwrite("name", &dt::ChannelSpec::name)
        .def_readwrite("injection_site", &dt::ChannelSpec::injection_site)
        .def_readwrite("state", &dt::ChannelSpec::state)
        .def_readwrite("direction", &dt::ChannelSpec::direction)
        .def_readwrite("semantic", &dt::ChannelSpec::semantic)
        .def_readwrite("allow_experience", &dt::ChannelSpec::allow_experience)
        .def_readwrite("allow_probe", &dt::ChannelSpec::allow_probe);

    py::class_<dt::InputRequest>(m, "InputRequest")
        .def(py::init<>())
        .def(py::init<std::string, std::uint16_t>(), py::arg("channel"), py::arg("s_reg"))
        .def_readwrite("channel", &dt::InputRequest::channel)
        .def_readwrite("s_reg", &dt::InputRequest::s_reg);

    py::class_<dt::EventReceipt>(m, "EventReceipt")
        .def(py::init<>())
        .def_readonly("id", &dt::EventReceipt::id)
        .def_readonly("kind", &dt::EventReceipt::kind)
        .def_readonly("status", &dt::EventReceipt::status)
        .def_readonly("requested_tick", &dt::EventReceipt::requested_tick)
        .def_readonly("effective_tick", &dt::EventReceipt::effective_tick)
        .def_readonly("channels", &dt::EventReceipt::channels)
        .def_readonly("reason", &dt::EventReceipt::reason);

    py::class_<dt::Observation>(m, "Observation")
        .def_readonly("tick", &dt::Observation::tick)
        .def_readonly("coordinate", &dt::Observation::coordinate)
        .def_readonly("raw", &dt::Observation::raw)
        .def_readonly("clock", &dt::Observation::clock)
        .def_readonly("record", &dt::Observation::record);

    py::class_<dt::WorldMetrics>(m, "WorldMetrics")
        .def_readonly("tick", &dt::WorldMetrics::tick)
        .def_readonly("raw_support", &dt::WorldMetrics::raw_support)
        .def_readonly("occupied", &dt::WorldMetrics::occupied)
        .def_readonly("s_reg_sum", &dt::WorldMetrics::s_reg_sum);

    py::class_<dt::ResearchStateEdit>(m, "ResearchStateEdit")
        .def(py::init<>())
        .def_readwrite("coordinate", &dt::ResearchStateEdit::coordinate)
        .def_readwrite("raw", &dt::ResearchStateEdit::raw)
        .def_readwrite("clock", &dt::ResearchStateEdit::clock)
        .def_readwrite("label", &dt::ResearchStateEdit::label);

    py::class_<dt::Runtime, std::shared_ptr<dt::Runtime>>(m, "Runtime")
        .def(py::init<int>(), py::arg("dimension"))
        .def_static("import_research_state", &dt::Runtime::import_research_state,
                    py::arg("dimension"), py::arg("tick"), py::arg("raw"), py::arg("clock"))
        .def_property_readonly("dimension", &dt::Runtime::dimension)
        .def_property_readonly("current_tick", &dt::Runtime::current_tick)
        .def_property_readonly("paused", &dt::Runtime::paused)
        .def_property("execution_options", &dt::Runtime::execution_options,
                      &dt::Runtime::set_execution_options)
        .def_property_readonly("last_tick_info", &dt::Runtime::last_tick_info,
                               py::return_value_policy::reference_internal)
        .def("register_channel", &dt::Runtime::register_channel, py::arg("channel"))
        .def_property_readonly("channel_names", &dt::Runtime::channel_names)
        .def("experience", &dt::Runtime::experience,
             py::arg("channel"), py::arg("at_tick"), py::arg("s_reg"))
        .def("experience_batch", &dt::Runtime::experience_batch,
             py::arg("inputs"), py::arg("at_tick"))
        .def("probe", &dt::Runtime::probe,
             py::arg("channel"), py::arg("at_tick"), py::arg("s_reg"))
        .def("receipt", &dt::Runtime::receipt, py::arg("event_id"))
        .def_property_readonly("receipts", &dt::Runtime::receipts)
        // The GIL intentionally remains held. Native DenseParallel workers still
        // run in C++, while Python cannot race a mutation/observation on one world.
        .def("advance", &dt::Runtime::advance, py::arg("count") = 1)
        .def("run_until", &dt::Runtime::run_until, py::arg("target_tick"))
        .def("pause", &dt::Runtime::pause)
        .def("resume", &dt::Runtime::resume)
        .def("observe", &dt::Runtime::observe, py::arg("coordinate"))
        .def("observe_many", &dt::Runtime::observe_many, py::arg("coordinates"))
        .def("metrics", &dt::Runtime::metrics)
        .def("fork", &dt::Runtime::fork)
        .def("diagnostic_fork", &dt::Runtime::diagnostic_fork,
             py::arg("edits"), py::arg("authorize_diagnostic_intervention"))
        .def("save_snapshot", &dt::Runtime::save_snapshot, py::arg("path"))
        .def_static("load_snapshot", &dt::Runtime::load_snapshot, py::arg("path"))
        .def("restore_snapshot", &dt::Runtime::restore_snapshot, py::arg("path"))
        .def("set_snapshot_metadata", &dt::Runtime::set_snapshot_metadata,
             py::arg("key"), py::arg("value"))
        .def("erase_snapshot_metadata", &dt::Runtime::erase_snapshot_metadata, py::arg("key"))
        .def("snapshot_metadata", &dt::Runtime::snapshot_metadata, py::arg("key"))
        .def_property_readonly("snapshot_metadata_entries", [](const dt::Runtime& value) {
            return value.snapshot_metadata_entries();
        })
        .def_property_readonly("loaded_snapshot_version", &dt::Runtime::loaded_snapshot_version)
        .def_property_readonly("imported_legacy_snapshot", &dt::Runtime::imported_legacy_snapshot)
        .def_property("protocol_phase", &dt::Runtime::protocol_phase, &dt::Runtime::set_protocol_phase)
        .def("raw_copy", &dt::Runtime::raw_copy)
        .def("clock_copy", &dt::Runtime::clock_copy);
}

void bind_catalog(py::module_& m) {
    auto family = py::enum_<cat::OrganizationFamily>(m, "OrganizationFamily")
        .value("TRANSPORT_REDIRECTION", cat::OrganizationFamily::TransportRedirection)
        .value("RELATIONAL_LEARNING", cat::OrganizationFamily::RelationalLearning)
        .value("FUNCTIONAL_UPDATE_TRANSFER", cat::OrganizationFamily::FunctionalUpdateTransfer)
        .value("RELATIVE_MEMORY_HISTORY_SELECTION", cat::OrganizationFamily::RelativeMemoryHistorySelection)
        .value("MULTICHANNEL_INTEGRATION_SEPARATION", cat::OrganizationFamily::MultichannelIntegrationSeparation)
        .value("RECURRENCE_LATER_USE", cat::OrganizationFamily::RecurrenceLaterUse)
        .value("DISTRIBUTED_CONTEXT_MEMORY", cat::OrganizationFamily::DistributedContextMemory);
    add_string_repr(family, cat::to_string);
    auto availability = py::enum_<cat::Availability>(m, "Availability")
        .value("AVAILABLE", cat::Availability::Available)
        .value("PENDING", cat::Availability::Pending);
    add_string_repr(availability, cat::to_string);
    py::enum_<cat::ParameterKind>(m, "ParameterKind")
        .value("INTEGER", cat::ParameterKind::Integer)
        .value("BOOLEAN", cat::ParameterKind::Boolean)
        .value("ENUMERATION", cat::ParameterKind::Enumeration);
    auto port_role = py::enum_<cat::PortRole>(m, "PortRole")
        .value("EXPERIENCE_INPUT", cat::PortRole::ExperienceInput)
        .value("QUERY_INPUT", cat::PortRole::QueryInput)
        .value("UPDATE_INPUT", cat::PortRole::UpdateInput)
        .value("SUPPLY_INPUT", cat::PortRole::SupplyInput)
        .value("PASSIVE_READOUT", cat::PortRole::PassiveReadout)
        .value("INTERNAL_OUTPUT", cat::PortRole::InternalOutput)
        .value("CONTEXT_INTERFACE", cat::PortRole::ContextInterface);
    add_string_repr(port_role, cat::to_string);
    auto contribution = py::enum_<cat::ContributionKind>(m, "ContributionKind")
        .value("CARRIER", cat::ContributionKind::Carrier)
        .value("COLLISION_PROPOSAL", cat::ContributionKind::CollisionProposal)
        .value("MOBILE_RELATION", cat::ContributionKind::MobileRelation)
        .value("CONTEXT_CONDITION", cat::ContributionKind::ContextCondition)
        .value("PASSIVE_OBSERVATION", cat::ContributionKind::PassiveObservation);
    add_string_repr(contribution, cat::to_string);

    py::class_<cat::ParameterSpec>(m, "ParameterSpec")
        .def(py::init<>())
        .def_readwrite("name", &cat::ParameterSpec::name)
        .def_readwrite("kind", &cat::ParameterSpec::kind)
        .def_readwrite("default_value", &cat::ParameterSpec::default_value)
        .def_readwrite("minimum", &cat::ParameterSpec::minimum)
        .def_readwrite("maximum", &cat::ParameterSpec::maximum)
        .def_readwrite("enumeration", &cat::ParameterSpec::enumeration)
        .def_readwrite("meaning", &cat::ParameterSpec::meaning);
    py::class_<cat::PortSpec>(m, "PortSpec")
        .def(py::init<>())
        .def_readwrite("name", &cat::PortSpec::name)
        .def_readwrite("role", &cat::PortSpec::role)
        .def_readwrite("contribution", &cat::PortSpec::contribution)
        .def_readwrite("relative_site", &cat::PortSpec::relative_site)
        .def_readwrite("direction", &cat::PortSpec::direction)
        .def_readwrite("earliest_tick", &cat::PortSpec::earliest_tick)
        .def_readwrite("latest_tick", &cat::PortSpec::latest_tick)
        .def_readwrite("minimum_load", &cat::PortSpec::minimum_load)
        .def_readwrite("maximum_load", &cat::PortSpec::maximum_load)
        .def_readwrite("transforms_world", &cat::PortSpec::transforms_world)
        .def_readwrite("timing_and_phase", &cat::PortSpec::timing_and_phase)
        .def_readwrite("maximum_connections", &cat::PortSpec::maximum_connections);
    py::class_<cat::InitialFootprintRecord>(m, "InitialFootprintRecord")
        .def_readonly("relative_site", &cat::InitialFootprintRecord::relative_site)
        .def_readonly("raw", &cat::InitialFootprintRecord::raw)
        .def_readonly("clock", &cat::InitialFootprintRecord::clock)
        .def_readonly("purpose", &cat::InitialFootprintRecord::purpose);
    py::class_<cat::ChannelContract>(m, "ChannelContract")
        .def_readonly("local_name", &cat::ChannelContract::local_name)
        .def_readonly("relative_site", &cat::ChannelContract::relative_site)
        .def_readonly("state", &cat::ChannelContract::state)
        .def_readonly("direction", &cat::ChannelContract::direction)
        .def_readonly("semantic", &cat::ChannelContract::semantic)
        .def_readonly("allow_experience", &cat::ChannelContract::allow_experience)
        .def_readonly("allow_probe", &cat::ChannelContract::allow_probe);
    py::class_<cat::ResourceBudget>(m, "ResourceBudget")
        .def_readonly("initial_voxels", &cat::ResourceBudget::initial_voxels)
        .def_readonly("persistent_sources", &cat::ResourceBudget::persistent_sources)
        .def_readonly("input_channels", &cat::ResourceBudget::input_channels)
        .def_readonly("declared_ports", &cat::ResourceBudget::declared_ports)
        .def_readonly("declared_connection_capacity", &cat::ResourceBudget::declared_connection_capacity);
    py::class_<cat::OrganizationDescriptor>(m, "OrganizationDescriptor")
        .def_readonly("id", &cat::OrganizationDescriptor::id)
        .def_readonly("constructor_version", &cat::OrganizationDescriptor::constructor_version)
        .def_readonly("families", &cat::OrganizationDescriptor::families)
        .def_readonly("availability", &cat::OrganizationDescriptor::availability)
        .def_readonly("source_mechanism", &cat::OrganizationDescriptor::source_mechanism)
        .def_readonly("source_reference", &cat::OrganizationDescriptor::source_reference)
        .def_readonly("summary", &cat::OrganizationDescriptor::summary)
        .def_readonly("parameters", &cat::OrganizationDescriptor::parameters)
        .def_readonly("ports", &cat::OrganizationDescriptor::ports)
        .def_readonly("preparation", &cat::OrganizationDescriptor::preparation)
        .def_readonly("resources", &cat::OrganizationDescriptor::resources)
        .def_readonly("query_effects", &cat::OrganizationDescriptor::query_effects)
        .def_readonly("possible_interference", &cat::OrganizationDescriptor::possible_interference)
        .def_readonly("retention_and_saturation", &cat::OrganizationDescriptor::retention_and_saturation)
        .def_readonly("tested_domain", &cat::OrganizationDescriptor::tested_domain)
        .def_readonly("pending_reason", &cat::OrganizationDescriptor::pending_reason)
        .def_readonly("initial_footprint", &cat::OrganizationDescriptor::initial_footprint)
        .def_readonly("functional_relation", &cat::OrganizationDescriptor::functional_relation)
        .def_readonly("read_region", &cat::OrganizationDescriptor::read_region)
        .def_readonly("required_context", &cat::OrganizationDescriptor::required_context)
        .def_readonly("context_horizon", &cat::OrganizationDescriptor::context_horizon);
    py::class_<cat::OrganizationRequest>(m, "OrganizationRequest")
        .def(py::init<>())
        .def_readwrite("catalog_id", &cat::OrganizationRequest::catalog_id)
        .def_readwrite("instance_id", &cat::OrganizationRequest::instance_id)
        .def_readwrite("anchor", &cat::OrganizationRequest::anchor)
        .def_readwrite("parameters", &cat::OrganizationRequest::parameters);
    py::class_<cat::InstancePort>(m, "InstancePort")
        .def_readonly("contract", &cat::InstancePort::contract)
        .def_readonly("absolute_site", &cat::InstancePort::absolute_site);
    py::class_<cat::OrganizationInstance>(m, "OrganizationInstance")
        .def_property_readonly("descriptor", &cat::OrganizationInstance::descriptor,
                               py::return_value_policy::reference_internal)
        .def_property_readonly("instance_id", &cat::OrganizationInstance::instance_id)
        .def_property_readonly("anchor", &cat::OrganizationInstance::anchor)
        .def_property_readonly("parameters", &cat::OrganizationInstance::parameters)
        .def_property_readonly("ports", &cat::OrganizationInstance::ports)
        .def_property_readonly("landmarks", &cat::OrganizationInstance::landmarks)
        .def_property_readonly("initial_footprint", &cat::OrganizationInstance::initial_footprint)
        .def_property_readonly("channel_contracts", &cat::OrganizationInstance::channel_contracts)
        .def_property_readonly("resource_budget", &cat::OrganizationInstance::resource_budget)
        .def("find_port", &cat::OrganizationInstance::find_port,
             py::arg("name"), py::return_value_policy::reference_internal);
    py::class_<cat::OrganizationCatalog>(m, "OrganizationCatalog")
        .def(py::init<>())
        .def_property_readonly("descriptors", &cat::OrganizationCatalog::descriptors)
        .def("find", &cat::OrganizationCatalog::find, py::arg("id"),
             py::return_value_policy::reference_internal)
        .def("instantiate", &cat::OrganizationCatalog::instantiate, py::arg("request"));

    py::enum_<cat::DiagnosticSeverity>(m, "DiagnosticSeverity")
        .value("INFORMATION", cat::DiagnosticSeverity::Information)
        .value("WARNING", cat::DiagnosticSeverity::Warning)
        .value("ERROR", cat::DiagnosticSeverity::Error);
    auto verification = py::enum_<cat::VerificationClass>(m, "VerificationClass")
        .value("STATIC_VERIFIED", cat::VerificationClass::StaticVerified)
        .value("REQUIRES_SIMULATION", cat::VerificationClass::RequiresSimulation)
        .value("UNSUPPORTED", cat::VerificationClass::Unsupported);
    add_string_repr(verification, cat::to_string);
    py::class_<cat::Diagnostic>(m, "Diagnostic")
        .def_readonly("severity", &cat::Diagnostic::severity)
        .def_readonly("verification", &cat::Diagnostic::verification)
        .def_readonly("code", &cat::Diagnostic::code)
        .def_readonly("message", &cat::Diagnostic::message);
    py::class_<cat::Endpoint>(m, "Endpoint")
        .def(py::init<>())
        .def_readwrite("instance", &cat::Endpoint::instance)
        .def_readwrite("port", &cat::Endpoint::port);
    py::class_<cat::ConnectionRequest>(m, "ConnectionRequest")
        .def(py::init<>())
        .def_readwrite("source", &cat::ConnectionRequest::source)
        .def_readwrite("target", &cat::ConnectionRequest::target)
        .def_readwrite("purpose", &cat::ConnectionRequest::purpose);
    py::class_<cat::ConnectionRecord>(m, "ConnectionRecord")
        .def_readonly("request", &cat::ConnectionRecord::request)
        .def_readonly("verification", &cat::ConnectionRecord::verification)
        .def_readonly("physical_contract", &cat::ConnectionRecord::physical_contract);
    py::class_<cat::PortInputRequest>(m, "PortInputRequest")
        .def(py::init<>())
        .def_readwrite("instance", &cat::PortInputRequest::instance)
        .def_readwrite("port", &cat::PortInputRequest::port)
        .def_readwrite("s_reg", &cat::PortInputRequest::s_reg);

    py::class_<cat::ComposedWorld>(m, "ComposedWorld")
        .def_static("load_snapshot",
                    py::overload_cast<const std::string&>(&cat::ComposedWorld::load_snapshot),
                    py::arg("path"))
        .def_property_readonly("runtime", py::overload_cast<>(&cat::ComposedWorld::runtime),
                               py::return_value_policy::reference_internal)
        .def_property_readonly("organizations", &cat::ComposedWorld::organizations)
        .def_property_readonly("connections", &cat::ComposedWorld::connections)
        .def_property_readonly("landmarks", &cat::ComposedWorld::landmarks)
        .def("qualified_channel", &cat::ComposedWorld::qualified_channel,
             py::arg("instance"), py::arg("local_name"))
        .def("experience", &cat::ComposedWorld::experience,
             py::arg("instance"), py::arg("port"), py::arg("at_tick"), py::arg("s_reg"))
        .def("experience_batch", &cat::ComposedWorld::experience_batch,
             py::arg("inputs"), py::arg("at_tick"))
        .def("probe", &cat::ComposedWorld::probe,
             py::arg("instance"), py::arg("port"), py::arg("at_tick"), py::arg("s_reg"))
        .def("manifest_json", &cat::ComposedWorld::manifest_json)
        .def("save_manifest", &cat::ComposedWorld::save_manifest, py::arg("path"))
        .def("save_snapshot", &cat::ComposedWorld::save_snapshot, py::arg("path"))
        .def("restore_snapshot", &cat::ComposedWorld::restore_snapshot, py::arg("path"));
    py::class_<cat::CompositionPlanner>(m, "CompositionPlanner")
        .def(py::init<int>(), py::arg("dimension"))
        .def("add", &cat::CompositionPlanner::add, py::arg("organization"))
        .def("connect", &cat::CompositionPlanner::connect, py::arg("connection"))
        .def_property_readonly("dimension", &cat::CompositionPlanner::dimension)
        .def_property_readonly("organizations", &cat::CompositionPlanner::organizations)
        .def_property_readonly("requested_connections", &cat::CompositionPlanner::requested_connections)
        .def("analyze", &cat::CompositionPlanner::analyze)
        .def("build", &cat::CompositionPlanner::build);
}

void bind_basal(py::module_& m) {
    auto preset = py::enum_<basal::Preset>(m, "BasalPreset")
        .value("RELATIONAL_BODY", basal::Preset::RelationalBody)
        .value("CONTEXTUAL_REWRITE", basal::Preset::ContextualRewrite);
    add_string_repr(preset, static_cast<const char* (*)(basal::Preset) noexcept>(&basal::to_string));
    auto history = py::enum_<basal::History>(m, "BasalHistory")
        .value("AB", basal::History::AB)
        .value("BA", basal::History::BA)
        .value("H0", basal::History::H0)
        .value("SIMULTANEOUS", basal::History::Simultaneous)
        .value("SHAM", basal::History::Sham);
    add_string_repr(history, static_cast<const char* (*)(basal::History) noexcept>(&basal::to_string));
    auto control = py::enum_<basal::Control>(m, "BasalControl")
        .value("FULL", basal::Control::Full)
        .value("NO_ACTION", basal::Control::NoAction)
        .value("RETURN_CUT", basal::Control::ReturnCut)
        .value("OFF_PATH", basal::Control::OffPath)
        .value("PHASE_MISS", basal::Control::PhaseMiss)
        .value("BARE", basal::Control::Bare)
        .value("READ_CUT", basal::Control::ReadCut)
        .value("ACTION_CUT", basal::Control::ActionCut);
    add_string_repr(control, static_cast<const char* (*)(basal::Control) noexcept>(&basal::to_string));
    auto domain = py::enum_<basal::DomainMode>(m, "BasalDomainMode")
        .value("VALIDATED", basal::DomainMode::Validated)
        .value("RESEARCH", basal::DomainMode::Research);
    add_string_repr(domain, static_cast<const char* (*)(basal::DomainMode) noexcept>(&basal::to_string));
    auto availability = py::enum_<basal::Availability>(m, "BasalAvailability")
        .value("AVAILABLE", basal::Availability::Available)
        .value("MISSING_A", basal::Availability::MissingA)
        .value("MISSING_B", basal::Availability::MissingB)
        .value("MISSING_COMPARATOR", basal::Availability::MissingComparator);
    add_string_repr(availability, static_cast<const char* (*)(basal::Availability) noexcept>(&basal::to_string));

    py::class_<basal::Config>(m, "BasalConfig")
        .def(py::init<>())
        .def_static("relational_reference", &basal::Config::relational_reference,
                    py::arg("seed_snapshot"))
        .def_static("contextual_reference", &basal::Config::contextual_reference,
                    py::arg("seed_snapshot"))
        .def_readwrite("preset", &basal::Config::preset)
        .def_readwrite("history", &basal::Config::history)
        .def_readwrite("control", &basal::Config::control)
        .def_readwrite("domain_mode", &basal::Config::domain_mode)
        .def_readwrite("dimension", &basal::Config::dimension)
        .def_readwrite("origin", &basal::Config::origin)
        .def_readwrite("action_distance", &basal::Config::action_distance)
        .def_readwrite("execution", &basal::Config::execution)
        .def_readwrite("seed_snapshot", &basal::Config::seed_snapshot);

    py::class_<basal::Ports>(m, "BasalPorts")
        .def(py::init<>())
        .def_readwrite("origin", &basal::Ports::origin)
        .def_readwrite("a", &basal::Ports::a)
        .def_readwrite("b", &basal::Ports::b)
        .def_readwrite("comparator", &basal::Ports::comparator)
        .def_readwrite("reader_source", &basal::Ports::reader_source)
        .def_readwrite("event_sources", &basal::Ports::event_sources)
        .def_readwrite("supports", &basal::Ports::supports)
        .def_readwrite("environmental_sources", &basal::Ports::environmental_sources)
        .def_readwrite("action_site", &basal::Ports::action_site)
        .def_readwrite("return_site", &basal::Ports::return_site)
        .def_readwrite("bend_site", &basal::Ports::bend_site)
        .def_readwrite("bend2_site", &basal::Ports::bend2_site);

    py::class_<basal::Observation>(m, "BasalObservation")
        .def_readonly("absolute_tick", &basal::Observation::absolute_tick)
        .def_readonly("relative_tick", &basal::Observation::relative_tick)
        .def_readonly("availability", &basal::Observation::availability)
        .def_readonly("a", &basal::Observation::a)
        .def_readonly("b", &basal::Observation::b)
        .def_readonly("comparator", &basal::Observation::comparator)
        .def_readonly("delta", &basal::Observation::delta)
        .def_readonly("axis_projection", &basal::Observation::axis_projection)
        .def_readonly("supports", &basal::Observation::supports);

    py::class_<basal::World>(m, "BasalWorld")
        .def_static("create", &basal::World::create, py::arg("config"))
        .def_static("attach", &basal::World::attach, py::arg("runtime"),
                    py::arg("config"), py::arg("ports"), py::arg("t0_tick"),
                    py::keep_alive<0, 1>())
        .def_static("load_snapshot", &basal::World::load_snapshot, py::arg("path"))
        .def_property_readonly("config", &basal::World::config,
                               py::return_value_policy::reference_internal)
        .def_property_readonly("ports", &basal::World::ports,
                               py::return_value_policy::reference_internal)
        .def_property_readonly("t0_tick", &basal::World::t0_tick)
        .def_property_readonly("runtime", [](basal::World& value) -> dt::Runtime& {
            return value.runtime();
        }, py::return_value_policy::reference_internal)
        .def("advance", &basal::World::advance, py::arg("count") = 1)
        .def("observe", &basal::World::observe)
        .def("fork", &basal::World::fork)
        .def("diagnostic_fork", &basal::World::diagnostic_fork,
             py::arg("edits"), py::arg("authorize_diagnostic_intervention"))
        .def("save_snapshot", &basal::World::save_snapshot, py::arg("path"));

    py::class_<obs::LocalSite>(m, "LocalSiteObservation")
        .def_readonly("offset", &obs::LocalSite::offset)
        .def_readonly("site", &obs::LocalSite::site)
        .def_readonly("raw", &obs::LocalSite::raw)
        .def_readonly("clock", &obs::LocalSite::clock)
        .def_readonly("record", &obs::LocalSite::record)
        .def_readonly("raw_present", &obs::LocalSite::raw_present)
        .def_readonly("active_for_rule", &obs::LocalSite::active_for_rule);
    py::class_<obs::WriteGate>(m, "WriteGateObservation")
        .def_readonly("site", &obs::WriteGate::site)
        .def_readonly("absolute_tick", &obs::WriteGate::absolute_tick)
        .def_readonly("local_clock", &obs::WriteGate::local_clock)
        .def_readonly("center", &obs::WriteGate::center)
        .def_readonly("center_available", &obs::WriteGate::center_available)
        .def_readonly("n_active", &obs::WriteGate::n_active)
        .def_readonly("direction_sum", &obs::WriteGate::direction_sum)
        .def_readonly("tetra_pattern", &obs::WriteGate::tetra_pattern)
        .def_readonly("hadron", &obs::WriteGate::hadron)
        .def_readonly("rule_value", &obs::WriteGate::rule_value)
        .def_readonly("survives_material_rule", &obs::WriteGate::survives_material_rule)
        .def_readonly("semantic_protected", &obs::WriteGate::semantic_protected)
        .def_readonly("write_protected", &obs::WriteGate::write_protected)
        .def_readonly("k", &obs::WriteGate::k)
        .def_readonly("period", &obs::WriteGate::period)
        .def_readonly("phase_remainder", &obs::WriteGate::phase_remainder)
        .def_readonly("ordinary_increment_condition", &obs::WriteGate::ordinary_increment_condition)
        .def_readonly("branch", &obs::WriteGate::branch)
        .def_readonly("demux_status", &obs::WriteGate::demux_status)
        .def_readonly("neighbors", &obs::WriteGate::neighbors);
    py::class_<obs::SiteTransition>(m, "SiteTransition")
        .def_readonly("site", &obs::SiteTransition::site)
        .def_readonly("tick_before", &obs::SiteTransition::tick_before)
        .def_readonly("tick_after", &obs::SiteTransition::tick_after)
        .def_readonly("raw_before", &obs::SiteTransition::raw_before)
        .def_readonly("raw_after", &obs::SiteTransition::raw_after)
        .def_readonly("clock_before", &obs::SiteTransition::clock_before)
        .def_readonly("clock_after", &obs::SiteTransition::clock_after)
        .def_readonly("changed_fields", &obs::SiteTransition::changed_fields)
        .def_readonly("classification", &obs::SiteTransition::classification);
    m.def("inspect_write_gate", &obs::inspect_write_gate, py::arg("runtime"),
          py::arg("site"), py::arg("include_neighbors") = true);
    m.def("compare_site_transition", &obs::compare_site,
          py::arg("before"), py::arg("after"), py::arg("site"));

    py::class_<gen::TrackedSite>(m, "TrackedSite")
        .def(py::init<>())
        .def_readwrite("id", &gen::TrackedSite::id)
        .def_readwrite("site", &gen::TrackedSite::site);
    py::class_<gen::TraceFrame>(m, "TraceFrame")
        .def_readonly("tick", &gen::TraceFrame::tick)
        .def_readonly("observations", &gen::TraceFrame::observations);
    py::class_<gen::TraceTransition>(m, "TraceTransition")
        .def_readonly("tick_before", &gen::TraceTransition::tick_before)
        .def_readonly("tick_after", &gen::TraceTransition::tick_after)
        .def_readonly("ids", &gen::TraceTransition::ids)
        .def_readonly("changes", &gen::TraceTransition::changes)
        .def_readonly("scope", &gen::TraceTransition::scope);
    py::class_<gen::PassiveTracker>(m, "PassiveTracker")
        .def(py::init<std::vector<gen::TrackedSite>, std::size_t>(),
             py::arg("sites"), py::arg("frame_budget") = 4096)
        .def("capture", &gen::PassiveTracker::capture, py::arg("runtime"))
        .def_property_readonly("transitions", &gen::PassiveTracker::transitions)
        .def_property_readonly("frames", &gen::PassiveTracker::frames)
        .def_property_readonly("frame_budget", &gen::PassiveTracker::frame_budget)
        .def_property_readonly("capture_stopped", &gen::PassiveTracker::capture_stopped)
        .def("clear_trace", &gen::PassiveTracker::clear_trace);

    py::class_<diag::AppliedEdit>(m, "AppliedDiagnosticEdit")
        .def_readonly("site", &diag::AppliedEdit::site)
        .def_readonly("label", &diag::AppliedEdit::label)
        .def_readonly("raw_before", &diag::AppliedEdit::raw_before)
        .def_readonly("raw_after", &diag::AppliedEdit::raw_after)
        .def_readonly("clock_before", &diag::AppliedEdit::clock_before)
        .def_readonly("clock_after", &diag::AppliedEdit::clock_after)
        .def_readonly("raw_changed", &diag::AppliedEdit::raw_changed)
        .def_readonly("clock_changed", &diag::AppliedEdit::clock_changed)
        .def_readonly("touches_declared_support", &diag::AppliedEdit::touches_declared_support);
    py::class_<diag::Comparison>(m, "DiagnosticComparison")
        .def_readonly("parent_tick", &diag::Comparison::parent_tick)
        .def_readonly("horizon", &diag::Comparison::horizon)
        .def_readonly("edits", &diag::Comparison::edits)
        .def_readonly("raw_different_sites", &diag::Comparison::raw_different_sites)
        .def_readonly("clock_different_sites", &diag::Comparison::clock_different_sites)
        .def_readonly("reference_observation", &diag::Comparison::reference_observation)
        .def_readonly("diagnostic_observation", &diag::Comparison::diagnostic_observation)
        .def_readonly("parent_unchanged", &diag::Comparison::parent_unchanged)
        .def_readonly("modality", &diag::Comparison::modality);
    m.def("compare_diagnostic_fork", &diag::compare_fork, py::arg("parent"),
          py::arg("edits"), py::arg("horizon"),
          py::arg("authorize_diagnostic_intervention"));
}

void bind_protocols(py::module_& m) {
    auto modality = py::enum_<proto::ProtocolModality>(m, "ProtocolModality")
        .value("NATIVE_POST_HOST_STOP", proto::ProtocolModality::NativePostHostStop)
        .value("COUPLED", proto::ProtocolModality::Coupled)
        .value("DIAGNOSTIC", proto::ProtocolModality::Diagnostic);
    add_string_repr(modality, proto::to_string);
    auto delay_arm = py::enum_<proto::DelayPositionArm>(m, "DelayPositionArm")
        .value("NATIVE", proto::DelayPositionArm::Native)
        .value("REVERSED_CALIBRATION", proto::DelayPositionArm::ReversedCalibration)
        .value("TARGET_ABSENT", proto::DelayPositionArm::TargetAbsent);
    add_string_repr(delay_arm, proto::to_string);
    auto repair_arm = py::enum_<proto::RepairArm>(m, "RepairArm")
        .value("TREATMENT", proto::RepairArm::Treatment)
        .value("BACKUP_UNTRAINED", proto::RepairArm::BackupUntrained)
        .value("BACKUP_DIRECTION_RESET", proto::RepairArm::BackupDirectionReset)
        .value("NO_BACKUP", proto::RepairArm::NoBackup)
        .value("PATH_CUT", proto::RepairArm::PathCut)
        .value("OFFPATH_CUT", proto::RepairArm::OffpathCut)
        .value("WRONG_RECEIVER", proto::RepairArm::WrongReceiver);
    add_string_repr(repair_arm, proto::to_string);
    auto accessibility_status = py::enum_<proto::AccessibilityStatus>(m, "AccessibilityStatus")
        .value("CONSTRUCTED", proto::AccessibilityStatus::Constructed)
        .value("REACHED", proto::AccessibilityStatus::Reached)
        .value("ACQUIRED", proto::AccessibilityStatus::Acquired)
        .value("NOT_DEMONSTRATED", proto::AccessibilityStatus::NotDemonstrated);
    add_string_repr(accessibility_status, proto::to_string);
    auto query_mode = py::enum_<proto::EnvironmentalQueryMode>(m, "EnvironmentalQueryMode")
        .value("INTACT", proto::EnvironmentalQueryMode::Intact)
        .value("ABSENT", proto::EnvironmentalQueryMode::Absent)
        .value("SHAM", proto::EnvironmentalQueryMode::Sham);
    add_string_repr(query_mode, proto::to_string);

    py::class_<proto::ProtocolResourceBudget>(m, "ProtocolResourceBudget")
        .def_readonly("initial_carriers", &proto::ProtocolResourceBudget::initial_carriers)
        .def_readonly("persistent_supports", &proto::ProtocolResourceBudget::persistent_supports)
        .def_readonly("declared_inputs", &proto::ProtocolResourceBudget::declared_inputs)
        .def_readonly("read_sites", &proto::ProtocolResourceBudget::read_sites)
        .def_readonly("resources_consumable", &proto::ProtocolResourceBudget::resources_consumable);
    py::class_<proto::ProtocolPortDescriptor>(m, "ProtocolPortDescriptor")
        .def_readonly("name", &proto::ProtocolPortDescriptor::name)
        .def_readonly("role", &proto::ProtocolPortDescriptor::role)
        .def_readonly("timing", &proto::ProtocolPortDescriptor::timing)
        .def_readonly("minimum_load", &proto::ProtocolPortDescriptor::minimum_load)
        .def_readonly("maximum_load", &proto::ProtocolPortDescriptor::maximum_load)
        .def_readonly("transforms_world", &proto::ProtocolPortDescriptor::transforms_world);
    py::class_<proto::IntegratedProtocolDescriptor>(m, "IntegratedProtocolDescriptor")
        .def_readonly("id", &proto::IntegratedProtocolDescriptor::id)
        .def_readonly("version", &proto::IntegratedProtocolDescriptor::version)
        .def_readonly("modality", &proto::IntegratedProtocolDescriptor::modality)
        .def_readonly("scientific_source", &proto::IntegratedProtocolDescriptor::scientific_source)
        .def_readonly("summary", &proto::IntegratedProtocolDescriptor::summary)
        .def_readonly("tested_domain", &proto::IntegratedProtocolDescriptor::tested_domain)
        .def_readonly("limits", &proto::IntegratedProtocolDescriptor::limits)
        .def_readonly("resources", &proto::IntegratedProtocolDescriptor::resources)
        .def_readonly("ports", &proto::IntegratedProtocolDescriptor::ports)
        .def_readonly("labels", &proto::IntegratedProtocolDescriptor::labels);

    py::class_<proto::ProtocolReceipt>(m, "ProtocolReceipt")
        .def_readonly("label", &proto::ProtocolReceipt::label)
        .def_readonly("receipt", &proto::ProtocolReceipt::receipt);
    py::class_<proto::ProtocolObservation>(m, "ProtocolObservation")
        .def_readonly("label", &proto::ProtocolObservation::label)
        .def_readonly("observation", &proto::ProtocolObservation::observation);

    py::class_<proto::DelayPositionConfig>(m, "DelayPositionConfig")
        .def(py::init<>())
        .def_readwrite("dimension", &proto::DelayPositionConfig::dimension)
        .def_readwrite("base", &proto::DelayPositionConfig::base)
        .def_readwrite("bank_axis", &proto::DelayPositionConfig::bank_axis)
        .def_readwrite("channel_spacing", &proto::DelayPositionConfig::channel_spacing)
        .def_readwrite("base_path_length", &proto::DelayPositionConfig::base_path_length)
        .def_readwrite("labels", &proto::DelayPositionConfig::labels)
        .def_readwrite("target_direction", &proto::DelayPositionConfig::target_direction)
        .def_readwrite("probe_direction", &proto::DelayPositionConfig::probe_direction)
        .def_readwrite("input_delay", &proto::DelayPositionConfig::input_delay)
        .def_readwrite("arm", &proto::DelayPositionConfig::arm)
        .def_readwrite("loads", &proto::DelayPositionConfig::loads)
        .def_readwrite("states", &proto::DelayPositionConfig::states)
        .def_readwrite("phases", &proto::DelayPositionConfig::phases);
    py::class_<proto::DelayPositionDetection>(m, "DelayPositionDetection")
        .def_readonly("tick", &proto::DelayPositionDetection::tick)
        .def_readonly("label", &proto::DelayPositionDetection::label)
        .def_readonly("record", &proto::DelayPositionDetection::record);
    py::class_<proto::DelayPositionResult>(m, "DelayPositionResult")
        .def_readonly("initial_hubs_empty", &proto::DelayPositionResult::initial_hubs_empty)
        .def_readonly("measurement", &proto::DelayPositionResult::measurement)
        .def_readonly("active_labels", &proto::DelayPositionResult::active_labels)
        .def_readonly("merged_events", &proto::DelayPositionResult::merged_events)
        .def_readonly("final_raw", &proto::DelayPositionResult::final_raw)
        .def_readonly("final_clock", &proto::DelayPositionResult::final_clock);

    py::class_<proto::SeparatedRepertoireConfig>(m, "SeparatedRepertoireConfig")
        .def(py::init<>())
        .def_readwrite("dimension", &proto::SeparatedRepertoireConfig::dimension)
        .def_readwrite("channels", &proto::SeparatedRepertoireConfig::channels)
        .def_readwrite("translation", &proto::SeparatedRepertoireConfig::translation)
        .def_readwrite("base_offset", &proto::SeparatedRepertoireConfig::base_offset)
        .def_readwrite("delta_cycle", &proto::SeparatedRepertoireConfig::delta_cycle)
        .def_readwrite("query_base", &proto::SeparatedRepertoireConfig::query_base)
        .def_readwrite("training_tick", &proto::SeparatedRepertoireConfig::training_tick)
        .def_readwrite("query_tick", &proto::SeparatedRepertoireConfig::query_tick)
        .def_readwrite("query_path", &proto::SeparatedRepertoireConfig::query_path);
    py::class_<proto::SeparatedRepertoireResult>(m, "SeparatedRepertoireResult")
        .def_readonly("ports_empty", &proto::SeparatedRepertoireResult::ports_empty)
        .def_readonly("exact_channels", &proto::SeparatedRepertoireResult::exact_channels)
        .def_readonly("all_exact", &proto::SeparatedRepertoireResult::all_exact)
        .def_readonly("training_budget_exact", &proto::SeparatedRepertoireResult::training_budget_exact)
        .def_readonly("read_budget_exact", &proto::SeparatedRepertoireResult::read_budget_exact)
        .def_readonly("load_accounting_exact", &proto::SeparatedRepertoireResult::load_accounting_exact)
        .def_readonly("observed_responses", &proto::SeparatedRepertoireResult::observed_responses)
        .def_readonly("final_raw", &proto::SeparatedRepertoireResult::final_raw)
        .def_readonly("final_clock", &proto::SeparatedRepertoireResult::final_clock);
    py::class_<proto::OverlapRepertoireConfig>(m, "OverlapRepertoireConfig")
        .def(py::init<>())
        .def_readwrite("dimension", &proto::OverlapRepertoireConfig::dimension)
        .def_readwrite("geometry_index", &proto::OverlapRepertoireConfig::geometry_index)
        .def_readwrite("deltas", &proto::OverlapRepertoireConfig::deltas)
        .def_readwrite("query_load", &proto::OverlapRepertoireConfig::query_load)
        .def_readwrite("off_fiber", &proto::OverlapRepertoireConfig::off_fiber)
        .def_readwrite("base_offset", &proto::OverlapRepertoireConfig::base_offset)
        .def_readwrite("training_tick", &proto::OverlapRepertoireConfig::training_tick)
        .def_readwrite("merge_tick", &proto::OverlapRepertoireConfig::merge_tick)
        .def_readwrite("query_tick", &proto::OverlapRepertoireConfig::query_tick);
    py::class_<proto::OverlapRepertoireResult>(m, "OverlapRepertoireResult")
        .def_readonly("port_empty", &proto::OverlapRepertoireResult::port_empty)
        .def_readonly("merge_exact", &proto::OverlapRepertoireResult::merge_exact)
        .def_readonly("composed_response_exact", &proto::OverlapRepertoireResult::composed_response_exact)
        .def_readonly("individual_identity_preserved", &proto::OverlapRepertoireResult::individual_identity_preserved)
        .def_readonly("false_merge", &proto::OverlapRepertoireResult::false_merge)
        .def_readonly("observed_merge_load", &proto::OverlapRepertoireResult::observed_merge_load)
        .def_readonly("observed_response_load", &proto::OverlapRepertoireResult::observed_response_load)
        .def_readonly("final_raw", &proto::OverlapRepertoireResult::final_raw)
        .def_readonly("final_clock", &proto::OverlapRepertoireResult::final_clock);

    py::class_<proto::RepairGeometry>(m, "RepairGeometry")
        .def(py::init<>())
        .def_readwrite("id", &proto::RepairGeometry::id)
        .def_readwrite("dimension", &proto::RepairGeometry::dimension)
        .def_readwrite("primary_distance", &proto::RepairGeometry::primary_distance)
        .def_readwrite("backup_distance", &proto::RepairGeometry::backup_distance)
        .def_readwrite("permutation", &proto::RepairGeometry::permutation)
        .def_readwrite("signs", &proto::RepairGeometry::signs)
        .def_readwrite("receiver", &proto::RepairGeometry::receiver);
    py::class_<proto::RepairConfig>(m, "RepairConfig")
        .def(py::init<>())
        .def_readwrite("geometry", &proto::RepairConfig::geometry)
        .def_readwrite("arm", &proto::RepairConfig::arm)
        .def_readwrite("authorize_diagnostic_damage", &proto::RepairConfig::authorize_diagnostic_damage)
        .def_readwrite("preparation_tag", &proto::RepairConfig::preparation_tag);
    py::class_<proto::RepairResult>(m, "RepairResult")
        .def_readonly("backup_learned", &proto::RepairResult::backup_learned)
        .def_readonly("primary_function_before_damage", &proto::RepairResult::primary_function_before_damage)
        .def_readonly("damage_applied", &proto::RepairResult::damage_applied)
        .def_readonly("function_lost_after_damage", &proto::RepairResult::function_lost_after_damage)
        .def_readonly("reconstructed_at_arrival", &proto::RepairResult::reconstructed_at_arrival)
        .def_readonly("fresh_function", &proto::RepairResult::fresh_function)
        .def_readonly("primary_source_depleted", &proto::RepairResult::primary_source_depleted)
        .def_readonly("backup_source_depleted", &proto::RepairResult::backup_source_depleted)
        .def_readonly("query_load", &proto::RepairResult::query_load)
        .def_readonly("query_direction", &proto::RepairResult::query_direction)
        .def_readonly("final_raw", &proto::RepairResult::final_raw)
        .def_readonly("final_clock", &proto::RepairResult::final_clock);

    py::class_<proto::AccessibilityReading>(m, "AccessibilityReading")
        .def(py::init<>())
        .def_readwrite("site", &proto::AccessibilityReading::site)
        .def_readwrite("raw", &proto::AccessibilityReading::raw)
        .def_readwrite("clock", &proto::AccessibilityReading::clock);
    py::class_<proto::AccessibilityCase>(m, "AccessibilityCase")
        .def(py::init<>())
        .def_readwrite("history_id", &proto::AccessibilityCase::history_id)
        .def_readwrite("baseline_tick", &proto::AccessibilityCase::baseline_tick)
        .def_readwrite("challenged_tick", &proto::AccessibilityCase::challenged_tick)
        .def_readwrite("baseline", &proto::AccessibilityCase::baseline)
        .def_readwrite("challenged", &proto::AccessibilityCase::challenged)
        .def_readwrite("history_status", &proto::AccessibilityCase::history_status)
        .def_readwrite("history_reached_natively", &proto::AccessibilityCase::history_reached_natively)
        .def_readwrite("challenge_applied_to_diagnostic_clone", &proto::AccessibilityCase::challenge_applied_to_diagnostic_clone);
    py::class_<proto::AccessibilityRequest>(m, "AccessibilityRequest")
        .def(py::init<>())
        .def_readwrite("observer_id", &proto::AccessibilityRequest::observer_id)
        .def_readwrite("challenge_id", &proto::AccessibilityRequest::challenge_id)
        .def_readwrite("apparatus_frozen", &proto::AccessibilityRequest::apparatus_frozen)
        .def_readwrite("challenge_frozen", &proto::AccessibilityRequest::challenge_frozen)
        .def_readwrite("ages_aligned", &proto::AccessibilityRequest::ages_aligned)
        .def_readwrite("cases", &proto::AccessibilityRequest::cases);
    py::class_<proto::AccessibilityEffect>(m, "AccessibilityEffect")
        .def_readonly("history_id", &proto::AccessibilityEffect::history_id)
        .def_readonly("raw_changed_sites", &proto::AccessibilityEffect::raw_changed_sites)
        .def_readonly("clock_changed_sites", &proto::AccessibilityEffect::clock_changed_sites)
        .def_readonly("s_reg_deltas", &proto::AccessibilityEffect::s_reg_deltas)
        .def_readonly("status", &proto::AccessibilityEffect::status);
    py::class_<proto::AccessibilityResult>(m, "AccessibilityResult")
        .def_readonly("comparable", &proto::AccessibilityResult::comparable)
        .def_readonly("history_conditioned_response", &proto::AccessibilityResult::history_conditioned_response)
        .def_readonly("effects", &proto::AccessibilityResult::effects)
        .def_readonly("diagnostics", &proto::AccessibilityResult::diagnostics);

    py::class_<proto::ReusableRevisionConfig>(m, "ReusableRevisionConfig")
        .def(py::init<>())
        .def_readwrite("id", &proto::ReusableRevisionConfig::id)
        .def_readwrite("revision1", &proto::ReusableRevisionConfig::revision1)
        .def_readwrite("revision2", &proto::ReusableRevisionConfig::revision2)
        .def_readwrite("sham1", &proto::ReusableRevisionConfig::sham1)
        .def_readwrite("sham2", &proto::ReusableRevisionConfig::sham2)
        .def_readwrite("trained_relation", &proto::ReusableRevisionConfig::trained_relation);
    py::class_<proto::ReusableRevisionResult>(m, "ReusableRevisionResult")
        .def_readonly("response_loads", &proto::ReusableRevisionResult::response_loads)
        .def_readonly("post_revision_loads", &proto::ReusableRevisionResult::post_revision_loads)
        .def_readonly("all_inputs_applied_at_t0", &proto::ReusableRevisionResult::all_inputs_applied_at_t0)
        .def_readonly("backend_fallback", &proto::ReusableRevisionResult::backend_fallback)
        .def_readonly("receipts", &proto::ReusableRevisionResult::receipts)
        .def_readonly("checkpoints", &proto::ReusableRevisionResult::checkpoints)
        .def_readonly("final_raw", &proto::ReusableRevisionResult::final_raw)
        .def_readonly("final_clock", &proto::ReusableRevisionResult::final_clock);

    py::class_<proto::EnvironmentalReturnConfig>(m, "EnvironmentalReturnConfig")
        .def(py::init<>())
        .def_readwrite("id", &proto::EnvironmentalReturnConfig::id)
        .def_readwrite("trained_response", &proto::EnvironmentalReturnConfig::trained_response)
        .def_readwrite("bias_load", &proto::EnvironmentalReturnConfig::bias_load)
        .def_readwrite("marker_load", &proto::EnvironmentalReturnConfig::marker_load)
        .def_readwrite("query_mode", &proto::EnvironmentalReturnConfig::query_mode)
        .def_readwrite("environment_clock_phase", &proto::EnvironmentalReturnConfig::environment_clock_phase);
    py::class_<proto::EnvironmentalReturnResult>(m, "EnvironmentalReturnResult")
        .def_readonly("upstream_response_load", &proto::EnvironmentalReturnResult::upstream_response_load)
        .def_readonly("environment_load", &proto::EnvironmentalReturnResult::environment_load)
        .def_readonly("downstream_loads", &proto::EnvironmentalReturnResult::downstream_loads)
        .def_readonly("overflow_total", &proto::EnvironmentalReturnResult::overflow_total)
        .def_readonly("query_admitted", &proto::EnvironmentalReturnResult::query_admitted)
        .def_readonly("all_inputs_applied_at_t0", &proto::EnvironmentalReturnResult::all_inputs_applied_at_t0)
        .def_readonly("backend_fallback", &proto::EnvironmentalReturnResult::backend_fallback)
        .def_readonly("receipts", &proto::EnvironmentalReturnResult::receipts)
        .def_readonly("checkpoints", &proto::EnvironmentalReturnResult::checkpoints)
        .def_readonly("final_raw", &proto::EnvironmentalReturnResult::final_raw)
        .def_readonly("final_clock", &proto::EnvironmentalReturnResult::final_clock);

    m.def("run_delay_position", &proto::run_delay_position,
          py::arg("config"), py::arg("options") = v27::TickOptions{});
    m.def("save_delay_position_checkpoint", &proto::save_delay_position_checkpoint,
          py::arg("config"), py::arg("stop_at_tick"), py::arg("path"),
          py::arg("options") = v27::TickOptions{});
    m.def("resume_delay_position_checkpoint", &proto::resume_delay_position_checkpoint,
          py::arg("path"), py::arg("options") = v27::TickOptions{});
    m.def("run_separated_repertoire", &proto::run_separated_repertoire,
          py::arg("config"), py::arg("options") = v27::TickOptions{});
    m.def("save_separated_repertoire_checkpoint", &proto::save_separated_repertoire_checkpoint,
          py::arg("config"), py::arg("stop_at_tick"), py::arg("path"),
          py::arg("options") = v27::TickOptions{});
    m.def("resume_separated_repertoire_checkpoint",
          &proto::resume_separated_repertoire_checkpoint,
          py::arg("path"), py::arg("options") = v27::TickOptions{});
    m.def("run_overlap_repertoire", &proto::run_overlap_repertoire,
          py::arg("config"), py::arg("options") = v27::TickOptions{});
    m.def("save_overlap_repertoire_checkpoint", &proto::save_overlap_repertoire_checkpoint,
          py::arg("config"), py::arg("stop_at_tick"), py::arg("path"),
          py::arg("options") = v27::TickOptions{});
    m.def("resume_overlap_repertoire_checkpoint", &proto::resume_overlap_repertoire_checkpoint,
          py::arg("path"), py::arg("options") = v27::TickOptions{});
    m.def("run_trained_redundancy_repair", &proto::run_trained_redundancy_repair,
          py::arg("config"), py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("save_trained_redundancy_repair_checkpoint",
          &proto::save_trained_redundancy_repair_checkpoint,
          py::arg("config"), py::arg("stop_after_tick"), py::arg("path"),
          py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("resume_trained_redundancy_repair_checkpoint",
          &proto::resume_trained_redundancy_repair_checkpoint,
          py::arg("path"), py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("analyze_accessibility", &proto::analyze_accessibility, py::arg("request"));
    m.def("run_reusable_revision", &proto::run_reusable_revision,
          py::arg("config"), py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("save_reusable_revision_checkpoint", &proto::save_reusable_revision_checkpoint,
          py::arg("config"), py::arg("stop_at_tick"), py::arg("path"),
          py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("resume_reusable_revision_checkpoint", &proto::resume_reusable_revision_checkpoint,
          py::arg("path"), py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("run_environmental_return", &proto::run_environmental_return,
          py::arg("config"), py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("save_environmental_return_checkpoint", &proto::save_environmental_return_checkpoint,
          py::arg("config"), py::arg("stop_at_tick"), py::arg("path"),
          py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("resume_environmental_return_checkpoint", &proto::resume_environmental_return_checkpoint,
          py::arg("path"), py::arg("options") = v27::TickOptions{v27::Backend::Lazy, 4});
    m.def("integrated_protocol_descriptors", []() {
        return proto::integrated_protocol_descriptors();
    });
    m.def("find_integrated_protocol", &proto::find_integrated_protocol,
          py::arg("id"), py::return_value_policy::reference);

    m.attr("H1_ID") = proto::kH1Id;
    m.attr("H2_ID") = proto::kH2Id;
    m.attr("H3_ID") = proto::kH3Id;
    m.attr("H4_ID") = proto::kH4Id;
    m.attr("F1_ID") = proto::kF1Id;
    m.attr("F2_ID") = proto::kF2Id;
}

}  // namespace

PYBIND11_MODULE(_native, m) {
    m.doc() = "Native bindings for DEE thinking; frozen DEE v27 dynamics";
    m.attr("__version__") = DEE_THINKING_PYTHON_VERSION;
    m.attr("KERNEL_MODULUS") = v27::kKernelModulus;
    m.attr("REDUCER_CAP") = v27::kReducerCap;

    bind_kernel(m);
    bind_runtime(m);
    bind_catalog(m);
    bind_basal(m);
    bind_protocols(m);
    bind_organizational(m);

    m.def("build_info", []() {
        py::dict info;
        info["product"] = "dee_thinking";
        info["product_version"] = DEE_THINKING_PYTHON_VERSION;
        info["kernel_version"] = 27;
        info["kernel_modulus"] = v27::kKernelModulus;
        info["reducer_cap"] = v27::kReducerCap;
        info["native_module"] = true;
        info["delegates_to_dee_universe_v27"] = false;
        info["gil_released_during_runtime_evolution"] = false;
        info["python_tag"] = "cp313";
        info["abi_tag"] = "cp313";
#if defined(_WIN64)
        info["platform_tag"] = "win_amd64";
#else
        info["platform_tag"] = "unsupported_for_this_delivery";
#endif
        return info;
    });
}
