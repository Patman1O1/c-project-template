# Builtin Imports
from pathlib import Path
from typing import Final

# Pip Imports
from github import Github
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser
import pytest

# Local Imports
from cproject.project import Project
from cproject.project import CMake
from tests import github

CMAKE: Final[CMake] = CMake(version="4.3.0", c_std=23, cxx_std=23)
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent

def setup_repo(test_dir: Path, project_type: str) -> None: # raises ValueError
    # Authenticate
    gh: Github = github.init(github.get_token())
    user: AuthenticatedUser = github.get_user(gh)

    # Get the template repo
    template_repo: Repository = gh.get_repo("Patman1O1/c-project-template")

    # Create the test repo on GitHub
    repo: Repository
    if project_type == "Executable":
        repo = github.create_repo(user, template_repo, "c-executable")
    elif project_type == "Static Library":
        repo = github.create_repo(user, template_repo, "c-static-library")
    elif project_type == "Shared Library":
        repo = github.create_repo(user, template_repo, "c-shared-library")
    elif project_type == "Interface Library":
        repo = github.create_repo(user, template_repo, "c-interface-library")
    else:
        raise ValueError(f"Unknown project type: {project_type}")


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

def test__render__executable() -> None:
    pass