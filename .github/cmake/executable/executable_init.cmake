# Declare the project primary target as a executable
set(PROJECT_PRIMARY_TARGET "${PROJECT_NAME}" CACHE STRING "The primary target that this project will build")
add_executable("${PROJECT_PRIMARY_TARGET}")
