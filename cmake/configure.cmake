# Define parameters
set(CONAN_PROFILE "" CACHE STRING "The Conan profile that will be used")
set(BUILD_TYPE "" CACHE STRING "The build type")
set(BUILD_TESTS OFF CACHE STRING "Build the project's test suites")

if(NOT CONAN_PROFILE)
    message(FATAL_ERROR "CONAN_PROFILE was not specified")
endif()

if(NOT BUILD_TYPE)
    message(FATAL_ERROR "BUILD_TYPE was not specified")
endif()

execute_process(
        COMMAND conan install "${CMAKE_SOURCE_DIR}" --profile="${CONAN_PROFILE}" -s build_type="${BUILD_TYPE}" --build=missing
)

execute_process(COMMAND "${CMAKE_COMMAND}" -S "${CMAKE_SOURCE_DIR}" -B "${CMAKE_SOURCE_DIR}/build" -D CMAKE_TOOLCHAIN_FILE="${CMAKE_SOURCE_DIR}/build/${BUILD_TYPE}/generators/conan_toolchain.cmake" -D CMAKE_BUILD_TYPE="${BUILD_TYPE}" -D BUILD_TESTS=${BUILD_TESTS})

