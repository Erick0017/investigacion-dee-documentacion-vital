#include "dee_thinking/consolidated.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <algorithm>
#include <sstream>

namespace py=pybind11;
namespace d=dee::thinking;
namespace c=dee::thinking::consolidated;
namespace {
py::list point(d::Coordinate q){py::list a;a.append(q.x);a.append(q.y);a.append(q.z);return a;}
py::list direction(d::Direction q){py::list a;a.append(q.dx);a.append(q.dy);a.append(q.dz);return a;}
py::dict observation(const d::Observation& o){
    py::dict x;x["tick"]=o.tick;x["site"]=point(o.coordinate);x["raw"]=std::to_string(o.raw);x["clock"]=std::to_string(o.clock);
    x["state"]=o.record.state;x["s_reg"]=o.record.s_reg;x["semantic"]=o.record.semantic;
    x["direction"]=direction({o.record.dx,o.record.dy,o.record.dz});x["active"]=o.record.state>0&&o.record.semantic!=5;return x;
}
py::dict readout(const c::DirectionalReadout& r){
    py::dict x;x["physical"]=observation(r.physical);x["applied"]=r.applied;x["covered"]=r.covered;x["coverage"]=r.covered;
    x["value"]=py::cast(r.value);x["status"]=r.status;x["ordinary_cap_reached"]=r.ordinary_cap_reached;x["modality"]=r.modality;x["scope"]=r.scope;
    if(r.receipt){const auto& z=*r.receipt;py::dict q;q["id"]=z.id;q["status"]=d::to_string(z.status);q["kind"]=d::to_string(z.kind);q["requested_tick"]=z.requested_tick;q["effective_tick"]=py::cast(z.effective_tick);q["channels"]=z.channels;q["reason"]=z.reason;x["receipt"]=q;}else x["receipt"]=py::none();return x;
}
py::dict geometry(const c::NativePreparation& p){
    py::dict x;x["schema"]="dee_thinking.consolidated.geometry.v1";x["kind"]=p.kind;x["N"]=p.recipe.dimension;x["K"]=p.forms.size();x["scope"]=p.domain;
    x["initial_state_available"]=p.initial_state_available;x["parameters"]=p.parameters;x["ticks"]=p.ticks;x["ports"]=p.ports;
    py::dict flat,directions;for(const auto& [k,q]:p.sites)flat[k.c_str()]=point(q);for(const auto& [k,q]:p.directions)directions[k.c_str()]=direction(q);
    x["sites"]=flat;x["directions"]=directions;
    py::list fs;for(const auto& f:p.forms){py::dict z;z["index"]=f.index;z["name"]=f.name;z["hub"]=point(f.hub);fs.append(z);}x["forms"]=fs;
    x["initial_material_sites"]=p.parameters.at("initial_material_sites");x["interfaces"]=p.parameters.at("interfaces");x["plane_gap"]=p.parameters.at("plane_gap");
    if(p.kind=="repertoire.cpc5.v1"){
        x["translation"]=point({static_cast<int>(p.parameters.at("translation_x")),static_cast<int>(p.parameters.at("translation_y")),static_cast<int>(p.parameters.at("translation_z"))});
        return x;
    }
    py::dict body;body["n"]=67;body["center"]=point(p.sites.at("body.center"));body["A"]=point(p.sites.at("body.A"));body["B"]=point(p.sites.at("body.B"));body["emission_site"]=point(p.sites.at("body.emission"));
    body["emission_tick"]=5;body["initial_phase"]=260;body["initial_relation"]=0;body["resource_sites"]=11;
    py::dict scalar;scalar["site"]=point(p.sites.at("body.source"));scalar["state"]=6100;scalar["semantic"]=4;scalar["direction"]=direction({});scalar["clock"]="19";
    scalar["initial_load"]=p.parameters.at("body_source_load");scalar["original_load"]=7;scalar["modality"]="INITIAL_PREPARATION; never a RAW edit afterT0";body["prepared_scalar_source"]=scalar;x["body"]=body;
    py::dict need,hubs,branches,banks,action_inputs,actions,names;
    need["prefix"]="need";py::dict nt;
    for(const auto& k:{"comparison","question","information","action","association"})nt[k]=p.ticks.at(k);
    nt["name_query"]=p.ticks.at("name_query_input");nt["name_read"]=p.ticks.at("name_read");need["ticks"]=nt;
    for(int sign:{-1,1}){
        const std::string lane=sign<0?"left":"right";hubs[lane.c_str()]=point(p.sites.at("comparison."+lane));
        for(int dx:{0,sign}){const auto key=lane+(dx==0?".equal":".different");py::dict b;b["lane"]=lane;b["dx"]=dx;b["request_site"]=point(p.sites.at("question."+key));b["comparison_direction"]=direction(p.directions.at("comparison."+key));branches[key.c_str()]=b;}
        py::dict b;b["form"]=p.forms[sign<0?0:1].name;b["hub"]=point(p.sites.at("bank."+lane));b["request_site"]=point(p.sites.at("question."+lane+".different"));b["request_direction"]=sign;b["question_tick"]=19;b["information_tick"]=70;b["question_distance"]=51;b["native_reader"]="Comparison-conditioned horizontal question, not a host probe";banks[lane.c_str()]=b;
        for(int value:{-1,1}){
            const std::string label=value<0?"minus":"plus",key=lane+"."+label;py::dict a;
            a["lane"]=lane;a["candidate_direction_y"]=value;a["site"]=point(p.sites.at("name."+key));
            a["teach_port"]=p.ports.at("name."+key+".teach");a["query_port"]=p.ports.at("name."+key+".query");a["teach_input_tick"]=72;a["association_tick"]=75;a["query_tick"]=139;a["read_tick"]=142;
            a["cue_direction"]=direction(p.directions.at("name."+key));a["prior_action_tick"]=72;a["scope"]="Fixed opaque cue paired after native use; all candidate routes receive it";names[key.c_str()]=a;
        }
    }
    need["comparison_hubs"]=hubs;need["branches"]=branches;x["need"]=need;x["banks"]=banks;x["names"]=names;
    for(const auto& label:{std::string("minus"),std::string("plus")}){
        const auto name="own.use."+label;py::dict a;a["site"]=point(p.sites.at("action_input."+label));a["target"]=point(p.sites.at("action."+label));a["input_tick"]=69;a["read_tick"]=72;a["roles"]=py::make_tuple("left","right");a["direction"]=direction({0,0,1});action_inputs[name.c_str()]=a;
        py::dict z;z["site"]=point(p.sites.at("action."+label));z["read_tick"]=72;z["possible_roles"]=py::make_tuple("left","right");actions[name.c_str()]=z;
    }
    x["action_inputs"]=action_inputs;x["actions"]=actions;x["traditional_datasource_interfaces_installed"]=false;
    x["shared_interface_policy"]="Coincident physical action ports are one shared resource; schedule once per unique interface.";
    py::dict guard;const auto mode=p.parameters.at("guard_mode");guard["mode"]=mode==0?"none":mode==1?"treatment":"sham";guard["placement_modality"]="INITIAL_PREPARATION beforeT0; never a MAIN state edit";
    py::list objects;for(int i=0;i<6;++i){auto it=p.sites.find("guard."+std::to_string(i));if(it==p.sites.end())continue;py::dict z;z["site"]=point(it->second);
        const auto material=std::find_if(p.recipe.placements.begin(),p.recipe.placements.end(),[&](const auto& v){return v.site==it->second;});
        if(material!=p.recipe.placements.end()){z["raw"]=std::to_string(material->raw);z["clock"]=std::to_string(material->clock);z["role"]=material->role;}objects.append(z);}
    guard["objects"]=objects;guard["resources_extra"]=objects.size();guard["state"]=1;guard["load"]=0;guard["semantic"]=4;guard["clock"]="0";guard["direction"]=direction({});guard["scope"]="Fixed prepared interception, not a learned regulation policy";x["residue_guard"]=guard;
    if(p.parameters.at("revision_interfaces")){
        py::dict revision,ports;for(const auto& mode_name:{std::string("treatment"),std::string("offpath_sham")})for(const auto& label:{std::string("minus"),std::string("plus")})ports[(mode_name+"."+label).c_str()]=p.ports.at("revision.teacher2."+mode_name+"."+label);
        revision["schema"]="CPC7.integrated_revision.geometry.v1";revision["form"]="L03";revision["hub"]=point(p.forms[2].hub);revision["input_tick"]=402;revision["revision_contact"]=405;revision["next_panel_input"]=469;revision["next_panel_read"]=472;revision["auxiliary_ports"]=ports;revision["auxiliary_sham_shift"]=point({0,0,55});revision["auxiliary_sham_plane"]=60;revision["scope"]="One directed consequence update; all opportunities present beforeT0";x["integrated_revision"]=revision;
    }
    return x;
}
}

void register_consolidated(py::module_& m){
    py::class_<c::RepertoireOptions>(m,"RepertoireOptions").def(py::init<>())
        .def_readwrite("dimension",&c::RepertoireOptions::dimension).def_readwrite("forms",&c::RepertoireOptions::forms)
        .def_readwrite("plane_gap",&c::RepertoireOptions::plane_gap).def_readwrite("translation",&c::RepertoireOptions::translation)
        .def_readwrite("revision_interfaces",&c::RepertoireOptions::revision_interfaces).def_readwrite("revision_form",&c::RepertoireOptions::revision_form).def_readwrite("execution",&c::RepertoireOptions::execution);
    py::class_<c::IntegratedOptions>(m,"IntegratedOptions").def(py::init<>())
        .def_readwrite("center",&c::IntegratedOptions::center).def_readwrite("guard_mode",&c::IntegratedOptions::guard_mode)
        .def_readwrite("body_source_load",&c::IntegratedOptions::body_source_load).def_readwrite("revision_interfaces",&c::IntegratedOptions::revision_interfaces).def_readwrite("execution",&c::IntegratedOptions::execution);
    py::class_<c::FormDescriptor>(m,"FormDescriptor").def_readonly("index",&c::FormDescriptor::index).def_readonly("name",&c::FormDescriptor::name).def_readonly("hub",&c::FormDescriptor::hub);
    py::class_<c::NativePreparation>(m,"NativePreparation").def(py::init<>())
        .def_property_readonly("recipe",[](const c::NativePreparation& p){return p.recipe;})
        .def_readonly("kind",&c::NativePreparation::kind).def_readonly("domain",&c::NativePreparation::domain)
        .def_readonly("forms",&c::NativePreparation::forms).def_readonly("sites",&c::NativePreparation::sites)
        .def_readonly("directions",&c::NativePreparation::directions).def_readonly("ticks",&c::NativePreparation::ticks)
        .def_readonly("ports",&c::NativePreparation::ports).def_readonly("parameters",&c::NativePreparation::parameters)
        .def_readonly("initial_state_available",&c::NativePreparation::initial_state_available)
        .def("create_world",&c::NativePreparation::create_world).def("geometry",&geometry);
    py::class_<c::DirectionalReadout>(m,"DirectionalReadout").def_readonly("physical",&c::DirectionalReadout::physical)
        .def_readonly("receipt",&c::DirectionalReadout::receipt).def_readonly("applied",&c::DirectionalReadout::applied)
        .def_readonly("covered",&c::DirectionalReadout::covered).def_readonly("coverage",&c::DirectionalReadout::covered)
        .def_readonly("ordinary_cap_reached",&c::DirectionalReadout::ordinary_cap_reached).def_readonly("value",&c::DirectionalReadout::value)
        .def_readonly("status",&c::DirectionalReadout::status).def_readonly("modality",&c::DirectionalReadout::modality).def_readonly("scope",&c::DirectionalReadout::scope).def("as_dict",&readout);
    m.def("prepare_repertoire",&c::prepare_repertoire,py::arg("options")=c::RepertoireOptions{});
    m.def("prepare_integrated_u0",&c::prepare_integrated_u0,py::arg("options")=c::IntegratedOptions{});
    m.def("preparation_for_world",&c::preparation_for_world,py::arg("world"));
    m.def("attach_preparation_descriptor",&c::attach_preparation_descriptor,py::arg("world"),py::arg("preparation"));
    m.def("experience_form",&c::experience_form,py::arg("world"),py::arg("preparation"),py::arg("form_index"),py::arg("current_sign"),py::arg("at_tick"),py::arg("cue_load")=5,py::arg("event_load")=11);
    m.def("query_form",&c::query_form,py::arg("world"),py::arg("preparation"),py::arg("form_index"),py::arg("payload"),py::arg("at_tick"));
    m.def("revise_form",&c::revise_form,py::arg("world"),py::arg("preparation"),py::arg("form_index"),py::arg("current_sign"),py::arg("at_tick"),py::arg("method")="double_teacher",py::arg("mode")="treatment",py::arg("cue_load")=5,py::arg("event_load")=11);
    m.def("read_directional_response",&c::read_directional_response,py::arg("world"),py::arg("site"),py::arg("receipt_id"),py::arg("probe_load"),py::arg("expected_read_tick")=std::nullopt);
    m.def("read_form_response",&c::read_form_response,py::arg("world"),py::arg("preparation"),py::arg("form_index"),py::arg("receipt_id"),py::arg("probe_load"),py::arg("expected_read_tick")=std::nullopt);
}
