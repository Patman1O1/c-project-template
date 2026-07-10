# Builtin Imports
from pathlib import Path
import shutil

# Pip Imports
from jinja2 import Template, Environment, FileSystemLoader

# Local Imports
from cproject.format import *
from cproject.cmake import CMake


class Project(object):
    TYPES: Final[list[str]] = ["Static Library", "Shared Library", "Interface Library", "Executable"]
    ROOT: Final[Path] = Path(__file__).resolve().parents[4]

    def __init__(self,
                 project_name: str,
                 project_type: str,
                 project_author: str,
                 project_namespace: str = "",
                 project_version: str = "0.1.0",
                 project_description: str = "") -> None: # raises ValueError
        self.name: str = project_name
        self.package_name: str = to_pascal_case(project_name)
        self.type: str = project_type
        self.author: str = project_author
        self.namespace: str = project_namespace
        self.version: str = project_version
        self.description: str = project_description
        self.env: Environment = Environment(
            loader=FileSystemLoader(Project.ROOT),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @property
    def name(self) -> str: return self._name

    @name.setter
    def name(self, value: str) -> None: self._name: str = to_snake_case(value)

    @property
    def type(self) -> str: return self._type

    @type.setter
    def type(self, value: str) -> None: # raises ValueError
        for project_type in Project.TYPES:
            if value == project_type:
                self._type = value
                return
        raise ValueError(f"Invalid project type: '{value}'")

    @property
    def namespace(self) -> str: return self._namespace

    @namespace.setter
    def namespace(self, value: str) -> None:
        self._namespace: str = value if to_snake_case(value) != "" else self.name

    @property
    def env(self) -> Environment: return self._env

    @env.setter
    def env(self, value: Environment) -> None:
        self._env = value
        self._env.filters["to_screaming_case"] = to_screaming_case
        self._env.filters["to_pascal_case"] = to_pascal_case

    def render(self, cmake: CMake) -> None:  # raises ValueError, jinja2.TemplateNotFound
        # Remove irrelevant directories based on the project type
        if self.type == "Executable":
            shutil.rmtree(Project.ROOT/"include")
            shutil.rmtree(Project.ROOT/"test_package")
        elif self.type == "Interface Library":
            shutil.rmtree(Project.ROOT/"src")

        entries: list[Path] = sorted(Project.ROOT.rglob("*"), key=lambda p: len(p.parts), reverse=True)

        for path in entries:
            if path.is_file() and path.suffix == ".j2":
                template: Template = self._env.get_template(path.relative_to(Project.ROOT).as_posix())
                path.write_text(template.render(project=self, cmake=cmake), encoding="utf-8")

        for path in entries:
            name: str = path.name.removesuffix(".j2")
            if "{{" in name:
                name = self._env.from_string(name).render(project=self, cmake=cmake)
            if name != path.name:
                path.rename(path.with_name(name))
