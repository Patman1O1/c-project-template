# Set BUILD_SHARED_LIBS to false and set the library type to static
option(BUILD_SHARED_LIBS "Build the primary target as a shared library" ON)

# Declare the project primary target as a static library
add_library("${PROJECT_NAME}")
add_library("${PROJECT_NAMESPACE}"::"${PROJECT_NAME}" ALIAS "${PROJECT_NAME}")

# Set the project's output name
set(PROJECT_OUTPUT_NAME "${PROJECT_NAME_KEBAB_CASE}")
