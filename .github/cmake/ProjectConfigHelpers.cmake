#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_SOURCE_DIR}/.github/cmake/executable/ExecutableInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/executable/ExecutableDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/interface_library/InterfaceLibraryInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/interface_library/InterfaceLibraryDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/static_library/StaticLibraryInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/static_library/StaticLibraryDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/shared_library/SharedLibraryInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/shared_library/SharedLibraryDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/functions.cmake")

#-----------------------------------------------------------------------------------------------------------------------
# Variables
#-----------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------------------------------------
function(configure_root_directory PROJECT_NAME PROJECT_NAMESPACE PROJECT_VERSION PROJECT_DESCRIPTION PROJECT_TYPE)
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/${PROJECT_TYPE}/${PROJECT_TYPE}_init.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/${PROJECT_TYPE}/${PROJECT_TYPE}_definition.cmake" PROJECT_DEFINE)

    # Configure the conanfile.py file
    configure_file("${CMAKE_SOURCE_DIR}/conanfile.py.in"
                   "${CMAKE_SOURCE_DIR}/conanfile.py"
                   @ONLY)
    file(REMOVE "${CMAKE_SOURCE_DIR}/conanfile.py.in")

    # Configure the project root CMakeLists.txt file
    configure_file("${CMAKE_SOURCE_DIR}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/CMakeLists.txt"
                   @ONLY)
    file(REMOVE "${CMAKE_SOURCE_DIR}/CMakeLists.txt.in")
endfunction()
