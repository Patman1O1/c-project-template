# Builtin Imports
from typing import Final
from pathlib import Path
import os
import subprocess

# Pip Imports
from github import Github, Auth
from github.Repository import Repository
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser
import git

C_PROJECT_TEMPLATE_PATH: Final[str] = "Patman1O1/c-project-template"

class GitHub(object):
    def __init__(self) -> None:
        self.gh: Final[Github] = Github(auth=Auth.Token(GitHub._get_token()))
        self.user: Final[AuthenticatedUser | NamedUser] = self.gh.get_user()
        self.template_repo: Final[Repository] = self.gh.get_repo(C_PROJECT_TEMPLATE_PATH)

    @staticmethod
    def _get_token() -> str:
        # First look in the environment variable
        token: str | None = os.environ.get("GITHUB_TOKEN")
        if token is not None:
            return token
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout

    def create_repo(self, name: str, description: str="") -> Repository:
        return self.user.create_repo_from_template(
            name=name,
            repo=self.template_repo,
            description=description,
            include_all_branches=False,
            private=True
        )

    @staticmethod
    def clone_repo(repo: Repository, dst: Path) -> None:
        if not dst.exists():
            dst.mkdir(mode=0o777, parents=True, exist_ok=True)
        git.Repo.clone_from(repo.ssh_url, dst)
        return

    @staticmethod
    def pull_repo(repo_path: Path) -> list[git.FetchInfo]: return git.Repo(repo_path).remote().pull()

    @staticmethod
    def run_workflow(repo: Repository, project_type: str) -> None:
        repo.get_workflow("create_project.yml").create_dispatch(
            ref="main",
            inputs={
                "project_type": project_type
            }
        )
