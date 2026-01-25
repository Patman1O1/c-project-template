#-----------------------------------------------------------------------------------------------------------------------
# Includes
#-----------------------------------------------------------------------------------------------------------------------
include("${CMAKE_SOURCE_DIR}/.github/cmake/executable/ExecutableInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/executable/ExecutableDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/interface_library/InterfaceLibraryInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/interface_library/InterfaceLibraryDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/static_library/StaticLibraryInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/static_library/StaticLibraryDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/shared_library/SharedLibraryInit.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/shared_library/SharedLibraryDefinition.cmake")
include("${CMAKE_SOURCE_DIR}/.github/cmake/functions.cmake")

#-----------------------------------------------------------------------------------------------------------------------
# Variables
#-----------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------------------------------------
function(configure_executable PROJECT_NAME)
    # Format the project name
    to_pascal_case("${PROJECT_NAME}" PROJECT_NAME_PASCAL_CASE)
    to_snake_case("${PROJECT_NAME}" PROJECT_NAME_SNAKE_CASE)
    to_kebab_case("${PROJECT_NAME}" PROJECT_NAME_KEBAB_CASE)
    string(TOUPPER "${PROJECT_NAME_SNAKE_CASE}" PROJECT_NAME_SCREAMING_CASE)

    # Configure the root directory CMakeLists.txt file
    configure_file("${CMAKE_SOURCE_DIR}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/CMakeLists.txt"
                   @ONLY)

    # Configure conanfile.py
    file(REMOVE "${CMAKE_SOURCE_DIR}/conanfile.py.in")
    configure_file("${CMAKE_SOURCE_DIR}/conanfile.py.in"
                   "${CMAKE_SOURCE_DIR}/conanfile.py"
                   @ONLY)

    # Rename directories
    file(COPY "${CMAKE_SOURCE_DIR}/src/template" DESTINATION "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/template")
    file(COPY "${CMAKE_SOURCE_DIR}/test/template" DESTINATION "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/test/template")
endfunction()

function(configure_static_library PROJECT_NAME)
    # Format the project name
    to_pascal_case("${PROJECT_NAME}" PROJECT_NAME_PASCAL_CASE)
    to_snake_case("${PROJECT_NAME}" PROJECT_NAME_SNAKE_CASE)
    to_kebab_case("${PROJECT_NAME}" PROJECT_NAME_KEBAB_CASE)
    string(TOUPPER "${PROJECT_NAME_SNAKE_CASE}" PROJECT_NAME_SCREAMING_CASE)

    # Configure the root directory CMakeLists.txt file
    configure_file("${CMAKE_SOURCE_DIR}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/CMakeLists.txt"
                   @ONLY)

    # Configure conanfile.py
    file(REMOVE "${CMAKE_SOURCE_DIR}/conanfile.py.in")
    configure_file("${CMAKE_SOURCE_DIR}/conanfile.py.in"
                   "${CMAKE_SOURCE_DIR}/conanfile.py"
                   @ONLY)

    # Rename directories
    file(COPY "${CMAKE_SOURCE_DIR}/src/template" DESTINATION "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/template")
    file(COPY "${CMAKE_SOURCE_DIR}/test/template" DESTINATION "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/test/template")
endfunction()

function(configure_shared_library PROJECT_NAME)
    # Format the project name
    to_pascal_case("${PROJECT_NAME}" PROJECT_NAME_PASCAL_CASE)
    to_snake_case("${PROJECT_NAME}" PROJECT_NAME_SNAKE_CASE)
    to_kebab_case("${PROJECT_NAME}" PROJECT_NAME_KEBAB_CASE)
    string(TOUPPER "${PROJECT_NAME_SNAKE_CASE}" PROJECT_NAME_SCREAMING_CASE)

    # Configure the root directory CMakeLists.txt file
    configure_file("${CMAKE_SOURCE_DIR}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/CMakeLists.txt"
                   @ONLY)

    # Configure conanfile.py
    file(REMOVE "${CMAKE_SOURCE_DIR}/conanfile.py.in")
    configure_file("${CMAKE_SOURCE_DIR}/conanfile.py.in"
                   "${CMAKE_SOURCE_DIR}/conanfile.py"
                   @ONLY)

    # Rename directories
    file(COPY "${CMAKE_SOURCE_DIR}/src/template" DESTINATION "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/template")
    file(COPY "${CMAKE_SOURCE_DIR}/test/template" DESTINATION "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/test/template")
endfunction()

function(configure_interface_library PROJECT_NAME)
    # Format the project name
    to_pascal_case("${PROJECT_NAME}" PROJECT_NAME_PASCAL_CASE)
    to_snake_case("${PROJECT_NAME}" PROJECT_NAME_SNAKE_CASE)
    to_kebab_case("${PROJECT_NAME}" PROJECT_NAME_KEBAB_CASE)
    string(TOUPPER "${PROJECT_NAME_SNAKE_CASE}" PROJECT_NAME_SCREAMING_CASE)

    # Configure the root directory CMakeLists.txt file
    configure_file("${CMAKE_SOURCE_DIR}/CMakeLists.txt.in"
                   "${CMAKE_SOURCE_DIR}/CMakeLists.txt"
                   @ONLY)

    # Configure conanfile.py
    file(REMOVE "${CMAKE_SOURCE_DIR}/conanfile.py.in")
    configure_file("${CMAKE_SOURCE_DIR}/conanfile.py.in"
                   "${CMAKE_SOURCE_DIR}/conanfile.py"
                   @ONLY)

    # Rename directories
    file(COPY "${CMAKE_SOURCE_DIR}/src/template" DESTINATION "${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/src/template")
    file(COPY "${CMAKE_SOURCE_DIR}/test/template" DESTINATION "${CMAKE_SOURCE_DIR}/test/${PROJECT_NAME_SNAKE_CASE}")
    file(REMOVE_RECURSE "${CMAKE_SOURCE_DIR}/test/template")
endfunction()
