# Builtin Imports
from pathlib import Path

# Pip Imports
import pytest

# Local Imports
from cproject.project import Project

def _get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent

def test__type_property_setter__invalid_type() -> None:
    with pytest.raises(ValueError):
        Project(_get_project_root(), "test", "Invalid Type", "Bill Gates")

def test__type_property_setter__executable() -> None:
    project: Project = Project(_get_project_root(), "test", "Executable", "Jeffrey Dahmer")
    assert project.type == "Executable"

def test__type_property_setter__static_library() -> None:
    project: Project = Project(_get_project_root(), "test", "Static Library", "Peter Griffin")
    assert project.type == "Static Library"

def test__type_property_setter__shared_library() -> None:
    project: Project = Project(_get_project_root(), "test", "Shared Library", "Linus Torvalds")
    assert project.type == "Shared Library"

def test__type_property_setter__interface_library() -> None:
    project: Project = Project(_get_project_root(), "test", "Interface Library", "Donald Trump")
    assert project.type == "Interface Library"

