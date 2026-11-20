#include "dee_thinking/cognitive.hpp"
#include <iostream>
using namespace dee::thinking;
// Usage: native_cognitive_demo reference_seed.deetsnap pending.deetsnap
int main(int argc,char** argv){
    if(argc!=3){std::cerr<<"usage: native_cognitive_demo seed snapshot\n";return 2;}
    CognitiveParameters p;p.seed_path=argv[1];p.profile="comparison";
    auto session=CognitiveSession::create(p);auto acquired=session.sense();auto emission=session.predict();
    session.set_interface_metadata("display_name","external_barrier_example");session.save_snapshot(argv[2]);
    auto restored=CognitiveSession::load_snapshot(argv[2]);auto compared=restored.compare();
    std::cout<<"native acquisition tick "<<acquired.tick<<", emission "<<emission.prediction->emission_tick
             <<", target "<<emission.prediction->target_tick<<", measured native marker "
             <<compared.comparison->presentation<<" at "<<compared.tick<<'\n';
    auto relations=NativeAssociationSession::create();relations.train({7,11});auto response=relations.query_panel();
    for(auto [name,value]:response.decoded)std::cout<<name<<": "<<(value?std::to_string(*value):"unavailable")<<'\n';
    auto cascade=create_learnable_cascade(2);experience_composition(cascade,{{3,9},{3,11}});auto composed=query_composition(cascade,13);
    for(auto [name,value]:composed.decoded)std::cout<<name<<": "<<(value?std::to_string(*value):"unavailable")<<'\n';
    return 0;
}
