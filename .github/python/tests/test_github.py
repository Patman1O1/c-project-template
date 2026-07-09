# Builtin Imports
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Any, Generator
import os
import shutil
import time

# Pip Imports
from github import Github
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser
from github.Workflow import Workflow
from github.WorkflowRun import WorkflowRun
from github.GithubException import GithubException
import pytest

# Local Imports
from tests import github

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# These are true end-to-end tests. For each project type they:
#   1. create a private repo from the template            (github.create_repo)
#   2. dispatch the "create_project" workflow             (see _dispatch_workflow)
#   3. wait for the Actions run to finish successfully
#   4. clone the pushed result                            (github.clone_repo)
#   5. assert the rendered project matches the type
#   6. delete the remote repo + local clone               (github.rm_repo)
#
# They hit the real GitHub API and Actions, so they are slow and need:
#   - credentials: GITHUB_TOKEN (repo + workflow scopes) or a logged-in `gh` CLI
#   - network access to github.com / api.github.com
#   - an SSH key registered with GitHub (github.clone_repo clones via ssh_url)
# When no credentials are available the whole module is skipped rather than failed.
#
# NOTE: we intentionally do NOT call github.run_workflow. On a freshly-created
# repo the workflow_dispatch run list is empty, and run_workflow snapshots it
# with `workflow.get_runs(...)[:30]` -- slicing an empty PyGithub PaginatedList
# raises `IndexError: list index out of range`. We dispatch here using plain
# iteration (which is empty-safe) instead. The one-line fix for github.py is to
# iterate rather than slice, e.g.:
#     seen = {r.id for r in itertools.islice(workflow.get_runs(...), 30)}
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

TEMPLATE_REPO: Final[str] = "Patman1O1/c-project-template"

# A repo created from a template needs a moment before Actions registers its
# workflows; poll until it resolves, then dispatch and wait for completion.
WORKFLOW_REGISTER_TIMEOUT: Final[float] = 300.0
WORKFLOW_REGISTER_POLL: Final[float] = 10.0
DISPATCH_TIMEOUT: Final[float] = 120.0
DISPATCH_POLL: Final[float] = 5.0
RUN_TIMEOUT: Final[float] = 600.0
RUN_POLL: Final[float] = 10.0
MAX_SEEN_RUNS: Final[int] = 30

# Per project type: the repo name to create, and the identifiers the workflow is
# expected to render from it (snake-case name/namespace, pascal-case package).
PROJECTS: Final[dict[str, dict[str, str]]] = {
    "Executable": {
        "repo": "c-executable",
        "name": "c_executable",
        "namespace": "c_executable",
        "package": "CExecutable",
    },
    "Static Library": {
        "repo": "c-static-library",
        "name": "c_static_library",
        "namespace": "c_static_library",
        "package": "CStaticLibrary",
    },
    "Shared Library": {
        "repo": "c-shared-library",
        "name": "c_shared_library",
        "namespace": "c_shared_library",
        "package": "CSharedLibrary",
    },
    "Interface Library": {
        "repo": "c-interface-library",
        "name": "c_interface_library",
        "namespace": "c_interface_library",
        "package": "CInterfaceLibrary",
    },
}

# Files the workflow is expected to render for every project type. Paths use
# {name}/{namespace}/{package} placeholders resolved per repo.
EXPECTED_LAYOUT: Final[tuple[str, ...]] = (
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


def _have_credentials() -> bool:
    if os.environ.get("GITHUB_TOKEN"):
        return True
    return shutil.which("gh") is not None


# Slow + integration, and skipped entirely without credentials.
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
    pytest.mark.skipif(
        not _have_credentials(),
        reason="no GitHub credentials (set GITHUB_TOKEN or run 'gh auth login')",
    ),
]


@dataclass
class RenderedRepo:
    project_type: str
    ids: dict[str, str]
    repo: Repository
    run: WorkflowRun
    path: Path


def _find_workflow(repo: Repository) -> Workflow | None:
    """Return the create_project workflow if Actions has registered it yet.

    Right after a repo is created from a template the workflow file exists but
    Actions indexes it asynchronously, so both the by-filename endpoint and the
    listing endpoint can 404 / lag briefly. Try both and swallow GithubException.
    """
    try:
        return repo.get_workflow(github.WORKFLOW_FILE_NAME)
    except GithubException:
        pass
    try:
        for workflow in repo.get_workflows():
            if workflow.path.endswith(github.WORKFLOW_FILE_NAME):
                return workflow
    except GithubException:
        pass
    return None


def _recent_run_ids(workflow: Workflow, ref: str) -> set[int]:
    """IDs of recent workflow_dispatch runs, iterated safely.

    Iterating a PaginatedList is empty-safe; slicing it (``[:30]``) is not, so we
    cap with a counter instead of a slice.
    """
    ids: set[int] = set()
    for run in workflow.get_runs(event="workflow_dispatch", branch=ref):
        ids.add(run.id)
        if len(ids) >= MAX_SEEN_RUNS:
            break
    return ids


def _newest_new_run(workflow: Workflow, ref: str, seen: set[int]) -> WorkflowRun | None:
    for run in workflow.get_runs(event="workflow_dispatch", branch=ref):
        if run.id not in seen:
            return run
    return None


def _dispatch_workflow(repo: Repository, project_type: str, ref: str) -> WorkflowRun:
    """Wait for the workflow to register, dispatch it once, and return the run."""
    # 1) Wait for Actions to register the workflow on the new repo.
    deadline: float = time.monotonic() + WORKFLOW_REGISTER_TIMEOUT
    workflow: Workflow | None = None
    while time.monotonic() < deadline:
        workflow = _find_workflow(repo)
        if workflow is not None:
            break
        time.sleep(WORKFLOW_REGISTER_POLL)
    if workflow is None:
        raise AssertionError(
            f"workflow {github.WORKFLOW_FILE_NAME!r} never registered on "
            f"{repo.full_name!r} within {WORKFLOW_REGISTER_TIMEOUT:.0f}s"
        )

    # 2) Snapshot existing runs, dispatch, then poll for the one that's new.
    seen: set[int] = _recent_run_ids(workflow, ref)
    assert workflow.create_dispatch(ref=ref, inputs={"project_type": project_type}), \
        f"failed to dispatch {github.WORKFLOW_FILE_NAME!r} on {ref!r}"

    deadline = time.monotonic() + DISPATCH_TIMEOUT
    while time.monotonic() < deadline:
        run: WorkflowRun | None = _newest_new_run(workflow, ref, seen)
        if run is not None:
            return run
        time.sleep(DISPATCH_POLL)
    raise AssertionError(f"no new workflow run appeared within {DISPATCH_TIMEOUT:.0f}s")


def _wait_for_completion(run: WorkflowRun, timeout: float, poll: float) -> WorkflowRun:
    deadline: float = time.monotonic() + timeout
    while time.monotonic() < deadline:
        run.update()
        if run.status == "completed":
            return run
        time.sleep(poll)
    raise TimeoutError(f"workflow run {run.id} did not complete within {timeout:.0f}s (status={run.status!r})")


# ── Fixtures ──────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def gh() -> Github:
    # Exercises github.get_token + github.init.
    return github.init(github.get_token())


@pytest.fixture(scope="session")
def user(gh: Github) -> AuthenticatedUser:
    # Exercises github.get_user (and asserts the token is an authenticated user).
    return github.get_user(gh)


@pytest.fixture(scope="session", params=list(PROJECTS), ids=list(PROJECTS))
def rendered_repo(request: pytest.FixtureRequest,
                  gh: Github,
                  user: AuthenticatedUser,
                  tmp_path_factory: pytest.TempPathFactory) -> Generator[RenderedRepo, Any, None]:
    """Create a repo from the template, run the workflow for one project type,
    clone the result, and hand it to the tests. Session-scoped so the expensive
    create+dispatch+clone happens once per type and is shared by all assertions.
    """
    project_type: str = request.param
    ids: dict[str, str] = PROJECTS[project_type]
    owner: str = user.login
    name: str = ids["repo"]

    # Clean up a leftover repo from a previously aborted run so create succeeds.
    if github.repo_exists(gh, owner, name):
        gh.get_repo(f"{owner}/{name}").delete()

    template: Repository = gh.get_repo(TEMPLATE_REPO)
    repo: Repository = github.create_repo(user, template, name, description=f"integration test: {project_type}")

    local: Path = tmp_path_factory.mktemp(name)
    try:
        run: WorkflowRun = _dispatch_workflow(repo, project_type, ref=repo.default_branch)
        run = _wait_for_completion(run, RUN_TIMEOUT, RUN_POLL)
        github.clone_repo(repo, local)
        yield RenderedRepo(project_type, ids, repo, run, local)
    finally:
        # Deletes the local clone and the remote repo.
        github.rm_repo(repo, local)


# ── authentication ────────────────────────────────────────────────────────────────────────────────────────────────────
def test__authenticates_as_a_user(user: AuthenticatedUser) -> None:
    assert user.login


# ── repo creation ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test__create_repo__exists_and_is_private(rendered_repo: RenderedRepo, gh: Github, user: AuthenticatedUser) -> None:
    assert github.repo_exists(gh, user.login, rendered_repo.ids["repo"])
    assert rendered_repo.repo.private is True


# ── workflow ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__run_workflow__completes_successfully(rendered_repo: RenderedRepo) -> None:
    assert rendered_repo.run.status == "completed"
    assert rendered_repo.run.conclusion == "success"


# ── workflow side effects (README rewrite, .github removal) ───────────────────────────────────────────────────────────
def test__workflow_regenerates_readme(rendered_repo: RenderedRepo) -> None:
    readme: str = (rendered_repo.path / "README.md").read_text(encoding="utf-8")
    assert readme.startswith(f"# {rendered_repo.ids['repo']}")


def test__workflow_removes_dot_github(rendered_repo: RenderedRepo) -> None:
    assert not (rendered_repo.path / ".github").exists()


# ── rendered layout ───────────────────────────────────────────────────────────────────────────────────────────────────
def test__clone_repo__renders_expected_layout(rendered_repo: RenderedRepo) -> None:
    ids: dict[str, str] = rendered_repo.ids
    root: Path = rendered_repo.path

    for rel in EXPECTED_LAYOUT:
        path: Path = root / rel.format(**ids)
        assert path.is_file(), f"expected rendered file missing: {path}"

    # No template scaffolding should survive the render (ignore the .git dir).
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        assert not path.name.endswith(".j2"), f"unrendered template left behind: {path}"
        assert "{{" not in path.name, f"unresolved name placeholder: {path}"


# ── rendered content reflects the project type ────────────────────────────────────────────────────────────────────────
def test__root_cmake_matches_project_type(rendered_repo: RenderedRepo) -> None:
    project_type: str = rendered_repo.project_type
    name: str = rendered_repo.ids["name"]
    root: str = (rendered_repo.path / "CMakeLists.txt").read_text(encoding="utf-8")

    if project_type == "Executable":
        assert "option(BUILD_SHARED_LIBS" not in root
        assert "configure_package_config_file(" not in root
        assert f"add_library({name} INTERFACE)" not in root
        assert "add_subdirectory(src)" in root
    elif project_type == "Static Library":
        assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" OFF)' in root
        assert "configure_package_config_file(" in root
        assert "add_subdirectory(src)" in root
    elif project_type == "Shared Library":
        assert 'option(BUILD_SHARED_LIBS "Build the project as a shared library" ON)' in root
        assert "configure_package_config_file(" in root
        assert "add_subdirectory(src)" in root
    else:  # Interface Library
        assert f"add_library({name} INTERFACE)" in root
        assert "configure_package_config_file(" in root
        assert "add_subdirectory(src)" not in root


def test__src_cmake_matches_project_type(rendered_repo: RenderedRepo) -> None:
    project_type: str = rendered_repo.project_type
    name: str = rendered_repo.ids["name"]
    src: str = (rendered_repo.path / "src" / "CMakeLists.txt").read_text(encoding="utf-8")

    if project_type == "Executable":
        assert f"add_executable({name})" in src
        assert f"add_library({name} STATIC)" not in src
        assert f"add_library({name} SHARED)" not in src
    elif project_type == "Static Library":
        assert f"add_library({name} STATIC)" in src
        assert f"add_library({name} SHARED)" not in src
        assert f"add_executable({name})" not in src
    elif project_type == "Shared Library":
        assert f"add_library({name} SHARED)" in src
        assert f"add_library({name} STATIC)" not in src
        assert f"add_executable({name})" not in src
    else:  # Interface Library — src has no compiled target
        assert f"add_executable({name})" not in src
        assert f"add_library({name} STATIC)" not in src
        assert f"add_library({name} SHARED)" not in src


# ── include guard reflects the rendered name ──────────────────────────────────────────────────────────────────────────
def test__public_header_include_guard(rendered_repo: RenderedRepo) -> None:
    ids: dict[str, str] = rendered_repo.ids
    header: str = (rendered_repo.path / "include" / ids["namespace"] / f"{ids['name']}.h").read_text(encoding="utf-8")
    guard: str = f"{ids['name'].upper()}_H"
    assert f"#ifndef {guard}" in header
    assert f"#define {guard}" in header


# ── local clone can be pulled (fast-forward no-op) ────────────────────────────────────────────────────────────────────
def test__pull_repo__succeeds_on_fresh_clone(rendered_repo: RenderedRepo) -> None:
    fetched = github.pull_repo(rendered_repo.path)
    assert fetched is not None