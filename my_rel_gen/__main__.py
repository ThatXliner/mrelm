#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line interface"""
import sys

import halo

from . import git_utils, utils

REPO = sys.argv[1]


def main() -> None:
    lst_commit = git_utils.get_lst_commit()
    if utils.is_version_bump(lst_commit.message):
        project_version = utils.get_project_version()
        print(f"\N{BOOKMARK} Project version: {project_version}")
        # git_utils.create_tag(
        #     REPO, "v{version}".format(version=project_version), on=lst_commit
        # )
        with halo.Halo(text="Building project..."):  # type: ignore
            artifacts = utils.build_project()
        with halo.Halo(text="Creating and uploading release"):  # type: ignore
            utils.create_release(
                msg=git_utils.generate_release_notes(*git_utils.get_lst_tags(2)),
                repo=REPO,
                tag_name=f"v{project_version}",
                title=f"Version v{project_version}",
                artifacts=artifacts.artifacts,
                commit_hash=lst_commit.hash_id,
            )
        artifacts.delete()
    print("No work needs to be done \N{SLEEPING FACE}")


if __name__ == "__main__":
    main()
