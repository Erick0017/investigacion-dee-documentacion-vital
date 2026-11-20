cmake_minimum_required(VERSION 3.20)

project(dee_thinking VERSION 1.0.0 LANGUAGES CXX)

option(DEE_THINKING_BUILD_TESTS "Build the DEE thinking validation suite" ON)
option(DEE_THINKING_BUILD_EXAMPLES "Build the DEE thinking examples" ON)

add_library(dee_thinking STATIC
    src/kernel_v27.cpp
    src/runtime.cpp
    src/organizations.cpp
)
add_library(DEE::thinking ALIAS dee_thinking)

target_include_directories(dee_thinking
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)
target_compile_features(dee_thinking PUBLIC cxx_std_20)
set_target_properties(dee_thinking PROPERTIES
    CXX_EXTENSIONS OFF
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

if(MSVC)
    target_compile_options(dee_thinking PRIVATE /W4 /permissive- /EHsc /bigobj)
else()
    target_compile_options(dee_thinking PRIVATE -Wall -Wextra -Wpedantic)
endif()

if(DEE_THINKING_BUILD_EXAMPLES)
    add_executable(dee_thinking_demo examples/dee_thinking_demo.cpp)
    target_link_libraries(dee_thinking_demo PRIVATE DEE::thinking)
    set_target_properties(dee_thinking_demo PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

    add_executable(dee_thinking_consumer examples/independent_consumer.cpp)
    target_link_libraries(dee_thinking_consumer PRIVATE DEE::thinking)
    set_target_properties(dee_thinking_consumer PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endif()

if(DEE_THINKING_BUILD_TESTS)
    include(CTest)
    enable_testing()

    add_executable(dee_kernel_fixture_tests tests/kernel_fixture_tests.cpp)
    target_link_libraries(dee_kernel_fixture_tests PRIVATE DEE::thinking)
    set_target_properties(dee_kernel_fixture_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME kernel_whl_differential
        COMMAND dee_kernel_fixture_tests "${CMAKE_CURRENT_SOURCE_DIR}/fixtures/whl_v27")

    add_executable(dee_runtime_tests tests/runtime_tests.cpp)
    target_link_libraries(dee_runtime_tests PRIVATE DEE::thinking)
    set_target_properties(dee_runtime_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME runtime_contract COMMAND dee_runtime_tests)

    add_executable(dee_reference_tests tests/reference_tests.cpp)
    target_link_libraries(dee_reference_tests PRIVATE DEE::thinking)
    set_target_properties(dee_reference_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME reference_organizations COMMAND dee_reference_tests)

    if(DEE_THINKING_BUILD_EXAMPLES)
        add_test(NAME independent_consumer_e2e COMMAND dee_thinking_consumer)
        add_test(NAME examples_smoke COMMAND dee_thinking_demo e1)
    endif()
endif()

include(GNUInstallDirs)
install(TARGETS dee_thinking EXPORT dee_thinkingTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT dee_thinkingTargets
    FILE dee_thinkingTargets.cmake
    NAMESPACE DEE::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/dee_thinking)
