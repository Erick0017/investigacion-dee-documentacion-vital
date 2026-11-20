#include "dee_thinking/composition.hpp"

#include <iostream>

int main() {
    using namespace dee::thinking;
    using namespace dee::thinking::catalog;
    OrganizationCatalog catalog;
    CompositionPlanner planner(34);
    planner.add(catalog.instantiate({"relation_learning.c6h01.v1", "learner", {10, 18, 14}, {}}));
    planner.add(catalog.instantiate({"relation_query.c6h01.v1", "reader", {10, 26, 14}, {}}));
    planner.connect({{"learner", "learned_relation"}, {"reader", "relation_input"}, "later query"});
    auto world = planner.build();
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
    if (world.experience_batch(
            {{"learner", "cue", 5}, {"learner", "teacher", 7}}, 0).status != EventStatus::Scheduled) return 2;
    world.runtime().run_until(6);
    if (world.probe("reader", "query", 6, 13).status !=
        EventStatus::Scheduled) return 3;
    world.runtime().run_until(11);
    const auto response = world.runtime().observe(world.landmarks().at("reader.response")).record;
    std::cout << "response_s_reg=" << response.s_reg << '\n';
    return response.s_reg == 25 ? 0 : 4;
}
