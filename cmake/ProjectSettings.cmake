#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include(CheckIPOSupported)
include(CMakePackageConfigHelpers)

#-----------------------------------------------------------------------------------------------------------------------
# CCache
#-----------------------------------------------------------------------------------------------------------------------
message(STATUS "Looking for CCache")
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    message(STATUS "CCache found")
    set(CMAKE_C_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
else()
    message(STATUS "Unable to find CCache")
endif()

#-----------------------------------------------------------------------------------------------------------------------
# Interprocedural Optimisation (IPO)
#-----------------------------------------------------------------------------------------------------------------------
message(STATUS "Checking if interprocedural optimisation (IPO) is available")
check_ipo_supported(RESULT result OUTPUT output)
if(result)
    message(STATUS "IPO is available")
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
else()
    message(SEND_ERROR "IPO not available: ${output}")
endif()

#-----------------------------------------------------------------------------------------------------------------------
# CMake Package Configuration
#-----------------------------------------------------------------------------------------------------------------------
configure_package_config_file(
        "${PROJECT_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in"
        "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
        INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}"
)

write_basic_package_version_file(
        "${PROJECT_NAME}ConfigVersion.cmake"
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY AnyNewerVersion
        ARCH_INDEPENDENT
)
