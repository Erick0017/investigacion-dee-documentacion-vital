cmake_minimum_required(VERSION 3.20)

project(dee_thinking VERSION 2.0.0 LANGUAGES CXX)

include(GNUInstallDirs)

option(DEE_THINKING_BUILD_TESTS "Build the DEE thinking validation suite" ON)
option(DEE_THINKING_BUILD_EXAMPLES "Build the DEE thinking examples" ON)
option(DEE_THINKING_BUILD_BENCHMARKS "Build technical backend benchmarks" ON)

find_package(Threads REQUIRED)

add_library(dee_thinking STATIC
    src/kernel_v27.cpp
    src/runtime.cpp
    src/organizations.cpp
    src/organization_catalog.cpp
    src/composition.cpp
)
add_library(DEE::thinking ALIAS dee_thinking)
set_target_properties(dee_thinking PROPERTIES EXPORT_NAME thinking)

target_include_directories(dee_thinking
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_compile_features(dee_thinking PUBLIC cxx_std_20)
target_link_libraries(dee_thinking PUBLIC Threads::Threads)
set_target_properties(dee_thinking PROPERTIES
    CXX_EXTENSIONS OFF
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

if(MSVC)
    target_compile_options(dee_thinking PRIVATE /W4 /permissive- /EHsc /bigobj)
else()
    target_compile_options(dee_thinking PRIVATE -Wall -Wextra -Wpedantic)
endif()

if(DEE_THINKING_BUILD_BENCHMARKS)
    add_executable(dee_backend_benchmark benchmarks/backend_benchmark.cpp)
    target_link_libraries(dee_backend_benchmark PRIVATE DEE::thinking)
    set_target_properties(dee_backend_benchmark PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
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

    add_executable(dee_composition_a examples/composition_a_learning_update.cpp)
    target_link_libraries(dee_composition_a PRIVATE DEE::thinking)
    set_target_properties(dee_composition_a PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

    add_executable(dee_composition_b examples/composition_b_context_multichannel.cpp)
    target_link_libraries(dee_composition_b PRIVATE DEE::thinking)
    set_target_properties(dee_composition_b PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

    add_executable(dee_catalog_transport examples/catalog_transport.cpp)
    target_link_libraries(dee_catalog_transport PRIVATE DEE::thinking)
    set_target_properties(dee_catalog_transport PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

    add_executable(dee_composition_c6_later_query examples/composition_c6_later_query.cpp)
    target_link_libraries(dee_composition_c6_later_query PRIVATE DEE::thinking)
    set_target_properties(dee_composition_c6_later_query PROPERTIES
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

    add_executable(dee_integration_persistence_tests tests/integration_persistence_tests.cpp)
    target_link_libraries(dee_integration_persistence_tests PRIVATE DEE::thinking)
    set_target_properties(dee_integration_persistence_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME integration_persistence
        COMMAND dee_integration_persistence_tests
                "${CMAKE_CURRENT_SOURCE_DIR}/fixtures/legacy_v1/pending_event_v1.deetsnap")

    add_executable(dee_backend_tests tests/backend_tests.cpp)
    target_link_libraries(dee_backend_tests PRIVATE DEE::thinking)
    set_target_properties(dee_backend_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME execution_backends
        COMMAND dee_backend_tests "${CMAKE_CURRENT_SOURCE_DIR}/fixtures/whl_v27")

    add_executable(dee_composition_catalog_tests tests/composition_catalog_tests.cpp)
    target_link_libraries(dee_composition_catalog_tests PRIVATE DEE::thinking)
    set_target_properties(dee_composition_catalog_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME composition_catalog COMMAND dee_composition_catalog_tests)

    add_executable(dee_composition_snapshot_tests tests/composition_snapshot_tests.cpp)
    target_link_libraries(dee_composition_snapshot_tests PRIVATE DEE::thinking)
    set_target_properties(dee_composition_snapshot_tests PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
    add_test(NAME composition_snapshot_restore
        COMMAND dee_composition_snapshot_tests
                "${CMAKE_CURRENT_SOURCE_DIR}/fixtures/legacy_v1/pending_event_v1.deetsnap")

    if(DEE_THINKING_BUILD_EXAMPLES)
        add_test(NAME independent_consumer_e2e COMMAND dee_thinking_consumer)
        add_test(NAME examples_smoke COMMAND dee_thinking_demo e1)
        add_test(NAME composition_a_e2e COMMAND dee_composition_a)
        add_test(NAME composition_b_e2e COMMAND dee_composition_b)
        add_test(NAME catalog_transport_e2e COMMAND dee_catalog_transport)
        add_test(NAME composition_c6_later_query_e2e COMMAND dee_composition_c6_later_query)
    endif()
endif()

include(CMakePackageConfigHelpers)
install(TARGETS dee_thinking EXPORT dee_thinkingTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

set(DEE_THINKING_INSTALL_CMAKEDIR "${CMAKE_INSTALL_LIBDIR}/cmake/dee_thinking"
    CACHE STRING "Install location for dee_thinking CMake package files")
configure_package_config_file(
    cmake/dee_thinkingConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/dee_thinkingConfig.cmake"
    INSTALL_DESTINATION "${DEE_THINKING_INSTALL_CMAKEDIR}")
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/dee_thinkingConfigVersion.cmake"
    VERSION "${PROJECT_VERSION}"
    COMPATIBILITY SameMajorVersion)
install(EXPORT dee_thinkingTargets
    FILE dee_thinkingTargets.cmake
    NAMESPACE DEE::
    DESTINATION "${DEE_THINKING_INSTALL_CMAKEDIR}")
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/dee_thinkingConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/dee_thinkingConfigVersion.cmake"
    DESTINATION "${DEE_THINKING_INSTALL_CMAKEDIR}")
