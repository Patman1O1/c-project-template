# Define parameters
set(TARGET_NAME "" CACHE STRING "TARGET_NAME")
set(TARGET_TYPE "" CACHE STRING "TARGET_TYPE")

# Make sure arguments are passed to the parameters
if(NOT TARGET_NAME)
    message(FATAL_ERROR "NAME was provided")
endif()
if (NOT TARGET_TYPE MATCHES "^(EXECUTABLE|OBJECT|STATIC|SHARED|INTERFACE|)$")
    message(FATAL_ERROR "TYPE was not specified as EXECUTABLE, OBJECT, STATIC, SHARED, or INTERFACE")
endif()

# Create the header file
file(TOUCH "${CMAKE_SOURCE_DIR}/include/${PROJECT_NAME}/${TARGET_NAME}.h")
file(APPEND "${CMAKE_SOURCE_DIR}/include/${PROJECT_NAME}/${TARGET_NAME}.h"
        "#ifndef TEST_H\n#define TEST_H\n\n#ifdef __cplusplus\nextern {\n\#endif // #ifdef __cplusplus\n\n#ifdef __cplusplus\n}\n#endif // #ifdef __cplusplus\n\n#endif // #ifndef TEST_H\n"
)