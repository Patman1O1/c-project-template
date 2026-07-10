# Builtin Imports
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Callable
import shutil
import subprocess

# Pip Imports
import pytest

# Local Imports
from cproject.project import Project, CMake

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# These tests render the template for every project type and then drive Conan
# through the full package lifecycle for every valid option combination:
#
#   `conan create` runs, in order:
#     - generate()  -> CMakeToolchain / CMakeDeps           (configuring)
#     - build()     -> cmake.configure() + cmake.build()    (building)
#     - package()   -> cmake.install()                      (installing)
#
# so a single `conan create` per combination exercises configuring, building,
# and installing.
#
# Option matrix (every possible combination):
#   build_tests is defined for ALL project types                     -> {True, False}
#   build_shared_libs is only defined for the LIBRARY conanfiles      -> {True, False}
#     (the Executable and Interface conanfiles do not declare it, so passing it
#      there would make Conan error; those types only vary build_tests.)
#
#   Executable        : tests{on,off}                         = 2
#   Static Library    : tests{on,off} x shared{on,off}        = 4
#   Shared Library    : tests{on,off} x shared{on,off}        = 4
#   Interface Library : tests{on,off}                         = 2
#                                                       total = 12
#
# build_type is fixed to Release: generate() forces BUILD_TESTS on in Debug, so
# only Release lets us test "without tests" deterministically.
#
# These are slow and require Conan (plus a C toolchain; Conan provisions CMake
# and GTest itself). The module is skipped when conan is not on PATH.
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

CMAKE: Final[CMake] = CMake(version="4.3.0", c_std=23, cxx_std=23)
VERSION: Final[str] = "0.1.0"
BUILD_TYPE: Final[str] = "Release"

# Project.ROOT points at the template on disk. render() rewrites templates in
# place, so we always copy from this pristine original, never a rendered copy.
ORIGINAL_ROOT: Final[Path] = Project.ROOT

# The (snake-case) Conan package name rendered for each project type. Also used
# as the working-directory name for the rendered project.
TYPE_INFO: Final[dict[str, str]] = {
    "Executable": "conan_executable",
    "Static Library": "conan_static",
    "Shared Library": "conan_shared",
    "Interface Library": "conan_interface",
}
PROJECT_TYPES: Final[tuple[str, ...]] = tuple(TYPE_INFO)
LIBRARY_TYPES: Final[frozenset[str]] = frozenset({"Static Library", "Shared Library"})

# Files copied from the repo that are irrelevant to (or would bloat) a render.
_IGNORE = shutil.ignore_patterns(
    ".git", ".github", "build*", "_build*", "cmake-build*", "__pycache__", "*.pyc",
    ".pytest_cache", ".venv", "venv", ".idea", ".vs", ".vscode", ".DS_Store",
    "CMakeUserPresets.json",
)


@dataclass(frozen=True)
class Case:
    project_type: str
    build_tests: bool
    build_shared_libs: bool | None  # None => option not defined for this type

    @property
    def id(self) -> str:
        parts: list[str] = [
            TYPE_INFO[self.project_type],
            "tests_on" if self.build_tests else "tests_off",
        ]
        if self.build_shared_libs is not None:
            parts.append("shared_on" if self.build_shared_libs else "shared_off")
        return "-".join(parts)


def _build_cases() -> list[Case]:
    cases: list[Case] = []
    for project_type in PROJECT_TYPES:
        shared_values: tuple[bool | None, ...] = (
            (True, False) if project_type in LIBRARY_TYPES else (None,)
        )
        for build_tests in (True, False):
            for build_shared_libs in shared_values:
                cases.append(Case(project_type, build_tests, build_shared_libs))
    return cases


CASES: Final[list[Case]] = _build_cases()


def _render_project(project_type: str, dest: Path) -> Path:
    """Copy the pristine template to `dest` and render it for `project_type`."""
    shutil.copytree(ORIGINAL_ROOT, dest, ignore=_IGNORE)

    # render() reads Project.ROOT (also the Jinja loader root), so point it at the
    # copy for the duration of the render, then restore it so nothing leaks to
    # other tests/modules.
    saved_root: Path = Project.ROOT
    Project.ROOT = dest
    try:
        Project(TYPE_INFO[project_type], project_type, "conan integration test").render(CMAKE)
    finally:
        Project.ROOT = saved_root
    return dest


def _conan_create_command(project_dir: Path,
                          reference: str,
                          *,
                          build_type: str,
                          build_tests: bool,
                          build_shared_libs: bool | None) -> list[str]:
    command: list[str] = [
        "conan", "create", str(project_dir),
        "--build=missing",
        "-s", f"build_type={build_type}",
        "-o", f"{reference}:build_tests={build_tests}",
    ]
    if build_shared_libs is not None:
        command += ["-o", f"{reference}:build_shared_libs={build_shared_libs}"]
    return command


# ── module marks: slow integration, skipped when conan is unavailable ─────────────────────────────────────────────────
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.skipif(shutil.which("conan") is None, reason="conan is not installed"),
]


# ── Fixtures ──────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def _ensure_conan_profile() -> None:
    # Conan needs a default profile to build. Create one if it's missing.
    # (conan presence is already guaranteed by the module-level skipif.)
    subprocess.run(["conan", "profile", "detect", "--exist-ok"], capture_output=True, text=True)


@pytest.fixture(scope="session")
def render_project(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    """Return a callable that renders a project type once and caches the result,
    so each type is rendered a single time and reused across its option combos.
    """
    cache: dict[str, Path] = {}
    root: Path = tmp_path_factory.mktemp("conan_projects")

    def _get(project_type: str) -> Path:
        if project_type not in cache:
            cache[project_type] = _render_project(project_type, root / TYPE_INFO[project_type])
        return cache[project_type]

    return _get


# ── the matrix ────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test__conan_create__configures_builds_and_installs(case: Case,
                                                        render_project: Callable[[str], Path]) -> None:
    project_dir: Path = render_project(case.project_type)
    reference: str = f"{TYPE_INFO[case.project_type]}/{VERSION}"

    command: list[str] = _conan_create_command(
        project_dir, reference,
        build_type=BUILD_TYPE,
        build_tests=case.build_tests,
        build_shared_libs=case.build_shared_libs,
    )

    result: subprocess.CompletedProcess[str] = subprocess.run(
        command, capture_output=True, text=True, timeout=3600,
    )
    assert result.returncode == 0, (
        f"`{' '.join(command)}` failed (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )