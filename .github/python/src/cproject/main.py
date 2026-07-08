# Builtin Imports
from pathlib import Path
import sys
import os

# Pip Imports
import click

from cproject.cmake import CMake
# Local Imports
from cproject.project import Project

@click.command("create-project")
@click.argument("project_name", required=True, type=click.STRING)
@click.argument("project_type", required=True, type=click.Choice(["Executable", "Static Library", "Shared Library", "Interface Library"]))
@click.argument("project_author", required=True, type=click.STRING)
@click.argument("project_namespace", required=False, type=click.STRING, default="")
@click.argument("project_version", required=False, type=click.STRING, default="0.1.0")
@click.argument("project_description", required=False, type=click.STRING, default="")
def main(project_name: str,
         project_type: str,
         project_author: str,
         project_namespace: str,
         project_version: str,
         project_description: str) -> int:
    try:
        # Create a new instance of Project
        project: Project = Project(project_name,
                                   project_type,
                                   project_author,
                                   project_namespace,
                                   project_version,
                                   project_description)

        # Render the project
        project.render(CMake(version="4.3.0", c_std=23, cxx_std=23))
        return 0
    except Exception as exception:
        os.write(sys.stderr.fileno(), str(f"{exception}\n").encode("utf-8"))
        return 1

if __name__ == "__main__":
    sys.exit(main())
