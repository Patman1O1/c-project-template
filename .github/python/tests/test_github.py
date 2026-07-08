# Builtin Imports
from typing import Final
from unittest.mock import MagicMock
import subprocess
import pytest

# Pip Imports
from github import Github
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubException import UnknownObjectException

# Local Imports
from tests import github

DUMMY_TOKEN: Final[str] = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# ---- get_token ----
def test__get_token__env_set(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", DUMMY_TOKEN)
    assert github.get_token() == DUMMY_TOKEN

def test__get_token__env_not_set(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    fake = subprocess.CompletedProcess(["gh","auth","token"], 0, stdout="tok_from_gh\n", stderr="")
    monkeypatch.setattr(github.subprocess, "run", lambda *a, **k: fake)
    assert github.get_token() == "tok_from_gh"           # newline stripped

# ---- init ----
def test__init__returns_github():
    assert isinstance(github.init(DUMMY_TOKEN), Github)

# ---- get_user ----
def test__get_user__rejects_non_authenticated():
    gh = MagicMock(spec=Github)
    gh.get_user.return_value = object()                  # exact type isn't AuthenticatedUser
    with pytest.raises(TypeError):
        github.get_user(gh)

def test__get_user__returns_authenticated(monkeypatch):
    class FakeAuth: pass
    monkeypatch.setattr(github, "AuthenticatedUser", FakeAuth)
    gh = MagicMock(spec=Github)
    user = FakeAuth(); user.requester = "R"
    gh.get_user.return_value = user
    assert github.get_user(gh) is user

# ---- repo_exists ----
def test__repo_exists__true():
    gh = MagicMock(spec=Github)
    gh.get_repo.return_value = MagicMock(spec=Repository)
    assert github.repo_exists(gh, "owner", "repo") is True
    gh.get_repo.assert_called_once_with("owner/repo")

def test__repo_exists__false_on_unknown():
    gh = MagicMock(spec=Github)
    gh.get_repo.side_effect = UnknownObjectException(404)
    assert github.repo_exists(gh, "owner", "repo") is False

# ---- create_repo ----
def test__create_repo__forwards_args():
    user = MagicMock(spec=AuthenticatedUser)
    template = MagicMock(spec=Repository)
    created = MagicMock(spec=Repository)
    user.create_repo_from_template.return_value = created
    assert github.create_repo(user, template, "myproj", "desc") is created
    user.create_repo_from_template.assert_called_once_with(
        name="myproj", repo=template, description="desc",
        include_all_branches=False, private=True)

def test__create_repo__default_description():
    user = MagicMock(spec=AuthenticatedUser)
    github.create_repo(user, MagicMock(spec=Repository), "p")
    assert user.create_repo_from_template.call_args.kwargs["description"] == ""

# ---- clone_repo ----
def test__clone_repo__creates_missing_dir_and_clones(tmp_path, monkeypatch):
    clone_from = MagicMock()
    monkeypatch.setattr(github.git.Repo, "clone_from", clone_from)
    repo = MagicMock(spec=Repository); repo.ssh_url = "git@github.com:o/r.git"
    dst = tmp_path / "target"
    github.clone_repo(repo, dst)
    assert dst.exists()
    clone_from.assert_called_once_with("git@github.com:o/r.git", dst)

def test__clone_repo__existing_dir_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(github.git.Repo, "clone_from", MagicMock())
    dst = tmp_path / "exists"; dst.mkdir()
    github.clone_repo(MagicMock(spec=Repository), dst)   # must not raise

# ---- pull_repo ----
def test__pull_repo__pulls_default_remote(monkeypatch, tmp_path):
    fetch = [MagicMock()]
    repo = MagicMock(); repo.remote.return_value.pull.return_value = fetch
    RepoCls = MagicMock(return_value=repo)
    monkeypatch.setattr(github.git, "Repo", RepoCls)
    assert github.pull_repo(tmp_path) is fetch
    RepoCls.assert_called_once_with(tmp_path)
    repo.remote.assert_called_once_with()
    repo.remote.return_value.pull.assert_called_once_with()
def test__run_workflow__triggers_and_returns_run(monkeypatch):
    repo = MagicMock(spec=Repository)
    workflow = MagicMock()
    repo.get_workflow.return_value = workflow
    r1, r2, new = MagicMock(id=1), MagicMock(id=2), MagicMock(id=3)
    workflow.get_runs.side_effect = [[r1, r2], [new, r1, r2]]   # snapshot, then new appears
    workflow.create_dispatch.return_value = True
    monkeypatch.setattr(github.time, "sleep", lambda *_: None)

    assert github.run_workflow(repo, "Executable") is new
    repo.get_workflow.assert_called_once_with(github.WORKFLOW_FILE_NAME)
    workflow.create_dispatch.assert_called_once_with(ref="main", inputs={"project_type": "Executable"})


def test__rm_repo__local_then_remote(monkeypatch, tmp_path):
    order = []
    monkeypatch.setattr(github.shutil, "rmtree", lambda *a, **k: order.append("rmtree"))
    repo = MagicMock(spec=Repository)
    repo.delete.side_effect = lambda: order.append("delete")
    github.rm_repo(repo, tmp_path)
    assert order == ["rmtree", "delete"]