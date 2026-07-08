# Builtin Imports
from typing import Final
from pathlib import Path
import os

# Pip Imports
from jinja2 import Template, Environment, FileSystemLoader

# Local Imports
from cproject.format import *
from cproject.cmake import CMake


class Project(object):
    TYPES: Final[list[str]] = ["Static Library", "Shared Library", "Interface Library", "Executable"]
    ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent.parent

    def __init__(self,
                 project_name: str,
                 project_type: str,
                 project_author: str,
                 project_version: str = "0.1.0",
                 project_description: str = "") -> None:  # raises ValueError
        self.name: str = project_name
        self.type: str = project_type
        self.author: str = project_author
        self.version: str = project_version
        self.description: str = project_description
        self.env: Environment = Environment(
            loader=FileSystemLoader(Project.ROOT),   # root must match _render's relative_to
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @property
    def type(self) -> str: return self._type

    @type.setter
    def type(self, value: str) -> None:  # raises ValueError
        for project_type in Project.TYPES:
            if value == project_type:
                self._type = value
                return
        raise ValueError(f"Invalid project type: '{value}'")

    @property
    def env(self) -> Environment: return self._env

    @env.setter
    def env(self, value: Environment) -> None:
        self._env = value
        self._env.filters["to_screaming_case"] = to_screaming_case
        self._env.filters["to_pascal_case"] = to_pascal_case

    def _render(self, filepath: Path, cmake: CMake) -> None:  # raises ValueError, jinja2.TemplateNotFound
        name: str = filepath.resolve().relative_to(Project.ROOT.resolve()).as_posix()
        template: Template = self._env.get_template(name)
        with filepath.open("w", encoding="utf-8") as file:
            file.write(template.render(project=self, cmake=cmake))
        os.rename(filepath, filepath.with_name(filepath.name.removesuffix(".j2")))

    def render(self, cmake: CMake) -> None:  # raises NotADirectoryError, ValueError, jinja2.TemplateNotFound
        # A single file: render it only if it is a template
        if Project.ROOT.is_file():
            if Project.ROOT.suffix == ".j2":
                self._render(Project.ROOT, cmake)
            return

        # Otherwise the path must be a directory
        if not Project.ROOT.is_dir():
            raise NotADirectoryError(f"{Project.ROOT} is not a directory")

        # Recursively render every *.j2 under the tree. rglob recurses;
        # sorted() materializes the listing before _render() renames files.
        for filepath in sorted(Project.ROOT.rglob("*.j2")):
            self._render(filepath, cmake)