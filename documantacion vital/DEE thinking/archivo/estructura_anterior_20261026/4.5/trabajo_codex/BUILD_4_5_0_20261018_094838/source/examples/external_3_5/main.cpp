#include <dee_thinking/organizational.hpp>
#include <dee_thinking/version.hpp>
#include <iostream>
#include <stdexcept>
#include <string>
namespace dt=dee::thinking;
int main(int argc,char** argv) try {
    if(argc<3)throw std::invalid_argument("create SNAP | continue INPUT OUTPUT | bridge SEED OUTPUT");
    const std::string mode=argv[1];
    if(mode=="create"){
        auto w=dt::OrganizationalWorld::create(dt::OrganizationRecipe::mobile_pair());
        for(int j=0;j<2;++j){w.submit("l"+std::to_string(j)+".cue",5,0);w.submit("l"+std::to_string(j)+".teacher",j?11:7,0);}
        w.run_until(6);w.start_mobile_sequence("cross_language",{13,7,17});w.run_until(13);
        dt::OutputDecoder decoder;w.declare_decoder("load",decoder);
        dt::TraceSession trace;trace.sample_budget=16;trace.sites={{"q0",w.view("q0").spec().ports.at("response")}};w.set_trace(trace);w.capture_trace();w.save_snapshot(argv[2]);
        std::cout<<"version="<<dt::kProductVersion<<" tick="<<w.runtime().current_tick()<<" next="<<w.protocols().front().next_capture<<'\n';
    }else if(mode=="continue"){
        if(argc!=4)throw std::invalid_argument("continue INPUT OUTPUT");
        auto w=dt::OrganizationalWorld::load_snapshot(argv[2]);w.run_until(21);w.save_snapshot(argv[3]);
        for(const auto& step:w.protocols().front().steps){for(const auto& obs:step.captured)std::cout<<obs.record.s_reg<<' ';std::cout<<'\n';}
    }else if(mode=="bridge"){
        if(argc!=4)throw std::invalid_argument("bridge SEED OUTPUT");
        auto w=dt::OrganizationalWorld::create(dt::OrganizationRecipe::mobile_basal(argv[2]));w.advance(6);
        auto read=w.view("body").observe();std::cout<<"bridge delta="<<*read.delta<<" comparator="<<read.observations.at("comparator").record.s_reg<<'\n';
        auto f=w.fork();f.probe("body.common_query",7,f.runtime().current_tick());f.advance(3);w.save_snapshot(argv[3]);
        std::cout<<"probe dx="<<static_cast<int>(f.observe("body","comparator").record.dx)<<'\n';
    }else throw std::invalid_argument("unknown mode");
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
