#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line interface"""
import argparse
import os

import halo
from colorama import Fore, init

init(autoreset=True)
from typing import Optional

from . import git_utils, py_utils, utils


def main() -> None:
    lst_commit = git_utils.get_lst_commit()
    parser = argparse.ArgumentParser("mrelm")
    parser.add_argument(
        "repo",
        nargs="?",
        default=os.getenv("REPO_NAME") or os.getenv("REPO"),
        help="The repository name",
    )
    parser.add_argument(
        "--no-release", action="store_true", help="Do not upload to PyPI"
    )
    action_flags = parser.add_mutually_exclusive_group()
    action_flags.add_argument(
        "--bootstrap", "-b", action="store_true", help="Should bootstrap project?"
    )
    action_flags.add_argument(
        "--generate-release-notes",
        "-g",
        action="store_true",
        help="Generate release notes from the commits between the last 2 tags",
    )
    args = parser.parse_args()
    repo: Optional[str] = args.repo
    should_bootstrap: bool = args.bootstrap
    should_generate_release_notes: bool = args.generate_release_notes
    should_release: bool = not args.no_release
    if repo is None:
        utils.errorize(
            "You must specify set `REPO_NAME` or `REPO` environment variable or"
            " add the `--repo=Username/repo_name` argument"
        )
    print(
        "\N{RIGHT-POINTING MAGNIFYING GLASS} Last commit:",
        Fore.YELLOW + str(lst_commit.hash_id),
    )
    if utils.is_version_bump(lst_commit.message) or should_bootstrap:
        if should_bootstrap:
            print("\N{MANS SHOE} Requested bootstrap")
        else:
            print("\N{WHITE HEAVY CHECK MARK} Version bump detected")
        project_version = utils.get_project_version()
        print(f"\N{BOOKMARK} Project version detected:", Fore.YELLOW + project_version)
        with halo.Halo("\N{HAMMER} Building project") as spinner:  # type: ignore
            try:
                artifacts = utils.build_project()
            except Exception as exception:
                spinner.fail(" Building project")
                raise exception
            spinner.succeed(" Building project")
        with halo.Halo("\N{GLOBE WITH MERIDIANS} Creating and uploading release") as spinner:  # type: ignore
            if should_bootstrap:
                utils.create_release(
                    repo=repo,
                    msg=(
                        "# \N{SPARKLES} Initial Release!\n"
                        "We this is our first, ever release! \N{PARTY POPPER}\n"
                    ),
                    tag_name=f"v{project_version}",
                    title=f"Version v{project_version}",
                    artifacts=artifacts.artifacts,
                    commit_hash=lst_commit.hash_id,
                )
            else:
                last_tags = git_utils.get_lst_tags(2)
                utils.create_release(
                    msg=git_utils.generate_release_notes(last_tags[0], last_tags[1]),
                    repo=repo,
                    tag_name=f"v{project_version}",
                    title=f"Version v{project_version}",
                    artifacts=artifacts.artifacts,
                    commit_hash=lst_commit.hash_id,
                )
            spinner.succeed(" Creating and uploading release")
        if should_release:
            with halo.Halo("\N{OUTBOX TRAY} Publishing to PyPi") as spinner:  # type: ignore
                py_utils.publish_for(py_utils.get_project_type())
                spinner.succeed(" Publishing to PyPi")
        artifacts.delete()
    elif should_generate_release_notes:
        from_, to_ = git_utils.get_lst_tags(2)
        print(git_utils.generate_release_notes(from_, to_))
    else:
        print("\N{SLEEPING FACE}", Fore.CYAN + "No work needs to be done")


if __name__ == "__main__":
    main()
