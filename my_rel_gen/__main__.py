#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line interface"""
import sys

import halo

from . import git_utils, utils

REPO = sys.argv[1]


def main() -> None:
    lst_commit = git_utils.get_lst_commit()
    print(
        f"\N{RIGHT-POINTING MAGNIFYING GLASS} Last commit: {lst_commit.hash_id} |",
        end=" ",
    )
    if utils.is_version_bump(lst_commit.message):
        print(" \N{WHITE HEAVY CHECK MARK} Version bump detected")
        project_version = utils.get_project_version()
        print(f"\N{BOOKMARK} Project version detected: {project_version}")
        with halo.Halo(text="Building project...") as spinner:  # type: ignore
            try:
                artifacts = utils.build_project()
            except Exception as exception:
                spinner.fail()
                raise exception
            spinner.succeed()
        with halo.Halo(text="Creating and uploading release") as spinner:  # type: ignore
            utils.create_release(
                msg=git_utils.generate_release_notes(*git_utils.get_lst_tags(2)),
                repo=REPO,
                tag_name=f"v{project_version}",
                title=f"Version v{project_version}",
                artifacts=artifacts.artifacts,
                commit_hash=lst_commit.hash_id,
            )
            spinner.succeed()
        artifacts.delete()
    else:
        print("\N{CROSS MARK} Not a version bump")
        print(
            "\N{SLEEPING FACE} No work needs to be done: last commit was not version bump"
        )


if __name__ == "__main__":
    main()
