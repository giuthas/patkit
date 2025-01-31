# Installing and using PATKIT

## Requisites

- A computer with a relatively new operating system which has a fairly regular
  file system.
- While pads and phones and watches are computers, PATKIT sadly does not run on
  them. ChromeOS may work, but it is a borderline case as the filesystem is a bit
  exotic for our purposes.
- A Linux, a Mac, or a Windows machine should be fine as long as it is capable
  of running a recent version of Python.
- If issues crop up, get in touch, and we'll see what can be done.

Currently, PATKIT is tested to work on
- PopOS 24.04, which means any recent Ubuntu-like system should be fine.

You only need to care about the detailed dependencies if you do not use uv or
pip for installing. In that case, see the `pyproject.toml` file for a full list
or the `uv.lock` for an even fuller list. If you do decide to use some other
system for installation, please get in touch -- we'd love to have the recipe in
case others need/want it.

## Installing for regular use

Do get in touch if you would like to *test* any of these. A downloadable
executable will hopefully also become reality. Do get in touch if you would like
to *develop* it.

Meanwhile `uv` and `pip` are valid options.

### Using uv

This works independent of patkit being released on
[PyPi](https://pypi.org/search/?q=patkit):
- Install [uv](https://docs.astral.sh/uv/#getting-started).
- Fork patkit on [github](https://github.com/giuthas/patkit) if you like, or
  just clone it directly with `git clone https://github.com/giuthas/patkit` or
  download [the latest
  sources](https://github.com/giuthas/patkit/releases/latest).
- In the root directory of the repository on your machine run `uv build` and `uv
  tool install patkit`.
- Patkit now runs from the commandline with `patkit`. Try `patkit --help` for
  instructions.

Once the [PyPi](https://pypi.org/search/?q=patkit) package exists this
simplifies to:
- Install [uv](https://docs.astral.sh/uv/#getting-started).
- On the commandline run `uv tool install patkit`.
- Running instructions [below](#running-patkit).

### Using pip

Once patkit is on [PyPi](https://pypi.org/search/?q=patkit) (at time of writing
this does not work yet, but once that link finds patkit, it should):

- First install python either using your OS's software shop features or from
  [the official download page](https://www.python.org/downloads/).
- Second, run `pip install patkit`.

## Installing for development

This works independent of patkit being released on
[PyPi](https://pypi.org/search/?q=patkit):
- Install [uv](https://docs.astral.sh/uv/#getting-started).
- Fork patkit on [github](https://github.com/giuthas/patkit) if you like, or
  just clone it directly with `git clone https://github.com/giuthas/patkit` or
  download [the latest
  sources](https://github.com/giuthas/patkit/releases/latest).
- Optionally run these to get Patkit installed as a commandline tool.
  - In the root directory of the repository on your machine run `uv build` and `uv
    tool install patkit`.
- Or you can just use `uv` to run patkit: `uv run patkit recorded_data/minimal`.
  See `uv`'s [docs](https://docs.astral.sh/uv/) for more.
  
## Running PATKIT

First install PATKIT to run from the commandline.

- Patkit uns from the commandline with `patkit`. 
- Try `patkit --help` for instructions.
- This will analyse a minimal three recording example and open the GUI `patkit
  recorded_data/minimal`

## Running the examples

TODO 0.15: update this

There are three small datasets included in the distribution. You can
run tests on them with the test script `pd_test.py`. Currently, the
following work and produce a new spaghetti_plot.pdf and a transcript
in `[method_name].log`.

``` shell
patkit recorded_data/tongue_data_1_1
```

The first example directory contains recordings with all files present
while the second is intentionally missing some files. The latter case
should therefore produce warnings in the resulting log. Running
without the exclusion list specified should produce a plot with a
couple more curves in it.

The routines to deal with a directory structure like that of `test2`
are yet to be implemented.

## Running the tests

Proper testing is yet to be implemented.
