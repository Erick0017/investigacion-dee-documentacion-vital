#include "dee_thinking/cognitive.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py=pybind11;
namespace d=dee::thinking;
namespace {
py::dict observed(const d::Observation& o){py::dict x;x["tick"]=o.tick;x["site"]=py::make_tuple(o.coordinate.x,o.coordinate.y,o.coordinate.z);x["raw"]=o.raw;x["RAW"]=o.raw;x["clock"]=o.clock;x["state"]=o.record.state;x["s_reg"]=o.record.s_reg;x["semantic"]=o.record.semantic;x["direction"]=py::make_tuple(o.record.dx,o.record.dy,o.record.dz);x["active"]=o.record.state>0&&o.record.semantic!=5;return x;}
py::dict receipt(const d::EventReceipt& r){py::dict x;x["id"]=r.id;x["kind"]=d::to_string(r.kind);x["status"]=d::to_string(r.status);x["requested_tick"]=r.requested_tick;x["effective_tick"]=py::cast(r.effective_tick);x["channels"]=r.channels;x["reason"]=r.reason;return x;}
py::dict sample(const d::BarrierSample& s){py::dict x;x["tick"]=s.tick;x["arrived"]=s.arrived;x["reference_branch"]=s.reference_branch;x["observable"]=s.observable;x["modality"]=s.modality;return x;}
py::dict call(const d::CognitiveCall& c){py::dict x;x["tick"]=c.tick;x["target_tick"]=c.target_tick;x["receipt_id"]=c.receipt_id;x["operation"]=c.operation;x["scope"]=c.scope;x["channel"]=c.channel;x["source"]=c.source;x["value"]=py::cast(c.value);return x;}
py::dict gate(const d::observation::WriteGate& g){py::dict x;x["absolute_tick"]=g.absolute_tick;x["clock"]=g.local_clock;x["n_active"]=g.n_active;x["direction_sum"]=py::make_tuple(g.direction_sum.dx,g.direction_sum.dy,g.direction_sum.dz);x["tetra_pattern"]=py::cast(g.tetra_pattern);x["hadron"]=g.hadron;x["rule_value"]=g.rule_value;x["survives"]=g.survives_material_rule;x["protected"]=g.write_protected;x["k"]=g.k;x["period"]=py::cast(g.period);x["phase_remainder"]=py::cast(g.phase_remainder);x["ordinary_increment_condition"]=g.ordinary_increment_condition;x["branch"]=g.branch;x["demux"]=g.demux_status;return x;}
py::dict comparison(const d::CognitiveComparison& c){py::dict x;x["physical_output"]=observed(c.physical_output);x["signed_comparison_marker_present"]=c.signed_comparison_marker_present;x["represented_expectation_before_report"]=c.represented_expectation_before_report;x["report_applied"]=c.report_applied;x["within_window"]=c.within_window;x["presentation"]=c.presentation.empty()?py::object(py::none()):py::object(py::str(c.presentation));x["validity"]=c.validity;x["scope"]=c.scope;return x;}
py::dict readout(const d::CognitiveReadout& r){py::dict x;x["tick"]=r.tick;x["delta"]=py::cast(r.memory.delta);x["centers_available"]=r.memory.centers_available;x["reader_available"]=r.memory.reader_available;x["supports_intact"]=r.memory.supports_intact;x["axis_projection"]=py::cast(r.memory.axis_projection);x["physical_output"]=observed(r.physical_output);x["a"]=observed(r.a);x["b"]=observed(r.b);x["prediction_set"]=r.prediction_set;x["profile"]=r.profile;x["comparison_stage"]=r.comparison_stage;x["forecast_domain"]=r.forecast_domain;x["domain_status"]=r.domain_status;x["modality"]="PASSIVE_OBSERVATION";py::dict gates;gates["A"]=gate(r.gate_a);gates["B"]=gate(r.gate_b);x["write_gates"]=gates;if(r.comparison)x["comparison_live"]=comparison(*r.comparison);return x;}
py::dict prediction(const d::CognitivePrediction& p){py::dict x;x["id"]=p.id;x["emission_tick"]=p.emission_tick;x["target_tick"]=p.target_tick;x["horizon"]=p.target_tick-p.emission_tick;x["physical_output"]=observed(p.physical_output);x["prediction_set"]=p.prediction_set;x["receipt"]=p.receipt?py::object(receipt(*p.receipt)):py::object(py::none());x["evaluated"]=p.evaluated;x["modality"]=p.modality;x["observable"]="packet_arrival_at_barrier_output";return x;}
py::dict evaluation(const d::CognitiveEvaluation& e){py::dict x;x["prediction_id"]=e.prediction_id;x["emission_tick"]=e.emission_tick;x["target_tick"]=e.target_tick;x["actual"]=e.actual;x["coverage"]=e.singleton;x["error"]=py::cast(e.error);x["modality"]=e.modality;return x;}
py::dict result(const d::CognitiveResult& r){py::dict x=readout(r.readout);x["kind"]=r.kind;x["status"]=r.status;x["modality"]=r.modality;x["detail"]=r.detail;x["observation"]=readout(r.readout);py::list rs,ss,es;for(auto& v:r.receipts)rs.append(receipt(v));for(auto& v:r.samples)ss.append(sample(v));for(auto& v:r.evaluations)es.append(evaluation(v));x["receipts"]=rs;x["samples"]=ss;x["evaluations"]=es;if(r.prediction){auto p=prediction(*r.prediction);for(auto item:p)x[item.first]=item.second;x["prediction"]=p;}if(r.comparison){x["comparison_decoder"]=comparison(*r.comparison);x["comparison"]=comparison(*r.comparison);}if(r.receipts.size()==1)x["input_receipt"]=receipt(r.receipts.front());if(r.samples.size()==1)x["source_actual"]=sample(r.samples.front());return x;}
py::dict association(const d::AssociationResponse& r){py::dict x;x["operation"]=r.operation;x["modality"]=r.modality;x["scope"]=r.scope;x["input_tick"]=r.input_tick;x["tick"]=r.tick;py::list receipts;for(auto& v:r.receipts)receipts.append(receipt(v));x["receipts"]=receipts;py::dict outputs,decoded;for(auto& [k,v]:r.outputs)outputs[py::str(k)]=observed(v);for(auto& [k,v]:r.decoded)decoded[py::str(k)]=py::cast(v);x["outputs"]=outputs;x["decoded"]=decoded;if(r.outputs.size()==1){x["physical_output"]=observed(r.outputs.begin()->second);x["decoded_value"]=py::cast(r.decoded.begin()->second);}return x;}
}
void register_cognitive(py::module_& m){
    py::class_<d::CognitiveParameters>(m,"CognitiveParameters")
        .def(py::init<>()).def_readwrite("seed_path",&d::CognitiveParameters::seed_path)
        .def_readwrite("profile",&d::CognitiveParameters::profile).def_readwrite("origin",&d::CognitiveParameters::origin)
        .def_readwrite("initial_open",&d::CognitiveParameters::initial_open).def_readwrite("change_tick",&d::CognitiveParameters::change_tick)
        .def_readwrite("event_state",&d::CognitiveParameters::event_state).def_readwrite("execution",&d::CognitiveParameters::execution)
        .def_readwrite("journal_limit",&d::CognitiveParameters::journal_limit).def_readwrite("prediction_limit",&d::CognitiveParameters::prediction_limit);
    py::class_<d::CognitiveSession>(m,"CognitiveSession")
        .def_static("create",&d::CognitiveSession::create,py::arg("parameters"))
        .def_static("load_snapshot",&d::CognitiveSession::load_snapshot,py::arg("path"))
        .def_static("load_legacy_physical_snapshot",&d::CognitiveSession::load_legacy_physical_snapshot,py::arg("path"))
        .def_property_readonly("world",[](d::CognitiveSession& s)->d::OrganizationalWorld&{return s.world();},py::return_value_policy::reference_internal)
        .def_property_readonly("tick",&d::CognitiveSession::tick).def_property_readonly("preferred_horizon",&d::CognitiveSession::preferred_horizon)
        .def_property_readonly("profile",[](const d::CognitiveSession& s){return s.parameters().profile;})
        .def_property_readonly("parameters",[](const d::CognitiveSession& s){return s.parameters();})
        .def_property_readonly("journal",[](const d::CognitiveSession& s){py::list out;for(auto& v:s.journal())out.append(call(v));return out;})
        .def_property_readonly("predictions",[](const d::CognitiveSession& s){py::list out;for(auto& v:s.predictions())out.append(prediction(v));return out;})
        .def_property_readonly("samples",[](const d::CognitiveSession& s){py::list out;for(auto& v:s.samples())out.append(sample(v));return out;})
        .def("observe",[](const d::CognitiveSession& s){return readout(s.observe());})
        .def("experience",[](d::CognitiveSession& s,const std::string& v){return result(s.experience(v));},py::arg("symbol"))
        .def("sense",[](d::CognitiveSession& s){return result(s.sense());})
        .def("predict",[](d::CognitiveSession& s,std::uint64_t h){return result(s.predict(h));},py::arg("horizon")=0)
        .def("compare",[](d::CognitiveSession& s){return result(s.compare());})
        .def("advance",[](d::CognitiveSession& s,std::uint64_t n){return result(s.advance(n));},py::arg("ticks")=1)
        .def("run_until",[](d::CognitiveSession& s,std::uint64_t t){return result(s.run_until(t));},py::arg("absolute_tick"))
        .def("fork",&d::CognitiveSession::fork)
        .def("save_snapshot",&d::CognitiveSession::save_snapshot,py::arg("path"),py::arg("include_trace")=true)
        .def("set_interface_metadata",&d::CognitiveSession::set_interface_metadata)
        .def("get_interface_metadata",&d::CognitiveSession::get_interface_metadata)
        .def_property_readonly("interface_metadata",&d::CognitiveSession::interface_metadata);
    py::class_<d::NativeAssociationParameters>(m,"NativeAssociationParameters")
        .def(py::init<>()).def_readwrite("translation",&d::NativeAssociationParameters::translation)
        .def_readwrite("execution",&d::NativeAssociationParameters::execution);
    py::class_<d::NativeAssociationSession>(m,"NativeAssociationSession")
        .def_static("create",&d::NativeAssociationSession::create,py::arg("parameters")=d::NativeAssociationParameters{})
        .def_static("load_snapshot",&d::NativeAssociationSession::load_snapshot)
        .def_property_readonly("world",[](d::NativeAssociationSession& s)->d::OrganizationalWorld&{return s.world();},py::return_value_policy::reference_internal)
        .def_property_readonly("tick",&d::NativeAssociationSession::tick)
        .def("train",[](d::NativeAssociationSession& s,const std::vector<std::uint16_t>& t,std::uint16_t c,const std::string& mode){return association(s.train(t,c,mode));},py::arg("teachers"),py::arg("cue")=5,py::arg("mode")="paired")
        .def("query",[](d::NativeAssociationSession& s,int port,std::uint16_t v){return association(s.query(port,v));},py::arg("port"),py::arg("payload")=13)
        .def("query_panel",[](d::NativeAssociationSession& s,std::uint16_t v){return association(s.query_panel(v));},py::arg("payload")=13)
        .def("observe",[](const d::NativeAssociationSession& s){return association(s.observe());})
        .def("fork",&d::NativeAssociationSession::fork)
        .def("start_sequence",&d::NativeAssociationSession::start_sequence,py::arg("payloads"),py::arg("protocol_id")="association_sequence",py::arg("first_tick")=6)
        .def("advance",&d::NativeAssociationSession::advance,py::arg("ticks")=1)
        .def("run_until",&d::NativeAssociationSession::run_until)
        .def("save_snapshot",&d::NativeAssociationSession::save_snapshot,py::arg("path"),py::arg("include_trace")=true)
        .def("set_interface_metadata",&d::NativeAssociationSession::set_interface_metadata)
        .def("get_interface_metadata",&d::NativeAssociationSession::get_interface_metadata)
        .def_property_readonly("interface_metadata",&d::NativeAssociationSession::interface_metadata);
    m.def("create_learnable_cascade",&d::create_learnable_cascade,py::arg("depth")=2,py::arg("translation")=d::Coordinate{},py::arg("execution")=dee::v27::TickOptions{dee::v27::Backend::Lazy,1});
    m.def("experience_composition",[](d::OrganizationalWorld& w,const std::vector<std::pair<std::uint16_t,std::uint16_t>>& p,std::optional<std::size_t> omit){py::list out;for(auto& r:d::experience_composition(w,p,omit))out.append(receipt(r));return out;},py::arg("world"),py::arg("pairs"),py::arg("omit")=std::nullopt);
    m.def("query_composition",[](d::OrganizationalWorld& w,std::uint16_t value){return association(d::query_composition(w,value));},py::arg("world"),py::arg("payload"));
}
