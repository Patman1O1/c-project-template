# Builtin Imports
import shutil
from pathlib import Path
from typing import Final, Any, Generator
import tempfile

# Pip Imports
import pytest

# Local Imports
from cproject.project import Project
from cproject.project import CMake
from cproject.format import to_screaming_case

CMAKE: Final[CMake] = CMake(version="4.3.0", c_std=23, cxx_std=23)
TEST_NAMES: Final[dict[str, str]] = {
    "Executable": "c-executable",
    "Static Library": "c-static",
    "Shared Library": "c-shared",
    "Interface Library": "c-interface",
}

# Every project type renders to the same on-disk layout; only file *contents*
# vary by type. Paths use {name}/{namespace}/{package} placeholders that each
# test fills in from the rendered Project.
COMMON_LAYOUT: Final[tuple[str, ...]] = (
    "CMakeLists.txt",
    "conanfile.py",
    "LICENSE",
    "README.md",
    "cmake/cmake_uninstall.cmake",
    "cmake/{package}Config.cmake.in",
    "include/{namespace}/export.h",
    "include/{namespace}/{name}.h",
    "src/CMakeLists.txt",
    "src/main.c",
    "src/{name}.c",
    "tests/CMakeLists.txt",
    "tests/{name}_test.cpp",
    "test_package/CMakeLists.txt",
    "test_package/conanfile.py",
    "test_package/src/CMakeLists.txt",
    "test_package/src/main.c",
)


@pytest.fixture()
def temp_dir() -> Generator[Path, Any, None]:
    tempdir: Path = Path(tempfile.mkdtemp())
    yield tempdir
    shutil.rmtree(tempdir)


def _render(project_type: str,
            project_name: str,
            temp_dir: Path,
            monkeypatch: pytest.MonkeyPatch) -> Project:
    """Render the template for a single project type in isolation.

    ``render()`` rewrites templates in place relative to ``Project.ROOT``, so we
    copy the template tree into a throwaway directory, point ``Project.ROOT`` at
    the copy (it also backs the Jinja loader built in ``__init__``), and render
    there. The real template on disk is never touched. Returns the rendered
    ``Project`` so callers can read back its computed name/namespace/package.
    """
    template_root: Path = temp_dir / "template"
    shutil.copytree(Project.ROOT, template_root)

    # Redirect the class-level root *before* constructing the Project, because
    # __init__ wires the Jinja FileSystemLoader to Project.ROOT.
    monkeypatch.setattr(Project, "ROOT", template_root)

    project: Project = Project(project_name, project_type, "Test Author")
    project.render(CMAKE)
    return project


def _read(*parts: str) -> str:
    return Project.ROOT.joinpath(*parts).read_text(encoding="utf-8")


def _assert_common_layout(project: Project) -> None:
    """Every expected rendered file exists and no template markers survive."""
    fmt: dict[str, str] = {
        "name": project.name,
        "namespace": project.namespace,
        "package": project.package_name,
    }
    for rel in COMMON_LAYOUT:
        path: Path = Project.ROOT / rel.format(**fmt)
        assert path.is_file(), f"expected rendered file missing: {path}"

    # Nothing should still carry a '.j2' suffix or an unresolved '{{ ... }}'.
    for path in Project.ROOT.rglob("*"):
        assert not path.name.endswith(".j2"), f"unrendered template left behind: {path}"
        assert "{{" not in path.name, f"unresolved name placeholder: {path}"


# ── type property setter ──────────────────────────────────────────────────────────────────────────────────────────────
def test__type_property_setter__invalid_type() -> None:
    with pytest.raises(ValueError):
        Project("test", "Invalid Type", "Bill Gates")

def test__type_property_setter__executable() -> None:
    project: Project = Project("test", "Executable", "Jeffrey Dahmer")
    assert project.type == "Executable"

def test__type_property_setter__static_library() -> None:
    project: Project = Project("test", "Static Library", "Peter Griffin")
    assert project.type == "Static Library"

def test__type_property_setter__shared_library() -> None:
    project: Project = Project("test", "Shared Library", "Linus Torvalds")
    assert project.type == "Shared Library"

def test__type_property_setter__interface_library() -> None:
    project: Project = Project("test", "Interface Library", "Donald Trump")
    assert project.type == "Interface Library"


# ── render ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__render__executable(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Executable", TEST_NAMES["Executable"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_namespace: str = project.namespace

    _assert_common_layout(project)

    # CMakeLists.txt
    cmake_lists_txt: str = _read("CMakeLists.txt")
    assert f'project("{project_name}"' in cmake_lists_txt
    assert "option(BUILD_SHARED_LIBS" not in cmake_lists_txt
    assert 'option(BUILD_TESTS "Build the project\'s test suite" OFF)' in cmake_lists_txt
    assert "configure_package_config_file(" not in cmake_lists_txt
    assert "write_basic_package_version_file(" not in cmake_lists_txt
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" not in cmake_lists_txt
    assert f"add_library({project_name}_headers INTERFACE)" in cmake_lists_txt
    assert f"add_library({project_name} INTERFACE)" not in cmake_lists_txt
    assert "add_subdirectory(src)" in cmake_lists_txt

    # conanfile.py
    conanfile_py: str = _read("conanfile.py")
    assert "build_shared_libs" not in conanfile_py
    assert f"        self.tool_requires(\"cmake/[>={CMAKE.version}]\")" in conanfile_py
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' not in conanfile_py

    # src/CMakeLists.txt
    src_cmake_lists_txt: str = _read("src", "CMakeLists.txt")
    assert f"add_executable({project_name})" in src_cmake_lists_txt
    assert f"add_executable({project_namespace}::{project_name} ALIAS {project_name})" in src_cmake_lists_txt
    assert f"add_library({project_name} STATIC)" not in src_cmake_lists_txt
    assert f"add_library({project_name} SHARED)" not in src_cmake_lists_txt
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" in src_cmake_lists_txt
    assert f"install(TARGETS {project_name} {project_name}_headers" in src_cmake_lists_txt
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" in src_cmake_lists_txt
    assert "include(GenerateExportHeader)" not in src_cmake_lists_txt
    assert "export_shared.h" not in src_cmake_lists_txt
    assert "export_static.h" not in src_cmake_lists_txt
    assert f"install(EXPORT {project_name}_export" not in src_cmake_lists_txt

def test__render__static_library(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Static Library", TEST_NAMES["Static Library"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_package_name: str = project.package_name
    project_macro_name: str = to_screaming_case(project_name)
    project_namespace: str = project.namespace

    _assert_common_layout(project)

    # CMakeLists.txt
    cmake_lists_txt: str = _read("CMakeLists.txt")
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" OFF)' in cmake_lists_txt
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" ON)' not in cmake_lists_txt
    assert "configure_package_config_file(" in cmake_lists_txt
    assert "write_basic_package_version_file(" in cmake_lists_txt
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" in cmake_lists_txt
    assert f"add_library({project_name} INTERFACE)" not in cmake_lists_txt
    assert "add_subdirectory(src)" in cmake_lists_txt

    # conanfile.py
    conanfile_py: str = _read("conanfile.py")
    assert '"build_shared_libs": [True, False]' in conanfile_py
    assert '"build_shared_libs": False,' in conanfile_py
    assert '"build_shared_libs": True,' not in conanfile_py
    assert f"        self.tool_requires(\"cmake/[>={CMAKE.version}]\")" in conanfile_py
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' in conanfile_py

    # include/<project_namespace>
    assert Path(temp_dir/"template"/"include"/f"{project_namespace}").exists()

    # include/<project_namespace>/export.h
    export_h: str = _read("include", f"{project_name}", "export.h")
    assert f"#ifndef {project_macro_name}_STATIC_DEFINE" in export_h
    assert f"    #include <{project_name}/export_shared.h>" in export_h
    assert f"    #include <{project_name}/export_static.h>" in export_h
    assert f"#endif // #ifndef {project_macro_name}_STATIC_DEFINE" in export_h

    # include/<project_namespace>/<project_name>.h
    project_name_h: str = _read("include", f"{project_name}", f"{project_name}.h")
    assert Path(temp_dir/"template"/"include"/f"{project_namespace}"/f"{project_name}.h").exists()
    assert f"#ifndef {project_macro_name}_H" in project_name_h
    assert f"#define {project_macro_name}_H" in project_name_h
    assert f"#endif // #ifndef {project_macro_name}_H" in project_name_h

    # src/CMakeLists.txt
    src_cmake_lists_txt: str = _read("src", "CMakeLists.txt")
    assert f"add_library({project_name} STATIC)" in src_cmake_lists_txt
    assert f"add_library({project_name} SHARED)" not in src_cmake_lists_txt
    assert f"add_executable({project_name})" not in src_cmake_lists_txt
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" not in src_cmake_lists_txt
    assert "include(GenerateExportHeader)" in src_cmake_lists_txt
    assert "set(EXPORT_HEADER_FILE export_shared.h)" in src_cmake_lists_txt
    assert "set(EXPORT_HEADER_FILE export_static.h)" in src_cmake_lists_txt
    assert f"{project_package_name}SharedTargets.cmake" in src_cmake_lists_txt
    assert f"{project_package_name}StaticTargets.cmake" in src_cmake_lists_txt
    assert f"{project_macro_name}_STATIC_DEFINE" in src_cmake_lists_txt
    assert f"generate_export_header({project_name}" in src_cmake_lists_txt
    assert f"install(EXPORT {project_name}_export" in src_cmake_lists_txt
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" not in src_cmake_lists_txt

    # src/<project_name>.c
    project_name_c: str = _read("src", f"{project_name}.c")
    assert Path(temp_dir/"template"/"src"/f"{project_name}.c").exists()
    assert f"#include \"{project_namespace}/{project_name}.h\"" in project_name_c


def test__render__shared_library(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Shared Library", TEST_NAMES["Shared Library"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_package_name: str = project.package_name
    project_macro_name: str = to_screaming_case(project_name)
    project_namespace: str = project.namespace

    _assert_common_layout(project)

    # CMakeLists.txt
    cmake_lists_txt: str = _read("CMakeLists.txt")
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" ON)' in cmake_lists_txt
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" OFF)' not in cmake_lists_txt
    assert "configure_package_config_file(" in cmake_lists_txt
    assert "write_basic_package_version_file(" in cmake_lists_txt
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" in cmake_lists_txt
    assert f"add_library({project_name} INTERFACE)" not in cmake_lists_txt
    assert "add_subdirectory(src)" in cmake_lists_txt

    # conanfile.py
    conanfile_py: str = _read("conanfile.py")
    assert '"build_shared_libs": [True, False]' in conanfile_py
    assert '"build_shared_libs": True,' in conanfile_py
    assert '"build_shared_libs": False,' not in conanfile_py
    assert f"        self.tool_requires(\"cmake/[>={CMAKE.version}]\")" in conanfile_py
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' in conanfile_py

    # include/<project_namespace>
    assert Path(temp_dir/"template"/"include"/f"{project_namespace}").exists()

    # include/<project_namespace>/export.h
    export_h: str = _read("include", f"{project_name}", "export.h")
    assert f"#ifndef {project_macro_name}_STATIC_DEFINE" in export_h
    assert f"    #include <{project_name}/export_shared.h>" in export_h
    assert f"    #include <{project_name}/export_static.h>" in export_h
    assert f"#endif // #ifndef {project_macro_name}_STATIC_DEFINE" in export_h

    # include/<project_namespace>/<project_name>.h
    project_name_h: str = _read("include", f"{project_name}", f"{project_name}.h")
    assert Path(temp_dir/"template"/"include"/f"{project_namespace}"/f"{project_name}.h").exists()
    assert f"#ifndef {project_macro_name}_H" in project_name_h
    assert f"#define {project_macro_name}_H" in project_name_h
    assert f"#endif // #ifndef {project_macro_name}_H" in project_name_h

    # src/CMakeLists.txt
    src_cmake_lists_txt: str = _read("src", "CMakeLists.txt")
    assert f"add_library({project_name} SHARED)" in src_cmake_lists_txt
    assert f"add_library({project_name} STATIC)" not in src_cmake_lists_txt
    assert f"add_executable({project_name})" not in src_cmake_lists_txt
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" not in src_cmake_lists_txt
    assert "include(GenerateExportHeader)" in src_cmake_lists_txt
    assert "set(EXPORT_HEADER_FILE export_shared.h)" in src_cmake_lists_txt
    assert "set(EXPORT_HEADER_FILE export_static.h)" in src_cmake_lists_txt
    assert f"{project_package_name}SharedTargets.cmake" in src_cmake_lists_txt
    assert f"{project_package_name}StaticTargets.cmake" in src_cmake_lists_txt
    assert f"{project_macro_name}_STATIC_DEFINE" in src_cmake_lists_txt
    assert f"generate_export_header({project_name}" in src_cmake_lists_txt
    assert f"install(EXPORT {project_name}_export" in src_cmake_lists_txt
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" not in src_cmake_lists_txt

    # src/<project_name>.c
    project_name_c: str = _read("src", f"{project_name}.c")
    assert Path(temp_dir / "template" / "src" / f"{project_name}.c").exists()
    assert f"#include \"{project_namespace}/{project_name}.h\"" in project_name_c


def test__render__interface_library(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Interface Library", TEST_NAMES["Interface Library"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_macro_name: str = to_screaming_case(project_name)
    project_namespace: str = project.namespace

    _assert_common_layout(project)

    # CMakeLists.txt
    cmake_lists_txt: str = _read("CMakeLists.txt")
    assert "option(BUILD_SHARED_LIBS" not in cmake_lists_txt
    assert "configure_package_config_file(" in cmake_lists_txt
    assert "write_basic_package_version_file(" in cmake_lists_txt
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" in cmake_lists_txt
    assert f"add_library({project_name} INTERFACE)" in cmake_lists_txt
    assert f"add_library({project_namespace}::{project_name} ALIAS {project_name})" in cmake_lists_txt
    assert f"target_link_libraries({project_name}" in cmake_lists_txt
    assert f"{project_namespace}::{project_name}_headers" in cmake_lists_txt
    assert f"install(TARGETS {project_name}" in cmake_lists_txt
    assert "add_subdirectory(src)" not in cmake_lists_txt

    # conanfile.py
    conanfile_py: str = _read("conanfile.py")
    assert "build_shared_libs" not in conanfile_py
    assert f"        self.tool_requires(\"cmake/[>={CMAKE.version}]\")" in conanfile_py
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' not in conanfile_py

    # include/<project_namespace>
    assert Path(temp_dir/"template"/"include"/f"{project_namespace}").exists()

    # include/<project_namespace>/<project_name>.h
    project_name_h: str = _read("include", f"{project_name}", f"{project_name}.h")
    assert Path(temp_dir/"template"/"include"/f"{project_namespace}"/f"{project_name}.h").exists()
    assert f"#ifndef {project_macro_name}_H" in project_name_h
    assert f"#define {project_macro_name}_H" in project_name_h
    assert f"#endif // #ifndef {project_macro_name}_H" in project_name_h


def test__render__tests(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Executable", TEST_NAMES["Executable"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_namespace: str = project.namespace

    # test/CMakeLists.txt
    cmake_lists_txt: str = _read("tests", "CMakeLists.txt")
    assert f"set(CMAKE_CXX_STANDARD {CMAKE.cxx_std})" in cmake_lists_txt
    assert f"# Target: {project_name}_test" in cmake_lists_txt
    assert f"# Alias: {project_namespace}::{project_name}_test" in cmake_lists_txt
    assert f"# Dependencies: GTest::gtest_main, GTest::gmock_main, {project_namespace}::{project_name}_headers" in cmake_lists_txt
    assert f"add_executable({project_name}_test)" in cmake_lists_txt
    assert f"add_executable({project_namespace}::{project_name}_test ALIAS {project_name}_test)" in cmake_lists_txt
    assert f"target_sources({project_name}_test" in cmake_lists_txt
    assert f"        ${{CMAKE_CURRENT_SOURCE_DIR}}/{project_name}_test.cpp" in cmake_lists_txt
    assert f"target_link_libraries({project_name}_test" in cmake_lists_txt
    assert f"        {project_namespace}::{project_name}_headers" in cmake_lists_txt
    assert f"gtest_discover_tests({project_name}_test)" in cmake_lists_txt

    project_name_test_cpp = _read("tests", f"{project_name}_test.cpp")
    assert Path(temp_dir/"template"/"tests"/f"{project_name}_test.cpp").exists()
    assert f"namespace {project_name}_testing {{" in project_name_test_cpp
    assert f"}} // namespace {project_name}_testing" in project_name_test_cpp

def test__render__test_package(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Executable", TEST_NAMES["Executable"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_version: str = project.version
    project_package_name: str = project.package_name
    project_namespace: str = project.namespace

    # test_package/CMakeLists.txt
    cmake_lists_txt: str = _read("test_package", "CMakeLists.txt")
    assert f"cmake_minimum_required(VERSION {CMAKE.version}" in cmake_lists_txt
    assert f"    set(CMAKE_C_STANDARD {CMAKE.c_std})" in cmake_lists_txt
    assert f"find_package({project_package_name} REQUIRED}}" in cmake_lists_txt

    # test_package/conanfile.py
    conanfile_py: str = _read("test_package", "conanfile.py")
    assert f"        self.requires(\"{project_name}/{project_version}\")" in conanfile_py
    assert f"        self.tool_requires(\"cmake/[>={CMAKE.version}]\")" in conanfile_py

    # test_package/src/CMakeLists.txt
    src_cmake_lists_txt: str = _read("test_package", "src", "CMakeLists.txt")
    assert f"# Dependencies: {project_namespace}::{project_name}" in src_cmake_lists_txt
    assert f"        {project_namespace}::{project_name}" in src_cmake_lists_txt

    # test_package/src/main.c.j2
    src_main_c: str = _read("test_package", "src", "main.c")
    assert f"#include <{project_namespace}/{project_name}.h>" in src_main_c

def test__render__name_namespace_package_substitution(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Static Library", "My-Cool-Lib", temp_dir, monkeypatch)

    # Name is snake-cased, package pascal-cased, and an empty namespace falls
    # back to the (snake-cased) name.
    assert project.name == "my_cool_lib"
    assert project.package_name == "MyCoolLib"
    assert project.namespace == "my_cool_lib"

    _assert_common_layout(project)

    # The screaming-case include guard is derived from the name.
    header: str = _read("include", project.namespace, f"{project.name}.h")
    assert "MY_COOL_LIB_H" in header