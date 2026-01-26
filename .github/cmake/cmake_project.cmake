#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_SOURCE_DIR}/.github/cmake/functions.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/ProjectConfigHelpers.cmake")


#-----------------------------------------------------------------------------------------------------------------------
# Parameters (Required)
#-----------------------------------------------------------------------------------------------------------------------
set(PROJECT_NAME "" CACHE STRING "The name of the project")
set(PROJECT_TYPE "" CACHE STRING "The type of the project")

#-----------------------------------------------------------------------------------------------------------------------
# Parameters (Optional)
#-----------------------------------------------------------------------------------------------------------------------
set(PROJECT_NAMESPACE "${PROJECT_NAME}" CACHE STRING "The namespace of the project")
set(PROJECT_VERSION 0.1.0 CACHE STRING "The version of the project")
set(PROJECT_DESCRIPTION "" CACHE STRING "The description of the project")

#-----------------------------------------------------------------------------------------------------------------------
# Parameter Validation
#-----------------------------------------------------------------------------------------------------------------------
# Validate the project name
if(NOT PROJECT_NAME)
    message(FATAL_ERROR "PROJECT_NAME was not specified")
    return()
endif()

# Format the project type in snake_case
to_snake_case("${PROJECT_TYPE}" PROJECT_TYPE)

# Validate the project type and set BUILD_SHARED_LIBS if the project type is a shared library
if(PROJECT_TYPE MATCHES "shared_library")
    set(BUILD_SHARED_LIBS ON)
elseif(PROJECT_TYPE MATCHES "^(executable|static_library|interface_library)$")
    set(BUILD_SHARED_LIBS OFF)
else()
    message(FATAL_ERROR "PROJECT_TYPE was not specified as Executable, Static Library, Shared Library, or Interface Library")
    return()
endif()

#-----------------------------------------------------------------------------------------------------------------------
# Variables
#-----------------------------------------------------------------------------------------------------------------------
# CMake Variables
set(CMAKE_MINIMUM_REQUIRED_VERSION 3.28.0)

# C Variables
set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)

# C++ Variables
set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#-----------------------------------------------------------------------------------------------------------------------
# Formating
#-----------------------------------------------------------------------------------------------------------------------
# Project name formating
to_pascal_case("${PROJECT_NAME}" PROJECT_NAME_PASCAL_CASE)
to_snake_case("${PROJECT_NAME}" PROJECT_NAME_SNAKE_CASE)
to_kebab_case("${PROJECT_NAME}" PROJECT_NAME_KEBAB_CASE)
string(TOUPPER "${PROJECT_NAME_SNAKE_CASE}" PROJECT_NAME_SCREAMING_CASE)

#-----------------------------------------------------------------------------------------------------------------------
# Project Root Directory Configuration
#-----------------------------------------------------------------------------------------------------------------------
configure_root_directory("${PROJECT_NAME_PASCAL_CASE}" "${PROJECT_NAMESPACE}" ${PROJECT_VERSION} "${PROJECT_DESCRIPTION}" "${PROJECT_TYPE}")

return() # temporary

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (cmake)
#-----------------------------------------------------------------------------------------------------------------------
file(RENAME "${CMAKE_SOURCE_DIR}/cmake/TemplateConfig.cmake.in" "${CMAKE_SOURCE_DIR}/cmake/${PROJECT_NAME_PASCAL_CASE}Config.cmake.in")

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (${CMAKE_SOURCE_DIR}/src)
#-----------------------------------------------------------------------------------------------------------------------
# Configure src/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/src/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/src/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/src/CMakeLists.txt.in")

# Configure src/${PROJECT_NAME}/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in")

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (${CMAKE_SOURCE_DIR}/test)
#-----------------------------------------------------------------------------------------------------------------------
# Configure test/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/test/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/test/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/test/CMakeLists.txt.in")

# Configure test/${PROJECT_NAME}/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME}/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME}/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME}/CMakeLists.txt.in")

# Configure test/${PROJECT_NAME}/${PROJECT_NAME}_test.cpp
configure_file("${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME}/template_test.cpp.in"
               "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME}/${PROJECT_NAME_SNAKE_CASE}_test.cpp"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME}/${PROJECT_NAME_SNAKE_CASE}_test.cpp.in")

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (Project Type)
#-----------------------------------------------------------------------------------------------------------------------
if("${PROJECT_TYPE}" MATCHES "EXECUTABLE")
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/executable/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/executable/ProjectDefinition.cmake" PROJECT_DEFINE)

    # Configure src/${PROJECT_NAME}/CMakeLists.txt
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/CMakeLists.txt"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/${PROJECT_NAME}.c
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/template.c.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/${PROJECT_NAME_SNAKE_CASE}.c"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/main.c
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/export.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/${PROJECT_NAME}.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/template.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/${PROJECT_NAME_SNAKE_CASE}.h"
                   @ONLY)
elseif("${PROJECT_TYPE}" MATCHES "STATIC LIBRARY")
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/static_library/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/static_library/ProjectDefinition.cmake" PROJECT_DEFINE)

    # Remove src/${PROJECT_NAME}/main.c (libraries don't have entry points)
    file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c.in")

    # Configure src/${PROJECT_NAME}/${PROJECT_NAME}.c
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/template.c.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/${PROJECT_NAME_SNAKE_CASE}.c"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/export.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/${PROJECT_NAME}.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/template.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/${PROJECT_NAME_SNAKE_CASE}.h"
                   @ONLY)
elseif("${PROJECT_TYPE}" MATCHES "SHARED LIBRARY")
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/shared_library/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/shared_library/ProjectDefinition.cmake" PROJECT_DEFINE)

    # Remove src/${PROJECT_NAME}/main.c (libraries don't have entry points)
    file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c.in")

    # Configure src/${PROJECT_NAME}/${PROJECT_NAME}.c
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/template.c.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/${PROJECT_NAME_SNAKE_CASE}.c"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/export.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/${PROJECT_NAME}.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/template.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/${PROJECT_NAME_SNAKE_CASE}.h"
                   @ONLY)
else()
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/interface_library/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/.github/cmake/interface_library/ProjectDefinition.cmake" PROJECT_DEFINE)

    # Remove all the source files (interface libraries are header only)
    file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/template.c.in")
    file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/main.c.in")

    # Configure src/${PROJECT_NAME}/include/export.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/export.h"
                   @ONLY)

    # Configure src/${PROJECT_NAME}/include/${PROJECT_NAME}.h
    configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/template.h.in"
                   "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}/include/${PROJECT_NAME_SNAKE_CASE}.h"
                   @ONLY)
endif()


