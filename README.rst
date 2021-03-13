mrelm
=====

My release maker

What is this
------------
This package is a simple script that will create a GitHub release.

It features

 - Auto generated release notes
 - Version tag based on project version bump
 - Nice terminal output
 - Easy usage

How do I use this?
------------------

This is meant to be used at the end of a CI, usually after the build and test step.

You must set the following environment variables:
 - ``GITHUB_TOKEN``: Your GitHub token
 - ``REPO``: The name of the repository (in the ``username/repo_name`` format)
 - ``PYPI_USERNAME``: The PyPi username (set it to ``__token__`` if you're using a token)
 - ``PYPI_PASSWORD``: The PyPI password (set it to your token if you're using a token)

How do I install this package?
------------------------------
Currently, I have not published this to the PyPi so you'll currently need to install it by executing the following command:

.. code-block:: bash

    git clone https://github.com/ThatXliner/mrelm.git  # Clone it
    cd mrelm
    python3 -m pip install poetry  # Install poetry
    poetry build
    python3 -m pip install dist/*.whl

Why not Semantic Release Bot?
------------------------------

Semantic Release Bot is a little big and hard to configure. I made this project for myself, so it currently only supports the following project types:

 - Python
    - Poetry-based

And the project must use the `Gitmoji Commit Standard <https://gitmoji.dev>`_.
