#include "dee_thinking/organizations.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool value, const std::string& message) {
    if (!value) throw std::runtime_error(message);
}

void train_and_query(dee::thinking::ReferenceWorld& world) {
    require(world.runtime.experience_batch(
                {{"cue_train", 5}, {"teacher", 7}}, 0).status ==
                dee::thinking::EventStatus::Scheduled,
            "training admission failed");
    world.runtime.run_until(6);
    require(world.runtime.probe("query", 6, 11).status ==
                dee::thinking::EventStatus::Scheduled,
            "query admission failed");
    world.runtime.run_until(11);
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const auto snapshot = argc > 1
            ? std::filesystem::path(argv[1])
            : std::filesystem::current_path() / "consumer_checkpoint.deetsnap";

        // This executable uses only the installed public C++ headers and library.
        auto world = dee::thinking::make_reprogramming_world();
        train_and_query(world);
        const auto response = world.runtime.observe(world.landmarks.at("response"));
        require(response.record.occupied(), "expected response is absent");
        require(response.record.dx == -1 && response.record.dy == 1 &&
                    response.record.dz == 0 && response.record.s_reg == 23,
                "unexpected response record");

        // Pause/save/load/fork do not ask a Python process to mediate the trajectory.
        world.runtime.set_protocol_phase("consumer_checkpoint");
        world.runtime.pause();
        world.runtime.save_snapshot(snapshot.string());
        auto resumed = dee::thinking::Runtime::load_snapshot(snapshot.string());
        require(resumed.paused(), "pause state was not serialized");
        resumed.resume();
        auto branch = resumed.fork();
        resumed.advance(3);
        branch.advance(3);
        require(resumed.raw_copy() == branch.raw_copy(), "forked RAW trajectory diverged");
        require(resumed.clock_copy() == branch.clock_copy(), "forked clock trajectory diverged");

        // A separately constructed causal control omits the teacher while preserving
        // the fixed apparatus and query protocol.
        auto control = dee::thinking::make_reprogramming_world();
        require(control.runtime.experience("cue_train", 0, 5).status ==
                    dee::thinking::EventStatus::Scheduled,
                "control cue admission failed");
        control.runtime.run_until(6);
        require(control.runtime.probe("query", 6, 11).status ==
                    dee::thinking::EventStatus::Scheduled,
                "control query admission failed");
        control.runtime.run_until(11);
        const auto control_response = control.runtime.observe(control.landmarks.at("response"));
        require(control_response.raw != response.raw, "teacher control failed to separate responses");

        std::cout << "DEE thinking independent consumer\n"
                  << "tick=" << world.runtime.current_tick() << '\n'
                  << "response={state:" << response.record.state
                  << ",s_reg:" << response.record.s_reg
                  << ",dir:[" << static_cast<int>(response.record.dx) << ','
                  << static_cast<int>(response.record.dy) << ','
                  << static_cast<int>(response.record.dz) << "]}\n"
                  << "control_raw_distinct=true\n"
                  << "snapshot=" << snapshot.string() << '\n'
                  << "native_resume_exact=true\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "independent consumer error: " << error.what() << '\n';
        return 1;
    }
}
