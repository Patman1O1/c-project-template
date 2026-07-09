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
    "test/CMakeLists.txt",
    "test/{name}_test.cpp",
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
    n: str = project.name
    ns: str = project.namespace

    _assert_common_layout(project)

    # ── root CMakeLists.txt ──
    root: str = _read("CMakeLists.txt")
    assert f'project("{n}"' in root
    # BUILD_SHARED_LIBS: neither the Shared (ON) nor Static (OFF) arm fires.
    assert "option(BUILD_SHARED_LIBS" not in root
    assert 'option(BUILD_TESTS "Build the project\'s test suite" OFF)' in root
    # Installation arm (type != Executable) is skipped for an executable.
    assert "configure_package_config_file(" not in root
    assert "write_basic_package_version_file(" not in root
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" not in root
    # Interface-target arm is skipped; only the unconditional headers target remains.
    assert f"add_library({n}_headers INTERFACE)" in root
    assert f"add_library({n} INTERFACE)" not in root
    # Subdirectory arm (type != Interface) is taken.
    assert "add_subdirectory(src)" in root

    # ── conanfile.py ──
    conan: str = _read("conanfile.py")
    # No build_shared_libs option, default, or toolchain variable for an executable.
    assert "build_shared_libs" not in conan
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' not in conan

    # ── src/CMakeLists.txt ──
    src: str = _read("src", "CMakeLists.txt")
    # Executable target-definition arm.
    assert f"add_executable({n})" in src
    assert f"add_executable({ns}::{n} ALIAS {n})" in src
    assert f"add_library({n} STATIC)" not in src
    assert f"add_library({n} SHARED)" not in src
    # main.c source arm (Executable only).
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" in src
    # Executable installation arm taken; library export arm skipped.
    assert f"install(TARGETS {n} {n}_headers" in src
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" in src
    assert "include(GenerateExportHeader)" not in src
    assert "export_shared.h" not in src
    assert "export_static.h" not in src
    assert f"install(EXPORT {n}_export" not in src

def test__render__static_library(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Static Library", TEST_NAMES["Static Library"], temp_dir, monkeypatch)
    n: str = project.name
    pkg: str = project.package_name
    scream: str = to_screaming_case(n)

    _assert_common_layout(project)

    # ── root CMakeLists.txt ──
    root: str = _read("CMakeLists.txt")
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" OFF)' in root
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" ON)' not in root
    assert "configure_package_config_file(" in root
    assert "write_basic_package_version_file(" in root
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" in root
    assert f"add_library({n} INTERFACE)" not in root
    assert "add_subdirectory(src)" in root

    # ── conanfile.py ──
    conan: str = _read("conanfile.py")
    assert '"build_shared_libs": [True, False]' in conan     # options arm
    assert '"build_shared_libs": False,' in conan            # default arm (Static)
    assert '"build_shared_libs": True,' not in conan
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' in conan  # generate() arm

    # ── src/CMakeLists.txt ──
    src: str = _read("src", "CMakeLists.txt")
    assert f"add_library({n} STATIC)" in src
    assert f"add_library({n} SHARED)" not in src
    assert f"add_executable({n})" not in src
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" not in src
    # Export-configuration arm; both static and shared halves are emitted.
    assert "include(GenerateExportHeader)" in src
    assert "set(EXPORT_HEADER_FILE export_shared.h)" in src
    assert "set(EXPORT_HEADER_FILE export_static.h)" in src
    assert f"{pkg}SharedTargets.cmake" in src
    assert f"{pkg}StaticTargets.cmake" in src
    assert f"{scream}_STATIC_DEFINE" in src
    assert f"generate_export_header({n}" in src
    assert f"install(EXPORT {n}_export" in src
    # Executable install arm not taken.
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" not in src


def test__render__shared_library(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Shared Library", TEST_NAMES["Shared Library"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_package_name: str = project.package_name
    project_macro_name: str = to_screaming_case(project_name)

    _assert_common_layout(project)

    # CMakeLists.txt
    root: str = _read("CMakeLists.txt")
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" ON)' in root
    assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" OFF)' not in root
    assert "configure_package_config_file(" in root
    assert "write_basic_package_version_file(" in root
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" in root
    assert f"add_library({project_name} INTERFACE)" not in root
    assert "add_subdirectory(src)" in root

    # conanfile.py
    conan: str = _read("conanfile.py")
    assert '"build_shared_libs": [True, False]' in conan
    assert '"build_shared_libs": True,' in conan
    assert '"build_shared_libs": False,' not in conan
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' in conan

    # src/CMakeLists.txt
    src: str = _read("src", "CMakeLists.txt")
    assert f"add_library({project_name} SHARED)" in src
    assert f"add_library({project_name} STATIC)" not in src
    assert f"add_executable({project_name})" not in src
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" not in src
    assert "include(GenerateExportHeader)" in src
    assert "set(EXPORT_HEADER_FILE export_shared.h)" in src
    assert "set(EXPORT_HEADER_FILE export_static.h)" in src
    assert f"{project_package_name}SharedTargets.cmake" in src
    assert f"{project_package_name}StaticTargets.cmake" in src
    assert f"{project_macro_name}_STATIC_DEFINE" in src
    assert f"generate_export_header({project_name}" in src
    assert f"install(EXPORT {project_name}_export" in src
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" not in src


def test__render__interface_library(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project: Project = _render("Interface Library", TEST_NAMES["Interface Library"], temp_dir, monkeypatch)
    project_name: str = project.name
    project_namespace: str = project.namespace

    _assert_common_layout(project)

    # root CMakeLists.txt
    root: str = _read("CMakeLists.txt")
    assert "option(BUILD_SHARED_LIBS" not in root
    assert "configure_package_config_file(" in root
    assert "write_basic_package_version_file(" in root
    assert "install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include" in root
    # Interface-target arm taken: target, alias, deps, properties, install.
    assert f"add_library({project_name} INTERFACE)" in root
    assert f"add_library({project_namespace}::{project_name} ALIAS {project_name})" in root
    assert f"target_link_libraries({project_name}" in root
    assert f"{project_namespace}::{project_name}_headers" in root
    assert f"install(TARGETS {project_name}" in root
    # src is not added for a header-only library.
    assert "add_subdirectory(src)" not in root

    # conanfile.py
    conan: str = _read("conanfile.py")
    assert "build_shared_libs" not in conan
    assert 'toolchain.variables["BUILD_SHARED_LIBS"]' not in conan

    # src/CMakeLists.txt
    src: str = _read("src", "CMakeLists.txt")
    assert f"add_executable({project_name})" not in src
    assert f"add_library({project_name} STATIC)" not in src
    assert f"add_library({project_name} SHARED)" not in src
    assert "${CMAKE_CURRENT_SOURCE_DIR}/main.c" not in src
    assert "include(GenerateExportHeader)" not in src
    assert "DESTINATION ${CMAKE_INSTALL_BINDIR}" not in src
    assert f"install(EXPORT {project_name}_export" not in src


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