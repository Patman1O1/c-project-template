# Declare the project primary target as a interface library
set(PROJECT_PRIMARY_TARGET "${PROJECT_NAME_SNAKE_CASE}" CACHE STRING "The primary target that this project will build")
add_library("${PROJECT_PRIMARY_TARGET}" INTERFACE)
add_library("${PROJECT_NAMESPACE}"::"${PROJECT_NAME}" ALIAS "${PROJECT_PRIMARY_TARGET}")
