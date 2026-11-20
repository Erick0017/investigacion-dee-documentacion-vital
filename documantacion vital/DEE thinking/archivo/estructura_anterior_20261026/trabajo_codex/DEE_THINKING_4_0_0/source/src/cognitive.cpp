#include "dee_thinking/cognitive.hpp"
#include <algorithm>
#include <array>
#include <limits>
#include <stdexcept>
#include <utility>

namespace dee::thinking {
namespace {
constexpr const char* cognitive_prefix="dee_thinking.cognitive.v1.";
constexpr const char* association_key="dee_thinking.association.v1";
constexpr std::size_t max_bytes=32*1024*1024;
constexpr std::array<std::uint64_t,5> slots{{163,292,554,812,945}};
void require(bool b,const std::string& s){if(!b)throw std::invalid_argument(s);}
bool active(const Observation& o){return o.record.state>0&&o.record.semantic!=5;}
std::vector<bool> fixed_decode(const Observation& o){if(active(o)&&o.record.dx>0)return {true};if(active(o)&&o.record.dx<0)return {false};return {false,true};}
Coordinate plus(Coordinate q,Direction d,int n){return {v27::wrap_coordinate(q.x+d.dx,n),v27::wrap_coordinate(q.y+d.dy,n),v27::wrap_coordinate(q.z+d.dz,n)};}
InterfaceSpec channel(std::string name,Coordinate q,Direction dr,std::uint32_t state=1,bool probe=true){InterfaceSpec i;i.name=name;i.channel={name,q,state,dr,1,true,probe};return i;}
void validate(CognitiveParameters& p){
    require(p.profile=="continuity"||p.profile=="comparison","unknown cognitive profile");
    require(!p.seed_path.empty(),"reference seed path is required to create a body");
    require(p.origin.x>=0&&p.origin.x<47&&p.origin.y>=0&&p.origin.y<47&&p.origin.z>=0&&p.origin.z<47,"origin outside N47");
    require(p.event_state>0,"event state must be occupied");
    require(p.journal_limit>=64&&p.journal_limit<=262144,"journal_limit outside [64,262144]");
    require(p.prediction_limit>0&&p.prediction_limit<=32768,"prediction_limit outside [1,32768]");
}
void validate_metadata(const std::map<std::string,std::string>& current,const std::string& key,const std::string& value){
    require(!key.empty()&&key.size()<=128&&value.size()<=1024*1024,"interface metadata size invalid");
    require(current.count(key)||current.size()<128,"too many interface metadata entries");
    std::size_t bytes=key.size()+value.size();for(const auto& [k,v]:current)if(k!=key)bytes+=k.size()+v.size();
    require(bytes<=2*1024*1024,"interface metadata total exceeds 2MiB");
}
// Small versioned binary format, uint64 lossless, bounds checked before read.
struct Writer {
    std::string b;
    void need(std::size_t n){require(n<=max_bytes-b.size(),"cognitive metadata too large");}
    void u(std::uint64_t x){need(8);for(int j=0;j<8;++j)b.push_back(static_cast<char>(x>>(8*j)));}
    void flag(bool x){u(x?1:0);}
    void s(const std::string& x){need(8+x.size());u(x.size());b+=x;}
    void q(Coordinate x){u(static_cast<std::uint64_t>(static_cast<std::int64_t>(x.x)));u(static_cast<std::uint64_t>(static_cast<std::int64_t>(x.y)));u(static_cast<std::uint64_t>(static_cast<std::int64_t>(x.z)));}
    void obs(const Observation& x){u(x.tick);q(x.coordinate);u(x.raw);u(x.clock);}
};
struct Reader {
    const std::string& b;std::size_t p{};
    void need(std::size_t n){require(n<=b.size()-p,"truncated cognitive metadata");}
    std::uint64_t u(){need(8);std::uint64_t x=0;for(int j=0;j<8;++j)x|=static_cast<std::uint64_t>(static_cast<unsigned char>(b[p++]))<<(8*j);return x;}
    std::size_t count(std::size_t lim){auto n=u();require(n<=lim,"cognitive metadata count exceeds limit");return static_cast<std::size_t>(n);}
    bool flag(){auto x=u();require(x<=1,"invalid boolean in cognitive metadata");return x!=0;}
    std::string s(){auto n=count(2*1024*1024);need(n);auto out=b.substr(p,n);p+=n;return out;}
    int i(){auto x=static_cast<std::int64_t>(u());require(x>=std::numeric_limits<int>::min()&&x<=std::numeric_limits<int>::max(),"coordinate overflow");return static_cast<int>(x);}
    Coordinate q(){Coordinate x;x.x=i();x.y=i();x.z=i();return x;}
    Observation obs(){Observation x;x.tick=u();x.coordinate=q();x.raw=u();x.clock=u();x.record=v27::decode_record(x.raw);return x;}
};
std::uint64_t checksum(const std::string& b){std::uint64_t h=1469598103934665603ULL;for(unsigned char c:b){h^=c;h*=1099511628211ULL;}return h;}
void seal(Writer& w){auto h=checksum(w.b);w.u(h);}
void verify(Reader& r){const auto p=r.p;auto h=r.u();require(r.p==r.b.size()&&h==checksum(r.b.substr(0,p)),"cognitive metadata checksum/trailing bytes invalid");}
void write_map(Writer& w,const std::map<std::string,std::string>& m){w.u(m.size());for(auto& [k,v]:m){w.s(k);w.s(v);}}
std::map<std::string,std::string> read_map(Reader& r){std::map<std::string,std::string> m;auto n=r.count(128);for(std::size_t j=0;j<n;++j){auto k=r.s(),v=r.s();require(!m.count(k),"duplicate interface metadata key");validate_metadata(m,k,v);m.emplace(std::move(k),std::move(v));}return m;}
void write_receipt(Writer& w,const EventReceipt& x){w.u(x.id);w.u(static_cast<unsigned>(x.kind));w.u(static_cast<unsigned>(x.status));w.u(x.requested_tick);w.flag(x.effective_tick.has_value());if(x.effective_tick)w.u(*x.effective_tick);w.u(x.channels.size());for(auto& s:x.channels)w.s(s);w.s(x.reason);}
EventReceipt read_receipt(Reader& r){EventReceipt x;x.id=r.u();auto k=r.u(),s=r.u();require(k>=1&&k<=2&&s>=1&&s<=7,"invalid cognitive receipt enum");x.kind=static_cast<EventKind>(k);x.status=static_cast<EventStatus>(s);x.requested_tick=r.u();if(r.flag())x.effective_tick=r.u();auto n=r.count(4096);for(std::size_t j=0;j<n;++j)x.channels.push_back(r.s());x.reason=r.s();return x;}
std::string hex(const std::string& x){static constexpr char digits[]="0123456789abcdef";std::string out;out.reserve(x.size()*2);for(unsigned char c:x){out.push_back(digits[c>>4]);out.push_back(digits[c&15]);}return out;}
std::string unhex(const std::string& x){require(x.size()%2==0&&x.size()<=2*max_bytes,"invalid encoded cognitive metadata size");auto d=[](char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;throw std::invalid_argument("invalid metadata hex");};std::string o;o.reserve(x.size()/2);for(std::size_t j=0;j<x.size();j+=2)o.push_back(static_cast<char>((d(x[j])<<4)|d(x[j+1])));return o;}
void put_metadata(Runtime& r,const std::string& prefix,const std::string& bytes){
    std::vector<std::string> old;for(const auto& [k,v]:r.snapshot_metadata_entries())if(k.starts_with(prefix))old.push_back(k);
    auto encoded=hex(bytes);constexpr std::size_t chunk=524288;auto n=(encoded.size()+chunk-1)/chunk;
    require(n>0&&n<=128,"cognitive metadata chunk count invalid");
    for(const auto& k:old)r.erase_snapshot_metadata(k);
    r.set_snapshot_metadata(prefix+"chunks",std::to_string(n));for(std::size_t j=0;j<n;++j)r.set_snapshot_metadata(prefix+std::to_string(j),encoded.substr(j*chunk,chunk));
}
std::string get_metadata(const Runtime& r,const std::string& prefix){auto c=r.snapshot_metadata(prefix+"chunks");require(c.has_value(),"snapshot has no native cognitive protocol; legacy physical load is separate");std::size_t end=0;auto n=std::stoull(*c,&end);require(end==c->size()&&n>0&&n<=128,"invalid cognitive metadata chunk count");std::string s;for(std::size_t j=0;j<n;++j){auto x=r.snapshot_metadata(prefix+std::to_string(j));require(x.has_value()&&x->size()<=524288&&x->size()<=max_bytes*2-s.size(),"missing/oversized cognitive metadata chunk");s+=*x;}return unhex(s);}
EventReceipt finalized(Runtime& r,std::uint64_t id){auto x=r.receipt(id);if(!x)throw std::runtime_error("Runtime lost declared input receipt");return *x;}
void add_response(AssociationResponse& out,std::string name,const Observation& o){out.outputs[name]=o;out.decoded[name]=active(o)?std::optional<std::uint16_t>(o.record.s_reg):std::nullopt;}
}

CognitiveSession::CognitiveSession(OrganizationalWorld w,CognitiveParameters p):world_(std::move(w)),parameters_(std::move(p)){}
CognitiveSession CognitiveSession::create(CognitiveParameters p){
    validate(p);auto recipe=OrganizationRecipe::relational(p.seed_path,basal::History::H0,false,p.origin);recipe.execution=p.execution;
    auto world=OrganizationalWorld::create(recipe);auto spec=world.view("body").spec();
    require(spec.a&&spec.b&&spec.comparator&&world.runtime().current_tick()==32,"invalid relational reference body");
    world.declare_interface(channel("sensor.A",plus(*spec.a,{0,-1,0},47),{0,0,-1},p.event_state));
    world.declare_interface(channel("sensor.B",plus(*spec.b,{0,1,0},47),{0,0,1},p.event_state));
    if(p.profile=="comparison")for(int sign:{-1,1})world.declare_interface(channel(sign>0?"actual_report.positive":"actual_report.negative",plus(p.origin,{sign,0,sign},47),{0,0,sign}));
    CognitiveSession e(std::move(world),std::move(p));
    e.log({32,32,0,"prepare","DECLARED_PRE_T0_CONFIGURATION","","relational.v1 H0; channels fixed before first experience",std::nullopt});return e;
}
std::uint64_t CognitiveSession::tick() const noexcept{return world_.runtime().current_tick();}
std::uint64_t CognitiveSession::preferred_horizon() const noexcept{return parameters_.profile=="comparison"?46:30;}
void CognitiveSession::log(CognitiveCall c){if(journal_.size()>=parameters_.journal_limit)throw std::length_error("session journal budget reached; no automatic reset of organization");journal_.push_back(std::move(c));}
bool CognitiveSession::barrier_at(std::uint64_t t) const{return (!parameters_.change_tick||t<*parameters_.change_tick)?parameters_.initial_open:!parameters_.initial_open;}
BarrierSample CognitiveSession::sample(bool reference){require(samples_.size()<262144,"external sample budget reached");BarrierSample s;s.tick=tick();s.reference_branch=reference;s.arrived=barrier_at(s.tick)!=reference;samples_.push_back(s);return s;}
void CognitiveSession::advance_to(std::uint64_t target){require(target>=tick(),"cannot rewind MAIN");log({tick(),target,0,"world.run_until","NATIVE_EVOLUTION","","USER_OR_PROTOCOL",std::nullopt});world_.run_until(target);require(tick()==target,"Runtime paused before requested boundary");}
CognitiveComparison CognitiveSession::comparison_readout(bool valid,bool applied) const{
    CognitiveComparison c;c.physical_output=world_.runtime().observe(*world_.view("body").spec().comparator);c.signed_comparison_marker_present=active(c.physical_output)&&c.physical_output.record.dz!=0;c.represented_expectation_before_report=valid;c.report_applied=applied;c.within_window=last_report_tick_&&tick()==*last_report_tick_;
    if(valid&&applied&&c.within_window&&c.signed_comparison_marker_present){c.presentation=c.physical_output.record.dx==0?"coincidencia_direccional":"discrepancia_direccional";c.validity="CURRENT_NATIVE_MARKER";}else c.validity="OUTSIDE_DECLARED_SINGLETON_ONE_TICK_COMPARISON_WINDOW";
    return c;
}
CognitiveReadout CognitiveSession::observe() const{
    CognitiveReadout p;p.tick=tick();auto view=world_.view("body");auto spec=view.spec();p.memory=view.observe();p.a=world_.runtime().observe(*spec.a);p.b=world_.runtime().observe(*spec.b);p.physical_output=world_.runtime().observe(*spec.comparator);p.gate_a=observation::inspect_write_gate(world_.runtime(),*spec.a,false);p.gate_b=observation::inspect_write_gate(world_.runtime(),*spec.b,false);p.prediction_set=fixed_decode(p.physical_output);p.profile=parameters_.profile;p.comparison_stage=comparison_stage_;p.domain_status=tick()<=1032?"WITHIN_FINITE_TESTED_HORIZON":"OUTSIDE_TESTED_HORIZON_MEASUREMENT_ONLY";
    if(parameters_.profile=="comparison"&&(comparison_stage_=="reported"||(active(p.physical_output)&&p.physical_output.record.dz!=0))){p.prediction_set={false,true};p.forecast_domain="OUTSIDE_FORECAST_DOMAIN_COMPARISON_CONTEXT";p.comparison=comparison_readout(last_comparison_valid_,last_comparison_valid_);}else p.forecast_domain="LIVE_CONTEXT_SENSITIVE_DIRECTION_READOUT";
    return p;
}
CognitiveResult CognitiveSession::result(std::string k,std::string status,std::string mode,std::string detail) const{CognitiveResult x;x.kind=std::move(k);x.status=std::move(status);x.modality=std::move(mode);x.detail=std::move(detail);x.tick=tick();x.readout=observe();return x;}
std::optional<std::uint64_t> CognitiveSession::next_slot(){while(slot_index_<slots.size()&&slots[slot_index_]<tick())++slot_index_;if(tick()<=33)return tick();if(slot_index_>=slots.size())return std::nullopt;return slots[slot_index_++];}
CognitiveResult CognitiveSession::input(const std::string& key,std::uint64_t when,const std::string& source){
    require(key=="A"||key=="B","only physical sensor A or B is supported");advance_to(when);auto r=world_.submit("sensor."+key,0,when);log({when,when,r.id,"submit","EXPERIENCE_PROTOCOL","sensor."+key,source,0});advance_to(when+1);auto rr=finalized(world_.runtime(),r.id);auto out=result("EXPERIENCE",to_string(rr.status),"EXPERIENCE_PROTOCOL","fixed zero-load input; no clock or center edits");out.receipts.push_back(rr);return out;
}
CognitiveResult CognitiveSession::experience(const std::string& symbol){require(symbol=="A"||symbol=="B","supported symbols are exactly A and B");if(pending_prediction_)expectation_invalidated_="INTERVENING_PHYSICAL_EXPERIENCE_REQUEST";auto t=next_slot();if(!t)return result("INTERFACE_LIMIT","NO_FURTHER_PHASE_SLOTS_IN_PUBLISHED_DOMAIN","INTERFACE_NOT_NATIVE_ANSWER");return input(symbol,*t,"USER_REQUEST_FIXED_EXTERNAL_PHASE_SCHEDULE");}
CognitiveResult CognitiveSession::sense(){
    if(parameters_.profile=="comparison"&&pending_prediction_)return compare();
    if(!past_pair_presented_&&tick()==32){std::vector<EventReceipt> receipts;std::vector<BarrierSample> samples;for(bool reference:{false,true}){auto s=sample(reference);samples.push_back(s);auto x=input(s.arrived?"A":"B",tick(),"CURRENT_EXTERNAL_BARRIER_CLASS_REFERENCE_PAIR");receipts.insert(receipts.end(),x.receipts.begin(),x.receipts.end());}past_pair_presented_=true;auto x=result("INITIAL_PAST_PAIR","MEASURED","EXPERIENCE_PROTOCOL","two observed external classes, second on declared inverted reference branch; not a native absence detector");x.receipts=std::move(receipts);x.samples=std::move(samples);return x;}
    auto t=next_slot();if(!t)return result("INTERFACE_LIMIT","NO_FURTHER_PHASE_SLOTS_IN_PUBLISHED_DOMAIN","INTERFACE_NOT_NATIVE_ANSWER");advance_to(*t);auto s=sample();auto x=input(s.arrived?"A":"B",*t,"CURRENT_EXTERNAL_BARRIER_CLASS_FIXED_PHASE");x.samples.push_back(s);return x;
}
std::vector<CognitiveEvaluation> CognitiveSession::evaluate_due(){std::vector<CognitiveEvaluation> out;for(auto& p:predictions_)if(!p.evaluated&&p.target_tick<=tick()){CognitiveEvaluation e;e.prediction_id=p.id;e.emission_tick=p.emission_tick;e.target_tick=p.target_tick;e.actual=barrier_at(p.target_tick);e.singleton=p.prediction_set.size()==1;if(e.singleton)e.error=p.prediction_set.front()!=e.actual;p.evaluated=true;out.push_back(e);}return out;}
CognitiveResult CognitiveSession::run_until(std::uint64_t absolute){advance_to(absolute);auto x=result("ADVANCE","MEASURED","NATIVE_EVOLUTION");x.evaluations=evaluate_due();return x;}
CognitiveResult CognitiveSession::advance(std::uint64_t n){require(n<=std::numeric_limits<std::uint64_t>::max()-tick(),"tick overflow");return run_until(tick()+n);}
CognitiveSession CognitiveSession::fork() const{
    auto child=*this;child.world_=world_.fork();
    child.log({tick(),tick(),0,"fork","EXPLICIT_DIAGNOSTIC_FORK","","USER_REQUEST_NOT_OPERATIONAL_PROTOCOL",std::nullopt});
    return child;
}
CognitiveResult CognitiveSession::predict(std::uint64_t horizon){
    if(!horizon)horizon=preferred_horizon();require(horizon>0,"positive horizon required");
    const auto probe_ticks=reader_primed_?0ULL:3ULL;
    require(probe_ticks<=std::numeric_limits<std::uint64_t>::max()-tick(),"query tick overflow");
    require(horizon<=std::numeric_limits<std::uint64_t>::max()-tick()-probe_ticks,"prediction target overflow");
    if(parameters_.profile=="comparison")require(horizon<std::numeric_limits<std::uint64_t>::max()-tick()-probe_ticks,"comparison needs one tick after target");
    if(parameters_.profile=="comparison"){
        if(comparison_stage_=="reported")return result("INTERFACE_LIMIT","OUTSIDE_FORECAST_DOMAIN","INTERFACE_NOT_NATIVE_ANSWER","comparison marker is not decoded as a fresh forecast");
        if(pending_prediction_)return result("INTERFACE_LIMIT","ONE_PENDING_EXPECTATION_ALREADY_REGISTERED","INTERFACE_NOT_NATIVE_ANSWER");
        auto o=observe().physical_output;if(active(o)&&o.record.dz!=0)return result("INTERFACE_LIMIT","OUTSIDE_FORECAST_DOMAIN","INTERFACE_NOT_NATIVE_ANSWER");
    }
    require(predictions_.size()<parameters_.prediction_limit,"prediction capture budget reached; no reset");
    std::optional<EventReceipt> receipt;if(!reader_primed_){require(tick()<=std::numeric_limits<std::uint64_t>::max()-3,"tick overflow");auto t=tick();auto r=world_.probe("body.common_query",0,t);log({t,t,r.id,"probe","PHYSICAL_PROBE_ON_MAIN","body.common_query","USER_QUERY",0});advance_to(t+3);receipt=finalized(world_.runtime(),r.id);reader_primed_=receipt->status==EventStatus::Applied;}
    require(horizon<=std::numeric_limits<std::uint64_t>::max()-tick(),"prediction target overflow");auto out=result("EMISSION","MEASURED",receipt?"PHYSICAL_PROBE_ON_MAIN":"PASSIVE_OBSERVATION_OF_RENEWED_MAIN_OUTPUT","current physical direction; no future external state is read");
    CognitivePrediction p;p.id=predictions_.size()+1;p.emission_tick=tick();p.target_tick=tick()+horizon;p.physical_output=out.readout.physical_output;p.prediction_set=(!receipt||receipt->status==EventStatus::Applied)?fixed_decode(p.physical_output):std::vector<bool>{false,true};p.receipt=receipt;p.modality=out.modality;predictions_.push_back(p);out.prediction=p;if(receipt)out.receipts.push_back(*receipt);
    if(parameters_.profile=="comparison"){pending_prediction_=predictions_.size()-1;comparison_stage_="pending";expectation_invalidated_.clear();}
    return out;
}
CognitiveResult CognitiveSession::compare(){
    if(parameters_.profile!="comparison")return result("INTERFACE_LIMIT","COMPARISON_PROFILE_NOT_PREPARED","INTERFACE_NOT_NATIVE_ANSWER");
    if(!pending_prediction_)return result("INTERFACE_LIMIT","NO_PENDING_COMPARABLE_EXPECTATION","INTERFACE_NOT_NATIVE_ANSWER");
    if(!expectation_invalidated_.empty())return result("INTERFACE_LIMIT","EXPECTATION_INVALIDATED_BY_EXPERIENCE","INTERFACE_NOT_NATIVE_ANSWER",expectation_invalidated_);
    const auto p=predictions_.at(*pending_prediction_);const auto& old=p.physical_output;
    if(!(p.prediction_set.size()==1&&active(old)&&(old.record.dx==-1||old.record.dx==1)&&old.record.dz==0))return result("INTERFACE_LIMIT","NO_SINGLETON_NATIVE_EXPECTATION","INTERFACE_NOT_NATIVE_ANSWER");
    if(tick()>p.target_tick)return result("INTERFACE_LIMIT","MISSED_COMPARISON_WINDOW","INTERFACE_NOT_NATIVE_ANSWER");
    advance_to(p.target_tick);auto live=observe().physical_output;if(!(active(live)&&live.record.dx==old.record.dx&&live.record.dz==0)){expectation_invalidated_="NATIVE_EXPECTATION_REPRESENTATION_CHANGED_BEFORE_ACTUAL";return result("INTERFACE_LIMIT","EXPECTATION_CHANGED_IN_NATIVE_EVOLUTION","INTERFACE_NOT_NATIVE_ANSWER");}
    // This codec reads ONLY the observed current class. It cannot inspect p,
    // delta, the stored forecast, an error, or a future outcome.
    require(tick()<std::numeric_limits<std::uint64_t>::max(),"comparison transition tick overflow");auto s=sample();const std::string name=s.arrived?"actual_report.positive":"actual_report.negative";auto t=tick();auto r=world_.submit(name,1,t);log({t,t,r.id,"submit","OBSERVED_EXTERNAL_EVENT_TO_NATIVE_GRADIENT",name,"CURRENT_ACTUAL_BARRIER_CLASS_ONLY",1});advance_to(t+1);auto rr=finalized(world_.runtime(),r.id);
    last_comparison_valid_=rr.status==EventStatus::Applied;last_report_tick_=tick();comparison_stage_="reported";pending_prediction_.reset();auto x=result("CURRENT_CONSEQUENCE_NATIVE_COMPARISON",last_comparison_valid_?"CURRENT_NATIVE_COMPARISON_MEASURED":"COMPARISON_UNRESOLVED","OBSERVED_EXTERNAL_EVENT_TO_NATIVE_GRADIENT");x.receipts.push_back(rr);x.samples.push_back(s);x.comparison=comparison_readout(true,last_comparison_valid_);x.evaluations=evaluate_due();return x;
}
void CognitiveSession::set_interface_metadata(const std::string& k,const std::string& v){validate_metadata(interface_metadata_,k,v);log({tick(),tick(),0,"set_interface_metadata","OPERATIVE_METADATA_NON_RAW",k,"EXTERNAL_INTERFACE_LABELS",std::nullopt});interface_metadata_[k]=v;}
std::optional<std::string> CognitiveSession::get_interface_metadata(const std::string& k) const{auto i=interface_metadata_.find(k);return i==interface_metadata_.end()?std::nullopt:std::optional<std::string>(i->second);}
std::string CognitiveSession::serialize() const{
    Writer w;w.u(0x34434f474e495431ULL);w.s(parameters_.seed_path);w.s(parameters_.profile);w.q(parameters_.origin);w.flag(parameters_.initial_open);w.flag(parameters_.change_tick.has_value());if(parameters_.change_tick)w.u(*parameters_.change_tick);w.u(parameters_.event_state);w.u(static_cast<unsigned>(parameters_.execution.backend));w.u(parameters_.execution.threads);w.u(parameters_.journal_limit);w.u(parameters_.prediction_limit);w.u(tick());
    w.flag(reader_primed_);w.flag(past_pair_presented_);w.u(slot_index_);w.s(comparison_stage_);w.s(expectation_invalidated_);w.flag(pending_prediction_.has_value());if(pending_prediction_)w.u(*pending_prediction_);w.flag(last_report_tick_.has_value());if(last_report_tick_)w.u(*last_report_tick_);w.flag(last_comparison_valid_);write_map(w,interface_metadata_);
    w.u(journal_.size());for(const auto& c:journal_){w.u(c.tick);w.u(c.target_tick);w.u(c.receipt_id);w.s(c.operation);w.s(c.scope);w.s(c.channel);w.s(c.source);w.flag(c.value.has_value());if(c.value)w.u(*c.value);}
    w.u(samples_.size());for(const auto& s:samples_){w.u(s.tick);w.flag(s.arrived);w.flag(s.reference_branch);}
    w.u(predictions_.size());for(const auto& p:predictions_){w.u(p.id);w.u(p.emission_tick);w.u(p.target_tick);w.obs(p.physical_output);w.u(p.prediction_set.size());for(bool x:p.prediction_set)w.flag(x);w.flag(p.receipt.has_value());if(p.receipt)write_receipt(w,*p.receipt);w.flag(p.evaluated);w.s(p.modality);}seal(w);return w.b;
}
void CognitiveSession::deserialize(const std::string& bytes){
    require(bytes.size()<=max_bytes,"cognitive metadata too large");Reader r{bytes};require(r.u()==0x34434f474e495431ULL,"unsupported cognitive metadata schema");parameters_.seed_path=r.s();parameters_.profile=r.s();parameters_.origin=r.q();parameters_.initial_open=r.flag();parameters_.change_tick.reset();if(r.flag())parameters_.change_tick=r.u();auto state=r.u();require(state<=std::numeric_limits<std::uint32_t>::max(),"event state overflow");parameters_.event_state=static_cast<std::uint32_t>(state);auto backend=r.u();require(backend<=2,"invalid cognitive backend");parameters_.execution.backend=static_cast<v27::Backend>(backend);parameters_.execution.threads=r.count(65536);parameters_.journal_limit=r.count(262144);parameters_.prediction_limit=r.count(32768);require(r.u()==tick(),"cognitive protocol/Runtime tick mismatch");validate(parameters_);
    reader_primed_=r.flag();past_pair_presented_=r.flag();slot_index_=r.count(slots.size());comparison_stage_=r.s();require(comparison_stage_=="ready"||comparison_stage_=="pending"||comparison_stage_=="reported","invalid comparison stage");expectation_invalidated_=r.s();pending_prediction_.reset();if(r.flag())pending_prediction_=r.count(parameters_.prediction_limit);last_report_tick_.reset();if(r.flag())last_report_tick_=r.u();last_comparison_valid_=r.flag();interface_metadata_=read_map(r);
    auto n=r.count(parameters_.journal_limit);journal_.clear();for(std::size_t j=0;j<n;++j){CognitiveCall c;c.tick=r.u();c.target_tick=r.u();c.receipt_id=r.u();c.operation=r.s();c.scope=r.s();c.channel=r.s();c.source=r.s();if(r.flag()){auto v=r.u();require(v<=65535,"journal load overflow");c.value=static_cast<std::uint16_t>(v);}journal_.push_back(std::move(c));}
    n=r.count(262144);samples_.clear();for(std::size_t j=0;j<n;++j){BarrierSample s;s.tick=r.u();s.arrived=r.flag();s.reference_branch=r.flag();require(s.tick<=tick(),"future sample in snapshot");samples_.push_back(s);}
    n=r.count(parameters_.prediction_limit);predictions_.clear();for(std::size_t j=0;j<n;++j){CognitivePrediction p;p.id=r.u();p.emission_tick=r.u();p.target_tick=r.u();p.physical_output=r.obs();auto m=r.count(2);require(m>=1,"empty prediction set");for(std::size_t k=0;k<m;++k)p.prediction_set.push_back(r.flag());if(r.flag())p.receipt=read_receipt(r);p.evaluated=r.flag();p.modality=r.s();require(p.id==j+1&&p.emission_tick<=tick()&&p.target_tick>=p.emission_tick,"invalid prediction chronology");predictions_.push_back(std::move(p));}verify(r);
    require(!pending_prediction_||*pending_prediction_<predictions_.size(),"pending prediction missing");require((comparison_stage_=="pending")==pending_prediction_.has_value(),"inconsistent pending comparison state");
    auto names=world_.runtime().channel_names();for(const auto& name:std::vector<std::string>{"sensor.A","sensor.B","body.common_query"})require(std::find(names.begin(),names.end(),name)!=names.end(),"missing cognitive interface; load never prepares missing channels");if(parameters_.profile=="comparison")for(const auto& name:{"actual_report.negative","actual_report.positive"})require(std::find(names.begin(),names.end(),name)!=names.end(),"missing comparison interface");
    require(world_.runtime().dimension()==47&&world_.recipe().id=="relational.v1","cognitive physical recipe mismatch");
}
void CognitiveSession::save_snapshot(const std::string& path,bool trace){log({tick(),tick(),0,"set_snapshot_metadata","OPERATIVE_METADATA_NON_RAW",cognitive_prefix,"USER_PERSISTENCE_REQUEST",std::nullopt});log({tick(),tick(),0,"save_snapshot","FILESYSTEM_OPERATIVE_PERSISTENCE",path,"USER_PERSISTENCE_REQUEST",std::nullopt});put_metadata(world_.runtime(),cognitive_prefix,serialize());world_.save_snapshot(path,trace);}
CognitiveSession CognitiveSession::load_snapshot(const std::string& path){auto w=OrganizationalWorld::load_snapshot(path);auto bytes=get_metadata(w.runtime(),cognitive_prefix);CognitiveSession e(std::move(w),{});e.deserialize(bytes);return e;}
Runtime CognitiveSession::load_legacy_physical_snapshot(const std::string& path){return Runtime::load_snapshot(path);}

NativeAssociationSession NativeAssociationSession::create(NativeAssociationParameters p){auto r=OrganizationRecipe::mobile_pair(p.translation);r.execution=p.execution;return NativeAssociationSession(OrganizationalWorld::create(r));}
AssociationResponse NativeAssociationSession::train(const std::vector<std::uint16_t>& teachers,std::uint16_t cue,const std::string& mode){require(tick()==0,"acquisition requires initial boundary zero; no hidden individual reconstruction");require(teachers.size()==2,"two teacher loads are required");require(mode=="paired"||mode=="unpaired"||mode=="omitted","unknown acquisition mode");AssociationResponse out;out.operation="acquisition";out.modality="EXPERIENCE_PROTOCOL";out.scope="fixed physical routes; native acquired additive relations, not arbitrary semantics";std::vector<std::uint64_t> ids;for(int j=0;j<2;++j)if(mode!="omitted"){ids.push_back(world_.submit("l"+std::to_string(j)+".cue",cue,0).id);ids.push_back(world_.submit("l"+std::to_string(j)+".teacher",teachers[j],mode=="unpaired"?1:0).id);}world_.run_until(6);for(auto id:ids)out.receipts.push_back(finalized(world_.runtime(),id));out.tick=tick();return out;}
AssociationResponse NativeAssociationSession::query(int port,std::uint16_t payload){require(port==0||port==1,"physical port outside [0,1]");auto t=tick();require(t<=std::numeric_limits<std::uint64_t>::max()-5,"query tick overflow");auto id=world_.probe("q"+std::to_string(port)+".query",payload,t).id;world_.advance(5);AssociationResponse out;out.operation="query";out.modality="PHYSICAL_PROBE_ON_MAIN";out.scope="fixed port consumable probe; late/occupied receipt remains explicit";out.input_tick=t;out.tick=tick();out.receipts.push_back(finalized(world_.runtime(),id));add_response(out,"q"+std::to_string(port),world_.observe("q"+std::to_string(port),"response"));return out;}
AssociationResponse NativeAssociationSession::query_panel(std::uint16_t payload){auto t=tick();require(t<=std::numeric_limits<std::uint64_t>::max()-5,"query tick overflow");std::vector<std::uint64_t> ids;for(int j=0;j<2;++j)ids.push_back(world_.probe("q"+std::to_string(j)+".query",payload,t).id);world_.advance(5);auto out=observe();out.operation="query_panel";out.modality="PHYSICAL_PROBE_ON_MAIN";out.input_tick=t;for(auto id:ids)out.receipts.push_back(finalized(world_.runtime(),id));return out;}
AssociationResponse NativeAssociationSession::observe() const{AssociationResponse out;out.operation="observe";out.modality="PASSIVE_OBSERVATION";out.scope="declared fixed sites; use sequence captures for moving relation queries";out.tick=tick();for(int j=0;j<2;++j)add_response(out,"q"+std::to_string(j),world_.observe("q"+std::to_string(j),"response"));return out;}
NativeAssociationSession NativeAssociationSession::fork() const{NativeAssociationSession child(world_.fork());child.metadata_=metadata_;return child;}
void NativeAssociationSession::start_sequence(const std::vector<std::int64_t>& values,const std::string& id,std::uint64_t first){world_.start_mobile_sequence(id,values,first,5);}
void NativeAssociationSession::advance(std::uint64_t n){world_.advance(n);}
void NativeAssociationSession::run_until(std::uint64_t t){world_.run_until(t);}
void NativeAssociationSession::set_interface_metadata(const std::string& k,const std::string& v){validate_metadata(metadata_,k,v);metadata_[k]=v;}
std::optional<std::string> NativeAssociationSession::get_interface_metadata(const std::string& k) const{auto i=metadata_.find(k);return i==metadata_.end()?std::nullopt:std::optional<std::string>(i->second);}
void NativeAssociationSession::save_snapshot(const std::string& path,bool trace){Writer w;w.u(0x344153534f433031ULL);write_map(w,metadata_);seal(w);put_metadata(world_.runtime(),std::string(association_key)+".",w.b);world_.save_snapshot(path,trace);}
NativeAssociationSession NativeAssociationSession::load_snapshot(const std::string& path){auto w=OrganizationalWorld::load_snapshot(path);require(w.recipe().id=="mobile_pair.v1","association snapshot recipe mismatch");auto bytes=get_metadata(w.runtime(),std::string(association_key)+".");Reader r{bytes};require(r.u()==0x344153534f433031ULL,"unsupported association schema");NativeAssociationSession s(std::move(w));s.metadata_=read_map(r);verify(r);return s;}
OrganizationalWorld create_learnable_cascade(int depth,Coordinate translation,v27::TickOptions execution){auto recipe=OrganizationRecipe::cascade(depth,translation);recipe.parameters["source_absent"]=1;recipe.execution=execution;auto w=OrganizationalWorld::create(recipe);for(int j=0;j<depth;++j){auto hub=w.view("stage"+std::to_string(j)).spec().ports.at("hub");w.declare_interface(channel("experience."+std::to_string(j)+".cue",plus(hub,{3,0,0},127),{-1,0,0},1,false));w.declare_interface(channel("experience."+std::to_string(j)+".teacher",plus(hub,{-3,-3,0},127),{1,1,0},1,false));}return w;}
std::vector<EventReceipt> experience_composition(OrganizationalWorld& w,const std::vector<std::pair<std::uint16_t,std::uint16_t>>& pairs,std::optional<std::size_t> omit){require(w.recipe().id=="cascade.v1"&&w.runtime().current_tick()==0,"online composition acquisition requires empty cascade at T0");require(pairs.size()==w.organization_ids().size()&&(!omit||*omit<pairs.size()),"composition pair/omission count mismatch");std::vector<std::uint64_t> ids;for(std::size_t j=0;j<pairs.size();++j)if(!omit||j!=*omit){ids.push_back(w.submit("experience."+std::to_string(j)+".cue",pairs[j].first,0).id);ids.push_back(w.submit("experience."+std::to_string(j)+".teacher",pairs[j].second,0).id);}w.run_until(6);std::vector<EventReceipt> receipts;for(auto id:ids)receipts.push_back(finalized(w.runtime(),id));return receipts;}
AssociationResponse query_composition(OrganizationalWorld& w,std::uint16_t payload){require(w.recipe().id=="cascade.v1","composition query requires cascade");const auto depth=w.organization_ids().size();auto t=w.runtime().current_tick();require(t<=std::numeric_limits<std::uint64_t>::max()-5*depth,"cascade tick overflow");auto id=w.probe("query",payload,t).id;AssociationResponse out;out.operation="composition_query";out.input_tick=t;out.modality="PHYSICAL_PROBE_ON_MAIN";out.scope="native additive composition of acquired relations; no answer dictionary";for(std::size_t j=0;j<depth;++j){w.run_until(t+5*(j+1));add_response(out,"stage"+std::to_string(j),w.observe("stage"+std::to_string(j),"response"));}out.tick=w.runtime().current_tick();out.receipts.push_back(finalized(w.runtime(),id));return out;}
} // namespace dee::thinking
