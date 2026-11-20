#include <dee_thinking/consolidated.hpp>
#include <dee_thinking/cognitive.hpp>
#include <dee_thinking/version.hpp>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

namespace dt=dee::thinking;
namespace api=dee::thinking::consolidated;

void require(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
void same_physical(const dt::OrganizationalWorld& a,const dt::OrganizationalWorld& b){
    require(a.runtime().current_tick()==b.runtime().current_tick(),"tick differs");
    require(a.runtime().raw_copy()==b.runtime().raw_copy(),"RAW differs");
    require(a.runtime().clock_copy()==b.runtime().clock_copy(),"clock differs");
}

int main(int argc,char** argv){
    try{
        require(argc==2,"Provide a NEW output directory");
        auto output=std::filesystem::absolute(argv[1]);
        require(!std::filesystem::exists(output),"Refusing to overwrite existing consumer output");
        std::filesystem::create_directories(output);
        require(std::string(dt::kProductVersion)=="4.5.0","wrong library version");
        require(dee::v27::kKernelModulus==19665,"wrong kernel identity");
        api::RepertoireOptions options;options.forms=2;options.dimension=67;options.plane_gap=2;
        auto preparation=api::prepare_repertoire(options);
        auto world=preparation.create_world();
        require(world.runtime().current_tick()==0,"Preparation advanced the world");
        auto left=api::experience_form(world,preparation,0,+1,0);
        auto right=api::experience_form(world,preparation,1,-1,0);
        require(left.size()==2&&right.size()==2,"experience receipt contract");
        world.run_until(3);
        dt::InputCodec codec;codec.minimum=0;codec.maximum=65535;
        const auto input=codec.encode_integer(9);
        auto q0=api::query_form(world,preparation,0,input,67);
        auto q1=api::query_form(world,preparation,1,input,67);
        world.run_until(67);
        const auto pending=(output/"pending67.deetsnap").string();
        world.save_snapshot(pending);
        auto restored=dt::OrganizationalWorld::load_snapshot(pending);
        auto descriptor=api::preparation_for_world(restored);
        require(descriptor.forms.size()==2,"descriptor-only restoration lost forms");
        same_physical(world,restored);
        world.run_until(70);restored.run_until(70);same_physical(world,restored);
        auto first=api::read_form_response(restored,descriptor,0,q0.id,input,70);
        auto second=api::read_form_response(restored,descriptor,1,q1.id,input,70);
        require(first.applied&&first.covered&&first.value==+1,"first acquired response");
        require(second.applied&&second.covered&&second.value==-1,"second acquired response");
        const auto raw=restored.runtime().raw_copy(),clocks=restored.runtime().clock_copy();
        (void)api::read_form_response(restored,descriptor,0,q0.id,input,70);
        require(raw==restored.runtime().raw_copy()&&clocks==restored.runtime().clock_copy(),"passive read mutated world");
        restored.save_snapshot((output/"continued70.deetsnap").string());
        // A legacy native composed mechanism is still online, not a table.
        auto cascade=dt::create_learnable_cascade(2);
        const auto exposures=dt::experience_composition(cascade,{{3,9},{3,11}});
        require(exposures.size()==4,"composed experience contract");
        cascade.run_until(6);
        auto response=dt::query_composition(cascade,13);
        require(cascade.runtime().current_tick()==16,"composed query horizon");
        require(response.decoded.at("stage0")==25&&response.decoded.at("stage1")==39,"composed response differs");
        cascade.save_snapshot((output/"composed16.deetsnap").string());
        std::cout<<"{\"status\":\"PASS\",\"version\":\"4.5.0\",\"kernel\":27,"
                 <<"\"new_native_repertoire\":true,\"input_codec\":true,\"pending_snapshot_continuation\":true,"
                 <<"\"passive_observation\":true,\"legacy_native_composition\":true}"<<std::endl;
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}
}
