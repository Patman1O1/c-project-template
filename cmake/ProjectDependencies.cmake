#-----------------------------------------------------------------------------------------------------------------------
# GoogleTest
#-----------------------------------------------------------------------------------------------------------------------
find_package(GTest REQUIRED)
include(GoogleTest)

#-----------------------------------------------------------------------------------------------------------------------
# CCache
#-----------------------------------------------------------------------------------------------------------------------
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    message(STATUS "CCache found")
    set(CMAKE_C_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
else()
    message(STATUS "CCache not found")
endif()

#-----------------------------------------------------------------------------------------------------------------------
# Interprocedural Optimisation (IPO)
#-----------------------------------------------------------------------------------------------------------------------
include(CheckIPOSupported)
check_ipo_supported(RESULT result OUTPUT output)
if(result)
    message(STATUS "IPO is available")
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
else()
    message(SEND_ERROR "IPO is unavailable: ${output}")
endif()

#-----------------------------------------------------------------------------------------------------------------------
# CPack
#-----------------------------------------------------------------------------------------------------------------------
set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
set(CPACK_SOURCE_IGNORE_FILES
        /.git
        /.vscode
        /.*build.*
        /\\\\.gitignore
        /\\\\.DS_Store
)
include(CPack)
