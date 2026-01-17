cmake_minimum_required(VERSION ${CMAKE_MINIMUM_REQUIRED_VERSION})

if(NOT TARGET gtest_main OR NOT TARGET gmock_main)
    FetchContent_Declare(
            googletest
            GIT_REPOSITORY "https://github.com/google/googletest.git"
            GIT_TAG release-1.12.1
    )

    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE) # do not override parent project's runtime settings on Windows
    set(INSTALL_GTEST OFF)

    # For simplicity, always build-presets googletest as static library. This prevents @NAME@-tests executable from
    # complaining about missing googletest DLLs on Windows.
    set(BUILD_SHARED_LIBS OFF)

    FetchContent_MakeAvailable(googletest)
endif()

include(GoogleTest)

list(APPEND SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}_tests.cpp")
source_group(TREE "${CMAKE_CURRENT_SOURCE_DIR}" FILES ${SOURCES})

add_executable(${PROJECT_NAME}_tests)
target_sources(${PROJECT_NAME}_tests PRIVATE ${SOURCES})
target_link_libraries(${LIBRARY_NAME}_tests
        PRIVATE
            gtest_main
            gmock_main
)
gtest_discover_tests(${PROJECT_NAME}_tests)
