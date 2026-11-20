#include "dee_thinking/integrated_protocols.hpp"

#include <iostream>

int main() {
    using namespace dee::thinking::protocols;

    std::cout << "Integrated DEE thinking protocols:\n";
    for (const auto& descriptor : integrated_protocol_descriptors()) {
        std::cout << "- " << descriptor.id << " v" << descriptor.version
                  << " [" << to_string(descriptor.modality) << "]\n";
    }

    DelayPositionConfig delay;
    delay.input_delay = 3;
    const auto measurement = run_delay_position(
        delay, {dee::v27::Backend::Lazy, 4});
    if (!measurement.measurement) {
        std::cerr << "H1 did not produce its bounded measurement\n";
        return 2;
    }
    std::cout << "H1 delay " << delay.input_delay << " selected label "
              << *measurement.measurement << '\n';

    AccessibilityRequest diagnostic;
    diagnostic.observer_id = "example.fixed.sreg";
    diagnostic.challenge_id = "example.challenge";
    AccessibilityCase a;
    a.history_id = "history-A";
    a.baseline_tick = a.challenged_tick = 12;
    a.history_status = AccessibilityStatus::Reached;
    a.history_reached_natively = true;
    a.baseline = {{{1, 1, 1},
                   dee::v27::pack_record(1, 10, 1, 0, 0, 1), 12}};
    a.challenged = {{{1, 1, 1},
                     dee::v27::pack_record(1, 15, 1, 0, 0, 1), 12}};
    auto b = a;
    b.history_id = "history-B";
    b.challenged[0].raw =
        dee::v27::pack_record(1, 12, 1, 0, 0, 1);
    diagnostic.cases = {a, b};
    const auto access = analyze_accessibility(diagnostic);
    std::cout << "H4 comparable=" << access.comparable
              << " history_conditioned="
              << access.history_conditioned_response << '\n';
    return access.comparable && access.history_conditioned_response ? 0 : 3;
}
