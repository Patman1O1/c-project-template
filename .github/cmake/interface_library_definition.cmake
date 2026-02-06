# Define the primary target as an interface library
add_library(${PROJECT_PRIMARY_TARGET} INTERFACE)
add_library(${PROJECT_NAMESPACE}::${PROJECT_PRIMARY_TARGET} ALIAS ${PROJECT_PRIMARY_TARGET})

# Include directories
target_include_directories(${PROJECT_PRIMARY_TARGET}
        PRIVATE
            "${CMAKE_SOURCE_DIR}/include/${PROJECT_PRIMARY_TARGET}"
        PUBLIC
            "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>"
            "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)

# Initialize export files
include(GenerateExportHeader)
set(EXPORT_HEADER_FILE)
set(EXPORT_TARGET_FILE)

if(NOT CMAKE_SKIP_INSTALL_RULES)
    # Generate the configuration file that includes the project exports
    include(CMakePackageConfigHelpers)
    configure_package_config_file(
            "${CMAKE_SOURCE_DIR}/cmake/${PROJECT_PACKAGE_NAME}Config.cmake.in"
            "${CMAKE_BINARY_DIR}/${PROJECT_PACKAGE_NAME}Config.cmake"
            INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_OUTPUT_NAME}"
            NO_SET_AND_CHECK_MACRO
            NO_CHECK_REQUIRED_COMPONENTS_MACRO
    )

    # Generate the version file for the configuration file
    write_basic_package_version_file(
            "${CMAKE_BINARY_DIR}/${PROJECT_PACKAGE_NAME}ConfigVersion.cmake"
            VERSION ${PROJECT_VERSION}
            COMPATIBILITY SameMajorVersion
    )

    # Install package files
    install(FILES
            "${CMAKE_BINARY_DIR}/${PROJECT_PACKAGE_NAME}Config.cmake"
            "${CMAKE_BINARY_DIR}/${PROJECT_PACKAGE_NAME}ConfigVersion.cmake"
            COMPONENT ${PROJECT_OUTPUT_NAME}-dev
            DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_OUTPUT_NAME}")

    # Create export files
    include(GenerateExportHeader)
    set(EXPORT_HEADER_FILE "export_static.h")
    set(EXPORT_TARGET_FILE "${PROJECT_EXPORT_NAME}StaticTargets.cmake")
    if(BUILD_SHARED_LIBS)
        set(EXPORT_HEADER_FILE "export_shared.h")
        set(EXPORT_TARGET_FILE "${PROJECT_PACKAGE_NAME}SharedTargets.cmake")
    endif()

    # Install the library target
    install(TARGETS ${PROJECT_PRIMARY_TARGET} EXPORT ${PROJECT_PRIMARY_TARGET}_export
            RUNTIME COMPONENT ${PROJECT_OUTPUT_NAME}
            LIBRARY COMPONENT ${PROJECT_OUTPUT_NAME} NAMELINK_COMPONENT ${PROJECT_OUTPUT_NAME}-dev
            ARCHIVE COMPONENT ${PROJECT_OUTPUT_NAME}-dev
            INCLUDES DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")

    # Install the library headers
    install(DIRECTORY "include/"
            TYPE INCLUDE
            COMPONENT ${PROJECT_OUTPUT_NAME}-dev)
    install(FILES "${CMAKE_BINARY_DIR}/include/${PROJECT_PRIMARY_TARGET}/${EXPORT_HEADER_FILE}"
            COMPONENT ${PROJECT_OUTPUT_NAME}-dev
            DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_OUTPUT_NAME}")

    # Install export files
    install(EXPORT ${PROJECT_PRIMARY_TARGET}_export
            COMPONENT mylib-dev
            FILE "${targets_file}"
            DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_OUTPUT_NAME}"
            NAMESPACE ${PROJECT_NAMESPACE}::)

endif()