cmake_minimum_required(VERSION 3.20)

project(dee_thinking_final_laboratory LANGUAGES CXX)

add_library(dee_thinking_baseline STATIC IMPORTED GLOBAL)
set_target_properties(dee_thinking_baseline PROPERTIES
    IMPORTED_LOCATION "${CMAKE_CURRENT_SOURCE_DIR}/baseline/lib/dee_thinking.lib"
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_SOURCE_DIR}/baseline/include")

add_executable(dee_final_laboratory runners/final_laboratory_runner.cpp)
target_link_libraries(dee_final_laboratory PRIVATE dee_thinking_baseline)
target_compile_features(dee_final_laboratory PRIVATE cxx_std_20)
if(MSVC)
    target_compile_options(dee_final_laboratory PRIVATE /W4 /permissive- /EHsc /O2 /Ob2)
endif()
set_target_properties(dee_final_laboratory PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

