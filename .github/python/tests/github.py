# Builtin Imports
from typing import Final
from pathlib import Path
import os
import sys
import subprocess
import shutil
import time

# Pip Imports
from github import Github, Auth
from github.Repository import Repository
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser
from github.Workflow import Workflow
from github.WorkflowRun import WorkflowRun
from github.GithubException import UnknownObjectException
import git

C_PROJECT_TEMPLATE_PATH: Final[str] = "Patman1O1/c-project-template"
WORKFLOW_FILE_NAME: Final[str] = "create_project.yml"

def get_token() -> str: # raises RuntimeError
    # First check if the environment variable is set
    token: str | None = os.environ.get("GITHUB_TOKEN")
    if token != "" and token is not None:
        return token

    # Fall back to the GitHub CLI
    result: subprocess.CompletedProcess[str] = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    token = result.stdout.strip()
    if result.returncode != os.EX_OK or token == "" or token is None:
        raise RuntimeError(
            "no GitHub token available: set GITHUB_TOKEN or run 'gh auth login' "
            f"({result.stderr.strip()})"
        )
    return token

def init(token: str) -> Github: return Github(auth=Auth.Token(token))

def get_user(gh: Github) -> AuthenticatedUser: # raises TypeError
    user: NamedUser | AuthenticatedUser = gh.get_user()
    if not isinstance(user, AuthenticatedUser):
        raise TypeError(f"Expected 'user' to be of type '{AuthenticatedUser.__name__}' but got '{type(user).__name__}'")
    return user

def repo_exists(gh: Github, owner_name: str, repo_name: str) -> bool:
    try:
        # Construct the full repository handle: "username/repository-name"
        gh.get_repo(f"{owner_name}/{repo_name}")
        return True
    except UnknownObjectException:
        # 404 Error: The repository doesn't exist, or it is private and your token lacks access
        return False

def create_repo(user: AuthenticatedUser, template_repo: Repository, name: str, description: str="") -> Repository:
    return user.create_repo_from_template(
            name=name,
            repo=template_repo,
            description=description,
            include_all_branches=False,
            private=True
    )

def clone_repo(repo: Repository, dst: Path) -> git.Repo:
    dst.mkdir(parents=True, exist_ok=True)
    return git.Repo.clone_from(repo.ssh_url, dst)

def pull_repo(repo_path: Path) -> list[git.FetchInfo]: return git.Repo(repo_path).remote().pull()

def run_workflow(repo: Repository, project_type: str, ref: str = "main",
                 timeout: float | int = 30.0, poll_interval: float | int = 2.0) -> WorkflowRun: # raises RuntimeError, TimeoutError
    workflow: Workflow = repo.get_workflow(WORKFLOW_FILE_NAME)

    # The dispatch endpoint returns 204 with no body, so record the runs that
    # already exist, trigger the dispatch, then poll for the one that's new.
    seen: set[int] = {run.id for run in workflow.get_runs(event="workflow_dispatch", branch=ref)[:30]}
    if not workflow.create_dispatch(ref=ref, inputs={"project_type": project_type}):
        raise RuntimeError(f"failed to dispatch workflow '{WORKFLOW_FILE_NAME}' on '{ref}'")

    deadline: float | int = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for run in workflow.get_runs(event="workflow_dispatch", branch=ref):
            if run.id not in seen:
                return run
        time.sleep(poll_interval)

    raise TimeoutError(f"no workflow run appeared within {timeout:.0f}s")


def _on_rm_error(func, path, _exc) -> None:
    # Clear read-only bits (e.g. Git's packed objects on Windows) and retry.
    os.chmod(path, 0o700)
    func(path)


def rm_repo(repo: Repository, local_dir: Path) -> None:
    if local_dir.exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(local_dir, onexc=_on_rm_error)
        else:
            shutil.rmtree(local_dir, onerror=_on_rm_error)
    repo.delete()
