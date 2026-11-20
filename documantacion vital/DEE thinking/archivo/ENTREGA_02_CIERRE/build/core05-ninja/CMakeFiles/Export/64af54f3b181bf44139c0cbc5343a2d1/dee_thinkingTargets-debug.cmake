#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "DEE::thinking" for configuration "Debug"
set_property(TARGET DEE::thinking APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(DEE::thinking PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "CXX"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/dee_thinking.lib"
  )

list(APPEND _cmake_import_check_targets DEE::thinking )
list(APPEND _cmake_import_check_files_for_DEE::thinking "${_IMPORT_PREFIX}/lib/dee_thinking.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
