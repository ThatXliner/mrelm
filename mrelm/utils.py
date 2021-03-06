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
import github
import toml

from . import py_utils


def make_gith_obj() -> github.Github:
    token = os.getenv("GITHUB_TOKEN")
    if token is None:
        raise ValueError("You must set the `GITHUB_TOKEN` enviorment variable")
    assert token is not None
    return github.Github(token)


class CommitTypeEnum(enum.Enum):
    FEATURE = "FEATURE"
    BREAKING = "BREAKING"
    BUG = "bug"
    MISC = "miscellaneous"


class ProjectTypeEnum(enum.Enum):
    PYTHON = "python"


class Artifacts:
    def __init__(self, artfacts: Sequence[str]) -> None:
        self.dir = os.path.commonpath(artfacts)
        self.artifacts = artfacts
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


def create_release(
    msg: str,
    repo: str,
    tag_name: str,
    commit_hash: str,
    artifacts: Sequence[str],
    title: str,
) -> None:
    gith = make_gith_obj()
    release = gith.get_repo(repo).create_git_release(
        tag=tag_name,
        target_commitish=commit_hash,
        name=title,
        message=msg,
    )
    for artifact in artifacts:
        if artifact.endswith(".whl"):
            release.upload_asset(artifact, label="Wheel Binary")
        elif artifact.endswith("pyz"):
            release.upload_asset(artifact, label="ZipApp")
        elif artifact.endswith(".tar.gz"):
            release.upload_asset(artifact, label="Source Distribution")


def build_project(
    *, project_type: ProjectTypeEnum = ProjectTypeEnum.PYTHON
) -> Artifacts:
    if project_type == ProjectTypeEnum.PYTHON:
        py_project_type = py_utils.get_project_type()
        return Artifacts(py_utils.build_for(py_project_type))
    raise NotImplementedError("Yeah, sorry: we haven't implemented that one yet")
