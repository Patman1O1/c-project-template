# Declare the project primary target as an executable
set(PROJECT_PRIMARY_TARGET "${PROJECT_NAME}" CACHE STRING "The project's primary target")
add_executable("${PROJECT_PRIMARY_TARGET}")
