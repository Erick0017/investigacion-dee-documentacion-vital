#include "dee_thinking/composition.hpp"

#include <iostream>
#include <vector>

int main() {
    using namespace dee::thinking;
    using namespace dee::thinking::catalog;
    std::cout << "composition_a: catalog\n" << std::flush;
    OrganizationCatalog catalog;
    CompositionPlanner planner(127);
    const Coordinate anchor{63, 63, 63};
    planner.add(catalog.instantiate({"mobile_lineage.c7h03.v1", "lineage", anchor, {}}));
    planner.add(catalog.instantiate({"native_update_bridge.p01.v1", "bridge", anchor, {}}));
    planner.add(catalog.instantiate({"query_recurrence.p01.v1", "queries", anchor, {}}));
    planner.connect({{"bridge", "native_update"}, {"lineage", "update_input"}, "native update"});
    planner.connect({{"lineage", "updated_relation"}, {"queries", "updated_relation_input"}, "later use"});
    std::cout << "composition_a: build\n" << std::flush;
    auto world = planner.build();
    std::cout << "composition_a: configure\n" << std::flush;
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
    const std::vector<PortInputRequest> inputs{
        {"lineage", "cue", 4083}, {"lineage", "teacher", 19},
        {"bridge", "supply", 23}, {"bridge", "marker", 17},
        {"queries", "program_redirect", 0}, {"queries", "query1", 7},
        {"queries", "query2", 5}, {"queries", "query3", 3},
        {"queries", "query_redirect1", 0}, {"queries", "query_redirect2", 0}};
    std::cout << "composition_a: schedule\n" << std::flush;
    if (world.experience_batch(inputs, 0).status != EventStatus::Scheduled) return 2;
    std::cout << "composition_a: run\n" << std::flush;
    world.runtime().run_until(58);
    const auto response = world.runtime().observe(world.landmarks().at("queries.response3")).record;
    std::cout << "response3_s_reg=" << response.s_reg << " tick=" << world.runtime().current_tick() << '\n';
    return response.s_reg == 4157 ? 0 : 3;
}
