#include "dee_thinking/organizational.hpp"
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <limits>
#include <set>
#include <stdexcept>
#include <utility>

namespace dee::thinking {
Runtime prepare_organizational_recipe(OrganizationRecipe&);
struct OrganizationalState {
    std::shared_ptr<Runtime> runtime;
    OrganizationRecipe recipe;
    std::vector<QueryProtocol> protocols;
    std::vector<DiagnosticEditReceipt> edits;
    std::vector<std::string> operations;
    std::map<std::string,OutputDecoder> decoders;
    TraceSession trace;
};
namespace {
constexpr std::size_t max_bytes=64U*1024U*1024U;
constexpr const char* metadata_prefix="dee_thinking.organizational.v1.";
void ensure(bool value,const char* msg){if(!value)throw std::invalid_argument(msg);}
void valid_direction(Direction d){ensure(d.dx>=-1&&d.dx<=1&&d.dy>=-1&&d.dy<=1&&d.dz>=-1&&d.dz<=1,"invalid physical direction");}
void valid_name(const std::string& s){ensure(!s.empty()&&s.size()<=1024,"name length invalid");}
Coordinate move(Coordinate q,Direction d,std::uint64_t steps,int n){
    const auto k=static_cast<int>(steps%static_cast<std::uint64_t>(n));
    return {v27::wrap_coordinate(q.x+d.dx*k,n),v27::wrap_coordinate(q.y+d.dy*k,n),v27::wrap_coordinate(q.z+d.dz*k,n)};
}
void check_site(Coordinate q,int n){(void)v27::linear_index(q.x,q.y,q.z,n);}
const OrganizationSpec& find_spec(const OrganizationalState& s,const std::string& id){
    auto it=std::find_if(s.recipe.organizations.begin(),s.recipe.organizations.end(),[&](const auto& o){return o.id==id;});
    if(it==s.recipe.organizations.end())throw std::invalid_argument("unknown organization view: "+id);return *it;
}
const InterfaceSpec& find_interface(const OrganizationalState& s,const std::string& id){
    auto it=std::find_if(s.recipe.interfaces.begin(),s.recipe.interfaces.end(),[&](const auto& o){return o.name==id;});
    if(it==s.recipe.interfaces.end())throw std::invalid_argument("unknown logical interface: "+id);return *it;
}
void validate_descriptors(const OrganizationalState& s){
    ensure(s.runtime!=nullptr,"Runtime owner missing");const auto n=s.runtime->dimension();
    ensure(s.recipe.dimension==n,"recipe/Runtime dimension mismatch");
    ensure(s.recipe.t0_tick<=s.runtime->current_tick(),"recipe t0 is after Runtime tick");
    std::set<std::string> names;
    for(const auto& o:s.recipe.organizations){valid_name(o.id);ensure(names.insert(o.id).second,"duplicate organization id");ensure(o.t0_tick<=s.runtime->current_tick(),"view t0 after Runtime");for(auto [id,q]:o.ports){valid_name(id);check_site(q,n);}for(auto q:o.supports)check_site(q,n);for(auto q:{o.a,o.b,o.comparator})if(q)check_site(*q,n);}
    names.clear();for(const auto& i:s.recipe.interfaces){valid_name(i.name);valid_name(i.channel.name);ensure(names.insert(i.name).second,"duplicate logical interface");check_site(i.channel.injection_site,n);valid_direction(i.channel.direction);ensure(i.channel.semantic<=7,"interface semantic invalid");i.codec.validate();}
    ensure(s.trace.sample_budget>0&&s.trace.sample_budget<=65536,"trace budget outside [1,65536]");
    ensure(s.trace.sites.size()<=128&&s.trace.segments.size()<=256,"trace instrument limit exceeded");
    for(auto [id,q]:s.trace.sites){valid_name(id);check_site(q,n);}for(const auto& segment:s.trace.segments){valid_name(segment.id);check_site(segment.birth_site,n);valid_direction(segment.direction);}
    for(const auto& p:s.protocols){ensure(p.next_capture<=p.steps.size(),"protocol cursor invalid");for(const auto& step:p.steps){ensure(step.read_tick>=step.input_tick,"protocol timing invalid");for(auto q:step.targets)check_site(q,n);}}
}
struct Writer {
    std::vector<std::uint8_t> bytes;
    void need(std::size_t n){if(n>max_bytes||bytes.size()>max_bytes-n)throw std::length_error("organizational metadata size limit");}
    void u8(std::uint8_t v){need(1);bytes.push_back(v);}
    void u64(std::uint64_t v){need(8);for(int j=0;j<8;++j)bytes.push_back(static_cast<std::uint8_t>(v>>(j*8)));}
    void str(const std::string& s){ensure(s.size()<=(1U<<20),"metadata string too long");u64(s.size());need(s.size());bytes.insert(bytes.end(),s.begin(),s.end());}
    void coord(Coordinate q){u64(static_cast<std::uint64_t>(static_cast<std::int64_t>(q.x)));u64(static_cast<std::uint64_t>(static_cast<std::int64_t>(q.y)));u64(static_cast<std::uint64_t>(static_cast<std::int64_t>(q.z)));}
    void direction(Direction d){coord({d.dx,d.dy,d.dz});}
    void obs(const Observation& o){u64(o.tick);coord(o.coordinate);u64(o.raw);u64(o.clock);}
    void optional(const std::optional<Coordinate>& q){u8(q.has_value());if(q)coord(*q);}
};
struct Reader {
    const std::vector<std::uint8_t>& bytes;std::size_t pos{};
    void need(std::size_t n){if(pos>bytes.size()||n>bytes.size()-pos)throw std::runtime_error("truncated organizational metadata");}
    std::uint8_t u8(){need(1);return bytes[pos++];}
    bool boolean(){auto v=u8();if(v>1)throw std::runtime_error("invalid boolean metadata");return v!=0;}
    std::uint64_t u64(){need(8);std::uint64_t v=0;for(int j=0;j<8;++j)v|=static_cast<std::uint64_t>(bytes[pos++])<<(j*8);return v;}
    std::size_t count(std::size_t cap){auto v=u64();if(v>cap)throw std::runtime_error("metadata collection limit exceeded");return static_cast<std::size_t>(v);}
    std::string str(){auto n=count(1U<<20);need(n);std::string s(reinterpret_cast<const char*>(bytes.data()+pos),n);pos+=n;return s;}
    int integer(){auto v=static_cast<std::int64_t>(u64());if(v<std::numeric_limits<int>::min()||v>std::numeric_limits<int>::max())throw std::runtime_error("coordinate integer overflow");return static_cast<int>(v);}
    Coordinate coord(){int x=integer(),y=integer(),z=integer();return {x,y,z};}
    Direction direction(){auto q=coord();return {q.x,q.y,q.z};}
    Observation obs(){Observation o;o.tick=u64();o.coordinate=coord();o.raw=u64();o.clock=u64();o.record=v27::decode_record(o.raw);return o;}
    std::optional<Coordinate> optional(){if(!boolean())return std::nullopt;return coord();}
};
template<class E> E read_enum(Reader& r,std::uint8_t maximum){auto v=r.u8();if(v<1||v>maximum)throw std::runtime_error("metadata enum invalid");return static_cast<E>(v);}
void write_symbols(Writer& w,const std::map<std::string,std::uint16_t>& m){w.u64(m.size());for(const auto& [s,v]:m){w.str(s);w.u64(v);}}
std::map<std::string,std::uint16_t> read_symbols(Reader& r){std::map<std::string,std::uint16_t> m;for(auto n=r.count(65536);n--;){auto s=r.str();auto v=r.u64();ensure(v<=65535,"codec load invalid");ensure(m.emplace(s,static_cast<std::uint16_t>(v)).second,"duplicate codec symbol");}return m;}
void write_codec(Writer& w,const InputCodec& c){w.str(c.version);w.u8(static_cast<std::uint8_t>(c.type));w.u64(static_cast<std::uint64_t>(c.minimum));w.u64(static_cast<std::uint64_t>(c.maximum));write_symbols(w,c.symbols);}
InputCodec read_codec(Reader& r){InputCodec c;c.version=r.str();c.type=read_enum<CodecType>(r,4);c.minimum=static_cast<std::int64_t>(r.u64());c.maximum=static_cast<std::int64_t>(r.u64());c.symbols=read_symbols(r);c.validate();return c;}
void write_recipe(Writer& w,const OrganizationRecipe& p){
    w.str(p.id);w.str(p.version);w.u64(p.dimension);w.coord(p.origin);w.u64(p.t0_tick);w.str(p.domain);w.u8(static_cast<std::uint8_t>(p.execution.backend));w.u64(p.execution.threads);
    w.u64(p.parameters.size());for(const auto& [s,v]:p.parameters){w.str(s);w.u64(static_cast<std::uint64_t>(v));}
    w.u64(p.options.size());for(const auto& [s,v]:p.options){w.str(s);w.str(v);}
    w.u64(p.placements.size());for(const auto& x:p.placements){w.coord(x.site);w.u64(x.raw);w.u64(x.clock);w.str(x.role);}
    w.u64(p.organizations.size());for(const auto& o:p.organizations){w.str(o.id);w.str(o.recipe_id);w.u64(o.t0_tick);w.optional(o.a);w.optional(o.b);w.optional(o.comparator);w.u64(o.ports.size());for(auto [s,q]:o.ports){w.str(s);w.coord(q);}w.u64(o.supports.size());for(auto q:o.supports)w.coord(q);}
    w.u64(p.interfaces.size());for(const auto& x:p.interfaces){w.str(x.name);w.str(x.channel.name);w.coord(x.channel.injection_site);w.u64(x.channel.state);w.direction(x.channel.direction);w.u8(x.channel.semantic);w.u8(x.channel.allow_experience);w.u8(x.channel.allow_probe);write_codec(w,x.codec);w.str(x.admission);w.str(x.meaning_location);}
    w.u64(p.actions.size());for(const auto& a:p.actions){w.str(a.id);w.str(a.scope);w.u64(a.sites.size());for(auto q:a.sites)w.coord(q);w.u64(a.roles.size());for(auto s:a.roles)w.str(s);w.u64(a.observation_ticks.size());for(auto t:a.observation_ticks)w.u64(t);}
}
OrganizationRecipe read_recipe(Reader& r){
    OrganizationRecipe p;p.id=r.str();p.version=r.str();p.dimension=r.integer();p.origin=r.coord();p.t0_tick=r.u64();p.domain=r.str();auto b=r.u8();ensure(b<=2,"backend metadata invalid");p.execution.backend=static_cast<v27::Backend>(b);p.execution.threads=r.count(65536);
    for(auto n=r.count(4096);n--;){auto s=r.str();auto v=static_cast<std::int64_t>(r.u64());ensure(p.parameters.emplace(s,v).second,"duplicate recipe parameter");}
    for(auto n=r.count(4096);n--;){auto s=r.str(),v=r.str();ensure(p.options.emplace(s,v).second,"duplicate recipe option");}
    for(auto n=r.count(1048576);n--;){InitialPlacement x;x.site=r.coord();x.raw=r.u64();x.clock=r.u64();x.role=r.str();p.placements.push_back(std::move(x));}
    for(auto n=r.count(4096);n--;){OrganizationSpec o;o.id=r.str();o.recipe_id=r.str();o.t0_tick=r.u64();o.a=r.optional();o.b=r.optional();o.comparator=r.optional();for(auto k=r.count(4096);k--;){auto s=r.str();auto q=r.coord();ensure(o.ports.emplace(s,q).second,"duplicate port");}for(auto k=r.count(65536);k--;)o.supports.push_back(r.coord());p.organizations.push_back(std::move(o));}
    for(auto n=r.count(65536);n--;){InterfaceSpec x;x.name=r.str();x.channel.name=r.str();x.channel.injection_site=r.coord();auto state=r.u64();ensure(state<=0xffffffffULL,"channel state overflow");x.channel.state=static_cast<std::uint32_t>(state);x.channel.direction=r.direction();x.channel.semantic=r.u8();x.channel.allow_experience=r.boolean();x.channel.allow_probe=r.boolean();x.codec=read_codec(r);x.admission=r.str();x.meaning_location=r.str();p.interfaces.push_back(std::move(x));}
    for(auto n=r.count(4096);n--;){ActionCoupling a;a.id=r.str();a.scope=r.str();for(auto k=r.count(65536);k--;)a.sites.push_back(r.coord());for(auto k=r.count(65536);k--;)a.roles.push_back(r.str());for(auto k=r.count(65536);k--;)a.observation_ticks.push_back(r.u64());p.actions.push_back(std::move(a));}return p;
}
void write_trace(Writer& w,const TraceSession& t){
    w.u64(t.sample_budget);w.u8(t.capture_stopped);w.u64(t.sites.size());for(auto [id,q]:t.sites){w.str(id);w.coord(q);}
    w.u64(t.segments.size());for(const auto& s:t.segments){w.str(s.id);w.coord(s.birth_site);w.direction(s.direction);w.u64(s.birth_tick);w.u64(s.last_tick);w.u8(s.expected_load.has_value());if(s.expected_load)w.u64(*s.expected_load);w.u8(s.expected_semantic.has_value());if(s.expected_semantic)w.u8(*s.expected_semantic);w.u8(s.correspondence_stopped);}
    w.u64(t.samples.size());for(const auto& s:t.samples){w.str(s.id);w.u64(s.tick);w.obs(s.observation);w.coord(s.relative_to_origin);for(auto q:s.unwrapped)w.u64(static_cast<std::uint64_t>(q));w.str(s.coverage);}
}
TraceSession read_trace(Reader& r){
    TraceSession t;t.sample_budget=r.count(65536);ensure(t.sample_budget>0,"trace budget invalid");t.capture_stopped=r.boolean();
    for(auto n=r.count(128);n--;){auto s=r.str();auto q=r.coord();ensure(t.sites.emplace(s,q).second,"duplicate traced site");}
    for(auto n=r.count(256);n--;){MobileSegment s;s.id=r.str();s.birth_site=r.coord();s.direction=r.direction();s.birth_tick=r.u64();s.last_tick=r.u64();if(r.boolean()){auto x=r.u64();ensure(x<=65535,"mobile load invalid");s.expected_load=static_cast<std::uint16_t>(x);}if(r.boolean()){auto x=r.u8();ensure(x<=7,"mobile semantic invalid");s.expected_semantic=x;}s.correspondence_stopped=r.boolean();t.segments.push_back(s);}
    for(auto n=r.count(t.sample_budget);n--;){TraceSample s;s.id=r.str();s.tick=r.u64();s.observation=r.obs();s.relative_to_origin=r.coord();for(auto& q:s.unwrapped)q=static_cast<std::int64_t>(r.u64());s.coverage=r.str();t.samples.push_back(s);}return t;
}
std::vector<std::uint8_t> serialize(const OrganizationalState& s,bool trace){
    Writer w;w.u64(1);write_recipe(w,s.recipe);w.u64(s.protocols.size());
    for(const auto& p:s.protocols){w.str(p.id);w.str(p.kind);w.u8(static_cast<std::uint8_t>(p.modality));w.u64(p.next_capture);w.u64(p.steps.size());for(const auto& x:p.steps){w.u64(x.input_tick);w.u64(x.read_tick);w.u64(static_cast<std::uint64_t>(x.input));w.u64(x.receipt_ids.size());for(auto id:x.receipt_ids)w.u64(id);w.u64(x.targets.size());for(auto q:x.targets)w.coord(q);w.u64(x.captured.size());for(const auto& o:x.captured)w.obs(o);}}
    w.u64(s.edits.size());for(const auto& e:s.edits){w.coord(e.site);w.str(e.label);w.u64(e.tick);w.u64(e.raw_before);w.u64(e.raw_after);w.u64(e.clock_before);w.u64(e.clock_after);w.u8(static_cast<std::uint8_t>(e.modality));}
    w.u64(s.operations.size());for(const auto& o:s.operations)w.str(o);
    w.u64(s.decoders.size());for(const auto& [id,d]:s.decoders){w.str(id);w.str(d.version);w.u8(static_cast<std::uint8_t>(d.type));write_symbols(w,d.symbols);}
    w.u8(trace);if(trace)write_trace(w,s.trace);return w.bytes;
}
void deserialize(OrganizationalState& s,const std::vector<std::uint8_t>& bytes){
    Reader r{bytes};ensure(r.u64()==1,"unsupported organizational metadata schema");s.recipe=read_recipe(r);
    for(auto n=r.count(4096);n--;){QueryProtocol p;p.id=r.str();p.kind=r.str();p.modality=read_enum<OperationModality>(r,6);p.next_capture=r.count(4096);for(auto k=r.count(4096);k--;){QueryStep x;x.input_tick=r.u64();x.read_tick=r.u64();x.input=static_cast<std::int64_t>(r.u64());for(auto j=r.count(4096);j--;)x.receipt_ids.push_back(r.u64());for(auto j=r.count(4096);j--;)x.targets.push_back(r.coord());for(auto j=r.count(4096);j--;)x.captured.push_back(r.obs());p.steps.push_back(std::move(x));}s.protocols.push_back(std::move(p));}
    for(auto n=r.count(1048576);n--;){DiagnosticEditReceipt e;e.site=r.coord();e.label=r.str();e.tick=r.u64();e.raw_before=r.u64();e.raw_after=r.u64();e.clock_before=r.u64();e.clock_after=r.u64();e.modality=read_enum<OperationModality>(r,6);s.edits.push_back(std::move(e));}
    for(auto n=r.count(1048576);n--;)s.operations.push_back(r.str());
    for(auto n=r.count(4096);n--;){auto id=r.str();OutputDecoder d;d.version=r.str();d.type=read_enum<CodecType>(r,4);d.symbols=read_symbols(r);ensure(s.decoders.emplace(id,d).second,"duplicate decoder");}
    if(r.boolean())s.trace=read_trace(r);ensure(r.pos==bytes.size(),"organizational metadata trailing bytes");validate_descriptors(s);
}
std::string hex(const std::vector<std::uint8_t>& b){const char* alphabet="0123456789abcdef";std::string s;s.reserve(b.size()*2);for(auto v:b){s+=alphabet[v>>4];s+=alphabet[v&15];}return s;}
std::vector<std::uint8_t> unhex(const std::string& s){ensure(s.size()%2==0&&s.size()<=max_bytes*2,"metadata hex size invalid");auto digit=[](char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;throw std::runtime_error("metadata hex invalid");};std::vector<std::uint8_t>b;b.reserve(s.size()/2);for(std::size_t j=0;j<s.size();j+=2)b.push_back(static_cast<std::uint8_t>(digit(s[j])*16+digit(s[j+1])));return b;}
std::uint64_t checksum(const std::vector<std::uint8_t>& b){std::uint64_t x=1469598103934665603ULL;for(auto v:b){x^=v;x*=1099511628211ULL;}return x;}
} // namespace

void InputCodec::validate() const {ensure(version=="1.0.0","unsupported codec version");ensure(static_cast<int>(type)>=1&&static_cast<int>(type)<=4,"codec type invalid");if(type==CodecType::BoundedInteger||type==CodecType::Boolean)ensure(minimum>=0&&maximum<=65535&&minimum<=maximum,"invalid codec range");if(type==CodecType::Enumeration||type==CodecType::RegisteredPattern){ensure(!symbols.empty()&&symbols.size()<=65536,"empty/oversized symbol encoding");for(auto [id,v]:symbols){valid_name(id);(void)v;}}}
std::uint16_t InputCodec::encode_integer(std::int64_t v) const {validate();ensure(type==CodecType::BoundedInteger||type==CodecType::Boolean,"symbol codec requires encode_symbol");if(type==CodecType::Boolean)ensure(v==0||v==1,"boolean codec requires 0/1");ensure(v>=minimum&&v<=maximum,"input outside declared range");return static_cast<std::uint16_t>(v);}
std::uint16_t InputCodec::encode_symbol(const std::string& v) const {validate();ensure(type==CodecType::Enumeration||type==CodecType::RegisteredPattern,"integer codec requires encode_integer");auto it=symbols.find(v);if(it==symbols.end())throw std::invalid_argument("unregistered symbol");return it->second;}
bool InputCodec::injective() const {validate();std::set<std::uint16_t> values;for(auto [id,v]:symbols)if(!values.insert(v).second)return false;return true;}
DecodedOutput OutputDecoder::decode(const Observation& o) const {
    ensure(version=="1.0.0","unsupported decoder version");DecodedOutput d;d.physical=o;d.available=o.record.state>0&&o.record.semantic!=5;d.ordinary_cap_reached=o.record.s_reg==v27::kReducerCap;
    if(!d.available){d.status="NO_ACTIVE_RESPONSE";return d;}
    if(type==CodecType::BoundedInteger){d.integer=o.record.s_reg;d.status=d.ordinary_cap_reached?"ORDINARY_CAP_OBSERVED":"MEASURED";}
    else if(type==CodecType::Boolean){if(o.record.s_reg<=1){d.integer=o.record.s_reg;d.status="MEASURED";}else{d.status="OUTSIDE_BOOLEAN_DECODER";d.ambiguous=true;}}
    else if(type==CodecType::Enumeration||type==CodecType::RegisteredPattern){for(auto [s,v]:symbols)if(v==o.record.s_reg)d.symbols.push_back(s);d.ambiguous=d.symbols.size()!=1;d.status=d.symbols.empty()?"UNMAPPED_PHYSICAL_RESPONSE":d.ambiguous?"NONINJECTIVE_AMBIGUITY":"MEASURED";}
    else throw std::invalid_argument("invalid decoder type");return d;
}
const char* to_string(OperationModality m) noexcept {switch(m){case OperationModality::NativeEvolution:return "NATIVE_EVOLUTION";case OperationModality::ExperienceProtocol:return "EXPERIENCE_PROTOCOL";case OperationModality::PassiveObservation:return "PASSIVE_OBSERVATION";case OperationModality::PhysicalProbe:return "PHYSICAL_PROBE";case OperationModality::DiagnosticFork:return "DIAGNOSTIC_FORK";case OperationModality::AssistedReconstruction:return "ASSISTED_RECONSTRUCTION";}return "INVALID";}
OrganizationView::OrganizationView(std::shared_ptr<OrganizationalState> s,std::string id):state_(std::move(s)),id_(std::move(id)){}
const OrganizationSpec& OrganizationView::spec() const{return find_spec(*state_,id_);}
Runtime& OrganizationView::runtime() const{return *state_->runtime;}
FunctionalReadout OrganizationView::observe() const {
    const auto& s=spec();FunctionalReadout f;f.organization_id=s.id;f.tick=runtime().current_tick();f.relative_tick=f.tick-s.t0_tick;f.supports_intact=true;
    for(auto [id,q]:s.ports)f.observations[id]=runtime().observe(q);
    if(s.a&&s.b){auto a=runtime().observe(*s.a),b=runtime().observe(*s.b);f.observations["A"]=a;f.observations["B"]=b;f.centers_available=a.record.state>0&&a.record.semantic==1&&b.record.state>0&&b.record.semantic==1;if(f.centers_available)f.delta=static_cast<std::int64_t>(a.record.s_reg)-b.record.s_reg;}
    if(s.comparator){auto c=runtime().observe(*s.comparator);f.observations["comparator"]=c;f.reader_available=c.record.state>0&&c.record.semantic!=5;if(f.reader_available)f.axis_projection=c.record.dx;}
    else {f.reader_available=std::any_of(f.observations.begin(),f.observations.end(),[](const auto& o){return o.second.record.state>0&&o.second.record.semantic!=5;});}
    for(auto q:s.supports){auto o=runtime().observe(q);if(o.raw==0||o.record.semantic!=4)f.supports_intact=false;}return f;
}
ResilienceObservation OrganizationView::resilience() const {ResilienceObservation r;r.functional=observe();for(auto q:spec().supports){auto o=runtime().observe(q);if(o.raw==0||o.record.semantic!=4)r.missing_supports.push_back(q);}for(auto [id,o]:r.functional.observations){if(o.record.s_reg==19664)r.ordinary_cap_sites.push_back(id);if(o.record.s_reg==65535)r.representable_cap_sites.push_back(id);}return r;}
OrganizationalWorld OrganizationalWorld::create(const OrganizationRecipe& recipe){
    auto state=std::make_shared<OrganizationalState>();state->recipe=recipe;
    auto extra_interfaces=recipe.interfaces;
    auto extra_views=recipe.organizations;
    // Descriptor collections supplied by a caller are kept only for research
    // recipes; named factories generate their effective contracts once.
    if(recipe.id!="research.v1"){state->recipe.organizations.clear();state->recipe.actions.clear();state->recipe.interfaces.clear();}
    state->runtime=std::make_shared<Runtime>(prepare_organizational_recipe(state->recipe));
    if(recipe.id!="research.v1") {
        for(const auto& e:extra_views) {
            auto it=std::find_if(state->recipe.organizations.begin(),state->recipe.organizations.end(),[&](const auto& x){return x.id==e.id;});
            if(it==state->recipe.organizations.end())state->recipe.organizations.push_back(e);
            else ensure(e.ports==it->ports,"custom view conflicts with generated geometry");
        }
        for(const auto& e:extra_interfaces) {
            auto it=std::find_if(state->recipe.interfaces.begin(),state->recipe.interfaces.end(),[&](const auto& x){return x.name==e.name;});
            if(it==state->recipe.interfaces.end())state->recipe.interfaces.push_back(e);
            else {ensure(e.channel.name==it->channel.name&&e.channel.injection_site==it->channel.injection_site&&e.channel.state==it->channel.state&&e.channel.semantic==it->channel.semantic&&e.channel.direction.dx==it->channel.direction.dx&&e.channel.direction.dy==it->channel.direction.dy&&e.channel.direction.dz==it->channel.direction.dz,"interface conflicts with generated physical channel");*it=e;}
        }
    }
    const auto existing=state->runtime->channel_names();
    for(const auto& i:state->recipe.interfaces){i.codec.validate();if(std::find(existing.begin(),existing.end(),i.channel.name)==existing.end())state->runtime->register_channel(i.channel);}
    state->operations.push_back("CREATE_PREPARATION tick="+std::to_string(state->runtime->current_tick()));validate_descriptors(*state);return OrganizationalWorld(state);
}
OrganizationalWorld OrganizationalWorld::attach(std::shared_ptr<Runtime> r,OrganizationRecipe p,std::vector<OrganizationSpec> specs){auto s=std::make_shared<OrganizationalState>();s->runtime=std::move(r);s->recipe=std::move(p);s->recipe.organizations=std::move(specs);validate_descriptors(*s);return OrganizationalWorld(s);}
Runtime& OrganizationalWorld::runtime() const{return *state_->runtime;}
const OrganizationRecipe& OrganizationalWorld::recipe() const{return state_->recipe;}
std::vector<std::string> OrganizationalWorld::organization_ids() const {std::vector<std::string>x;for(const auto& o:state_->recipe.organizations)x.push_back(o.id);return x;}
OrganizationView OrganizationalWorld::view(const std::string& id) const{(void)find_spec(*state_,id);return OrganizationView(state_,id);}
std::vector<InterfaceSpec> OrganizationalWorld::interfaces() const{return state_->recipe.interfaces;}
void OrganizationalWorld::declare_interface(InterfaceSpec i){valid_name(i.name);i.codec.validate();if(std::any_of(state_->recipe.interfaces.begin(),state_->recipe.interfaces.end(),[&](const auto& x){return x.name==i.name;}))throw std::invalid_argument("logical interface already declared");runtime().register_channel(i.channel);state_->recipe.interfaces.push_back(std::move(i));state_->operations.push_back("DECLARE_INTERFACE tick="+std::to_string(runtime().current_tick()));}
EventReceipt OrganizationalWorld::submit(const std::string& id,std::int64_t v,std::uint64_t t){const auto& i=find_interface(*state_,id);const auto load=i.codec.encode_integer(v);auto r=runtime().experience(i.channel.name,t,load);state_->operations.push_back("EXPERIENCE_PROTOCOL interface="+id+" at="+std::to_string(t)+" load="+std::to_string(load)+" receipt="+std::to_string(r.id));return r;}
EventReceipt OrganizationalWorld::submit_symbol(const std::string& id,const std::string& v,std::uint64_t t){const auto& i=find_interface(*state_,id);const auto load=i.codec.encode_symbol(v);auto r=runtime().experience(i.channel.name,t,load);state_->operations.push_back("EXPERIENCE_PROTOCOL symbol interface="+id+" at="+std::to_string(t)+" load="+std::to_string(load)+" receipt="+std::to_string(r.id));return r;}
EventReceipt OrganizationalWorld::probe(const std::string& id,std::int64_t v,std::uint64_t t){const auto& i=find_interface(*state_,id);const auto load=i.codec.encode_integer(v);auto r=runtime().probe(i.channel.name,t,load);state_->operations.push_back("PHYSICAL_PROBE interface="+id+" at="+std::to_string(t)+" load="+std::to_string(load)+" receipt="+std::to_string(r.id));return r;}
EventReceipt OrganizationalWorld::probe_symbol(const std::string& id,const std::string& v,std::uint64_t t){const auto& i=find_interface(*state_,id);const auto load=i.codec.encode_symbol(v);auto r=runtime().probe(i.channel.name,t,load);state_->operations.push_back("PHYSICAL_PROBE symbol interface="+id+" at="+std::to_string(t)+" load="+std::to_string(load)+" receipt="+std::to_string(r.id));return r;}
Observation OrganizationalWorld::observe(const std::string& org,const std::string& port) const{const auto& s=find_spec(*state_,org);auto it=s.ports.find(port);if(it==s.ports.end())throw std::invalid_argument("unknown observation port");return runtime().observe(it->second);}
DecodedOutput OrganizationalWorld::decode(const std::string& org,const std::string& port,const OutputDecoder& d) const{return d.decode(observe(org,port));}
void OrganizationalWorld::declare_decoder(std::string id,OutputDecoder d){valid_name(id);ensure(d.version=="1.0.0","unsupported decoder");state_->decoders.insert_or_assign(std::move(id),std::move(d));}
OutputDecoder OrganizationalWorld::decoder(const std::string& id) const{auto it=state_->decoders.find(id);if(it==state_->decoders.end())throw std::invalid_argument("unknown decoder");return it->second;}
v27::TickInfo OrganizationalWorld::advance(std::uint64_t count){ensure(count<=std::numeric_limits<std::uint64_t>::max()-runtime().current_tick(),"tick overflow");return run_until(runtime().current_tick()+count);}
v27::TickInfo OrganizationalWorld::run_until(std::uint64_t target){
    if(target<runtime().current_tick())throw std::invalid_argument("target is in the past");
    v27::TickInfo info;while(runtime().current_tick()<target){auto boundary=target;bool tracing=!state_->trace.capture_stopped&&(!state_->trace.sites.empty()||!state_->trace.segments.empty());if(tracing)boundary=std::min(boundary,runtime().current_tick()+1);
        for(const auto& p:state_->protocols)if(p.next_capture<p.steps.size())boundary=std::min(boundary,p.steps[p.next_capture].read_tick);
        if(boundary>runtime().current_tick())info=runtime().run_until(boundary);
        for(auto& p:state_->protocols)while(p.next_capture<p.steps.size()&&p.steps[p.next_capture].read_tick<=runtime().current_tick()){auto& s=p.steps[p.next_capture++];for(auto q:s.targets)s.captured.push_back(runtime().observe(q));}
        if(tracing)capture_trace();if(runtime().paused())break;
    }return info;
}
void OrganizationalWorld::start_mobile_sequence(const std::string& id,const std::vector<std::int64_t>& inputs,std::uint64_t first,std::uint64_t interval){
    valid_name(id);ensure(state_->recipe.id=="mobile_pair.v1","mobile sequence requires mobile_pair recipe");ensure(!inputs.empty()&&inputs.size()<=1024,"sequence count outside [1,1024]");ensure(first>=6&&first>=runtime().current_tick(),"first query before admissible boundary");ensure(interval==5,"published mobile sequence interval is five");ensure(first<=std::numeric_limits<std::uint64_t>::max()-5,"sequence tick overflow");ensure(inputs.size()-1<=(std::numeric_limits<std::uint64_t>::max()-first-5)/interval,"sequence tick overflow");
    ensure(std::none_of(state_->protocols.begin(),state_->protocols.end(),[&](const auto& p){return p.id==id;}),"duplicate protocol id");
    for(auto v:inputs)ensure(v>=0&&v<=65535,"query load range invalid");QueryProtocol p;p.id=id;p.kind="native_mobile_sequential_queries.v1";
    for(std::size_t k=0;k<inputs.size();++k){QueryStep step;step.input_tick=first+k*interval;step.read_tick=step.input_tick+5;step.input=inputs[k];
        for(int j=0;j<2;++j){auto base=find_spec(*state_,"q"+std::to_string(j)).ports.at("response");auto target=move(base,{0,1,0},first-6,runtime().dimension());if(k)target=move(target,{-1,1,0},k*interval,runtime().dimension());step.targets.push_back(target);InterfaceSpec i;i.name=id+"."+std::to_string(k)+"."+std::to_string(j);i.channel={i.name,move(target,{1,0,0},5,runtime().dimension()),1,{-1,0,0},1,true,true};declare_interface(i);auto rec=probe(i.name,inputs[k],step.input_tick);step.receipt_ids.push_back(rec.id);}
        p.steps.push_back(std::move(step));
    }state_->protocols.push_back(std::move(p));
}
const std::vector<QueryProtocol>& OrganizationalWorld::protocols() const{return state_->protocols;}
OrganizationalWorld OrganizationalWorld::fork() const{auto s=std::make_shared<OrganizationalState>(*state_);s->runtime=std::make_shared<Runtime>(runtime().fork());return OrganizationalWorld(s);}
OrganizationalWorld OrganizationalWorld::diagnostic_fork(const std::vector<ResearchStateEdit>& edits,bool authorize) const{
    auto branch=fork();branch.state_->runtime=std::make_shared<Runtime>(runtime().diagnostic_fork(edits,authorize));for(const auto& e:edits){auto a=runtime().observe(e.coordinate),b=branch.runtime().observe(e.coordinate);branch.state_->edits.push_back({e.coordinate,e.label,runtime().current_tick(),a.raw,b.raw,a.clock,b.clock,OperationModality::DiagnosticFork});}return branch;
}
OrganizationalWorld OrganizationalWorld::assisted_reconstruction(const OrganizationalWorld& src,const ReconstructionSpec& spec) const {
    ensure(spec.authorize_assisted_reconstruction,"assisted reconstruction authorization missing");ensure(!spec.source_sites.empty()&&spec.source_sites.size()==spec.destination_sites.size()&&spec.source_sites.size()<=65536,"reconstruction region invalid");ensure(spec.copy_raw||spec.copy_clocks,"no reconstruction fields selected");
    std::vector<ResearchStateEdit> edits;std::set<std::size_t> targets;
    for(std::size_t j=0;j<spec.source_sites.size();++j){auto q=spec.destination_sites[j];auto idx=v27::linear_index(q.x,q.y,q.z,runtime().dimension());ensure(targets.insert(idx).second,"duplicate reconstruction target");auto o=src.runtime().observe(spec.source_sites[j]);ResearchStateEdit e;e.coordinate=q;e.label="assisted_reconstruction source="+std::to_string(o.coordinate.x)+","+std::to_string(o.coordinate.y)+","+std::to_string(o.coordinate.z);if(spec.copy_raw)e.raw=o.raw;if(spec.copy_clocks)e.clock=o.clock;edits.push_back(e);}
    auto b=diagnostic_fork(edits,true);for(std::size_t j=b.state_->edits.size()-edits.size();j<b.state_->edits.size();++j)b.state_->edits[j].modality=OperationModality::AssistedReconstruction;return b;
}
const std::vector<DiagnosticEditReceipt>& OrganizationalWorld::diagnostic_edits() const{return state_->edits;}
const std::vector<std::string>& OrganizationalWorld::external_operations() const{return state_->operations;}
void OrganizationalWorld::set_trace(TraceSession t){auto old=state_->trace;state_->trace=std::move(t);try{validate_descriptors(*state_);}catch(...){state_->trace=std::move(old);throw;}}
TraceSession OrganizationalWorld::trace() const{return state_->trace;}
void OrganizationalWorld::capture_trace(){state_->trace.capture(runtime(),state_->recipe.origin);}
void OrganizationalWorld::save_snapshot(const std::string& path,bool trace) const{
    auto copy=runtime().fork();std::vector<std::string> old;for(auto [key,v]:copy.snapshot_metadata_entries())if(key.starts_with(metadata_prefix))old.push_back(key);for(auto key:old)copy.erase_snapshot_metadata(key);
    auto bytes=serialize(*state_,trace);auto encoded=hex(bytes);constexpr std::size_t chunk=524288;auto count=(encoded.size()+chunk-1)/chunk;
    copy.set_snapshot_metadata(std::string(metadata_prefix)+"chunks",std::to_string(count));for(std::size_t j=0;j<count;++j)copy.set_snapshot_metadata(std::string(metadata_prefix)+std::to_string(j),encoded.substr(j*chunk,chunk));copy.save_snapshot(path);
}
OrganizationalWorld OrganizationalWorld::load_snapshot(const std::string& path){
    auto s=std::make_shared<OrganizationalState>();s->runtime=std::make_shared<Runtime>(Runtime::load_snapshot(path));auto count=s->runtime->snapshot_metadata(std::string(metadata_prefix)+"chunks");if(!count)throw std::invalid_argument("snapshot contains no OrganizationalWorld metadata; use Runtime.load_snapshot or explicit inert attach");
    std::size_t consumed=0;auto n=std::stoull(*count,&consumed);ensure(consumed==count->size()&&n>0&&n<=256,"organizational chunk count invalid");std::string encoded;for(std::size_t j=0;j<n;++j){auto chunk=s->runtime->snapshot_metadata(std::string(metadata_prefix)+std::to_string(j));ensure(chunk.has_value(),"missing organizational metadata chunk");ensure(encoded.size()<=max_bytes*2-chunk->size(),"organizational metadata too large");encoded+=*chunk;}deserialize(*s,unhex(encoded));return OrganizationalWorld(s);
}
void TraceSession::capture(const Runtime& r,Coordinate origin){
    ensure(sample_budget>0&&sample_budget<=65536&&sites.size()<=128&&segments.size()<=256,"trace budget/config invalid");if(capture_stopped)return;
    auto add=[&](std::string id,Coordinate q,std::array<std::int64_t,3> u,std::string coverage){if(samples.size()>=sample_budget){capture_stopped=true;return;}TraceSample s;s.id=std::move(id);s.tick=r.current_tick();s.observation=r.observe(q);s.relative_to_origin={q.x-origin.x,q.y-origin.y,q.z-origin.z};s.unwrapped=u;s.coverage=std::move(coverage);samples.push_back(std::move(s));};
    for(auto [id,q]:sites)add(id,q,{q.x,q.y,q.z},"DECLARED_SITE_PASSIVE");
    for(auto& s:segments){if(r.current_tick()<s.birth_tick||s.correspondence_stopped)continue;auto steps=r.current_tick()-s.birth_tick;ensure(steps<=static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max()/2),"unwrapped trace horizon overflow");auto q=move(s.birth_site,s.direction,steps,r.dimension());auto o=r.observe(q);bool match=o.record.state>0&&o.record.dx==s.direction.dx&&o.record.dy==s.direction.dy&&o.record.dz==s.direction.dz&&(!s.expected_load||o.record.s_reg==*s.expected_load)&&(!s.expected_semantic||o.record.semantic==*s.expected_semantic);
        const auto k=static_cast<std::int64_t>(steps);add(s.id,q,{s.birth_site.x+s.direction.dx*k,s.birth_site.y+s.direction.dy*k,s.birth_site.z+s.direction.dz*k},match?"OBSERVED_DECLARED_BALLISTIC_SEGMENT_NOT_UNIQUE_ANCESTRY":"TRANSFORMATION_OR_ABSENCE_UNRESOLVED_CORRESPONDENCE_STOPPED");s.last_tick=r.current_tick();if(!match)s.correspondence_stopped=true;
    }
}
void TraceSession::export_trace(const std::string& path) const{Writer w;w.u64(0x3533545241434531ULL);write_trace(w,*this);w.u64(checksum(w.bytes));std::ofstream f(path,std::ios::binary|std::ios::trunc);if(!f)throw std::runtime_error("trace export open failed");f.write(reinterpret_cast<const char*>(w.bytes.data()),static_cast<std::streamsize>(w.bytes.size()));f.close();if(!f)throw std::runtime_error("trace export failed");}
TraceSession TraceSession::load_trace(const std::string& path){std::ifstream f(path,std::ios::binary|std::ios::ate);if(!f)throw std::runtime_error("trace open failed");auto size=f.tellg();ensure(size>=16&&size<=static_cast<std::streamoff>(max_bytes),"trace file size invalid");f.seekg(0);std::vector<std::uint8_t>b(static_cast<std::size_t>(size));f.read(reinterpret_cast<char*>(b.data()),size);ensure(static_cast<bool>(f),"trace read failed");Reader r{b};ensure(r.u64()==0x3533545241434531ULL,"trace schema invalid");auto t=read_trace(r);auto checkpos=r.pos;auto check=r.u64();ensure(r.pos==b.size(),"trace trailing bytes");b.resize(checkpos);ensure(checksum(b)==check,"trace checksum invalid");return t;}
EncounterObservation observe_encounter(const Runtime& before,const Runtime& after,Coordinate q){
    ensure(before.dimension()==after.dimension()&&after.current_tick()==before.current_tick()+1,"encounter requires adjacent same-dimension states");EncounterObservation e;e.tick_before=before.current_tick();e.tick_after=after.current_tick();e.destination=q;e.before=before.observe(q);e.after=after.observe(q);e.destination_gate=observation::inspect_write_gate(before,q,false);auto n=before.dimension();
    for(int dx=-1;dx<=1;++dx)for(int dy=-1;dy<=1;++dy)for(int dz=-1;dz<=1;++dz){if(dx==0&&dy==0&&dz==0)continue;Coordinate p{v27::wrap_coordinate(q.x+dx,n),v27::wrap_coordinate(q.y+dy,n),v27::wrap_coordinate(q.z+dz,n)};auto o=before.observe(p);if(o.raw!=0&&o.record.state<=1&&o.record.dx==-dx&&o.record.dy==-dy&&o.record.dz==-dz)e.direct_ballistic_contributors.push_back(o);}
    e.branch=e.destination_gate.branch;e.attribution_scope="observed direct ballistic candidates; not certified field genealogy or DEMUX provenance";return e;
}
} // namespace dee::thinking
