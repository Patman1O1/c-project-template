# Declare the project primary target as a executable
set(PROJECT_PRIMARY_TARGET "${PROJECT_NAME_SNAKE_CASE}" CACHE STRING "The primary target that this project will build")
add_executable("${PROJECT_PRIMARY_TARGET}")
