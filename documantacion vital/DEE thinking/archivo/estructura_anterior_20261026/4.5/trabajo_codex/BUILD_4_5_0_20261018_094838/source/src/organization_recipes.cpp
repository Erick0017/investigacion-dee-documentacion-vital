#include "dee_thinking/organizational.hpp"
#include <algorithm>
#include <limits>
#include <set>
#include <stdexcept>

namespace dee::thinking {
namespace {
using namespace catalog;
Coordinate plus(Coordinate q, Direction d, std::int64_t k, int n) {
    auto wrap=[n](std::int64_t x){ auto r=x%n; return static_cast<int>(r<0?r+n:r); };
    return {wrap(q.x+d.dx*k),wrap(q.y+d.dy*k),wrap(q.z+d.dz*k)};
}
Coordinate translated(Coordinate q, Coordinate t, int n) { return plus(q,{t.x,t.y,t.z},1,n); }
std::int64_t param(const OrganizationRecipe& r,const std::string& name,std::int64_t fallback) {
    auto it=r.parameters.find(name);return it==r.parameters.end()?fallback:it->second;
}
std::string option(const OrganizationRecipe& r,const std::string& name,std::string fallback) {
    auto it=r.options.find(name);return it==r.options.end()?fallback:it->second;
}
void range(std::int64_t v,std::int64_t lo,std::int64_t hi,const char* name) {
    if(v<lo||v>hi)throw std::invalid_argument(std::string(name)+" outside recipe range");
}
OrganizationRecipe basic(std::string id,int n,Coordinate o={}) {
    OrganizationRecipe r;r.id=std::move(id);r.dimension=n;r.origin=o;
    r.domain="Finite reference geometry; custom parameters require measurement";return r;
}
OrganizationRequest req(std::string id,std::string inst,Coordinate q,std::map<std::string,std::int64_t> p={}) {
    return {std::move(id),std::move(inst),q,std::move(p)};
}
void link(CompositionPlanner& pl,std::string a,std::string ap,std::string b,std::string bp) {
    pl.connect({{std::move(a),std::move(ap)},{std::move(b),std::move(bp)},"native physical recipe route"});
}
void adopt(OrganizationRecipe& r,const ComposedWorld& world) {
    for(const auto& org:world.organizations()) {
        OrganizationSpec s;s.id=org.instance_id();s.recipe_id=org.descriptor().id;s.t0_tick=r.t0_tick;
        s.ports=org.landmarks();for(const auto& p:org.ports())s.ports.emplace(p.contract.name,p.absolute_site);
        for(const auto& f:org.initial_footprint())if(v27::decode_record(f.raw).semantic==4)
            s.supports.push_back(translated(org.anchor(),f.relative_site,r.dimension));
        if(s.recipe_id=="relative_history.i02.v1") {
            s.a=plus(org.anchor(),{-1,0,0},1,r.dimension);s.b=plus(org.anchor(),{1,0,0},1,r.dimension);s.comparator=org.anchor();
        }
        r.organizations.push_back(std::move(s));
        for(const auto& ch:org.channel_contracts()) {
            InterfaceSpec i;i.name=world.qualified_channel(org.instance_id(),ch.local_name);
            i.channel={i.name,translated(org.anchor(),ch.relative_site,r.dimension),ch.state,ch.direction,ch.semantic,ch.allow_experience,ch.allow_probe};
            // Runtime timing deliberately stays distinct from catalog port timing.
            r.interfaces.push_back(std::move(i));
        }
    }
}
void put(std::vector<std::uint64_t>& raw,std::vector<std::uint64_t>& clk,int n,Coordinate q,
         std::uint16_t load,Direction d,std::uint32_t state=1,std::uint8_t sem=1,std::uint64_t clock=0) {
    const auto i=v27::linear_index(q.x,q.y,q.z,n);
    if(raw[i]!=0)throw std::invalid_argument("recipe preparation overlaps a nonzero record");
    raw[i]=v27::pack_record(state,load,d.dx,d.dy,d.dz,sem);clk[i]=clock;
}
void collision(std::vector<std::uint64_t>& raw,std::vector<std::uint64_t>& clk,int n,Coordinate hub,
               Direction d,int time,std::uint16_t cue,std::uint16_t teacher) {
    const Direction q{-1,0,0},e{1,d.dy,d.dz};
    put(raw,clk,n,plus(hub,q,-time,n),cue,q);put(raw,clk,n,plus(hub,e,-time,n),teacher,e);
}
void interface(OrganizationRecipe& r,std::string name,Coordinate site,Direction dir,std::uint32_t state=1,std::uint8_t sem=1) {
    InterfaceSpec i;i.name=name;i.channel={name,site,state,dir,sem,true,true};r.interfaces.push_back(std::move(i));
}
void body_view(OrganizationRecipe& r,const basal::Ports& p) {
    OrganizationSpec s;s.id="body";s.recipe_id=r.id;s.t0_tick=r.t0_tick;s.a=p.a;s.b=p.b;s.comparator=p.comparator;
    s.supports=p.supports;s.ports={{"A",p.a},{"B",p.b},{"comparator",p.comparator},{"reader_source",p.reader_source}};
    if(p.action_site)s.ports["action"]=*p.action_site;
    if(p.bend_site)s.ports["environment"]=*p.bend_site;
    if(p.return_site)s.ports["return"]=*p.return_site;
    r.organizations.push_back(std::move(s));
    interface(r,"body.common_query",plus(r.origin,{0,-1,0},1,r.dimension),{0,1,0},6000,5);
    if(p.action_site && p.bend_site && p.return_site)
        r.actions.push_back({"body.environment",{*p.action_site,*p.bend_site,*p.return_site},{"action","environment","return"},{r.t0_tick+8,r.t0_tick+13,r.t0_tick+14}});
}
basal::History history(const OrganizationRecipe& r) {
    auto h=param(r,"history",1);range(h,1,5,"history");return static_cast<basal::History>(h);
}
} // namespace

OrganizationRecipe OrganizationRecipe::mobile_pair(Coordinate t){return basic("mobile_pair.v1",34,t);}
OrganizationRecipe OrganizationRecipe::cascade(int d,Coordinate t){auto r=basic("cascade.v1",127,t);r.parameters["depth"]=d;return r;}
OrganizationRecipe OrganizationRecipe::phase(int m,Coordinate o){auto r=basic("phase.v1",31,o);r.parameters["mode"]=m;return r;}
OrganizationRecipe OrganizationRecipe::distributed(int h,Coordinate o){auto r=basic("distributed.v1",127,o);r.parameters["history_mode"]=h;return r;}
OrganizationRecipe OrganizationRecipe::relational(std::string seed,basal::History h,bool keep,Coordinate o){
    auto r=basic("relational.v1",47,o);r.options["seed"]=std::move(seed);r.parameters["history"]=static_cast<int>(h);r.parameters["keep_reader"]=keep;r.t0_tick=32;return r;
}
OrganizationRecipe OrganizationRecipe::contextual(std::string s,Coordinate o){auto r=relational(std::move(s),basal::History::AB,true,o);r.id="contextual.v1";return r;}
OrganizationRecipe OrganizationRecipe::mobile_basal(std::string s,basal::History h,Coordinate o){auto r=relational(std::move(s),h,false,o);r.id="mobile_basal.v1";return r;}
OrganizationRecipe OrganizationRecipe::native_transfer(Coordinate t){auto r=cascade(2,t);r.id="native_transfer.v1";return r;}
OrganizationRecipe OrganizationRecipe::contingent(std::string s,Coordinate o){auto r=relational(std::move(s),basal::History::AB,true,o);r.id="contingent.v1";return r;}
OrganizationRecipe OrganizationRecipe::information(std::string s,basal::History h,std::uint16_t hidden,Coordinate o){auto r=relational(std::move(s),h,true,o);r.id="information.v1";r.parameters["hidden"]=hidden;return r;}
OrganizationRecipe OrganizationRecipe::competition(Coordinate t){return basic("competition.v1",34,t);}
OrganizationRecipe OrganizationRecipe::predictive(Coordinate t){return basic("predictive.v1",34,t);}
OrganizationRecipe OrganizationRecipe::research(int n,std::vector<InitialPlacement> p,std::uint64_t t){auto r=basic("research.v1",n);r.placements=std::move(p);r.t0_tick=t;return r;}

// Internal entry point shared by the C++ world and Python binding. All builders
// port the effective physical recipes, not the handlers' expected readouts.
Runtime prepare_organizational_recipe(OrganizationRecipe& r) {
    if(r.version!="1.0.0")throw std::invalid_argument("unsupported recipe version");
    if(r.execution.threads==0)throw std::invalid_argument("threads must be positive");
    std::set<std::string> keys, options;
    if(r.id=="mobile_pair.v1")for(int j=0;j<2;++j)for(auto axis:{"x","y","z"})keys.insert("anchor"+std::to_string(j)+"_"+axis);
    else if(r.id=="phase.v1") {
        keys={"mode","distance","permutation","signs","source_index"};
        for(int j=0;j<4;++j){keys.insert("source"+std::to_string(j)+"_clock_high");keys.insert("source"+std::to_string(j)+"_clock_low");}
    } else if(r.id=="distributed.v1")keys={"history_mode","with_history","with_recurrence"};
    else if(r.id=="relational.v1"||r.id=="contextual.v1"||r.id=="mobile_basal.v1"||r.id=="contingent.v1"||r.id=="information.v1"){
        keys={"history","keep_reader","control"};options={"seed"};
        if(r.id=="mobile_basal.v1")keys.insert({"mobile_only","body_only","offpath","paired"});
        if(r.id=="information.v1")keys.insert({"informative_side","hidden","extra_receiver"});
        if(r.id=="contingent.v1")keys.insert({"independent","inverse"});
    } else if(r.id=="cascade.v1"||r.id=="native_transfer.v1"){
        keys={"depth","omit","source_absent"};for(int j=0;j<8;++j){keys.insert("cue"+std::to_string(j));keys.insert("teacher"+std::to_string(j));}
    } else if(r.id=="competition.v1"){keys={"shift","second_y","second_z"};options={"arm","destination"};}
    else if(r.id=="predictive.v1")keys={"sign","consequence_tick","naive","paired","consequence"};
    else if(r.id!="research.v1")throw std::invalid_argument("unknown organizational recipe");
    if(r.id!="research.v1"){
        for(const auto& [key,value]:r.parameters){(void)value;if(!keys.contains(key))throw std::invalid_argument("unknown recipe parameter: "+key);}
        for(const auto& [key,value]:r.options){(void)value;if(!options.contains(key))throw std::invalid_argument("unknown recipe option: "+key);}
        for(const auto& key:{"keep_reader","with_history","with_recurrence","mobile_only","body_only","offpath","paired","extra_receiver","independent","inverse","source_absent","naive","consequence"}){
            auto it=r.parameters.find(key);if(it!=r.parameters.end())range(it->second,0,1,key);
        }
    }
    Runtime checked(r.dimension); // performs size/overflow validation before allocating recipes
    std::vector<std::uint64_t> raw,clk;
    auto blank=[&]{raw=checked.raw_copy();clk=checked.clock_copy();};
    if(r.id=="mobile_pair.v1" || r.id=="phase.v1" || r.id=="distributed.v1") {
        const int expected=r.id=="mobile_pair.v1"?34:r.id=="phase.v1"?31:127;
        if(r.dimension!=expected)throw std::invalid_argument("catalog recipe dimension outside published domain");
        OrganizationCatalog cat;CompositionPlanner pl(r.dimension);
        if(r.id=="mobile_pair.v1") {
            for(int j=0;j<2;++j) {
                Coordinate anchor=translated({10,10,j==0?8:24},r.origin,34);
                // Individually configurable anchors are research preparation, not answers.
                for(auto [axis,target]:std::vector<std::pair<std::string,int*>>{{"x",&anchor.x},{"y",&anchor.y},{"z",&anchor.z}}) {
                    auto it=r.parameters.find("anchor"+std::to_string(j)+"_"+axis);
                    if(it!=r.parameters.end()){range(it->second,0,33,"anchor");*target=static_cast<int>(it->second);}
                }
                const auto l="l"+std::to_string(j),q="q"+std::to_string(j);
                pl.add(cat.instantiate(req("relation_learning.c6h01.v1",l,anchor)));
                pl.add(cat.instantiate(req("relation_query.c6h01.v1",q,plus(anchor,{0,1,0},8,34))));
                link(pl,l,"learned_relation",q,"relation_input");
            }
        } else if(r.id=="phase.v1") {
            const auto mode=param(r,"mode",0);range(mode,0,2,"mode");
            std::map<std::string,std::int64_t> p{{"control_mode",mode},{"distance",param(r,"distance",4)},
                {"permutation_code",param(r,"permutation",0)},{"sign_mask",param(r,"signs",0)},{"source_index",param(r,"source_index",3)}};
            for(int j=0;j<4;++j)for(const char* part:{"high","low"}) {
                auto key="source"+std::to_string(j)+"_clock_"+part;
                if(r.parameters.count(key))p[key]=r.parameters.at(key);
            }
            pl.add(cat.instantiate(req("temporal_phase_memory.core05.v1","phase",r.origin,p)));
        } else {
            auto h=param(r,"history_mode",1);range(h,0,2,"history_mode");
            pl.add(cat.instantiate(req("distributed_context.i05.v1","context",r.origin)));
            if(param(r,"with_history",1)) {
                pl.add(cat.instantiate(req("relative_history.i02.v1","history",r.origin,{{"history_mode",h}})));
                link(pl,"context","context_output","history","context");
            }
            if(param(r,"with_recurrence",1)) {
                pl.add(cat.instantiate(req("contextual_multichannel_recurrence.p02.v1","integration",r.origin)));
                link(pl,param(r,"with_history",1)?"history":"context",param(r,"with_history",1)?"history_state":"context_output","integration","context_input");
            }
        }
        auto w=pl.build();adopt(r,w);auto rt=w.runtime().fork();rt.set_execution_options(r.execution);
        if(r.id=="phase.v1") {
            const auto source=w.landmarks().at("phase.installed_source3");const auto mouth=w.landmarks().at("phase.mouth3");
            const auto sr=rt.observe(source).record;
            // In source-absent controls the direction belongs to the frozen
            // declared geometry, not to an inferred output.
            auto fallback=cat.instantiate(req("temporal_phase_memory.core05.v1","geometry",r.origin,{{"control_mode",0},{"distance",param(r,"distance",4)},{"permutation_code",param(r,"permutation",0)},{"sign_mask",param(r,"signs",0)},{"source_index",3}}));
            Direction d{sr.dx,sr.dy,sr.dz};if(d.dx==0&&d.dy==0&&d.dz==0) {
                for(const auto& f:fallback.initial_footprint())if(translated(fallback.anchor(),f.relative_site,r.dimension)==source){auto x=v27::decode_record(f.raw);d={x.dx,x.dy,x.dz};break;}
            }
            auto target=plus(mouth,d,1,r.dimension);r.organizations[0].ports["access_response"]=target;
            interface(r,"phase.access_query",plus(target,{-1,0,0},-2,r.dimension),{-1,0,0});
        }
        if(r.id=="distributed.v1"&&param(r,"with_history",1))interface(r,"history.common_query",plus(r.origin,{0,-1,0},1,127),{0,1,0},6000,5);
        if(!r.placements.empty()) {
            std::vector<ResearchStateEdit> edits;std::set<std::size_t> seen;
            for(const auto& p:r.placements) { auto i=v27::linear_index(p.site.x,p.site.y,p.site.z,r.dimension);if(rt.observe(p.site).raw!=0||!seen.insert(i).second)throw std::invalid_argument("custom placement overlaps catalog preparation");edits.push_back({p.site,p.raw,p.clock,"declared pre-T0 catalog extension"}); }
            rt=rt.diagnostic_fork(edits,true);
        }
        return rt;
    }
    if(r.id=="relational.v1"||r.id=="contextual.v1"||r.id=="mobile_basal.v1"||r.id=="contingent.v1"||r.id=="information.v1") {
        if(r.dimension!=47||r.t0_tick!=32)throw std::invalid_argument("basal research recipe requires N47 and seed tick32");
        auto cfg=basal::Config::relational_reference(option(r,"seed",""));cfg.history=history(r);cfg.origin=r.origin;
        cfg.execution=r.execution;cfg.domain_mode=basal::DomainMode::Research;
        cfg.control=param(r,"keep_reader",0)?basal::Control::Bare:basal::Control::ReadCut;
        if(r.id=="contextual.v1") {cfg.preset=basal::Preset::ContextualRewrite;cfg.control=basal::Control::Full;}
        if(r.id=="contingent.v1")cfg.control=basal::Control::Full;
        auto requested_control=param(r,"control",0);
        if(requested_control){range(requested_control,1,8,"control");cfg.control=static_cast<basal::Control>(requested_control);}
        auto w=basal::World::create(cfg);raw=w.runtime().raw_copy();clk=w.runtime().clock_copy();
        if(cfg.control==basal::Control::ReadCut)for(const auto q:w.ports().environmental_sources)raw[v27::linear_index(q.x,q.y,q.z,47)]=0;
        body_view(r,w.ports());
        if(r.id=="mobile_basal.v1") {
            if(param(r,"mobile_only",0)){std::fill(raw.begin(),raw.end(),0);std::fill(clk.begin(),clk.end(),0);}
            auto hub=plus(r.origin,{0,-1,0},3,47);if(param(r,"offpath",0))hub=plus(hub,{0,0,1},6,47);
            if(!param(r,"body_only",0)) {
                if(param(r,"paired",1))collision(raw,clk,47,hub,{0,1,0},3,5,7);
                else {
                    // Install only actual sources. A site never installed must
                    // retain the seed's empty-site clock, not be cleared to zero.
                    put(raw,clk,47,plus(hub,{-1,0,0},-3,47),5,{-1,0,0});
                    put(raw,clk,47,plus(hub,{1,1,0},-4,47),7,{1,1,0});
                }
            }
            OrganizationSpec s;s.id="mobile";s.recipe_id="c6.native.v1";s.t0_tick=32;s.ports={{"hub",hub},{"arrival",r.origin}};r.organizations.push_back(s);
        }
        if(r.id=="information.v1") {
            const auto side=param(r,"informative_side",1);if(side!=-1&&side!=1)throw std::invalid_argument("informative_side must be +/-1");
            auto action=plus(r.origin,{static_cast<int>(side),1,0},5,47);Direction hd{-static_cast<int>(side),0,1};
            auto source=plus(action,hd,-8,47);auto hidden=param(r,"hidden",23);range(hidden,0,65535,"hidden");put(raw,clk,47,source,static_cast<std::uint16_t>(hidden),hd);
            const auto response=plus(action,{0,1,1},8,47);
            if(param(r,"extra_receiver",1))put(raw,clk,47,plus(response,{-1,0,0},-16,47),13,{-1,0,0});
            r.organizations[0].ports["conditional"]=action;r.organizations[0].ports["downstream"]=response;
            r.actions.push_back({"conditional",{action,response},{"native encounter","downstream use"},{40,48}});
        }
        if(r.id=="contingent.v1"&&(param(r,"independent",0)||param(r,"inverse",0))) {
            const auto bend=*w.ports().bend_site;Direction d=param(r,"inverse",0)?Direction{1,1,-1}:Direction{-1,-1,-1};
            if(param(r,"independent",0)) {
                for(auto q:w.ports().environmental_sources)raw[v27::linear_index(q.x,q.y,q.z,47)]=0;
                put(raw,clk,47,plus(bend,d,-13,47),48,d);
            } else {
                auto q=plus(bend,{-1,-1,-1},-13,47);auto i=v27::linear_index(q.x,q.y,q.z,47);auto old=v27::decode_record(raw[i]);raw[i]=0;
                // Previous diagnostic move preserves clocks at both locations.
                auto dest=plus(bend,d,-13,47);auto j=v27::linear_index(dest.x,dest.y,dest.z,47);if(raw[j])throw std::invalid_argument("inverse environment overlap");
                raw[j]=v27::pack_record(old.state,old.s_reg,d.dx,d.dy,d.dz,old.semantic);
            }
        }
    } else {
        blank();const int n=r.dimension;
        if(r.id=="cascade.v1"||r.id=="native_transfer.v1") {
            if(n!=127)throw std::invalid_argument("cascade requires N127");const auto depth=param(r,"depth",4);range(depth,1,8,"depth");
            if(r.id=="native_transfer.v1"&&depth!=2)throw std::invalid_argument("published native relay requires depth two");
            range(param(r,"omit",r.id=="native_transfer.v1"?1:-1),-1,depth-1,"omit");
            auto h0=translated({40,30,30},r.origin,n),first=plus(h0,{0,1,0},8,n);
            for(int j=0;j<depth;++j) {
                const int t=11+5*j;auto meet=plus(first,{-1,1,0},5*j,n),hub=plus(meet,{0,1,0},-(t-3),n);
                auto cue=param(r,"cue"+std::to_string(j),r.id=="native_transfer.v1"?5:3);
                auto teacher=param(r,"teacher"+std::to_string(j),r.id=="native_transfer.v1"?7:9+2*j);
                range(cue,0,65535,"cue");range(teacher,0,65535,"teacher");
                auto omit=param(r,"omit",r.id=="native_transfer.v1"?1:-1);
                if(j!=omit&&!param(r,"source_absent",0))collision(raw,clk,n,hub,{0,1,0},3,static_cast<std::uint16_t>(cue),static_cast<std::uint16_t>(teacher));
                OrganizationSpec s;s.id="stage"+std::to_string(j);s.recipe_id="c6.cascade.stage.v1";s.ports={{"hub",hub},{"response",meet}};r.organizations.push_back(s);
            }
            interface(r,"query",plus(first,{-1,0,0},-5,n),{-1,0,0});
            if(r.id=="native_transfer.v1") {
                auto target=plus(first,{-1,1,0},10,n);interface(r,"receiver_query",plus(target,{-1,0,0},-5,n),{-1,0,0});
                r.organizations[0].ports["receiver_response"]=target;
            }
        } else if(r.id=="competition.v1") {
            if(n!=34)throw std::invalid_argument("competition requires N34");auto meet=translated({12,16,15},r.origin,n);
            const auto shift=param(r,"shift",0);range(shift,-1,1,"shift");Direction bd{0,static_cast<int>(param(r,"second_y",0)),static_cast<int>(param(r,"second_z",1))};
            if(bd.dy < -1||bd.dy>1||bd.dz < -1||bd.dz>1||(bd.dy==0&&bd.dz==0))throw std::invalid_argument("second direction outside encounter family");
            auto h1=plus(meet,{0,1,0},-3,n),h2=plus(meet,bd,-3-shift,n);auto arm=option(r,"arm","both");
            if(arm!="both"&&arm!="A_only"&&arm!="B_only")throw std::invalid_argument("unknown competition arm");
            if(arm!="both"&&arm!="A_only"&&arm!="B_only")throw std::invalid_argument("unknown encounter arm");
            if(arm!="B_only")collision(raw,clk,n,h1,{0,1,0},3,5,7);if(arm!="A_only")collision(raw,clk,n,h2,bd,3,9,15);
            auto dst=option(r,"destination","empty");
            if(dst!="empty"&&dst!="material"&&dst!="protected")throw std::invalid_argument("unknown destination preparation");
            if(dst!="empty") {
                if(dst!="material"&&dst!="protected")throw std::invalid_argument("unknown destination policy");
                put(raw,clk,n,meet,100,{0,0,0},1000,dst=="protected"?4:1,1);
                if(dst=="material") {
                    const std::array<Direction,4> ds{{{-1,0,0},{-1,1,1},{0,0,1},{0,1,0}}};int j=0;
                    for(auto d:ds){put(raw,clk,n,plus(meet,d,1,n),0,{0,0,0},3000+j,4,31+j);++j;}
                }
            }
            auto final=plus(meet,{0,1,1},4,n);interface(r,"joint_query",plus(final,{-1,0,0},-4,n),{-1,0,0});
            OrganizationSpec s;s.id="encounter";s.recipe_id=r.id;s.ports={{"meeting",meet},{"hubA",h1},{"hubB",h2},{"response",final}};r.organizations.push_back(s);
            auto target=plus(final,{-1,1,1},10,n);interface(r,"later_query",plus(target,{0,0,-1},-6,n),{0,0,-1});r.organizations[0].ports["later_response"]=target;
        } else if(r.id=="predictive.v1") {
            if(n!=34)throw std::invalid_argument("predictive requires N34");const auto sign=param(r,"sign",1);if(sign!=1&&sign!=-1)throw std::invalid_argument("sign +/-1 required");
            const auto delay=param(r,"consequence_tick",18);range(delay,18,100,"consequence horizon");auto hub=translated({10,15,14},r.origin,n);
            if(!param(r,"naive",0)) {
                collision(raw,clk,n,hub,{0,static_cast<int>(sign),0},3,5,7);
                if(!param(r,"paired",1)) {auto q=plus(hub,{1,static_cast<int>(sign),0},-3,n),p=plus(q,{1,static_cast<int>(sign),0},-1,n);auto i=v27::linear_index(q.x,q.y,q.z,n),j=v27::linear_index(p.x,p.y,p.z,n);if(raw[j])throw std::invalid_argument("unpaired overlap");raw[j]=raw[i];clk[j]=clk[i];raw[i]=0;clk[i]=0;}
            }
            const Direction route{-1,static_cast<int>(sign),0};auto dst=plus(hub,{0,static_cast<int>(sign),0},8,n),op=plus(dst,route,3,n),future=plus(dst,route,delay-11,n);
            if(param(r,"consequence",1))put(raw,clk,n,plus(future,{1,-static_cast<int>(sign),0},-delay,n),23,{1,-static_cast<int>(sign),0});
            for(int j=0;j<2;++j)interface(r,"signal"+std::to_string(j),plus(plus(hub,{0,j==0?1:-1,0},8,n),{-1,0,0},-5,n),{-1,0,0});
            OrganizationSpec s;s.id="predictive";s.recipe_id=r.id;s.ports={{"hub",hub},{"response",dst},{"opportunity",op},{"consequence",future}};r.organizations.push_back(s);
        } else if(r.id!="research.v1")throw std::invalid_argument("unknown organization recipe");
    }
    std::set<std::size_t> declared;
    for(const auto& p:r.placements) {
        auto i=v27::linear_index(p.site.x,p.site.y,p.site.z,r.dimension);
        if(raw[i]!=0||!declared.insert(i).second)throw std::invalid_argument("custom placement overlap (even a declared zero)");
        const auto rec=v27::decode_record(p.raw);(void)rec;raw[i]=p.raw;clk[i]=p.clock;
    }
    auto rt=Runtime::import_research_state(r.dimension,r.t0_tick,std::move(raw),std::move(clk));rt.set_execution_options(r.execution);
    return rt;
}
} // namespace dee::thinking
