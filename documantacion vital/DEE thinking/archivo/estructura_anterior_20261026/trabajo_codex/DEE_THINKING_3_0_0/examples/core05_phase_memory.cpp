#include "dee_thinking/composition.hpp"

#include <iostream>

int main() {
    using namespace dee::thinking;
    using namespace dee::thinking::catalog;

    OrganizationCatalog catalog;
    CompositionPlanner planner(17);
    planner.add(catalog.instantiate({
        "temporal_phase_memory.core05.v1", "memory", {1, 6, 13},
        {{"distance", 3}, {"permutation_code", 2}, {"sign_mask", 1},
         {"control_mode", 1}, {"source_index", 3},
         {"source0_sreg", 11}, {"source1_sreg", 13},
         {"source2_sreg", 17}, {"source3_sreg", 19}}}));
    auto world = planner.build();
    world.runtime().set_execution_options({dee::v27::Backend::Lazy, 4});

    std::cout << "constructor="
              << world.organizations().front().descriptor().constructor_version << '\n';
    for (int tick = 0; tick <= 15; ++tick) {
        const auto hub = world.runtime().observe(world.landmarks().at("memory.hub"));
        if (hub.raw != 0) {
            std::cout << "tick=" << tick << " hub_sreg=" << hub.record.s_reg
                      << " direction=(" << static_cast<int>(hub.record.dx) << ','
                      << static_cast<int>(hub.record.dy) << ','
                      << static_cast<int>(hub.record.dz) << ")\n";
        }
        if (tick != 15) world.runtime().advance();
    }
    return 0;
}
