#include "dee_thinking/organizations.hpp"
#include "test_support.hpp"

#include <cstdint>
#include <initializer_list>
#include <string>
#include <utility>
#include <vector>

using dee::thinking::EventStatus;
using dee::thinking::HistoryMode;
using dee::thinking::InputRequest;
using dee::thinking::ReferenceWorld;

namespace {

void apply_reprogramming_protocol(ReferenceWorld& world, bool teacher) {
    std::vector<InputRequest> stage_one{{"cue_train", 5}};
    if (teacher) stage_one.push_back({"teacher", 7});
    const auto training = world.runtime.experience_batch(stage_one, 0);
    if (training.status != EventStatus::Scheduled) throw std::runtime_error("training was not scheduled");
    world.runtime.run_until(6);
    const auto query = world.runtime.probe("query", 6, 11);
    if (query.status != EventStatus::Scheduled) throw std::runtime_error("query was not scheduled");
    world.runtime.run_until(11);
}

struct RecurrenceResult {
    dee::v27::Record consequence;
    dee::v27::Record redirect;
    dee::v27::Record q;
};

RecurrenceResult run_recurrence(
    HistoryMode history,
    std::initializer_list<InputRequest> channels,
    bool cut_link = false) {
    auto world = dee::thinking::make_recurrence_multichannel_world(history);
    std::vector<InputRequest> requests(channels);
    const auto stimulus = world.runtime.experience_batch(requests, 0);
    if (stimulus.status != EventStatus::Scheduled) {
        throw std::runtime_error("recurrence stimulus was not scheduled");
    }
    if (cut_link) {
        const auto cut = world.runtime.experience("cut_link", 0, 0);
        if (cut.status != EventStatus::Scheduled) throw std::runtime_error("cut was not scheduled");
    }
    world.runtime.run_until(6);
    const auto consequence = world.runtime.observe(world.landmarks.at("consequence")).record;
    world.runtime.run_until(8);
    const auto redirect = world.runtime.observe(world.landmarks.at("redirect")).record;
    world.runtime.run_until(12);
    const auto q = world.runtime.observe(world.landmarks.at("q")).record;
    return {consequence, redirect, q};
}

}  // namespace

int main() {
    dee::thinking::test::Suite suite("reference_tests");

    // E1: transport is a real v27 trajectory. A zero-load carrier is physically
    // distinct from absence, and an occupied observer destination is not cleared.
    {
        auto world = dee::thinking::make_transport_world(false);
        const auto event = world.runtime.experience("carrier", 0, 7);
        DEE_CHECK_EQ(suite, event.status, EventStatus::Scheduled);
        world.runtime.run_until(5);
        const auto destination = world.runtime.observe(world.landmarks.at("destination"));
        DEE_CHECK(suite, destination.record.occupied());
        DEE_CHECK_EQ(suite, destination.record.s_reg, 7);
        DEE_CHECK_EQ(suite, destination.record.dx, 1);
        DEE_CHECK_EQ(suite, destination.record.dy, 0);
        DEE_CHECK_EQ(suite, destination.record.dz, 0);
    }
    {
        auto zero_load = dee::thinking::make_transport_world(false);
        auto absent = dee::thinking::make_transport_world(false);
        zero_load.runtime.experience("carrier", 0, 0);
        zero_load.runtime.run_until(5);
        absent.runtime.run_until(5);
        const auto q = zero_load.landmarks.at("destination");
        DEE_CHECK(suite, zero_load.runtime.observe(q).raw != 0);
        DEE_CHECK_EQ(suite, zero_load.runtime.observe(q).record.s_reg, 0);
        DEE_CHECK_EQ(suite, absent.runtime.observe(q).raw, 0ULL);
    }
    {
        auto occupied = dee::thinking::make_transport_world(true);
        const auto initial = occupied.runtime.observe(occupied.landmarks.at("destination"));
        occupied.runtime.experience("carrier", 0, 7);
        occupied.runtime.run_until(5);
        const auto terminal = occupied.runtime.observe(occupied.landmarks.at("destination"));
        DEE_CHECK_EQ(suite, terminal.raw, initial.raw);
        DEE_CHECK_EQ(suite, terminal.record.semantic, 4);
        DEE_CHECK_EQ(suite, terminal.record.state, 7000U);
        DEE_CHECK_EQ(suite, terminal.clock, initial.clock + 5);
    }

    // E2: the same fixed apparatus yields a teacher-dependent transformation.
    // All writes use declared channels; the query is explicitly marked as a probe.
    {
        auto trained = dee::thinking::make_reprogramming_world();
        auto no_teacher = dee::thinking::make_reprogramming_world();
        apply_reprogramming_protocol(trained, true);
        apply_reprogramming_protocol(no_teacher, false);
        const auto trained_response = trained.runtime.observe(trained.landmarks.at("response")).record;
        const auto control_response = no_teacher.runtime.observe(no_teacher.landmarks.at("response")).record;
        DEE_CHECK(suite, trained_response.occupied());
        DEE_CHECK_EQ(suite, trained_response.s_reg, 23);
        DEE_CHECK_EQ(suite, trained_response.dx, -1);
        DEE_CHECK_EQ(suite, trained_response.dy, 1);
        DEE_CHECK_EQ(suite, trained_response.dz, 0);
        DEE_CHECK(suite, control_response.raw != trained_response.raw);
        DEE_CHECK_EQ(suite, control_response.s_reg, 11);
        DEE_CHECK_EQ(suite, control_response.dx, -1);
        DEE_CHECK_EQ(suite, control_response.dy, 0);
        DEE_CHECK_EQ(suite, control_response.dz, 0);
    }

    // E3: common-age readout of the fixed history apparatus. HA/HB exchange the
    // early/late order, and the comparator direction separates HA, H0 and HB at t=3.
    {
        auto h0 = dee::thinking::make_history_world(HistoryMode::H0);
        auto ha = dee::thinking::make_history_world(HistoryMode::HA);
        auto hb = dee::thinking::make_history_world(HistoryMode::HB);
        h0.runtime.run_until(3);
        ha.runtime.run_until(3);
        hb.runtime.run_until(3);
        const auto h0_record = h0.runtime.observe(h0.landmarks.at("comparator")).record;
        const auto ha_record = ha.runtime.observe(ha.landmarks.at("comparator")).record;
        const auto hb_record = hb.runtime.observe(hb.landmarks.at("comparator")).record;
        DEE_CHECK_EQ(suite, h0_record.s_reg, 7);
        DEE_CHECK_EQ(suite, ha_record.s_reg, 7);
        DEE_CHECK_EQ(suite, hb_record.s_reg, 7);
        DEE_CHECK_EQ(suite, h0_record.dx, 0);
        DEE_CHECK_EQ(suite, ha_record.dx, 1);
        DEE_CHECK_EQ(suite, hb_record.dx, -1);
        DEE_CHECK_EQ(suite, h0_record.dy, 1);
        DEE_CHECK_EQ(suite, ha_record.dy, 1);
        DEE_CHECK_EQ(suite, hb_record.dy, 1);
        DEE_CHECK(suite, h0.runtime.raw_copy() != ha.runtime.raw_copy());
        DEE_CHECK(suite, ha.runtime.raw_copy() != hb.runtime.raw_copy());
    }

    // E4: the integrated history/multichannel/recurrence apparatus reproduces the
    // registered t6 -> t8 -> t12 chain. Loads are A=8, B=9, C=4. A causal cut at
    // the redirect preserves the upstream consequence but removes its q update.
    {
        const auto ha_ab = run_recurrence(HistoryMode::HA, {{"A", 8}, {"B", 9}});
        const auto ha_abc = run_recurrence(
            HistoryMode::HA, {{"A", 8}, {"B", 9}, {"C", 4}});
        const auto cut = run_recurrence(HistoryMode::HA, {{"A", 8}, {"B", 9}}, true);

        DEE_CHECK_EQ(suite, ha_ab.consequence.s_reg, 24);
        DEE_CHECK_EQ(suite, ha_ab.redirect.s_reg, 24);
        DEE_CHECK_EQ(suite, ha_ab.q.s_reg, 391);
        DEE_CHECK_EQ(suite, ha_abc.consequence.s_reg, 28);
        DEE_CHECK_EQ(suite, ha_abc.redirect.s_reg, 28);
        DEE_CHECK_EQ(suite, ha_abc.q.s_reg, 395);
        DEE_CHECK_EQ(suite, cut.consequence.s_reg, 24);
        DEE_CHECK_EQ(suite, cut.redirect.s_reg, 24);
        DEE_CHECK_EQ(suite, cut.q.s_reg, 367);
        DEE_CHECK(suite, ha_ab.q.raw != cut.q.raw);
    }

    return suite.finish();
}
