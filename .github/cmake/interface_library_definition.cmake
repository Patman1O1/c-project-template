# Define the primary target as an interface library
add_library(${PROJECT_PRIMARY_TARGET} INTERFACE)
add_library(${PROJECT_NAMESPACE}::${PROJECT_PRIMARY_TARGET} ALIAS ${PROJECT_PRIMARY_TARGET}})

# Include directories
target_include_directories(${PROJECT_PRIMARY_TARGET}
        PRIVATE
            "${CMAKE_SOURCE_DIR}/include/${PROJECT_PRIMARY_TARGET}"
        PUBLIC
            "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>"
            "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>"
)
