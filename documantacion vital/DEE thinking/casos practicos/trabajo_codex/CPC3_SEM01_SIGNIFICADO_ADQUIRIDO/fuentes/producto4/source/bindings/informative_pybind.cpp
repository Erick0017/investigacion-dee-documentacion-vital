#include "dee_thinking/informative.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py=pybind11;
namespace d=dee::thinking;
namespace {
py::dict observation(const d::Observation& o){py::dict x;x["tick"]=o.tick;x["coordinate"]=py::make_tuple(o.coordinate.x,o.coordinate.y,o.coordinate.z);x["raw"]=o.raw;x["clock"]=o.clock;x["state"]=o.record.state;x["semantic"]=o.record.semantic;x["load"]=o.record.s_reg;x["direction"]=py::make_tuple(static_cast<int>(o.record.dx),static_cast<int>(o.record.dy),static_cast<int>(o.record.dz));x["active"]=o.record.state>0&&o.record.semantic!=5;return x;}
py::dict candidate(const d::PhysicalCandidate& c){py::dict x;x["port"]=c.port;x["source"]=c.source;x["presentation"]=c.presentation;x["physical"]=observation(c.physical);x["physical_output"]=observation(c.physical);x["value"]=py::cast(c.value);return x;}
py::list candidates(const std::vector<d::PhysicalCandidate>& c){py::list x;for(const auto& v:c)x.append(candidate(v));return x;}
py::dict readout(const d::InformationReadout& r){py::dict x;x["tick"]=r.tick;x["profile"]=r.profile;x["status"]=r.status;x["scope"]=r.scope;x["modality"]=d::to_string(r.modality);x["comparisons"]=candidates(r.comparisons);x["policies"]=candidates(r.policies);x["actions"]=candidates(r.actions);x["information"]=candidates(r.information);x["later_responses"]=candidates(r.later_responses);py::dict p;for(const auto& [k,o]:r.physical_outputs)p[k.c_str()]=observation(o);x["physical_outputs"]=p;x["current_prediction"]=py::cast(r.current_prediction);x["delta"]=py::cast(r.delta);x["centers_available"]=r.centers_available;x["supports_intact"]=r.supports_intact;x["journal_truncated"]=r.journal_truncated;py::list receipts;for(const auto& v:r.receipts){py::dict z;z["id"]=v.id;z["status"]=d::to_string(v.status);z["kind"]=d::to_string(v.kind);z["requested_tick"]=v.requested_tick;z["effective_tick"]=py::cast(v.effective_tick);z["channels"]=v.channels;z["reason"]=v.reason;receipts.append(z);}x["receipts"]=receipts;return x;}
}

void register_informative(py::module_& m){
    py::enum_<d::SourceRole>(m,"SourceRole").value("P_INFORMATIVE",d::SourceRole::PInformative).value("Q_INFORMATIVE",d::SourceRole::QInformative);
    py::class_<d::FinitePolicyParameters>(m,"FinitePolicyParameters").def(py::init<>())
        .def_readwrite("origin",&d::FinitePolicyParameters::origin).def_readwrite("roles",&d::FinitePolicyParameters::roles)
        .def_readwrite("actual_class",&d::FinitePolicyParameters::actual_class).def_readwrite("actual_enabled",&d::FinitePolicyParameters::actual_enabled)
        .def_readwrite("execution",&d::FinitePolicyParameters::execution);
    py::class_<d::NativeInformationParameters>(m,"NativeInformationParameters").def(py::init<>())
        .def_readwrite("seed_path",&d::NativeInformationParameters::seed_path).def_readwrite("origin",&d::NativeInformationParameters::origin)
        .def_readwrite("history",&d::NativeInformationParameters::history).def_readwrite("context",&d::NativeInformationParameters::context)
        .def_readwrite("actual_class",&d::NativeInformationParameters::actual_class).def_readwrite("information_load",&d::NativeInformationParameters::information_load)
        .def_readwrite("query_enabled",&d::NativeInformationParameters::query_enabled).def_readwrite("actual_enabled",&d::NativeInformationParameters::actual_enabled)
        .def_readwrite("source_enabled",&d::NativeInformationParameters::source_enabled).def_readwrite("post_query",&d::NativeInformationParameters::post_query)
        .def_readwrite("source_cut",&d::NativeInformationParameters::source_cut).def_readwrite("distance",&d::NativeInformationParameters::distance)
        .def_readwrite("execution",&d::NativeInformationParameters::execution);
    py::class_<d::InformativeOperation>(m,"InformativeOperation").def_readonly("tick",&d::InformativeOperation::tick)
        .def_readonly("operation",&d::InformativeOperation::operation).def_readonly("interface_name",&d::InformativeOperation::interface_name)
        .def_readonly("value",&d::InformativeOperation::value).def_readonly("receipt_id",&d::InformativeOperation::receipt_id)
        .def_readonly("modality",&d::InformativeOperation::modality);
    py::class_<d::PhysicalCandidate>(m,"PhysicalCandidate").def_readonly("port",&d::PhysicalCandidate::port)
        .def_readonly("source",&d::PhysicalCandidate::source).def_readonly("presentation",&d::PhysicalCandidate::presentation)
        .def_readonly("physical",&d::PhysicalCandidate::physical).def_readonly("value",&d::PhysicalCandidate::value).def("as_dict",&candidate);
    py::class_<d::InformationReadout>(m,"InformationReadout").def_readonly("tick",&d::InformationReadout::tick)
        .def_readonly("profile",&d::InformationReadout::profile).def_readonly("status",&d::InformationReadout::status)
        .def_readonly("scope",&d::InformationReadout::scope).def_readonly("modality",&d::InformationReadout::modality)
        .def_readonly("comparisons",&d::InformationReadout::comparisons).def_readonly("policies",&d::InformationReadout::policies)
        .def_readonly("actions",&d::InformationReadout::actions).def_readonly("information",&d::InformationReadout::information)
        .def_readonly("later_responses",&d::InformationReadout::later_responses).def_readonly("physical_outputs",&d::InformationReadout::physical_outputs)
        .def_readonly("receipts",&d::InformationReadout::receipts).def_readonly("current_prediction",&d::InformationReadout::current_prediction)
        .def_readonly("delta",&d::InformationReadout::delta).def_readonly("centers_available",&d::InformationReadout::centers_available)
        .def_readonly("supports_intact",&d::InformationReadout::supports_intact).def_readonly("journal_truncated",&d::InformationReadout::journal_truncated)
        .def("as_dict",&readout);
    py::class_<d::FinitePolicySession>(m,"FinitePolicySession")
        .def_static("create",&d::FinitePolicySession::create,py::arg("parameters")=d::FinitePolicyParameters{})
        .def_static("load_snapshot",&d::FinitePolicySession::load_snapshot)
        .def_property_readonly("tick",&d::FinitePolicySession::tick)
        .def_property_readonly("world",&d::FinitePolicySession::world,py::return_value_policy::reference_internal)
        .def_property_readonly("parameters",&d::FinitePolicySession::parameters,py::return_value_policy::copy)
        .def_property_readonly("journal",&d::FinitePolicySession::journal,py::return_value_policy::copy)
        .def_property_readonly("interface_metadata",&d::FinitePolicySession::interface_metadata,py::return_value_policy::copy)
        .def("set_interface_metadata",py::overload_cast<std::map<std::string,std::string>>(&d::FinitePolicySession::set_interface_metadata))
        .def("set_interface_metadata",py::overload_cast<std::string,std::string>(&d::FinitePolicySession::set_interface_metadata))
        .def("get_interface_metadata",&d::FinitePolicySession::get_interface_metadata)
        .def("observe",&d::FinitePolicySession::observe).def("advance",&d::FinitePolicySession::advance,py::arg("count")=1)
        .def("run_until",&d::FinitePolicySession::run_until).def("compare",&d::FinitePolicySession::compare)
        .def("source",&d::FinitePolicySession::source).def("sense",&d::FinitePolicySession::sense)
        .def("submit_actual",&d::FinitePolicySession::submit_actual).def("process_boundary",&d::FinitePolicySession::process_boundary)
        .def("fork",&d::FinitePolicySession::fork).def("diagnostic_fork",&d::FinitePolicySession::diagnostic_fork,py::arg("edits"),py::arg("authorize"))
        .def("save_snapshot",&d::FinitePolicySession::save_snapshot,py::arg("path"),py::arg("include_trace")=true);
    py::class_<d::NativeInformationSession>(m,"NativeInformationSession")
        .def_static("create",&d::NativeInformationSession::create)
        .def_static("load_snapshot",&d::NativeInformationSession::load_snapshot)
        .def_property_readonly("tick",&d::NativeInformationSession::tick)
        .def_property_readonly("world",&d::NativeInformationSession::world,py::return_value_policy::reference_internal)
        .def_property_readonly("parameters",&d::NativeInformationSession::parameters,py::return_value_policy::copy)
        .def_property_readonly("journal",&d::NativeInformationSession::journal,py::return_value_policy::copy)
        .def_property_readonly("interface_metadata",&d::NativeInformationSession::interface_metadata,py::return_value_policy::copy)
        .def("set_interface_metadata",py::overload_cast<std::map<std::string,std::string>>(&d::NativeInformationSession::set_interface_metadata))
        .def("set_interface_metadata",py::overload_cast<std::string,std::string>(&d::NativeInformationSession::set_interface_metadata))
        .def("get_interface_metadata",&d::NativeInformationSession::get_interface_metadata)
        .def("observe",&d::NativeInformationSession::observe).def("advance",&d::NativeInformationSession::advance,py::arg("count")=1)
        .def("run_until",&d::NativeInformationSession::run_until).def("compare",&d::NativeInformationSession::compare)
        .def("source",&d::NativeInformationSession::source).def("sense",&d::NativeInformationSession::sense)
        .def("submit_actual",&d::NativeInformationSession::submit_actual).def("process_boundary",&d::NativeInformationSession::process_boundary)
        .def("fork",&d::NativeInformationSession::fork).def("diagnostic_fork",&d::NativeInformationSession::diagnostic_fork,py::arg("edits"),py::arg("authorize"))
        .def("save_snapshot",&d::NativeInformationSession::save_snapshot,py::arg("path"),py::arg("include_trace")=true);
}
