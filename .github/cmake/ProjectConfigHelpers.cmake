#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_CURRENT_LIST_DIR}/functions.cmake")

#-----------------------------------------------------------------------------------------------------------------------
# Variables
#-----------------------------------------------------------------------------------------------------------------------
set(PROJECT_ROOT_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")

#-----------------------------------------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------------------------------------
function(configure_root_directory PROJECT_NAME PROJECT_NAMESPACE PROJECT_VERSION PROJECT_DESCRIPTION PROJECT_TYPE)
    # Configure the project root CMakeLists.txt file
    file(READ "${CMAKE_CURRENT_LIST_DIR}/${PROJECT_TYPE}/${PROJECT_TYPE}_init.cmake" PROJECT_INIT)
    configure_file("${PROJECT_ROOT_DIR}/CMakeLists.txt.in"
            "${PROJECT_ROOT_DIR}/CMakeLists.txt"
            @ONLY)
    file(REMOVE "${PROJECT_ROOT_DIR}/CMakeLists.txt.in")

    # Configure the conanfile.py file
    configure_file("${PROJECT_ROOT_DIR}/conanfile.py.in"
                   "${PROJECT_ROOT_DIR}/conanfile.py"
                   @ONLY)
    file(REMOVE "${PROJECT_ROOT_DIR}/conanfile.py.in")
endfunction()

function(configure_include_directory PROJECT_NAME)
    # Rename the template subdirectory to the project name
    file(RENAME "${PROJECT_ROOT_DIR}/include/template" "${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}")

    # Configure the project header file (i.e. ${PROJECT_NAME}.h)
    configure_file("${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}/template.h.in"
                   "${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}/${PROJECT_NAME}.h"
                   @ONLY)
    file(REMOVE "${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}/template.h.in")

    # Configure the export header file (i.e. export.h)
    configure_file("${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}/export.h.in"
                   "${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}/export.h"
                   @ONLY)
    file(REMOVE "${PROJECT_ROOT_DIR}/include/${PROJECT_NAME}/export.h.in")
endfunction()

function(configure_source_directory PROJECT_NAME PROJECT_NAMESPACE PROJECT_TYPE)
    if(PROJECT_TYPE MATCHES "^(static_library|shared_library)$")
        # Rename ${PROJECT_ROOT_DIR}/src/template to ${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}
        file(RENAME "${PROJECT_ROOT_DIR}/src/template" "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}")

        # Configure the source directory CMakeLists.txt
        configure_file("${PROJECT_ROOT_DIR}/src/CMakeLists.txt.in"
                       "${PROJECT_ROOT_DIR}/src/CMakeLists.txt"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/CMakeLists.txt.in")

        # Configure the CMakeLists.txt file in ${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}
        file(READ "${CMAKE_CURRENT_LIST_DIR}/${PROJECT_TYPE}/${PROJECT_TYPE}_definition.cmake" PROJECT_DEFINE)
        configure_file("${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in"
                       "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/CMakeLists.txt"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in")

        # Remove main.c.in (libraries don't have entry points)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/main.c.in")

        # Configure ${PROJECT_NAME}.c
        configure_file("${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/template.c.in"
                       "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/${PROJECT_NAME}.c"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/template.c.in")
    elseif(PROJECT_TYPE MATCHES "interface_library")
        # Remove the source directory entirely (interface libraries are header only)
        file(REMOVE_RECURSE "${PROJECT_ROOT_DIR}/src")
    else()
        # Rename ${PROJECT_ROOT_DIR}/src/template to ${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}
        file(RENAME "${PROJECT_ROOT_DIR}/src/template" "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}")

        # Configure the source directory CMakeLists.txt
        configure_file("${PROJECT_ROOT_DIR}/src/CMakeLists.txt.in"
                       "${PROJECT_ROOT_DIR}/src/CMakeLists.txt"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/CMakeLists.txt.in")

        # Configure the CMakeLists.txt file in ${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}
        file(READ "${CMAKE_CURRENT_LIST_DIR}/${PROJECT_TYPE}/${PROJECT_TYPE}_definition.cmake" PROJECT_DEFINE)
        configure_file("${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in"
                       "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/CMakeLists.txt"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in")

        # Configure main.c
        configure_file("${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/main.c.in"
                       "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/main.c"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/main.c.in")

        # Configure ${PROJECT_NAME}.c
        configure_file("${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/template.c.in"
                       "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/${PROJECT_NAME}.c"
                       @ONLY)
        file(REMOVE "${PROJECT_ROOT_DIR}/src/${PROJECT_NAME}/template.c.in")
    endif()
endfunction()


