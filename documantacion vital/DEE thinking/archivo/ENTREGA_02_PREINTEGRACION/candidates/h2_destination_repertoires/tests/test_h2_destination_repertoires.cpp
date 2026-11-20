#include "h2_destination_repertoires_candidate.hpp"

#include <iostream>
#include <stdexcept>

using namespace dee::thinking::candidates::h2;

void require(bool value, const char* message) {
    if (!value) throw std::runtime_error(message);
}

template <typename Function>
void require_invalid(Function&& function, const char* message) {
    try {
        function();
    } catch (const std::invalid_argument&) {
        return;
    }
    throw std::runtime_error(message);
}

int main() {
    try {
        SeparatedConfig small;
        const auto dense = run_separated(small, {dee::v27::Backend::DenseSequential, 1});
        require(dense.ports_empty && dense.all_exact && dense.training_budget_exact &&
                    dense.read_budget_exact && dense.sreg_accounting_exact,
                "separated panel contract failed");
        const auto lazy = run_separated(small, {dee::v27::Backend::Lazy, 4});
        require(lazy.final_raw == dense.final_raw && lazy.final_clock == dense.final_clock,
                "separated Dense/Lazy mismatch");
        SeparatedConfig seven = small;
        seven.channels = 7;
        seven.translation = {11, 3, 13};
        const auto seven_result = run_separated(seven, {dee::v27::Backend::Lazy, 4});
        require(seven_result.ports_empty && seven_result.all_exact &&
                    seven_result.training_budget_exact && seven_result.read_budget_exact &&
                    seven_result.sreg_accounting_exact,
                "seven separated repertoires or resource accounting failed");
        OverlapConfig overlap;
        const auto merged = run_overlap(overlap);
        require(merged.port_empty && merged.merge_exact && merged.composed_response_exact &&
                    !merged.individual_identity,
                "overlap identity-loss contract failed");
        overlap.off_fiber = true;
        require(!run_overlap(overlap).false_merge, "off-fiber control produced false merge");
        SeparatedConfig saturated = small;
        saturated.base_offset = 20;
        require_invalid([&] { (void)run_separated(saturated); },
                        "underflow-prone separated configuration was accepted");
        OverlapConfig wrapped = overlap;
        wrapped.dimension = 41;
        require_invalid([&] { (void)run_overlap(wrapped); },
                        "self-wrapping overlap configuration was accepted");
        std::cout << "H2_CANDIDATE_PASS separated=3,7 budgets_exact=1 "
                     "overlap_identity_lost=1 off_fiber=1 dense_lazy_exact=1 domain_guards=2\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "H2_CANDIDATE_FAIL " << error.what() << '\n';
        return 1;
    }
}
