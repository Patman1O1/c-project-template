# Set the default of BUILD_SHARED_LIBS to ON
option(BUILD_SHARED_LIBS "Build the library as a shared library" ON)

# Declare the project primary target as a shared library
set(PROJECT_PRIMARY_TARGET "${PROJECT_NAME}" CACHE STRING "The project's primary target")
add_library("${PROJECT_PRIMARY_TARGET}")
add_library("${PROJECT_NAMESPACE}"::"${PROJECT_PRIMARY_TARGET}" ALIAS "${PROJECT_PRIMARY_TARGET}")
