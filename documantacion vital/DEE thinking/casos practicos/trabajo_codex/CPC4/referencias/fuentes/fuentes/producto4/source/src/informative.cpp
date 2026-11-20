#include "dee_thinking/informative.hpp"
#include <algorithm>
#include <array>
#include <limits>
#include <set>
#include <stdexcept>
#include <tuple>
#include <utility>

namespace dee::thinking {
namespace {
constexpr const char* policy_key="dee_thinking.informative.policy.v1";
constexpr const char* information_key="dee_thinking.informative.native_information.v1";
// With the fixed internal operation/interface names, 8192 journal records plus
// the allowed 512KiB UI map fit the 2MiB metadata bound. Capture truncation never
// stops, resets or repairs the physical Runtime.
constexpr std::size_t journal_limit=8192, metadata_limit=2U*1024U*1024U;
constexpr Direction policy_p{1,0,0}, policy_q{0,1,0}, sensor{-1,0,1};
constexpr Direction action_p{0,0,1}, action_q{-1,1,1};
void require(bool v,const char* message){if(!v)throw std::invalid_argument(message);}
bool active(const Observation& o){return o.record.state>0&&o.record.semantic!=5;}
bool direction(const Observation& o,Direction v){return o.record.dx==v.dx&&o.record.dy==v.dy&&o.record.dz==v.dz;}
Coordinate moved(Coordinate q,Direction d,std::int64_t steps,int n){
    const auto k=steps%n;auto wrap=[n](std::int64_t v){v%=n;return static_cast<int>(v<0?v+n:v);};
    return {wrap(q.x+d.dx*k),wrap(q.y+d.dy*k),wrap(q.z+d.dz*k)};
}
void check_origin(Coordinate q,int n){(void)v27::linear_index(q.x,q.y,q.z,n);}
void check_execution(v27::TickOptions x){require(x.threads>0&&x.threads<=1024,"native thread count outside [1,1024]");require(static_cast<unsigned>(x.backend)<=2,"unknown backend");}
void check_policy(const FinitePolicyParameters& p){check_origin(p.origin,67);require(p.roles==SourceRole::PInformative||p.roles==SourceRole::QInformative,"unknown source role");require(p.actual_class==-1||p.actual_class==1,"actual report must be -1 or +1");check_execution(p.execution);}
void check_information(const NativeInformationParameters& p){check_origin(p.origin,47);require(!p.seed_path.empty()&&p.seed_path.size()<=32768,"seed path missing or too long");require(p.history==basal::History::AB||p.history==basal::History::BA||p.history==basal::History::H0,"native information history must be AB, BA or H0");require(p.context==0||p.context==1,"context must be 0 or 1");require(p.actual_class==-1||p.actual_class==1,"actual report must be -1 or +1");require(p.distance==10,"published native information geometry requires distance10");require(p.source_cut.empty()||p.source_cut=="P"||p.source_cut=="Q","source_cut must be empty, P or Q");check_execution(p.execution);}
void validate_interface_metadata(const std::map<std::string,std::string>& values){require(values.size()<=128,"interface metadata entry limit");std::size_t bytes=0;for(const auto& [k,v]:values){require(!k.empty()&&k.size()<=1024&&v.size()<=65536,"interface metadata size invalid");bytes+=k.size()+v.size();require(bytes<=524288,"interface metadata total limit");}}
InitialPlacement placement(Coordinate q,std::uint16_t load,Direction d,std::uint32_t state=1,std::uint8_t semantic=1,std::uint64_t clock=0,std::string role="prepared_resource"){
    return {q,v27::pack_record(state,load,d.dx,d.dy,d.dz,semantic),clock,std::move(role)};
}
InterfaceSpec interface(std::string name,Coordinate q,Direction d){InterfaceSpec i;i.name=name;i.channel={name,q,1,d,1,true,true};return i;}
struct Preparation {
    int n;std::vector<InitialPlacement> placements;std::map<std::tuple<int,int,int>,std::size_t> sites;
    void put(InitialPlacement p){auto key=std::tuple{p.site.x,p.site.y,p.site.z};auto it=sites.find(key);if(it!=sites.end()){const auto& old=placements[it->second];require(old.raw==p.raw&&old.clock==p.clock,"informative preparation overlaps unlike physical resources");return;}sites.emplace(key,placements.size());placements.push_back(std::move(p));}
    void arrive(Coordinate target,std::int64_t time,Direction dr,std::uint16_t load,std::string role){put(placement(moved(target,dr,-time,n),load,dr,1,1,0,std::move(role)));}
};
void append_operation(std::vector<InformativeOperation>& journal,bool& truncated,InformativeOperation op){if(journal.size()<journal_limit)journal.push_back(std::move(op));else truncated=true;}
void add_current(InformationReadout& r,const OrganizationalWorld& w,const std::string& organization){for(const auto& [key,q]:w.view(organization).spec().ports)r.physical_outputs.emplace(key,w.runtime().observe(q));r.receipts=w.runtime().receipts();}
void require_advance(const OrganizationalWorld& w,std::uint64_t count){require(!w.runtime().paused(),"cannot advance a paused informative Runtime; resume explicitly");require(count<=static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())&&count<=std::numeric_limits<std::uint64_t>::max()-w.runtime().current_tick(),"advance count overflow");}
std::string token(std::uint64_t tick,const std::string& name){return std::to_string(tick)+":"+name;}

// Versioned bounded binary metadata. It contains only inert descriptors,
// protocol cursor, journals and UI metadata; all physical/pending state is in
// the OrganizationalWorld snapshot, never regenerated while loading.
struct Writer {
    std::vector<std::uint8_t> bytes;
    void u64(std::uint64_t v){require(bytes.size()+8<=metadata_limit,"informative metadata size limit");for(int j=0;j<8;++j)bytes.push_back(static_cast<std::uint8_t>(v>>(8*j)));}
    void boolean(bool v){u64(v?1:0);}
    void str(const std::string& s){require(s.size()<=metadata_limit,"metadata string too long");u64(s.size());require(s.size()<=metadata_limit-bytes.size(),"informative metadata size limit");bytes.insert(bytes.end(),s.begin(),s.end());}
    void coord(Coordinate q){u64(static_cast<std::uint64_t>(q.x));u64(static_cast<std::uint64_t>(q.y));u64(static_cast<std::uint64_t>(q.z));}
};
struct Reader {
    std::vector<std::uint8_t> bytes;std::size_t at{};
    std::uint64_t u64(){require(at<=bytes.size()&&bytes.size()-at>=8,"truncated informative metadata");std::uint64_t x=0;for(int j=0;j<8;++j)x|=static_cast<std::uint64_t>(bytes[at++])<<(8*j);return x;}
    std::size_t count(std::size_t cap){auto x=u64();require(x<=cap,"informative metadata collection limit");return static_cast<std::size_t>(x);}
    bool boolean(){auto x=u64();require(x<=1,"invalid informative boolean");return x!=0;}
    int integer(){auto x=static_cast<std::int64_t>(u64());require(x>=std::numeric_limits<int>::min()&&x<=std::numeric_limits<int>::max(),"metadata integer overflow");return static_cast<int>(x);}
    std::string str(){auto size=count(metadata_limit);require(at<=bytes.size()&&size<=bytes.size()-at,"truncated metadata string");std::string x(reinterpret_cast<const char*>(bytes.data()+at),size);at+=size;return x;}
    Coordinate coord(){int x=integer(),y=integer(),z=integer();return {x,y,z};}
    void done(){require(at==bytes.size(),"unexpected trailing informative metadata");}
};
std::string encode(const Writer& w){static constexpr char digits[]="0123456789abcdef";std::string out;out.reserve(2*w.bytes.size());for(auto b:w.bytes){out+=digits[b>>4];out+=digits[b&15];}return out;}
Reader decode(const std::string& value){require(value.size()%2==0&&value.size()<=metadata_limit*2,"invalid informative metadata encoding size");auto digit=[](char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;throw std::invalid_argument("invalid informative metadata encoding");};Reader r;for(std::size_t j=0;j<value.size();j+=2)r.bytes.push_back(static_cast<std::uint8_t>((digit(value[j])<<4)|digit(value[j+1])));return r;}
void write_execution(Writer& w,v27::TickOptions x){w.u64(static_cast<unsigned>(x.backend));w.u64(x.threads);}
v27::TickOptions read_execution(Reader& r){auto b=r.count(2);auto t=r.count(1024);require(t>0,"metadata thread count missing");return {static_cast<v27::Backend>(b),t};}
void write_ui(Writer& w,const std::map<std::string,std::string>& ui){w.u64(ui.size());for(const auto& [k,v]:ui){w.str(k);w.str(v);}}
std::map<std::string,std::string> read_ui(Reader& r){std::map<std::string,std::string> out;for(auto n=r.count(128);n--;){auto k=r.str(),v=r.str();require(out.emplace(std::move(k),std::move(v)).second,"duplicate interface metadata key");}validate_interface_metadata(out);return out;}
void write_journal(Writer& w,const std::vector<InformativeOperation>& journal,bool truncated){w.boolean(truncated);w.u64(journal.size());for(const auto& x:journal){w.u64(x.tick);w.str(x.operation);w.str(x.interface_name);w.u64(static_cast<std::uint64_t>(x.value));w.boolean(x.receipt_id.has_value());if(x.receipt_id)w.u64(*x.receipt_id);w.u64(static_cast<unsigned>(x.modality));}}
std::vector<InformativeOperation> read_journal(Reader& r,bool& truncated,const OrganizationalWorld& world){truncated=r.boolean();std::vector<InformativeOperation> out;for(auto n=r.count(journal_limit);n--;){InformativeOperation x;x.tick=r.u64();x.operation=r.str();x.interface_name=r.str();x.value=static_cast<std::int64_t>(r.u64());if(r.boolean())x.receipt_id=r.u64();auto m=r.count(6);require(m>0,"invalid journal modality");x.modality=static_cast<OperationModality>(m);require(x.tick<=world.runtime().current_tick(),"journal record after snapshot tick");if(x.receipt_id)require(world.runtime().receipt(*x.receipt_id).has_value(),"journal refers to missing receipt");out.push_back(std::move(x));}return out;}
void write_metadata(OrganizationalWorld& world,const char* key,const Writer& value){
    const std::string prefix=std::string(key)+".";std::vector<std::string> old;for(const auto& [name,x]:world.runtime().snapshot_metadata_entries()){(void)x;if(name==key||name.starts_with(prefix))old.push_back(name);}for(const auto& name:old)world.runtime().erase_snapshot_metadata(name);
    const auto encoded=encode(value);constexpr std::size_t chunk=524288;const auto count=(encoded.size()+chunk-1)/chunk;world.runtime().set_snapshot_metadata(prefix+"chunks",std::to_string(count));for(std::size_t j=0;j<count;++j)world.runtime().set_snapshot_metadata(prefix+std::to_string(j),encoded.substr(j*chunk,chunk));
}
Reader metadata(const OrganizationalWorld& world,const char* key){
    const std::string prefix=std::string(key)+".";auto value=world.runtime().snapshot_metadata(prefix+"chunks");require(value.has_value(),"snapshot has no requested informative session metadata");std::size_t consumed{};const auto count=std::stoull(*value,&consumed);require(consumed==value->size()&&count>0&&count<=8,"invalid informative metadata chunk count");std::string encoded;for(std::uint64_t j=0;j<count;++j){auto x=world.runtime().snapshot_metadata(prefix+std::to_string(j));require(x.has_value(),"missing informative metadata chunk");require(x->size()<=metadata_limit*2-encoded.size(),"informative metadata total limit");encoded+=*x;}return decode(encoded);
}
}

FinitePolicySession::FinitePolicySession(OrganizationalWorld w,FinitePolicyParameters p):world_(std::move(w)),parameters_(std::move(p)){}
std::uint64_t FinitePolicySession::tick() const{return world_.runtime().current_tick();}
void FinitePolicySession::append(InformativeOperation op){append_operation(journal_,journal_truncated_,std::move(op));}
FinitePolicySession FinitePolicySession::create(FinitePolicyParameters p){
    check_policy(p);constexpr int n=67;Preparation prep{n};const int pv=p.roles==SourceRole::PInformative?p.actual_class:-p.actual_class,qv=-pv;
    const auto first_action=moved(p.origin,policy_p,1,n),first_report=moved(first_action,action_p,1,n);
    prep.put(placement(p.origin,7,policy_p,1,1,11,"initial_policy_P"));prep.arrive(first_action,1,sensor,47,"first_common_sensor");prep.arrive(first_report,2,{pv,1,-1},31,"source_P_initial_content");
    OrganizationSpec view;view.id="selection";view.recipe_id="finite_r14_source_revision.product4.v1";view.ports={{"initial_policy",p.origin},{"first_action",first_action},{"first_report",first_report}};
    std::vector<InterfaceSpec> inputs;
    for(int e:{-1,1}){const std::string tag=e<0?"negative":"positive";const auto hub=moved(first_report,{e,1,0},4,n);view.ports[tag+"_comparison"]=hub;
        for(int c:{-1,1}){Direction dr{-c,0,1};inputs.push_back(interface("actual."+tag+"."+std::to_string(c),moved(hub,dr,-4,n),dr));}
        for(int dx:{0,e}){const auto key=tag+"_"+std::to_string(dx);const auto wp=moved(hub,{dx,1,1},4,n);const Direction normalizer=dx==0?Direction{1,-1,-1}:Direction{-dx,0,-1};prep.arrive(wp,10,normalizer,11,"native_comparison_to_policy_"+key);view.ports[key+"_policy"]=wp;
            for(bool source_p:{true,false}){const auto source=source_p?"P":"Q";const auto query=moved(wp,source_p?policy_p:policy_q,1,n);prep.arrive(query,11,sensor,17,"symmetric_policy_query_"+key+source);const auto info=moved(query,source_p?action_p:action_q,3,n);const int value=source_p?pv:qv;
                std::vector<Direction> vectors;if(source_p)vectors.push_back({value,1,-1});else if(value<0)vectors.push_back({0,0,-1});else vectors={{1,0,-1},{1,0,0}};
                for(std::size_t j=0;j<vectors.size();++j)prep.arrive(info,14,vectors[j],static_cast<std::uint16_t>(23+j),"source_"+std::string(source)+"_content_"+key);
                view.ports[key+"_"+source+"_action"]=query;view.ports[key+"_"+source+"_information"]=info;
            }
        }
    }
    auto recipe=OrganizationRecipe::research(n,std::move(prep.placements),0);recipe.execution=p.execution;recipe.interfaces=std::move(inputs);recipe.organizations={view};recipe.domain="Finite one-revision retainP/switchQ policy; binary complementary explicit source reports; prepared rule, not arbitrary utility learning";
    FinitePolicySession result(OrganizationalWorld::create(recipe),p);result.append({0,"create_preparation","",0,std::nullopt,OperationModality::ExperienceProtocol});return result;
}
std::vector<EventReceipt> FinitePolicySession::submit_actual(int value){require(value==-1||value==1,"actual report must be -1 or +1");require(tick()==2,"actual report is admissible only at boundary2");require(!actual_submitted_,"actual report already submitted");std::vector<EventReceipt> out;for(const auto tag:{"negative","positive"}){auto name="actual."+std::string(tag)+"."+std::to_string(value);auto r=world_.submit(name,1,tick());append({tick(),"submit",name,1,r.id,OperationModality::ExperienceProtocol});out.push_back(r);}actual_submitted_=true;return out;}
void FinitePolicySession::process_boundary(){if(tick()==2&&!actual_submitted_&&parameters_.actual_enabled)(void)submit_actual(parameters_.actual_class);}
InformationReadout FinitePolicySession::advance(std::uint64_t count){require_advance(world_,count);const auto start=tick();for(std::uint64_t j=0;j<count;++j){process_boundary();const auto before=tick();world_.advance();require(tick()==before+1,"Runtime did not advance");}if(count)append({tick(),"advance_completed","from_tick="+std::to_string(start),static_cast<std::int64_t>(count),std::nullopt,OperationModality::NativeEvolution});return observe();}
InformationReadout FinitePolicySession::run_until(std::uint64_t target){require(target>=tick(),"cannot rewind a policy session");return advance(target-tick());}
InformationReadout FinitePolicySession::observe() const{
    InformationReadout r;r.tick=tick();r.profile="finite_policy";r.status="NO_PUBLISHED_READOUT_AT_CURRENT_TICK";r.scope="One prepared retainP_on_match/switchQ_on_discrepancy revision; complementary binary sources; no arbitrary or repeated utility learning";r.journal_truncated=journal_truncated_;add_current(r,world_,"selection");
    for(const auto& [key,o]:r.physical_outputs){if(!active(o))continue;if(tick()==6&&key.ends_with("_comparison")&&o.record.dy==1&&o.record.dz==1)r.comparisons.push_back({key,"",o.record.dx==0?"coincidence":"directional_discrepancy",o,o.record.dx});
        if(tick()==10&&key.ends_with("_policy")&&(direction(o,policy_p)||direction(o,policy_q)))r.policies.push_back({key,direction(o,policy_p)?"P":"Q","current_native_policy",o,std::nullopt});
        if(tick()==11&&key.ends_with("_action")){const auto source=key.find("_P_action")!=std::string::npos?"P":"Q";if(direction(o,source==std::string("P")?action_p:action_q))r.actions.push_back({key,source,"current_native_source_action",o,std::nullopt});}
        if(tick()==14&&key.ends_with("_information")&&o.record.dy==1&&o.record.dz==0&&(o.record.dx==-1||o.record.dx==1)){auto source=key.find("_P_information")!=std::string::npos?"P":"Q";r.information.push_back({key,source,"current_native_information",o,o.record.dx});}}
    if(tick()==6||tick()==10||tick()==11||tick()==14)r.status="CURRENT_DECLARED_FUNCTIONAL_WINDOW";return r;
}
InformationReadout FinitePolicySession::compare(){if(tick()>6){auto r=observe();r.status="OUTSIDE_CURRENT_COMPARISON_WINDOW";return r;}return run_until(6);}
InformationReadout FinitePolicySession::source(){if(tick()>11){auto r=observe();r.status="OUTSIDE_CURRENT_SOURCE_ACTION_WINDOW";return r;}return run_until(11);}
InformationReadout FinitePolicySession::sense(){if(tick()<=2){auto r=run_until(3);std::size_t reports=0,applied=0;for(const auto& receipt:r.receipts)if(std::any_of(receipt.channels.begin(),receipt.channels.end(),[](const auto& name){return name.starts_with("actual.");})){++reports;if(receipt.status==EventStatus::Applied)++applied;}r.status=!actual_submitted_?"ACTUAL_REPORT_OMITTED":reports==2&&applied==2?"EXTERNAL_CURRENT_ACTUAL_REPORT_APPLIED":applied?"ACTUAL_REPORT_PARTIALLY_APPLIED":"ACTUAL_REPORT_NOT_APPLIED";r.modality=OperationModality::ExperienceProtocol;return r;}if(tick()<=14)return run_until(14);auto r=observe();r.status="FINITE_RESOURCE_PROTOCOL_COMPLETED";return r;}
FinitePolicySession FinitePolicySession::fork() const{FinitePolicySession x(world_.fork(),parameters_);x.actual_submitted_=actual_submitted_;x.journal_=journal_;x.journal_truncated_=journal_truncated_;x.interface_metadata_=interface_metadata_;return x;}
FinitePolicySession FinitePolicySession::diagnostic_fork(const std::vector<ResearchStateEdit>& edits,bool authorize) const{FinitePolicySession x(world_.diagnostic_fork(edits,authorize),parameters_);x.actual_submitted_=actual_submitted_;x.journal_=journal_;x.journal_truncated_=journal_truncated_;x.interface_metadata_=interface_metadata_;x.append({tick(),"explicit_diagnostic_fork_edits","",static_cast<std::int64_t>(edits.size()),std::nullopt,OperationModality::DiagnosticFork});return x;}
void FinitePolicySession::set_interface_metadata(std::map<std::string,std::string> x){validate_interface_metadata(x);interface_metadata_=std::move(x);append({tick(),"set_interface_metadata_NON_RAW","",0,std::nullopt,OperationModality::PassiveObservation});}
void FinitePolicySession::set_interface_metadata(std::string key,std::string value){auto x=interface_metadata_;x[std::move(key)]=std::move(value);set_interface_metadata(std::move(x));}
std::optional<std::string> FinitePolicySession::get_interface_metadata(const std::string& key) const{auto i=interface_metadata_.find(key);if(i==interface_metadata_.end())return std::nullopt;return i->second;}
void FinitePolicySession::save_snapshot(const std::string& path,bool trace) const{Writer w;w.str("finite_policy.v1");w.coord(parameters_.origin);w.u64(static_cast<unsigned>(parameters_.roles));w.u64(static_cast<std::uint64_t>(parameters_.actual_class));w.boolean(parameters_.actual_enabled);write_execution(w,parameters_.execution);w.boolean(actual_submitted_);write_journal(w,journal_,journal_truncated_);write_ui(w,interface_metadata_);auto copy=world_.fork();write_metadata(copy,policy_key,w);copy.save_snapshot(path,trace);}
FinitePolicySession FinitePolicySession::load_snapshot(const std::string& path){auto world=OrganizationalWorld::load_snapshot(path);require(world.runtime().dimension()==67,"policy snapshot dimension mismatch");require(world.view("selection").spec().recipe_id=="finite_r14_source_revision.product4.v1","policy snapshot view mismatch");auto r=metadata(world,policy_key);require(r.str()=="finite_policy.v1","policy metadata version mismatch");FinitePolicyParameters p;p.origin=r.coord();auto role=r.count(2);require(role>0,"invalid source role");p.roles=static_cast<SourceRole>(role);p.actual_class=r.integer();p.actual_enabled=r.boolean();p.execution=read_execution(r);check_policy(p);FinitePolicySession out(std::move(world),p);out.actual_submitted_=r.boolean();out.journal_=read_journal(r,out.journal_truncated_,out.world_);out.interface_metadata_=read_ui(r);r.done();return out;}

NativeInformationSession::NativeInformationSession(OrganizationalWorld w,NativeInformationParameters p):world_(std::move(w)),parameters_(std::move(p)){}
std::uint64_t NativeInformationSession::tick() const{return world_.runtime().current_tick();}
void NativeInformationSession::append(InformativeOperation op){append_operation(journal_,journal_truncated_,std::move(op));}
NativeInformationSession NativeInformationSession::create(NativeInformationParameters p){
    check_information(p);constexpr int n=47;const auto target=moved(p.origin,{0,1,0},1,n),inlet=moved(p.origin,{0,3,0},1,n);const int arrival=37+p.distance;Preparation prep{n};prep.put(placement(moved(p.origin,{0,2,1},1,n),0,{0,0,0},7000,4,71,"finite_initial_reader_support"));
    auto recipe=OrganizationRecipe::relational(p.seed_path,basal::History::H0,false,p.origin);recipe.execution=p.execution;OrganizationSpec view;view.id="adapter";view.recipe_id="native_binary_feedback_adapter.product4.v1";view.t0_tick=32;view.ports["body_output"]=target;std::vector<InterfaceSpec> inputs;
    for(int e:{-1,1}){const std::string tag=e<0?"negative":"positive";const auto hub=moved(target,{e,1,0},p.distance,n);view.ports[tag+"_meeting"]=hub;
        for(int c:{-1,1}){Direction dr{-c,0,1};inputs.push_back(interface("observed_consequence."+tag+"."+std::to_string(c),moved(hub,dr,-4,n),dr));}
        for(int dx:{-1,0,1}){const auto key=tag+"_"+std::to_string(dx);const auto qt=moved(hub,{dx,1,1},4,n);Direction qd{0,-1,-1};prep.put(placement(moved(qt,qd,-(arrival+4-32),n),13,qd,1,1,0,"prepared_common_future_query"));view.ports[key+"_query"]=qt;
            if(dx){const auto access=moved(qt,{dx,0,0},5,n);const std::string source=dx>0?"Q":"P",informative=p.context==0?"P":"Q";auto load=source==informative?p.information_load:static_cast<std::uint16_t>(5);if(p.source_enabled&&p.source_cut!=source)prep.put(placement(moved(access,{0,1,0},-(arrival+9-32),n),load,{0,1,0},1,1,0,"prepared_information_"+source));view.ports[key+"_"+source+"_access"]=access;
                if(p.post_query){const auto later=moved(access,{dx,1,0},8,n);Direction ld{0,-1,1};inputs.push_back(interface("post_information."+key,moved(later,ld,-3,n),ld));view.ports[key+"_later_response"]=later;}
            }
        }
    }
    recipe.placements=std::move(prep.placements);recipe.organizations={view};auto world=OrganizationalWorld::create(recipe);for(auto& i:inputs)world.declare_interface(std::move(i));auto body=world.view("body").spec();world.declare_interface(interface("sensor.A",moved(*body.a,{0,-1,0},1,n),{0,0,-1}));world.declare_interface(interface("sensor.B",moved(*body.b,{0,1,0},1,n),{0,0,1}));world.declare_interface(interface("read.offaxis",inlet,{0,-1,0}));NativeInformationSession result(std::move(world),p);result.append({32,"create_preparation","",0,std::nullopt,OperationModality::ExperienceProtocol});return result;
}
std::vector<EventReceipt> NativeInformationSession::submit_actual(int value){require(value==-1||value==1,"actual report must be -1 or +1");require(tick()==static_cast<std::uint64_t>(33+parameters_.distance),"actual report outside declared boundary");require(std::find(executed_.begin(),executed_.end(),"actual") == executed_.end(),"actual report already submitted");std::vector<EventReceipt> out;for(const auto tag:{"negative","positive"}){auto name="observed_consequence."+std::string(tag)+"."+std::to_string(value);auto r=world_.submit(name,17,tick());append({tick(),"submit",name,17,r.id,OperationModality::ExperienceProtocol});out.push_back(r);}executed_.push_back("actual");return out;}
void NativeInformationSession::process_boundary(){const auto t=tick();auto submit=[&](std::string name,int load,bool probe){const auto key=token(t,name);if(std::find(executed_.begin(),executed_.end(),key)!=executed_.end())return;auto r=probe?world_.probe(name,load,t):world_.submit(name,load,t);executed_.push_back(key);append({t,probe?"probe":"submit",name,load,r.id,probe?OperationModality::PhysicalProbe:OperationModality::ExperienceProtocol});};
    if((t==32||t==33)&&parameters_.history!=basal::History::H0){const bool first_a=parameters_.history==basal::History::AB;submit(((t==32)==first_a)?"sensor.A":"sensor.B",0,false);}if(t==34&&parameters_.query_enabled)submit("read.offaxis",7,true);if(t==static_cast<std::uint64_t>(33+parameters_.distance)&&parameters_.actual_enabled&&std::find(executed_.begin(),executed_.end(),"actual")==executed_.end())(void)submit_actual(parameters_.actual_class);
    if(parameters_.post_query&&t==static_cast<std::uint64_t>(51+parameters_.distance))for(const auto tag:{"negative","positive"})for(int dx:{-1,1})submit("post_information."+std::string(tag)+"_"+std::to_string(dx),7,true);
}
InformationReadout NativeInformationSession::advance(std::uint64_t count){require_advance(world_,count);const auto start=tick();for(std::uint64_t j=0;j<count;++j){process_boundary();const auto before=tick();world_.advance();require(tick()==before+1,"Runtime did not advance");}if(count)append({tick(),"advance_completed","from_tick="+std::to_string(start),static_cast<std::int64_t>(count),std::nullopt,OperationModality::NativeEvolution});return observe();}
InformationReadout NativeInformationSession::run_until(std::uint64_t target){require(target>=tick(),"cannot rewind a native information session");return advance(target-tick());}
InformationReadout NativeInformationSession::observe() const{
    InformationReadout r;r.tick=tick();r.profile="native_information";r.status="NO_PUBLISHED_READOUT_AT_CURRENT_TICK";r.scope="Distinct N47 individual; finite prepared access routes, external actual report; no optimal utility policy, automatic body rewrite or indefinite reuse";r.journal_truncated=journal_truncated_;add_current(r,world_,"adapter");const auto body=world_.view("body").observe();r.delta=body.delta;r.centers_available=body.centers_available;r.supports_intact=body.supports_intact;const auto& output=r.physical_outputs.at("body_output");if(active(output)&&output.record.dy==1&&output.record.dz==0&&output.record.dx)r.current_prediction=output.record.dx>0?1:-1;const auto arrival=static_cast<std::uint64_t>(37+parameters_.distance);
    for(const auto& [key,o]:r.physical_outputs){if(!active(o))continue;if(tick()==arrival&&key.ends_with("_meeting")&&o.record.dy==1&&o.record.dz==1)r.comparisons.push_back({key,"",o.record.dx==0?"coincidence":"directional_discrepancy",o,o.record.dx});
        if(tick()==arrival+4&&key.ends_with("_query")&&o.record.dx&&o.record.dy==0&&o.record.dz==0)r.actions.push_back({key,o.record.dx>0?"Q":"P","current_native_source_action",o,std::nullopt});
        if(tick()==arrival+9&&key.ends_with("_access")&&o.record.dx&&o.record.dy==1&&o.record.dz==0){const auto source=key.find("_P_access")!=std::string::npos?"P":"Q";std::optional<std::int64_t> value;if(o.record.s_reg>=37)value=static_cast<std::int64_t>(o.record.s_reg)-37;r.information.push_back({key,source,"physical_load_minus_declared_transport37",o,value});}
        if(parameters_.post_query&&tick()==arrival+17&&key.ends_with("_later_response")&&o.record.dx&&o.record.dy==0&&o.record.dz==1)r.later_responses.push_back({key,"","current_native_later_response",o,o.record.s_reg});
    }if(tick()==37||tick()==arrival||tick()==arrival+4||tick()==arrival+9||(parameters_.post_query&&tick()==arrival+17))r.status="CURRENT_DECLARED_FUNCTIONAL_WINDOW";return r;
}
InformationReadout NativeInformationSession::compare(){const auto target=static_cast<std::uint64_t>(37+parameters_.distance);if(tick()>target){auto r=observe();r.status="OUTSIDE_CURRENT_COMPARISON_WINDOW";return r;}return run_until(target);}
InformationReadout NativeInformationSession::source(){const auto target=static_cast<std::uint64_t>(41+parameters_.distance);if(tick()>target){auto r=observe();r.status="OUTSIDE_CURRENT_SOURCE_ACTION_WINDOW";return r;}return run_until(target);}
InformationReadout NativeInformationSession::sense(){const auto target=static_cast<std::uint64_t>(46+parameters_.distance);if(tick()>target){auto r=observe();r.status="OUTSIDE_CURRENT_INFORMATION_WINDOW";return r;}return run_until(target);}
NativeInformationSession NativeInformationSession::fork() const{NativeInformationSession x(world_.fork(),parameters_);x.executed_=executed_;x.journal_=journal_;x.journal_truncated_=journal_truncated_;x.interface_metadata_=interface_metadata_;return x;}
NativeInformationSession NativeInformationSession::diagnostic_fork(const std::vector<ResearchStateEdit>& edits,bool authorize) const{NativeInformationSession x(world_.diagnostic_fork(edits,authorize),parameters_);x.executed_=executed_;x.journal_=journal_;x.journal_truncated_=journal_truncated_;x.interface_metadata_=interface_metadata_;x.append({tick(),"explicit_diagnostic_fork_edits","",static_cast<std::int64_t>(edits.size()),std::nullopt,OperationModality::DiagnosticFork});return x;}
void NativeInformationSession::set_interface_metadata(std::map<std::string,std::string> x){validate_interface_metadata(x);interface_metadata_=std::move(x);append({tick(),"set_interface_metadata_NON_RAW","",0,std::nullopt,OperationModality::PassiveObservation});}
void NativeInformationSession::set_interface_metadata(std::string key,std::string value){auto x=interface_metadata_;x[std::move(key)]=std::move(value);set_interface_metadata(std::move(x));}
std::optional<std::string> NativeInformationSession::get_interface_metadata(const std::string& key) const{auto i=interface_metadata_.find(key);if(i==interface_metadata_.end())return std::nullopt;return i->second;}
void NativeInformationSession::save_snapshot(const std::string& path,bool trace) const{Writer w;w.str("native_information.v1");w.str(parameters_.seed_path);w.coord(parameters_.origin);w.u64(static_cast<unsigned>(parameters_.history));w.u64(parameters_.context);w.u64(static_cast<std::uint64_t>(parameters_.actual_class));w.u64(parameters_.information_load);w.boolean(parameters_.query_enabled);w.boolean(parameters_.actual_enabled);w.boolean(parameters_.source_enabled);w.boolean(parameters_.post_query);w.str(parameters_.source_cut);w.u64(parameters_.distance);write_execution(w,parameters_.execution);w.u64(executed_.size());for(const auto& key:executed_)w.str(key);write_journal(w,journal_,journal_truncated_);write_ui(w,interface_metadata_);auto copy=world_.fork();write_metadata(copy,information_key,w);copy.save_snapshot(path,trace);}
NativeInformationSession NativeInformationSession::load_snapshot(const std::string& path){auto world=OrganizationalWorld::load_snapshot(path);require(world.runtime().dimension()==47&&world.runtime().current_tick()>=32,"native information snapshot domain mismatch");require(world.view("adapter").spec().recipe_id=="native_binary_feedback_adapter.product4.v1","native information view mismatch");(void)world.view("body");auto r=metadata(world,information_key);require(r.str()=="native_information.v1","native information metadata version mismatch");NativeInformationParameters p;p.seed_path=r.str();p.origin=r.coord();p.history=static_cast<basal::History>(r.count(3));p.context=r.integer();p.actual_class=r.integer();p.information_load=static_cast<std::uint16_t>(r.count(65535));p.query_enabled=r.boolean();p.actual_enabled=r.boolean();p.source_enabled=r.boolean();p.post_query=r.boolean();p.source_cut=r.str();p.distance=r.integer();p.execution=read_execution(r);check_information(p);NativeInformationSession out(std::move(world),p);std::set<std::string> seen;for(auto n=r.count(64);n--;){auto key=r.str();require(seen.insert(key).second,"duplicate native information protocol token");out.executed_.push_back(std::move(key));}out.journal_=read_journal(r,out.journal_truncated_,out.world_);out.interface_metadata_=read_ui(r);r.done();return out;}

} // namespace dee::thinking
