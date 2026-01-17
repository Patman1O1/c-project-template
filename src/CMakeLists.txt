cmake_minimum_required(VERSION ${CMAKE_MINIMUM_REQUIRED_VERSION})

list(APPEND SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/main.c")
source_group(TREE "${CMAKE_CURRENT_SOURCE_DIR}" FILES ${SOURCES})

add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE ${SOURCES})
