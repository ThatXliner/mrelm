import enum
import glob
import shutil
import subprocess
import zipapp
from pathlib import Path
from typing import List

import toml


class PythonProjectTypeEnum(enum.Enum):
    POETRY = "poetry"


def get_project_type() -> PythonProjectTypeEnum:
    # TODO: Support other python project types, too
    return PythonProjectTypeEnum.POETRY


def build_for(project_type: PythonProjectTypeEnum) -> List[str]:
    if project_type == PythonProjectTypeEnum.POETRY:
        module_name = str(
            Path().joinpath(toml.load("pyproject.toml")["tool"]["poetry"]["name"])  # type: ignore
        )
        poetry_binary = shutil.which("poetry")
        assert poetry_binary is not None
        subprocess.run([poetry_binary, "build"], check=True, stdout=subprocess.DEVNULL)
        zipapp.create_archive(
            Path().joinpath(module_name.replace("-", "_")),
            target=Path().joinpath("dist").joinpath(module_name + ".pyz"),
            interpreter=shutil.which("python3")
            or shutil.which("python")
            or shutil.which("py")
            or shutil.which("py3"),
        )
        return glob.glob(str(Path().joinpath("dist")))
    else:
        raise NotImplementedError("Yeah, sorry: we haven't implemented that one yet")
