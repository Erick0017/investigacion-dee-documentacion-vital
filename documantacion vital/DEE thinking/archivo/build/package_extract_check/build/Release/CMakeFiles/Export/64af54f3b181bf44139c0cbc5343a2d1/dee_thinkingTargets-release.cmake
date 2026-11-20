#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "DEE::dee_thinking" for configuration "Release"
set_property(TARGET DEE::dee_thinking APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(DEE::dee_thinking PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/dee_thinking.lib"
  )

list(APPEND _cmake_import_check_targets DEE::dee_thinking )
list(APPEND _cmake_import_check_files_for_DEE::dee_thinking "${_IMPORT_PREFIX}/lib/dee_thinking.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
