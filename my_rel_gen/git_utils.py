#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git utilities"""

import shutil
import subprocess
from collections import defaultdict
from typing import DefaultDict, List, NamedTuple, Optional

from . import utils


class Commit(NamedTuple):
    message: str
    hash_id: str


GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("Git is not installed on this system.")


def create_tag(
    repo: str, tag_name: str, on: Optional[Commit] = None, msg: str = ""
) -> None:
    gith = utils.make_gith_obj()
    gith.get_repo(repo).create_git_tag(
        tag=tag_name,
        message=msg,
        object=on if on.hash else get_lst_commit_hash(),
        type="commit",
    )
    # command: List[str] = gitify(["tag", tag_name])
    # if on is not None:
    #     command.append(on.hash_id)
    # subprocess.run(command, check=True)


def get_lst_commit() -> Commit:
    return Commit(message=get_lst_commit_msg(), hash_id=get_lst_commit_hash())


def get_lst_commit_hash(branch: Optional[str] = None) -> str:
    command: List[str] = gitify(["log", "-1", "--pretty=%H"])
    if branch:
        command.append(branch)
    return subprocess.check_output(command).decode()


def gitify(command_args: List[str], *, git_dir: Optional[str] = None) -> List[str]:
    assert GIT is not None
    commands = command_args
    commands.insert(0, GIT)
    if git_dir is not None:
        commands.insert(1, "-C")
        commands.insert(2, git_dir)
    return commands


def generate_release_notes(from_: str, to: str, *, add_watermark: bool = True) -> str:
    def make_section(section_name: str, commits: List[List[str]]) -> str:
        output = f"## {section_name}\n"
        for item in commits:
            output += generate_commit_markdown(*item)
        return output

    def generate_commit_markdown(commit_hash: str, commit_msg: str) -> str:
        return f" - {commit_msg} (`{commit_hash}`)\n"

    commits = (
        subprocess.check_output(gitify(["log", f"{from_}..{to}", "--pretty='%h|%s'"]))
        .decode()
        .splitlines()
    )
    release_notes: DefaultDict[str, List[List[str]]] = defaultdict(list)
    for commit in commits:
        release_notes[utils.get_commit_type(commit)].append(commit.split("|", 1))
    output = "# Changelog\n"
    if release_notes.get("BREAKING") is not None:
        output += make_section(
            "\N{COLLISION SYMBOL} BREAKING CHANGES!", release_notes["BREAKING"]
        )

    if release_notes.get("FEATURE") is not None:
        output += make_section("\N{SPARKLES} New features", release_notes["FEATURE"])
    if release_notes.get("BUG") is not None:
        output += make_section("\N{BUG} Bug fixes", release_notes["BUG"])
    if release_notes.get("PERF") is not None:
        output += make_section(
            "\N{LIGHTNING} Performance increases", release_notes["PERF"]
        )
    return (
        output
        + "\n"
        + (
            "--\n<small>Made with "
            '<a href="https://github.com/ThatXliner">@ThatXliner</a>\'s'
            " mrelg</small>"
            if add_watermark
            else ""
        )
    )


def get_lst_commit_msg(branch: Optional[str] = None) -> str:
    """Get the last commit's message"""
    command: List[str] = gitify(["log", "-1", "--pretty=%s"])
    if branch:
        command.append(branch)
    return subprocess.check_output(command).decode()


def get_lst_tags(limit: int = 1) -> List[str]:
    """Get the last tag's name"""
    assert GIT is not None
    command: List[str] = gitify(
        [
            "for-each-ref",
            "refs/tags",
            "--sort=-taggerdate",
            "--format='%(refname:short)'",
            f"--count={limit}",
        ]
    )
    return subprocess.check_output(command).decode().splitlines()


def get_current_branch() -> str:
    """Get the current branch"""
    assert GIT is not None
    command: List[str] = gitify(["rev-parse", "--abbrev-ref", "HEAD"])
    return subprocess.check_output(command).decode()
