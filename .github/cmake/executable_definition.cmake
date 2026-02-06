# Define the primary target as an executable
add_executable(${PROJECT_PRIMARY_TARGET})

# Set properties
set_target_properties(${PROJECT_PRIMARY_TARGET} PROPERTIES
        OUTPUT_NAME ${PROJECT_OUTPUT_NAME}
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
)

# Include directories
target_include_directories(${PROJECT_PRIMARY_TARGET}
        PRIVATE
            "${CMAKE_SOURCE_DIR}/include/${PROJECT_PRIMARY_TARGET}"
        PUBLIC
            "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>"
            "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)

# Set sources
target_sources(${PROJECT_PRIMARY_TARGET}
        PRIVATE
            "${CMAKE_SOURCE_DIR}/src/${PROJECT_PRIMARY_TARGET}/${PROJECT_PRIMARY_TARGET}.c"
            "${CMAKE_SOURCE_DIR}/src/${PROJECT_PRIMARY_TARGET}/main.c"
)

# Define installation rules
if(NOT CMAKE_SKIP_INSTALL_RULES)
    include(GNUInstallDirs)

    install(TARGETS ${PROJECT_PRIMARY_TARGET}
            RUNTIME COMPONENT ${PROJECT_PRIMARY_TARGET}
            DESTINATION "${CMAKE_INSTALL_BINDIR}"
    )
endif()
