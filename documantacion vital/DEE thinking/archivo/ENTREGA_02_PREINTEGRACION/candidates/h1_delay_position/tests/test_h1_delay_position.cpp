#include "h1_delay_position_candidate.hpp"

#include <iostream>
#include <stdexcept>

using namespace dee::thinking::candidates::h1;

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
        Config config;
        int native_correct = 0;
        int reversed_correct = 0;
        for (const int delta : config.labels) {
            config.input_delta = delta;
            config.arm = Arm::Native;
            const auto native = run(config, {dee::v27::Backend::Lazy, 4});
            require(native.initial_hubs_empty, "native hub occupied at tick zero");
            native_correct += native.measurement == delta;
            config.arm = Arm::ReversedCalibration;
            const auto reversed = run(config, {dee::v27::Backend::Lazy, 4});
            reversed_correct += reversed.measurement == delta;
        }
        require(native_correct == 11, "native delay-position decoding failed");
        require(reversed_correct == 1, "reversed calibration control failed");
        config.input_delta = 0;
        config.arm = Arm::TargetAbsent;
        require(!run(config, {dee::v27::Backend::Lazy, 4}).measurement.has_value(),
                "absent target produced a record");
        config.input_delta = 3;
        config.arm = Arm::Native;
        const auto dense = run(config, {dee::v27::Backend::DenseSequential, 1});
        const auto lazy = run(config, {dee::v27::Backend::Lazy, 4});
        require(dense.final_raw == lazy.final_raw, "Dense/Lazy RAW mismatch");
        require(dense.final_clock == lazy.final_clock, "Dense/Lazy clock mismatch");
        Config wrapped = config;
        wrapped.dimension = 31;
        require_invalid([&] { (void)run(wrapped); }, "self-wrapping domain was accepted");
        Config nonorthogonal = config;
        nonorthogonal.probe_direction = nonorthogonal.target_direction;
        require_invalid([&] { (void)run(nonorthogonal); }, "nonorthogonal frame was accepted");
        std::cout << "H1_CANDIDATE_PASS native=11/11 reversed=1/11 absent=1 "
                     "dense_lazy_exact=1 domain_guards=2\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "H1_CANDIDATE_FAIL " << error.what() << '\n';
        return 1;
    }
}
