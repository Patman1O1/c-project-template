#-----------------------------------------------------------------------------------------------------------------------
# cmake_source.cmake
#-----------------------------------------------------------------------------------------------------------------------
# Define parameters
set(PROJECT_NAME "" CACHE STRING "PROJECT_NAME") # Required
set(SOURCE_NAME "" CACHE STRING "SOURCE_NAME") # Required
set(CREATE_HEADER OFF CACHE STRING "CREATE_HEADER")

# Variables
string(TOUPPER "${SOURCE_NAME}" SOURCE_NAME_UPPER)

# Make sure the characters in CREATE_HEADER are all uppercase
string(TOUPPER "${CREATE_HEADER}" CREATE_HEADER)

set(CMAKE_SOURCE_DIR "/home/patman101/c-project-template") # temporary

# Ensure arguments are passed to required parameters
if(NOT PROJECT_NAME)
    message(FATAL_ERROR "\"PROJECT_NAME\" was not specified")
    return()
endif()
if(NOT SOURCE_NAME)
    message(FATAL_ERROR "\"SOURCE_NAME\" was not specified")
    return()
endif()

# Ensure only "ON" or "OFF" are passed in as an argument for the CREATE_HEADER parameter
if(NOT CREATE_HEADER MATCHES "^(ON|OFF)$")
    message(FATAL_ERROR "\"CREATE_HEADER\" expected ON or OFF as an argument but received ${CREATE_HEADER}")
    return()
endif()

# Check if the source file already exists
if(EXISTS "${CMAKE_SOURCE_DIR}/src/${SOURCE_NAME}.c")
    message(NOTICE "${SOURCE_NAME} already exists")
    return()
endif()

# Create the source file
file(TOUCH "${CMAKE_SOURCE_DIR}/src/${SOURCE_NAME}.c")

# Create the associated header file if it doesn't already exist and CREATE_HEADER is ON
if(NOT EXISTS "${CMAKE_SOURCE_DIR}/include/${PROJECT_NAME}/${SOURCE_NAME}.h" AND CREATE_HEADER MATCHES "ON")
    # Create the associated header file
    execute_process(COMMAND "${CMAKE_COMMAND} -D PROJECT_NAME=${PROJECT_NAME} -D HEADER_NAME=${SOURCE_NAME} -P ${CMAKE_SOURCE_DIR}/cmake/cmake_header.cmake")
endif()

# Include the header file in the source file
file(WRITE "${CMAKE_SOURCE_DIR}/src/${SOURCE_NAME}.c" "#include <${PROJECT_NAME}/${SOURCE_NAME}.h>\n\n")

file(APPEND "${CMAKE_SOURCE_DIR}/src/${SOURCE_NAME}.c"
        "#ifdef __cplusplus\nextern \"C\" {\n#endif // #ifdef __cplusplus\n\n#ifdef __cplusplus\n}\n#endif // #ifdef __cplusplus\n"
)
