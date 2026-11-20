#include "dee_thinking/consolidated.hpp"
#include "test_support.hpp"
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <iterator>
#include <string>
#include <vector>
using namespace dee::thinking;
using namespace dee::thinking::consolidated;
using namespace dee::thinking::test;
namespace {
std::ofstream primary_trace;
DirectionalReadout record_read(DirectionalReadout r,const char* operation,std::size_t form=0){
    if(primary_trace){const auto& o=r.physical;const auto& v=o.record;
        primary_trace << "{\"operation\":" << std::quoted(operation) << ",\"form\":" << form
          << ",\"tick\":" << o.tick << ",\"site\":[" << o.coordinate.x << ',' << o.coordinate.y << ',' << o.coordinate.z
          << "],\"raw\":\"" << o.raw << "\",\"clock\":\"" << o.clock << "\",\"state\":" << v.state
          << ",\"s_reg\":" << v.s_reg << ",\"semantic\":" << int(v.semantic)
          << ",\"direction\":[" << int(v.dx) << ',' << int(v.dy) << ',' << int(v.dz)
          << "],\"applied\":" << (r.applied?"true":"false") << ",\"covered\":" << (r.covered?"true":"false")
          << ",\"status\":" << std::quoted(r.status) << ",\"value\":";
        if(r.value)primary_trace << *r.value;else primary_trace << "null";
        primary_trace << ",\"receipt_id\":";if(r.receipt)primary_trace << r.receipt->id;else primary_trace << "null";
        primary_trace << "}\n";
    }return r;
}
DirectionalReadout traced_form_response(const OrganizationalWorld& w,const NativePreparation& p,std::size_t form,std::uint64_t receipt,std::uint16_t payload,std::optional<std::uint64_t> tick=std::nullopt){
    return record_read(dee::thinking::consolidated::read_form_response(w,p,form,receipt,payload,tick),"read_form_response",form);
}
DirectionalReadout traced_directional_response(const OrganizationalWorld& w,Coordinate site,std::uint64_t receipt,std::uint16_t payload,std::optional<std::uint64_t> tick=std::nullopt){
    return record_read(dee::thinking::consolidated::read_directional_response(w,site,receipt,payload,tick),"read_directional_response");
}
#define read_form_response traced_form_response
#define read_directional_response traced_directional_response
bool same(const OrganizationalWorld& a,const OrganizationalWorld& b){return a.runtime().current_tick()==b.runtime().current_tick()&&a.runtime().raw_copy()==b.runtime().raw_copy()&&a.runtime().clock_copy()==b.runtime().clock_copy();}
template<class Operation>void inert_structure_failure(Suite& s,OrganizationalWorld& w,const std::filesystem::path& out,const std::string& label,Operation operation){
    const auto before=out/(label+"_before.deetsnap"),after=out/(label+"_after.deetsnap");w.save_snapshot(before.string());
    const auto raw=w.runtime().raw_copy(),clocks=w.runtime().clock_copy();const auto tick=w.runtime().current_tick();
    const auto operations=w.external_operations(),channels=w.runtime().channel_names();const auto receipts=w.runtime().receipts().size();
    DEE_CHECK_THROWS(s,operation());w.save_snapshot(after.string());
    auto bytes=[](const auto& path){std::ifstream in(path,std::ios::binary);return std::vector<char>(std::istreambuf_iterator<char>(in),std::istreambuf_iterator<char>());};
    DEE_CHECK_EQ(s,bytes(before),bytes(after));DEE_CHECK_EQ(s,raw,w.runtime().raw_copy());DEE_CHECK_EQ(s,clocks,w.runtime().clock_copy());
    DEE_CHECK_EQ(s,tick,w.runtime().current_tick());DEE_CHECK_EQ(s,operations,w.external_operations());DEE_CHECK_EQ(s,channels,w.runtime().channel_names());DEE_CHECK_EQ(s,receipts,w.runtime().receipts().size());
}
const std::vector<int> values{1,-1,-1,1,1,1,-1,-1,-1,1,1,-1,-1,1,-1,1};
void integrated_before74(OrganizationalWorld& w,const NativePreparation& p,Suite& s){
    w.submit("event.A",3,0);w.submit("event.B",3,1);w.probe("order.read",7,2);
    for(std::size_t k=0;k<8;++k)(void)experience_form(w,p,k,values[k],0);
    w.run_until(5);const auto prediction=w.runtime().observe(p.sites.at("body.emission"));DEE_CHECK_EQ(s,prediction.record.dx,std::int8_t(1));DEE_CHECK_EQ(s,prediction.record.dy,std::int8_t(-1));DEE_CHECK_EQ(s,prediction.record.s_reg,std::uint16_t(7));
    w.run_until(11);w.submit(p.ports.at("actual.left.minus"),17,11);w.submit(p.ports.at("actual.right.minus"),17,11);
    w.run_until(19);const auto question=w.runtime().observe(p.sites.at("question.right.different"));DEE_CHECK_EQ(s,question.record.dx,std::int8_t(1));DEE_CHECK_EQ(s,question.record.dy,std::int8_t(0));DEE_CHECK_EQ(s,question.record.dz,std::int8_t(0));
    w.run_until(69);w.probe("own.use.minus",7,69);w.probe("own.use.plus",7,69);
    w.run_until(70);const auto info=w.runtime().observe(p.sites.at("bank.right"));DEE_CHECK_EQ(s,info.record.dx,std::int8_t(1));DEE_CHECK_EQ(s,info.record.dy,std::int8_t(-1));DEE_CHECK_EQ(s,info.record.s_reg,std::uint16_t(53));
    w.run_until(72);const auto use=w.runtime().observe(p.sites.at("action.minus"));DEE_CHECK_EQ(s,use.record.dx,std::int8_t(1));DEE_CHECK_EQ(s,use.record.dy,std::int8_t(-1));DEE_CHECK_EQ(s,use.record.dz,std::int8_t(1));
    for(const auto& lane:{std::string("left"),std::string("right")})for(const auto& label:{std::string("minus"),std::string("plus")})w.submit(p.ports.at("name."+lane+"."+label+".teach"),5,72);
    w.run_until(74);
}
void integrated_after74(OrganizationalWorld& w,const NativePreparation& p,Suite& s){
    w.run_until(134);for(std::size_t k=8;k<16;++k)(void)experience_form(w,p,k,values[k],134);
    w.run_until(139);std::vector<std::pair<std::string,std::uint64_t>> names;
    for(const auto& lane:{std::string("left"),std::string("right")})for(const auto& label:{std::string("minus"),std::string("plus")}){const auto key=lane+"."+label;names.emplace_back(key,w.probe(p.ports.at("name."+key+".query"),11,139).id);}
    w.run_until(142);std::size_t covered{};for(const auto& [key,id]:names){const auto out=read_directional_response(w,p.sites.at("name."+key),id,11,142);if(out.covered){++covered;DEE_CHECK_EQ(s,key,std::string("right.minus"));DEE_CHECK_EQ(s,out.value,std::optional<int>(-1));}}DEE_CHECK_EQ(s,covered,std::size_t(1));
    for(std::uint64_t tick:{201ULL,335ULL}){
        w.run_until(tick);std::vector<std::uint64_t> ids;for(std::size_t k=2;k<16;++k)ids.push_back(query_form(w,p,k,5,tick).id);w.run_until(tick+3);
        for(std::size_t k=2;k<16;++k){const auto out=read_form_response(w,p,k,ids[k-2],5,tick+3);DEE_CHECK(s,out.covered);DEE_CHECK_EQ(s,out.value,std::optional<int>(values[k]));}
    }
    w.run_until(402);(void)revise_form(w,p,2,1,402);
    w.run_until(469);std::vector<std::uint64_t> ids;for(std::size_t k=2;k<16;++k)ids.push_back(query_form(w,p,k,5,469).id);w.run_until(472);
    for(std::size_t k=2;k<16;++k){const auto out=read_form_response(w,p,k,ids[k-2],5,472);DEE_CHECK(s,out.covered);DEE_CHECK_EQ(s,out.value,std::optional<int>(k==2?1:values[k]));}
}
}
int main(int argc,char** argv){
    Suite s("consolidated_4_5");const auto out=std::filesystem::path(argc>1?argv[1]:"consolidated_test_states");std::filesystem::create_directories(out);primary_trace.open(out/"OBSERVATIONS_CPP.jsonl");
    RepertoireOptions invalid;invalid.forms=0;DEE_CHECK_THROWS(s,prepare_repertoire(invalid));invalid.forms=66;DEE_CHECK_THROWS(s,prepare_repertoire(invalid));invalid.forms=16;invalid.dimension=30;DEE_CHECK_THROWS(s,prepare_repertoire(invalid));invalid.dimension=31;DEE_CHECK_THROWS(s,prepare_repertoire(invalid));invalid.forms=1;invalid.plane_gap=std::numeric_limits<int>::max();DEE_CHECK_THROWS(s,prepare_repertoire(invalid));
    IntegratedOptions bad;bad.guard_mode="learned";DEE_CHECK_THROWS(s,prepare_integrated_u0(bad));bad.guard_mode="treatment";bad.center.x=-1;DEE_CHECK_THROWS(s,prepare_integrated_u0(bad));DEE_CHECK_THROWS(s,NativePreparation{}.create_world());
    {
        RepertoireOptions o;o.forms=2;const auto p=prepare_repertoire(o);
        for(int scenario=0;scenario<6;++scenario){auto r=p.recipe;
            auto target=[&](const std::string& name)->InterfaceSpec&{return *std::find_if(r.interfaces.begin(),r.interfaces.end(),[&](const auto& i){return i.name==name;});};
            auto erase=[&](const std::string& name){std::erase_if(r.interfaces,[&](const auto& i){return i.name==name;});};
            if(scenario==0)erase("L01.event.plus");
            if(scenario==1)erase(p.ports.at("revision.teacher2.treatment.plus"));
            if(scenario==2)target("L01.event.plus").channel.injection_site.z+=1;
            if(scenario==3)target("L01.event.plus").codec.maximum=5;
            if(scenario==4)target("L01.signal").channel.direction.dx=0;
            if(scenario==5)erase(p.ports.at("revision.counter.treatment.minus"));
            auto w=OrganizationalWorld::create(r);(void)w.probe("L02.signal",9,20); // Existing queue must survive a helper error.
            inert_structure_failure(s,w,out,"incompatible_"+std::to_string(scenario),[&](){
                if(scenario==1)return (void)revise_form(w,p,0,1,268);
                if(scenario==4)return (void)query_form(w,p,0,5,67);
                if(scenario==5)return (void)revise_form(w,p,0,1,268,"symmetric_counterflow");
                return (void)experience_form(w,p,0,1,0);
            });
        }
        auto occupied=p.recipe;const auto signal=std::find_if(occupied.interfaces.begin(),occupied.interfaces.end(),[](const auto& i){return i.name=="L01.signal";});
        occupied.placements.push_back({signal->channel.injection_site,dee::v27::pack_record(1,7,0,0,0,1),0,"Physical admission test, not helper configuration"});
        auto w=OrganizationalWorld::create(occupied);const auto q=experience_form(w,p,0,1,0);DEE_CHECK_EQ(s,q[0].status,EventStatus::Scheduled);
        w.run_until(1);DEE_CHECK_EQ(s,w.runtime().receipt(q[0].id)->status,EventStatus::RejectedOccupied);
    }
    for(std::size_t k=1;k<=65;++k){RepertoireOptions o;o.dimension=131;o.forms=k;o.revision_interfaces=false;auto p=prepare_repertoire(o);DEE_CHECK_EQ(s,p.forms.size(),k);DEE_CHECK_EQ(s,p.recipe.interfaces.size(),3*k);DEE_CHECK(s,p.recipe.placements.empty());}
    {
        RepertoireOptions o;o.forms=2;auto p=prepare_repertoire(o);auto w=p.create_world();DEE_CHECK_EQ(s,w.runtime().current_tick(),0ULL);DEE_CHECK_EQ(s,w.interfaces().size(),std::size_t(14));
        DEE_CHECK_THROWS(s,experience_form(w,p,0,0,0));DEE_CHECK_THROWS(s,query_form(w,p,2,5,67));
        (void)experience_form(w,p,0,-1,0);(void)experience_form(w,p,1,1,0);w.run_until(3);
        auto a=query_form(w,p,0,5,67),b=query_form(w,p,1,5,67);const auto pending=read_form_response(w,p,0,a.id,5);DEE_CHECK(s,!pending.applied&&!pending.value);
        w.run_until(70);auto r=read_form_response(w,p,0,a.id,5,70);DEE_CHECK(s,r.covered);DEE_CHECK_EQ(s,r.value,std::optional<int>(-1));DEE_CHECK_EQ(s,read_form_response(w,p,1,b.id,5,70).value,std::optional<int>(1));
        auto raw=w.runtime().raw_copy(),clocks=w.runtime().clock_copy();for(int j=0;j<5;++j)(void)read_form_response(w,p,0,a.id,5,70);DEE_CHECK_EQ(s,raw,w.runtime().raw_copy());DEE_CHECK_EQ(s,clocks,w.runtime().clock_copy());
        DEE_CHECK(s,!read_form_response(w,p,1,a.id,5,70).covered);DEE_CHECK(s,!read_form_response(w,p,0,a.id,5,71).covered);
        (void)revise_form(w,p,0,1,268);const auto snap=(out/"repertoire_pending.deetsnap").string();w.save_snapshot(snap);auto loaded=OrganizationalWorld::load_snapshot(snap);auto restored=preparation_for_world(loaded);DEE_CHECK(s,!restored.initial_state_available);DEE_CHECK_THROWS(s,restored.create_world());DEE_CHECK(s,same(w,loaded));
        const auto q0=query_form(w,p,0,5,335),q1=query_form(w,p,1,5,335);const auto l0=query_form(loaded,restored,0,5,335),l1=query_form(loaded,restored,1,5,335);w.run_until(338);loaded.run_until(338);DEE_CHECK(s,same(w,loaded));
        DEE_CHECK_EQ(s,read_form_response(w,p,0,q0.id,5,338).value,std::optional<int>(1));DEE_CHECK_EQ(s,read_form_response(w,p,1,q1.id,5,338).value,std::optional<int>(1));DEE_CHECK_EQ(s,read_form_response(loaded,restored,0,l0.id,5,338).value,std::optional<int>(1));DEE_CHECK_EQ(s,read_form_response(loaded,restored,1,l1.id,5,338).value,std::optional<int>(1));
        DEE_CHECK_THROWS(s,revise_form(w,p,1,-1,268));DEE_CHECK_THROWS(s,revise_form(w,p,0,-1,269));
    }
    {
        RepertoireOptions o;o.forms=2;auto p=prepare_repertoire(o);auto w=p.create_world();(void)experience_form(w,p,0,1,0);(void)experience_form(w,p,1,-1,0);auto a=query_form(w,p,0,9,67),b=query_form(w,p,1,9,67);w.run_until(70);DEE_CHECK(s,read_form_response(w,p,0,a.id,9,70).covered);DEE_CHECK(s,read_form_response(w,p,1,b.id,9,70).covered);
        (void)revise_form(w,p,0,-1,268,"symmetric_counterflow");a=query_form(w,p,0,9,335);b=query_form(w,p,1,9,335);w.run_until(338);DEE_CHECK_EQ(s,read_form_response(w,p,0,a.id,9,338).value,std::optional<int>(-1));DEE_CHECK_EQ(s,read_form_response(w,p,1,b.id,9,338).value,std::optional<int>(-1));
    }
    {
        RepertoireOptions o;o.dimension=131;o.forms=65;o.revision_interfaces=false;auto p=prepare_repertoire(o);auto w=p.create_world();
        for(std::size_t k=0;k<65;++k)(void)experience_form(w,p,k,k%3==0?-1:1,0);
        for(std::uint64_t cycle=1;cycle<=3;++cycle){std::vector<std::uint64_t> ids;const auto at=131*cycle;for(std::size_t k=0;k<65;++k)ids.push_back(query_form(w,p,k,9,at).id);w.run_until(at+3);for(std::size_t k=0;k<65;++k){const auto r=read_form_response(w,p,k,ids[k],9,at+3);DEE_CHECK(s,r.covered);DEE_CHECK_EQ(s,r.value,std::optional<int>(k%3==0?-1:1));}}
    }
    {
        std::vector<std::uint64_t> raw,clock;for(auto backend:{dee::v27::Backend::DenseSequential,dee::v27::Backend::DenseParallel,dee::v27::Backend::Lazy}){
            RepertoireOptions o;o.forms=2;o.execution={backend,backend==dee::v27::Backend::DenseSequential?1U:2U};auto p=prepare_repertoire(o);auto w=p.create_world();(void)experience_form(w,p,0,-1,0);(void)experience_form(w,p,1,1,0);(void)query_form(w,p,0,5,67);(void)query_form(w,p,1,5,67);w.run_until(70);if(raw.empty()){raw=w.runtime().raw_copy();clock=w.runtime().clock_copy();}else{DEE_CHECK_EQ(s,raw,w.runtime().raw_copy());DEE_CHECK_EQ(s,clock,w.runtime().clock_copy());}}
    }
    {
        auto p=prepare_integrated_u0();DEE_CHECK_EQ(s,p.forms.size(),std::size_t(16));DEE_CHECK_EQ(s,p.recipe.placements.size(),std::size_t(21));DEE_CHECK_EQ(s,p.recipe.interfaces.size(),std::size_t(69));
        auto w=p.create_world();integrated_before74(w,p,s);const auto snapshot=(out/"integrated74.deetsnap").string();w.save_snapshot(snapshot);auto loaded=OrganizationalWorld::load_snapshot(snapshot);const auto restored=preparation_for_world(loaded);DEE_CHECK(s,same(w,loaded));
        integrated_after74(w,p,s);integrated_after74(loaded,restored,s);DEE_CHECK(s,same(w,loaded));DEE_CHECK_EQ(s,w.runtime().current_tick(),472ULL);
        DEE_CHECK_THROWS(s,revise_form(w,p,2,-1,402,"symmetric_counterflow"));
    }
    {
        RepertoireOptions o;o.forms=1;o.revision_interfaces=false;auto p=prepare_repertoire(o);auto legacy_recipe=p.recipe;legacy_recipe.options.erase("dee_thinking.consolidated.descriptor.v1");auto legacy=OrganizationalWorld::create(legacy_recipe);
        (void)experience_form(legacy,p,0,1,0);legacy.run_until(3);const auto raw=legacy.runtime().raw_copy(),clock=legacy.runtime().clock_copy();DEE_CHECK_THROWS(s,preparation_for_world(legacy));attach_preparation_descriptor(legacy,p);DEE_CHECK_EQ(s,raw,legacy.runtime().raw_copy());DEE_CHECK_EQ(s,clock,legacy.runtime().clock_copy());DEE_CHECK_EQ(s,legacy.runtime().current_tick(),3ULL);
        const auto restored=preparation_for_world(legacy);const auto q=query_form(legacy,restored,0,5,67);legacy.run_until(70);DEE_CHECK_EQ(s,read_form_response(legacy,restored,0,q.id,5,70).value,std::optional<int>(1));
        legacy.runtime().set_snapshot_metadata("dee_thinking.consolidated.attached_descriptor.v1","CNATIVE1 truncated");DEE_CHECK_THROWS(s,preparation_for_world(legacy));
    }
    return s.finish();
}
