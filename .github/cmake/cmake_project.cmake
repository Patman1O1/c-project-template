#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_SOURCE_DIR}/.github/cmake/functions.cmake")

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
set(CMAKE_MINIMUM_REQUIRED_VERSION 3.28.0 CACHE STRING "The minimum required version for CMake")

#-----------------------------------------------------------------------------------------------------------------------
# Parameter Validation
#-----------------------------------------------------------------------------------------------------------------------
# Validate the project name
if(NOT PROJECT_NAME)
    message(FATAL_ERROR "PROJECT_NAME was not specified")
    return()
endif()

# Make sure all characters are uppercase when validating the project type
string(TOUPPER "${PROJECT_TYPE}" PROJECT_TYPE)

# Validate the project type
if(NOT PROJECT_TYPE MATCHES "^(EXECUTABLE|STATIC LIBRARY|SHARED LIBRARY|INTERFACE LIBRARY)$")
    message(FATAL_ERROR "PROJECT_TYPE was not specified as EXECUTABLE, STATIC LIBRARY, SHARED LIBRARY, or INTERFACE LIBRARY")
    return()
endif()

#-----------------------------------------------------------------------------------------------------------------------
# Formating
#-----------------------------------------------------------------------------------------------------------------------
to_pascal_case("${PROJECT_NAME}" PROJECT_NAME_PASCAL_CASE)

to_snake_case("${PROJECT_NAME}" PROJECT_NAME_SNAKE_CASE)

to_kebab_case("${PROJECT_NAME}" PROJECT_NAME_KEBAB_CASE)

string(TOUPPER "${PROJECT_NAME_SNAKE_CASE}" PROJECT_NAME_SCREAMING_CASE)

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (${CMAKE_SOURCE_DIR})
#-----------------------------------------------------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (cmake)
#-----------------------------------------------------------------------------------------------------------------------
file(RENAME "${CMAKE_SOURCE_DIR}/cmake/TemplateConfig.cmake.in" "${CMAKE_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in")

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (${CMAKE_SOURCE_DIR}/src)
#-----------------------------------------------------------------------------------------------------------------------
# Rename the src/template to src/${PROJECT_NAME}
file(COPY "${CMAKE_SOURCE_DIR}/src/template" DESTINATION "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}")
file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/template")

# Configure src/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/src/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/src/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/src/CMakeLists.txt.in")

# Configure src/${PROJECT_NAME}/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}/CMakeLists.txt.in")

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (${CMAKE_SOURCE_DIR}/test)
#-----------------------------------------------------------------------------------------------------------------------
# Rename the test/template to test/${PROJECT_NAME}
file(COPY "${CMAKE_SOURCE_DIR}/test/template" DESTINATION "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}")
file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/test/template")

# Configure test/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/test/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/test/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/test/CMakeLists.txt.in")

# Configure test/${PROJECT_NAME}/CMakeLists.txt
configure_file("${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}/CMakeLists.txt.in"
               "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}/CMakeLists.txt"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}/CMakeLists.txt.in")

# Configure test/${PROJECT_NAME}/${PROJECT_NAME}_test.cpp
configure_file("${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}/${PROJECT_NAME_SNAKE_CASE}_test.cpp.in"
               "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}/${PROJECT_NAME_SNAKE_CASE}_test.cpp"
               @ONLY)
file(REMOVE "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}/${PROJECT_NAME_SNAKE_CASE}_test.cpp.in")

#-----------------------------------------------------------------------------------------------------------------------
# Project Configuration (Project Type)
#-----------------------------------------------------------------------------------------------------------------------
if("${PROJECT_TYPE}" MATCHES "EXECUTABLE")
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/executable/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/executable/ProjectDefinition.cmake" PROJECT_DEFINE)


elseif("${PROJECT_TYPE}" MATCHES "STATIC LIBRARY")
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/static_library/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/static_library/ProjectDefinition.cmake" PROJECT_DEFINE)
elseif("${PROJECT_TYPE}" MATCHES "SHARED LIBRARY")
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/shared_library/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/shared_library/ProjectDefinition.cmake" PROJECT_DEFINE)
else()
    # Read the contents of the project init and definition files and store their contents
    file(READ "${CMAKE_SOURCE_DIR}/interface_library/ProjectInit.cmake" PROJECT_INIT)
    file(READ "${CMAKE_SOURCE_DIR}/interface_library/ProjectDefinition.cmake" PROJECT_DEFINE)

    # Remove all the source files (interface libraries are header only)
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/")
endif()


