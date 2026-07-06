# Builtin Imports
from typing import Final
import sys
import os

# Pip Imports
from jinja2 import Environment, Template, FileSystemLoader

class CMake(object):
    def __init__(self, version: str, c_std: int, cxx_std: int) -> None:
        self.version: str = version
        self.c_std: int = c_std
        self.cxx_std: int = cxx_std


class Project(object):
    TYPES: Final[list[str]] = ["Static Library", "Shared Library", "Interface Library", "Executable"]

    def __init__(self,
                 project_name: str,
                 project_type: str,
                 project_author: str,
                 project_version: str="0.1.0",
                 project_description: str="") -> None: # raises ValueError
        self.name: str = project_name
        self.type: str = project_type
        self.author: str = project_author
        self.version: str = project_version
        self.description: str = project_description

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str) -> None: # raises ValueError
        self._type: str
        for project_type in Project.TYPES:
            if value == project_type:
                self._type = value
                break
        raise ValueError(f"Invalid project type: '{value}'")

def render_project(project: Project, cmake: CMake) -> None:

    return

def main() -> int:
    try:
        cmake: CMake = CMake(version="4.3.0", c_std=23, cxx_std=23)
        project: Project = Project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        render_project(project, cmake)
        return 0
    except Exception as exception:
        os.write(sys.stderr.fileno(), str(f"{exception}\n").encode("utf-8"))
        return 1

if __name__ == "__main__":
    sys.exit(main())
