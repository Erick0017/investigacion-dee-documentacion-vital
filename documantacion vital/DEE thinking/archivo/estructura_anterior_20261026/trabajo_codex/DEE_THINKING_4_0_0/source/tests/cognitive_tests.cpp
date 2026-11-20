#include "dee_thinking/cognitive.hpp"
#include "test_support.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <type_traits>
using namespace dee::thinking;
using namespace dee::thinking::test;
static_assert(!std::is_copy_constructible_v<CognitiveSession> && std::is_move_constructible_v<CognitiveSession>);
static_assert(!std::is_copy_constructible_v<NativeAssociationSession> && std::is_move_constructible_v<NativeAssociationSession>);
namespace {
bool same(const Runtime& a,const Runtime& b){return a.current_tick()==b.current_tick()&&a.raw_copy()==b.raw_copy()&&a.clock_copy()==b.clock_copy();}
CognitiveParameters params(const std::string& seed,std::string profile="continuity"){CognitiveParameters p;p.seed_path=seed;p.profile=std::move(profile);return p;}
}
int main(int argc,char** argv){
    if(argc==4&&std::string(argv[1])=="--write-pending"){
        auto e=CognitiveSession::create(params(argv[2],"comparison"));e.sense();e.predict();e.set_interface_metadata("cross_language","cpp_pending");e.save_snapshot(argv[3]);std::cout<<"CXX_PENDING "<<e.tick()<<'\n';return 0;
    }
    if(argc==4&&std::string(argv[1])=="--continue"){
        auto e=CognitiveSession::load_snapshot(argv[2]);auto x=e.compare();e.save_snapshot(argv[3]);std::cout<<"CXX_CONTINUED "<<e.tick()<<' '<<x.status<<' '<<x.readout.physical_output.raw<<' '<<x.readout.physical_output.clock<<'\n';return 0;
    }
    if(argc<3)return 2;Suite s("cognitive_4_0");const std::string seed=argv[1];const auto dir=std::filesystem::path(argv[2]);std::filesystem::create_directories(dir);
    auto p=params(seed);auto invalid=p;invalid.profile="universal";DEE_CHECK_THROWS(s,CognitiveSession::create(invalid));invalid=p;invalid.origin.x=47;DEE_CHECK_THROWS(s,CognitiveSession::create(invalid));
    auto e=CognitiveSession::create(p);auto before=e.world().runtime().raw_copy(),clocks=e.world().runtime().clock_copy();for(int j=0;j<5;++j)e.observe();DEE_CHECK_EQ(s,before,e.world().runtime().raw_copy());DEE_CHECK_EQ(s,clocks,e.world().runtime().clock_copy());
    auto acquired=e.sense();DEE_CHECK_EQ(s,e.tick(),34ULL);DEE_CHECK_EQ(s,acquired.receipts.size(),std::size_t(2));for(auto r:acquired.receipts)DEE_CHECK(s,r.status==EventStatus::Applied);DEE_CHECK_EQ(s,*e.observe().memory.delta,-1);
    auto em=e.predict();DEE_CHECK_EQ(s,e.tick(),37ULL);DEE_CHECK_EQ(s,em.prediction->prediction_set,std::vector<bool>{false});DEE_CHECK_EQ(s,em.prediction->target_tick,67ULL);
    auto diagnostic=e.fork();diagnostic.sense();DEE_CHECK_EQ(s,e.tick(),37ULL);DEE_CHECK_EQ(s,diagnostic.tick(),164ULL);DEE_CHECK_EQ(s,e.journal().back().operation,std::string("world.run_until"));
    e.set_interface_metadata("alias","sensor externo");auto snap=(dir/"continuity.deetsnap").string();e.save_snapshot(snap);auto copy=CognitiveSession::load_snapshot(snap);DEE_CHECK(s,same(e.world().runtime(),copy.world().runtime()));DEE_CHECK_EQ(s,copy.get_interface_metadata("alias"),std::optional<std::string>("sensor externo"));DEE_CHECK_EQ(s,copy.predictions().size(),e.predictions().size());
    auto x=e.sense(),y=copy.sense();DEE_CHECK_EQ(s,x.receipts[0].status,y.receipts[0].status);DEE_CHECK(s,same(e.world().runtime(),copy.world().runtime()));DEE_CHECK_EQ(s,e.tick(),164ULL);DEE_CHECK_EQ(s,x.receipts[0].status,EventStatus::Applied);DEE_CHECK_EQ(s,*e.observe().memory.delta,-1);
    auto no_rewind=e.tick();DEE_CHECK_THROWS(s,e.run_until(no_rewind-1));DEE_CHECK_THROWS(s,e.experience("C"));DEE_CHECK_THROWS(s,e.advance(std::numeric_limits<std::uint64_t>::max()));
    for(bool initial:{false,true})for(bool change:{false,true}){
        auto q=params(seed,"comparison");q.initial_open=initial;if(!change)q.change_tick.reset();auto c=CognitiveSession::create(q);c.sense();auto f=c.predict();DEE_CHECK_EQ(s,c.tick(),37ULL);DEE_CHECK(s,f.prediction->prediction_set==std::vector<bool>{initial});DEE_CHECK_EQ(s,c.predict().status,std::string("ONE_PENDING_EXPECTATION_ALREADY_REGISTERED"));
        auto name=(dir/(std::string("pending_")+(initial?"1":"0")+(change?"1":"0")+".deetsnap")).string();c.save_snapshot(name);auto restored=CognitiveSession::load_snapshot(name);auto a=c.compare(),b=restored.compare();DEE_CHECK(s,same(c.world().runtime(),restored.world().runtime()));DEE_CHECK_EQ(s,c.tick(),84ULL);DEE_CHECK_EQ(s,a.receipts[0].status,EventStatus::Applied);DEE_CHECK_EQ(s,a.comparison->presentation,std::string(change?"discrepancia_direccional":"coincidencia_direccional"));DEE_CHECK_EQ(s,a.comparison->presentation,b.comparison->presentation);DEE_CHECK_EQ(s,c.predict().status,std::string("OUTSIDE_FORECAST_DOMAIN"));c.advance(1);DEE_CHECK(s,c.observe().comparison->presentation.empty());
    }
    auto late=CognitiveSession::create(params(seed,"comparison"));late.sense();late.predict();late.run_until(84);auto count=late.world().runtime().receipts().size();DEE_CHECK_EQ(s,late.compare().status,std::string("MISSED_COMPARISON_WINDOW"));DEE_CHECK_EQ(s,count,late.world().runtime().receipts().size());
    auto a=NativeAssociationSession::create();auto trained=a.train({7,11});DEE_CHECK_EQ(s,trained.receipts.size(),std::size_t(4));auto af=a.fork();af.query_panel();DEE_CHECK_EQ(s,a.tick(),6ULL);DEE_CHECK_EQ(s,af.tick(),11ULL);a.set_interface_metadata("form0","tavu");auto ap=(dir/"association.deetsnap").string();a.save_snapshot(ap);auto b=NativeAssociationSession::load_snapshot(ap);auto ar=a.query_panel(),br=b.query_panel();DEE_CHECK_EQ(s,*ar.decoded.at("q0"),25);DEE_CHECK_EQ(s,*ar.decoded.at("q1"),29);DEE_CHECK(s,same(a.world().runtime(),b.world().runtime()));DEE_CHECK_EQ(s,ar.outputs.at("q0").raw,br.outputs.at("q0").raw);DEE_CHECK_THROWS(s,a.train({7,11}));DEE_CHECK_THROWS(s,a.query(2));
    auto c=create_learnable_cascade(2);auto receipts=experience_composition(c,{{3,9},{3,11}});for(auto r:receipts)DEE_CHECK_EQ(s,r.status,EventStatus::Applied);auto response=query_composition(c,13);DEE_CHECK_EQ(s,*response.decoded.at("stage0"),25);DEE_CHECK_EQ(s,*response.decoded.at("stage1"),39);
    auto legacy=CognitiveSession::load_legacy_physical_snapshot(seed);DEE_CHECK_EQ(s,legacy.current_tick(),32ULL);DEE_CHECK_THROWS(s,CognitiveSession::load_snapshot(seed));
    std::ofstream trunc(dir/"truncated.deetsnap",std::ios::binary);trunc<<"not a snapshot";trunc.close();DEE_CHECK_THROWS(s,CognitiveSession::load_snapshot((dir/"truncated.deetsnap").string()));
    return s.finish();
}
