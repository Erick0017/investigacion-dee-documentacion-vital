cmake_minimum_required(VERSION 3.20)

project(dee_thinking_basal_consumer LANGUAGES CXX)

find_package(dee_thinking 4 CONFIG REQUIRED)

add_executable(dee_thinking_basal_consumer main.cpp)
target_link_libraries(dee_thinking_basal_consumer PRIVATE DEE::thinking)
target_compile_features(dee_thinking_basal_consumer PRIVATE cxx_std_20)
