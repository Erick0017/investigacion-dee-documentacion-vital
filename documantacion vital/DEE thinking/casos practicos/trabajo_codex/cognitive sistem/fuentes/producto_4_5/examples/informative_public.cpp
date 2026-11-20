#include "dee_thinking/informative.hpp"
#include <filesystem>
#include <iostream>
#include <stdexcept>

namespace d=dee::thinking;
void check(bool value,const char* what){if(!value)throw std::runtime_error(what);}
int main(int argc,char** argv){
    try{
        if(argc<3)throw std::invalid_argument("usage: informative_public seed.deetsnap output_directory");
        const std::filesystem::path output=argv[2];std::filesystem::create_directories(output);
        for(auto roles:{d::SourceRole::PInformative,d::SourceRole::QInformative}){
            d::FinitePolicyParameters parameters;parameters.roles=roles;
            auto session=d::FinitePolicySession::create(parameters);session.run_until(2);session.process_boundary();session.set_interface_metadata("external_alias","source");
            auto path=(output/(roles==d::SourceRole::PInformative?"policy_p.deetsnap":"policy_q.deetsnap")).string();session.save_snapshot(path);auto copy=d::FinitePolicySession::load_snapshot(path);
            check(copy.world().runtime().raw_copy()==session.world().runtime().raw_copy(),"policy restore RAW");check(copy.get_interface_metadata("external_alias")=="source","policy UI metadata");
            auto a=session.run_until(14),b=copy.run_until(14);check(a.information.size()==1&&b.information.size()==1,"unique current information");check(a.information[0].value==1,"actual report from physical record");check(a.information[0].source==(roles==d::SourceRole::PInformative?"P":"Q"),"experience-dependent native source");check(copy.world().runtime().clock_copy()==session.world().runtime().clock_copy(),"policy continued clocks");
        }
        d::NativeInformationParameters p;p.seed_path=argv[1];p.history=d::basal::History::BA;
        auto info=d::NativeInformationSession::create(p);info.run_until(43);info.process_boundary();auto path=(output/"information_pending.deetsnap").string();info.save_snapshot(path);auto restored=d::NativeInformationSession::load_snapshot(path);auto a=info.run_until(64),b=restored.run_until(64);
        check(info.world().runtime().raw_copy()==restored.world().runtime().raw_copy(),"information continued RAW");check(info.world().runtime().clock_copy()==restored.world().runtime().clock_copy(),"information continued clocks");check(!a.later_responses.empty()&&!b.later_responses.empty(),"native information is physically used later");bool load67=false;for(const auto& x:a.later_responses)if(x.value==67)load67=true;check(load67,"native later response reference");
        std::cout<<"informative C++ public operations and integral persistence verified\n";return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
