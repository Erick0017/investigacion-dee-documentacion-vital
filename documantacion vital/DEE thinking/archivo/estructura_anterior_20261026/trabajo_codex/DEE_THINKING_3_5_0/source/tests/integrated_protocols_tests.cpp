#include "dee_thinking/integrated_protocols.hpp"
#include "test_support.hpp"

#include <array>
#include <filesystem>
#include <string>

using namespace dee::thinking;
using namespace dee::thinking::protocols;

namespace {

std::filesystem::path checkpoint(const char* name) {
    return std::filesystem::temp_directory_path() / name;
}

void remove_if_present(const std::filesystem::path& path) {
    std::error_code ignored;
    std::filesystem::remove(path, ignored);
}

void replace_with_incompatible_protocol_version(
    const std::filesystem::path& path) {
    auto snapshot = Runtime::load_snapshot(path.string());
    snapshot.set_snapshot_metadata("protocol.version", "999.0.0");
    snapshot.save_snapshot(path.string());
}

}  // namespace

int main() {
    dee::thinking::test::Suite suite("integrated_protocols_tests");
    const dee::v27::TickOptions lazy{dee::v27::Backend::Lazy, 4};

    const auto& descriptors = integrated_protocol_descriptors();
    DEE_CHECK_EQ(suite, descriptors.size(), std::size_t{6});
    for (const auto* id : {kH1Id, kH2Id, kH3Id, kH4Id, kF1Id, kF2Id}) {
        const auto* descriptor = find_integrated_protocol(id);
        DEE_CHECK(suite, descriptor != nullptr);
        DEE_CHECK_EQ(suite, descriptor->version, std::string("1.0.0"));
        DEE_CHECK(suite, !descriptor->tested_domain.empty());
        DEE_CHECK(suite, !descriptor->limits.empty());
        DEE_CHECK(suite, !descriptor->ports.empty());
    }
    DEE_CHECK(suite, find_integrated_protocol("fanout.general") == nullptr);

    DelayPositionConfig h1;
    h1.input_delay = 3;
    const auto h1_native = run_delay_position(h1, lazy);
    DEE_CHECK(suite, h1_native.initial_hubs_empty);
    DEE_CHECK(suite, h1_native.measurement.has_value());
    DEE_CHECK_EQ(suite, *h1_native.measurement, 3);
    // The public H1 contract advertises the complete calibrated bank -5..5.
    // Freeze every published native label rather than inferring the range from
    // the single historical delay used by the persistence fixture below.
    for (int delay = -5; delay <= 5; ++delay) {
        auto domain_case = h1;
        domain_case.input_delay = delay;
        const auto domain_result = run_delay_position(domain_case, lazy);
        DEE_CHECK(suite, domain_result.initial_hubs_empty);
        DEE_CHECK(suite, domain_result.measurement.has_value());
        DEE_CHECK_EQ(suite, *domain_result.measurement, delay);
        DEE_CHECK_EQ(suite, domain_result.active_labels,
                     std::vector<int>{delay});
        DEE_CHECK_EQ(suite, domain_result.merged_events.size(), std::size_t{1});
    }
    const auto h1_dense = run_delay_position(
        h1, {dee::v27::Backend::DenseSequential, 1});
    DEE_CHECK_EQ(suite, h1_dense.final_raw, h1_native.final_raw);
    DEE_CHECK_EQ(suite, h1_dense.final_clock, h1_native.final_clock);
    h1.arm = DelayPositionArm::ReversedCalibration;
    const auto h1_reversed = run_delay_position(h1, lazy);
    DEE_CHECK(suite, h1_reversed.measurement.has_value());
    DEE_CHECK_EQ(suite, *h1_reversed.measurement, -3);
    h1.arm = DelayPositionArm::TargetAbsent;
    const auto h1_absent = run_delay_position(h1, lazy);
    DEE_CHECK(suite, !h1_absent.measurement.has_value());
    h1.arm = DelayPositionArm::Native;
    const auto h1_path = checkpoint("dee_thinking_h1_integration.deetsnap");
    remove_if_present(h1_path);
    save_delay_position_checkpoint(h1, 5, h1_path.string(), lazy);
    const auto h1_resumed = resume_delay_position_checkpoint(h1_path.string(), lazy);
    DEE_CHECK_EQ(suite, h1_resumed.final_raw, h1_native.final_raw);
    DEE_CHECK_EQ(suite, h1_resumed.final_clock, h1_native.final_clock);
    DEE_CHECK_EQ(suite, h1_resumed.measurement, h1_native.measurement);
    replace_with_incompatible_protocol_version(h1_path);
    DEE_CHECK_THROWS(suite, resume_delay_position_checkpoint(h1_path.string(), lazy));
    remove_if_present(h1_path);
    auto invalid_h1_frame = h1;
    invalid_h1_frame.bank_axis = invalid_h1_frame.target_direction;
    DEE_CHECK_THROWS(suite, run_delay_position(invalid_h1_frame, lazy));

    SeparatedRepertoireConfig separated;
    separated.channels = 3;
    const auto h2_k3 = run_separated_repertoire(separated, lazy);
    DEE_CHECK(suite, h2_k3.all_exact);
    DEE_CHECK(suite, h2_k3.training_budget_exact);
    DEE_CHECK(suite, h2_k3.read_budget_exact);
    DEE_CHECK(suite, h2_k3.load_accounting_exact);
    const auto h2_k3_dense = run_separated_repertoire(
        separated, {dee::v27::Backend::DenseSequential, 1});
    DEE_CHECK_EQ(suite, h2_k3_dense.final_raw, h2_k3.final_raw);
    DEE_CHECK_EQ(suite, h2_k3_dense.final_clock, h2_k3.final_clock);
    separated.channels = 7;
    const auto h2_k7 = run_separated_repertoire(separated, lazy);
    DEE_CHECK_EQ(suite, h2_k7.exact_channels, std::size_t{7});
    DEE_CHECK(suite, h2_k7.all_exact);
    DEE_CHECK(suite, h2_k7.training_budget_exact);
    DEE_CHECK(suite, h2_k7.read_budget_exact);
    DEE_CHECK(suite, h2_k7.load_accounting_exact);
    DEE_CHECK_EQ(suite, h2_k7.observed_responses.size(), std::size_t{7});
    separated.channels = 3;
    const auto h2_sep_path = checkpoint("dee_thinking_h2_separated.deetsnap");
    remove_if_present(h2_sep_path);
    save_separated_repertoire_checkpoint(separated, 10, h2_sep_path.string(), lazy);
    const auto h2_sep_resumed = resume_separated_repertoire_checkpoint(h2_sep_path.string(), lazy);
    DEE_CHECK_EQ(suite, h2_sep_resumed.final_raw, h2_k3.final_raw);
    DEE_CHECK_EQ(suite, h2_sep_resumed.final_clock, h2_k3.final_clock);
    replace_with_incompatible_protocol_version(h2_sep_path);
    DEE_CHECK_THROWS(suite, resume_separated_repertoire_checkpoint(h2_sep_path.string(), lazy));
    remove_if_present(h2_sep_path);

    OverlapRepertoireConfig overlap;
    const auto h2_overlap = run_overlap_repertoire(overlap, lazy);
    DEE_CHECK(suite, h2_overlap.merge_exact);
    DEE_CHECK(suite, h2_overlap.composed_response_exact);
    DEE_CHECK(suite, !h2_overlap.individual_identity_preserved);
    const auto h2_overlap_dense = run_overlap_repertoire(
        overlap, {dee::v27::Backend::DenseSequential, 1});
    DEE_CHECK_EQ(suite, h2_overlap_dense.final_raw, h2_overlap.final_raw);
    DEE_CHECK_EQ(suite, h2_overlap_dense.final_clock, h2_overlap.final_clock);
    auto off_fiber = overlap;
    off_fiber.off_fiber = true;
    const auto h2_off = run_overlap_repertoire(off_fiber, lazy);
    DEE_CHECK(suite, !h2_off.false_merge);
    const auto h2_overlap_path = checkpoint("dee_thinking_h2_overlap.deetsnap");
    remove_if_present(h2_overlap_path);
    save_overlap_repertoire_checkpoint(overlap, 16, h2_overlap_path.string(), lazy);
    const auto h2_overlap_resumed = resume_overlap_repertoire_checkpoint(h2_overlap_path.string(), lazy);
    DEE_CHECK_EQ(suite, h2_overlap_resumed.final_raw, h2_overlap.final_raw);
    DEE_CHECK_EQ(suite, h2_overlap_resumed.final_clock, h2_overlap.final_clock);
    DEE_CHECK_EQ(suite, h2_overlap_resumed.merge_exact,
                 h2_overlap.merge_exact);
    DEE_CHECK_EQ(suite, h2_overlap_resumed.composed_response_exact,
                 h2_overlap.composed_response_exact);
    DEE_CHECK_EQ(suite, h2_overlap_resumed.observed_merge_load,
                 h2_overlap.observed_merge_load);
    DEE_CHECK_EQ(suite, h2_overlap_resumed.observed_response_load,
                 h2_overlap.observed_response_load);
    replace_with_incompatible_protocol_version(h2_overlap_path);
    DEE_CHECK_THROWS(suite, resume_overlap_repertoire_checkpoint(h2_overlap_path.string(), lazy));
    remove_if_present(h2_overlap_path);

    RepairConfig repair;
    repair.authorize_diagnostic_damage = true;
    const std::array<RepairGeometry, 2> repair_geometries{{
        repair.geometry,
        {"fresh_like_01", 31, 6, 6, {0, 1, 2}, {1, 1, -1}, {15, 15, 15}},
    }};
    const std::array<RepairArm, 7> repair_arms{{
        RepairArm::Treatment, RepairArm::BackupUntrained,
        RepairArm::BackupDirectionReset, RepairArm::NoBackup,
        RepairArm::PathCut, RepairArm::OffpathCut, RepairArm::WrongReceiver,
    }};
    RepairResult h3_treatment;
    for (std::size_t geometry_index = 0;
         geometry_index < repair_geometries.size(); ++geometry_index) {
        for (const auto arm : repair_arms) {
            RepairConfig current;
            current.geometry = repair_geometries[geometry_index];
            current.arm = arm;
            current.authorize_diagnostic_damage = true;
            const auto lazy_result =
                run_trained_redundancy_repair(current, lazy);
            const auto dense_result = run_trained_redundancy_repair(
                current, {dee::v27::Backend::DenseSequential, 1});
            DEE_CHECK_EQ(suite, dense_result.final_raw, lazy_result.final_raw);
            DEE_CHECK_EQ(suite, dense_result.final_clock, lazy_result.final_clock);
            const bool expected_function = arm == RepairArm::Treatment ||
                                           arm == RepairArm::OffpathCut;
            DEE_CHECK_EQ(suite, lazy_result.fresh_function, expected_function);
            if (geometry_index == 0 && arm == RepairArm::Treatment) {
                h3_treatment = lazy_result;
                DEE_CHECK(suite, h3_treatment.backup_learned);
                DEE_CHECK(suite, h3_treatment.damage_applied);
                DEE_CHECK(suite, h3_treatment.reconstructed_at_arrival);
            }
        }
    }
    auto no_authorization = repair;
    no_authorization.authorize_diagnostic_damage = false;
    DEE_CHECK_THROWS(suite, run_trained_redundancy_repair(no_authorization, lazy));
    auto invalid_repair_geometry = repair;
    invalid_repair_geometry.geometry.id = "invented";
    DEE_CHECK_THROWS(suite, run_trained_redundancy_repair(invalid_repair_geometry, lazy));
    auto invalid_repair_arm = repair;
    invalid_repair_arm.arm = static_cast<RepairArm>(99);
    DEE_CHECK_THROWS(suite, run_trained_redundancy_repair(invalid_repair_arm, lazy));
    const auto h3_path = checkpoint("dee_thinking_h3_repair.deetsnap");
    remove_if_present(h3_path);
    save_trained_redundancy_repair_checkpoint(repair, 62, h3_path.string(), lazy);
    const auto h3_resumed = resume_trained_redundancy_repair_checkpoint(h3_path.string(), lazy);
    DEE_CHECK_EQ(suite, h3_resumed.final_raw, h3_treatment.final_raw);
    DEE_CHECK_EQ(suite, h3_resumed.final_clock, h3_treatment.final_clock);
    DEE_CHECK_EQ(suite, h3_resumed.fresh_function, h3_treatment.fresh_function);
    replace_with_incompatible_protocol_version(h3_path);
    DEE_CHECK_THROWS(suite, resume_trained_redundancy_repair_checkpoint(h3_path.string(), lazy));
    remove_if_present(h3_path);

    AccessibilityRequest access;
    access.observer_id = "fixed.two_site.sreg";
    access.challenge_id = "fixed.challenge.v1";
    AccessibilityCase history_a;
    history_a.history_id = "A";
    history_a.baseline_tick = history_a.challenged_tick = 20;
    history_a.history_status = AccessibilityStatus::Reached;
    history_a.history_reached_natively = true;
    history_a.baseline = {{{1, 2, 3}, dee::v27::pack_record(1, 10, 1, 0, 0, 1), 20}};
    history_a.challenged = {{{1, 2, 3}, dee::v27::pack_record(1, 15, 1, 0, 0, 1), 20}};
    auto history_b = history_a;
    history_b.history_id = "B";
    history_b.challenged[0].raw = dee::v27::pack_record(1, 12, 1, 0, 0, 1);
    access.cases = {history_a, history_b};
    const auto h4 = analyze_accessibility(access);
    DEE_CHECK(suite, h4.comparable);
    DEE_CHECK(suite, h4.history_conditioned_response);
    DEE_CHECK_EQ(suite, h4.effects[0].s_reg_deltas[0], 5);
    DEE_CHECK_EQ(suite, h4.effects[1].s_reg_deltas[0], 2);
    auto bad_access = access;
    bad_access.ages_aligned = false;
    DEE_CHECK(suite, !analyze_accessibility(bad_access).comparable);

    const std::array<ReusableRevisionConfig, 6> f1_configs{{
        {"REV_11_13", 11, 13, 0, 0, true},
        {"REV_13_11", 13, 11, 0, 0, true},
        {"FIRST_ONLY_11", 11, 0, 0, 13, true},
        {"SECOND_ONLY_13", 0, 13, 11, 0, true},
        {"SHAM_11_13", 0, 0, 11, 13, true},
        {"NO_TRAINED_RELATION", 11, 13, 0, 0, false},
    }};
    const std::array<std::array<std::uint16_t, 3>, 6> f1_expected{{
        {4149, 4165, 4181}, {4149, 4167, 4181}, {4149, 4165, 4168},
        {4149, 4154, 4170}, {4149, 4154, 4157}, {7, 5, 3},
    }};
    ReusableRevisionResult f1_reference;
    for (std::size_t i = 0; i < f1_configs.size(); ++i) {
        const auto result = run_reusable_revision(f1_configs[i], lazy);
        DEE_CHECK_EQ(suite, result.response_loads, f1_expected[i]);
        DEE_CHECK(suite, result.all_inputs_applied_at_t0);
        DEE_CHECK(suite, !result.backend_fallback);
        if (i == 0) f1_reference = result;
    }
    const auto f1_dense = run_reusable_revision(
        f1_configs[0], {dee::v27::Backend::DenseParallel, 4});
    DEE_CHECK_EQ(suite, f1_dense.final_raw, f1_reference.final_raw);
    DEE_CHECK_EQ(suite, f1_dense.final_clock, f1_reference.final_clock);
    const auto f1_path = checkpoint("dee_thinking_f1_revision.deetsnap");
    remove_if_present(f1_path);
    save_reusable_revision_checkpoint(f1_configs[0], 40, f1_path.string(), lazy);
    const auto f1_resumed = resume_reusable_revision_checkpoint(f1_path.string(), lazy);
    DEE_CHECK_EQ(suite, f1_resumed.final_raw, f1_reference.final_raw);
    DEE_CHECK_EQ(suite, f1_resumed.final_clock, f1_reference.final_clock);
    DEE_CHECK_EQ(suite, f1_resumed.response_loads, f1_reference.response_loads);
    replace_with_incompatible_protocol_version(f1_path);
    DEE_CHECK_THROWS(suite, resume_reusable_revision_checkpoint(f1_path.string(), lazy));
    remove_if_present(f1_path);

    const std::array<EnvironmentalReturnConfig, 6> f2_configs{{
        {"ENV_INTACT", true, 15515, 17, EnvironmentalQueryMode::Intact, 353},
        {"ENV_RESPONSE_CUT", false, 15515, 17, EnvironmentalQueryMode::Intact, 353},
        {"ENV_NO_QUERY", true, 15515, 17, EnvironmentalQueryMode::Absent, 353},
        {"ENV_QUERY_SHAM", true, 15515, 17, EnvironmentalQueryMode::Sham, 353},
        {"ENV_SUBTHRESHOLD", true, 15514, 17, EnvironmentalQueryMode::Intact, 353},
        {"ENV_CONTENT_19", true, 15515, 19, EnvironmentalQueryMode::Intact, 353},
    }};
    const std::array<std::array<std::uint16_t, 5>, 6> f2_expected{{
        {24, 55, 62, 62, 67}, {23, 54, 61, 61, 66},
        {0, 31, 7, 0, 5}, {0, 31, 7, 0, 5},
        {23, 54, 61, 61, 66}, {24, 55, 62, 62, 67},
    }};
    const std::array<std::uint16_t, 6> f2_environment_expected{{
        19664, 15515, 19664, 19664, 19663, 19664,
    }};
    const std::array<std::uint64_t, 6> f2_overflow_expected{{
        1, 0, 1, 1, 0, 1,
    }};
    const std::array<bool, 6> f2_query_admitted_expected{{
        true, true, false, true, true, true,
    }};
    EnvironmentalReturnResult f2_reference;
    for (std::size_t i = 0; i < f2_configs.size(); ++i) {
        const auto result = run_environmental_return(f2_configs[i], lazy);
        DEE_CHECK_EQ(suite, result.downstream_loads, f2_expected[i]);
        DEE_CHECK_EQ(suite, result.environment_load, f2_environment_expected[i]);
        DEE_CHECK_EQ(suite, result.overflow_total, f2_overflow_expected[i]);
        DEE_CHECK_EQ(suite, result.query_admitted,
                     f2_query_admitted_expected[i]);
        DEE_CHECK(suite, result.all_inputs_applied_at_t0);
        DEE_CHECK(suite, !result.backend_fallback);
        if (i == 0) {
            DEE_CHECK_EQ(suite, result.overflow_total, std::uint64_t{1});
            DEE_CHECK_EQ(suite, result.upstream_response_load,
                         std::uint16_t{4149});
            f2_reference = result;
        }
        if (i == 5) {
            DEE_CHECK_EQ(suite, result.upstream_response_load,
                         std::uint16_t{4151});
            DEE_CHECK_EQ(suite, result.downstream_loads[4],
                         f2_reference.downstream_loads[4]);
        }
    }
    const auto f2_dense = run_environmental_return(
        f2_configs[0], {dee::v27::Backend::DenseParallel, 4});
    DEE_CHECK_EQ(suite, f2_dense.final_raw, f2_reference.final_raw);
    DEE_CHECK_EQ(suite, f2_dense.final_clock, f2_reference.final_clock);
    const auto f2_path = checkpoint("dee_thinking_f2_environment.deetsnap");
    remove_if_present(f2_path);
    save_environmental_return_checkpoint(f2_configs[0], 40, f2_path.string(), lazy);
    const auto f2_resumed = resume_environmental_return_checkpoint(f2_path.string(), lazy);
    DEE_CHECK_EQ(suite, f2_resumed.final_raw, f2_reference.final_raw);
    DEE_CHECK_EQ(suite, f2_resumed.final_clock, f2_reference.final_clock);
    DEE_CHECK_EQ(suite, f2_resumed.downstream_loads, f2_reference.downstream_loads);
    DEE_CHECK_EQ(suite, f2_resumed.overflow_total, f2_reference.overflow_total);
    replace_with_incompatible_protocol_version(f2_path);
    DEE_CHECK_THROWS(suite, resume_environmental_return_checkpoint(f2_path.string(), lazy));
    remove_if_present(f2_path);

    ReusableRevisionConfig invalid_f1;
    invalid_f1.revision1 = 99;
    DEE_CHECK_THROWS(suite, run_reusable_revision(invalid_f1, lazy));
    auto mismatched_f1 = f1_configs[0];
    mismatched_f1.id = "REV_13_11";
    DEE_CHECK_THROWS(suite, run_reusable_revision(mismatched_f1, lazy));
    EnvironmentalReturnConfig invalid_f2;
    invalid_f2.environment_clock_phase = 1;
    DEE_CHECK_THROWS(suite, run_environmental_return(invalid_f2, lazy));
    auto mismatched_f2 = f2_configs[0];
    mismatched_f2.id = "ENV_RESPONSE_CUT";
    DEE_CHECK_THROWS(suite, run_environmental_return(mismatched_f2, lazy));

    return suite.finish();
}
