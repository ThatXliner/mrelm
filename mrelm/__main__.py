#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line interface"""

import sys
from pathlib import Path

import halo
from colorama import Fore, init

init(autoreset=True)
from typing import Optional

from . import git_utils, py_utils, utils

project_dir = Path(__file__).parent.parent


def main() -> None:
    last_commit = git_utils.get_last_commit()

    print(
        "\N{RIGHT-POINTING MAGNIFYING GLASS} Last commit:",
        Fore.YELLOW + str(last_commit.hash_id),
    )
    if utils.is_version_bump(last_commit.message) or "--force" in sys.argv[1:]:
        if utils.is_version_bump(last_commit.message):
            print("\N{WHITE HEAVY CHECK MARK} Version bump detected")
        else:
            print("\N{WHITE HEAVY CHECK MARK} Forced build")
        project_version = utils.get_project_version()
        print(f"\N{BOOKMARK} Project version detected:", Fore.YELLOW + project_version)
        with halo.Halo("\N{HAMMER} Building project") as spinner:  # type: ignore
            try:
                artifacts = utils.build_project()
            except Exception as exception:
                spinner.fail(" Building project")
                raise exception
            spinner.succeed(f" Building project (artifacts in {artifacts.dir})")

        with halo.Halo("\N{PENCIL} Generating release notes") as spinner:  # type: ignore
            tags = git_utils.get_lst_tags(2)
            if len(tags) == 2:
                from_, to_ = tags
                version = project_version
            else:
                from_ = git_utils.get_first_commit()
                to_ = git_utils.get_last_commit()
                version = "<initial>"
            project_dir.joinpath(artifacts.dir).touch("CHANGELOG.md")
            project_dir.joinpath(artifacts.dir).joinpath("CHANGELOG.md").write_text(
                git_utils.generate_release_notes(
                    from_.hash_id, to_.hash_id, version=version
                )
            )
            spinner.succeed(" Generating release notes")
    else:
        print(
            "\N{SLEEPING FACE}",
            Fore.CYAN + "No work needs to be done (not a version bump)",
        )


if __name__ == "__main__":
    main()
