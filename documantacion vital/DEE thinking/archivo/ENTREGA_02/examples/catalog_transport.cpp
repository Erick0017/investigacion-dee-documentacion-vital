#include "dee_thinking/composition.hpp"

#include <iostream>

int main() {
    using namespace dee::thinking;
    using namespace dee::thinking::catalog;
    OrganizationCatalog catalog;
    CompositionPlanner planner(17);
    planner.add(catalog.instantiate(
        {"transport.axis.v1", "carrier_path", {2, 8, 8}, {{"distance", 5}, {"direction_code", 0}}}));
    auto world = planner.build();
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});
    if (world.experience("carrier_path", "carrier", 0, 7).status !=
        EventStatus::Scheduled) return 2;
    world.runtime().run_until(5);
    const auto record = world.runtime().observe(world.landmarks().at("carrier_path.arrival")).record;
    std::cout << "arrival_s_reg=" << record.s_reg << '\n';
    return record.s_reg == 7 ? 0 : 3;
}
