#include "dee_thinking/composition.hpp"

#include <iostream>

int main() {
    using namespace dee::thinking;
    using namespace dee::thinking::catalog;
    std::cout << "composition_b: catalog\n" << std::flush;
    OrganizationCatalog catalog;
    CompositionPlanner planner(127);
    const Coordinate anchor{30, 30, 30};
    planner.add(catalog.instantiate({"distributed_context.i05.v1", "context", anchor, {}}));
    planner.add(catalog.instantiate({"relative_history.i02.v1", "history", anchor, {{"history_mode", 1}}}));
    planner.add(catalog.instantiate({"contextual_multichannel_recurrence.p02.v1", "integration", anchor, {}}));
    planner.connect({{"context", "context_output"}, {"history", "context"}, "distributed history"});
    planner.connect({{"history", "history_state"}, {"integration", "context_input"}, "condition recurrence"});
    std::cout << "composition_b: build\n" << std::flush;
    auto world = planner.build();
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
    std::cout << "composition_b: schedule\n" << std::flush;
    const auto event = world.experience_batch(
        {{"integration", "A", 8}, {"integration", "B", 9}}, 0);
    if (event.status != EventStatus::Scheduled) return 2;
    std::cout << "composition_b: run\n" << std::flush;
    world.runtime().run_until(12);
    const auto response = world.runtime().observe(world.landmarks().at("integration.q")).record;
    std::cout << "q_s_reg=" << response.s_reg << " tick=" << world.runtime().current_tick() << '\n';
    return response.s_reg == 391 ? 0 : 3;
}
