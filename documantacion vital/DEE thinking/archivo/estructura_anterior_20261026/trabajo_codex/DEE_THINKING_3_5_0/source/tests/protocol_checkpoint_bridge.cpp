#include "dee_thinking/integrated_protocols.hpp"

#include <array>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

using namespace dee::thinking::protocols;

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

int run(const std::string& mode, const std::string& path) {
    const dee::v27::TickOptions lazy{dee::v27::Backend::Lazy, 2};
    if (mode == "save-h1") {
        DelayPositionConfig config;
        config.input_delay = 3;
        save_delay_position_checkpoint(config, 5, path, lazy);
        std::cout << "cpp_save_h1 tick=5\n";
        return 0;
    }
    if (mode == "resume-h1") {
        DelayPositionConfig config;
        config.input_delay = 3;
        const auto resumed = resume_delay_position_checkpoint(path, lazy);
        const auto uninterrupted = run_delay_position(config, lazy);
        require(resumed.measurement == uninterrupted.measurement &&
                    resumed.active_labels == uninterrupted.active_labels &&
                    resumed.merged_events.size() ==
                        uninterrupted.merged_events.size(),
                "H1 resumed functional result differs");
        require(resumed.final_raw == uninterrupted.final_raw,
                "H1 resumed RAW differs from uninterrupted trajectory");
        require(resumed.final_clock == uninterrupted.final_clock,
                "H1 resumed clock differs from uninterrupted trajectory");
        std::cout << "cpp_resume_h1 exact_state=true measurement=3\n";
        return 0;
    }
    if (mode == "save-h2-separated") {
        save_separated_repertoire_checkpoint(
            SeparatedRepertoireConfig{}, 10, path, lazy);
        std::cout << "cpp_save_h2_separated tick=10\n";
        return 0;
    }
    if (mode == "resume-h2-separated") {
        const auto resumed =
            resume_separated_repertoire_checkpoint(path, lazy);
        const auto uninterrupted =
            run_separated_repertoire(SeparatedRepertoireConfig{}, lazy);
        require(resumed.all_exact == uninterrupted.all_exact &&
                    resumed.exact_channels == uninterrupted.exact_channels &&
                    resumed.training_budget_exact ==
                        uninterrupted.training_budget_exact &&
                    resumed.read_budget_exact ==
                        uninterrupted.read_budget_exact &&
                    resumed.load_accounting_exact ==
                        uninterrupted.load_accounting_exact &&
                    resumed.observed_responses ==
                        uninterrupted.observed_responses,
                "H2 separated resumed functional result differs");
        require(resumed.final_raw == uninterrupted.final_raw,
                "H2 separated resumed RAW differs from uninterrupted trajectory");
        require(resumed.final_clock == uninterrupted.final_clock,
                "H2 separated resumed clock differs from uninterrupted trajectory");
        std::cout << "cpp_resume_h2_separated exact_state=true channels=3\n";
        return 0;
    }
    if (mode == "save-h2-overlap") {
        save_overlap_repertoire_checkpoint(
            OverlapRepertoireConfig{}, 16, path, lazy);
        std::cout << "cpp_save_h2_overlap tick=16\n";
        return 0;
    }
    if (mode == "resume-h2-overlap") {
        const auto resumed = resume_overlap_repertoire_checkpoint(path, lazy);
        const auto uninterrupted =
            run_overlap_repertoire(OverlapRepertoireConfig{}, lazy);
        require(resumed.merge_exact == uninterrupted.merge_exact &&
                    resumed.composed_response_exact ==
                        uninterrupted.composed_response_exact &&
                    resumed.individual_identity_preserved ==
                        uninterrupted.individual_identity_preserved &&
                    resumed.false_merge == uninterrupted.false_merge &&
                    resumed.observed_merge_load ==
                        uninterrupted.observed_merge_load &&
                    resumed.observed_response_load ==
                        uninterrupted.observed_response_load,
                "H2 overlap resumed functional result differs");
        require(resumed.final_raw == uninterrupted.final_raw,
                "H2 overlap resumed RAW differs from uninterrupted trajectory");
        require(resumed.final_clock == uninterrupted.final_clock,
                "H2 overlap resumed clock differs from uninterrupted trajectory");
        std::cout << "cpp_resume_h2_overlap exact_state=true merge=true\n";
        return 0;
    }
    if (mode == "save-h3") {
        RepairConfig config;
        config.authorize_diagnostic_damage = true;
        save_trained_redundancy_repair_checkpoint(config, 62, path, lazy);
        std::cout << "cpp_save_h3 tick=62\n";
        return 0;
    }
    if (mode == "resume-h3") {
        RepairConfig config;
        config.authorize_diagnostic_damage = true;
        const auto resumed =
            resume_trained_redundancy_repair_checkpoint(path, lazy);
        const auto uninterrupted =
            run_trained_redundancy_repair(config, lazy);
        require(resumed.final_raw == uninterrupted.final_raw,
                "H3 resumed RAW differs from uninterrupted trajectory");
        require(resumed.final_clock == uninterrupted.final_clock,
                "H3 resumed clock differs from uninterrupted trajectory");
        require(resumed.backup_learned == uninterrupted.backup_learned &&
                    resumed.damage_applied == uninterrupted.damage_applied &&
                    resumed.function_lost_after_damage ==
                        uninterrupted.function_lost_after_damage &&
                    resumed.reconstructed_at_arrival ==
                        uninterrupted.reconstructed_at_arrival &&
                    resumed.fresh_function == uninterrupted.fresh_function &&
                    resumed.query_load == uninterrupted.query_load &&
                    resumed.query_direction.dx ==
                        uninterrupted.query_direction.dx &&
                    resumed.query_direction.dy ==
                        uninterrupted.query_direction.dy &&
                    resumed.query_direction.dz ==
                        uninterrupted.query_direction.dz,
                "H3 resumed functional result differs");
        std::cout << "cpp_resume_h3 exact_state=true fresh_function="
                  << resumed.fresh_function << '\n';
        return 0;
    }
    if (mode == "save-f1") {
        save_reusable_revision_checkpoint(ReusableRevisionConfig{}, 40, path, lazy);
        std::cout << "cpp_save_f1 tick=40\n";
        return 0;
    }
    if (mode == "resume-f1") {
        const auto resumed = resume_reusable_revision_checkpoint(path, lazy);
        const auto uninterrupted =
            run_reusable_revision(ReusableRevisionConfig{}, lazy);
        require(resumed.response_loads == std::array<std::uint16_t, 3>{4149, 4165, 4181},
                "F1 resumed response differs");
        require(resumed.response_loads == uninterrupted.response_loads &&
                    resumed.post_revision_loads ==
                        uninterrupted.post_revision_loads &&
                    resumed.all_inputs_applied_at_t0 ==
                        uninterrupted.all_inputs_applied_at_t0 &&
                    resumed.backend_fallback == uninterrupted.backend_fallback,
                "F1 resumed functional result differs");
        require(resumed.final_raw == uninterrupted.final_raw,
                "F1 resumed RAW differs from uninterrupted trajectory");
        require(resumed.final_clock == uninterrupted.final_clock,
                "F1 resumed clock differs from uninterrupted trajectory");
        std::cout << "cpp_resume_f1 exact_state=true responses=4149,4165,4181\n";
        return 0;
    }
    if (mode == "save-f2") {
        save_environmental_return_checkpoint(EnvironmentalReturnConfig{}, 40, path, lazy);
        std::cout << "cpp_save_f2 tick=40\n";
        return 0;
    }
    if (mode == "resume-f2") {
        const auto resumed = resume_environmental_return_checkpoint(path, lazy);
        const auto uninterrupted =
            run_environmental_return(EnvironmentalReturnConfig{}, lazy);
        require(resumed.downstream_loads ==
                    std::array<std::uint16_t, 5>{24, 55, 62, 62, 67},
                "F2 resumed response differs");
        require(resumed.overflow_total > 0,
                "F2 resumed path has no overflow event");
        require(resumed.upstream_response_load ==
                        uninterrupted.upstream_response_load &&
                    resumed.environment_load == uninterrupted.environment_load &&
                    resumed.downstream_loads == uninterrupted.downstream_loads &&
                    resumed.overflow_total == uninterrupted.overflow_total &&
                    resumed.query_admitted == uninterrupted.query_admitted &&
                    resumed.all_inputs_applied_at_t0 ==
                        uninterrupted.all_inputs_applied_at_t0 &&
                    resumed.backend_fallback == uninterrupted.backend_fallback,
                "F2 resumed functional result differs");
        require(resumed.final_raw == uninterrupted.final_raw,
                "F2 resumed RAW differs from uninterrupted trajectory");
        require(resumed.final_clock == uninterrupted.final_clock,
                "F2 resumed clock differs from uninterrupted trajectory");
        std::cout << "cpp_resume_f2 exact_state=true downstream=24,55,62,62,67\n";
        return 0;
    }
    throw std::invalid_argument("unknown protocol bridge mode");
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: dee_protocol_checkpoint_bridge "
                         "save-h1|resume-h1|"
                         "save-h2-separated|resume-h2-separated|"
                         "save-h2-overlap|resume-h2-overlap|"
                         "save-h3|resume-h3|save-f1|resume-f1|"
                         "save-f2|resume-f2 PATH\n";
            return 2;
        }
        return run(argv[1], argv[2]);
    } catch (const std::exception& error) {
        std::cerr << "protocol checkpoint bridge error: " << error.what() << '\n';
        return 1;
    }
}
