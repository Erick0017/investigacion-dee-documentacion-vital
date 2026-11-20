#include <dee_thinking/cognitive.hpp>
#include <dee_thinking/informative.hpp>
#include <filesystem>
#include <iostream>
#include <stdexcept>
using namespace dee::thinking;
void require(bool b,const char* s){if(!b)throw std::runtime_error(s);}
int main(int argc,char** argv){try{
 if(argc<3)return 2;std::filesystem::path out=argv[2];std::filesystem::create_directories(out);
 CognitiveParameters p;p.seed_path=argv[1];p.profile="comparison";
 auto c=CognitiveSession::create(p);c.sense();auto prediction=c.predict();require(prediction.prediction.has_value(),"native forecast");
 c.save_snapshot((out/"pending.deetsnap").string());auto d=CognitiveSession::load_snapshot((out/"pending.deetsnap").string());
 auto a=c.compare(),b=d.compare();require(c.world().runtime().raw_copy()==d.world().runtime().raw_copy(),"continued RAW");require(c.world().runtime().clock_copy()==d.world().runtime().clock_copy(),"continued clocks");require(a.comparison->presentation=="discrepancia_direccional","physical comparison");
 auto association=NativeAssociationSession::create();association.train({7,11});auto response=association.query_panel();require(*response.decoded.at("q0")==25&&*response.decoded.at("q1")==29,"native acquired association");
 auto w=create_learnable_cascade(2);experience_composition(w,{{3,9},{3,11}});w.save_snapshot((out/"composition.deetsnap").string());auto restored=OrganizationalWorld::load_snapshot((out/"composition.deetsnap").string());auto y=query_composition(restored,13);require(*y.decoded.at("stage1")==39,"physical composed response");
 std::cout<<"DEE4 external C++: organization, transduction, observation, persistence, composition verified\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
