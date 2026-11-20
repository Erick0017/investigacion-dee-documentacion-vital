#include "dee_thinking/organizational.hpp"
#include "dee_thinking/version.hpp"
#include "test_support.hpp"
#include <filesystem>
#include <fstream>
#include <limits>
using namespace dee::thinking;
using namespace dee::thinking::test;

bool same(const Runtime& a,const Runtime& b){return a.dimension()==b.dimension()&&a.current_tick()==b.current_tick()&&a.raw_copy()==b.raw_copy()&&a.clock_copy()==b.clock_copy();}
void learn(OrganizationalWorld& w,int second=11){for(int j=0;j<2;++j){w.submit("l"+std::to_string(j)+".cue",5,0);w.submit("l"+std::to_string(j)+".teacher",j?second:7,0);}w.run_until(6);}
int main(int argc,char** argv){
    Suite s("organizational_3_5");if(argc<3)return 2;const std::string seed=argv[1];const auto dir=std::filesystem::path(argv[2]);std::filesystem::create_directories(dir);
    DEE_CHECK_EQ(s,std::string(kProductVersion),std::string("4.5.0"));
    auto mobile=OrganizationalWorld::create(OrganizationRecipe::mobile_pair());learn(mobile);
    auto independent=mobile.fork();independent.probe("q0.query",13,6);independent.probe("q1.query",13,6);independent.run_until(11);
    DEE_CHECK_EQ(s,independent.observe("q0","response").record.s_reg,25);DEE_CHECK_EQ(s,independent.observe("q1","response").record.s_reg,29);
    const auto physical=mobile.runtime().raw_copy(),clock=mobile.runtime().clock_copy();auto v=mobile.view("q0");for(int j=0;j<8;++j){v.observe();v.resilience();}DEE_CHECK_EQ(s,physical,mobile.runtime().raw_copy());DEE_CHECK_EQ(s,clock,mobile.runtime().clock_copy());
    mobile.start_mobile_sequence("sequence",{0,1,2,3,4});mobile.run_until(13);
    auto snap=dir/"sequence.deetsnap";mobile.save_snapshot(snap.string());auto restored=OrganizationalWorld::load_snapshot(snap.string());
    DEE_CHECK(s,same(mobile.runtime(),restored.runtime()));DEE_CHECK_EQ(s,restored.protocols()[0].next_capture,std::size_t(1));
    mobile.run_until(31);restored.run_until(31);DEE_CHECK(s,same(mobile.runtime(),restored.runtime()));
    DEE_CHECK_EQ(s,restored.protocols()[0].steps.back().captured[0].record.s_reg,22);DEE_CHECK_EQ(s,restored.protocols()[0].steps.back().captured[1].record.s_reg,26);
    DEE_CHECK_EQ(s,mobile.runtime().receipts().size(),restored.runtime().receipts().size());
    auto retained_view=[&]{auto w=OrganizationalWorld::create(OrganizationRecipe::competition());return w.view("encounter");}();DEE_CHECK_EQ(s,retained_view.runtime().dimension(),34);
    auto rt=std::make_shared<Runtime>(9);auto recipe=OrganizationRecipe::research(9,{});OrganizationSpec os;os.id="inert";os.ports={{"site",{1,1,1}}};auto attached=OrganizationalWorld::attach(rt,recipe,{os});DEE_CHECK(s,same(*rt,attached.runtime()));DEE_CHECK_EQ(s,rt->channel_names().size(),std::size_t(0));
    rt.reset();DEE_CHECK_EQ(s,attached.view("inert").runtime().dimension(),9);
    InputCodec codec;codec.minimum=1;codec.maximum=17;DEE_CHECK_EQ(s,codec.encode_integer(5),5);DEE_CHECK_THROWS(s,codec.encode_integer(-1));DEE_CHECK_THROWS(s,codec.encode_integer(65536));
    codec.type=CodecType::Boolean;codec.minimum=0;codec.maximum=1;DEE_CHECK_EQ(s,codec.encode_integer(1),1);DEE_CHECK_THROWS(s,codec.encode_integer(2));
    codec.type=CodecType::Enumeration;codec.symbols={{"Sensor_Activo",7},{"alias",7},{"other",11}};DEE_CHECK(s,!codec.injective());DEE_CHECK_EQ(s,codec.encode_symbol("other"),11);DEE_CHECK_THROWS(s,codec.encode_symbol("missing"));
    OutputDecoder decoder;decoder.type=CodecType::Enumeration;decoder.symbols=codec.symbols;Observation o;o.raw=dee::v27::pack_record(1,7,1,0,0,1);o.record=dee::v27::decode_record(o.raw);DEE_CHECK(s,decoder.decode(o).ambiguous);o.raw=0;o.record=dee::v27::decode_record(0);DEE_CHECK(s,!decoder.decode(o).available);
    auto body=OrganizationalWorld::create(OrganizationRecipe::relational(seed));body.advance(25);DEE_CHECK_EQ(s,body.view("body").observe().delta,std::optional<std::int64_t>(1));
    auto q=body.fork();q.probe("body.common_query",7,q.runtime().current_tick());q.advance(3);auto reply=q.observe("body","comparator");DEE_CHECK_EQ(s,reply.record.dx,1);DEE_CHECK_EQ(s,reply.record.s_reg,7);
    auto ba=OrganizationalWorld::create(OrganizationRecipe::relational(seed,basal::History::BA));ba.advance(25);ba.probe("body.common_query",7,ba.runtime().current_tick());ba.advance(3);DEE_CHECK_EQ(s,ba.observe("body","comparator").record.dx,-1);
    ResearchStateEdit e;e.coordinate=*body.view("body").spec().a;e.raw=0;e.label="explicit missing A";DEE_CHECK_THROWS(s,body.diagnostic_fork({e},false));auto damaged=body.diagnostic_fork({e},true);DEE_CHECK(s,!damaged.view("body").observe().delta);DEE_CHECK_EQ(s,body.view("body").observe().delta,std::optional<std::int64_t>(1));
    ReconstructionSpec rr;rr.source_sites={*body.view("body").spec().a};rr.destination_sites=rr.source_sites;rr.authorize_assisted_reconstruction=true;auto rescued=damaged.assisted_reconstruction(body,rr);DEE_CHECK_EQ(s,rescued.view("body").observe().delta,std::optional<std::int64_t>(1));DEE_CHECK_EQ(s,rescued.diagnostic_edits().back().modality,OperationModality::AssistedReconstruction);
    auto context=OrganizationalWorld::create(OrganizationRecipe::contextual(seed));context.advance(131);auto gate=observation::inspect_write_gate(context.runtime(),*context.view("body").spec().b);DEE_CHECK_EQ(s,gate.local_clock,std::uint64_t(391));DEE_CHECK_EQ(s,gate.n_active,6);context.advance();DEE_CHECK_EQ(s,context.view("body").observe().delta,std::optional<std::int64_t>(0));
    auto blocked=OrganizationalWorld::create(OrganizationRecipe::contextual(seed));InterfaceSpec event;event.name="zero_event";event.channel={event.name,{16,16,15},1,{0,0,1},1,true,true};blocked.declare_interface(event);blocked.submit("zero_event",0,162);blocked.run_until(164);DEE_CHECK_EQ(s,blocked.view("body").observe().delta,std::optional<std::int64_t>(1));
    auto bridge=OrganizationalWorld::create(OrganizationRecipe::mobile_basal(seed));TraceSession tr;tr.sample_budget=30;tr.sites={{"comparator",{15,15,15}}};bridge.set_trace(tr);auto plain=bridge.fork();plain.set_trace(TraceSession{});bridge.advance(12);plain.advance(12);DEE_CHECK(s,same(bridge.runtime(),plain.runtime()));DEE_CHECK_EQ(s,bridge.observe("body","comparator").record.s_reg,12);
    bridge.save_snapshot((dir/"bridge.deetsnap").string());auto bcopy=OrganizationalWorld::load_snapshot((dir/"bridge.deetsnap").string());DEE_CHECK_EQ(s,bcopy.trace().samples.size(),bridge.trace().samples.size());bridge.trace().export_trace((dir/"trace.deetrace").string());DEE_CHECK_EQ(s,TraceSession::load_trace((dir/"trace.deetrace").string()).samples.size(),bridge.trace().samples.size());
    for(int depth:{2,4,8}){auto w=OrganizationalWorld::create(OrganizationRecipe::cascade(depth));w.probe("query",13,6);w.run_until(11+5*(depth-1));DEE_CHECK_EQ(s,w.observe("stage"+std::to_string(depth-1),"response").record.s_reg,depth==2?39:depth==4?73:165);}
    auto relay=OrganizationalWorld::create(OrganizationRecipe::native_transfer());relay.probe("query",0,6);relay.probe("receiver_query",13,16);relay.run_until(21);DEE_CHECK_EQ(s,relay.observe("stage0","receiver_response").record.s_reg,25);
    auto phase=OrganizationalWorld::create(OrganizationRecipe::phase(1));phase.advance(40);DEE_CHECK_EQ(s,phase.observe("phase","hub").record.s_reg,41);
    auto distributed=OrganizationalWorld::create(OrganizationRecipe::distributed());distributed.submit("integration.A",8,0);distributed.submit("integration.B",9,0);distributed.run_until(12);DEE_CHECK_EQ(s,distributed.observe("integration","q").record.s_reg,391);distributed.run_until(700);DEE_CHECK_EQ(s,distributed.observe("integration","q").record.s_reg,19664);DEE_CHECK_EQ(s,distributed.view("history").observe().delta,std::optional<std::int64_t>(1));
    auto action=OrganizationalWorld::create(OrganizationRecipe::contingent(seed));action.advance(13);DEE_CHECK_EQ(s,action.observe("body","environment").record.s_reg,48);
    auto information=OrganizationalWorld::create(OrganizationRecipe::information(seed));information.advance(16);DEE_CHECK_EQ(s,information.observe("body","downstream").record.s_reg,43);
    auto encounter=OrganizationalWorld::create(OrganizationRecipe::competition());encounter.run_until(5);auto pre=encounter.runtime().fork();encounter.advance();auto en=observe_encounter(pre,encounter.runtime(),encounter.view("encounter").spec().ports.at("meeting"));DEE_CHECK_EQ(s,en.direct_ballistic_contributors.size(),std::size_t(2));DEE_CHECK_EQ(s,en.after.record.s_reg,36);
    encounter.probe("joint_query",13,6);encounter.run_until(14);auto joint=encounter.fork();joint.probe("later_query",17,14);joint.run_until(20);DEE_CHECK_EQ(s,joint.observe("encounter","later_response").record.s_reg,66);
    auto pending=OrganizationalWorld::create(OrganizationRecipe::mobile_pair());pending.submit("l0.cue",5,0);pending.submit("l0.teacher",7,0);pending.save_snapshot((dir/"pending.deetsnap").string());auto pending_copy=OrganizationalWorld::load_snapshot((dir/"pending.deetsnap").string());pending.advance(3);pending_copy.advance(3);DEE_CHECK(s,same(pending.runtime(),pending_copy.runtime()));
    auto bp=OrganizationalWorld::create(OrganizationRecipe::mobile_pair());learn(bp);auto dense=bp.fork(),parallel=bp.fork();dense.runtime().set_execution_options({dee::v27::Backend::DenseSequential,1});parallel.runtime().set_execution_options({dee::v27::Backend::DenseParallel,2});for(auto* w:{&bp,&dense,&parallel}){w->probe("q0.query",13,6);w->advance(5);}DEE_CHECK(s,same(bp.runtime(),dense.runtime()));DEE_CHECK(s,same(bp.runtime(),parallel.runtime()));
    auto budget=OrganizationalWorld::create(OrganizationRecipe::mobile_pair());TraceSession t;t.sample_budget=2;t.sites={{"site",{1,1,1}}};budget.set_trace(t);budget.advance(10);DEE_CHECK(s,budget.trace().capture_stopped);DEE_CHECK_EQ(s,budget.runtime().current_tick(),std::uint64_t(10));DEE_CHECK_EQ(s,budget.trace().samples.size(),std::size_t(2));
    DEE_CHECK_THROWS(s,OrganizationalWorld::create(OrganizationRecipe::cascade(20)));DEE_CHECK_THROWS(s,OrganizationalWorld::create(OrganizationRecipe::research(10000,{})));DEE_CHECK_THROWS(s,budget.advance(std::numeric_limits<std::uint64_t>::max()));
    InitialPlacement p;p.site={1,1,1};p.raw=0;DEE_CHECK_THROWS(s,OrganizationalWorld::create(OrganizationRecipe::research(7,{p,p})));
    std::ifstream input(snap,std::ios::binary);std::string bytes((std::istreambuf_iterator<char>(input)),{});std::ofstream broken(dir/"truncated.deetsnap",std::ios::binary);broken.write(bytes.data(),20);broken.close();DEE_CHECK_THROWS(s,OrganizationalWorld::load_snapshot((dir/"truncated.deetsnap").string()));
    return s.finish();
}
