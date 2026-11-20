#include "dee_thinking/consolidated.hpp"
#include <algorithm>
#include <iomanip>
#include <limits>
#include <set>
#include <sstream>
#include <stdexcept>
#include <tuple>

namespace dee::thinking::consolidated {
namespace {
constexpr const char* descriptor_key="dee_thinking.consolidated.descriptor.v1";
constexpr const char* attached_key="dee_thinking.consolidated.attached_descriptor.v1";
void require(bool ok,const char* what){if(!ok)throw std::invalid_argument(what);}
Coordinate move(Coordinate q,Direction d,std::int64_t amount,int n){
    auto wrap=[n](std::int64_t v){v%=n;return static_cast<int>(v<0?v+n:v);};
    return {wrap(static_cast<std::int64_t>(q.x)+d.dx*amount),wrap(static_cast<std::int64_t>(q.y)+d.dy*amount),wrap(static_cast<std::int64_t>(q.z)+d.dz*amount)};
}
Coordinate translated(Coordinate q,Coordinate d,int n){return move(q,{d.x,d.y,d.z},1,n);}
std::string form_name(std::size_t i){std::ostringstream s;s<<'L'<<std::setw(2)<<std::setfill('0')<<(i+1);return s.str();}
void add_port(NativePreparation& p,const std::string& name,Coordinate q,Direction direction,std::uint32_t state=1){
    InterfaceSpec i;i.name=name;i.channel={name,q,state,direction,1,true,true};
    p.recipe.interfaces.push_back(std::move(i));p.ports[name]=name;
}
void put(NativePreparation& p,Coordinate q,std::uint32_t state,std::uint16_t load,std::uint8_t semantic,std::uint64_t clock,const std::string& role,Direction dir={}){
    require(std::none_of(p.recipe.placements.begin(),p.recipe.placements.end(),[q](const auto& v){return v.site==q;}),"initial material placements overlap");
    p.recipe.placements.push_back({q,v27::pack_record(state,load,dir.dx,dir.dy,dir.dz,semantic),clock,role});
}
void forms(NativePreparation& p,const std::vector<Coordinate>& hubs){
    for(std::size_t k=0;k<hubs.size();++k){
        const auto name=form_name(k);const auto q=hubs[k];p.forms.push_back({k,name,q});p.sites["form."+name]=q;
        add_port(p,name+".signal",move(q,{-1,0,0},-3,p.recipe.dimension),{-1,0,0});
        for(int sign:{1,-1}){const auto label=sign==1?"plus":"minus";const Direction d{1,sign,0};add_port(p,name+".event."+label,move(q,d,-3,p.recipe.dimension),d);}
    }
}
std::string manifest(const NativePreparation& p){
    std::ostringstream s;s<<"CNATIVE1 "<<p.recipe.dimension<<' '<<std::quoted(p.kind)<<' '<<std::quoted(p.domain)<<'\n';
    s<<p.forms.size()<<'\n';for(const auto& f:p.forms)s<<f.index<<' '<<std::quoted(f.name)<<' '<<f.hub.x<<' '<<f.hub.y<<' '<<f.hub.z<<'\n';
    s<<p.sites.size()<<'\n';for(const auto& [k,q]:p.sites)s<<std::quoted(k)<<' '<<q.x<<' '<<q.y<<' '<<q.z<<'\n';
    s<<p.directions.size()<<'\n';for(const auto& [k,d]:p.directions)s<<std::quoted(k)<<' '<<d.dx<<' '<<d.dy<<' '<<d.dz<<'\n';
    s<<p.ticks.size()<<'\n';for(const auto& [k,t]:p.ticks)s<<std::quoted(k)<<' '<<t<<'\n';
    s<<p.ports.size()<<'\n';for(const auto& [k,v]:p.ports)s<<std::quoted(k)<<' '<<std::quoted(v)<<'\n';
    s<<p.parameters.size()<<'\n';for(const auto& [k,v]:p.parameters)s<<std::quoted(k)<<' '<<v<<'\n';return s.str();
}
void finish(NativePreparation& p){
    std::set<std::string> port_names;for(const auto& i:p.recipe.interfaces)require(port_names.insert(i.name).second,"duplicate physical interface name");
    p.parameters["N"]=p.recipe.dimension;p.parameters["K"]=static_cast<std::int64_t>(p.forms.size());
    p.parameters["initial_material_sites"]=static_cast<std::int64_t>(p.recipe.placements.size());p.parameters["interfaces"]=static_cast<std::int64_t>(p.recipe.interfaces.size());
    p.recipe.domain=p.domain;p.recipe.parameters=p.parameters;p.recipe.options["consolidated_profile"]=p.kind;
    OrganizationSpec o;o.id="organization";o.recipe_id=p.kind;o.ports=p.sites;
    if(p.kind=="integrated_u0.cpc7.v1"){o.a=p.sites.at("body.A");o.b=p.sites.at("body.B");o.comparator=p.sites.at("body.center");}
    for(const auto& q:p.recipe.placements)if(v27::decode_record(q.raw).semantic==4)o.supports.push_back(q.site);
    p.recipe.organizations.push_back(std::move(o));p.recipe.options[descriptor_key]=manifest(p);p.initial_state_available=true;
}
const FormDescriptor& checked_form(const NativePreparation& p,std::size_t index){require(index<p.forms.size(),"form index outside preparation");return p.forms[index];}
void compatible(const OrganizationalWorld& w,const NativePreparation& p){require(w.runtime().dimension()==p.recipe.dimension,"preparation/world dimensions differ");}
void sign_ok(int sign){require(sign==-1||sign==1,"current consequence direction must be -1 or +1");}
struct PlannedInput {std::string port;std::uint16_t payload;};
// Structural preflight only. Never inspect matter, clocks, phase or admission:
// physically occupied/conflicting inputs must still reach Runtime and receipts.
void preflight(const OrganizationalWorld& w,const NativePreparation& p,const std::vector<PlannedInput>& inputs){
    compatible(w,p);const auto actual=w.interfaces();const auto registered=w.runtime().channel_names();
    auto find=[](const auto& list,const std::string& name)->const InterfaceSpec&{
        const auto it=std::find_if(list.begin(),list.end(),[&](const auto& i){return i.name==name;});
        require(it!=list.end(),"consolidated helper interface is absent");
        require(std::count_if(list.begin(),list.end(),[&](const auto& i){return i.name==name;})==1,"duplicate consolidated helper interface");return *it;};
    auto channel=[](const auto& i){const auto& c=i.channel;return std::tuple{i.name,c.name,c.injection_site.x,c.injection_site.y,c.injection_site.z,
        c.state,c.direction.dx,c.direction.dy,c.direction.dz,c.semantic,c.allow_experience,c.allow_probe};};
    auto codec=[](const auto& i){const auto& c=i.codec;return std::tuple{c.version,c.type,c.minimum,c.maximum,c.symbols};};
    for(const auto& input:inputs){const auto& expected=find(p.recipe.interfaces,input.port);const auto& found=find(actual,input.port);
        require(channel(expected)==channel(found),"consolidated helper/world channel geometry differs");
        require(codec(expected)==codec(found),"consolidated helper/world input codec differs");
        require(std::find(registered.begin(),registered.end(),found.channel.name)!=registered.end(),"consolidated helper Runtime channel is absent");
        // Validate every encoding before the first queue mutation, rather than
        // letting a later item fail after an earlier item has been scheduled.
        require(expected.codec.encode_integer(input.payload)==found.codec.encode_integer(input.payload),"consolidated helper/world encoded payload differs");
    }
}
void repertoire_revision_ports(NativePreparation& p,std::size_t index){
    const auto h=p.forms[index].hub;const int n=p.recipe.dimension;const auto off=move(h,{0,0,1},10,n);
    p.sites["revision.hub"]=h;p.sites["revision.sham_hub"]=off;p.parameters["revision_form"]=static_cast<std::int64_t>(index);
    for(int sign:{1,-1}){
        const std::string label=sign==1?"plus":"minus";const Direction d{-1,sign,0};const Direction cd{1,sign,0};
        const auto target=move(h,{4,4*sign,0},1,n),sham=move(off,{4,4*sign,0},1,n);
        for(const auto& mode:{std::string("treatment"),std::string("offpath_sham")}){
            const auto suffix=mode=="treatment"?"":"sham.";
            const auto teacher="revision.teacher2."+std::string(suffix)+label,counter="revision.counter."+std::string(suffix)+label;
            add_port(p,teacher,move(mode=="treatment"?h:off,d,-3,n),d);
            add_port(p,counter,move(mode=="treatment"?target:sham,cd,-3,n),cd);
            p.ports["revision.teacher2."+mode+"."+label]=teacher;p.ports["revision.counter."+mode+"."+label]=counter;
        }
    }
}
}

OrganizationalWorld NativePreparation::create_world() const {
    require(initial_state_available,"descriptor restored from a live world cannot prepare a new body");
    return OrganizationalWorld::create(recipe);
}

NativePreparation prepare_repertoire(const RepertoireOptions& o){
    require(o.dimension>=31&&o.dimension<=151,"repertoire N outside representable [31,151]");
    require(o.forms>=1&&o.forms<=65,"repertoire form count outside [1,65]");
    require(o.plane_gap>=2&&static_cast<std::int64_t>(o.plane_gap)*static_cast<std::int64_t>(o.forms)<=o.dimension,"repertoire planes are not distinct and separated");
    require(!o.revision_interfaces||o.revision_form<o.forms,"revision form index outside repertoire");
    NativePreparation p;p.kind="repertoire.cpc5.v1";p.recipe=OrganizationRecipe::research(o.dimension,{},0);p.recipe.execution=o.execution;
    p.domain="K opaque correspondences, two physical direction classes; not K NSM meanings. Mechanical range N31..151,K1..65,gap>=2,gap*K<=N. Historical witnesses N31/K8,N67/K16,N131/K65; new combinations require functional measurement. M1/M2 timing finite; z+10 offpath control was validated for K2, not arbitrary populated planes.";
    p.parameters={{"plane_gap",o.plane_gap},{"translation_x",o.translation.x},{"translation_y",o.translation.y},{"translation_z",o.translation.z},{"revision_interfaces",o.revision_interfaces?1:0}};
    std::vector<Coordinate> hubs;for(std::size_t k=0;k<o.forms;++k)hubs.push_back(translated({30,30,1+static_cast<int>(k)*o.plane_gap},o.translation,o.dimension));forms(p,hubs);
    p.ticks={{"acquisition_path",3},{"query_path",3},{"first_query_input",static_cast<std::uint64_t>(o.dimension)},
        {"revision_input",static_cast<std::uint64_t>(4*o.dimension)},{"revision_read",static_cast<std::uint64_t>(4*o.dimension+3)},
        {"post_revision_query",static_cast<std::uint64_t>(5*o.dimension)},{"post_revision_read",static_cast<std::uint64_t>(5*o.dimension+3)}};
    if(o.revision_interfaces)repertoire_revision_ports(p,o.revision_form);finish(p);return p;
}

NativePreparation prepare_integrated_u0(const IntegratedOptions& o){
    constexpr int n=67;require(o.center.x>=0&&o.center.x<n&&o.center.y>=0&&o.center.y<n&&o.center.z>=0&&o.center.z<n,"integrated center outside N67");
    require(o.guard_mode=="none"||o.guard_mode=="treatment"||o.guard_mode=="sham","unknown integrated guard mode");
    NativePreparation p;p.kind="integrated_u0.cpc7.v1";p.recipe=OrganizationRecipe::research(n,{},0);p.recipe.execution=o.execution;
    p.domain="Fresh N67 U0; default center33,25,42/source0,16 directional correspondences, one selected own high bank,14 lower panel, one local L03 revision. Prepared comparison/request, fixed guards and later external cue; not learned information/utility policy or65NSM meanings. Tested horizon472, LAZY; custom centers/source loads are research preparations.";
    p.parameters={{"body_source_load",o.body_source_load},{"body_phase",260},{"guard_mode",o.guard_mode=="none"?0:o.guard_mode=="treatment"?1:2},{"revision_interfaces",o.revision_interfaces?1:0},{"revision_form",2},{"plane_gap",2}};
    const auto center=o.center,a=move(center,{-1,0,0},1,n),b=move(center,{1,0,0},1,n),origin=move(center,{0,-1,0},1,n);
    p.sites["body.center"]=center;p.sites["body.A"]=a;p.sites["body.B"]=b;p.sites["body.emission"]=origin;p.sites["body.source"]=move(center,{0,0,1},1,n);
    put(p,a,1000,100,1,260,"Fresh relative-order support, not an acquired association");put(p,b,2000,100,1,260,"Fresh relative-order support, not an acquired association");
    const Direction pa[]={{-1,0,0},{-1,1,1},{0,0,1},{0,1,0}},pb[]={{0,-1,0},{0,0,-1},{1,-1,-1},{1,0,0}};
    for(int k=0;k<4;++k){const auto qa=move(a,pa[k],1,n),qb=move(b,pb[k],1,n);put(p,qa,3000+k,0,4,31+k,"Fresh relative-order support, not an acquired association");put(p,qb,4000+k,0,4,41+k,"Fresh relative-order support, not an acquired association");}
    put(p,p.sites.at("body.source"),6100,o.body_source_load,4,19,"Fresh relative-order support; explicit initial source-load calibration");
    add_port(p,"event.A",move(a,{0,-1,0},1,n),{0,-1,0},5000);add_port(p,"event.B",move(b,{0,1,0},1,n),{0,1,0},5001);add_port(p,"order.read",origin,{0,1,0});
    std::vector<Coordinate> hubs;for(int k=0;k<16;++k)hubs.push_back({30,30,1+2*k});
    for(int sign:{-1,1}){
        const std::string lane=sign<0?"left":"right";const auto comparison=move(origin,{sign,-1,0},10,n);p.sites["comparison."+lane]=comparison;
        for(int actual:{-1,1}){const Direction d{-actual,0,1};const auto port="need.actual."+lane+"."+std::to_string(actual);add_port(p,port,move(comparison,d,-4,n),d);p.ports["actual."+lane+"."+(actual<0?"minus":"plus")]=port;}
        for(int dx:{0,sign}){const auto branch=lane+(dx==0?".equal":".different");const auto request=move(comparison,{dx,-1,1},4,n);p.sites["question."+branch]=request;p.directions["comparison."+branch]={dx,-1,1};
            put(p,move(request,{0,1,-1},-19,n),1,13,1,0,"Prepared common request opportunity "+branch,{0,1,-1});}
        const auto hub=move(p.sites.at("question."+lane+".different"),{sign,0,0},51,n);hubs[sign<0?0:1]=hub;p.sites["bank."+lane]=hub;p.directions["request."+lane]={sign,0,0};
        for(int value:{-1,1}){
            const std::string label=value<0?"minus":"plus",code=lane+"."+label;const auto action=move(hub,{sign,value,0},2,n);
            if(!p.sites.count("action."+label)){p.sites["action."+label]=action;p.sites["action_input."+label]=move(action,{0,0,1},-3,n);add_port(p,"own.use."+label,p.sites.at("action_input."+label),{0,0,1});}
            else require(p.sites.at("action."+label)==action,"shared action resource no longer coincides");
            const auto anchor=move(action,{sign,value,1},3,n);const Direction cue{-sign,0,-1};p.sites["name."+code]=anchor;p.directions["name."+code]=cue;
            const auto teach="own.name.teach."+code,query="own.name.query."+code;add_port(p,teach,move(anchor,cue,-3,n),cue);add_port(p,query,move(anchor,{-1,0,0},-3,n),{-1,0,0});p.ports["name."+code+".teach"]=teach;p.ports["name."+code+".query"]=query;
        }
    }
    forms(p,hubs);
    if(o.guard_mode!="none"){
        int index=0;for(const auto& lane:{std::string("left"),std::string("right")})for(const auto& label:{std::string("minus"),std::string("plus")}){
            const auto key=lane+"."+label;auto q=move(p.sites.at("name."+key),p.directions.at("name."+key),8,n);if(o.guard_mode=="sham")q=move(q,{0,1,0},12,n);p.sites["guard."+std::to_string(index++)]=q;put(p,q,1,0,4,0,"Prepared stationary zero-load semantic4 interceptor unused_teaching_cue."+key+(o.guard_mode=="sham"?" offpath sham":""));}
        for(const auto& label:{std::string("minus"),std::string("plus")}){auto q=move(p.sites.at("action."+label),{0,0,1},8,n);if(o.guard_mode=="sham")q=move(q,{0,1,0},12,n);p.sites["guard."+std::to_string(index++)]=q;put(p,q,1,0,4,0,"Prepared stationary zero-load semantic4 interceptor unused_action_resource.own.use."+label+(o.guard_mode=="sham"?" offpath sham":""));}
    }
    if(o.revision_interfaces){const auto hub=p.forms[2].hub;p.sites["revision.hub"]=hub;p.sites["revision.sham_hub"]=move(hub,{0,0,1},55,n);
        for(const auto& mode:{std::string("treatment"),std::string("offpath_sham")})for(int sign:{-1,1}){const std::string label=sign<0?"minus":"plus";const Direction d{-1,sign,0};const auto target=mode=="treatment"?hub:p.sites.at("revision.sham_hub");const auto port="revision.second."+mode+"."+label;add_port(p,port,move(target,d,-3,n),d);p.ports["revision.teacher2."+mode+"."+label]=port;}}
    p.ticks={{"body_emission",5},{"actual_input",11},{"comparison",15},{"question",19},{"information",70},{"action_input",69},{"action",72},{"name_teach_input",72},{"association",75},{"name_query_input",139},{"name_read",142},{"second_acquisition",134},{"lower_query_1",201},{"lower_read_1",204},{"lower_query_2",335},{"lower_read_2",338},{"revision_input",402},{"revision_read",405},{"post_revision_query",469},{"post_revision_read",472},{"acquisition_path",3},{"query_path",3}};
    finish(p);return p;
}

NativePreparation preparation_for_world(const OrganizationalWorld& world){
    const auto& r=world.recipe();auto it=r.options.find(descriptor_key);std::string encoded;
    if(it!=r.options.end())encoded=it->second;else{const auto attached=world.runtime().snapshot_metadata(attached_key);require(attached.has_value(),"world has no consolidated descriptor; legacy physical load must remain explicit");encoded=*attached;}
    require(encoded.size()<=2U*1024U*1024U,"consolidated descriptor too large");std::istringstream s(encoded);std::string magic;NativePreparation p;int n{};
    s>>magic>>n>>std::quoted(p.kind)>>std::quoted(p.domain);require(magic=="CNATIVE1"&&n==world.runtime().dimension(),"invalid consolidated descriptor identity");
    require(p.kind=="repertoire.cpc5.v1"||p.kind=="integrated_u0.cpc7.v1","unsupported consolidated descriptor profile");
    auto count=[&](){std::size_t z{};s>>z;require(static_cast<bool>(s)&&z<=4096,"invalid consolidated descriptor count");return z;};
    auto coord=[&](){Coordinate q;s>>q.x>>q.y>>q.z;require(static_cast<bool>(s)&&q.x>=0&&q.x<n&&q.y>=0&&q.y<n&&q.z>=0&&q.z<n,"invalid descriptor coordinate");return q;};
    for(auto left=count();left--;){FormDescriptor f;s>>f.index>>std::quoted(f.name);f.hub=coord();require(f.index==p.forms.size()&&f.name==form_name(f.index),"invalid descriptor form index/name");p.forms.push_back(f);}
    for(auto left=count();left--;){std::string key;s>>std::quoted(key);auto q=coord();require(p.sites.emplace(key,q).second,"duplicate descriptor site");}
    for(auto left=count();left--;){std::string key;Direction d;s>>std::quoted(key)>>d.dx>>d.dy>>d.dz;require(d.dx>=-1&&d.dx<=1&&d.dy>=-1&&d.dy<=1&&d.dz>=-1&&d.dz<=1,"invalid descriptor direction");require(p.directions.emplace(key,d).second,"duplicate descriptor direction");}
    for(auto left=count();left--;){std::string key;std::uint64_t t{};s>>std::quoted(key)>>t;require(p.ticks.emplace(key,t).second,"duplicate descriptor tick");}
    for(auto left=count();left--;){std::string key,v;s>>std::quoted(key)>>std::quoted(v);require(p.ports.emplace(key,v).second,"duplicate descriptor port");}
    for(auto left=count();left--;){std::string key;std::int64_t v{};s>>std::quoted(key)>>v;require(p.parameters.emplace(key,v).second,"duplicate descriptor parameter");}
    require(static_cast<bool>(s),"truncated consolidated descriptor");s>>std::ws;require(s.eof(),"trailing consolidated descriptor bytes");
    require(!p.forms.empty()&&p.forms.size()<=65&&p.parameters.at("N")==n&&p.parameters.at("K")==static_cast<std::int64_t>(p.forms.size()),"inconsistent consolidated descriptor size");
    require(p.kind!="integrated_u0.cpc7.v1"||(n==67&&p.forms.size()==16),"inconsistent integrated descriptor domain");
    require(p.ticks.at("revision_input")==static_cast<std::uint64_t>(p.kind=="integrated_u0.cpc7.v1"?402:4*n),"inconsistent descriptor revision cadence");
    const auto declared=world.runtime().channel_names();const std::set<std::string> channel_names(declared.begin(),declared.end());
    for(const auto& [key,name]:p.ports){(void)key;require(channel_names.count(name)==1,"descriptor points to an absent channel");}
    for(const auto& f:p.forms)require(p.sites.at("form."+f.name)==f.hub,"descriptor form hub differs from its landmark");
    p.recipe=r;p.initial_state_available=false;return p;
}

void attach_preparation_descriptor(OrganizationalWorld& world,const NativePreparation& preparation){
    compatible(world,preparation);
    const auto& actual=world.recipe();const auto& expected=preparation.recipe;
    auto material=[](const auto& list){std::map<std::tuple<int,int,int>,std::pair<std::uint64_t,std::uint64_t>> out;for(const auto& q:list)require(out.emplace(std::make_tuple(q.site.x,q.site.y,q.site.z),std::make_pair(q.raw,q.clock)).second,"duplicate initial recipe placement");return out;};
    require(material(actual.placements)==material(expected.placements),"legacy initial physical preparation differs from descriptor");
    using Channel=std::tuple<int,int,int,std::uint32_t,int,int,int,std::uint8_t,bool,bool>;
    auto channels=[](const auto& list){std::map<std::string,Channel> out;for(const auto& v:list){const auto& q=v.channel;require(out.emplace(v.name,Channel{q.injection_site.x,q.injection_site.y,q.injection_site.z,q.state,q.direction.dx,q.direction.dy,q.direction.dz,q.semantic,q.allow_experience,q.allow_probe}).second,"duplicate initial interface");}return out;};
    require(channels(actual.interfaces)==channels(expected.interfaces),"legacy interfaces differ from descriptor");
    auto runtime_names=world.runtime().channel_names();std::set<std::string> wanted;for(const auto& i:expected.interfaces)wanted.insert(i.channel.name);
    require(std::set<std::string>(runtime_names.begin(),runtime_names.end())==wanted,"legacy Runtime channel set differs");
    const auto encoded=manifest(preparation);const auto native=actual.options.find(descriptor_key);
    if(native!=actual.options.end()){require(native->second==encoded,"native descriptor already exists with another geometry");return;}
    if(const auto prior=world.runtime().snapshot_metadata(attached_key))require(*prior==encoded,"an attached descriptor already exists with another geometry");
    world.runtime().set_snapshot_metadata(attached_key,encoded);
    world.runtime().set_snapshot_metadata("dee_thinking.consolidated.attach.provenance.v1","EXPLICIT_INERT_LEGACY_ATTACH; initial RAW/clocks and channels validated; live RAW/clocks/tick preserved; no preparation executed");
}

std::vector<EventReceipt> experience_form(OrganizationalWorld& w,const NativePreparation& p,std::size_t index,int sign,std::uint64_t tick,std::uint16_t cue,std::uint16_t event){
    compatible(w,p);sign_ok(sign);const auto& f=checked_form(p,index);const auto signal=f.name+".signal",current=f.name+".event."+(sign>0?"plus":"minus");
    preflight(w,p,{{signal,cue},{current,event}});return {w.submit(signal,cue,tick),w.submit(current,event,tick)};
}
EventReceipt query_form(OrganizationalWorld& w,const NativePreparation& p,std::size_t index,std::uint16_t value,std::uint64_t tick){compatible(w,p);const auto name=checked_form(p,index).name+".signal";preflight(w,p,{{name,value}});return w.probe(name,value,tick);}
std::vector<EventReceipt> revise_form(OrganizationalWorld& w,const NativePreparation& p,std::size_t index,int sign,std::uint64_t tick,const std::string& method,const std::string& mode,std::uint16_t cue,std::uint16_t event){
    compatible(w,p);sign_ok(sign);checked_form(p,index);require(p.parameters.at("revision_interfaces")==1,"revision interfaces not prepared");require(static_cast<std::int64_t>(index)==p.parameters.at("revision_form"),"revision targets a different initially declared form");
    require(method=="double_teacher"||method=="symmetric_counterflow","unknown revision method");require(mode=="treatment"||mode=="offpath_sham","unknown revision mode");require(tick==p.ticks.at("revision_input"),"revision outside published finite cadence");
    require(p.kind!="integrated_u0.cpc7.v1"||method=="double_teacher","symmetric counterflow is not integrated into U0");
    std::vector<PlannedInput> inputs;const std::string label=sign>0?"plus":"minus";const auto& f=checked_form(p,index);
    if(method=="symmetric_counterflow"){require(tick>=4,"counterflow tick underflow");for(const auto& v:{std::string("plus"),std::string("minus")})inputs.push_back({p.ports.at("revision.counter."+mode+"."+v),0});}
    inputs.push_back({f.name+".signal",cue});inputs.push_back({f.name+".event."+label,event});
    if(method=="double_teacher")inputs.push_back({p.ports.at("revision.teacher2."+mode+"."+label),event});
    preflight(w,p,inputs);std::vector<EventReceipt> out;
    for(std::size_t k=0;k<inputs.size();++k)out.push_back(w.submit(inputs[k].port,inputs[k].payload,method=="symmetric_counterflow"&&k<2?tick-4:tick));return out;
}
DirectionalReadout read_directional_response(const OrganizationalWorld& w,Coordinate q,std::uint64_t id,std::uint16_t load,std::optional<std::uint64_t> expected){
    DirectionalReadout out;out.physical=w.runtime().observe(q);out.receipt=w.runtime().receipt(id);const auto& r=out.physical.record;out.ordinary_cap_reached=r.s_reg==v27::kReducerCap;
    if(expected&&*expected!=out.physical.tick){out.status="OUTSIDE_REQUESTED_READ_TICK";return out;}
    if(!out.receipt){out.status="MISSING_RECEIPT";return out;}out.applied=out.receipt->status==EventStatus::Applied;
    if(!out.applied){out.status=to_string(out.receipt->status);return out;}
    if(r.state==0||r.semantic==5){out.status="NO_ACTIVE_RESPONSE";return out;}
    if(r.semantic!=1){out.status="OUTSIDE_DIRECTIONAL_SEMANTIC";return out;}
    if(r.s_reg<=load){out.status="PROBE_ONLY_OR_INSUFFICIENT_LOAD";return out;}
    if(r.dx!=-1||(r.dy!=-1&&r.dy!=1)||r.dz!=0){out.status="OUTSIDE_DIRECTIONAL_DECODER";return out;}
    out.covered=true;out.value=static_cast<int>(r.dy);out.status="MEASURED";return out;
}
DirectionalReadout read_form_response(const OrganizationalWorld& w,const NativePreparation& p,std::size_t index,std::uint64_t id,std::uint16_t load,std::optional<std::uint64_t> expected){
    compatible(w,p);const auto& f=checked_form(p,index);auto out=read_directional_response(w,f.hub,id,load,expected);
    if(out.receipt&&std::find(out.receipt->channels.begin(),out.receipt->channels.end(),f.name+".signal")==out.receipt->channels.end()){out.covered=false;out.value.reset();out.status="RECEIPT_FOR_DIFFERENT_INTERFACE";}return out;
}
} // namespace dee::thinking::consolidated
