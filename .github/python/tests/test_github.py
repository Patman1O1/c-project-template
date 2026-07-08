# Builtin Imports
import http
from pathlib import Path
from typing import Final
from unittest.mock import MagicMock
import subprocess

# Pip Imports
from github import Github
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubException import UnknownObjectException
import pytest


# Local Imports
from tests import github

DUMMY_TOKEN: Final[str] = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# ── get_token ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__get_token__env_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", DUMMY_TOKEN)
    assert github.get_token() == DUMMY_TOKEN

def test__get_token__env_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    fake = subprocess.CompletedProcess(["gh","auth","token"], 0, stdout="tok_from_gh\n", stderr="")
    monkeypatch.setattr(github.subprocess, "run", lambda *a, **k: fake)
    assert github.get_token() == "tok_from_gh"

# ── init ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__init__returns_github() -> None: assert isinstance(github.init(DUMMY_TOKEN), Github)

# ── get_user ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__get_user__rejects_non_authenticated() -> None:
    gh: Github = MagicMock(spec=Github)
    gh.get_user.return_value = object()
    with pytest.raises(TypeError):
        github.get_user(gh)

def test__get_user__returns_authenticated(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeAuth: pass
    monkeypatch.setattr(github, "AuthenticatedUser", FakeAuth)
    gh: Github = MagicMock(spec=Github)
    user: FakeAuth = FakeAuth(); user.requester = "R"
    gh.get_user.return_value = user
    assert github.get_user(gh) is user

# ── repo_exists ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test__repo_exists__true() -> None:
    gh: MagicMock = MagicMock(spec=Github)
    gh.get_repo.return_value = MagicMock(spec=Repository)
    assert github.repo_exists(gh, "owner", "repo") is True
    gh.get_repo.assert_called_once_with("owner/repo")

def test__repo_exists__false_on_unknown() -> None:
    gh: MagicMock = MagicMock(spec=Github)
    gh.get_repo.side_effect = UnknownObjectException(http.HTTPStatus.NOT_FOUND)
    assert github.repo_exists(gh, "owner", "repo") is False

# ── create_repo ───────────────────────────────────────────────────────────────────────────────────────────────────────
def test__create_repo__forwards_args() -> None:
    user: MagicMock = MagicMock(spec=AuthenticatedUser)
    template: MagicMock = MagicMock(spec=Repository)
    created: MagicMock = MagicMock(spec=Repository)
    user.create_repo_from_template.return_value = created
    assert github.create_repo(user, template, "myproj", "desc") is created
    user.create_repo_from_template.assert_called_once_with(
        name="myproj", repo=template, description="desc",
        include_all_branches=False, private=True)

def test__create_repo__default_description() -> None:
    user: MagicMock = MagicMock(spec=AuthenticatedUser)
    github.create_repo(user, MagicMock(spec=Repository), "p")
    assert user.create_repo_from_template.call_args.kwargs["description"] == ""

# ── clone_repo ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__clone_repo__creates_missing_dir_and_clones(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clone_from: MagicMock = MagicMock()
    monkeypatch.setattr(github.git.Repo, "clone_from", clone_from)
    repo: MagicMock = MagicMock(spec=Repository)
    repo.ssh_url = "git@github.com:o/r.git"
    dst: Path = tmp_path/"target"
    github.clone_repo(repo, dst)
    assert dst.exists()
    clone_from.assert_called_once_with("git@github.com:o/r.git", dst)

def test__clone_repo__existing_dir_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(github.git.Repo, "clone_from", MagicMock())
    dst: Path = tmp_path/"exists"
    dst.mkdir()
    github.clone_repo(MagicMock(spec=Repository), dst)

# ---- pull_repo ----
# ── pull_repo ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__pull_repo__pulls_default_remote(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fetch: list[MagicMock] = [MagicMock()]
    repo: MagicMock = MagicMock()
    repo.remote.return_value.pull.return_value = fetch
    RepoCls: MagicMock = MagicMock(return_value=repo)
    monkeypatch.setattr(github.git, "Repo", RepoCls)
    assert github.pull_repo(tmp_path) is fetch
    RepoCls.assert_called_once_with(tmp_path)
    repo.remote.assert_called_once_with()
    repo.remote.return_value.pull.assert_called_once_with()

# ── run_workflow ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test__run_workflow__triggers_and_returns_run__executable(monkeypatch: pytest.MonkeyPatch) -> None:
    repo: MagicMock = MagicMock(spec=Repository)
    workflow: MagicMock = MagicMock()
    repo.get_workflow.return_value = workflow

    r1: MagicMock = MagicMock(id=1)
    r2: MagicMock = MagicMock(id=2)
    new: MagicMock = MagicMock(id=3)

    workflow.get_runs.side_effect = [[r1, r2], [new, r1, r2]]
    workflow.create_dispatch.return_value = True
    monkeypatch.setattr(github.time, "sleep", lambda *_: None)

    assert github.run_workflow(repo, "Executable") is new
    repo.get_workflow.assert_called_once_with(github.WORKFLOW_FILE_NAME)
    workflow.create_dispatch.assert_called_once_with(ref="main", inputs={"project_type": "Executable"})

def test__run_workflow__triggers_and_returns_run__static_library(monkeypatch: pytest.MonkeyPatch) -> None:
    repo: MagicMock = MagicMock(spec=Repository)
    workflow: MagicMock = MagicMock()
    repo.get_workflow.return_value = workflow

    r1: MagicMock = MagicMock(id=1)
    r2: MagicMock = MagicMock(id=2)
    new: MagicMock = MagicMock(id=3)

    workflow.get_runs.side_effect = [[r1, r2], [new, r1, r2]]
    workflow.create_dispatch.return_value = True
    monkeypatch.setattr(github.time, "sleep", lambda *_: None)

    assert github.run_workflow(repo, "Static Library") is new
    repo.get_workflow.assert_called_once_with(github.WORKFLOW_FILE_NAME)
    workflow.create_dispatch.assert_called_once_with(ref="main", inputs={"project_type": "Static Library"})

def test__run_workflow__triggers_and_returns_run__shared_library(monkeypatch: pytest.MonkeyPatch) -> None:
    repo: MagicMock = MagicMock(spec=Repository)
    workflow: MagicMock = MagicMock()
    repo.get_workflow.return_value = workflow

    r1: MagicMock = MagicMock(id=1)
    r2: MagicMock = MagicMock(id=2)
    new: MagicMock = MagicMock(id=3)

    workflow.get_runs.side_effect = [[r1, r2], [new, r1, r2]]
    workflow.create_dispatch.return_value = True
    monkeypatch.setattr(github.time, "sleep", lambda *_: None)

    assert github.run_workflow(repo, "Shared Library") is new
    repo.get_workflow.assert_called_once_with(github.WORKFLOW_FILE_NAME)
    workflow.create_dispatch.assert_called_once_with(ref="main", inputs={"project_type": "Shared Library"})

def test__run_workflow__triggers_and_returns_run__interface_library(monkeypatch: pytest.MonkeyPatch) -> None:
    repo: MagicMock = MagicMock(spec=Repository)
    workflow: MagicMock = MagicMock()
    repo.get_workflow.return_value = workflow

    r1: MagicMock = MagicMock(id=1)
    r2: MagicMock = MagicMock(id=2)
    new: MagicMock = MagicMock(id=3)

    workflow.get_runs.side_effect = [[r1, r2], [new, r1, r2]]
    workflow.create_dispatch.return_value = True
    monkeypatch.setattr(github.time, "sleep", lambda *_: None)

    assert github.run_workflow(repo, "Interface Library") is new
    repo.get_workflow.assert_called_once_with(github.WORKFLOW_FILE_NAME)
    workflow.create_dispatch.assert_called_once_with(ref="main", inputs={"project_type": "Interface Library"})



# ── rm_repo ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test__rm_repo__local_then_remote(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    order: list[str] = []
    monkeypatch.setattr(github.shutil, "rmtree", lambda *a, **k: order.append("rmtree"))
    repo: MagicMock = MagicMock(spec=Repository)
    repo.delete.side_effect = lambda: order.append("delete")
    github.rm_repo(repo, tmp_path)
    assert order == ["rmtree", "delete"]