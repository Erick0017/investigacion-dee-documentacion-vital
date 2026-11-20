# Included by the product root after the native dee_thinking target exists.
# This file is intentionally optional for pure C++ consumers.
find_package(Python 3.13 EXACT COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 3.1 CONFIG REQUIRED)

pybind11_add_module(dee_thinking_python MODULE
    "${PROJECT_SOURCE_DIR}/bindings/dee_thinking_pybind.cpp"
    "${PROJECT_SOURCE_DIR}/bindings/organizational_pybind.cpp"
    "${PROJECT_SOURCE_DIR}/bindings/cognitive_pybind.cpp"
    "${PROJECT_SOURCE_DIR}/bindings/informative_pybind.cpp"
    "${PROJECT_SOURCE_DIR}/bindings/consolidated_pybind.cpp")
target_link_libraries(dee_thinking_python PRIVATE DEE::thinking)
target_compile_features(dee_thinking_python PRIVATE cxx_std_20)
target_compile_definitions(dee_thinking_python PRIVATE
    DEE_THINKING_PYTHON_VERSION="${DEE_THINKING_PYTHON_VERSION}")
if(NOT DEFINED DEE_THINKING_PYTHON_OUTPUT_DIR)
    set(DEE_THINKING_PYTHON_OUTPUT_DIR "${CMAKE_BINARY_DIR}/python/dee_thinking")
endif()
set_target_properties(dee_thinking_python PROPERTIES
    OUTPUT_NAME "_native"
    LIBRARY_OUTPUT_DIRECTORY "${DEE_THINKING_PYTHON_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY "${DEE_THINKING_PYTHON_OUTPUT_DIR}")

install(TARGETS dee_thinking_python
    LIBRARY DESTINATION dee_thinking
    RUNTIME DESTINATION dee_thinking)
