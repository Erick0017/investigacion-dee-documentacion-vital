cmake_minimum_required(VERSION 3.20)
project(dee_thinking_installed_consumer LANGUAGES CXX)

find_package(dee_thinking 3 CONFIG REQUIRED)

add_executable(installed_consumer main.cpp)
target_compile_features(installed_consumer PRIVATE cxx_std_20)
target_link_libraries(installed_consumer PRIVATE DEE::thinking)
