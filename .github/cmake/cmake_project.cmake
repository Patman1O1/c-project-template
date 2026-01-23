#-----------------------------------------------------------------------------------------------------------------------
# Parameters (Required)
#-----------------------------------------------------------------------------------------------------------------------
set(PROJECT_NAME "" CACHE STRING "The name of the project")
set(PROJECT_TYPE "" CACHE STRING "The type of the project")

#-----------------------------------------------------------------------------------------------------------------------
# Parameters (Optional)
#-----------------------------------------------------------------------------------------------------------------------
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
if (NOT PROJECT_TYPE MATCHES "^(EXECUTABLE|STATIC LIBRARY|SHARED LIBRARY|INTERFACE LIBRARY)$")
    message(FATAL_ERROR "PROJECT_TYPE was not specified as EXECUTABLE, STATIC LIBRARY, SHARED LIBRARY, or INTERFACE LIBRARY")
    return()
endif()

#-----------------------------------------------------------------------------------------------------------------------
# .in File Configuration
#-----------------------------------------------------------------------------------------------------------------------
file(TOUCH "${CMAKE_SOURCE_DIR}/${PROJECT_TYPE}.txt")
