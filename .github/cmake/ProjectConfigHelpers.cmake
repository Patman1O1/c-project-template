#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_CURRENT_LIST_DIR}/.github/cmake/functions.cmake")

#-----------------------------------------------------------------------------------------------------------------------
# Variables
#-----------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------------------------------------
function(configure_root_directory PROJECT_NAME PROJECT_NAMESPACE PROJECT_VERSION PROJECT_DESCRIPTION PROJECT_TYPE)
    # Configure the project root CMakeLists.txt file
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/${PROJECT_TYPE}/${PROJECT_TYPE}_init.cmake" PROJECT_INIT)
    configure_file("${CMAKE_SOURCE_DIR}/CMakeLists.txt.in"
            "${CMAKE_SOURCE_DIR}/CMakeLists.txt"
            @ONLY)
    file(REMOVE "${CMAKE_SOURCE_DIR}/CMakeLists.txt.in")

    # Configure the conanfile.py file
    configure_file("${CMAKE_SOURCE_DIR}/conanfile.py.in"
                   "${CMAKE_SOURCE_DIR}/conanfile.py"
                   @ONLY)
    file(REMOVE "${CMAKE_SOURCE_DIR}/conanfile.py.in")
endfunction()

function(configure_source_directory PROJECT_NAME PROJECT_NAMESPACE PROJECT_TYPE)
    # Rename the "template" subdirectory to the project name
    file(COPY "${CMAKE_SOURCE_DIR}/src/template" DESTINATION "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/template")

    if(PROJECT_TYPE MATCHES "^(static_library|shared_library)$")
        # Remove main.c.in (libraries don't have entry points)
        file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c.in")
    elseif(PROJECT_TYPE MATCHES "interface_library")
        # Remove all source files (interface_libraries are header-only)
        file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c.in")
        file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/${PROJECT_NAME}.c.in")
    endif()

    # Configure the source CMakeLists.txt.in file
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/${PROJECT_TYPE}/${PROJECT_TYPE}_definition.cmake" PROJECT_DEFINE)
    configure_file("${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/CMakeLists.txt"
                    @ONLY)

    # Configure the .c source file
    configure_file("${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/template.c.in"
                   "${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/${PROJECT_NAME}.c"
                   @ONLY)

    # Configure the .h header file
    configure_file("${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/include/template.h.in"
                   "${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/include/${PROJECT_NAME}.h"
                   @ONLY)

    # Configure the export header file
    configure_file("${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/include/export.h.in"
                   "${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/include/export.h"
                   @ONLY)
endfunction()
