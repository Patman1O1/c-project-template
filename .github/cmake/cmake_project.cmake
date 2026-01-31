#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_CURRENT_LIST_DIR}/functions.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/ProjectConfigHelpers.cmake")

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

# Project Variables
set(PROJECT_ROOT_DIR "${CMAKE_CURRENT_LIST_DIR}/../..")

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

#-----------------------------------------------------------------------------------------------------------------------
# Project Include Directory Configuration
#-----------------------------------------------------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------------------------------------------------
# Project Source Directory Configuration
#----------------------------------------------------------------------------------------------------------------------
configure_source_directory("${PROJECT_NAME}" "${PROJECT_NAMESPACE}" "${PROJECT_TYPE}")

#-----------------------------------------------------------------------------------------------------------------------
# Project Test Directory Configuration
#----------------------------------------------------------------------------------------------------------------------
configure_test_directory("${PROJECT_NAME}")
