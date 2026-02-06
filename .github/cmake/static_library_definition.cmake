# Set the default value of BUILD_SHARED_LIBS to OFF
option(BUILD_SHARED_LIBS "Build the library as a shared library" OFF)

# Declare the project primary target as a static library
add_library(${PROJECT_PRIMARY_TARGET})
add_library(${PROJECT_NAMESPACE}::${PROJECT_PRIMARY_TARGET} ALIAS ${PROJECT_PRIMARY_TARGET})

include(GenerateExportHeader)

# Set the primary target's header files
set(PROJECT_PRIMARY_TARGET_HEADERS "include/${PROJECT_PRIMARY_TARGET}.h" PARENT_SCOPE)

# Set the primary target's source files
set(PROJECT_PRIMARY_TARGET_SOURCES "${PROJECT_PRIMARY_TARGET}.c" PARENT_SCOPE)

if(NOT BUILD_SHARED_LIBS)
    # Set the primary target's properties
    set_target_properties(${PROJECT_PRIMARY_TARGET} PROPERTIES
            OUTPUT_NAME "${PROJECT_NAME_KEBAB_CASE}"
            VERSION ${PROJECT_VERSION}
            SOVERSION ${PROJECT_VERSION_MAJOR}
            PUBLIC_HEADER "${PROJECT_PRIMARY_TARGET_HEADERS}"
            POSITION_INDEPENDENT_CODE ON
    )

    # Define compile definitions
    target_compile_definitions(${PROJECT_PRIMARY_TARGET}
            PUBLIC
            ${PROJECT_NAME_SCREAMING_CASE}_STATIC_DEFINE
    )

    set(EXPORT_FILE_NAME "export_static.h")
else()
    # Set the primary target's properties
    set_target_properties(${PROJECT_PRIMARY_TARGET} PROPERTIES
            OUTPUT_NAME "${PROJECT_NAME_KEBAB_CASE}"
            VERSION ${PROJECT_VERSION}
            SOVERSION ${PROJECT_VERSION_MAJOR}
            PUBLIC_HEADER "${PROJECT_PRIMARY_TARGET_HEADERS}"
            C_VISIBILITY_PRESET hidden
            VISIBILITY_INLINES_HIDDEN ON
    )

    # Define compile definitions
    target_compile_definitions(${PROJECT_PRIMARY_TARGET}
            PUBLIC
            $<$<NOT:$<BOOL:${BUILD_SHARED_LIBS}>>:${PROJECT_NAME_SCREAMING_CASE}_STATIC_DEFINE>
    )

    set(EXPORT_FILE_NAME "export_shared.h")
endif()

# Include directories
target_include_directories(${PROJECT_PRIMARY_TARGET}
        PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
        PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/src"
)

# Group all targets
set(PROJECT_TARGETS)
list(APPEND PROJECT_TARGETS "${PROJECT_PRIMARY_TARGET}")

if(NOT CMAKE_SKIP_INSTALL_RULES)
    # Install the library targets
    install(TARGETS ${PROJECT_TARGETS}
            EXPORT "${PROJECT_NAME_PASCAL_CASE}Targets"
            LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
            COMPONENT Runtime
            NAMELINK_COMPONENT Development
            ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
            COMPONENT Development
            RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
            COMPONENT Runtime
            PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME_KEBAB_CASE}"
            COMPONENT Development
            INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    )

    # Install export set (for find_package support)
    install(EXPORT "${PROJECT_NAME_PASCAL_CASE}Targets"
            FILE "${PROJECT_NAME_PASCAL_CASE}Targets"
            NAMESPACE ${PROJECT_NAMESPACE}::
            DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}"
            COMPONENT Development
    )

    # Generate the configuration file that includes the project exports
    include(CMakePackageConfigHelpers)
    configure_package_config_file(
            "${CMAKE_SOURCE_DIR}/cmake/${PROJECT_NAME_PASCAL_CASE}Config.cmake.in"
            "${CMAKE_BINARY_DIR}/${PROJECT_NAME_PASCAL_CASE}Config.cmake"
            INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}"
            NO_SET_AND_CHECK_MACRO
            NO_CHECK_REQUIRED_COMPONENTS_MACRO
    )

    # Generate the version file for the configuration file
    write_basic_package_version_file(
            "${CMAKE_BINARY_DIR}/${PROJECT_NAME_PASCAL_CASE}ConfigVersion.cmake"
            VERSION ${PROJECT_VERSION}
            COMPATIBILITY SameMajorVersion
    )

    # Install the configuration files
    install(FILES
            "${CMAKE_BINARY_DIR}/${PROJECT_NAME_PASCAL_CASE}Config.cmake"
            "${CMAKE_BINARY_DIR}/${PROJECT_NAME_PASCAL_CASE}ConfigVersion.cmake"
            DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}"
            COMPONENT Development
    )

    # Export the project
    export(EXPORT ${PROJECT_NAME_PASCAL_CASE}Targets
            FILE "${CMAKE_BINARY_DIR}/${PROJECT_NAME_PASCAL_CASE}Targets.cmake"
            NAMESPACE ${PROJECT_NAMESPACE}::
    )
    export(PACKAGE ${PROJECT_NAME})
endif()
