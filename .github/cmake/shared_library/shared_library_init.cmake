# Declare the project primary target as a shared library
set(PROJECT_PRIMARY_TARGET "${PROJECT_NAME}" CACHE STRING "The primary target that this project will build")
add_library("${PROJECT_PRIMARY_TARGET}" SHARED)
add_library("${PROJECT_NAMESPACE}"::"${PROJECT_NAME}" ALIAS "${PROJECT_PRIMARY_TARGET}")
