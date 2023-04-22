#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilities for keeping one sane"""

import enum
import os
import os.path
import shutil
import sys
from typing import NoReturn, Sequence

from colorama import Fore, Style, init

init(autoreset=True)

import toml

from . import py_utils


class CommitTypeEnum(enum.Enum):
    FEATURE = "FEATURE"
    BREAKING = "BREAKING"
    BUG = "bug"
    MISC = "miscellaneous"


class ProjectTypeEnum(enum.Enum):
    PYTHON = "python"


class Artifacts:
    def __init__(self, artifacts: Sequence[str]) -> None:
        self.dir = os.path.commonpath(artifacts)
        self.artifacts = artifacts
        self.glob: str = self.dir + "/*"

    def delete(self) -> None:
        shutil.rmtree(self.dir)


def is_version_bump(commit_msg: str) -> bool:
    return ":bookmark:" in commit_msg or "\N{BOOKMARK}" in commit_msg


def get_project_version() -> str:  # TODO: Add support for non-poetry projects and detect them
    return toml.load("pyproject.toml")["tool"]["poetry"]["version"]  # type: ignore


def get_commit_type(commit_msg: str) -> str:
    if ":breaking:" in commit_msg or "\N{COLLISION SYMBOL}" in commit_msg:
        return "BREAKING"
    if ":bug:" in commit_msg or "\N{BUG}" in commit_msg:
        return "BUG"
    if ":feature:" in commit_msg or "\N{SPARKLES}" in commit_msg:
        return "FEATURE"
    if ":zap:" in commit_msg or "\N{LIGHTNING}" in commit_msg:
        return "PERF"
    return "MISC"


def errorize(msg: str, returncode: int = 1) -> NoReturn:
    print(Style.BRIGHT + Fore.RED + msg)
    sys.exit(returncode)


def build_project(
    *, project_type: ProjectTypeEnum = ProjectTypeEnum.PYTHON
) -> Artifacts:
    if project_type == ProjectTypeEnum.PYTHON:
        py_project_type = py_utils.get_project_type()
        return Artifacts(py_utils.build_for(py_project_type))
    raise NotImplementedError("Yeah, sorry: we haven't implemented that one yet")
