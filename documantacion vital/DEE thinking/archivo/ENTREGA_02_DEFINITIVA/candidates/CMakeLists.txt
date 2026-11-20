cmake_minimum_required(VERSION 3.20)
project(dee_preintegration_candidates LANGUAGES CXX)

enable_testing()

find_package(Threads REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_library(dee_thinking_inherited STATIC IMPORTED GLOBAL)
set_target_properties(dee_thinking_inherited PROPERTIES
    IMPORTED_LOCATION "${CMAKE_CURRENT_LIST_DIR}/../build/Release/lib/dee_thinking.lib"
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_LIST_DIR}/../include")
target_link_libraries(dee_thinking_inherited INTERFACE Threads::Threads)

add_executable(h1t
    h1_delay_position/source/h1_delay_position_candidate.cpp
    h1_delay_position/tests/test_h1_delay_position.cpp)
target_include_directories(h1t PRIVATE
    h1_delay_position/include)
target_link_libraries(h1t PRIVATE dee_thinking_inherited)
target_compile_features(h1t PRIVATE cxx_std_20)
set_target_properties(h1t PROPERTIES
    OUTPUT_NAME h1_delay_position_candidate_tests
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/bin")
add_test(NAME candidate_h1_delay_position COMMAND h1t)

add_executable(h2t
    h2_destination_repertoires/source/h2_destination_repertoires_candidate.cpp
    h2_destination_repertoires/tests/test_h2_destination_repertoires.cpp)
target_include_directories(h2t PRIVATE
    h2_destination_repertoires/include)
target_link_libraries(h2t PRIVATE dee_thinking_inherited)
target_compile_features(h2t PRIVATE cxx_std_20)
set_target_properties(h2t PROPERTIES
    OUTPUT_NAME h2_destination_repertoires_candidate_tests
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/bin")
add_test(NAME candidate_h2_destination_repertoires COMMAND h2t)

add_executable(h3_repair
    repair_core17/repair_core17_candidate.cpp)
target_link_libraries(h3_repair PRIVATE dee_thinking_inherited)
target_compile_features(h3_repair PRIVATE cxx_std_20)
set_target_properties(h3_repair PROPERTIES
    OUTPUT_NAME repair_core17_candidate
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/bin")
add_test(NAME candidate_h3_repair_core17
    COMMAND h3_repair "${CMAKE_CURRENT_BINARY_DIR}/repair_core17_results.json")
add_test(NAME candidate_h3_repair_core17_verify
    COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_LIST_DIR}/repair_core17/verify_repair_results.py"
        "${CMAKE_CURRENT_BINARY_DIR}/repair_core17_results.json"
        --output "${CMAKE_CURRENT_BINARY_DIR}/repair_core17_validation.json")
set_tests_properties(candidate_h3_repair_core17_verify PROPERTIES
    DEPENDS candidate_h3_repair_core17)

add_test(NAME candidate_h4_accessibility_contract
    COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_LIST_DIR}/accessibility/verify_accessibility_contract.py")

add_executable(preintegration_lab
    ../laboratory/preintegration/runners/preintegration_runner.cpp)
target_link_libraries(preintegration_lab PRIVATE dee_thinking_inherited)
target_compile_features(preintegration_lab PRIVATE cxx_std_20)
set_target_properties(preintegration_lab PROPERTIES
    OUTPUT_NAME preintegration_runner
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../laboratory/preintegration/bin")
add_test(NAME preintegration_laboratory_lazy
    COMMAND preintegration_lab "${CMAKE_CURRENT_BINARY_DIR}/lab_lazy" lazy-4)
add_test(NAME preintegration_laboratory_dense
    COMMAND preintegration_lab "${CMAKE_CURRENT_BINARY_DIR}/lab_dense" dense-1)
