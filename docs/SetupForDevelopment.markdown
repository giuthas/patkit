# Setting PATKIT up for Development

# NOTE: 

As of PATKIT 0.14, these instructions are incorrect and only here in case
someone wants to install PATKIT using mamba/conda etc. If you are that someone
and would like to contribute, please fork PATKIT, update these instructions, and
send us a pull request.

## On with the instructions

The most important steps for getting PATKIT installed in development mode are:

- [Setting PATKIT up for Development](#setting-patkit-up-for-development)
  - [Preliminaries](#preliminaries)
  - [Fork and clone the repository](#fork-and-clone-the-repository)
  - [Clone directly from the PATKIT main](#clone-directly-from-the-patkit-main)
  - [Create the conda environments](#create-the-conda-environments)
  - [Install PATKIT in development mode](#install-patkit-in-development-mode)
  - [Other topics](#other-topics)
    - [Rebuild and activate a conda environment after updating the environment](#rebuild-and-activate-a-conda-environment-after-updating-the-environment)

## Preliminaries

Install the following:

- [Mamba](https://mamba.readthedocs.io/en/latest/installation.html)
  - Mamba is used for building the conda environments that PATKIT runs in.
  - If you already have Conda installed, you will still need Mamba, since Conda
    has been shown to not be able to deal with the rather complex dependencies,
    and in any case Mamba is much faster.
  - If Mamba is not available, it is possible to try to install all the
    dependencies with using just pypi. If you manage to do that, please
    document how you did it and let us know, so that those instructions can be
    added here. (We have not tried to do this.)
- [VSCode](https://code.visualstudio.com/),
  [PyCharm](https://www.jetbrains.com/pycharm/),
  [Emacs](https://www.gnu.org/software/emacs/), or some other IDE that you
  would like to use.
  - For any of these it is a good idea to get PyLint and some version of
    autopep8 installed and working in the IDE to manage most of style and many
    other issues with the code automatically.
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) in some
  form.
  - The basic version is a command line tool, but there are many GUIs
    available.
  - For using GitHub from the command line (see below),
    [gh](https://cli.github.com/) maybe worth a look.

If planning to fork the GitHub repository, you will also need a [GitHub
account](https://github.com/join).

## Fork and clone the repository

First, fork the repository from
[https://github.com/giuthas/patkit](https://github.com/giuthas/patkit).

Second, clone the repository to your local system.

Third, if not automatically done, setup the original repository as your
upstream repo:

```bash
git remote add upstream https://github.com/giuthas/patkit
git fetch upstream
git merge upstream/main main
```

Here's what this does in practice:

![forking PATKIT](forking_patkit.drawio.png)

## Clone directly from the PATKIT main

In a directory that you would like the clone to live in, run the following
command optionally giving a name for the directory PATKIT will be cloned to.

```bash
git clone https://github.com/giuthas/patkit [optional directory]
```

## Create the conda environments

Once you have a copy of PATKIT's source code, run these commands on the command
line:

```bash
cd [patkit root]
mamba env create -f patkit_stable_conda_env.yaml
mamba env create -f patkit_devel_conda_env.yaml
```

And to actually use the latter:

```bash
conda activate patkit-devel
```

## Install PATKIT in development mode

This should work in [the usual
way](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode)
for Python packages by just running `pip install -e .` in the root directory of
PATKIT -- NOT the `patkit` directory inside the package, but the root directory
of the repository.

This will enable use of PATKIT as a library as if it were a regularly installed
Python package, while waht actually gets used is the live code base in the
local repository. **This needs to be done separately for each Python
conda/virtual environment in use.**

## Other topics

Other topics covered by this guide:

- [Rebuild and activate a conda environment after updating the environment](#rebuild-and-activate-a-conda-environment-after-updating-the-environment).

### Rebuild and activate a conda environment after updating the environment

After either downloading a newer version or making local changes, run these
commands on the command line:

```bash
conda activate base
conda env remove -n patkit-devel
mamba env create -f patkit_devel_conda_env.yaml
conda activate patkit-devel
```

Substitute `patkit-stable` for `patkit-devel` and
`patkit_stable_conda_env.yaml` for `patkit_devel_conda_env.yaml` to update the
stable environment.
