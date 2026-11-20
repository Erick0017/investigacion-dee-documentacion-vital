cmake_minimum_required(VERSION 3.24)

project(dee_thinking_entrega03_native_learning LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(dee_thinking 2.2.0 CONFIG REQUIRED)

add_executable(dee_entrega03_native_learning
    src/native_environment_learning.cpp
)
target_link_libraries(dee_entrega03_native_learning PRIVATE DEE::thinking)

if(MSVC)
    target_compile_options(dee_entrega03_native_learning PRIVATE /W4 /permissive- /EHsc)
else()
    target_compile_options(dee_entrega03_native_learning PRIVATE -Wall -Wextra -Wpedantic)
endif()

install(TARGETS dee_entrega03_native_learning RUNTIME DESTINATION bin)

